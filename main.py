# Member 2's preprocessing
from preprocessing.preprocess_lidar import (
    generate_synthetic_scan, remove_invalid_points, distance_filter,
    height_filter, voxel_downsample, remove_statistical_outliers
)
# Member 1's segmentation
from ml.semantic_segmentation import semantic_segmentation as ml_segmentation, class_counts
# Member 4's grid
from grid.adaptive_grid import adaptive_grid as build_adaptive_grid, points_from_arrays

# Member 3's updated visualization tools (including the new navigation map)
from visualization.lidar_visualization import (
    print_visualization_summary, 
    plot_adaptive_grid, 
    plot_25d_elevation, 
    plot_navigation_map,
    visualize_semantic
)


def load_data():
    print("1. Loading raw LiDAR data...")
    points, intensity = generate_synthetic_scan()
    return points, intensity


def preprocess(data):
    print("2. Preprocessing point cloud...")
    points, intensity = data
    points, intensity = remove_invalid_points(points, intensity)
    points, intensity = distance_filter(points, intensity, min_range=0.5, max_range=60.0)
    points, intensity = height_filter(points, intensity, z_min=-2.2, z_max=2.0)
    points, intensity = voxel_downsample(points, intensity, voxel_size=0.2)
    points, intensity = remove_statistical_outliers(points, intensity)
    return points, intensity


def semantic_segmentation(data):
    print("3. Performing semantic segmentation...")
    points, intensity = data
    labels = ml_segmentation(points)
    counts = class_counts(labels)
    print(f"   -> Found: {counts.get('Ground', 0)} Ground, {counts.get('Static Obstacle', 0)} Static")
    return points, labels


def terrain_analysis(data):
    print("4. Performing terrain analysis...")
    return data 


def adaptive_grid(data):
    print("5. Generating adaptive grid...")
    points_np, labels_np = data
    
    point_objects = points_from_arrays(points_np, labels_np)
    cells = build_adaptive_grid(point_objects)
    print(f"   -> Compressed {len(points_np)} points into {len(cells)} cells.")
    
    return points_np, labels_np, cells


def generate_2_5d_map(data):
    print("6. Generating 2.5D map...")
    return data


def visualize(data):
    print("7. Visualizing final map...")
    points, labels, cells = data
    
    print_visualization_summary(points, labels, cells)
    plot_adaptive_grid(cells, title="TERA PULSE - Adaptive Grid Map")
    plot_25d_elevation(cells, title="TERA PULSE - 2.5D Elevation Map")
    
    # NEW: Render Member 3's navigation/traversability map
    plot_navigation_map(cells, title="TERA PULSE - Navigation / Traversability Map")
    
    visualize_semantic(points, labels, window_name="TERA PULSE - 3D Semantic LiDAR")


def main():
    print("--- Starting TERA PULSE Pipeline ---")
    data1 = load_data()
    data2 = preprocess(data1)
    data3 = semantic_segmentation(data2)
    data4 = terrain_analysis(data3)
    data5 = adaptive_grid(data4)
    data6 = generate_2_5d_map(data5)
    visualize(data6)
    print("--- Pipeline Completed ---")


if __name__ == "__main__":
    main()