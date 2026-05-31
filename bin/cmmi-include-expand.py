#!/usr/bin/env python3
"""cmmi-include-expand — resolve <!-- pycsl-include: ... --> anchors.

Anchor syntax (single-line HTML comment):
    <!-- pycsl-include: source=<path> scope=<tag> -->

The `source=` value is resolved relative to the repository root. The
`scope=` value is metadata only (for audit grep).

Modes:
    cmmi-include-expand.py <file.md>                  # print expanded
    cmmi-include-expand.py --verify <file.md> [...]   # exit 0 iff every
                                                       #   include resolves
    cmmi-include-expand.py --verify --all             # walk projects/pycsl
                                                       #   recursively

Read-only: never modifies the input file. The expanded form is
printed to stdout; redirect to materialise.

Per cmmi-tailoring-plan.md §"Per-skill tailoring → 4. cmmi-documents"
and §"Verification" check 4.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

INCLUDE_RE = re.compile(
    r"<!--\s*pycsl-include:\s*source=(\S+)\s+scope=(\S+)\s*-->"
)


def resolve_source(src: str) -> Path:
    """Resolve a source= value to an absolute path under REPO_ROOT."""
    return (REPO_ROOT / src).resolve()


def expand(md_path: Path) -> str:
    """Return the file's content with every include anchor expanded."""
    text = md_path.read_text()
    out_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        m = INCLUDE_RE.search(line)
        if not m:
            out_lines.append(line)
            continue
        src, scope = m.group(1), m.group(2)
        target = resolve_source(src)
        if not target.is_file():
            out_lines.append(
                f"<!-- pycsl-include: BROKEN source={src} scope={scope} -->\n"
            )
            continue
        out_lines.append(
            f"<!-- BEGIN pycsl-include source={src} scope={scope} -->\n"
        )
        out_lines.append(target.read_text())
        if not out_lines[-1].endswith("\n"):
            out_lines.append("\n")
        out_lines.append(
            f"<!-- END pycsl-include source={src} scope={scope} -->\n"
        )
    return "".join(out_lines)


def verify(md_paths: list[Path]) -> int:
    """Return 0 iff every include in every path resolves; report otherwise."""
    broken: list[tuple[Path, str, str]] = []
    checked = 0
    for p in md_paths:
        if not p.is_file():
            print(f"verify: skip non-file {p}", file=sys.stderr)
            continue
        text = p.read_text()
        for m in INCLUDE_RE.finditer(text):
            checked += 1
            src, scope = m.group(1), m.group(2)
            if not resolve_source(src).is_file():
                broken.append((p, src, scope))
    if broken:
        for path, src, scope in broken:
            print(
                f"BROKEN: {path.relative_to(REPO_ROOT)} -> source={src} scope={scope}",
                file=sys.stderr,
            )
        print(
            f"\ncmmi-include-expand: {len(broken)}/{checked} broken",
            file=sys.stderr,
        )
        return 1
    print(f"cmmi-include-expand: {checked}/{checked} includes resolve")
    return 0


def collect_all_md(root: Path) -> list[Path]:
    """Walk projects/pycsl recursively for .md files."""
    base = root / "projects" / "pycsl"
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*.md") if p.is_file())


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Resolve or verify pycsl-include anchors."
    )
    ap.add_argument("--verify", action="store_true")
    ap.add_argument(
        "--all",
        action="store_true",
        help="Walk projects/pycsl recursively (only with --verify).",
    )
    ap.add_argument("paths", nargs="*", type=Path)
    args = ap.parse_args(argv)

    if args.verify:
        if args.all:
            paths = collect_all_md(REPO_ROOT)
            if not paths:
                print(
                    "cmmi-include-expand: projects/pycsl/ has no .md files yet",
                    file=sys.stderr,
                )
                return 0
        else:
            paths = args.paths
        if not paths:
            ap.error("--verify needs paths or --all")
        return verify(paths)

    # expand mode: must have exactly one path
    if len(args.paths) != 1:
        ap.error("expand mode takes exactly one path; use --verify for many")
    md = args.paths[0]
    if not md.is_file():
        print(f"cmmi-include-expand: not a file: {md}", file=sys.stderr)
        return 2
    sys.stdout.write(expand(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
