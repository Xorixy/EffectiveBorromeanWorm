#pragma once
#include <h5pp/h5pp.h>
#include "settings.h"
#include <vector>
#include <string>
#include "sim.h"
#include <climits>

namespace sim {
    struct SaveStruct;
}

namespace io {
    inline h5pp::File outfile;

    void load_settings();
    void save_settings();

    void save_slice(const sim::SaveStruct& save, const std::string& prefix);

    void save_annulus_size(int annulus_size);

    void save_base();
}