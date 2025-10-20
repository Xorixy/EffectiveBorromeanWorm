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

def is_valid_distance(s1, s2, err1, err2, tol_factor):
    return np.abs(s1 - s2) > tol_factor*(err1 + err2)
def find_bis_edges(p, s, s_err, st, st_err, tol_factor):
    edges = np.array([])
    print(f"Target S : {st} +- {tol_factor} * {st_err}")
    for i in range(1,len(s)):
        sign_prev = np.sign(s[i-1] - st)
        sign_next = np.sign(s[i] - st)
        if sign_prev != sign_next:
            print("Edge found :")
            print(f"P : {p[i-1]} , S : {s[i-1]} +- {tol_factor} * {s_err[i-1]}")
            print(f"P : {p[i]} , S : {s[i]} +- {tol_factor} * {s_err[i]}")
            if is_valid_distance(s[i], st, s_err[i], st_err, tol_factor) and is_valid_distance(s[i - 1], st, s_err[i - 1], st_err, tol_factor):
                if len(edges) == 0:
                    edges = np.array([[i-1, i]])
                else:
                    edges = np.append(edges, [[i-1, i]], axis=0)
            else:
                print("Edge equals target S within tolerance.")

    return edges

def start_bisection():
    print("Starting bisection")
    print("Reading parameter file...")
    p = try_load_json(args.parameters)
    print(p["sim_folder"])
    sim_folder = p["sim_folder"]
    print("Creating folders...")
    if os.path.isdir(sim_folder):
        if not args.cont:
            raise Exception("Sim folder already exists")
    elif args.cont:
        raise Exception("Sim folder doesn't exist and cont flag was given")
    chis = get_chi_list(p)
    if not args.cont:
        os.makedirs(sim_folder)
        os.makedirs(sim_folder + "/sim/sym")
        for i in range(len(chis)):
            os.makedirs(sim_folder + "/sim/" + str(i))
        p["chis"] = chis.tolist()
        print("Writing parameters file")
        with open(sim_folder + "/params.json", "w") as f:
            json.dump(p, f, indent=4)
        print("Copying python files")
        python_file = p["python_file"]
        shutil.copyfile(python_file, sim_folder + "/bisection.py")
        batch_file = p["batch_file"]
        shutil.copyfile(batch_file, sim_folder + "/batch.py")
    else:
        old_params = try_load_json(sim_folder + "/params.json")
        old_chis = get_chi_list(old_params)
        chis = np.append(old_chis, chis).tolist()
        old_params["chis"] = chis
        with open(sim_folder + "/params.json", "w") as f:
            json.dump(old_params, f, indent=4)
        p = try_load_json(sim_folder + "/params.json")
    exec_loc = p["exec_loc"]
    size = p["size"]
    P_sym = p["P_sym"]
    n_steps = p["n_steps"]
    n_therm = p["n_therm"]
    counter_chi_factor = p["counter_chi_factor"]
    print(f"Estimated runtime : {estimate_run_time(n_steps, n_therm)}s")
    if not args.cont:
        print("Launching sym step")
        n_parallel = p["n_parallel"]
        n_array_sym = p["n_array_sym"]
        res = try_load_h5(sim_folder + "/result.h5", "x")
        res.attrs["size"] = size
        res.create_group("sym")
        res["sym"].attrs["P"] = P_sym
        sym_id = launch_array(sim_folder + "/sim/sym", size, P_sym, 0, n_steps, n_therm, counter_chi_factor, n_parallel, n_array_sym, exec_loc, 0, True, 'sym')
        launch_sym_step(sym_id, sim_folder)
        res.flush()
        res.close()
    else:
        print("Launching chi steps")
        for i in range(len(old_chis), len(chis)):
            start_new_chi_step(p, i)


def sym_step():
    print("Sym step")
    print("Reading parameter file...")
    p = try_load_json(args.sim_folder + "/params.json")
    sim_folder = p["sim_folder"]
    size = p["size"]
    n_parallel = p["n_parallel"]
    n_array_sym = p["n_array_sym"]
    print("Opening res file...")
    res = try_load_h5(sim_folder + "/result.h5", "r+")
    print("Collecting sym data...")
    S_mean, S_var = get_sim_result(sim_folder + "/sim/sym/out/out", n_array_sym*n_parallel, size, 0)
    res["sym"].attrs["S"] = S_mean
    res["sym"].attrs["S_err"] = np.sqrt(S_var)
    print("Done")
    print("Launching bisection steps")
    chis = get_chi_list(p)
    for i in range(len(chis)):
        start_new_chi_step(p, i)
    res.flush()
    res.close()
def bisection_step():
    print("Bisection step")
    p = try_load_json(args.sim_folder + "/params.json")
    print(p["sim_folder"])
    sim_folder = p["sim_folder"]
    size = p["size"]
    n_parallel = p["n_parallel"]
    n_array = p["n_array"]
    n_array_sym = p["n_array_sym"]
    res = try_load_h5(sim_folder + "/result.h5", "r+")
    k_chi = args.k_chi
    print("k_chi = ", k_chi)
    if k_chi == -1:
        print("Collecting sym data")
        S_mean, S_var = get_sim_result(sim_folder + "/sim/sym/out/out", n_parallel*n_array_sym, size, 0)
        res["sym"].attrs["S"] = S_mean
        res["sym"].attrs["S"] = np.sqrt(S_var)
        print("Done")
    else:
        print("Continuing bisection")
        continue_chi_step(p, k_chi)
    res.flush()
    res.close()

def continue_chi_step(parameters, k_chi):
    n = args.n
    print(f"Bisection step : {n}")
    sim_folder = parameters["sim_folder"]
    size = parameters["size"]
    n_steps = parameters["n_steps"]
    n_therm = parameters["n_therm"]
    n_parallel = parameters["n_parallel"]
    n_array = parameters["n_array"]
    n_P_parallel = parameters["n_P_parallel"]
    exec_loc = parameters["exec_loc"]
    counter_chi_factor = parameters["counter_chi_factor"]
    tol = parameters["tol"]
    res = try_load_h5(sim_folder + f"/result_{k_chi}.h5", "r+")
    print(f"Running step for chi {k_chi}")
    chis = get_chi_list(parameters)
    chi = chis[k_chi]
    target_S = res["sym"].attrs["S"]
    n_P = res[str(k_chi)].attrs["n_P"]
    n_S = res[str(k_chi)].attrs["n_S"]
    n_bis = res[str(k_chi)].attrs["n_bis"]
    P = res[str(k_chi) + "/P"][()][:n_P]
    S = res[str(k_chi) + "/S"][()][:n_S]
    S_err = res[str(k_chi) + "/S_err"][()][:n_S]
    print("Data found in res file:")
    print("P : ", P)
    print("S : ", S)
    print("S_err : ", S_err)
    print("n_P : ", n_P)
    print("n_S : ", n_S)
    sim_P = P[len(S):]
    sim_S, sim_S_var = get_sim_array_result(sim_folder + f"/sim/{k_chi}/out/out", n_parallel*n_array, size, sim_P)
    S = np.append(S, sim_S)
    S_err = np.append(S_err, np.sqrt(sim_S_var))
    sort = P.argsort()
    P = P[sort]
    S = S[sort]
    S_err = S_err[sort]
    n_S = len(S)
    if len(S) != len(S_err):
        raise ValueError("Error : numer of S is not equal to number of S_err")
    print("Writing to file:")
    print("S : ", S)
    print("n_S :", n_S)
    file_S = res[str(k_chi) + "/S"][...]
    res[str(k_chi)].attrs["n_S"] = n_S
    res.flush()
    file_S[:n_S] = S
    res[str(k_chi) + "/S"][...] = file_S
    res.flush()
    print("S_err : ", S_err)
    file_S_err = res[str(k_chi) + "/S_err"][...]
    file_S_err[:n_S] = S_err
    res[str(k_chi) + "/S_err"][...] = file_S_err
    res.flush()
    finished = False
    if len(P) == 1:
        print("Only P_min simulated. Running step for P_max so that bisection can start")
        P_max = parameters["P_max"]
        new_P = np.array([P_max])
        P = np.append(P, P_max)
        print("Writing to file:")
        print("P : ", P)
        n_P = len(P)
        print("n_P : ", n_P)
        res[str(k_chi)].attrs["n_P"] = n_P
        res.flush()
        file_P = res[str(k_chi) + "/P"][...]
        file_P[:n_P] = P
        res[str(k_chi) + "/P"][...] = file_P
        res.flush()
        sim_ids = launch_step_array(sim_folder + f"/sim/{k_chi}", size, new_P, chi, n_steps, n_therm, counter_chi_factor, n_parallel, n_array, exec_loc, str(k_chi))
        launch_bisection_step(sim_ids, sim_folder, k_chi, n + 1)
    else:
        edges = find_bis_edges(P, S, S_err, target_S, 0, tol)
        if n_bis < n:
            print(f"All bisections done.\n{n - 1}/{n_bis} bisection steps performed in total.")
            finished = True
        elif len(edges) == 0:
            print(f"No edge found or bisection done to target precision.\n{n - 1}/{n_bis} bisection steps performed in total.")
            finished = True
        else:
            print(f'Target S : {target_S}')
            print(f"Following edges found:")
            for edge in edges:
                print(f"(P = {P[edge[0]]}, S = {S[edge[0]]}), (P = {P[edge[1]]}, S = {S[edge[1]]})")
            print(f"Launching new bisection step")
            new_P = np.array([])
            for edge in edges:
                new_P = np.append(new_P, get_P_step(P[edge[0]], P[edge[1]], n_P_parallel))
            P = np.append(P, new_P)
            print("New P to simulate:")
            print(new_P)
            print(P)
            n_P = len(P)
            res[str(k_chi)].attrs["n_P"] = n_P
            res.flush()
            print(n_P)
            file_P = res[str(k_chi) + "/P"][...]
            print("len(file_P) : ")
            print(len(file_P))
            file_P[:n_P] = P
            res[str(k_chi) + "/P"][...] = file_P
            res.flush()
            sim_ids = launch_step_array(sim_folder + f"/sim/{k_chi}", size, new_P, chi, n_steps, n_therm, counter_chi_factor, n_parallel, n_array, exec_loc, str(k_chi))
            launch_bisection_step(sim_ids, sim_folder, k_chi, n + 1)
    res.flush()
    if finished:
        sym = try_load_h5(sim_folder + "/result.h5", "r+")
        res.copy(res[str(k_chi)], sym, str(k_chi))
        sym.flush()
        sym.close()
    res.close()



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
    P_max = parameters["P_max"]
    P_min = parameters["P_min"]
    n_steps = parameters["n_steps"]
    n_therm = parameters["n_therm"]
    n_parallel = parameters["n_parallel"]
    n_array = parameters["n_array"]
    n_bis = parameters["n_bis"]
    n_P_parallel = parameters["init_n_P_parallel"] - 2
    exec_loc = parameters["exec_loc"]
    counter_chi_factor = parameters["counter_chi_factor"]
    sym = try_load_h5(sim_folder + "/result.h5", "r+")
    target_S = sym["sym"].attrs["S"]
    print(f"Starting bisection for chi {k_chi}")
    chis = get_chi_list(parameters)
    chi = chis[k_chi]
    P = np.array([P_min])
    if n_P_parallel <= 0:
        n_P_parallel = 1
        P = get_P_init(P_min, P_max, n_P_parallel)
    print(P)
    print(P + chi)
    print(P - counter_chi_factor*chi)
    np_max = n_P_parallel + (n_P_parallel == 1) + n_bis*parameters["n_P_parallel"]
    print("np_max : ", np_max)
    sim_ids = launch_step_array(sim_folder + f"/sim/{k_chi}", size, P, chi, n_steps, n_therm, counter_chi_factor, n_parallel, n_array, exec_loc, str(k_chi))
    res = try_load_h5(sim_folder + f"/result_{k_chi}.h5", "x")
    res.create_group("sym")
    res["sym"].attrs["S"] = target_S
    res.create_group(str(k_chi))
    res.flush()
    zeros = np.zeros(np_max)
    print("zeros : ", zeros)
    res.create_dataset(str(k_chi) + "/P", data=zeros)
    res.flush()
    new_P = zeros
    new_P[:len(P)] = P
    print("Saving Ps : ", P)
    res[str(k_chi) + "/P"][...] = new_P
    res.flush()
    res[str(k_chi)].attrs["n_P"] = len(P)
    res.flush()
    res[str(k_chi)].attrs["n_bis"] = n_bis
    res.flush()
    res.create_dataset(str(k_chi) + "/S", data=zeros)
    res.flush()
    res[str(k_chi)].attrs["n_S"] = 0
    res.flush()
    res.create_dataset(str(k_chi) + "/S_err", data=zeros)
    res.flush()
    res[str(k_chi)].attrs["chi"] = chi
    res.flush()
    launch_bisection_step(sim_ids, sim_folder, k_chi, 1)
    res.close()

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

def get_P_init(P_min, P_max , n_P_parallel):
    return np.linspace(P_min, P_max, n_P_parallel + 2)

def get_P_step(P_min, P_max, n_P_parallel):
    return get_P_init(P_min, P_max, n_P_parallel)[1:-1]

def launch_bisection_step(prev_ids, sim_folder, k_chi, n):
    s = BatchScript()
    s.set_job_name(f"effborr-bisection-step-{k_chi}")
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

def launch_sym_step(prev_ids, sim_folder):
    s = BatchScript()
    s.set_job_name("effborr-sym-step")
    s.set_output_name(sim_folder)
    s.set_run_time(3600)
    s.set_verbose(True)
    s.set_log_name("sym")
    command = "python3 " + sim_folder + "/bisection.py" + " sym " + "--sim_folder " + sim_folder
    print("Launching bisection step with command : ")
    print(command)
    s.set_dependency(f"afterany:{prev_ids}")
    s.set_command(command)
    s.run_batch()

def launch_step_array(loc, size, P, chi, n_steps, n_therm, counter_chi_factor, n_parallel, n_array, exec_loc, name):
    sim_ids = ""
    new_folder = True
    for i in range(len(P)):
        sim_id = str(launch_array(loc, size, P[i], chi, n_steps, n_therm, counter_chi_factor, n_parallel, n_array, exec_loc, i*n_array, new_folder, name))
        if sim_id is not None:
            if sim_ids == "":
                sim_ids = sim_id
            else:
                sim_ids += ","
                sim_ids += sim_id
        new_folder = False
    return sim_ids

def launch_array(loc, size, P, chi, n_steps, n_therm, counter_chi_factor, n_parallel, n_array, exec_loc, array_start, new_folder, name):
    settings_loc = loc + "/settings" + str(array_start) + ".h5"
    create_settings_file(settings_loc, size, P, chi, n_steps, n_therm, counter_chi_factor)
    s = BatchScript()
    s.set_job_name(f"effborr-bisection-{name}")
    s.set_array_start(array_start)
    s.set_array_end(array_start + n_array - 1)
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

    s.set_ntasks(n_parallel)

    parallel_string = ""
    for i in range(n_parallel):
        parallel_string += f"{i} "

    out_loc += "/out"
    command = "parallel " + exec_loc + " -s " + settings_loc + " -o " + out_loc + " --array --n_parallel " + str(n_parallel) + " -r {1} ::: " + parallel_string
    s.set_command(command)
    return s.run_batch()

def create_settings_file(settings_loc, size, P, chi, n_steps, n_therm, counter_chi_factor):
    with h5.File(settings_loc, "w") as f:
        f["settings/save/windings"] = True
        f["settings/save/correlations"] = False
        f["settings/save/time_series"] = False

        f["settings/sim/size_x"] = np.int32(size)
        f["settings/sim/size_y"] = np.int32(size)
        f["settings/sim/n_steps"] = np.uint64(n_steps)
        f["settings/sim/n_therm"] = np.uint64(n_therm)
        f["settings/sim/single_weight"] = np.float64(P + chi)
        f["settings/sim/counter_weight"] = np.float64(P - counter_chi_factor*chi)

        f["settings/save/annulus_size"] = np.float64(0.5)
        f["settings/save/save_interval"] = np.int32(1)

def get_sim_array_result(outfile, n_sims, size, P):
    S_means = np.zeros(len(P))
    S_vars  = np.zeros(len(P))
    for i in range(len(P)):
        S_mean, S_var = get_sim_result(outfile, n_sims, size, i*n_sims)
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
        chi_min = params["chi_min"]
        chis = np.linspace(chi_min, chi_max, n_chis)[:]
    return np.unique(chis)

def try_load_json(filename):
    max_tries = 50
    while max_tries > 0:
        try:
            with open(filename) as f:
                p = json.load(f)
            return p
        except Exception as e:
            print(f"Cannot open file, error {e}.\nWaiting 5s...")
            time.sleep(1)
            max_tries -= 1
    raise Exception("Error. Could not open file " + filename)

def try_load_h5(filename, access):
    max_tries = 50
    while max_tries > 0:
        try:
            f = h5.File(filename, access)
            return f
        except Exception as e:
            t_wait = 5
            print(f"Cannot open file, error {e}.\nWaiting {t_wait}s...")
            time.sleep(t_wait)
            max_tries -= 1
    raise Exception("Error. Could not open file " + filename)

parser = argparse.ArgumentParser(description = "Bisection find constant curve")
subparsers = parser.add_subparsers(help="Sub-command help", required = True)
start_parser = subparsers.add_parser("start", help="Start bisection")
step_parser = subparsers.add_parser("step", help="Bisection step")
sym_parser = subparsers.add_parser("sym", help="Sym step")
start_parser.set_defaults(func = start_bisection)
step_parser.set_defaults(func = bisection_step)
sym_parser.set_defaults(func = sym_step)

start_parser.add_argument("-p", "--parameters", help="Path to parameter file", required = True)
start_parser.add_argument("--cont", action="store_true", help="If this flag is given then we continue a previous bisection with new chis")
step_parser.add_argument("--sim_folder", help="Path to the sim folder", required = True)
step_parser.add_argument("--k_chi", type=int, help="Which chi id the step corresponds to", required=True)
step_parser.add_argument("-n", type=int, help = "How many steps we are on", default = 0)
sym_parser.add_argument("--sim_folder", help="Path to the sim folder", required = True)
args = parser.parse_args()
args.func()

