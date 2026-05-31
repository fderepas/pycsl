#!/usr/bin/env python3
"""cmmi-mod-index — generate L4 Module-level spec indices for PyCSL systems.

Under Profile-P, the L4 Module spec is an auto-generated index of every
`def` (function or method) in a `.py` file, with line refs. The .py file
IS the spec; this index is a pointer table.

Modes:
    cmmi-mod-index.py --system SY3-Pycsl          # walk src/<sys>/ recursively
    cmmi-mod-index.py --all                       # walk every System in PROJECT.md
    cmmi-mod-index.py --verify --system SY3-Pycsl # check index counts match def counts
    cmmi-mod-index.py --file <path.py>            # one-off index for a single file

Outputs land at projects/pycsl/BL/<SY>/.../<MO-Name>/specifications/main.md.

Read-only with respect to src/. Never writes inside src/.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_BL = REPO_ROOT / "projects" / "pycsl" / "BL"
PROJECT_MD = REPO_ROOT / "projects" / "pycsl" / "PROJECT.md"

# Parse PROJECT.md for the 9-System inventory rows
SYSTEM_ROW_RE = re.compile(
    r"\|\s*(SY\d)\s*\|\s*([A-Za-z0-9_]+)\s*\|.*?\|\s*`([^`]+)/`\s*\|"
)


def discover_systems() -> dict[str, tuple[str, Path]]:
    """Return {sy_id: (name, src_path)} from PROJECT.md's 9-System inventory."""
    text = PROJECT_MD.read_text()
    out: dict[str, tuple[str, Path]] = {}
    for m in SYSTEM_ROW_RE.finditer(text):
        sy, name, src = m.group(1), m.group(2), m.group(3)
        out[f"{sy}-{name}"] = (name, REPO_ROOT / src)
    return out


def collect_defs(py_path: Path) -> list[tuple[str, int, bool]]:
    """Return [(qualname, lineno, is_private)] for every def in the file."""
    try:
        tree = ast.parse(py_path.read_text())
    except (SyntaxError, UnicodeDecodeError):
        return []
    out: list[tuple[str, int, bool]] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def _visit_func(
            self, node: ast.FunctionDef | ast.AsyncFunctionDef
        ) -> None:
            qual = ".".join([*self.stack, node.name])
            is_private = node.name.startswith("_") and not (
                node.name.startswith("__") and node.name.endswith("__")
            )
            out.append((qual, node.lineno, is_private))
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_FunctionDef = _visit_func
        visit_AsyncFunctionDef = _visit_func

    Visitor().visit(tree)
    return out


def safe_mo_name(file_stem: str) -> str:
    """Convert a snake_case file stem to a PascalCase MO-Name (no leading digit)."""
    parts = re.split(r"[_\-]", file_stem)
    name = "".join(p.capitalize() for p in parts if p)
    return name or "Unnamed"


def index_for_file(
    py_path: Path, src_root: Path, sy_dir: Path, *, mo_counter: dict[Path, int]
) -> Path:
    """Generate the L4 index for one .py file. Returns the output path."""
    rel = py_path.relative_to(src_root)
    co_parent = sy_dir
    co_parts: list[str] = []
    # The first level under src_root is the Component (CO); deeper levels
    # collapse into the MO-Name (with dotted-style prefix in the title).
    if len(rel.parts) > 1:
        comp_dir_name = rel.parts[0]
        co_parts.append(comp_dir_name)
        # Find / assign a CO<M> number for this Component within the System
        # We use a simple counter keyed on the comp dir absolute path.
        co_abs = src_root / comp_dir_name
        if co_abs not in mo_counter:
            mo_counter[co_abs] = len(
                [k for k in mo_counter if k.parent == src_root]
            ) + 1
        co_num = mo_counter[co_abs]
        co_parent = sy_dir / f"CO{co_num}-{safe_mo_name(comp_dir_name)}"
        # Sub-subdirs flatten into the MO name
        if len(rel.parts) > 2:
            co_parts.extend(rel.parts[1:-1])

    # MO-Name and MO number within its CO parent
    file_stem = py_path.stem
    if file_stem == "__init__":
        # The component's __init__.py becomes the CO-level spec; emit there
        mo_dir = co_parent
        mo_main = mo_dir / "specifications" / "main.md"
        title_prefix = f"CO {'.'.join(co_parts) or 'root'} package"
    else:
        # Standard module file
        mo_key = co_parent
        if mo_key not in mo_counter:
            mo_counter[mo_key] = 0
        mo_counter[mo_key] += 1
        mo_num = mo_counter[mo_key]
        mo_dir = co_parent / f"MO{mo_num}-{safe_mo_name(file_stem)}"
        mo_main = mo_dir / "specifications" / "main.md"
        title_prefix = f"MO {'.'.join([*co_parts, file_stem])}"

    defs = collect_defs(py_path)
    public_defs = [(q, ln) for (q, ln, priv) in defs if not priv]
    private_defs = [(q, ln) for (q, ln, priv) in defs if priv]

    rel_from_repo = py_path.relative_to(REPO_ROOT)
    lines: list[str] = [
        f"# {title_prefix} — L4 Module Index (auto-generated)",
        "",
        f"**Source file:** `{rel_from_repo}` (the .py file IS the L4 spec).",
        "**Layer:** L4 (Module — auto-generated by `bin/cmmi-mod-index.py`).",
        "**DO NOT EDIT BY HAND.** Regenerate via:",
        "",
        "```bash",
        f"bin/cmmi-mod-index.py --file {rel_from_repo}",
        "```",
        "",
        "---",
        "",
        f"## Public functions / methods ({len(public_defs)})",
        "",
    ]
    if public_defs:
        for qn, ln in public_defs:
            lines.append(f"- `{qn}` — `{rel_from_repo}:{ln}`")
    else:
        lines.append("_(none)_")
    lines += [
        "",
        f"## Private (leading-`_`) defs ({len(private_defs)})",
        "",
    ]
    if private_defs:
        for qn, ln in private_defs:
            lines.append(f"- `{qn}` — `{rel_from_repo}:{ln}`")
    else:
        lines.append("_(none)_")
    lines += [
        "",
        "---",
        "",
        "## L5 (Unit) specs",
        "",
        f"The `#@` contract block immediately preceding each `def` in "
        f"`{rel_from_repo}` is the Unit-level spec. Under Profile-P these "
        "contracts are read in-source; no `UN<N>-<Name>/` directories are "
        "materialised.",
        "",
        f"Total defs: **{len(defs)}** "
        f"(public: {len(public_defs)}, private: {len(private_defs)}).",
        "",
    ]
    mo_main.parent.mkdir(parents=True, exist_ok=True)
    mo_main.write_text("\n".join(lines))
    return mo_main


def walk_system(sy_full: str, src_root: Path) -> tuple[int, int]:
    """Generate indices for every .py under src_root. Returns (file_count, def_count)."""
    sy_dir = PROJECTS_BL / sy_full
    if not sy_dir.is_dir():
        print(
            f"cmmi-mod-index: skip {sy_full} (no BL/ dir at {sy_dir})",
            file=sys.stderr,
        )
        return 0, 0
    if not src_root.is_dir():
        print(
            f"cmmi-mod-index: skip {sy_full} (no src dir at {src_root})",
            file=sys.stderr,
        )
        return 0, 0
    mo_counter: dict[Path, int] = {}
    total_defs = 0
    py_files: list[Path] = sorted(
        p for p in src_root.rglob("*.py")
        if "__pycache__" not in p.parts
        and ".egg-info" not in str(p)
        # skip empty __init__.py package markers (no content to index)
        and not (p.name == "__init__.py" and p.stat().st_size == 0)
    )
    for py in py_files:
        out = index_for_file(py, src_root, sy_dir, mo_counter=mo_counter)
        total_defs += len(collect_defs(py))
        # quiet by default
        _ = out
    print(f"{sy_full}: indexed {len(py_files)} files, {total_defs} defs")
    return len(py_files), total_defs


def verify_system(sy_full: str, src_root: Path) -> int:
    """Verify L4 indices reflect reality: index entry count == def count per file."""
    sy_dir = PROJECTS_BL / sy_full
    failures: list[str] = []
    for py in src_root.rglob("*.py"):
        if "__pycache__" in py.parts or ".egg-info" in str(py):
            continue
        # skip empty __init__.py (same filter as index generator)
        if py.name == "__init__.py" and py.stat().st_size == 0:
            continue
        actual = len(collect_defs(py))
        # Find the index file. Same logic as index_for_file but reversed.
        # For simplicity: grep all index files under sy_dir for the source-file path.
        rel = py.relative_to(REPO_ROOT)
        marker = f"`{rel}`"
        match = None
        for cand in sy_dir.rglob("specifications/main.md"):
            text = cand.read_text()
            if marker in text and "auto-generated by `bin/cmmi-mod-index.py`" in text:
                match = cand
                break
        if match is None:
            failures.append(f"{rel}: no index file found")
            continue
        # Count list bullets that look like `- \`<qual>\` — \`<file>:<lineno>\``
        text = match.read_text()
        bullets = re.findall(r"^- `[^`]+` — `[^`]+:\d+`$", text, re.M)
        if len(bullets) != actual:
            failures.append(
                f"{rel}: index has {len(bullets)} entries, file has {actual} defs"
            )
    if failures:
        for f in failures:
            print(f"VERIFY FAIL: {f}", file=sys.stderr)
        print(f"cmmi-mod-index --verify: {len(failures)} mismatches", file=sys.stderr)
        return 1
    print(f"cmmi-mod-index --verify {sy_full}: OK")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate L4 Module indices.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--system", type=str, help="System ID-Name (e.g. SY3-Pycsl)")
    g.add_argument("--all", action="store_true")
    g.add_argument("--file", type=Path, help="Index a single .py file (Pycsl as containing system)")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args(argv)

    systems = discover_systems()
    if not systems:
        print(
            "cmmi-mod-index: PROJECT.md has no parseable system rows",
            file=sys.stderr,
        )
        return 2

    if args.file:
        # Pick a containing system based on src/<sys>/ prefix
        for sy_full, (_, src_root) in systems.items():
            try:
                args.file.resolve().relative_to(src_root)
            except ValueError:
                continue
            sy_dir = PROJECTS_BL / sy_full
            if not sy_dir.is_dir():
                print(f"cmmi-mod-index: no BL/ dir for {sy_full}", file=sys.stderr)
                return 2
            mo_counter: dict[Path, int] = {}
            out = index_for_file(
                args.file.resolve(), src_root, sy_dir, mo_counter=mo_counter
            )
            print(f"indexed -> {out.relative_to(REPO_ROOT)}")
            return 0
        print(f"cmmi-mod-index: {args.file} not under any known System src/")
        return 2

    targets = (
        [(args.system, *systems[args.system])]
        if args.system and args.system in systems
        else [(k, *v) for k, v in systems.items()]
        if args.all
        else []
    )
    if not targets and args.system:
        print(
            f"cmmi-mod-index: unknown system {args.system}; known: {list(systems)}",
            file=sys.stderr,
        )
        return 2

    rc = 0
    for sy_full, _name, src_root in targets:
        if args.verify:
            rc |= verify_system(sy_full, src_root)
        else:
            walk_system(sy_full, src_root)
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
