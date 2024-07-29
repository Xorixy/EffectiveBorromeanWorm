#include "save.h"

void save_z_data(sim_t *sim) {
    if (sim->save_flags->save_windings) {
        save_windings_sqr(sim);
    }
    if (sim->save_flags->save_bonds) {
        save_number_of_bonds(sim);
    }
    if (sim->save_flags->save_annulus) {
        save_G0(sim);
    }
}

void save_G(sim_t *sim) {
    long int head = sim->worm->worm_head;
    long int tail = sim->worm->worm_tail;
    constants_t* consts = sim->constants;
    if (consts->dim == 4){
        int deltax = (consts->positions[4*head + 0] - consts->positions[4*tail + 0] + consts->nx + consts->nx/2)%consts->nx;
        int deltay = (consts->positions[4*head + 1] - consts->positions[4*tail + 1] + consts->ny + consts->ny/2)%consts->ny;
        int deltaz = (consts->positions[4*head + 2] - consts->positions[4*tail + 2] + consts->nz + consts->nz/2)%consts->nz;
        int deltaw = (consts->positions[4*head + 3] - consts->positions[4*tail + 3] + consts->nw + consts->nw/2)%consts->nw;
        sim->save->G[ consts->nw*consts->nz*consts->ny*deltax + consts->nw*consts->nz*deltay + consts->nw*deltaz + deltaw ] += 1;
    } else if (consts->dim == 3){
        int deltax = (consts->positions[3*head + 0] - consts->positions[3*tail + 0] + consts->nx + consts->nx/2)%consts->nx;
        int deltay = (consts->positions[3*head + 1] - consts->positions[3*tail + 1] + consts->ny + consts->ny/2)%consts->ny;
        int deltaz = (consts->positions[3*head + 2] - consts->positions[3*tail + 2] + consts->nz + consts->nz/2)%consts->nz;
        sim->save->G[ consts->nz*consts->ny*deltax + consts->nz*deltay + deltaz ] += 1;
    } else if (consts->dim == 2) {
        int deltax = (consts->positions[2*head + 0] - consts->positions[2*tail + 0] + consts->nx + consts->nx/2)%consts->nx;
        int deltay = (consts->positions[2*head + 1] - consts->positions[2*tail + 1] + consts->ny + consts->ny/2)%consts->ny;
        sim->save->G[ consts->ny*deltax + deltay ] += 1;
    }
}

void save_windings_sqr(sim_t *sim) {
    for (int iw = 0 ; iw < sim->constants->dim*sim->constants->colors ; iw++) {
            sim->save->windings_sqr[iw] += sim->state->n_wind[iw]*sim->state->n_wind[iw];
        }
    sim->save->windings_sqr[sim->constants->dim*sim->constants->colors] += 1;
}

void save_number_of_bonds(sim_t *sim) {
    sim->save->sum_bonds[0] += sim->state->n_bonds;
    sim->save->sum_bonds[1] += sim->state->n_bonds*sim->state->n_bonds;
    sim->save->sum_bonds[2] += 1;
}

static inline
long int point_id_2D(int x, int y, int ny){
    return y + x*ny;
}

void save_annulus(sim_t *sim) {
    long int head = sim->worm->worm_head;
    long int tail = sim->worm->worm_tail;
    constants_t* consts = sim->constants;
    int deltax = (consts->positions[2*head + 0] - consts->positions[2*tail + 0] + consts->nx)%consts->nx;
    int deltay = (consts->positions[2*head + 1] - consts->positions[2*tail + 1] + consts->ny)%consts->ny;
    sim->save->annulus_sum += sim->constants->annulus[point_id_2D(deltax, deltay, sim->constants->nx)];
}

void save_G0(sim_t *sim) {
    sim->save->G0 += 1;
}