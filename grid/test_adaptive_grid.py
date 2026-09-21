"""Standard-library regression tests for the adaptive grid engine."""
import unittest

from grid.adaptive_grid import Point, adaptive_grid, distance_xy, uniform_grid


class AdaptiveGridTests(unittest.TestCase):
    def test_distance_uses_horizontal_coordinates_only(self):
        self.assertEqual(distance_xy(Point(3, 4, 99)), 5)

    def test_each_distance_band_selects_its_resolution(self):
        points = [Point(1, 0, 0), Point(15, 0, 0), Point(35, 0, 0)]
        cells = adaptive_grid(points, near=10, middle=30, fine=.25, medium=.75, coarse=2)
        self.assertEqual({cell.resolution for cell in cells}, {.25, .75, 2})

    def test_cell_keeps_useful_elevation_and_majority_class(self):
        points = [Point(.1, .1, 1, "ground"), Point(.15, .15, 3, "vehicle"),
                  Point(.2, .2, 2, "ground")]
        cell = adaptive_grid(points)[0]
        self.assertEqual(cell.point_count, 3)
        self.assertEqual(cell.elevation, 3)
        self.assertEqual(cell.semantic_class, "ground")
        self.assertEqual(cell.mean_elevation, 2)

    def test_uniform_grid_has_one_resolution(self):
        cells = uniform_grid([Point(0, 0, 0), Point(3, 3, 0)], resolution=.5)
        self.assertTrue(all(cell.resolution == .5 for cell in cells))


if __name__ == "__main__":
    unittest.main(verbosity=2)
