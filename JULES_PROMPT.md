# Jules Build Prompt — ContextKit v1.0

## What You Are Building

**ContextKit** is an open-source CLI tool that curates the minimal, maximally relevant code context for AI coding assistants. Instead of dumping your entire codebase into Claude/Copilot/Cursor and hoping it figures out what matters, ContextKit analyzes your task description + git changes and builds a precision-trimmed context bundle — exactly the files, functions, and types the AI needs, nothing it doesn't.

The core problem: AI models degrade significantly past ~130k tokens despite claiming 200k+ context windows. Developers manually decide what to include — usually too much (wastes tokens, introduces noise) or too little (causes hallucinations). ContextKit builds a dependency graph of your codebase and computes the *minimal sufficient context* for any given task, cutting token usage by 60-80% while improving AI output quality.

**Target:** Top GitHub trending. Every developer using any AI coding tool hits context limits daily.

---

## Core User Flow

```bash
# Install
pip install contextkit

# Index your codebase (builds dependency graph, ~10 seconds)
contextkit index

# Generate context for a task — outputs to clipboard or file
contextkit build "fix the JWT token validation bug"
contextkit build "add pagination to the users API endpoint"
contextkit build --files auth/validators.py --task "refactor this module"

# Show what's in the context bundle
contextkit show

# Copy to clipboard (ready to paste into Claude/ChatGPT)
contextkit build "add rate limiting" --copy

# Output as markdown file
contextkit build "add rate limiting" --output context.md

# Show token count estimate
contextkit build "add rate limiting" --count-tokens

# Update index after code changes
contextkit index --update
```

**Output:**
```
ContextKit — Context Builder
──────────────────────────────────────────────────
✦ Task                "fix the JWT token validation bug"
✦ Index size          2,847 symbols, 94 files

  Resolving relevant files...
  ✓ auth/validators.py        (direct match — "JWT", "token", "validation")
  ✓ auth/models.py            (referenced by validators.py)
  ✓ auth/exceptions.py        (imported by validators.py)
  ✓ tests/test_validators.py  (test file for validators.py)
  ✗ payment/processor.py      (excluded — unrelated to JWT)
  ✗ api/routes/*.py           (excluded — no token logic)

✦ Context bundle      4 files, 847 lines
✦ Token estimate      ~11,200 tokens (vs 94,000 full codebase)
✦ Reduction           88% fewer tokens

  Copied to clipboard ✓
──────────────────────────────────────────────────
Paste into Claude/Cursor/ChatGPT and ask your question.
```

---

## Tech Stack

- **Language:** Python 3.10+
- **CLI framework:** Typer + Rich
- **AI:** Anthropic Claude API (`claude-sonnet-4-6`) — for task relevance scoring (optional)
- **AST analysis:** Python `ast` module for import graph + symbol extraction
- **Semantic search:** `sentence-transformers` (local, offline) for file relevance scoring
- **Token counting:** `tiktoken` (OpenAI's tokenizer — works for all major models)
- **Clipboard:** `pyperclip` for cross-platform copy
- **Storage:** Local JSON index (`.contextkit-index.json`)
- **Packaging:** `pyproject.toml` (hatchling), entry point `contextkit`

---

## Project Structure

```
contextkit/
├── contextkit/
│   ├── __init__.py
│   ├── cli.py              # Typer app — index, build, show, config
│   ├── indexer.py          # Builds dependency graph + symbol map from codebase
│   ├── relevance.py        # Scores files by relevance to task description
│   ├── graph_resolver.py   # Walks import graph to pull in transitive dependencies
│   ├── bundle_builder.py   # Assembles final context bundle with token budget
│   ├── token_counter.py    # Estimates token count using tiktoken
│   ├── formatter.py        # Formats bundle as markdown, XML, or plain text
│   ├── display.py          # Rich terminal output
│   └── config.py           # Config file reader/writer
├── tests/
│   ├── test_indexer.py
│   ├── test_relevance.py
│   ├── test_graph_resolver.py
│   ├── test_bundle_builder.py
│   └── fixtures/
│       ├── sample_project/       # Small fake Python project for testing
│       │   ├── auth/
│       │   │   ├── validators.py # References models.py and exceptions.py
│       │   │   ├── models.py
│       │   │   └── exceptions.py
│       │   ├── payment/
│       │   │   └── processor.py  # Unrelated to auth — should be excluded
│       │   └── tests/
│       │       └── test_validators.py
│       └── expected_bundle.md    # Expected output for "fix JWT bug" task on sample_project
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
└── README.md
```

---

## Detailed Module Specs

### `indexer.py` — Codebase indexing
Walk all `.py` files, for each file extract:
- All imports (absolute + relative) — builds dependency edges
- All function/class/type definitions — builds symbol map
- File summary: line count, last modified, primary symbols

Store as `.contextkit-index.json`:
```json
{
  "files": {
    "auth/validators.py": {
      "imports": ["auth.models", "auth.exceptions"],
      "symbols": ["validate_token", "check_expiry"],
      "lines": 89
    }
  },
  "edges": [["auth/validators.py", "auth/models.py"], ...],
  "indexed_at": "2026-05-15T08:00:00Z"
}
```

Auto-rebuild if any source file is newer than the index.

### `relevance.py` — Task-to-file relevance scoring
Two strategies (use both, combine scores):

**Keyword matching (fast, offline):**
- Extract keywords from task description (e.g., "JWT", "token", "validation")
- Score each file by keyword frequency in: filename, function names, comments, string literals
- Normalize 0.0–1.0

**Semantic similarity (optional, slower):**
- Use `sentence-transformers` (all-MiniLM-L6-v2, tiny model) to embed task description
- Embed each file's symbol names + docstrings
- Cosine similarity → relevance score
- Only used if `--semantic` flag passed (opt-in, requires model download on first run)

### `graph_resolver.py` — Transitive dependency resolution
Given a seed set of relevant files:
1. Walk the import graph (BFS, max depth 3)
2. Include all files that the seed files directly import
3. Exclude: stdlib modules, site-packages, files with relevance score < 0.1
4. Always include: test files corresponding to seed files

### `bundle_builder.py` — Context assembly
Token budget: default 30,000 tokens (configurable with `--max-tokens`).
Priority order for inclusion:
1. Files with relevance score > 0.8 (always include, full content)
2. Transitive dependencies (include, truncated to relevant functions only)
3. Test files for seed files (include, full content)
4. Low-relevance transitive deps (include just function signatures, not bodies)

### `formatter.py` — Output formatting
Three formats (configurable):
- `markdown` (default): fenced code blocks with file paths as headers
- `xml`: `<file path="..."><content>...</content></file>` (better for some models)
- `plain`: just file contents concatenated with separator comments

---

## README Spec

1. **Hero** — badges + one-liner: *"AI models degrade past 130k tokens. ContextKit keeps you under 30k — without losing what matters."*
2. **The problem** — dumping your whole codebase into Claude. The AI hallucinates because there's too much noise.
3. **Demo** — `<!-- Add demo.gif here -->`
4. **Install** — `pip install contextkit`
5. **Quick start** — `contextkit index && contextkit build "your task" --copy`
6. **Sample output** — exact Rich output from above, showing 88% token reduction
7. **How it works** — 4 steps: index → score relevance → walk dependency graph → bundle
8. **Supported models** — works with Claude, ChatGPT, Cursor, Copilot, Gemini (any AI tool)
9. **Token reduction benchmarks** — table: small project 60% reduction, medium project 80%, large project 88%
10. **Configuration** — max tokens, output format, semantic mode
11. **Contributing / License**

---

## `pyproject.toml`

```toml
[project]
name = "contextkit"
version = "0.1.0"
description = "Build minimal, maximally relevant code context bundles for AI coding assistants"
authors = [{name = "UA9-TA", email = "vkrmsatsangi@gmail.com"}]
keywords = ["ai", "context", "llm", "developer-tools", "cli", "cursor", "copilot", "claude"]
dependencies = [
    "typer>=0.12", "rich>=13", "anthropic>=0.25",
    "tiktoken>=0.6", "pyperclip>=1.8",
    "tomli>=2.0; python_version < '3.11'",
]
[project.optional-dependencies]
dev = ["pytest", "ruff", "pytest-mock", "pytest-cov"]
semantic = ["sentence-transformers>=2.7"]
[project.scripts]
contextkit = "contextkit.cli:app"
[project.urls]
Homepage = "https://github.com/UA9-TA/contextkit"
Changelog = "https://github.com/UA9-TA/contextkit/blob/main/CHANGELOG.md"
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--ignore=tests/fixtures"
[tool.ruff]
line-length = 100
target-version = "py310"
[tool.ruff.lint]
select = ["E", "F", "W", "I"]
ignore = ["E501"]
```

Note: `sentence-transformers` is an optional extra — don't require it for basic functionality.

---

## Fixtures

### `tests/fixtures/sample_project/`
A small Python project (4 files, ~200 lines total) with clear dependency relationships.
`auth/validators.py` imports from `auth/models.py` and `auth/exceptions.py`.
`payment/processor.py` is completely unrelated to auth.

### `tests/fixtures/expected_bundle.md`
The expected markdown output when running `contextkit build "fix JWT validation bug"` on the sample project. Tests use this as the ground truth.

---

## Definition of Done

- [ ] `contextkit index` builds index from `tests/fixtures/sample_project/`
- [ ] `contextkit build "fix JWT validation bug"` includes auth files, excludes payment files
- [ ] Token count estimate is computed and shown
- [ ] `--copy` flag copies to clipboard (mock `pyperclip` in tests)
- [ ] `--output context.md` writes markdown file
- [ ] Bundle respects `--max-tokens` limit
- [ ] Index auto-updates when source files are newer
- [ ] CI passes on Python 3.10, 3.11, 3.12
- [ ] ruff passes

## Repo Details
- GitHub: https://github.com/UA9-TA/contextkit
- Local path: /Users/chitra/Documents/Projects/contextkit
- Branch: main — License: MIT
