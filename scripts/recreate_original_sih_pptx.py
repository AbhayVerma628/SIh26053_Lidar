import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color definitions
    NAVY = RGBColor(15, 23, 42)               # #0f172a (Primary Dark)
    ROYAL_BLUE = RGBColor(29, 78, 216)        # #1d4ed8 (Bold Accent Blue)
    ELECTRIC_BLUE = RGBColor(2, 132, 199)     # #0284c7 (Cyan/Electric)
    CARD_BG = RGBColor(248, 250, 252)         # #f8fafc (Subtle Card Background)
    BORDER_COL = RGBColor(226, 232, 240)      # #e2e8f0 (Clean Card Border)
    TEXT_MAIN = RGBColor(30, 41, 59)          # #1e293b (Charcoal Text)
    TEXT_MUTED = RGBColor(100, 116, 139)      # #64748b (Slate)
    WHITE = RGBColor(255, 255, 255)
    GREEN = RGBColor(16, 185, 129)            # #10b981 (Success Green)
    DARK_GREEN = RGBColor(4, 120, 87)         # #047857
    CORAL_RED = RGBColor(225, 29, 72)         # #e11d48 (Alert Red)
    AMBER = RGBColor(217, 119, 6)             # #d97706 (Amber)
    FOOTER_BLUE = RGBColor(14, 116, 144)      # #0e7490
    LIGHT_BLUE_BG = RGBColor(239, 246, 255)   # #eff6ff (Soft Tint)

    blank_layout = prs.slide_layouts[6]
    img_dir = r"C:\Users\HP\Desktop\SIH26053_Lidar\docs\template_images"
    sih_logo_path = os.path.join(img_dir, "page_1_1_Im1.png")
    brain_img_path = os.path.join(img_dir, "page_1_0_Im0.png")
    car_sensor_path = os.path.join(img_dir, "car_lidar_sensor.png")
    pipeline_img_path = os.path.join(img_dir, "page_6_33_Im2.jpg")

    def add_top_template_header(slide, title_text, slide_num):
        # 1. Oval TERA PULSE logo on top-left (Vibrant styling)
        oval = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.5), Inches(0.2), Inches(1.4), Inches(0.9))
        oval.fill.solid()
        oval.fill.fore_color.rgb = WHITE
        oval.line.color.rgb = ROYAL_BLUE
        oval.line.width = Pt(2.0)
        otf = oval.text_frame
        otf.word_wrap = True
        otf.margin_left = otf.margin_top = otf.margin_right = otf.margin_bottom = 0
        op = otf.paragraphs[0]
        op.alignment = PP_ALIGN.CENTER
        op.text = "TERA\nPULSE"
        op.font.name = "Arial"
        op.font.size = Pt(12)
        op.font.bold = True
        op.font.color.rgb = ROYAL_BLUE

        # 2. Centered Title Banner (Clean stylized look with top accent line)
        banner_box = slide.shapes.add_textbox(Inches(2.1), Inches(0.2), Inches(8.8), Inches(0.9))
        btf = banner_box.text_frame
        btf.word_wrap = True
        btf.margin_left = btf.margin_top = btf.margin_right = btf.margin_bottom = 0
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = title_text
        bp.font.name = "Arial"
        bp.font.size = Pt(22)
        bp.font.bold = True
        bp.font.color.rgb = NAVY

        # 3. SIH 2026 Logo on top-right
        if os.path.exists(sih_logo_path):
            slide.shapes.add_picture(sih_logo_path, Inches(11.1), Inches(0.18), width=Inches(1.75))

        # 4. Footer Bar
        footer_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.12), Inches(13.333), Inches(0.38))
        footer_bar.fill.solid()
        footer_bar.fill.fore_color.rgb = FOOTER_BLUE
        footer_bar.line.fill.background()
        ftf = footer_bar.text_frame
        ftf.margin_top = Inches(0.06)
        fp = ftf.paragraphs[0]
        fp.alignment = PP_ALIGN.CENTER
        fp.text = f"@SIH Idea submission- Template {slide_num}"
        fp.font.name = "Arial"
        fp.font.size = Pt(10.5)
        fp.font.bold = True
        fp.font.color.rgb = WHITE

    # ==================== SLIDE 1: Title & Team Details ====================
    s1 = prs.slides.add_slide(blank_layout)

    # Top SIH 2026 header with decorative bar
    top_txt = s1.shapes.add_textbox(Inches(1.0), Inches(0.28), Inches(10.0), Inches(0.65))
    ttf = top_txt.text_frame
    tp = ttf.paragraphs[0]
    tp.alignment = PP_ALIGN.CENTER
    tp.text = "SMART INDIA HACKATHON 2026"
    tp.font.name = "Arial"
    tp.font.size = Pt(26)
    tp.font.bold = True
    tp.font.color.rgb = ROYAL_BLUE

    # Title: Highlighted in two contrasting bold colors
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.88), Inches(10.5), Inches(1.35))
    ttf2 = t_box.text_frame
    ttf2.word_wrap = True
    tp2 = ttf2.paragraphs[0]
    tp2.alignment = PP_ALIGN.CENTER
    r1 = tp2.add_run()
    r1.text = "Adaptive Foveated 2.5D Semantic Mapping\n"
    r1.font.name = "Arial"
    r1.font.size = Pt(28)
    r1.font.bold = True
    r1.font.color.rgb = NAVY

    r2 = tp2.add_run()
    r2.text = "for Autonomous Navigation"
    r2.font.name = "Arial"
    r2.font.size = Pt(26)
    r2.font.bold = True
    r2.font.color.rgb = ROYAL_BLUE

    # Accent divider line under title
    div_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.5), Inches(2.28), Inches(4.33), Inches(0.05))
    div_line.fill.solid()
    div_line.fill.fore_color.rgb = ELECTRIC_BLUE
    div_line.line.fill.background()

    # SIH Logo on top right
    if os.path.exists(sih_logo_path):
        s1.shapes.add_picture(sih_logo_path, Inches(11.1), Inches(0.18), width=Inches(1.75))

    # Left: Details Card with highlighted bold labels
    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.48), Inches(7.2), Inches(4.5))
    card1.fill.solid()
    card1.fill.fore_color.rgb = CARD_BG
    card1.line.color.rgb = BORDER_COL
    card1.line.width = Pt(1.5)
    c1_tf = card1.text_frame
    c1_tf.word_wrap = True
    c1_tf.margin_left = c1_tf.margin_top = Inches(0.25)

    d_items = [
        ("Problem Statement ID –", " 26053"),
        ("Problem Statement Title –", " Adaptive Foveated 2.5D Semantic Mapping from LiDAR Point Clouds for Autonomous Navigation"),
        ("Theme –", " Smart Vehicles"),
        ("PS Category –", " Software"),
        ("Team ID –", " TBA"),
        ("Team Name –", " TeraPulse"),
        ("Team Members –", " Abhay Verma (Team Leader), Lokendra Singh,\nYashvardhan Jain, Chetan Meena, Sachin Chaubey, Esha Verma"),
        ("Institute –", " Indian Institute of Information Technology Bhopal")
    ]
    for i, (label, val) in enumerate(d_items):
        p = c1_tf.paragraphs[0] if i == 0 else c1_tf.add_paragraph()
        p.space_after = Pt(6)
        run_lbl = p.add_run()
        run_lbl.text = f"•  {label}"
        run_lbl.font.name = "Arial"
        run_lbl.font.size = Pt(13)
        run_lbl.font.bold = True
        run_lbl.font.color.rgb = ROYAL_BLUE

        run_val = p.add_run()
        run_val.text = val
        run_val.font.name = "Arial"
        run_val.font.size = Pt(13)
        run_val.font.bold = False
        run_val.font.color.rgb = NAVY

    # Right: Official SIH Brain Bulb Image (Enlarged to 5.1 inches)
    if os.path.exists(brain_img_path):
        s1.shapes.add_picture(brain_img_path, Inches(8.2), Inches(2.35), width=Inches(4.8))

    # ==================== SLIDE 2: Proposed Solution ====================
    s2 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s2, "Adaptive Foveated 2.5D Semantic Mapping\nfor Autonomous Navigation", 2)

    # Left Column: Card Container with bold highlighted lead-ins
    left_card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.2), Inches(6.5), Inches(4.3))
    left_card.fill.solid()
    left_card.fill.fore_color.rgb = CARD_BG
    left_card.line.color.rgb = BORDER_COL
    left_card.line.width = Pt(1.5)
    lc_tf = left_card.text_frame
    lc_tf.word_wrap = True
    lc_tf.margin_left = lc_tf.margin_top = Inches(0.25)

    hp = lc_tf.paragraphs[0]
    hp.text = "❖ Proposed Solution"
    hp.font.name = "Arial"
    hp.font.size = Pt(18)
    hp.font.bold = True
    hp.font.color.rgb = ROYAL_BLUE
    hp.space_after = Pt(6)

    sol_bullets = [
        ("2.5D Semantic Elevation Map: ", "Generates an efficient multi-resolution heightmap from raw 3D LiDAR point clouds."),
        ("High-Precision Near Field (0–10 m): ", "Fine 0.25 m cells for sub-meter obstacle clearance, terrain slope, and reactive steering."),
        ("Bandwidth-Saving Far Field: ", "Gradually reduces to 0.75 m & 2.0 m resolution to slash unnecessary distant computations."),
        ("Full Elevation Profiling: ", "Preserves height, step slope & obstacle boundaries without full 3D voxel memory overload."),
        ("Real-Time Terrain Intelligence: ", "Accurately classifies drivable ground, static obstacles, and dynamic moving objects."),
        ("Autonomous Navigation Stack: ", "Enables instant A* heuristic path planning and smooth Pure Pursuit vehicle steering.")
    ]
    for tag, desc in sol_bullets:
        p = lc_tf.add_paragraph()
        p.space_after = Pt(4)
        r_tag = p.add_run()
        r_tag.text = "• " + tag
        r_tag.font.name = "Arial"
        r_tag.font.size = Pt(11.5)
        r_tag.font.bold = True
        r_tag.font.color.rgb = ROYAL_BLUE

        r_desc = p.add_run()
        r_desc.text = desc
        r_desc.font.name = "Arial"
        r_desc.font.size = Pt(11.5)
        r_desc.font.color.rgb = TEXT_MAIN

    # Innovation Box below
    in_card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(5.6), Inches(6.5), Inches(1.35))
    in_card.fill.solid()
    in_card.fill.fore_color.rgb = LIGHT_BLUE_BG
    in_card.line.color.rgb = ROYAL_BLUE
    in_card.line.width = Pt(1.5)
    ic_tf = in_card.text_frame
    ic_tf.word_wrap = True
    ic_tf.margin_left = ic_tf.margin_top = Inches(0.18)

    ip = ic_tf.paragraphs[0]
    ip.text = "❖ Innovation & Uniqueness"
    ip.font.name = "Arial"
    ip.font.size = Pt(15)
    ip.font.bold = True
    ip.font.color.rgb = ROYAL_BLUE
    ip.space_after = Pt(4)

    ip2 = ic_tf.add_paragraph()
    r_it = ip2.add_run()
    r_it.text = "Foveated adaptive resolution "
    r_it.font.bold = True
    r_it.font.color.rgb = NAVY
    r_it2 = ip2.add_run()
    r_it2.text = "focuses computational resources where they matter most — slashing memory by "
    r_it2.font.color.rgb = TEXT_MAIN
    r_it3 = ip2.add_run()
    r_it3.text = "66.2% "
    r_it3.font.bold = True
    r_it3.font.color.rgb = DARK_GREEN
    r_it4 = ip2.add_run()
    r_it4.text = "and cutting latency to "
    r_it4.font.color.rgb = TEXT_MAIN
    r_it5 = ip2.add_run()
    r_it5.text = "24.23 ms (>35 FPS)."
    r_it5.font.bold = True
    r_it5.font.color.rgb = ROYAL_BLUE

    # Right: Foveated Concentric Circle Graphic (Matching original visual!)
    c_out = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(7.5), Inches(1.65), Inches(5.2), Inches(5.2))
    c_out.fill.solid()
    c_out.fill.fore_color.rgb = RGBColor(190, 220, 250)
    c_out.line.color.rgb = RGBColor(100, 160, 230)
    c_out.line.width = Pt(2.5)

    c_in = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(8.85), Inches(3.0), Inches(2.5), Inches(2.5))
    c_in.fill.solid()
    c_in.fill.fore_color.rgb = RGBColor(20, 110, 200)
    c_in.line.color.rgb = RGBColor(10, 80, 160)
    c_in.line.width = Pt(2.5)

    v_dot = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.85), Inches(4.0), Inches(0.52), Inches(0.52))
    v_dot.fill.solid()
    v_dot.fill.fore_color.rgb = WHITE
    v_dot.line.fill.background()

    c_title = s2.shapes.add_textbox(Inches(7.3), Inches(1.15), Inches(5.5), Inches(0.45))
    ctf = c_title.text_frame
    cp = ctf.paragraphs[0]
    cp.alignment = PP_ALIGN.CENTER
    cp.text = "Foveated 2.5D Semantic Elevation Map"
    cp.font.name = "Arial"
    cp.font.size = Pt(16)
    cp.font.bold = True
    cp.font.color.rgb = NAVY

    # Legend at bottom right
    leg1 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.4), Inches(6.35), Inches(0.4), Inches(0.28))
    leg1.fill.solid()
    leg1.fill.fore_color.rgb = RGBColor(20, 110, 200)
    leg1.line.fill.background()
    t_leg1 = s2.shapes.add_textbox(Inches(7.9), Inches(6.32), Inches(5.0), Inches(0.32))
    t_leg1.text_frame.margin_left = t_leg1.text_frame.margin_top = 0
    p = t_leg1.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "High resolution near vehicle "
    r.font.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = ROYAL_BLUE
    r2 = p.add_run()
    r2.text = "(near-field: 0.25 m bubble)"
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = TEXT_MAIN

    leg2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.4), Inches(6.72), Inches(0.4), Inches(0.28))
    leg2.fill.solid()
    leg2.fill.fore_color.rgb = RGBColor(190, 220, 250)
    leg2.line.fill.background()
    t_leg2 = s2.shapes.add_textbox(Inches(7.9), Inches(6.68), Inches(5.0), Inches(0.32))
    t_leg2.text_frame.margin_left = t_leg2.text_frame.margin_top = 0
    p = t_leg2.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Lower resolution for distant regions "
    r.font.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = NAVY
    r2 = p.add_run()
    r2.text = "(far-field: 0.75m & 2.0m)"
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = TEXT_MAIN

    # ==================== SLIDE 3: Technical Approach ====================
    s3 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s3, "TECHNICAL APPROACH", 3)

    sw_title = s3.shapes.add_textbox(Inches(0.6), Inches(1.22), Inches(4.8), Inches(0.45))
    sw_tf = sw_title.text_frame
    sw_p = sw_tf.paragraphs[0]
    sw_p.text = "⚙️ System Workflow Pipeline"
    sw_p.font.name = "Arial"
    sw_p.font.size = Pt(18)
    sw_p.font.bold = True
    sw_p.font.color.rgb = ROYAL_BLUE

    wf_boxes = [
        ("1", "LiDAR Point Cloud Ingestion"),
        ("2", "Preprocessing & Noise Removal"),
        ("3", "Deep Semantic Classification"),
        ("4", "Foveated Adaptive Grid Generation"),
        ("5", "2.5D Semantic Elevation Map"),
        ("6", "Real-Time Visualization & Navigation")
    ]
    cur_y = 1.78
    box_h = 0.58
    for i, (num, wftxt) in enumerate(wf_boxes):
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(cur_y), Inches(4.6), Inches(box_h))
        box.fill.solid()
        box.fill.fore_color.rgb = ROYAL_BLUE
        box.line.color.rgb = WHITE
        box.line.width = Pt(1.0)
        btf = box.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = f"[{num}]  {wftxt}"
        bp.font.name = "Arial"
        bp.font.size = Pt(12)
        bp.font.bold = True
        bp.font.color.rgb = WHITE
        
        cur_y += box_h + 0.08
        if i < len(wf_boxes) - 1:
            arrow = s3.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(2.75), Inches(cur_y - 0.05), Inches(0.3), Inches(0.2))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = ELECTRIC_BLUE
            arrow.line.fill.background()
            cur_y += 0.21

    # Right: BIG 5-Panel System Dashboard Photo (7.4 inches wide!)
    dash_path = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\navigation_dashboard.png"
    if os.path.exists(dash_path):
        s3.shapes.add_picture(dash_path, Inches(5.4), Inches(1.25), width=Inches(7.4))

    # Technologies Box below photo
    tech_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.4), Inches(5.05), Inches(7.4), Inches(1.9))
    tech_card.fill.solid()
    tech_card.fill.fore_color.rgb = CARD_BG
    tech_card.line.color.rgb = BORDER_COL
    tech_card.line.width = Pt(1.5)
    tc_tf = tech_card.text_frame
    tc_tf.word_wrap = True
    tc_tf.margin_left = tc_tf.margin_top = Inches(0.18)

    tp = tc_tf.paragraphs[0]
    tp.text = "💻 Technologies & Software Implementation:"
    tp.font.name = "Arial"
    tp.font.size = Pt(13.5)
    tp.font.bold = True
    tp.font.color.rgb = ROYAL_BLUE
    tp.space_after = Pt(4)

    tech_list = [
        ("Core Stack: ", "Python 3.12, NumPy (vectorized hashing), Open3D (point cloud geometry)"),
        ("Semantic Intelligence: ", "4-Class ML Classifier (Ground, Static Obstacles, Dynamic Vehicles)"),
        ("Autonomous Motion: ", "A* Graph Search, Catmull-Rom Splines, Ackermann Pure Pursuit Kinematics"),
        ("Live Web Dashboard: ", "Flask REST API, 60 FPS HTML5 Canvas with dynamic moving-car foveation")
    ]
    for tag, desc in tech_list:
        p = tc_tf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.name = "Arial"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY

        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Arial"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MAIN

    # ==================== SLIDE 4: Feasibility and Viability ====================
    s4 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s4, "FEASIBILITY AND VIABILITY", 4)

    def add_styled_pill(slide, text, left, top, width, color):
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, Inches(0.48))
        pill.fill.solid()
        pill.fill.fore_color.rgb = color
        pill.line.fill.background()
        ptf = pill.text_frame
        ptf.vertical_anchor = MSO_ANCHOR.MIDDLE
        pp = ptf.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = text
        pp.font.name = "Arial"
        pp.font.size = Pt(13)
        pp.font.bold = True
        pp.font.color.rgb = WHITE

    # Left: Feasibility (Green Pill)
    add_styled_pill(s4, "✔ Feasibility & Viability", Inches(0.6), Inches(1.22), Inches(2.6), DARK_GREEN)
    f_box = s4.shapes.add_textbox(Inches(0.6), Inches(1.8), Inches(5.8), Inches(2.0))
    ftf = f_box.text_frame
    ftf.word_wrap = True
    ftf.margin_left = ftf.margin_top = 0
    f_bullets = [
        ("Open-Source & Standard Datasets: ", "Built on widely tested LiDAR datasets and open tools."),
        ("Rapid Edge Prototype: ", "Python 3.12, Open3D, and PyTorch enable agile modular development."),
        ("Edge Compute Efficiency: ", "Adaptive resolution drastically reduces RAM and latency."),
        ("Independent Subsystem Verification: ", "Modular pipeline with 5/5 automated unit tests passing.")
    ]
    for tag, desc in f_bullets:
        p = ftf.paragraphs[0] if tag == f_bullets[0][0] else ftf.add_paragraph()
        p.space_after = Pt(3)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = DARK_GREEN
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_MAIN

    # Left: Challenges (Coral Red Pill)
    add_styled_pill(s4, "⚠ Tactical Challenges", Inches(0.6), Inches(3.9), Inches(2.6), CORAL_RED)
    c_box = s4.shapes.add_textbox(Inches(0.6), Inches(4.48), Inches(5.8), Inches(2.4))
    ctf = c_box.text_frame
    ctf.word_wrap = True
    ctf.margin_left = ctf.margin_top = 0
    c_bullets = [
        ("Heavy LiDAR Data Deluge: ", "Real-time processing of 1.5M points/sec from 10–20 Hz sweeps."),
        ("Unstructured Off-Road Terrain: ", "Accurate terrain segmentation in dusty, rocky environments."),
        ("Bridge / Underpass False Obstacles: ", "Preventing ceiling points from falsely blocking tunnels."),
        ("Preserving Geometry in Low-Res: ", "Retaining safety clearance while reducing distant cell detail.")
    ]
    for tag, desc in c_bullets:
        p = ctf.paragraphs[0] if tag == c_bullets[0][0] else ctf.add_paragraph()
        p.space_after = Pt(3)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = CORAL_RED
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_MAIN

    # Middle: Mitigation Strategy (Royal Blue Pill)
    add_styled_pill(s4, "🛡 Mitigation Strategies", Inches(6.7), Inches(1.22), Inches(2.8), ROYAL_BLUE)
    m_box = s4.shapes.add_textbox(Inches(6.7), Inches(1.8), Inches(6.0), Inches(1.6))
    mtf = m_box.text_frame
    mtf.word_wrap = True
    mtf.margin_left = mtf.margin_top = 0
    m_bullets = [
        ("Foveated Attention Hashing: ", "Focuses 0.25 m resolution in near-field for instant 24.23 ms execution."),
        ("SOR & RANSAC Ground Fit: ", "Statistical filters eliminate dust scatter and extract clean ground plane."),
        ("Vertical Clearance Filtering: ", "Clips points >2.2 m to allow safe tunnel traversal without 3D voxels."),
        ("Rigorous Verification: ", "Benchmarked on 20,672 points at >35 FPS with zero crash failures.")
    ]
    for tag, desc in m_bullets:
        p = mtf.paragraphs[0] if tag == m_bullets[0][0] else mtf.add_paragraph()
        p.space_after = Pt(3)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = ROYAL_BLUE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_MAIN

    # Right: Autonomous Car Sensor Visual (Bigger: 6.2 inches)
    if os.path.exists(car_sensor_path):
        s4.shapes.add_picture(car_sensor_path, Inches(6.7), Inches(3.45), width=Inches(6.2))

    # ==================== SLIDE 5: Impact and Benefits ====================
    s5 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s5, "IMPACT AND BENEFITS", 5)

    add_styled_pill(s5, "🎖 Strategic Defence Impact", Inches(0.6), Inches(1.22), Inches(3.0), NAVY)
    i_box = s5.shapes.add_textbox(Inches(0.6), Inches(1.8), Inches(4.9), Inches(1.65))
    itf = i_box.text_frame
    itf.word_wrap = True
    itf.margin_left = itf.margin_top = 0
    i_bullets = [
        ("Autonomous Tactical UGVs: ", "Border patrol (Ladakh/Siachen) & minefield reconnaissance without soldier casualties."),
        ("Zero-Visibility Warfare: ", "LiDAR penetrates smoke, sandstorms, fog & darkness where cameras fail."),
        ("Sub-Meter Hazard Detection: ", "Guarantees obstacle clearance in safety-critical vehicle zones."),
        ("Real-Time Terrain Intelligence: ", "Prevents roll-overs on steep inclines and hidden ditches.")
    ]
    for tag, desc in i_bullets:
        p = itf.paragraphs[0] if tag == i_bullets[0][0] else itf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = ROYAL_BLUE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MAIN

    add_styled_pill(s5, "🌐 Dual-Use Applications", Inches(0.6), Inches(3.55), Inches(2.8), AMBER)
    a_box = s5.shapes.add_textbox(Inches(0.6), Inches(4.1), Inches(4.9), Inches(1.4))
    atf = a_box.text_frame
    atf.word_wrap = True
    atf.margin_left = atf.margin_top = 0
    a_bullets = [
        ("Defence & Security: ", "UGVs, logistics convoys & border patrol rovers."),
        ("Disaster Response: ", "Search-and-rescue rovers in earthquake rubble & caves."),
        ("Industrial Autonomy: ", "Autonomous tractors on farmland & mining dump trucks.")
    ]
    for tag, desc in a_bullets:
        p = atf.paragraphs[0] if tag == a_bullets[0][0] else atf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = AMBER
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MAIN

    add_styled_pill(s5, "⚡ Measurable Benefits", Inches(0.6), Inches(5.35), Inches(2.6), DARK_GREEN)
    ben_box = s5.shapes.add_textbox(Inches(0.6), Inches(5.9), Inches(4.9), Inches(1.3))
    btf = ben_box.text_frame
    btf.word_wrap = True
    btf.margin_left = btf.margin_top = 0
    ben_bullets = [
        ("66.2% Cell Reduction: ", "Slashing memory and compute load on embedded edge hardware."),
        ("4.8× Faster Latency: ", "Down from 115.94 ms to 24.23 ms for true 35+ FPS control."),
        ("Full 2.5D Elevation: ", "Preserves slopes, roughness & step heights without 3D voxels.")
    ]
    for tag, desc in ben_bullets:
        p = btf.paragraphs[0] if tag == ben_bullets[0][0] else btf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = DARK_GREEN
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MAIN

    # Right: BEFORE & AFTER PHOTOS (Enlarged with badge tags!)
    bef_img = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\before.png"
    aft_img = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\after.png"
    
    t_photo = s5.shapes.add_textbox(Inches(5.7), Inches(1.22), Inches(7.1), Inches(0.35))
    t_photo.text_frame.margin_left = t_photo.text_frame.margin_top = 0
    t_p = t_photo.text_frame.paragraphs[0]
    t_p.text = "📸 Visual Impact: Raw Point Cloud vs Cleaned 2.5D Elevation Map"
    t_p.font.name = "Arial"
    t_p.font.size = Pt(14)
    t_p.font.bold = True
    t_p.font.color.rgb = ROYAL_BLUE

    if os.path.exists(bef_img):
        s5.shapes.add_picture(bef_img, Inches(5.7), Inches(1.65), width=Inches(3.55))
        lbl1 = s5.shapes.add_textbox(Inches(5.7), Inches(4.35), Inches(3.55), Inches(0.35))
        lbl1.text_frame.margin_left = lbl1.text_frame.margin_top = 0
        p = lbl1.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = "Raw LiDAR Scan "
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = "(20,672 points with noise)"
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_MUTED

    if os.path.exists(aft_img):
        s5.shapes.add_picture(aft_img, Inches(9.35), Inches(1.65), width=Inches(3.55))
        lbl2 = s5.shapes.add_textbox(Inches(9.35), Inches(4.35), Inches(3.55), Inches(0.35))
        lbl2.text_frame.margin_left = lbl2.text_frame.margin_top = 0
        p = lbl2.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = "Filtered 2.5D Elevation Map "
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = DARK_GREEN
        r2 = p.add_run()
        r2.text = "(Drivable Ground Extracted)"
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_MUTED

    # Benchmark Card
    res_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.7), Inches(4.8), Inches(7.2), Inches(2.15))
    res_card.fill.solid()
    res_card.fill.fore_color.rgb = LIGHT_BLUE_BG
    res_card.line.color.rgb = ROYAL_BLUE
    res_card.line.width = Pt(1.5)
    rc_tf = res_card.text_frame
    rc_tf.word_wrap = True
    rc_tf.margin_left = rc_tf.margin_top = Inches(0.18)
    rp = rc_tf.paragraphs[0]
    rp.text = "🏆 Production Performance Benchmark (KITTI Velodyne HDL-64E):"
    rp.font.name = "Arial"
    rp.font.size = Pt(12)
    rp.font.bold = True
    rp.font.color.rgb = ROYAL_BLUE
    rp.space_after = Pt(4)

    stats = [
        ("Active Stored Cells: ", "Reduced from 2,888 (uniform) to 976 (adaptive) — ", "66.2% Cell Reduction"),
        ("Mapping Compute Time: ", "Reduced from 115.94 ms to 24.23 ms — ", "4.8× Latency Speedup"),
        ("Traversable Corridor: ", "817 safe cells (83.71%) accurately identified without collision risk", ""),
        ("Autonomous Trajectory: ", "47-cell A* path tracked smoothly via Pure Pursuit (10 Hz Telemetry)", "")
    ]
    for tag, desc, hilight in stats:
        p = rc_tf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.name = "Arial"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY

        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Arial"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MAIN

        if hilight:
            r3 = p.add_run()
            r3.text = hilight
            r3.font.name = "Arial"
            r3.font.size = Pt(10.5)
            r3.font.bold = True
            r3.font.color.rgb = DARK_GREEN

    # ==================== SLIDE 6: Research and References ====================
    s6 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s6, "RESEARCH AND REFERENCES", 6)

    add_styled_pill(s6, "📚 Research Areas", Inches(0.6), Inches(1.22), Inches(2.4), NAVY)
    ra_box = s6.shapes.add_textbox(Inches(0.6), Inches(1.8), Inches(4.5), Inches(1.8))
    ratf = ra_box.text_frame
    ratf.word_wrap = True
    ratf.margin_left = ratf.margin_top = 0
    ra_bullets = [
        ("LiDAR Processing: ", "Point cloud filtering, SOR & RANSAC ground estimation."),
        ("2.5D Elevation Mapping: ", "Robot-centric height & slope representation."),
        ("Semantic Understanding: ", "Deep learning segmentation of large-scale point clouds."),
        ("Autonomous Navigation: ", "A* heuristic planning & Pure Pursuit vehicle kinematics."),
        ("Adaptive Spatial Hashing: ", "Foveated variable-resolution concentric indexing.")
    ]
    for tag, desc in ra_bullets:
        p = ratf.paragraphs[0] if tag == ra_bullets[0][0] else ratf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = ROYAL_BLUE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MAIN

    add_styled_pill(s6, "📖 Academic References", Inches(0.6), Inches(3.75), Inches(2.8), ROYAL_BLUE)
    ref_box = s6.shapes.add_textbox(Inches(0.6), Inches(4.3), Inches(4.5), Inches(2.6))
    reftf = ref_box.text_frame
    reftf.word_wrap = True
    reftf.margin_left = reftf.margin_top = 0
    ref_bullets = [
        ("KITTI Vision Suite: ", "Geiger et al. (Karlsruhe / Toyota Tech), Velodyne HDL-64E LiDAR benchmark."),
        ("ETH Zurich Elevation Mapping: ", "P. Fankhauser et al. (IEEE IROS), Robot-Centric Elevation Mapping."),
        ("CMU Pure Pursuit Tracker: ", "R. C. Coulter (Carnegie Mellon Robotics Institute), Pure Pursuit Kinematics."),
        ("Large-Scale Segmentation: ", "Q. Hu et al. (Oxford / CVPR), RandLA-Net Point Cloud Segmentation."),
        ("Foveated Visual Attention: ", "J. Martinez et al. (IEEE Trans. Robotics), Foveated Saliency for Navigation.")
    ]
    for tag, desc in ref_bullets:
        p = reftf.paragraphs[0] if tag == ref_bullets[0][0] else reftf.add_paragraph()
        p.space_after = Pt(3)
        r1 = p.add_run()
        r1.text = "• " + tag
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MAIN

    # Right: Numbered Research Pipeline Graphic (Enlarged: 7.8 inches!)
    if os.path.exists(pipeline_img_path):
        pipe_title = s6.shapes.add_textbox(Inches(5.3), Inches(1.2), Inches(7.7), Inches(0.4))
        pipe_title.text_frame.margin_left = pipe_title.text_frame.margin_top = 0
        pp = pipe_title.text_frame.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = "LiDAR 2.5 RESEARCH PIPELINE"
        pp.font.name = "Arial"
        pp.font.size = Pt(17)
        pp.font.bold = True
        pp.font.color.rgb = NAVY

        s6.shapes.add_picture(pipeline_img_path, Inches(5.2), Inches(1.7), width=Inches(7.8))

    deliv_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.2), Inches(5.05), Inches(7.8), Inches(1.9))
    deliv_box.fill.solid()
    deliv_box.fill.fore_color.rgb = LIGHT_BLUE_BG
    deliv_box.line.color.rgb = ROYAL_BLUE
    deliv_box.line.width = Pt(1.5)
    dtf = deliv_box.text_frame
    dtf.word_wrap = True
    dtf.margin_left = dtf.margin_top = Inches(0.16)
    p = dtf.paragraphs[0]
    p.text = "💻 Verified Project Deliverables & Repository:"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ROYAL_BLUE
    p.space_after = Pt(3)

    d_items = [
        ("Interactive Localhost Simulator: ", "60 FPS HTML5 / Flask Dashboard with live dynamic foveation & HUD"),
        ("Automated Test Suite: ", "5/5 comprehensive unit tests (tests/test_pipeline.py) passing in 4.0s"),
        ("Open-Source Codebase: ", "Production GitHub repository: github.com/AbhayVerma628/SIH26053_Lidar"),
        ("Autonomous Output Artifacts: ", "5-panel dashboard, 10 Hz telemetry CSV, planned A* path, benchmark JSON")
    ]
    for tag, desc in d_items:
        p = dtf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = "✔ " + tag
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = DARK_GREEN
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MAIN

    # Save presentation
    out_pptx1 = r"C:\Users\HP\Desktop\SIH26053_Lidar\docs\SIH26053_TeraPulse_Official_Presentation.pptx"
    out_pptx2 = r"C:\Users\HP\Desktop\SIH26053_TeraPulse_Official_Presentation.pptx"
    prs.save(out_pptx1)
    prs.save(out_pptx2)
    print("SUCCESS: Highlighted, bold, and attractive presentation built successfully!")
    print("Saved PPTX to:", out_pptx1)
    print("Saved PPTX to:", out_pptx2)

if __name__ == "__main__":
    build_presentation()
