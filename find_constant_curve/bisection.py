import numpy as np
import h5py as h5
import os
from batch import BatchScript
import argparse
import json
import shutil


def estimate_run_time(n_steps, n_therm):
    return int(2*(n_steps + n_therm)/(10 ** 7)) + 10
def start_bisection():
    print("Starting bisection")
    print("Reading parameter file...")
    with open(args.parameters) as f:
        p = json.load(f)
    print(p["sim_folder"])
    sim_folder = p["sim_folder"]
    if os.path.isdir(sim_folder):
        raise Exception("Sim folder already exists")
    os.makedirs(sim_folder)
    print("Copying parameter file")
    shutil.copyfile(args.parameters, sim_folder + "/bisection.json")
    size = p["size"]
    P = p["initial_P"]
    n_steps = p["n_steps"]
    n_therm = p["n_therm"]
    n_sim = p["n_sim"]
    counter_chi_factor = p["counter_chi_factor"]
    exec = p["exec_loc"]
    #launch_array(sim_folder, size, P, 0, n_steps, n_therm, counter_chi_factor, n_sim, exec)
    print(get_sim_result(sim_folder, n_sim))
def bisection_step():
    print("Bisection step")

def launch_array(loc, size, P, chi, n_steps, n_therm, counter_chi_factor, n_sim, exec_loc):
    settings_loc = loc + "/settings.h5"
    create_settings_file(settings_loc, size, P, chi, n_steps, n_therm, counter_chi_factor)
    s = BatchScript()
    s.set_job_name("effborr-bisection")
    s.set_array_start(1)
    s.set_array_end(n_sim)
    s.set_output_name(loc)
    s.set_run_time(estimate_run_time(n_steps, n_therm))
    s.set_verbose(True)
    out_loc = loc + "/out"
    command = "." + exec_loc + " -s " + settings_loc + " -o " + out_loc + " --array"
    s.set_command(command)
    s.run_batch()

def create_settings_file(settings_loc, size, P, chi, n_steps, n_therm, counter_chi_factor):
    with h5.File(settings_loc, "w") as f:
        f["settings/save/windings"] = np.bool(True)
        f["settings/save/correlations"] = np.bool(False)
        f["settings/save/time_series"] = np.bool(False)

        f["settings/sim/size_x"] = np.int32(size)
        f["settings/sim/size_y"] = np.int32(size)
        f["settings/sim/n_steps"] = np.uint64(n_steps)
        f["settings/sim/n_therm"] = np.uint64(n_therm)
        f["settings/sim/single_weight"] = np.float64(P + chi)
        f["settings/sim/counter_weight"] = np.float64(P - counter_chi_factor*chi)

        f["settings/save/annulus_size"] = np.float64(0.5)
        f["settings/save/save_interval"] = np.int32(1)

def get_sim_result(outfile, n_sims):
    part_f = np.zeros(n_sims)
    windings_diff_s_x = np.zeros(n_sims)
    windings_diff_s_y = np.zeros(n_sims)
    windings_sum_s_x = np.zeros(n_sims)
    windings_sum_s_y = np.zeros(n_sims)
    for i in range(n_sims):
        file_path = outfile + "_" + str(i + 1) + ".h5"
        with h5.File(file_path, "r") as sim_file:
            base = np.array(sim_file['/constants/base_minus_one'], dtype=np.uint64).astype(dtype=object) + 1
            part_f[i] = np.array(sim_file['/data/partition_function'], dtype=np.int64)
            windings_diff_s_x[i] = (np.array(sim_file['/data/windings_diff_squared_x/big'], dtype=np.uint64) * base +
                                    np.array(sim_file['/data/windings_diff_squared_x/small'], dtype=np.uint64))
            windings_sum_s_x[i] = (np.array(sim_file['/data/windings_sum_squared_x/big'], dtype=np.uint64) * base +
                                   np.array(sim_file['/data/windings_sum_squared_x/small'], dtype=np.uint64))
            windings_diff_s_y[i] = (np.array(sim_file['/data/windings_diff_squared_y/big'], dtype=np.uint64) * base +
                                    np.array(sim_file['/data/windings_diff_squared_y/small'], dtype=np.uint64))
            windings_sum_s_y[i] = (np.array(sim_file['/data/windings_sum_squared_y/big'], dtype=np.uint64) * base +
                                   np.array(sim_file['/data/windings_sum_squared_y/big'], dtype=np.uint64))
    windings_diff_x = windings_diff_s_x / part_f
    windings_sum_x = windings_sum_s_x / part_f
    windings_diff_y = windings_diff_s_y / part_f
    windings_sum_y = windings_sum_s_y / part_f
    windings_diff = np.append(windings_diff_x, windings_diff_y)
    windings_sum = np.append(windings_sum_x, windings_sum_y)
    diff_mean = np.mean(windings_diff)
    sum_mean = np.mean(windings_sum)
    diff_var = np.var(windings_diff, ddof=1) / n_sims
    sum_var = np.var(windings_sum, ddof=1) / n_sims
    return diff_mean, sum_mean, diff_var, sum_var
def get_chi_list(params):
    try:
        chis = np.array(params["chis"])
        if (len(chis) < 1):
            raise Exception("Chi list is empty")
    except:
        n_chis = params["n_chi"]
        chi_max = params["chi_max"]
        chis = np.linspace(0, chi_max, n_chis + 1)[1:]
    if params["two_sided"]:
        chis = np.append(chis, -chis)
    return chis

parser = argparse.ArgumentParser(description = "Bisection find constant curve")
subparsers = parser.add_subparsers(help="Sub-command help", required = True)
start_parser = subparsers.add_parser("start", help="Start bisection")
step_parser = subparsers.add_parser("step", help="Bisection step")
start_parser.set_defaults(func = start_bisection)
step_parser.set_defaults(func = bisection_step)

start_parser.add_argument("-p", "--parameters", help="Path to parameter file", required = True)


args = parser.parse_args()
print(args.parameters)
args.func()

