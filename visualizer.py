import matplotlib.pyplot as plt
import numpy as np

def visualize_points(points: np.ndarray):
    plt.figure(figsize=(10,10))
    ax = plt.subplot(111, polar=True)
    ax.scatter(points[:,0],points[:,1], s=1, c=plt.cm.jet(points[:,2] / 255))

    ax.set_rlim([0, 125])
    ax.set_thetalim([0,np.pi*2])
    plt.show()
