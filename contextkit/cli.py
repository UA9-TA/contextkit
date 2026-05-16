
import pyperclip
import typer

from contextkit.bundle_builder import build_bundle
from contextkit.display import console
from contextkit.formatter import format_bundle
from contextkit.graph_resolver import resolve_dependencies
from contextkit.indexer import build_index, load_index, needs_update
from contextkit.relevance import score_relevance
from contextkit.token_counter import count_bundle_tokens

app = typer.Typer(help="ContextKit — Context Builder for AI Assistants")

@app.command()
def index(update: bool = typer.Option(False, "--update", help="Force update the index")):
    """Index your codebase."""
    if update or needs_update():
        console.print("Building index...")
        idx = build_index()
        num_files = len(idx["files"])
        num_symbols = sum(len(d.get("symbols", [])) for d in idx["files"].values())
        console.print(f"[green]✓ Index built with {num_symbols} symbols across {num_files} files.[/green]")
    else:
        console.print("Index is up to date.")

@app.command()
def build(
    task: str = typer.Argument(..., help="The task description"),
    files: list[str] = typer.Option(None, "--files", help="Specific files to start from"),
    copy: bool = typer.Option(False, "--copy", help="Copy bundle to clipboard"),
    output: str = typer.Option(None, "--output", help="Output file path"),
    max_tokens: int = typer.Option(30000, "--max-tokens", help="Maximum tokens allowed in bundle"),
    format: str = typer.Option("markdown", "--format", help="Output format (markdown, xml, plain)"),
    semantic: bool = typer.Option(False, "--semantic", help="Use semantic search"),
    count_tokens_flag: bool = typer.Option(False, "--count-tokens", help="Only show token count")
):
    """Generate context for a task."""

    if needs_update():
        build_index()

    idx = load_index()
    if not idx:
        console.print("[red]Index not found. Run `contextkit index` first.[/red]")
        raise typer.Exit(1)

    num_files = len(idx["files"])
    num_symbols = sum(len(d.get("symbols", [])) for d in idx["files"].values())

    # 1. Relevance
    scores = score_relevance(task, idx, use_semantic=semantic)

    # 2. Seed files
    seed_files = []
    if files:
        for f in files:
            # allow partial matches
            matches = [path for path in scores if f in path]
            seed_files.extend(matches)
    else:
        # Top 3 highest scoring files as seeds
        sorted_files = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        seed_files = [f for f, s in sorted_files[:3] if s > 0.0]

    if not seed_files:
        console.print("[yellow]No relevant files found for this task.[/yellow]")
        raise typer.Exit()

    # 3. Resolve
    resolved = resolve_dependencies(seed_files, idx.get("edges", []), scores)

    # 4. Bundle
    bundle_items = build_bundle(resolved, seed_files, scores, max_tokens)

    formatted = format_bundle(bundle_items, format_type=format)
    tokens = count_bundle_tokens(bundle_items, format_type=format)

    # Rough baseline full codebase tokens
    total_tokens_est = num_files * 1000 # Very rough estimate for display
    reduction = max(0, int((1 - (tokens / total_tokens_est)) * 100)) if total_tokens_est > 0 else 0

    if count_tokens_flag:
        console.print(f"{tokens}")
        raise typer.Exit()

    # Output to user
    console.print("\nContextKit — Context Builder")
    console.print("──────────────────────────────────────────────────")
    console.print(f"✦ Task                \"{task}\"")
    console.print(f"✦ Index size          {num_symbols:,} symbols, {num_files} files\n")

    console.print("  Resolving relevant files...")
    for f in resolved:
        if f in bundle_items:
            console.print(f"  [green]✓ {f}[/green]")
        else:
            console.print(f"  [red]✗ {f} (excluded — budget/relevance)[/red]")

    num_bundle_files = len(bundle_items)
    num_lines = len(formatted.splitlines())

    console.print(f"\n✦ Context bundle      {num_bundle_files} files, {num_lines:,} lines")
    console.print(f"✦ Token estimate      ~{tokens:,} tokens (vs {total_tokens_est:,} full codebase)")
    console.print(f"✦ Reduction           {reduction}% fewer tokens\n")

    if copy:
        pyperclip.copy(formatted)
        console.print("  [blue]Copied to clipboard ✓[/blue]")

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(formatted)
        console.print(f"  [blue]Written to {output} ✓[/blue]")

    console.print("──────────────────────────────────────────────────")
    console.print("Paste into Claude/Cursor/ChatGPT and ask your question.\n")

@app.command()
def show():
    """Show what's in the current index."""
    idx = load_index()
    if not idx:
        console.print("[red]Index not found. Run `contextkit index` first.[/red]")
        raise typer.Exit(1)

    console.print(f"Index last updated: {idx.get('indexed_at')}")
    console.print(f"Indexed files: {len(idx.get('files', {}))}")

if __name__ == "__main__":
    app()
