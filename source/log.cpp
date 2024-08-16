#include "../include/log.h"

void logger::print_params() {
    logger::log->info("n_steps          : {}", settings::sim::n_steps);
    logger::log->info("n_therm          : {}", settings::sim::n_therm);
    logger::log->info("size_x           : {}", settings::sim::size_x);
    logger::log->info("size_y           : {}", settings::sim::size_y);
    logger::log->info("single_weight    : {}", settings::sim::single_weight);
    logger::log->info("counter_weight   : {}", settings::sim::counter_weight);
    logger::log->info("windings         : {}", settings::save::windings);
    logger::log->info("correlations     : {}", settings::save::correlations);
    logger::log->info("annulus_size     : {}", settings::save::annulus_size);
    logger::log->info("time_series      : {}", settings::save::time_series);
    logger::log->info("save_interval    : {}", settings::save::save_interval);
    logger::log->info("seed             : {}", settings::random::seed);
    logger::log->info("filename         : {}", settings::io::filename);
    logger::log->info("replace files    : {}", settings::io::replace_file);
}
