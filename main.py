"""
================================================================================
TERA PULSE - Autonomous Vehicle 2.5D Adaptive LiDAR Navigation Pipeline
Smart India Hackathon 2026 | Problem Statement: SIH26053
Domain: Defence / DRDO | Software Category
================================================================================

Master End-to-End Orchestrator integrating all 5 team member deliverables:
- Member 1: Machine Learning & Semantic Segmentation (ml/semantic_segmentation.py)
- Member 2: Point Cloud Ingestion & Preprocessing (preprocessing/preprocess_lidar.py)
- Member 3: Multi-Panel Visualization & Dashboards (navigation/navigation_dashboard.py)
- Member 4: Adaptive Variable-Resolution 2.5D Elevation Grid (grid/adaptive_grid.py)
- Member 5: System Integration, A* Path Planning & Motion Control (navigation/)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
import numpy as np

# Ensure project root is in Python module search path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Member 2: Preprocessing
from preprocessing.preprocess_lidar import (
    load_point_cloud,
    generate_synthetic_scan,
    remove_invalid_points,
    distance_filter,
    height_filter,
    voxel_downsample,
    remove_statistical_outliers,
)

# Member 1: Semantic Segmentation
from ml.semantic_segmentation import (
    semantic_segmentation,
    class_counts,
    CLASS_NAMES,
)

# Member 4: Adaptive 2.5D Grid Engine
from adaptive_grid import (
    points_from_arrays,
    adaptive_grid,
    uniform_grid,
    timed,
    save_cells,
    write_top_down_svg,
    write_project_report,
)

# Member 5: Traversability, Path Planning & Autonomous Motion Control
from navigation.path_planner import (
    analyze_navigation_cells,
    find_start_goal,
    a_star,
    print_path_summary,
    save_path_csv,
)
from navigation.navigation_controller import (
    simulate_vehicle_navigation,
    save_telemetry_csv,
)

# Member 3: Visualization & Dashboard
from navigation.navigation_dashboard import create_dashboard


def banner():
    print("=" * 78)
    print("           TERA PULSE - AUTONOMOUS NAVIGATION PIPELINE (SIH26053)           ")
    print("   Adaptive Variable-Resolution 2.5D LiDAR Mapping for Dynamic Perception   ")
    print("=" * 78)


def run_pipeline(
    input_file: str | None = None,
    use_synthetic: bool = False,
    show_ui: bool = False,
    voxel_size: float = 0.15,
) -> dict:
    start_total_time = time.perf_counter()
    banner()

    outputs_dir = ROOT / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------------------------
    # STAGE 1: DATA INGESTION & PREPROCESSING (Member 2)
    # --------------------------------------------------------------------------
    print("\n>>> STAGE 1: Point Cloud Ingestion & Preprocessing (Member 2)")
    default_pcd = ROOT / "data" / "lidar" / "0001.pcd"

    if use_synthetic or (input_file is None and not default_pcd.exists()):
        print("  [Mode] Generating synthetic LiDAR street scene...")
        raw_points, raw_intensity = generate_synthetic_scan(n_ground=20000, n_objects=6, seed=42)
        source_name = "Synthetic LiDAR Scene"
    else:
        file_to_load = Path(input_file) if input_file else default_pcd
        print(f"  [Mode] Ingesting real LiDAR scan from: {file_to_load}")
        raw_points, raw_intensity = load_point_cloud(str(file_to_load))
        source_name = file_to_load.name

    raw_count = len(raw_points)
    print(f"  [1.1] Raw input points: {raw_count:,}")

    # Cleaning & filtering pipeline
    pts, inten = remove_invalid_points(raw_points, raw_intensity)
    pts, inten = distance_filter(pts, inten, min_range=0.5, max_range=65.0)
    pts, inten = height_filter(pts, inten, z_min=-2.6, z_max=3.5)

    # Downsampling for real-time edge feasibility
    if voxel_size > 0:
        pts, inten = voxel_downsample(pts, inten, voxel_size=voxel_size)

    # Outlier removal
    if len(pts) > 200:
        pts, inten = remove_statistical_outliers(pts, inten, nb_neighbors=16, std_ratio=1.8)

    clean_count = len(pts)
    print(f"  [1.2] Cleaned & downsampled points: {clean_count:,} ({100.0 * clean_count / raw_count:.1f}% retained)")

    # --------------------------------------------------------------------------
    # STAGE 2: SEMANTIC SEGMENTATION (Member 1)
    # --------------------------------------------------------------------------
    print("\n>>> STAGE 2: Deep Semantic Classification (Member 1)")
    labels = semantic_segmentation(pts)
    counts = class_counts(labels)
    print(f"  [2.1] Ground (Drivable):     {counts['Ground']:,} points")
    print(f"  [2.2] Static Obstacles:      {counts['Static Obstacle']:,} points")
    print(f"  [2.3] Dynamic Objects:       {counts['Dynamic Object']:,} points")
    print(f"  [2.4] Unknown / Sparse:      {counts['Unknown']:,} points")

    # --------------------------------------------------------------------------
    # STAGE 3: ADAPTIVE VARIABLE-RESOLUTION 2.5D GRID (Member 4)
    # --------------------------------------------------------------------------
    print("\n>>> STAGE 3: Adaptive Variable-Resolution 2.5D Elevation Grid (Member 4)")
    m4_points = points_from_arrays(pts, labels)

    # Benchmark: Adaptive vs Uniform Grid
    adaptive_cells, adaptive_time_ms = timed(adaptive_grid, m4_points)
    uniform_cells, uniform_time_ms = timed(lambda p: uniform_grid(p, resolution=0.25), m4_points)

    reduction_pct = 100.0 * (1.0 - len(adaptive_cells) / max(1, len(uniform_cells)))
    time_savings_pct = 100.0 * (1.0 - adaptive_time_ms / max(0.001, uniform_time_ms))

    print(f"  [3.1] Uniform Grid (0.25m everywhere): {len(uniform_cells):,} cells in {uniform_time_ms:.2f} ms")
    print(f"  [3.2] Adaptive 2.5D Grid (Foveated):   {len(adaptive_cells):,} cells in {adaptive_time_ms:.2f} ms")
    print(f"  [3.3] Storage Reduction:             {reduction_pct:.1f}% fewer cells stored")
    print(f"  [3.4] Processing Speedup:            {time_savings_pct:.1f}% faster mapping latency")

    # Save grid comparison artifacts
    comparison_data = {
        "dataset": source_name,
        "raw_points": raw_count,
        "processed_points": clean_count,
        "foveated_bands_meters": {
            "near_0_to_10m": 0.25,
            "middle_10_to_30m": 0.75,
            "far_30_to_100m": 2.00,
        },
        "uniform_grid_0.25m": {
            "cell_count": len(uniform_cells),
            "latency_ms": round(uniform_time_ms, 2),
        },
        "adaptive_grid": {
            "cell_count": len(adaptive_cells),
            "latency_ms": round(adaptive_time_ms, 2),
        },
        "performance_gain": {
            "cell_reduction_percent": round(reduction_pct, 2),
            "latency_reduction_percent": round(time_savings_pct, 2),
        },
    }

    comp_file = outputs_dir / "comparison.json"
    with open(comp_file, "w") as f:
        json.dump(comparison_data, f, indent=2)

    save_cells(outputs_dir / "adaptive_cells.csv", adaptive_cells)
    write_top_down_svg(outputs_dir / "adaptive_grid_top_down.svg", adaptive_cells, near=10.0, middle=30.0)

    # --------------------------------------------------------------------------
    # STAGE 4: AUTONOMOUS NAVIGATION & MOTION CONTROL (Member 5)
    # --------------------------------------------------------------------------
    print("\n>>> STAGE 4: Traversability, A* Path Planning & Autonomous Motion Control (Member 5)")
    traversable, blocked = analyze_navigation_cells(adaptive_cells)

    start, goal = find_start_goal(adaptive_cells)
    print(f"  [4.1] Selected START Center: x={start.x:.2f}m, y={start.y:.2f}m, res={start.resolution:.2f}m")
    print(f"  [4.2] Selected GOAL Center:  x={goal.x:.2f}m, y={goal.y:.2f}m, res={goal.resolution:.2f}m")

    path = a_star(start, goal, traversable)
    if not path:
        raise RuntimeError("A* Path Planning failed to find a valid route.")

    print_path_summary(path)
    planned_path_file = outputs_dir / "planned_path.csv"
    save_path_csv(path, str(planned_path_file))

    # Autonomous Kinematic Simulation & Pure Pursuit Motion Commands
    print("\n  [4.3] Executing Kinematic Pure Pursuit Motion Control Simulator...")
    sim_result = simulate_vehicle_navigation(path, dt=0.1)
    telemetry_file = outputs_dir / "vehicle_telemetry.csv"
    save_telemetry_csv(sim_result["history"], str(telemetry_file))

    print(f"  [4.4] Navigation Mission Status:     {'SUCCESS' if sim_result['success'] else 'INCOMPLETE'}")
    print(f"  [4.5] Autonomous Mission Time:       {sim_result['total_time_sec']} seconds")
    print(f"  [4.6] Trajectory Distance Traveled:  {sim_result['total_distance_m']} meters")
    print(f"  [4.7] Average Operating Speed:       {sim_result['average_speed_mps']} m/s ({sim_result['average_speed_mps']*3.6:.1f} km/h)")
    print(f"  [4.8] Dynamic Telemetry Steps:       {sim_result['telemetry_samples']} samples @ 10Hz")

    # --------------------------------------------------------------------------
    # STAGE 5: VISUALIZATION & COMPREHENSIVE DASHBOARD (Member 3)
    # --------------------------------------------------------------------------
    print("\n>>> STAGE 5: Multi-Panel Visual Analytics & Dashboard (Member 3)")
    dashboard_img = outputs_dir / "navigation_dashboard.png"

    create_dashboard(
        points=pts,
        cells=adaptive_cells,
        traversable=traversable,
        blocked=blocked,
        start=start,
        goal=goal,
        path=path,
        sim_result=sim_result,
        show_plot=show_ui,
    )

    total_pipeline_time = round(time.perf_counter() - start_total_time, 2)

    # Mission Summary JSON
    summary = {
        "project": "TERA PULSE",
        "hackathon": "Smart India Hackathon 2026",
        "problem_statement": "SIH26053 - Adaptive Variable Resolution 2.5D LiDAR Mapping",
        "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_execution_time_sec": total_pipeline_time,
        "input_source": source_name,
        "raw_points": raw_count,
        "preprocessed_points": clean_count,
        "semantic_breakdown": counts,
        "adaptive_cells_total": len(adaptive_cells),
        "traversable_cells": len(traversable),
        "blocked_cells": len(blocked),
        "cell_storage_reduction_percent": round(reduction_pct, 2),
        "path_planning": {
            "algorithm": "A* on Variable-Resolution Adjacency Graph",
            "number_of_cells": len(path),
            "start_coordinates": [round(start.x, 2), round(start.y, 2)],
            "goal_coordinates": [round(goal.x, 2), round(goal.y, 2)],
        },
        "autonomous_execution": {
            "controller": "Pure Pursuit with Curvature & Goal Slowdown",
            "success": sim_result["success"],
            "mission_time_sec": sim_result["total_time_sec"],
            "mission_distance_meters": sim_result["total_distance_m"],
            "avg_speed_mps": sim_result["average_speed_mps"],
            "telemetry_log": str(telemetry_file.relative_to(ROOT)),
        },
        "artifacts_generated": [
            str(dashboard_img.relative_to(ROOT)),
            str(telemetry_file.relative_to(ROOT)),
            str(planned_path_file.relative_to(ROOT)),
            str(comp_file.relative_to(ROOT)),
            "outputs/adaptive_grid_top_down.svg",
        ],
    }

    with open(outputs_dir / "mission_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 78)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {total_pipeline_time} SECONDS!")
    print(f"All project outputs saved in: {outputs_dir}")
    print(f"1. High-Res Multi-Panel Dashboard: {dashboard_img}")
    print(f"2. Vehicle Motion Telemetry:       {telemetry_file}")
    print(f"3. A* Planned Waypoint Route:      {planned_path_file}")
    print(f"4. Benchmark & Metrics JSON:       {comp_file}")
    print(f"5. Mission Summary Report:         {outputs_dir / 'mission_summary.json'}")
    print("=" * 78)

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="TERA PULSE - Autonomous Variable-Resolution 2.5D LiDAR Navigation Pipeline"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to raw LiDAR scan (.pcd, .bin, .ply). Default uses data/lidar/0001.pcd",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Run pipeline using generated synthetic street scene",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Open interactive visual dashboard window",
    )
    parser.add_argument(
        "--voxel-size",
        type=float,
        default=0.15,
        help="Voxel downsampling leaf size in meters (default: 0.15m)",
    )

    args = parser.parse_args()

    run_pipeline(
        input_file=args.input,
        use_synthetic=args.synthetic,
        show_ui=args.show,
        voxel_size=args.voxel_size,
    )


if __name__ == "__main__":
    main()
