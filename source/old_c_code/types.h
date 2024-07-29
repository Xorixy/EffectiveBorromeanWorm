#pragma once
#include "pcg_basic.h"
#include <stdbool.h>

//Type that stores save flags
typedef struct {
    bool save_time_series;
    bool save_G;
    bool save_windings;
    bool save_bonds;
    bool save_annulus;
    bool save_bond_number;
} save_flags_t;

//Type that stores the current bond configuration + auxilliary data
typedef struct {
    signed char *bonds;
    signed char *bond_counts;
    long long int n_bonds;
    long long int *n_wind;
} state_t;

//Type that stores fixed data regarding our system
typedef struct {
    int nx;
    int ny;
    int nz;
    int nw;
    long int N;
    double K;
	long int *neighbours;
	long int *positions;
    char* annulus;
    double annulus_thickness;
    long int annulus_size;
    int dim;
    int colors;
    int max_bonds;
    double *bond_weights;
} constants_t;

//Type that stores the information regarding a single worm
typedef struct {
    long int worm_head;
    long int worm_tail;
    double p_position;
    double p_color;
    int worm_color_forward;
    int worm_color_backward;
} worm_t;

//Type that stores 
typedef struct {   
	long long int *G;
	__int128_t *windings_sqr;
	__int128_t *sum_bonds;
    long long int G0;
    long long int annulus_sum;
} save_t;

typedef struct {
    constants_t *constants;
    worm_t *worm;
    state_t *state;
    save_flags_t *save_flags;
    save_t *save;
    save_t *time_series;
    long long unsigned int n_iter;
    long long unsigned int n_iter_therm;
    bool thermalizing;
    int save_interval;
    pcg32_random_t *rng;
    bool double_bond_winding;
} sim_t;

typedef struct {
    int nx;
    int ny; 
    int nz; 
    int nw;
    double K; 
    int colors; 
    double p0; 
    double pc; 
    int dim;
    int max_bonds;
    int weight_function;
    double relative_thickness;
    bool save_time_series;
    bool save_G;
    bool save_windings;
    bool save_bonds;
    bool save_annulus;
    bool save_bond_number;
    long long unsigned int n_iter;
    long long unsigned int n_iter_therm;
    int save_interval;
    bool double_bond_winding;
} sim_params_t;





