import numpy as np
import h5py as h5
import os
from batch import BatchScript
import argparse
import json
import shutil

def estimate_run_time(n_steps, n_therm):
    return 1000
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
    launch_array(sim_folder, size, P, 0, n_steps, n_therm, counter_chi_factor, n_sim, exec)

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

