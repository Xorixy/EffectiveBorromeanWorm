#include "simulation.h"
#include "print_debug.h"



static inline
long randint(pcg32_random_t *rng, long int max) {
    return pcg32_boundedrand_r(rng, max);
    return pcg32_random_r(rng) % max;
}

static inline
double randuniform(pcg32_random_t *rng){
    return ldexp(pcg32_random_r(rng), -32);
}


//static inline
int seed_random(pcg32_random_t *rng){
        FILE *f;
        f = fopen("/dev/random", "r");
        __uint128_t initstate;
        __uint128_t initseq;
        if (fread(&initstate, sizeof(__uint64_t), 1, f) != 1){
            return 1;
        }
        if (fread(&initseq, sizeof(__uint64_t), 1, f) != 1){
            return 1;
        }
        fclose(f);
        pcg32_srandom_r(rng, initstate, initseq);
        return 0;
}

int worm_algorithm( sim_params_t *params,
                    char *filename,
		            bool seeded,
		            __uint128_t initstate,
		            __uint128_t initseq)
{
    sim_t sim;
    pcg32_random_t rng;
    printf("Seeding rng...\n");
    time_t begin = time(NULL);
    if (seeded) {
        __uint128_t initstate;
        __uint128_t initseq;
        pcg32_srandom_r(&rng, initstate, initseq);
	    printf("PRESEEDED\n");
    } else if (seed_random(&rng) == 1) {
        return 1;
    }
    
    time_t end = time(NULL);
    double time_spent = (double)(end - begin) / 1;
    printf("Rng seeded (time elapsed = %lf)\n", time_spent);

    sim.rng = &rng;
    
    printf("Initializing state...\n");
    begin = time(NULL);
    int err = init_sim(&sim, params);
    if (err != 0) {
        return err + 1;
    }
    end = time(NULL);
    time_spent = (double)(end - begin) / 1;
    printf("State initialized (time elapsed = %lf)\n", time_spent);
    run_sim(&sim);

    if (filename != NULL) {
	printf("Saving files...\n");
        begin = time(NULL);
        write_simulation(filename, &sim);
        end = time(NULL);
        time_spent = (double)(end - begin) / 1;
        printf("Files saved (time elapsed = %lf)\n", time_spent);
    }


    return 0;
}



void next_time_slice(sim_t* sim) {
    save_t *current = sim->save;
    save_t *next = current + 1;
    if (sim->save_flags->save_windings) {
        for (int i = 0 ; i < sim->constants->dim*sim->constants->colors+1 ; i++) {
            next->windings_sqr[i] = current->windings_sqr[i];
        }
    }
    if (sim->save_flags->save_bond_number) {
        for (int i = 0 ; i < 3 ; i++) {
            next->sum_bonds[i] = current->sum_bonds[i];
        }
    }
    next->annulus_sum = current->annulus_sum;
    next->G0 = current->G0;

    sim->save += 1;
}


void run_sim(sim_t* sim) {
    create_worm(sim);
    sim->thermalizing = true;
    printf("Thermalizing...\n");
    time_t begin = time(NULL);
    for (long int it = 0 ; it < sim->n_iter_therm ; it++){
        update_sim(sim);
    }
    while (sim->worm->worm_head != sim->worm->worm_tail) update_sim(sim);
    time_t end = time(NULL);
    double time_spent = (double)(end - begin) / 1;
    printf("Thermalization complete (time elapsed = %lf)\n", time_spent);

    create_worm(sim);
    sim->thermalizing = false;
    printf("Riding on the worm...\n");
    begin = time(NULL);
    for (long int in = 1 ; in <= sim->n_iter ; in++){
        update_sim(sim);
        if (sim->save_flags->save_time_series && (in % sim->save_interval == 0) && (in != sim->n_iter)) {
            next_time_slice(sim);
        }
    }
    end = time(NULL);
    time_spent = (double)(end - begin) / 1;
    printf("Wormride complete (time elapsed = %lf)\n", time_spent);
    //print_bonds2D(sim);
    }