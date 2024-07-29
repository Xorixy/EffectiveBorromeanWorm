#pragma once
#include "io.h"
#include <h5pp/h5pp.h>
#include "settings.h"
#include <vector>
#include <string>

namespace io {
    void test();
    void load_settings(std::string settings_path);
    void save_settings(std::string settings_path);
}