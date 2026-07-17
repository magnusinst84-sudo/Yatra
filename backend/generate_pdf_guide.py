"""
generate_pdf_guide.py
---------------------
Compiles a polished, beautifully styled PDF testing guide for the Yatra RAG + World State
pipeline using ReportLab. Includes step-by-step curls, validation criteria, and how
to verify image prompts for B1/B2 integration.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def build_pdf(filename="RAG_Walkthrough_Testing_Guide.pdf"):
    # Target 0.75-inch margins
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    NAVY = colors.HexColor('#0F172A')
    SLATE = colors.HexColor('#475569')
    LIGHT_BG = colors.HexColor('#F8FAFC')
    ACCENT = colors.HexColor('#2563EB')
    BORDER_COLOR = colors.HexColor('#E2E8F0')
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=NAVY,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=SLATE,
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=NAVY,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=NAVY,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=0
    )

    def make_code_panel(text):
        p = Paragraph(text.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style)
        t = Table([[p]], colWidths=[doc.width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        return t

    story = []
    
    # -------------------------------------------------------------------------
    # COVER / HEADER SECTION
    # -------------------------------------------------------------------------
    story.append(Paragraph("YATRA — AI Historical Walkthroughs", title_style))
    story.append(Paragraph("<b>RAG + World State Integration Testing Guide</b><br/>"
                           "A reference document for testing retrieval accuracy, narrative generation, "
                           "and image prompts.", subtitle_style))
    story.append(Spacer(1, 10))
    
    # -------------------------------------------------------------------------
    # SECTION 1: ARCHITECTURE OVERVIEW
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. System Architecture Overview", h1_style))
    story.append(Paragraph(
        "Yatra uses a unified RAG & LLM pipeline running inside the main FastAPI backend. "
        "When a walkthrough is requested, the system performs a localized search to ground the "
        "ensuing scene and prompt generation in historical fact.", body_style
    ))
    
    # Visual Flow Table
    flow_data = [
        ["Step", "Component", "Operation", "Performance"],
        ["1", "API Endpoint", "POST /api/walkthrough receives (place, era)", "HTTP Request"],
        ["2", "Fast RAG Path", "Checks key in chunks/snapshot_index.json", "O(1) memory lookup (~0ms)"],
        ["3", "Fuzzy RAG Fallback", "Chroma DB query (gemini-embedding-001)", "Similarity search (<200ms)"],
        ["4", "World State Gen", "Sends RAG context + prompt to Gemini API", "LLM Generation (2 - 5s)"]
    ]
    flow_table = Table(flow_data, colWidths=[0.5*inch, 1.5*inch, 3.25*inch, 1.75*inch])
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 15))
    
    # -------------------------------------------------------------------------
    # SECTION 2: RUNNING & CONFIGURING THE PIPELINE
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Server Setup & Launch", h1_style))
    story.append(Paragraph("Ensure you have your environment configured inside <b>backend/.env</b> with a valid API key:", body_style))
    story.append(make_code_panel("GEMINI_API_KEY=AIzaSyYourKeyHere..."))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("Start the server from the repository root directory <b>Yatra/</b>:", body_style))
    story.append(make_code_panel(
        "cd /Users/dakshsablok/Yatra\n"
        "PYTHONPATH=. backend/venv/bin/uvicorn backend.main:app --reload --port 8000"
    ))
    story.append(Spacer(1, 15))
    
    # -------------------------------------------------------------------------
    # SECTION 3: STEP-BY-STEP TESTING CURLS
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Integration Test Scenarios", h1_style))
    
    story.append(Paragraph("Scenario A: Fast Path Lookup (Valid Place & Era)", h2_style))
    story.append(Paragraph("Verify O(1) retrieval match works for indexed places (e.g. Hampi, Agra, Mohenjo-daro). This hits the cached JSON index instantly without querying Chroma DB.", body_style))
    story.append(make_code_panel(
        "curl -X POST http://localhost:8000/api/walkthrough \\\n"
        "  -H \"Content-Type: application/json\" \\\n"
        "  -d '{\n"
        "    \"place\": \"Hampi\",\n"
        "    \"era\": \"Vijayanagara Empire (c. 1500 CE)\"\n"
        "  }'"
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Scenario B: List Supported Combinations", h2_style))
    story.append(Paragraph("Call the helper route to list all 25 valid place/era keys stored in the database.", body_style))
    story.append(make_code_panel("curl http://localhost:8000/api/walkthrough/places"))
    
    story.append(PageBreak())  # Move to Page 2 for clean layout

    # -------------------------------------------------------------------------
    # SECTION 4: INTEGRATION CRITERIA & CONTINUITY
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. World State Validation Criteria", h1_style))
    story.append(Paragraph(
        "When verifying the JSON response payload, your teammate must ensure the following schema constraints "
        "and architectural rules are fulfilled:", body_style
    ))
    
    criteria = [
        "<b>Stops Count:</b> Must generate between 3 and 5 stops.",
        "<b>Narration Word Count:</b> Each stop's narration_script must contain at least 120 words.",
        "<b>Context Grounding:</b> The daily_life_facts array must have at least 3 factual details extracted from retrieval context.",
        "<b>Image Prompt Continuity:</b> Every stop's image_prompt after the first must explicitly refer to the previous stop's vantage point or contain transition markers (e.g., 'Continuing from...', 'Leaving the...')."
    ]
    for c in criteria:
        story.append(Paragraph(f"• {c}", bullet_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 5: IMAGE GENERATION DESIGN GUIDELINES (B1/B2 integration)
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Visual Prompt Guidelines for Imagen Integration", h1_style))
    story.append(Paragraph(
        "The generated image prompts are optimized specifically for historical accuracy and architectural environments. "
        "Ensure your image generation modules (Imagen/DALL-E) adhere to these prompt qualities:", body_style
    ))
    
    visual_guidelines = [
        "<b>Environment-Focused:</b> Prompt details must describe the cityscape, lighting, weather, building materials, and street layout, rather than close-up characters or modern tourist settings.",
        "<b>Material Grounding:</b> Expect prompts to contain specific historical materials (e.g., 'sandstone', 'terracotta brick', 'monolithic granite carvings', 'bitumen sealants') derived from the RAG database.",
        "<b>Transition Prompts:</b> Prompts will naturally reference previous stops to preserve camera continuity, facilitating an immersive 'walkthrough' progression."
    ]
    for vg in visual_guidelines:
        story.append(Paragraph(f"• {vg}", bullet_style))
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # PAGE NUMBER FOOTER SETUP
    # -------------------------------------------------------------------------
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(SLATE)
        canvas.drawString(54, 30, "Yatra Developer Guides — Confidential")
        canvas.drawRightString(doc.pagesize[0]-54, 30, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)

if __name__ == "__main__":
    build_pdf()
