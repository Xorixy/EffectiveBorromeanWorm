#pragma once
#include "rnd.h"
#include "log.h"
#include "settings.h"
#include <CLI/CLI.hpp>
#include <fmt/core.h>
#include <string>

namespace cli {
    int parse(int argc, char *argv[]);
}