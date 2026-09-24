from pathlib import Path
import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


ROOT = Path(__file__).resolve().parent.parent
path_file = ROOT / "outputs" / "planned_path.csv"


# ============================================================
# LOAD A* PATH
# ============================================================

path = []

with open(path_file, "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        path.append({
            "x": float(row["x"]),
            "y": float(row["y"]),
            "resolution": float(row["resolution"]),
            "semantic_class": row["semantic_class"]
        })


if not path:
    raise ValueError("No planned path found.")


# ============================================================
# PATH COORDINATES
# ============================================================

path_x = [p["x"] for p in path]
path_y = [p["y"] for p in path]


# ============================================================
# FIGURE
# ============================================================

fig, ax = plt.subplots(figsize=(13, 9))


# ============================================================
# DRAW ADAPTIVE PATH CELLS
# ============================================================

for p in path:

    x = p["x"]
    y = p["y"]
    size = p["resolution"]

    rect = Rectangle(
        (x - size / 2, y - size / 2),
        size,
        size,
        fill=False,
        linewidth=0.8,
        alpha=0.45
    )

    ax.add_patch(rect)


# ============================================================
# DRAW A* PATH
# ============================================================

ax.plot(
    path_x,
    path_y,
    linewidth=4,
    label="A* Planned Path",
    zorder=5
)


# ============================================================
# START
# ============================================================

ax.scatter(
    path_x[0],
    path_y[0],
    s=180,
    marker="o",
    edgecolors="black",
    linewidths=1.5,
    label="START",
    zorder=10
)


# ============================================================
# GOAL
# ============================================================

ax.scatter(
    path_x[-1],
    path_y[-1],
    s=250,
    marker="*",
    edgecolors="black",
    linewidths=1.5,
    label="GOAL",
    zorder=10
)


# ============================================================
# LABELS
# ============================================================

ax.annotate(
    "START",
    (path_x[0], path_y[0]),
    xytext=(10, 10),
    textcoords="offset points",
    fontsize=11,
    fontweight="bold"
)

ax.annotate(
    "GOAL",
    (path_x[-1], path_y[-1]),
    xytext=(10, 10),
    textcoords="offset points",
    fontsize=11,
    fontweight="bold"
)


# ============================================================
# INFORMATION BOX
# ============================================================

info = (
    f"Path cells: {len(path)}\n"
    f"Start: ({path_x[0]:.2f}, {path_y[0]:.2f})\n"
    f"Goal: ({path_x[-1]:.2f}, {path_y[-1]:.2f})"
)

ax.text(
    0.02,
    0.98,
    info,
    transform=ax.transAxes,
    verticalalignment="top",
    bbox=dict(
        boxstyle="round",
        facecolor="white",
        alpha=0.85
    )
)


# ============================================================
# FINAL STYLE
# ============================================================

ax.set_title(
    "TERA PULSE - Adaptive Grid A* Navigation",
    fontsize=17,
    fontweight="bold"
)

ax.set_xlabel("X (meters)")
ax.set_ylabel("Y (meters)")

ax.grid(True, alpha=0.3)

ax.axis("equal")

ax.legend()

plt.tight_layout()

plt.show()
