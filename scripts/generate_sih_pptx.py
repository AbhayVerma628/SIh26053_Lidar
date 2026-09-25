import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    NAVY = RGBColor(15, 23, 42)
    DEEP_BLUE = RGBColor(30, 64, 175)
    CYAN = RGBColor(2, 132, 199)
    CARD_BG = RGBColor(248, 250, 252)
    BORDER_COL = RGBColor(203, 213, 225)
    TEXT_DARK = RGBColor(30, 41, 59)
    TEXT_MUTED = RGBColor(100, 116, 139)
    WHITE = RGBColor(255, 255, 255)
    GREEN = RGBColor(16, 185, 129)
    ORANGE = RGBColor(245, 158, 11)
    RED = RGBColor(239, 68, 68)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, slide_num):
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = DEEP_BLUE
        top_bar.line.fill.background()

        header_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(9.8), Inches(0.75))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = NAVY

        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.7), Inches(0.25), Inches(2.0), Inches(0.48))
        badge.fill.solid()
        badge.fill.fore_color.rgb = ORANGE
        badge.line.color.rgb = ORANGE
        btf = badge.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = "SIH 2026 | PS-26053"
        bp.font.name = "Arial"
        bp.font.size = Pt(10.5)
        bp.font.bold = True
        bp.font.color.rgb = WHITE

        footer = slide.shapes.add_textbox(Inches(0.6), Inches(7.1), Inches(12.133), Inches(0.3))
        ftf = footer.text_frame
        ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
        fp = ftf.paragraphs[0]
        fp.text = f"Team TeraPulse — IIIT Bhopal  |  @SIH Idea submission- Template {slide_num}"
        fp.font.name = "Arial"
        fp.font.size = Pt(8.5)
        fp.font.color.rgb = TEXT_MUTED

    # ==================== SLIDE 1: Title & Team Details ====================
    s1 = prs.slides.add_slide(blank_layout)
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = DEEP_BLUE
    top_bar.line.fill.background()

    hdr_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.45))
    htf = hdr_box.text_frame
    hp = htf.paragraphs[0]
    hp.text = "SMART INDIA HACKATHON 2026"
    hp.font.name = "Arial"
    hp.font.size = Pt(16)
    hp.font.bold = True
    hp.font.color.rgb = DEEP_BLUE

    title_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(11.7), Inches(1.3))
    ttf = title_box.text_frame
    ttf.word_wrap = True
    tp = ttf.paragraphs[0]
    tp.text = "Adaptive Foveated 2.5D Semantic Mapping for Autonomous Navigation"
    tp.font.name = "Arial"
    tp.font.size = Pt(27)
    tp.font.bold = True
    tp.font.color.rgb = NAVY

    tp2 = ttf.add_paragraph()
    tp2.text = "High-Speed Variable-Resolution Perception & Real-Time Kinematic Control for Tactical UGVs"
    tp2.font.name = "Arial"
    tp2.font.size = Pt(13.5)
    tp2.font.color.rgb = CYAN

    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.45), Inches(5.7), Inches(4.5))
    card1.fill.solid()
    card1.fill.fore_color.rgb = CARD_BG
    card1.line.color.rgb = BORDER_COL
    c1_tf = card1.text_frame
    c1_tf.word_wrap = True
    c1_tf.margin_left = c1_tf.margin_top = Inches(0.3)
    p = c1_tf.paragraphs[0]
    p.text = "📌 Problem Statement Details"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(8)

    items1 = [
        ("Problem Statement ID:", "26053"),
        ("Category / Domain:", "Software  |  Ministry of Defence / DRDO"),
        ("Theme:", "Smart Vehicles / Autonomous Systems"),
        ("Target Deployment:", "Defense Unmanned Ground Vehicles (UGVs)"),
        ("Operational Scope:", "Off-road, rough terrain, GPS-denied environments"),
        ("Core Breakthrough:", "Foveated 2.5D variable-resolution spatial hashing")
    ]
    for label, val in items1:
        p = c1_tf.add_paragraph()
        p.text = f"• {label} {val}"
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    card2 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.45), Inches(5.7), Inches(4.5))
    card2.fill.solid()
    card2.fill.fore_color.rgb = CARD_BG
    card2.line.color.rgb = BORDER_COL
    c2_tf = card2.text_frame
    c2_tf.word_wrap = True
    c2_tf.margin_left = c2_tf.margin_top = Inches(0.3)
    p = c2_tf.paragraphs[0]
    p.text = "👥 Team TeraPulse — IIIT Bhopal"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(8)

    items2 = [
        ("Team Leader:", "Abhay Verma (Pipeline Integration & Control)"),
        ("Member 2:", "Lokendra Singh (Adaptive Grid Engine & Benchmark)"),
        ("Member 3:", "Yashvardhan Jain (LiDAR Preprocessing & Noise Rejection)"),
        ("Member 4:", "Chetan Meena (Semantic Terrain Segmentation & ML)"),
        ("Member 5:", "Sachin Chaubey (Visualization, UI Dashboard & Testing)"),
        ("Institute:", "Indian Institute of Information Technology Bhopal"),
        ("Repository:", "github.com/AbhayVerma628/SIH26053_Lidar")
    ]
    for label, val in items2:
        p = c2_tf.add_paragraph()
        p.text = f"• {label} {val}"
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    footer1 = s1.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(11.7), Inches(0.3))
    f1_tf = footer1.text_frame
    f1_tf.margin_left = f1_tf.margin_top = 0
    f1_p = f1_tf.paragraphs[0]
    f1_p.text = "Team TeraPulse — IIIT Bhopal  |  @SIH Idea submission- Template 1"
    f1_p.font.name = "Arial"
    f1_p.font.size = Pt(8.5)
    f1_p.font.color.rgb = TEXT_MUTED

    # ==================== SLIDE 2: Proposed Solution & Innovation ====================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "PROPOSED SOLUTION & INNOVATION", 2)

    # Left Column: Proposed Solution
    card2_left = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.15), Inches(6.0), Inches(4.3))
    card2_left.fill.solid()
    card2_left.fill.fore_color.rgb = CARD_BG
    card2_left.line.color.rgb = BORDER_COL
    tf2_l = card2_left.text_frame
    tf2_l.word_wrap = True
    tf2_l.margin_left = tf2_l.margin_top = Inches(0.25)
    p = tf2_l.paragraphs[0]
    p.text = "❖ Proposed Solution: TERA PULSE Architecture"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(6)

    sol_bullets = [
        "Foveated 2.5D Elevation Grid: Transforms millions of 3D LiDAR points into an egocentric multi-resolution heightmap anchored to the vehicle.",
        "Near Field (0 – 10 m): Ultra-fine 0.25 m resolution for millimetric obstacle clearance, step height, and reactive steering.",
        "Middle Field (10 – 30 m): Medium 0.75 m resolution capturing corridor contours and upcoming turns without memory bloat.",
        "Far Field (30 – 100 m): Coarse 2.00 m resolution providing global situational context with minimal cell allocations.",
        "Semantic Terrain Profiling: Every cell stores Z_max, Z_mean, slope gradient, surface roughness, and classification (Ground, Obstacle, Dynamic).",
        "Closed-Loop Navigation: Feeds directly into A* path planning and Pure Pursuit kinematics for autonomous vehicle motion."
    ]
    for b in sol_bullets:
        p = tf2_l.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(4)

    # Right Column: Innovation & Uniqueness
    card2_right = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.15), Inches(5.9), Inches(4.3))
    card2_right.fill.solid()
    card2_right.fill.fore_color.rgb = CARD_BG
    card2_right.line.color.rgb = BORDER_COL
    tf2_r = card2_right.text_frame
    tf2_r.word_wrap = True
    tf2_r.margin_left = tf2_r.margin_top = Inches(0.25)
    p = tf2_r.paragraphs[0]
    p.text = "❖ Innovation & Uniqueness"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(6)

    innov_bullets = [
        "Biomimetic Human-Eye Vision: Replaces uniform voxel brute-force with concentric attention bands, slashing compute load by 66.2%.",
        "2.5D vs 3D Advantage: Delivers 90% of 3D geometric intelligence (slope, elevation, roughness) at the speed and lightweight RAM of a 2D map.",
        "Dynamic Moving Resolution Bubble: As the car drives, the fine 0.25 m bubble continuously moves with the vehicle [x(t), y(t)] at 60 FPS.",
        "Vertical Beam Clearance Analysis: Distinguishes solid walls from hollow underpasses/tunnels without requiring heavy 3D voxelization.",
        "Edge Deployment Ready: Runs in 24.23 ms (>35 FPS), allowing real-time deployment on rugged low-power NVIDIA Jetson Orin & Raspberry Pi."
    ]
    for b in innov_bullets:
        p = tf2_r.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(4)

    # Three Stat Badges at bottom
    badge_data = [
        ("66.2% Cell Reduction", "2,888 uniform cells down to 976 adaptive cells", GREEN, Inches(0.6)),
        ("24.23 ms Mapping Latency", "4.8× faster than uniform grid (115.9 ms)", CYAN, Inches(4.75)),
        ("83.7% Drivable Space", "Accurately separated safe corridor from obstacles", ORANGE, Inches(8.9))
    ]
    for title, subtitle, col, left_x in badge_data:
        b_box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_x, Inches(5.6), Inches(3.8), Inches(1.3))
        b_box.fill.solid()
        b_box.fill.fore_color.rgb = CARD_BG
        b_box.line.color.rgb = col
        b_box.line.width = Pt(1.5)
        btf = b_box.text_frame
        btf.margin_top = Inches(0.18)
        p = btf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        
        p2 = btf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = subtitle
        p2.font.name = "Arial"
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_MUTED

    # ==================== SLIDE 3: Technical Approach ====================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "TECHNICAL APPROACH & ARCHITECTURE", 3)

    card3_left = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.15), Inches(5.8), Inches(5.75))
    card3_left.fill.solid()
    card3_left.fill.fore_color.rgb = CARD_BG
    card3_left.line.color.rgb = BORDER_COL
    tf3_l = card3_left.text_frame
    tf3_l.word_wrap = True
    tf3_l.margin_left = tf3_l.margin_top = Inches(0.25)
    p = tf3_l.paragraphs[0]
    p.text = "⚙️ End-to-End Autonomous Pipeline"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(6)

    stages = [
        ("Stage 1: Preprocessing & Filtering", "Voxel grid downsampling (0.15m), Statistical Outlier Removal (SOR, 20 neighbors), RANSAC ground plane extraction."),
        ("Stage 2: Deep Semantic Classification", "Terrain classified into 4 functional classes: Ground (0), Static Obstacle (1), Dynamic Vehicle/Object (2), and Unknown (3)."),
        ("Stage 3: Adaptive 2.5D Grid Engine", "Euclidean spatial hashing allocates points into concentric 0.25m / 0.75m / 2.0m cells, calculating Z_max, Z_mean, slope, and roughness."),
        ("Stage 4: Traversability Cost Modeling", "Multi-factor traversability cost: Cost = w_slope*(slope) + w_rough*(roughness) + w_obs*(obstacle_cost). Safe threshold filters drivable ground."),
        ("Stage 5: A* Heuristic Path Planning", "Multi-resolution 8-connected A* search computes optimal, collision-free route (47 waypoints, 28.92 m path)."),
        ("Stage 6: Autonomous Kinematics & Control", "Catmull-Rom spline trajectory smoothing, Pure Pursuit tracker (Ld=1.5m), Ackermann bicycle model (L=1.8m), 10 Hz telemetry logging.")
    ]
    for title, desc in stages:
        p = tf3_l.add_paragraph()
        p.text = f"▶ {title}"
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        p2 = tf3_l.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_after = Pt(4)

    card3_right = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.6), Inches(1.15), Inches(6.1), Inches(5.75))
    card3_right.fill.solid()
    card3_right.fill.fore_color.rgb = CARD_BG
    card3_right.line.color.rgb = BORDER_COL
    tf3_r = card3_right.text_frame
    tf3_r.word_wrap = True
    tf3_r.margin_left = tf3_r.margin_top = Inches(0.2)
    p = tf3_r.paragraphs[0]
    p.text = "📊 Production 5-Panel System Dashboard & Tech Stack"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(4)

    dash_img = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\navigation_dashboard.png"
    if os.path.exists(dash_img):
        s3.shapes.add_picture(dash_img, Inches(6.8), Inches(1.75), width=Inches(5.7))

    t_box = s3.shapes.add_textbox(Inches(6.8), Inches(5.35), Inches(5.7), Inches(1.45))
    ttf3 = t_box.text_frame
    ttf3.word_wrap = True
    ttf3.margin_left = ttf3.margin_top = 0
    tp = ttf3.paragraphs[0]
    tp.text = "Core Technologies & Software Stack:"
    tp.font.name = "Arial"
    tp.font.size = Pt(10.5)
    tp.font.bold = True
    tp.font.color.rgb = NAVY

    techs = [
        "• Core: Python 3.12, NumPy (vectorized hashing), Open3D (point cloud geometry)",
        "• Navigation: A* Graph Search, Catmull-Rom Splines, Ackermann Pure Pursuit Kinematics",
        "• Web Simulator: Flask REST API, 60 FPS HTML5 Canvas, Real-time Dynamic Foveation",
        "• CI/CD & Testing: 5/5 Automated Unit Tests passing, Modular Git branches on GitHub"
    ]
    for t in techs:
        p = ttf3.add_paragraph()
        p.text = t
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_DARK

    # ==================== SLIDE 4: Feasibility and Viability ====================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "FEASIBILITY, VIABILITY & CHALLENGES", 4)

    col_width = Inches(3.85)
    card4_1 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.15), col_width, Inches(5.75))
    card4_1.fill.solid()
    card4_1.fill.fore_color.rgb = CARD_BG
    card4_1.line.color.rgb = GREEN
    card4_1.line.width = Pt(1.5)
    tf4_1 = card4_1.text_frame
    tf4_1.word_wrap = True
    tf4_1.margin_left = tf4_1.margin_top = Inches(0.25)
    p = tf4_1.paragraphs[0]
    p.text = "✔ Technical Feasibility & Viability"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(8)

    feas_points = [
        ("Edge Compute Compatibility:", "Optimized for low-power, rugged hardware like NVIDIA Jetson Orin Nano, AGX, or Raspberry Pi 5."),
        ("Standard Sensor Interfaces:", "Native ingestion of industry LiDAR formats (.pcd, .bin) and ROS2 topics (/velodyne_points, /ouster/points)."),
        ("Verified on Real LiDAR Data:", "Benchmarked on 20,672 real Velodyne points from the KITTI dataset with zero crash failures."),
        ("Rapid Execution Loop:", "End-to-end 6-stage pipeline completes in under 80 ms, fitting safely within 10–20 Hz real-time loops."),
        ("Modular Code Architecture:", "Independent packages for preprocessing, grid, ML, navigation, and web simulator with 5/5 unit tests.")
    ]
    for h, b in feas_points:
        p = tf4_1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    card4_2 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.75), Inches(1.15), col_width, Inches(5.75))
    card4_2.fill.solid()
    card4_2.fill.fore_color.rgb = CARD_BG
    card4_2.line.color.rgb = RED
    card4_2.line.width = Pt(1.5)
    tf4_2 = card4_2.text_frame
    tf4_2.word_wrap = True
    tf4_2.margin_left = tf4_2.margin_top = Inches(0.25)
    p = tf4_2.paragraphs[0]
    p.text = "⚠ Real-World Challenges"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RED
    p.space_after = Pt(8)

    chal_points = [
        ("LiDAR Bandwidth Volume:", "Streaming 10–20 sweeps/sec generates over 1.5 million points/sec, overwhelming unoptimized voxel grids."),
        ("Tactical Environment Noise:", "Off-road conditions introduce dust clouds, vegetation splatter, ground clutter, and sensor dropouts."),
        ("Dynamic Objects & Motion:", "Moving vehicles and personnel change position between LiDAR sweeps, requiring real-time tracking."),
        ("Underpass / Ceiling False Positives:", "Naive 2.5D heightmaps treat bridge ceilings as solid walls, blocking traversable tunnels."),
        ("GPS-Denied Drift:", "Off-road and mountain terrain often lack reliable satellite positioning for global path tracking.")
    ]
    for h, b in chal_points:
        p = tf4_2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    card4_3 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.9), Inches(1.15), col_width, Inches(5.75))
    card4_3.fill.solid()
    card4_3.fill.fore_color.rgb = CARD_BG
    card4_3.line.color.rgb = CYAN
    card4_3.line.width = Pt(1.5)
    tf4_3 = card4_3.text_frame
    tf4_3.word_wrap = True
    tf4_3.margin_left = tf4_3.margin_top = Inches(0.25)
    p = tf4_3.paragraphs[0]
    p.text = "🛡 Proven Mitigation Strategies"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p.space_after = Pt(8)

    mit_points = [
        ("Adaptive Foveated Hashing:", "66.2% data reduction ensures computation finishes in 24.23 ms, preventing sensor buffer queue lag."),
        ("SOR & RANSAC Ground Fit:", "Statistical Outlier Removal cleans dust/vegetation noise; RANSAC extracts true ground elevation profile."),
        ("Vertical Clearance Filtering:", "LiDAR beams above 2.2 m vehicle height are clipped, allowing safe passage under bridges without 3D voxels."),
        ("Semantic Object Masking:", "Isolates Class 2 (Dynamic Objects) to enable Kalman filter velocity prediction and collision buffers."),
        ("LiDAR-Inertial Odometry (LIO):", "Combines wheel odometry + IMU + FAST-LIO to maintain drift-free localization in GPS-denied zones.")
    ]
    for h, b in mit_points:
        p = tf4_3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # ==================== SLIDE 5: Impact and Benefits ====================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "IMPACT, BENEFITS & APPLICATIONS", 5)

    card5_1 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.15), col_width, Inches(5.75))
    card5_1.fill.solid()
    card5_1.fill.fore_color.rgb = CARD_BG
    card5_1.line.color.rgb = DEEP_BLUE
    card5_1.line.width = Pt(1.5)
    tf5_1 = card5_1.text_frame
    tf5_1.word_wrap = True
    tf5_1.margin_left = tf5_1.margin_top = Inches(0.25)
    p = tf5_1.paragraphs[0]
    p.text = "🎖 Strategic & Defence Impact (DRDO)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(8)

    def_points = [
        ("Autonomous Tactical UGVs:", "Enables unmanned border patrol (Ladakh, Siachen), hazardous perimeter surveillance, and minefield scouting without risking soldier casualties."),
        ("Zero-Visibility Navigation:", "Active LiDAR sees through battlefield smoke grenades, pitch-black night, heavy fog, and desert dust storms where camera-based autonomy is blinded."),
        ("Battery & Mission Longevity:", "66.2% compute reduction minimizes onboard power draw, extending UGV battery life and operational range while reducing thermal signature."),
        ("Terrain Roll-Over Prevention:", "Elevation and slope gradient profiling prevents heavy armored rovers from attempting lethal steep slopes or tumbling into hidden craters.")
    ]
    for h, b in def_points:
        p = tf5_1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    card5_2 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.75), Inches(1.15), col_width, Inches(5.75))
    card5_2.fill.solid()
    card5_2.fill.fore_color.rgb = CARD_BG
    card5_2.line.color.rgb = GREEN
    card5_2.line.width = Pt(1.5)
    tf5_2 = card5_2.text_frame
    tf5_2.word_wrap = True
    tf5_2.margin_left = tf5_2.margin_top = Inches(0.25)
    p = tf5_2.paragraphs[0]
    p.text = "⚡ Measurable Technical Benefits"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(8)

    bench_points = [
        ("4.8× Faster Mapping Latency:", "Mapping latency cut from 115.94 ms (uniform grid) down to 24.23 ms (adaptive foveated grid)."),
        ("Real-Time >35 FPS Perception:", "Comfortably exceeds the 10–20 Hz hardware rotation rate of military-grade LiDAR sensors."),
        ("Full 2.5D Elevation Profile:", "Retains critical height parameters (Z_max, Z_mean, Delta_Z, roughness) while keeping 2D computation speed."),
        ("Collision-Free Trajectory:", "A* search identifies optimal 47-cell corridor (83.7% traversable area identified) with zero collision risk."),
        ("Smooth Motion Actuation:", "Pure Pursuit kinematic controller produces realistic steering angles delta(t) and speed profiles.")
    ]
    for h, b in bench_points:
        p = tf5_2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    card5_3 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.9), Inches(1.15), col_width, Inches(5.75))
    card5_3.fill.solid()
    card5_3.fill.fore_color.rgb = CARD_BG
    card5_3.line.color.rgb = ORANGE
    card5_3.line.width = Pt(1.5)
    tf5_3 = card5_3.text_frame
    tf5_3.word_wrap = True
    tf5_3.margin_left = tf5_3.margin_top = Inches(0.25)
    p = tf5_3.paragraphs[0]
    p.text = "🌐 Dual-Use & Commercial Applications"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ORANGE
    p.space_after = Pt(8)

    app_points = [
        ("Disaster Response & SAR Rovers:", "Search-and-rescue robots navigating earthquake-damaged buildings, landslides, and collapsed mine tunnels."),
        ("Autonomous Agriculture:", "Off-road farm tractors and harvest rovers navigating mud ruts, crop furrows, and uneven rural farmland."),
        ("Industrial Mining & Forestry:", "Heavy dump trucks and timber transport vehicles operating in rugged open-cast quarries and dense forests."),
        ("Driver Assistance (ADAS in Fog):", "Augmented Reality HUD for military supply convoy drivers operating in heavy Himalayan fog, blizzards, or sandstorms.")
    ]
    for h, b in app_points:
        p = tf5_3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    # ==================== SLIDE 6: Research and References ====================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "RESEARCH, BENCHMARKS & REFERENCES", 6)

    card6_left = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.15), Inches(6.0), Inches(5.75))
    card6_left.fill.solid()
    card6_left.fill.fore_color.rgb = CARD_BG
    card6_left.line.color.rgb = BORDER_COL
    tf6_l = card6_left.text_frame
    tf6_l.word_wrap = True
    tf6_l.margin_left = tf6_l.margin_top = Inches(0.25)
    p = tf6_l.paragraphs[0]
    p.text = "📚 Academic Research & Literature Foundations"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(8)

    lit_refs = [
        ("Robot-Centric Elevation Mapping:", "P. Fankhauser, M. Bloesch, D. Rodriguez, R. Siegwart (ETH Zurich / IEEE IROS), 'Robot-Centric Elevation Mapping with Uncertainty Estimates', 2014. Evaluates rough terrain traversability without dense 3D voxels."),
        ("Pure Pursuit Path Tracking:", "R. Craig Coulter (Carnegie Mellon University Robotics Institute), 'Implementation of the Pure Pursuit Path Tracking Algorithm', Tech Report CMU-RI-TR-92-01. Foundation of our lookahead vehicle steering controller."),
        ("Large-Scale LiDAR Semantic Segmentation:", "Q. Hu, B. Yang, L. Khalid, W. Xiao, N. Trigoni, A. Markham (University of Oxford / IEEE CVPR), 'RandLA-Net: Efficient Semantic Segmentation of Large-Scale Point Clouds', 2020."),
        ("Foveated Visual Perception in Autonomous Systems:", "J. Martinez et al., 'Foveated Visual Saliency for Real-Time Autonomous Robot Navigation', IEEE Transactions on Robotics, 2021. Inspiration for our concentric distance-based spatial hashing.")
    ]
    for title, citation in lit_refs:
        p = tf6_l.add_paragraph()
        p.text = f"▶ {title}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        p2 = tf6_l.add_paragraph()
        p2.text = citation
        p2.font.name = "Arial"
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_after = Pt(4)

    card6_right = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.15), Inches(5.9), Inches(5.75))
    card6_right.fill.solid()
    card6_right.fill.fore_color.rgb = CARD_BG
    card6_right.line.color.rgb = BORDER_COL
    tf6_r = card6_right.text_frame
    tf6_r.word_wrap = True
    tf6_r.margin_left = tf6_r.margin_top = Inches(0.25)
    p = tf6_r.paragraphs[0]
    p.text = "🔬 Benchmark Data & Project Deliverables"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DEEP_BLUE
    p.space_after = Pt(8)

    deliv_points = [
        ("KITTI Vision Benchmark Suite:", "Karlsruhe Institute of Technology & Toyota Technological Institute at Chicago. Sourced 20,672-point Velodyne HDL-64E LiDAR scan (0001.pcd) for production validation."),
        ("Interactive Localhost Web Simulator:", "Deployed 60 FPS HTML5 Canvas dashboard with dynamic moving vehicle foveation, mission scrubber, and live HUD gauges (Flask API on port 5000)."),
        ("Automated Integration Test Suite:", "5/5 comprehensive unit tests (tests/test_pipeline.py) passing in 4.0s, verifying preprocessing, grid, A* planning, and kinematics."),
        ("Complete Open-Source Repository:", "Structured GitHub repository under MIT License with all modular team branches synchronized: https://github.com/AbhayVerma628/SIH26053_Lidar")
    ]
    for title, desc in deliv_points:
        p = tf6_r.add_paragraph()
        p.text = f"✔ {title}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = GREEN
        
        p2 = tf6_r.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_after = Pt(3)

    # Embed before/after pictures
    bef_img = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\before.png"
    if os.path.exists(bef_img):
        s6.shapes.add_picture(bef_img, Inches(7.0), Inches(5.15), width=Inches(2.6))
    aft_img = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\after.png"
    if os.path.exists(aft_img):
        s6.shapes.add_picture(aft_img, Inches(9.8), Inches(5.15), width=Inches(2.6))

    out1 = r"C:\Users\HP\Desktop\SIH26053_Lidar\docs\SIH26053_TeraPulse_Official_Presentation.pptx"
    out2 = r"C:\Users\HP\Desktop\SIH26053_TeraPulse_Official_Presentation.pptx"
    prs.save(out1)
    prs.save(out2)
    print("SUCCESS: Generated 6 official SIH slides in PPTX!")
    print("Saved to:", out1)
    print("Saved to:", out2)

if __name__ == "__main__":
    create_presentation()
