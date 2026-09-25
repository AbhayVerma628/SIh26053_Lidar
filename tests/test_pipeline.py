"""
TERA PULSE - Automated Pipeline Test Suite
Tests all 5 member modules and end-to-end integration.
"""

import sys
import unittest
from pathlib import Path
import numpy as np

# Ensure root in sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from preprocessing.preprocess_lidar import (
    generate_synthetic_scan,
    remove_invalid_points,
    distance_filter,
    height_filter,
    voxel_downsample,
)
from ml.semantic_segmentation import semantic_segmentation, class_counts
from adaptive_grid import points_from_arrays, adaptive_grid, uniform_grid
from navigation.path_planner import (
    analyze_navigation_cells,
    find_start_goal,
    a_star,
    cell_distance,
)
from navigation.navigation_controller import (
    simulate_vehicle_navigation,
    smooth_path_waypoints,
    PurePursuitController,
)


class TestTeraPulsePipeline(unittest.TestCase):

    def setUp(self):
        # Generate reproducible synthetic test scan
        self.raw_points, self.raw_intensity = generate_synthetic_scan(n_ground=2000, n_objects=4, seed=42)

    def test_stage1_preprocessing(self):
        """Test Member 2 Preprocessing filtering pipeline."""
        pts, inten = remove_invalid_points(self.raw_points, self.raw_intensity)
        self.assertGreater(len(pts), 0)
        pts, inten = distance_filter(pts, inten, min_range=0.5, max_range=60.0)
        self.assertGreater(len(pts), 0)
        pts, inten = height_filter(pts, inten, z_min=-2.5, z_max=3.0)
        self.assertGreater(len(pts), 0)
        pts, inten = voxel_downsample(pts, inten, voxel_size=0.3)
        self.assertGreater(len(pts), 0)
        self.assertLessEqual(len(pts), len(self.raw_points))

    def test_stage2_semantic_segmentation(self):
        """Test Member 1 Semantic Segmentation labeling."""
        labels = semantic_segmentation(self.raw_points)
        self.assertEqual(len(labels), len(self.raw_points))
        counts = class_counts(labels)
        self.assertIn("Ground", counts)
        self.assertIn("Static Obstacle", counts)
        self.assertGreater(counts["Ground"], 0)

    def test_stage3_adaptive_grid(self):
        """Test Member 4 Adaptive 2.5D Grid generation and compression."""
        labels = semantic_segmentation(self.raw_points)
        m4_points = points_from_arrays(self.raw_points, labels)
        self.assertEqual(len(m4_points), len(self.raw_points))

        adaptive_cells = adaptive_grid(m4_points)
        uniform_cells = uniform_grid(m4_points, resolution=0.25)

        self.assertGreater(len(adaptive_cells), 0)
        self.assertGreater(len(uniform_cells), 0)
        # Adaptive cells must achieve reduction over uniform 0.25m cells
        self.assertLess(len(adaptive_cells), len(uniform_cells))

    def test_stage4_path_planning(self):
        """Test Member 5 Traversability analysis and A* path planning."""
        labels = semantic_segmentation(self.raw_points)
        m4_points = points_from_arrays(self.raw_points, labels)
        cells = adaptive_grid(m4_points)

        traversable, blocked = analyze_navigation_cells(cells)
        self.assertGreater(len(traversable), 0)

        start, goal = find_start_goal(cells)
        self.assertIsNotNone(start)
        self.assertIsNotNone(goal)

        path = a_star(start, goal, traversable)
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 1)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)

    def test_stage5_motion_controller(self):
        """Test Member 5 Pure Pursuit motion simulation."""
        from adaptive_grid import Cell
        # Create a representative 10-meter straight path with varying resolutions
        test_path = [
            Cell(x=float(i), y=0.0, resolution=0.25 if i < 3 else 0.75,
                 elevation=0.0, mean_elevation=0.0, semantic_class="ground", point_count=10)
            for i in range(15)
        ]

        waypoints = smooth_path_waypoints(test_path)
        self.assertGreater(len(waypoints), len(test_path))

        sim = simulate_vehicle_navigation(test_path, dt=0.1)
        self.assertTrue(sim["success"])
        self.assertGreater(sim["total_distance_m"], 5.0)
        self.assertGreater(len(sim["history"]), 10)


if __name__ == "__main__":
    unittest.main()
