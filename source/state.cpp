#include "../include/state.h"



namespace state = sim::state;
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
    , m_winding_numbers(2, std::vector<long long unsigned int>(2, 0))
    , worm_head { 0 }
    , worm_tail { 0 }
    , worm_color_forward { 0 }
    , worm_color_backward { 0 }
{}


void state::State::try_to_add_bond(Point p, int dir) {
    if (worm_color_backward == -1) {
        if (
            true //Must fix this logic
            )
        {
            m_bonds.at(p).at(dir).at(worm_color_forward) += 1;
            const Point p_opposite = m_lattice.get_neighbours(p).at(dir);
            m_bonds.at(p_opposite).at(opposite_direction(dir)).at(worm_color_forward) -= 1;
            m_winding_numbers.at(worm_color_forward).at(absolute_direction(dir)) += direction_sign(dir);
            worm_head = m_lattice.get_neighbours(worm_head).at(dir);
        }
    } else {
        if (
            true //Must fix this logic
            )
        {
            m_bonds.at(p).at(dir).at(worm_color_forward) += 1;
            const Point p_opposite = m_lattice.get_neighbours(p).at(dir);
            m_bonds.at(p_opposite).at(opposite_direction(dir)).at(worm_color_forward) -= 1;
            m_winding_numbers.at(worm_color_forward).at(absolute_direction(dir)) += direction_sign(dir);
            worm_head = m_lattice.get_neighbours(worm_head).at(dir);
        }
    }
}

void state::State::relocate_worm() {
    if (worm_head != worm_tail) throw SimulationException("Error: tried relocating the worm, but the head and tail are not in the same position.");
    const int new_pos = rnd::uniform(0, settings::sim::size_x*settings::sim::size_y - 1);
    worm_head = new_pos;
    worm_tail = new_pos;
}

void state::State::recolor_worm() {
    switch (rnd::uniform(0, 2)) {
        case 0:
            worm_color_forward = 0;
            worm_color_backward = -1;
            break;
        case 1:
            worm_color_forward = 1;
            worm_color_backward = -1;
            break;
        case 2:
            worm_color_forward = 0;
            worm_color_backward = 1;
    }

}







