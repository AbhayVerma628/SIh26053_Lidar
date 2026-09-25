import open3d as o3d
import numpy as np

from semantic_segmentation import semantic_segmentation


# Real LiDAR file
pcd_path = "data/lidar/0001.pcd"

# Load point cloud
pcd = o3d.io.read_point_cloud(pcd_path)

# Convert to NumPy
points = np.asarray(pcd.points)

print("Total points:", len(points))

# Semantic segmentation
labels = semantic_segmentation(points)

# Create colors for each class
colors = np.zeros((len(points), 3))

colors[labels == 0] = [0.2, 0.8, 0.2]   # Ground
colors[labels == 1] = [0.9, 0.2, 0.2]   # Static obstacle
colors[labels == 2] = [0.2, 0.4, 1.0]   # Dynamic candidate
colors[labels == 3] = [0.6, 0.6, 0.6]   # Unknown

# Apply colors
pcd.colors = o3d.utility.Vector3dVector(colors)

# Show semantic point cloud
o3d.visualization.draw_geometries(
    [pcd],
    window_name="Semantic LiDAR Visualization"
)