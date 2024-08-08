#pragma once
#include <h5pp/h5pp.h>
#include "settings.h"
#include <vector>
#include <string>
#include "sim.h"
#include <climits>
#include "../include/log.h"
#include <thread>
#include <chrono>

namespace sim {
    struct SaveStruct;
    struct TimeSeriesStruct;
}

namespace io {
    inline h5pp::File outfile;

    void load_settings();
    void save_settings();

    void save_slice(const sim::SaveStruct& save, const std::string& prefix);

    void save_time_series(const sim::TimeSeriesStruct& save, const std::string& prefix);

    void save_annulus_size(int annulus_size);

    void save_base();

    h5pp::File try_to_open_file(const std::string& filename, bool readonly);

    void save_uint_vec(const simple_uint128_vec& vec, const std::string &path);
}