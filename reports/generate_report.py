import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(processed_dir="data/processed", output_path="reports/business_report.pdf"):
    print("Generating Business PDF Report...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Load processed data
    df_rev = pd.read_csv(os.path.join(processed_dir, "monthly_revenue_kpis.csv"))
    df_seg = pd.read_csv(os.path.join(processed_dir, "segment_clv_metrics.csv"))
    
    # Extract latest stats
    latest = df_rev.iloc[-2]  # Use second-to-last month since the very last month (June 2026) is partial
    mrr_val = latest["mrr"]
    arr_val = latest["arr"]
    active_users = latest["active_users"]
    arpu_val = latest["arpu"]
    
    # Start document
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        name="DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#1e3a8a"),
        alignment=0, # Left-aligned
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        name="DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        name="ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=10
    )
    
    kpi_title_style = ParagraphStyle(
        name="KPITitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#ffffff"),
        alignment=1
    )
    
    kpi_value_style = ParagraphStyle(
        name="KPIValue",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#ffffff"),
        alignment=1
    )

    story = []
    
    # ------------------
    # Header / Cover Element
    # ------------------
    story.append(Paragraph("RevenueIQ — SaaS Business Intelligence & Customer Analytics Platform", title_style))
    story.append(Paragraph("Executive Business Analytics Report & KPI Analysis", subtitle_style))
    story.append(Spacer(1, 10))
    
    # ------------------
    # Section: Executive Summary
    # ------------------
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(
        "This performance report summarizes key commercial SaaS metrics and customer engagement insights "
        "derived from the Product Intelligence Platform. Metrics are calculated using our star schema "
        "warehouse, capturing over 120,000 billing transactions. Key dimensions evaluated include "
        "customer lifetime value (CLV), recurring run rates (MRR/ARR), churn rate coefficients, and cohort analysis.",
        body_style
    ))
    story.append(Spacer(1, 15))
    
    # ------------------
    # KPI Grid Table
    # ------------------
    kpi_data = [
        [
            Paragraph("Monthly Rec. Revenue", kpi_title_style),
            Paragraph("Annual Rec. Revenue", kpi_title_style),
            Paragraph("Active Paying Users", kpi_title_style),
            Paragraph("Avg Revenue Per User", kpi_title_style)
        ],
        [
            Paragraph(f"${mrr_val:,.2f}", kpi_value_style),
            Paragraph(f"${arr_val:,.2f}", kpi_value_style),
            Paragraph(f"{int(active_users):,}", kpi_value_style),
            Paragraph(f"${arpu_val:,.2f}", kpi_value_style)
        ]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[125, 125, 125, 125])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1e3a8a")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 2),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,1), (-1,1), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#3b82f6")),
    ]))
    
    story.append(kpi_table)
    story.append(Spacer(1, 20))
    
    # ------------------
    # Section: Customer Segment Analysis
    # ------------------
    story.append(Paragraph("Customer Segment Performance Metrics", h1_style))
    story.append(Paragraph(
        "Different client tiers (SMB, Mid-Market, Enterprise) display varying contract sizes, lifetime retention profiles, "
        "and overall predicted value. Enterprise customers present high individual value with low relative churn rates.",
        body_style
    ))
    
    # Build Segment Metrics Table
    seg_headers = ["Segment", "ARPU", "Churn Rate (%)", "Est. Lifetime Value (CLV)"]
    seg_rows = [[row["segment"], f"${row['arpu']:.2f}", f"{row['churn_rate']*100:.2f}%", f"${row['predicted_clv']:,.2f}"] for idx, row in df_seg.iterrows()]
    
    table_data = [seg_headers] + seg_rows
    seg_table = Table(table_data, colWidths=[120, 120, 120, 140])
    seg_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f3f4f6")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#1f2937")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
    ]))
    
    story.append(seg_table)
    story.append(Spacer(1, 20))
    
    # ------------------
    # Section: Key Takeaways
    # ------------------
    story.append(Paragraph("Strategic Insights & Recommendations", h1_style))
    story.append(Paragraph(
        "<b>1. Stabilize SMB Retention:</b> SMB accounts exhibit the highest monthly churn rate (~3.3%). Marketing and "
        "customer success should launch specific retention campaigns or incentivize migration to annual agreements.<br/>"
        "<b>2. Expand Enterprise Tier:</b> Enterprise clients, despite representing only 5% of the total base, provide "
        "extremely high Predictive CLV (~$20,000) and exhibit very low churn (~0.8% monthly equivalent). Accelerate sales efforts to acquire enterprise logos.",
        body_style
    ))
    
    # Build Document
    doc.build(story)
    print("Report PDF generated successfully.")

if __name__ == "__main__":
    generate_pdf_report()
