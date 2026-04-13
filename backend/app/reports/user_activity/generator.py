"""
User Activity — PDF Generator
================================
Builds a branded PDF report with KPI cards, a bar chart, and a data table.
Uses ReportLab's Platypus (flow-based layout engine).
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart

from app.reports.user_activity.data_source import UserActivityData

# ── Palette ────────────────────────────────────────────────────────────────
C_BRAND      = colors.HexColor("#6366F1")
C_BRAND_DARK = colors.HexColor("#1E293B")
C_ACCENT     = colors.HexColor("#10B981")
C_MUTED      = colors.HexColor("#64748B")
C_BG_LIGHT   = colors.HexColor("#F8FAFC")
C_BORDER     = colors.HexColor("#E2E8F0")
C_WHITE      = colors.white
C_ALT_ROW    = colors.HexColor("#F1F5F9")


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=24,
            textColor=C_BRAND_DARK,
            spaceAfter=2 * mm,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Helvetica",
            fontSize=11,
            textColor=C_MUTED,
            spaceAfter=6 * mm,
        ),
        "section": ParagraphStyle(
            "section",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=C_BRAND_DARK,
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label",
            fontName="Helvetica",
            fontSize=9,
            textColor=C_MUTED,
            alignment=TA_CENTER,
        ),
        "kpi_value": ParagraphStyle(
            "kpi_value",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=C_BRAND,
            alignment=TA_CENTER,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=C_WHITE,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName="Helvetica",
            fontSize=9,
            textColor=C_BRAND_DARK,
            alignment=TA_CENTER,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica",
            fontSize=8,
            textColor=C_MUTED,
            alignment=TA_CENTER,
        ),
    }


def _kpi_table(data: UserActivityData, styles: dict) -> Table:
    """Render 4 KPI cards in a single row."""
    kpis = [
        ("Total Active Users", f"{data.total_active_users:,}"),
        ("New Signups",         f"{data.total_new_signups:,}"),
        ("Total Sessions",      f"{data.total_sessions:,}"),
        ("Avg Session",         f"{data.avg_session_minutes} min"),
    ]

    cells = []
    for label, value in kpis:
        cells.append([
            Paragraph(value, styles["kpi_value"]),
            Paragraph(label, styles["kpi_label"]),
        ])

    # Transpose: one row of 4 columns, each column has [value, label]
    table_data = [
        [Paragraph(v, styles["kpi_value"]) for _, v in kpis],
        [Paragraph(l, styles["kpi_label"]) for l, _ in kpis],
    ]

    t = Table(table_data, colWidths=[42 * mm] * 4)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), C_BG_LIGHT),
        ("BOX",         (0, 0), (-1, -1), 0.5, C_BORDER),
        ("INNERGRID",   (0, 0), (-1, -1), 0.5, C_BORDER),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [3]),
    ]))
    return t


def _bar_chart(data: UserActivityData) -> Drawing:
    """Render a vertical bar chart of daily active users."""
    width, height = 168 * mm, 70 * mm
    drawing = Drawing(width, height)

    chart = VerticalBarChart()
    chart.x = 12 * mm
    chart.y = 10 * mm
    chart.width = width - 20 * mm
    chart.height = height - 18 * mm

    chart.data = [[d.active_users for d in data.daily]]
    chart.categoryAxis.categoryNames = [d.date[5:] for d in data.daily]  # MM-DD

    chart.bars[0].fillColor = C_BRAND
    chart.bars[0].strokeColor = None

    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(d.active_users for d in data.daily) + 300
    chart.valueAxis.valueStep = 500
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 8
    chart.valueAxis.labels.fillColor = C_MUTED

    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 8
    chart.categoryAxis.labels.fillColor = C_MUTED
    chart.categoryAxis.labels.angle = 0

    chart.groupSpacing = 5

    drawing.add(chart)
    return drawing


def _detail_table(data: UserActivityData, styles: dict) -> Table:
    """Render the daily breakdown table."""
    headers = ["Date", "Active Users", "New Signups", "Sessions", "Avg Session (min)"]
    header_row = [Paragraph(h, styles["table_header"]) for h in headers]

    rows = [header_row]
    for i, d in enumerate(data.daily):
        bg = C_ALT_ROW if i % 2 == 0 else C_WHITE
        rows.append([
            Paragraph(d.date, styles["table_cell"]),
            Paragraph(f"{d.active_users:,}", styles["table_cell"]),
            Paragraph(f"{d.new_signups:,}", styles["table_cell"]),
            Paragraph(f"{d.sessions:,}", styles["table_cell"]),
            Paragraph(str(d.avg_session_minutes), styles["table_cell"]),
        ])

    col_widths = [30 * mm, 35 * mm, 30 * mm, 30 * mm, 43 * mm]
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  C_BRAND),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  C_WHITE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_WHITE, C_ALT_ROW]),
        ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def build_pdf(data: UserActivityData, output_path: str) -> None:
    """Build and save the User Activity PDF report to `output_path`."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="User Activity Report",
        author="Report Platform",
    )

    styles = _styles()
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("User Activity Report", styles["title"]))
    story.append(Paragraph(f"Period: {data.period_label}", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BRAND, spaceAfter=6 * mm))

    # ── KPI Cards ───────────────────────────────────────────────────────────
    story.append(Paragraph("Key Metrics", styles["section"]))
    story.append(_kpi_table(data, styles))
    story.append(Spacer(1, 6 * mm))

    # ── Bar Chart ───────────────────────────────────────────────────────────
    story.append(Paragraph("Daily Active Users", styles["section"]))
    story.append(_bar_chart(data))
    story.append(Spacer(1, 4 * mm))

    # ── Detail Table ────────────────────────────────────────────────────────
    story.append(Paragraph("Daily Breakdown", styles["section"]))
    story.append(_detail_table(data, styles))
    story.append(Spacer(1, 8 * mm))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("Generated by Report Platform", styles["footer"]))

    doc.build(story)
