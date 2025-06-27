import numpy as np
import matplotlib.pyplot as plt
import h5py as h5










filename = "../data/bis.h5"
f = h5.File(filename, "r")
print(f.keys())
