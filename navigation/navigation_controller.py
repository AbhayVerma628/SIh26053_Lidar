"""
TERA PULSE - Autonomous Vehicle Navigation Controller & Simulator
SIH26053: Adaptive Variable Resolution 2.5D LiDAR Mapping

This module bridges high-level A* path planning cells with actual autonomous vehicle
kinematics and motion control:
1. Trajectory Smoothing: Converts discrete A* cell centers into smooth continuous waypoints.
2. Pure Pursuit Motion Controller: Computes real-time steering angle and velocity commands.
3. Kinematic Simulation: Simulates vehicle state [x, y, theta, v, steering] from start to goal.
4. Telemetry Logging: Outputs timestamped execution telemetry for analysis and visualization.
"""

from __future__ import annotations

import math
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Any


@dataclass
class VehicleState:
    x: float
    y: float
    theta: float        # Heading angle in radians (0 = along +X axis)
    v: float            # Linear velocity in m/s
    steering: float     # Front wheel steering angle in radians


@dataclass
class Waypoint:
    x: float
    y: float
    resolution: float
    target_speed: float
    curvature: float = 0.0


class PurePursuitController:
    """
    Pure Pursuit path-following controller with dynamic velocity profiling
    for an Ackermann / bicycle-model autonomous vehicle (UGV).
    """

    def __init__(
        self,
        wheelbase: float = 1.8,             # Vehicle wheelbase in meters
        lookahead_distance: float = 1.5,    # Lookahead distance in meters
        max_speed: float = 3.5,             # Max linear speed in m/s (~12.6 km/h)
        max_steering_angle: float = math.radians(32.0), # Max steering angle (~32 deg)
        max_acceleration: float = 1.5,      # Max acceleration m/s^2
        max_deceleration: float = 2.0,      # Max deceleration m/s^2
    ):
        self.wheelbase = wheelbase
        self.lookahead_distance = lookahead_distance
        self.max_speed = max_speed
        self.max_steering_angle = max_steering_angle
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration

    def find_lookahead_point(
        self, state: VehicleState, waypoints: List[Waypoint]
    ) -> Tuple[Waypoint, int]:
        """Find the waypoint at or just beyond the lookahead distance."""
        closest_idx = 0
        min_dist = float("inf")

        # Find closest waypoint ahead of the vehicle
        for i, wp in enumerate(waypoints):
            dx = wp.x - state.x
            dy = wp.y - state.y
            dist = math.hypot(dx, dy)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i

        # Look forward for the first waypoint >= lookahead_distance
        target_wp = waypoints[-1]
        target_idx = len(waypoints) - 1

        for i in range(closest_idx, len(waypoints)):
            wp = waypoints[i]
            dist = math.hypot(wp.x - state.x, wp.y - state.y)
            if dist >= self.lookahead_distance:
                target_wp = wp
                target_idx = i
                break

        return target_wp, target_idx

    def compute_control(
        self, state: VehicleState, waypoints: List[Waypoint], dt: float = 0.1
    ) -> Tuple[float, float, str]:
        """
        Compute (steering_angle_rad, target_velocity_mps, status_label)
        using Pure Pursuit geometry.
        """
        target_wp, target_idx = self.find_lookahead_point(state, waypoints)
        goal_wp = waypoints[-1]
        dist_to_goal = math.hypot(goal_wp.x - state.x, goal_wp.y - state.y)

        # Check arrival condition
        if dist_to_goal < 0.6:
            return 0.0, 0.0, "ARRIVED_AT_GOAL"

        # Transform target point into vehicle local coordinate frame
        dx = target_wp.x - state.x
        dy = target_wp.y - state.y

        # Local coordinates (alpha is angle to target relative to heading)
        alpha = math.atan2(dy, dx) - state.theta
        # Normalize alpha to [-pi, pi]
        alpha = (alpha + math.pi) % (2 * math.pi) - math.pi

        # Pure Pursuit curvature: kappa = 2 * sin(alpha) / Ld
        lookahead = max(0.8, math.hypot(dx, dy))
        curvature = 2.0 * math.sin(alpha) / lookahead

        # Steering angle delta = atan(kappa * L)
        steering = math.atan2(self.wheelbase * curvature, 1.0)
        # Clamp steering
        steering = max(-self.max_steering_angle, min(self.max_steering_angle, steering))

        # Dynamic velocity profile:
        # Slow down on sharp turns and when approaching goal
        curve_factor = max(0.3, 1.0 - abs(steering) / self.max_steering_angle * 0.6)
        goal_factor = min(1.0, max(0.25, dist_to_goal / 6.0))
        target_v = self.max_speed * curve_factor * goal_factor

        # Smooth acceleration / deceleration
        if target_v > state.v:
            v_cmd = min(target_v, state.v + self.max_acceleration * dt)
        else:
            v_cmd = max(target_v, state.v - self.max_deceleration * dt)

        # Status text
        steer_deg = math.degrees(steering)
        if abs(steer_deg) > 12.0:
            status = f"TURNING_{'LEFT' if steer_deg > 0 else 'RIGHT'}"
        elif v_cmd < state.v and dist_to_goal < 5.0:
            status = "DECELERATING_APPROACH"
        elif v_cmd > state.v + 0.1:
            status = "ACCELERATING"
        else:
            status = "CRUISING"

        return steering, v_cmd, status


def smooth_path_waypoints(
    cells: List[Any], points_per_segment: int = 4
) -> List[Waypoint]:
    """
    Interpolate and smooth discrete A* cell centers into continuous waypoints
    using Catmull-Rom spline formulation.
    """
    if not cells:
        return []

    # Raw coordinates from cells
    raw_coords = []
    for c in cells:
        x = getattr(c, "x", None) if hasattr(c, "x") else c.get("x")
        y = getattr(c, "y", None) if hasattr(c, "y") else c.get("y")
        res = getattr(c, "resolution", 0.5) if hasattr(c, "resolution") else c.get("resolution", 0.5)
        raw_coords.append((float(x), float(y), float(res)))

    if len(raw_coords) == 1:
        return [Waypoint(raw_coords[0][0], raw_coords[0][1], raw_coords[0][2], 0.0)]

    waypoints: List[Waypoint] = []

    # Multi-point Catmull-Rom smoothing
    pts = [(raw_coords[0][0], raw_coords[0][1])] + [(c[0], c[1]) for c in raw_coords] + [(raw_coords[-1][0], raw_coords[-1][1])]

    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        res = raw_coords[min(i - 1, len(raw_coords) - 1)][2]

        for step in range(points_per_segment):
            t = step / float(points_per_segment)
            t2 = t * t
            t3 = t2 * t

            # Catmull-Rom interpolation basis
            x = 0.5 * (
                (2.0 * p1[0])
                + (-p0[0] + p2[0]) * t
                + (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2.0 * p1[1])
                + (-p0[1] + p2[1]) * t
                + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3
            )
            waypoints.append(Waypoint(x=x, y=y, resolution=res, target_speed=2.5))

    # Add final destination point
    last = raw_coords[-1]
    waypoints.append(Waypoint(x=last[0], y=last[1], resolution=last[2], target_speed=0.0))
    return waypoints


def simulate_vehicle_navigation(
    cells: List[Any],
    dt: float = 0.1,
    max_duration_sec: float = 60.0,
) -> Dict[str, Any]:
    """
    Simulates autonomous vehicle driving along the planned path from Start to Goal.
    Returns simulation history, metrics, and commands.
    """
    waypoints = smooth_path_waypoints(cells, points_per_segment=4)
    if not waypoints:
        return {"success": False, "message": "No waypoints generated"}

    controller = PurePursuitController()

    # Initial vehicle state aligned with first segment
    start_wp = waypoints[0]
    next_wp = waypoints[min(3, len(waypoints) - 1)]
    initial_heading = math.atan2(next_wp.y - start_wp.y, next_wp.x - start_wp.x)

    state = VehicleState(
        x=start_wp.x,
        y=start_wp.y,
        theta=initial_heading,
        v=0.0,
        steering=0.0,
    )

    history: List[Dict[str, Any]] = []
    goal = waypoints[-1]

    sim_time = 0.0
    total_travel_distance = 0.0
    arrived = False

    while sim_time < max_duration_sec:
        # Distance to final goal
        dist_to_goal = math.hypot(goal.x - state.x, goal.y - state.y)

        # Compute controller commands
        steering_cmd, v_cmd, status = controller.compute_control(state, waypoints, dt=dt)

        # Record telemetry
        history.append({
            "time_sec": round(sim_time, 2),
            "x": round(state.x, 3),
            "y": round(state.y, 3),
            "heading_deg": round(math.degrees(state.theta), 2),
            "velocity_mps": round(state.v, 2),
            "velocity_kmh": round(state.v * 3.6, 2),
            "steering_deg": round(math.degrees(steering_cmd), 2),
            "dist_to_goal_m": round(dist_to_goal, 2),
            "status": status,
        })

        if status == "ARRIVED_AT_GOAL" or dist_to_goal < 0.35:
            arrived = True
            break

        # Kinematic vehicle state update (Bicycle Model)
        state.steering = steering_cmd
        state.v = v_cmd

        # Movement in dt
        ds = state.v * dt
        state.x += ds * math.cos(state.theta)
        state.y += ds * math.sin(state.theta)
        state.theta += (state.v / controller.wheelbase) * math.tan(state.steering) * dt
        # Normalize theta
        state.theta = (state.theta + math.pi) % (2 * math.pi) - math.pi

        total_travel_distance += ds
        sim_time += dt

    return {
        "success": arrived,
        "total_time_sec": round(sim_time, 2),
        "total_distance_m": round(total_travel_distance, 2),
        "average_speed_mps": round(total_travel_distance / max(0.1, sim_time), 2),
        "max_speed_mps": round(max([h["velocity_mps"] for h in history], default=0.0), 2),
        "num_waypoints": len(waypoints),
        "telemetry_samples": len(history),
        "history": history,
        "waypoints": waypoints,
    }


def save_telemetry_csv(history: List[Dict[str, Any]], filename: str = "outputs/vehicle_telemetry.csv") -> Path:
    """Save vehicle navigation telemetry to CSV."""
    out_path = Path(filename)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not history:
        return out_path

    fieldnames = list(history[0].keys())
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(history)

    return out_path
