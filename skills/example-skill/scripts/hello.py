#!/usr/bin/env python3
"""Example skill script — a simple greeting generator.

Usage:
    python3 hello.py --name "Agent"
    python3 hello.py --name "Agent" --format json
    python3 hello.py --help
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Generate a greeting. Demonstrates skill script conventions."
    )
    parser.add_argument("--name", required=True, help="Name to greet")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it",
    )

    args = parser.parse_args()

    greeting = f"Hello, {args.name}! This is the example skill."

    if args.dry_run:
        print(f"[DRY RUN] Would greet: {args.name}")
        return

    if args.format == "json":
        print(json.dumps({"greeting": greeting, "name": args.name}))
    else:
        print(greeting)


if __name__ == "__main__":
    main()
