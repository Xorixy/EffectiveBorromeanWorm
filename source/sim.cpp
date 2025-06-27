#include "../include/sim.h"

sim::Simulation::Simulation() = default;

/*
void sim::Simulation::print_save_data() {
    fmt::print("Windings difference squared : {} {}\n", save.windings_difference_squared.big, save.windings_difference_squared.small);
    fmt::print("Windings sum squared : {} {}\n", save.windings_sum_squared.big, save.windings_sum_squared.small);
    fmt::print("Partition function: {}\n", save.partition_function);
    fmt::print("Annulus sum: {}\n", save.annulus_sum);
}
*/

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
        if (settings::save::time_series && i_iter % settings::save::save_interval == 0) {
            auto & component_windings = m_state.get_winding_numbers();
            if (settings::save::save_therm) {
                save.windings.at(0) = component_windings.at(0).at(0);
                save.windings.at(1) = component_windings.at(0).at(1);
                save.windings.at(2) = component_windings.at(1).at(0);
                save.windings.at(3) = component_windings.at(1).at(1);
                save.total_bonds = m_state.get_total_bonds();
            }
            time.add_slice(save);
        }
    }
    elapsed = std::chrono::steady_clock::now() - start_time;
    logger::log->info("Done in {} s\n", elapsed.count());
    start_time = std::chrono::steady_clock::now();
    logger::log->info("Saving simulation...");
    io::outfile = io::try_to_open_file(settings::io::filename, false);
    io::save_base();
    io::save_annulus_size(m_annulus.get_size());
    if (!settings::save::time_series || i_iter % settings::save::save_interval != 0) {
        auto & component_windings = m_state.get_winding_numbers();
        if (settings::save::save_therm) {
            save.windings.at(0) = component_windings.at(0).at(0);
            save.windings.at(1) = component_windings.at(0).at(1);
            save.windings.at(2) = component_windings.at(1).at(0);
            save.windings.at(3) = component_windings.at(1).at(1);
            save.total_bonds = m_state.get_total_bonds();
        }
        time.add_slice(save);
    }
    if (settings::save::time_series) {
        io::save_time_series(time, "data/");
    } else {
        io::save_slice(save, "data/");
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
            auto [wind_diff_x, wind_diff_y] = m_state.get_winding_diff_square();
            auto [wind_sum_x , wind_sum_y ] = m_state.get_winding_sum_square();
            save.windings_difference_squared_x.add(wind_diff_x);
            save.windings_difference_squared_y.add(wind_diff_y);
            save.windings_sum_squared_x.add(wind_sum_x);
            save.windings_sum_squared_y.add(wind_sum_y);
        }
    }
    else if (settings::save::correlations && m_annulus.contains(m_state.get_coords(worm_head), m_state.get_coords(worm_tail)))
        save.annulus_sum++;
}

sim::TimeSeriesStruct::TimeSeriesStruct()
    : windings_sum_squared_x(0)
    , windings_sum_squared_y(0)
    , windings_difference_squared_x(0)
    , windings_difference_squared_y(0)
    , partition_function(0)
    , annulus_sum(0)
    , windings(0)
    , total_bonds(0)
{}

void sim::TimeSeriesStruct::add_slice(const SaveStruct &save) {
    windings_sum_squared_x.push_back(save.windings_sum_squared_x);
    windings_sum_squared_y.push_back(save.windings_sum_squared_y);
    windings_difference_squared_x.push_back(save.windings_difference_squared_x);
    windings_difference_squared_y.push_back(save.windings_difference_squared_y);
    partition_function.push_back(save.partition_function);
    annulus_sum.push_back(save.annulus_sum);
    windings.push_back(save.windings);
    total_bonds.push_back(save.total_bonds);
}
