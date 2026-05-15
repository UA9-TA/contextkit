from typing import Any, Dict, List

from rich.console import Console

console = Console()

class Display:
    @staticmethod
    def print_index_result(index_data: Dict[str, Any]):
        num_files = len(index_data.get("files", {}))
        num_symbols = sum(len(f.get("symbols", [])) for f in index_data.get("files", {}).values())
        console.print("[green]Successfully indexed codebase.[/green]")
        console.print(f"Index size: {num_symbols:,} symbols across {num_files:,} files.")

    @staticmethod
    def print_build_result(task: str, index_size_str: str, resolved_files: List[str], bundle_files: int, bundle_lines: int, tokens: int, total_tokens: int, reduction: int):
        console.print("ContextKit — Context Builder")
        console.print("──────────────────────────────────────────────────")
        console.print(f"✦ Task                \"{task}\"")
        console.print(f"✦ Index size          {index_size_str}")
        console.print("")
        console.print("  Resolving relevant files...")
        for f in resolved_files:
             console.print(f"  ✓ {f}")
        console.print("")
        console.print(f"✦ Context bundle      {bundle_files} files, {bundle_lines} lines")
        console.print(f"✦ Token estimate      ~{tokens:,} tokens (vs {total_tokens:,} full codebase)")
        console.print(f"✦ Reduction           {reduction}% fewer tokens")
        console.print("──────────────────────────────────────────────────")
