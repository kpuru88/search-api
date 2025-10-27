#!/usr/bin/env python3
"""Command-line product search using Parallel AI Task API."""
import argparse
import json
import os
import sys
import time
from dotenv import load_dotenv
from parallel import Parallel

load_dotenv()

# Configuration
PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY")
if not PARALLEL_API_KEY:
    raise ValueError("PARALLEL_API_KEY environment variable is required")


def run_search(
    query: str,
    processor: str = "base",
    output_format: str = "pretty",
    max_wait_time: float = 300.0,
    poll_interval: float = 2.0
) -> dict:
    """
    Run a product search query using Parallel AI Task API.
    
    Args:
        query: Search query (e.g., "black couch")
        processor: Processor to use (base, pro, core)
        output_format: Output format (json, pretty)
        max_wait_time: Maximum time to wait for results
        poll_interval: Time between status checks
        
    Returns:
        Task result dictionary
    """
    client = Parallel(api_key=PARALLEL_API_KEY)
    
    print(f"Searching for: {query}", file=sys.stderr)
    print(f"Processor: {processor}", file=sys.stderr)
    print(f"Please wait...\n", file=sys.stderr)
    
    try:
        # 1. Create task run with structured output schema
        print(f"Creating task...", file=sys.stderr)
        task_run = client.task_run.create(
            input=f"Find the best matching products for: {query}. Return multiple product options.",
            processor=processor,
            task_spec={
                "output_schema": {
                    "type": "json",
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The original search query"
                            },
                            "matched_products": {
                                "type": "array",
                                "description": "List of matching products",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "Unique product identifier"
                                        },
                                        "title": {
                                            "type": "string",
                                            "description": "Product title or name"
                                        },
                                        "price": {
                                            "type": "number",
                                            "description": "Product price"
                                        },
                                        "currency": {
                                            "type": "string",
                                            "description": "Currency code (e.g., USD, EUR)"
                                        },
                                        "url": {
                                            "type": "string",
                                            "description": "Product URL"
                                        }
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
        
        run_id = task_run.run_id
        print(f"✓ Task created: {run_id}", file=sys.stderr)
        
        # 2. Poll for completion
        elapsed = 0.0
        while elapsed < max_wait_time:
            status = client.task_run.retrieve(run_id)
            
            if status.status == "completed":
                print(f"Search completed!\n", file=sys.stderr)
                
                # 3. Get result
                result = client.task_run.result(run_id)
                
                # Extract output content (should be JSON)
                output_content = result.output
                if hasattr(output_content, 'content'):
                    output_data = output_content.content
                else:
                    output_data = output_content
                
                # Try to parse as JSON if it's a string
                if isinstance(output_data, str):
                    try:
                        import json as json_module
                        output_data = json_module.loads(output_data)
                    except:
                        pass
                
                return {
                    "run_id": run_id,
                    "status": status.status,
                    "output": output_data
                }
            
            elif status.status == "failed":
                error = getattr(status, 'error', 'Unknown error')
                print(f"Task failed: {error}", file=sys.stderr)
                sys.exit(1)
            
            elif status.status in ["cancelled", "cancelling"]:
                print(f"Task was cancelled", file=sys.stderr)
                sys.exit(1)
            
            # Still running
            print(f"⏳ Status: {status.status}...", file=sys.stderr)
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        # Timeout
        print(f"Timeout: Task did not complete within {max_wait_time}s", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


def format_output(result: dict, format_type: str = "pretty") -> str:
    """
    Format the result for display.
    
    Args:
        result: Task result dictionary
        format_type: Output format (json, pretty)
        
    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(result, indent=2)
    
    # Pretty format
    output = []
    output.append("=" * 70)
    output.append("SEARCH RESULTS")
    output.append("=" * 70)
    
    data = result.get('output', {})
    
    # If output is structured JSON with our schema (multiple products)
    if isinstance(data, dict) and 'matched_products' in data:
        output.append(f"\n🔍 Query: {data.get('query', 'N/A')}")
        
        products = data.get('matched_products', [])
        output.append(f"📊 Found {len(products)} product(s)")
        output.append("\n" + "-" * 70)
        
        for idx, product in enumerate(products, 1):
            output.append(f"\n✅ Product {idx}:")
            output.append(f"   Title:    {product.get('title', 'N/A')}")
            output.append(f"   ID:       {product.get('id', 'N/A')}")
            output.append(f"   Price:    {product.get('price', 'N/A')} {product.get('currency', '')}")
            output.append(f"   URL:      {product.get('url', 'N/A')}")
            if idx < len(products):
                output.append("")  # Empty line between products
    else:
        # Fallback for other output formats
        output.append(f"\nRun ID: {result.get('run_id', 'N/A')}")
        output.append(f"Status: {result.get('status', 'N/A')}")
        output.append("\n" + "-" * 70)
        output.append("\nOutput:")
        output.append(str(data))
    
    output.append("\n" + "=" * 70)
    return "\n".join(output)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Product search using Parallel AI Task API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "black couch"
  %(prog)s --query "gaming laptop under $1500" --processor pro
  %(prog)s -q "wireless headphones" --format json
  %(prog)s -q "standing desk" --timeout 120
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        required=True,
        help="Search query (e.g., 'black couch')"
    )
    
    parser.add_argument(
        "-p", "--processor",
        type=str,
        default="base",
        choices=["base", "pro", "core"],
        help="Processor to use (default: base)"
    )
    
    parser.add_argument(
        "-f", "--format",
        type=str,
        default="pretty",
        choices=["json", "pretty"],
        help="Output format (default: pretty)"
    )
    
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=300.0,
        help="Maximum wait time in seconds (default: 300)"
    )
    
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Polling interval in seconds (default: 2)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 2.0.0"
    )
    
    args = parser.parse_args()
    
    # Run the search
    result = run_search(
        query=args.query,
        processor=args.processor,
        output_format=args.format,
        max_wait_time=args.timeout,
        poll_interval=args.poll_interval
    )
    
    # Output the result
    print(format_output(result, args.format))


if __name__ == "__main__":
    main()
