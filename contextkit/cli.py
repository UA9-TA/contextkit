from pathlib import Path
from typing import List, Optional

import pyperclip
import typer

from .bundle_builder import BundleBuilder
from .config import Config
from .display import Display, console
from .formatter import Formatter
from .graph_resolver import GraphResolver
from .indexer import Indexer
from .relevance import RelevanceScorer
from .token_counter import TokenCounter

app = typer.Typer(help="ContextKit — Context Builder")
config = Config()

@app.command()
def index(update: bool = typer.Option(False, "--update", help="Update existing index")):
    """Index your codebase."""
    root_dir = "."
    indexer = Indexer(root_dir)
    with console.status("Indexing codebase..."):
        index_data = indexer.index(update=update)
    Display.print_index_result(index_data)

@app.command()
def build(
    task: str = typer.Argument(..., help="Task description"),
    files: Optional[List[str]] = typer.Option(None, "--files", help="Seed files to start with"),
    copy: bool = typer.Option(False, "--copy", help="Copy to clipboard"),
    output: str = typer.Option(None, "--output", help="Output to file"),
    count_tokens: bool = typer.Option(False, "--count-tokens", help="Show token count estimate"),
    max_tokens: int = typer.Option(None, "--max-tokens", help="Maximum tokens to include"),
    semantic: bool = typer.Option(False, "--semantic", help="Use semantic search")
):
    """Generate context for a task."""
    root_dir = "."
    indexer = Indexer(root_dir)

    if not indexer.index_file.exists():
        console.print("[red]Index not found. Run 'contextkit index' first.[/red]")
        raise typer.Exit(1)

    index_data = indexer.index(update=False)

    num_files = len(index_data.get("files", {}))
    num_symbols = sum(len(f.get("symbols", [])) for f in index_data.get("files", {}).values())
    index_size_str = f"{num_symbols:,} symbols, {num_files:,} files"

    scorer = RelevanceScorer(root_dir, index_data)
    use_semantic = semantic or config.get("semantic")
    scores = scorer.score(task, use_semantic=use_semantic)

    resolver = GraphResolver(index_data)
    seed_files = files if files else [f for f, s in scores.items() if s > 0]
    # For small tests, we might want to just grab the top relevant files
    if not files and scores:
        # Sort and take top matches as seed
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        # Take anything with score > 0.5 of max score or top 3
        max_score = sorted_scores[0][1]
        seed_files = [f for f, s in sorted_scores if s >= max_score * 0.5][:3]
        if not seed_files:
             seed_files = [sorted_scores[0][0]]

    resolved_files = resolver.resolve(seed_files, max_depth=3, relevance_scores=scores)

    budget = max_tokens if max_tokens else config.get("max_tokens")
    builder = BundleBuilder(root_dir, max_tokens=budget)

    bundle_data = builder.build(resolved_files, relevance_scores=scores)

    bundle_content = bundle_data["files"]
    formatted_output = Formatter.format(bundle_content, format_type=config.get("format"))

    if copy:
        pyperclip.copy(formatted_output)
        console.print("Copied to clipboard ✓")

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        console.print(f"Written to {output} ✓")

    if count_tokens or not (copy or output):
        # Calculate full codebase tokens roughly for comparison
        counter = TokenCounter()
        total_tokens = 0
        for f in index_data.get("files", {}):
            try:
                with open(Path(root_dir) / f, 'r', encoding='utf-8') as file:
                    total_tokens += counter.count(file.read())
            except Exception:
                pass
        if total_tokens == 0:
             total_tokens = 1
        reduction = int(100 * (1 - bundle_data['total_tokens'] / total_tokens))

        bundle_lines = len(formatted_output.splitlines())

        Display.print_build_result(
            task=task,
            index_size_str=index_size_str,
            resolved_files=list(bundle_content.keys()),
            bundle_files=len(bundle_content),
            bundle_lines=bundle_lines,
            tokens=bundle_data["total_tokens"],
            total_tokens=total_tokens,
            reduction=reduction
        )

        if not (copy or output):
            console.print(formatted_output)

@app.command()
def show():
    """Show what's in the current index."""
    root_dir = "."
    indexer = Indexer(root_dir)
    if not indexer.index_file.exists():
        console.print("[red]Index not found. Run 'contextkit index' first.[/red]")
        raise typer.Exit(1)

    index_data = indexer.index(update=False)
    Display.print_index_result(index_data)

if __name__ == "__main__":
    app()
