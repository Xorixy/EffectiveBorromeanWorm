#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "types.h"

#define BASE 4611686018427387904

int write_simulation(const char *filename, const sim_t *sim);

int write_g(FILE *file, const long long int *G, const long int N);
int write_winding(FILE *file, const __int128_t *windings, const int dim, const int colors);
int write_split(FILE *file, const __int128_t num, __int128_t base);
int write_params(FILE *file, const int nx, const int ny, const int nz, const int nw, 
                 const double K, const int dim, const int colors, const int max_bonds, 
                 const long long unsigned int n_iter, const int save_interval, const long int annulus_size);
int write_bonds(FILE *file, const signed char *bonds, const long int N, const int dim, const int colors);
int write_sum_bonds(FILE *file, const __int128_t *sum_bonds);
int write_annulus(FILE *file, const long long int *annulus_sum, const long long int *G0);