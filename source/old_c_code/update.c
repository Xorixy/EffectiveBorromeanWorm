#include "update.h"

//NOTE: This is not the mathematical sign function since it returns -1 for negative numbers and +1 for 0 and positive numbers
//This is convienient for calculating the bond difference
static inline
int charsign(signed char x){
    return 2*(x>>7) + 1;
}

static inline
long randint(pcg32_random_t *rng, long int max) {
    return pcg32_boundedrand_r(rng, max);
    return pcg32_random_r(rng) % max;
}

static inline
double randuniform(pcg32_random_t *rng){
    return ldexp(pcg32_random_r(rng), -32);
}

//Moves the worm head and tail to a random new position
static inline
void relocate_worm(sim_t *sim){
    int new_head = (int) pcg32_boundedrand_r(sim->rng, sim->constants->N);
    sim->worm->worm_head = new_head;
    sim->worm->worm_tail = sim->worm->worm_head;
}

//Makes the forward and backward colors 
static inline
void repaint_worm(sim_t *sim){
    sim->worm->worm_color_forward = (int) pcg32_boundedrand_r(sim->rng, sim->constants->colors);
    sim->worm->worm_color_backward = (sim->worm->worm_color_forward + 
                                      pcg32_boundedrand_r(sim->rng, sim->constants->colors - 1) + 1)%sim->constants->colors;
}

void create_worm(sim_t *sim){
    relocate_worm(sim);
    repaint_worm(sim);
}


//If the half charge in the forward color is less than zero it means we will remove half a charge, otherwise we will add half a charge
//Similarly if the half charge in the backward color is greater than zero we will remove half a charge, else we will add half a charge
//The total change in the number of charges is then the sum of these two.
static inline
int bond_diff(sim_t* sim, int dir){
    int c = sim->constants->colors;
    int d = sim->constants->dim;
    return (charsign(sim->state->bonds[2*c*d*sim->worm->worm_head + c*dir + sim->worm->worm_color_forward]) + 
           charsign(-sim->state->bonds[2*c*d*sim->worm->worm_head + c*dir + sim->worm->worm_color_backward]))/2;
}

void move_worm(sim_t *sim, int dir1){
    int c = sim->constants->colors;
    int d = sim->constants->dim;
    
    //Old head
    long int ind1 = sim->worm->worm_head;
    //New head
    long int ind2 = sim->constants->neighbours[2*d*sim->worm->worm_head + dir1];
    //From the point of view of the new head, the bond is going in the opposite direction
    int dir2 = (dir1 + d)%(2*d);
    
    int bdiff = bond_diff(sim, dir1);

    //Update the total number of bonds in the state as well as the local charge count.
    sim->state->n_bonds += bdiff;
    sim->state->bond_counts[2*d*ind1 + dir1] += bdiff;
    sim->state->bond_counts[2*d*ind2 + dir2] += bdiff;
    
    //Index 1 is the old head, index 2 the new head. The half bond from 1 -> 2 will
    //therefore change with +1 for the forward color and -1 for the backward color.
    //The half bond from index2 to index1 will change in the opposite way.
    sim->state->bonds[2*c*d*ind1 + c*dir1 + sim->worm->worm_color_forward] += 1;
    sim->state->bonds[2*c*d*ind1 + c*dir1 + sim->worm->worm_color_backward] -= 1;
    sim->state->bonds[2*c*d*ind2 + c*dir2 + sim->worm->worm_color_forward] -= 1;
    sim->state->bonds[2*c*d*ind2 + c*dir2 + sim->worm->worm_color_backward] += 1;

    //Winding numbers are stored for each dimension.
    //The directions d and (d + dim) % (2*dim) correspond to
    //movement along the same axis in opposite directions
    //We define the directions 0, 1, ... dim - 1 to be negative directions
    //and dim, dim + 1, ... 2*dim - 1 to be positive directions.
    //Depending on this we either increase or decrease the winding numbers
    //of the forward and backward colors
    if (!sim->double_bond_winding) {
        sim->state->n_wind[c*(dir1%d) + sim->worm->worm_color_forward] += 2*(dir1/d) - 1;
        sim->state->n_wind[c*(dir1%d) + sim->worm->worm_color_backward] += 2*(dir2/d) - 1;
    } else {
        //If we count the windings not in individual colors, but in pair of colors, the situation will be slightly different.
        //For 2 and 3 dimensions, we can uniquely represent a bond pair by simple ading the forward and backwards colors, giving the
        //three possible bonds (0,1) -> 1, (0,2) -> 2, (1,2) -> 3.
        //Since we are working with 0 indexed arrays we also remove one from this value.
        int dirval = 2*(dir1/d) - 1;
        int bondval = (sim->worm->worm_color_forward - sim->worm->worm_color_backward)/abs(sim->worm->worm_color_forward - sim->worm->worm_color_backward);
        sim->state->n_wind[c*(dir1%d) + sim->worm->worm_color_forward + sim->worm->worm_color_backward - 1] += dirval*bondval;
    }

    sim->worm->worm_head = sim->constants->neighbours[2*sim->constants->dim*sim->worm->worm_head + dir1];
}

void update_sim(sim_t *sim){
    if (sim->worm->worm_head == sim->worm->worm_tail){
        if (sim->worm->p_position > randuniform(sim->rng)){
            relocate_worm(sim);
        }
        if (sim->worm->p_color > randuniform(sim->rng)){
            repaint_worm(sim);
        }
    }

    int d = sim->constants->dim;
    int direction = randint(sim->rng, 2*d);
    //This is ONLY for watching the worm yourself. Needs small system size to be able to see all at once.
    /*
    int dr;
    print_bonds2D(sim);
    scanf("%d", &dr);
    printf("You entered %d\n", dr);
    //if ((dr >= 0) && (dr < 2*d)) direction = dr;
    */

    if (
        !(sim->state->bond_counts[2*d*sim->worm->worm_head + direction] + bond_diff(sim, direction) > sim->constants->max_bonds) &&
        ((bond_diff(sim, direction) <= 0) ||
        (sim->constants->bond_weights[sim->state->bond_counts[2*d*sim->worm->worm_head + direction]] > randuniform(sim->rng))))
    {
        move_worm(sim, direction);
    }
    if (!sim->thermalizing) {
        if (sim->save_flags->save_G) {
            save_G(sim);
        }
        if (sim->save_flags->save_annulus) {
            save_annulus(sim);
        }
        if (sim->worm->worm_head == sim->worm->worm_tail) {
            save_z_data(sim);
        }
    }
}




