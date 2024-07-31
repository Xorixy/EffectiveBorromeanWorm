#include "../include/io.h"


void io::load_settings(const std::string& settings_path) {
    const h5pp::File s_file(settings_path, h5pp::FileAccess::READONLY);
    s_file.readDataset<int>(settings::sim::size_x, "settings/sim/size_x");
    s_file.readDataset<int>(settings::sim::size_y, "settings/sim/size_y");
    s_file.readDataset<long long unsigned int>(settings::sim::n_steps, "settings/sim/n_steps");
    s_file.readDataset<long long unsigned int>(settings::sim::n_therm, "settings/sim/n_therm");
    s_file.readDataset<double>(settings::sim::single_weight, "settings/sim/single_weight");
    s_file.readDataset<double>(settings::sim::counter_weight, "settings/sim/counter_weight");
    s_file.readDataset<bool>(settings::save::windings, "settings/save/windings");
    s_file.readDataset<bool>(settings::save::correlations, "settings/save/correlations");
    s_file.readDataset<double>(settings::save::annulus_size, "settings/save/annulus_size");
    s_file.readDataset<int>(settings::save::save_interval, "settings/save/save_interval");
    s_file.readDataset<bool>(settings::save::time_series, "settings/save/time_series");
}

void io::save_settings(const std::string& settings_path) {
    h5pp::File s_file;
    if (settings::io::replace_file) s_file = h5pp::File(settings_path, h5pp::FileAccess::REPLACE);
    else s_file = h5pp::File(settings_path, h5pp::FileAccess::COLLISION_FAIL);
    s_file.writeDataset<int>(settings::sim::size_x, "settings/sim/size_x");
    s_file.writeDataset<int>(settings::sim::size_y, "settings/sim/size_y");
    s_file.writeDataset<long long unsigned int>(settings::sim::n_steps, "settings/sim/n_steps");
    s_file.writeDataset<long long unsigned int>(settings::sim::n_therm, "settings/sim/n_therm");
    s_file.writeDataset<double>(settings::sim::single_weight, "settings/sim/single_weight");
    s_file.writeDataset<double>(settings::sim::counter_weight, "settings/sim/counter_weight");
    s_file.writeDataset<bool>(settings::save::windings, "settings/save/windings");
    s_file.writeDataset<bool>(settings::save::correlations, "settings/save/correlations");
    s_file.writeDataset<double>(settings::save::annulus_size, "settings/save/annulus_size");
    s_file.writeDataset<int>(settings::save::save_interval, "settings/save/save_interval");
    s_file.writeDataset<bool>(settings::save::time_series, "settings/save/time_series");
}

void io::save_annulus_size(const int annulus_size) {
    io::outfile.writeDataset(annulus_size, "/annulus_size");
}


void io::save_slice(sim::SaveStruct& save, const std::string& prefix) {
    io::outfile.writeDataset<long long unsigned int>(save.windings_difference_squared.big, prefix + "/windings_diff_squared/big");
    io::outfile.writeDataset<long long unsigned int>(save.windings_difference_squared.small, prefix + "/windings_diff_squared//small");
    io::outfile.writeDataset<long long unsigned int>(save.windings_sum_squared.big, prefix + "/windings_sum_squared/big");
    io::outfile.writeDataset<long long unsigned int>(save.windings_sum_squared.small, prefix + "/windings_sum_squared//small");
    io::outfile.writeDataset<long long unsigned int>(save.partition_function, prefix + "/partition_function");
    io::outfile.writeDataset<long long unsigned int>(save.annulus_sum, prefix + "/annulus_sum");
}