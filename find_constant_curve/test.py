import numpy as np
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

a = np.array([1, 2, 3, 4, 5, -1, -2, -3, -4, -5])
print(a)
for i in range(len(a)):
    print(f"{i}: {a[i]} : {get_prev_k_chis(a, i)}")