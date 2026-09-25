"""
Real LiDAR Navigation Test
TERA PULSE - SIH26053

Real pipeline:

0001.pcd
   ↓
M1 Semantic Segmentation
   ↓
M4 Adaptive Grid
   ↓
Traversability
   ↓
Start / Goal
   ↓
A* Path Planning
"""

from pathlib import Path
import sys

import open3d as o3d
import numpy as np


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(ROOT)
)

sys.path.insert(
    0,
    str(ROOT / "ml")
)

sys.path.insert(
    0,
    str(ROOT / "navigation")
)


# ============================================================
# IMPORTS
# ============================================================

from ml.semantic_segmentation import (
    semantic_segmentation
)

from adaptive_grid import (
    points_from_arrays,
    adaptive_grid
)

from path_planner import (
    analyze_navigation_cells,
    find_start_goal,
    a_star,
    print_path_summary,
    count_connections,
    save_path_csv
)


# ============================================================
# 1. LOAD REAL LIDAR
# ============================================================

pcd_path = (
    ROOT /
    "data" /
    "lidar" /
    "0001.pcd"
)


print("\n========================================")
print("      TERA PULSE NAVIGATION TEST")
print("========================================")


print("\n===== STEP 1: REAL LIDAR =====")

print(
    f"Loading: {pcd_path}"
)


pcd = o3d.io.read_point_cloud(
    str(pcd_path)
)


points = np.asarray(
    pcd.points
)


print(
    f"Total points: {len(points)}"
)


if len(points) == 0:

    raise ValueError(
        "No LiDAR points were loaded."
    )


# ============================================================
# 2. M1 SEMANTIC SEGMENTATION
# ============================================================

print(
    "\n===== STEP 2: M1 SEMANTIC SEGMENTATION ====="
)


labels = semantic_segmentation(
    points
)


print(
    f"Labels shape: {labels.shape}"
)


if len(labels) != len(points):

    raise ValueError(
        "Number of labels does not match "
        "number of LiDAR points."
    )


# ============================================================
# 3. M4 INPUT
# ============================================================

print(
    "\n===== STEP 3: M4 INPUT ====="
)


m4_points = points_from_arrays(
    points,
    labels
)


print(
    f"M4 points: {len(m4_points)}"
)


# ============================================================
# 4. CURRENT M4 ADAPTIVE GRID
# ============================================================

print(
    "\n===== STEP 4: M4 ADAPTIVE GRID ====="
)


cells = adaptive_grid(
    m4_points
)


print(
    f"Adaptive cells: {len(cells)}"
)


if len(cells) == 0:

    raise ValueError(
        "M4 generated zero adaptive cells."
    )


# ============================================================
# 5. TRAVERSABILITY
# ============================================================

print(
    "\n===== STEP 5: TRAVERSABILITY ====="
)


traversable, blocked = (
    analyze_navigation_cells(
        cells
    )
)


if len(traversable) == 0:

    raise ValueError(
        "No traversable cells available."
    )


# ============================================================
# 6. START / GOAL
# ============================================================

print(
    "\n===== STEP 6: START / GOAL ====="
)


start, goal = find_start_goal(
    cells
)
count_connections(cells)

print(
    f"Start: "
    f"x={start.x:.2f}, "
    f"y={start.y:.2f}, "
    f"resolution={start.resolution:.2f}m"
)


print(
    f"Goal: "
    f"x={goal.x:.2f}, "
    f"y={goal.y:.2f}, "
    f"resolution={goal.resolution:.2f}m"
)


# ============================================================
# 7. A* PATH PLANNING
# ============================================================

print(
    "\n===== STEP 7: A* PATH PLANNING ====="
)


path = a_star(
    start,
    goal,
    traversable
)


# ============================================================
# 8. RESULT
# ============================================================

print_path_summary(
    path
)
save_path_csv(path)

# ============================================================
# 9. SUCCESS / FAILURE
# ============================================================

print(
    "\n========================================"
)


if path is not None:

    print(
        "A* PATH FOUND SUCCESSFULLY"
    )

    print(
        f"Number of path cells: "
        f"{len(path)}"
    )

else:

    print(
        "NO PATH FOUND"
    )


print(
    "========================================\n"
)