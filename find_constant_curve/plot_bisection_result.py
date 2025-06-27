import numpy as np
import matplotlib.pyplot as plt
import h5py as h5
import matplotlib.tri as mtri
from mpl_toolkits.mplot3d import Axes3D


filename = "../data/bis1.h5"
f = h5.File(filename, "r")
n_points_P = 0
n_points_S = 0
for key in f.keys():
    if key != "sym":
        n_points_P += len(f[key]["Ps"][()])
        n_points_S += len(f[key]["S"][()])
        if n_points_P != n_points_S:
            raise ValueError("Number of points P and S do not match for chi = " + str(f[key]["chi"][()]))

P = np.zeros(n_points_P)
chi = np.zeros(n_points_P)
S = np.zeros(n_points_P)
S_err = np.zeros(n_points_P)
i = 0

for key in f.keys():
    if key != "sym":
        for j in range(len(f[key]["Ps"])):
            P[i] = f[key]["Ps"][()][j]
            S[i] = f[key]["S"][()][j]
            chi[i] = f[key]["chi"][()]
            S_err[i] = f[key]["S_err"][()][j]
            i += 1
#print(P)
#print(chi)
#print(S)
#rint(S_err)


triang = mtri.Triangulation(P, chi)

fig = plt.figure(figsize=(16, 10))
ax = fig.add_subplot(1,1,1, projection='3d')

ax.plot_trisurf(triang, S, cmap='jet')
ax.scatter(P,chi,S, marker='.', s=10, c="black", alpha=0.5)
ax.view_init(elev=60, azim=-45)

ax.set_xlabel('P')
ax.set_ylabel('chi')
ax.set_zlabel('S')

fig_err = plt.figure(figsize=(16, 10))
ax_err = fig_err.add_subplot(1,1,1, projection='3d')

ax_err.plot_trisurf(triang, S_err, cmap='jet')
ax_err.scatter(P,chi,S_err, marker='.', s=10, c="black", alpha=0.5)
ax_err.view_init(elev=60, azim=-45)

ax_err.set_xlabel('P')
ax_err.set_ylabel('chi')
ax_err.set_zlabel('S_err')
plt.show()
