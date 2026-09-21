"""
LiDAR Visualization Module
Member 3 - Computer Vision / Visualization

Responsibilities:
    1. Visualize raw/preprocessed LiDAR point clouds.
    2. Visualize semantic segmentation results.
    3. Visualize the final adaptive 2.5D grid produced by Member 4.

Important:
    This module does NOT create or calculate the adaptive grid.
    Adaptive-grid generation belongs to adaptive_grid.py.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d


# ----------------------------------------------------------------------
# SEMANTIC COLORS
# ----------------------------------------------------------------------

SEMANTIC_COLORS = {
    0: [0.20, 0.80, 0.20],   # Ground - green
    1: [0.90, 0.20, 0.20],   # Static obstacle - red
    2: [0.20, 0.40, 1.00],   # Dynamic candidate - blue
    3: [0.60, 0.60, 0.60],   # Unknown - grey
}


# ----------------------------------------------------------------------
# BASIC POINT CLOUD LOADING
# ----------------------------------------------------------------------

def load_point_cloud(path: str | Path) -> o3d.geometry.PointCloud:
    """Load a PCD/PLY point cloud using Open3D."""
    path = str(path)

    pcd = o3d.io.read_point_cloud(path)

    if pcd.is_empty():
        raise ValueError(f"Point cloud is empty or could not be loaded: {path}")

    return pcd


# ----------------------------------------------------------------------
# HEIGHT-BASED VISUALIZATION
# ----------------------------------------------------------------------

def height_colors(points: np.ndarray) -> np.ndarray:
    """
    Generate normalized colors based on point height.

    This is useful for showing elevation variation before
    semantic/adaptive visualization.
    """
    if len(points) == 0:
        return np.empty((0, 3))

    z = points[:, 2]

    z_min = np.min(z)
    z_max = np.max(z)

    if z_max == z_min:
        normalized = np.zeros_like(z)
    else:
        normalized = (z - z_min) / (z_max - z_min)

    # Use matplotlib colormap without storing custom colors.
    cmap = plt.get_cmap("viridis")
    return cmap(normalized)[:, :3]


def visualize_height(
    points: np.ndarray,
    window_name: str = "LiDAR Height Visualization",
) -> None:
    """Display a 3D point cloud colored according to height."""

    if len(points) == 0:
        print("No points available for visualization.")
        return

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(height_colors(points))

    o3d.visualization.draw_geometries(
        [pcd],
        window_name=window_name,
    )


# ----------------------------------------------------------------------
# SEMANTIC VISUALIZATION
# ----------------------------------------------------------------------

def semantic_colors(labels: np.ndarray) -> np.ndarray:
    """Convert integer semantic labels into RGB colors."""

    labels = np.asarray(labels)

    colors = np.zeros((len(labels), 3), dtype=float)

    for label, color in SEMANTIC_COLORS.items():
        colors[labels == label] = color

    return colors


def visualize_semantic(
    points: np.ndarray,
    labels: np.ndarray,
    window_name: str = "Semantic LiDAR Visualization",
) -> None:
    """
    Visualize semantic segmentation results.

    Labels:
        0 = Ground
        1 = Static obstacle
        2 = Dynamic candidate
        3 = Unknown
    """

    points = np.asarray(points)
    labels = np.asarray(labels)

    if len(points) != len(labels):
        raise ValueError(
            f"Points and labels must have the same length. "
            f"Got {len(points)} points and {len(labels)} labels."
        )

    if len(points) == 0:
        print("No points available for visualization.")
        return

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(
        semantic_colors(labels)
    )

    o3d.visualization.draw_geometries(
        [pcd],
        window_name=window_name,
    )


# ----------------------------------------------------------------------
# TOP-DOWN POINT CLOUD VIEW
# ----------------------------------------------------------------------

def plot_top_down(
    points: np.ndarray,
    labels: np.ndarray | None = None,
    title: str = "LiDAR Top-Down View",
) -> None:
    """
    Plot the point cloud from the top.

    X axis -> horizontal
    Y axis -> vertical
    """

    points = np.asarray(points)

    if len(points) == 0:
        print("No points available for top-down visualization.")
        return

    plt.figure(figsize=(10, 7))

    if labels is None:
        plt.scatter(
            points[:, 0],
            points[:, 1],
            s=1,
        )
    else:
        colors = semantic_colors(np.asarray(labels))

        plt.scatter(
            points[:, 0],
            points[:, 1],
            s=1,
            c=colors,
        )

    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title(title)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()


# ----------------------------------------------------------------------
# ADAPTIVE 2.5D GRID VISUALIZATION
# ----------------------------------------------------------------------

def plot_adaptive_grid(
    cells,
    title: str = "Adaptive Variable-Resolution 2.5D LiDAR Map",
    save_path: str | Path | None = None,
) -> None:
    """
    Visualize cells generated by M4's adaptive_grid().

    IMPORTANT:
        This function only VISUALIZES the cells.
        It does not calculate resolution or create cells.

    Each cell is expected to contain:
        x
        y
        resolution
        elevation
        mean_elevation
        semantic_class
        point_count
    """

    cells = list(cells)

    if not cells:
        print("No adaptive-grid cells available for visualization.")
        return

    fig, ax = plt.subplots(figsize=(11, 8))

    # Resolution-based display colors.
    # These are only visualization categories.
    resolution_values = sorted(
        set(float(cell.resolution) for cell in cells)
    )

    # Matplotlib automatically handles the color mapping.
    cmap = plt.get_cmap("viridis")

    if len(resolution_values) == 1:
        normalized_resolution = {
            resolution_values[0]: 0.5
        }
    else:
        normalized_resolution = {
            resolution: index / (len(resolution_values) - 1)
            for index, resolution in enumerate(resolution_values)
        }

    for cell in cells:
        resolution = float(cell.resolution)

        rect = plt.Rectangle(
            (
                cell.x - resolution / 2,
                cell.y - resolution / 2,
            ),
            resolution,
            resolution,
            facecolor=cmap(normalized_resolution[resolution]),
            edgecolor="black",
            linewidth=0.15,
            alpha=0.75,
        )

        ax.add_patch(rect)

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title(title)
    ax.set_aspect("equal")

    # Show the sensor at origin.
    ax.scatter(
        [0],
        [0],
        marker="^",
        s=100,
        label="LiDAR sensor",
    )

    ax.legend()
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Saved adaptive-grid visualization -> {save_path}")

    plt.show()


# ----------------------------------------------------------------------
# 2.5D ELEVATION VISUALIZATION
# ----------------------------------------------------------------------

def plot_25d_elevation(
    cells,
    title: str = "Adaptive 2.5D Elevation Map",
    save_path: str | Path | None = None,
) -> None:
    """
    Display the elevation stored in M4's adaptive cells.

    The adaptive grid itself is NOT generated here.
    """

    cells = list(cells)

    if not cells:
        print("No cells available for 2.5D visualization.")
        return

    x = np.array([cell.x for cell in cells])
    y = np.array([cell.y for cell in cells])
    z = np.array([cell.elevation for cell in cells])

    plt.figure(figsize=(11, 8))

    scatter = plt.scatter(
        x,
        y,
        c=z,
        s=np.array([cell.resolution for cell in cells]) * 15,
    )

    plt.colorbar(scatter, label="Elevation (m)")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title(title)
    plt.axis("equal")
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Saved 2.5D elevation visualization -> {save_path}")

    plt.show()


# ----------------------------------------------------------------------
# SUMMARY
# ----------------------------------------------------------------------

def print_visualization_summary(
    points: np.ndarray,
    labels: np.ndarray | None = None,
    cells=None,
) -> None:
    """Print useful information for the integration/demo."""

    print("\n===== VISUALIZATION SUMMARY =====")
    print(f"Point count: {len(points)}")

    if labels is not None:
        labels = np.asarray(labels)

        label_names = {
            0: "Ground",
            1: "Static Obstacle",
            2: "Dynamic Object",
            3: "Unknown",
        }

        print("\nSemantic classes:")

        for label, name in label_names.items():
            count = int(np.sum(labels == label))
            print(f"  {name}: {count}")

    if cells is not None:
        cells = list(cells)
        print(f"\nAdaptive grid cells: {len(cells)}")

        resolutions = sorted(
            set(float(cell.resolution) for cell in cells)
        )

        print(
            "Resolutions:",
            ", ".join(f"{r:g} m" for r in resolutions),
        )


# ----------------------------------------------------------------------
# SIMPLE TEST
# ----------------------------------------------------------------------

if __name__ == "__main__":

    # This section is only a basic manual test.
    # The final integrated pipeline should be started by M5's main.py.

    pcd_path = Path("data/lidar/0001.pcd")

    if not pcd_path.exists():
        print(f"Test file not found: {pcd_path}")
        print("Run this module from the project root.")
    else:
        pcd = load_point_cloud(pcd_path)

        points = np.asarray(pcd.points)

        print(f"Loaded {len(points)} LiDAR points.")

        visualize_height(points)