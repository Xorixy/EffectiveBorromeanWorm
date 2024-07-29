#pragma once

#include "update.h"
#include "save.h"
#include "init.h"
#include "pcg_basic.h"
#include <stdbool.h>
#include "types.h"
#include <stdio.h>
#include <time.h>
#include "files.h"
#include <unistd.h>


void run_sim(sim_t* sim);
int worm_algorithm( sim_params_t *params,
                    char *filename,
		            bool seeded,
		            __uint128_t initstate,
		            __uint128_t initseq);
void next_time_slice(sim_t* sim);