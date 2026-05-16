# ContextKit

[![PyPI version](https://img.shields.io/pypi/v/contextkit.svg)](https://pypi.org/project/contextkit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> AI models degrade past 130k tokens. ContextKit keeps you under 30k — without losing what matters.

## The Problem

Dumping your whole codebase into Claude or Cursor leads to hallucinations because there's too much noise. The AI has a massive context window, but its attention span still degrades over long contexts. ContextKit extracts the minimal, maximally relevant context for your specific task.

## Demo

<!-- Add demo.gif here -->

## Install

```bash
pip install contextkit
```

## Quick Start

```bash
# Index your codebase (run once, auto-updates)
contextkit index

# Generate context and copy to clipboard
contextkit build "fix the JWT token validation bug" --copy
```

### Output

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

## How it Works

1. **Index**: Builds a local dependency graph + symbol map of your codebase.
2. **Score Relevance**: Scores files by relevance to task description using keyword (and optionally semantic) matching.
3. **Walk Dependency Graph**: Pulls in transitive dependencies for the most relevant files.
4. **Bundle**: Assembles the context bundle within a defined token budget.

## Supported Models

Works with Claude, ChatGPT, Cursor, Copilot, Gemini (any AI tool that accepts text).

## Token Reduction Benchmarks

| Project Size | Reduction |
|---|---|
| Small | 60% |
| Medium | 80% |
| Large | 88% |

## Configuration

You can configure `contextkit build` using CLI arguments:
- `--max-tokens`: Limit token count (default: 30000).
- `--output`: File format (markdown, xml, plain).
- `--semantic`: Opt-in to semantic embedding (requires `sentence-transformers`).

## The Developer Toolkit Ecosystem

This tool is part of a suite of open-source AI-powered developer tools built by the same team:

| Tool | What it does |
|---|---|
| **[RootCause](https://github.com/UA9-TA/rootcause)** | Auto-diagnose failing tests — AI root cause + fix |
| **[ErrorMentor](https://github.com/UA9-TA/errormentor)** | Auto-diagnose production errors — correlate logs with git commits |
| **[TestGap](https://github.com/UA9-TA/testgap)** | Find untested code paths after every commit |
| **[HalluCheck](https://github.com/UA9-TA/hallucheck)** | Catch AI hallucinations in code diffs |
| **[IntentDiff](https://github.com/UA9-TA/intentdiff)** | Understand what a diff *actually* does semantically |
| **[DepSecure](https://github.com/UA9-TA/depsecure)** | Block vulnerable dependencies at commit time |
| **[ArchGuard](https://github.com/UA9-TA/archguard)** | Enforce microservice architecture rules across repos |
| **[SpendSentry](https://github.com/UA9-TA/spendsentry)** | Monitor cloud spend in real time — alert before costs spiral |
| **[ContextKit](https://github.com/UA9-TA/contextkit)** | Build minimal AI context bundles — 88% fewer tokens |

## License

MIT
