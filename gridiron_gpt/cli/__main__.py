# gridiron_gpt/cli/__main__.py

import click

from gridiron_gpt.cli.ask import ask
from gridiron_gpt.data_ingest.digest_loader import build_digest


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


cli.add_command(ask)


if __name__ == "__main__":
    cli()
