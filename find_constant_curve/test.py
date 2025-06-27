import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from mpl_toolkits.mplot3d import Axes3D



points = 500
data = np.zeros([points,3])
seed = 0
np.random.seed(seed)
x = np.random.rand(points)*100
y = np.random.rand(points)*100
z = np.sinc((x-20)/100*3.14) + np.sinc((y-50)/100*3.14)

if points == 9:
    x = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
    y = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])

fig1 = plt.figure()
ax1 = fig1.add_subplot(1,1,1)

ax1.scatter(x, y, marker=".", c="#DC143C", edgecolors="black", s=100)
ax1.set_xlabel('X')
ax1.set_ylabel('Y')


triang = mtri.Triangulation(x, y)

fig2 = plt.figure()
ax2 = fig2.add_subplot(1,1,1)

ax2.triplot(triang, c="#D3D3D3", marker='.', markerfacecolor="#DC143C",
           markeredgecolor="black", markersize=10)

ax2.set_xlabel('X')
ax2.set_ylabel('Y')

fig = plt.figure()
ax = fig.add_subplot(1,1,1, projection='3d')

ax.plot_trisurf(triang, z, cmap='jet')
ax.scatter(x,y,z, marker='.', s=10, c="black", alpha=0.5)
ax.view_init(elev=60, azim=-45)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()

