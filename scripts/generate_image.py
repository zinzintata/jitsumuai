#!/usr/bin/env python3
"""
Blog eye-catch image generator using gpt-image-2.

Usage:
  python3 scripts/generate_image.py "prompt" --slug article-slug [--type eyecatch|inline] [--size wide|square]

Examples:
  python3 scripts/generate_image.py "AI tools for manufacturing workers, modern flat illustration" --slug chatgpt-gijiroku
  python3 scripts/generate_image.py "digital workflow diagram" --slug chatgpt-gijiroku --type inline --size square
"""

import sys
import os
import base64
import argparse
from pathlib import Path
import datetime

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip3 install openai", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate blog images with gpt-image-2")
    parser.add_argument("prompt", help="Image generation prompt (English recommended)")
    parser.add_argument("--slug", required=True, help="Article slug for organized file naming")
    parser.add_argument("--type", choices=["eyecatch", "inline"], default="eyecatch",
                        help="eyecatch=article hero (1536x1024), inline=in-article (1024x1024)")
    parser.add_argument("--size", choices=["wide", "square"], default=None,
                        help="Override size: wide=1536x1024, square=1024x1024")
    parser.add_argument("--output-dir", default=None,
                        help="Override output directory (default: public/images/blog/[slug]/)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY='sk-...'", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Determine image size
    if args.size == "square" or (args.size is None and args.type == "inline"):
        size = "1024x1024"
        size_label = "square"
    else:
        size = "1536x1024"
        size_label = "wide"

    # Determine output path
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        # Relative to repo root (where this script is run from)
        out_dir = Path("public/images/blog") / args.slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # File name
    if args.type == "eyecatch":
        filename = "eyecatch.png"
    else:
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        filename = f"img_{timestamp}.png"

    out_path = out_dir / filename

    print(f"Generating {size_label} image ({size})...")
    print(f"Prompt: {args.prompt}")

    try:
        result = client.images.generate(
            model="gpt-image-1",
            prompt=args.prompt,
            size=size,
        )
    except Exception as e:
        print(f"ERROR: Image generation failed: {e}", file=sys.stderr)
        sys.exit(1)

    # gpt-image-1 returns b64_json by default
    image_data = result.data[0]
    if hasattr(image_data, 'b64_json') and image_data.b64_json:
        image_bytes = base64.b64decode(image_data.b64_json)
    elif hasattr(image_data, 'url') and image_data.url:
        import urllib.request
        with urllib.request.urlopen(image_data.url) as resp:
            image_bytes = resp.read()
    else:
        print("ERROR: No image data in response", file=sys.stderr)
        sys.exit(1)
    out_path.write_bytes(image_bytes)

    # Output the web path (relative to public/)
    web_path = "/" + str(out_path).replace("public/", "", 1)
    print(f"Saved: {out_path}")
    print(f"Web path: {web_path}")
    print(f"Markdown: ![{args.slug}]({web_path})")
    print(f"Frontmatter: image: \"{web_path}\"")


if __name__ == "__main__":
    main()
