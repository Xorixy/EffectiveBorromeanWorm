import numpy as np
import matplotlib.pyplot as plt
import h5py as h5


def get_chi(array):
    #Returns the autocorrelation function of the array
    z = array - np.mean(array)
    rfs = np.fft.rfft(z, 2*len(z))
    chi = np.fft.irfft(rfs*np.conj(rfs), 2*len(z))
    return chi[:len(z)]

def sokal_int_tau(chi):
    #The integrated autocorrelation time is analytically tau = int_0^inf chi(t) dt
    #The problem with doing this however is that the tail of chi(t) has relatively big fluctuations which makes this formula bad to use in practice
    #Therefore we slightly modify our formula to tau = int_0^C*tau chi(t) dt, so that we ignore the big tail.
    #For large enough C this will essentially give the same value analytically but is much more well-behaved.
    c = 10
    M = 1
    tau = chi[0]/chi[0]
    while M < c*tau:
        tau += chi[M]/chi[0]
        M += 1

    return tau

def find_tau(array, step):
    kstep = 10000
    taus = np.array([])
    k0 = 10
    k = k0
    while k*kstep < len(array):
        print(k*kstep)
        taus = np.append(taus, sokal_int_tau(get_chi(array[:k*kstep])))
        k += 1

    print(len(np.arange(k0*kstep, k*kstep, kstep)))
    print(len(taus))

    #This plots the ratio between number of timesteps used in the calculation of tau and tau.
    plt.plot(step*np.arange(k0*kstep, k*kstep, kstep), np.arange(k0*kstep, k*kstep, kstep)/taus)
    plt.title("#steps/tau")
    plt.figure()
    #This plots tau as a function of the number of timesteps used in the calculation of tau
    plt.plot(step*np.arange(k0*kstep, k*kstep, kstep), step*taus)
    plt.title("tau")
    plt.ylim(0, 1.1*np.max(taus*step))
    plt.show()


f = h5.File("build/release-conan/simulation.h5")
print(f.keys())
windings = f['data/windings'][:]
total_bonds = f['data/total_bonds'][:]
print(total_bonds)
save_interval = 1000
t_max = len(total_bonds[:,0])
print(t_max)
t = np.linspace(0, t_max-1, t_max)*save_interval

windings_1x = windings[:,0]
chi = get_chi(windings_1x[:])
plt.plot(t, chi/chi[0])
plt.plot(t, np.exp(-t/(sokal_int_tau(chi)*save_interval)))
print(sokal_int_tau(chi)*save_interval)

"""
plt.plot(t, windings[:,0])
plt.plot(t, windings[:,2])
plt.figure()
plt.plot(t, windings[:,1])
plt.plot(t, windings[:,3])
plt.figure()
plt.plot(t, total_bonds[:,0])
plt.plot(t, total_bonds[:,1])
"""
plt.show()
