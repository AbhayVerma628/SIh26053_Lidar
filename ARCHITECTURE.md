# TERA PULSE - System Architecture

## Pipeline
Raw LiDAR Point Cloud → Preprocessing → Semantic Segmentation → Terrain Analysis → Adaptive Variable-Resolution Grid → 2.5D Map Generation → Visualization

## Module Interfaces
* **Data Loading:** Input raw LiDAR file → Output point cloud
* **Preprocessing:** Input raw point cloud → Output cleaned point cloud
* **Semantic Segmentation:** Input processed point cloud → Output point cloud with semantic labels
* **Adaptive Grid:** Input point cloud + semantic labels → Output variable-resolution 2.5D grid
* **Visualization:** Input 2.5D adaptive map → Output visual representation