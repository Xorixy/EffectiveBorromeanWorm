#pragma once
#include <vector>
#include "settings.h"
#include <cmath>
#include "uint128.h"
#include "../include/rnd.h"
#include "../include/sim.h"

namespace sim::state {
    using Point = int;
    using Coord = std::pair<int, int>;
    Point point_id(const Coord & coord);
    Point point_id(int x, int y);
    int opposite_direction(int x);
    int direction_sign(int x);
    int absolute_direction(int x);

    //Returns the relative coordinates of c1, c2 adjusted such that a relative
    //Distance of zero return s the origin at size_x/2, size_y/2
    inline Coord relative_coord(const Coord& c1, const Coord& c2);

    class Lattice {
        private:
            std::vector<std::vector<Point>> m_neighbours;
            std::vector<Coord> m_coords;
        public:
            Lattice();
            [[nodiscard]] std::vector<Point>& get_neighbours(Point p);
            [[nodiscard]] Coord get_coordinates(Point p);
    };
    class Annulus {
        private:
            std::vector<bool> m_annulus;
            int m_size;
        public:
            Annulus();

            //Returns true if the annulus contains the relative coordinate r
            [[nodiscard]] bool contains(const Coord& r);

            //Returns true if the annulus contains the relative coordinate between c1 and c2
            [[nodiscard]] bool contains(const Coord& c1, const Coord& c2);

            //Returns the number of points in the annulus
            [[nodiscard]] int get_size() const;
    };

    class State {
        private:
            Lattice m_lattice;
            std::vector<std::vector<std::vector<int>>> m_bonds;
            std::vector<std::vector<long long unsigned int>> m_winding_numbers;
            Point worm_head;
            Point worm_tail;
            int worm_color_forward;
            int worm_color_backward;
        public:
            State();
            void try_to_add_bond(Point p, int dir);
            void move_worm();
            Point get_worm_head();
            Point get_worm_tail();
            void relocate_worm();
            void recolor_worm();
    };
}
