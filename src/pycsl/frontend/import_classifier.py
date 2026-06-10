"""Import classifier — Phase 1 implementation of UB-7.4 (C-extension
boundary detection) from the NoException_and_UBDetection workplan.

Walks a Python AST for `Import` / `ImportFrom` statements and classifies
each imported module against:

  1. The library-stub set under ``src/pycsl_lib/`` (the trusted-stub
     mechanism PyCSL already uses for stdlib coverage; renamed from
     ``data/lib_stubs/`` per StdlibCoverage workplan PR 3).
  2. The configurable deny-list (``ctypes``, ``cffi``,
     ``numpy.ctypeslib``, ``cython``, ``ctypes.util``). Any import
     whose top-level module name matches a deny-list entry is
     classified as ``UNVERIFIED``.
  3. Everything else: ``TRUSTED_STUB`` if a stub file is present,
     otherwise ``UNRESOLVED`` (silent — only the deny-list is treated
     as a hard error in this phase).

The classifier raises ``PyCSLSemanticError`` when an ``UNVERIFIED``
import is found *and* no function in the file carries an explicit
``#@ \\trusted`` annotation *and* the
``--allow-unverified-imports`` CLI flag is not set. This is the
cheapest UB win in Part II — surfacing the verification-perimeter
boundary at the import statement itself, rather than letting the
verifier silently treat extension modules as ambient int.
"""

from __future__ import annotations

from frontend import pure_ast as ast  # consume the same pure-Python tree Module3 builds
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

from errors import PyCSLSemanticError


# ----------------------------------------------------------------------
# Classification labels
# ----------------------------------------------------------------------

TRUSTED_STUB = "TRUSTED_STUB"
UNVERIFIED   = "UNVERIFIED"
UNRESOLVED   = "UNRESOLVED"


# ----------------------------------------------------------------------
# Configurable deny-list
# ----------------------------------------------------------------------
# Top-level module names that bypass Python's value-only semantics and
# enter the C-extension boundary. Imports of any of these (or any
# submodule thereof) are unverifiable by PyCSL's WhyML backend.

DEFAULT_DENY_LIST: frozenset = frozenset({
    "ctypes",
    "ctypes.util",
    "cffi",
    "numpy.ctypeslib",
    "cython",
})


def _stub_set(stub_dir: Path) -> Set[str]:
    """Return the set of stem names under ``stub_dir`` ending in ``.py``."""
    if not stub_dir.is_dir():
        return set()
    return {p.stem for p in stub_dir.iterdir() if p.suffix == ".py"}


def classify(module_name: str, stubs: Set[str],
             deny_list: frozenset = DEFAULT_DENY_LIST) -> str:
    """Classify a single module name."""
    top = module_name.split(".", 1)[0]
    if module_name in deny_list or top in deny_list:
        return UNVERIFIED
    if module_name in stubs or top in stubs:
        return TRUSTED_STUB
    return UNRESOLVED


def collect_imports(tree: ast.AST) -> List[Tuple[str, int]]:
    """Walk an AST and return ``(module_name, line)`` for every Import /
    ImportFrom statement."""
    out: List[Tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.append((node.module, node.lineno))
    return out


def any_function_trusted(tree: ast.AST) -> bool:
    """True iff at least one function in ``tree`` has ``#@ \\trusted``.

    A file with ``\\trusted`` somewhere is opt-in for the unverified
    boundary — the user has acknowledged that some surface is excluded
    from verification.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if getattr(node, "csl_trusted", False):
                return True
    return False


def check_imports(tree: ast.AST, *,
                  stub_dir: Path,
                  allow_unverified: bool = False,
                  filename: str = "<input>",
                  deny_list: frozenset = DEFAULT_DENY_LIST) -> List[Tuple[str, str, int]]:
    """Classify all imports in ``tree`` and enforce the deny-list policy.

    Returns the full ``[(module, label, line), ...]`` classification
    list. Raises ``PyCSLSemanticError`` for any ``UNVERIFIED`` import
    when neither the override flag is set nor the file has a
    ``\\trusted`` opt-in.
    """
    stubs = _stub_set(stub_dir)
    imports = collect_imports(tree)
    classified: List[Tuple[str, str, int]] = [
        (mod, classify(mod, stubs, deny_list), line) for mod, line in imports
    ]
    if allow_unverified:
        return classified
    has_trusted = any_function_trusted(tree)
    for mod, label, line in classified:
        if label == UNVERIFIED and not has_trusted:
            raise PyCSLSemanticError(
                f"{filename} (line {line}): import '{mod}' is on the "
                f"C-extension deny-list. Either annotate the importing "
                f"function(s) with `#@ \\trusted` to acknowledge that "
                f"the boundary is excluded from verification, or pass "
                f"`--allow-unverified-imports` to opt out of the check. "
                f"See config/skills/pycsl-ub-catalog/SKILL.md §7.4."
            )
    return classified
