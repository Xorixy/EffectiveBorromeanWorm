#include "simulation.h"
#include "types.h"
#include <stdio.h>
#include <string.h>
#include <getopt.h>
#include <time.h>
#include <stdbool.h>

#define MAX_64 4611686018427387904





int main(int argc, char * argv[]){
    long long unsigned int n_iter_therm = 10;
    long long unsigned int n_iter = 10;
    int sizex = -1;
    int sizey = -1;
    int sizez = -1;
    int sizew = -1;
    int dim = 2;
    double K = 0.5;
    int size = 5;
    int colors = 3;
    char *filename = NULL;
    int max_bonds = 1;
    int weight_function = 0;
    int save_flag = 0;
    unsigned long long initstate = 0;
    unsigned long long initseq = 0;
    bool ist = false;
    bool isq = false;
    bool save_annulus = false;
    bool save_G = false;
    bool save_windings = false;
    bool save_bonds = false;
    bool save_bond_number = false;
    double relative_thickness = 0.0;
    int save_interval = 0;
    bool save_time_series = false;
    bool double_bond_winding = false;

    int option;
    while((option = getopt(argc, argv, "n:t:k:s:x:y:z:w:c:f:d:m:r:q:a:bvugli:")) != -1){ //get option from the getopt() method
		switch(option){
            case 'n':
                sscanf(optarg, "%llu", &n_iter);
                break;
            case 't':
                sscanf(optarg, "%llu", &n_iter_therm);
                break;
            case 'k':
                sscanf(optarg, "%lf", &K);
                break;
            case 's':
                sscanf(optarg, "%d", &size);
                break;
            case 'x':
                sscanf(optarg, "%d", &sizex);
                break;
            case 'y':
                sscanf(optarg, "%d", &sizey);
                break;
            case 'z':
                sscanf(optarg, "%d", &sizez);
                break;
            case 'w':
                sscanf(optarg, "%d", &sizew);
                break;
            case 'c':
                sscanf(optarg, "%d", &colors);
                break;
            case 'd':
                sscanf(optarg, "%d", &dim);
                break;
            case 'm':
                sscanf(optarg, "%d", &max_bonds);
                break;
            case 'b':
                save_bond_number = true;
                break;
            case 'v':
                save_windings = true;
                break;
            case 'r':
                sscanf(optarg, "%llu", &initstate);
		        ist = true;
                break;
            case 'q':
                sscanf(optarg, "%llu", &initseq);
		        isq = true;
                break;
            case 'f':
				filename = optarg;
				break;
            case 'a':
                sscanf(optarg, "%lf", &relative_thickness);
                save_annulus = true;
                break;
            case 'g':
                save_G = true;
                break;
            case 'l':
                save_bonds = true;
                break;
            case 'u':
                double_bond_winding = true;
                break;
            case 'i':
                sscanf(optarg, "%d", &save_interval);
                if (save_interval <= 0) {
                    printf("Warning: Save interval must be at least 1 to make a time series. Ignoring command.");
                } else {
                    save_time_series = true;
                }
                break;
            case '?': //used for some unknown options
				printf("unknown option: %c\n", optopt);
				break;
        }
	}
    
    if (filename == NULL) {
        printf("Error: no filename specified\n");
        return 1;
    }
    if (dim < 2 || dim > 4) {
        printf("Error: dim must be either 2, 3, or 4.");
        return 1;
    }

    if (sizex == -1) {
        sizex = size;
    }
    if (sizey == -1) {
        sizey = size;
    }
    if (sizez == -1) {
        sizez = size;
    }
    if (sizew == -1) {
        sizew = size;
    }
    if (dim < 3) {
        sizez = 1;
    }
    if (dim < 4) {
        sizew = 1;
    }
    if (max_bonds < 1) {
        printf("Error: Max_bonds must be at least 1");
        return 1;
    }

    if (save_flag < 0 || save_flag > 2) {
        printf("Warning: Save flag must be either 0, 1, or 2, save flag passed is %d. Switching to default flag (0).\n", save_flag);
        save_flag = 0;
    }

    if (double_bond_winding && dim > 3) {
        printf("Error, double bond winding is only implemented for d < 4. Turning the flag off.\n");
        double_bond_winding = false;
    }
    
    sim_params_t params = {
                            sizex,
                            sizey,
                            sizez,
                            sizew,
                            K,
                            colors,
                            0.5,
                            1,
                            dim,
                            max_bonds,
                            0,
                            relative_thickness,
                            save_time_series,
                            save_G,
                            save_windings,
                            save_bonds,
                            save_annulus,
                            save_bond_number,
                            n_iter,
                            n_iter_therm,
                            save_interval,
                            double_bond_winding

    };

    time_t begin = time(NULL); 
    switch (worm_algorithm(&params, filename, (ist && isq), (__uint128_t) initstate, (__uint128_t) initseq)) {
        case 1: 
            printf("Error: could not read /dev/random");
            break;
        case 2:
            printf("Error: size_x and size_y must be the same for the ring calculation!\n");
            break;
        case 3:
            printf("Error: can't save bond or correlation function as time series. Consider removing these flags.");
            break;
        case 4:
            printf("Error: Time series interval must be at least 1.");
            break;
    };
    time_t end = time(NULL);
    double time_spent = (double)(end - begin) / 1;
    printf("Total CPU time usage was %lf\n", time_spent);
    
    

    return 0;
}