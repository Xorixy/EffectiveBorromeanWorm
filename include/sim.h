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
        simple_uint128 windings_sum_squared { 0 };
        simple_uint128 windings_difference_squared { 0 };
        long long unsigned int partition_function { 0 };
        long long unsigned int annulus_sum { 0 };
    };

    class Simulation {
        private:
            state::State m_state;
            state::Annulus m_annulus;
            SaveStruct save;
        public:
            Simulation();
            void print_save_data();
            void run();
            void extract_state_data();
    };
}


