"""Generate a reproducible sample PCD frame, run the baseline, and save a screenshot."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from semantic_segmentation import (
    CLASS_NAMES,
    DYNAMIC_OBJECT,
    GROUND,
    STATIC_OBSTACLE,
    UNKNOWN,
    class_counts,
    semantic_segmentation,
)

HERE = Path(__file__).resolve().parent
PCD_PATH = HERE / "sample_lidar_frame.pcd"
SCREENSHOT_PATH = HERE / "segmentation_result.png"


def _grid_surface(x_range, y_range, z_value, step=0.30):
    x, y = np.meshgrid(np.arange(*x_range, step), np.arange(*y_range, step))
    z = np.full_like(x, z_value, dtype=float)
    return np.column_stack((x.ravel(), y.ravel(), z.ravel()))


def create_sample_frame() -> np.ndarray:
    """Make a compact, LiDAR-like road scene for a deterministic smoke test.

    The scene is synthetic (not an ML training dataset): a road, a static wall,
    a static pole, a vehicle-shaped elevated cluster, and a few unknown points.
    """
    rng = np.random.default_rng(26053)
    road = _grid_surface((-12, 15), (-7, 7), 0.0)
    road[:, 2] += rng.normal(0, 0.025, len(road))

    # Static wall at the far side of the road.
    wall_y, wall_z = np.meshgrid(np.arange(4.5, 11.5, 0.22), np.arange(0.25, 3.4, 0.20))
    wall = np.column_stack((np.full(wall_y.size, -8.5), wall_y.ravel(), wall_z.ravel()))

    # Static pole: cylindrical vertical structure.
    angle, pole_z = np.meshgrid(np.linspace(0, 2 * np.pi, 20, endpoint=False), np.arange(0.15, 3.8, 0.12))
    pole = np.column_stack((2.0 + 0.14 * np.cos(angle).ravel(), -4.3 + 0.14 * np.sin(angle).ravel(), pole_z.ravel()))

    # Compact vehicle-sized box surface. The baseline calls it a motion candidate.
    vehicle_parts = [
        _grid_surface((3.0, 5.3), (1.0, 2.7), 1.55, step=0.16),
        _grid_surface((3.0, 5.3), (1.0, 2.7), 0.28, step=0.16),
    ]
    for x_value in (3.0, 5.3):
        y, z = np.meshgrid(np.arange(1.0, 2.7, 0.16), np.arange(0.28, 1.55, 0.16))
        vehicle_parts.append(np.column_stack((np.full(y.size, x_value), y.ravel(), z.ravel())))
    for y_value in (1.0, 2.7):
        x, z = np.meshgrid(np.arange(3.0, 5.3, 0.16), np.arange(0.28, 1.55, 0.16))
        vehicle_parts.append(np.column_stack((x.ravel(), np.full(x.size, y_value), z.ravel())))
    vehicle = np.vstack(vehicle_parts) + rng.normal(0, 0.01, (sum(len(p) for p in vehicle_parts), 3))

    # Intentionally sparse points - expected to remain Unknown.
    unknown = np.array([[75.0, 0.0, 0.0], [np.nan, 1.0, 0.0], [0.0, np.inf, 0.0]])
    return np.vstack((road, wall, pole, vehicle, unknown))


def write_ascii_pcd(points: np.ndarray, path: Path) -> None:
    """Write a standard ASCII XYZ PCD file. NaNs are kept for interface testing."""
    header = "\n".join([
        "# .PCD v0.7 - Point Cloud Data file format",
        "VERSION 0.7",
        "FIELDS x y z",
        "SIZE 4 4 4",
        "TYPE F F F",
        "COUNT 1 1 1",
        f"WIDTH {len(points)}",
        "HEIGHT 1",
        "VIEWPOINT 0 0 0 1 0 0 0",
        f"POINTS {len(points)}",
        "DATA ascii",
    ])
    np.savetxt(path, points, fmt="%.4f", header=header, comments="")


def read_ascii_xyz_pcd(path: Path) -> np.ndarray:
    """Read the included simple ASCII XYZ PCD frame for the integration demo."""
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        data_line = next(i for i, line in enumerate(lines) if line.strip().lower() == "data ascii")
    except StopIteration as error:
        raise ValueError("Only ASCII PCD files with a 'DATA ascii' header are supported by this demo reader") from error
    return np.loadtxt(lines[data_line + 1 :], dtype=float, ndmin=2)


def save_screenshot(points: np.ndarray, labels: np.ndarray, counts: dict[str, int]) -> None:
    """Save a dependency-light PNG screenshot using Pillow."""
    palette = {GROUND: "#4daf4a", STATIC_OBSTACLE: "#e41a1c", DYNAMIC_OBJECT: "#377eb8", UNKNOWN: "#888888"}
    image = Image.new("RGB", (1440, 760), "#f8fafc")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype("arial.ttf", 28)
    heading_font = ImageFont.truetype("arial.ttf", 20)
    body_font = ImageFont.truetype("arial.ttf", 16)
    tiny_font = ImageFont.truetype("arial.ttf", 13)

    draw.text((40, 22), "SIH26053 - LiDAR Point-Cloud Segmentation Prototype", fill="#102a43", font=title_font)
    draw.text((40, 60), "Rule-based baseline (not a trained ML model)", fill="#52606d", font=body_font)
    panels = [(40, "Input sample LiDAR frame"), (760, "Semantic labels")]
    x_min, x_max, y_min, y_max = -13.0, 16.0, -8.0, 12.0

    def project(point, left):
        px = left + 42 + (point[0] - x_min) / (x_max - x_min) * 616
        py = 680 - 42 - (point[1] - y_min) / (y_max - y_min) * 520
        return int(px), int(py)

    for left, heading in panels:
        draw.rounded_rectangle((left, 106, left + 696, 690), radius=12, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((left + 20, 122), heading, fill="#1f2933", font=heading_font)
        for tick in range(-10, 16, 5):
            px, _ = project((tick, 0), left)
            draw.line((px, 158, px, 638), fill="#edf2f7", width=1)
            draw.text((px - 11, 647), f"{tick}", fill="#7b8794", font=tiny_font)
        for tick in range(-5, 11, 5):
            _, py = project((0, tick), left)
            draw.line((left + 42, py, left + 658, py), fill="#edf2f7", width=1)
            draw.text((left + 8, py - 7), f"{tick}", fill="#7b8794", font=tiny_font)
        draw.text((left + 592, 655), "x (m)", fill="#52606d", font=tiny_font)
        draw.text((left + 9, 150), "y (m)", fill="#52606d", font=tiny_font)

    finite = np.isfinite(points[:, :2]).all(axis=1)
    for point in points[finite]:
        px, py = project(point, 40)
        draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill="#6b7280")
    for class_id, _name in CLASS_NAMES.items():
        for point in points[(labels == class_id) & finite]:
            px, py = project(point, 760)
            draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=palette[class_id])

    legend_y = 178
    for class_id, name in CLASS_NAMES.items():
        draw.rectangle((1210, legend_y, 1224, legend_y + 14), fill=palette[class_id])
        draw.text((1232, legend_y - 2), f"{name}: {counts[name]}", fill="#334e68", font=body_font)
        legend_y += 31
    draw.text((790, 610), "Blue = shape-based motion candidate", fill="#334e68", font=body_font)
    draw.text((790, 634), "(single frame cannot verify motion)", fill="#52606d", font=tiny_font)
    image.save(SCREENSHOT_PATH)


def main() -> None:
    write_ascii_pcd(create_sample_frame(), PCD_PATH)
    points = read_ascii_xyz_pcd(PCD_PATH)
    labels = semantic_segmentation(points)
    counts = class_counts(labels)
    save_screenshot(points, labels, counts)

    print(f"Input: {PCD_PATH.name} ({len(points)} points)")
    print(f"Output: labels shape = {labels.shape}, dtype = {labels.dtype}")
    for name, count in counts.items():
        print(f"{name}: {count}")
    print(f"Screenshot: {SCREENSHOT_PATH.name}")


if __name__ == "__main__":
    main()
