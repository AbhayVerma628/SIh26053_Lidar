# Member 4 — Adaptive Grid Engine

## How exactly does variable-resolution mapping work?

Each LiDAR point `(x, y, z)` is assigned a horizontal sensor distance:

`distance = sqrt(x² + y²)`

The distance selects exactly one grid resolution:

| Range from sensor | Resolution | Rationale |
| --- | ---: | --- |
| 0–10 m | 0.25 m | Nearby obstacle geometry needs the most detail. |
| 10–30 m | 0.75 m | Mid-range structure is retained with less storage. |
| 30–100 m | 2.00 m | Distant context is represented compactly. |

The selected cell is found using `floor(x / resolution)` and `floor(y / resolution)`. Points sharing that cell are aggregated into one record:

`{x, y, resolution, elevation_max, elevation_mean, semantic_class, point_count}`

`elevation_max` preserves obstacle height; `elevation_mean` provides a smoother terrain estimate; `semantic_class` is the majority class of the points in the cell.

## Same-input comparison

The following is from the generated demonstration scene containing **11,420 points**. It is reproducible because the synthetic scene uses a fixed random seed.

| Measure | Uniform grid (0.25 m everywhere) | Adaptive grid | 
| --- | ---: | ---: |
| Occupied cells / stored cell records | 11,288 | 6,656 |
| Measured processing time (one local run) | 56.058 ms | 35.657 ms |

The adaptive representation used **41.0% fewer occupied cell records** on this specific input. This is a measured result for this scene and configuration, not a universal performance claim.

## Why adaptive resolution helps

Uniform fine cells allocate the same detail to nearby obstacles and distant background. The adaptive approach spends the smallest cells only where detail matters most, and uses larger far-range cells to reduce the number of occupied records while retaining elevation and class summaries. The actual reduction varies with point density, sensor range, and chosen thresholds.

## Run with your LiDAR data

```powershell
python adaptive_grid.py --input your_points.csv --output-dir run
```

Input CSV headers must be `x,y,z`; `semantic_class` is optional. The run creates adaptive and uniform cell CSVs, a JSON comparison, and a top-down SVG diagram.
