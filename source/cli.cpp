#include "../include/cli.h"

int cli::parse(int argc, char *argv[]) {
    CLI::App app;
    app.description("Simulation of effective borromeanicity");
    app.get_formatter()->column_width(90);
    app.option_defaults()->always_capture_default();
    app.allow_extras(false);

    int size = -1;
    std::string settings_path = "settings.h5";

    /* clang-format off */
    /*
    app.add_option("-n, --n_steps"          , settings::sim::n_steps, "Number of simulation steps");
    app.add_option("-t, --n_therm"          , settings::sim::n_therm, "Number of thermalization steps");
    app.add_option("-x, --size_x"           , settings::sim::size_x, "System size in the x direction");
    app.add_option("-y, --size_y"           , settings::sim::size_y, "System size in the y direction");
    app.add_option("-s, --size"             , size                 , "System size in both x- and y directions. If --size is set it overrides --size_x/--size_y flags");
    app.add_option("-k, --single_weight"    , settings::sim::single_weight, "Weight of a single bond");
    app.add_option("-c, --counter_weight"   , settings::sim::single_weight, "Weight of a counter bond");
    app.add_flag  ("-w, --windings"           , settings::save::windings, "Save windings");
    app.add_flag  ("-g, --correlations"       , settings::save::correlations, "Save correlations");
    app.add_flag  ("-m, --time_series"        , settings::save::time_series, "Save as time series");
    app.add_flag  ("-b, --bond_config"        , settings::save::bond_config, "Save final bond configuration");
    app.add_option("-a, --annulus_size"      , settings::save::annulus_size, "Sets size of the annulus for saving correlations. Outer radius of annulus is always system size/2, inner radius equals outer radius * ( 1 - annulus_size)");
    app.add_option("-i, --save_interval"       , settings::save::save_interval, "Interval (in steps) for saving in time series");
    app.add_option("-r, --seed"              , settings::random::seed            , "Random number seed");
    */
    app.add_option("-s, --settings", settings_path, "Path to an h5 file containing the program settings");
    app.add_option("-r, --seed"              , settings::random::seed            , "Random number seed");
    app.add_option("-o, --filename"          , settings::io::filename     , "Path to the output file");
    app.add_option("-l, --loglevel"          , settings::log::level              , "Verbosity 0:high --> 6:off")->check(CLI::Range(0,6));

    /* clang-format on */
    CLI11_PARSE(app, argc, argv);

    if (size != -1) {
        settings::sim::size_x = size;
        settings::sim::size_y = size;
    }
    logger::log = spdlog::stdout_color_mt("EffBor", spdlog::color_mode::always);
    logger::log->set_level(static_cast<spdlog::level::level_enum>(settings::log::level));

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
    logger::log->info("bond_config      : {}", settings::save::bond_config);
    logger::log->info("seed             : {}", settings::random::seed);
    logger::log->info("filename         : {}", settings::io::filename);

    return 0;
}