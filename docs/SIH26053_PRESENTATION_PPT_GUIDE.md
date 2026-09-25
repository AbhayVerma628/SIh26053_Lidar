# Smart India Hackathon (SIH 2026) — Official Idea Presentation Guide

**Problem Statement ID:** SIH26053  
**Problem Statement Title:** Adaptive Variable Resolution 2.5D LiDAR Mapping for Dynamic Environment Perception  
**Domain:** Ministry of Defence / DRDO Domain  
**Category:** Software  
**Team Name:** TERA PULSE  

---

## 📋 Official Presentation Structure (15 Slides)

Follow this slide-by-slide structure directly in PowerPoint / Google Slides / Canva to export your **Idea Presentation PDF** for the SIH submission portal.

---

### Slide 1: Title Slide & Project Identity
- **Project Name:** TERA PULSE
- **Tagline:** Adaptive Variable-Resolution 2.5D LiDAR Perception & Autonomous Navigation Architecture
- **Problem Statement ID:** SIH26053
- **Theme / Ministry:** Defence / DRDO (Software Track)
- **Team Members & College Name:**
  - Team Leader & Integration Lead: [Your Name]
  - Member 1: ML & Semantic Understanding Lead
  - Member 2: LiDAR Preprocessing & Data Ingestion Lead
  - Member 3: Computer Vision & Visualization Lead
  - Member 4: Adaptive Grid & Spatial Engine Lead
  - Member 5: Autonomous Motion Planning & Kinematics Lead
- **Visuals:** Project logo / DRDO & SIH official logos.

---

### Slide 2: Problem Definition & Critical Bottlenecks
- **Context:** Autonomous Ground Vehicles (UGVs) and tactical defense robots operating in unmapped off-road terrains.
- **The Core Conflict:**
  1. *Massive Point Density:* Modern 3D LiDAR sensors stream $1.5\text{--}2.5$ million points per second. Processing this raw cloud at uniform ultra-fine scale saturates embedded bus bandwidth and exhausts GPU/CPU memory on edge compute.
  2. *The 2D Flaw:* Standard 2D occupancy grids discard the elevation axis entirely, failing to perceive negative obstacles (ditches, drop-offs), curbs, and low overhanging branches.
  3. *The 3D Flaw:* 3D voxel grids allocate memory uniformly to empty air and distant irrelevant background, driving latency above real-time thresholds ($>100\,\text{ms}$).
- **Key Takeaway:** Real-time autonomy demands high fidelity close to the vehicle and efficient representation far away.

---

### Slide 3: Comparison with Existing Approaches
| Feature | Traditional 2D Occupancy Grid | Standard Uniform 3D Voxel Grid | TERA PULSE Adaptive 2.5D Grid |
| :--- | :---: | :---: | :---: |
| **Elevation & Height Profile** | ❌ None (Flattened) | ✅ High | **✅ Preserved ($Z_{max}, Z_{mean}, \Delta Z$)** |
| **Computational Overhead** | Low | ❌ Extremely High | **⚡ Optimized ($<17\,\text{ms}$ latency)** |
| **Memory Footprint** | Low | ❌ Huge ($>100\,\text{MB}$ per scan) | **📉 Reduced by 66.2%** |
| **Terrain Roughness & Slope** | ❌ Blind | Moderate | **✅ Dedicated Terrain Features** |
| **Tactical Defense Viability** | Inadequate for Off-Road | Too slow for Edge Hardware | **🎯 Optimized for Embedded UGVs** |

---

### Slide 4: Proposed Solution & The Biomimetic Principle
- **Biomimetic "Foveated" Perception:**
  - Mirrors human vision: High acuity in central fovea (near vehicle), low acuity in peripheral vision (distant horizon).
- **Three Strategic Concentric Bands:**
  - **Near Band ($0\text{--}10\,\text{m}$ @ $0.25\,\text{m}$ resolution):** Critical obstacle clearance, negative obstacle detection, precision steering.
  - **Middle Band ($10\text{--}30\,\text{m}$ @ $0.75\,\text{m}$ resolution):** Corridor identification, curve anticipation, vehicle tracking.
  - **Far Band ($30\text{--}100\,\text{m}$ @ $2.00\,\text{m}$ resolution):** Regional boundary awareness, horizon anchoring, horizon trajectory guidance.
- **2.5D Elevation Layering:** Every cell stores centroid $(x, y)$, height bounds ($Z_{max}, Z_{mean}$), slope/roughness, and majority semantic classification.

---

### Slide 5: System Architecture & Workflow Pipeline
- **Mermaid Flowchart to include on slide:**
  `Raw LiDAR (.pcd/.bin) → Preprocessing (Filter/Voxel) → Semantic Segmentation → Adaptive 2.5D Grid → Traversability Analysis → A* Path Planning → Pure Pursuit Controller → Multi-Panel Dashboard`
- **Modular Data Contract:**
  - Standardized NumPy array and dataclass interfaces allow independent testing and zero regression during team integration.

---

### Slide 6: Point Cloud Ingestion & Preprocessing
- **Cleaning Stages:**
  - Invalid Point Elimination ($NaN$, $Inf$, zero-intensity dropouts).
  - Cylindrical Range Gating: $0.5\,\text{m} \le R \le 65.0\,\text{m}$.
  - Vertical Elevation Gating: $-2.6\,\text{m} \le Z \le 3.5\,\text{m}$.
  - Voxel Downsampling ($0.15\,\text{m}$ leaf) reducing raw 20,672 points to 9,132 points ($44.2\%$ retained) while maintaining sharp structural boundaries.
  - Statistical Outlier Removal (SOR, $k=16, 1.8\sigma$).
- **Visual:** Embed screenshot of raw point cloud vs preprocessed point cloud.

---

### Slide 7: Deep Semantic Segmentation & Terrain Analysis
- **Semantic Classification Categories:**
  - `Ground / Drivable Terrain (Class 0):` Flat surfaces, road, passable soil.
  - `Static Obstacle (Class 1):` Rocks, barriers, walls, tree trunks.
  - `Dynamic Object Candidate (Class 2):` Moving vehicles, pedestrians, soldiers.
  - `Unknown / Sparse (Class 3):` Distant or ambiguous returns.
- **Measured Distribution (on 20,672 Real LiDAR Points):**
  - Ground: 4,397 points | Static Obstacles: 3,268 points | Dynamic: 853 points | Unknown: 614 points.

---

### Slide 8: The Adaptive 2.5D Elevation Grid Engine
- **How Variable-Resolution Hashing Works:**
  - Fast spatial hashing using `floor(x / res)` and `floor(y / res)`.
  - Dynamically switches resolution based on Euclidean radius $r = \sqrt{x^2 + y^2}$.
- **Quantitative Grid Compression:**
  - Uniform $0.25\,\text{m}$ Grid: **2,888 occupied cells**
  - TERA PULSE Adaptive Grid: **976 occupied cells**
  - **Memory Reduction:** **66.2% fewer cell records**
  - **Mapping Latency:** Dropped from **23.82 ms** to **16.62 ms** (**30.2% faster**).

---

### Slide 9: 2D vs 2.5D vs 3D Spatial Comparison
- **Visual Slide:** Place top-down vector diagram (`outputs/adaptive_grid_top_down.svg`) alongside 3D elevation map.
- **Elevation Preservation:** Shows that unlike 2D maps where a $0.3\,\text{m}$ curb and a $3\,\text{m}$ wall look identical, our 2.5D elevation layer preserves height differentials:
  $$\Delta Z = Z_{max} - Z_{mean}$$
- **Slope & Roughness Calculation:** Directly feeds vehicle roll/pitch physical constraints into autonomous navigation.

---

### Slide 10: Quantitative Experimental Benchmarks
- Include a high-impact benchmark card:
  - **Input Scan:** 20,672 real Velodyne LiDAR points.
  - **Processing Throughput:** 8.13 seconds for total end-to-end mission pipeline (including I/O, segmentation, A*, kinematic simulation, and 180 DPI rendering).
  - **Grid Engine Throughput:** 16.6 ms per scan ($\approx 60\,\text{FPS}$ processing rate), far exceeding the 10–20 Hz LiDAR sensor frequency!
  - **Traversability Score:** 817 of 976 cells (83.71%) validated as safely drivable.

---

### Slide 11: Autonomous Navigation & Kinematic Motion Control
- **Addressing the Real Question: "How Does the UGV Actually Navigate?"**
  1. *Multi-Resolution A\* Search:* Finds the optimal sequence of 47 cells over a 28.92 m route.
  2. *Catmull-Rom Spline Smoothing:* Converts discrete orthogonal/diagonal cell hops into continuous waypoints.
  3. *Pure Pursuit Motion Controller:*
     - Simulates bicycle vehicle kinematics ($L=1.8\,\text{m}$, lookahead $L_d=1.5\,\text{m}$).
     - Dynamic steering angle $\delta(t) \in [-32^\circ, +32^\circ]$ and heading $\theta(t)$.
     - Intelligent deceleration: Throttles down on sharp turns and when approaching goal.
  4. *Mission Telemetry:* 13.8 seconds travel time, average operating speed $1.97\,\text{m/s}$ ($7.1\,\text{km/h}$), logged at 10Hz.

---

### Slide 12: Comprehensive 5-Panel System Dashboard
- **Visual Slide:** Embed `outputs/navigation_dashboard.png` prominently.
- **Highlight each of the 5 Panels:**
  - Panel 1: Real 3D LiDAR Point Cloud with elevation color spectrum.
  - Panel 2: 2.5D Adaptive Traversability Grid (Green = Drivable, Red = Blocked).
  - Panel 3: Autonomous Navigation Route (A* cell route + smoothed vehicle trajectory).
  - Panel 4: Vehicle Speed & Distance Profile ($v$ in km/h, distance to goal vs time).
  - Panel 5: Real-Time Dynamic Steering Angle & Heading Telemetry.

---

### Slide 13: Technical Novelty & Defence / Tactical Relevance
- **Direct Alignment with DRDO Mission Objectives:**
  - Operates reliably in GPS-denied environments (forward operating bases, dense foliage, urban canyons).
  - Handles dynamic terrain perception: differentiates moving threats from static landscape.
  - Extreme energy and compute efficiency: suitable for battery-operated reconnaissance UGVs.
- **Scalability:** Handles any LiDAR sensor geometry (16, 32, 64, or 128 beams, solid-state or mechanical).

---

### Slide 14: Project Development Status & Roadmap
- **COMPLETED (Proven Working Prototype):**
  - ✅ Ingestion of real LiDAR point clouds (`.pcd`, `.bin`).
  - ✅ Robust preprocessing, voxel downsampling, and SOR.
  - ✅ Multi-class semantic segmentation pipeline.
  - ✅ Foveated 2.5D variable-resolution grid engine with 66.2% compression.
  - ✅ A* navigation and Pure Pursuit kinematic vehicle controller.
  - ✅ Automated test suite passing with 100% success rate.
- **IN PROGRESS (Next 4–8 Weeks):**
  - 🔄 TensorRT acceleration for PointNet++ / Sparse CNN on NVIDIA Jetson.
  - 🔄 ROS 2 Humble node integration for real robot hardware.
- **FUTURE EXPANSION:**
  - 🔮 Multi-sensor fusion (Camera RGB + Thermal + Radar + LiDAR).
  - 🔮 SLAM loop closure over adaptive 2.5D submaps.

---

### Slide 15: Conclusion & Q&A Readiness
- **Core Value Proposition:** TERA PULSE solves the 3D perception bottleneck by combining human-like foveated mapping with 2.5D elevation awareness and autonomous kinematic control.
- **Open-Source GitHub Repository:** [AbhayVerma628/SIH26053-LiDAR](https://github.com/AbhayVerma628/SIH26053-LiDAR)
- **Thank You:** "We are now ready for your questions."
