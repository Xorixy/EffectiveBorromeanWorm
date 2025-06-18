import datetime
import os
from sys import executable
import subprocess

class BatchScript:

    def __init__(self):
        self.job_name = None
        self.output_name = None
        self.run_time = None
        self.array_start = None
        self.array_end = None
        self.command = None
        self.memory = None
        self.reservation = None
        self.nodes = 1
        self.ntasks = 1
        self.cpu_per_task = 1
        self.openmp = False

    def set_job_name(self, job_name):
        self.job_name = job_name

    def set_output_name(self, output_name):
        self.output_name = output_name

    #Sets run time in seconds
    def set_run_time(self, run_time):
        run_time = int(run_time + 1)
        hours = run_time // 3600
        run_time = run_time % 3600
        minutes = run_time // 60
        seconds = run_time % 60
        self.run_time = f"{hours}:{minutes}:{seconds}"
        print(self.run_time)

    def set_array_start(self, array_start):
        self.array_start = array_start

    def set_array_end(self, array_end):
        self.array_end = array_end

    def set_command(self, command):
        self.command = command

    def set_memory(self, memory):
        self.memory = memory

    def set_reservation(self, reservation):
        self.reservation = reservation

    def set_openmp(self, openmp):
        self.openmp = openmp

    def set_ntasks(self, ntasks):
        self.ntasks = ntasks

    def set_cpu_per_task(self, cpu_per_task):
        self.cpu_per_task = cpu_per_task

    def create_batch_script(self):
        if self.job_name is None or self.command is None or self.run_time is None or self.output_name is None:
            raise Exception("Error, not all required parameters are set")
        with open(f'{self.job_name}.slurm', "x") as script:
            script.write("#!/bin/bash\n")
            script.write(f"#SBATCH --job-name={self.job_name}\n")
            script.write(f"#SBATCH --output={self.output_name}/log/log_%a.txt\n")
            script.write(f"#SBATCH --error={self.output_name}/err/err_%a.txt\n")
            script.write(f"#SBATCH --time={self.run_time}\n")
            script.write(f"#SBATCH --nodes={self.nodes}\n")
            script.write(f"#SBATCH --ntasks={self.ntasks}\n")
            script.write(f"#SBATCH --cpus-per-task={self.cpu_per_task}\n")
            if self.array_start is not None and self.array_end is not None:
                script.write(f"#SBATCH --array={self.array_start}-{self.array_end}\n")
            if self.reservation is not None:
                script.write(f"#SBATCH --reservation={self.reservation}\n")
            if self.memory is not None:
                script.write(f"#SBATCH --mem={self.memory}\n")
            if self.openmp is True:
                script.write("export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK\n")

            script.write(self.command)

    def run_batch(self):
        try:
            self.create_batch_script()
        except Exception as e:
            print("Failed to create batch script")
            print(e)
            return
        out = None
        try:
            out = subprocess.run(["sbatch", f'{self.job_name}.slurm'], capture_output=True)
            out = out.stdout.decode()
        except Exception as e:
            print("Script failed to launch")
            print(e)
        os.remove(f'{self.job_name}.slurm')
        return out