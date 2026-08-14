from __future__ import annotations

from io import BytesIO

from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulation


COMPONENT_LABELS = {
    "baseline": "baseline",
    "market": "market",
    "role": "role",
    "cortex": "Cortex",
    "availability": "availability",
}


def compact_takeaway(score) -> str:
    """Return a short draft-day takeaway suitable for compact PDF rows."""
    primary = [
        (name, value)
        for name, value in score.components.items()
        if name != "availability"
    ]
    if not primary:
        return "Limited ranking evidence"

    primary.sort(key=lambda item: item[1], reverse=True)
    strong = [item for item in primary if item[1] >= 70.0]

    if len(strong) >= 2:
        first = COMPONENT_LABELS.get(strong[0][0], strong[0][0])
        second = COMPONENT_LABELS.get(strong[1][0], strong[1][0])
        qualifier = "Elite" if strong[0][1] >= 85.0 else "Strong"
        return f"{qualifier} {first} + {second}"

    if strong:
        label = COMPONENT_LABELS.get(strong[0][0], strong[0][0])
        qualifier = "Elite" if strong[0][1] >= 85.0 else "Strong"
        return f"{qualifier} {label} profile"

    best = COMPONENT_LABELS.get(primary[0][0], primary[0][0])
    return f"{best.title()}-led profile"


def _rows(scores) -> list[dict]:
    rows: list[dict] = []
    for rank, score in enumerate(scores, start=1):
        rows.append(
            {
                "Rank": rank,
                "Player": score.player_name,
                "Pos": score.position or "-",
                "Team": score.team or "-",
                "Score": score.ranking_score,
                "Baseline": score.components.get("baseline"),
                "Market": score.components.get("market"),
                "Role": score.components.get("role"),
                "Cortex": score.components.get("cortex"),
                "Availability": score.components.get("availability"),
                "Takeaway": compact_takeaway(score),
                "Provenance": " | ".join(
                    f"{name}: {source}"
                    for name, source in score.provenance.items()
                ),
            }
        )
    return rows


def build_rankings_xlsx(
    population: FantasyRankingPopulation,
    *,
    overall_limit: int | None = None,
    position_limit: int | None = None,
) -> bytes:
    """Build an XLSX workbook with overall and position-specific sheets."""
    import pandas as pd

    output = BytesIO()
    overall = population.overall[:overall_limit] if overall_limit else population.overall

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(_rows(overall)).to_excel(
            writer,
            sheet_name="Overall",
            index=False,
        )
        for position in ("QB", "RB", "WR", "TE"):
            scores = population.by_position.get(position, [])
            if position_limit:
                scores = scores[:position_limit]
            pd.DataFrame(_rows(scores)).to_excel(
                writer,
                sheet_name=position,
                index=False,
            )

        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for column_cells in worksheet.columns:
                width = min(
                    55,
                    max(
                        10,
                        max(len(str(cell.value or "")) for cell in column_cells) + 2,
                    ),
                )
                worksheet.column_dimensions[column_cells[0].column_letter].width = width

    return output.getvalue()


def build_rankings_pdf(
    population: FantasyRankingPopulation,
    *,
    overall_limit: int = 100,
    position_limit: int = 50,
) -> bytes:
    """Build a compact PDF draft list with short 2-5 word takeaways."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=letter,
        rightMargin=0.35 * inch,
        leftMargin=0.35 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
        title="GridironGPT Fantasy Rankings",
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph("GridironGPT Fantasy Rankings", styles["Title"]),
        Paragraph(
            "Integrated evidence: historical production, market/ADP, role, Cortex, and availability.",
            styles["BodyText"],
        ),
        Spacer(1, 0.12 * inch),
    ]

    def add_section(title: str, scores) -> None:
        story.append(Paragraph(title, styles["Heading2"]))
        data = [["#", "Player", "Pos", "Tm", "Score", "Takeaway"]]
        for rank, score in enumerate(scores, start=1):
            data.append(
                [
                    rank,
                    score.player_name,
                    score.position or "-",
                    score.team or "-",
                    f"{score.ranking_score:.2f}",
                    compact_takeaway(score),
                ]
            )
        table = Table(
            data,
            repeatRows=1,
            colWidths=[0.32 * inch, 2.15 * inch, 0.42 * inch, 0.42 * inch, 0.55 * inch, 2.45 * inch],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(table)

    add_section("Overall", population.overall[:overall_limit])
    for position in ("QB", "RB", "WR", "TE"):
        story.append(PageBreak())
        add_section(
            position,
            population.by_position.get(position, [])[:position_limit],
        )

    doc.build(story)
    return output.getvalue()
