import open3d as o3d
import numpy as np

from semantic_segmentation import semantic_segmentation, class_counts


# Real LiDAR PCD file
pcd_path = "data/lidar/0001.pcd"
# Load point cloud
pcd = o3d.io.read_point_cloud(pcd_path)

# Convert Open3D points to NumPy array
points = np.asarray(pcd.points)

print("Total points:", len(points))

# Run semantic segmentation
labels = semantic_segmentation(points)

# Count each class
counts = class_counts(labels)

print("\nSegmentation Result:")
for name, count in counts.items():
    print(f"{name}: {count}")

print("\nLabels shape:", labels.shape)