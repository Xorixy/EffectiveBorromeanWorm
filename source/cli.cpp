#include "../include/cli.h"
#include "../include/io.h"

int cli::parse(int argc, char *argv[]) {
    CLI::App app;
    app.description("Simulation of effective borromeanicity");
    app.get_formatter()->column_width(90);
    app.option_defaults()->always_capture_default();
    app.allow_extras(false);

    bool save_settings_no_run = false;
    bool save_settings = false;
    bool debug = false;

    app.add_option("-n, --n_steps"          , settings::sim::n_steps, "Number of simulation steps");
    app.add_option("-t, --n_therm"          , settings::sim::n_therm, "Number of thermalization steps");
    app.add_option("-x, --size_x"           , settings::sim::size_x, "System size in the x direction");
    app.add_option("-y, --size_y"           , settings::sim::size_y, "System size in the y direction");
    app.add_option("-k, --single_weight"    , settings::sim::single_weight, "Weight of a single bond");
    app.add_option("-c, --counter_weight"   , settings::sim::counter_weight, "Weight of a counter bond");
    app.add_flag  ("-w, --windings"           , settings::save::windings, "Save windings");
    app.add_flag  ("-g, --correlations"       , settings::save::correlations, "Save correlations");
    app.add_flag  ("-m, --time_series"        , settings::save::time_series, "Save as time series");
    app.add_option("-a, --annulus_size"      , settings::save::annulus_size, "Sets size of the annulus for saving correlations. Outer radius of annulus is always system size/2, inner radius equals outer radius * ( 1 - annulus_size)");
    app.add_option("-i, --save_interval"       , settings::save::save_interval, "Interval (in steps) for saving in time series");
    app.add_option("-s, --settings_file", settings::io::settings_path, "Path to an h5 file containing the program settings");
    app.add_option("-r, --seed"              , settings::random::seed            , "Random number seed");
    app.add_option("-o, --filename"          , settings::io::filename     , "Path to the output file");
    app.add_option("-l, --loglevel"          , settings::log::level              , "Verbosity 0:high --> 6:off")->check(CLI::Range(0,6));
    app.add_flag("--save_settings_no_run", save_settings_no_run, "Saves the sim settings given here to the file corresponding to settings_path. Does not run simulation. Overrides debug.");
    app.add_flag("--save_settings_run", save_settings, "Saves the sim settings given here to the file corresponding to settings_path.");
    app.add_flag("--debug"          , debug, "Enters debug mode with the settings from the settings file.");

    /* clang-format on */
    CLI11_PARSE(app, argc, argv);

    if (save_settings || save_settings_no_run) {
        io::save_settings();
        logger::log->info("Saving sim parameters in \"{}\"", settings::io::settings_path);
        if (save_settings_no_run) {
            logger::print_params();
            return 1;
        }
    }

    if (settings::random::seed == 0) io::save_base();

    io::load_settings();

    settings::worm::single_to_counter_ratio = settings::sim::counter_weight/settings::sim::single_weight;
    settings::worm::counter_to_single_ratio = settings::sim::single_weight/settings::sim::counter_weight;
    if (settings::worm::counter_to_single_ratio > 1.0) settings::worm::counter_to_single_ratio = 1.0;
    if (settings::worm::single_to_counter_ratio > 1.0) settings::worm::single_to_counter_ratio = 1.0;

    logger::print_params();

    if (debug) return 2;

    if (settings::io::replace_file) io::outfile = h5pp::File(settings::io::filename, h5pp::FileAccess::REPLACE);
    else io::outfile = h5pp::File(settings::io::filename, h5pp::FileAccess::COLLISION_FAIL);

    return 0;
}