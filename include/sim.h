#pragma once
#include "state.h"
#include "uint128.h"
#include "rnd.h"
#include "log.h"
#include "io.h"
#include <chrono>
#include <fmt/core.h>

namespace sim {

    struct SaveStruct {
        simple_uint128 windings_sum_squared_x { 0 };
        simple_uint128 windings_sum_squared_y { 0 };
        simple_uint128 windings_difference_squared_x { 0 };
        simple_uint128 windings_difference_squared_y { 0 };
        long long unsigned int partition_function { 0 };
        long long unsigned int annulus_sum { 0 };
        std::array<long long int, 4> windings { 0,0,0,0 };
    };

    struct TimeSeriesStruct {
        simple_uint128_vec windings_sum_squared_x;
        simple_uint128_vec windings_sum_squared_y;
        simple_uint128_vec windings_difference_squared_x;
        simple_uint128_vec windings_difference_squared_y;
        std::vector<long long unsigned int> partition_function;
        std::vector<long long unsigned int> annulus_sum;
        std::vector<std::array<long long int, 4>> windings;
        TimeSeriesStruct();
        void add_slice(const SaveStruct &save);
    };

    class Simulation {
        private:
            state::State m_state;
            state::Annulus m_annulus;
            SaveStruct save;
            TimeSeriesStruct time;
        public:
            Simulation();
            void print_save_data();
            void run();
            void extract_state_data();
    };
}


