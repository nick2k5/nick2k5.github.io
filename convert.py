#!/usr/bin/env python3
"""Convert Word documents to Jekyll markdown posts and drafts.

Usage: python convert.py

Posts (in _word/posts/):
    Filename: YYYY-MM-DD-Title of Post.docx or YYYY-MM-Title of Post.docx
    Output: _posts/YYYY-MM-DD-title-of-post.md
    Layout: post (includes date display)

Drafts (in _word/drafts/):
    Filename: Title of Draft.docx (no date prefix needed)
    Output: _ideas/title-of-draft.md
    Layout: draft (no date display)

The script will NOT overwrite existing markdown files. To re-convert,
delete the corresponding output file first.

Requires: pip install -r requirements.txt (inside a venv)
"""

import os
import re
import sys
import glob

import pypandoc

POSTS_WORD_DIR = "_word/posts"
DRAFTS_WORD_DIR = "_word/drafts"
POSTS_DIR = "_posts"
IDEAS_DIR = "_ideas"
MEDIA_DIR = "assets/images"

# Match: YYYY-MM-DD-Title or YYYY-MM-Title
POST_FILENAME_RE = re.compile(
    r"^(\d{4})-(\d{2})(?:-(\d{2}))?-(.+)\.docx$"
)


def slugify(text):
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def find_existing_file(directory, filename):
    """Check if a file already exists."""
    path = os.path.join(directory, filename)
    return os.path.exists(path)


def convert_docx(docx_path, output_path, title, front_matter):
    """Convert a .docx file to markdown using pandoc."""
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

    # Write output
    with open(output_path, "w") as f:
        f.write(front_matter)
        f.write(markdown)

    print(f"  -> {output_path}")
    return True


def convert_posts():
    """Convert Word docs in _word/posts/ to Jekyll posts."""
    if not os.path.isdir(POSTS_WORD_DIR):
        return 0, 0

    os.makedirs(POSTS_DIR, exist_ok=True)

    docx_files = [f for f in os.listdir(POSTS_WORD_DIR) if f.endswith(".docx")]
    converted = 0
    skipped = 0

    for filename in sorted(docx_files):
        match = POST_FILENAME_RE.match(filename)
        if not match:
            print(f"SKIP: {filename} (doesn't match YYYY-MM-DD-Title.docx or YYYY-MM-Title.docx)")
            skipped += 1
            continue

        year, month, day, raw_title = match.groups()
        day = day or "01"
        date_str = f"{year}-{month}-{day}"
        title = raw_title.replace("-", " ").strip()
        slug = slugify(raw_title)

        output_filename = f"{date_str}-{slug}.md"
        output_path = os.path.join(POSTS_DIR, output_filename)
        docx_path = os.path.join(POSTS_WORD_DIR, filename)

        # Check if already converted
        if find_existing_file(POSTS_DIR, output_filename):
            print(f"SKIP: {filename} (markdown already exists)")
            skipped += 1
            continue

        front_matter = "---\n"
        front_matter += f"layout: post\n"
        front_matter += f"title: \"{title}\"\n"
        front_matter += f"date: {date_str}\n"
        front_matter += "---\n\n"

        print(f"Converting post: {filename}")
        if convert_docx(docx_path, output_path, title, front_matter):
            converted += 1
        else:
            skipped += 1

    return converted, skipped


def convert_drafts():
    """Convert Word docs in _word/drafts/ to Jekyll drafts (ideas collection)."""
    if not os.path.isdir(DRAFTS_WORD_DIR):
        return 0, 0

    os.makedirs(IDEAS_DIR, exist_ok=True)

    docx_files = [f for f in os.listdir(DRAFTS_WORD_DIR) if f.endswith(".docx")]
    converted = 0
    skipped = 0

    for filename in sorted(docx_files):
        # Strip optional date prefix from draft filenames
        raw_title = filename[:-5]  # Remove .docx
        date_match = POST_FILENAME_RE.match(filename)
        if date_match:
            # Has date prefix - extract just the title part
            raw_title = date_match.group(4)
        title = raw_title.replace("-", " ").strip()
        slug = slugify(raw_title)

        output_filename = f"{slug}.md"
        output_path = os.path.join(IDEAS_DIR, output_filename)
        docx_path = os.path.join(DRAFTS_WORD_DIR, filename)

        # Check if already converted
        if find_existing_file(IDEAS_DIR, output_filename):
            print(f"SKIP: {filename} (markdown already exists)")
            skipped += 1
            continue

        front_matter = "---\n"
        front_matter += f"layout: draft\n"
        front_matter += f"title: \"{title}\"\n"
        front_matter += f"permalink: /drafts/{slug}.html\n"
        front_matter += "---\n\n"

        print(f"Converting draft: {filename}")
        if convert_docx(docx_path, output_path, title, front_matter):
            converted += 1
        else:
            skipped += 1

    return converted, skipped


def main():
    posts_exist = os.path.isdir(POSTS_WORD_DIR)
    drafts_exist = os.path.isdir(DRAFTS_WORD_DIR)

    if not posts_exist and not drafts_exist:
        print(f"No {POSTS_WORD_DIR}/ or {DRAFTS_WORD_DIR}/ directory found.")
        sys.exit(1)

    os.makedirs(MEDIA_DIR, exist_ok=True)

    posts_converted, posts_skipped = convert_posts()
    drafts_converted, drafts_skipped = convert_drafts()

    total_converted = posts_converted + drafts_converted
    total_skipped = posts_skipped + drafts_skipped

    if total_converted == 0 and total_skipped == 0:
        print("No .docx files found.")
    else:
        print(f"\nDone. Converted: {total_converted}, Skipped: {total_skipped}")


if __name__ == "__main__":
    main()
