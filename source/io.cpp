#include "../include/io.h"

void io::load_settings() {
    const h5pp::File s_file = try_to_open_file(settings::io::settings_path, true);
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

void io::save_settings() {
    h5pp::File s_file = try_to_open_file(settings::io::settings_path, false);
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

void io::save_base() {
    io::outfile.writeDataset<long long unsigned int>(ULLONG_MAX, "constants/base_minus_one");
}

void io::save_annulus_size(const int annulus_size) {
    io::outfile.writeDataset(annulus_size, "constants/annulus_area");
}


void io::save_slice(const sim::SaveStruct& save, const std::string& prefix) {
    io::outfile.writeDataset<long long unsigned int>(save.windings_difference_squared_x.big, prefix + "/windings_diff_squared_x/big");
    io::outfile.writeDataset<long long unsigned int>(save.windings_difference_squared_x.small, prefix + "/windings_diff_squared_x/small");
    io::outfile.writeDataset<long long unsigned int>(save.windings_difference_squared_y.big, prefix + "/windings_diff_squared_y/big");
    io::outfile.writeDataset<long long unsigned int>(save.windings_difference_squared_y.small, prefix + "/windings_diff_squared_y/small");
    io::outfile.writeDataset<long long unsigned int>(save.windings_sum_squared_x.big, prefix + "/windings_sum_squared_x/big");
    io::outfile.writeDataset<long long unsigned int>(save.windings_sum_squared_x.small, prefix + "/windings_sum_squared_x/small");
    io::outfile.writeDataset<long long unsigned int>(save.windings_sum_squared_y.big, prefix + "/windings_sum_squared_y/big");
    io::outfile.writeDataset<long long unsigned int>(save.windings_sum_squared_y.small, prefix + "/windings_sum_squared_y/small");
    io::outfile.writeDataset<long long unsigned int>(save.partition_function, prefix + "/partition_function");
    io::outfile.writeDataset<long long unsigned int>(save.annulus_sum, prefix + "/annulus_sum");
    io::outfile.writeDataset<std::array<long long int, 4>>(save.windings, prefix + "/windings");
}

void io::save_time_series(const sim::TimeSeriesStruct& save, const std::string& prefix) {
    io::save_uint_vec(save.windings_difference_squared_x, prefix + "/windings_diff_squared_x");
    io::save_uint_vec(save.windings_difference_squared_y, prefix + "/windings_diff_squared_y");
    io::save_uint_vec(save.windings_sum_squared_x, prefix + "/windings_sum_squared_x");
    io::save_uint_vec(save.windings_sum_squared_y, prefix + "/windings_sum_squared_y");
    io::outfile.writeDataset<std::vector<std::array<long long int, 4>>>(save.windings, prefix + "/windings");
    io::outfile.writeDataset<std::vector<long long unsigned int>>(save.partition_function, prefix + "/partition_function");
    io::outfile.writeDataset<std::vector<long long unsigned int>>(save.annulus_sum, prefix + "/annulus_sum");
}

h5pp::File io::try_to_open_file(const std::string& filename, bool readonly) {
    int n_tries = 0;
    h5pp::File file;
    while(true) {
        try {
            if (!readonly) {
                if (settings::io::replace_file) file = h5pp::File(filename, h5pp::FileAccess::REPLACE);
                else file = h5pp::File(filename, h5pp::FileAccess::COLLISION_FAIL);
            } else {
                file = h5pp::File(filename, h5pp::FileAccess::READONLY);
            }
            break;
        } catch (std::exception &e) {
            logger::log->info("Failed to open file with error: {}\n", e.what());
            logger::log->info("Waiting 3 seconds and trying again...\n");
            std::this_thread::sleep_for(std::chrono::seconds(3));
            n_tries++;
            if (n_tries >= 10) throw e;
        }
    }
    return file;
}

void io::save_uint_vec(const simple_uint128_vec& vec, const std::string &path) {
    io::outfile.writeDataset<std::vector<unsigned long long int>>(vec.bigs  , path + "/big");
    io::outfile.writeDataset<std::vector<unsigned long long int>>(vec.smalls, path + "/small");
}

