import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class Indexer:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.index_file = self.root_dir / ".contextkit-index.json"

    def index(self, update: bool = False) -> Dict[str, Any]:
        if not update and self.index_file.exists():
            with open(self.index_file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    pass

        index_data = {
            "files": {},
            "edges": [],
            "indexed_at": datetime.now(timezone.utc).isoformat()
        }

        for py_file in self.root_dir.rglob("*.py"):
            if ".venv" in py_file.parts or "venv" in py_file.parts or "__pycache__" in py_file.parts or py_file.name.startswith("."):
                continue

            rel_path = py_file.relative_to(self.root_dir).as_posix()
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.splitlines()
            except Exception:
                continue

            imports = []
            symbols = []

            try:
                tree = ast.parse(content, filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module
                            if node.level > 0:
                                parts = list(py_file.relative_to(self.root_dir).parts[:-1])
                                if node.level <= len(parts):
                                    base = ".".join(parts[:-node.level])
                                    if base:
                                        module = f"{base}.{module}"
                            imports.append(module)
                        else:
                            if node.level > 0:
                                parts = list(py_file.relative_to(self.root_dir).parts[:-1])
                                if node.level <= len(parts):
                                    base = ".".join(parts[:-node.level])
                                    if base:
                                        imports.append(base)
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        symbols.append(node.name)
            except SyntaxError:
                pass

            index_data["files"][rel_path] = {
                "imports": list(set(imports)),
                "symbols": symbols,
                "lines": len(lines)
            }

        # Build edges based on imports mapping to relative files
        module_to_file = {}
        for rel_path in index_data["files"]:
            # auth/validators.py -> auth.validators
            module_name = rel_path.replace("/", ".")[:-3]
            if module_name.endswith(".__init__"):
                module_name = module_name[:-9]
            module_to_file[module_name] = rel_path

        edges = set()
        for rel_path, data in index_data["files"].items():
            for imp in data["imports"]:
                if imp in module_to_file:
                    edges.add((rel_path, module_to_file[imp]))
                else:
                    # check for partial match if it's importing a function from a module
                    for mod_name, f_path in module_to_file.items():
                        if imp.startswith(mod_name):
                            edges.add((rel_path, f_path))
                            break

        index_data["edges"] = list(edges)

        with open(self.index_file, "w") as f:
            json.dump(index_data, f, indent=2)

        return index_data
