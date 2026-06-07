# gridiron_gpt/cli/__main__.py

import click

from gridiron_gpt.cli.ask import ask
from gridiron_gpt.data_ingest.timeline import build_player_timeline
from gridiron_gpt.data_ingest.digest_loader import build_digest
from gridiron_gpt.data_ingest.risers import build_risers_report
from gridiron_gpt.data_ingest.fallers import build_fallers_report
from gridiron_gpt.data_ingest.player_report import build_player_report
from gridiron_gpt.data_ingest.news_fetcher import create_news_item, save_news_item
from gridiron_gpt.data_ingest.injury_fetcher import create_injury_item, save_injury_item
from gridiron_gpt.data_ingest.rss_news_fetcher import fetch_and_save_from_env
from gridiron_gpt.data_ingest.player_matcher import extract_player_and_team
from gridiron_gpt.data_ingest.player_scores import build_draft_watch_report
from gridiron_gpt.data_ingest.team_report import build_team_report
from gridiron_gpt.data_ingest.roster_fetcher import (
    create_roster_item,
    save_roster_item,
)

@click.group()
def cli():
    """GridironGPT command line interface."""
    pass


@cli.command()
@click.option("--dry-run", is_flag=True, help="Run diagnostics without making changes.")
def doctor(dry_run):
    """Run project diagnostics."""
    from gridiron_gpt.cli.doctor import run_diagnostics
    run_diagnostics(dry_run=dry_run)


@cli.command()
def digest():
    """Show the daily training camp digest."""
    click.echo(build_digest())


@cli.command()
def risers():
    """Show players trending up during training camp."""
    click.echo(build_risers_report())


@cli.command()
def fallers():
    """Show players trending down during training camp."""
    click.echo(build_fallers_report())


@cli.command()
@click.option("--player", required=True, help="Player name to report on.")
def report(player):
    """Show a camp report for a specific player."""
    click.echo(build_player_report(player))


@cli.command("update-news")
@click.option("--player", required=True, help="Player name.")
@click.option("--team", required=True, help="NFL team abbreviation.")
@click.option("--headline", required=True, help="News headline or update.")
@click.option("--source", default="Manual Entry", show_default=True, help="News source.")
@click.option(
    "--impact",
    default="unknown",
    show_default=True,
    type=click.Choice(["positive", "negative", "monitor", "neutral", "unknown"]),
    help="Fantasy impact label.",
)
def update_news(player, team, headline, source, impact):
    """Add a manual training camp news item."""
    item = create_news_item(
        player=player,
        team=team,
        headline=headline,
        source=source,
        fantasy_impact=impact,
    )
    path = save_news_item(item)
    click.echo(f"Saved news item to {path}")

@cli.command("update-injury")
@click.option("--player", required=True, help="Player name.")
@click.option("--team", required=True, help="NFL team abbreviation.")
@click.option("--headline", required=True, help="Injury headline or update.")
@click.option("--status", default="unknown", show_default=True, help="Practice/player status.")
@click.option("--injury", default="unknown", show_default=True, help="Injury type.")
@click.option(
    "--impact",
    default="monitor",
    show_default=True,
    type=click.Choice(["positive", "negative", "monitor", "neutral", "unknown"]),
    help="Fantasy impact label.",
)
def update_injury(player, team, headline, status, injury, impact):
    """Add a manual training camp injury item."""
    item = create_injury_item(
        player=player,
        team=team,
        headline=headline,
        status=status,
        injury=injury,
        fantasy_impact=impact,
    )
    path = save_injury_item(item)
    click.echo(f"Saved injury item to {path}")

@cli.command("update-roster")
@click.option("--player", required=True)
@click.option("--team", required=True)
@click.option("--headline", required=True)
@click.option("--movement", default="unknown", show_default=True)
@click.option(
    "--impact",
    default="unknown",
    show_default=True,
    type=click.Choice(
        ["positive", "negative", "monitor", "neutral", "unknown"]
    ),
)
def update_roster(player, team, headline, movement, impact):
    """Add a manual roster movement item."""
    item = create_roster_item(
        player=player,
        team=team,
        headline=headline,
        movement=movement,
        fantasy_impact=impact,
    )

    path = save_roster_item(item)
    click.echo(f"Saved roster item to {path}")

@cli.command("fetch-rss-news")
def fetch_rss_news_command():
    """Fetch news from GRIDIRON_RSS_URL and save it."""
    try:
        count, path = fetch_and_save_from_env()
    except RuntimeError as e:
        raise click.ClickException(str(e))

    click.echo(f"Fetched {count} RSS news items into {path}")

@cli.command("update-all")
@click.option(
    "--show-digest",
    is_flag=True,
    help="Print the full camp digest after updating."
)
def update_all(show_digest):
    """Fetch latest news and show camp movement summaries."""
    click.echo("🏈 Updating GridironGPT...")
    click.echo("")

    try:
        count, path = fetch_and_save_from_env()
    except RuntimeError as e:
        raise click.ClickException(str(e))

    click.echo(f"✓ Fetched {count} RSS news items")
    click.echo(f"✓ Updated news file: {path}")
    click.echo("")

    click.echo(build_risers_report())
    click.echo("")
    click.echo(build_fallers_report())

    if show_digest:
        click.echo("")
        click.echo(build_digest())

@cli.command("report-team")
@click.option("--team", required=True, help="NFL team abbreviation, e.g. HOU, DAL, GB.")
def report_team(team):
    """Show a camp report for a specific team."""
    click.echo(build_team_report(team))

@cli.command()
@click.option("--player", required=True, help="Player name to show timeline for.")
def timeline(player):
    """Show dated camp updates for a player."""
    click.echo(build_player_timeline(player))

@cli.command("draft-watch")
def draft_watch():
    """Show players with the strongest positive and negative fantasy signals."""
    click.echo(build_draft_watch_report())

cli.add_command(ask)


if __name__ == "__main__":
    cli()
