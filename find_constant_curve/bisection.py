from logging import exception

import numpy as np
import h5py as h5
import os

from numpy.f2py.auxfuncs import throw_error

from batch import BatchScript
import argparse
import json
import shutil
import time

def get_S(single_stiffness, double_stiffness):
    v = np.pi*single_stiffness - 2
    w = np.pi*double_stiffness - 2
    S = 8*v**2 + 5*w**2 - 4*v*w
    return S
def estimate_run_time(n_steps, n_therm):
    return int(2*(n_steps + n_therm)/(10 ** 7)) + 10
def start_bisection():
    print("Starting bisection")
    print("Reading parameter file...")
    p = try_load_json(args.parameters)
    print(p["sim_folder"])
    sim_folder = p["sim_folder"]
    print("Creating folders...")
    if os.path.isdir(sim_folder):
        raise Exception("Sim folder already exists")
    os.makedirs(sim_folder)
    chis = get_chi_list(p)
    os.makedirs(sim_folder + "/sim/sym")
    for i in range(len(chis)):
        os.makedirs(sim_folder + "/sim/" + str(i))
    print("Copying parameter file")
    shutil.copyfile(args.parameters, sim_folder + "/bisection.json")
    print("Copying python files")
    python_file = p["python_file"]
    shutil.copyfile(python_file, sim_folder + "/bisection.py")
    batch_file = p["batch_file"]
    shutil.copyfile(batch_file, sim_folder + "/batch.py")
    exec_loc = p["exec_loc"]
    size = p["size"]
    P = p["initial_P"]
    n_steps = p["n_steps"]
    n_therm = p["n_therm"]
    n_sim = p["n_sim"]
    counter_chi_factor = p["counter_chi_factor"]
    res = try_load_h5(sim_folder + "/result.h5", "x")
    res.create_dataset("sym/P", data=P)
    sym_id = launch_array(sim_folder + "/sim/sym", size, P, 0, n_steps, n_therm, counter_chi_factor, n_sim, exec_loc, 1, True)
    launch_bisection_step(sym_id, sim_folder, -1, 1)
    for i in range(len(chis)):
        start_new_chi_step(p, i)
def bisection_step():
    print("Bisection step")
    p = try_load_json(args.sim_folder + "/bisection.json")
    print(p["sim_folder"])
    sim_folder = p["sim_folder"]
    size = p["size"]
    n_sim = p["n_sim"]
    res = try_load_h5(sim_folder + "/result.h5", "r+")
    k_chi = args.k_chi
    print("k_chi = ", k_chi)
    if k_chi == -1:
        print("Collecting sym data")
        S_mean, S_var = get_sim_result(sim_folder + "/sim/sym/out/out", n_sim, size, 1)
        res.create_dataset("sym/S", data=S_mean)
        res.create_dataset("sym/S_err", data=np.sqrt(S_var))
        print("Done")
    else:
        print("Continuing bisection")
        continue_chi_step(p, k_chi)

def continue_chi_step(parameters, k_chi):
    sim_folder = parameters["sim_folder"]
    size = parameters["size"]
    P = parameters["initial_P"]
    n_steps = parameters["n_steps"]
    n_therm = parameters["n_therm"]
    n_sim = parameters["n_sim"]
    n_P_parallel = parameters["n_P_parallel"]
    exec_loc = parameters["exec_loc"]
    counter_chi_factor = parameters["counter_chi_factor"]
    width = parameters["initial_width"]
    res = try_load_h5(sim_folder + "/result.h5", "r+")
    print(f"Running step for chi {k_chi}")
    chis = get_chi_list(parameters)
    target_S = res["sym/S"][()]
    Ps = res[str(k_chi) + "/Ps"][:]
    S = res[str(k_chi) + "/S"][:]
    S_err = res[str(k_chi) + "/S_err"][:]
    sim_Ps = Ps[len(S):]
    sim_S, sim_S_var = get_sim_array_result(sim_folder + f"/sim/{k_chi}/out/out", n_sim, size, Ps)
    S = np.append(S, sim_S)
    S_err = np.append(S_err, np.sqrt(sim_S_var))
    del res[str(k_chi) + "/Ps"]
    del res[str(k_chi) + "/S"]
    del res[str(k_chi) + "/S_err"]
    sort = Ps.argsort()
    Ps = Ps[sort]
    S = S[sort]
    S_err = S_err[sort]
    res.create_dataset(str(k_chi) + "/Ps", data=Ps)
    res.create_dataset(str(k_chi) + "/S", data=S)
    res.create_dataset(str(k_chi) + "/S_err", data=S_err)
    if len(Ps) >= parameters["max_num_P"]:
        print("All Ps done!")

    """
    index_min, index_max = -1, -1
    multiple_target_s = False
    for i in range(1,len(S)):
        if S[i] < target_S and target_S < S[i-1]:
            if index_min != -1 or index_max != -1:
                raise Exception("Error: target S found in multiple places")
            index_min = i-1
            index_max = i
        elif S[i] > target_S and target_S > S[i-1]:
            if index_min != -1 or index_max != -1:
                raise Exception("Error: target S found in multiple places")
            index_min = i-1
            index_max = i
    """

def start_new_chi_step(parameters, k_chi):
    sim_folder = parameters["sim_folder"]
    size = parameters["size"]
    P = parameters["initial_P"]
    n_steps = parameters["n_steps"]
    n_therm = parameters["n_therm"]
    n_sim = parameters["n_sim"]
    n_P_parallel = parameters["n_P_parallel"]
    exec_loc = parameters["exec_loc"]
    counter_chi_factor = parameters["counter_chi_factor"]
    width = parameters["initial_width"]
    res = try_load_h5(sim_folder + "/result.h5", "r+")
    print(f"Starting bisection for chi {k_chi}")
    chis = get_chi_list(parameters)
    chi = chis[k_chi]
    P_mid = P
    """
    prev_k, prev_prev_k = get_prev_k_chis(chis, k_chi)
    if prev_k != -1:
        prev_chi = chis[prev_k]
        prev_P = res[str(prev_k) + "/P_est"][()]
        prev_prev_chi = 0
        prev_prev_P = P
        if prev_prev_k != -1:
            prev_prev_chi = chis[prev_prev_k]
            prev_prev_P = res[str(prev_prev_k) + "/P_est"][()]

        P_mid = prev_prev_P + (prev_P - prev_prev_P)*(chi - prev_prev_chi)/(prev_chi - prev_prev_chi)
    """
    P_max = P_mid + width / 2
    P_min = P_mid - width / 2
    Ps = get_Ps_init(P_min, P_max, n_P_parallel)
    print(Ps)
    print(Ps + chi)
    print(Ps - counter_chi_factor*chi)
    sim_ids = launch_step_array(sim_folder + f"/sim/{k_chi}", size, Ps, chi, n_steps, n_therm, counter_chi_factor, n_sim, exec_loc)
    res.create_dataset(str(k_chi) + "/Ps", data=Ps)
    S = np.array([])
    S_err = np.array([])
    res.create_dataset(str(k_chi) + "/S", data=S)
    res.create_dataset(str(k_chi) + "/S_err", data=S_err)
    res.create_dataset(str(k_chi) + "/chi", data=chi)
    launch_bisection_step(sim_ids, sim_folder, k_chi, 1)




def get_prev_k_chis(chis, k_chi):
    #This function returns the k_chis of the previous and previous-previous steps in the same chi direction as before.
    #If there is no previous step, then the value of k_prev = -1
    #As an example, if the chi list is [1, 2, 3, -1, -2, -3] then the pk and ppk of k = 0 are -1, -1 since
    #there is no lower positive chi value than 1
    #For k = 1 corresponding to chi = 2, we have pk = 0, ppk = -1 and
    #for k = 2 we have pk = 1, ppk = 0.
    #For k = 3 however, we start anew and we should thus have pk = ppk = -1
    chi = chis[k_chi]
    prev_chi = 0
    prev_k_chi = -1
    prev_prev_chi = 0
    prev_prev_k_chi = -1
    if k_chi != 0:
        prev_chi = chis[k_chi - 1]
    if np.sign(chi) == np.sign(prev_chi):
        prev_k_chi = k_chi - 1

    if prev_k_chi != -1:
        if prev_k_chi != 0:
            prev_prev_chi = chis[prev_k_chi - 1]
        if np.sign(prev_chi) == np.sign(prev_prev_chi):
            prev_prev_k_chi = prev_k_chi - 1

    return prev_k_chi, prev_prev_k_chi

def get_Ps_init(P_min, P_max , n_P_parallel):
    return np.linspace(P_min, P_max, n_P_parallel + 2)

def get_Ps_step(P_min, P_max, n_P_parallel):
    return get_Ps_init(P_min, P_max, n_P_parallel)[1:-1]

def launch_bisection_step(prev_ids, sim_folder, k_chi, n):
    s = BatchScript()
    s.set_job_name("effborr-bisection-step")
    s.set_output_name(sim_folder)
    s.set_run_time(3600)
    s.set_verbose(True)
    s.set_log_name(f"{k_chi}_{n}")
    command = "python3 " + sim_folder + "/bisection.py" + " step " + "--sim_folder " + sim_folder + " --k_chi " + str(k_chi) + " -n " + str(n)
    print("Launching bisection step with command : ")
    print(command)
    s.set_dependency(f"afterany:{prev_ids}")
    s.set_command(command)
    s.run_batch()

def launch_step_array(loc, size, Ps, chi, n_steps, n_therm, counter_chi_factor, n_sim, exec_loc):
    sim_ids = str(launch_array(loc, size, Ps[0], chi, n_steps, n_therm, counter_chi_factor, n_sim, exec_loc, 1, True))
    for i in range(1, len(Ps)):
        sim_ids += ","
        sim_ids += str(launch_array(loc, size, Ps[i], chi, n_steps, n_therm, counter_chi_factor, n_sim, exec_loc, 1 + i*n_sim, False))
    return sim_ids

def launch_array(loc, size, P, chi, n_steps, n_therm, counter_chi_factor, n_sim, exec_loc, array_start, new_folder):
    settings_loc = loc + "/settings" + str(array_start) + ".h5"
    create_settings_file(settings_loc, size, P, chi, n_steps, n_therm, counter_chi_factor)
    s = BatchScript()
    s.set_job_name("effborr-bisection")
    s.set_array_start(array_start)
    s.set_array_end(array_start + n_sim - 1)
    out_loc = loc + "/out"
    print(out_loc)
    if new_folder is True:
        if os.path.isdir(out_loc):
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
    command = exec_loc + " -s " + settings_loc + " -o " + out_loc + " --array"
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

def get_sim_array_result(outfile, n_sims, size, Ps):
    S_means = np.zeros(len(Ps))
    S_vars  = np.zeros(len(Ps))
    for i in range(len(Ps)):
        S_mean, S_var = get_sim_result(outfile, n_sims, size, 1 + i*n_sims)
        S_means[i] = S_mean
        S_vars[i] = S_var
    return S_means, S_vars

def get_sim_result(outfile, n_sims, size, array_start):
    part_f = np.zeros(n_sims)
    windings_diff_s_x = np.zeros(n_sims)
    windings_diff_s_y = np.zeros(n_sims)
    windings_sum_s_x = np.zeros(n_sims)
    windings_sum_s_y = np.zeros(n_sims)
    for i in range(n_sims):
        file_path = outfile + "_" + str(i + array_start) + ".h5"
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
    switched_sign = False
    for i in range(1, len(chis)):
        if chis[i] == 0:
            raise Exception("Chi list contains zero. Aborting")
        if chis[i-1] == 0:
            raise Exception("Chi list contains zero. Aborting")
        if np.sign(chis[i]) != np.sign(chis[i - 1]):
            if not switched_sign:
                switched_sign = True
            else:
                raise Exception("Chi list switched sign twice. Aborting")
        elif np.sign(chis[i]) != np.sign(chis[i] - chis[i - 1]):
            raise Exception("Chi list is not in increasing absolute value. Aborting")
    return np.append(0, chis)

def try_load_json(filename):
    max_tries = 50
    while max_tries > 0:
        try:
            with open(filename) as f:
                p = json.load(f)
            return p
        except:
            print("Cannot open file. Waiting 1s...")
            time.sleep(1)
            max_tries -= 1
    raise exception("Error. Could not open file " + filename)

def try_load_h5(filename, access):
    max_tries = 50
    while max_tries > 0:
        try:
            f = h5.File(filename, access)
            return f
        except:
            print("Cannot open file. Waiting 5s...")
            time.sleep(5)
            max_tries -= 1
    raise exception("Error. Could not open file " + filename)

parser = argparse.ArgumentParser(description = "Bisection find constant curve")
subparsers = parser.add_subparsers(help="Sub-command help", required = True)
start_parser = subparsers.add_parser("start", help="Start bisection")
step_parser = subparsers.add_parser("step", help="Bisection step")
start_parser.set_defaults(func = start_bisection)
step_parser.set_defaults(func = bisection_step)

start_parser.add_argument("-p", "--parameters", help="Path to parameter file", required = True)
step_parser.add_argument("--sim_folder", help="Path to the sim folder", required = True)
step_parser.add_argument("--k_chi", type=int, help="Which chi id the step corresponds to", required=True)
step_parser.add_argument("-n", type=int, help = "How many steps we are on", default = 0)
args = parser.parse_args()
args.func()

