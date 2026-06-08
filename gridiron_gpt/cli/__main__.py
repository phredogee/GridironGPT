# gridiron_gpt/cli/__main__.py

import click

from gridiron_gpt.cli.ask import ask
from gridiron_gpt.data_ingest.timeline import build_player_timeline
from gridiron_gpt.data_ingest.player_trends import build_player_trend
from gridiron_gpt.data_ingest.digest_loader import build_digest
from gridiron_gpt.data_ingest.risers import build_risers_report
from gridiron_gpt.data_ingest.fallers import build_fallers_report
from gridiron_gpt.data_ingest.player_report import build_player_report
from gridiron_gpt.data_ingest.news_fetcher import create_news_item, save_news_item
from gridiron_gpt.data_ingest.injury_fetcher import create_injury_item, save_injury_item
from gridiron_gpt.data_ingest.rss_news_fetcher import fetch_and_save_from_env
from gridiron_gpt.data_ingest.player_matcher import extract_player_and_team
from gridiron_gpt.data_ingest.team_report import build_team_report
from gridiron_gpt.data_ingest.player_compare import build_player_comparison
from gridiron_gpt.data_ingest.player_scores import (
    build_draft_watch_report,
    build_player_scorecard,
    build_signal_rankings,
    build_recommendations_report,
)
from gridiron_gpt.data_ingest.roster_fetcher import (
    create_roster_item,
    save_roster_item,
)

from gridiron_gpt.data_ingest.player_trends import (
    build_player_trend,
    build_hot_players_report,
    build_cold_players_report,
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

@cli.command()
@click.option("--player", required=True, help="Player name to score.")
def score(player):
    """Show fantasy signal scorecard for a player."""
    click.echo(build_player_scorecard(player))

@cli.command()
@click.option("--player1", required=True, help="First player to compare.")
@click.option("--player2", required=True, help="Second player to compare.")
def compare(player1, player2):
    """Compare two players using current fantasy signal scores."""
    click.echo(build_player_comparison(player1, player2))

@cli.command()
@click.option("--limit", default=25, show_default=True, help="Number of players to show.")
@click.option("--team", default=None, help="Filter by NFL team abbreviation, e.g. HOU.")
@click.option("--position", default=None, help="Filter by position, e.g. QB, RB, WR, TE.")
@click.option("--buy", "recommendation", flag_value="BUY", default=None, help="Show BUY candidates.")
@click.option("--watch", "recommendation", flag_value="WATCH", help="Show WATCH candidates.")
@click.option("--hold", "recommendation", flag_value="HOLD", help="Show HOLD candidates.")
@click.option("--monitor", "recommendation", flag_value="MONITOR", help="Show MONITOR candidates.")
@click.option("--sell", "recommendation", flag_value="SELL", help="Show SELL candidates.")
def rankings(limit, team, position, recommendation):
    """Show ranked players by current fantasy signal score."""
    click.echo(
        build_signal_rankings(
            limit=limit,
            team_filter=team,
            position_filter=position,
            recommendation_filter=recommendation,
        )
    )

@cli.command()
@click.option("--player", required=True, help="Player name to trend.")
def trend(player):
    """Show daily fantasy signal trend for a player."""
    click.echo(build_player_trend(player))

@cli.command()
@click.option("--limit", default=10, show_default=True, help="Players per recommendation group.")
def recommendations(limit):
    """Show BUY/WATCH/HOLD/MONITOR/SELL recommendation groups."""
    click.echo(build_recommendations_report(limit=limit))

@cli.command()
@click.option("--limit", default=10, show_default=True)
def hot(limit):
    """Show players gaining momentum."""
    click.echo(build_hot_players_report(limit))

@cli.command()
@click.option("--limit", default=10, show_default=True)
def cold(limit):
    """Show players losing momentum."""
    click.echo(build_cold_players_report(limit))

cli.add_command(ask)



if __name__ == "__main__":
    cli()
