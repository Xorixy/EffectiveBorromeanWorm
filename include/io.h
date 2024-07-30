#pragma once
#include <h5pp/h5pp.h>
#include "settings.h"
#include <vector>
#include <string>
#include "sim.h"

namespace sim {
    class SaveStruct;
}

namespace io {
    inline h5pp::File outfile;

    void load_settings(const std::string& settings_path);
    void save_settings(const std::string& settings_path);

    void save_slice(sim::SaveStruct& save, const std::string& prefix);
}