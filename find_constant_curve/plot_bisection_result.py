import numpy as np
import matplotlib.pyplot as plt
import h5py as h5
import matplotlib.tri as mtri
from mpl_toolkits.mplot3d import Axes3D


def get_points_from_sim(filename):
    f = h5.File(filename, "r")
    n_points_P = 0
    n_points_S = 0
    for key in f.keys():
        if key != "sym":
            n_points_P += len(f[key]["Ps"][()])
            n_points_S += len(f[key]["S"][()])
            if n_points_P != n_points_S:
                print(f[key]["Ps"][()])
                print(f[key]["S"][()])
                raise ValueError("Number of points P and S do not match for chi = " + str(f[key]["chi"][()]))
            print(f[key]["chi"][()])
            print(f[key]["Ps"][()])

    P = np.zeros(n_points_P)
    chi = np.zeros(n_points_P)
    S = np.zeros(n_points_P)
    S_err = np.zeros(n_points_P)
    i = 0
    P_bis = np.array([])
    chi_bis = np.array([])
    target_S = f["sym/S"][()]
    P_sym = f["sym/P"][()]
    for key in f.keys():
        if key != "sym":
            for j in range(len(f[key]["Ps"])):
                P[i] = f[key]["Ps"][()][j]
                S[i] = f[key]["S"][()][j]
                chi[i] = f[key]["chi"][()]
                S_err[i] = f[key]["S_err"][()][j]
                i += 1
                if j != 0:
                    sign_prev = np.sign(f[key]["S"][()][j-1] - target_S)
                    sign_next = np.sign(f[key]["S"][()][j]   - target_S)
                    if sign_prev != sign_next:
                        P0 = f[key]["Ps"][()][j - 1] + (target_S - f[key]["S"][()][j - 1])*(f[key]["Ps"][()][j] - f[key]["Ps"][()][j - 1])/(f[key]["S"][()][j] - f[key]["S"][()][j - 1])
                        P_bis = np.append(P_bis, P0)
                        chi_bis = np.append(chi_bis, f[key]["chi"][()])


    return P, chi, S, S_err, P_bis, chi_bis, P_sym, target_S

def plot_res(P, chi, S, S_err, P_bis, chi_bis, P_sym, target_S):
    S_min = 0
    S_max = 1
    indices = (S_min < S) & (S < S_max)
    P = P[indices]
    chi = chi[indices]
    S = S[indices]
    S_err = S_err[indices]

    triang = mtri.Triangulation(P, chi)

    fig_cont = plt.figure(figsize=(16, 10))
    ax_cont = fig_cont.add_subplot(1,1,1)
    ax_cont.tricontour(P, chi, S, levels=14, linewidths=0.5, colors='k')
    cntr2 = ax_cont.tricontourf(P, chi, S, levels=14, cmap="RdBu_r")
    ax_cont.scatter(P,chi, marker='.', s=10, c="black", alpha=0.5)
    ax_cont.scatter(P_bis, chi_bis, marker='.', s=15, c='green')
    ax_cont.scatter(P_sym, 0, marker='.', s=15, c='red')
    ax_cont.set_xlabel('P')
    ax_cont.set_ylabel('chi')
    ax_cont.set_ylim(1.1*np.array([np.min(chi), np.max(chi)]))

    return

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

    fig_rerr = plt.figure(figsize=(16, 10))
    ax_rerr = fig_rerr.add_subplot(1,1,1, projection='3d')


    ax_rerr.plot_trisurf(triang, S_err/S, cmap='jet')
    ax_rerr.scatter(P,chi,S_err/S, marker='.', s=10, c="black", alpha=0.5)
    ax_rerr.view_init(elev=60, azim=-45)

    ax_rerr.set_xlabel('P')
    ax_rerr.set_ylabel('chi')
    ax_rerr.set_zlabel('S_err/S')


def plot_bisection_result(filenames):
    P = np.array([])
    chi = np.array([])
    S = np.array([])
    S_err = np.array([])
    P_bis = np.array([])
    chi_bis = np.array([])
    P_sym = 0
    target_S = 0
    for filename in filenames:
        P_sim, chi_sim, S_sim, S_err_sim, P_bis_sim, chi_bis_sim, P_sym, target_S = get_points_from_sim(filename)
        P = np.append(P, P_sim)
        chi = np.append(chi, chi_sim)
        S = np.append(S, S_sim)
        S_err = np.append(S_err, S_err_sim)
        P_bis = np.append(P_bis, P_bis_sim)
        chi_bis = np.append(chi_bis, chi_bis_sim)

    plot_res(P, chi, S, S_err, P_bis, chi_bis, P_sym, target_S)
    plt.show()


#filenames = ["../data/bis_test4.h5", "../data/bis_test5.h5"]
#filenames = ["../data/bis_bid3.h5"]
filenames = ["../data/bis_50_2.h5"]

plot_bisection_result(filenames)


