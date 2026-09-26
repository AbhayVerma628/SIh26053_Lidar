import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_perfect_sih_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Exact palette sampled directly from the user's original presentation
    NAVY_TITLE = RGBColor(30, 39, 96)       # #1e2760 (Slide 1 header & highlighted boxes)
    PILL_BLUE = RGBColor(0, 111, 192)       # #006fc0 (Official Blue for pills, footer, buttons)
    HEADING_BLUE = RGBColor(31, 72, 124)    # #1f487c (Deep blue for underlined section headings)
    BANNER_GRAY = RGBColor(191, 192, 191)   # #bfc0bf (Original gray title banner box)
    BORDER_PURPLE = RGBColor(128, 99, 161)  # #8063a1 (Original TERA PULSE oval border)
    DIVIDER_GRAY = RGBColor(195, 195, 195)  # Subtle column divider
    BLACK = RGBColor(0, 0, 0)               # Pure black for titles and bold lead-ins
    TEXT_DARK = RGBColor(35, 35, 35)        # Dark charcoal for regular text
    WHITE = RGBColor(255, 255, 255)

    blank_layout = prs.slide_layouts[6]
    img_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "assets")
    sih_logo_path = os.path.join(img_dir, "sih_logo.png")
    brain_img_path = os.path.join(img_dir, "sih_brain.png")
    car_sensor_path = os.path.join(img_dir, "car_lidar_sensor.png")
    pipeline_img_path = os.path.join(img_dir, "colored_research_pipeline.jpg")
    dash_img_path = r"C:\Users\HP\Desktop\SIH26053_Lidar\outputs\navigation_dashboard.png"

    # Helper: Master Header and Footer for Slides 2-6 (Exact original template)
    def add_master_header_footer(slide, title_text, slide_num, is_two_line=False):
        # 1. Oval TERA PULSE logo on top-left (Exact original styling)
        oval = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.4), Inches(0.22), Inches(1.4), Inches(0.85))
        oval.fill.solid()
        oval.fill.fore_color.rgb = WHITE
        oval.line.color.rgb = BORDER_PURPLE
        oval.line.width = Pt(1.5)
        otf = oval.text_frame
        otf.word_wrap = True
        otf.margin_left = otf.margin_top = otf.margin_right = otf.margin_bottom = 0
        op = otf.paragraphs[0]
        op.alignment = PP_ALIGN.CENTER
        op.text = "TERA\nPULSE"
        op.font.name = "Arial"
        op.font.size = Pt(12)
        op.font.bold = True
        op.font.color.rgb = BLACK

        # 2. Gray Title Banner (Exact original template)
        banner_w = Inches(8.3)
        banner_h = Inches(0.9) if is_two_line else Inches(0.72)
        banner_top = Inches(0.2) if is_two_line else Inches(0.28)
        banner_left = Inches(2.35)

        banner_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, banner_left, banner_top, banner_w, banner_h)
        banner_bg.fill.solid()
        banner_bg.fill.fore_color.rgb = BANNER_GRAY
        banner_bg.line.fill.background()

        btf = banner_bg.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        btf.word_wrap = True
        btf.margin_left = btf.margin_right = btf.margin_top = btf.margin_bottom = 0
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = title_text
        bp.font.name = "Arial" if is_two_line else "Times New Roman"
        bp.font.size = Pt(20) if is_two_line else Pt(25)
        bp.font.bold = True
        bp.font.color.rgb = BLACK

        # 3. SIH 2026 Logo on top-right
        if os.path.exists(sih_logo_path):
            slide.shapes.add_picture(sih_logo_path, Inches(11.2), Inches(0.18), width=Inches(1.65))

        # 4. Footer Blue Bar
        footer = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.15), Inches(13.333), Inches(0.35))
        footer.fill.solid()
        footer.fill.fore_color.rgb = PILL_BLUE
        footer.line.fill.background()
        
        ftf = footer.text_frame
        ftf.vertical_anchor = MSO_ANCHOR.MIDDLE
        ftf.margin_left = Inches(0.6)
        ftf.margin_right = Inches(0.6)
        fp = ftf.paragraphs[0]
        fp.alignment = PP_ALIGN.CENTER
        fp.text = "@SIH Idea submission- Template"
        fp.font.name = "Arial"
        fp.font.size = Pt(11)
        fp.font.color.rgb = WHITE

        # Slide number on far right
        num_box = slide.shapes.add_textbox(Inches(12.3), Inches(7.16), Inches(0.6), Inches(0.32))
        np = num_box.text_frame.paragraphs[0]
        np.alignment = PP_ALIGN.RIGHT
        np.text = str(slide_num)
        np.font.name = "Arial"
        np.font.size = Pt(11)
        np.font.bold = True
        np.font.color.rgb = WHITE

    # Helper: Blue pill header with underlined white text (Original template element)
    def add_blue_pill(slide, text, left, top, width=Inches(2.3), height=Inches(0.5)):
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
        pp.font.size = Pt(15)
        pp.font.bold = True
        pp.font.underline = True
        pp.font.color.rgb = WHITE
        return pill

    # Helper: Underlined section heading (Original template element)
    def add_underlined_heading(slide, text, left, top, width=Inches(5.0)):
        box = slide.shapes.add_textbox(left, top, width, Inches(0.45))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = 0
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = "Arial"
        p.font.size = Pt(19)
        p.font.bold = True
        p.font.underline = True
        p.font.color.rgb = HEADING_BLUE
        return box

    # ==================== SLIDE 1: Title & Team Details ====================
    s1 = prs.slides.add_slide(blank_layout)

    # Top SIH Header (Times New Roman, Navy Blue)
    top_txt = s1.shapes.add_textbox(Inches(1.0), Inches(0.32), Inches(10.0), Inches(0.55))
    ttf = top_txt.text_frame
    tp = ttf.paragraphs[0]
    tp.alignment = PP_ALIGN.CENTER
    tp.text = "SMART INDIA HACKATHON 2026"
    tp.font.name = "Times New Roman"
    tp.font.size = Pt(28)
    tp.font.bold = True
    tp.font.color.rgb = NAVY_TITLE

    # Presentation Title
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(10.5), Inches(1.15))
    ttf2 = t_box.text_frame
    ttf2.word_wrap = True
    tp2 = ttf2.paragraphs[0]
    tp2.alignment = PP_ALIGN.CENTER
    tp2.text = "Adaptive Foveated 2.5D Semantic Mapping for\nAutonomous Navigation"
    tp2.font.name = "Arial"
    tp2.font.size = Pt(28)
    tp2.font.bold = True
    tp2.font.color.rgb = BLACK

    # SIH Logo on top right
    if os.path.exists(sih_logo_path):
        s1.shapes.add_picture(sih_logo_path, Inches(11.2), Inches(0.18), width=Inches(1.65))

    # Left: Details with large 14pt font, bold labels, including Member 6 (Esha Verma)
    details_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.35), Inches(7.2), Inches(4.8))
    dtf = details_box.text_frame
    dtf.word_wrap = True
    dtf.margin_left = dtf.margin_top = 0

    d_items = [
        ("• Problem Statement ID –", " 26053"),
        ("• Problem Statement Title –", " Adaptive Foveated 2.5D Semantic Mapping from LiDAR Point Clouds for Autonomous Navigation"),
        ("• Theme –", " Smart Vehicles"),
        ("• PS Category –", " Software"),
        ("• Team ID –", " 137735"),
        ("• Team Name –", " TeraPulse"),
        ("• Team Members –", " Abhay Verma (Team Leader), Lokendra Singh,\nYashvardhan Jain, Chetan Meena, Sachin Chaubey, Esha Verma"),
        ("• Institute –", " Indian Institute of Information Technology Bhopal")
    ]
    for i, (label, val) in enumerate(d_items):
        p = dtf.paragraphs[0] if i == 0 else dtf.add_paragraph()
        p.space_after = Pt(8)
        r_lbl = p.add_run()
        r_lbl.text = label
        r_lbl.font.name = "Arial"
        r_lbl.font.size = Pt(13.8)
        r_lbl.font.bold = True
        r_lbl.font.color.rgb = BLACK

        r_val = p.add_run()
        r_val.text = val
        r_val.font.name = "Arial"
        r_val.font.size = Pt(13.8)
        r_val.font.bold = False
        r_val.font.color.rgb = TEXT_DARK

    # Right: Official SIH Brain Bulb Image
    if os.path.exists(brain_img_path):
        s1.shapes.add_picture(brain_img_path, Inches(7.8), Inches(2.2), width=Inches(5.2))

    # ==================== SLIDE 2: Proposed Solution ====================
    s2 = prs.slides.add_slide(blank_layout)
    add_master_header_footer(s2, "Adaptive Foveated 2.5D Semantic Mapping\nfor Autonomous Navigation", 2, is_two_line=True)

    # Left: Proposed Solution (Underlined Heading)
    add_underlined_heading(s2, "❖ Proposed Solution", Inches(0.6), Inches(1.3), Inches(6.6))

    b1 = s2.shapes.add_textbox(Inches(0.6), Inches(1.85), Inches(6.6), Inches(2.8))
    btf = b1.text_frame
    btf.word_wrap = True
    btf.margin_left = btf.margin_top = 0

    sol_bullets = [
        ("• 2.5D Semantic Elevation Map: ", "Generated directly from raw LiDAR point clouds."),
        ("• High-Precision Near Field: ", "Fine resolution (0.25 m) near vehicle for critical steering."),
        ("• Bandwidth-Saving Far Field: ", "Lower resolution (0.75 m & 2.0 m) for distant regions — cuts unnecessary compute."),
        ("• Elevation & Slope Awareness: ", "Preserves terrain slopes, curbs & ditches without full 3D voxels."),
        ("• Real-Time Terrain Intelligence: ", "Identifies drivable ground, static obstacles & dynamic objects."),
        ("• Autonomous Navigation Ready: ", "Enables instant A* path planning & Pure Pursuit motion control.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(sol_bullets):
        p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
        p.space_after = Pt(4)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(12.5)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(12.5)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Left: Innovation & Uniqueness
    add_underlined_heading(s2, "❖ Innovation & Uniqueness", Inches(0.6), Inches(4.8), Inches(6.6))

    b2 = s2.shapes.add_textbox(Inches(0.6), Inches(5.35), Inches(6.6), Inches(1.6))
    btf2 = b2.text_frame
    btf2.word_wrap = True
    btf2.margin_left = btf2.margin_top = 0

    p_in = btf2.paragraphs[0]
    p_in.space_after = Pt(5)
    r1 = p_in.add_run()
    r1.text = "Foveated adaptive resolution "
    r1.font.name = "Arial"
    r1.font.size = Pt(12.5)
    r1.font.bold = True
    r1.font.color.rgb = BLACK

    r2 = p_in.add_run()
    r2.text = "focuses computational resources where they matter most, instead of processing the entire environment at the same resolution."
    r2.font.name = "Arial"
    r2.font.size = Pt(12.5)
    r2.font.italic = True
    r2.font.color.rgb = TEXT_DARK

    p_imp = btf2.add_paragraph()
    r_ex1 = p_imp.add_run()
    r_ex1.text = "• Measurable Impact: "
    r_ex1.font.name = "Arial"
    r_ex1.font.size = Pt(12.5)
    r_ex1.font.bold = True
    r_ex1.font.color.rgb = BLACK

    r_ex2 = p_imp.add_run()
    r_ex2.text = "Slashes cell memory by 66.2% and cuts processing latency to 24.23 ms (>35 FPS)."
    r_ex2.font.name = "Arial"
    r_ex2.font.size = Pt(12.5)
    r_ex2.font.bold = False
    r_ex2.font.color.rgb = TEXT_DARK

    # Right: Foveated Concentric Circle Graphic (Original Diagram Layout)
    c_title = s2.shapes.add_textbox(Inches(7.4), Inches(1.3), Inches(5.4), Inches(0.4))
    cp = c_title.text_frame.paragraphs[0]
    cp.alignment = PP_ALIGN.CENTER
    cp.text = "Foveated 2.5D Semantic Elevation Map"
    cp.font.name = "Arial"
    cp.font.size = Pt(16)
    cp.font.bold = True
    cp.font.color.rgb = BLACK

    # Outer Circle (diameter 4.2", centered at x=10.1", y=3.85")
    c_out = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(8.0), Inches(1.75), Inches(4.2), Inches(4.2))
    c_out.fill.solid()
    c_out.fill.fore_color.rgb = RGBColor(190, 220, 250)
    c_out.line.color.rgb = RGBColor(100, 160, 230)
    c_out.line.width = Pt(2.0)

    # Inner Circle (diameter 2.1", centered at x=10.1", y=3.85")
    c_in = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.05), Inches(2.8), Inches(2.1), Inches(2.1))
    c_in.fill.solid()
    c_in.fill.fore_color.rgb = PILL_BLUE
    c_in.line.color.rgb = RGBColor(10, 80, 160)
    c_in.line.width = Pt(2.0)

    # Center Vehicle Rectangle (matching original diagram)
    v_car = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.85), Inches(3.7), Inches(0.5), Inches(0.3))
    v_car.fill.solid()
    v_car.fill.fore_color.rgb = NAVY_TITLE
    v_car.line.fill.background()

    # Scatter dots around vehicle (white in inner, blue in outer)
    dot_coords = [
        # Inner ring dots (white)
        (9.5, 3.2, WHITE), (10.6, 3.2, WHITE), (9.35, 3.8, WHITE), (10.75, 3.8, WHITE),
        (9.6, 4.4, WHITE), (10.5, 4.4, WHITE), (10.1, 3.1, WHITE), (10.1, 4.5, WHITE),
        # Outer ring dots (blue)
        (8.5, 2.3, PILL_BLUE), (11.6, 2.3, PILL_BLUE), (8.3, 3.8, PILL_BLUE),
        (11.8, 3.8, PILL_BLUE), (8.6, 5.2, PILL_BLUE), (11.5, 5.2, PILL_BLUE),
        (10.1, 2.05, PILL_BLUE), (10.1, 5.6, PILL_BLUE)
    ]
    for dx, dy, col in dot_coords:
        d = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(dx), Inches(dy), Inches(0.12), Inches(0.12))
        d.fill.solid()
        d.fill.fore_color.rgb = col
        d.line.fill.background()

    # Legend cleanly positioned below circle (No overlap!)
    leg1 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.7), Inches(6.22), Inches(0.35), Inches(0.24))
    leg1.fill.solid()
    leg1.fill.fore_color.rgb = PILL_BLUE
    leg1.line.fill.background()
    t_leg1 = s2.shapes.add_textbox(Inches(8.15), Inches(6.19), Inches(4.8), Inches(0.3))
    t_leg1.text_frame.margin_left = t_leg1.text_frame.margin_top = 0
    p = t_leg1.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "High resolution near the vehicle "
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = BLACK
    r2 = p.add_run()
    r2.text = "(near-field: 0.25 m bubble)"
    r2.font.size = Pt(11)
    r2.font.color.rgb = TEXT_DARK

    leg2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.7), Inches(6.58), Inches(0.35), Inches(0.24))
    leg2.fill.solid()
    leg2.fill.fore_color.rgb = RGBColor(190, 220, 250)
    leg2.line.fill.background()
    t_leg2 = s2.shapes.add_textbox(Inches(8.15), Inches(6.55), Inches(4.8), Inches(0.3))
    t_leg2.text_frame.margin_left = t_leg2.text_frame.margin_top = 0
    p = t_leg2.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Lower resolution for distant regions "
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = BLACK
    r2 = p.add_run()
    r2.text = "(far-field: 0.75m & 2.0m)"
    r2.font.size = Pt(11)
    r2.font.color.rgb = TEXT_DARK

    # ==================== SLIDE 3: Technical Approach ====================
    s3 = prs.slides.add_slide(blank_layout)
    add_master_header_footer(s3, "TECHNICAL APPROACH", 3)

    # Left: System Workflow Flowchart (Exact layout from user's template)
    add_underlined_heading(s3, "System Workflow", Inches(0.6), Inches(1.3), Inches(4.6))

    wf_boxes = [
        ("LiDAR Point Cloud", PILL_BLUE, False),
        ("Preprocessing & Noise Removal", PILL_BLUE, False),
        ("Semantic Understanding", PILL_BLUE, False),
        ("Foveated Adaptive Grid Generation", PILL_BLUE, False),
        ("2.5D Semantic Elevation Map", NAVY_TITLE, True),   # Highlighted dark navy box in original!
        ("Real-Time Visualization & Navigation", PILL_BLUE, False)
    ]
    cur_y = 1.85
    box_h = 0.54
    for i, (wftxt, bg_col, is_highlight) in enumerate(wf_boxes):
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(cur_y), Inches(4.6), Inches(box_h))
        box.fill.solid()
        box.fill.fore_color.rgb = bg_col
        box.line.fill.background()
        btf = box.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = wftxt
        bp.font.name = "Arial"
        bp.font.size = Pt(12 if is_highlight else 11.5)
        bp.font.bold = True
        bp.font.color.rgb = WHITE
        
        cur_y += box_h + 0.06
        if i < len(wf_boxes) - 1:
            arrow = s3.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(2.78), Inches(cur_y - 0.04), Inches(0.24), Inches(0.18))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = NAVY_TITLE
            arrow.line.fill.background()
            cur_y += 0.20

    # Right: Technologies Heading (Underlined)
    add_underlined_heading(s3, "Technologies & Implementation", Inches(5.6), Inches(1.3), Inches(7.1))

    tech_box = s3.shapes.add_textbox(Inches(5.6), Inches(1.8), Inches(7.1), Inches(1.4))
    ttf = tech_box.text_frame
    ttf.word_wrap = True
    ttf.margin_left = ttf.margin_top = 0
    tech_list = [
        ("• Python, Open3D & NumPy: ", "Point cloud preprocessing, voxelization & spatial hashing."),
        ("• Deep Learning: ", "Semantic terrain classification (Ground, Static Obstacles, Dynamic Vehicles)."),
        ("• A* Search & Pure Pursuit: ", "Collision-free path planning & smooth 10 Hz vehicle steering kinematics."),
        ("• Interactive Web Dashboard: ", "Flask REST API, 60 FPS HTML5 Canvas with moving foveation bubble.")
    ]
    for i, (tag, desc) in enumerate(tech_list):
        p = ttf.paragraphs[0] if i == 0 else ttf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = tag
        r1.font.name = "Arial"
        r1.font.size = Pt(11.5)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Right Bottom: High-Resolution Real Dashboard Picture (Cleanly placed, ZERO overlap with footer!)
    # Height = 3.4", width = 3.4 * 1.655 = 5.63". Placed at x=6.35", y=3.45" -> bottom at 6.85" (well above 7.15" footer)
    if os.path.exists(dash_img_path):
        dash_pic = s3.shapes.add_picture(dash_img_path, Inches(6.2), Inches(3.45), height=Inches(3.4))
        dash_pic.line.color.rgb = BANNER_GRAY
        dash_pic.line.width = Pt(1.0)

    # ==================== SLIDE 4: Feasibility and Viability ====================
    s4 = prs.slides.add_slide(blank_layout)
    add_master_header_footer(s4, "FEASIBILITY AND VIABILITY", 4)

    # Left: Feasibility (Original Blue Pill)
    add_blue_pill(s4, "Feasibility", Inches(0.6), Inches(1.25), Inches(2.2))
    f_box = s4.shapes.add_textbox(Inches(0.6), Inches(1.85), Inches(5.6), Inches(1.9))
    ftf = f_box.text_frame
    ftf.word_wrap = True
    ftf.margin_left = ftf.margin_top = 0
    f_bullets = [
        ("• Standard Datasets: ", "Uses widely available LiDAR point cloud datasets & open-source tools."),
        ("• Rapid Development: ", "Python, Open3D, and PyTorch enable agile modular prototyping."),
        ("• Low-Power Efficiency: ", "Adaptive resolution drastically reduces memory & compute requirements."),
        ("• Modular Pipeline: ", "Components tested independently with 5/5 automated unit tests passing.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(f_bullets):
        p = ftf.paragraphs[0] if i == 0 else ftf.add_paragraph()
        p.space_after = Pt(3)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(11.5)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Left: Challenges (Original Blue Pill)
    add_blue_pill(s4, "Challenges", Inches(0.6), Inches(3.95), Inches(2.2))
    c_box = s4.shapes.add_textbox(Inches(0.6), Inches(4.55), Inches(5.6), Inches(2.3))
    ctf = c_box.text_frame
    ctf.word_wrap = True
    ctf.margin_left = ctf.margin_top = 0
    c_bullets = [
        ("• Heavy Data Stream: ", "Real-time processing of large LiDAR point clouds at 10–20 Hz."),
        ("• Off-Road Accuracy: ", "Accurate semantic classification in unstructured off-road scenes."),
        ("• Underpasses & Tunnels: ", "Avoiding false-positive obstacle detection for bridge ceilings."),
        ("• Detail Retention: ", "Maintaining critical safety clearance while reducing distant resolution.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(c_bullets):
        p = ctf.paragraphs[0] if i == 0 else ctf.add_paragraph()
        p.space_after = Pt(3)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(11.5)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Vertical Column Divider Line (Matching original template)
    div_line4 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.45), Inches(1.3), Inches(0.02), Inches(5.6))
    div_line4.fill.solid()
    div_line4.fill.fore_color.rgb = DIVIDER_GRAY
    div_line4.line.fill.background()

    # Right: Mitigation Strategy (Original Blue Pill)
    add_blue_pill(s4, "Mitigation Strategy", Inches(6.75), Inches(1.25), Inches(2.7))
    m_box = s4.shapes.add_textbox(Inches(6.75), Inches(1.85), Inches(6.0), Inches(1.7))
    mtf = m_box.text_frame
    mtf.word_wrap = True
    mtf.margin_left = mtf.margin_top = 0
    m_bullets = [
        ("• Foveated Attention: ", "Variable-resolution mapping concentrates compute in near-field (24.23 ms)."),
        ("• SOR & RANSAC Fit: ", "Statistical Outlier Removal & ground fit eliminate dust & sensor reflections."),
        ("• Vertical Clearance: ", "Clearance filter ignores points >2.2 m, enabling safe tunnel traversal."),
        ("• Proven Benchmark: ", "Benchmarked on 20,672 points at >35 FPS with zero crash failures.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(m_bullets):
        p = mtf.paragraphs[0] if i == 0 else mtf.add_paragraph()
        p.space_after = Pt(3)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(11.5)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Right Bottom: Autonomous Car Sensor Perception Visual (Clean style inside screen bounds)
    if os.path.exists(car_sensor_path):
        s4.shapes.add_picture(car_sensor_path, Inches(6.9), Inches(3.75), width=Inches(5.5))

    # ==================== SLIDE 5: Impact and Benefits ====================
    s5 = prs.slides.add_slide(blank_layout)
    add_master_header_footer(s5, "IMPACT AND BENEFITS", 5)

    # Left: Impact (Original Blue Pill)
    add_blue_pill(s5, "Impact", Inches(0.6), Inches(1.25), Inches(2.1))
    i_box = s5.shapes.add_textbox(Inches(0.6), Inches(1.85), Inches(4.8), Inches(1.6))
    itf = i_box.text_frame
    itf.word_wrap = True
    itf.margin_left = itf.margin_top = 0
    i_bullets = [
        ("• Tactical UGV Navigation: ", "Supports safer and faster autonomous military navigation."),
        ("• Critical Near-Field Safety: ", "Sub-meter precision in safety-critical perimeter around vehicle."),
        ("• Zero-Visibility Ops: ", "Active LiDAR penetrates smoke, dust, fog & battlefield darkness."),
        ("• Terrain Intelligence: ", "Real-time elevation slope, ditches & surface roughness understanding.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(i_bullets):
        p = itf.paragraphs[0] if i == 0 else itf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Left: Applications (Original Blue Pill)
    add_blue_pill(s5, "Applications", Inches(0.6), Inches(3.8), Inches(2.3))
    a_box = s5.shapes.add_textbox(Inches(0.6), Inches(4.4), Inches(4.8), Inches(2.2))
    atf = a_box.text_frame
    atf.word_wrap = True
    atf.margin_left = atf.margin_top = 0
    a_bullets = [
        ("• Defence & Tactical UGVs: ", "Logistics convoys, perimeter patrols, scout rovers & minefield recon."),
        ("• Off-Road Autonomous Rovers: ", "Search-and-rescue rovers in disaster zones, agricultural robotics."),
        ("• Driver Assistance (ADAS): ", "Intelligent terrain HUD and active collision prevention in dense fog.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(a_bullets):
        p = atf.paragraphs[0] if i == 0 else atf.add_paragraph()
        p.space_after = Pt(3)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Vertical Column Divider Line
    div_line5 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.6), Inches(1.3), Inches(0.02), Inches(5.6))
    div_line5.fill.solid()
    div_line5.fill.fore_color.rgb = DIVIDER_GRAY
    div_line5.line.fill.background()

    # Right: Benefits (Original Blue Pill)
    add_blue_pill(s5, "Benefits", Inches(5.9), Inches(1.25), Inches(2.1))
    ben_box = s5.shapes.add_textbox(Inches(5.9), Inches(1.85), Inches(6.8), Inches(1.8))
    btf = ben_box.text_frame
    btf.word_wrap = True
    btf.margin_left = btf.margin_top = 0
    ben_bullets = [
        ("• 66.2% Memory Reduction: ", "Stored active cells drop from 2,888 to 976 via foveated concentration."),
        ("• 4.8× Faster Latency: ", "Down from 115.94 ms to 24.23 ms — exceeds 35 FPS real-time vehicle requirement."),
        ("• Full 2.5D Elevation Profile: ", "Preserves critical ground slope, curbs & height without voxel clutter."),
        ("• Verified Path Traversability: ", "817 safe corridor cells verified with smooth 10 Hz Pure Pursuit steering.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(ben_bullets):
        p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Right: Clean Student Benchmark Table (Replaces artificial AI cards!)
    table_shape = s5.shapes.add_table(5, 4, Inches(5.9), Inches(4.0), Inches(6.8), Inches(2.75))
    table = table_shape.table
    table.columns[0].width = Inches(1.9)
    table.columns[1].width = Inches(1.5)
    table.columns[2].width = Inches(1.7)
    table.columns[3].width = Inches(1.7)

    headers = ["Evaluation Metric", "Uniform Grid", "TeraPulse Foveated", "Practical Advantage"]
    for col_idx, htext in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PILL_BLUE
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = htext
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE

    row_data = [
        ("Active Stored Cells", "2,888 cells", "976 cells", "66.2% RAM Saved"),
        ("Compute Latency", "115.94 ms (8.6 FPS)", "24.23 ms (>35 FPS)", "4.8× Faster Control"),
        ("Hardware Footprint", "High-End Desktop GPU", "Embedded CPU / Jetson", "Low Power UGV Edge"),
        ("Path Generation", "Delayed Waypoints", "10 Hz Dynamic Telemetry", "Safe Agile Steering")
    ]
    for row_idx, rvals in enumerate(row_data, start=1):
        bg = RGBColor(245, 248, 252) if row_idx % 2 == 1 else WHITE
        for col_idx, val in enumerate(rvals):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if col_idx == 0 else PP_ALIGN.CENTER
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(10)
            p.font.bold = (col_idx == 2 or col_idx == 3)
            p.font.color.rgb = PILL_BLUE if (col_idx == 2 or col_idx == 3) else BLACK

    # ==================== SLIDE 6: Research and References ====================
    s6 = prs.slides.add_slide(blank_layout)
    add_master_header_footer(s6, "RESEARCH AND REFERENCES", 6)

    # Left: Research Areas (Underlined Heading)
    add_underlined_heading(s6, "Research Areas", Inches(0.6), Inches(1.3), Inches(4.8))

    ra_box = s6.shapes.add_textbox(Inches(0.6), Inches(1.8), Inches(4.8), Inches(1.8))
    ratf = ra_box.text_frame
    ratf.word_wrap = True
    ratf.margin_left = ratf.margin_top = 0
    ra_bullets = [
        ("• LiDAR Point Cloud Processing: ", "Statistical outlier removal & RANSAC ground plane fit."),
        ("• 2.5D Elevation Mapping: ", "Robot-centric height & slope mapping for rough terrain."),
        ("• Semantic Segmentation: ", "Deep learning segmentation of drivable vs obstacle cells."),
        ("• Autonomous Navigation: ", "A* heuristic planning & Pure Pursuit vehicle kinematics."),
        ("• Adaptive Spatial Hashing: ", "Foveated variable-resolution concentric indexing.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(ra_bullets):
        p = ratf.paragraphs[0] if i == 0 else ratf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Left: References (Underlined Heading)
    add_underlined_heading(s6, "References", Inches(0.6), Inches(3.8), Inches(4.8))

    ref_box = s6.shapes.add_textbox(Inches(0.6), Inches(4.3), Inches(4.8), Inches(2.6))
    reftf = ref_box.text_frame
    reftf.word_wrap = True
    reftf.margin_left = reftf.margin_top = 0
    ref_bullets = [
        ("• KITTI Vision Suite: ", "Geiger et al., Velodyne HDL-64E LiDAR benchmark."),
        ("• ETH Zurich Mapping: ", "P. Fankhauser et al. (IEEE IROS), Robot-Centric Elevation Mapping."),
        ("• CMU Pure Pursuit: ", "R. C. Coulter (Carnegie Mellon), Pure Pursuit Path Tracking."),
        ("• Point Cloud ML: ", "Q. Hu et al. (CVPR), RandLA-Net Point Cloud Segmentation."),
        ("• Open-Source Tools: ", "Open3D, PyTorch, NumPy, Flask REST APIs.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(ref_bullets):
        p = reftf.paragraphs[0] if i == 0 else reftf.add_paragraph()
        p.space_after = Pt(3)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Right: Horizontal Numbered Research Pipeline Flowchart (Zero Overlap!)
    # Note: image itself already contains title "LiDAR 2.5 RESEARCH PIPELINE" at the top!
    if os.path.exists(pipeline_img_path):
        s6.shapes.add_picture(pipeline_img_path, Inches(5.7), Inches(1.3), width=Inches(6.9))

    # Clean Deliverables Section below the pipeline image (starting at y=5.25", zero overlap!)
    add_underlined_heading(s6, "Project Deliverables & Repository", Inches(5.7), Inches(5.2), Inches(6.9))

    deliv_box = s6.shapes.add_textbox(Inches(5.7), Inches(5.65), Inches(6.9), Inches(1.4))
    dtf = deliv_box.text_frame
    dtf.word_wrap = True
    dtf.margin_left = dtf.margin_top = 0

    d_items = [
        ("• Interactive Web Simulator: ", "Flask REST API + 60 FPS HTML5 Canvas with live vehicle foveation."),
        ("• Automated Test Suite: ", "5/5 unit tests (tests/test_pipeline.py) passing in 4.0s."),
        ("• GitHub Repository: ", "github.com/AbhayVerma628/SIH26053_Lidar (Open Source MIT License)."),
        ("• Telemetry & Artifacts: ", "5-panel dashboard, 10 Hz vehicle telemetry CSV & planned A* waypoints.")
    ]
    for i, (bold_txt, reg_txt) in enumerate(d_items):
        p = dtf.paragraphs[0] if i == 0 else dtf.add_paragraph()
        p.space_after = Pt(2)
        r1 = p.add_run()
        r1.text = bold_txt
        r1.font.name = "Arial"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = BLACK

        r2 = p.add_run()
        r2.text = reg_txt
        r2.font.name = "Arial"
        r2.font.size = Pt(10.5)
        r2.font.bold = False
        r2.font.color.rgb = TEXT_DARK

    # Save presentation to both paths
    out_pptx1 = r"C:\Users\HP\Desktop\SIH26053_Lidar\docs\SIH26053_TeraPulse_Official_Presentation.pptx"
    out_pptx2 = r"C:\Users\HP\Desktop\SIH26053_TeraPulse_Official_Presentation.pptx"
    prs.save(out_pptx1)
    prs.save(out_pptx2)
    print("SUCCESS: Perfect authentic human-styled SIH PPTX built successfully!")

if __name__ == "__main__":
    build_perfect_sih_presentation()
