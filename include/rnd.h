#pragma once
#include <optional>
#include <pcg_random.hpp>
#include <random>

namespace rnd {
    namespace internal {
        inline pcg64 prng; // The pseudorandom number generator
    }

    void seed(std::optional<uint64_t> number = std::nullopt);

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
