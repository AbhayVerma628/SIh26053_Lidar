"""
TERA PULSE - Final Navigation & Autonomous Perception Dashboard
SIH26053: Adaptive Variable Resolution 2.5D LiDAR Mapping

Comprehensive visualization layer combining:
1. Real LiDAR Point Cloud with Elevation Spectrum
2. 2.5D Adaptive Variable-Resolution Grid & Traversability Analysis
3. Autonomous Navigation: A* Safe Path & Continuous Vehicle Trajectory
4. Vehicle Dynamic Telemetry: Velocity Profile v(t) & Steering Angle delta(t)
"""

from pathlib import Path
import sys
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
import open3d as o3d

# Add repo root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.semantic_segmentation import semantic_segmentation
from adaptive_grid import points_from_arrays, adaptive_grid
from navigation.path_planner import (
    analyze_navigation_cells,
    find_start_goal,
    a_star,
    print_path_summary,
    save_path_csv,
)
from navigation.navigation_controller import (
    simulate_vehicle_navigation,
    save_telemetry_csv,
)

DATA_FILE = ROOT / "data" / "lidar" / "0001.pcd"
DASHBOARD_OUTPUT = ROOT / "outputs" / "navigation_dashboard.png"


def load_lidar(path: Path):
    print("\n===== TERA PULSE NAVIGATION DASHBOARD =====")
    print("\n[1] REAL LiDAR")
    if not path.exists():
        raise FileNotFoundError(f"LiDAR file not found: {path}")

    cloud = o3d.io.read_point_cloud(str(path))
    points = np.asarray(cloud.points)
    print(f"File: {path}")
    print(f"LiDAR points: {len(points)}")

    if len(points) == 0:
        raise ValueError("No LiDAR points were loaded.")
    return cloud, points


def run_segmentation(points: np.ndarray):
    print("\n[2] SEMANTIC SEGMENTATION")
    labels = semantic_segmentation(points)
    print(f"Labels: {labels.shape}")

    unique, counts = np.unique(labels, return_counts=True)
    for label, count in zip(unique, counts):
        class_name = {0: "Ground", 1: "Static Obstacle", 2: "Dynamic Object", 3: "Unknown"}.get(label, "Other")
        print(f"  Class {label} ({class_name}): {count}")
    return labels


def build_navigation(points: np.ndarray, labels: np.ndarray):
    print("\n[3] M4 ADAPTIVE GRID")
    m4_points = points_from_arrays(points, labels)
    cells = adaptive_grid(m4_points)
    print(f"Adaptive cells: {len(cells)}")

    print("\n[4] NAVIGATION TRAVERSABILITY")
    traversable, blocked = analyze_navigation_cells(cells)

    print("\n[5] START / GOAL")
    start, goal = find_start_goal(cells)
    print(f"Start: x={start.x:.2f}, y={start.y:.2f}, res={start.resolution:.2f}m")
    print(f"Goal:  x={goal.x:.2f}, y={goal.y:.2f}, res={goal.resolution:.2f}m")

    print("\n[6] A* PATH PLANNING")
    path = a_star(start, goal, traversable)
    print_path_summary(path)
    save_path_csv(path, str(ROOT / "outputs" / "planned_path.csv"))

    print("\n[7] AUTONOMOUS MOTION SIMULATION")
    sim_result = simulate_vehicle_navigation(path)
    save_telemetry_csv(sim_result["history"], str(ROOT / "outputs" / "vehicle_telemetry.csv"))
    print(f"Simulation completed: {sim_result['total_time_sec']}s, {sim_result['total_distance_m']}m, {sim_result['telemetry_samples']} steps")

    return cells, traversable, blocked, start, goal, path, sim_result


def style_axis(ax, title: str):
    ax.set_title(title, fontsize=14, fontweight="bold", pad=10)
    ax.set_xlabel("X (meters)", fontsize=10)
    ax.set_ylabel("Y (meters)", fontsize=10)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def create_dashboard(
    points: np.ndarray,
    cells: list,
    traversable: list,
    blocked: list,
    start: any,
    goal: any,
    path: list,
    sim_result: dict,
    show_plot: bool = False,
):
    print("\n[8] GENERATING MULTI-PANEL NAVIGATION DASHBOARD")

    # Set up figure with 2 rows: Top 3 spatial panels, Bottom 2 telemetry graphs
    fig = plt.figure(figsize=(22, 12))
    gs = fig.add_gridspec(2, 6, height_ratios=[1.8, 1.0], hspace=0.32, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, 0:2])
    ax2 = fig.add_subplot(gs[0, 2:4])
    ax3 = fig.add_subplot(gs[0, 4:6])
    ax4 = fig.add_subplot(gs[1, 0:3])
    ax5 = fig.add_subplot(gs[1, 3:6])

    # --------------------------------------------------------
    # PANEL 1 — REAL LiDAR
    # --------------------------------------------------------
    scatter = ax1.scatter(
        points[:, 0],
        points[:, 1],
        c=points[:, 2],
        s=2.5,
        cmap="viridis",
        alpha=0.85,
        linewidths=0,
    )
    cbar = fig.colorbar(scatter, ax=ax1, fraction=0.046, pad=0.03)
    cbar.set_label("Elevation Z (m)", fontsize=9)
    style_axis(ax1, "1. Real 3D LiDAR Point Cloud")

    ax1.text(
        0.03,
        0.97,
        f"Points: {len(points):,}\nSensor: Velodyne HDL-64\nRange: ~60 m",
        transform=ax1.transAxes,
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.92),
    )

    # --------------------------------------------------------
    # PANEL 2 — ADAPTIVE 2.5D GRID & TRAVERSABILITY
    # --------------------------------------------------------
    for cell in blocked:
        rect = Rectangle(
            (cell.x - cell.resolution / 2, cell.y - cell.resolution / 2),
            cell.resolution,
            cell.resolution,
            facecolor=(0.88, 0.28, 0.28),
            edgecolor="darkred",
            linewidth=0.4,
            alpha=0.75,
        )
        ax2.add_patch(rect)

    for cell in traversable:
        rect = Rectangle(
            (cell.x - cell.resolution / 2, cell.y - cell.resolution / 2),
            cell.resolution,
            cell.resolution,
            facecolor=(0.30, 0.75, 0.45),
            edgecolor="darkgreen",
            linewidth=0.25,
            alpha=0.55,
        )
        ax2.add_patch(rect)

    style_axis(ax2, "2. Adaptive 2.5D Traversability Grid")
    trav_pct = 100.0 * len(traversable) / max(1, len(cells))
    ax2.text(
        0.03,
        0.97,
        (
            f"Adaptive Cells: {len(cells):,}\n"
            f"Traversable: {len(traversable):,} ({trav_pct:.1f}%)\n"
            f"Blocked (Obstacles): {len(blocked):,}\n"
            f"Foveated Bands: 0.25m / 0.75m / 2.0m"
        ),
        transform=ax2.transAxes,
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.92),
    )

    legend_elements_p2 = [
        Patch(facecolor=(0.30, 0.75, 0.45), edgecolor="darkgreen", label="Traversable (Drivable)"),
        Patch(facecolor=(0.88, 0.28, 0.28), edgecolor="darkred", label="Blocked (Obstacle/Rough)"),
    ]
    ax2.legend(handles=legend_elements_p2, loc="lower right", framealpha=0.92, fontsize=8.5)

    # --------------------------------------------------------
    # PANEL 3 — AUTONOMOUS NAVIGATION (A* PATH + SMOOTH TRAJECTORY)
    # --------------------------------------------------------
    for cell in blocked:
        rect = Rectangle(
            (cell.x - cell.resolution / 2, cell.y - cell.resolution / 2),
            cell.resolution,
            cell.resolution,
            facecolor=(0.88, 0.28, 0.28),
            edgecolor="none",
            alpha=0.30,
        )
        ax3.add_patch(rect)

    for cell in traversable:
        rect = Rectangle(
            (cell.x - cell.resolution / 2, cell.y - cell.resolution / 2),
            cell.resolution,
            cell.resolution,
            facecolor=(0.30, 0.70, 0.40),
            edgecolor="none",
            alpha=0.18,
        )
        ax3.add_patch(rect)

    path_distance = 0.0
    if path:
        path_x = [cell.x for cell in path]
        path_y = [cell.y for cell in path]
        for i in range(len(path) - 1):
            path_distance += float(np.hypot(path[i + 1].x - path[i].x, path[i + 1].y - path[i].y))

        # A* cell center links
        ax3.plot(
            path_x,
            path_y,
            linewidth=1.8,
            linestyle="--",
            color="orange",
            marker="o",
            markersize=3.0,
            label="A* Grid Route",
            zorder=6,
        )

    # Continuous smooth vehicle trajectory from simulator
    history = sim_result.get("history", [])
    if history:
        traj_x = [h["x"] for h in history]
        traj_y = [h["y"] for h in history]
        ax3.plot(
            traj_x,
            traj_y,
            linewidth=3.2,
            color="#0284c7",
            label="Vehicle Trajectory (Pure Pursuit)",
            zorder=7,
        )

    ax3.scatter(start.x, start.y, s=200, color="blue", marker="o", label="START", zorder=10)
    ax3.scatter(goal.x, goal.y, s=260, color="crimson", marker="*", label="GOAL", zorder=10)

    ax3.annotate("START", (start.x, start.y), xytext=(8, 8), textcoords="offset points", fontsize=9.5, fontweight="bold", zorder=11)
    ax3.annotate("GOAL", (goal.x, goal.y), xytext=(8, 8), textcoords="offset points", fontsize=9.5, fontweight="bold", zorder=11)

    style_axis(ax3, "3. Autonomous Navigation & Trajectory")
    ax3.legend(loc="upper right", framealpha=0.92, fontsize=8.5)

    ax3.text(
        0.03,
        0.97,
        (
            f"Path Cells: {len(path)}\n"
            f"Route Distance: {path_distance:.2f} m\n"
            f"Travel Time: {sim_result.get('total_time_sec', 0)} s\n"
            f"Kinematics: Ackermann / Pure Pursuit"
        ),
        transform=ax3.transAxes,
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.92),
    )

    # Common spatial limits for Panels 1, 2, 3
    x_all = points[:, 0]
    y_all = points[:, 1]
    margin = 2.5
    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(np.min(x_all) - margin, np.max(x_all) + margin)
        ax.set_ylim(np.min(y_all) - margin, np.max(y_all) + margin)

    # --------------------------------------------------------
    # PANEL 4 — TELEMETRY: VELOCITY PROFILE v(t)
    # --------------------------------------------------------
    if history:
        t_vals = [h["time_sec"] for h in history]
        v_mps = [h["velocity_mps"] for h in history]
        v_kmh = [h["velocity_kmh"] for h in history]
        dist_goal = [h["dist_to_goal_m"] for h in history]

        color_v = "#0284c7"
        ax4.plot(t_vals, v_kmh, linewidth=2.5, color=color_v, label="Speed (km/h)")
        ax4.set_title("4. Vehicle Speed & Distance Profile", fontsize=12, fontweight="bold", pad=8)
        ax4.set_xlabel("Time (seconds)", fontsize=10)
        ax4.set_ylabel("Speed (km/h)", color=color_v, fontsize=10)
        ax4.tick_params(axis="y", labelcolor=color_v)
        ax4.grid(True, linestyle="--", alpha=0.3)

        ax4_dist = ax4.twinx()
        color_d = "#e11d48"
        ax4_dist.plot(t_vals, dist_goal, linewidth=2.0, linestyle=":", color=color_d, label="Dist to Goal (m)")
        ax4_dist.set_ylabel("Distance to Goal (m)", color=color_d, fontsize=10)
        ax4_dist.tick_params(axis="y", labelcolor=color_d)

        lines_4 = [
            Line2D([0], [0], color=color_v, lw=2.5, label="Velocity (km/h)"),
            Line2D([0], [0], color=color_d, lw=2.0, ls=":", label="Distance to Goal (m)"),
        ]
        ax4.legend(handles=lines_4, loc="upper right", framealpha=0.9, fontsize=8.5)

    # --------------------------------------------------------
    # PANEL 5 — TELEMETRY: STEERING ANGLE delta(t) & HEADING
    # --------------------------------------------------------
    if history:
        steer_vals = [h["steering_deg"] for h in history]
        heading_vals = [h["heading_deg"] for h in history]

        color_steer = "#7c3aed"
        ax5.plot(t_vals, steer_vals, linewidth=2.5, color=color_steer, label="Steering Angle δ (deg)")
        ax5.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        ax5.set_title("5. Dynamic Steering Angle & Heading", fontsize=12, fontweight="bold", pad=8)
        ax5.set_xlabel("Time (seconds)", fontsize=10)
        ax5.set_ylabel("Steering Angle (deg)", color=color_steer, fontsize=10)
        ax5.tick_params(axis="y", labelcolor=color_steer)
        ax5.grid(True, linestyle="--", alpha=0.3)

        ax5_head = ax5.twinx()
        color_head = "#059669"
        ax5_head.plot(t_vals, heading_vals, linewidth=2.0, linestyle="-.", color=color_head, label="Heading θ (deg)")
        ax5_head.set_ylabel("Vehicle Heading (deg)", color=color_head, fontsize=10)
        ax5_head.tick_params(axis="y", labelcolor=color_head)

        lines_5 = [
            Line2D([0], [0], color=color_steer, lw=2.5, label="Steering Angle δ (deg)"),
            Line2D([0], [0], color=color_head, lw=2.0, ls="-.", label="Heading θ (deg)"),
        ]
        ax5.legend(handles=lines_5, loc="lower right", framealpha=0.9, fontsize=8.5)

    # Global Title and Branding
    fig.suptitle(
        "TERA PULSE — SIH26053 Autonomous Navigation System\nAdaptive Variable-Resolution 2.5D LiDAR Mapping & Dynamic Control",
        fontsize=18,
        fontweight="bold",
        y=0.985,
    )

    DASHBOARD_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(DASHBOARD_OUTPUT, dpi=180, bbox_inches="tight")
    print(f"[OK] Dashboard successfully saved to: {DASHBOARD_OUTPUT}")

    if show_plot:
        plt.show()
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="TERA PULSE Navigation Dashboard")
    parser.add_argument("--input", type=str, default=str(DATA_FILE), help="Path to input LiDAR .pcd file")
    parser.add_argument("--show", action="store_true", help="Display interactive window")
    parser.add_argument("--save-only", action="store_true", default=True, help="Save dashboard image without blocking")
    args = parser.parse_args()

    input_path = Path(args.input)
    _, points = load_lidar(input_path)
    labels = run_segmentation(points)
    cells, traversable, blocked, start, goal, path, sim_result = build_navigation(points, labels)

    show_plot = args.show and not args.save_only
    create_dashboard(points, cells, traversable, blocked, start, goal, path, sim_result, show_plot=show_plot)


if __name__ == "__main__":
    main()
