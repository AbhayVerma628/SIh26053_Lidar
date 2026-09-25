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

    # Color definitions matching original PDF
    TITLE_BLUE = RGBColor(30, 64, 130)       # Deep SIH blue
    BLACK = RGBColor(17, 24, 39)              # Text & banner
    DARK_BANNER = RGBColor(220, 224, 230)     # Light grey banner background or white
    HEADER_BLUE = RGBColor(14, 116, 144)      # Accent blue
    PILL_BLUE = RGBColor(29, 78, 216)         # Deep blue pill for headers (#1d4ed8)
    LIGHT_BLUE_BG = RGBColor(239, 246, 255)   # #eff6ff
    TEXT_MAIN = RGBColor(31, 41, 55)          # Dark gray text
    TEXT_MUTED = RGBColor(107, 114, 128)      # Gray
    WHITE = RGBColor(255, 255, 255)
    NEAR_BLUE = RGBColor(2, 132, 199)         # Cyan/blue for near field
    FAR_BLUE = RGBColor(186, 230, 253)        # Light sky blue for far field
    FOOTER_BLUE = RGBColor(14, 116, 144)

    blank_layout = prs.slide_layouts[6]
    img_dir = r"C:\Users\HP\Desktop\SIH26053_Lidar\docs\template_images"
    sih_logo_path = os.path.join(img_dir, "page_1_1_Im1.png")
    brain_img_path = os.path.join(img_dir, "page_1_0_Im0.png")
    car_sensor_path = os.path.join(img_dir, "car_lidar_sensor.png")
    pipeline_img_path = os.path.join(img_dir, "page_6_33_Im2.jpg")

    def add_top_template_header(slide, title_text, slide_num):
        # 1. Oval TERA PULSE logo on top-left
        oval = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.5), Inches(0.25), Inches(1.35), Inches(0.85))
        oval.fill.solid()
        oval.fill.fore_color.rgb = WHITE
        oval.line.color.rgb = BLACK
        oval.line.width = Pt(1.5)
        otf = oval.text_frame
        otf.word_wrap = True
        otf.margin_left = otf.margin_top = otf.margin_right = otf.margin_bottom = 0
        op = otf.paragraphs[0]
        op.alignment = PP_ALIGN.CENTER
        op.text = "TERA\nPULSE"
        op.font.name = "Arial"
        op.font.size = Pt(11)
        op.font.bold = True
        op.font.color.rgb = BLACK

        # 2. Centered Title Banner
        banner_box = slide.shapes.add_textbox(Inches(2.1), Inches(0.25), Inches(8.8), Inches(0.85))
        btf = banner_box.text_frame
        btf.word_wrap = True
        btf.margin_left = btf.margin_top = btf.margin_right = btf.margin_bottom = 0
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = title_text
        bp.font.name = "Arial"
        bp.font.size = Pt(21)
        bp.font.bold = True
        bp.font.color.rgb = BLACK

        # 3. SIH 2026 Logo on top-right
        if os.path.exists(sih_logo_path):
            slide.shapes.add_picture(sih_logo_path, Inches(11.2), Inches(0.2), width=Inches(1.6))

        # 4. Footer Bar
        footer_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.15), Inches(13.333), Inches(0.35))
        footer_bar.fill.solid()
        footer_bar.fill.fore_color.rgb = FOOTER_BLUE
        footer_bar.line.fill.background()
        ftf = footer_bar.text_frame
        ftf.margin_top = Inches(0.05)
        fp = ftf.paragraphs[0]
        fp.alignment = PP_ALIGN.CENTER
        fp.text = f"@SIH Idea submission- Template {slide_num}"
        fp.font.name = "Arial"
        fp.font.size = Pt(10)
        fp.font.color.rgb = WHITE

    # ==================== SLIDE 1: Title & Team Details ====================
    s1 = prs.slides.add_slide(blank_layout)

    # Top SIH 2026 header
    top_txt = s1.shapes.add_textbox(Inches(1.0), Inches(0.35), Inches(10.0), Inches(0.6))
    ttf = top_txt.text_frame
    tp = ttf.paragraphs[0]
    tp.alignment = PP_ALIGN.CENTER
    tp.text = "SMART INDIA HACKATHON 2026"
    tp.font.name = "Arial"
    tp.font.size = Pt(24)
    tp.font.bold = True
    tp.font.color.rgb = TITLE_BLUE

    # Title
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(10.5), Inches(1.2))
    ttf2 = t_box.text_frame
    ttf2.word_wrap = True
    tp2 = ttf2.paragraphs[0]
    tp2.alignment = PP_ALIGN.CENTER
    tp2.text = "Adaptive Foveated 2.5D Semantic Mapping for\nAutonomous Navigation"
    tp2.font.name = "Arial"
    tp2.font.size = Pt(26)
    tp2.font.bold = True
    tp2.font.color.rgb = BLACK

    # SIH Logo on top right
    if os.path.exists(sih_logo_path):
        s1.shapes.add_picture(sih_logo_path, Inches(11.2), Inches(0.2), width=Inches(1.6))

    # Left: Details
    details_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.5), Inches(7.5), Inches(4.5))
    dtf = details_box.text_frame
    dtf.word_wrap = True
    dtf.margin_left = dtf.margin_top = 0

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
        p = dtf.paragraphs[0] if i == 0 else dtf.add_paragraph()
        p.text = f"•  {label}{val}"
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = BLACK
        p.space_after = Pt(8)

    # Right: Official SIH Brain Bulb Image
    if os.path.exists(brain_img_path):
        s1.shapes.add_picture(brain_img_path, Inches(7.8), Inches(2.3), width=Inches(4.8))

    # ==================== SLIDE 2: Proposed Solution ====================
    s2 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s2, "Adaptive Foveated 2.5D Semantic Mapping\nfor Autonomous Navigation", 2)

    # Left Column: Proposed Solution & Innovation
    # Section 1 Header: ❖ Proposed Solution
    h1 = s2.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(6.2), Inches(0.5))
    htf = h1.text_frame
    hp = htf.paragraphs[0]
    hp.text = "❖ Proposed Solution"
    hp.font.name = "Arial"
    hp.font.size = Pt(17)
    hp.font.bold = True
    hp.font.color.rgb = PILL_BLUE

    # Bullets
    b1 = s2.shapes.add_textbox(Inches(0.6), Inches(1.75), Inches(6.2), Inches(2.7))
    btf = b1.text_frame
    btf.word_wrap = True
    btf.margin_left = btf.margin_top = 0
    p2_bullets = [
        "2.5D semantic elevation map generated from raw LiDAR point clouds.",
        "High resolution near the vehicle (0.25 m) for critical near-field perception.",
        "Lower resolution for distant regions (0.75 m & 2.0 m) — cuts unnecessary computation.",
        "Preserves height, terrain gradient & obstacle boundaries without full 3D voxels.",
        "Identifies drivable ground, static obstacles & dynamic objects in real time.",
        "Enables fast closed-loop environmental understanding for path planning."
    ]
    for i, b in enumerate(p2_bullets):
        p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
        p.text = b
        p.font.name = "Arial"
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(4)

    # Section 2 Header: ❖ Innovation & Uniqueness
    h2 = s2.shapes.add_textbox(Inches(0.6), Inches(4.55), Inches(6.2), Inches(0.45))
    htf2 = h2.text_frame
    hp2 = htf2.paragraphs[0]
    hp2.text = "❖ Innovation & Uniqueness"
    hp2.font.name = "Arial"
    hp2.font.size = Pt(17)
    hp2.font.bold = True
    hp2.font.color.rgb = PILL_BLUE

    b2 = s2.shapes.add_textbox(Inches(0.6), Inches(5.0), Inches(6.2), Inches(1.9))
    btf2 = b2.text_frame
    btf2.word_wrap = True
    btf2.margin_left = btf2.margin_top = 0
    p = btf2.paragraphs[0]
    p.text = "Foveated adaptive resolution focuses computational resources where they matter most, instead of processing the entire environment at the same resolution."
    p.font.name = "Arial"
    p.font.size = Pt(11.5)
    p.font.italic = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(6)

    p_extra = btf2.add_paragraph()
    p_extra.text = "• Slashing cell memory by 66.2% and processing time to 24.23 ms (>35 FPS)."
    p_extra.font.name = "Arial"
    p_extra.font.size = Pt(11.5)
    p_extra.font.color.rgb = TEXT_MAIN

    # Right: Foveated Concentric Circle Graphic (Matching original visual!)
    # Outer ring (Far field)
    c_out = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(7.5), Inches(1.8), Inches(4.8), Inches(4.8))
    c_out.fill.solid()
    c_out.fill.fore_color.rgb = RGBColor(190, 220, 250)
    c_out.line.color.rgb = RGBColor(100, 160, 230)
    c_out.line.width = Pt(2)

    # Inner ring (Near field)
    c_in = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(8.7), Inches(3.0), Inches(2.4), Inches(2.4))
    c_in.fill.solid()
    c_in.fill.fore_color.rgb = RGBColor(20, 110, 200)
    c_in.line.color.rgb = RGBColor(10, 80, 160)
    c_in.line.width = Pt(2)

    # Center Vehicle Dot / Shape
    v_dot = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.65), Inches(3.95), Inches(0.5), Inches(0.5))
    v_dot.fill.solid()
    v_dot.fill.fore_color.rgb = WHITE
    v_dot.line.fill.background()

    # Title above circle
    c_title = s2.shapes.add_textbox(Inches(7.2), Inches(1.3), Inches(5.4), Inches(0.4))
    ctf = c_title.text_frame
    cp = ctf.paragraphs[0]
    cp.alignment = PP_ALIGN.CENTER
    cp.text = "Foveated 2.5D Semantic Elevation Map"
    cp.font.name = "Arial"
    cp.font.size = Pt(14)
    cp.font.bold = True
    cp.font.color.rgb = BLACK

    # Legend at bottom right
    leg1 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.5), Inches(6.4), Inches(0.35), Inches(0.25))
    leg1.fill.solid()
    leg1.fill.fore_color.rgb = RGBColor(20, 110, 200)
    leg1.line.fill.background()
    t_leg1 = s2.shapes.add_textbox(Inches(7.95), Inches(6.35), Inches(4.8), Inches(0.3))
    t_leg1.text_frame.margin_left = t_leg1.text_frame.margin_top = 0
    t_leg1.text_frame.paragraphs[0].text = "High resolution near the vehicle (near-field: 0.25 m)"
    t_leg1.text_frame.paragraphs[0].font.size = Pt(9.5)
    t_leg1.text_frame.paragraphs[0].font.color.rgb = TEXT_MAIN

    leg2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.5), Inches(6.75), Inches(0.35), Inches(0.25))
    leg2.fill.solid()
    leg2.fill.fore_color.rgb = RGBColor(190, 220, 250)
    leg2.line.fill.background()
    t_leg2 = s2.shapes.add_textbox(Inches(7.95), Inches(6.7), Inches(4.8), Inches(0.3))
    t_leg2.text_frame.margin_left = t_leg2.text_frame.margin_top = 0
    t_leg2.text_frame.paragraphs[0].text = "Lower resolution for distant regions (far-field: 0.75m & 2.0m)"
    t_leg2.text_frame.paragraphs[0].font.size = Pt(9.5)
    t_leg2.text_frame.paragraphs[0].font.color.rgb = TEXT_MAIN

    # ==================== SLIDE 3: Technical Approach ====================
    s3 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s3, "TECHNICAL APPROACH", 3)

    # Left: System Workflow Title
    sw_title = s3.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(5.0), Inches(0.45))
    sw_tf = sw_title.text_frame
    sw_p = sw_tf.paragraphs[0]
    sw_p.text = "System Workflow"
    sw_p.font.name = "Arial"
    sw_p.font.size = Pt(17)
    sw_p.font.bold = True
    sw_p.font.color.rgb = PILL_BLUE

    # Workflow Stack (Vertical Blue Boxes with Arrows)
    wf_boxes = [
        "LiDAR Point Cloud",
        "Preprocessing & Noise Removal",
        "Semantic Understanding",
        "Foveated Adaptive Grid Generation",
        "2.5D Semantic Elevation Map",
        "Real-Time Visualization & Navigation"
    ]
    cur_y = 1.85
    box_h = 0.55
    for i, wftxt in enumerate(wf_boxes):
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(cur_y), Inches(4.6), Inches(box_h))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(20, 110, 200)
        box.line.fill.background()
        btf = box.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = wftxt
        bp.font.name = "Arial"
        bp.font.size = Pt(11)
        bp.font.bold = True
        bp.font.color.rgb = WHITE
        
        cur_y += box_h + 0.08
        if i < len(wf_boxes) - 1:
            arrow = s3.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(2.75), Inches(cur_y - 0.05), Inches(0.3), Inches(0.2))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = RGBColor(100, 150, 210)
            arrow.line.fill.background()
            cur_y += 0.22

    # Right: Production Visual Photo + Technologies
    # BIG PHOTO OF OUR NAVIGATION DASHBOARD!
    dash_path = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\navigation_dashboard.png"
    if os.path.exists(dash_path):
        s3.shapes.add_picture(dash_path, Inches(5.6), Inches(1.35), width=Inches(7.2))

    # Technologies Box below photo
    tech_title = s3.shapes.add_textbox(Inches(5.6), Inches(5.1), Inches(7.2), Inches(0.35))
    tech_title.text_frame.margin_left = tech_title.text_frame.margin_top = 0
    tp = tech_title.text_frame.paragraphs[0]
    tp.text = "Technologies & Core Implementation:"
    tp.font.name = "Arial"
    tp.font.size = Pt(13)
    tp.font.bold = True
    tp.font.color.rgb = PILL_BLUE

    tech_box = s3.shapes.add_textbox(Inches(5.6), Inches(5.5), Inches(7.2), Inches(1.5))
    ttf = tech_box.text_frame
    ttf.word_wrap = True
    ttf.margin_left = ttf.margin_top = 0
    tech_list = [
        "• Python 3.12, NumPy (vectorized hashing), Open3D (point cloud geometry)",
        "• Deep Learning-Based Semantic Segmentation (Ground, Obstacles, Dynamic Vehicles)",
        "• A* Graph Search & Pure Pursuit Kinematics (Catmull-Rom splines, Ackermann model)",
        "• Real-Time Web Dashboard (Flask REST API, 60 FPS Canvas with moving foveation bubble)"
    ]
    for i, t in enumerate(tech_list):
        p = ttf.paragraphs[0] if i == 0 else ttf.add_paragraph()
        p.text = t
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(2)

    # ==================== SLIDE 4: Feasibility and Viability ====================
    s4 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s4, "FEASIBILITY AND VIABILITY", 4)

    def add_blue_pill(slide, text, left, top, width=Inches(2.2), height=Inches(0.45)):
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        pill.fill.solid()
        pill.fill.fore_color.rgb = PILL_BLUE
        pill.line.fill.background()
        ptf = pill.text_frame
        ptf.vertical_anchor = MSO_ANCHOR.MIDDLE
        pp = ptf.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = text
        pp.font.name = "Arial"
        pp.font.size = Pt(12.5)
        pp.font.bold = True
        pp.font.color.rgb = WHITE

    # Left Column: Feasibility & Challenges
    add_blue_pill(s4, "Feasibility", Inches(0.6), Inches(1.3), Inches(2.2))
    f_box = s4.shapes.add_textbox(Inches(0.6), Inches(1.85), Inches(5.8), Inches(2.0))
    ftf = f_box.text_frame
    ftf.word_wrap = True
    ftf.margin_left = ftf.margin_top = 0
    f_bullets = [
        "• Uses widely available LiDAR point cloud datasets and open-source tools",
        "• Python, Open3D, and PyTorch enable rapid prototype development",
        "• Adaptive resolution reduces memory and computational requirements",
        "• Modular pipeline allows components to be developed and tested independently"
    ]
    for i, b in enumerate(f_bullets):
        p = ftf.paragraphs[0] if i == 0 else ftf.add_paragraph()
        p.text = b
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(3)

    add_blue_pill(s4, "Challenges", Inches(0.6), Inches(4.0), Inches(2.2))
    c_box = s4.shapes.add_textbox(Inches(0.6), Inches(4.55), Inches(5.8), Inches(2.4))
    ctf = c_box.text_frame
    ctf.word_wrap = True
    ctf.margin_left = ctf.margin_top = 0
    c_bullets = [
        "• Real-time processing of large LiDAR point clouds at 10–20 Hz",
        "• Accurate semantic classification in unstructured off-road scenes",
        "• Avoiding false-positive obstacles for underpasses & overhead foliage",
        "• Maintaining critical safety detail while reducing distant cell resolution"
    ]
    for i, b in enumerate(c_bullets):
        p = ctf.paragraphs[0] if i == 0 else ctf.add_paragraph()
        p.text = b
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(3)

    # Middle: Mitigation Strategy
    add_blue_pill(s4, "Mitigation Strategy", Inches(6.8), Inches(1.3), Inches(2.6))
    m_box = s4.shapes.add_textbox(Inches(6.8), Inches(1.85), Inches(5.8), Inches(1.6))
    mtf = m_box.text_frame
    mtf.word_wrap = True
    mtf.margin_left = mtf.margin_top = 0
    m_bullets = [
        "• Foveated variable-resolution mapping concentrates power in near-field",
        "• Efficient preprocessing (SOR & RANSAC ground fit) filters dust & noise",
        "• Vertical beam clearance filter enables underpass & tunnel passage",
        "• Validated on 20,672 points in 24.23 ms with 5/5 passing unit tests"
    ]
    for i, b in enumerate(m_bullets):
        p = mtf.paragraphs[0] if i == 0 else mtf.add_paragraph()
        p.text = b
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(3)

    # Right: Autonomous Car Sensor Visual (Matching original visual!)
    if os.path.exists(car_sensor_path):
        s4.shapes.add_picture(car_sensor_path, Inches(6.8), Inches(3.6), width=Inches(5.8))

    # ==================== SLIDE 5: Impact and Benefits ====================
    s5 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s5, "IMPACT AND BENEFITS", 5)

    # Left: Impact & Applications
    add_blue_pill(s5, "Impact", Inches(0.6), Inches(1.3), Inches(2.0))
    i_box = s5.shapes.add_textbox(Inches(0.6), Inches(1.85), Inches(5.0), Inches(1.6))
    itf = i_box.text_frame
    itf.word_wrap = True
    itf.margin_left = itf.margin_top = 0
    i_bullets = [
        "• Supports safer, faster, and reliable autonomous UGV navigation",
        "• Provides sub-meter precision in safety-critical near-field zones",
        "• Active LiDAR penetrates smoke, fog & night darkness for defence",
        "• Enables true real-time terrain and obstacle understanding"
    ]
    for i, b in enumerate(i_bullets):
        p = itf.paragraphs[0] if i == 0 else itf.add_paragraph()
        p.text = b
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(2)

    add_blue_pill(s5, "Applications", Inches(0.6), Inches(3.55), Inches(2.2))
    a_box = s5.shapes.add_textbox(Inches(0.6), Inches(4.1), Inches(5.0), Inches(1.4))
    atf = a_box.text_frame
    atf.word_wrap = True
    atf.margin_left = atf.margin_top = 0
    a_bullets = [
        "• Defence UGVs (border surveillance, minefield reconnaissance, logistics)",
        "• Off-road autonomous vehicles, mobile robots & SAR rovers",
        "• Intelligent driver assistance (ADAS HUD in dense Himalayan fog)"
    ]
    for i, b in enumerate(a_bullets):
        p = atf.paragraphs[0] if i == 0 else atf.add_paragraph()
        p.text = b
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(2)

    # Middle: Benefits
    add_blue_pill(s5, "Benefits", Inches(0.6), Inches(5.3), Inches(2.0))
    ben_box = s5.shapes.add_textbox(Inches(0.6), Inches(5.8), Inches(5.0), Inches(1.3))
    btf = ben_box.text_frame
    btf.word_wrap = True
    btf.margin_left = btf.margin_top = 0
    ben_bullets = [
        "• 66.2% lower memory footprint & 4.8× faster latency (24.23 ms)",
        "• Preserves critical 2.5D height profiles (slope, roughness, Z_max)",
        "• Runs smoothly on low-power edge hardware (NVIDIA Jetson Orin)"
    ]
    for i, b in enumerate(ben_bullets):
        p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
        p.text = b
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(2)

    # Right: PHOTOS OF BEFORE & AFTER POINT CLOUD FILTERING!
    # Visualizing the real impact of our system!
    bef_img = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\before.png"
    aft_img = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\after.png"
    
    t_photo = s5.shapes.add_textbox(Inches(5.9), Inches(1.25), Inches(6.8), Inches(0.35))
    t_photo.text_frame.margin_left = t_photo.text_frame.margin_top = 0
    t_p = t_photo.text_frame.paragraphs[0]
    t_p.text = "Visual Impact: Raw Input vs Cleaned Adaptive Perception"
    t_p.font.name = "Arial"
    t_p.font.size = Pt(13)
    t_p.font.bold = True
    t_p.font.color.rgb = PILL_BLUE

    if os.path.exists(bef_img):
        s5.shapes.add_picture(bef_img, Inches(5.9), Inches(1.7), width=Inches(3.45))
        lbl1 = s5.shapes.add_textbox(Inches(5.9), Inches(4.3), Inches(3.45), Inches(0.3))
        lbl1.text_frame.margin_left = lbl1.text_frame.margin_top = 0
        lbl1.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        lbl1.text_frame.paragraphs[0].text = "Raw LiDAR (20,672 points)"
        lbl1.text_frame.paragraphs[0].font.size = Pt(10)
        lbl1.text_frame.paragraphs[0].font.bold = True
        lbl1.text_frame.paragraphs[0].font.color.rgb = TEXT_MAIN

    if os.path.exists(aft_img):
        s5.shapes.add_picture(aft_img, Inches(9.5), Inches(1.7), width=Inches(3.45))
        lbl2 = s5.shapes.add_textbox(Inches(9.5), Inches(4.3), Inches(3.45), Inches(0.3))
        lbl2.text_frame.margin_left = lbl2.text_frame.margin_top = 0
        lbl2.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        lbl2.text_frame.paragraphs[0].text = "Filtered 2.5D Traversability Map"
        lbl2.text_frame.paragraphs[0].font.size = Pt(10)
        lbl2.text_frame.paragraphs[0].font.bold = True
        lbl2.text_frame.paragraphs[0].font.color.rgb = TEXT_MAIN

    # Real-Time Moving Foveation Result Callout Card
    res_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.9), Inches(4.75), Inches(7.0), Inches(2.2))
    res_card.fill.solid()
    res_card.fill.fore_color.rgb = LIGHT_BLUE_BG
    res_card.line.color.rgb = PILL_BLUE
    res_card.line.width = Pt(1.5)
    rc_tf = res_card.text_frame
    rc_tf.word_wrap = True
    rc_tf.margin_left = rc_tf.margin_top = Inches(0.2)
    rp = rc_tf.paragraphs[0]
    rp.text = "🏆 Production Performance Benchmark on KITTI Velodyne Data:"
    rp.font.name = "Arial"
    rp.font.size = Pt(11)
    rp.font.bold = True
    rp.font.color.rgb = PILL_BLUE
    rp.space_after = Pt(4)

    stats = [
        "• Active Stored Cells: Reduced from 2,888 (uniform) to 976 (adaptive) — 66.2% Cell Reduction",
        "• Mapping Compute Time: Reduced from 115.94 ms to 24.23 ms — 4.8× Latency Speedup",
        "• Traversable Area: 817 safe cells (83.71%) accurately identified without collision risk",
        "• Autonomous Execution: Zero-collision 47-cell A* path tracked smoothly via Pure Pursuit"
    ]
    for s in stats:
        p = rc_tf.add_paragraph()
        p.text = s
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(2)

    # ==================== SLIDE 6: Research and References ====================
    s6 = prs.slides.add_slide(blank_layout)
    add_top_template_header(s6, "RESEARCH AND REFERENCES", 6)

    # Left: Research Areas & References
    r_title1 = s6.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(4.5), Inches(0.4))
    r_title1.text_frame.margin_left = r_title1.text_frame.margin_top = 0
    p = r_title1.text_frame.paragraphs[0]
    p.text = "Research Areas"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = PILL_BLUE

    ra_box = s6.shapes.add_textbox(Inches(0.6), Inches(1.75), Inches(4.5), Inches(1.8))
    ratf = ra_box.text_frame
    ratf.word_wrap = True
    ratf.margin_left = ratf.margin_top = 0
    ra_bullets = [
        "• LiDAR point cloud processing & filtering",
        "• 2.5D and elevation mapping for rough terrain",
        "• Deep semantic segmentation of point clouds",
        "• Autonomous UGV navigation & kinematics",
        "• Adaptive and variable-resolution mapping"
    ]
    for i, b in enumerate(ra_bullets):
        p = ratf.paragraphs[0] if i == 0 else ratf.add_paragraph()
        p.text = b
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(2)

    r_title2 = s6.shapes.add_textbox(Inches(0.6), Inches(3.8), Inches(4.5), Inches(0.4))
    r_title2.text_frame.margin_left = r_title2.text_frame.margin_top = 0
    p = r_title2.text_frame.paragraphs[0]
    p.text = "References"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = PILL_BLUE

    ref_box = s6.shapes.add_textbox(Inches(0.6), Inches(4.25), Inches(4.5), Inches(2.6))
    reftf = ref_box.text_frame
    reftf.word_wrap = True
    reftf.margin_left = reftf.margin_top = 0
    ref_bullets = [
        "• KITTI Vision Benchmark Suite (Velodyne HDL-64E)",
        "• ETH Zurich Robot-Centric Elevation Mapping (P. Fankhauser)",
        "• CMU Robotics Institute Pure Pursuit Kinematics (R. C. Coulter)",
        "• Open3D & PyTorch Deep Learning Documentation",
        "• Research literature on LiDAR semantic segmentation & autonomous foveated navigation"
    ]
    for i, b in enumerate(ref_bullets):
        p = reftf.paragraphs[0] if i == 0 else reftf.add_paragraph()
        p.text = b
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(3)

    # Right: Horizontal Numbered Research Pipeline Graphic (Original Visual!)
    # "LiDAR 2.5 RESEARCH PIPELINE"
    if os.path.exists(pipeline_img_path):
        pipe_title = s6.shapes.add_textbox(Inches(5.4), Inches(1.3), Inches(7.5), Inches(0.4))
        pipe_title.text_frame.margin_left = pipe_title.text_frame.margin_top = 0
        pp = pipe_title.text_frame.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = "LiDAR 2.5 RESEARCH PIPELINE"
        pp.font.name = "Arial"
        pp.font.size = Pt(16)
        pp.font.bold = True
        pp.font.color.rgb = BLACK

        s6.shapes.add_picture(pipeline_img_path, Inches(5.3), Inches(1.85), width=Inches(7.6))

    # Real-Time Simulator & GitHub Deliverable Box below graphic
    deliv_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.3), Inches(5.1), Inches(7.6), Inches(1.85))
    deliv_box.fill.solid()
    deliv_box.fill.fore_color.rgb = LIGHT_BLUE_BG
    deliv_box.line.color.rgb = PILL_BLUE
    deliv_box.line.width = Pt(1.5)
    dtf = deliv_box.text_frame
    dtf.word_wrap = True
    dtf.margin_left = dtf.margin_top = Inches(0.15)
    p = dtf.paragraphs[0]
    p.text = "💻 Verified Project Deliverables & Repository:"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PILL_BLUE
    p.space_after = Pt(3)

    d_items = [
        "• Working 60 FPS HTML5 / Flask Localhost Simulator with moving-car foveation",
        "• Automated Unit Test Suite (5/5 tests passing in 4.0s verifying all modules)",
        "• Open Source GitHub Repository: github.com/AbhayVerma628/SIH26053_Lidar",
        "• Complete 5-panel Matplotlib dashboard, 10 Hz vehicle telemetry log CSV & benchmarks"
    ]
    for d in d_items:
        p = dtf.add_paragraph()
        p.text = d
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(2)

    # Save presentation
    out_pptx1 = r"C:\Users\HP\Desktop\SIH26053_Lidar\docs\SIH26053_TeraPulse_Official_Presentation.pptx"
    out_pptx2 = r"C:\Users\HP\Desktop\SIH26053_TeraPulse_Official_Presentation.pptx"
    prs.save(out_pptx1)
    prs.save(out_pptx2)
    print("SUCCESS: Original Template Recreated with Photos & Esha Verma!")
    print("Saved PPTX to:", out_pptx1)
    print("Saved PPTX to:", out_pptx2)

if __name__ == "__main__":
    build_presentation()
