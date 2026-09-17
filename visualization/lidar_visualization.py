import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# ============================================================
# 1. LOAD LiDAR POINT CLOUD
# ============================================================

file_path = "data/lidar/0001.pcd"

point_cloud = o3d.io.read_point_cloud(file_path)

points = np.asarray(point_cloud.points)

print("Total points:", len(points))


# ============================================================
# 2. HEIGHT INFORMATION
# ============================================================

z = points[:, 2]

z_min = z.min()
z_max = z.max()

print("Minimum height:", z_min)
print("Maximum height:", z_max)

# Normalize height between 0 and 1
normalized_z = (z - z_min) / (z_max - z_min)

# Give colors according to height
colors = np.zeros((len(points), 3))

colors[:, 0] = normalized_z
colors[:, 2] = 1 - normalized_z

point_cloud.colors = o3d.utility.Vector3dVector(colors)


# ============================================================
# 3. X AND Y COORDINATES
# ============================================================

x = points[:, 0]
y = points[:, 1]

print("X range:", x.min(), "to", x.max())
print("Y range:", y.min(), "to", y.max())


# ============================================================
# 4. CREATE BASIC TOP-DOWN VIEW
# ============================================================

plt.figure(figsize=(12, 7))

plt.scatter(
    x,
    y,
    s=0.5,
    c=normalized_z,
    cmap="turbo"
)

plt.xlabel("X (meters)")
plt.ylabel("Y (meters)")

plt.title("TERA PULSE - Top-Down LiDAR View")

plt.axis("equal")

plt.colorbar(label="Relative Height")


# ============================================================
# 5. ADAPTIVE GRID FUNCTIONS
# ============================================================

grid = {}


def required_resolution(x0, y0, size):

    # Four corners of the current cell
    corners = [
        (x0, y0),
        (x0 + size, y0),
        (x0, y0 + size),
        (x0 + size, y0 + size)
    ]

    # Distance of all corners from LiDAR origin
    distances = []

    for cx, cy in corners:

        distance = np.sqrt(cx**2 + cy**2)

        distances.append(distance)

    nearest = min(distances)
    farthest = max(distances)

    # Cell completely inside 0-10m region
    if farthest <= 10:
        return 0.5

    # Cell completely inside 10-30m region
    elif nearest >= 10 and farthest <= 30:
        return 1.0

    # Cell completely inside 30-50m region
    elif nearest >= 30 and farthest <= 50:
        return 2.0

    # Cell completely outside 50m
    elif nearest >= 50:
        return 4.0

    # Cell crosses a resolution boundary
    else:
        return None


def subdivide(x0, y0, size, indices):

    required_size = required_resolution(
        x0,
        y0,
        size
    )

    # Cell has reached its required resolution
    if required_size is not None and size <= required_size:

        height = max(
            points[i, 2]
            for i in indices
        )

        grid[(x0, y0, size)] = height

        return

    # Minimum resolution
    if size <= 0.5:

        height = max(
            points[i, 2]
            for i in indices
        )

        grid[(x0, y0, size)] = height

        return

    # Divide cell into 4 equal cells
    half = size / 2

    children = [
        (x0, y0),
        (x0 + half, y0),
        (x0, y0 + half),
        (x0 + half, y0 + half)
    ]

    for child_x, child_y in children:

        child_indices = []

        for i in indices:

            if (
                child_x <= x[i] < child_x + half
                and
                child_y <= y[i] < child_y + half
            ):

                child_indices.append(i)

        if child_indices:

            subdivide(
                child_x,
                child_y,
                half,
                child_indices
            )


# ============================================================
# 6. CREATE BASE GRID
# ============================================================

base_size = 4.0

base_cells = {}

for i in range(len(points)):

    cell_x = np.floor(x[i] / base_size) * base_size
    cell_y = np.floor(y[i] / base_size) * base_size

    cell = (cell_x, cell_y)

    if cell not in base_cells:

        base_cells[cell] = []

    base_cells[cell].append(i)


# ============================================================
# 7. BUILD ADAPTIVE GRID
# ============================================================

for (x0, y0), indices in base_cells.items():

    subdivide(
        x0,
        y0,
        base_size,
        indices
    )


adaptive_cells = len(grid)

print("Adaptive occupied cells:", adaptive_cells)


# ============================================================
# 8. DRAW ADAPTIVE GRID
# ============================================================

for (x0, y0, size), height in grid.items():

    rectangle = Rectangle(
        (x0, y0),
        size,
        size,
        fill=False,
        linewidth=0.35
    )

    plt.gca().add_patch(rectangle)


plt.show()


# ============================================================
# 9. UNIFORM 0.5m GRID
# ============================================================

uniform_grid = set()

uniform_size = 0.5

for i in range(len(points)):

    cell_x = np.floor(x[i] / uniform_size)
    cell_y = np.floor(y[i] / uniform_size)

    uniform_grid.add(
        (cell_x, cell_y)
    )


uniform_cells = len(uniform_grid)

print("Uniform 0.5m cells:", uniform_cells)


# ============================================================
# 10. CELL REDUCTION
# ============================================================

reduction = (
    1 -
    adaptive_cells / uniform_cells
) * 100


print(
    "Adaptive cells:",
    adaptive_cells
)

print(
    "Cell reduction:",
    round(reduction, 2),
    "%"
)


# ============================================================
# 11. UNIFORM VS ADAPTIVE COMPARISON
# ============================================================

fig, axes = plt.subplots(
    1,
    2,
    figsize=(16, 7)
)


# ------------------------------------------------------------
# LEFT: UNIFORM GRID
# ------------------------------------------------------------

axes[0].scatter(
    x,
    y,
    s=0.5,
    c=normalized_z,
    cmap="turbo"
)


for cell_x, cell_y in uniform_grid:

    rectangle = Rectangle(
        (
            cell_x * uniform_size,
            cell_y * uniform_size
        ),
        uniform_size,
        uniform_size,
        fill=False,
        linewidth=0.15
    )

    axes[0].add_patch(rectangle)


axes[0].set_title(
    f"Uniform 0.5m Grid\n"
    f"{uniform_cells} occupied cells"
)

axes[0].set_xlabel("X (meters)")
axes[0].set_ylabel("Y (meters)")

axes[0].axis("equal")


# ------------------------------------------------------------
# RIGHT: ADAPTIVE GRID
# ------------------------------------------------------------

axes[1].scatter(
    x,
    y,
    s=0.5,
    c=normalized_z,
    cmap="turbo"
)


for (x0, y0, size), height in grid.items():

    rectangle = Rectangle(
        (x0, y0),
        size,
        size,
        fill=False,
        linewidth=0.35
    )

    axes[1].add_patch(rectangle)


axes[1].set_title(
    f"Adaptive Grid\n"
    f"{adaptive_cells} occupied cells"
)

axes[1].set_xlabel("X (meters)")
axes[1].set_ylabel("Y (meters)")

axes[1].axis("equal")


# ------------------------------------------------------------
# FINAL TITLE
# ------------------------------------------------------------

plt.suptitle(
    "TERA PULSE - Uniform vs Adaptive 2.5D Mapping\n"
    f"Cell Reduction: {reduction:.2f}%"
)

plt.tight_layout()

plt.show()


# ============================================================
# 12. 3D LiDAR VISUALIZATION
# ============================================================

o3d.visualization.draw_geometries(
    [point_cloud],
    window_name="TERA PULSE - Height Colored LiDAR",
    width=1200,
    height=800
)