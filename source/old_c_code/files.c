#include "files.h"
#include <stdio.h>


int write_simulation(const char *filebase, const sim_t *sim)
{   
    constants_t *consts = sim->constants;
    {
        FILE *file;
        char *append = "_params.bin";
        char filename[strlen(filebase) + strlen(append) + 1];
        strcat(strcpy(filename, filebase), append);
        file = fopen(filename, "w" );
        write_params(file, consts->nx, consts->ny, consts->nz, consts->nw, 
                        consts->K, consts->dim, consts->colors, consts->max_bonds, 
                        sim->n_iter, sim->save_interval, consts->annulus_size);
        fclose(file);
    }
    if (sim->save_flags->save_G) {
        FILE *file;
        char *append = "_g.bin";
        char filename[strlen(filebase) + strlen(append) + 1];
        strcat(strcpy(filename, filebase), append);
        file = fopen(filename, "w" );
        write_g(file, sim->save->G, consts->N);
        fclose(file);
    }
    if (sim->save_flags->save_bonds)  {
        FILE *file;
        char *append = "_bonds.bin";
        char filename[strlen(filebase) + strlen(append) + 1];
        strcat(strcpy(filename, filebase), append);
        file = fopen(filename, "w" );
        write_bonds(file, sim->state->bonds, consts->N, consts->dim, consts->colors);
        fclose(file);
    }
    if (sim->save_flags->save_windings) {
        FILE *file;
        char *append = "_windings.bin";
        char filename[strlen(filebase) + strlen(append) + 1];
        strcat(strcpy(filename, filebase), append);
        file = fopen(filename, "w" );
        if (sim->save_flags->save_time_series == false) {
            write_winding(file, sim->save->windings_sqr, consts->dim, consts->colors);
        } else {
            save_t *time_slice = sim->time_series;
            for (int i = 0 ; i < sim->n_iter/sim->save_interval ; i++) {
                write_winding(file, time_slice->windings_sqr, consts->dim, consts->colors);
                time_slice++;
            }
        }
        fclose(file);
    }
    if (sim->save_flags->save_bond_number) {
        FILE *file;
        char *append = "_sum_bonds.bin";
        char filename[strlen(filebase) + strlen(append) + 1];
        strcat(strcpy(filename, filebase), append);
        file = fopen(filename, "w" );
        if (sim->save_flags->save_time_series == false) {
            write_sum_bonds(file, sim->save->sum_bonds);
        } else {
            save_t *time_slice = sim->time_series;
            for (int i = 0 ; i < sim->n_iter/sim->save_interval ; i++) {
                write_sum_bonds(file, time_slice->sum_bonds);
                time_slice++;
            }
        }
        fclose(file);
    }
    if (sim->save_flags->save_annulus) {
        FILE *file;
        char *append = "_annulus.bin";
        char filename[strlen(filebase) + strlen(append) + 1];
        strcat(strcpy(filename, filebase), append);
        file = fopen(filename, "w" );
        if (sim->save_flags->save_time_series == false) {
            write_annulus(file, &sim->save->annulus_sum, &sim->save->G0);
        } else {
            save_t *time_slice = sim->time_series;
            for (int i = 0 ; i < sim->n_iter/sim->save_interval ; i++) {
                write_annulus(file, &time_slice->annulus_sum, &time_slice->G0);
                time_slice++;
            }
        }
        fclose(file);
    }
    return 0;
}

int write_params(FILE *file, 
                 const int nx, 
                 const int ny, 
                 const int nz, 
                 const int nw, 
                 const double K, 
                 const int dim, 
                 const int colors, 
                 const int max_bonds,
                 const long long unsigned int n_iter,
                 const int save_interval,
                 const long int annulus_size){
    

    
    fwrite(&nx, sizeof(int), 1, file);
    fwrite(&ny, sizeof(int), 1, file);
    fwrite(&nz, sizeof(int), 1, file);
    fwrite(&nw, sizeof(int), 1, file);
    fwrite(&K, sizeof(double), 1, file);
    fwrite(&dim, sizeof(int), 1, file);
    fwrite(&colors, sizeof(int), 1, file);
    fwrite(&max_bonds, sizeof(int), 1, file);
    fwrite(&n_iter, sizeof(long long unsigned int), 1, file);
    fwrite(&save_interval, sizeof(int), 1, file);
    fwrite(&annulus_size, sizeof(long int), 1, file);

    return 0;
}

int write_g(FILE *file, const long long int *G, const long int N){
    fwrite(G, sizeof(long long int), N, file);
    return 0;
}

int write_bonds(FILE *file, const signed char *bonds, const long int N, const int dim, const int colors){
    fwrite(bonds, sizeof(signed char), 2*dim*colors*N, file);
    return 0;
}

//Winding array should have the form {wind_sqr_x0, wind_sqr_x1, wind_sqr_x2, wind_sqr_y0, ..., wind_sqr_z3, n_winding}
//The saved array will be {base, wind_sqr_x_big, wind_sqr_x_small, wind_sqr_y_big, ..., wind_sqr_z_small, n_winding},
//where wind_sqr_i = (wind_sqr_i0 + wind_sqr_i1 + wind_sqr_i2) for i=x,y,z,
//and base defining how each number is split into two long long ints, 
//for any saved number num, num = big*base + small. 
int write_winding(FILE *file, const __int128_t *windings, const int dim, const int colors){
    __int128_t t_wind;
    for (int id = 0 ; id < dim ; id++){
        t_wind = 0;
        for (int ic = 0 ; ic < colors ; ic++){
            t_wind += windings[colors*id + ic];
        }
        write_split(file, t_wind, BASE);
    }
    long long int n_wind = windings[dim*colors];
    fwrite(&n_wind, sizeof(long long int), 1, file);




    return 0;
}

//Sum of bonds array should have the form {sum_bonds, sum_bonds_sqr, n_sum_bonds}
//The saved array will be {base, sum_bonds_big, sum_bonds_small, sum_bonds_sqr_big, sum_bonds_sqr_small, n_sum_bonds},
//where base defines how each number is split into two long long ints, 
//for any saved number num, num = big*base + small. 
int write_sum_bonds(FILE *file, const __int128_t *sum_bonds){
    write_split(file, sum_bonds[0], BASE);
    write_split(file, sum_bonds[1], BASE);
    long long int n_sum_bonds = sum_bonds[2];
    fwrite(&n_sum_bonds, sizeof(long long int), 1, file);
    
    return 0;
}

int write_split(FILE *file, const __int128_t num, __int128_t base){
    long long int big = num / base;
    long long int small = num % base;
    //printf("big = %llu, small = %llu\n", big, small);
    fwrite(&big, sizeof(long long int), 1, file);
    fwrite(&small, sizeof(long long int), 1, file);

    return 0;
}

int write_annulus(FILE *file, const long long int *annulus_sum, const long long int *G0) {
    fwrite(annulus_sum, sizeof(long long int), 1, file);
    fwrite(G0, sizeof(long long int), 1, file);

    return 0;
}