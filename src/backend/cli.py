import click
import asyncio
from typing import Optional
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from backend.business_logic import NoveltyChecker
from backend.logger import logger
from backend.config import get_settings
import braintrust
import os
from dotenv import load_dotenv

console = Console()


def print_result(result, papers_limit: Optional[int] = None):
    """Pretty print the novelty check result"""
    # Create the main result panel
    novelty_color = "green" if result.novelty == "YES" else "red"
    main_panel = Panel(
        f"[{novelty_color}]{result.novelty}[/{novelty_color}]\n\n"
        f"{result.explanation}",
        title="Novelty Check Result",
        expand=False,
    )
    console.print(main_panel)

    # Print papers found
    if result.papers:
        papers_to_show = result.papers[:papers_limit] if papers_limit else result.papers
        papers_text = "\n\n".join(
            [
                f"📄 {paper.title}\n"
                f"   📅 {paper.published_date.year if paper.published_date else 'N/A'}\n"
                f"   🔗 {paper.url}\n"
                f"   📝 {paper.summary if paper.summary else 'No summary available'}"
                for paper in papers_to_show
            ]
        )
        papers_panel = Panel(
            papers_text,
            title=f"Related Papers (showing {len(papers_to_show)} of {len(result.papers)})",
            expand=False,
        )
        console.print(papers_panel)


@click.group()
def cli():
    """Novelty Checker CLI - Check if your research question has been addressed before"""
    pass


@cli.command()
@click.argument("question", type=str)
@click.option(
    "--papers-limit",
    "-l",
    type=int,
    default=3,
    help="Limit the number of papers shown in the output",
)
@click.option(
    "--hybrid/--no-hybrid", default=False, help="Use both neural and keyword search"
)
@click.option(
    "--neural-ratio",
    type=float,
    default=0.5,
    help="Ratio of neural to keyword results when using hybrid search (0.0-1.0)",
)
def check(question: str, papers_limit: int, hybrid: bool, neural_ratio: float):
    """Check if a research question has been addressed in existing literature"""
    try:
        # Override settings if hybrid search is requested
        if hybrid:
            settings = get_settings()
            settings.EXA_USE_HYBRID_SEARCH = True
            settings.EXA_NEURAL_RATIO = max(
                0.0, min(1.0, neural_ratio)
            )  # Clamp between 0 and 1

        # Create spinner for better UX
        with console.status("[bold green]Checking novelty...") as status:
            checker = NoveltyChecker()
            result = asyncio.run(checker.check_novelty(question))

        # Print results
        print_result(result, papers_limit)

    except Exception as e:
        logger.error(f"Error during novelty check: {str(e)}", exc_info=True)
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print("\n[red]Full traceback:[/red]")
        import traceback

        console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
def serve():
    """Start the Novelty Checker API server"""
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)


def main():
    load_dotenv()

    # Initialize Braintrust
    # braintrust.init(api_key=os.getenv("BRAINTRUST_API_KEY"))

    cli()


if __name__ == "__main__":
    main()
