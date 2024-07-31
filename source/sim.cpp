#include "../include/sim.h"

sim::Simulation::Simulation() = default;

void sim::Simulation::print_save_data() {
    fmt::print("Windings difference squared : {} {}\n", save.windings_difference_squared.big, save.windings_difference_squared.small);
    fmt::print("Windings sum squared : {} {}\n", save.windings_sum_squared.big, save.windings_sum_squared.small);
    fmt::print("Partition function: {}\n", save.partition_function);
    fmt::print("Annulus sum: {}\n", save.annulus_sum);
}

void sim::Simulation::run() {
    logger::log->info("Done\n");
    std::chrono::time_point<std::chrono::steady_clock> start_time;
    start_time = std::chrono::steady_clock::now();
    logger::log->info("Thermalizing...");
    unsigned long long int i_iter = 0;
    while((i_iter < settings::sim::n_therm) || (m_state.get_worm_head() != m_state.get_worm_tail())) {
        m_state.try_to_move_worm();
        i_iter++;
    }
    std::chrono::duration<double> elapsed = std::chrono::steady_clock::now() - start_time;
    logger::log->info("Done in {} s\n", elapsed.count());
    i_iter = 0;
    start_time = std::chrono::steady_clock::now();
    logger::log->info("Running simulation...");
    while(i_iter < settings::sim::n_steps) {
        m_state.try_to_move_worm();
        extract_state_data();
        i_iter++;
        /*
        fmt::print("Iteration {}\n", i_iter);
        m_state.print_windings();
        fmt::print("Diffsqr: {}\n", m_state.get_winding_diff_square());
        fmt::print("Sumsqr: {}\n\n", m_state.get_winding_sum_square());
        fmt::print("Saved data:\n");
        print_save_data();
        fmt::print("\n");
        */
        if (settings::save::time_series && i_iter % settings::save::save_interval == 0) {
            //fmt::print("Saving slice\n");
            try {
                io::save_slice(save, std::to_string(settings::random::seed) + "/" + std::to_string(i_iter) + "/");
            } catch (std::exception& e) {
                logger::log->info("Error {}\n", e.what());
                return;
            }
        }
    }
    if (!settings::save::time_series || i_iter % settings::save::save_interval != 0) {
        io::save_slice(save, std::to_string(settings::random::seed) + "/" + std::to_string(i_iter) + "/");
    }

    elapsed = std::chrono::steady_clock::now() - start_time;
    logger::log->info("Done in {} s\n", elapsed.count());
}

void sim::Simulation::extract_state_data() {
    const int worm_head = m_state.get_worm_head();
    const int worm_tail = m_state.get_worm_tail();
    if (worm_head == worm_tail) {
        save.partition_function++;
        if (settings::save::windings) {
            save.windings_difference_squared.add(m_state.get_winding_diff_square());
            save.windings_sum_squared.add(m_state.get_winding_sum_square());
        }
    }
    else if (settings::save::correlations && m_annulus.contains(m_state.get_coords(worm_head), m_state.get_coords(worm_tail)))
        save.annulus_sum++;
}

