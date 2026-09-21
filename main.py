# Import Member 2's preprocessing tools
from preprocessing.preprocess_lidar import (
    generate_synthetic_scan,
    remove_invalid_points,
    distance_filter,
    height_filter,
    voxel_downsample,
    remove_statistical_outliers
)

# Import Member 1's semantic segmentation tools
from ml.semantic_segmentation import semantic_segmentation as ml_segmentation, class_counts

def load_data():
    print("1. Loading raw LiDAR data...")
    # Using Member 2's synthetic generator to test the pipeline without external files
    points, intensity = generate_synthetic_scan()
    print(f"   -> Successfully loaded {len(points)} raw points.")
    return points, intensity


def preprocess(data):
    print("2. Preprocessing point cloud...")
    points, intensity = data
    
    # Passing data through Member 2's sequential filters
    points, intensity = remove_invalid_points(points, intensity)
    points, intensity = distance_filter(points, intensity, min_range=0.5, max_range=60.0)
    points, intensity = height_filter(points, intensity, z_min=-2.2, z_max=2.0)
    points, intensity = voxel_downsample(points, intensity, voxel_size=0.2)
    points, intensity = remove_statistical_outliers(points, intensity)
    
    print(f"   -> Cleaned and downsampled to {len(points)} points.")
    return points, intensity


def semantic_segmentation(data):
    print("3. Performing semantic segmentation...")
    points, intensity = data  # Unpack the cleaned data from Step 2
    
    # Run Member 1's semantic segmentation model
    labels = ml_segmentation(points)
    
    # Print the classification results
    counts = class_counts(labels)
    print(f"   -> Found: {counts['Ground']} Ground, {counts['Static Obstacle']} Static, {counts['Dynamic Object']} Dynamic, {counts['Unknown']} Unknown")
    
    # Pass the points and their new labels forward to Step 4
    return points, labels


def terrain_analysis(data):
    print("4. Performing terrain analysis...")
    return data # Placeholder


def adaptive_grid(data):
    print("5. Generating adaptive grid...")
    return data # Placeholder until Member 4's code is merged


def generate_2_5d_map(data):
    print("6. Generating 2.5D map...")
    return data # Placeholder


def visualize(data):
    print("7. Visualizing final map...")
    return data # Placeholder until Member 3's code is merged


def main():
    print("--- Starting TERA PULSE Pipeline ---")
    
    data1 = load_data()
    data2 = preprocess(data1)
    
    # Passing the actual processed data down the skeleton pipeline
    data3 = semantic_segmentation(data2)
    data4 = terrain_analysis(data3)
    data5 = adaptive_grid(data4)
    data6 = generate_2_5d_map(data5)
    visualize(data6)
    
    print("--- Pipeline Completed ---")


if __name__ == "__main__":
    main()