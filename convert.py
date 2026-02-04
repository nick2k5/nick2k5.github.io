#!/usr/bin/env python3
"""Convert Word documents in _word/ to Jekyll markdown posts in _posts/.

Usage: python convert.py

Filename convention for Word docs:
    YYYY-MM-DD-Title of Post.docx
    YYYY-MM-Title of Post.docx     (day defaults to 01)

The script will NOT overwrite existing markdown files. To re-convert a post,
delete the corresponding file in _posts/ first.

Requires: pip install -r requirements.txt (inside a venv)
"""

import os
import re
import sys
import glob

import pypandoc

WORD_DIR = "_word"
POSTS_DIR = "_posts"
MEDIA_DIR = "assets/images"

# Match: YYYY-MM-DD-Title or YYYY-MM-Title
FILENAME_RE = re.compile(
    r"^(\d{4})-(\d{2})(?:-(\d{2}))?-(.+)\.docx$"
)


def slugify(text):
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def find_existing_post(date_str, slug):
    """Check if a post with this date and slug already exists."""
    pattern = os.path.join(POSTS_DIR, f"{date_str}-{slug}.md")
    return glob.glob(pattern)


def convert_docx(docx_path, date_str, title, slug):
    """Convert a .docx file to markdown using pandoc."""
    output_path = os.path.join(POSTS_DIR, f"{date_str}-{slug}.md")

    # Convert with pandoc via pypandoc
    try:
        markdown = pypandoc.convert_file(
            docx_path,
            "markdown",
            format="docx",
            extra_args=[f"--extract-media={MEDIA_DIR}"],
        )
    except RuntimeError as e:
        print(f"  ERROR: pandoc failed: {e}")
        return False

    # Strip pandoc attribute syntax from images: ![alt](src){...} -> ![alt](src)
    markdown = re.sub(r"(!\[[^\]]*\]\([^)]*\))\{[^}]*\}", r"\1", markdown)

    # Make image paths absolute for Jekyll
    markdown = re.sub(r"!\[([^\]]*)\]\(assets/", r"![\1](/assets/", markdown)

    # Remove duplicate title heading and date line that pandoc extracts from the doc body
    # Strip leading heading matching the title
    lines = markdown.split("\n")
    cleaned = []
    skip_next_blank = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Skip a heading that matches the title
        if re.match(r"^#+\s*" + re.escape(title) + r"\s*$", line, re.IGNORECASE):
            skip_next_blank = True
            i += 1
            continue
        # Skip a standalone date-like line (e.g. "February 2026") right after title
        if skip_next_blank and re.match(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$", line):
            i += 1
            continue
        # Skip blank lines immediately after removed lines
        if skip_next_blank and line == "":
            skip_next_blank = False
            i += 1
            continue
        skip_next_blank = False
        cleaned.append(lines[i])
        i += 1
    markdown = "\n".join(cleaned)

    # Build front matter
    front_matter = "---\n"
    front_matter += f"layout: post\n"
    front_matter += f"title: \"{title}\"\n"
    front_matter += f"date: {date_str}\n"
    front_matter += "---\n\n"

    # Write output
    with open(output_path, "w") as f:
        f.write(front_matter)
        f.write(markdown)

    print(f"  -> {output_path}")
    return True


def main():
    if not os.path.isdir(WORD_DIR):
        print(f"No {WORD_DIR}/ directory found.")
        sys.exit(1)

    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(MEDIA_DIR, exist_ok=True)

    docx_files = [f for f in os.listdir(WORD_DIR) if f.endswith(".docx")]

    if not docx_files:
        print(f"No .docx files found in {WORD_DIR}/.")
        return

    converted = 0
    skipped = 0

    for filename in sorted(docx_files):
        match = FILENAME_RE.match(filename)
        if not match:
            print(f"SKIP: {filename} (doesn't match YYYY-MM-DD-Title.docx or YYYY-MM-Title.docx)")
            skipped += 1
            continue

        year, month, day, raw_title = match.groups()
        day = day or "01"
        date_str = f"{year}-{month}-{day}"
        title = raw_title.replace("-", " ").strip()
        slug = slugify(raw_title)

        docx_path = os.path.join(WORD_DIR, filename)

        # Check if already converted
        if find_existing_post(date_str, slug):
            print(f"SKIP: {filename} (markdown already exists)")
            skipped += 1
            continue

        print(f"Converting: {filename}")
        if convert_docx(docx_path, date_str, title, slug):
            converted += 1
        else:
            skipped += 1

    print(f"\nDone. Converted: {converted}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
