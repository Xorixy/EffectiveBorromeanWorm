import os
import argparse as arg
import numpy as np
import struct as st
from multiprocessing import Pool
import h5py as h5

SIM_LOC = '/system_data/location'
SIM_PARAMS_LOC = '/system_data/sim_params'

WINDINGS_LOC = '/settings/save/windings'
CORRELATIONS_LOC = '/settings/save/correlations'
ANNULUS_SIZE_LOC = '/settings/save/annulus_size'
SAVE_INTERVAL_LOC = '/settings/save/save_interval'
TIME_SERIES_LOC = '/settings/save/time_series'

SIZE_X_LOC = '/settings/sim/size_x'
SIZE_Y_LOC = '/settings/sim/size_y'
N_STEPS_LOC = '/settings/sim/n_steps'
N_THERM_LOC = '/settings/sim/n_therm'
SINGLE_WEIGHT_LOC = '/settings/sim/single_weight'
COUNTER_WEIGHT_LOC = '/settings/sim/counter_weight'
ANNULUS_AREA_LOC = '/settings/sim/annulus_area'
BASE_MINUS_ONE_LOC = '/settings/sim/base_minus_one'

N_SYSTEMS_LOC = '/settings/sim/n_systems'   
N_SAMPLES_LOC = '/settings/sim/n_samples'
NUMBER_OF_STEPS_LOC = '/settings/sim/number_of_steps'

WINDING_DIFF_RES_BIG_X_LOC = '/windings_diff_squared_x/big'
WINDING_DIFF_RES_SMALL_X_LOC = '/windings_diff_squared_x/small'

WINDING_SUM_RES_BIG_X_LOC = '/windings_sum_squared_x/big'
WINDING_SUM_RES_SMALL_X_LOC = '/windings_sum_squared_x/small'

WINDING_DIFF_RES_BIG_Y_LOC = '/windings_diff_squared_y/big'
WINDING_DIFF_RES_SMALL_Y_LOC = '/windings_diff_squared_y/small'

WINDING_SUM_RES_BIG_Y_LOC = '/windings_sum_squared_y/big'
WINDING_SUM_RES_SMALL_Y_LOC = '/windings_sum_squared_y/small'

ANNULUS_SUM_LOC = '/annulus_sum'
PARTITION_FUNCTION_LOC = '/partition_function'

SIZE_X_ARR_LOC = '/results/size_x'
SIZE_Y_ARR_LOC = '/results/size_y'

SINGLE_WEIGHT_ARR_LOC = '/results/single_weight'
COUNTER_WEIGHT_ARR_LOC = '/results/counter_weight'

ANNULUS_RES_LOC = '/results/annulus_res'
ANNULUS_RES_STD_LOC = '/results/annulus_res_std'
WINDING_DIFF_X_RES_LOC = '/results/windings_diff_squared_x'
WINDING_DIFF_X_RES_STD_LOC = '/results/windings_diff_squared_x_std'
WINDING_DIFF_Y_RES_LOC = '/results/windings_diff_squared_y'
WINDING_DIFF_Y_RES_STD_LOC = '/results/windings_diff_squared_y_std'
WINDING_SUM_X_RES_LOC = '/results/windings_sum_squared_x'
WINDING_SUM_X_RES_STD_LOC = '/results/windings_sum_squared_x_std'
WINDING_SUM_Y_RES_LOC = '/results/windings_sum_squared_y'
WINDING_SUM_Y_RES_STD_LOC = '/results/windings_sum_squared_y_std'

parser = arg.ArgumentParser(prog = 'BorromeanWorms')
parser.add_argument('-fn', '--file_name', help='sourse of the data', required=True)
args = parser.parse_args()
name = args.file_name

foldername = os.environ['SIM_PATH'] + name
dist_name = os.environ['DATA_PATH'] + name + '.h5'

if not os.path.isdir(foldername):
    raise OSError(1, 'No folder with such name')

"""
if os.path.isfile(dist_name):
    raise OSError(1, 'Data is ready')
"""

folder_names = os.listdir(foldername)

curr_folder_check = sorted(os.listdir(foldername + '/0'))
settings_check_path = foldername + '/0/' + curr_folder_check[-1]

with h5.File(settings_check_path, "r") as settings_file:
    location = np.array(settings_file[SIM_LOC])
    sim_params_string = np.array(settings_file[SIM_PARAMS_LOC])
    save_interval = np.array(settings_file[SAVE_INTERVAL_LOC], dtype=np.int64)
    time_series = np.array(settings_file[TIME_SERIES_LOC], dtype=np.int64)
    n_steps = np.array(settings_file[N_STEPS_LOC], dtype=np.int64)
    base = np.array(settings_file[BASE_MINUS_ONE_LOC], dtype=np.uint64).astype(dtype=object) + 1
    

n_systems = len(folder_names)
n_samples = len(curr_folder_check) - 1
number_of_steps = np.ceil(n_steps / save_interval).astype(dtype=np.int64)

size_x_arr = np.zeros(n_systems)
size_y_arr = np.zeros(n_systems)
n_steps_arr = np.zeros(n_systems)
n_therm_arr = np.zeros(n_systems)
single_weight_arr = np.zeros(n_systems)
counter_weight_arr = np.zeros(n_systems)

annulus_arr = np.zeros((n_systems, number_of_steps))
annulus_arr_s = np.zeros((n_systems, number_of_steps))

windings_diff_arr_x = np.zeros((n_systems, number_of_steps))
windings_diff_arr_x_s = np.zeros((n_systems, number_of_steps))

windings_sum_arr_x = np.zeros((n_systems, number_of_steps))
windings_sum_arr_x_s = np.zeros((n_systems, number_of_steps))

windings_diff_arr_y = np.zeros((n_systems, number_of_steps))
windings_diff_arr_y_s = np.zeros((n_systems, number_of_steps))

windings_sum_arr_y = np.zeros((n_systems, number_of_steps))
windings_sum_arr_y_s = np.zeros((n_systems, number_of_steps))

for l in range(n_systems):
    curr_folder = sorted(os.listdir(foldername + '/' + folder_names[l]))
    settings_file_path = foldername + '/' + folder_names[l] + '/' + curr_folder[-1]
    with h5.File(settings_file_path, "r") as settings_file:
        size_x = np.array(settings_file[SIZE_X_LOC])
        size_y = np.array(settings_file[SIZE_Y_LOC])
        n_steps = np.array(settings_file[N_STEPS_LOC])
        n_therm = np.array(settings_file[N_THERM_LOC])
        single_weight = np.array(settings_file[SINGLE_WEIGHT_LOC])
        counter_weight = np.array(settings_file[COUNTER_WEIGHT_LOC])
        annulus_area = np.array(settings_file[ANNULUS_AREA_LOC])
    
    ann_sum = np.zeros((n_samples, number_of_steps), dtype=np.uint64)
    part_f = np.zeros((n_samples, number_of_steps), dtype=np.uint64)
    windings_diff_s_x = np.zeros((n_samples, number_of_steps), dtype=object)
    windings_sum_s_x = np.zeros((n_samples, number_of_steps), dtype=object)
    windings_diff_s_y = np.zeros((n_samples, number_of_steps), dtype=object)
    windings_sum_s_y = np.zeros((n_samples, number_of_steps), dtype=object)

    for i in range(n_samples):
        file_path = foldername + '/' + folder_names[l] + '/' + curr_folder[i]
        with h5.File(file_path, "r") as sim_file:
            iter_names = np.sort(np.array(list(sim_file.keys())))
            for j in range(number_of_steps):
                inner_path = str(iter_names[j]) + '/'
                ann_sum[i, j] = np.array(sim_file[inner_path + ANNULUS_SUM_LOC], dtype=np.uint64)
                part_f[i, j] = np.array(sim_file[inner_path + PARTITION_FUNCTION_LOC], dtype=np.int64)
                windings_diff_s_x[i, j] = (np.array(sim_file[inner_path + WINDING_DIFF_RES_BIG_X_LOC], dtype=np.uint64) * base + 
                                         np.array(sim_file[inner_path + WINDING_DIFF_RES_SMALL_X_LOC], dtype=np.uint64))
                windings_sum_s_x[i, j] = (np.array(sim_file[inner_path + WINDING_SUM_RES_BIG_X_LOC], dtype=np.uint64) * base + 
                                         np.array(sim_file[inner_path + WINDING_SUM_RES_SMALL_X_LOC], dtype=np.uint64))
                windings_diff_s_y[i, j] = (np.array(sim_file[inner_path + WINDING_DIFF_RES_BIG_Y_LOC], dtype=np.uint64) * base + 
                                         np.array(sim_file[inner_path + WINDING_DIFF_RES_SMALL_Y_LOC], dtype=np.uint64))
                windings_sum_s_y[i, j] = (np.array(sim_file[inner_path + WINDING_SUM_RES_BIG_Y_LOC], dtype=np.uint64) * base + 
                                         np.array(sim_file[inner_path + WINDING_SUM_RES_SMALL_Y_LOC], dtype=np.uint64))

    size_x_arr[l] = size_x
    size_y_arr[l] = size_y
    n_steps_arr[l] = n_steps
    n_therm_arr[l] = n_therm
    single_weight_arr[l] = single_weight
    counter_weight_arr[l] = counter_weight

    annulus_arr[l] = np.mean(ann_sum / part_f, axis=0) / annulus_area
    annulus_arr_s[l] = np.std(ann_sum / part_f, axis=0) / annulus_area

    windings_diff_arr_x[l] = np.mean((windings_diff_s_x / part_f).astype(np.float64), axis=0)
    windings_diff_arr_x_s[l] = np.std((windings_diff_s_x / part_f).astype(np.float64), axis=0)
    windings_diff_arr_y[l] = np.mean((windings_diff_s_y / part_f).astype(np.float64), axis=0)
    windings_diff_arr_y_s[l] = np.std((windings_diff_s_y / part_f).astype(np.float64), axis=0)

    windings_sum_arr_x[l] = np.mean((windings_sum_s_x / part_f).astype(np.float64), axis=0)
    windings_sum_arr_x_s[l] = np.std((windings_sum_s_x / part_f).astype(np.float64), axis=0)
    windings_sum_arr_y[l] = np.mean((windings_sum_s_y / part_f).astype(np.float64), axis=0)
    windings_sum_arr_y_s[l] = np.std((windings_sum_s_y / part_f).astype(np.float64), axis=0)

with h5.File(dist_name, "w") as dist_file:
    dist_file[N_STEPS_LOC] = n_steps_arr
    dist_file[N_THERM_LOC] = n_therm_arr
    dist_file[N_SYSTEMS_LOC] = n_systems
    dist_file[N_SAMPLES_LOC] = n_samples
    dist_file[NUMBER_OF_STEPS_LOC] = number_of_steps

    dist_file[SIZE_X_ARR_LOC] = size_x_arr
    dist_file[SIZE_Y_ARR_LOC] = size_y_arr
    dist_file[SINGLE_WEIGHT_ARR_LOC] = single_weight_arr
    dist_file[COUNTER_WEIGHT_ARR_LOC] = counter_weight_arr

    dist_file[ANNULUS_RES_LOC] = annulus_arr
    dist_file[ANNULUS_RES_STD_LOC] = annulus_arr_s

    dist_file[WINDING_DIFF_X_RES_LOC] = windings_diff_arr_x
    dist_file[WINDING_DIFF_X_RES_STD_LOC] = windings_diff_arr_x_s

    dist_file[WINDING_DIFF_Y_RES_LOC] = windings_diff_arr_y
    dist_file[WINDING_DIFF_Y_RES_STD_LOC] = windings_diff_arr_y_s

    dist_file[WINDING_SUM_X_RES_LOC] = windings_sum_arr_x
    dist_file[WINDING_SUM_X_RES_STD_LOC] = windings_sum_arr_x_s

    dist_file[WINDING_SUM_Y_RES_LOC] = windings_sum_arr_y
    dist_file[WINDING_SUM_Y_RES_STD_LOC] = windings_sum_arr_y_s
    
    dist_file.create_dataset(SIM_LOC, data=location)
    dist_file.create_dataset(SIM_PARAMS_LOC, data=sim_params_string)

print('File ' + dist_name + ' is ready')
