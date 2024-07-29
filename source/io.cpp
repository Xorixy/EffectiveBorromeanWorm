#include "../include/io.h"


void io::test() {
    std::vector<double> v = {1.0, 2.0, 3.0};    // Define a vector
    h5pp::File file(settings::io::filename, h5pp::FileAccess::READWRITE);    // Create a file
    file.writeDataset(v, "test/myStdVector");        // Write the vector into a new dataset "myStdVector"
    auto rv = file.readDataset<std::vector<double>>("test/myStdVector");
    fmt::print("{}, {}, {}\n", rv.at(0), rv.at(1), rv.at(2));
}

void io::loadSettings(std::string settings_path) {
    h5pp::File s_file(settings_path, h5pp::FileAccess::READONLY);

}

