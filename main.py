from preprocessing.preprocess_lidar import (
    generate_synthetic_scan,
    remove_invalid_points,
    distance_filter,
    height_filter,
    voxel_downsample,
    remove_statistical_outliers
)

def load_data():
    print("1. Loading raw LiDAR data...")
    points, intensity = generate_synthetic_scan()
    print(f"   -> Successfully loaded {len(points)} raw points.")
    return points, intensity


def preprocess(data):
    print("2. Preprocessing point cloud...")
    points, intensity = data
    
    points, intensity = remove_invalid_points(points, intensity)
    points, intensity = distance_filter(points, intensity, min_range=0.5, max_range=60.0)
    points, intensity = height_filter(points, intensity, z_min=-2.2, z_max=2.0)
    points, intensity = voxel_downsample(points, intensity, voxel_size=0.2)
    points, intensity = remove_statistical_outliers(points, intensity)
    
    print(f"   -> Cleaned and downsampled to {len(points)} points.")
    return points, intensity


def semantic_segmentation(data):
    print("3. Performing semantic segmentation...")
    return data


def terrain_analysis(data):
    print("4. Performing terrain analysis...")
    return data


def adaptive_grid(data):
    print("5. Generating adaptive grid...")
    return data


def generate_2_5d_map(data):
    print("6. Generating 2.5D map...")
    return data


def visualize(data):
    print("7. Visualizing final map...")
    return data


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