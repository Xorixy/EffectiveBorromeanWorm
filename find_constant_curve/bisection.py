import numpy as np
import h5py as h5
import os
from batch import BatchScript
import argparse
import json
import shutil

def get_S(single_stiffness, double_stiffness):
    v = np.pi*single_stiffness - 2
    w = double_stiffness - 2
    return 8*v**2 + 5*w**2 - 4*v*w
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
    print("Copying python file")
    python_file = p["python_file"]
    shutil.copyfile(python_file, sim_folder + "/bisection.py")
    size = p["size"]
    P = p["initial_P"]
    n_steps = p["n_steps"]
    n_therm = p["n_therm"]
    n_sim = p["n_sim"]
    counter_chi_factor = p["counter_chi_factor"]
    exec = p["exec_loc"]
    sym_id = launch_array(sim_folder, size, P, 0, n_steps, n_therm, counter_chi_factor, n_sim, exec)
    res = h5.File(sim_folder + "/result.h5", "x")
    res.create_dataset("sym/id", data=sym_id)


def bisection_step():
    print("Bisection step")

    with open(args.sim_folder + "/bisection.json") as f:
        p = json.load(f)
    print(p["sim_folder"])
    sim_folder = p["sim_folder"]
    n_sim = p["n_sim"]
    size = p["size"]
    res = h5.File(sim_folder + "/result.h5", "r+")


def launch_bisection_step(prev_ids, sim_folder):
    s = BatchScript()
    s.set_job_name("effborr-bisection-step")
    s.set_output_name(sim_folder)
    s.set_run_time(3600)
    s.set_verbose(True)
    s.set_dependency(f"afterany:{prev_ids}")
    s.set_command("python3 " + sim_folder + "/bisection.py" + " step " + "--sim_folder " + sim_folder)

def launch_array(loc, size, P, chi, n_steps, n_therm, counter_chi_factor, n_sim, exec_loc):
    settings_loc = loc + "/settings.h5"
    create_settings_file(settings_loc, size, P, chi, n_steps, n_therm, counter_chi_factor)
    s = BatchScript()
    s.set_job_name("effborr-bisection")
    s.set_array_start(1)
    s.set_array_end(n_sim)
    out_loc = loc
    if os.path.isdir(loc + "/sim"):
        for filename in os.listdir(out_loc):
            file_path = os.path.join(out_loc, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        os.makedirs(out_loc)
    s.set_output_name(out_loc)
    s.set_run_time(estimate_run_time(n_steps, n_therm))
    s.set_verbose(True)

    out_loc += "/out"
    command = "." + exec_loc + " -s " + settings_loc + " -o " + out_loc + " --array"
    s.set_command(command)
    return s.run_batch()

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

def get_sim_result(outfile, n_sims, size):
    part_f = np.zeros(n_sims)
    windings_diff_s_x = np.zeros(n_sims)
    windings_diff_s_y = np.zeros(n_sims)
    windings_sum_s_x = np.zeros(n_sims)
    windings_sum_s_y = np.zeros(n_sims)
    for i in range(n_sims):
        file_path = outfile + "_" + str(i + 1) + ".h5"
        with h5.File(file_path, "r") as sim_file:
            base = int(sim_file['/constants/base_minus_one'][()]) + 1
            part_f[i] = int(sim_file['/data/partition_function'][()])
            windings_diff_s_x[i] = (int(sim_file['/data/windings_diff_squared_x/big'][()]) * base +
                                    int(sim_file['/data/windings_diff_squared_x/small'][()]))
            windings_sum_s_x[i] = (int(sim_file['/data/windings_sum_squared_x/big'][()]) * base +
                                   int(sim_file['/data/windings_sum_squared_x/small'][()]))
            windings_diff_s_y[i] = (int(sim_file['/data/windings_diff_squared_y/big'][()]) * base +
                                    int(sim_file['/data/windings_diff_squared_y/small'][()]))
            windings_sum_s_y[i] = (int(sim_file['/data/windings_sum_squared_y/big'][()]) * base +
                                   int(sim_file['/data/windings_sum_squared_y/small'][()]))
    lambda_diff_x = windings_diff_s_x / (part_f * size ** 2)
    lambda_sum_x = windings_sum_s_x / (part_f * size ** 2)
    lambda_diff_y = windings_diff_s_y / (part_f * size ** 2)
    lambda_sum_y = windings_sum_s_y / (part_f * size ** 2)
    lambda_diff = (lambda_diff_x + lambda_diff_y) / 2
    lambda_sum = (lambda_sum_x + lambda_sum_y) / 2
    lambda_single = (lambda_diff + lambda_sum) / 4
    S = get_S(lambda_single, lambda_sum)
    S_mean = np.mean(S)
    S_var = np.var(S, ddof=1) / n_sims
    return S_mean, S_var

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
step_parser.add_argument("--sim_folder", help="Path to the sim folder", required = True)

args = parser.parse_args()
print(args.parameters)
args.func()

