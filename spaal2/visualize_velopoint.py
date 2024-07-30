import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import simple_pcd_viewer as spv

from .velo_point import VeloPoint


def visualize(points: list[VeloPoint]):
    # pcd = o3d.geometry.PointCloud()
    # pcd.points = o3d.utility.Vector3dVector(np.array([[p.x, p.y, p.z] for p in points]))
    # cmap = plt.get_cmap("jet")
    # pcd.colors = o3d.utility.Vector3dVector(np.array([cmap(p.intensity)[:3] for p in points]))
    # o3d.visualization.draw_geometries([pcd])
    cmap = plt.get_cmap("jet")
    p = np.array([
        [p.x, p.y, p.z] for p in points
    ])
    c = np.array([
        cmap(p.intensity)[:3] for p in points
    ])
    rule = spv.single.PcdReadingRule(colorize_type=spv.single.ColorizeType.RGB)
    vis = spv.single.SingleFrameVisualizer(np.hstack([p,c]), rule=rule)
    vis.show(show_controller=False)
