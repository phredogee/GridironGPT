# gridiron_gpt/cli/ask.py

import os
import click
from gridiron_gpt.core.advisor import Advisor
from gridiron_gpt.core.llm import generate_advice
from gridiron_gpt.feedback import banner, error


@click.command()
@click.argument("query")
@click.option("--top", default=5, show_default=True, type=int, help="Number of results to retrieve")
@click.option("--raw", is_flag=True, help="Skip LLM — show raw similarity results only")
def ask(query, top, raw):
    """Ask a fantasy football question against the player index.

    Examples:\n
      python -m gridiron_gpt ask "best RB to start this week"\n
      python -m gridiron_gpt ask "top wide receivers" --top 10\n
      python -m gridiron_gpt ask "Atlanta Falcons players" --raw
    """
    advisor = Advisor()
    try:
        advisor.load()
    except FileNotFoundError as e:
        error(str(e))
        return

    try:
        results = advisor.query(query, top_k=top)
    except RuntimeError as e:
        error(str(e))
        return

    if not results:
        banner("No results found for that query.", emoji="❓")
        return

    use_llm = os.environ.get("GRIDIRON_LLM", "ollama").lower() != "none"

    if not raw and use_llm:
        advice = generate_advice(query, results)
        if advice and not advice.startswith("[LLM error"):
            click.echo(f"\n🏈  {query}\n")
            click.echo("─" * 60)
            click.echo(advice)
            click.echo("─" * 60)
            click.echo(f"\n  (based on {len(results)} indexed players — use --raw to see them)\n")
            return
        # LLM failed — fall through to raw output
        click.echo(advice)  # show the error message

    # Raw / fallback display
    click.echo(f"\n🔍  {query}\n")
    click.echo(f"  {'#':<4} {'Player / Position / Team / Week / Points':<55} {'Match':>6}")
    click.echo("  " + "─" * 67)
    for i, r in enumerate(results, 1):
        pct = int(r["similarity"] * 100)
        click.echo(f"  {i:<4} {r['text']:<55} {pct:>5}%")

    if not use_llm and not raw:
        click.echo(
            "\n  💡 Set GRIDIRON_LLM=ollama to get AI-generated advice instead of raw results.\n"
        )
    else:
        click.echo()
