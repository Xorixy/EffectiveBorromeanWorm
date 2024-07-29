#include "../include/settings.h"
#include "../include/cli.h"
#include "../include/io.h"
#include <fmt/core.h>

int main(int argc, char * argv[]) {
    cli::parse(argc, argv);
    io::test();
}
