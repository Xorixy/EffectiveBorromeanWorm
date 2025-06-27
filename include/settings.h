#pragma once
#include <string>

namespace settings {

    namespace random {
        inline auto seed         = 0ul;
    }

    namespace worm {
        inline double p_move = 1.0;
        inline double p_type = 1.0;
        inline double single_to_counter_ratio = 1.0;
        inline double counter_to_single_ratio = 1.0;
    }

    namespace sim {
        //System sizes
        inline int size_x = 300;
        inline int size_y = 300;

        //Number of simulation/thermalization steps
        inline long long unsigned int n_steps = 1000000000;
        inline long long unsigned int n_therm = 100000000;

        //Weight of single/counterflow bond
        inline double single_weight = 0.4716;
        inline double counter_weight = 0.4716;
    }

    namespace save {
        //Winding numbers
        inline bool windings = true;


        //Correlations are saved averaged over an annulus
        //Outer radius of annulus is always system size/2
        //Inner radius equals outer radius * ( 1 - annulus_size)
        inline bool correlations = false;
        inline double annulus_size = 0.1;

        //Whether to save the simulation as a time series,
        //and at what step interval the time series should be saved
        inline bool time_series = false;
        inline int save_interval = 1000;

        inline bool save_therm = false;
    }

    namespace io {
        inline std::string filename = "simulation.h5";
        inline std::string settings_path = "settings.h5";
        //Probably want to set it to false in the final code.
        inline bool replace_file = true;
    }

    namespace log {
        inline long level = 0l;
    }
}