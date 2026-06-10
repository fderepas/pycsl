#!/usr/bin/env python3
"""PyCSL capability manifest generator (refactor.md Phase D).

Emits a JSON manifest describing what THIS build of the PyCSL verifier supports:

  * ``ir_version`` / ``accepted_ir_versions`` — the IR-as-wire-format contract
    (read from ``src/pycsl/ir_schema.py``: ``IR_VERSION`` / ``ACCEPTED_IR_VERSIONS``).
  * ``directives`` — the supported ``#@`` contract directives, reusing
    ``bin/doc-coherency.py``'s canonical extractor (``test-suite/annotations.md``).
  * ``verification_levels`` — the level ladder the CLI offers (L1 parse / L2
    semantic-on-IR / L3-tc typecheck / L3-proof), matching ``pycsl.py``'s ``[level]``.
  * ``ir_node_types`` — the IR expression + statement node inventory, parsed from
    the §7 / §8 node tables of ``docs/ir.md`` (the normative IR contract).
  * ``diagnostic_codes`` — the stable machine-readable error codes assigned at the
    core's raise sites (scanned from ``core_ir_semantic.py`` / ``ir_schema.py`` /
    ``pycsl.py``).
  * ``corpus`` — pass/fail statistics: the reference corpus by declared
    ``# pycsl-expected:`` outcome, and the frozen conformance-corpus golden counts.

The output is DETERMINISTIC: all keys are sorted, all lists are sorted by a stable
key, and only static repository facts are read (no prover is run, so the manifest is
reproducible byte-for-byte across machines). Run it twice → identical bytes.

Usage:
    pycsl-capability-manifest.py            # JSON manifest to stdout
    pycsl-capability-manifest.py -o FILE     # write to FILE

Exit codes: 0 ok; 2 tool error (a required source is missing).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = REPO_ROOT / "bin"
SRC_DIR = REPO_ROOT / "src" / "pycsl"
IR_SCHEMA = SRC_DIR / "ir_schema.py"
CORE_SEM = SRC_DIR / "core_ir_semantic.py"
PYCSL_PY = SRC_DIR / "pycsl.py"
IR_MD = REPO_ROOT / "docs" / "ir.md"
PYCSL_REF = REPO_ROOT / "test-suite" / "corpus" / "pycsl-reference"
PYTHON_REF = REPO_ROOT / "test-suite" / "corpus" / "python-reference"
CONFORMANCE = REPO_ROOT / "test-suite" / "corpus" / "conformance"


def _die(msg: str) -> "None":
    print(f"[!] capability-manifest: {msg}", file=sys.stderr)
    sys.exit(2)


def _ir_versions() -> Dict[str, object]:
    """Read IR_VERSION + ACCEPTED_IR_VERSIONS from ir_schema.py (regex, no import)."""
    if not IR_SCHEMA.exists():
        _die(f"missing {IR_SCHEMA}")
    text = IR_SCHEMA.read_text()
    m = re.search(r'IR_VERSION\s*=\s*"([^"]+)"', text)
    ir_version = m.group(1) if m else None
    accepted = sorted(set(re.findall(r'"(\d+\.\d+)"',
                                     re.search(r"ACCEPTED_IR_VERSIONS\s*=.*?\)",
                                               text, re.DOTALL).group(0))))
    return {"ir_version": ir_version, "accepted_ir_versions": accepted}


def _directives() -> List[str]:
    """Reuse doc-coherency's canonical directive extractor (annotations.md)."""
    sys.path.insert(0, str(BIN_DIR))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "doc_coherency", BIN_DIR / "doc-coherency.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return sorted(mod.extract_directives_from_annotations())


def _ir_node_types() -> Dict[str, List[str]]:
    """Parse the §7 (expression) and §8 (statement) node-type tables of docs/ir.md.

    Each node row begins ``| `NodeName` | ...``. §7 spans from its header to §8's
    header; §8 spans from its header to §9's. Node names are sorted within each kind."""
    if not IR_MD.exists():
        _die(f"missing {IR_MD}")
    lines = IR_MD.read_text().splitlines()

    def _header_line(pat: str) -> int:
        for i, ln in enumerate(lines):
            if re.match(pat, ln):
                return i
        _die(f"section header not found: {pat}")
        return -1  # unreachable

    s7 = _header_line(r"^## 7\.")
    s8 = _header_line(r"^## 8\.")
    s9 = _header_line(r"^## 9\.")
    row = re.compile(r"^\|\s*`([A-Za-z][A-Za-z0-9_]*)`\s*\|")
    # The discriminator-column header rows (``| `type` | Fields | ...`` for expression
    # tables, ``| `stmt` | Fields | ...`` for the statement table) match the row regex
    # but are NOT node names — drop them.
    _HEADERS = {"type", "stmt"}

    def _names(lo: int, hi: int) -> List[str]:
        out: set = set()
        for ln in lines[lo:hi]:
            m = row.match(ln)
            if m and m.group(1) not in _HEADERS:
                out.add(m.group(1))
        return sorted(out)

    return {"expressions": _names(s7, s8), "statements": _names(s8, s9)}


def _diagnostic_codes() -> List[str]:
    """Scan the core seam + IR + typecheck for assigned stable diagnostic codes."""
    codes: set = set()
    pat = re.compile(r'code\s*=\s*"(PYCSL-[A-Z0-9-]+)"')
    for f in (CORE_SEM, IR_SCHEMA, PYCSL_PY):
        if f.exists():
            codes |= set(pat.findall(f.read_text()))
    return sorted(codes)


def _corpus() -> Dict[str, object]:
    """Static corpus statistics (deterministic; no prover run).

    Reference corpus: count drivers by their declared ``# pycsl-expected:`` marker
    (PASS / FAIL / unmarked). Conformance corpus: count frozen goldens (one per
    ``NNNN.ir.json`` / ``NNNN.expected.mlw`` pair under conformance/core)."""
    exp_pat = re.compile(r"^# pycsl-expected:\s*(\w+)", re.MULTILINE)

    def _ref_stats(d: Path) -> Dict[str, int]:
        total = pass_ = fail = unmarked = 0
        for py in sorted(d.glob("*.py")):
            total += 1
            m = exp_pat.search(py.read_text())
            if not m:
                unmarked += 1
            elif m.group(1).upper() == "PASS":
                pass_ += 1
            elif m.group(1).upper() == "FAIL":
                fail += 1
            else:
                unmarked += 1
        return {"total": total, "expected_pass": pass_,
                "expected_fail": fail, "unmarked": unmarked}

    core_dir = CONFORMANCE / "core"
    conf_goldens = (len(sorted(core_dir.glob("*.ir.json")))
                    if core_dir.exists() else 0)

    return {
        "pycsl_reference": _ref_stats(PYCSL_REF) if PYCSL_REF.exists() else {},
        "python_reference": _ref_stats(PYTHON_REF) if PYTHON_REF.exists() else {},
        "conformance_goldens": conf_goldens,
    }


def build_manifest() -> Dict[str, object]:
    manifest: Dict[str, object] = {
        "schema": "pycsl-capability-manifest/1",
        "corpus": _corpus(),
        "diagnostic_codes": _diagnostic_codes(),
        "directives": _directives(),
        "ir_node_types": _ir_node_types(),
        "verification_levels": [
            {"level": "L1", "name": "parse",
             "description": "front-end parse + weave (source -> AST -> IR)"},
            {"level": "L2", "name": "semantic-on-IR",
             "description": "language-agnostic IR semantic checks "
                            "(core_ir_semantic.run_ir_semantic_checks)"},
            {"level": "L3-tc", "name": "typecheck",
             "description": "why3 prove --type-only on the emitted WhyML "
                            "(default-on honest gate; --no-typecheck opts out)"},
            {"level": "L3-proof", "name": "proof",
             "description": "why3 prove with SMT solvers (alt-ergo, z3); "
                            "discharges the verification conditions"},
        ],
    }
    manifest.update(_ir_versions())
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", metavar="FILE", default=None,
                    help="write the manifest to FILE (default: stdout)")
    args = ap.parse_args()

    text = json.dumps(build_manifest(), sort_keys=True, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
