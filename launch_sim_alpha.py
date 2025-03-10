import numpy as np
import sim_params
import os
import h5py as h5
import subprocess

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

foldername = os.environ['SIM_PATH'] + sim_params.sim_name
log_folder_name = os.environ['LOG_PATH'] + sim_params.sim_name

def add_settings(filename, sim_params, windings, correlations, annulus_size, save_interval, time_series,
                 size_x, size_y, n_steps, n_therm, single_weight, counter_weight):
    with open(sim_params.__file__, "r+") as params_file:
            sim_params_string = params_file.read()
            
    with h5.File(filename, "w") as f:
        f[SIM_LOC] = os.environ['LOCATION']
        f.create_dataset(SIM_PARAMS_LOC, data=sim_params_string)

        f[WINDINGS_LOC] = np.uint8(windings)
        f[CORRELATIONS_LOC] = np.uint8(correlations)
        f[ANNULUS_SIZE_LOC] = np.float64(annulus_size)
        f[SAVE_INTERVAL_LOC] = np.int32(save_interval)
        f[TIME_SERIES_LOC] = np.uint8(time_series)

        f[SIZE_X_LOC] = np.int32(size_x)
        f[SIZE_Y_LOC] = np.int32(size_y)
        f[N_STEPS_LOC] = np.uint64(n_steps)
        f[N_THERM_LOC] = np.uint64(n_therm)
        f[SINGLE_WEIGHT_LOC] = np.float64(single_weight)
        f[COUNTER_WEIGHT_LOC] = np.float64(counter_weight)

if not os.path.isdir(foldername):
     os.mkdir(foldername)
     if os.environ['LOCATION'] == 'kraken' or os.environ['LOCATION'] == 'Tetralith':
        os.mkdir(log_folder_name)
else:
    raise OSError(4, 'Folder already exists')

for i in range(len(sim_params.size)):
    os.mkdir(foldername + "/" + str(i))
    settings_path = foldername + "/" + str(i) + '/' + sim_params.set_name + '.h5'
    add_settings(settings_path, sim_params, sim_params.windings[i], sim_params.correlations[i], 
                sim_params.annulus_size[i], sim_params.save_interval[i], sim_params.time_series[i],
                sim_params.size_x[i], sim_params.size_y[i], sim_params.n_steps[i], 
                sim_params.n_therm[i], sim_params.single_weight[i], sim_params.counter_weight[i])

if  os.environ['LOCATION'] == 'landau':
    for i in range(len(sim_params.size)):
        settings_path = foldername + "/" + str(i) + '/' + sim_params.set_name + '.h5'
        for j in range(sim_params.n_samples):
            filename = foldername + "/" + str(i) + '/' + str(j) + '.h5'
            subprocess.run(['build/release-conan/EFFBORR', '-o', filename, '-s', settings_path, '-r', str(j)]) 

elif os.environ['LOCATION'] == 'kraken':
    comm_list = [ "#!/bin/bash -l",
                    "#SBATCH -J " + sim_params.sim_name,
                    "#SBATCH --mem-per-cpu=" + sim_params.mem_per_cpu,
                    "#SBATCH --time=" + sim_params.time_limit,
                    "#SBATCH --clusters=kraken",
                    "#SBATCH --partition=all", 
                    "#SBATCH --output=" + log_folder_name + r"/%a.out",
                    "#SBATCH --error=" + log_folder_name + r"/%a.err",
                    "#SBATCH --array=0-" + str(len(sim_params.size) * sim_params.n_samples - 1),
                    "A=$((SLURM_ARRAY_TASK_ID/" + str(sim_params.n_samples) + "))",
                    "B=$((SLURM_ARRAY_TASK_ID%" + str(sim_params.n_samples) + "))",
                    "sleep $B",
                    "echo \"\n===========\nThis is job number $A, $B\"\n",
                    ("./build/release-conan/EFFBORR -g -o " + foldername + '/$A/$B.h5 -s ' 
                     + foldername + '/$A/' + sim_params.set_name + '.h5 -r $B')
                    ]

    # Writing the runfile
    run_file = open(f"srunfile.sh", "w")
    run_file.writelines("\n".join(comm_list))
    run_file.close()

    # Submitting runfile
    result_str = os.popen("sbatch srunfile.sh").read()
    job_id = result_str.split()[3]
    os.remove("srunfile.sh")

    comm_list_2 = comm_list[:-8] + ["#SBATCH --output=" + log_folder_name + "/sampling.out",
                                    "#SBATCH --error=" + log_folder_name + "/sampling.err",
                                    "#SBATCH --depend=afterok:" + job_id, "srun python ./sampling.py -f " + sim_params.sim_name]
    run_file = open(f"srunfile.sh", "w")
    run_file.writelines("\n".join(comm_list_2))
    run_file.close()
    os.system("sbatch srunfile.sh")
    os.remove("srunfile.sh")
    # Deleting runfile

elif os.environ['LOCATION'] == 'Tetralith':
    tet_path = "./build/tetralith/EFFBORR"
    if os.path.exists(tet_path):
        exe_path = tet_path
    else:
        exe_path = "./build/release-conan/EFFBORR"
    comm_list = [ "#!/bin/bash -l",
                    "#SBATCH -J " + sim_params.sim_name,
                    "#SBATCH --mem-per-cpu=" + sim_params.mem_per_cpu,
                    "#SBATCH --time=" + sim_params.time_limit,
                    "#SBATCH --output=" + log_folder_name + r"/%a.out",
                    "#SBATCH --error=" + log_folder_name + r"/%a.err",
                    "#SBATCH --array=0-" + str(len(sim_params.size) * sim_params.n_samples - 1),
                    "A=$((SLURM_ARRAY_TASK_ID/" + str(sim_params.n_samples) + "))",
                    "B=$((SLURM_ARRAY_TASK_ID%" + str(sim_params.n_samples) + "))",
                    "sleep $B",
                    "echo \"\n===========\nThis is job number $A, $B\"\n",
                    (exe_path + " -o " + foldername + '/$A/$B.h5 -s ' 
                     + foldername + '/$A/' + sim_params.set_name + '.h5 -r $B')
                    ]

    # Writing the runfile

    time_list = list(map(int, sim_params.time_limit.split(':')))
    time = time_list[0] * 3600 + time_list[1] * 60 + time_list[2]
    if (sim_params.devel and len(sim_params.size) * sim_params.n_samples <= 64 and time <= 3600):
        comm_list.insert(1, "#SBATCH --reservation=now")
    run_file = open(f"srunfile.sh", "w")
    run_file.writelines("\n".join(comm_list))
    run_file.close()

    # Submitting runfile
    result_str = os.popen("sbatch srunfile.sh").read()
    job_id = result_str.split()[3]
    os.remove("srunfile.sh")

    comm_list_2 = comm_list[:-11] + [ "#SBATCH -J " + sim_params.sim_name + '_pp',
                                    "#SBATCH --mem-per-cpu=2000",
                                    "#SBATCH --time=00:05:00", 
                                    "#SBATCH --output=" + log_folder_name + "/sampling.out",
                                    "#SBATCH --error=" + log_folder_name + "/sampling.err",
                                    "#SBATCH --depend=afterok:" + job_id, "srun python ./sampling.py -f " + sim_params.sim_name]
    run_file = open(f"srunfile.sh", "w")
    run_file.writelines("\n".join(comm_list_2))
    run_file.close()
    os.system("sbatch srunfile.sh")
    os.remove("srunfile.sh")
    
else:
    raise OSError(10, 'Unknown location')

