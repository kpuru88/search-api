# Product Search Evaluation

Evaluate and compare product search APIs using AI-powered judging.

---

## Overview

This project compares **Parallel AI Task Search (PWS)** and **Exa Search**, using an **AI Judge** to score results for relevance, price accuracy, and product quality.

---

## Files

- `pws_search.py` – Parallel AI Task API (structured product data)
- `exa_search.py` – Exa web search (fast content extraction)
- `relevance_judge.ipynb` – AI-powered evaluation notebook
- `evals/product_search_rubric.json` – Evaluation criteria
- `pyproject.toml` – Project dependencies (uses `uv`)

---

## Quick Start

```bash
# 1. Set up API keys
echo "PARALLEL_API_KEY=your_parallel_key" > .env
echo "EXA_API_KEY=your_exa_key" >> .env
echo "OPENAI_API_KEY=your_openai_key" >> .env   # required for AI judge

# 2. Install uv (Python 3.13+)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync

# 4. Run searches
uv run python pws_search.py -q "black couch"
uv run python exa_search.py -q "black couch"

# 5. Compare both APIs (CSV or JSON)
uv run python compare_search.py -q "black couch"
uv run python compare_search.py -q "headphones" --json

# 6. Evaluate with AI judge
jupyter notebook relevance_judge.ipynb
