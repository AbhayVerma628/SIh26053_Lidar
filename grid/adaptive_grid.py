"""Variable-resolution LiDAR elevation grid prototype.

Input CSV columns: x,y,z[,semantic_class]. Coordinates are metres in the
sensor frame. With no --input, a deterministic synthetic LiDAR-like scene is
used so the prototype can be demonstrated immediately.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float
    semantic_class: str = "unknown"


@dataclass
class Cell:
    x: float                 # cell centre, metres
    y: float
    resolution: float        # cell side length, metres
    elevation: float         # maximum observed z, metres
    mean_elevation: float
    semantic_class: str      # majority point class
    point_count: int


def distance_xy(point: Point) -> float:
    """Horizontal sensor distance; z is deliberately not included."""
    if math.isnan(point.x) or math.isnan(point.y):
        return float("inf")
    return math.hypot(point.x, point.y)


def load_points(path: Path) -> list[Point]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"x", "y", "z"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Input CSV must have headers x,y,z[,semantic_class]")
        return [Point(float(row["x"]), float(row["y"]), float(row["z"]),
                      row.get("semantic_class") or "unknown") for row in reader]
    
def points_from_arrays(points, labels):
    """
    Convert NumPy LiDAR points + semantic labels
    into M4 Point objects.
    """
    if len(points) != len(labels):
        raise ValueError(
            "Points and labels must have the same length."
        )

    result = []

    for xyz, label in zip(points, labels):
        x, y, z = xyz

        # Convert M1 numeric label to M4 semantic name
        label_map = {
            0: "ground",
            1: "static_obstacle",
            2: "dynamic_object",
            3: "unknown",
        }

        semantic_class = label_map.get(int(label), "unknown")

        result.append(
            Point(
                x=float(x),
                y=float(y),
                z=float(z),
                semantic_class=semantic_class,
            )
        )

    return result

def synthetic_scene(seed: int = 7, count: int = 18000) -> list[Point]:
    """Road-like point cloud whose density falls off with sensor distance."""
    rng = random.Random(seed)
    points: list[Point] = []
    for _ in range(count):
        # Area sampling, tapered to resemble lower return density at range.
        radius = 100 * math.sqrt(rng.random())
        if rng.random() < radius / 180:
            continue
        theta = rng.uniform(-math.pi, math.pi)
        x, y = radius * math.cos(theta), radius * math.sin(theta)
        road = -0.015 * x + 0.004 * y + rng.gauss(0, 0.025)
        # A small elevated object makes retained elevation information visible.
        if 12 < x < 18 and -4 < y < 3:
            z, label = road + 1.45 + rng.gauss(0, 0.03), "vehicle"
        elif abs(y) > 25 and rng.random() < 0.3:
            z, label = road + 0.8 + rng.random() * 2.2, "vegetation"
        else:
            z, label = road, "ground"
        points.append(Point(x, y, z, label))
    return points


def majority_class(points: list[Point]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for point in points:
        counts[point.semantic_class] += 1
    return min(counts, key=lambda label: (-counts[label], label))


def aggregate(points: Iterable[Point], resolution_for) -> list[Cell]:
    """Bin each point by the resolution selected from its sensor distance."""
    buckets: dict[tuple[float, int, int], list[Point]] = defaultdict(list)
    for point in points:
        if math.isnan(point.x) or math.isnan(point.y) or math.isnan(point.z) or math.isinf(point.x) or math.isinf(point.y) or math.isinf(point.z):
            continue
        resolution = resolution_for(point)
        # floor works correctly for negative sensor-frame coordinates.
        key = (resolution, math.floor(point.x / resolution), math.floor(point.y / resolution))
        buckets[key].append(point)
    cells: list[Cell] = []
    for (resolution, ix, iy), bucket in buckets.items():
        elevations = [point.z for point in bucket]
        cells.append(Cell(
            x=(ix + 0.5) * resolution, y=(iy + 0.5) * resolution,
            resolution=resolution, elevation=max(elevations),
            mean_elevation=statistics.fmean(elevations),
            semantic_class=majority_class(bucket), point_count=len(bucket),
        ))
    return sorted(cells, key=lambda cell: (cell.resolution, cell.x, cell.y))


def adaptive_grid(points: Iterable[Point], near=10.0, middle=30.0,
                  fine=0.25, medium=0.75, coarse=2.0) -> list[Cell]:
    """0ΓÇônear: fine; nearΓÇômiddle: medium; beyond middle: coarse."""
    if not (0 < near < middle and 0 < fine <= medium <= coarse):
        raise ValueError("Require 0 < near < middle and fine <= medium <= coarse")
    def resolution_for(point: Point) -> float:
        distance = distance_xy(point)
        if distance < near:
            return fine
        if distance < middle:
            return medium
        return coarse
    return aggregate(points, resolution_for)


def zone_summary(points: Iterable[Point], near: float, middle: float) -> dict[str, int]:
    """Count point assignments before aggregation, making band use auditable."""
    counts = {"fine_0_to_near_m": 0, "medium_near_to_middle_m": 0, "coarse_beyond_middle_m": 0}
    for point in points:
        distance = distance_xy(point)
        if distance < near:
            counts["fine_0_to_near_m"] += 1
        elif distance < middle:
            counts["medium_near_to_middle_m"] += 1
        else:
            counts["coarse_beyond_middle_m"] += 1
    return counts


def uniform_grid(points: Iterable[Point], resolution=0.25) -> list[Cell]:
    return aggregate(points, lambda _point: resolution)


def timed(builder, points: list[Point]):
    started = time.perf_counter()
    cells = builder(points)
    return cells, (time.perf_counter() - started) * 1000


def save_cells(path: Path, cells: list[Cell]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(cells[0]).keys()) if cells else list(Cell.__annotations__))
        writer.writeheader()
        writer.writerows(asdict(cell) for cell in cells)


def write_top_down_svg(path: Path, cells: list[Cell], near: float, middle: float) -> None:
    """Write a lightweight top-down diagram from the actual adaptive cells."""
    canvas, extent = 800, 105.0
    scale = canvas / (2 * extent)
    def px(value: float) -> float:
        return canvas / 2 + value * scale
    def py(value: float) -> float:
        return canvas / 2 - value * scale
    colours = {0.25: "#1677ff", 0.75: "#f59e0b", 2.0: "#9ca3af"}
    rects = []
    for cell in cells:
        side = cell.resolution * scale
        rects.append(f'<rect x="{px(cell.x)-side/2:.2f}" y="{py(cell.y)-side/2:.2f}" width="{side:.2f}" height="{side:.2f}" fill="{colours.get(cell.resolution, "#9ca3af")}"/>')
    rings = "".join(f'<circle cx="400" cy="400" r="{r*scale:.1f}" fill="none" stroke="#334155" stroke-width="1.5" stroke-dasharray="6 6"/>' for r in (near, middle))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800" role="img" aria-label="Top-down adaptive LiDAR grid">
<rect width="800" height="800" fill="#f8fafc"/>{''.join(rects)}{rings}
<circle cx="400" cy="400" r="8" fill="#111827"/><path d="M400 378 L391 397 L409 397 Z" fill="white"/>
<text x="412" y="370" font-family="Arial" font-size="16" fill="#111827">LiDAR sensor</text>
<text x="435" y="365" font-family="Arial" font-size="16" fill="#111827">10 m: fine (0.25 m)</text>
<text x="525" y="278" font-family="Arial" font-size="16" fill="#111827">30 m: medium (0.75 m)</text>
<g font-family="Arial" font-size="17" fill="#111827"><rect x="25" y="25" width="260" height="92" rx="8" fill="white" opacity=".93"/>
<text x="45" y="53" font-weight="bold">Adaptive top-down grid</text><rect x="45" y="66" width="14" height="14" fill="#1677ff"/><text x="68" y="78">fine: 0ΓÇô10 m</text><rect x="150" y="66" width="14" height="14" fill="#f59e0b"/><text x="173" y="78">medium: 10ΓÇô30 m</text><rect x="45" y="91" width="14" height="14" fill="#9ca3af"/><text x="68" y="103">coarse: 30ΓÇô100 m</text></g>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def write_project_report(path: Path, metrics: dict) -> None:
    """Create a concise handoff document from the measured run results."""
    strategy = metrics["strategy"]
    uniform, adaptive = metrics["uniform"], metrics["adaptive"]
    reduction = 100 * (1 - adaptive["cells"] / uniform["cells"]) if uniform["cells"] else 0
    report = f"""# Member 4 ΓÇö Adaptive Grid Engine

## How exactly does variable-resolution mapping work?

Each LiDAR point `(x, y, z)` is assigned a horizontal sensor distance:

`distance = sqrt(x┬▓ + y┬▓)`

The distance selects exactly one grid resolution:

| Range from sensor | Resolution | Rationale |
| --- | ---: | --- |
| 0ΓÇô{strategy['near_band_m'][1]:g} m | {strategy['fine_m']:.2f} m | Nearby obstacle geometry needs the most detail. |
| {strategy['middle_band_m'][0]:g}ΓÇô{strategy['middle_band_m'][1]:g} m | {strategy['medium_m']:.2f} m | Mid-range structure is retained with less storage. |
| {strategy['far_band_m'][0]:g}ΓÇô{strategy['far_band_m'][1]:g} m | {strategy['coarse_m']:.2f} m | Distant context is represented compactly. |

The selected cell is found using `floor(x / resolution)` and `floor(y / resolution)`. Points sharing that cell are aggregated into one record:

`{{x, y, resolution, elevation_max, elevation_mean, semantic_class, point_count}}`

`elevation_max` preserves obstacle height; `elevation_mean` provides a smoother terrain estimate; `semantic_class` is the majority class of the points in the cell.

## Same-input comparison

The following is from the generated demonstration scene containing **{metrics['input_points']:,} points**. It is reproducible because the synthetic scene uses a fixed random seed.

| Measure | Uniform grid ({strategy['uniform_resolution_m']:.2f} m everywhere) | Adaptive grid | 
| --- | ---: | ---: |
| Occupied cells / stored cell records | {uniform['cells']:,} | {adaptive['cells']:,} |
| Measured processing time (one local run) | {uniform['processing_ms']:.3f} ms | {adaptive['processing_ms']:.3f} ms |

The adaptive representation used **{reduction:.1f}% fewer occupied cell records** on this specific input. This is a measured result for this scene and configuration, not a universal performance claim.

## Why adaptive resolution helps

Uniform fine cells allocate the same detail to nearby obstacles and distant background. The adaptive approach spends the smallest cells only where detail matters most, and uses larger far-range cells to reduce the number of occupied records while retaining elevation and class summaries. The actual reduction varies with point density, sensor range, and chosen thresholds.

## Run with your LiDAR data

```powershell
python adaptive_grid.py --input your_points.csv --output-dir run
```

Input CSV headers must be `x,y,z`; `semantic_class` is optional. The run creates adaptive and uniform cell CSVs, a JSON comparison, and a top-down SVG diagram.
"""
    path.write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build uniform and adaptive LiDAR elevation grids.")
    parser.add_argument("--input", type=Path, help="CSV with x,y,z[,semantic_class]")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--near", type=float, default=10.0)
    parser.add_argument("--middle", type=float, default=30.0)
    parser.add_argument("--fine", type=float, default=0.25)
    parser.add_argument("--medium", type=float, default=0.75)
    parser.add_argument("--coarse", type=float, default=2.0)
    parser.add_argument("--uniform", type=float, default=0.25, help="Uniform comparison resolution")
    args = parser.parse_args()
    points = load_points(args.input) if args.input else synthetic_scene()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    adaptive, adaptive_ms = timed(lambda p: adaptive_grid(p, args.near, args.middle, args.fine, args.medium, args.coarse), points)
    uniform, uniform_ms = timed(lambda p: uniform_grid(p, args.uniform), points)
    save_cells(args.output_dir / "adaptive_cells.csv", adaptive)
    save_cells(args.output_dir / "uniform_cells.csv", uniform)
    write_top_down_svg(args.output_dir / "adaptive_grid_top_down.svg", adaptive, args.near, args.middle)
    metrics = {
        "input_points": len(points),
        "strategy": {"near_band_m": [0, args.near], "middle_band_m": [args.near, args.middle],
                     "far_band_m": [args.middle, 100], "fine_m": args.fine,
                     "medium_m": args.medium, "coarse_m": args.coarse,
                     "uniform_resolution_m": args.uniform},
        "uniform": {"cells": len(uniform), "stored_cell_values": len(uniform), "processing_ms": round(uniform_ms, 3)},
        "adaptive": {"cells": len(adaptive), "stored_cell_values": len(adaptive), "processing_ms": round(adaptive_ms, 3)},
        "adaptive_point_assignments_by_zone": zone_summary(points, args.near, args.middle),
        "note": "Processing measurements are one local run; compare them only on the same machine and input.",
    }
    (args.output_dir / "comparison.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    write_project_report(args.output_dir / "M4_PROJECT_REPORT.md", metrics)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
