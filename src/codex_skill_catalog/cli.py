from __future__ import annotations

import argparse
from pathlib import Path

from .render import render_markdown
from .scanner import scan_catalog


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="codex-skill-catalog",
        description="Generate a local Markdown and JSON catalog for Codex-style skills.",
    )
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        help="Skill root to scan. Can be passed multiple times. Default: ~/.codex/skills",
    )
    parser.add_argument(
        "--config",
        default="~/.codex/config.toml",
        help="Config TOML to inspect for section names. Default: ~/.codex/config.toml",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="CODEX_SKILL_CATALOG.md",
        help="Markdown output path.",
    )
    parser.add_argument("--json", default="", help="Optional JSON inventory output path.")
    parser.add_argument(
        "--title",
        default="Codex Skill Catalog",
        help="Markdown report title.",
    )
    parser.add_argument("--print", action="store_true", help="Print Markdown report to stdout.")
    args = parser.parse_args()

    roots = args.root or ["~/.codex/skills"]
    catalog = scan_catalog(roots, config_path=args.config)
    markdown = render_markdown(catalog, title=args.title)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")

    if args.json:
        json_output = Path(args.json)
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(catalog.to_json(), encoding="utf-8")

    if args.print:
        print(markdown)
    else:
        print(f"Wrote Markdown catalog to {output}")
        if args.json:
            print(f"Wrote JSON inventory to {args.json}")
        print(f"Found {len(catalog.skills)} skills across {len(catalog.roots)} root(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
