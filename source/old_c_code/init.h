#pragma once
#include "types.h"
#include <stdbool.h>
#include <stdlib.h>
#include <math.h>

#include <stdio.h>

void init_geometric_arrays(long int *neighbours, long int* positions, int nx, int ny, int nz, int nw, int d);
int init_annulus_array(char* annulus, int nx, int ny, double relative_thickness);
int init_sim(sim_t *sim, sim_params_t *params);