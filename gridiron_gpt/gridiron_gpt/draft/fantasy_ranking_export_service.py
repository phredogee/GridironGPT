from __future__ import annotations

from io import BytesIO

from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulation


FIELD_LABELS = {
    "rank": "Rank",
    "player": "Player",
    "position": "Pos",
    "position_rank": "Pos Rank",
    "tier": "Tier",
    "team": "Team",
    "bye": "Bye",
    "score": "Score",
    "consensus_adp": "Consensus ADP",
    "ffc_adp": "FFC ADP",
    "nfl_adp": "NFL ADP",
    "adp_spread": "ADP Spread",
    "adp_source_count": "ADP Sources",
    "draft_value": "Draft Value",
    "baseline": "Baseline",
    "market": "Market",
    "role": "Role",
    "cortex": "Cortex",
    "availability": "Availability",
    "football_notes": "Football Notes",
    "provenance": "Provenance",
}

DRAFT_DAY_FIELDS = (
    "rank",
    "player",
    "position",
    "position_rank",
    "tier",
    "team",
    "bye",
    "score",
    "consensus_adp",
    "draft_value",
    "football_notes",
)

FULL_ANALYSIS_FIELDS = tuple(FIELD_LABELS)

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


def _validated_fields(selected_fields) -> tuple[str, ...]:
    fields = tuple(selected_fields or DRAFT_DAY_FIELDS)
    unknown = [field for field in fields if field not in FIELD_LABELS]
    if unknown:
        raise ValueError(f"Unknown export fields: {', '.join(unknown)}")
    if not fields:
        raise ValueError("At least one export field is required")
    return fields


def _rows(
    scores,
    *,
    selected_fields,
    bye_week_by_team: dict[str, int] | None = None,
    football_notes_by_player_id: dict[str, str] | None = None,
    market_views_by_player_id: dict | None = None,
) -> list[dict]:
    fields = _validated_fields(selected_fields)
    bye_week_by_team = bye_week_by_team or {}
    football_notes_by_player_id = football_notes_by_player_id or {}
    market_views_by_player_id = market_views_by_player_id or {}

    rows: list[dict] = []
    for rank, score in enumerate(scores, start=1):
        market_view = market_views_by_player_id.get(score.player_id)
        source_adps = getattr(market_view, "source_adps", {}) if market_view else {}
        values = {
            "rank": rank,
            "player": score.player_name,
            "position": score.position or "-",
            "position_rank": getattr(market_view, "position_rank", None),
            "tier": getattr(market_view, "tier", None),
            "team": score.team or "-",
            "bye": bye_week_by_team.get((score.team or "").upper()),
            "score": score.ranking_score,
            "consensus_adp": getattr(market_view, "consensus_adp", None),
            "ffc_adp": source_adps.get("Fantasy Football Calculator"),
            "nfl_adp": source_adps.get("NFL Fantasy"),
            "adp_spread": getattr(market_view, "adp_spread", None),
            "adp_source_count": getattr(market_view, "adp_source_count", 0),
            "draft_value": getattr(market_view, "draft_value", None),
            "baseline": score.components.get("baseline"),
            "market": score.components.get("market"),
            "role": score.components.get("role"),
            "cortex": score.components.get("cortex"),
            "availability": score.components.get("availability"),
            "football_notes": football_notes_by_player_id.get(
                score.player_id,
                compact_takeaway(score),
            ),
            "provenance": " | ".join(
                f"{name}: {source}"
                for name, source in score.provenance.items()
            ),
        }
        rows.append({FIELD_LABELS[field]: values[field] for field in fields})
    return rows


def build_rankings_xlsx(
    population: FantasyRankingPopulation,
    *,
    overall_limit: int | None = None,
    position_limit: int | None = None,
    selected_fields=DRAFT_DAY_FIELDS,
    bye_week_by_team: dict[str, int] | None = None,
    football_notes_by_player_id: dict[str, str] | None = None,
    market_views_by_player_id: dict | None = None,
) -> bytes:
    """Build an XLSX workbook with selectable fields and position sheets."""
    import pandas as pd

    fields = _validated_fields(selected_fields)
    output = BytesIO()
    overall = population.overall[:overall_limit] if overall_limit else population.overall

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(
            _rows(
                overall,
                selected_fields=fields,
                bye_week_by_team=bye_week_by_team,
                football_notes_by_player_id=football_notes_by_player_id,
                market_views_by_player_id=market_views_by_player_id,
            )
        ).to_excel(writer, sheet_name="Overall", index=False)

        for position in ("QB", "RB", "WR", "TE"):
            scores = population.by_position.get(position, [])
            if position_limit:
                scores = scores[:position_limit]
            pd.DataFrame(
                _rows(
                    scores,
                    selected_fields=fields,
                    bye_week_by_team=bye_week_by_team,
                    football_notes_by_player_id=football_notes_by_player_id,
                    market_views_by_player_id=market_views_by_player_id,
                )
            ).to_excel(writer, sheet_name=position, index=False)

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
    selected_fields=DRAFT_DAY_FIELDS,
    bye_week_by_team: dict[str, int] | None = None,
    football_notes_by_player_id: dict[str, str] | None = None,
    market_views_by_player_id: dict | None = None,
) -> bytes:
    """Build a compact PDF draft list using only selected fields."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    fields = _validated_fields(selected_fields)
    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(letter),
        rightMargin=0.3 * inch,
        leftMargin=0.3 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch,
        title="GridironGPT Fantasy Rankings",
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph("GridironGPT Fantasy Rankings", styles["Title"]),
        Paragraph(
            "Draft list generated from GridironGPT integrated rankings.",
            styles["BodyText"],
        ),
        Spacer(1, 0.1 * inch),
    ]

    def add_section(title: str, scores) -> None:
        rows = _rows(
            scores,
            selected_fields=fields,
            bye_week_by_team=bye_week_by_team,
            football_notes_by_player_id=football_notes_by_player_id,
            market_views_by_player_id=market_views_by_player_id,
        )
        story.append(Paragraph(title, styles["Heading2"]))
        headers = [FIELD_LABELS[field] for field in fields]
        data = [headers]
        for row in rows:
            formatted = []
            for header in headers:
                value = row.get(header)
                if isinstance(value, float):
                    value = f"{value:.1f}"
                elif value is None:
                    value = "-"
                formatted.append(value)
            data.append(formatted)

        available_width = 10.4 * inch
        preferred = {
            "Rank": 0.36,
            "Player": 1.55,
            "Pos": 0.38,
            "Pos Rank": 0.48,
            "Tier": 0.38,
            "Team": 0.42,
            "Bye": 0.38,
            "Score": 0.52,
            "Consensus ADP": 0.68,
            "FFC ADP": 0.55,
            "NFL ADP": 0.55,
            "ADP Spread": 0.58,
            "ADP Sources": 0.55,
            "Draft Value": 0.62,
            "Baseline": 0.58,
            "Market": 0.54,
            "Role": 0.48,
            "Cortex": 0.54,
            "Availability": 0.68,
            "Football Notes": 2.0,
            "Provenance": 2.4,
        }
        raw_widths = [preferred.get(header, 0.8) for header in headers]
        scale = min(1.0, available_width / sum(raw_widths))
        col_widths = [width * scale * inch for width in raw_widths]

        table = Table(data, repeatRows=1, colWidths=col_widths)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                    ("GRID", (0, 0), (-1, -1), 0.2, colors.grey),
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
