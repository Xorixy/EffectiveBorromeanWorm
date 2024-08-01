import numpy as np

sim_name = 'test_l1'
set_name = 'settings'


single_weight_arr = np.linspace(0.4, 0.6, 2)
counter_weight_arr = np.linspace(0.5, 0.5, 1)
size_arr = np.linspace(40, 40, 1)

(single_weight_t, 
 counter_weight_t, 
 size_t) = np.meshgrid(single_weight_arr, 
                       counter_weight_arr, 
                       size_arr)

size = size_t.flatten()
single_weight = single_weight_t.flatten()
counter_weight = counter_weight_t.flatten()

size_x = size
size_y = size

mem_per_cpu = '500'
time_limit = '00:10:00'

n_samples = 2
n_steps = 100000000 * np.ones_like(size)
n_therm = 100000000 * np.ones_like(size)

#size_x = 5
#size_y = 5
#single_weight = 0.5
#counter_weight = 0.4

windings = 1 * np.ones_like(size)
correlations = 0 * np.ones_like(size)
annulus_size = 0.1 * np.ones_like(size)
save_interval = 1000000 * np.ones_like(size)
time_series = 1 * np.ones_like(size)