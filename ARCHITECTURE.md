# TERA PULSE — Technical System Architecture Specification

**Project Title:** Adaptive Variable Resolution 2.5D LiDAR Mapping for Dynamic Environment Perception  
**Problem Statement:** SIH26053 (Smart India Hackathon 2026)  
**Target Domain:** Defence / DRDO Autonomous Ground Vehicles (UGVs)

---

## 1. System Overview

TERA PULSE addresses the fundamental trade-off in autonomous robotics: **Spatial Resolution vs. Real-Time Computational Efficiency**. By leveraging a foveated mapping principle, the system dynamically allocates high spatial fidelity to immediate tactical zones while preserving distant environmental context at reduced computational overhead.

```
+---------------------------------------------------------------------------------------------------+
|                                      TERA PULSE PIPELINE                                          |
+---------------------------------------------------------------------------------------------------+
|  1. Ingestion     -->  2. Preprocessing  -->  3. ML Segmentation  -->  4. Adaptive 2.5D Grid      |
|  (PCD/BIN/Streams)     (Filter/Voxel/SOR)     (Ground/Obstacle)        (Foveated Bands)           |
+---------------------------------------------------------------------------------------------------+
                                                                                     |
                                                                                     v
+---------------------------------------------------------------------------------------------------+
|  7. Visual Dashboard <--  6. Motion Control   <--  5. A* Path Planning  <-- Traversability Graph  |
|  (5-Panel Telemetry)   (Pure Pursuit / 10Hz)       (Multi-Res Graph)        (Slope & Clearance)   |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Module Specifications & Interfaces

### 2.1 Stage 1: LiDAR Point Cloud Preprocessing (`preprocessing/preprocess_lidar.py`)
- **Input:** Raw LiDAR frame (`.pcd`, `.bin`, `.ply` or synthetic array of size $N \times 3$).
- **Operations:**
  1. *Invalid Point Filtering:* Identifies and purges `NaN`, `Inf`, and zero-distance noise returns.
  2. *Cylindrical Range Gating:* Restricts point cloud to $R \in [0.5, 65.0]\,\text{m}$ to discard sensor self-occlusions and divergent far-field noise.
  3. *Elevation Slicing:* Restricts height $Z \in [-2.6, 3.5]\,\text{m}$ relative to sensor origin to filter overhanging tree canopies and sub-ground artifacts.
  4. *Voxel Downsampling:* Uniform 3D voxel grid filter with leaf size $r_{vox} = 0.15\,\text{m}$ reducing point density by $\approx 50\text{--}60\%$ without loss of obstacle geometry.
  5. *Statistical Outlier Removal (SOR):* Computes mean distance to $k=16$ nearest neighbors; prunes points deviating beyond $\mu + 1.8\sigma$.
- **Output:** Cleaned point cloud array ($M \times 3$) and intensity channels.

### 2.2 Stage 2: Semantic Segmentation (`ml/semantic_segmentation.py`)
- **Input:** Cleaned point cloud ($M \times 3$).
- **Classification Schema:**
  - `Class 0 (Ground):` Drivable flat surfaces, road planes, mild slope terrains.
  - `Class 1 (Static Obstacle):` Curbs, rocks, barriers, walls, tree trunks, non-drivable elevations.
  - `Class 2 (Dynamic Object):` Vehicles, moving targets, pedestrian-sized elevated clusters.
  - `Class 3 (Unknown):` Sparse/ambiguous returns.
- **Output:** Integer label vector $L \in \{0, 1, 2, 3\}^M$.

### 2.3 Stage 3: Adaptive Variable-Resolution 2.5D Grid Engine (`grid/adaptive_grid.py`)
- **Foveated Resolution Selection:**
  For each point $p_i = (x_i, y_i, z_i)$, calculate horizontal distance $d_{xy} = \sqrt{x_i^2 + y_i^2}$.
  
  $$\text{Resolution}(d_{xy}) = \begin{cases} 
  0.25\,\text{m}, & 0 \le d_{xy} < 10\,\text{m} \quad (\text{Near Band - Critical Hazard Zone}) \\ 
  0.75\,\text{m}, & 10 \le d_{xy} < 30\,\text{m} \quad (\text{Middle Band - Tactical Corridor}) \\ 
  2.00\,\text{m}, & 30 \le d_{xy} < 100\,\text{m} \quad (\text{Far Band - Regional Awareness}) 
  \end{cases}$$

- **Spatial Hashing & Aggregation:**
  Points are indexed into discrete spatial buckets using:
  $$i_x = \left\lfloor \frac{x_i}{\text{res}} \right\rfloor, \quad i_y = \left\lfloor \frac{y_i}{\text{res}} \right\rfloor$$
- **Cell Attributes Stored:**
  - Centroid Coordinates: $x_c = (i_x + 0.5) \cdot \text{res}$, $y_c = (i_y + 0.5) \cdot \text{res}$
  - Resolution: $\text{res} \in \{0.25, 0.75, 2.0\}$
  - Maximum Elevation: $Z_{max} = \max(\{z_k\})$
  - Mean Elevation: $Z_{mean} = \frac{1}{K}\sum_{k=1}^K z_k$
  - Dominant Semantic Class: $\arg\max_c (\text{count}(c))$
  - Point Count: $K$
- **Output:** List of `Cell` objects and comparison metrics vs. uniform grid.

### 2.4 Stage 4: Traversability Analysis & Graph Building (`navigation/path_planner.py`)
- **Traversability Logic:**
  A cell is deemed traversable if:
  1. Majority semantic class is `Ground`.
  2. Height difference $\Delta Z = Z_{max} - Z_{mean} \le 0.35\,\text{m}$.
  3. Cell is not classified as `Static Obstacle` or `Dynamic Object`.
- **Multi-Resolution Adjacency Graph:**
  Two cells $C_a$ and $C_b$ of resolutions $r_a, r_b$ are spatial neighbors if:
  $$|x_a - x_b| \le \frac{r_a + r_b}{2} + \epsilon, \quad |y_a - y_b| \le \frac{r_a + r_b}{2} + \epsilon \quad (\epsilon = 0.05\,\text{m})$$
- **A\* Path Planning:**
  - Heuristic: Euclidean distance $h(n) = \sqrt{(x_n - x_{goal})^2 + (y_n - y_{goal})^2}$.
  - Movement Cost: Center-to-center distance $g(n) = g(p) + d(p, n)$.
  - Connected Component Validation: Prior to search, breadth-first search (BFS) verifies reachability of goal from vehicle origin.
- **Output:** Ordered sequence of collision-free cells from Start to Goal.

### 2.5 Stage 5: Autonomous Motion Controller & Kinematics (`navigation/navigation_controller.py`)
- **Catmull-Rom Trajectory Smoothing:**
  Transforms discrete cell hops into continuous waypoints $W_k = (x_k, y_k, v_k^{target})$ with bounded curvature.
- **Bicycle Kinematic Model:**
  $$\dot{x} = v \cos(\theta), \quad \dot{y} = v \sin(\theta), \quad \dot{\theta} = \frac{v}{L} \tan(\delta)$$
  Where:
  - $L = 1.8\,\text{m}$ (Wheelbase)
  - $\delta$ = Front steering angle (bounded to $[-32^\circ, +32^\circ]$)
  - $v$ = Longitudinal velocity
- **Pure Pursuit Steering Law:**
  $$\kappa = \frac{2 \sin(\alpha)}{L_d}, \quad \delta = \arctan(L \cdot \kappa)$$
  Where $\alpha$ is the heading error to lookahead waypoint ($L_d = 1.5\,\text{m}$).
- **Dynamic Speed Profiling:**
  Automatically throttles speed down when encountering high-curvature turns or when approaching within $6.0\,\text{m}$ of the destination.
- **Output:** 10Hz telemetry log (`outputs/vehicle_telemetry.csv`).

### 2.6 Stage 6: Multi-Panel Visual Analytics (`navigation/navigation_dashboard.py`)
- Generates a 5-panel figure:
  1. Real 3D LiDAR point cloud colored by elevation.
  2. 2.5D Adaptive Grid showing traversable vs blocked cells.
  3. Spatial navigation map showing A* route, Start/Goal, and continuous vehicle trajectory.
  4. Longitudinal Velocity Profile $v(t)$ and Distance to Goal over mission time.
  5. Steering Angle $\delta(t)$ and Vehicle Heading $\theta(t)$ telemetry.

---

## 3. Data Flow & Contract Summary

| Source Module | Output Interface | Downstream Consumer |
| :--- | :--- | :--- |
| `preprocess_lidar.py` | `(points: np.ndarray [M, 3], intensity: np.ndarray [M])` | `semantic_segmentation.py` |
| `semantic_segmentation.py` | `(labels: np.ndarray [M])` | `adaptive_grid.py` |
| `adaptive_grid.py` | `(cells: List[Cell])` | `path_planner.py` |
| `path_planner.py` | `(path: List[Cell], start: Cell, goal: Cell)` | `navigation_controller.py` |
| `navigation_controller.py` | `(sim_result: Dict[str, Any], history: List[Dict])` | `navigation_dashboard.py` |
| `navigation_dashboard.py` | `outputs/navigation_dashboard.png` | Operator / Evaluator UI |

---

## 4. Hardware Deployment Blueprint (Edge Optimization)

For target deployment on tactical UGVs (e.g., DRDO Daksh, Wheeled/Tracked UGV platforms):
- **Target Edge Compute:** NVIDIA Jetson AGX Orin / Xavier.
- **Sensor Input:** 32/64/128-beam 3D LiDAR (Velodyne, Ouster, Hesai) via Ethernet (UDP packets).
- **Communication Framework:** ROS 2 (Humble / Iron) nodes communicating via zero-copy shared memory IPC.
- **Acceleration Pipeline:**
  - Voxelization & SOR $\rightarrow$ CUDA kernels.
  - Semantic Segmentation $\rightarrow$ TensorRT INT8 inference engine.
  - 2.5D Grid Hashing $\rightarrow$ GPU parallel spatial hash table.
  - Expected real-time throughput: $>25\,\text{Hz}$ full frame rate.
