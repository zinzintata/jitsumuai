#!/usr/bin/env python3
"""
Desktop → Blog image importer.

Scans ~/Desktop for PNG/JPG files whose filename matches an article slug,
copies them to public/images/blog/[slug]/eyecatch.png,
and updates the article's frontmatter to add the image path.

Usage:
  python3 scripts/import_desktop_images.py
  python3 scripts/import_desktop_images.py --dry-run   # preview only
"""

import os
import re
import shutil
import argparse
from pathlib import Path

DESKTOP = Path.home() / "Desktop"
CONTENT_DIR = Path("src/content/blog")
PUBLIC_DIR = Path("public/images/blog")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def get_all_slugs():
    """Return set of all article slugs (folder or filename without .md)."""
    slugs = set()
    for f in CONTENT_DIR.glob("*.md"):
        slugs.add(f.stem)
    for d in CONTENT_DIR.iterdir():
        if d.is_dir():
            index = d / "index.md"
            if index.exists():
                slugs.add(d.name)
    return slugs


def get_article_path(slug):
    """Return path to article markdown file."""
    direct = CONTENT_DIR / f"{slug}.md"
    if direct.exists():
        return direct
    index = CONTENT_DIR / slug / "index.md"
    if index.exists():
        return index
    return None


def already_has_image(article_path):
    """Check if article frontmatter already has an image field."""
    content = article_path.read_text(encoding="utf-8")
    in_frontmatter = False
    for line in content.splitlines():
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter and re.match(r"^image\s*:", line):
            return True
    return False


def update_frontmatter_image(article_path, web_path):
    """Insert image field into frontmatter after 'draft:' or before closing ---."""
    content = article_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    in_fm = False
    fm_end = None
    insert_after = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            if not in_fm:
                in_fm = True
            else:
                fm_end = i
                break
        if in_fm:
            if re.match(r"^draft\s*:", stripped):
                insert_after = i

    if fm_end is None:
        print(f"  WARNING: No closing --- found in {article_path.name}")
        return

    image_line = f'image: "{web_path}"\n'

    if insert_after is not None:
        lines.insert(insert_after + 1, image_line)
    else:
        lines.insert(fm_end, image_line)

    article_path.write_text("".join(lines), encoding="utf-8")


def scan_desktop(slugs):
    """Find Desktop image files whose stem matches a known slug."""
    matches = []
    for f in DESKTOP.iterdir():
        if f.suffix.lower() in IMAGE_EXTENSIONS and f.stem in slugs:
            matches.append(f)
    return sorted(matches)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    args = parser.parse_args()

    slugs = get_all_slugs()
    found = scan_desktop(slugs)

    if not found:
        print("Desktopに対象画像が見つかりませんでした。")
        print(f"  ・拡張子: {', '.join(IMAGE_EXTENSIONS)}")
        print(f"  ・ファイル名: 記事スラッグと同じにしてください（例: chatgpt-gijiroku.png）")
        return

    print(f"Desktop で {len(found)} 件の画像を発見:\n")
    processed = []

    for src in found:
        slug = src.stem
        article_path = get_article_path(slug)

        if article_path is None:
            print(f"  ⚠️  {src.name} → 対応記事が見つかりません（スキップ）")
            continue

        dest_dir = PUBLIC_DIR / slug
        dest = dest_dir / "eyecatch.png"
        web_path = f"/images/blog/{slug}/eyecatch.png"

        has_image = already_has_image(article_path)

        print(f"  ✅ {src.name}")
        print(f"     記事: {article_path.name}")
        print(f"     保存先: {dest}")
        print(f"     フロントマター: image: \"{web_path}\"")
        if has_image:
            print(f"     ⚠️  すでに image フィールドあり（上書きします）")
        print()

        if not args.dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if has_image:
                # Replace existing image field
                content = article_path.read_text(encoding="utf-8")
                content = re.sub(r'^image\s*:.*$', f'image: "{web_path}"', content, flags=re.MULTILINE)
                article_path.write_text(content, encoding="utf-8")
            else:
                update_frontmatter_image(article_path, web_path)

        processed.append(slug)

    if args.dry_run:
        print("（dry-run モード: 変更は加えていません）")
        return

    if processed:
        print(f"\n✅ {len(processed)} 件処理完了: {', '.join(processed)}")
        print("\n次のコマンドでデプロイ:")
        print("  git add -A && git commit -m 'Add eyecatch images' && git push")
    else:
        print("処理された画像はありませんでした。")


if __name__ == "__main__":
    main()
