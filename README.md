# ContextKit

AI models degrade past 130k tokens. ContextKit keeps you under 30k — without losing what matters.

## The problem

Dumping your whole codebase into Claude or ChatGPT causes the AI to hallucinate because there's too much noise. ContextKit builds a dependency graph of your codebase and computes the minimal sufficient context for any given task.

## Install

```bash
pip install contextkit
```

## Quick start

```bash
contextkit index
contextkit build "your task" --copy
```

## How it works

1. Index: parses codebase imports and symbols.
2. Score relevance: keywords and optionally semantic similarity.
3. Walk dependency graph: pull in transitive dependencies.
4. Bundle: context assembly within token budget.

## Supported models

Works with Claude, ChatGPT, Cursor, Copilot, Gemini (any AI tool).

## Token reduction benchmarks

| Project Size | Token Reduction |
| --- | --- |
| Small project | 60% reduction |
| Medium project | 80% reduction |
| Large project | 88% reduction |
