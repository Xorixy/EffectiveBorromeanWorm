#include "init.h"
#include "types.h"
#include <stdlib.h>


static inline
long int point_id_4D(int x, int y, int z, int w, int ny, int nz, int nw){
    return w + z*nw + y*nz*nw + x*ny*nz*nw;
}

static inline
long int point_id_3D(int x, int y, int z, int ny, int nz){
    return z + y*nz + x*ny*nz;
}

static inline
long int point_id_2D(int x, int y, int ny){
    return y + x*ny;
}

//Initiates the geometric arrays (neighbours and positions)
void init_geometric_arrays(long int *neighbours, long int* positions, int nx, int ny, int nz, int nw, int d){
    if (d == 4){
        for (int ix = 0 ; ix < nx ; ix++){
            for (int iy = 0 ; iy < ny ; iy++){
                for (int iz = 0 ; iz < nz ; iz++){
                    for (int iw = 0 ; iw < nw ; iw++){
                        long int pid = point_id_4D(ix, iy, iz, iw, ny, nz, nw);
                        positions[4*pid + 0] = ix;
                        positions[4*pid + 1] = iy;
                        positions[4*pid + 2] = iz;
                        positions[4*pid + 3] = iw;
                        neighbours[8*pid + 0] = point_id_4D((ix + 1) % nx, iy, iz, iw, ny, nz, nw);
                        neighbours[8*pid + 1] = point_id_4D(ix, (iy + 1) % ny, iz, iw, ny, nz, nw);
                        neighbours[8*pid + 2] = point_id_4D(ix, iy, (iz + 1) % nz, iw, ny, nz, nw);
                        neighbours[8*pid + 3] = point_id_4D(ix, iy, iz, (iw + 1) % nw, ny, nz, nw);
                        neighbours[8*pid + 4] = point_id_4D((ix - 1 + nz) % nx, iy, iz, iw, ny, nz, nw);
                        neighbours[8*pid + 5] = point_id_4D(ix, (iy - 1 + ny) % ny, iz, iw, ny, nz, nw);
                        neighbours[8*pid + 6] = point_id_4D(ix, iy, (iz -1 + nz) % nz, iw, ny, nz, nw);
                        neighbours[8*pid + 7] = point_id_4D(ix, iy, iz, (iw - 1 + nw) % nw, ny, nz, nw);
                    }
                }
            }
        }
    } else if (d == 3){
        for (int ix = 0 ; ix < nx ; ix++){
            for (int iy = 0 ; iy < ny ; iy++){
                for (int iz = 0 ; iz < nz ; iz++){
                    long int pid = point_id_3D(ix, iy, iz, ny, nz);
                    positions[3*pid + 0] = ix;
                    positions[3*pid + 1] = iy;
                    positions[3*pid + 2] = iz;
                    neighbours[6*pid + 0] = point_id_3D((ix + 1) % nx, iy, iz, ny, nz);
                    neighbours[6*pid + 1] = point_id_3D(ix, (iy + 1) % ny, iz, ny, nz);
                    neighbours[6*pid + 2] = point_id_3D(ix, iy, (iz + 1) % nz, ny, nz);
                    neighbours[6*pid + 3] = point_id_3D((ix - 1 + nx) % nx, iy, iz, ny, nz);
                    neighbours[6*pid + 4] = point_id_3D(ix, (iy - 1 + ny) % ny, iz, ny, nz);
                    neighbours[6*pid + 5] = point_id_3D(ix, iy, (iz - 1 + nz) % nz, ny, nz);
                }
            }
        }
    } else if (d == 2) {
        for (int ix = 0 ; ix < nx ; ix++){
            for (int iy = 0 ; iy < ny ; iy++){
                long int pid = point_id_2D(ix, iy, ny);
                positions[2*pid + 0] = ix;
                positions[2*pid + 1] = iy;
                neighbours[4*pid + 0] = point_id_2D((ix + 1) % nx, iy, ny);
                neighbours[4*pid + 1] = point_id_2D(ix, (iy + 1) % ny, ny);
                neighbours[4*pid + 2] = point_id_2D((ix - 1 + nx) % nx, iy, ny);
                neighbours[4*pid + 3] = point_id_2D(ix, (iy - 1 + ny) % ny, ny);
            }
        }
    }
}

//Only works for 2D
int init_annulus_array(char* annulus, int nx, int ny, double relative_thickness) {
    if (nx != ny) {
        return -1;
    }
    long int size = 0;
    double l_max = ((double) nx)/2;
    double l_min = l_max*(1.0 - relative_thickness);

    for (int ix = 0 ; ix < nx ; ix++){
        for (int iy = 0 ; iy < ny ; iy++){
            int px, py;
            if (ix <= nx/2) {
                px = ix;
            } else {
                px = nx - ix;
            }
            if (iy <= ny/2) {
                py = iy;
            } else {
                py = ny - iy;
            }
            int r_sqr = px*px + py*py;
            if ((r_sqr <= l_max*l_max) && (r_sqr >= l_min*l_min)) {
                annulus[point_id_2D(ix, iy, ny)] = 1;
                size++;
            } else {
                annulus[point_id_2D(ix, iy, ny)] = 0;
            }
        }
    }
    printf("Annulus percentage is %lf, continuous limit should be %lf.\n", ((double) size)/(nx*ny), 3.1415926*(l_max*l_max - l_min*l_min)/(nx*ny));
    return size;
}

int gaussian_weight(int bond){
    return bond*bond;
}

int linear_weight(int bond){
    return bond;
}

/*We assume that the energy cost of a bond with charge n is U*f(n), with n < m => f(n) >= f(m).
  Furthermore we assume that f(1) = 1, f(0) = 0.
  Given the control parameter K=e^(-U) = e^(-Uf(1)) = P(1),
  the probability of a bond with charge n is e^(-Uf(n)) = K^f(n) = P(n).
  Since we are at most changing 1 bond charge at a time, we only care about these transitions.
  Since we assume monotonically decreasing f(n) the monte carlo acceptance rate for transitions
  that change the total charge by -1 or 0 are accepted with probability 1.
  Transitions that add a charge are accepted with a probability P(n+1)/P(n) = K^{f(n+1)-f(n)}
  In the bond weight array we store exactly these numbers, i.e arr[n] = P(n+1)/P(n)
  */
void init_bond_weights(double *weights, double K, int max_bonds, int (*bond_weight_function)(int)){
    for (int b = 0 ; b < max_bonds ; b++){
        weights[b] = pow(K, bond_weight_function(b+1)-bond_weight_function(b));
    }
}


int init_sim(sim_t *sim, sim_params_t *params)
{   
    if (params->save_annulus && (params->save_G || params->save_bonds)) {
        return 2;
    }

    sim->double_bond_winding = params->double_bond_winding;

    long int N = params->nx*params->ny*params->nz*params->nw;

    sim->save_interval = params->save_interval;
    sim->n_iter_therm = params->n_iter_therm;
    if (params->save_time_series) {
        if (params->save_interval < 1) {
            return 3;
        }
        if (params->n_iter % params->save_interval == 0) {
            sim->n_iter = params->n_iter;
        } else {
            sim->n_iter = params->save_interval*(1 + params->n_iter/params->save_interval);
        }

        save_t *time_series = malloc(sizeof(save_t)*sim->n_iter/sim->save_interval);
        for (int i = 0 ; i < sim->n_iter/sim->save_interval ; i++) {
            save_t time_slice;
            if (params->save_windings) {
                __int128_t *windings_sqr = calloc(params->dim*params->colors+1, sizeof(__int128_t));
                time_slice.windings_sqr = windings_sqr;
            }
            if (params->save_bond_number) {
                __int128_t *sum_bonds = calloc(3, sizeof(__int128_t));
                time_slice.sum_bonds = sum_bonds;
            }
            time_slice.annulus_sum = 0;
            time_slice.G0 = 0;

            time_series[i] = time_slice;
        }
        sim->save = time_series;
        sim->time_series = time_series;
    } else {
        save_t *save = malloc(sizeof(save_t));
        sim->n_iter = params->n_iter;
        sim->save_interval = 0;
        long long int *G;
        if (params->save_G) G = calloc(N, sizeof(long long int));
        __int128_t *windings_sqr = calloc(params->dim*params->colors+1, sizeof(__int128_t));;
        __int128_t *sum_bonds = calloc(3, sizeof(__int128_t));;
        save->sum_bonds = sum_bonds;
        save->windings_sqr = windings_sqr;
        save->G = G;

        sim->save = save;
        sim->time_series = save;
        sim->save->G0 = 0;
    }
    
    save_flags_t *sf = malloc(sizeof(save_flags_t));

    sf->save_time_series = params->save_time_series;
    sf->save_G = params->save_G;
    sf->save_windings = params->save_windings;
    sf->save_bonds = params->save_bonds;
    sf->save_annulus = params->save_annulus;
    sf->save_bond_number = params->save_bond_number;

    sim->save_flags = sf;

    
    long int *neighbours = malloc(sizeof(long int)*N*2*params->dim);
    long int *positions = malloc(sizeof(long int)*N*params->dim);
    char *annulus = malloc(sizeof(char)*params->nx*params->ny);
    
    signed char *bonds = calloc(N*2*params->dim*params->colors, sizeof(signed char));
    signed char *bond_counts = calloc(N*2*params->dim, sizeof(signed char));
    //print_bonds(bonds, N);
    __int128_t *windings_sqr = calloc(params->dim*params->colors+1, sizeof(__int128_t));
    __int128_t *sum_bonds = calloc(3, sizeof(__int128_t));
    long long int *n_wind = calloc(params->dim*params->colors, sizeof(long long int));

    init_geometric_arrays(neighbours, positions, params->nx, params->ny, params->nz, params->nw, params->dim);
    double *bond_weights = malloc(params->max_bonds*sizeof(double));

    init_bond_weights(bond_weights, params->K, params->max_bonds, &gaussian_weight);

    /*
    if (weight_function == 0) {
        initialize_bond_weights(bond_weights, K, max_bonds, &linear_weight);
    } else {
        initialize_bond_weights(bond_weights, K, max_bonds, &gaussian_weight);
    }
    */
    long int annulus_size = 0;
    if (params->save_annulus) {
        annulus_size = init_annulus_array(annulus, params->nx, params->ny, params->relative_thickness);
        if (annulus_size == -1) {
            return 1;
        }
    }
    
    constants_t* cs = malloc(sizeof(constants_t));
    cs->nx = params->nx;
    cs->ny = params->ny;
    cs->nz = params->nz;
    cs->nw = params->nw;
    cs->N = N;
    cs->K = params->K;
    cs->neighbours = neighbours;
    cs->positions = positions;
    cs->annulus = annulus;
    cs->annulus_thickness = params->relative_thickness;
    cs->annulus_size = annulus_size;
    cs->dim = params->dim;
    cs->colors = params->colors;
    cs->max_bonds = params->max_bonds,
    cs->bond_weights = bond_weights;

    sim->constants = cs;


    worm_t *worm = malloc(sizeof(worm_t));
    worm->p_position = params->p0;
    worm->p_color = params->pc;
    sim->worm = worm;
    
    state_t *state = malloc(sizeof(state_t));
    state->bonds = bonds;
    state->bond_counts = bond_counts;
    state->n_bonds = 0;
    state->n_wind = n_wind;

    sim->state = state;

    return 0;
}