"""Rule-based semantic segmentation baseline for preprocessed LiDAR points.

Label IDs are deliberately kept small and stable for downstream integration:
    0 = Ground
    1 = Static Obstacle
    2 = Dynamic Object (motion candidate in this single-frame baseline)
    3 = Unknown

This is a prototype, not a trained ML model.  A single point-cloud frame has no
temporal evidence of motion, so label 2 is assigned only to compact,
vehicle/pedestrian-sized elevated clusters.  Replace this function with a
PointNet++/Sparse CNN inference adapter when a trained model is available;
retain the same input/output contract.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Tuple

import numpy as np


GROUND = 0
STATIC_OBSTACLE = 1
DYNAMIC_OBJECT = 2
UNKNOWN = 3

CLASS_NAMES: Dict[int, str] = {
    GROUND: "Ground",
    STATIC_OBSTACLE: "Static Obstacle",
    DYNAMIC_OBJECT: "Dynamic Object",
    UNKNOWN: "Unknown",
}


def _as_xyz(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return an Nx3 float array and a validity mask, accepting Nx3 or wider."""
    array = np.asarray(points, dtype=float)
    if array.ndim != 2 or array.shape[1] < 3:
        raise ValueError("points must be a 2-D array with at least x, y, z columns")
    xyz = array[:, :3]
    return xyz, np.isfinite(xyz).all(axis=1)


def _local_ground(xyz: np.ndarray, cell_size: float) -> np.ndarray:
    """Estimate a local ground height from the low percentile in each XY cell."""
    cells = np.floor(xyz[:, :2] / cell_size).astype(np.int64)
    ground_by_cell: Dict[Tuple[int, int], float] = {}
    for cell in np.unique(cells, axis=0):
        in_cell = np.all(cells == cell, axis=1)
        # The 15th percentile is less sensitive than min(z) to isolated noise.
        ground_by_cell[(int(cell[0]), int(cell[1]))] = float(np.percentile(xyz[in_cell, 2], 15))
    return np.asarray([ground_by_cell[(int(c[0]), int(c[1]))] for c in cells])


def _connected_components_xy(xy: np.ndarray, radius: float) -> list[np.ndarray]:
    """Find compact XY components using a simple spatial-hash neighbourhood."""
    if len(xy) == 0:
        return []
    grid = np.floor(xy / radius).astype(np.int64)
    buckets: Dict[Tuple[int, int], list[int]] = {}
    for index, cell in enumerate(grid):
        buckets.setdefault((int(cell[0]), int(cell[1])), []).append(index)

    visited = np.zeros(len(xy), dtype=bool)
    components: list[np.ndarray] = []
    radius_sq = radius * radius
    for start in range(len(xy)):
        if visited[start]:
            continue
        visited[start] = True
        queue: deque[int] = deque([start])
        component: list[int] = []
        while queue:
            current = queue.popleft()
            component.append(current)
            cell = grid[current]
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for neighbour in buckets.get((int(cell[0] + dx), int(cell[1] + dy)), []):
                        if not visited[neighbour] and np.sum((xy[current] - xy[neighbour]) ** 2) <= radius_sq:
                            visited[neighbour] = True
                            queue.append(neighbour)
        components.append(np.asarray(component, dtype=int))
    return components


def _looks_like_dynamic_candidate(cluster: np.ndarray) -> bool:
    """Heuristic for compact raised objects; this is not real motion detection."""
    if len(cluster) < 12:
        return False
    extents = np.ptp(cluster, axis=0)
    horizontal = sorted(extents[:2])
    width, length = horizontal[0], horizontal[1]
    height = extents[2]
    # Broad pedestrian/vehicle-sized envelope; walls and poles are excluded.
    return 0.25 <= width <= 2.8 and 0.45 <= length <= 6.5 and 0.35 <= height <= 3.2


def semantic_segmentation(points: np.ndarray) -> np.ndarray:
    """Assign one baseline semantic label to every input LiDAR point.

    Parameters
    ----------
    points:
        Preprocessed Nx3 (or NxK, K >= 3) numeric array. Columns 0:3 are x, y,
        z in metres. Extra columns such as intensity are accepted and ignored.

    Returns
    -------
    numpy.ndarray
        Integer labels of shape ``(N,)``. Every input row receives exactly one
        label; non-finite, sparse, or out-of-range points receive ``UNKNOWN``.
    """
    xyz, valid = _as_xyz(points)
    labels = np.full(len(xyz), UNKNOWN, dtype=np.int32)
    if not np.any(valid):
        return labels

    valid_indices = np.flatnonzero(valid)
    cloud = xyz[valid]
    distance = np.linalg.norm(cloud[:, :2], axis=1)
    in_range = distance <= 60.0
    if not np.any(in_range):
        return labels

    active_indices = valid_indices[in_range]
    active_cloud = cloud[in_range]
    local_ground = _local_ground(active_cloud, cell_size=0.75)
    height_above_ground = active_cloud[:, 2] - local_ground

    # Road/terrain band around the local ground estimate.
    ground_mask = np.abs(height_above_ground) <= 0.18
    labels[active_indices[ground_mask]] = GROUND

    # Remaining sufficiently raised, dense points default to static obstacles.
    elevated_mask = height_above_ground > 0.25
    labels[active_indices[elevated_mask]] = STATIC_OBSTACLE

    # Identify compact elevated components and relabel likely movable shapes.
    elevated_local_indices = np.flatnonzero(elevated_mask)
    elevated_cloud = active_cloud[elevated_mask]
    for component in _connected_components_xy(elevated_cloud[:, :2], radius=0.9):
        cluster = elevated_cloud[component]
        if _looks_like_dynamic_candidate(cluster):
            labels[active_indices[elevated_local_indices[component]]] = DYNAMIC_OBJECT

    return labels


def class_counts(labels: np.ndarray) -> Dict[str, int]:
    """Return stable, human-readable counts for all four classes."""
    labels = np.asarray(labels)
    return {name: int(np.sum(labels == class_id)) for class_id, name in CLASS_NAMES.items()}
