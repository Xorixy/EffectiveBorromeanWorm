#include "../include/state.h"
#include "../include/io.h"

using Point = state::Point;
using Coord = state::Coord;

Coord state::relative_coord(const Coord& c1, const Coord& c2) {
    return {
        (c1.first - c2.first + settings::sim::size_x + settings::sim::size_x/2)%settings::sim::size_x,
        (c1.second - c2.second + settings::sim::size_y + settings::sim::size_y/2)%settings::sim::size_y
    };
}

int state::opposite_direction(const int x) {
    return (x + 2) % 4;
}

int state::direction_sign(const int x) {
    return 2*(x / 2) - 1;
}
int state::absolute_direction(const int x) {
    return x % 2;
}

Point state::point_id(const Coord & coord) {
    return coord.second + settings::sim::size_y * coord.first;
}

Point state::point_id(int x, int y) {
    return y + settings::sim::size_y * x;
}

state::Lattice::Lattice()
    : m_neighbours(settings::sim::size_x*settings::sim::size_y, std::vector<Point>(4))
    , m_coords(settings::sim::size_x*settings::sim::size_y)
{
     const int size_x = settings::sim::size_x;
     const int size_y = settings::sim::size_y;
     const int size = size_x*size_y;
     for (int ix = 0 ; ix < size_x ; ix ++) {
        for (int iy = 0 ; iy < size_y ; iy ++) {
            const Point point = point_id(ix, iy);
            m_coords.at(point) = {ix, iy};
            m_neighbours.at(point).at(0) = point_id((ix + 1 + size_x) % size_x , iy);
            m_neighbours.at(point).at(1) = point_id(ix                       , (iy + 1 + size_y) % size_y);
            m_neighbours.at(point).at(2) = point_id((ix - 1 + size_x) % size_x , iy);
            m_neighbours.at(point).at(3) = point_id(ix                       , (iy - 1 + size_y) % size_y);
        }
     }
}

std::vector<state::Point> &state::Lattice::get_neighbours(const Point p) {
    return m_neighbours.at(p);
}

state::Coord state::Lattice::get_coordinates(const Point p) {
    return m_coords.at(p);
}

state::Annulus::Annulus()
    : m_annulus(settings::sim::size_x*settings::sim::size_y)
    , m_size { 0 }
{
    Coord origin = {0,0};
    const double l_max = 0.5*settings::sim::size_x;
    const double l_min = (1 - settings::save::annulus_size)*l_max;

    for (int ix = 0 ; ix < settings::sim::size_x ; ix++) {
        for (int iy = 0 ; iy < settings::sim::size_y ; iy++) {
            int px, py;
            if (ix <= settings::sim::size_x/2) {
                px = ix;
            } else {
                px = settings::sim::size_x - ix;
            }
            if (iy <= settings::sim::size_y/2) {
                py = iy;
            } else {
                py = settings::sim::size_y - iy;
            }
            if (const int r_sqr = px * px + py * py; (r_sqr >= l_min*l_min) && (r_sqr <= l_max*l_max)) {
                m_annulus[point_id(ix, iy)] = true;
                m_size++;
            } else {
                m_annulus[point_id(ix, iy)] = false;
            }
        }
    }
}

bool state::Annulus::contains(const Coord& r) {
    return m_annulus.at(point_id(r));
}

bool state::Annulus::contains(const Coord& c1, const Coord& c2) {
    return contains(relative_coord(c1, c2));
}

int state::Annulus::get_size() const {
    return m_size;
}

state::State::State()
    : m_bonds(settings::sim::size_x*settings::sim::size_y, std::vector<std::vector<int>>(4, std::vector<int>(2, 0)))
    , m_winding_numbers(2, std::vector<long long int>(2, 0))
    , worm_head { 0 }
    , worm_tail { 0 }
    , worm_color_forward { 0 }
    , worm_color_backward { 0 }
{
    recolor_worm();
}

int other_color(int c) {
    return (c + 1) % 2;
}

void state::State::try_to_add_bond(int dir) {
    Point p = worm_head;
    int cf = worm_color_forward;
    int cb = worm_color_backward;
    auto bonds = m_bonds.at(p).at(dir);
    if (cb == -1) {
        if (
            (bonds.at(cf) == -1 && (bonds.at(other_color(cf)) == 0
            || rnd::uniform_unit() < settings::worm::counter_to_single_ratio))
            || (bonds.at(cf) == 0 &&
            ((bonds.at(other_color(cf)) == 0 && rnd::uniform_unit() < settings::sim::single_weight)
            || (bonds.at(other_color(cf)) == -1 && rnd::uniform_unit() < settings::worm::single_to_counter_ratio)))
        )
        {
            m_bonds.at(p).at(dir).at(cf) += 1;
            const Point p_opposite = m_lattice.get_neighbours(p).at(dir);
            m_bonds.at(p_opposite).at(opposite_direction(dir)).at(cf) -= 1;
            if (settings::save::windings) {
                m_winding_numbers.at(cf).at(absolute_direction(dir)) += direction_sign(dir);
            }
            worm_head = p_opposite;
        }
    }
    else if (cf == -1) {
        if (
            (bonds.at(cb) == 1 && (bonds.at(other_color(cb)) == 0
                                    || rnd::uniform_unit() < settings::worm::counter_to_single_ratio))
            || (bonds.at(cb) == 0 &&
                ((bonds.at(other_color(cb)) == 0 && rnd::uniform_unit() < settings::sim::single_weight)
                 || (bonds.at(other_color(cb)) == 1 && rnd::uniform_unit() < settings::worm::single_to_counter_ratio)))
        )
        {
            m_bonds.at(p).at(dir).at(cb) -= 1;
            const Point p_opposite = m_lattice.get_neighbours(p).at(dir);
            m_bonds.at(p_opposite).at(opposite_direction(dir)).at(cb) += 1;
            if (settings::save::windings) {
                m_winding_numbers.at(cb).at(absolute_direction(dir)) -= direction_sign(dir);
            }
            worm_head = p_opposite;
        }
    }

    else {
        if (
            (bonds.at(cf) == -1 || bonds.at(cb) == 1)
            || (bonds.at(cf) == 0 && bonds.at(cb) == 0 && rnd::uniform_unit() < settings::sim::counter_weight )
        )
        {
            m_bonds.at(p).at(dir).at(cf) += 1;
            m_bonds.at(p).at(dir).at(cb) -= 1;
            const Point p_opposite = m_lattice.get_neighbours(p).at(dir);
            m_bonds.at(p_opposite).at(opposite_direction(dir)).at(cf) -= 1;
            m_bonds.at(p_opposite).at(opposite_direction(dir)).at(cb) += 1;
            if (settings::save::windings) {
                m_winding_numbers.at(cf).at(absolute_direction(dir)) += direction_sign(dir);
                m_winding_numbers.at(cb).at(absolute_direction(dir)) -= direction_sign(dir);
            }
            worm_head = p_opposite;
        }
    }
}

void state::State::relocate_worm() {
    if (worm_head != worm_tail) throw sim::SimulationException("Error: tried relocating the worm, but the head and tail are not in the same position.");
    const int new_pos = rnd::uniform_loc();
    worm_head = new_pos;
    worm_tail = new_pos;
}

void state::State::recolor_worm() {
    if (worm_head != worm_tail) throw sim::SimulationException("Error: tried recoloring the worm, but the head and tail are not in the same position.");
    switch (rnd::uniform_color()) {
        case 0:
            worm_color_forward = 0;
            worm_color_backward = -1;
            break;
        case 1:
            worm_color_forward = 1;
            worm_color_backward = -1;
            break;
        case 2:
            worm_color_forward = -1;
            worm_color_backward = 0;
            break;
        case 3:
            worm_color_forward = -1;
            worm_color_backward = 1;
            break;
        case 4:
            worm_color_forward = 0;
            worm_color_backward = 1;
            break;
        case 5:
            worm_color_forward = 1;
            worm_color_backward = 0;
            break;
    }
}

void state::State::try_to_move_worm() {
    if (worm_head == worm_tail && rnd::uniform_unit() < settings::worm::p_move) relocate_worm();
    if (worm_head == worm_tail && rnd::uniform_unit() < settings::worm::p_type) recolor_worm();
    int dir = rnd::uniform_dir();
    try_to_add_bond(dir);
}

Point state::State::get_worm_head() const {
    return worm_head;
}

Point state::State::get_worm_tail() const {
    return worm_tail;
}


void state::State::print_state() {
    //Should only be used for small ish grids
    std::string row1, row2, row3, row4;
    fmt::print("STATE OF BONDS:\n");
    fmt::print("COLOR FORWARD: {}   , COLOR BACKWARD: {}\n", worm_color_forward, worm_color_backward);
    fmt::print("WINDINGS: C1 UP = {}, C1 LEFT = {}, C2 UP = {}, C2 LEFT = {}\n", m_winding_numbers.at(0).at(0), m_winding_numbers.at(0).at(1),m_winding_numbers.at(1).at(0), m_winding_numbers.at(1).at(1));
    for (int ix = 0 ; ix < settings::sim::size_x ; ix++) {
        row1 = "";
        row2 = "";
        row3 = "";
        row4 = "";
        for (int iy = 0 ; iy < settings::sim::size_y ; iy++) {
            Point p = point_id(ix, iy);
            row1 += " ";
            switch (m_bonds.at(p).at(2).at(0)) {
                case 1:
                    row1 += "A";
                    break;
                case -1:
                    row1 += "V";
                    break;
                default:
                    row1 += " ";
            }
            switch (m_bonds.at(p).at(2).at(1)) {
                case 1:
                    row1 += "A";
                    break;
                case -1:
                    row1 += "V";
                    break;
                default:
                    row1 += " ";
            }
            row1 += " ";
            switch (m_bonds.at(p).at(3).at(0)) {
                case 1:
                    row2 += "<";
                    break;
                case -1:
                    row2 += ">";
                    break;
                default:
                    row2 += " ";
            }
            if (worm_head == worm_tail && p == worm_head) {
                row2 += "WW";
            } else if (p == worm_head) {
                row2 += "HH";
            } else if (p == worm_tail) {
                row2 += "TT";
            } else {
                row2 += "OO";
            }
            switch (m_bonds.at(p).at(1).at(0)) {
                case 1:
                    row2 += ">";
                    break;
                case -1:
                    row2 += "<";
                    break;
                default:
                    row2 += " ";
            }
            switch (m_bonds.at(p).at(3).at(1)) {
                case 1:
                    row3 += "<";
                    break;
                case -1:
                    row3 += ">";
                    break;
                default:
                    row3 += " ";
            }
            if (worm_head == worm_tail && p == worm_head) {
                row3 += "WW";
            } else if (p == worm_head) {
                row3 += "HH";
            } else if (p == worm_tail) {
                row3 += "TT";
            } else {
                row3 += "OO";
            }
            switch (m_bonds.at(p).at(1).at(1)) {
                case 1:
                    row3 += ">";
                    break;
                case -1:
                    row3 += "<";
                    break;
                default:
                    row3 += " ";
            }
            row4 += " ";
            switch (m_bonds.at(p).at(0).at(0)) {
                case 1:
                    row4 += "V";
                    break;
                case -1:
                    row4 += "A";
                    break;
                default:
                    row4 += " ";
            }
            switch (m_bonds.at(p).at(0).at(1)) {
                case 1:
                    row4 += "V";
                    break;
                case -1:
                    row4 += "A";
                    break;
                default:
                    row4 += " ";
            }
            row4 += " ";
        }
        fmt::print("{}\n", row1);
        fmt::print("{}\n", row2);
        fmt::print("{}\n", row3);
        fmt::print("{}\n", row4);
    }
}

std::pair<long long, long long> state::State::get_winding_diff_square() {
    return {(m_winding_numbers.at(0).at(0) - m_winding_numbers.at(1).at(0))*(m_winding_numbers.at(0).at(0) - m_winding_numbers.at(1).at(0)),
           (m_winding_numbers.at(0).at(1) - m_winding_numbers.at(1).at(1))*(m_winding_numbers.at(0).at(1) - m_winding_numbers.at(1).at(1))};
}

std::pair<long long, long long> state::State::get_winding_sum_square() {
    return {(m_winding_numbers.at(0).at(0) + m_winding_numbers.at(1).at(0))*(m_winding_numbers.at(0).at(0) + m_winding_numbers.at(1).at(0)),
           (m_winding_numbers.at(0).at(1) + m_winding_numbers.at(1).at(1))*(m_winding_numbers.at(0).at(1) + m_winding_numbers.at(1).at(1))};
}

Coord state::State::get_coords(state::Point p) {
    return m_lattice.get_coordinates(p);
}

void state::State::print_windings() {
    fmt::print("WINDINGS: C1 UP = {}, C1 LEFT = {}, C2 UP = {}, C2 LEFT = {}\n", m_winding_numbers.at(0).at(0), m_winding_numbers.at(0).at(1),m_winding_numbers.at(1).at(0), m_winding_numbers.at(1).at(1));
}