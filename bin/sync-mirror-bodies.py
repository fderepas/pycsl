#!/usr/bin/env python3
"""sync-mirror-bodies.py — copy function/method bodies from
`src/pycsl/<file>.py` into the matching `src/self-annotate/src/<file>.py`
mirror, preserving the mirror's existing `#@ …` annotations.

Per-function merge: for each `FunctionDef` / `AsyncFunctionDef` in the
mirror, find the matching def in the source (by (class_path, name)),
and replace the body field. Top-level annotations between functions,
class-level annotations, and decorators on the mirror's def stay
intact.

Limitations:
  - A function present in the mirror but absent from the source emits
    a warning and is left untouched.
  - A function present in the source but absent from the mirror is
    silently ignored (the mirror sets the surface the verifier sees).
  - Top-level statements outside any function are NOT copied — the
    mirror's module-level shape (imports, class scaffolding, top-level
    annotations) is the source of truth for everything outside def
    bodies.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import libcst as cst


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = REPO_ROOT / "src" / "pycsl"
MIRROR_ROOT = REPO_ROOT / "src" / "self-annotate" / "src"


# ---------------------------------------------------------------------------
# Build (class_path, func_name) → body lookup from source
# ---------------------------------------------------------------------------


class _SourceBodyCollector(cst.CSTVisitor):
    """Walk a `src/pycsl/<file>.py` AST and collect each FunctionDef's
    (params, body, returns) triple keyed by (qualified_class_path,
    function_name).

    `params` and `returns` are synced alongside `body` because the
    copied body references the source's parameter set and may rely on
    its return-type annotation. The mirror's existing signature is
    overwritten."""

    def __init__(self) -> None:
        self.class_stack: List[str] = []
        self.bodies: Dict[Tuple[str, str], Tuple[cst.Parameters,
                                                  cst.BaseSuite,
                                                  cst.Annotation]] = {}

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.class_stack.append(node.name.value)

    def leave_ClassDef(self, original_node: cst.ClassDef) -> None:
        self.class_stack.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        key = (".".join(self.class_stack), node.name.value)
        self.bodies[key] = (node.params, node.body, node.returns)


# ---------------------------------------------------------------------------
# Apply body lookup to the mirror, replacing each FunctionDef body
# ---------------------------------------------------------------------------


class _MirrorBodyMerger(cst.CSTTransformer):
    """Walk the mirror tree; replace each FunctionDef's body with the
    matching one from `bodies` (keyed by (class_path, name))."""

    def __init__(self, bodies: Dict[Tuple[str, str],
                                       Tuple[cst.Parameters,
                                             cst.BaseSuite,
                                             cst.Annotation]]) -> None:
        self.class_stack: List[str] = []
        self.bodies = bodies
        self.replaced = 0
        self.missing: List[Tuple[str, str]] = []

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.class_stack.append(node.name.value)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        self.class_stack.pop()
        return updated_node

    def leave_FunctionDef(
        self,
        original_node: cst.FunctionDef,
        updated_node: cst.FunctionDef,
    ) -> cst.FunctionDef:
        key = (".".join(self.class_stack), original_node.name.value)
        if key in self.bodies:
            self.replaced += 1
            params, body, returns = self.bodies[key]
            return updated_node.with_changes(
                params=params, body=body, returns=returns,
            )
        self.missing.append(key)
        return updated_node


# ---------------------------------------------------------------------------
# Per-file driver
# ---------------------------------------------------------------------------


def sync_file(filename: str, dry_run: bool = False) -> None:
    """Sync function bodies from `src/pycsl/<filename>` into
    `src/self-annotate/src/<filename>`."""
    src_path = SOURCE_ROOT / filename
    mirror_path = MIRROR_ROOT / filename
    if not src_path.is_file():
        print(f"  [!] source not found: {src_path}", file=sys.stderr)
        return
    if not mirror_path.is_file():
        print(f"  [!] mirror not found: {mirror_path}", file=sys.stderr)
        return

    source_tree = cst.parse_module(src_path.read_text())
    collector = _SourceBodyCollector()
    source_tree.visit(collector)

    mirror_tree = cst.parse_module(mirror_path.read_text())
    merger = _MirrorBodyMerger(collector.bodies)
    new_mirror = mirror_tree.visit(merger)

    print(f"  ✓ {filename}: replaced {merger.replaced} bodies; "
          f"missing-from-source {len(merger.missing)}")
    if merger.missing:
        for cls, fn in merger.missing[:5]:
            print(f"      missing: {cls or '<module>'}.{fn}")
        if len(merger.missing) > 5:
            print(f"      ... and {len(merger.missing) - 5} more")

    if not dry_run:
        mirror_path.write_text(new_mirror.code)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print summary per file but don't write changes.",
    )
    parser.add_argument(
        "files", nargs="*",
        help="Filenames to sync (default: all known mirror files).",
    )
    args = parser.parse_args()

    files = args.files or [
        "Module1_Ingestor.py",
        "Module2_Parser.py",
        "Module3_Weaver.py",
        "Module4_SemanticAnalyzer.py",
        "Module5_IREmitter.py",
        "Module6_WhyMLTranspiler.py",
        "ConcurrencyChecker.py",
        "ir_schema.py",
        "errors.py",
        "exception_model.py",
        "import_classifier.py",
        "audit_proof.py",
        "pycsl.py",
        "__init__.py",
    ]

    print(f"=== syncing bodies from {SOURCE_ROOT} → {MIRROR_ROOT} ===")
    for f in files:
        sync_file(f, dry_run=args.dry_run)
    print("=== done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
