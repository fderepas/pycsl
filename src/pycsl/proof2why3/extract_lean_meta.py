"""Python wrapper for the Lean meta-extractor
(`bin/proof2why3-lean-extract.lean`) — proof2why3 Phase B.

Runs `lake env lean --run` on the meta-script, parses one JSON object
per cited qualname, and returns a dict of `{qualname: ast_json_dict}`.

The caller (typically `crosscheck_ir.py` when
`PROOF2WHY3_USE_LEAN_META=1`) then feeds the AST into
`from_lean_json.project_to_ir` to obtain shared-IR Terms.

Per-test lakefile is required at `<proofs_dir>/lakefile.lean`. If
absent the wrapper falls back to the v1 `#check` extractor.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


_REPO_ROOT = Path(__file__).resolve().parents[3]
_META_SCRIPT = _REPO_ROOT / "bin" / "proof2why3-lean-extract.lean"


def lean_meta_available(proofs_dir: Path) -> bool:
    """True iff this directory has a lakefile.lean (needed to resolve
    the import target for the meta-script)."""
    return (proofs_dir / "lakefile.lean").is_file() and _META_SCRIPT.is_file()


def extract_lean_statements_meta(proof_file: Path,
                                  qualnames: List[str]) -> Dict[str, Dict[str, Any]]:
    """Run the meta-extractor and return `{qualname: ast_dict}`.

    On failure (lake not on PATH, lakefile missing, extraction error)
    returns an empty dict — caller should fall back to the v1 `#check`
    extractor.
    """
    proofs_dir = proof_file.parent
    if not lean_meta_available(proofs_dir):
        return {}
    import_module = proof_file.stem  # `Gcd` for `Gcd.lean`
    cmd = [
        "lake", "env", "lean", "--run", str(_META_SCRIPT),
        import_module,
        ",".join(qualnames),
    ]
    try:
        res = subprocess.run(
            cmd, cwd=str(proofs_dir),
            capture_output=True, text=True, timeout=600,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {}
    if res.returncode != 0:
        return {}

    out: Dict[str, Dict[str, Any]] = {}
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("end"):
            continue
        qn = obj.get("qualname")
        if not qn or "error" in obj:
            continue
        out[qn] = obj
    return out
