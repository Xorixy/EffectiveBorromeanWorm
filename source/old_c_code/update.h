#pragma once

#include "types.h"
#include <math.h>
#include <stdlib.h>
#include "save.h"
#include <stdio.h>
#include "print_debug.h"

void update_state(sim_t *sim, long int ind1, int dir1);
void update_sim(sim_t *sim);
void update_G(sim_t *sim, long int head, long int tail);
void create_worm(sim_t *sim);
int new_dir(sim_t *sim);