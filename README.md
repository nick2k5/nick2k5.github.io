# nickalexander.org

Personal blog hosted on GitHub Pages with Jekyll.

## Structure

- `_posts/` - Markdown blog posts (never overwritten by the converter)
- `_ideas/` - Markdown drafts (ideas collection, served at `/drafts/`)
- `_word/posts/` - Drop Word docs here for post conversion
- `_word/drafts/` - Drop Word docs here for draft conversion
- `_layouts/` - HTML templates (table-based, Web 1.0 style)
- `assets/images/` - Images extracted from Word docs
- `convert.py` - Word-to-markdown conversion script
- `index.html` - Homepage (manually curated)

## Adding a new post

1. Name your Word doc: `YYYY-MM-DD-Title of Post.docx` or `YYYY-MM-Title of Post.docx` (day defaults to 01 if omitted)
2. Drop it in `_word/posts/`
3. Run `python3 convert.py`
4. Review and edit the generated markdown in `_posts/`
5. To set a custom URL, add `permalink: /my-url.html` to the post's front matter
6. Add a link to the post on `index.html`
7. Commit and push

## Adding a draft

Drafts are ideas or works-in-progress that appear at `/drafts/` URLs without a date displayed.

1. Name your Word doc: `Title of Draft.docx` (no date prefix needed)
2. Drop it in `_word/drafts/`
3. Run `python3 convert.py`
4. Review and edit the generated markdown in `_ideas/`
5. The draft will be available at `/drafts/title-of-draft.html`

To convert a draft to a full post, move the markdown from `_ideas/` to `_posts/`, add a date to the filename and front matter, and change the layout from `draft` to `post`.

## Re-converting

The converter never overwrites existing markdown. To re-convert a post or draft, delete the corresponding file in `_posts/` or `_ideas/` first, then run `python convert.py` again.

## Setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Dependencies

- Python 3
- All Python dependencies (including pandoc) are installed via `requirements.txt`

## Checking build status

After pushing, check if GitHub Pages has finished building:

```
gh api repos/nick2k5/nick2k5.github.io/pages/builds/latest --jq '{status, error}'
```

When `status` shows `"built"`, the site is live.
