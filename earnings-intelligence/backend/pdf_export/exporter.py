import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

NAVY = colors.HexColor("#0f3460")
LIGHT_BLUE = colors.HexColor("#f0f4ff")
GREEN = colors.HexColor("#155724")
RED = colors.HexColor("#721c24")
GOLD = colors.HexColor("#856404")
MUTED = colors.HexColor("#6b7a99")


def _fmt_num(n, prefix=""):
    if n is None:
        return "—"
    try:
        n = float(n)
        if abs(n) >= 1e9:
            return f"{prefix}{n/1e9:.2f}B"
        if abs(n) >= 1e6:
            return f"{prefix}{n/1e6:.1f}M"
        return f"{prefix}{n:,.2f}"
    except Exception:
        return str(n)


def _pct(n):
    if n is None:
        return "—"
    sign = "+" if float(n) > 0 else ""
    return f"{sign}{n}%"


def generate_pdf(report_data: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", fontSize=18, textColor=NAVY,
                                  spaceAfter=4, fontName="Helvetica-Bold")
    h2_style = ParagraphStyle("h2", fontSize=13, textColor=NAVY,
                               spaceAfter=6, spaceBefore=14, fontName="Helvetica-Bold")
    h3_style = ParagraphStyle("h3", fontSize=11, textColor=NAVY,
                               spaceAfter=4, spaceBefore=8, fontName="Helvetica-Bold")
    body_style = ParagraphStyle("body", fontSize=9, spaceAfter=4,
                                 leading=14, fontName="Helvetica")
    meta_style = ParagraphStyle("meta", fontSize=8, textColor=MUTED,
                                 spaceAfter=10, fontName="Helvetica")
    synthesis_style = ParagraphStyle("synth", fontSize=9, leading=15,
                                      spaceAfter=4, fontName="Helvetica",
                                      leftIndent=8, rightIndent=8)

    def section_rule():
        return HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=6)

    def table_style_base():
        return TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e0e4ef")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])

    story = []

    ticker = report_data.get("ticker", "")
    period = report_data.get("period", "")
    generated_at = report_data.get("generated_at", "")

    story.append(Paragraph(f"Earnings Intelligence: {ticker} — {period}", title_style))
    story.append(Paragraph(f"Generated {generated_at} · Public data sources", meta_style))
    story.append(section_rule())

    # ── Module 1: Earnings Summary ───────────────────────────────────────────
    earnings = report_data.get("earnings") or {}
    eps = earnings.get("eps") or {}
    revenue = earnings.get("revenue") or {}
    margins = earnings.get("margins") or {}
    guidance = earnings.get("guidance") or {}

    story.append(Paragraph("1. Earnings Summary", h2_style))

    kpi_data = [
        ["Metric", "Actual", "Estimate", "Δ / Note"],
        [
            "EPS",
            str(eps.get("actual") or "—"),
            str(eps.get("estimate") or "—"),
            f"{_pct(eps.get('surprise_pct'))}  [{eps.get('badge','N/A')}]",
        ],
        [
            "Revenue",
            _fmt_num(revenue.get("actual"), "$"),
            _fmt_num(revenue.get("estimate"), "$"),
            f"YoY {_pct(revenue.get('yoy_pct'))}  QoQ {_pct(revenue.get('qoq_pct'))}",
        ],
        [
            "Gross Margin",
            f"{margins.get('gross_margin_pct') or '—'}%",
            "—", "—",
        ],
        [
            "Op. Margin",
            f"{margins.get('operating_margin_pct') or '—'}%",
            "—", "—",
        ],
    ]
    t = Table(kpi_data, colWidths=[1.4 * inch, 1.2 * inch, 1.2 * inch, 3.0 * inch])
    t.setStyle(table_style_base())
    story.append(t)

    if guidance.get("next_quarter_revenue_low"):
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"Guidance (next quarter): Revenue {_fmt_num(guidance['next_quarter_revenue_low'],'$')} "
            f"– {_fmt_num(guidance.get('next_quarter_revenue_high'),'$')}",
            body_style,
        ))

    # ── Module 3: Guidance Tracker ───────────────────────────────────────────
    guidance_data = report_data.get("guidance") or {}
    summary = guidance_data.get("summary") or {}
    quarters = guidance_data.get("quarters") or []

    story.append(Paragraph("2. Guidance Tracker", h2_style))
    story.append(Paragraph(
        f"Beat rate: <b>{summary.get('beat_rate','—')}%</b> over "
        f"{summary.get('quarters_analyzed','—')} quarters  |  "
        f"Avg beat: <b>{summary.get('avg_beat_magnitude_pct','—')}%</b>  |  "
        f"Style: <b>{(summary.get('guidance_style') or 'unknown').upper()}</b>",
        body_style,
    ))

    if quarters:
        q_data = [["Date", "EPS Actual", "EPS Estimate", "Beat %"]]
        for q in quarters:
            q_data.append([
                q.get("date", "—"),
                str(q.get("eps_actual") or "—"),
                str(q.get("eps_estimate") or "—"),
                _pct(q.get("eps_beat_pct")),
            ])
        t2 = Table(q_data, colWidths=[1.4 * inch, 1.4 * inch, 1.4 * inch, 1.4 * inch])
        t2.setStyle(table_style_base())
        story.append(t2)

    # ── Module 4: Price Performance ──────────────────────────────────────────
    price_data = report_data.get("price") or {}
    current_info = price_data.get("current_info") or {}
    ratings = price_data.get("ratings") or {}
    consensus = ratings.get("consensus") or {}
    changes = ratings.get("changes") or []

    story.append(Paragraph("3. Price Performance & Analyst Ratings", h2_style))

    price_kpi = [
        ["Current Price", "52W High", "52W Low", "Mean PT", "Consensus"],
        [
            _fmt_num(current_info.get("current_price"), "$"),
            _fmt_num(current_info.get("week_52_high"), "$"),
            _fmt_num(current_info.get("week_52_low"), "$"),
            _fmt_num(consensus.get("mean_price_target"), "$"),
            f"{consensus.get('buy',0)}B / {consensus.get('hold',0)}H / {consensus.get('sell',0)}S",
        ],
    ]
    t3 = Table(price_kpi, colWidths=[1.36 * inch] * 5)
    t3.setStyle(table_style_base())
    story.append(t3)

    if changes:
        story.append(Paragraph("Recent Rating Changes", h3_style))
        rc_data = [["Date", "Firm", "From", "To", "Action"]]
        for r in changes[:10]:
            rc_data.append([
                r.get("date", ""),
                r.get("firm", ""),
                r.get("from_grade", "—"),
                r.get("to_grade", "—"),
                r.get("action", ""),
            ])
        t4 = Table(rc_data, colWidths=[1.0 * inch, 2.0 * inch, 1.1 * inch, 1.1 * inch, 1.0 * inch])
        t4.setStyle(table_style_base())
        story.append(t4)

    # ── Module 2: Events Timeline ────────────────────────────────────────────
    events = report_data.get("events") or []
    story.append(Paragraph("4. Events Timeline (recent 20)", h2_style))

    if events:
        ev_data = [["Date", "Type", "Title", "Source"]]
        for e in events[:20]:
            ev_data.append([
                e.get("date", ""),
                e.get("type", ""),
                (e.get("title") or "")[:70],
                e.get("source", ""),
            ])
        t5 = Table(ev_data, colWidths=[0.85 * inch, 0.65 * inch, 4.2 * inch, 1.1 * inch])
        t5.setStyle(table_style_base())
        story.append(t5)
    else:
        story.append(Paragraph("No events data available.", body_style))

    # ── Module 5: AI Synthesis ───────────────────────────────────────────────
    synthesis = report_data.get("synthesis")
    story.append(Paragraph("5. AI Synthesis", h2_style))

    if synthesis:
        bg_table = Table(
            [[Paragraph(synthesis.replace("\n", "<br/>"), synthesis_style)]],
            colWidths=[6.8 * inch],
        )
        bg_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("BOX", (0, 0), (-1, -1), 1.5, NAVY),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(bg_table)
    else:
        story.append(Paragraph(
            "AI synthesis not included in this export. Use the web app to generate it.",
            body_style,
        ))

    doc.build(story)
    return buf.getvalue()
