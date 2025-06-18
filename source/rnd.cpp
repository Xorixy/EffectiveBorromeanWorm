//
// Created by david on 2024-02-28.
//
#include "../include/rnd.h"

void rnd::seed(std::optional<uint64_t> number) {
    if(number.has_value()) {
        pcg_extras::seed_seq_from<pcg64> seq(number.value());
        internal::prng.seed(seq);
    }
}

int rnd::uniform_dir() {
    if (internal::direction_dist == std::nullopt) {
        internal::direction_dist = std::uniform_int_distribution<int>(0, 3);
    }
    return internal::direction_dist.value()(internal::prng);
}

double rnd::uniform_unit() {
    if (internal::unit_dist == std::nullopt) {
        internal::unit_dist = std::uniform_real_distribution<double>(0.0, 1.0);
    }
    return internal::unit_dist.value()(internal::prng);
}

int rnd::uniform_loc() {
    if (internal::location_dist == std::nullopt) {
        internal::location_dist = std::uniform_int_distribution<int>(0, settings::sim::size_x*settings::sim::size_y - 1);
    }
    return internal::location_dist.value()(internal::prng);
}

int rnd::uniform_color() {
    if (internal::color_dist == std::nullopt) {
        internal::color_dist = std::uniform_int_distribution<int>(0, 5);
    }
    return internal::color_dist.value()(internal::prng);
}