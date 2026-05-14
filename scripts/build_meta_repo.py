#!/usr/bin/env python3
"""Scaffold auto-updating GitHub meta repositories for any owner."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
UPDATE_TEMPLATE = SKILL_ROOT / "scripts" / "update_meta_template.py"


UPDATE_WORKFLOW = '''name: Update meta repository

on:
  workflow_dispatch:
  schedule:
    - cron: "17 3 * * *"

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Refresh metadata
        env:
          META_INCLUDE_PRIVATE: "false"
          META_GITHUB_TOKEN: ${{ secrets.META_GITHUB_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/update_meta.py

      - name: Commit changes
        run: |
          if [[ -n "$(git status --porcelain)" ]]; then
            git config user.name "github-actions[bot]"
            git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
            git add -A
            git commit -m "chore: refresh meta repository"
            git push
          else
            echo "No metadata changes."
          fi
'''


PAGES_WORKFLOW = '''name: Deploy GitHub Pages

on:
  workflow_dispatch:
  push:
    branches: ["main"]
    paths:
      - "docs/**"
      - ".github/workflows/deploy-pages.yml"

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Configure Pages
        uses: actions/configure-pages@v5
        with:
          enablement: true
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: "./docs"
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
'''


LICENSE = '''MIT License

Copyright (c) 2026 {owner}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


MODES = {
    "atlas": ("project-atlas", "Download-first project atlas for APK, EXE, package, and release asset links."),
    "release": ("release-hub", "Auto-updating release dashboard."),
    "pages": ("pages-hub", "Visual GitHub Pages gallery."),
    "skills": ("skills-hub", "Skill and workflow registry."),
}


def slug_owner(owner: str) -> str:
    return owner.lower().replace("_", "-")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def init_git(repo_dir: Path, commit: bool) -> None:
    if not commit:
        return
    if not (repo_dir / ".git").exists():
        subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True)
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, text=True, stdout=subprocess.PIPE, check=True).stdout.strip()
    if status:
        subprocess.run(["git", "commit", "-m", "Initial auto-updating meta repository"], cwd=repo_dir, check=True)


def build_one(owner: str, output: Path, prefix: str, mode: str, fetch: bool, commit: bool) -> Path:
    suffix, description = MODES[mode]
    repo_name = f"{prefix}-{suffix}"
    repo_dir = output / repo_name
    repo_dir.mkdir(parents=True, exist_ok=True)

    hub_links = {
        "atlas": f"https://github.com/{owner}/{prefix}-project-atlas",
        "release": f"https://github.com/{owner}/{prefix}-release-hub",
        "pages": f"https://github.com/{owner}/{prefix}-pages-hub",
        "skills": f"https://github.com/{owner}/{prefix}-skills-hub",
    }
    config = {
        "owner": owner,
        "mode": mode,
        "title": repo_name,
        "description": description,
        "includePrivate": False,
        "privateOmitted": 0,
        "hubLinks": hub_links,
    }

    (repo_dir / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(UPDATE_TEMPLATE, repo_dir / "scripts" / "update_meta.py")
    write(repo_dir / "meta.config.json", json.dumps(config, ensure_ascii=False, indent=2))
    write(repo_dir / ".github" / "workflows" / "update-meta.yml", UPDATE_WORKFLOW)
    write(repo_dir / ".github" / "workflows" / "deploy-pages.yml", PAGES_WORKFLOW)
    write(repo_dir / "LICENSE", LICENSE.format(owner=owner))

    if fetch:
        subprocess.run([sys.executable, "scripts/update_meta.py"], cwd=repo_dir, check=True)
    else:
        write(repo_dir / "README.md", f"# {repo_name}\n\nRun `python scripts/update_meta.py` to generate this meta repository.\n")

    init_git(repo_dir, commit)
    return repo_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True, help="GitHub owner, user, or organization.")
    parser.add_argument("--output", required=True, help="Directory where meta repositories will be created.")
    parser.add_argument("--prefix", help="Repository name prefix. Defaults to lowercase owner.")
    parser.add_argument("--mode", choices=sorted(MODES), action="append", help="Mode to create. Repeatable; default creates all modes.")
    parser.add_argument("--no-fetch", action="store_true", help="Create scaffolds without fetching GitHub metadata.")
    parser.add_argument("--no-git", action="store_true", help="Do not initialize Git repositories or create commits.")
    args = parser.parse_args()

    output = Path(args.output).expanduser().resolve()
    prefix = args.prefix or slug_owner(args.owner)
    modes = args.mode or ["atlas", "release", "pages", "skills"]
    built = [str(build_one(args.owner, output, prefix, mode, fetch=not args.no_fetch, commit=not args.no_git)) for mode in modes]
    print(json.dumps({"built": built}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
