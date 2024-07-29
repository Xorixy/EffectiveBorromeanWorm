#pragma once
#include "state.h"
#include "uint128.h"

namespace sim {

    class SimulationException final : public std::exception
    {
        private:
        std::string m_error{}; // handle our own string

        public:
        explicit SimulationException(std::string_view error)
            : m_error{error}
        {
        }

        // std::exception::what() returns a const char*, so we must as well
        [[nodiscard]] const char* what() const noexcept override { return m_error.c_str(); }
    };

    struct SaveStruct {
        simple_uint128 windings_sum_squared { 0 };
        simple_uint128 windings_difference_squared { 0 };
        long long unsigned int parititon_function { 0 };
        long long unsigned int annulus_sum { 0 };
    };

    class Simulation {
        private:
            state::State m_state;
            state::Annulus m_annulus;
            SaveStruct save;
        public:

    };
}
