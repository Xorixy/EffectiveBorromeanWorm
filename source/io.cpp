#include "../include/io.h"


void io::test() {
    int v = 10;
    h5pp::File file("settings.h5", h5pp::FileAccess::READWRITE);    // Create a file
    file.writeDataset(v, "settings/sim/size_x");        // Write the vector into a new dataset "myStdVector"
}

void io::load_settings(std::string settings_path) {
    const h5pp::File s_file(settings_path, h5pp::FileAccess::READONLY);
    s_file.readDataset<int>(settings::sim::size_x, "settings/sim/size_x");
    s_file.readDataset<int>(settings::sim::size_y, "settings/sim/size_y");
    s_file.readDataset<long long unsigned int>(settings::sim::n_steps, "settings/sim/n_steps");
    s_file.readDataset<long long unsigned int>(settings::sim::n_therm, "settings/sim/n_therm");
    s_file.readDataset<double>(settings::sim::single_weight, "settings/sim/single_weight");
    s_file.readDataset<double>(settings::sim::counter_weight, "settings/sim/counter_weight");
    s_file.readDataset<bool>(settings::save::windings, "settings/save/windings");
    s_file.readDataset<bool>(settings::save::correlations, "settings/save/correlations");
    s_file.readDataset<bool>(settings::save::bond_config, "settings/save/bond_config");
    s_file.readDataset<double>(settings::save::annulus_size, "settings/save/annulus_size");
    s_file.readDataset<int>(settings::save::save_interval, "settings/save/save_interval");
}

void io::save_settings(std::string settings_path) {
    h5pp::File s_file(settings_path, h5pp::FileAccess::REPLACE);
    s_file.writeDataset<int>(settings::sim::size_x, "settings/sim/size_x");
    s_file.writeDataset<int>(settings::sim::size_y, "settings/sim/size_y");
    s_file.writeDataset<long long unsigned int>(settings::sim::n_steps, "settings/sim/n_steps");
    s_file.writeDataset<long long unsigned int>(settings::sim::n_therm, "settings/sim/n_therm");
    s_file.writeDataset<double>(settings::sim::single_weight, "settings/sim/single_weight");
    s_file.writeDataset<double>(settings::sim::counter_weight, "settings/sim/counter_weight");
    s_file.writeDataset<bool>(settings::save::windings, "settings/save/windings");
    s_file.writeDataset<bool>(settings::save::correlations, "settings/save/correlations");
    s_file.writeDataset<bool>(settings::save::bond_config, "settings/save/bond_config");
    s_file.writeDataset<double>(settings::save::annulus_size, "settings/save/annulus_size");
    s_file.writeDataset<int>(settings::save::save_interval, "settings/save/save_interval");
}
