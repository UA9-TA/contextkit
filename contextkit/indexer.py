import ast
import json
from datetime import datetime, timezone
from pathlib import Path

from contextkit.config import get_index_path, get_project_root


class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.symbols = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.symbols.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.symbols.append(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.symbols.append(node.name)
        self.generic_visit(node)

def index_file(filepath: Path, root_dir: Path) -> dict:
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = len(content.splitlines())

        try:
            tree = ast.parse(content, filename=str(filepath))
            visitor = CodeVisitor()
            visitor.visit(tree)

            return {
                "imports": list(set(visitor.imports)),
                "symbols": list(set(visitor.symbols)),
                "lines": lines
            }
        except SyntaxError:
            return {"imports": [], "symbols": [], "lines": lines, "error": "SyntaxError"}
    except Exception as e:
         return {"imports": [], "symbols": [], "lines": 0, "error": str(e)}

def _resolve_import_to_path(imp: str, all_py_files: list[str], root_dir: Path) -> str | None:
    # A simplified resolver. For "auth.models", it looks for "auth/models.py" or "auth/models/__init__.py"
    parts = imp.split('.')
    path_str = "/".join(parts) + ".py"
    if path_str in all_py_files:
        return path_str

    path_dir_str = "/".join(parts) + "/__init__.py"
    if path_dir_str in all_py_files:
        return path_dir_str

    return None

def build_index(start_path: str = ".") -> dict:
    root = get_project_root(start_path)

    # Exclude certain directories
    excludes = {".git", "__pycache__", "venv", ".venv", "env", "node_modules", "build", "dist"}

    files_data = {}
    py_files = []

    for py_file in root.rglob("*.py"):
        if any(part in excludes for part in py_file.parts):
            continue
        rel_path = str(py_file.relative_to(root))
        py_files.append(rel_path)
        files_data[rel_path] = index_file(py_file, root)

    edges = set()
    for rel_path, data in files_data.items():
        for imp in data.get("imports", []):
            resolved = _resolve_import_to_path(imp, py_files, root)
            if resolved:
                edges.add((rel_path, resolved))

    index_data = {
        "files": files_data,
        "edges": list(edges),
        "indexed_at": datetime.now(timezone.utc).isoformat()
    }

    index_path = get_index_path(start_path)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)

    return index_data

def load_index(start_path: str = ".") -> dict | None:
    index_path = get_index_path(start_path)
    if not index_path.exists():
        return None
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)

def needs_update(start_path: str = ".") -> bool:
    idx = load_index(start_path)
    if not idx:
        return True

    indexed_at = datetime.fromisoformat(idx["indexed_at"])
    root = get_project_root(start_path)
    excludes = {".git", "__pycache__", "venv", ".venv", "env", "node_modules", "build", "dist"}

    for py_file in root.rglob("*.py"):
        if any(part in excludes for part in py_file.parts):
            continue
        mtime = datetime.fromtimestamp(py_file.stat().st_mtime, timezone.utc)
        if mtime > indexed_at:
            return True
    return False
