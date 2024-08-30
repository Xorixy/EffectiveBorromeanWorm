#include "../include/settings.h"
#include "../include/uint128.h"
#include "../include/cli.h"
#include "../include/io.h"
#include "../include/log.h"
#include <fmt/core.h>
#include <chrono>
#include <string>
#include <iostream>
#include <exception>
#include "mkl.h"

int main(int argc, char * argv[]) {
    std::chrono::time_point<std::chrono::steady_clock> start_time;
    start_time = std::chrono::steady_clock::now();
    logger::log = spdlog::stdout_color_mt("EffBor", spdlog::color_mode::always);
    logger::log->set_level(static_cast<spdlog::level::level_enum>(settings::log::level));
    logger::log->info("Loading settings... ");
    int cliout;
    try {
        cliout = cli::parse(argc, argv);
    } catch (std::exception& e) {
        fmt::print("File error: {}\n", e.what());
    }
    switch (cliout) {
        //This means that the user has saved settings data to a file and wants to quit,
        case 1:
            return 0;
            break;
        case 2:
            state::State s;
            std::string input;
            while (input != "q") {
                s.print_state();
                std::cin >> input;
                if (input == "w") s.try_to_add_bond(2);
                else if (input == "d") s.try_to_add_bond(1);
                else if (input == "s") s.try_to_add_bond(0);
                else if (input == "a") s.try_to_add_bond(3);
                else if (input == "n") s.try_to_move_worm();
                else if (input == "r") s = state::State();
            }
            return 0;
            break;
    }
    logger::log->info("Done\n");
    logger::log->info("Initializing sim...");
    sim::Simulation worm;
    worm.run();
    std::chrono::duration<double> elapsed = std::chrono::steady_clock::now() - start_time;
    logger::log->info("Simulation finished in {} s\n", elapsed.count());
}
