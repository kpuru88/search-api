#!/usr/bin/env python3
"""Command-line product search using Exa API."""
import argparse
import json
import os
import sys
from dotenv import load_dotenv
from exa_py import Exa

load_dotenv()


def run_search(
    query: str,
    num_results: int = 10,
    output_format: str = "pretty"
) -> dict:
    """
    Run a product search query using Exa API.
    
    Args:
        query: Search query (e.g., "black couch")
        num_results: Number of results to return
        output_format: Output format (json, pretty)
        
    Returns:
        Search result dictionary
    """
    # Get API key
    exa_api_key = os.getenv("EXA_API_KEY")
    if not exa_api_key:
        raise ValueError("EXA_API_KEY environment variable is required")
    
    client = Exa(api_key=exa_api_key)
    
    print(f"Searching for: {query}", file=sys.stderr)
    
    try:
        
        # Search with content extraction
        search_response = client.search_and_contents(
            query,
            num_results=num_results,
            text=True,
            highlights=True
        )
        
        print(f"Search completed!\n", file=sys.stderr)
        
        # Format results to match our schema
        results = []
        for idx, result in enumerate(search_response.results):
            product = {
                "id": result.id or f"result-{idx}",
                "title": result.title or "No title",
                "url": result.url or "",
                "score": result.score if hasattr(result, 'score') else None,
                "published_date": result.published_date if hasattr(result, 'published_date') else None,
                "price": getattr(result, 'price', None) if hasattr(result, 'price') else None,
                "text": result.text[:500] if hasattr(result, 'text') and result.text else None,
                "highlights": result.highlights if hasattr(result, 'highlights') else None
            }
            results.append(product)
        
        # Return first result as "matched_product" for consistency
        matched_product = results[0] if results else None
        
        return {
            "query": query,
            "matched_product": matched_product,
            "all_results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


def format_output(result: dict, format_type: str = "pretty") -> str:
    """
    Format the result for display.
    
    Args:
        result: Search result dictionary
        format_type: Output format (json, pretty)
        
    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(result, indent=2)
    
    # Pretty format
    output = []
    output.append("=" * 70)
    output.append("SEARCH RESULTS (EXA)")
    
    matched = result.get('matched_product')
    if matched:
        output.append("Top Matched Result:")
        output.append(f"Title: {matched.get('title', 'N/A')}")
        output.append(f"ID: {matched.get('id', 'N/A')}")
        output.append(f"URL: {matched.get('url', 'N/A')}")
        if matched.get('score'):
            output.append(f"   Score:    {matched.get('score')}")
        if matched.get('published_date'):
            output.append(f"   Published: {matched.get('published_date')}")
        if matched.get('text'):
            output.append(f"\n   Preview:  {matched.get('text')[:200]}...")
    
    # Show all results summary
    all_results = result.get('all_results', [])
    if len(all_results) > 1:
        output.append("\n" + "-" * 70)
        output.append("\nAll Results:")
        for idx, res in enumerate(all_results[:5], 1):  # Show top 5
            output.append(f"\n   {idx}. {res.get('title', 'No title')}")
            output.append(f"      {res.get('url', 'No URL')}")
    
    output.append("\n" + "=" * 70)
    return "\n".join(output)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Product search using Exa API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            %(prog)s --query "black couch"
            %(prog)s --query "gaming laptop under $1500" --num-results 20
            %(prog)s -q "wireless headphones" --format json
            %(prog)s -q "standing desk"
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        required=True,
        help="Search query (e.g., 'black couch')"
    )
    
    parser.add_argument(
        "-n", "--num-results",
        type=int,
        default=10,
        help="Number of results to return (default: 10)"
    )
    
    parser.add_argument(
        "-f", "--format",
        type=str,
        default="pretty",
        choices=["json", "pretty"],
        help="Output format (default: pretty)"
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
        num_results=args.num_results,
        output_format=args.format
    )
    
    # Output the result
    print(format_output(result, args.format))


if __name__ == "__main__":
    main()

