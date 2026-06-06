# gridiron_gpt/cli/__main__.py

import click

from gridiron_gpt.cli.ask import ask
from gridiron_gpt.data_ingest.digest_loader import build_digest
from gridiron_gpt.data_ingest.risers import build_risers_report
from gridiron_gpt.data_ingest.fallers import build_fallers_report
from gridiron_gpt.data_ingest.player_report import build_player_report
from gridiron_gpt.data_ingest.news_fetcher import create_news_item, save_news_item


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


cli.add_command(ask)


if __name__ == "__main__":
    cli()
