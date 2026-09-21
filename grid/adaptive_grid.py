"""
Adaptive Variable-Resolution 2.5D LiDAR Grid
Member 4 - Adaptive Grid Engine

Responsibilities:
    - Convert LiDAR points into adaptive-resolution cells.
    - Use smaller cells near the sensor.
    - Use larger cells farther from the sensor.
    - Preserve elevation information.
    - Preserve semantic information when available.
    - Compare adaptive and uniform representations.

This module does NOT perform visualization.
Visualization is handled by Member 3.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import time

from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


# ======================================================================
# DATA STRUCTURES
# ======================================================================

@dataclass(frozen=True)
class Point:
    """Single LiDAR point."""

    x: float
    y: float
    z: float
    semantic_class: str = "unknown"


@dataclass
class Cell:
    """Single occupied 2.5D grid cell."""

    x: float
    y: float
    resolution: float
    elevation: float
    mean_elevation: float
    semantic_class: str
    point_count: int


# ======================================================================
# DISTANCE
# ======================================================================

def distance_xy(point: Point) -> float:
    """
    Calculate horizontal distance from the LiDAR sensor.

    Z is intentionally ignored because resolution depends on
    horizontal distance.
    """

    return math.hypot(point.x, point.y)


# ======================================================================
# CSV LOADING
# ======================================================================

def load_points(path: Path) -> list[Point]:
    """
    Load points from CSV.

    Required columns:
        x, y, z

    Optional:
        semantic_class
    """

    with path.open(newline="", encoding="utf-8") as handle:

        reader = csv.DictReader(handle)

        required = {"x", "y", "z"}

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                "Input CSV must contain x,y,z[,semantic_class]"
            )

        points = []

        for row in reader:

            points.append(
                Point(
                    float(row["x"]),
                    float(row["y"]),
                    float(row["z"]),
                    row.get("semantic_class") or "unknown",
                )
            )

    return points


# ======================================================================
# NUMPY / M1-M2 ADAPTER
# ======================================================================

def points_from_arrays(points, labels=None) -> list[Point]:
    """
    Convert NumPy-style Nx3 point data into M4 Point objects.

    This function allows M5 to directly connect:

        M2 preprocessing
                +
        M1 semantic segmentation
                ↓
        M4 adaptive grid

    Parameters
    ----------
    points:
        Nx3 array-like object containing x, y, z.

    labels:
        Optional semantic labels.

    Label mapping:
        0 -> ground
        1 -> static_obstacle
        2 -> dynamic_object
        3 -> unknown
    """

    label_names = {
        0: "ground",
        1: "static_obstacle",
        2: "dynamic_object",
        3: "unknown",
    }

    points = list(points)

    if labels is not None:
        labels = list(labels)

        if len(points) != len(labels):
            raise ValueError(
                "points and labels must contain the same number of entries"
            )

    result = []

    for index, xyz in enumerate(points):

        if len(xyz) < 3:
            raise ValueError(
                "Every point must contain x, y and z"
            )

        semantic_class = "unknown"

        if labels is not None:
            semantic_class = label_names.get(
                int(labels[index]),
                "unknown",
            )

        result.append(
            Point(
                x=float(xyz[0]),
                y=float(xyz[1]),
                z=float(xyz[2]),
                semantic_class=semantic_class,
            )
        )

    return result


# ======================================================================
# SYNTHETIC DEMO
# ======================================================================

def synthetic_scene(
    seed: int = 7,
    count: int = 18000,
) -> list[Point]:

    """
    Generate deterministic synthetic LiDAR-like data.

    This is ONLY for testing the M4 module.
    Real project integration should use real LiDAR data.
    """

    import random

    rng = random.Random(seed)

    points = []

    for _ in range(count):

        radius = 100 * math.sqrt(rng.random())

        if rng.random() < radius / 180:
            continue

        theta = rng.uniform(-math.pi, math.pi)

        x = radius * math.cos(theta)
        y = radius * math.sin(theta)

        road = (
            -0.015 * x
            + 0.004 * y
            + rng.gauss(0, 0.025)
        )

        # Example elevated vehicle-like object
        if 12 < x < 18 and -4 < y < 3:

            z = (
                road
                + 1.45
                + rng.gauss(0, 0.03)
            )

            label = "vehicle"

        # Example vegetation
        elif abs(y) > 25 and rng.random() < 0.3:

            z = (
                road
                + 0.8
                + rng.random() * 2.2
            )

            label = "vegetation"

        else:

            z = road
            label = "ground"

        points.append(
            Point(
                x=x,
                y=y,
                z=z,
                semantic_class=label,
            )
        )

    return points


# ======================================================================
# SEMANTIC AGGREGATION
# ======================================================================

def majority_class(points: list[Point]) -> str:
    """Return the most common semantic class."""

    counts = defaultdict(int)

    for point in points:
        counts[point.semantic_class] += 1

    return min(
        counts,
        key=lambda label: (-counts[label], label),
    )


# ======================================================================
# CELL AGGREGATION
# ======================================================================

def aggregate(
    points: Iterable[Point],
    resolution_for,
) -> list[Cell]:

    """
    Convert points into grid cells.

    resolution_for(point) determines the cell resolution.

    Multiple points falling inside the same cell are represented
    by one Cell object.
    """

    buckets = defaultdict(list)

    for point in points:

        resolution = resolution_for(point)

        ix = math.floor(point.x / resolution)
        iy = math.floor(point.y / resolution)

        key = (
            resolution,
            ix,
            iy,
        )

        buckets[key].append(point)

    cells = []

    for (
        resolution,
        ix,
        iy,
    ), bucket in buckets.items():

        elevations = [
            point.z
            for point in bucket
        ]

        cells.append(
            Cell(
                x=(ix + 0.5) * resolution,
                y=(iy + 0.5) * resolution,
                resolution=resolution,
                elevation=max(elevations),
                mean_elevation=statistics.fmean(elevations),
                semantic_class=majority_class(bucket),
                point_count=len(bucket),
            )
        )

    return sorted(
        cells,
        key=lambda cell: (
            cell.resolution,
            cell.x,
            cell.y,
        ),
    )


# ======================================================================
# ADAPTIVE GRID
# ======================================================================

def adaptive_grid(
    points: Iterable[Point],
    near: float = 10.0,
    middle: float = 30.0,
    fine: float = 0.25,
    medium: float = 0.75,
    coarse: float = 2.0,
) -> list[Cell]:

    """
    Build variable-resolution 2.5D grid.

    Default configuration:

        0 - 10 m       -> 0.25 m
        10 - 30 m      -> 0.75 m
        30 m and beyond -> 2.0 m
    """

    if not (
        0 < near < middle
        and 0 < fine <= medium <= coarse
    ):
        raise ValueError(
            "Require 0 < near < middle and "
            "0 < fine <= medium <= coarse"
        )

    def resolution_for(point: Point) -> float:

        distance = distance_xy(point)

        if distance < near:
            return fine

        if distance < middle:
            return medium

        return coarse

    return aggregate(
        points,
        resolution_for,
    )


# ======================================================================
# ZONE SUMMARY
# ======================================================================

def zone_summary(
    points: Iterable[Point],
    near: float,
    middle: float,
) -> dict[str, int]:

    """Count points assigned to each distance zone."""

    counts = {
        "fine_0_to_near_m": 0,
        "medium_near_to_middle_m": 0,
        "coarse_beyond_middle_m": 0,
    }

    for point in points:

        distance = distance_xy(point)

        if distance < near:

            counts["fine_0_to_near_m"] += 1

        elif distance < middle:

            counts["medium_near_to_middle_m"] += 1

        else:

            counts["coarse_beyond_middle_m"] += 1

    return counts


# ======================================================================
# UNIFORM GRID
# ======================================================================

def uniform_grid(
    points: Iterable[Point],
    resolution: float = 0.25,
) -> list[Cell]:

    """Build a uniform-resolution grid for comparison."""

    if resolution <= 0:
        raise ValueError(
            "Uniform resolution must be greater than zero"
        )

    return aggregate(
        points,
        lambda _point: resolution,
    )


# ======================================================================
# TIMING
# ======================================================================

def timed(
    builder,
    points: list[Point],
):

    """Measure grid construction time."""

    started = time.perf_counter()

    cells = builder(points)

    elapsed_ms = (
        time.perf_counter() - started
    ) * 1000

    return cells, elapsed_ms


# ======================================================================
# SAVE CELLS
# ======================================================================

def save_cells(
    path: Path,
    cells: list[Cell],
) -> None:

    """Save grid cells as CSV."""

    fieldnames = list(
        Cell.__annotations__
    )

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for cell in cells:

            writer.writerow(
                asdict(cell)
            )


# ======================================================================
# METRICS
# ======================================================================

def calculate_metrics(
    points: list[Point],
    uniform: list[Cell],
    adaptive: list[Cell],
    uniform_ms: float,
    adaptive_ms: float,
    near: float,
    middle: float,
    fine: float,
    medium: float,
    coarse: float,
    uniform_resolution: float,
) -> dict:

    uniform_cells = len(uniform)
    adaptive_cells = len(adaptive)

    reduction = (
        100
        * (
            1
            - adaptive_cells / uniform_cells
        )
        if uniform_cells
        else 0
    )

    return {
        "input_points": len(points),

        "strategy": {
            "near_band_m": [0, near],
            "middle_band_m": [
                near,
                middle,
            ],
            "far_band_m": [
                middle,
                100,
            ],
            "fine_m": fine,
            "medium_m": medium,
            "coarse_m": coarse,
            "uniform_resolution_m":
                uniform_resolution,
        },

        "uniform": {
            "cells": uniform_cells,
            "processing_ms":
                round(uniform_ms, 3),
        },

        "adaptive": {
            "cells": adaptive_cells,
            "processing_ms":
                round(adaptive_ms, 3),
        },

        "cell_reduction_percent":
            round(reduction, 2),

        "adaptive_point_assignments_by_zone":
            zone_summary(
                points,
                near,
                middle,
            ),
    }


# ======================================================================
# COMMAND LINE TEST / DEMO
# ======================================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Build adaptive and uniform "
            "LiDAR 2.5D grids."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        help=(
            "CSV containing "
            "x,y,z[,semantic_class]"
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
    )

    parser.add_argument(
        "--near",
        type=float,
        default=10.0,
    )

    parser.add_argument(
        "--middle",
        type=float,
        default=30.0,
    )

    parser.add_argument(
        "--fine",
        type=float,
        default=0.25,
    )

    parser.add_argument(
        "--medium",
        type=float,
        default=0.75,
    )

    parser.add_argument(
        "--coarse",
        type=float,
        default=2.0,
    )

    parser.add_argument(
        "--uniform",
        type=float,
        default=0.25,
    )

    args = parser.parse_args()

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------------
    # Load data
    # --------------------------------------------------------------

    if args.input:

        points = load_points(
            args.input
        )

    else:

        print(
            "No input supplied. "
            "Using synthetic demo scene."
        )

        points = synthetic_scene()

    # --------------------------------------------------------------
    # Build grids
    # --------------------------------------------------------------

    adaptive, adaptive_ms = timed(
        lambda p: adaptive_grid(
            p,
            args.near,
            args.middle,
            args.fine,
            args.medium,
            args.coarse,
        ),
        points,
    )

    uniform, uniform_ms = timed(
        lambda p: uniform_grid(
            p,
            args.uniform,
        ),
        points,
    )

    # --------------------------------------------------------------
    # Save
    # --------------------------------------------------------------

    save_cells(
        args.output_dir
        / "adaptive_cells.csv",
        adaptive,
    )

    save_cells(
        args.output_dir
        / "uniform_cells.csv",
        uniform,
    )

    metrics = calculate_metrics(
        points=points,
        uniform=uniform,
        adaptive=adaptive,
        uniform_ms=uniform_ms,
        adaptive_ms=adaptive_ms,
        near=args.near,
        middle=args.middle,
        fine=args.fine,
        medium=args.medium,
        coarse=args.coarse,
        uniform_resolution=args.uniform,
    )

    comparison_path = (
        args.output_dir
        / "comparison.json"
    )

    comparison_path.write_text(
        json.dumps(
            metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            metrics,
            indent=2,
        )
    )


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()