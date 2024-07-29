#pragma once
#include "io"
#include <h5pp/h5pp.h>
#include "settings.h"
#include <vector>
#include <string>

namespace io {
    void test();
    void loadSettings(std::string settings_path);
}