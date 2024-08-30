#pragma once
#include <optional>
#include <pcg_random.hpp>
#include <random>
#include "settings.h"

namespace rnd {
    namespace internal {
        inline pcg64 prng; // The pseudorandom number generator
        inline std::optional<std::uniform_int_distribution<int>> direction_dist;
        inline std::optional<std::uniform_real_distribution<double>> unit_dist;
        inline std::optional<std::uniform_int_distribution<int>> location_dist;
        inline std::optional<std::uniform_int_distribution<int>> color_dist;
    }

    void seed(std::optional<uint64_t> number = std::nullopt);
    double uniform_unit();
    int uniform_dir();
    int uniform_loc();
    int uniform_color();

    template<typename T>
    [[nodiscard]] T uniform(T min, T max) {
        static_assert(std::is_arithmetic_v<T>);
        if constexpr(std::is_integral_v<T>) {
            std::uniform_int_distribution<T> dist(min, max);
            return dist(internal::prng);
        } else if constexpr(std::is_floating_point_v<T>) {
            std::uniform_real_distribution<T> dist(min, max);
            return dist(internal::prng);
        }
    }



    template<typename T>
    [[nodiscard]] T normal(T mu, T sigma) {
        static_assert(std::is_floating_point_v<T>);
        std::normal_distribution<T> dist(mu, sigma);
        return dist(internal::prng);
    }

}
