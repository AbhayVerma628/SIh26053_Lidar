"""
LiDAR Preprocessing Pipeline
============================
Member 2 deliverable: raw point cloud -> cleaned, filtered, downsampled point cloud.

Usage:
    python preprocess_lidar.py --input path/to/scan.bin   # KITTI-style X Y Z Intensity float32
    python preprocess_lidar.py --input path/to/scan.pcd   # any Open3D-readable pcd/ply
    python preprocess_lidar.py                            # no --input -> generates a synthetic
                                                            # "street scene" scan so the pipeline
                                                            # can be demoed/tested today.

Outputs (written next to this script, or to --outdir):
    raw.pcd         - the untouched input, saved in a standard format
    processed.pcd   - after cleaning + filtering + downsampling
    before.png      - screenshot of raw cloud
    after.png       - screenshot of processed cloud
"""

import argparse
import os
import numpy as np
import open3d as o3d


# ----------------------------------------------------------------------
# 1. LOADING
# ----------------------------------------------------------------------

def load_kitti_bin(path):
    """KITTI Velodyne .bin files are raw float32 arrays: X Y Z Intensity per point."""
    scan = np.fromfile(path, dtype=np.float32).reshape(-1, 4)
    points = scan[:, :3]
    intensity = scan[:, 3]
    return points, intensity


def load_point_cloud(path):
    """Load .pcd/.ply/.bin into (points Nx3, intensity N or None)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".bin":
        return load_kitti_bin(path)
    pcd = o3d.io.read_point_cloud(path)
    points = np.asarray(pcd.points)
    intensity = None
    if pcd.has_colors():
        # some pcd exports stash intensity in the "colors" channel (grayscale)
        colors = np.asarray(pcd.colors)
        intensity = colors[:, 0]
    return points, intensity


def generate_synthetic_scan(n_ground=20000, n_objects=6, seed=0):
    """
    Builds a plausible LiDAR-style scan of a street scene so the pipeline
    can be built/tested/screenshotted before a real dataset is downloaded:
    - a ground plane with mild noise
    - a few box-shaped 'obstacles' (cars/poles) at various distances
    - some sparse far-away noise points (like KITTI's max-range returns)
    - a handful of NaN/inf points, like a real sensor dropout
    """
    rng = np.random.default_rng(seed)

    # Ground plane: -30m to 30m in X/Y, slight roughness in Z
    gx = rng.uniform(-30, 30, n_ground)
    gy = rng.uniform(-20, 20, n_ground)
    gz = rng.normal(0, 0.03, n_ground) - 1.6  # sensor mounted 1.6m above ground
    ground = np.stack([gx, gy, gz], axis=1)
    ground_intensity = rng.uniform(0.05, 0.25, n_ground)

    # A few solid "objects" (boxes) at different ranges - like nearby cars/poles
    obj_points = []
    obj_intensity = []
    for i in range(n_objects):
        cx, cy = rng.uniform(-15, 15), rng.uniform(3, 25)
        w, d, h = rng.uniform(1.5, 2.2), rng.uniform(3.5, 4.8), rng.uniform(1.3, 1.8)
        n = rng.integers(400, 900)
        ox = cx + rng.uniform(-w / 2, w / 2, n)
        oy = cy + rng.uniform(-d / 2, d / 2, n)
        oz = rng.uniform(-1.6, -1.6 + h, n)
        obj_points.append(np.stack([ox, oy, oz], axis=1))
        obj_intensity.append(rng.uniform(0.4, 0.9, n))
    objects = np.concatenate(obj_points, axis=0)
    objects_intensity = np.concatenate(obj_intensity, axis=0)

    # Sparse far-range junk (beyond useful sensing range, e.g. sky reflections)
    n_far = 800
    fx = rng.uniform(-120, 120, n_far)
    fy = rng.uniform(-120, 120, n_far)
    fz = rng.uniform(-5, 15, n_far)
    far = np.stack([fx, fy, fz], axis=1)
    far_intensity = rng.uniform(0.0, 1.0, n_far)

    points = np.concatenate([ground, objects, far], axis=0)
    intensity = np.concatenate([ground_intensity, objects_intensity, far_intensity], axis=0)

    # Inject sensor dropout: NaN/Inf points, like a real raw scan would have
    n_bad = 150
    bad_idx = rng.choice(len(points), n_bad, replace=False)
    bad_points = points.copy()
    half = n_bad // 2
    bad_points[bad_idx[:half]] = np.nan
    bad_points[bad_idx[half:]] = np.inf
    points = np.concatenate([points, bad_points[bad_idx]], axis=0)
    intensity = np.concatenate([intensity, rng.uniform(0, 1, n_bad)], axis=0)

    return points, intensity


# ----------------------------------------------------------------------
# 2. PREPROCESSING STEPS
# ----------------------------------------------------------------------

def remove_invalid_points(points, intensity=None):
    """Drop NaN / Inf points -- corrupted or invalid sensor returns."""
    mask = np.isfinite(points).all(axis=1)
    if intensity is not None:
        mask &= np.isfinite(intensity)
        return points[mask], intensity[mask]
    return points[mask], None


def distance_filter(points, intensity=None, min_range=0.5, max_range=60.0):
    """
    Keep only points within a useful sensing range.
    - min_range removes points essentially on top of the sensor (e.g. the
      vehicle's own hood/roof reflecting back).
    - max_range removes far, noisy, low-density returns that aren't reliable
      for navigation decisions.
    """
    dist = np.linalg.norm(points, axis=1)
    mask = (dist >= min_range) & (dist <= max_range)
    if intensity is not None:
        return points[mask], intensity[mask]
    return points[mask], None


def height_filter(points, intensity=None, z_min=-2.2, z_max=2.0):
    """
    Keep points within a plausible height band relative to the sensor.
    Removes sky reflections / birds (too high) and severe ground undershoot
    from multipath errors (too low), while keeping the ground plane and
    obstacles relevant to navigation.
    """
    mask = (points[:, 2] >= z_min) & (points[:, 2] <= z_max)
    if intensity is not None:
        return points[mask], intensity[mask]
    return points[mask], None


def voxel_downsample(points, intensity=None, voxel_size=0.2):
    """
    Reduce point density by averaging points inside a 3D grid cell (voxel).
    Cuts point count drastically while preserving the overall shape --
    critical for real-time downstream processing.
    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    if intensity is not None:
        # stash intensity as grayscale "color" so it survives downsampling
        colors = np.stack([intensity, intensity, intensity], axis=1)
        pcd.colors = o3d.utility.Vector3dVector(colors)
    down = pcd.voxel_down_sample(voxel_size)
    out_points = np.asarray(down.points)
    out_intensity = np.asarray(down.colors)[:, 0] if down.has_colors() else None
    return out_points, out_intensity


def remove_statistical_outliers(points, intensity=None, nb_neighbors=16, std_ratio=2.0):
    """
    Remove points whose neighborhood distance is a statistical outlier --
    catches stray noise points that survive range/height filtering.
    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    if intensity is not None:
        colors = np.stack([intensity, intensity, intensity], axis=1)
        pcd.colors = o3d.utility.Vector3dVector(colors)
    clean, ind = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    out_points = np.asarray(clean.points)
    out_intensity = np.asarray(clean.colors)[:, 0] if clean.has_colors() else None
    return out_points, out_intensity


def to_o3d_pcd(points, intensity=None):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    if intensity is not None and len(intensity) == len(points):
        colors = np.stack([intensity, intensity, intensity], axis=1)
        colors = np.clip(colors, 0, 1)
        pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd


# ----------------------------------------------------------------------
# 3. SCREENSHOTS (headless, no display needed)
# ----------------------------------------------------------------------

def save_screenshot(pcd, out_path):
    # Use only finite points to frame the camera (raw clouds may still contain
    # NaN/Inf points at this stage -- that's expected, it's what we're about
    # to clean up).
    pts = np.asarray(pcd.points)
    finite_mask = np.isfinite(pts).all(axis=1)
    clean_pts = pts[finite_mask]

    render = o3d.visualization.rendering.OffscreenRenderer(1000, 750)
    mat = o3d.visualization.rendering.MaterialRecord()
    mat.shader = "defaultUnlit"
    mat.point_size = 2.5

    render.scene.set_background([1, 1, 1, 1])

    # Build a display-safe copy so Open3D doesn't choke on NaN/Inf internally
    display_pcd = o3d.geometry.PointCloud()
    display_pcd.points = o3d.utility.Vector3dVector(clean_pts)
    if pcd.has_colors():
        display_pcd.colors = o3d.utility.Vector3dVector(np.asarray(pcd.colors)[finite_mask])
    render.scene.add_geometry("pcd", display_pcd, mat)

    if len(clean_pts) > 0:
        # Use robust percentiles (not raw min/max) so a handful of far-range
        # noise points don't blow out the framing.
        lo = np.percentile(clean_pts, 2, axis=0)
        hi = np.percentile(clean_pts, 98, axis=0)
        center = (lo + hi) / 2
        extent = float(np.linalg.norm(hi - lo))
        extent = max(extent, 1.0)
    else:
        center = np.array([0, 0, 0])
        extent = 10.0

    eye = center + np.array([0, -extent * 0.9, extent * 0.75])
    render.scene.camera.look_at(center, eye, [0, 0, 1])

    img = render.render_to_image()
    o3d.io.write_image(out_path, img)


# ----------------------------------------------------------------------
# 4. MAIN PIPELINE
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default=None,
                         help="Path to .bin / .pcd / .ply LiDAR scan. Omit to use synthetic demo data.")
    parser.add_argument("--outdir", type=str, default=".")
    parser.add_argument("--min_range", type=float, default=0.5)
    parser.add_argument("--max_range", type=float, default=60.0)
    parser.add_argument("--z_min", type=float, default=-2.2)
    parser.add_argument("--z_max", type=float, default=2.0)
    parser.add_argument("--voxel_size", type=float, default=0.2)
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # --- Load ---
    if args.input:
        print(f"[1/6] Loading point cloud from: {args.input}")
        points, intensity = load_point_cloud(args.input)
    else:
        print("[1/6] No --input given: generating synthetic demo LiDAR scan.")
        points, intensity = generate_synthetic_scan()

    n_raw = len(points)
    print(f"      Raw point count: {n_raw}")

    raw_pcd = to_o3d_pcd(points, intensity)
    raw_path = os.path.join(args.outdir, "raw.pcd")
    o3d.io.write_point_cloud(raw_path, raw_pcd)
    print(f"      Saved raw cloud -> {raw_path}")

    save_screenshot(raw_pcd, os.path.join(args.outdir, "before.png"))
    print(f"      Saved before.png")

    # --- Preprocess ---
    print("[2/6] Removing invalid (NaN/Inf) points...")
    points, intensity = remove_invalid_points(points, intensity)
    print(f"      Remaining: {len(points)}")

    print(f"[3/6] Distance filtering ({args.min_range}m - {args.max_range}m)...")
    points, intensity = distance_filter(points, intensity, args.min_range, args.max_range)
    print(f"      Remaining: {len(points)}")

    print(f"[4/6] Height filtering ({args.z_min}m to {args.z_max}m)...")
    points, intensity = height_filter(points, intensity, args.z_min, args.z_max)
    print(f"      Remaining: {len(points)}")

    print(f"[5/6] Voxel downsampling (voxel size = {args.voxel_size}m)...")
    points, intensity = voxel_downsample(points, intensity, args.voxel_size)
    print(f"      Remaining: {len(points)}")

    print("[5.5/6] Removing statistical outliers...")
    points, intensity = remove_statistical_outliers(points, intensity)
    n_processed = len(points)
    print(f"      Remaining: {n_processed}")

    # --- Save processed ---
    processed_pcd = to_o3d_pcd(points, intensity)
    processed_path = os.path.join(args.outdir, "processed.pcd")
    o3d.io.write_point_cloud(processed_path, processed_pcd)
    print(f"[6/6] Saved processed cloud -> {processed_path}")

    save_screenshot(processed_pcd, os.path.join(args.outdir, "after.png"))
    print("      Saved after.png")

    # --- Summary ---
    reduction = 100 * (1 - n_processed / n_raw) if n_raw else 0
    print("\n===== SUMMARY =====")
    print(f"Points before preprocessing: {n_raw}")
    print(f"Points after preprocessing:  {n_processed}")
    print(f"Reduction: {reduction:.1f}%")


if __name__ == "__main__":
    main()
