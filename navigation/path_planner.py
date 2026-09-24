"""
Navigation and A* Path Planning
TERA PULSE - SIH26053

Pipeline:
M4 Adaptive Cells
        ↓
Traversability
        ↓
Start / Goal
        ↓
A* Path Planning
"""

import heapq
import math


# ============================================================
# 1. TRAVERSABILITY
# ============================================================

SAFE_CLASSES = {
    "ground",
}

BLOCKED_CLASSES = {
    "static_obstacle",
    "dynamic_object",
    "unknown",
    "vehicle",
    "vegetation",
}


def is_traversable(cell):
    """Check whether an adaptive cell is traversable."""

    semantic_class = str(
        cell.semantic_class
    ).lower()

    return semantic_class in SAFE_CLASSES


def classify_cells(cells):
    """Separate cells into traversable and blocked."""

    traversable = []
    blocked = []

    for cell in cells:

        if is_traversable(cell):
            traversable.append(cell)

        else:
            blocked.append(cell)

    return traversable, blocked


def print_traversability_summary(
    traversable,
    blocked
):
    """Print navigation statistics."""

    total = (
        len(traversable)
        + len(blocked)
    )

    print(
        "\n===== TRAVERSABILITY SUMMARY ====="
    )

    print(
        f"Total cells: {total}"
    )

    print(
        f"Traversable cells: "
        f"{len(traversable)}"
    )

    print(
        f"Blocked cells: "
        f"{len(blocked)}"
    )

    if total > 0:

        percentage = (
            100.0
            * len(traversable)
            / total
        )

        print(
            f"Traversable area: "
            f"{percentage:.2f}%"
        )


def analyze_navigation_cells(cells):
    """Analyze adaptive cells for navigation."""

    traversable, blocked = (
        classify_cells(cells)
    )

    print_traversability_summary(
        traversable,
        blocked
    )

    return traversable, blocked


# ============================================================
# 2. START / GOAL
# ============================================================

def find_start_goal(cells):
    """
    Choose a start cell near the sensor origin,
    then choose the farthest reachable traversable
    cell from that start.

    This guarantees that start and goal belong
    to the same connected component.
    """

    traversable, _ = classify_cells(cells)

    if not traversable:
        raise ValueError(
            "No traversable cells available."
        )

    # --------------------------------------------------------
    # 1. Find candidate start cells
    # --------------------------------------------------------

    candidates = sorted(
        traversable,
        key=lambda cell:
            cell.x ** 2 + cell.y ** 2
    )

    start = None

    # Prefer a start cell that actually has neighbours.
    for candidate in candidates:

        neighbors = find_neighbors(
            candidate,
            traversable
        )

        if len(neighbors) > 0:
            start = candidate
            break

    if start is None:
        raise ValueError(
            "All traversable cells are isolated."
        )

    # --------------------------------------------------------
    # 2. Find all cells reachable from start
    # --------------------------------------------------------

    visited = {id(start)}

    queue = [start]

    reachable = [start]

    while queue:

        current = queue.pop(0)

        neighbors = find_neighbors(
            current,
            traversable
        )

        for neighbor in neighbors:

            neighbor_id = id(neighbor)

            if neighbor_id not in visited:

                visited.add(neighbor_id)

                queue.append(neighbor)

                reachable.append(neighbor)

    # --------------------------------------------------------
    # 3. Select farthest reachable cell as goal
    # --------------------------------------------------------

    goal = max(
        reachable,
        key=lambda cell:
            cell_distance(
                start,
                cell
            )
    )

    print(
        f"\nReachable cells from start: "
        f"{len(reachable)}"
    )

    return start, goal


# ============================================================
# 3. DISTANCE
# ============================================================

def cell_distance(a, b):
    """Euclidean distance between cell centers."""

    return math.sqrt(
        (a.x - b.x) ** 2
        + (a.y - b.y) ** 2
    )


# ============================================================
# 4. NEIGHBOURS
# ============================================================

def find_neighbors(
    cell,
    traversable,
    max_distance_factor=2.5
):
    """
    Find nearby traversable cells.

    Supports transitions between
    different adaptive resolutions.
    """

    neighbors = []

    for other in traversable:

        if other is cell:
            continue

        dx = abs(cell.x - other.x)
        dy = abs(cell.y - other.y)

        cell_size = float(cell.resolution)
        other_size = float(other.resolution)

        max_x = (cell_size + other_size) / 2
        max_y = (cell_size + other_size) / 2

        tolerance = 0.05

        if (
            dx <= max_x + tolerance
            and
            dy <= max_y + tolerance
        ):
            neighbors.append(other)

    return neighbors

def count_connections(cells):
    """
    Check how many neighbouring traversable cells
    each cell has.
    """

    traversable, _ = classify_cells(cells)

    isolated = 0
    total_connections = 0

    for cell in traversable:
        neighbors = find_neighbors(
            cell,
            traversable
        )

        total_connections += len(neighbors)

        if len(neighbors) == 0:
            isolated += 1

    print("\n===== GRAPH CONNECTIVITY =====")
    print(f"Traversable cells: {len(traversable)}")
    print(f"Total connections: {total_connections}")
    print(f"Isolated cells: {isolated}")

    return isolated

# ============================================================
# 5. HEURISTIC
# ============================================================

def heuristic(a, goal):
    """A* straight-line heuristic."""

    return cell_distance(
        a,
        goal
    )


# ============================================================
# 6. A* PATH PLANNER
# ============================================================

def a_star(
    start,
    goal,
    traversable,
    max_distance_factor=1.5
):
    """
    Perform A* search over traversable
    adaptive-grid cells.
    """

    open_heap = []

    counter = 0

    heapq.heappush(
        open_heap,
        (
            0.0,
            counter,
            start
        )
    )

    came_from = {}

    # IMPORTANT:
    # Cell objects are not hashable.
    # Therefore use id(cell) as dictionary key.
    g_score = {
        id(start): 0.0
    }

    f_score = {
        id(start):
        heuristic(
            start,
            goal
        )
    }

    visited = set()

    while open_heap:

        _, _, current = (
            heapq.heappop(
                open_heap
            )
        )

        current_id = id(current)

        if current_id in visited:
            continue

        visited.add(
            current_id
        )

        # Goal reached
        if current is goal:

            return reconstruct_path(
                came_from,
                current
            )

        neighbors = find_neighbors(
            current,
            traversable,
            max_distance_factor
        )

        for neighbor in neighbors:

            neighbor_id = id(
                neighbor
            )

            if neighbor_id in visited:
                continue

            movement_cost = (
                cell_distance(
                    current,
                    neighbor
                )
            )

            tentative_g = (
                g_score[current_id]
                + movement_cost
            )

            old_g = g_score.get(
                neighbor_id,
                float("inf")
            )

            if tentative_g < old_g:

                came_from[
                    neighbor_id
                ] = current

                g_score[
                    neighbor_id
                ] = tentative_g

                f_score[
                    neighbor_id
                ] = (
                    tentative_g
                    + heuristic(
                        neighbor,
                        goal
                    )
                )

                counter += 1

                heapq.heappush(
                    open_heap,
                    (
                        f_score[
                            neighbor_id
                        ],
                        counter,
                        neighbor
                    )
                )

    return None


# ============================================================
# 7. PATH RECONSTRUCTION
# ============================================================

def reconstruct_path(
    came_from,
    current
):
    """Reconstruct path from goal to start."""

    path = [current]

    while id(current) in came_from:

        current = came_from[
            id(current)
        ]

        path.append(
            current
        )

    path.reverse()

    return path


# ============================================================
# 8. PATH SUMMARY
# ============================================================

def print_path_summary(path):
    """Print final A* path information."""

    print(
        "\n===== A* PATH RESULT ====="
    )

    if path is None:

        print(
            "No valid path found."
        )

        return

    print(
        f"Path cells: {len(path)}"
    )

    total_distance = 0.0

    for i in range(
        len(path) - 1
    ):

        total_distance += (
            cell_distance(
                path[i],
                path[i + 1]
            )
        )

    print(
        f"Path distance: "
        f"{total_distance:.2f} m"
    )

    start = path[0]
    goal = path[-1]

    print(
        f"Start: "
        f"x={start.x:.2f}, "
        f"y={start.y:.2f}"
    )

    print(
        f"Goal: "
        f"x={goal.x:.2f}, "
        f"y={goal.y:.2f}"
    )
def save_path_csv(path, filename="outputs/planned_path.csv"):
    """Save A* path coordinates for visualization."""

    if path is None:
        print("No path to save.")
        return

    from pathlib import Path

    output_path = Path(filename)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "w") as f:
        f.write("x,y,resolution,semantic_class\n")

        for cell in path:
            f.write(
                f"{cell.x},"
                f"{cell.y},"
                f"{cell.resolution},"
                f"{cell.semantic_class}\n"
            )

    print(
        f"Path saved to: {output_path}"
    )

# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Navigation and A* module "
        "loaded successfully."
    )