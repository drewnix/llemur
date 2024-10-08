import typer
from rich.console import Console

from llemur.cr import cr
from llemur.perf_analysis import perf_analysis
from llemur.summarize import summarize

console = Console()

llemur = typer.Typer(no_args_is_help=True)

llemur.command(name="cr", help="llm code review")(cr)
llemur.command(name="summarize", help="llm code summarization")(summarize)
llemur.command(name="perf_analysis", help="llm code summarization")(perf_analysis)


if __name__ == "__main__":
    llemur()
