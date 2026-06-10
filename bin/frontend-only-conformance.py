#!/usr/bin/env python3
"""Front-end-only conformance runner — refactor.md Phase E, corpus (2): source -> expected-IR.

The mirror of ``bin/core-only-conformance.py``. Where the core-only corpus freezes the
language-agnostic CORE (golden resolved IR -> expected WhyML, no front-end), THIS corpus
freezes the FRONT-END contract: source -> resolved IR, with NO Module 6 and NO prover.

For each golden ``<corpus-dir>/NNNN.ir.json`` (the frozen resolved IR — exactly the output of
``bin/pycsl-ir-dump.py --resolved`` on ``test-suite/corpus/pycsl-reference/NNNN.py``), this
runner locates the SOURCE, re-derives the resolved IR via the SAME ``--resolved`` path
(Modules 1-5 + the three pure post-M5 IR->IR passes ``apply_inheritance`` /
``apply_composition`` / ``apply_inline_globals``), and diffs the re-derived IR against the
golden. A Module1-5 change that alters the IR is thereby caught, freezing the IR a second
front-end can target.

refactor.md Phase C (C2c): this runner now derives the resolved IR by IMPORTING the
front-end DIRECTLY (``dump_ir(..., resolved=True)`` from ``bin/pycsl-ir-dump.py``, which
imports only Modules 1-5 and ``frontend.ir_resolve``) — NO subprocess for the main
conformance check. This is possible because ``pycsl.py`` now imports
``Module6_WhyMLTranspiler`` lazily (at the transpile call site), so nothing on the
front-end import path drags in the core. The runner ASSERTS in-process that no core /
Module 6 / prover module is in ``sys.modules`` AFTER the front-end import — the whole
point of the front-end/core split: the front-end stands alone.

Comparison policy:
  * Compare as PARSED JSON (``json.loads`` both, assert structural equality) so insignificant
    whitespace never matters.
  * The ``ir_version`` field is a SCHEMA/metadata stamp emitted by Module 5, NOT front-end-
    derived program content. Some goldens were frozen at an older stamp (``1.0``) than the
    current emitter (``1.1``). We do NOT modify the frozen goldens; instead a difference that
    is CONFINED to ``ir_version`` is reported as a non-fatal ``VERSION-SKEW`` (still surfaced
    in the tally), while ANY difference in actual IR content (functions / type_decls /
    module_constants / source_language) is a hard ``MISMATCH``.

Determinism gate:
  * For a sample of drivers, re-derive the canonical resolved IR serialization under two
    different ``PYTHONHASHSEED`` values and confirm byte-identical output — the front-end IR
    must be canonical (the repo fixed hash/set nondeterminism; this corpus depends on it).
    PYTHONHASHSEED is read once at interpreter startup, so this gate necessarily re-derives
    in SUBPROCESSES (one per seed). That is the only subprocess use that remains; it spawns
    only the front-end ``--resolved`` path, never Module 6 or a prover.

Usage:  frontend-only-conformance.py [corpus-dir]
        (default corpus-dir: test-suite/corpus/conformance/core)
"""
import glob
import importlib.util
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IR_DUMP = os.path.join(ROOT, "bin", "pycsl-ir-dump.py")
PYBIN = os.path.join(ROOT, ".venv", "bin", "python3")
if not os.path.exists(PYBIN):
    PYBIN = sys.executable
REFERENCE_DIR = os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference")

# Front-end alone: this PROCESS must not have pulled in the core / Module 6 / the prover.
# After importing the front-end (dump_ir), we assert these prefixes are ABSENT from
# sys.modules — the C2c invariant that importing the front-end never loads the core.
_FORBIDDEN_PREFIXES = ("Module6", "module6_whyml", "core_ir_semantic", "why3")


def _load_dump_ir():
    """Import ``dump_ir`` from bin/pycsl-ir-dump.py DIRECTLY (no subprocess).

    pycsl-ir-dump.py imports only the front-end (Modules 1-5 + frontend.ir_resolve);
    now that pycsl.py imports Module6 lazily, this pulls in NO core/prover module. The
    front-end-alone invariant is then asserted by ``_assert_no_core_or_prover``.
    """
    sys.path.insert(0, os.path.join(ROOT, "src", "pycsl"))
    spec = importlib.util.spec_from_file_location("pycsl_ir_dump", IR_DUMP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.dump_ir


def _assert_no_core_or_prover() -> None:
    leaked = sorted(m for m in sys.modules if m.startswith(_FORBIDDEN_PREFIXES))
    if leaked:
        print(f"[!] front-end-only violation: core/Module6/prover modules present: {leaked}")
        sys.exit(2)


# Imported at module load so the assertion covers the front-end import side-effect.
_dump_ir = _load_dump_ir()


def derive_resolved_ir(src_path: str) -> str:
    """Re-derive the canonical resolved-IR serialization from SOURCE, IN-PROCESS.

    Calls the directly-imported ``dump_ir(..., resolved=True)`` and re-serializes with the
    same canonical ``json.dumps(..., indent=2)`` the dump tool's main() uses, so the output
    matches the frozen goldens exactly.
    """
    ir_json = _dump_ir(src_path, resolved=True)
    return json.dumps(json.loads(ir_json), indent=2)


def derive_resolved_ir_subprocess(src_path: str, hashseed: str) -> str:
    """Re-derive the resolved IR in a SUBPROCESS under a fixed PYTHONHASHSEED.

    Used ONLY by the determinism gate, which must vary PYTHONHASHSEED (read once at
    interpreter startup). Spawns the front-end ``--resolved`` path only — never the core.
    """
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = hashseed
    r = subprocess.run(
        [PYBIN, IR_DUMP, "--resolved", src_path],
        capture_output=True, text=True, env=env, cwd=ROOT,
    )
    if r.returncode != 0:
        raise RuntimeError(f"pycsl-ir-dump.py failed for {src_path}: {r.stderr.strip()}")
    return r.stdout


def _content_without_version(ir: dict) -> dict:
    """The IR with the metadata version stamp stripped, for content comparison."""
    return {k: v for k, v in ir.items() if k != "ir_version"}


def run(corpus_dir: str) -> int:
    _assert_no_core_or_prover()
    goldens = sorted(glob.glob(os.path.join(corpus_dir, "*.ir.json")))
    if not goldens:
        print(f"[!] no *.ir.json golden inputs found in {corpus_dir}")
        return 2

    ok = 0
    mismatch = 0
    version_skew = 0

    for g in goldens:
        name = os.path.basename(g)[: -len(".ir.json")]
        src = os.path.join(REFERENCE_DIR, f"{name}.py")
        if not os.path.exists(src):
            print(f"  {name}: MISSING source {src}")
            mismatch += 1
            continue

        try:
            derived_text = derive_resolved_ir(src)
        except Exception as e:
            print(f"  {name}: DUMP-FAIL {e}")
            mismatch += 1
            continue

        derived = json.loads(derived_text)
        golden = json.load(open(g))

        if derived == golden:
            ok += 1
        elif _content_without_version(derived) == _content_without_version(golden):
            # Only the metadata stamp differs — frozen golden lags the current emitter.
            version_skew += 1
            ok += 1
            print(f"  {name}: VERSION-SKEW (ir_version golden={golden.get('ir_version')!r} "
                  f"derived={derived.get('ir_version')!r}) — IR content identical")
        else:
            mismatch += 1
            print(f"  {name}: MISMATCH — IR content differs from golden")
            for line in _content_diff(derived, golden):
                print(f"      {line}")

    # The front-end import happened (dump_ir at module load + every derive call); the
    # invariant must still hold — no core/prover module leaked in.
    _assert_no_core_or_prover()

    print(f"front-end conformance: {ok} OK / {mismatch} MISMATCH "
          f"({len(goldens)} goldens; {version_skew} version-skew)")
    print("front-end-only: no core/Module6/prover module in sys.modules (import-based, "
          "no subprocess for the conformance check)")

    det_ok, det_bad = determinism_check(goldens)
    if det_bad:
        print(f"[!] determinism: {len(det_bad)} of {det_ok + len(det_bad)} sampled drivers "
              f"VARY across PYTHONHASHSEED: {det_bad}")
    else:
        print(f"determinism: {det_ok}/{det_ok} sampled drivers byte-stable across "
              f"PYTHONHASHSEED (0 vs 1)")

    failed = mismatch > 0 or bool(det_bad)
    return 1 if failed else 0


def determinism_check(goldens, sample: int = 10):
    """Re-derive ~`sample` drivers under PYTHONHASHSEED=0 and =1; confirm byte-identical."""
    sampled = goldens[:sample]
    good = 0
    bad = []
    for g in sampled:
        name = os.path.basename(g)[: -len(".ir.json")]
        src = os.path.join(REFERENCE_DIR, f"{name}.py")
        if not os.path.exists(src):
            continue
        try:
            a = derive_resolved_ir_subprocess(src, hashseed="0")
            b = derive_resolved_ir_subprocess(src, hashseed="1")
        except RuntimeError:
            bad.append(name)
            continue
        if a == b:
            good += 1
        else:
            bad.append(name)
    return good, bad


def _content_diff(a, b, path=""):
    """Yield human-readable content differences (a=derived, b=golden), ir_version aside."""
    out = []
    if type(a) is not type(b):
        return [f"TYPE {path or '<root>'}: derived={type(a).__name__} golden={type(b).__name__}"]
    if isinstance(a, dict):
        ka, kb = set(a), set(b)
        if ka != kb:
            out.append(f"KEYS {path or '<root>'}: only-derived={sorted(ka - kb)} "
                       f"only-golden={sorted(kb - ka)}")
        for k in sorted(ka & kb):
            out += _content_diff(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f"LEN {path}: derived={len(a)} golden={len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            out += _content_diff(x, y, f"{path}[{i}]")
    else:
        if a != b:
            out.append(f"VAL {path}: derived={a!r} golden={b!r}")
    return out[:30]


if __name__ == "__main__":
    cd = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        "test-suite", "corpus", "conformance", "core")
    if not os.path.isabs(cd):
        cd = os.path.join(ROOT, cd)
    sys.exit(run(cd))
