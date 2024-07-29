#pragma once
#include <string>

namespace settings {

    namespace random {
        inline auto seed         = 0ul;
    }

    namespace worm {
        inline double p_move = 1.0;
        inline double p_type = 1.0;
    }

    namespace sim {
        //System sizes
        inline int size_x = 5;
        inline int size_y = 5;

        //Number of simulation/thermalization steps
        inline long long unsigned int n_steps = 10;
        inline long long unsigned int n_therm = 10;

        //Weight of single/counterflow bond
        inline double single_weight = 0.5;
        inline double counter_weight = 0.5;
    }

    namespace save {
        //Winding numbers
        inline bool windings = false;

        //Correlations
        //Correlations are saved averaged over an annulus
        //Outer radius of annulus is always system size/2
        //Inner radius equals outer radius * ( 1 - annulus_size)
        inline bool correlations = false;
        inline double annulus_size = 0.1;

        //Whether to save the simulation as a time series,
        //and at what step interval the time series should be saved
        inline bool time_series = false;
        inline int save_interval = 10000;

        //Whether to save the final bond configuration
        inline bool bond_config = false;
    }

    namespace io {
        inline std::string filename = "simulation.h5";
    }

    namespace log {
        inline long level = 0l;
    }
}