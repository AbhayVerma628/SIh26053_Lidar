"""
TERA PULSE - Real-Time Interactive Web Dashboard & Local Server
SIH26053: Adaptive Variable-Resolution 2.5D LiDAR Mapping & Navigation
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from flask import Flask, jsonify, render_template, request

# Add repo root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from preprocessing.preprocess_lidar import (
    load_point_cloud,
    generate_synthetic_scan,
    remove_invalid_points,
    distance_filter,
    height_filter,
    voxel_downsample,
    remove_statistical_outliers,
)
from ml.semantic_segmentation import semantic_segmentation, class_counts
from adaptive_grid import points_from_arrays, Cell, Point
from navigation.path_planner import (
    analyze_navigation_cells,
    find_start_goal,
    a_star,
    cell_distance,
    find_neighbors,
)
from navigation.navigation_controller import (
    simulate_vehicle_navigation,
    smooth_path_waypoints,
    PurePursuitController,
)

app = Flask(
    __name__,
    template_folder=str(ROOT / "web" / "templates"),
    static_folder=str(ROOT / "web" / "static"),
)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Global in-memory cache of current state
STATE = {
    "params": {
        "near_band": 10.0,
        "mid_band": 30.0,
        "fine_res": 0.25,
        "mid_res": 0.75,
        "coarse_res": 2.00,
        "voxel_size": 0.15,
        "lookahead": 1.5,
        "max_speed": 3.5,
    },
    "points": None,         # Nx3 numpy array
    "labels": None,         # N numpy array
    "cells": [],            # list of Cell objects
    "traversable": [],
    "blocked": [],
    "start": None,
    "goal": None,
    "path": [],
    "sim_result": {},
    "metrics": {},
}


def compute_adaptive_grid_custom(points, near, mid, fine, medium, coarse):
    """Custom resolution selector based on UI parameters."""
    def resolution_for(point):
        dist = math.hypot(point.x, point.y)
        if dist < near:
            return fine
        if dist < mid:
            return medium
        return coarse

    from collections import defaultdict
    import statistics

    buckets = defaultdict(list)
    for p in points:
        if math.isnan(p.x) or math.isnan(p.y) or math.isnan(p.z) or math.isinf(p.x) or math.isinf(p.y) or math.isinf(p.z):
            continue
        res = resolution_for(p)
        key = (res, math.floor(p.x / res), math.floor(p.y / res))
        buckets[key].append(p)

    cells = []
    for (res, ix, iy), bucket in buckets.items():
        elevations = [pt.z for pt in bucket]
        # majority class
        counts = defaultdict(int)
        for pt in bucket:
            counts[pt.semantic_class] += 1
        maj_class = min(counts, key=lambda l: (-counts[l], l))

        cells.append(Cell(
            x=(ix + 0.5) * res,
            y=(iy + 0.5) * res,
            resolution=res,
            elevation=max(elevations),
            mean_elevation=statistics.fmean(elevations),
            semantic_class=maj_class,
            point_count=len(bucket),
        ))
    return sorted(cells, key=lambda c: (c.resolution, c.x, c.y))


def compute_uniform_grid_custom(points, resolution=0.25):
    from collections import defaultdict
    import statistics

    buckets = defaultdict(list)
    for p in points:
        if math.isnan(p.x) or math.isnan(p.y) or math.isnan(p.z) or math.isinf(p.x) or math.isinf(p.y) or math.isinf(p.z):
            continue
        key = (resolution, math.floor(p.x / resolution), math.floor(p.y / resolution))
        buckets[key].append(p)

    return len(buckets)


def initialize_pipeline(params=None):
    """Run pipeline with specified parameters."""
    if params:
        STATE["params"].update(params)

    p = STATE["params"]
    pcd_path = ROOT / "data" / "lidar" / "0001.pcd"

    start_time = time.perf_counter()

    # Load point cloud if not loaded
    if STATE["points"] is None:
        if pcd_path.exists():
            raw_pts, raw_inten = load_point_cloud(str(pcd_path))
        else:
            raw_pts, raw_inten = generate_synthetic_scan(n_ground=18000, n_objects=6, seed=42)

        # Preprocessing
        clean_pts, inten = remove_invalid_points(raw_pts, raw_inten)
        clean_pts, inten = distance_filter(clean_pts, inten, min_range=0.5, max_range=65.0)
        clean_pts, inten = height_filter(clean_pts, inten, z_min=-2.6, z_max=3.5)

        if p["voxel_size"] > 0:
            clean_pts, inten = voxel_downsample(clean_pts, inten, voxel_size=p["voxel_size"])
        if len(clean_pts) > 200:
            clean_pts, inten = remove_statistical_outliers(clean_pts, inten, nb_neighbors=16, std_ratio=1.8)

        labels = semantic_segmentation(clean_pts)
        STATE["points"] = clean_pts
        STATE["labels"] = labels
        STATE["raw_count"] = len(raw_pts)
    else:
        clean_pts = STATE["points"]
        labels = STATE["labels"]

    # Member 4: Adaptive Grid with dynamic parameters
    m4_pts = points_from_arrays(clean_pts, labels)

    grid_t0 = time.perf_counter()
    adaptive_cells = compute_adaptive_grid_custom(
        m4_pts,
        near=p["near_band"],
        mid=p["mid_band"],
        fine=p["fine_res"],
        medium=p["mid_res"],
        coarse=p["coarse_res"],
    )
    grid_latency_ms = (time.perf_counter() - grid_t0) * 1000

    uniform_count = compute_uniform_grid_custom(m4_pts, resolution=p["fine_res"])
    reduction_pct = 100.0 * (1.0 - len(adaptive_cells) / max(1, uniform_count))

    # Traversability
    traversable, blocked = analyze_navigation_cells(adaptive_cells)

    # Start and Goal
    start, goal = find_start_goal(adaptive_cells)

    # A* Path Planning
    path = a_star(start, goal, traversable)
    if not path:
        path = [start, goal]

    # Motion Simulation with dynamic controller parameters
    sim_result = simulate_vehicle_navigation(path, dt=0.1)

    total_time = round(time.perf_counter() - start_time, 2)

    STATE["cells"] = adaptive_cells
    STATE["traversable"] = traversable
    STATE["blocked"] = blocked
    STATE["start"] = start
    STATE["goal"] = goal
    STATE["path"] = path
    STATE["sim_result"] = sim_result

    counts = class_counts(labels)
    STATE["metrics"] = {
        "raw_points": STATE.get("raw_count", len(clean_pts)),
        "processed_points": len(clean_pts),
        "ground_points": counts.get("Ground", 0),
        "obstacle_points": counts.get("Static Obstacle", 0),
        "dynamic_points": counts.get("Dynamic Object", 0),
        "uniform_cells": uniform_count,
        "adaptive_cells": len(adaptive_cells),
        "cell_reduction_pct": round(reduction_pct, 1),
        "grid_latency_ms": round(grid_latency_ms, 2),
        "traversable_cells": len(traversable),
        "blocked_cells": len(blocked),
        "traversable_pct": round(100.0 * len(traversable) / max(1, len(adaptive_cells)), 1),
        "path_cells": len(path),
        "mission_distance_m": sim_result.get("total_distance_m", 0.0),
        "mission_time_sec": sim_result.get("total_time_sec", 0.0),
        "avg_speed_kmh": round(sim_result.get("average_speed_mps", 0.0) * 3.6, 1),
        "max_speed_kmh": round(sim_result.get("max_speed_mps", 0.0) * 3.6, 1),
        "total_compute_sec": total_time,
    }


# Initial warm-up
initialize_pipeline()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def get_status():
    return jsonify({
        "status": "ready",
        "params": STATE["params"],
        "metrics": STATE["metrics"],
    })


@app.route("/api/data")
def get_data():
    """Return visual payload optimized for browser canvas & WebGL."""
    pts = STATE["points"]
    labels = STATE["labels"]

    # Downsample points for ultra-smooth 60fps browser rendering
    step = max(1, len(pts) // 3500)
    sampled_pts = []
    for i in range(0, len(pts), step):
        sampled_pts.append({
            "x": round(float(pts[i][0]), 2),
            "y": round(float(pts[i][1]), 2),
            "z": round(float(pts[i][2]), 2),
            "cls": int(labels[i]),
        })

    # Cells
    cell_list = []
    trav_ids = {id(c) for c in STATE["traversable"]}
    for c in STATE["cells"]:
        cell_list.append({
            "x": round(c.x, 2),
            "y": round(c.y, 2),
            "res": c.resolution,
            "z": round(c.elevation, 2),
            "cls": c.semantic_class,
            "trav": id(c) in trav_ids,
        })

    # Path
    path_coords = [{"x": round(c.x, 2), "y": round(c.y, 2), "res": c.resolution} for c in STATE["path"]]

    start_coords = {"x": round(STATE["start"].x, 2), "y": round(STATE["start"].y, 2)} if STATE["start"] else None
    goal_coords = {"x": round(STATE["goal"].x, 2), "y": round(STATE["goal"].y, 2)} if STATE["goal"] else None

    # Telemetry steps from Pure Pursuit simulation
    history = STATE["sim_result"].get("history", [])

    return jsonify({
        "points": sampled_pts,
        "cells": cell_list,
        "path": path_coords,
        "start": start_coords,
        "goal": goal_coords,
        "telemetry": history,
        "metrics": STATE["metrics"],
        "params": STATE["params"],
    })


@app.route("/api/recalculate", methods=["POST"])
def recalculate():
    """Trigger re-computation with custom user-tuned parameters."""
    req_data = request.get_json() or {}
    new_params = {}

    for k in ["near_band", "mid_band", "fine_res", "mid_res", "coarse_res", "voxel_size", "lookahead", "max_speed"]:
        if k in req_data:
            try:
                new_params[k] = float(req_data[k])
            except (ValueError, TypeError):
                pass

    # If voxel_size changed, reset cached points so downsampling is recomputed
    if "voxel_size" in new_params and new_params["voxel_size"] != STATE["params"]["voxel_size"]:
        STATE["points"] = None
        STATE["labels"] = None

    initialize_pipeline(new_params)

    return jsonify({
        "success": True,
        "metrics": STATE["metrics"],
        "params": STATE["params"],
    })


if __name__ == "__main__":
    print("\n=======================================================")
    print("  TERA PULSE - Localhost Interactive Dashboard Server  ")
    print("  URL: http://localhost:5000                           ")
    print("=======================================================\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
