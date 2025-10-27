# Product Search Evaluation

Evaluate and compare product search APIs using AI-powered judging with LLM agents.

**Components:**
1. **`pws_search.py`** - Parallel AI Task API (structured product data)
2. **`exa_search.py`** - Exa web search (fast content extraction)
3. **`compare_search.py`** - Run both in parallel and compare results
4. **`relevance_judge.ipynb`** - AI-powered evaluation notebook with automated judging


## Quick Start

```bash
# 1. Set up your API keys
echo "PARALLEL_API_KEY=your_parallel_key" > .env
echo "EXA_API_KEY=your_exa_key" >> .env

# 2. Install dependencies
uv sync

# 3. Run searches
uv run python pws_search.py --query "black couch"
uv run python exa_search.py --query "black couch"

# 4. Compare both APIs
uv run python compare_search.py --query "black couch"

# 5. Evaluate search quality with AI judge
jupyter notebook relevance_judge.ipynb
```

## Evaluation with AI Judge

The `relevance_judge.ipynb` notebook provides AI-powered evaluation of search results:

- **Parallel Execution**: Runs both EXA and PWS searches simultaneously
- **Automated Judging**: Uses OpenAI-powered agents to evaluate each result against custom rubrics
- **Criteria-Based Scoring**: Evaluates multiple criteria (relevance, price fit, product match, etc.)
- **Excel Reports**: Generates detailed evaluation reports with scores and reasoning
- **Async Processing**: All evaluations run in parallel for maximum speed

### Rubric Configuration

Edit `evals/product_search_rubric.json` to define evaluation criteria:

```json
{
  "rubrics": [
    {
      "query": "Black couch under $100",
      "criteria": [
        {
          "name": "Color Match",
          "weight": 0.25,
          "score_definitions": { ... }
        }
      ]
    }
  ]
}
```

## Architecture

```
search/
├── pws_search.py              # Parallel AI search
├── exa_search.py              # Exa search
├── compare_search.py          # Compare both APIs
├── relevance_judge.ipynb      # AI evaluation notebook
├── evals/
│   └── product_search_rubric.json  # Evaluation criteria
├── pyproject.toml             # Dependencies
└── .env                       # API keys
```

### Components

- **`pws_search.py`**: Parallel AI Task API search
  - Structured product data with pricing
  - AI-powered search understanding
  - Multiple processor options (base, pro, core)
  - Async task execution with polling

- **`exa_search.py`**: Exa web search
  - Fast web search with content extraction
  - Multiple results with relevance scores
  - Published dates and highlights
  - Synchronous execution

- **`compare_search.py`**: Parallel comparison tool
  - Runs both APIs simultaneously
  - Outputs results to CSV
  - Includes timing for each API
  - Perfect for benchmarking

- **`relevance_judge.ipynb`**: AI-powered evaluation notebook
  - Automated quality assessment using LLM agents
  - Parallel evaluation of all results
  - Custom rubric-based scoring
  - Excel report generation with detailed breakdowns

## What is Parallel AI Task API?

The [Parallel AI Task API v1](https://docs.parallel.ai/api-reference/task-api-v1/create-task-run) is a powerful asynchronous task execution system that:

- **Accepts natural language inputs** - Just describe what you want in plain text
- **Runs asynchronously** - Create a task, get a `run_id`, then poll for results
- **Handles complex workflows** - Can use web search, MCP servers, and other tools automatically
- **Supports multiple processors** - Choose speed vs. quality tradeoffs (base, pro, core)
- **Tracks progress** - Optional event streaming to monitor task execution

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)

### Setup

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create `.env` file:
```bash
echo "PARALLEL_API_KEY=your_parallel_key" > .env
echo "EXA_API_KEY=your_exa_key" >> .env
echo "OPENAI_API_KEY=your_openai_key" >> .env  # For AI judge
```

3. Install dependencies:
```bash
uv sync
```

This will:
- Install Python 3.13 (if needed)
- Create a virtual environment at `.venv`
- Install all dependencies from `pyproject.toml`

## Usage

### 1. Parallel AI Search (PWS)

```bash
uv run python pws_search.py --query "black couch"
uv run python pws_search.py -q "gaming laptop" --processor pro --format json
```

### 2. Exa Search

```bash
uv run python exa_search.py --query "black couch"
uv run python exa_search.py -q "wireless headphones" --num-results 20
```

### 3. Compare Both APIs (Parallel Execution)

```bash
# Run both searches in parallel and save to CSV
uv run python compare_search.py --query "black couch"

# IMPORTANT: Always use quotes around the query!
uv run python compare_search.py --query "iphone under 200"

# Custom output file
uv run python compare_search.py -q "gaming laptop" -o my_results.csv

# Get full JSON output instead of CSV
uv run python compare_search.py -q "headphones" --json
```


**pws_search.py:**
- `-q, --query` (required) - Search query
- `-p, --processor` - Processor: `base` (default), `pro`, `core`
- `-f, --format` - Output: `pretty` (default), `json`
- `-t, --timeout` - Max wait time in seconds (default: 300)

**exa_search.py:**
- `-q, --query` (required) - Search query
- `-n, --num-results` - Number of results (default: 10)
- `-f, --format` - Output: `pretty` (default), `json`

**compare_search.py:**
- `-q, --query` (required) - Search query
- `-o, --output` - Output CSV file (default: search_comparison.csv)
- `-p, --processor` - PWS processor (default: base)
- `-n, --num-results` - Exa results count (default: 10)
- `--json` - Output full JSON instead of CSV

## Example Queries

The APIs understand natural language, so you can be descriptive:

```bash
# Simple product name
uv run python pws_search.py -q "wireless headphones"

# With specifications
uv run python pws_search.py -q "gaming laptop with RTX 4070 under $1500"

# Comparative queries
uv run python compare_search.py -q "iPhone 15 Pro vs Samsung S24 Ultra"

# Best/top queries
uv run python exa_search.py -q "best noise-cancelling headphones under $300"

# Detailed specifications
uv run python pws_search.py -q "ergonomic office chair with lumbar support"

# Multiple criteria
uv run python compare_search.py -q "4K monitor 27 inch with high refresh rate"
```

### Tips for Better Results

1. **Be specific** - More details = better results
2. **Use natural language** - The AI understands conversational queries
3. **Include constraints** - Price ranges, features, brands, etc.
4. **Try different processors**:
   - `base` - Fast and cost-effective (default)
   - `pro` - More thorough research
   - `core` - Balanced approach

## Output Formats

The search returns structured data with the following schema:

```json
{
  "query": "black couch",
  "matched_products": [
    {
      "id": "sofa-ikea-kivik-black",
      "title": "IKEA KIVIK Sofa (Black)",
      "price": 699.0,
      "currency": "USD",
      "url": "https://ikea.com/couch/..."
    },
    {
      "id": "sofa-west-elm-harmony",
      "title": "West Elm Harmony Sofa (Black)",
      "price": 1299.0,
      "currency": "USD",
      "url": "https://westelm.com/..."
    }
  ]
}
```

### Pretty Format (Default)

```
======================================================================
SEARCH RESULTS
======================================================================

🔍 Query: black couch
📊 Found 2 product(s)

----------------------------------------------------------------------

✅ Product 1:
   Title:    IKEA KIVIK Sofa (Black)
   ID:       sofa-ikea-kivik-black
   Price:    699.0 USD
   URL:      https://ikea.com/couch/...

✅ Product 2:
   Title:    West Elm Harmony Sofa (Black)
   ID:       sofa-west-elm-harmony
   Price:    1299.0 USD
   URL:      https://westelm.com/...

======================================================================
```

### JSON Format

```bash
uv run python pws_search.py -q "wireless headphones" --format json
uv run python exa_search.py -q "wireless headphones" --format json
```

Returns the raw JSON structure with `run_id`, `status`, and `output` fields.

## Advanced Usage

### Using the Python SDK Directly

```python
import os
from parallel import Parallel

client = Parallel(api_key=os.getenv("PARALLEL_API_KEY"))

# Create task with structured output schema (returns multiple products)
task_run = client.task_run.create(
    input="Find the best matching products for: black couch",
    processor="base",
    task_spec={
        "output_schema": {
            "type": "json",
            "json_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "matched_products": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "price": {"type": "number"},
                                "currency": {"type": "string"},
                                "url": {"type": "string"}
                            },
                            "required": ["id", "title", "price", "currency", "url"]
                        }
                    }
                },
                "required": ["query", "matched_products"]
            }
        }
    }
)

# Get result
result = client.task_run.result(run_id=task_run.run_id)
print(result.output)
```

For more information, see the [Parallel SDK documentation](https://pypi.org/project/parallel-web/) and [Task API documentation](https://docs.parallel.ai/api-reference/task-api-v1/create-task-run)

### Shell Aliases (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias pws='cd /path/to/search && uv run python pws_search.py --query'
alias exa='cd /path/to/search && uv run python exa_search.py --query'
alias compare='cd /path/to/search && uv run python compare_search.py --query'
```

Then use:
```bash
pws "wireless headphones"
exa "wireless headphones"
compare "wireless headphones"
```

## Configuration

Configuration is loaded from `.env`:
- `PARALLEL_API_KEY` - Your Parallel AI API key (required for PWS)
- `EXA_API_KEY` - Your Exa API key (required for Exa search)
- `OPENAI_API_KEY` - Your OpenAI API key (required for AI judge)
- Poll interval: 2 seconds (configurable via `--poll-interval`)
- Timeout: 300 seconds (configurable via `--timeout`)

## Dependencies

Core dependencies:
- **parallel-web** - Official Parallel AI SDK
- **exa-py** - Exa search SDK
- **agents** - OpenAI agents framework (for evaluation)
- **pydantic** - Data validation (for structured outputs)
- **pandas** - Data processing (for Excel reports)
- **openpyxl** - Excel file generation
- **python-dotenv** - Environment variable management

## Why Task API?

The Task API provides several advantages over direct API calls:

1. **Natural Language** - No need to structure complex queries
2. **Automatic Tool Use** - Handles web search, extraction, etc. automatically
3. **Asynchronous** - Better for long-running operations
4. **Unified Interface** - One API for all task types
5. **Progress Tracking** - Know what's happening during execution



## Troubleshooting

### "PARALLEL_API_KEY environment variable is required"
Make sure you have a `.env` file with your API key:
```bash
echo "PARALLEL_API_KEY=your_actual_key" > .env
```

### "Task run did not complete within Xs"
Increase the timeout:
```bash
uv run python pws_search.py -q "your query" --timeout 600  # 10 minutes
```

### Python version issues
Ensure Python 3.13+ is installed:
```bash
uv python install 3.13
```

## Reference

- [Parallel AI Task API Documentation](https://docs.parallel.ai/api-reference/task-api-v1/create-task-run)
- [uv Documentation](https://github.com/astral-sh/uv)
