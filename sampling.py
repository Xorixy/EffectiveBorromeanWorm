import os
import argparse as arg
import numpy as np
import struct as st
from multiprocessing import Pool
import h5py as h5

BASE = 4611686018427387904

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



def upload_one_iter(full_name):
    with open(full_name + "_params.bin", mode="rb") as bin_file:
        params = params_unpack(bin_file.read(params_len))
    with open(full_name + "_windings.bin", mode="rb") as bin_file:
        windings = np.array(windings_unpack(bin_file.read(windings_len))).reshape(-1, (dim * 2 + 1))

    w_temp = np.zeros((save_number, dim), dtype=object)
    bond_temp = np.zeros(save_number, dtype=object)
    annulus = np.zeros((save_number, 2), dtype=object)

    for i in range(dim):
        w_temp[:, i] += windings[:, i * 2] * BASE + windings[:, i * 2 + 1]
    
    if not args.no_an:
        with open(full_name + "_sum_bonds.bin", mode="rb") as bin_file:
            sum_bonds = np.array(sum_bonds_unpack(bin_file.read(sum_bonds_len))).reshape(-1, 5)
        with open(full_name + "_annulus.bin", mode="rb") as bin_file:
            annulus = np.array(annulus_unpack(bin_file.read(annulus_len)), dtype=object).reshape(-1, 2)
        bond_temp += (sum_bonds[:, 0] * BASE + sum_bonds[:, 1] + 
                      sum_bonds[:, 2] * BASE + sum_bonds[:, 3])

    if not args.no_Gf:
        with open(full_name + "_g.bin", mode="rb") as bin_file:
            g_c = g_unpack(bin_file.read(g_len))
    else:
        g_c = np.zeros([*params[:dim]])
    return w_temp, bond_temp, windings[:, -1], np.array(g_c).reshape(*params[:dim]), annulus, params

parser = arg.ArgumentParser(prog = 'BorromeanWorms')
parser.add_argument('-fn', '--file_name', help='sourse of the data', required=True)
args = parser.parse_args()
name = args.file_name

foldername = os.environ['SIM_PATH'] + name
dist_name = os.environ['DATA_PATH'] + name + '.h5'

if not os.path.isdir(foldername):
    raise OSError(1, 'No folder with such name')

if os.path.isfile(dist_name):
    raise OSError(1, 'Data is ready')

folder_names = os.listdir(foldername)

for el in folder_names:
    curr_folder = os.path.isdir(foldername + '/' + el).sort()
    set_file_path = foldername + '/' + el + '/' + curr_folder[-1]
    with h5.File(set_file_path, "r") as settings_file:
        windings = settings_file[WINDINGS_LOC]
        correlations = settings_file[CORRELATIONS_LOC]
        annulus_size = settings_file[ANNULUS_SIZE_LOC]
        save_interval = settings_file[SAVE_INTERVAL_LOC]
        time_series = settings_file[TIME_SERIES_LOC]

        size_x = settings_file[SIZE_X_LOC]
        size_y = settings_file[SIZE_Y_LOC]
        n_steps = settings_file[N_STEPS_LOC]
        n_therm = settings_file[N_THERM_LOC]
        single_weight = settings_file[SINGLE_WEIGHT_LOC]
        counter_weight = settings_file[COUNTER_WEIGHT_LOC]
    
    number_of_steps = np.ceil(n_steps / save_interval, dtype=int)
    ann_sum = np.zeros((len(curr_folder) - 1, number_of_steps), dtype=np.uint64)
    part_f = np.zeros((len(curr_folder) - 1, number_of_steps), dtype=np.uint64)
    windings_diff_s = np.zeros((len(curr_folder) - 1, number_of_steps), dtype=object)
    windings_sum_s = np.zeros((len(curr_folder) - 1, number_of_steps), dtype=object)


n_i_res = {}
params_res = {}
w_res = {}
bond_res = {}
g_res = {}
annulus_res = {}
w_res_s = {}
bond_res_s = {}
g_res_s = {}
annulus_res_s = {}
n_k = len(folder_names)
number_of_samples = {}
number_of_samples_s = {}
control_par_arr = np.zeros(n_k)

for i in range(n_k):
    control_par = float(folder_names[i][2:])
    control_par_arr[i] = control_par
    file_names = os.listdir(SIM_PATH + name + '/' + folder_names[i])
    if not args.no_an:
        n_i = len(file_names) // 4
    else:
        n_i = len(file_names) // 2
    n_i_res[control_par] = n_i

    if n_i != 0:
        poss_iter_numbers = []
        for el in file_names:
            if el[-11:] == "_params.bin":
                par_name = el
                poss_iter_numbers.append(el[:-11])

        params_fmt = '=4id3iQil'

        params_len = st.calcsize(params_fmt)
        params_unpack = st.Struct(params_fmt).unpack_from

        with open(SIM_PATH + name + '/' + folder_names[i] + '/' + par_name, mode="rb") as bin_file:
            params = params_unpack(bin_file.read(params_len))
            dim = params[5]
            colors = params[6]
            max_bonds = params[7]
            n_iter = params[8]
            save_interval = params[9]
            annulus_size = params[10]
            save_number = n_iter // save_interval

        params_res[control_par] = np.zeros((n_i, 11))
        g_res[control_par] = np.zeros([*params[:dim]])
        g_res_s[control_par] = np.zeros([*params[:dim]])
        w_res[control_par] = np.zeros((save_number, dim), dtype=object)
        w_res_s[control_par] = np.zeros((save_number, dim), dtype=object)
        bond_res[control_par] = np.zeros(save_number, dtype=object)
        bond_res_s[control_par] = np.zeros(save_number, dtype=object)
        annulus_res[control_par] = np.zeros((save_number, 2), dtype=object)
        annulus_res_s[control_par] = np.zeros((save_number), dtype=object)
        number_of_samples[control_par] = np.zeros(save_number, dtype=object)
        number_of_samples_s[control_par] = np.zeros(save_number, dtype=object)

        sum_bonds_fmt = '=' + str(5 * save_number) + 'q'
        sum_bonds_len = st.calcsize(sum_bonds_fmt)
        sum_bonds_unpack = st.Struct(sum_bonds_fmt).unpack_from

        windings_fmt = '=' + str((dim * 2 + 1) * save_number) + 'q'
        windings_len = st.calcsize(windings_fmt)
        windings_unpack = st.Struct(windings_fmt).unpack_from

        annulus_fmt = '=' + str(2 * save_number) + 'q'
        annulus_len = st.calcsize(annulus_fmt)
        annulus_unpack = st.Struct(annulus_fmt).unpack_from

        g_fmt = '=' + str(g_res[control_par].size) + 'q' 
        g_len = st.calcsize(g_fmt)
        g_unpack = st.Struct(g_fmt).unpack_from

        full_names = [SIM_PATH + name + '/' + folder_names[i] + '/' + j for j in poss_iter_numbers]

        pool = Pool() 

        for i, temp_var in enumerate(pool.imap(upload_one_iter, full_names)):
            w_temp, bond_temp, n_temp, g_temp, annulus_temp, params_temp = temp_var
            n_temp[n_temp == 0] = 1
            params_res[control_par][i] = np.array(params_temp)
            for k in range(dim):
                w_res[control_par][:, k] += w_temp[:, k] / n_temp
                w_res_s[control_par][:, k] += (w_temp[:, k] / n_temp) ** 2
            bond_res[control_par] += bond_temp
            bond_res_s[control_par] += bond_temp ** 2
            number_of_samples[control_par] += n_temp
            number_of_samples_s[control_par] += n_temp ** 2
            g_res[control_par] += g_temp
            g_res_s[control_par] += g_temp ** 2
            annulus_temp[:, 1][annulus_temp[:, 1] == 0] = 1
            annulus_res[control_par][:, 0] += annulus_temp[:, 0] / annulus_temp[:, 1]
            annulus_res[control_par][:, 1] += annulus_temp[:, 1] / annulus_temp[:, 1]
            annulus_res_s[control_par] += (annulus_temp[:, 0] / annulus_temp[:, 1]) ** 2


        pool.close()
        pool.join()

n_i_arr = np.zeros(len(control_par_arr), dtype=object)
for i in range(len(control_par_arr)):
    n_i_arr[i] = n_i_res[control_par_arr[i]]

params_arr = np.zeros((len(control_par_arr), np.max(n_i_arr), 11), dtype=object)
w_arr = np.zeros((len(control_par_arr), save_number, dim), dtype=object)
w_arr_s = np.zeros((len(control_par_arr), save_number, dim), dtype=object)
bond_arr = np.zeros((len(control_par_arr), save_number), dtype=object)
bond_arr_s = np.zeros((len(control_par_arr), save_number), dtype=object)
number_arr = np.zeros((len(control_par_arr), save_number), dtype=object)
number_arr_s = np.zeros((len(control_par_arr), save_number), dtype=object)
annulus_arr = np.zeros((len(control_par_arr), save_number, 2), dtype=object)
annulus_arr_s = np.zeros((len(control_par_arr), save_number), dtype=object)

for i in range(len(control_par_arr)):
    params_arr[i, :n_i_arr[i]] = params_res[control_par_arr[i]]
    w_arr[i] = w_res[control_par_arr[i]]
    w_arr_s[i] = w_res_s[control_par_arr[i]]
    bond_arr[i] = bond_res[control_par_arr[i]]
    bond_arr_s[i] = bond_res_s[control_par_arr[i]]
    number_arr[i] = number_of_samples[control_par_arr[i]]
    number_arr_s[i] = number_of_samples_s[control_par_arr[i]]
    annulus_arr[i] = annulus_res[control_par_arr[i]]
    annulus_arr_s[i] = annulus_res_s[control_par_arr[i]]

if not args.issize:
    g_arr = np.zeros((len(control_par_arr), *params[:dim]), dtype=object)
    g_arr_s = np.zeros((len(control_par_arr), *params[:dim]), dtype=object)
    for i in range(len(control_par_arr)):
        g_arr[i] = g_res[control_par_arr[i]]
        g_arr_s[i] = g_res_s[control_par_arr[i]]
else:
    g_arr = [0] * len(control_par_arr)
    g_arr_s = [0] * len(control_par_arr)
    for i in range(len(control_par_arr)):
        g_arr[i] = g_res[control_par_arr[i]]
        g_arr_s[i] = g_res_s[control_par_arr[i]]

inds = control_par_arr.argsort()
control_par_arr = control_par_arr[inds]
w_arr = w_arr[inds]
w_arr_s = w_arr_s[inds]
bond_arr = bond_arr[inds]
bond_arr_s = bond_arr_s[inds]
number_arr = number_arr[inds]
number_arr_s = number_arr_s[inds]
annulus_arr = annulus_arr[inds]
annulus_arr_s = annulus_arr_s[inds]
params_arr = params_arr[inds]
n_i_arr = n_i_arr[inds]

if not args.issize:
    g_arr = g_arr[inds]
    g_arr_s = g_arr_s[inds]
if not args.issize:
    np.savez(RES_PATH + name + '.npz', control_par_arr=control_par_arr, w_arr=w_arr, bond_arr=bond_arr, g_arr=g_arr, number_arr=number_arr, params_arr=params_arr, 
             w_arr_s=w_arr_s, bond_arr_s=bond_arr_s, g_arr_s=g_arr_s, number_arr_s=number_arr_s, annulus_arr=annulus_arr, annulus_arr_s=annulus_arr_s, n_i_arr=n_i_arr)
else:
    np.savez(RES_PATH + name + '.npz', control_par_arr=control_par_arr, w_arr=w_arr, bond_arr=bond_arr, number_arr=number_arr, params_arr=params_arr, 
             w_arr_s=w_arr_s, bond_arr_s=bond_arr_s, number_arr_s=number_arr_s, annulus_arr=annulus_arr, annulus_arr_s=annulus_arr_s, n_i_arr=n_i_arr)
