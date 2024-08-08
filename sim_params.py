import numpy as np

sim_name = 'large_test'
set_name = 'settings'


single_weight_arr = np.linspace(0.46, 0.48, 5)
counter_weight_arr = np.linspace(0.4, 0.5, 2)
size_arr = np.logspace(np.log10(8), np.log10(100), 10, dtype=np.int32)

#(single_weight_t, 
# counter_weight_t, 
# size_t) = np.meshgrid(single_weight_arr, 
#                       counter_weight_arr, 
#                       size_arr)

(single_weight_t, 
 size_t) = np.meshgrid(single_weight_arr, 
                       size_arr)

counter_weight_t = single_weight_t

size = size_t.flatten()
single_weight = single_weight_t.flatten()
counter_weight = counter_weight_t.flatten()

size_x = size
size_y = size

mem_per_cpu = '500'
time_limit = '01:30:00'
devel = False

n_samples = 5
n_steps = 10 ** 10 * np.ones_like(size)
n_therm = 10 ** 10 * np.ones_like(size)

#size_x = 5
#size_y = 5
#single_weight = 0.5
#counter_weight = 0.4

windings = 1 * np.ones_like(size)
correlations = 1 * np.ones_like(size)
annulus_size = 0.1 * np.ones_like(size)
save_interval = 1000000 * np.ones_like(size)
time_series = 1 * np.ones_like(size)
