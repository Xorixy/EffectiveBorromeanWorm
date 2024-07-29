#include "../include/settings.h"
#include "../include/uint128.h"
#include "../include/cli.h"
#include "../include/io.h"
#include <fmt/core.h>
#include <chrono>

int main(int argc, char * argv[]) {
    if (cli::parse(argc, argv) == 1) return 0;
    std::chrono::time_point<std::chrono::steady_clock> start, end;


}
