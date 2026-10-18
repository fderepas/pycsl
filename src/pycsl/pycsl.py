#!/usr/bin/env python3
from __future__ import annotations

import argparse
from frontend import pure_ast as _ast  # dependency import-discovery parses via the pure-Python front-end
import hashlib
import json as _json
import os
import sys
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure sibling modules are importable regardless of cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the PyCSL Pipeline Modules
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
# Module 4 (SemanticAnalyzer) DROPPED — B-final reorder: its checks migrated to the IR
# seam (core_ir_semantic). The pipeline is now M1-3 → M5 → IR semantic checks → M6.
from errors import PyCSLError, PyCSLParseError
from frontend.Module5_IREmitter import Module5_IREmitter
# refactor.md Phase C (C2c): Module6_WhyMLTranspiler is the CORE backend. Import it
# LAZILY at the transpile call site (inside _run_pipeline) rather than at module load,
# so importing the front-end through `pycsl` never transitively drags in the core. This
# is what lets bin/frontend-only-conformance.py import the front-end DIRECTLY (no
# subprocess) and assert no core module is in sys.modules.
from ir_schema import validate_ir
from core_ir_semantic import run_ir_semantic_checks
from frontend.ConcurrencyChecker import ConcurrencyChecker

# refactor.md Phase C (C2b): the four post-Module5 IR-resolution passes now live in
# the front-end package (frontend/ir_resolve.py), so the front-end emits the fully
# RESOLVED IR — the wire the language-agnostic core consumes. `_collect_calls` is a
# shared IR-walk helper used here by the Soundness Ledger and the --fun filter; it is
# re-imported from ir_resolve to keep a single definition.
from frontend.ir_resolve import resolve as _ir_resolve, _collect_calls


def _proof_reference_mlw_name(source_file: str) -> str:
    """Return the stable <source>.mlw filename stored in a proof directory."""
    return os.path.splitext(os.path.basename(source_file))[0] + ".mlw"


def _make_temp_mlw_path() -> str:
    """Allocate a per-invocation temporary WhyML file path."""
    fd, path = tempfile.mkstemp(prefix=".pycsl_", suffix=".mlw")
    os.close(fd)
    return path


def _generate_rocq_obligations(mlw_path: str, output_dir: str, unproven_count: int,
                               source_file: Optional[str] = None) -> None:
    """Generate Rocq proof obligations for goals that SMT provers could not discharge."""
    os.makedirs(output_dir, exist_ok=True)

    # Add a Makefile for cleaning compilation artifacts
    makefile_path = os.path.join(output_dir, "Makefile")
    if not os.path.exists(makefile_path):
        with open(makefile_path, "w") as mf:
            mf.write(".PHONY:default, clean\n\ndefault:\n\nclean:\n")
            mf.write("\trm -rf *.glob *.vo *.vok *.vos *~ \n")

    # Copy the WhyML source as reference
    mlw_basename = (os.path.basename(mlw_path) if source_file is None
                    else _proof_reference_mlw_name(source_file))
    mlw_dest = os.path.join(output_dir, mlw_basename)
    import shutil
    shutil.copy2(mlw_path, mlw_dest)

    # Run why3 prove with Coq prover to generate .v skeletons
    cmd = [
        "why3", "prove",
        "-P", "Coq,8.20.1,",
        "-a", "split_vc",
        "-o", output_dir,
        mlw_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Collect generated .v files
        v_files = [f for f in os.listdir(output_dir) if f.endswith(".v")]
        if v_files:
            print(f"\n[*] Generated {len(v_files)} Rocq proof obligation(s) in {output_dir}/")
            for vf in sorted(v_files):
                print(f"    → {output_dir}/{vf}")
            print(f"    → {mlw_dest}  (WhyML source reference)")
            print(f"\n[*] To complete the proofs:")
            print(f"    1. Edit the .v file(s) — fill in proof scripts between 'Proof.' and 'Qed.'")
            print(f"    2. Compile: coqc -R ~/.opam/default/lib/coq/user-contrib/Why3 Why3 <file>.v")
        else:
            print(f"\n[*] No .v files generated — Coq prover may not have produced skeletons.")
            print(f"    The WhyML source is saved at: {mlw_dest}")
            print(f"    You can open it in Why3 IDE: why3 ide {mlw_dest}")
    except FileNotFoundError:
        print(f"\n[!] Could not run 'why3 prove -P Coq'. Is why3-coq installed?")
        print(f"    The WhyML source is saved at: {mlw_dest}")


def _sha256_file(path: str) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_coqc() -> Optional[str]:
    """Locate the coqc binary, checking opam default first."""
    opam_coqc = os.path.expanduser("~/.opam/default/bin/coqc")
    if os.path.isfile(opam_coqc) and os.access(opam_coqc, os.X_OK):
        return opam_coqc
    import shutil as _sh
    return _sh.which("coqc")


def _find_why3_coq_lib() -> Optional[str]:
    """Locate the Why3 Coq library directory."""
    opam_lib = os.path.expanduser("~/.opam/default/lib/why3/coq")
    if os.path.isdir(opam_lib):
        return opam_lib
    return None


def _check_rocq_proofs(proof_dir: str, mlw_path: str, unproven_goal_names: List[str]) -> int:
    """Check for pre-existing Rocq proofs and replay them with coqc.

    Returns the number of goals successfully proved by Rocq.
    """
    if not os.path.isdir(proof_dir):
        return 0

    coqc = _find_coqc()
    if not coqc:
        print("[!] coqc not found — cannot replay Rocq proofs.")
        return 0

    why3_coq = _find_why3_coq_lib()
    if not why3_coq:
        print("[!] Why3 Coq library not found — cannot replay Rocq proofs.")
        return 0

    # Staleness check: compare current .mlw with stored .mlw
    stored_mlw = None
    for f in os.listdir(proof_dir):
        if f.endswith(".mlw"):
            stored_mlw = os.path.join(proof_dir, f)
            break

    if stored_mlw:
        current_hash = _sha256_file(mlw_path)
        stored_hash = _sha256_file(stored_mlw)
        if current_hash != stored_hash:
            print(f"[!] Rocq proofs found but .mlw hash mismatch — proofs may be stale.")
            print(f"    Current:  {current_hash[:16]}...")
            print(f"    Stored:   {stored_hash[:16]}...")
            print(f"    Regenerate proofs with: pycsl --rocq {proof_dir}/ {mlw_path}")
            return 0

    # Find .v proof files
    v_files = sorted(f for f in os.listdir(proof_dir) if f.endswith(".v"))
    if not v_files:
        return 0

    proved_count = 0
    print(f"\n[*] {len(v_files)} Rocq proof(s) found in {proof_dir}/ — replaying with coqc...")

    for vf in v_files:
        vpath = os.path.join(proof_dir, vf)
        cmd = [coqc, "-R", why3_coq, "Why3", vpath]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"[*] Rocq proof verified: {vf}")
                proved_count += 1
            else:
                print(f"[!] Rocq proof FAILED to compile: {vf}")
                if result.stderr.strip():
                    for line in result.stderr.strip().splitlines()[:3]:
                        print(f"    {line}")
        except subprocess.TimeoutExpired:
            print(f"[!] Rocq proof compilation timed out: {vf}")
        except FileNotFoundError:
            print(f"[!] coqc not found during proof replay.")
            return proved_count

    return proved_count


def _parse_args() -> argparse.Namespace:
    """Build and return the parsed CLI argument namespace."""
    parser = argparse.ArgumentParser(description="PyCSL: Python Contract Specification Language Verifier")
    parser.add_argument("file", help="The Python file to verify")

    # Flags are grouped by concern for readable `--help`; grouping affects only the
    # help layout, not the parsed namespace.
    g_prover = parser.add_argument_group("prover selection")
    g_prover.add_argument("-p", "--prover", default=None,
                        help="Single prover to use (e.g. 'Alt-Ergo,2.6.2,' or 'Z3,4.13.3,'). "
                             "Overrides --provers and agents-config.json.")
    g_prover.add_argument("--provers", default=None,
                        help="Comma-separated list of Why3 prover IDs to try in order "
                             "(e.g. 'Alt-Ergo,2.6.2,,Z3,4.13.3,'). "
                             "Why3 tries each prover per goal and accepts the first Valid. "
                             "Overrides agents-config.json. "
                             "Default: Alt-Ergo then Z3.")
    g_prover.add_argument("--memory-model", default=None,
                        choices=["hoare", "typed", "store", "concurrent"],
                        help="Memory model for WhyML emission (default: hoare). "
                             "'typed'/'store' use a global heap (map loc int). "
                             "'concurrent' enables mutex-discipline verification.")

    g_scope = parser.add_argument_group("scope / output")
    g_scope.add_argument("--keep-mlw", action="store_true",
                        help="Keep the generated WhyML (.mlw) file for debugging")
    g_scope.add_argument("--soundness-report", action="store_true",
                        help="Emit a Soundness Ledger (07-1143 R4): classify every "
                             "function/VC as Modelled (body-verified), Specified "
                             "(axiomatic contract), Stubbed (signature-only), or "
                             "Confinement (HAPPY \\preserves), flag trusted dependencies, "
                             "and print JSON + a human summary. Skips proving.")
    g_scope.add_argument("--fun", action="append", default=None, metavar="NAME",
                        help="Only verify the named function and its transitive "
                             "call-dependencies (may be repeated). "
                             "Other functions become trusted stubs.")
    g_scope.add_argument("--deep", action="store_true",
                        help="Recursively resolve transitive imports in "
                             "dependency files (default: only direct imports "
                             "of the main file are resolved).")
    g_scope.add_argument("--import-path", action="append", default=[],
                        metavar="DIR",
                        help="Extra directory to search when resolving imports "
                             "(repeatable), after the main file's dir/CWD/src/Lib. "
                             "Lets single-file verification resolve a dependency "
                             "elsewhere in the repo (e.g. --import-path src/pycsl "
                             "so a self-annotate mirror finds ir_schema).")
    g_scope.add_argument("--diagnostics-json", action="store_true",
                        help="On a pipeline error, ALSO print the structured "
                             "diagnostic {code, stage, file, line, message} as a single "
                             "JSON object to stderr (the human message line is unchanged). "
                             "For machine consumption / coded-diagnostic tooling.")

    g_proof = parser.add_argument_group("proof modes")
    g_proof.add_argument("--no-proof", action="store_true",
                        help="Skip the proof step. Only run the pipeline "
                             "(parse, transpile) and report success "
                             "if WhyML is generated.")
    g_proof.add_argument("--typecheck", action="store_true",
                        help="(no-op; default-on since refactor.md Phase D2) The honest "
                             "typecheck gate now runs by DEFAULT on every `--no-proof` run, "
                             "so this flag is a harmless alias kept for backward compatibility. "
                             "Use --no-typecheck to opt OUT (fast emit-only).")
    g_proof.add_argument("--no-typecheck", action="store_true",
                        help="Opt OUT of the default-on honest typecheck gate (refactor.md "
                             "Phase D2): a `--no-proof` run then reports SUCCESS as soon as "
                             "WhyML is emitted, WITHOUT running `why3 prove --type-only`. "
                             "Use for fast byte-diff / dev sweeps and when why3 is absent. "
                             "(A missing why3 is already treated as skip-not-fail by the gate.)")
    g_proof.add_argument("--check-vacuity", dest="check_vacuity",
                        action="store_true", default=True,
                        help="Run the NON-VACUITY GATE (now ON BY DEFAULT — fail-closed). "
                             "After a file verifies, the gate "
                             "re-proves, per body-bearing function, a probe with an extra "
                             "`ensures false`. split_vc emits one such goal per NORMAL-EXIT "
                             "path; the function is VACUOUS iff EVERY one proves Valid (every "
                             "exit's context is inconsistent, so its 'green' is discharged for "
                             "free) — the gate then FAILS, naming the function(s). If even one "
                             "exit is consistent (its false-goal is Unknown/Timeout) the "
                             "function is SOUND, even when a DEAD branch's false-goal is Valid "
                             "(a consequence test's 'didn't-happen' branch is provably dead by "
                             "design — this is why the criterion is ALL exits, not ANY). "
                             "`-> NoReturn` and `#@ \\diverges` functions are EXEMPT (their "
                             "sound green is expected-vacuous on the unreachable normal exit). "
                             "Route #267: each call to a body-less (\\abstract/\\trusted) callee "
                             "is also probed with `check false` after and before it; the "
                             "function is VACUOUS if the point after is unreachable while the "
                             "point before is not (the callee's contract killed the branch). "
                             "The probe filters to the injected goal only and uses a short "
                             "per-goal timelimit; a missing why3 skips it (skip-not-fail).")
    g_proof.add_argument("--no-check-vacuity", dest="check_vacuity",
                        action="store_false",
                        help="Opt OUT of the (default-on) non-vacuity gate — for fast "
                             "byte-diff / dev sweeps, or when a slow-to-manifest vacuity "
                             "probe would dominate. The hole is then unguarded, so use only "
                             "when soundness is being checked elsewhere.")
    g_proof.add_argument("--vacuity-timelimit", metavar="SECS", default="5",
                        help="Per-goal timelimit (seconds) for the non-vacuity gate probe "
                             "(default 5). An inconsistent context derives `false` quickly; "
                             "raise it if you suspect a slow-to-manifest vacuity.")
    g_proof.add_argument("--rocq", metavar="DIR", default=None,
                        help="On SMT prover failure, generate Rocq (Coq) "
                             "proof obligations in DIR. Why3 emits .v files "
                             "with proof skeletons that you complete manually "
                             "and compile with coqc.")
    g_proof.add_argument("--rocq-proofs", metavar="DIR", default=None, nargs="?",
                        const="__auto__",
                        help="Check DIR for pre-existing Rocq proofs when SMT "
                             "provers fail. Each .v file is replayed with coqc "
                             "for full verification. If DIR is omitted, "
                             "auto-detects <file>.proofs/ next to the input.")

    g_strict = parser.add_argument_group("strictness / extra checks")
    g_strict.add_argument("--strict-concurrent-checks", action="store_true",
                        help="Escalate ConcurrencyChecker warnings (unprotected "
                             "shared access, nested locking without lock_order) to "
                             "hard errors. Off by default to preserve backward "
                             "compatibility for existing concurrent-model corpora. "
                             "See config/skills/pycsl-ub-catalog/SKILL.md §7.3.")
    g_strict.add_argument("--verify-imports", action="store_true",
                        help="(#49 gen #30, route #212.) VERIFY each resolved local "
                             "import before trusting its contracts, transitively. OFF by "
                             "default, so no existing behaviour or byte output changes. "
                             "Without it an importing unit BELIEVES every contract of an "
                             "imported module — frames, postconditions, class invariants "
                             "— and nothing checks the module was ever verified: an "
                             "owner declaring `assigns \\nothing` over a body that writes "
                             "`a[0]` FAILS compiled alone while its importer PROVES "
                             "`x - a[0] == 0` (CPython: -4). This flag is the module-level "
                             "certificate that hole needs.")
    g_strict.add_argument("--allow-unverified-imports", action="store_true",
                        help="Permit imports on the C-extension deny-list "
                             "(ctypes, cffi, numpy.ctypeslib, cython) without "
                             "a #@ \\trusted opt-in on the importing function. "
                             "Off by default. See config/skills/pycsl-ub-catalog/SKILL.md §7.4.")
    g_strict.add_argument("--strict-hash-eq-consistency", action="store_true",
                        help="Emit the UB-7.2 hash/eq consistency property as a "
                             "Why3 goal that must be discharged (typically via "
                             "an external proof citation). Off by default — emits "
                             "as an axiom and trusts the user.")
    g_strict.add_argument("--strict-float-finite", action="store_true",
                        help="Drop the FLOAT-FINITE model assumption (route #250): "
                             "model a NaN float value, so every float comparison "
                             "and `==` also requires its operands to be non-NaN "
                             "(`x == x` no longer proves for a float parameter). "
                             "Off by default — floats are assumed finite and "
                             "non-NaN, a declared assumption listed by "
                             "--soundness-report. Costs TRUE claims of the shape "
                             "`\\result == <float arithmetic>`.")
    g_strict.add_argument("--check-behavioral-subtyping", action="store_true",
                        help="Layer D: emit Liskov refinement goals for "
                             "overriding methods (pre_base ⇒ pre_sub, "
                             "post_sub ⇒ post_base). Fails if an override "
                             "strengthens a precondition or weakens a "
                             "postcondition.")
    g_strict.add_argument("--strict-no-exception-propagation", action="store_true",
                        help="(Experimental, off by default.) Under `no_exception` "
                             "treat unannotated callees pessimistically: any call "
                             "from a `no_exception`-enabled function to an abstract "
                             "callee becomes an unsatisfiable VC. See the NoException "
                             "workplan §1.4 / docs/pycsl-static-semantics-reference §2.1.13.")

    g_audit = parser.add_argument_group("proof auditing")
    g_audit.add_argument("--audit-proof", action="store_true",
                        help="Audit every #@ proof rocq / lean directive "
                             "in the file. Confirms each cited theorem is "
                             "declared inside the matching nested namespace "
                             "in the proof file. Audit-only: skips transpile "
                             "and verify. Exit 0 PASS / 1 FAIL.")
    g_audit.add_argument("--audit-proof-rocq", action="store_true",
                        help="Like --audit-proof but only Rocq directives.")
    g_audit.add_argument("--audit-proof-lean", action="store_true",
                        help="Like --audit-proof but only Lean directives.")
    g_audit.add_argument("--rocq-proofs-path", metavar="DIR", default=None,
                        help="Override default Rocq proof dir for --audit-proof "
                             "(default: <file>.proofs/rocq/).")
    g_audit.add_argument("--lean-proofs-path", metavar="DIR", default=None,
                        help="Override default Lean proof dir for --audit-proof "
                             "(default: <file>.proofs/lean/).")
    g_audit.add_argument("--reverify-proofs", action="store_true",
                        help="With --audit-proof: actually invoke coqc / "
                             "lake env lean on the cited proof files and check "
                             "that each cited theorem's assumption set is in "
                             "the kernel-axiom allow-list "
                             "(src/pycsl/proof_axiom_allowlist.py). Closes the "
                             "syntactic-only gap of the default --audit-proof. "
                             "Cached by SHA-256 in .audit-cache/. "
                             "See sticky-01.md Phase 0.")
    return parser.parse_args()


def _build_soundness_report(ir_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """07-1143 R4 — the Soundness Ledger. Classify every function (and thus its VCs)
    into one of four provenance buckets and record what trust each rests on:

      - Modelled    : body-verified — a real proof.
      - Specified   : a `\\trusted`/`\\abstract` method WITH a contract (ensures) — the
                      contract is assumed (axiomatic), so it enters the TCB.
      - Stubbed     : a `\\trusted`/`\\abstract` method with no contract — proves nothing.
      - Confinement : a method carrying `#@ \\preserves` — its HAPPY-boundary promise is
                      assumed, so it enters the TCB.

    Conservative by construction: any non-body provenance is reported as trust (never
    under-reported). `trusted_dependencies` lists the trusted/abstract callees a Modelled
    function relies on, so a body proof that rests on an assumed stub is visible."""
    funcs = ir_data.get("functions", [])
    trusted_names = {f["name"] for f in funcs if f.get("trusted") or f.get("abstract")}
    counts = {"Modelled": 0, "Specified": 0, "Stubbed": 0, "Confinement": 0}
    vcs: List[Dict[str, Any]] = []
    for f in funcs:
        name = f["name"]
        ens = bool(f.get("contracts", {}).get("ensures"))
        if f.get("preserves"):
            bucket = "Confinement"
        elif f.get("trusted") or f.get("abstract"):
            bucket = "Specified" if ens else "Stubbed"
        else:
            bucket = "Modelled"
        counts[bucket] += 1
        deps = sorted((_collect_calls(f.get("body", [])) & trusted_names) - {name})
        vcs.append({
            "function": name, "bucket": bucket, "has_contract": ens,
            "trusted": bool(f.get("trusted")), "abstract": bool(f.get("abstract")),
            "preserves": bool(f.get("preserves")), "trusted_dependencies": deps,
        })
    # ROUTES #250/#253 — the DECLARED MODEL ASSUMPTIONS. Two facts every proof over builtin
    # values rests on, that no VC states and no axiom carries (the same class as the reviewed
    # HASH-EQ-CONSISTENCY axiom, but with no emitted text a plane could classify):
    #   FLOAT-FINITE   a `float` value is finite and non-NaN (the model is Why3 `real`, so
    #                  `x == x`, `x <= x` and trichotomy hold for every float); dropped by
    #                  `--strict-float-finite`.
    #   BUILTIN-EXACT  a value whose static type is a builtin is an EXACT instance of it — no
    #                  subclass overriding a dunder (`class I(int): __sub__ -> 7` makes
    #                  `x - x == 0` false); no strict mode.
    # Reported iff the program RELIES on them, conservatively (over-, never under-reported):
    # FLOAT-FINITE for every comparison/`==`/min/max whose operand subtree mentions a float
    # (a float literal, or a float-typed variable, field or `\result`); BUILTIN-EXACT for
    # every operator (any IR node with an `op`) whose operand subtree reads a builtin-typed
    # variable, field or `\result`. Each entry names the function, the operator and the
    # values it touches.
    _ma_builtin = {"int", "float", "str", "bool", "bytes", "tuple", "list", "dict", "set",
                   "frozenset"}
    _ma_fields: Dict[str, str] = {}
    for _ma_td in ir_data.get("type_decls", []) or []:
        for _ma_fd in (_ma_td.get("fields") or []) if isinstance(_ma_td, dict) else []:
            if isinstance(_ma_fd, dict) and isinstance(_ma_fd.get("type"), str):
                _ma_b = _ma_fd["type"].split("[")[0].strip().lower()
                if _ma_b in _ma_builtin and _ma_fields.get(_ma_fd.get("name")) != "float":
                    _ma_fields[_ma_fd.get("name")] = _ma_b
    _ma_cmp = {"<", "<=", ">", ">=", "==", "!="}
    _ma_float_uses: List[str] = []
    _ma_exact_uses: List[str] = []
    for f in funcs:
        _ma_types: Dict[str, str] = {}
        for _ma_src in (f.get("symbol_table") or {}, f.get("param_annotations") or {}):
            for _ma_n, _ma_t in _ma_src.items():
                if isinstance(_ma_t, str):
                    _ma_b = _ma_t.split("[")[0].strip().lower()
                    if _ma_b in _ma_builtin:
                        _ma_types[_ma_n] = _ma_b
        _ma_ret = str(f.get("return_annotation") or "").split("[")[0].strip().lower()
        _ma_stack: List[Any] = [f.get("body", []), f.get("contracts", {})]
        while _ma_stack:
            _ma_node = _ma_stack.pop()
            if isinstance(_ma_node, list):
                _ma_stack.extend(_ma_node)
                continue
            if not isinstance(_ma_node, dict):
                continue
            _ma_stack.extend(_ma_node.values())
            _ma_op = _ma_node.get("op")
            _ma_call = (_ma_node.get("type") == "Call"
                        and _ma_node.get("func") in ("min", "max"))
            if not (isinstance(_ma_op, str) or _ma_call):
                continue
            # the builtin-typed / float values read anywhere under this operator
            _ma_seen: List[str] = []
            _ma_fseen: List[str] = []
            _ma_fl = False
            if isinstance(_ma_node.get("target"), str) and _ma_node["target"] in _ma_types:
                _ma_seen.append("%s: %s" % (_ma_node["target"], _ma_types[_ma_node["target"]]))
            # (operand, under-a-nested-operator): a value read under a NESTED operator is
            # that operator's operand (reported on its own visit), not this one's — except
            # for float-ness, which flows through arithmetic into the comparison.
            _ma_sub: List[Any] = [(v, False) for k, v in _ma_node.items() if k != "op"]
            while _ma_sub:
                _ma_x, _ma_in = _ma_sub.pop()
                if isinstance(_ma_x, list):
                    _ma_sub.extend((_ma_y, _ma_in) for _ma_y in _ma_x)
                    continue
                if not isinstance(_ma_x, dict):
                    continue
                _ma_nest = _ma_in or isinstance(_ma_x.get("op"), str)
                _ma_sub.extend((_ma_y, _ma_nest) for _ma_y in _ma_x.values())
                _ma_k = _ma_x.get("type")
                _ma_t = None
                if _ma_k == "Var":
                    _ma_t = _ma_types.get(_ma_x.get("name"))
                    _ma_lbl = str(_ma_x.get("name"))
                elif _ma_k == "FieldGet":
                    _ma_t = _ma_fields.get(_ma_x.get("field"))
                    _ma_lbl = "%s.%s" % (_ma_x.get("object"), _ma_x.get("field"))
                elif _ma_k == "Result":
                    _ma_t = _ma_ret if _ma_ret in _ma_builtin else None
                    _ma_lbl = "\\result"
                elif _ma_k == "Number" and isinstance(_ma_x.get("value"), float):
                    _ma_fl = True
                if _ma_t:
                    if _ma_t == "float":
                        _ma_fl = True
                        _ma_fseen.append(_ma_lbl)
                    if not _ma_in:
                        _ma_seen.append("%s: %s" % (_ma_lbl, _ma_t))
            _ma_what = "min/max" if _ma_call else "`%s`" % _ma_op
            _ma_vals = ", ".join(sorted(set(_ma_seen)))
            if _ma_fl and (_ma_call or _ma_op in _ma_cmp):
                _ma_float_uses.append("%s: %s on %s" % (
                    f["name"], _ma_what,
                    ", ".join(sorted(set(_ma_fseen))) or "a float literal"))
            if _ma_seen and isinstance(_ma_op, str):
                _ma_exact_uses.append("%s: %s on %s" % (f["name"], _ma_what, _ma_vals))
    # ROUTE #256 — FIELD-DISJOINT. The model gives every mutable field (a list/dict/set or a
    # record value) its own Why3 region, so two DISTINCT fields never alias: a write through
    # `self.xs` leaves `self.ys` unchanged (the emitted frame says so). Python makes no such
    # promise — `T(L, L)` puts one list in both — and a verified caller that builds the alias
    # is refused (R167, routes #243/#244), so the residue is an alias built in UNVERIFIED code.
    # That is the ownership discipline's rule R1 (docs/pycsl-ownership-discipline.md §2),
    # surfaced here: reported for every function that mutates a mutable field in place
    # (subscript store/delete, a mutator method call, an augmented assignment, a nested field
    # store) while it also reads or mutates ANOTHER mutable field (another field name, or the
    # same field of another object). Conservative: field types are matched by name only.
    _fd_mut: Set[str] = set()
    _fd_recs = {_td.get("name") for _td in (ir_data.get("type_decls") or [])
                if isinstance(_td, dict) and _td.get("kind") == "record"}
    for _fd_td in ir_data.get("type_decls", []) or []:
        for _fd_fd in (_fd_td.get("fields") or []) if isinstance(_fd_td, dict) else []:
            if isinstance(_fd_fd, dict) and isinstance(_fd_fd.get("type"), str) and (
                    _fd_fd["type"].split("[")[0].strip().lower() in (
                        "list", "dict", "set", "bytearray", "deque", "defaultdict")
                    or _fd_fd["type"] in _fd_recs):
                _fd_mut.add(_fd_fd.get("name"))
    _fd_uses: List[str] = []
    for f in (funcs if _fd_mut else []):
        _fd_w: Set[str] = set()
        _fd_r: Set[str] = set()
        _fd_stack: List[Any] = [f.get("body", []), f.get("contracts", {})]
        while _fd_stack:
            _fd_n = _fd_stack.pop()
            if isinstance(_fd_n, list):
                _fd_stack.extend(_fd_n)
                continue
            if not isinstance(_fd_n, dict):
                continue
            _fd_stack.extend(_fd_n.values())
            if (_fd_n.get("type") == "FieldGet" and _fd_n.get("field") in _fd_mut
                    and isinstance(_fd_n.get("object"), str)):
                _fd_r.add("%s.%s" % (_fd_n["object"], _fd_n["field"]))
            _fd_tgt = None
            if _fd_n.get("stmt") in ("ArraySet", "ArraySliceSet", "DelSubscript"):
                _fd_tgt = _fd_n.get("array")
            if (isinstance(_fd_tgt, dict) and _fd_tgt.get("type") == "FieldGet"
                    and _fd_tgt.get("field") in _fd_mut):
                _fd_w.add("%s.%s" % (_fd_tgt.get("object"), _fd_tgt.get("field")))
            if (_fd_n.get("stmt") == "FieldAugAssign" and _fd_n.get("field") in _fd_mut):
                _fd_w.add("%s.%s" % (_fd_n.get("object"), _fd_n.get("field")))
            if (_fd_n.get("stmt") == "FieldAssign" and isinstance(_fd_n.get("object"), str)
                    and "." in _fd_n["object"]
                    and _fd_n["object"].rsplit(".", 1)[1] in _fd_mut):
                _fd_w.add(_fd_n["object"])
            _fd_fn = _fd_n.get("func") if _fd_n.get("type") == "Call" else None
            if isinstance(_fd_fn, str) and _fd_fn.count(".") >= 2:
                _fd_recv = _fd_fn.rsplit(".", 1)[0]
                if _fd_recv.rsplit(".", 1)[1] in _fd_mut:
                    _fd_r.add(_fd_recv)
                    if _fd_fn.rsplit(".", 1)[1] in (
                            "append", "extend", "insert", "pop", "remove", "clear", "sort",
                            "reverse", "add", "discard", "update", "setdefault", "popitem",
                            "intersection_update", "difference_update",
                            "symmetric_difference_update", "appendleft", "popleft"):
                        _fd_w.add(_fd_recv)
        for _fd_x in sorted(_fd_w):
            _fd_o = sorted((_fd_r | _fd_w) - {_fd_x})
            if _fd_o:
                _fd_uses.append("%s: mutates %s, also accesses %s" % (
                    f["name"], _fd_x, ", ".join(_fd_o)))
    assumptions: List[Dict[str, Any]] = []
    if _ma_float_uses:
        assumptions.append({
            "name": "FLOAT-FINITE",
            "statement": "every float value is finite and non-NaN (float is modelled as "
                         "the Why3 real: x == x, x <= x and trichotomy hold)",
            "counterexample": "x = float('nan'): x == x is False (corpus 2500-2502)",
            "strict_mode": "--strict-float-finite",
            "relied_on_by": sorted(set(_ma_float_uses)),
        })
    if _ma_exact_uses:
        assumptions.append({
            "name": "BUILTIN-EXACT",
            "statement": "a value whose static type is a builtin (int/float/str/bool/bytes/"
                         "tuple/list/dict/set) is an exact instance of it, not a subclass "
                         "overriding a dunder",
            "counterexample": "class I(int): __sub__ -> 7; x - x == 7 for x = I(5) "
                              "(corpus 2506)",
            "strict_mode": None,
            "relied_on_by": sorted(set(_ma_exact_uses)),
        })
    if _fd_uses:
        assumptions.append({
            "name": "FIELD-DISJOINT",
            "statement": "two distinct mutable fields (list/dict/set/record-valued; of one "
                         "record, or the same field of two record values) hold distinct "
                         "objects, so a mutation through one is invisible through the other "
                         "(ownership discipline rule R1)",
            "counterexample": "L = [0]; T(L, L): a write through self.xs is seen by "
                              "self.ys (corpus 2570)",
            "strict_mode": None,
            "relied_on_by": sorted(set(_fd_uses)),
        })
    return {"file": filename, "summary": counts, "vcs": vcs,
            "model_assumptions": assumptions}


def _print_soundness_report(report: Dict[str, Any]) -> None:
    """Print the R4 Soundness Ledger: machine-parseable JSON, then a human summary."""
    print("=== SOUNDNESS REPORT (JSON) ===")
    print(_json.dumps(report, indent=2))
    print("\n=== SOUNDNESS REPORT (summary) ===")
    s = report["summary"]
    total = sum(s.values())
    print(f"file: {report['file']}   functions/VCs: {total}")
    for bucket in ("Modelled", "Specified", "Stubbed", "Confinement"):
        print(f"  {bucket:<12}: {s[bucket]}")
    tcb = [v for v in report["vcs"] if v["bucket"] in ("Specified", "Confinement")]
    if tcb:
        print("  --- TCB entries (assumed, not body-verified) ---")
        for v in tcb:
            why = ("\\preserves" if v["bucket"] == "Confinement"
                   else "axiomatic contract")
            print(f"    {v['function']}  [{v['bucket']}]  ({why})")
    dep = [v for v in report["vcs"] if v["bucket"] == "Modelled" and v["trusted_dependencies"]]
    if dep:
        print("  --- body proofs resting on trusted/abstract stubs ---")
        for v in dep:
            print(f"    {v['function']}  depends on: {', '.join(v['trusted_dependencies'])}")
    ma = report.get("model_assumptions") or []
    if ma:
        print("  --- declared model assumptions (not proved; see the reference docs) ---")
        for a in ma:
            print(f"    {a['name']}: {a['statement']}")
            print(f"      counterexample: {a['counterexample']}")
            print(f"      strict mode: {a['strict_mode'] or 'none (always assumed)'}")
            for u in a["relied_on_by"][:10]:
                print(f"      relied on by {u}")
            if len(a["relied_on_by"]) > 10:
                print(f"      ... and {len(a['relied_on_by']) - 10} more (see JSON)")


def _run_pipeline(source_code: str, memory_model: str, args: argparse.Namespace) -> str:
    """Run Modules 1–6 on *source_code*. Returns WhyML code string."""
    print(f"[*] Parsing and Semantic Analysis for '{args.file}'...")
    print(f"[*] Memory model: {memory_model}")

    # [Modules 1-3] Ingest, Parse, and Weave
    ingestor = Module1_Ingestor(source_code)
    # (#45) A PARSE FAILURE MUST BE A REFUSAL, NOT A CRASH. `pure_ast.parse` raises
    # `PyCSLSyntaxError`, a subclass of the builtin `SyntaxError` and NOT of
    # `PyCSLError`, so it escaped `main`'s `except PyCSLError` and surfaced as
    # `[!] UNEXPECTED PIPELINE ERROR: <python message>`. Three python-reference
    # drivers did exactly that — 0202 ("unexpected token in expression"), 0203
    # ("mapping match pattern not yet implemented") and 0204 ("expected ')'") — and
    # ALL THREE ARE `# pycsl-expected: FAIL`, which is the population the reference
    # suite cannot tell a clean refusal from a crash in. Found by running
    # `bin/check-internal-crash-free.py`, the gate built for `0540`, over the OTHER
    # corpus.
    #
    # WRAPPED HERE rather than in `Module1_Ingestor.process`: that method's mirror
    # counterpart is a `\trusted` stub, and a `raise` in its live body moves
    # `check-trusted-raises-honesty` (68 -> 69) and — measured — moves THREE mirror
    # emissions (Module3_Weaver, frontend/__init__, ir_resolve), owing three
    # whole-file re-proofs to restate a refusal `_run_pipeline` can make for
    # nothing. `_run_pipeline` already raises and is already in that plane's
    # population. Same choke-point rule as routes #29/#30/#31/#35/#37/#38.
    #
    # The message is preserved verbatim; only the exception class changes.
    try:
        extracted_data = ingestor.process()
    except PyCSLError:
        raise
    except SyntaxError as _exc_parse:
        from errors import PyCSLParseError as _PyCSLParseErr45
        raise _PyCSLParseErr45(str(_exc_parse), stage="parse") from _exc_parse

    parser_mod = Module2_Parser()
    weaver = Module3_Weaver(source_code, extracted_data, parser_mod)
    unified_ast = weaver.process()

    # [07-1839 P5b] Constant-`exec("…")` straight-line splice: replace a constant exec with
    # its parsed body (verification-equivalent to inline source; whitelist bars control flow).
    # No-op for files without a constant exec. Dynamic exec is handled downstream (P5a/P5a').
    from frontend.exec_splice import splice_constant_exec
    unified_ast = splice_constant_exec(unified_ast)


    # [Module 4 DROPPED — B-final reorder] The pipeline is now M1-3 → M5 (build IR) →
    # all semantic checks (on the IR, via core_ir_semantic.run_ir_semantic_checks) → M6.
    # Module 4 used to run here between M3 and M5; every one of its language-agnostic
    # checks migrated to the IR seam, so its `.process()` had become a no-op visitor and
    # the construction is removed. Downstream (import classifier, ConcurrencyChecker,
    # Module 5) takes the woven AST directly.

    # [ConcurrencyChecker] Static concurrency analysis (warnings only)
    # [Import classifier] UB-7.4 — C-extension boundary
    from frontend.import_classifier import check_imports
    from pathlib import Path as _Path
    _project_root = _Path(__file__).resolve().parents[2]  # …/pycsl/
    check_imports(
        unified_ast,
        stub_dir=_project_root / "src" / "pycsl_lib",
        allow_unverified=getattr(args, "allow_unverified_imports", False),
        filename=getattr(args, "file", "<input>"),
    )

    cc = ConcurrencyChecker(
        unified_ast,
        strict_mode=getattr(args, "strict_concurrent_checks", False),
        filename=getattr(args, "file", "<input>"),
    )
    cc_warnings = cc.check()
    if cc_warnings:
        print(cc.summary())

    # [Module 5] IR Generation
    emitter = Module5_IREmitter(unified_ast)
    json_ir = emitter.generate_json()

    # Validate IR structure before handing off to Module 6
    ir_data = _json.loads(json_ir)
    validate_ir(ir_data)
    # Language-agnostic semantic checks on the IR (spec §6.2; refactor.md Phase B).
    # The migration target for Module4's language-agnostic checks — runs on the IR
    # alone, no AST reference.
    run_ir_semantic_checks(ir_data)
    # [UB-7.1] Mutation-during-iteration check. Walks function bodies for
    # `for x in C: ...` whose body mutates C (and the loop isn't opted
    # out via `#@ allow_iteration_mutation`). Raises PyCSLSemanticError
    # on the first violation. See ub-catalog §7.1.
    from module6_whyml.ir_scanner import IRScanner as _IRScanner
    from errors import PyCSLSemanticError as _PyCSLSemanticError
    for _func in ir_data.get("functions", []):
        _viols = _IRScanner.find_iteration_mutations(_func.get("body", []))
        if _viols:
            v = _viols[0]
            raise _PyCSLSemanticError(
                f"{args.file} (function '{_func.get('name')}', for-loop near "
                f"line {v.get('loop_line', '?')}): UB-7.1 — the loop body "
                f"mutates the iterated collection '{v.get('iterable_name')}'. "
                f"This is undefined behaviour in CPython "
                f"(iterator state corruption). Either rewrite to iterate "
                f"over a snapshot (`for k in list({v.get('iterable_name')}):`) "
                f"or annotate the loop with `#@ allow_iteration_mutation` "
                f"to acknowledge the boundary. "
                f"See config/skills/pycsl-ub-catalog/SKILL.md §7.1."
            )

    # refactor.md Phase C (C2b): run the four post-Module5 IR-resolution passes — in
    # order: import resolution → inheritance (Layers B+C) → Tier-1 composition →
    # inline-globals — via the front-end's single resolution entry, leaving ir_data the
    # fully RESOLVED IR (the wire Module 6 / the core consumes). Pure relocation: the
    # passes and their order are unchanged, so emission stays byte-identical.
    imported_names = _ir_resolve(ir_data, unified_ast, args.file, deep=args.deep, import_paths=args.import_path)

    # ORDER MATTERS, AND THE FIRST PLACEMENT GOT IT WRONG. Landed before Module 5
    # this refusal fired BEFORE the TY3 monomorphization checks and made GT4
    # (polymorphic recursion) DEAD: GT4 keys on a recursive call whose type
    # ARGUMENT is the generic's own TypeVar, which only the subscripted spelling
    # can express, so refusing the spelling first would have silently retired
    # another refusal — and witness 1783 stopped witnessing GT4, which is how it
    # was caught. Running AFTER `_ir_resolve` (which runs monomorphization) keeps
    # GT1/GT3/GT4/BOUND firing first and refuses only a call that SURVIVED them.
    # (#49) ROUTE #215 — `f[T](...)` ON A GENERIC **FUNCTION** IS NOT PYTHON, AND THE
    # MODEL WAS PROVING THINGS ABOUT IT. PEP 695 makes a generic CLASS subscriptable
    # (`Box[int]()` runs; `__class_getitem__`), but a generic FUNCTION is NOT: CPython
    # 3.14 answers `TypeError: 'function' object is not subscriptable` for
    # `ident[int](1)`. PyCSL accepted the call, failed to resolve it to the specialization,
    # and ERASED it to the per-name opaque `pycsl_erased_<var>` — so a local REBOUND from
    # a second such call read the SAME constant and the two values collapsed:
    #
    #     def ident[T](n: int) -> int:  return n      #@ ensures \result == n
    #     def probe() -> int:                         #@ ensures \result == 0
    #         a = ident[int](1); x = a; a = ident[int](2); return x - a
    #
    #   emitted `a := (any int); x := pycsl_erased_a; a := (any int); (!x - pycsl_erased_a)`
    #   and PROVED `\result == 0` — for a program CPython cannot even run. The TRUE twin
    #   (`\result == 0 - 1`, the value the UNSUBSCRIPTED spelling computes) is REFUSED.
    #   The PLAIN call `ident(1)` is lowered faithfully (`a := (ident 1)`) and the false
    #   claim FAILS there, which is the control.
    #
    # MEASURED BLAST RADIUS before landing this (lesson (d3), all four populations):
    # `f[T](...)` on a locally-defined FUNCTION occurs 2 times in the corpus — both in
    # witness 1783, an expected-FAIL file that fires the GT4 polymorphic-recursion refusal
    # first — and ZERO times in the mirror, the live tree and `src/pycsl_lib`. The refusal
    # is therefore byte-inert everywhere that must keep verifying.
    #
    # CHOKE POINT: `_run_pipeline`'s mirror twin is `#@ \trusted`, so this costs no marker,
    # no mirror edit and no re-proof.
    # NOTE THE MODULE: the pipeline parses with `frontend.pure_ast`, NOT the stdlib
    # `ast`, so this scan must use the SAME node classes — the first spelling imported
    # `ast` and matched nothing, which is the `pure_ast`-vs-`ast` confusion route #209
    # was made of (a matcher asked about nodes of the wrong family).
    from frontend import pure_ast as _ast215
    _fn215 = {_n.name for _n in _ast215.walk(unified_ast)
              if isinstance(_n, (_ast215.FunctionDef, _ast215.AsyncFunctionDef))
              and getattr(_n, "type_params", None)}
    if _fn215:
        from errors import PyCSLSemanticError as _PyCSLSemErr215
        for _n215 in _ast215.walk(unified_ast):
            if (isinstance(_n215, _ast215.Call)
                    and isinstance(_n215.func, _ast215.Subscript)
                    and isinstance(_n215.func.value, _ast215.Name)
                    and _n215.func.value.id in _fn215):
                raise _PyCSLSemErr215(
                    f"{args.file} (line {getattr(_n215, 'lineno', 0)}): "
                    f"`{_n215.func.value.id}[...](...)` SUBSCRIPTS A GENERIC FUNCTION at a "
                    f"call site, and that is not Python: PEP 695 makes a generic CLASS "
                    f"subscriptable (`Box[int]()` runs) but a generic FUNCTION is not — "
                    f"CPython answers `TypeError: 'function' object is not subscriptable`. "
                    f"PyCSL used to accept it, fail to resolve it to the specialization, "
                    f"and ERASE the call to an opaque per-name constant, so a local rebound "
                    f"from a second such call read the SAME constant and two different "
                    f"values were proved equal (route #215). Write the plain call "
                    f"`{_n215.func.value.id}(...)`, which IS Python and IS lowered "
                    f"faithfully; the type argument is inferred at the instantiation sites "
                    f"the monomorphizer already scans.",
                    filename=args.file, line=getattr(_n215, "lineno", 0) or 0,
                    stage="ir-semantic", code="PYCSL-SEM-GENERIC-SUBSCRIPT-CALL")

    # (#49) ROUTE #216 — A DUNDER OVERRIDE ERASES THE LISKOV OBLIGATION.
    #
    # Two files identical except for ONE IDENTIFIER, under
    # `--check-behavioral-subtyping`: `Sub.m` returning 0 against `Base.m`'s
    # `#@ ensures \result >= 5` FAILS, and the emission carries the unprovable
    # `goal sub__m_refines_base`. Rename `m` to `__len__` in both and the run prints
    # "All contracts formally proven" over a module whose entire body is
    # `type sub = {  }` — no methods, no override pair, NO GOAL. `#@ conforms_to` has
    # the same hole through a different recorder (Module5_IREmitter rather than
    # ir_resolve.apply_inheritance). Dunders are not emitted as functions, so the pair
    # is never RECORDED, and `PYCSL-SUBTYPING-PAIR` — written for exactly this hazard,
    # naming route #97 — only fires on a pair that was recorded and cannot be RESOLVED.
    #
    # WHY A REFUSAL AND NOT A REPAIR. Emitting dunders is the real fix and is the same
    # work witness 1800 waits on; it changes lowering broadly and is byte-diff-RISKY.
    # Recording the pair anyway means editing `ir_resolve` and `Module5_IREmitter`,
    # both UN-TRUSTED mirror twins, which owes a mirror edit and a re-proof. This site
    # is `_run_pipeline`, whose mirror twin is `\trusted` — the choke-point rule — so
    # the refusal costs no marker, no mirror edit and no re-proof.
    #
    # BLAST RADIUS MEASURED BEFORE LANDING: ZERO dunder override pairs in 1722 corpus
    # files, 53 mirror, 94 live and 104 `pycsl_lib` sources. It is also gated on the
    # flag being ON, so no default run changes at all.
    #
    # IT CANNOT RETIRE AN EARLIER REFUSAL (lesson (n3)): it fires only on DUNDER pairs,
    # and a dunder pair is precisely what no other check can see.
    # (#49) gen #31 — THE REFUSAL IS NOW SCOPED TO THE DUNDERS THAT ARE STILL DROPPED.
    # "Emitting dunders is the real fix" (above) LANDED. With it, an overriding `__len__`
    # IS emitted, the pair IS recorded, and `goal sub____len___refines_base` IS built and
    # correctly FAILS for a weakened contract — measured by the independent reviewer of the
    # emit-dunders report (oracle O6), first with the refusal in place (still refused, no
    # goal built, so the "obligation becomes checkable" claim would have SHIPPED FALSE) and
    # then with it gated off (goal built, goal fails). So the refusal is lifted for every
    # emitted dunder and KEPT for `__new__` and `__post_init__`, which remain dropped for
    # their own measured reasons (`Module5_IREmitter._KEEP_SKIPPED_DUNDERS`) and for which
    # the original hazard is unchanged: the pair is still never recorded, and a run would
    # still report `All contracts formally proven` with the obligation silently absent.
    # A refusal whose stated cause has been REPAIRED must narrow to what is still true, or
    # it becomes the third kind of wrong number this campaign keeps finding — a gate that
    # is green, loud, and about something that no longer exists.
    if getattr(args, "check_behavioral_subtyping", False):
        from frontend import pure_ast as _ast216
        # The dunders `Module5_IREmitter._should_skip_method` still drops. Kept as a
        # literal here rather than imported from the emitter: that method's body is a
        # VERBATIM-MIRRORED specification whose shape is constrained by what the mirror can
        # lower, so it holds no constant to import. The pairing is enforced by corpus
        # 1805/1806 (still refused) and 1827 (an emitted-dunder override whose Liskov goal
        # is now BUILT and fails) — a drift between the two lists moves one of those files.
        _still_dropped216 = {"__init__", "__new__", "__post_init__"}
        _cls216 = {}
        for _n216 in _ast216.walk(unified_ast):
            if isinstance(_n216, _ast216.ClassDef):
                _cls216[_n216.name] = (
                    {_m.name for _m in _n216.body
                     if isinstance(_m, (_ast216.FunctionDef, _ast216.AsyncFunctionDef))
                     and _m.name.startswith("__") and _m.name.endswith("__")
                     and _m.name in _still_dropped216
                     and _m.name != "__init__"},
                    [_b.id for _b in _n216.bases if isinstance(_b, _ast216.Name)],
                    getattr(_n216, "lineno", 0))
        # `#@ conforms_to P` is a CONTRACT COMMENT, so it is not in the AST at all: read
        # it off the source the same way the front end does, by pairing each directive
        # with the next `class` header under it.
        _conf216 = {}
        try:
            _lines216 = open(args.file, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            _lines216 = []
        _pending216 = []
        for _ln216 in _lines216:
            _st216 = _ln216.strip()
            if _st216.startswith("#@ conforms_to "):
                _pending216.append(_st216.split(None, 2)[2].strip())
            elif _st216.startswith("class ") and _pending216:
                _nm216 = _st216[6:].split("(")[0].split(":")[0].strip()
                _conf216.setdefault(_nm216, []).extend(_pending216)
                _pending216 = []
            elif _st216 and not _st216.startswith("#"):
                _pending216 = []
        for _sub216, (_duns216, _bases216, _line216) in sorted(_cls216.items()):
            for _base216 in list(_bases216) + _conf216.get(_sub216, []):
                _other216 = _cls216.get(_base216)
                if _other216 is None:
                    continue
                _shared216 = sorted(_duns216 & _other216[0])
                if not _shared216:
                    continue
                from errors import PyCSLSemanticError as _PyCSLSemErr216
                raise _PyCSLSemErr216(
                    f"{args.file} (line {_line216}): class `{_sub216}` overrides "
                    f"`{_base216}`'s " + ", ".join("`" + _d + "`" for _d in _shared216)
                    + " and `--check-behavioral-subtyping` was requested, but a DUNDER is "
                    "not emitted as a function, so no override pair is recorded and NO "
                    "refinement goal is built. The run would report `All contracts "
                    "formally proven` with the substitutability obligation silently "
                    "absent (route #216, the same shape as route #97). Refusing instead "
                    "of certifying. FIX: give the method a non-dunder name — the "
                    "identical program spelled `m` instead of `__len__` produces the goal "
                    "`sub__m_refines_base` and is checked — or drop "
                    "`--check-behavioral-subtyping`, which then claims nothing about this "
                    "pair rather than claiming something false.",
                    filename=args.file, line=_line216,
                    stage="ir-semantic", code="PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED")

    # (#49) gen #31 — `#@ assumes bounded_int(N)` FOR AN N WHY3 HAS NO MODULE FOR.
    # `preamble.py` emits `use mach.int.Int<N>` with N interpolated straight from the
    # directive, and why3's `mach/int.mlw` defines EXACTLY Int16, Int31, Int32, Int63 and
    # Int64. `#@ assumes bounded_int(8)` therefore emits `use mach.int.Int8` and the run
    # ends with
    #     Module Int8 not found in library mach.int
    #     [-] Verification FAILED or INCOMPLETE.
    # — a why3 LIBRARY error for a directive PyCSL accepted, with nothing to tell the
    # reader which widths exist. It FAILS CLOSED, so this is a diagnosability defect and
    # not a soundness one, and it is the same family as the six broken advice messages gen
    # #30's audit repaired: the compiler told the user to write something that does not
    # compile, and said nothing when they did.
    # annotations.md documents the form as `bounded_int(N)` with N unconstrained ("Use
    # `mach.int.IntN` types"), so the DOCUMENTATION is repaired alongside this.
    # FOUND BY `bin/check-directive-enforcement.py`: the SATISFYING half of the `assumes`
    # pair would not verify, which is exactly what that half is for — a violation that
    # fails tells you nothing if the honest program fails too.
    # CENSUS: the corpus uses only 32 and 64; the mirror, the live tree and `pycsl_lib` use
    # `bounded_int` not at all. Byte-inert by measurement.
    _BI_OK = (16, 31, 32, 63, 64)
    try:
        _lines_bi = open(args.file, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        _lines_bi = []
    for _i_bi, _ln_bi in enumerate(_lines_bi):
        _st_bi = _ln_bi.strip()
        if not _st_bi.startswith("#@ assumes bounded_int("):
            continue
        _arg_bi = _st_bi[len("#@ assumes bounded_int("):].split(")")[0].strip()
        if not _arg_bi.isdigit() or int(_arg_bi) in _BI_OK:
            continue
        from errors import PyCSLSemanticError as _PyCSLSemErrBI
        raise _PyCSLSemErrBI(
            "`#@ assumes bounded_int(%s)` (line %d): Why3's `mach.int` library defines "
            "machine-integer modules for widths %s ONLY. This directive lowers to "
            "`use mach.int.Int%s`, which why3 answers with `Module Int%s not found in "
            "library mach.int` — a LIBRARY error for a directive PyCSL accepted, telling "
            "you nothing about which widths exist. Refusing instead. FIX: use one of %s, "
            "or drop the directive and reason about unbounded integers (PyCSL's default)."
            % (_arg_bi, _i_bi + 1, ", ".join(str(_w) for _w in _BI_OK), _arg_bi, _arg_bi,
               ", ".join(str(_w) for _w in _BI_OK)),
            filename=args.file, line=_i_bi + 1,
            stage="ir-semantic", code="PYCSL-SEM-BOUNDED-INT-WIDTH")

    # (#49) ROUTE #223 — A `Protocol` MEMBER'S BODY IS DISCARDED AND ITS CONTRACT IS
    # ASSUMED, SO AN IMPLEMENTATION THAT CONTRADICTS ITS OWN CONTRACT CERTIFIES.
    # `_emit_protocol_interface` emits each member as an `abstract: True` function — a
    # bodyless `val` defined BY ITS CONTRACT, the refinement target (P1a) — and
    # `visit_ClassDef` returns WITHOUT `generic_visit`, so the body is never visited. Its
    # own comment states the premise: "the protocol class body carries ONLY member
    # declarations ... so skipping the walk is correct", and the member's body is "`...`/
    # `pass` by PEP 544 convention". PEP 544 also permits a DEFAULT IMPLEMENTATION, and
    # when one is written the model keeps the CONTRACT and drops the CODE:
    #
    #     class P(Protocol):
    #         #@ ensures \result == 99
    #         def m(self) -> int:
    #             return 1                 # the real answer, and it is not 99
    #     class C(P):
    #         def __init__(self) -> None: self.v: int = 0
    #     #@ ensures \result == 99
    #     def use() -> int:
    #         c = C()
    #         return c.m()
    #     [+] Verification SUCCESS! All contracts formally proven.
    #
    # CPython answers **1**, and the TRUE twin (`\result == 1`) FAILS. The emission is the
    # whole story — `val c__m (self: c) : int ensures { (result = 99) }`, an abstract val
    # carrying the protocol's contract, with `return 1` nowhere in the module. Drop the
    # `(Protocol)` base and the identical class FAILS, which is what makes this a route and
    # not a missing feature: the checker works, and one token switches it off.
    #
    # REFUSED, NOT MODELLED. Emitting the default implementation AND keeping the abstract
    # refinement target is a real design question (the member is both a specification and a
    # definition, and `#@ conforms_to` refinement is stated against the former), and the
    # honest interim answer is to reject the construct the model cannot carry rather than
    # to trust it. A `...`/`pass` body — the convention the code already documents — is
    # untouched, and so is every Protocol that declares members without implementing them.
    #
    # AT THE CHOKE POINT, for the reason route #222 learned an hour earlier: the natural
    # site is `_emit_protocol_interface`, whose mirror twin is `\trusted` and contains NO
    # `raise` today, so a refusal there would ADD it to
    # `check-trusted-raises-honesty`'s SILENT population and move a ratchet. `_run_pipeline`
    # is already in that population.
    #
    # CENSUS BEFORE LANDING (lesson d3): `class ...(Protocol)` occurs in 6 corpus files,
    # 0 mirror, 0 live and 0 `pycsl_lib` sources, and NONE declares a member with a
    # non-trivial body.
    _proto223 = []
    for _n223 in _ast.walk(unified_ast):
        if not isinstance(_n223, _ast.ClassDef):
            continue
        _isp223 = False
        for _b223 in _n223.bases:
            _bn223 = (_b223.id if isinstance(_b223, _ast.Name)
                      else (_b223.attr if isinstance(_b223, _ast.Attribute) else ""))
            if _bn223 == "Protocol":
                _isp223 = True
                break
        if not _isp223:
            continue
        for _m223 in _n223.body:
            if not isinstance(_m223, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                continue
            _body223 = [_st223 for _st223 in _m223.body
                        if not (isinstance(_st223, _ast.Expr)
                                and isinstance(getattr(_st223, "value", None), _ast.Constant)
                                and isinstance(_st223.value.value, str))]   # drop docstrings
            if len(_body223) == 1:
                _only223 = _body223[0]
                if isinstance(_only223, _ast.Pass):
                    continue
                if (isinstance(_only223, _ast.Expr)
                        and isinstance(getattr(_only223, "value", None), _ast.Constant)
                        and _only223.value.value is Ellipsis):
                    continue
            if not _body223:
                continue
            _proto223.append((_n223.name, _m223.name, getattr(_m223, "lineno", 0)))
    if _proto223:
        _c223, _mn223, _l223 = _proto223[0]
        from errors import PyCSLSemanticError as _PyCSLSemErr223
        raise _PyCSLSemErr223(
            "`Protocol` member '%s.%s' (line %d) has a DEFAULT IMPLEMENTATION, and a "
            "protocol member is emitted as a bodyless `val` DEFINED BY ITS CONTRACT — the "
            "refinement target every `#@ conforms_to` is checked against. The body would be "
            "DISCARDED while the contract was ASSUMED, so a member whose code CONTRADICTS "
            "its own contract would certify: measured, `#@ ensures \\result == 99` over "
            "`return 1`, inherited by a conforming class, PROVED `\\result == 99` for a "
            "call CPython answers 1, and the TRUE twin was rejected. Refusing instead of "
            "trusting. FIX: give the member the `...` or `pass` body PEP 544 uses for a "
            "protocol declaration and put the implementation in the conforming class, where "
            "it is CHECKED against this contract — or drop the `Protocol` base, and the "
            "class is verified as an ordinary class."
            % (_c223, _mn223, _l223),
            filename=args.file, line=_l223,
            stage="ir-semantic", code="PYCSL-SEM-PROTOCOL-DEFAULT-IMPL")

    # (#49) ROUTE #222 — AN `@overload` STUB CONTRIBUTES ONLY ITS `ensures`, AND EVERY
    # OTHER CLAUSE WENT NOWHERE AND SAID NOTHING.
    # `Module5_IREmitter._synthesize_overload_guard` reads `csl_ensures` and nothing else;
    # the stub node is then discarded at `visit_FunctionDef`'s early return. MEASURED:
    #     #@ requires x > 100
    #     @overload
    #     def f(x: int) -> int: ...
    #     #@ ensures \result == x
    #     def f(x: int) -> int:  return x
    #     #@ ensures \result == 0
    #     def use() -> int:      return f(0)      # violates the declared precondition
    #     [+] Verification SUCCESS! All contracts formally proven.
    # and the emission shows the clause is not weakened but ABSENT:
    #     let f (x: int) : int  ensures { (result = x) }  =  x
    # Move the identical clause to the IMPLEMENTATION and `f(0)` is correctly refused, so
    # the precondition machinery was never broken — it was bypassed by WHERE the clause was
    # written. Found by walking the SECOND early return of `visit_FunctionDef`; the FIRST
    # was route #219.
    #
    # SOUND, AND REFUSED ANYWAY. Dropping a PRECONDITION proves the callee under a WEAKER
    # assumption, so the body must discharge its own postcondition without it and no caller
    # gains anything false. What is wrong is the headline: a contract the user WROTE is
    # enforced nowhere while the run says `All contracts formally proven` — the sentence
    # routes #216 and #219 turn on. Carrying a precondition into a guarded family is a real
    # design question (which arm's guard does it hide under?) and a refusal is not where to
    # answer it.
    #
    # WHY HERE AND NOT AT THE SITE. The natural home is `visit_FunctionDef`'s own early
    # return. Placed there it adds a `raise` to a LIVE function whose mirror twin is
    # `\trusted` and declares no `#@ raises`, which moves `check-trusted-raises-honesty`
    # 62 -> 64 (TWO mirror stubs are named `visit_FunctionDef`, so one new raise counts
    # twice) and would owe a `#@ raises` edit plus the re-proof of every mirror that calls
    # them. `_run_pipeline`'s own mirror twin is `\trusted` AND ALREADY IN THAT POPULATION,
    # so the refusal costs no marker, no emission move, no new definition and no new
    # honesty entry — the CHOKE-POINT RULE, the same reasoning routes #206-#215 used.
    # The cost is that the clauses must be read off the SOURCE TEXT rather than the AST
    # (a `#@` line is a comment), exactly as route #216's `conforms_to` scan does below.
    #
    # CENSUS BEFORE LANDING (lesson d3): `@overload` occurs in ZERO corpus files, 1 mirror,
    # 3 live and 1 `pycsl_lib` source, and NONE puts a non-`ensures` clause on a stub.
    _OVL222 = ("requires", "assigns", "raises", "no_exception", "diverges", "variant",
               "loop invariant", "loop variant", "class invariant")
    try:
        _lines222 = open(args.file, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        _lines222 = []
    _pend222 = []          # non-`ensures` clause names seen in the current `#@` block
    _ovl222 = False        # an `@overload` decorator seen since the block started
    for _i222, _ln222 in enumerate(_lines222):
        _st222 = _ln222.strip()
        if _st222.startswith("#@ "):
            _cl222 = _st222[3:].strip()
            for _k222 in _OVL222:
                if _cl222 == _k222 or _cl222.startswith(_k222 + " "):
                    _pend222.append(_k222)
                    break
        elif _st222.startswith("@") and _st222.lstrip("@").split("(")[0].strip().endswith("overload"):
            _ovl222 = True
        elif _st222.startswith("def ") or _st222.startswith("async def "):
            if _ovl222 and _pend222:
                _nm222 = _st222.split("def ", 1)[1].split("(")[0].strip()
                from errors import PyCSLSemanticError as _PyCSLSemErr222
                raise _PyCSLSemErr222(
                    "`@overload` stub '%s' (line %d) carries `#@ %s`, and an `@overload` "
                    "stub only ever contributes its `#@ ensures` clauses — each becomes "
                    "the guarded postcondition `isinstance(p, T) ==> Q` on the "
                    "IMPLEMENTATION, and the stub node itself is discarded. Every other "
                    "clause would be DROPPED WITHOUT A WORD while the run still reported "
                    "`All contracts formally proven`: measured, `#@ requires x > 100` on a "
                    "stub left the call `f(0)` accepted, and the emitted `let f` carried no "
                    "`requires` at all. Refusing instead of discarding. FIX: move the "
                    "clause to the IMPLEMENTATION `def`, where it is enforced at every "
                    "call site — the identical `#@ requires` there correctly refuses "
                    "`f(0)`."
                    % (_nm222, _i222 + 1, "`, `#@ ".join(sorted(set(_pend222)))),
                    filename=args.file, line=_i222 + 1,
                    stage="ir-semantic", code="PYCSL-SEM-OVERLOAD-CLAUSE-DISCARDED")
            _pend222 = []
            _ovl222 = False
        elif _st222 and not _st222.startswith("#"):
            _pend222 = []
            _ovl222 = False

    # (#49) gen #31 — `#@ mixin` HAD NO ENFORCED CONSEQUENCE, IN EITHER DIRECTION.
    # annotations.md §2.7 row 1: "Mixin — `#@ mixin` — `class` — Marks the class as a
    # composable mixin (not instantiated directly)." Both halves were measured ABSENT:
    #   * the flagship driver 0549 with `#@ mixin` DELETED from `CoreEmit` — still named in
    #     `#@ compose_from CoreEmit, MapOps` — composed and verified exactly as before;
    #   * a `#@ mixin` class instantiated directly verified too, and so did the same file
    #     with the marker removed, so the two halves were indistinguishable.
    # `ir_resolve.apply_composition` reads the names off the `#@ compose_from` line and
    # never consults the marker. Found by `bin/check-directive-enforcement.py` while trying
    # to write the directive's enforcement pair: there was no violating program to write,
    # which is that plane's third kind of answer, filed as
    # `getting-better/open-routes/finding-mixin-marker-has-no-teeth.md`.
    #
    # NOT A SOUNDNESS HOLE — the flatten-and-re-verify compensation (S2b, finding w66) does
    # not depend on the marker, so deleting it removed a LABEL and not a check. What was at
    # risk is the READING: "this class is a mixin, so it is never instantiated, so I need
    # not reason about its `__init__` or its class invariant standing alone." That reading
    # was unsupported, and a directive with no teeth is a directive a reader trusts for a
    # guarantee that is not there.
    #
    # WHY HERE AND NOT IN `apply_composition`, WHICH IS WHERE IT BELONGS — MEASURED, NOT
    # PREFERRED. The natural home reads `is_mixin` off the class's `type_decl`, and
    # **`type_decls` IS EMPTY FOR EXACTLY THE CLASSES THAT ARE MIXINS**: a class with no
    # fields and no `__init__` produces no record decl (its Why3 type is the `int` alias),
    # and the flagship mixin shape has neither. Instrumented `apply_composition` on the
    # violating file and it printed `DBG decls: [] mixins: ['CoreEmit', 'MapOps']` — the
    # pass cannot see the marker it would need. `_run_pipeline` has the SOURCE TEXT, its
    # mirror twin is `\trusted` and already in the raises-honesty population, and a `#@`
    # line is a comment, so the choke-point rule (routes #206-#215, #222, #223) applies.
    #
    # CENSUS BEFORE LANDING (lesson d3): 17 sources declare `#@ mixin`, and ZERO name an
    # unmarked class in a `#@ compose_from` list. Corpus-inert.
    try:
        _lines_mx = open(args.file, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        _lines_mx = []
    _mx_marked = set()        # class names carrying `#@ mixin`
    _mx_composed = []         # (composer_line, [names]) from each `#@ compose_from`
    _mx_pend = False          # a `#@ mixin` seen since the block started
    for _i_mx, _ln_mx in enumerate(_lines_mx):
        _st_mx = _ln_mx.strip()
        if _st_mx.startswith("#@ "):
            _cl_mx = _st_mx[3:].strip()
            if _cl_mx == "mixin":
                _mx_pend = True
            elif _cl_mx.startswith("compose_from "):
                _mx_composed.append((_i_mx + 1,
                                     [_n.strip() for _n in
                                      _cl_mx[len("compose_from "):].split(",")
                                      if _n.strip()]))
        elif _st_mx.startswith("class "):
            if _mx_pend:
                _mx_marked.add(_st_mx[len("class "):].split("(")[0].split(":")[0].strip())
            _mx_pend = False
        elif _st_mx and not _st_mx.startswith("#") and not _st_mx.startswith("@"):
            _mx_pend = False
    for _ln_no_mx, _names_mx in _mx_composed:
        for _nm_mx in _names_mx:
            if _nm_mx not in _mx_marked:
                from errors import PyCSLSemanticError as _PyCSLSemErrMx
                raise _PyCSLSemErrMx(
                    "`#@ compose_from` (line %d) names '%s', which is not declared "
                    "`#@ mixin`. A composable mixin must SAY SO: the marker is what tells a "
                    "reader the class is flattened into a composer rather than used on its "
                    "own, and composing a class that never claimed to be one silently "
                    "changes what its `__init__` and its class invariant mean. Until this "
                    "refusal the marker had no enforced consequence at all — the flagship "
                    "0549 with it deleted composed and verified unchanged. FIX: put "
                    "`#@ mixin` on the line before `class %s:`, or drop '%s' from the "
                    "`#@ compose_from` list."
                    % (_ln_no_mx, _nm_mx, _nm_mx, _nm_mx),
                    filename=args.file, line=_ln_no_mx,
                    stage="ir-semantic", code="PYCSL-SEM-COMPOSE-FROM-NOT-A-MIXIN")
    # ... and the OTHER half of the same sentence: "not instantiated directly". The
    # marked-name set is already in hand, so this is one AST walk. A mixin's `__init__`
    # and its class invariant are written to be read AS PART OF A COMPOSER — the whole
    # point of the flatten-and-re-verify discipline is that the composer's record is what
    # the methods are proved against — so a direct construction gets a record the mixin's
    # own methods were never verified over.
    #
    # ONLY the CALLEE position: `MixinCls(...)`. A mixin name in an ARGUMENT
    # (`isinstance(x, MixinCls)`) or an annotation is not a construction and is left alone.
    #
    # CENSUS BEFORE LANDING (lesson d3), by AST rather than by grep: 20 sources declare
    # `#@ mixin`, 19 marked classes between them, and ZERO constructor calls of any of
    # them anywhere in the corpus, `src/`, the mirror or `pycsl_lib`. Corpus-inert.
    if _mx_marked:
        for _n_mi in _ast.walk(unified_ast):
            if (isinstance(_n_mi, _ast.Call)
                    and isinstance(_n_mi.func, _ast.Name)
                    and _n_mi.func.id in _mx_marked):
                from errors import PyCSLSemanticError as _PyCSLSemErrMi
                raise _PyCSLSemErrMi(
                    "`#@ mixin` class '%s' is CONSTRUCTED here (line %d). A mixin is "
                    "declared composable, not instantiable: its methods are verified "
                    "against the COMPOSER's record (the flatten-and-re-verify discipline), "
                    "so a direct construction produces an object whose own methods were "
                    "never proved over it, and its `__init__` and class invariant are "
                    "written to be read as part of a composer. Until gen #31 neither half "
                    "of `#@ mixin` was enforced. FIX: construct the `#@ compose_from` "
                    "class that composes '%s', or drop the `#@ mixin` marker if '%s' is "
                    "meant to be used on its own."
                    % (_n_mi.func.id, getattr(_n_mi, "lineno", 0),
                       _n_mi.func.id, _n_mi.func.id),
                    filename=args.file, line=getattr(_n_mi, "lineno", 0),
                    stage="ir-semantic", code="PYCSL-SEM-MIXIN-INSTANTIATED")

    # (#49) gen #31 — A `#@ lemma` WITH NO `#@ assigns` CLAUSE AT ALL. annotations.md
    # §2.1.16 states five hard-error rules for a lemma; four were enforced and the fifth
    # only half was. `core_ir_semantic._check_lemma` rejects a DECLARED frame that is not
    # `\nothing`:
    #     for t in contracts.get("assigns", []) or []:
    #         if not (… t.get("type") == "Nothing"): raise …
    # and an EMPTY list satisfies that loop vacuously, so omitting the clause entirely was
    # the one way past a rule the documentation states as a hard error. Found by writing the
    # program each hard-error sentence in annotations.md describes — the same audit that
    # confirmed the other eight.
    #
    # NOT A SOUNDNESS HOLE, and the probes matter: a frameless lemma that actually MUTATES
    # is still caught one layer down. Writing a module global is refused outright ("writes
    # g through a `global` declaration"); writing a list PARAMETER makes the emitted frame
    # obligation unprovable and the file FAILS. What was missing is the DIAGNOSTIC — the
    # user got an unprovable frame goal where the rule has a name.
    #
    # WHY HERE AND NOT IN `_check_lemma`, WHICH IS WHERE IT BELONGS. Measured, and the
    # measurement is the point. `_check_lemma`'s mirror twin is UN-TRUSTED, so its text is
    # emitted verbatim and must PROVE. Both natural spellings broke the self-proof:
    #   * `if not (contracts.get("assigns", []) or []):` — an `or`-defaulted `.get` on a
    #     heterogeneous dict in BOOLEAN context;
    #   * a counter incremented inside the existing loop — which ALSO broke it, and at the
    #     PRE-EXISTING line `if not (contracts.get("ensures") or []):`, with
    #     `This expression has type 'mu -> option.Option.option int, but is expected to
    #     have type int`. Adding a use of `contracts` moved the dict's inferred value type
    #     and took an untouched line down with it.
    # That is the self-hosting constraint doing exactly what it exists to do: the compiler
    # may not grow a line it cannot verify about itself. `_run_pipeline`'s mirror twin is
    # `\trusted` and already in the raises-honesty population, so the CHOKE-POINT RULE
    # (routes #206-#215, #222, #223) applies — no marker, no emission move, no honesty
    # entry, and the clause is read off the SOURCE TEXT because a `#@` line is a comment.
    #
    # CENSUS BEFORE LANDING (lesson d3): 16 `#@ lemma` declarations across the corpus and
    # `src/`. Thirteen already carry `#@ assigns`; the three that do not are
    # `1731`/`1733`/`1747`, all `# pycsl-expected: FAIL` witnesses for the OTHER lemma
    # rules — and `_check_lemma` tests `\diverges`, `ensures` and `-> None` BEFORE any
    # frame check, so each still refuses with its own message (verified). Byte-inert.
    try:
        _lines_lem = open(args.file, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        _lines_lem = []
    _lem_blk = []          # the `#@` clause keywords of the current block
    for _i_lem, _ln_lem in enumerate(_lines_lem):
        _st_lem = _ln_lem.strip()
        if _st_lem.startswith("#@ "):
            _lem_blk.append(_st_lem[3:].strip())
        elif _st_lem.startswith("def ") or _st_lem.startswith("async def "):
            if (any(_c == "lemma" for _c in _lem_blk)
                    and not any(_c.startswith("assigns") for _c in _lem_blk)):
                _nm_lem = _st_lem.split("def ", 1)[1].split("(")[0].strip()
                from errors import PyCSLSemanticError as _PyCSLSemErrLem
                raise _PyCSLSemErrLem(
                    "`#@ lemma` '%s' (line %d) has no `#@ assigns` clause, and a lemma "
                    "must state `#@ assigns \\nothing` explicitly. The clause is the ghost "
                    "discipline written down — a lemma is erased at extraction and computes "
                    "nothing — and the rule was enforced only for a lemma that DECLARED a "
                    "frame, so omitting it entirely was the one way past it. FIX: add "
                    "`#@ assigns \\nothing` to '%s'."
                    % (_nm_lem, _i_lem + 1, _nm_lem),
                    filename=args.file, line=_i_lem + 1,
                    stage="ir-semantic", code="PYCSL-SEM-LEMMA-NO-ASSIGNS")
            _lem_blk = []
        elif _st_lem and not _st_lem.startswith("#"):
            _lem_blk = []

    # (#49) gen #31 — `#@ verify_module <name>` MUST NAME A CAPITALIZED IDENTIFIER, and
    # nothing said so. `#@ verify_module leaf` emits `module leafSig` / `module leaf`, and
    # Why3 rejects a lowercase module name outright:
    #     syntax error: expected module name must be an capitalized identifier
    #     (token UIDENT_NQ), found "leafSig"
    # MEASURED on a two-method class, lowercase vs capitalized, everything else identical.
    # There is no refusal, no warning and no hint that the DIRECTIVE is the cause: the user
    # gets a Why3 syntax error naming a symbol (`leafSig`) that appears nowhere in their
    # source, because the `Sig` suffix is synthesized by the emitter. A wrong-looking error
    # about a name you did not write is the worst kind of diagnostic — it sends the reader
    # to the wrong file.
    #
    # NOT A SOUNDNESS ISSUE: the run FAILS, loudly, and nothing is proved. This is a
    # diagnostic repair, and it is fail-closed either way — what changes is WHICH message
    # the user reads. Found while trying to write this directive's enforcement pair for
    # `bin/check-directive-enforcement.py`; the pair itself is not written, because the
    # observable difference `verify_module` makes needs `#@ proof` axioms to co-reside or
    # not, and those need a Rocq toolchain this switch does not have (0211-0220 fail on
    # `Why3 Coq library not found`). The directive stays UNCOVERED there and honest here.
    #
    # WHY HERE: the choke-point rule (routes #206-#215, #222, #223). `_run_pipeline`'s
    # mirror twin is `\trusted` and ALREADY in the raises-honesty population, so a refusal
    # placed here costs no new marker, no emission move and no new honesty entry.
    #
    # CENSUS BEFORE LANDING (lesson d3): `#@ verify_module` occurs in ZERO corpus files and
    # in exactly one library source, `src/pycsl_lib/os/UnixInodeFileSystem.py` (`ReadMod`,
    # `FindSlotMod`, `FindFreeMod`) — all three already capitalized. Byte-inert.
    try:
        _lines_vm = open(args.file, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        _lines_vm = []
    for _i_vm, _ln_vm in enumerate(_lines_vm):
        _st_vm = _ln_vm.strip()
        if not _st_vm.startswith("#@ "):
            continue
        _cl_vm = _st_vm[3:].strip()
        if not _cl_vm.startswith("verify_module "):
            continue
        _nm_vm = _cl_vm[len("verify_module "):].strip()
        if not _nm_vm or _nm_vm[0].isupper():
            continue
        from errors import PyCSLSemanticError as _PyCSLSemErrVM
        raise _PyCSLSemErrVM(
            "`#@ verify_module %s` (line %d) names a group that is lowered to a Why3 "
            "`module`, and Why3 module names must be CAPITALIZED identifiers. Emitted as "
            "written, this produces `module %sSig` and Why3 stops with `syntax error: "
            "expected module name must be an capitalized identifier (token UIDENT_NQ), "
            "found \"%sSig\"` — an error naming a symbol that appears nowhere in your "
            "source, because the `Sig` suffix is synthesized. Refusing here so the message "
            "names the directive instead. FIX: capitalize the group name (`#@ "
            "verify_module %s`); methods sharing a group name co-reside in one module, so "
            "capitalize every occurrence of it."
            % (_nm_vm, _i_vm + 1, _nm_vm, _nm_vm, _nm_vm[:1].upper() + _nm_vm[1:]),
            filename=args.file, line=_i_vm + 1,
            stage="ir-semantic", code="PYCSL-SEM-VERIFY-MODULE-NAME-NOT-CAPITALIZED")

    # (#49) ROUTE #212 — THE MODULE-LEVEL CERTIFICATE. The importing unit believes every
    # contract of an imported module and nothing checks that the module was verified.
    # `--verify-imports` (OFF by default: no existing run changes) discharges the
    # assumption the only way it can be discharged — by verifying the module. Transitive,
    # with a seen-set in the environment so a cycle terminates and a diamond is verified
    # once. Deliberately NOT the default: turning it on re-verifies a dependency on every
    # run of every importer, which is a policy decision for the user, not for a repair.
    if getattr(args, "verify_imports", False):
        import subprocess as _sp212
        from frontend.ir_resolve import _resolve_module_path as _rmp212
        _seen212 = set(filter(None, os.environ.get("PYCSL_VERIFIED_IMPORTS", "").split(os.pathsep)))
        _self212 = os.path.abspath(args.file)
        _seen212.add(_self212)
        _targets212 = []
        for _n212 in _ast.walk(unified_ast):
            if isinstance(_n212, _ast.Import):
                for _a212 in _n212.names:
                    _targets212.append((_a212.name, 0))
            elif isinstance(_n212, _ast.ImportFrom) and _n212.module:
                _targets212.append((_n212.module, getattr(_n212, "level", 0) or 0))
        for _mod212, _lvl212 in _targets212:
            _path212 = _rmp212(_mod212, _lvl212, args.file)
            if not _path212:
                continue
            _path212 = os.path.abspath(_path212)
            if _path212 in _seen212:
                continue
            _env212 = dict(os.environ)
            _env212["PYCSL_VERIFIED_IMPORTS"] = os.pathsep.join(sorted(_seen212 | {_path212}))
            # `args.memory_model` DEFAULTS TO None, not to "hoare": passing it straight
            # through made subprocess raise "expected str, bytes or os.PathLike object,
            # not NoneType" for every import that resolved. Measured on the first
            # `from pycsl_lib.mth import factorial` this flag ever saw.
            _mm212 = getattr(args, "memory_model", None) or "hoare"
            _cmd212 = [sys.executable, os.path.abspath(__file__), "--verify-imports",
                       "--memory-model", _mm212, _path212]
            for _ip212 in (args.import_path or []):
                _cmd212 += ["--import-path", _ip212]
            _r212 = _sp212.run(_cmd212, capture_output=True, text=True, env=_env212)
            if "Verification SUCCESS" not in (_r212.stdout or ""):
                from errors import PyCSLSemanticError as _PyCSLSemErr212
                raise _PyCSLSemErr212(
                    f"{args.file}: `--verify-imports` was given and the imported module "
                    f"'{_mod212}' ({_path212}) does NOT verify, so none of its contracts "
                    f"may be believed here. Verify it first, or drop the flag and accept "
                    f"that its frames, postconditions and class invariants are ASSUMED "
                    f"(route #212: an owner declaring `assigns \\nothing` over a body "
                    f"that writes `a[0]` fails alone while its importer proves "
                    f"`x - a[0] == 0`).",
                    filename=args.file, stage="imports", code="PYCSL-SEM-IMPORT-UNVERIFIED")
            _seen212.add(_path212)

    # (#49) ROUTE #213 — THE REFUSAL THAT USED TO BE HERE IS REVERTED, AND THE MEASUREMENT
    # THAT REMOVED IT IS THE POINT. The route is real (two reads of the same `getattr` are
    # ONE CONSTANT across a call that writes the attribute; witness carriers in
    # `getting-better/open-routes/`), and the refusal shipped after a blast-radius census
    # that covered the CORPUS and `src/pycsl_lib` — where the shape does not occur — and
    # NOT the mirror or the live tree, where `getattr(self, "_x", {})` is a ubiquitous
    # idiom. Measured afterwards: **212 live functions and 14 mirror functions** read the
    # same `getattr` twice with an intervening call, and the mirror stopped EMITTING (44 of
    # 53 sources), which took four emission-dependent planes red. Narrowing to a NON-`self`
    # receiver that is an `Any`/unannotated PARAMETER still leaves 12 live and 4 mirror
    # hits — including this very file's `_run_pipeline`, which reads `getattr(args, …)`
    # twice, because that is how argparse namespaces are read everywhere.
    # SO A SYNTACTIC IR-SEAM REFUSAL CANNOT SEPARATE THE ROUTE FROM THE IDIOM: the thing
    # that distinguishes them is the receiver's static CLASS (`_ga_cls` in
    # `module6_whyml/expressions.py`), and that is Module-6 knowledge. The faithful repair
    # is the STATE-KEYED DEVICE priced in the route doc — `val function
    # pycsl_getattr_missing_<h> (s: int) : int` applied to `!_pyobj_state` — which fixes
    # the route without refusing a single existing program. Route #213 is therefore OPEN,
    # with carriers under `getting-better/open-routes/` and
    # `bin/check-open-route-carriers.py` running them.


    # (#49) ROUTE #204 — AN `#@ interface assigns` IS NOT CHECKED AGAINST THE DEFINITION'S.
    # `module6_whyml/functions.py::_emit_narrowing_vc` proves the interface is a sound
    # WEAKENING of the definition for `ensures` (def_req -> def_ens -> iface_ens) and for
    # `requires` (iface_req -> def_req). It emits NOTHING for `assigns`, while Module 5
    # carries `interface.assigns` into the IR and importers frame the call with it.
    # MEASURED:
    #     # owner
    #     #@ assigns a[0]
    #     #@ ensures a[0] == 5
    #     #@ interface assigns \nothing
    #     def bump(a: List[int]) -> None:  a[0] = 5
    #     # importer
    #     #@ requires \length(a) >= 1
    #     #@ ensures \result == 0
    #     def caller(a: List[int]) -> int:
    #         x = a[0]; bump(a); return x - a[0]
    # The importer PROVED `\result == 0` (witness 1707) while CPython answers -4 for
    # `a = [1]`, an argument the precondition admits. The context is NOT inconsistent — the
    # absurd twin `\result == 999` is refused and the non-vacuity gate stays silent —
    # because the narrow frame plus the inherited `ensures a[0] == 5` merely force the
    # caller into "the element was already 5", which is satisfiable and false of the call.
    # THE RULE: an interface frame may claim MORE writes than the definition, never FEWER.
    # Checked AFTER `_ir_resolve`, not before it: the exploit needs TWO files, and the
    # importer is the one that proves the false thing. A check placed at the pre-resolution
    # seam sees only the importer's own functions and lets `--deep` walk straight past the
    # owner's narrowed frame — measured, the importer still PROVED with the check in the
    # earlier position. This is beside route #200's refusal, where the mirror twin is
    # `\trusted` — so it costs no marker, no emission move and no new definition.
    from errors import PyCSLSemanticError as _PyCSLSemErr204
    # (#49) gen #31 — `Callable[[Rekt], int]` FOR A CLASS THAT DOES NOT EXIST WAS SILENTLY
    # `int`. `_callable_tag_to_whyml` resolves a bare name against Module 6's
    # `_record_types`/`_variant_types` and falls back to `int` for anything else, with the
    # honest note that "Why3 then rejects the application if the arg type disagrees, which
    # is sound". Sound, yes — and it is the BACKEND covering for a missing front-end rule,
    # the same accident that keeps the legacy-`Generic[T]` finding from being a route. A
    # typo in a type the user wrote should not be answered by a type error about something
    # else, and the COLLECTION half of this same sentence is already a loud refusal
    # (`PYCSL-TY3-CALLABLE-SCOPE`), which is what made the class half look enforced.
    #
    # WHY HERE AND NOT AT THE FALLBACK. `_callable_tag_to_whyml`'s mirror twin is
    # UN-TRUSTED — a verbatim body that must itself PROVE — so a `raise` added there costs
    # a whole-file re-proof of `module6_whyml/functions.py` and has to stay inside the
    # modelled fragment; that is the seam that broke `_check_lemma` twice. The tables it
    # consults are BUILT from `ir_data["type_decls"]`, which `_run_pipeline` already holds,
    # so the admissible set is available here at no cost and `_run_pipeline`'s twin is
    # `\trusted` (the choke-point rule, routes #206-#215, #222, #223).
    #
    # CENSUS BEFORE LANDING (lesson d3): 17 files in both corpora, `src/pycsl`,
    # `src/self-annotate/src`, `src/pycsl_lib` and `tests/` contain a `Callable[`
    # annotation; exactly TWO name something that is neither a builtin tag nor a class or
    # `#@ datatype` declared in the same file — `List` and `bytes` — and both are the
    # already-repaired COLLECTION half. The unknown-CLASS population is EMPTY, so this is
    # byte-inert by construction.
    # THE ADMISSIBLE SET IS WIDER THAN "the four tags plus the records", and both of the
    # additions were found by CONSTRUCTING THE STRONGEST PROGRAM THE RULE WOULD FORBID
    # rather than by counting what exists (lesson (u4), learned an hour earlier on the
    # `#@ datatype` exhaustiveness item, which was RETIRED for exactly this reason):
    #   * an IMPORTED class — `Callable[[Box], int]` with `Box` from another unit VERIFIES,
    #     and it is admissible here because import resolution puts `Box` into `type_decls`
    #     before this point (checked: the emission carries `type box = { mutable n: int }`).
    #   * a TYPEVAR — `Callable[[T], int]` with `T = TypeVar("T")` VERIFIES today, and a
    #     refusal keyed on `type_decls` alone would have forbidden it. `typevar_registry`
    #     and the PEP 695 `type_params` are added so it stays writable.
    _cal_ok = {"int", "bool", "str", "float"}
    for _td_cal in (ir_data.get("type_decls", []) or []):
        if _td_cal.get("name"):
            _cal_ok.add(_td_cal["name"])
        for _tp_cal in (_td_cal.get("type_params") or []):
            _cal_ok.add(str(_tp_cal))
    for _tv_cal in (ir_data.get("typevar_registry") or {}):
        _cal_ok.add(str(_tv_cal))
    for _f_tp in (ir_data.get("functions", []) or []):
        for _tp_cal in (_f_tp.get("type_params") or []):
            _cal_ok.add(str(_tp_cal))
    for _f_cal in (ir_data.get("functions", []) or []):
        _st_cal = _f_cal.get("symbol_table") or {}
        if not isinstance(_st_cal, dict):
            continue
        for _v_cal, _t_cal in sorted(_st_cal.items()):
            if not (isinstance(_t_cal, str) and _t_cal.startswith("callable:")):
                continue
            _body_cal = _t_cal[len("callable:"):]
            _args_cal, _, _ret_cal = _body_cal.partition("->")
            for _tag_cal in [_x for _x in _args_cal.split(",") if _x] + [_ret_cal]:
                if _tag_cal in _cal_ok:
                    continue
                from errors import PyCSLSemanticError as _PyCSLSemErrCal
                raise _PyCSLSemErrCal(
                    "the `Callable` annotation on '%s' (in '%s') names '%s', which is "
                    "neither a primitive tag (`int`, `bool`, `str`, `float`) nor a class "
                    "or `#@ datatype` declared in this module. It was silently lowered to "
                    "`int`, so `Callable[[%s], ...]` became `int -> ...` and the only thing "
                    "that caught a mistake was Why3 rejecting the APPLICATION — a type "
                    "error about the argument, naming nothing you wrote. FIX: declare "
                    "'%s', or use one of the primitive tags."
                    % (_v_cal, _f_cal.get("name", "?"), _tag_cal, _tag_cal, _tag_cal),
                    filename=args.file,
                    stage="ir-semantic", code="PYCSL-TY3-CALLABLE-SCOPE")

    # (#49) gen #31 — `#@ uses <name>` NAMING A LEMMA THAT IS NOT IN THE EMISSION.
    #
    # The directive is ordering-only and "emits no WhyML" (annotations.md row 17), so a
    # name that resolves to nothing was DROPPED IN SILENCE: `#@ uses no_such_lemma` and
    # `[+] Verification SUCCESS! All contracts formally proven.` Not unsound — but the
    # proof that was supposed to rest on the lemma then fails for a reason the user cannot
    # connect to anything they wrote, and the compiler knew the admissible set exactly.
    #
    # THIRD MEMBER OF ONE FAMILY found the same day, and the family is the finding: a NAME
    # THE USER WROTE THAT RESOLVES TO NOTHING AND IS DROPPED IN SILENCE. The other two are
    # `Callable[[Rekt], int]` (an unknown class silently becomes `int`) and
    # `#@ verify_module leafmod` (a lowercase group name, repaired this gen).
    #
    # THE (u4) COUNTER-PROGRAM SHARPENED THIS RULE INSTEAD OF REFUTING IT, which is why it
    # lands while the `#@ datatype` exhaustiveness rule did not. The program to beat was
    # `#@ uses <lemma>` citing an IMPORTED lemma — and it VERIFIES, but the emitted `.mlw`
    # contains NO TRACE of the cited lemma: it is not emitted, its fact is not in scope,
    # and the citation is a no-op that reports success. So refusing it is telling the
    # truth. The gap that exposes — EMIT AN IMPORTED CITED LEMMA — is recorded as its own
    # capability in `open-routes/finding-uses-names-an-unknown-lemma-silently.md`.
    #
    # CENSUS (lesson d3): THREE `#@ uses` sites in the whole tree — `0582` twice, `0565`
    # once — every one citing a `#@ lemma` in its own file. Zero cross-module. Byte-inert.
    _lem_names = set()
    for _f_us in (ir_data.get("functions", []) or []):
        if _f_us.get("lemma") and _f_us.get("name"):
            _lem_names.add(str(_f_us["name"]))
            _lem_names.add(str(_f_us["name"]).split(".")[-1])
    for _f_us in (ir_data.get("functions", []) or []):
        for _u_us in (_f_us.get("uses") or []):
            if str(_u_us) in _lem_names:
                continue
            from errors import PyCSLSemanticError as _PyCSLSemErrUs
            raise _PyCSLSemErrUs(
                "`#@ uses %s` on '%s' names no `#@ lemma` in this emission, and the "
                "citation was silently dropped — the file still reported success while "
                "the fact it was meant to bring into scope was never there. FIX: check "
                "the spelling, or define `%s` as a `#@ lemma` in this module. NOTE that "
                "a lemma in an IMPORTED module does not count: an imported cited lemma is "
                "not emitted at all today, so citing one is the same no-op."
                % (_u_us, _f_us.get("name", "?"), _u_us),
                filename=args.file,
                stage="ir-semantic", code="PYCSL-SEM-USES-UNKNOWN-LEMMA")

    # (#49) gen #31 — `#@ reveal <name>` NAMING NO FUNCTION. Same family as
    # `#@ uses` above, and this one is THIS GENERATION'S OWN FEATURE, implemented eight
    # hours before the audit that found it (wall-lesson (v4): run the new audit against
    # your own newest increment first). The repair collects the module's reveal names into
    # a set and asks whether the function being stubbed is in it; a name matching nothing
    # simply never matches, and nothing looked.
    #
    #     #@ reveal no_such_function
    #     #@ requires x > 0
    #     #@ ensures \result == x
    #     def caller(x: int) -> int: return x
    #     [+] Verification SUCCESS! All contracts formally proven.
    #
    # The admissible set is every function the IR carries — local or import-injected —
    # matched on the plain name and on the tail after the last `__`, because a method
    # arrives as `<class>__<method>`. `#@ reveal` on a name that is not a function has no
    # reading under which it does anything.
    _rv_known = set()
    for _f_rv in (ir_data.get("functions", []) or []):
        _n_rv = _f_rv.get("name")
        if not _n_rv:
            continue
        _rv_known.add(str(_n_rv))
        _rv_known.add(str(_n_rv).split("__")[-1])
        _rv_known.add(str(_n_rv).split(".")[-1])
    for _f_rv in (ir_data.get("functions", []) or []):
        for _r_rv in (_f_rv.get("reveal") or []):
            if str(_r_rv) in _rv_known:
                continue
            from errors import PyCSLSemanticError as _PyCSLSemErrRv
            raise _PyCSLSemErrRv(
                "`#@ reveal %s` on '%s' names no function in this emission, and the "
                "directive was silently dropped — the file still reported success while "
                "the definition-fact it was meant to bring across the import boundary was "
                "never cited. FIX: check the spelling, or import the function you meant. "
                "(A `#@ reveal` inside the unit that OWNS the function is a documented "
                "no-op, but the NAME still has to resolve.)"
                % (_r_rv, _f_rv.get("name", "?")),
                filename=args.file,
                stage="ir-semantic", code="PYCSL-SEM-REVEAL-UNKNOWN-NAME")

    # (#49) gen #31 — THE SAME FAMILY ON A FIELD THAT IS A KEYWORD, NOT A NAME. Found by
    # re-running the sweep with the phrase corrected: "every directive with a FIELD WHOSE
    # VALUE COMES FROM A FIXED SET", not "whose grammar admits an identifier". The first
    # phrase missed both of these, and a search is only as complete as the phrase that
    # generated it.
    #
    #   * `#@ ghost g : no_such_type = 0` VERIFIED, silently becoming the documented `int`
    #     default. annotations.md §11's "untyped ghost declarations default to `int`" is
    #     what made the silence look intentional: the DEFAULT is documented; the FALLBACK
    #     FROM A MISSPELLED KEYWORD to that default is not.
    #   * `#@ proof rocqq <qualname>` VERIFIED, and the emitted `.mlw` was BYTE-IDENTICAL
    #     to the one spelled `rocq` — the prover keyword is not dropped, it is NOT READ.
    #     Bounded: the axiom BODY comes from `_AXIOM_REGISTRY` and an unregistered qualname
    #     is refused outright, so no unaudited axiom can be smuggled in; what breaks
    #     silently is `pycsl --audit-proof`'s per-driver citation.
    #
    # BOTH AT THE CHOKE POINT, and the reason is lesson (n4) measured rather than assumed:
    # `Module2_Parser._parse_ghost` is where the ghost keyword is read, and its mirror twin
    # is UN-TRUSTED — a verbatim body that must itself PROVE, plus a whole-file re-proof of
    # a large parser. `_run_pipeline`'s twin is `\trusted` and the IR carries both fields
    # already (`{"stmt": "GhostAssign", …, "ghost_type": …}` and
    # `func["proof"] = [{"prover": …, "qualname": …}]`).
    # THE SET IS THE NINE THE EMITTER ACTUALLY DISPATCHES ON, not the twelve a stale
    # dataclass comment in the parser lists. `_resolve_effective_ghost_type`'s consumers
    # branch on exactly `string`, `array`, `ghost_dict`, `ghost_list`, `ghost_set`,
    # `tuple2`/`tuple3`/`tuple4`, with `int` as the default — which is also exactly the
    # nine rows of annotations.md §11.1. The parser's comment additionally names `list`,
    # `set` and `dict`; those reach no branch and would be silently `int`, so they are
    # REFUSED too. CENSUS: 53 `#@ ghost <n> : <t>` sites across both corpora and `src/`,
    # spelling only `ghost_dict` (11), `ghost_set` (10), `ghost_list` (9), `tuple2` (8),
    # `array` (7), `string` (5), `tuple3` (2), `tuple4` (1) — every one admissible, and
    # the bare `list`/`set`/`dict` spellings appear NOWHERE. Byte-inert.
    _GHOST_TYPES = ("int", "string", "array",
                    "ghost_list", "ghost_set", "ghost_dict",
                    "tuple2", "tuple3", "tuple4")
    _stk_gt = [_f_gt.get("body") for _f_gt in (ir_data.get("functions", []) or [])]
    while _stk_gt:
        _n_gt = _stk_gt.pop()
        if isinstance(_n_gt, list):
            _stk_gt.extend(_n_gt)
            continue
        if not isinstance(_n_gt, dict):
            continue
        for _v_gt in _n_gt.values():
            if isinstance(_v_gt, (list, dict)):
                _stk_gt.append(_v_gt)
        if _n_gt.get("stmt") != "GhostAssign":
            continue
        _gt = _n_gt.get("ghost_type")
        if _gt is None or str(_gt) in _GHOST_TYPES:
            continue
        from errors import PyCSLSemanticError as _PyCSLSemErrGt
        raise _PyCSLSemErrGt(
            "`#@ ghost %s : %s` names no ghost type. The declared type must be one of "
            "%s; an unrecognised keyword was silently treated as the `int` default, so a "
            "mistyped `ghost_dict` gave you an int ghost and no message. FIX: use one of "
            "those keywords, or drop the `: <type>` entirely (an untyped ghost is `int` "
            "BY DESIGN, which is the documented case this refusal does not touch)."
            % (_n_gt.get("target", "?"), _gt, ", ".join("`%s`" % _t for _t in _GHOST_TYPES)),
            filename=args.file,
            stage="ir-semantic", code="PYCSL-SEM-GHOST-UNKNOWN-TYPE")
    for _f_pv in (ir_data.get("functions", []) or []):
        for _p_pv in (_f_pv.get("proof") or []):
            if not isinstance(_p_pv, dict):
                continue
            _pv = _p_pv.get("prover")
            if _pv in ("rocq", "lean", None):
                continue
            from errors import PyCSLSemanticError as _PyCSLSemErrPv
            raise _PyCSLSemErrPv(
                "`#@ proof %s %s` names no prover. The prover must be `rocq` or `lean`; "
                "anything else was NOT READ AT ALL — the emitted WhyML is byte-identical "
                "either way, so the axiom arrived while `pycsl --audit-proof` looked for "
                "the citation under a prover that does not exist. FIX: spell it `rocq` or "
                "`lean`."
                % (_pv, _p_pv.get("qualname", "?")),
                filename=args.file,
                stage="ir-semantic", code="PYCSL-SEM-PROOF-UNKNOWN-PROVER")

    for _f204 in ir_data.get("functions", []):
        _if204 = _f204.get("interface") or {}
        if not _if204:
            continue
        _ia204 = _if204.get("assigns")
        if _ia204 is None:
            continue                      # absent interface frame inherits the definition
        _da204 = ((_f204.get("contracts") or {}).get("assigns")) or []
        _def_t = [_json.dumps(t, sort_keys=True) for t in _da204
                  if isinstance(t, dict) and t.get("type") != "Nothing"]
        if not _def_t:
            continue                      # definition assigns nothing: any interface is a
                                          # weakening of nothing, which is sound
        _if_t = [_json.dumps(t, sort_keys=True) for t in (_ia204 or [])
                 if isinstance(t, dict) and t.get("type") != "Nothing"]
        _missing = [t for t in _def_t if t not in _if_t]
        if _missing:
            raise _PyCSLSemErr204(
                f"{args.file} (function '{_f204.get('name')}'): the `#@ interface "
                f"assigns` frame is NARROWER than the definition's `#@ assigns` — it "
                f"omits {len(_missing)} target(s) the body may write. An importer frames "
                f"the call with the INTERFACE, so it would carry those locations across "
                f"the call UNCHANGED while the body changes them, and prove things "
                f"CPython contradicts. The interface frame may claim MORE writes than "
                f"the definition, never fewer: list every `#@ assigns` target in the "
                f"`#@ interface assigns` clause, or drop the interface frame entirely "
                f"(an absent one inherits the definition's).",
                filename=args.file, line=_f204.get("line", 0) or 0,
                stage="ir-semantic", code="PYCSL-SEM-IFACE-FRAME")

    # ROUTE #29 (relaunch #45) — REFUSE the four array spec atoms under a HEAP memory
    # model, because Module 6 ERASES them there and a FALSE CONTRACT PROVES.
    #
    #   `module6_whyml/expressions.py` lowers `\is_sorted`, `\array_eq` and
    #   `\permutation` as `if self._value_semantic: <real formula>` with the
    #   fall-through `return "true"`, and `\sum` with the fall-through `return "0"`.
    #   `_value_semantic` is `memory_model in ("hoare", "concurrent")`, so the WHOLE
    #   typed/store family took the fall-through and the postcondition emitted as
    #   `ensures { true }`. MEASURED: `#@ ensures \is_sorted(arr, 0, 3)` on a function
    #   that writes 3, 2, 1 — strictly DESCENDING — printed "Verification SUCCESS! All
    #   contracts formally proven." under BOTH --memory-model typed and store, and
    #   correctly FAILED under hoare. Same for `\array_eq` and `\permutation`.
    #   Witnesses 1004-1008.
    #
    #   `\length2d` and `\valid2d` are in the set on the SAME EVIDENCE minus the
    #   exploit: a mechanical census of every `self._value_semantic` gate in Module 6
    #   (scratchpad `vs_census.py`) shows `_handle_length2d_expr` and
    #   `_handle_valid2d_expr` with the identical `if value_semantic: <formula> ...
    #   return "true"` shape, masked TODAY only by `unbound type symbol 'matrix'` —
    #   the same accident that masks `\sum`. Refusing them makes them fail-closed BY
    #   DESIGN rather than by an unrelated bug a completeness fix could remove at any
    #   time. The census found NO other literal fall-through: the one remaining
    #   `return "true"` (`_handle_separated_expr`, under the VALUE model) is sound,
    #   because Why3's region typing rejects an aliased array application outright
    #   ("This application creates an illegal alias" — probed), so two array
    #   parameters really are always separated there.
    #
    #   WHY REFUSE RATHER THAN EMIT `false`. `false` is fail-closed in a POSTCONDITION
    #   and fail-OPEN in a PRECONDITION — `requires { false }` makes every goal of the
    #   function vacuously provable — so swapping the literal trades one unsoundness
    #   for another. Refusing is sound in every clause position.
    #
    #   WHY HERE RATHER THAN IN THE FOUR HANDLERS. The choke point rule: the four
    #   handlers are CONVERTED mirror methods, so a `raise` in their bodies would need
    #   a `#@ raises` on them and on `_expr_to_whyml`, re-proving a 20125-goal file to
    #   restate a refusal the pipeline can make once, before emission, on the resolved
    #   IR. This scans the wire IR for the four `type` tags and is a pure add on a
    #   `\trusted` mirror method — no mirror body moves, no re-proof is owed, and no
    #   new def is introduced (which would move the mirror-coverage ratchet).
    #
    #   THE CAPABILITY THIS DEFERS, recorded rather than silently dropped: a faithful
    #   heap lowering of these atoms is expressible — `\is_sorted(a, lo, hi)` is
    #   `forall i. lo <= i < hi-1 -> Map.get !int_mem (a+i) <= Map.get !int_mem (a+i+1)`
    #   and `\array_eq` is the same shape over two bases plus the `_len` companions.
    #   `\permutation` needs an uninterpreted predicate over (loc, len) pairs and
    #   `\sum` a heap-indexed recursive function. Until those exist, this refuses.
    if memory_model in ("typed", "store"):
        _r29_tags = ("IsSorted", "ArrayEq", "Permutation", "Sum",
                     "Length2D", "Valid2D")
        _r29_names = {"IsSorted": "\\is_sorted", "ArrayEq": "\\array_eq",
                      "Permutation": "\\permutation", "Sum": "\\sum",
                      "Length2D": "\\length2d", "Valid2D": "\\valid2d"}
        _r29_hit = None
        _r29_stack = [ir_data]
        while _r29_stack:
            _r29_n = _r29_stack.pop()
            if isinstance(_r29_n, dict):
                if _r29_n.get("type") in _r29_tags:
                    _r29_hit = _r29_n.get("type")
                    break
                _r29_stack.extend(_r29_n.values())
            elif isinstance(_r29_n, (list, tuple)):
                _r29_stack.extend(_r29_n)
        if _r29_hit is not None:
            from errors import PyCSLSemanticError as _PyCSLSemErr29
            raise _PyCSLSemErr29(
                f"the array spec atom `{_r29_names[_r29_hit]}` is not interpreted "
                f"under the {memory_model!r} memory model (ROUTE #29): its Module 6 "
                f"lowering is gated on the value-semantic models and would ERASE to a "
                f"literal here, making a contract that is FALSE of the program "
                f"provable. Use the default `--memory-model hoare` (or `concurrent`), "
                f"where the atom lowers to its real quantified formula.",
                stage="whyml-emit", code="PYCSL-R29-HEAP-SPEC-ERASURE")

    # (#49) ROUTE #200 — REFUSE A STRING LITERAL ACTUAL AGAINST A PARAMETER THE CALLEE
    # DECLARES `int` / `bool` / `float`.
    #
    #   `module6_whyml/expressions.py::_coerce_dotted_args` coerces each actual to its
    #   declared param type, and for a scalar param that runs `_coerce_to_int`, whose
    #   string arm answers `stable_hash(<literal>)`. `bin/check-argument-coercion.py`
    #   left that substitution standing with a caveat about it: "a caller cannot predict
    #   the hash it would have to name in a contract to exploit it -- but that is a claim
    #   about difficulty, not about soundness, so re-probe it if anything ever makes the
    #   hash predictable." NOTHING HAD TO. `stable_hash` is deterministic and its source
    #   ships in this repository. MEASURED:
    #
    #       #@ ensures p == 747471683 ==> \result == 1
    #       #@ ensures p != 747471683 ==> \result == 2
    #       def callee(p: int) -> int:
    #           if p == 747471683: return 1
    #           return 2
    #       #@ ensures \result == 1
    #       def probe() -> int: return callee("a")
    #
    #   emitted `(callee 747471683)` and PROVED `\result == 1`, while CPython answers 2
    #   and the TRUE twin `\result == 2` was REFUSED (witnesses 1697/1698).
    #
    #   KEYED ON THE DECLARED ANNOTATION, WHICH IS WHAT MAKES IT FREE. The 46 sites where
    #   a string literal reaches an `int` param across the 53 mirror emissions are `int`
    #   BY ERASURE — the callee's parameter carries no annotation at all. The witness's
    #   parameter is `int` BY DECLARATION and the actual is a `str`: a type error Python
    #   does not enforce and the model BELIEVES, which is route #51's situation one
    #   argument position to the left, and route #51's answer is a refusal. Dry-run of
    #   this exact predicate before it was written: 1622 pycsl-reference + 53
    #   self-annotate + 2217 python-reference + 104 pycsl_lib files, ZERO hits.
    #
    #   WHY HERE, and it is route #29's rule three paragraphs up applied again: this is a
    #   pure add inside a `\trusted` mirror method, with an ITERATIVE walk and NO nested
    #   def. The first attempt put it in `core_ir_semantic.run_ir_semantic_checks` with a
    #   nested `_walk_str_arg`, and TWO planes caught that: `check-mirror-coverage` (550 >
    #   549 — a nested def is an ABSENT function, the Battery H lesson) and
    #   `check-trusted-raises-honesty` (63 > 62 — a `\trusted` stub whose live body newly
    #   RAISES with no `#@ raises`). `_run_pipeline` is already on both lists, so moving
    #   the refusal here moves neither ratchet.
    # (#49) ROUTE #202 — THE RESIDUE #200 LEFT, CLOSED ON THE AXIS THAT ACTUALLY MATTERS.
    #   #200 keys on the DECLARED annotation, because the 46 sites where a string literal
    #   reaches an `int` param across the 53 mirror emissions are `int` BY ERASURE (no
    #   annotation at all). That reasoning is what made #200 free, and it is also what it
    #   missed: a parameter with NO annotation is erased to `int` and gets the SAME hash.
    #   MEASURED: `def callee(p) -> int` carrying `ensures p == 747471683 ==> \result == 1`
    #   — true of its own body — called as `callee("a")` emitted `(callee 747471683)` and
    #   PROVED `\result == 1` while CPython answers 2, with the TRUE twin REFUSED.
    #
    #   THE HASH IS ONLY DANGEROUS WHEN A CONTRACT CAN READ THE PARAMETER. So the
    #   un-annotated case is gated on exactly that: the callee's own `requires`/`ensures`
    #   must MENTION the parameter. The 46 mirror sites are `\trusted` stubs whose contracts
    #   do not mention theirs, so they stay untouched — measured by a dry run of this exact
    #   predicate before it was written, not asserted afterwards.
    #
    #   The DECLARED-scalar rule below is NOT narrowed by this: it still fires whether or
    #   not the contract mentions the param, so this change is strictly MORE refusals than
    #   the tree had a minute ago, never fewer.
    _r200_sigs = {}
    for _r200_f in (ir_data.get("functions", []) or []):
        _r200_nm = _r200_f.get("name")
        if not _r200_nm:
            continue
        # the parameter names this function's OWN contract reads
        _r202_seen = set()
        _r202_stack = [(_r200_f.get("contracts") or {}).get(_k)
                       for _k in ("requires", "ensures", "assigns", "raises")]
        while _r202_stack:
            _r202_n = _r202_stack.pop()
            if isinstance(_r202_n, dict):
                if _r202_n.get("type") == "Var" and _r202_n.get("name"):
                    _r202_seen.add(_r202_n["name"])
                _r202_stack.extend(_r202_n.values())
            elif isinstance(_r202_n, (list, tuple)):
                _r202_stack.extend(_r202_n)
        _r200_e = (_r200_f.get("formal_params") or [],
                   _r200_f.get("param_annotations") or {},
                   _r202_seen, _r200_f.get("vararg_str_param"))
        _r200_sigs[_r200_nm] = _r200_e
        _r200_sigs.setdefault(_r200_nm.rsplit(".", 1)[-1], _r200_e)
    for _r200_f in (ir_data.get("functions", []) or []):
        _r200_caller = _r200_f.get("name", "<anonymous>")
        _r200_stack = [_r200_f.get("body", []) or []]
        while _r200_stack:
            _r200_n = _r200_stack.pop()
            if isinstance(_r200_n, dict):
                if (_r200_n.get("type") == "Call"
                        and isinstance(_r200_n.get("func"), str)):
                    _r200_fn = _r200_n["func"]
                    _r200_sig = (_r200_sigs.get(_r200_fn)
                                 or _r200_sigs.get(_r200_fn.rsplit(".", 1)[-1]))
                    if _r200_sig:
                        (_r200_formals, _r200_anns, _r202_reads,
                         _r202_vararg) = _r200_sig
                        _r200_off = (1 if (_r200_formals
                                           and _r200_formals[0] == "self") else 0)
                        # POSITIONAL actuals, plus the KEYWORD slot the IR keeps
                        # SEPARATELY (`{"args": [], "keywords": [{"arg": ..., "value":
                        # ...}]}`). Route #200's first version read `args` only, so
                        # `callee(p="a")` walked straight past it and still PROVED — the
                        # generation's own lesson (i) ("name which SPELLINGS were run"),
                        # missed on my own repair an hour after banking it.
                        _r202_pairs = []
                        for _r200_i, _r200_a in enumerate(_r200_n.get("args") or []):
                            _r200_j = _r200_i + _r200_off
                            if _r200_j >= len(_r200_formals):
                                break
                            # A VARARG formal PACKS every remaining actual into one
                            # sequence; those actuals are not a parameter mismatch at all.
                            # Measured: without this, `member_of("+", "+", "-")` in corpus
                            # 0931 (a `*vals: str` vararg) would be REFUSED, and that file
                            # verifies today.
                            if (_r202_vararg is not None
                                    and _r200_formals[_r200_j] == _r202_vararg):
                                break
                            _r202_pairs.append((_r200_formals[_r200_j], _r200_a))
                        for _r202_kw in (_r200_n.get("keywords") or []):
                            if not isinstance(_r202_kw, dict):
                                continue
                            _r202_kwname = _r202_kw.get("arg")
                            if (_r202_kwname and _r202_kwname != _r202_vararg
                                    and _r202_kwname in _r200_formals):
                                _r202_pairs.append((_r202_kwname, _r202_kw.get("value")))
                        for _r200_pname, _r200_a in _r202_pairs:
                            if not (isinstance(_r200_a, dict)
                                    and _r200_a.get("type") == "String"):
                                continue
                            _r200_ann = _r200_anns.get(_r200_pname)
                            _r202_hit = (_r200_ann in ("int", "bool", "float")
                                         or (_r200_ann is None
                                             and _r200_pname in _r202_reads))
                            if _r202_hit:
                                from errors import PyCSLSemanticError as _PyCSLSemErr200
                                raise _PyCSLSemErr200(
                                    f"in '{_r200_caller}': the call to '{_r200_fn}' "
                                    f"passes a string literal to parameter "
                                    f"'{_r200_pname}', which '{_r200_fn}' "
                                    f"declares `{_r200_ann or 'no type at all, so the model '
                                                 'erases it to int'}` "
                                    f"(ROUTE #200/#202). Python does "
                                    f"not enforce the hint and the model BELIEVES it: "
                                    f"the string is replaced by a STABLE HASH of its "
                                    f"own text, so a contract of '{_r200_fn}' that "
                                    f"names that integer is DECIDED — and the hash is "
                                    f"computable from this repository. Pass a value of "
                                    f"the declared type, or annotate the parameter "
                                    f"`str`.",
                                    stage="ir-semantic", code="PYCSL-SEM-STRARG")
                _r200_stack.extend(_r200_n.values())
            elif isinstance(_r200_n, (list, tuple)):
                _r200_stack.extend(_r200_n)

    # 07-1143 R4: the Soundness Ledger is a provenance view of the fully-resolved IR
    # (after imports/inheritance/composition), so it runs here and short-circuits before
    # WhyML emission / proving.
    if getattr(args, "soundness_report", False):
        _print_soundness_report(_build_soundness_report(ir_data, args.file))
        sys.exit(0)

    json_ir = _json.dumps(ir_data)

    # Non-vacuity gate exempt-set — stashed on `args` (the object shared with
    # `_run_proofs`, where the gate runs but `ir_data` is out of scope). A declared
    # `-> NoReturn` (is_noreturn) or an explicit `#@ \diverges` function is SOUNDLY
    # vacuous-looking on its unreachable normal exit (a diverging function satisfies
    # any postcondition), so the gate must NOT flag it. Keyed on the annotation flags,
    # never the inferred postcondition (which would exempt every genuine vacuity).
    try:
        from module6_whyml.identifiers import whyml_ident as _wid_vac
        args._vacuity_exempt = {
            _wid_vac(f.get("name", "")) for f in ir_data.get("functions", [])
            if f.get("is_noreturn") or f.get("diverges")}
    except Exception:
        args._vacuity_exempt = set()

    # --fun filter: mark non-selected functions as trusted
    if args.fun:
        ir_data = _json.loads(json_ir)
        all_func_names = {f["name"] for f in ir_data["functions"]}
        fun_names = set(args.fun)
        missing = fun_names - all_func_names
        if missing:
            print(f"[!] Error: Function(s) not found: {', '.join(sorted(missing))}")
            print(f"    Available: {', '.join(sorted(all_func_names))}")
            sys.exit(1)
        call_graph = {f["name"]: _collect_calls(f["body"]) & all_func_names
                      for f in ir_data["functions"]}
        reachable = set(fun_names)
        worklist = list(fun_names)
        while worklist:
            fname = worklist.pop()
            for callee in call_graph.get(fname, set()):
                if callee not in reachable:
                    reachable.add(callee)
                    worklist.append(callee)
        for f in ir_data["functions"]:
            if f["name"] not in reachable:
                f["trusted"] = True
        json_ir = _json.dumps(ir_data)
        verified_names = sorted(reachable & all_func_names)
        trusted_names = sorted(all_func_names - reachable)
        if trusted_names:
            print(f"[*] --fun filter: verifying {verified_names}, trusting {trusted_names}")

    # Phase C boundary (refactor.md): the core consumes the SERIALIZED, fully-resolved IR.
    # Re-validate it HERE — after the inheritance/composition/inline/--fun mutations — at the
    # real Module-5→core seam, not only the pre-mutation IR validated near the top of the
    # pipeline. This closes the gap where the IR Module 6 actually consumes was never
    # structurally checked: a malformed post-mutation IR previously failed mysteriously
    # inside Module 6 instead of with a located ir-validate error at the boundary.
    validate_ir(_json.loads(json_ir), stage="ir-validate-boundary")

    # (#49) ROUTE #263 — RECURSION THROUGH A METHOD CALL WAS NEVER CHECKED FOR TERMINATION.
    # Module 6 lowers a `self.m(...)` / `obj.m(...)` / `C().m(...)` call to a bodyless
    # abstract `val` carrying the callee's propagated `ensures`, so Why3 sees no edge from
    # the caller to the callee's BODY: a top-level `def f(): return f()` is a `let rec`
    # whose missing variant fails, but the same body as a METHOD is a plain `let` that
    # claims termination for free and assumes its own postcondition circularly.
    # MEASURED at 283d1033 (witnesses `getting-better/open-routes/witnesses-r263/`, corpus
    # 2770-2779): `def m(self, k): return self.m(k)` PROVED `\result == 0`; the mutual
    # pair a<->b PROVED `\result == 5`; `g -> c.m -> g` PROVED; under `#@ no_exception
    # \all` it PROVED; and `#@ happy availability: targets parse total` PROVED for a
    # `parse` that is its own only callee (route #206 closes only cycles through bodyless
    # stubs). CPython: RecursionError in every one.
    # THE RULE: build the module's call graph INCLUDING method calls — a receiver is
    # resolved by class (`self` -> the enclosing class's hierarchy, `super()` -> what
    # follows the class in an MRO, a typed or constructor-bound local/parameter -> its
    # class's hierarchy, a typed field -> its type, an imported module or a builtin -> no
    # method of this module, anything else -> EVERY method of that name: over-approximation
    # is the sound direction) plus constructor edges (`C(...)` -> the calls in
    # `C.__init__`, which Module 5 drops) — and refuse every strongly connected component
    # holding an edge Why3 does not see. Which method calls Why3 DOES see is decided on the
    # EMITTED WhyML just before `return _mlw` below (a concrete `(<callee> …)` application
    # inside the same `let rec … with …` group, e.g. corpus 0966), because Module 6 owns
    # that decision and re-deriving it here would be a second producer of it.
    # The one admissible form is the honest one: every function of the cycle marked
    # `#@ \diverges` (partial correctness; assuming a recursive callee's postcondition is
    # then the standard, sound recursion rule). `\trusted`/`\abstract` functions have no
    # body, so they contribute no edges. INLINE (no nested defs: check-mirror-coverage);
    # CHOKE POINT: `_run_pipeline`'s mirror twin is `\trusted` (routes #206-#215).
    _ir263 = _json.loads(json_ir)
    _fn263 = [f for f in (_ir263.get("functions") or []) if isinstance(f, dict)
              and isinstance(f.get("name"), str)]
    _names263 = {f["name"] for f in _fn263}
    _byname263 = {f["name"]: f for f in _fn263}
    _bases263 = {}
    _fields263 = {}
    for _td263 in (_ir263.get("type_decls") or []):
        if isinstance(_td263, dict) and isinstance(_td263.get("name"), str):
            _bases263[_td263["name"]] = [b for b in (_td263.get("bases") or [])
                                         if isinstance(b, str)]
            _fields263[_td263["name"]] = {
                _fd.get("name"): _fd.get("type") for _fd in (_td263.get("fields") or [])
                if isinstance(_fd, dict)}
    _anc263 = {}
    for _c263 in _bases263:
        _sn263 = set()
        _td263 = [_c263]
        while _td263:
            _x263 = _td263.pop()
            if _x263 in _sn263:
                continue
            _sn263.add(_x263)
            _td263.extend(_bases263.get(_x263, ()))
        _anc263[_c263] = _sn263
    # A receiver statically of class C may run C's method, an ancestor's (inherited) or a
    # descendant's (override): `_rel263[C]`.
    _desc263 = {_c263: {_d for _d in _bases263 if _c263 in _anc263[_d]} for _c263 in _bases263}
    _rel263 = {_c263: _anc263[_c263] | _desc263[_c263] for _c263 in _bases263}
    _meths263 = {}
    for _f263 in _fn263:
        _st263 = _f263.get("self_type")
        if _f263.get("kind") == "method" and isinstance(_st263, str) and _st263:
            _pre263 = _st263.lower() + "__"
            if _f263["name"].startswith(_pre263):
                _meths263.setdefault(_f263["name"][len(_pre263):], []).append(
                    (_st263, _f263["name"]))
    _modnames263 = set()
    for _im263 in (_ir263.get("imports") or []):
        if isinstance(_im263, list) and _im263 and isinstance(_im263[0], str):
            _modnames263.add(_im263[0].split(".")[0])
    import builtins as _bi263
    _builtins263 = set(dir(_bi263)) - set(_bases263)
    # Classes a value of declared type T may be an instance of; `None` = unknown (any).
    _tstr263 = set()
    for _f263 in _fn263:
        _tstr263 |= {v for v in (_f263.get("symbol_table") or {}).values() if isinstance(v, str)}
        _tstr263 |= {v for v in (_f263.get("param_annotations") or {}).values()
                     if isinstance(v, str)}
    for _fm263 in _fields263.values():
        _tstr263 |= {v for v in _fm263.values() if isinstance(v, str)}
    _tcls263 = {}
    for _t263 in _tstr263:
        if not _t263 or _t263 in ("Any", "object"):
            _tcls263[_t263] = None
        elif _t263 in _bases263:
            _tcls263[_t263] = {_t263}
        else:
            # a builtin/collection type names no class (no method of this module); a
            # container or Optional of a class may hold that class.
            _tcls263[_t263] = {c for c in _bases263 if _re.search(
                r"(?<![\w])" + _re.escape(c) + r"(?![\w])", _t263)}
    _graph263 = {}
    _unchk263 = set()
    for _f263 in _fn263:
        _src263 = _f263["name"]
        _graph263.setdefault(_src263, set())
        # (#49) ROUTE #269 (R5) — an IMPORTED function is a trusted stub HERE, but its body
        # (kept by `ir_resolve._process_dependency`) is evidence of a CROSS-MODULE cycle:
        # `a.g -> b.f -> a.g` PROVED in BOTH units at 8b0bfbbd (each assumes the other's
        # stub; CPython: RecursionError). Its calls back INTO this unit become edges.
        _imp269 = (_src263 in (imported_names or set())
                   and not _f263.get("abstract") and not _f263.get("lemma"))
        if (_f263.get("trusted") or _f263.get("abstract") or _f263.get("lemma")) and not _imp269:
            continue
        _calls263 = []
        _ctorloc263 = {}
        _otherloc263 = set()
        _stk263 = [_f263.get("body")]
        while _stk263:
            _n263 = _stk263.pop()
            if isinstance(_n263, dict):
                if _n263.get("type") == "Call" and isinstance(_n263.get("func"), str):
                    _calls263.append(_n263)
                if _n263.get("stmt") in ("Assign", "AnnAssign") and isinstance(
                        _n263.get("target"), str):
                    # A local bound ONLY to constructor calls is of those classes (the
                    # symbol table records `c = C()` as `Any`).
                    _v263 = _n263.get("value")
                    if (isinstance(_v263, dict) and _v263.get("type") == "Call"
                            and _v263.get("func") in _bases263 and "receiver" not in _v263):
                        _ctorloc263.setdefault(_n263["target"], set()).add(_v263["func"])
                    else:
                        _otherloc263.add(_n263["target"])
                _stk263.extend(_n263.values())
            elif isinstance(_n263, list):
                _stk263.extend(_n263)
        _symt263 = dict(_f263.get("symbol_table") or {})
        _symt263.update(_f263.get("param_annotations") or {})
        _selft263 = _f263.get("self_type") if _f263.get("kind") == "method" else None
        for _c263 in _calls263:
            _fs263 = _c263["func"]
            _m263 = _fs263.split(".")[-1]
            _exact263 = False
            if _imp269:
                # Only an edge BACK into a module-level function of THIS unit (by its
                # last name segment, whatever the qualifier — the over-approximation);
                # the dependency's own recursion was checked when it was verified.
                if ("receiver" not in _c263 and _m263 in _names263
                        and _m263 not in (imported_names or set())
                        and _byname263[_m263].get("kind") != "method"):
                    _graph263[_src263].add(_m263)
                    _unchk263.add((_src263, _m263))
                continue
            if "receiver" in _c263:
                _rv263 = _c263.get("receiver")
                if (isinstance(_rv263, dict) and _rv263.get("type") == "Call"
                        and _rv263.get("func") == "super" and _selft263):
                    # `super().m()` in class A runs the first `m` AFTER A in the MRO of
                    # `type(self)`: an ancestor of a subclass of A, never A or a subclass.
                    _dn263 = _desc263.get(_selft263, {_selft263})
                    _cls263 = set()
                    for _d263 in _dn263:
                        _cls263 |= _anc263.get(_d263, {_d263})
                    _cls263 -= _dn263
                    _exact263 = True
                elif (isinstance(_rv263, dict) and _rv263.get("type") == "Call"
                        and _rv263.get("func") in _bases263 and "receiver" not in _rv263):
                    _cls263 = {_rv263["func"]}
                elif (isinstance(_rv263, dict) and _rv263.get("type") == "Var"
                        and isinstance(_rv263.get("name"), str)
                        and isinstance(_symt263.get(_rv263["name"]), str)):
                    _cls263 = _tcls263.get(_symt263[_rv263["name"]])
                else:
                    _cls263 = None
            elif "." not in _fs263:
                if _fs263 in _names263:
                    # A direct call: Module 6 puts both ends in one `let rec` group.
                    _graph263[_src263].add(_fs263)
                    if _fs263 in (imported_names or set()):
                        # (#269 R5) ... unless the callee is an IMPORTED stub.
                        _unchk263.add((_src263, _fs263))
                elif _fs263 in _bases263:
                    _graph263[_src263].add("__init__@" + _fs263)
                    _unchk263.add((_src263, "__init__@" + _fs263))
                continue
            else:
                _pt263 = _fs263.split(".")
                _b263 = _pt263[0]
                if _b263 == "self" and _selft263:
                    _cls263 = {_selft263}
                elif (_b263 in _ctorloc263 and _b263 not in _otherloc263
                      and _tcls263.get(_symt263.get(_b263)) is None):
                    _cls263 = set(_ctorloc263[_b263])
                elif _b263 in _symt263:
                    _cls263 = (_tcls263.get(_symt263[_b263])
                               if isinstance(_symt263[_b263], str) else None)
                elif _b263 in _bases263:
                    _cls263 = {_b263}
                elif _b263 in _modnames263 or _b263 in _builtins263:
                    # an imported module or a builtin (`type.__instancecheck__`,
                    # `str.join`): no method of THIS unit. (#269 R5) `mod.f(...)` naming
                    # an IMPORTED function is an edge to its stub.
                    _cls263 = set()
                    if (len(_pt263) == 2 and _b263 in _modnames263
                            and _pt263[1] in (imported_names or set())
                            and _pt263[1] in _names263):
                        _graph263[_src263].add(_pt263[1])
                        _unchk263.add((_src263, _pt263[1]))
                else:
                    _cls263 = None
                for _fld263 in _pt263[1:-1]:
                    if _cls263 is None or not _cls263:
                        break
                    _nx263 = set()
                    for _k263 in _cls263:
                        _ft263 = None
                        _hit263 = False
                        for _a263 in sorted(_anc263.get(_k263, {_k263})):
                            if _fld263 in _fields263.get(_a263, {}):
                                _ft263 = _tcls263.get(_fields263[_a263][_fld263])
                                _hit263 = True
                                break
                        if not _hit263 or _ft263 is None:
                            _nx263 = None
                            break
                        _nx263 |= _ft263
                    _cls263 = _nx263
            _wide263 = None
            if _cls263 is not None and not _exact263:
                _wide263 = set()
                for _k263 in _cls263:
                    _wide263 |= _rel263.get(_k263, {_k263})
            elif _cls263 is not None:
                _wide263 = set(_cls263)
            for _cl263, _nm263 in _meths263.get(_m263, ()):
                if _wide263 is None or _cl263 in _wide263:
                    _graph263[_src263].add(_nm263)
                    _unchk263.add((_src263, _nm263))
    # Constructors: Module 5 keeps only `self.f = <param>` of `__init__`, so its calls are
    # read from the woven AST, resolved by method name (coarse — the sound direction).
    from frontend import pure_ast as _ast263
    for _cd263 in _ast263.walk(unified_ast):
        if not isinstance(_cd263, _ast263.ClassDef) or _cd263.name not in _bases263:
            continue
        _ini263 = "__init__@" + _cd263.name
        _graph263.setdefault(_ini263, set())
        for _md263 in _cd263.body:
            if not (isinstance(_md263, _ast263.FunctionDef)
                    and _md263.name in ("__init__", "__post_init__", "__new__")):
                continue
            for _n263 in _ast263.walk(_md263):
                if not isinstance(_n263, _ast263.Call):
                    continue
                _fx263 = _n263.func
                _to263 = set()
                if isinstance(_fx263, _ast263.Name):
                    if _fx263.id in _names263:
                        _to263.add(_fx263.id)
                    elif _fx263.id in _bases263:
                        _to263.add("__init__@" + _fx263.id)
                elif isinstance(_fx263, _ast263.Attribute):
                    _wide263 = None
                    if isinstance(_fx263.value, _ast263.Name) and _fx263.value.id == "self":
                        _wide263 = _rel263.get(_cd263.name, {_cd263.name})
                    elif (isinstance(_fx263.value, _ast263.Name)
                          and (_fx263.value.id in _modnames263
                               or _fx263.value.id in _builtins263)):
                        _wide263 = set()
                    for _cl263, _nm263 in _meths263.get(_fx263.attr, ()):
                        if _wide263 is None or _cl263 in _wide263:
                            _to263.add(_nm263)
                for _t263 in _to263:
                    _graph263[_ini263].add(_t263)
                    _unchk263.add((_ini263, _t263))
    # Tarjan's SCCs, iterative and deterministic.
    _idx263 = {}
    _low263 = {}
    _onst263 = set()
    _stack263 = []
    _sccs263 = []
    _ctr263 = 0
    for _root263 in sorted(_graph263):
        if _root263 in _idx263:
            continue
        _idx263[_root263] = _low263[_root263] = _ctr263
        _ctr263 += 1
        _stack263.append(_root263)
        _onst263.add(_root263)
        _work263 = [(_root263, sorted(_graph263.get(_root263, ())), 0)]
        while _work263:
            _v263, _succ263, _i263 = _work263[-1]
            if _i263 < len(_succ263):
                _work263[-1] = (_v263, _succ263, _i263 + 1)
                _w263 = _succ263[_i263]
                if _w263 not in _idx263:
                    _idx263[_w263] = _low263[_w263] = _ctr263
                    _ctr263 += 1
                    _stack263.append(_w263)
                    _onst263.add(_w263)
                    _work263.append((_w263, sorted(_graph263.get(_w263, ())), 0))
                elif _w263 in _onst263:
                    _low263[_v263] = min(_low263[_v263], _idx263[_w263])
                continue
            _work263.pop()
            if _work263:
                _p263 = _work263[-1][0]
                _low263[_p263] = min(_low263[_p263], _low263[_v263])
            if _low263[_v263] == _idx263[_v263]:
                _comp263 = []
                while True:
                    _x263 = _stack263.pop()
                    _onst263.discard(_x263)
                    _comp263.append(_x263)
                    if _x263 == _v263:
                        break
                _sccs263.append(sorted(_comp263))
    _pending263 = []
    for _comp263 in _sccs263:
        _cs263 = set(_comp263)
        _cand263 = sorted((a, b) for (a, b) in _unchk263 if a in _cs263 and b in _cs263)
        if _cand263:
            _pending263.append((_comp263, _cand263))
    # (#49) ROUTE #269 (R4) — `#@ \diverges` + `#@ no_exception \all` ON A RECURSION.
    # `\all` is the Phase-1 set (`exception_model.KNOWN_EXCEPTIONS`); RecursionError is not
    # in it, and PyCSL does not model the interpreter's recursion limit. For a TERMINATING
    # recursion that is a documented scope statement; for a recursion that is DECLARED
    # possibly non-terminating it is the claim's whole content: the only way an unbounded
    # Python recursion fails to return is RecursionError. MEASURED at 8b0bfbbd:
    # `def f(k): return f(k)` and `def m(self, k): return self.m(k)` under both clauses
    # PROVED `\result == 0`; CPython raises RecursionError. RULE: a `\diverges` function
    # declaring `no_exception \all` may not reach a call-graph cycle (this unit's graph
    # above, method and constructor edges included; itself on a cycle counts).
    _cyc269 = set()
    for _comp263 in _sccs263:
        if len(_comp263) > 1 or _comp263[0] in _graph263.get(_comp263[0], ()):
            _cyc269 |= set(_comp263)
    for _f263 in _fn263:
        if (not _f263.get("diverges") or _f263.get("trusted") or _f263.get("abstract")
                or not (_f263.get("contracts") or {}).get("no_exception_all")):
            continue
        _sn269 = set()
        _td269 = [_f263["name"]]
        _hit269 = ""
        while _td269 and not _hit269:
            _x269 = _td269.pop()
            if _x269 in _sn269:
                continue
            _sn269.add(_x269)
            if _x269 in _cyc269:
                _hit269 = _x269
            _td269.extend(sorted(_graph263.get(_x269, ())))
        if _hit269:
            from errors import PyCSLSemanticError as _PyCSLSemErr269
            raise _PyCSLSemErr269(
                f"'{_f263['name']}' is `#@ \\diverges` and declares `#@ no_exception "
                f"\\all`, but it reaches the recursive call cycle through '{_hit269}'. A "
                f"Python recursion that does not terminate does not run forever: it raises "
                f"RecursionError, which is NOT among the exceptions `\\all` covers "
                f"(exception_model.KNOWN_EXCEPTIONS — PyCSL does not model the recursion "
                f"limit), so the claim would hold of the model and not of CPython. Drop "
                f"`no_exception \\all` (or name the exceptions you mean), or give the "
                f"recursion a `#@ \\variant` instead of `#@ \\diverges`.",
                filename=args.file, stage="ir-semantic",
                code="PYCSL-SEM-DIVERGES-NO-EXCEPTION-RECURSION")

    # (#49) ROUTE #243 — A CONSTRUCTOR THAT GIVES ONE DICT/SET TWO FIELD NAMES.
    # A dict/set field is a PURE map, so two fields bound to ONE Python object are two
    # independent copies in the model. Module 6 refuses that shape in every EMITTED body,
    # but `__init__` / `__post_init__` / `__new__` never reach Module 6 as bodies: Module 5
    # keeps only each `self.f = <param>` binding (`init_body`) and havocs the rest
    # (`init_unknown_fields`), and `__post_init__` is dropped outright. Measured at
    # cdac19a6, each PROVED `\result == False` where CPython answers True, for a method
    # doing `if 1 in self.g: return False; self.d[1] = 5; return 1 in self.g`:
    #     def __post_init__(self): self.g = self.d
    #     def __init__(self): self.d = {}; self.g = self.d
    #     def __init__(self, p): self.d = p; self.g = p
    # So scan those three bodies here, on the source: a store to a dict/set field (typed
    # by the IR's own record declarations) must be a FRESH value, or a parameter of that
    # method that is named exactly once in it. CHOKE POINT: `_run_pipeline`'s mirror twin
    # is `\trusted`.
    _ir243 = _json.loads(json_ir)
    _dsf243 = {}
    for _td243 in (_ir243.get("type_decls") or []):
        if isinstance(_td243, dict) and isinstance(_td243.get("name"), str):
            _dsf243[_td243["name"]] = {
                _fd.get("name") for _fd in (_td243.get("fields") or [])
                if isinstance(_fd, dict) and _fd.get("type") in ("dict", "set", "frozenset")}
    # GATED, like the Module 6 rule, on an in-place mutation that could EXPOSE the alias.
    # Every in-place dict/set mutation in the parsed unit (a subscript store or `del`, an
    # augmented `|=`/`&=`/`^=`/`-=`, a mutator call) is recorded by the ROOT of its
    # receiver: the first attribute of a `<name>.<attr>...` chain goes into `_mf243` (a
    # field), a bare name sets `_mn243` (a local or parameter). A store is refused only if
    # its target field, or a field its value reads, is in `_mf243` — or its value reads a
    # plain name and `_mn243` is set. Without such a mutation an alias and a copy are
    # indistinguishable (the mirror's own `__init__` reads `self.ir.get(...)` into fields
    # no code mutates).
    _mf243 = set()
    _mn243 = False
    if any(_dsf243.values()):
        from frontend import pure_ast as _ast243
        for _n243 in _ast243.walk(unified_ast):
            _rc243 = []
            if isinstance(_n243, (_ast243.Assign, _ast243.AugAssign, _ast243.Delete)):
                _tg243 = (list(_n243.targets) if not isinstance(_n243, _ast243.AugAssign)
                          else [_n243.target])
                for _t243 in _tg243:
                    if isinstance(_t243, _ast243.Subscript):
                        _rc243.append(_t243.value)
                    elif (isinstance(_n243, _ast243.AugAssign)
                          and type(_n243.op).__name__ in ("BitOr", "BitAnd", "BitXor", "Sub")):
                        _rc243.append(_t243)
            elif (isinstance(_n243, _ast243.Call) and isinstance(_n243.func, _ast243.Attribute)
                  and _n243.func.attr in ("add", "discard", "remove", "pop", "popitem", "clear",
                                          "update", "setdefault", "intersection_update",
                                          "difference_update", "symmetric_difference_update")):
                _rc243.append(_n243.func.value)
            for _r243 in _rc243:
                _root243 = None
                while isinstance(_r243, (_ast243.Attribute, _ast243.Subscript)):
                    if (isinstance(_r243, _ast243.Attribute)
                            and isinstance(_r243.value, _ast243.Name)):
                        _root243 = _r243.attr
                    _r243 = _r243.value
                if _root243 is not None:
                    _mf243.add(_root243)
                elif isinstance(_r243, _ast243.Name):
                    _mn243 = True
                else:
                    _mn243 = True
                    _mf243.add("*")
    if _mf243 or _mn243:
        _fresh243 = ("set", "dict", "frozenset", "defaultdict", "OrderedDict", "Counter")
        for _c243 in _ast243.walk(unified_ast):
            if not (isinstance(_c243, _ast243.ClassDef) and _dsf243.get(_c243.name)):
                continue
            _fl243 = _dsf243[_c243.name]
            for _m243 in _c243.body:
                if not (isinstance(_m243, (_ast243.FunctionDef, _ast243.AsyncFunctionDef))
                        and _m243.name in ("__init__", "__post_init__", "__new__")):
                    continue
                _a243 = list(getattr(_m243.args, "posonlyargs", []) or []) + list(
                    _m243.args.args or []) + list(getattr(_m243.args, "kwonlyargs", []) or [])
                if not _a243:
                    continue
                _self243 = _a243[0].arg
                _params243 = {_x.arg for _x in _a243[1:]}
                _uses243 = {}
                for _n243 in _ast243.walk(_m243):
                    if isinstance(_n243, _ast243.Name):
                        _uses243[_n243.id] = _uses243.get(_n243.id, 0) + 1
                for _n243 in _ast243.walk(_m243):
                    if isinstance(_n243, _ast243.Assign):
                        _tg243, _v243 = list(_n243.targets), _n243.value
                    elif isinstance(_n243, _ast243.AnnAssign) and _n243.value is not None:
                        _tg243, _v243 = [_n243.target], _n243.value
                    else:
                        continue
                    _hit243 = None
                    _st243 = list(_tg243)
                    while _st243:
                        _t243 = _st243.pop()
                        if isinstance(_t243, (_ast243.Tuple, _ast243.List)):
                            _st243.extend(_t243.elts)
                            if any(isinstance(_e, _ast243.Attribute) for _e in _t243.elts):
                                _hit243 = _hit243 or "?"
                        elif (isinstance(_t243, _ast243.Attribute)
                              and isinstance(_t243.value, _ast243.Name)
                              and _t243.value.id == _self243 and _t243.attr in _fl243):
                            _hit243 = _t243.attr
                    if _hit243 is None and not (
                            isinstance(_v243, _ast243.Attribute)
                            and isinstance(_v243.value, _ast243.Name)
                            and _v243.value.id == _self243 and _v243.attr in _fl243):
                        continue
                    _ok243 = (
                        isinstance(_v243, (_ast243.Dict, _ast243.Set, _ast243.DictComp,
                                           _ast243.SetComp, _ast243.List, _ast243.ListComp,
                                           _ast243.Constant))
                        or (isinstance(_v243, _ast243.Call)
                            and ((isinstance(_v243.func, _ast243.Name)
                                  and _v243.func.id in _fresh243)
                                 or (isinstance(_v243.func, _ast243.Attribute)
                                     and _v243.func.attr == "copy")))
                        or (isinstance(_v243, _ast243.Name) and _v243.id in _params243
                            and _uses243.get(_v243.id, 0) == 1 and _hit243 not in (None, "?")))
                    if not _ok243:
                        # Which fields / plain names does the value READ?
                        _rd243, _rn243 = set(), False
                        for _x243 in _ast243.walk(_v243):
                            if (isinstance(_x243, _ast243.Attribute)
                                    and isinstance(_x243.value, _ast243.Name)):
                                _rd243.add(_x243.attr)
                            elif isinstance(_x243, _ast243.Name) and _x243.id != _self243:
                                _rn243 = True
                        _ok243 = not ("*" in _mf243
                                      or (_hit243 == "?" and _mf243)
                                      or ({_hit243} | _rd243) & _mf243
                                      or (_rn243 and _mn243))
                    if not _ok243:
                        from errors import PyCSLSemanticError as _PyCSLSemErr243
                        raise _PyCSLSemErr243(
                            f"{args.file} (line {getattr(_n243, 'lineno', 0)}): "
                            f"`{_c243.name}.{_m243.name}` binds a dict/set field to a value "
                            f"that is not a fresh dict/set (or to a parameter it also uses "
                            f"elsewhere), so ONE Python object would be reachable through two "
                            f"names. PyCSL models a dict/set as a pure map, so each name holds a "
                            f"COPY and an in-place mutation through one is invisible through the "
                            f"other (route #243). Refusing instead of answering incorrectly. "
                            f"Bind the field to a fresh value (a literal, `dict(x)`/`set(x)`, "
                            f"`x.copy()`).",
                            filename=args.file, line=getattr(_n243, "lineno", 0) or 0,
                            stage="ir-semantic", code="PYCSL-SEM-COLLECTION-ALIAS")

    # (#49) ROUTE #272 — THE RAISE THE STUB DROPPED.
    # A METHOD call (`self.m()`, `obj.m()`, `C.m()`, `C().m()`, `super().m()`, `self.f.m()`)
    # lowers to an abstract `val` stub carrying the callee's `ensures` and nothing of its
    # exceptions: an UNDECLARED escaping `raise` in the callee is read partially (an added
    # `raises { E }` on the callee's own `let`) and never reaches the stub, so a caller's
    # `#@ no_exception` is discharged by NOBODY. MEASURED at 5fe6cbdd (CPython raises
    # ValueError in each): `self.chk(k)`, `c.chk(k)`, `C.chk(k)`, `C().chk(k)`,
    # `super().chk(k)`, `self.d.chk(k)` with `chk` raising undeclared, all PROVED
    # `no_exception \all`; so did a chain `m -> mid -> chk` through a method or a module
    # function (`mid` itself has nothing to declare: its exception arrives through a stub),
    # and a `C.chk(k)` (static) whose `#@ raises ValueError when k > 0` IS declared — the
    # route #100/#105/#186 wrap is keyed on `self.`/typed-variable receivers only. A MODULE
    # function call is applied concretely, so Why3's effect typing already sees its own
    # `raise` ("raises unlisted exception") — but not one hidden behind a stub inside it.
    # RULE (fail-closed): HIDDEN(call) = what the callee may raise that the call site cannot
    # see — for a method callee, its escaping undeclared raises (a bare/computed `raise`
    # counts as unknown), plus its DECLARED ones when the receiver form is not one the wrap
    # resolves (`self.…` or a variable typed with a class of this unit), plus HIDDEN-OUT of
    # the callee; for a module-function callee, HIDDEN-OUT only. HIDDEN-OUT(g) = the union
    # of HIDDEN over g's calls not caught by an enclosing handler of g (a declared `raises`
    # on g does NOT excuse it: the hidden path never checks g's condition). A function
    # claiming `no_exception` (`\all`: any exception; a named list: a listed class or a
    # subclass, or a name outside the modelled hierarchy) with a call whose HIDDEN set it
    # covers, outside a handler catching it, is refused. Callees are resolved on route
    # #263's call graph (over-approximating: an unresolved receiver names every method of
    # that name). `\trusted`/`\abstract`/imported callees speak by their contract only
    # (route #207 refuses a bodyless METHOD under `no_exception`; an imported function's
    # stub carries the `raises` its body shows). Constructors are route #179's.
    # No `no_exception` function in the unit -> nothing is computed. INLINE
    # (check-mirror-coverage); `_run_pipeline`'s mirror twin is `\trusted`.
    if any((_f.get("contracts") or {}).get("no_exception")
           or (_f.get("contracts") or {}).get("no_exception_all") for _f in _fn263):
        from exception_model import (handler_catches as _hc272,
                                     EXCEPTION_BASES as _eb272,
                                     KNOWN_EXCEPTIONS as _ke272)
        _dir272 = {}
        _calls272 = {}
        _decl272 = {}
        for _f272 in _fn263:
            _n272 = _f272["name"]
            _decl272[_n272] = {_r.get("exc_type") for _r in
                               ((_f272.get("contracts") or {}).get("raises") or [])
                               if isinstance(_r, dict) and _r.get("exc_type")}
            _dir272[_n272] = set()
            _calls272[_n272] = []
            if (_f272.get("trusted") or _f272.get("abstract") or _f272.get("lemma")
                    or _n272 in (imported_names or set())):
                continue
            _w272 = [(_f272.get("body"), frozenset())]
            while _w272:
                _x272, _cg272 = _w272.pop()
                if isinstance(_x272, list):
                    _w272.extend((_v, _cg272) for _v in _x272)
                    continue
                if not isinstance(_x272, dict):
                    continue
                if _x272.get("stmt") == "Try":
                    _hs272 = set()
                    for _h272 in (_x272.get("handlers") or []):
                        if isinstance(_h272, dict) and isinstance(_h272.get("exc_type"), str):
                            _hs272 |= {_p.strip() for _p in _h272["exc_type"].split("|")
                                       if _p.strip()}
                    _w272.append((_x272.get("body"), _cg272 | _hs272))
                    _w272.extend((_v, _cg272) for _k, _v in _x272.items() if _k != "body")
                    continue
                if _x272.get("stmt") == "Raise":
                    _e272 = _x272.get("exc_type") or "*"
                    if not any(_hc272(_c, _e272) for _c in _cg272):
                        _dir272[_n272].add(_e272)
                if _x272.get("type") == "Call" and isinstance(_x272.get("func"), str):
                    _calls272[_n272].append((_x272, _cg272))
                _w272.extend((_v, _cg272) for _v in _x272.values())
        # Per call: [(callee, is_method, receiver form resolved by the wrap)].
        _res272 = {}
        _gl272 = {_g.get("name") for _g in (_ir263.get("module_globals") or [])
                  if isinstance(_g, dict) and _g.get("class")}
        for _f272 in _fn263:
            _n272 = _f272["name"]
            _sy272 = dict(_f272.get("symbol_table") or {})
            _sy272.update(_f272.get("param_annotations") or {})
            # receivers the wrap resolves (`find_record_var_classes`, `_record_param_classes`,
            # `_module_global_classes`): a constructor-bound local, a class-typed
            # variable, a module-global instance
            _rv272 = set(_gl272)
            _w272 = [_f272.get("body")]
            while _w272:
                _x272 = _w272.pop()
                if isinstance(_x272, list):
                    _w272.extend(_x272)
                elif isinstance(_x272, dict):
                    _v272 = _x272.get("value")
                    if (_x272.get("stmt") == "Assign" and isinstance(_x272.get("target"), str)
                            and isinstance(_v272, dict) and _v272.get("type") == "Call"
                            and _v272.get("func") in _bases263 and "receiver" not in _v272):
                        _rv272.add(_x272["target"])
                    _w272.extend(_x272.values())
            _rv272 |= {_k for _k, _t in _sy272.items()
                       if isinstance(_t, str) and _tcls263.get(_t)}
            for _i272, (_c272, _cg272) in enumerate(_calls272[_n272]):
                _fs272 = _c272["func"]
                _out272 = []
                if "." not in _fs272 and "receiver" not in _c272:
                    if (_fs272 in _byname263
                            and _byname263[_fs272].get("kind") != "method"):
                        _out272.append((_fs272, False, True))
                else:
                    _pt272 = _fs272.split(".")
                    _good272 = "receiver" not in _c272 and (
                        (_pt272[0] == "self" and len(_pt272) >= 2)
                        or (len(_pt272) == 2 and _pt272[0] not in _bases263
                            and _pt272[0] in _rv272))
                    for _cl272, _nm272 in _meths263.get(_pt272[-1], ()):
                        if _nm272 in _graph263.get(_n272, ()):
                            _out272.append((_nm272, True, _good272))
                _res272[(_n272, _i272)] = _out272
        _ho272 = {_n: set() for _n in _dir272}
        _chg272 = True
        while _chg272:
            _chg272 = False
            for _n272 in _ho272:
                _new272 = set()
                for _i272, (_c272, _cg272) in enumerate(_calls272[_n272]):
                    for _g272, _ism272, _good272 in _res272[(_n272, _i272)]:
                        _hid272 = set(_ho272.get(_g272, ()))
                        if _ism272:
                            _hid272 |= _dir272.get(_g272, set()) - _decl272.get(_g272, set())
                            if not _good272:
                                _hid272 |= _decl272.get(_g272, set())
                        _new272 |= {_e for _e in _hid272
                                    if not any(_hc272(_c, _e) for _c in _cg272)}
                if not _new272 <= _ho272[_n272]:
                    _ho272[_n272] |= _new272
                    _chg272 = True
        _viol272 = []
        for _f272 in _fn263:
            _n272 = _f272["name"]
            _ct272 = _f272.get("contracts") or {}
            _all272 = bool(_ct272.get("no_exception_all"))
            _act272 = [a for a in (_ct272.get("no_exception") or []) if isinstance(a, str)]
            if not (_all272 or _act272) or not _calls272.get(_n272):
                continue
            for _i272, (_c272, _cg272) in enumerate(_calls272[_n272]):
                for _g272, _ism272, _good272 in _res272[(_n272, _i272)]:
                    _hid272 = set(_ho272.get(_g272, ()))
                    if _ism272:
                        _hid272 |= _dir272.get(_g272, set()) - _decl272.get(_g272, set())
                        if not _good272:
                            _hid272 |= _decl272.get(_g272, set())
                    for _e272 in sorted(_hid272):
                        if any(_hc272(_c, _e272) for _c in _cg272):
                            continue
                        if (_all272 or any(_hc272(_a, _e272) for _a in _act272)
                                or (_e272 not in _eb272 and _e272 not in _ke272)):
                            _viol272.append((_n272, _c272["func"], _g272, _e272))
        if _viol272:
            from errors import PyCSLSemanticError as _PyCSLSemErr272
            _v272 = _viol272[0]
            raise _PyCSLSemErr272(
                f"'{_v272[0]}' claims `#@ no_exception` and calls `{_v272[1]}(...)` (resolved "
                f"to '{_v272[2]}'), which may raise "
                f"{'an exception PyCSL cannot name' if _v272[3] == '*' else '`' + _v272[3] + '`'}"
                f" where this call site cannot see it: a METHOD call lowers to an abstract "
                f"`val` that carries only the callee's DECLARED `#@ raises` (and only for a "
                f"`self.`/typed-variable receiver), so an undeclared `raise` in the callee — or "
                f"one reaching it through such a stub further down — is assumed not to happen "
                f"and the claim would be proved while CPython raises (route #272). Declare the "
                f"exception on EVERY function of the chain with `#@ raises E when <cond>` and "
                f"call it through `self.` or a typed variable, catch it around the call, or "
                f"drop it from the `#@ no_exception` context"
                f"{'' if len(_viol272) == 1 else f' (also: {_viol272[1:4]})'}.",
                filename=args.file, stage="ir-semantic",
                code="PYCSL-SEM-UNDECLARED-CALLEE-RAISE")

    # (#49) ROUTE #264 — A READ OF A LOCAL THAT IS NOT DEFINITELY ASSIGNED.
    #
    # Module 6 hoists every local as `let y = ref 0 in` and `del y` lowers to `()`, so a
    # read of a local that no path has bound read the DECLARATION DEFAULT 0. Python raises
    # `UnboundLocalError` there, and PyCSL claims normal termination by default, so the
    # raising path PROVED postconditions. MEASURED at 283d1033, all five Verification
    # SUCCESS, all five `UnboundLocalError` in CPython (witnesses-r264/):
    #     if c: y = 1          / return y           (s04, `f(False)`)
    #     n += 1               / n never bound      (s03)
    #     x = 1; del x; return x                    (s06)
    #     n = 0 at module level, `n += 1` with no `global`   (s01/s07 — a name bound
    #         ANYWHERE in a function is local to ALL of it, so the module global is
    #         never consulted)
    # THE RULE is Python's own: the function's locals are its parameters and every name
    # its own scope binds (assignment / augmented / annotated-with-value targets, `for`
    # and `with ... as` targets, `except ... as`, a walrus — also from inside a
    # comprehension, PEP 572 —, `import`, a nested `def`/`class`, a `match` capture, and
    # `del`), minus `global`/`nonlocal` names. A MUST-ASSIGN dataflow over a control-flow
    # graph of the body then refuses every read (and every `del`) of a local that is not
    # bound on EVERY path reaching it. The graph is Python's: a loop body may run zero
    # times (except `while True` and `for` over a constant non-empty `range`, whose first
    # iteration is certain); `break`/`continue`/`return`/`raise` end their path; an
    # exception edge from inside a `try` carries the state BEFORE the raising operation;
    # `except E as e` UNBINDS `e` when the handler ends; a `finally` is analysed on the
    # normal path and once more on the exceptional one; a `with` body may be left by an
    # exception its `__exit__` SUPPRESSES; a `match` with no irrefutable unguarded arm may
    # fall through; `and`/`or`/`if-else` operands and comprehension bodies are
    # conditional, so a walrus there binds nothing definitely. A call statement to a
    # same-file function (or `self.` method) EVERY definition of which ends in `raise` and
    # has no `return` cannot fall through (the parsers' `self._err(...)` idiom).
    # UNREACHABLE code is never refused (its state is TOP).
    #
    # SCOPE: functions whose body is LOWERED — a `\trusted`/`\abstract` function is
    # skipped together with everything nested in it, since its body is never modelled.
    # RESIDUE (stated, not hidden): a read inside a NESTED function/lambda of an enclosing
    # local (a closure cell read at CALL time) and the deferred parts of a generator
    # expression are not tracked; a `self.<m>` no-return call trusts that no subclass
    # overrides `<m>` with a returning body.
    #
    # BLAST RADIUS, MEASURED before landing (CPython-`ast` prototype of THIS block): 47
    # findings in pycsl-reference, all in 31 files — 25 PASS `--no-proof` concurrency
    # drivers whose workers do `counter += 1` on a `#@ shared` module global WITHOUT
    # `global` (every one an `UnboundLocalError` in CPython; their sources gain the
    # missing `global` line, emission byte-identical), 5 expected-FAIL concurrency
    # witnesses and 1993 (each refused EARLIER, for its own reason, since this check runs
    # after Module 5 and the IR checks), 1026 (cleared by the constant-`range` rule). 1 in
    # python-reference (0177, a constant `range(100)` loop — cleared by the same rule).
    # 12 in the mirror, all in `\trusted` functions or behind a `self._err`/`self.error`
    # call (cleared). 3 in `pycsl_lib/json/encoder.py`, already REFUSED.
    #
    # CHOKE POINT: `_run_pipeline`'s mirror twin is `#@ \trusted`, and the whole analysis
    # is written INLINE (no nested `def`: `check-mirror-coverage`), iteratively.
    from frontend import pure_ast as _A264
    _r264_tree = unified_ast
    _r264_bad = []
    _R264_COMPS = (_A264.ListComp, _A264.SetComp, _A264.DictComp, _A264.GeneratorExp)
    _R264_FNS = (_A264.FunctionDef, _A264.AsyncFunctionDef)
    # same-file names whose every definition ends in `raise` and contains no `return`
    _r264_defs = {}
    _r264_range_ok = True
    for _r264_n in _A264.walk(_r264_tree):
        if isinstance(_r264_n, _R264_FNS):
            # (#270) a GENERATOR (any own `yield`/`yield from`) or a coroutine is never
            # no-return: calling it only BUILDS the generator/coroutine, its body does
            # not run at the call — so it counts here exactly like a `return`.
            _r264_ret = isinstance(_r264_n, _A264.AsyncFunctionDef)
            _r264_stk = [] if _r264_ret else list(_r264_n.body)
            while _r264_stk:
                _r264_m = _r264_stk.pop()
                if isinstance(_r264_m, (_A264.Return, _A264.Yield, _A264.YieldFrom)):
                    _r264_ret = True
                    break
                if not isinstance(_r264_m, (_R264_FNS, _A264.ClassDef, _A264.Lambda)):
                    _r264_stk.extend(_A264.iter_child_nodes(_r264_m))
            _r264_defs.setdefault(_r264_n.name, []).append(
                bool(_r264_n.body) and isinstance(_r264_n.body[-1], _A264.Raise)
                and not _r264_ret)
            if _r264_n.name == "range":
                _r264_range_ok = False
        elif (isinstance(_r264_n, _A264.Name) and _r264_n.id == "range"
              and isinstance(_r264_n.ctx, (_A264.Store, _A264.Del))):
            _r264_range_ok = False
        elif isinstance(_r264_n, _A264.alias) and (_r264_n.asname or _r264_n.name) == "range":
            _r264_range_ok = False
    _r264_noret = {_r264_k for _r264_k, _r264_v in _r264_defs.items() if all(_r264_v)}
    _r264_fns = []
    _r264_stk = [_r264_tree]
    while _r264_stk:
        _r264_n = _r264_stk.pop()
        if isinstance(_r264_n, _R264_FNS):
            if (getattr(_r264_n, "csl_trusted", False)
                    or getattr(_r264_n, "csl_abstract", False)):
                continue
            _r264_fns.append(_r264_n)
        _r264_stk.extend(_A264.iter_child_nodes(_r264_n))
    for _r264_fn in _r264_fns:
        # ---- 1. the function's LOCALS: every name bound anywhere in its own scope ----
        _r264_a = _r264_fn.args
        _r264_params = [_r264_x.arg for _r264_x in (
            list(getattr(_r264_a, "posonlyargs", None) or [])
            + list(_r264_a.args or []) + list(_r264_a.kwonlyargs or []))]
        if _r264_a.vararg is not None:
            _r264_params.append(_r264_a.vararg.arg)
        if _r264_a.kwarg is not None:
            _r264_params.append(_r264_a.kwarg.arg)
        _r264_bound = set()
        _r264_glob = set()
        _r264_stk = list(_r264_fn.body)
        while _r264_stk:
            _r264_n = _r264_stk.pop()
            if isinstance(_r264_n, list):
                _r264_stk.extend(_r264_n)
                continue
            if not isinstance(_r264_n, _A264.AST):
                continue
            if isinstance(_r264_n, (_A264.Global, _A264.Nonlocal)):
                _r264_glob.update(_r264_n.names)
                continue
            if isinstance(_r264_n, (_R264_FNS, _A264.ClassDef)):
                _r264_bound.add(_r264_n.name)
                _r264_stk.extend(_r264_n.decorator_list or [])
                if isinstance(_r264_n, _A264.ClassDef):
                    _r264_stk.extend(_r264_n.bases or [])
                    _r264_stk.extend(_r264_k.value for _r264_k in (_r264_n.keywords or []))
                else:
                    _r264_stk.extend(_r264_n.args.defaults or [])
                    _r264_stk.extend(_r264_d for _r264_d in (_r264_n.args.kw_defaults or [])
                                     if _r264_d is not None)
                continue
            if isinstance(_r264_n, _A264.Lambda):
                _r264_stk.extend(_r264_n.args.defaults or [])
                _r264_stk.extend(_r264_d for _r264_d in (_r264_n.args.kw_defaults or [])
                                 if _r264_d is not None)
                continue
            if isinstance(_r264_n, _R264_COMPS):
                # a comprehension's own targets are ITS locals; only a walrus inside it
                # binds in the enclosing function (PEP 572).
                for _r264_m in _A264.walk(_r264_n):
                    if (isinstance(_r264_m, _A264.NamedExpr)
                            and isinstance(_r264_m.target, _A264.Name)):
                        _r264_bound.add(_r264_m.target.id)
                continue
            if (isinstance(_r264_n, _A264.Name)
                    and isinstance(_r264_n.ctx, (_A264.Store, _A264.Del))):
                _r264_bound.add(_r264_n.id)
            elif (isinstance(_r264_n, _A264.NamedExpr)
                  and isinstance(_r264_n.target, _A264.Name)):
                _r264_bound.add(_r264_n.target.id)
            elif isinstance(_r264_n, _A264.ExceptHandler) and _r264_n.name:
                _r264_bound.add(_r264_n.name)
            elif isinstance(_r264_n, _A264.alias) and _r264_n.name != "*":
                _r264_bound.add(_r264_n.asname or _r264_n.name.split(".")[0])
            elif (isinstance(_r264_n, (_A264.MatchAs, _A264.MatchStar))
                  and getattr(_r264_n, "name", None)):
                _r264_bound.add(_r264_n.name)
            elif isinstance(_r264_n, _A264.MatchMapping) and getattr(_r264_n, "rest", None):
                _r264_bound.add(_r264_n.rest)
            _r264_stk.extend(_A264.iter_child_nodes(_r264_n))
        _r264_locals = (_r264_bound | set(_r264_params)) - _r264_glob
        if not (_r264_bound - _r264_glob):
            continue
        # ---- 2. a control-flow graph of the body, built with an explicit task stack ----
        # node = [op, normal successors, exception successors]. An EXCEPTION edge carries
        # the node's IN state (the operation may raise before it takes effect), a normal
        # edge its OUT state. Node 0 is the entry.
        _r264_nodes = [[None, [], []]]
        _r264_cur = 0
        _r264_exc = []
        _r264_loops = []
        _r264_tk = [("S", _r264_s) for _r264_s in reversed(_r264_fn.body)]
        while _r264_tk:
            _r264_t = _r264_tk.pop()
            _r264_k = _r264_t[0]
            _r264_seq = None
            if _r264_k == "op":
                _r264_nodes.append([_r264_t[1], [], [_r264_exc[-1]] if _r264_exc else []])
                _r264_nodes[_r264_cur][1].append(len(_r264_nodes) - 1)
                _r264_cur = len(_r264_nodes) - 1
            elif _r264_k == "link":
                _r264_nodes[_r264_cur][1].append(_r264_t[1])
            elif _r264_k == "setcur":
                _r264_cur = _r264_t[1]
            elif _r264_k == "newfrom":
                _r264_nodes.append([None, [], []])
                _r264_nodes[_r264_t[1]][1].append(len(_r264_nodes) - 1)
                _r264_cur = len(_r264_nodes) - 1
            elif _r264_k == "fresh":
                _r264_nodes.append([None, [], []])
                _r264_cur = len(_r264_nodes) - 1
            elif _r264_k == "xpush":
                _r264_exc.append(_r264_t[1])
            elif _r264_k == "xpop":
                _r264_exc.pop()
            elif _r264_k == "lpush":
                _r264_loops.append((_r264_t[1], _r264_t[2]))
            elif _r264_k == "lpop":
                _r264_loops.pop()
            elif _r264_k == "B":
                if not _r264_t[2]:
                    _r264_seq = [("op", ("def", _r264_t[1]))]
            elif _r264_k in ("T", "D"):
                _r264_e = _r264_t[1]
                if isinstance(_r264_e, _A264.Name):
                    _r264_seq = [("op", ("def", _r264_e.id) if _r264_k == "T"
                                  else ("del", _r264_e.id, getattr(_r264_e, "lineno", 0)))]
                elif isinstance(_r264_e, (_A264.Tuple, _A264.List)):
                    _r264_seq = [(_r264_k, _r264_x) for _r264_x in _r264_e.elts]
                elif isinstance(_r264_e, _A264.Starred):
                    _r264_seq = [(_r264_k, _r264_e.value)]
                elif isinstance(_r264_e, _A264.Attribute):
                    _r264_seq = [("E", _r264_e.value, False, frozenset())]
                elif isinstance(_r264_e, _A264.Subscript):
                    _r264_seq = [("E", _r264_e.value, False, frozenset()),
                                 ("E", _r264_e.slice, False, frozenset())]
                if _r264_exc and isinstance(_r264_e, (_A264.Attribute, _A264.Subscript)):
                    # (#270) the attribute/item STORE or DELETE itself may raise
                    _r264_seq.append(("op", ("nop",)))
            elif _r264_k == "P":
                _r264_e = _r264_t[1]
                _r264_seq = []
                if isinstance(_r264_e, _A264.MatchValue):
                    _r264_seq = [("E", _r264_e.value, False, frozenset())]
                elif isinstance(_r264_e, _A264.MatchSequence):
                    _r264_seq = [("P", _r264_x) for _r264_x in _r264_e.patterns]
                elif isinstance(_r264_e, _A264.MatchStar):
                    _r264_seq = [("op", ("def", _r264_e.name))] if _r264_e.name else []
                elif isinstance(_r264_e, _A264.MatchMapping):
                    _r264_seq = ([("E", _r264_x, False, frozenset()) for _r264_x in _r264_e.keys]
                                 + [("P", _r264_x) for _r264_x in _r264_e.patterns]
                                 + ([("op", ("def", _r264_e.rest))] if _r264_e.rest else []))
                elif isinstance(_r264_e, _A264.MatchClass):
                    _r264_seq = ([("E", _r264_e.cls, False, frozenset())]
                                 + [("P", _r264_x) for _r264_x in _r264_e.patterns]
                                 + [("P", _r264_x) for _r264_x in _r264_e.kwd_patterns])
                elif isinstance(_r264_e, _A264.MatchAs):
                    _r264_seq = (([("P", _r264_e.pattern)] if _r264_e.pattern is not None else [])
                                 + ([("op", ("def", _r264_e.name))] if _r264_e.name else []))
                elif isinstance(_r264_e, _A264.MatchOr):
                    _r264_seq = [("P", _r264_x) for _r264_x in _r264_e.patterns]
                if _r264_exc:
                    # (#270) matching a pattern may raise (`__eq__`, `__getitem__`,
                    # `isinstance` on a non-class, a missing attribute)
                    _r264_seq.append(("op", ("nop",)))
            elif _r264_k == "E":
                _r264_e, _r264_c, _r264_sh = _r264_t[1], _r264_t[2], _r264_t[3]
                if isinstance(_r264_e, list):
                    _r264_seq = [("E", _r264_x, _r264_c, _r264_sh) for _r264_x in _r264_e]
                elif not isinstance(_r264_e, _A264.AST):
                    pass
                elif isinstance(_r264_e, _A264.Name):
                    if (_r264_e.id in _r264_locals and _r264_e.id not in _r264_sh
                            and not isinstance(_r264_e.ctx, (_A264.Store, _A264.Del))):
                        _r264_seq = [("op", ("use", _r264_e.id, getattr(_r264_e, "lineno", 0)))]
                elif isinstance(_r264_e, _A264.NamedExpr):
                    _r264_seq = [("E", _r264_e.value, _r264_c, _r264_sh),
                                 ("B", _r264_e.target.id, _r264_c)]
                elif isinstance(_r264_e, _A264.BoolOp):
                    _r264_seq = ([("E", _r264_e.values[0], _r264_c, _r264_sh)]
                                 + [("E", _r264_x, True, _r264_sh)
                                    for _r264_x in _r264_e.values[1:]])
                elif isinstance(_r264_e, _A264.IfExp):
                    _r264_seq = [("E", _r264_e.test, _r264_c, _r264_sh),
                                 ("E", _r264_e.body, True, _r264_sh),
                                 ("E", _r264_e.orelse, True, _r264_sh)]
                elif isinstance(_r264_e, _A264.Lambda):
                    _r264_seq = ([("E", _r264_x, _r264_c, _r264_sh)
                                  for _r264_x in (_r264_e.args.defaults or [])]
                                 + [("E", _r264_x, _r264_c, _r264_sh)
                                    for _r264_x in (_r264_e.args.kw_defaults or [])
                                    if _r264_x is not None])
                elif isinstance(_r264_e, _R264_COMPS):
                    _r264_sh2 = set(_r264_sh)
                    for _r264_g in _r264_e.generators:
                        for _r264_m in _A264.walk(_r264_g.target):
                            if isinstance(_r264_m, _A264.Name):
                                _r264_sh2.add(_r264_m.id)
                    _r264_sh2 = frozenset(_r264_sh2)
                    _r264_seq = [("E", _r264_e.generators[0].iter, _r264_c, _r264_sh)]
                    for _r264_gi, _r264_g in enumerate(_r264_e.generators):
                        if _r264_gi:
                            _r264_seq.append(("E", _r264_g.iter, True, _r264_sh2))
                        _r264_seq.extend(("E", _r264_x, True, _r264_sh2)
                                         for _r264_x in _r264_g.ifs)
                    for _r264_f in ("elt", "key", "value"):
                        if getattr(_r264_e, _r264_f, None) is not None:
                            _r264_seq.append(("E", getattr(_r264_e, _r264_f), True, _r264_sh2))
                else:
                    _r264_seq = [("E", _r264_x, _r264_c, _r264_sh)
                                 for _r264_x in _A264.iter_child_nodes(_r264_e)]
                # (#270) EVERY potentially-raising expression inside a protected region
                # (a `try` body/else/handler under a `finally`, a `with` body) adds an
                # exception edge carrying the state at that point — not only the
                # operations that read or write a local. A call, `1 // 0`, a subscript,
                # an attribute access, ... reading no local used to create NO edge, so
                # a `try` whose body was only `C.g(1)` left its handler unreachable
                # (TOP) and the `else`-path binding looked definite. Measured at
                # c9d7f157: `if c: y = 2` / `try: C.g(1) except ValueError: pass else:
                # y = 1` / `return y` PROVED; CPython `f(False)`: UnboundLocalError.
                # Only a literal, a lambda (creating one cannot raise), a walrus (its
                # value gets its own edge) and a local read (its `use` op already has
                # the edge) add none.
                if (_r264_exc and isinstance(_r264_e, _A264.AST)
                        and not isinstance(_r264_e, (_A264.Constant, _A264.Lambda,
                                                     _A264.NamedExpr))
                        and not (isinstance(_r264_e, _A264.Name) and _r264_seq)):
                    _r264_seq = list(_r264_seq or []) + [("op", ("nop",))]
            elif _r264_k == "S":
                _r264_s = _r264_t[1]
                _r264_z = frozenset()
                _r264_outer = _r264_exc[-1] if _r264_exc else None
                if isinstance(_r264_s, _A264.Expr):
                    _r264_seq = [("E", _r264_s.value, False, _r264_z)]
                    _r264_v = _r264_s.value
                    if (isinstance(_r264_v, _A264.Call) and (
                            (isinstance(_r264_v.func, _A264.Name)
                             and _r264_v.func.id in _r264_noret)
                            or (isinstance(_r264_v.func, _A264.Attribute)
                                and isinstance(_r264_v.func.value, _A264.Name)
                                and _r264_v.func.value.id in ("self", "cls")
                                and _r264_v.func.attr in _r264_noret))):
                        _r264_seq += [("op", ("nop",)), ("fresh",)]
                elif isinstance(_r264_s, _A264.Assign):
                    _r264_seq = ([("E", _r264_s.value, False, _r264_z)]
                                 + [("T", _r264_x) for _r264_x in _r264_s.targets])
                elif isinstance(_r264_s, _A264.AugAssign):
                    if isinstance(_r264_s.target, _A264.Name):
                        _r264_seq = [("op", ("use", _r264_s.target.id,
                                             getattr(_r264_s, "lineno", 0))),
                                     ("E", _r264_s.value, False, _r264_z),
                                     ("op", ("def", _r264_s.target.id))]
                    else:
                        _r264_seq = [("T", _r264_s.target), ("E", _r264_s.value, False, _r264_z)]
                elif isinstance(_r264_s, _A264.AnnAssign):
                    if _r264_s.value is not None:
                        _r264_seq = [("E", _r264_s.value, False, _r264_z), ("T", _r264_s.target)]
                elif isinstance(_r264_s, _A264.Delete):
                    _r264_seq = [("D", _r264_x) for _r264_x in _r264_s.targets]
                elif isinstance(_r264_s, _A264.Return):
                    _r264_seq = [("E", _r264_s.value, False, _r264_z), ("op", ("nop",)),
                                 ("fresh",)]
                elif isinstance(_r264_s, _A264.Raise):
                    _r264_seq = [("E", _r264_s.exc, False, _r264_z),
                                 ("E", _r264_s.cause, False, _r264_z),
                                 ("op", ("nop",)), ("fresh",)]
                elif isinstance(_r264_s, _A264.Assert):
                    _r264_seq = [("E", _r264_s.test, False, _r264_z),
                                 ("E", _r264_s.msg, True, _r264_z), ("op", ("nop",))]
                elif isinstance(_r264_s, (_A264.Break, _A264.Continue)):
                    if _r264_loops:
                        _r264_seq = [("op", ("nop",)),
                                     ("link", _r264_loops[-1][
                                         0 if isinstance(_r264_s, _A264.Break) else 1]),
                                     ("fresh",)]
                elif isinstance(_r264_s, (_A264.Import, _A264.ImportFrom)):
                    _r264_seq = [("op", ("def", _r264_x.asname or _r264_x.name.split(".")[0]))
                                 for _r264_x in _r264_s.names if _r264_x.name != "*"]
                elif isinstance(_r264_s, (_R264_FNS, _A264.ClassDef)):
                    _r264_seq = [("E", _r264_x, False, _r264_z)
                                 for _r264_x in (_r264_s.decorator_list or [])]
                    if isinstance(_r264_s, _A264.ClassDef):
                        _r264_seq += [("E", _r264_x, False, _r264_z)
                                      for _r264_x in (_r264_s.bases or [])]
                        _r264_seq += [("E", _r264_x.value, False, _r264_z)
                                      for _r264_x in (_r264_s.keywords or [])]
                    else:
                        _r264_seq += [("E", _r264_x, False, _r264_z)
                                      for _r264_x in (_r264_s.args.defaults or [])]
                        _r264_seq += [("E", _r264_x, False, _r264_z)
                                      for _r264_x in (_r264_s.args.kw_defaults or [])
                                      if _r264_x is not None]
                    _r264_seq.append(("op", ("def", _r264_s.name)))
                elif isinstance(_r264_s, _A264.If):
                    _r264_nodes.extend([[None, [], []], [None, [], []]])
                    _r264_C, _r264_J = len(_r264_nodes) - 2, len(_r264_nodes) - 1
                    _r264_seq = ([("E", _r264_s.test, False, _r264_z), ("link", _r264_C),
                                  ("newfrom", _r264_C)]
                                 + [("S", _r264_x) for _r264_x in _r264_s.body]
                                 + [("link", _r264_J), ("newfrom", _r264_C)]
                                 + [("S", _r264_x) for _r264_x in _r264_s.orelse]
                                 + [("link", _r264_J), ("setcur", _r264_J)])
                elif isinstance(_r264_s, _A264.While):
                    _r264_nodes.extend([[None, [], []], [None, [], []], [None, [], []]])
                    _r264_H, _r264_C, _r264_X = (len(_r264_nodes) - 3, len(_r264_nodes) - 2,
                                                 len(_r264_nodes) - 1)
                    _r264_seq = ([("link", _r264_H), ("setcur", _r264_H),
                                  ("E", _r264_s.test, False, _r264_z), ("link", _r264_C),
                                  ("lpush", _r264_X, _r264_H), ("newfrom", _r264_C)]
                                 + [("S", _r264_x) for _r264_x in _r264_s.body]
                                 + [("link", _r264_H), ("lpop",)])
                    if not (isinstance(_r264_s.test, _A264.Constant)
                            and _r264_s.test.value is True):
                        _r264_seq += ([("newfrom", _r264_C)]
                                      + [("S", _r264_x) for _r264_x in _r264_s.orelse]
                                      + [("link", _r264_X)])
                    _r264_seq.append(("setcur", _r264_X))
                elif isinstance(_r264_s, (_A264.For, _A264.AsyncFor)):
                    # `for _ in range(<constant ints>)` over a NON-EMPTY range runs its
                    # first iteration for certain: the loop is entered at the body, not
                    # at the head that may exit.
                    _r264_once = False
                    _r264_it = _r264_s.iter
                    if (_r264_range_ok and isinstance(_r264_s, _A264.For)
                            and isinstance(_r264_it, _A264.Call)
                            and isinstance(_r264_it.func, _A264.Name)
                            and _r264_it.func.id == "range" and "range" not in _r264_locals
                            and not _r264_it.keywords and 1 <= len(_r264_it.args) <= 3):
                        _r264_iv = []
                        for _r264_x in _r264_it.args:
                            if (isinstance(_r264_x, _A264.UnaryOp)
                                    and isinstance(_r264_x.op, _A264.USub)
                                    and isinstance(_r264_x.operand, _A264.Constant)
                                    and type(_r264_x.operand.value) is int):
                                _r264_iv.append(-_r264_x.operand.value)
                            elif (isinstance(_r264_x, _A264.Constant)
                                  and type(_r264_x.value) is int):
                                _r264_iv.append(_r264_x.value)
                        if (len(_r264_iv) == len(_r264_it.args)
                                and not (len(_r264_iv) == 3 and _r264_iv[2] == 0)):
                            _r264_once = len(range(*_r264_iv)) > 0
                    _r264_nodes.extend([[None, [], []], [None, [], []], [None, [], []]])
                    _r264_H, _r264_X, _r264_B = (len(_r264_nodes) - 3, len(_r264_nodes) - 2,
                                                 len(_r264_nodes) - 1)
                    _r264_nodes[_r264_H][1].append(_r264_B)
                    _r264_seq = ([("E", _r264_s.iter, False, _r264_z),
                                  ("link", _r264_B if _r264_once else _r264_H),
                                  ("lpush", _r264_X, _r264_H), ("setcur", _r264_B),
                                  ("op", ("nop",)), ("T", _r264_s.target)]
                                 + [("S", _r264_x) for _r264_x in _r264_s.body]
                                 + [("link", _r264_H), ("lpop",), ("newfrom", _r264_H)]
                                 + [("S", _r264_x) for _r264_x in _r264_s.orelse]
                                 + [("link", _r264_X), ("setcur", _r264_X)])
                elif isinstance(_r264_s, (_A264.With, _A264.AsyncWith)):
                    # a context manager's `__exit__` may SUPPRESS the body's exception, so
                    # control can reach the statement after the `with` from inside it.
                    _r264_nodes.extend([[None, [], []], [None, [], []]])
                    _r264_W, _r264_X = len(_r264_nodes) - 2, len(_r264_nodes) - 1
                    _r264_nodes[_r264_W][1].append(_r264_X)
                    if _r264_outer is not None:
                        _r264_nodes[_r264_W][1].append(_r264_outer)
                    _r264_seq = []
                    for _r264_x in _r264_s.items:
                        _r264_seq.append(("E", _r264_x.context_expr, False, _r264_z))
                        if _r264_x.optional_vars is not None:
                            _r264_seq.append(("T", _r264_x.optional_vars))
                    _r264_seq += ([("xpush", _r264_W)]
                                  + [("S", _r264_x) for _r264_x in _r264_s.body]
                                  + [("xpop",), ("link", _r264_X), ("setcur", _r264_X)])
                elif isinstance(_r264_s, _A264.Try) or type(_r264_s).__name__ == "TryStar":
                    _r264_nodes.extend([[None, [], []], [None, [], []], [None, [], []]])
                    _r264_H, _r264_F, _r264_N = (len(_r264_nodes) - 3, len(_r264_nodes) - 2,
                                                 len(_r264_nodes) - 1)
                    _r264_fin = bool(_r264_s.finalbody)
                    if _r264_s.handlers:
                        if _r264_fin:
                            _r264_nodes[_r264_H][1].append(_r264_F)
                        elif _r264_outer is not None:
                            _r264_nodes[_r264_H][1].append(_r264_outer)
                    _r264_seq = []
                    if _r264_s.handlers or _r264_fin:
                        _r264_seq.append(("xpush", _r264_H if _r264_s.handlers else _r264_F))
                    _r264_seq += [("S", _r264_x) for _r264_x in _r264_s.body]
                    if _r264_s.handlers or _r264_fin:
                        _r264_seq.append(("xpop",))
                    if _r264_fin:
                        _r264_seq.append(("xpush", _r264_F))
                    _r264_seq += [("S", _r264_x) for _r264_x in _r264_s.orelse]
                    if _r264_fin:
                        _r264_seq.append(("xpop",))
                    _r264_seq.append(("link", _r264_N))
                    for _r264_h in _r264_s.handlers:
                        if _r264_fin:
                            _r264_seq.append(("xpush", _r264_F))
                        _r264_seq += [("newfrom", _r264_H), ("E", _r264_h.type, False, _r264_z)]
                        if _r264_h.name:
                            _r264_seq.append(("op", ("def", _r264_h.name)))
                        _r264_seq += [("S", _r264_x) for _r264_x in _r264_h.body]
                        if _r264_h.name:
                            # `except E as e:` DELETES `e` when the handler ends.
                            _r264_seq.append(("op", ("undef", _r264_h.name)))
                        _r264_seq.append(("link", _r264_N))
                        if _r264_fin:
                            _r264_seq.append(("xpop",))
                    if _r264_fin:
                        _r264_seq += ([("setcur", _r264_F)]
                                      + [("S", _r264_x) for _r264_x in _r264_s.finalbody]
                                      + ([("link", _r264_outer)]
                                         if _r264_outer is not None else [])
                                      + [("setcur", _r264_N)]
                                      + [("S", _r264_x) for _r264_x in _r264_s.finalbody])
                    else:
                        _r264_seq.append(("setcur", _r264_N))
                elif type(_r264_s).__name__ == "Match":
                    _r264_nodes.extend([[None, [], []], [None, [], []]])
                    _r264_X, _r264_P = len(_r264_nodes) - 2, len(_r264_nodes) - 1
                    _r264_seq = [("E", _r264_s.subject, False, _r264_z), ("link", _r264_P)]
                    for _r264_cs in _r264_s.cases:
                        _r264_nodes.append([None, [], []])
                        _r264_P2 = len(_r264_nodes) - 1
                        if not (_r264_cs.guard is None
                                and isinstance(_r264_cs.pattern, _A264.MatchAs)
                                and _r264_cs.pattern.pattern is None):
                            _r264_nodes[_r264_P][1].append(_r264_P2)
                        _r264_seq += ([("newfrom", _r264_P), ("P", _r264_cs.pattern),
                                       ("E", _r264_cs.guard, False, _r264_z)]
                                      + [("S", _r264_x) for _r264_x in _r264_cs.body]
                                      + [("link", _r264_X)])
                        _r264_P = _r264_P2
                    _r264_nodes[_r264_P][1].append(_r264_X)
                    _r264_seq.append(("setcur", _r264_X))
                elif type(_r264_s).__name__ == "TypeAlias":
                    _r264_seq = [("T", _r264_s.name)]
            if _r264_seq:
                _r264_tk.extend(reversed(_r264_seq))
        # ---- 3. MUST-ASSIGN dataflow: IN = intersection over predecessors, TOP = None ----
        _r264_in = [None] * len(_r264_nodes)
        _r264_in[0] = frozenset(_r264_params)
        _r264_wl = [0]
        while _r264_wl:
            _r264_k = _r264_wl.pop()
            _r264_st = _r264_in[_r264_k]
            _r264_op = _r264_nodes[_r264_k][0]
            _r264_out = _r264_st
            if _r264_op is not None and _r264_op[0] == "def":
                _r264_out = _r264_st | {_r264_op[1]}
            elif _r264_op is not None and _r264_op[0] in ("del", "undef"):
                _r264_out = _r264_st - {_r264_op[1]}
            for _r264_sx, _r264_val in ([(_r264_x, _r264_out) for _r264_x in _r264_nodes[_r264_k][1]]
                                        + [(_r264_x, _r264_st) for _r264_x in _r264_nodes[_r264_k][2]]):
                _r264_old = _r264_in[_r264_sx]
                _r264_new = _r264_val if _r264_old is None else (_r264_old & _r264_val)
                if _r264_new != _r264_old:
                    _r264_in[_r264_sx] = _r264_new
                    _r264_wl.append(_r264_sx)
        for _r264_k, _r264_nd in enumerate(_r264_nodes):
            if (_r264_nd[0] is not None and _r264_nd[0][0] in ("use", "del")
                    and _r264_in[_r264_k] is not None and _r264_nd[0][1] in _r264_locals
                    and _r264_nd[0][1] not in _r264_in[_r264_k]):
                _r264_bad.append((_r264_fn.name, _r264_nd[0][2], _r264_nd[0][1],
                                  _r264_nd[0][0]))
    if _r264_bad:
        _r264_bad.sort(key=lambda _r264_b: _r264_b[1])
        _r264_fname, _r264_line, _r264_name, _r264_kind = _r264_bad[0]
        from errors import PyCSLSemanticError as _PyCSLSemErr264
        raise _PyCSLSemErr264(
            f"{args.file} (line {_r264_line}): function `{_r264_fname}` "
            f"{'reads' if _r264_kind == 'use' else 'deletes'} the local `{_r264_name}`, "
            f"which is not definitely assigned on every path that reaches it. Python makes "
            f"a name LOCAL to the whole function as soon as the function binds it anywhere "
            f"(assignment, augmented assignment, `for`/`with`/`except` target, walrus, "
            f"import, `del`), so this access raises `UnboundLocalError` on the path where "
            f"no binding happened — and a module global of the same name is NOT consulted. "
            f"PyCSL used to model the read as the declaration default 0 and prove contracts "
            f"of a program that raises (route #264). Bind `{_r264_name}` on every path "
            f"before this point (initialise it before the branch, loop or `try`). If the "
            f"module-level variable is meant and the function only READS it, declare "
            f"`global {_r264_name}`; a WRITE through `global` is refused separately in the "
            f"sequential memory model.",
            filename=args.file, line=_r264_line or 0,
            stage="ir-semantic", code="PYCSL-SEM-UNBOUND-LOCAL")

    # (#49) ROUTE #265 — `case True:` / `case False:` MATCH BY IDENTITY, NOT EQUALITY.
    #
    # PEP 634: the singleton literal patterns `True`, `False` and `None` compare with `is`.
    # `Module5_IREmitter._match_pattern_to_ir` turned `MatchSingleton(True)` into a VALUE
    # pattern on the int-encoded `bool`, so Module 6 emitted `if (n = 1)` and
    # `x = 1; match x: case True: return 1` PROVED `\result == 1` where CPython returns 0
    # (`1 is True` is False) — route #90's `is True` defect through the match path.
    # MEASURED at 283d1033: witnesses-r265/m09 and m10, a guarded arm
    # (`case False if n == 0`) and an or-pattern (`case 5 | True`) all PROVED a
    # falsehood. `case None` is NOT affected — it lowers to the opaque `pycsl_none`
    # (routes #40/#44/#50) and the same probes fail there.
    # THE RULE IS ROUTE #42's WHITELIST, reused: a `True`/`False` pattern is admitted only
    # where the matched value is a Python `bool` BY CONSTRUCTION — a bool literal, a
    # comparison/membership result, or a `not` — and only as the subject itself (a
    # top-level pattern or a top-level or-pattern alternative), never a sub-pattern of a
    # sequence/class pattern. An ANNOTATION is not a fact (route #90), so a `bool`-typed
    # name is refused. `case 1:` against a True subject is a VALUE pattern and stays
    # equality, as PEP 634 says. CENSUS: ZERO `case True/False/None` in either corpus, the
    # mirror, `src/pycsl_lib` and `src/pycsl`, so the refusal costs nothing that exists.
    for _r265_n in _A264.walk(unified_ast):
        if type(_r265_n).__name__ != "Match":
            continue
        _r265_subj = _r265_n.subject
        _r265_ok = (
            (isinstance(_r265_subj, _A264.Constant) and type(_r265_subj.value) is bool)
            or isinstance(_r265_subj, _A264.Compare)
            or (isinstance(_r265_subj, _A264.UnaryOp)
                and isinstance(_r265_subj.op, _A264.Not)))
        for _r265_cs in _r265_n.cases:
            _r265_top = ([_r265_cs.pattern] if not isinstance(_r265_cs.pattern, _A264.MatchOr)
                         else list(_r265_cs.pattern.patterns))
            for _r265_m in _A264.walk(_r265_cs.pattern):
                if (isinstance(_r265_m, _A264.MatchSingleton)
                        and type(_r265_m.value) is bool
                        and not (_r265_ok and any(_r265_m is _r265_p for _r265_p in _r265_top))):
                    from errors import PyCSLSemanticError as _PyCSLSemErr265
                    raise _PyCSLSemErr265(
                        f"{args.file} (line {getattr(_r265_m, 'lineno', 0)}): "
                        f"`case {_r265_m.value}:` is an IDENTITY test (PEP 634 matches the "
                        f"singleton literals True/False/None with `is`), and it is refused "
                        f"unless the matched value is a Python `bool` BY CONSTRUCTION (a "
                        f"bool literal, a comparison or a `not`), as route #42 refuses "
                        f"`X is True`. PyCSL int-encodes `bool`, so the model decided the "
                        f"arm as VALUE equality: measured, `x = 1; match x: case True: "
                        f"return 1` proved `\\result == 1` where Python returns 0, because "
                        f"`1 is True` is False (route #265). Write `case 1:` / `case 0:` for "
                        f"VALUE equality, or test the value with `if`.",
                        filename=args.file, line=getattr(_r265_m, "lineno", 0) or 0,
                        stage="ir-semantic", code="PYCSL-SEM-MATCH-BOOL-SINGLETON")

    # [Module 6] WhyML Transpilation
    # C2c: lazy import — the core backend is only loaded when we actually transpile,
    # keeping the front-end import path free of the core.
    from Module6_WhyMLTranspiler import Module6_WhyMLTranspiler
    transpiler = Module6_WhyMLTranspiler(
        json_ir, memory_model=memory_model,
        strict_no_exception_propagation=getattr(args, "strict_no_exception_propagation", False),
        strict_hash_eq_consistency=getattr(args, "strict_hash_eq_consistency", False),
        check_behavioral_subtyping=getattr(args, "check_behavioral_subtyping", False),
    )
    # ROUTE #250 — opt-in drop of the FLOAT-FINITE assumption (read by the float
    # comparison lowering in `module6_whyml/expressions.py::_handle_binop`).
    transpiler.strict_float_finite = bool(getattr(args, "strict_float_finite", False))
    _mlw = transpiler.transpile()

    # ROUTE #30 (relaunch #45) — REFUSE an UNINTERPRETED `match` pattern.
    #
    #   `module6_whyml/expressions.py::_match_pattern_cond` used to end in a bare
    #   `return "true"` for every pattern kind it did not recognize, and
    #   `Module5_IREmitter._py_pattern_to_ir` emits SEVEN kinds (`Value`,
    #   `Wildcard`, `Capture`, `Or`, `Sequence`, `Constructor`, `Unknown`). So an
    #   arm whose pattern was not interpreted got an UNCONDITIONALLY TRUE
    #   condition and was taken in the model whatever the subject was. MEASURED in
    #   the DEFAULT hoare model with no flags: `match x: case [1, 2]: return 1 /
    #   case _: return 2` under `#@ requires x == 5` PROVED `\result == 1` while
    #   Python returns 2, from the emission `if true then 1 else 2`.
    #   Witness 1011.
    #
    #   A SECOND MECHANISM, same route: a match with any `Constructor` arm takes
    #   the NATIVE Why3 match path, and `_render_match_pattern` wrote the
    #   constructor name verbatim. Why3 reads a lowercase identifier that is not a
    #   known constructor as a fresh VARIABLE BINDER — an irrefutable catch-all —
    #   so `case str():` emitted `match x with | str -> 1 | _ -> 2` and proved the
    #   same false contract. Witness 1012. Its own fall-through, a bare `_`, was
    #   the third instance of the identical mistake.
    #
    #   `false` / `_`-with-a-guard IS NOT THE FIX. Refusing the arm is unsound in
    #   the other direction: on a subject the pattern really does match, the model
    #   takes a LATER arm and the same false-contract proof returns with the arms
    #   swapped. The condition for an uninterpreted pattern is UNKNOWN, and a
    #   boolean has no room for that, so the only sound answer is to REFUSE.
    #
    #   WHY THE MARKER RATHER THAN A `raise` AT THE SITE. Both handlers are
    #   `\trusted` mirror stubs; a `raise` in their live bodies moves
    #   `check-trusted-raises-honesty` (SILENT 68 -> 71), because an emitted `val`
    #   with no `raises` tells Why3 the call has ONE exit path — and declaring
    #   `#@ raises` on a stub is a caller-wide cascade (the 32-method fixpoint
    #   noted in `Module2_Parser._err`). `_run_pipeline` already raises and is
    #   already in that plane's population, so the refusal costs the trust surface
    #   nothing. The marker is ALSO an unbound Why3 symbol, so an emission that
    #   escaped this check is rejected by the type-checker instead of proved —
    #   defence in depth BY CONSTRUCTION, not the accidental fail-closure that
    #   route #29 turned out to be relying on.
    # ROUTE #38 (relaunch #45) — REFUSE a `with` over a USER-DEFINED context manager.
    #
    #   The WHOLE `with` protocol is absent from the model: neither `__enter__` nor
    #   `__exit__` is called, and Module 5 does not even carry the statement into the
    #   IR (the `with` body is inlined and the header disappears — a `with c: pass`
    #   arrives as a bare `Pass`). MEASURED in the default hoare model, no flags:
    #
    #       class CM:
    #           def __init__(self): self.n = 0
    #           def __enter__(self): return 0
    #           def __exit__(self, a, b, c): self.n = 5; return 0
    #       c = CM()
    #       with c: pass
    #       return c.n          #@ ensures \result == 0   -> PROVED. Python gives 5.
    #
    #   The emission is `let c = { n = 0 } in (); c.n`. Witness
    #   `pycsl-reference/1030`.
    #
    #   THE NEIGHBOURING RATCHET HAS BEEN COUNTING HALF OF THIS FOR TWO WINDOWS:
    #   `check-dropped-mutation`'s CTXBIND = 51 records "`with ... as X` — the binding
    #   is not read". The binding is the visible half; the PROTOCOL CALLS are the
    #   half that carries the state change, and nothing counted or established those.
    #
    #   THE REFUSAL IS NARROW BY NECESSITY, not by taste. The mirror uses `with` in 52
    #   places, and every one of them is a `@contextmanager` GENERATOR (`self.block()`,
    #   `self.delimit()`) or a builtin (`open`, `tempfile`, `os`) — measured by an AST
    #   census. A generator CM has no `__enter__`/`__exit__` METHODS to look for, so
    #   keying the refusal on a class that DEFINES them leaves all 52 alone. (The
    #   generator case is NOT thereby sound — `yield-erasure`'s ratchet of 2 records
    #   that `_unparser.block` drops its indent/dedent — but it is unobservable while
    #   the emitted `_unparser` record is empty, which is exactly the precondition
    #   relaunch #43 wrote down for converting `_Unparser.__init__`. Refusing it here
    #   would break the mirror outright and buy nothing today.)
    # ROUTE #43 (relaunch #46) — REFUSE A COMPLEX LITERAL. It was the integer zero.
    #
    #   `_py_expr_constant` lowers `isinstance(expr.value, complex)` to
    #   `{"type": "Number", "value": int(expr.value.real)}` — the imaginary part is
    #   DISCARDED and the real part is TRUNCATED TO AN INT. There is no complex model
    #   anywhere in the pipeline, so what the model gets is an ordinary integer that
    #   every comparison then decides on. MEASURED in the default hoare model, no
    #   flags, with Python run to confirm each right-hand column:
    #
    #     x = 3j;     if x == 0: return 7   ->  `\result == 7` PROVED. `3j == 0` is False.
    #     x = 1 + 2j; if x == 1: return 7   ->  PROVED.  `(1+2j) == 1` is False.
    #     x = 3j;     if x:      return 7   ->  `\result == 0` PROVED. `bool(3j)` is True.
    #
    #   Witnesses 1050-1052. THIS IS THE WINDOW'S GENERAL SHAPE A FOURTH TIME: a Python
    #   value the model cannot represent, lowered to an INTEGER LITERAL, is not merely
    #   lost — it is DECIDABLE, and decided wrongly.
    #
    #   REFUSED RATHER THAN MADE OPAQUE, and the reason is a measurement: the whole
    #   tree contains exactly ONE complex literal (`python-reference/0044`, an
    #   `assert`-only coverage driver, now `pycsl-expected: FAIL`), so opacity would
    #   buy no program anything, while a refusal says the true thing — PyCSL models no
    #   complex arithmetic at all, and `c.real`/`c.imag` are not modelled either.
    #   Placed HERE for the choke-point reason routes #29/#30/#37/#38 were: the
    #   producer `_py_expr_constant` is a CONVERTED mirror method, so a raise in its
    #   body would owe a mirror body sync and a 2109-goal re-proof to state a refusal
    #   the pipeline can make once, before emission, and `_run_pipeline` already
    #   raises and is already in `check-trusted-raises-honesty`'s population.
    if unified_ast is not None:
        from frontend import pure_ast as _pa43
        for _n43 in _pa43.walk(unified_ast):
            if (_n43.__class__.__name__ == "Constant"
                    and isinstance(getattr(_n43, "value", None), complex)):
                from errors import PyCSLSemanticError as _PyCSLSemErr43
                raise _PyCSLSemErr43(
                    "a COMPLEX literal (%r) has no model (ROUTE #43): "
                    "`_py_expr_constant` lowers it to `int(value.real)`, so the "
                    "imaginary part is DISCARDED, the real part is TRUNCATED, and the "
                    "result is an ordinary integer the model then DECIDES on — "
                    "measured, `x = 3j; if x == 0: return 7` proved `\\result == 7` "
                    "while Python's `3j == 0` is False, and `if x:` proved the branch "
                    "NOT taken while `bool(3j)` is True. PyCSL models no complex "
                    "arithmetic; use two reals."
                    % (getattr(_n43, "value", None),),
                    stage="whyml-emit", code="PYCSL-R43-COMPLEX-LITERAL-ERASED")

    # ROUTE #39 (relaunch #46) — ROUTE #38's REFUSAL WAS A BLACKLIST OVER AN
    # UNDER-APPROXIMATE CLASS RESOLUTION, AND TWO ORDINARY SHAPES WALKED PAST IT.
    #
    #   #38 keyed on "the `with` context expression is a Call to a class that
    #   DEFINES `__enter__`/`__exit__`, or a Name bound by a plain `Assign` to
    #   such a call". BOTH halves of that resolution are partial, and each gap is
    #   a full re-run of #38's own exploit in the default hoare model, no flags:
    #
    #     (a) AN ANNOTATED ASSIGNMENT.  `c: CM = CM()` is an `AnnAssign`, not an
    #         `Assign`, so the binding census never saw it.  MEASURED:
    #             c: CM = CM()
    #             with c: pass
    #             return c.n        #@ ensures \result == 0  -> PROVED. Python: 5.
    #         Emission: `let c = { n = 0 } in (); c.n`.  Witness 1033.
    #     (b) AN INHERITED PROTOCOL.  `class CM(Base)` where `Base` — not `CM` —
    #         defines `__enter__`/`__exit__`.  The class scan only looked at each
    #         ClassDef's own body, so `CM` was never in the set.  Same emission,
    #         same false proof.  Witness 1035.
    #
    #   THE FIX IS A WHITELIST, NOT A WIDER BLACKLIST, because the enumeration of
    #   ways to name a value is open-ended and the previous shape had already been
    #   wrong twice.  ONCE THE FILE DEFINES A CONTEXT-MANAGER CLASS AT ALL, every
    #   `with` in it must be positively recognized or it is refused:
    #
    #     W1  a call to an in-file `@contextmanager` GENERATOR, or to an in-file
    #         function whose returns are all such calls (`delimit_if` returns
    #         `self.delimit(...)` or `_nullcontext()`; `require_parens` returns
    #         `delimit_if(...)`).  This is a FIXPOINT, not a one-level test.
    #         The generator case is NOT thereby sound — `check-yield-erasure`'s
    #         ratchet of 2 records that `_unparser.block` drops its indent/dedent
    #         — it is the pre-existing, ratcheted status quo #38 deliberately left
    #         alone, and narrowing it here would break 52 mirror sites and buy
    #         nothing today.
    #     W2  a call to one of a small set of stdlib context managers whose effect
    #         is entirely outside the value model (`open`, `tempfile.*`, `os.fdopen`,
    #         `io.StringIO`, an executor, `nullcontext`).
    #
    #   A file that defines no `__enter__`/`__exit__` is untouched, so all 33
    #   `with <lock>:` critical sections in `pycsl-reference` and the whole mirror
    #   keep working exactly as before.  CENSUS behind that claim: mirror 52 `with`
    #   items, every one W1 or W2; pycsl-reference 33 bare `Name(lock_*)` plus the
    #   three route-#20/#38 witnesses; python-reference 3, all already
    #   `pycsl-expected: FAIL`; `pycsl_lib` 1, in a file with no CM class.
    if unified_ast is not None:
        from frontend import pure_ast as _pa38

        # `_seg38(e)` — the last segment of a base / decorator / callee expression —
        # is written INLINE at each of its four uses rather than as a helper `def`.
        # A new live function has no mirror counterpart, and
        # `bin/check-mirror-coverage.py` would count it: 550 -> 551, RATCHET BROKEN.
        # A refusal is not worth weakening a plane for. The idiom below is, verbatim:
        #     _x = <expr>
        #     while _x is not None and _x.__class__.__name__ == "Call":
        #         _x = getattr(_x, "func", None)
        #     _seg = ((getattr(_x, "id", None) or getattr(_x, "attr", None))
        #             if _x is not None else None)
        # (a Name carries `id`, an Attribute carries `attr`, anything else neither.)

        # (1) classes that define the protocol, CLOSED UNDER INHERITANCE (gap (b)).
        _bases38 = {}
        _cm38 = set()
        for _n38 in _pa38.walk(unified_ast):
            if _n38.__class__.__name__ != "ClassDef":
                continue
            _cn38 = getattr(_n38, "name", "")
            _bl38 = []
            for _b38 in getattr(_n38, "bases", []) or []:
                _x38 = _b38
                while _x38 is not None and _x38.__class__.__name__ == "Call":
                    _x38 = getattr(_x38, "func", None)
                _s38 = ((getattr(_x38, "id", None) or getattr(_x38, "attr", None))
                        if _x38 is not None else None)
                if _s38:
                    _bl38.append(_s38)
            _bases38[_cn38] = _bl38
            for _b38 in getattr(_n38, "body", []) or []:
                if (_b38.__class__.__name__ in ("FunctionDef", "AsyncFunctionDef")
                        and getattr(_b38, "name", "") in ("__enter__", "__exit__",
                                                            "__aenter__", "__aexit__")):
                    _cm38.add(_cn38)
        _grew38 = True
        while _grew38:
            _grew38 = False
            for _cn38, _bs38 in _bases38.items():
                if _cn38 not in _cm38 and any(_b38 in _cm38 for _b38 in _bs38):
                    _cm38.add(_cn38)
                    _grew38 = True

        if _cm38:
            # (2) W1 — the CM-PRODUCING in-file functions, as a fixpoint.
            _funs38 = {}
            _cmfun38 = {"nullcontext", "_nullcontext"} - _cm38
            for _n38 in _pa38.walk(unified_ast):
                if _n38.__class__.__name__ not in ("FunctionDef", "AsyncFunctionDef"):
                    continue
                _fn38 = getattr(_n38, "name", "")
                _funs38.setdefault(_fn38, []).append(_n38)
                for _d38 in getattr(_n38, "decorator_list", []) or []:
                    _x38 = _d38
                    while _x38 is not None and _x38.__class__.__name__ == "Call":
                        _x38 = getattr(_x38, "func", None)
                    _dn38 = (((getattr(_x38, "id", None) or getattr(_x38, "attr", None))
                              if _x38 is not None else None) or "")
                    if _dn38.lower().endswith("contextmanager") and _fn38 not in _cm38:
                        _cmfun38.add(_fn38)
            _grew38 = True
            while _grew38:
                _grew38 = False
                for _fn38, _nodes38 in _funs38.items():
                    if _fn38 in _cmfun38:
                        continue
                    _rets38 = [_r38 for _nd38 in _nodes38
                               for _r38 in _pa38.walk(_nd38)
                               if _r38.__class__.__name__ == "Return"
                               and getattr(_r38, "value", None) is not None]
                    _allcm38 = bool(_rets38)
                    for _r38 in _rets38:
                        if _r38.value.__class__.__name__ != "Call":
                            _allcm38 = False
                            break
                        _x38 = _r38.value
                        while _x38 is not None and _x38.__class__.__name__ == "Call":
                            _x38 = getattr(_x38, "func", None)
                        _s38 = ((getattr(_x38, "id", None) or getattr(_x38, "attr", None))
                                if _x38 is not None else None)
                        if _s38 not in _cmfun38:
                            _allcm38 = False
                            break
                    if _allcm38 and _fn38 not in _cm38:
                        _cmfun38.add(_fn38)
                        _grew38 = True
            # (3) W2 — stdlib context managers with no value-model footprint.
            _stdcm38 = {
                "open", "NamedTemporaryFile", "TemporaryDirectory", "TemporaryFile",
                "fdopen", "StringIO", "BytesIO", "ThreadPoolExecutor",
                "ProcessPoolExecutor", "suppress", "redirect_stdout", "redirect_stderr",
                "closing",
            }
            for _n38 in _pa38.walk(unified_ast):
                if _n38.__class__.__name__ not in ("With", "AsyncWith"):
                    continue
                for _it38 in getattr(_n38, "items", []) or []:
                    _ce38 = getattr(_it38, "context_expr", None)
                    if _ce38 is None:
                        continue
                    _ok38 = False
                    if _ce38.__class__.__name__ == "Call":
                        _x38 = _ce38
                        while _x38 is not None and _x38.__class__.__name__ == "Call":
                            _x38 = getattr(_x38, "func", None)
                        _cal38 = ((getattr(_x38, "id", None) or getattr(_x38, "attr", None))
                                  if _x38 is not None else None)
                        # A name that IS a context-manager class is never allow-listed,
                        # whatever else carries that name. Without this, a class called
                        # `closing` or `suppress` that defines `__enter__` would be waved
                        # through by the W2 stdlib list purely because the list matches on
                        # the LAST SEGMENT — the allowlist would be laundering the exact
                        # thing it is meant to exclude.
                        _ok38 = (_cal38 not in _cm38
                                 and ((_cal38 in _cmfun38) or (_cal38 in _stdcm38)))
                    if _ok38:
                        continue
                    from errors import PyCSLSemanticError as _PyCSLSemErr38
                    raise _PyCSLSemErr38(
                        "a `with` statement in a file that defines a context-manager "
                        "class (%s) uses a context expression this build cannot "
                        "positively recognize as modelled (ROUTE #38/#39): the "
                        "context-manager PROTOCOL is not modelled at all — neither "
                        "`__enter__` nor `__exit__` is called, the statement does not "
                        "even reach the IR, and a contract that is FALSE of the "
                        "program becomes provable (measured: an `__exit__` that writes "
                        "`self.n` left the field at its initial value in the model, "
                        "under a plain `c = CM()`, an annotated `c: CM = CM()` and an "
                        "INHERITED protocol alike). Call the setup/teardown explicitly "
                        "around the block."
                        % ", ".join(sorted(_cm38)),
                        stage="whyml-emit", code="PYCSL-R38-CONTEXT-MANAGER-DROPPED")

    # (#49) ROUTE #257 — ROUTE #38/#39's WHITELIST ONLY RAN IN A FILE THAT DEFINES A
    # CONTEXT-MANAGER CLASS, SO EVERY CM THE FILE DOES NOT DEFINE WALKED PAST IT.
    #
    #   `Module5_IREmitter._py_stmt_with` lowers a bare `with <cm>:` to its BODY ALONE:
    #   the context expression is never evaluated and neither `__enter__` nor `__exit__`
    #   (nor a generator CM's code before/after its `yield`) is modelled. #38/#39 refused
    #   that only when `_cm38` was non-empty — i.e. only for a protocol class DEFINED IN
    #   THE SAME FILE. MEASURED at 49f6a35d, default hoare model, no flags, each claim
    #   FALSE of CPython and each "All contracts formally proven":
    #     - `from cmlib import Counter; c = Counter(); with c: pass; return c.n`
    #       (`__enter__` writes `self.n`)          `\result == 0` PROVED, Python 1;
    #     - an IN-FILE `@contextmanager` METHOD writing `self.n`, `with b.bump():`;
    #     - the same through an imported class / an imported `@contextmanager` function /
    #       an in-file generator writing its ARGUMENT / a plain call returning the CM /
    #       a multi-item `with c, d:` (witnesses 2560-2566).
    #
    #   THE REPAIR IS FAIL-CLOSED AND FILE-INDEPENDENT. Outside a `\trusted`/`\abstract`
    #   function (whose body is never lowered — the same exemption #20's `with ... as`
    #   refusal makes in `functions.py`), every BARE `with` item must be POSITIVELY shown
    #   inert in the model, or the program is refused. `as` items are left to #20's
    #   refusal (unchanged message); `async with` is refused outright. INERT means:
    #
    #     (L) a NAME bound ONLY by `<name> = threading.Lock()` / `threading.RLock()`
    #         (with `import threading`): a lock's enter/exit is acquire/release, which
    #         touches no modelled value — the concurrency layer's `#@ critical` /
    #         `#@ acquires` model is attached to the SAME statement by the weaver.
    #     (G) a CALL to an in-file PRODUCER P — a module-level `def P` named once and
    #         never rebound, or `self.P` inside a method of class K that defines P once
    #         and no in-file subclass of K overrides — where P is in the greatest set
    #         INERT such that, for every member:
    #           * it is `@contextmanager` (resolved through `from contextlib import
    #             contextmanager [as X]` / `contextlib.contextmanager`) with EXACTLY ONE
    #             `yield`, a top-level statement (it yields exactly once), or its body
    #             is exactly `return <call>` to an INERT producer or `contextlib`'s
    #             `nullcontext()` (the #39 W1 fixpoint, now required to be inert);
    #           * its body has no `global`/`nonlocal`/`try`/`with`/`raise`/`del`/
    #             `assert`/loop/comprehension/nested def/`await`/`yield from`/import;
    #             it calls only `len`/`isinstance` among builtins; stores only to LOCAL names
    #             or to `self.<attr>` of a K whose model record has NO FIELDS (the IR
    #             `type_decls` entry, read below; absent = not empty); every call is
    #             to an INERT producer, or to an in-file def whose frame is exactly
    #             `assigns \nothing` with no `raises`, and is a module-level name or a
    #             `self.` method resolved as above;
    #           OR it is `\trusted` with every `assigns` target `\nothing` or
    #             `self.<attr>`, as a method of such a FIELDLESS K called on `self`.
    #         The call's ARGUMENTS must satisfy the same call/store rule (the header
    #         is not evaluated in the model either).
    #
    #   WHAT (G) STILL TRUSTS, stated: a `\trusted` producer's REVIEWED frame is taken to
    #   cover the protocol of the CM it returns (the mirror's `_Unparser.delimit_if`,
    #   `assigns self._source` on a record with no fields). The REMAINING generator
    #   erasure on a fieldless record is `check-yield-erasure`'s ratcheted status quo,
    #   unobservable while the record is empty — the precondition #38 recorded.
    #
    #   CENSUS before the change (Modules 1-3 over corpus + mirror + `pycsl_lib`, 147
    #   items): 49 bare lock NAMES in 32 `pycsl-reference` files, every one `lock_X =
    #   threading.Lock()` with `import threading` -> (L); 41 mirror items
    #   (`self.block/delimit/require_parens/delimit_if` in `pure_ast._Unparser`, record
    #   `{ }`) -> (G); `1031`'s `blk()` (body `yield`) -> (G); 11 items inside
    #   `\trusted` mirror functions -> exempt; everything else was already refused.
    #   CHOKE POINT: `_run_pipeline`'s mirror twin is `\trusted` (routes #38/#39), and no
    #   helper `def` is added (mirror-coverage ratchet).
    if unified_ast is not None:
        from frontend import pure_ast as _pa257
        _ir257 = _json.loads(json_ir)
        _empty257 = {
            _td["name"] for _td in (_ir257.get("type_decls") or [])
            if isinstance(_td, dict) and isinstance(_td.get("name"), str)
            and isinstance(_td.get("fields"), list) and not _td.get("fields")}
        # parent links, iteratively (no nested def)
        _par257 = {}
        _st257 = [unified_ast]
        while _st257:
            _n257 = _st257.pop()
            for _c257 in _pa257.iter_child_nodes(_n257):
                _par257[id(_c257)] = _n257
                _st257.append(_c257)
        _withs257 = [_n for _n in _pa257.walk(unified_ast)
                     if _n.__class__.__name__ in ("With", "AsyncWith")]
        _todo257 = []
        for _w257 in _withs257:
            # enclosing function chain; exempt under any \trusted / \abstract ancestor
            _p257 = _par257.get(id(_w257))
            _fn257 = None
            _ex257 = False
            while _p257 is not None:
                if _p257.__class__.__name__ in ("FunctionDef", "AsyncFunctionDef"):
                    if _fn257 is None:
                        _fn257 = _p257
                    if getattr(_p257, "csl_trusted", False) or getattr(_p257, "csl_abstract", False):
                        _ex257 = True
                _p257 = _par257.get(id(_p257))
            if not _ex257:
                _todo257.append((_w257, _fn257))
        if _todo257:
            _mod257 = getattr(unified_ast, "body", []) or []
            # contextlib resolution
            _cmdeco257, _nullc257, _ctxlib257, _thr257 = set(), set(), set(), set()
            for _n257 in _pa257.walk(unified_ast):
                _k257 = _n257.__class__.__name__
                if _k257 == "ImportFrom" and getattr(_n257, "module", None) == "contextlib":
                    for _a257 in _n257.names:
                        if _a257.name == "contextmanager":
                            _cmdeco257.add(_a257.asname or _a257.name)
                        if _a257.name == "nullcontext":
                            _nullc257.add(_a257.asname or _a257.name)
                elif _k257 == "Import":
                    for _a257 in _n257.names:
                        if _a257.name == "contextlib":
                            _ctxlib257.add(_a257.asname or _a257.name)
                        if _a257.name == "threading" and not _a257.asname:
                            _thr257.add("threading")
            # every binding of every name (to tell "bound once, never rebound")
            _binds257 = {}
            for _n257 in _pa257.walk(unified_ast):
                _k257 = _n257.__class__.__name__
                _nm257 = None
                if _k257 == "Name" and getattr(_n257, "ctx", None).__class__.__name__ in ("Store", "Del"):
                    _nm257 = _n257.id
                elif _k257 in ("FunctionDef", "AsyncFunctionDef", "ClassDef"):
                    _nm257 = _n257.name
                elif _k257 == "arg":
                    _nm257 = _n257.arg
                elif _k257 == "alias":
                    _nm257 = (_n257.asname or _n257.name).split(".")[0]
                elif _k257 in ("ExceptHandler", "MatchAs", "MatchStar"):
                    _nm257 = getattr(_n257, "name", None)
                elif _k257 == "MatchMapping":
                    _nm257 = getattr(_n257, "rest", None)
                elif _k257 in ("Global", "Nonlocal"):
                    for _gn257 in _n257.names:
                        _binds257.setdefault(_gn257, []).append(_n257)
                if _nm257:
                    _binds257.setdefault(_nm257, []).append(_n257)
            # classes: methods, bases (for the override check)
            _cls257, _cbases257 = {}, {}
            for _n257 in _pa257.walk(unified_ast):
                if _n257.__class__.__name__ == "ClassDef":
                    _ms257 = {}
                    for _b257 in _n257.body:
                        if _b257.__class__.__name__ in ("FunctionDef", "AsyncFunctionDef"):
                            _ms257.setdefault(_b257.name, []).append(_b257)
                    _cls257[_n257.name] = _ms257
                    _cbases257[_n257.name] = [getattr(_x, "id", None) or getattr(_x, "attr", None)
                                              for _x in (_n257.bases or [])]
            # an import-bound name counts only if the import is its ONLY binding
            # (`contextmanager = my_deco`, `threading = shim` must not pass)
            for _set257 in (_cmdeco257, _nullc257, _ctxlib257, _thr257):
                for _nm257 in list(_set257):
                    if not all(_b.__class__.__name__ == "alias"
                               for _b in _binds257.get(_nm257, [])) \
                            or len(_binds257.get(_nm257, [])) != 1:
                        _set257.discard(_nm257)
            _modfn257 = {}
            for _b257 in _mod257:
                if _b257.__class__.__name__ in ("FunctionDef", "AsyncFunctionDef"):
                    _modfn257.setdefault(_b257.name, []).append(_b257)
            # every def that can be RESOLVED: key (class-or-"", name) -> node
            _defs257 = {}
            for _nm257, _ns257 in _modfn257.items():
                if len(_ns257) == 1 and len(_binds257.get(_nm257, [])) == 1:
                    _defs257[("", _nm257)] = _ns257[0]
            for _cn257, _ms257 in _cls257.items():
                for _nm257, _ns257 in _ms257.items():
                    _ovr257 = False
                    for _sc257 in _cls257:
                        _seen257, _q257 = set(), [_sc257]
                        while _q257:
                            _x257 = _q257.pop()
                            if _x257 in _seen257:
                                continue
                            _seen257.add(_x257)
                            _q257.extend(_b for _b in _cbases257.get(_x257, []) if _b)
                        if _sc257 != _cn257 and _cn257 in _seen257 and _nm257 in _cls257[_sc257]:
                            _ovr257 = True
                    if len(_ns257) == 1 and not _ovr257:
                        _defs257[(_cn257, _nm257)] = _ns257[0]
            _owner257 = {id(_v): _k[0] for _k, _v in _defs257.items()}

            # A call's callee key, from inside a def owned by class `own` ("" = module).
            # Written as a loop-free expression at each use site would be unreadable, so
            # it is computed per node into this dict once (no helper def).
            _ckey257 = {}
            for _n257 in _pa257.walk(unified_ast):
                if _n257.__class__.__name__ != "Call":
                    continue
                _f257 = _n257.func
                _k257 = None
                if _f257.__class__.__name__ == "Name":
                    _k257 = ("", _f257.id)
                elif (_f257.__class__.__name__ == "Attribute"
                      and _f257.value.__class__.__name__ == "Name"
                      and _f257.value.id == "self"):
                    # resolve against the class whose method lexically encloses the call
                    _p257 = _par257.get(id(_n257))
                    _meth257 = None
                    while _p257 is not None:
                        if _p257.__class__.__name__ in ("FunctionDef", "AsyncFunctionDef"):
                            _meth257 = _p257
                        if _p257.__class__.__name__ == "ClassDef":
                            break
                        _p257 = _par257.get(id(_p257))
                    if (_p257 is not None and _meth257 is not None
                            and _par257.get(id(_meth257)) is _p257
                            and (_meth257.args.args or [None])[0] is not None
                            and _meth257.args.args[0].arg == "self"):
                        _k257 = (_p257.name, _f257.attr)
                _ckey257[id(_n257)] = _k257

            _isnull257, _pure257 = {}, {}
            for _n257 in _pa257.walk(unified_ast):
                if _n257.__class__.__name__ == "Call":
                    _f257 = _n257.func
                    # the two builtins whose model is pure (`len`, `isinstance` — the
                    # mirror's `delimit_if` conditions), unshadowed
                    _pure257[id(_n257)] = (_f257.__class__.__name__ == "Name"
                                           and _f257.id in ("len", "isinstance")
                                           and _f257.id not in _binds257)
                    _isnull257[id(_n257)] = (
                        (_f257.__class__.__name__ == "Name" and _f257.id in _nullc257)
                        or (_f257.__class__.__name__ == "Attribute"
                            and _f257.attr == "nullcontext"
                            and _f257.value.__class__.__name__ == "Name"
                            and _f257.value.id in _ctxlib257))

            # frame-\nothing, raise-free in-file defs (callable from inert code)
            _quiet257 = set()
            for _k257, _d257 in _defs257.items():
                _as257 = getattr(_d257, "csl_assigns", None) or []
                if (_as257 and all(_t.__class__.__name__ == "Nothing"
                                   for _a in _as257 for _t in (getattr(_a, "targets", None) or [None]))
                        and not (getattr(_d257, "csl_raises", None) or [])
                        and _d257.__class__.__name__ == "FunctionDef"):
                    _quiet257.add(_k257)

            _bad257 = ("Global", "Nonlocal", "Try", "TryStar", "With", "AsyncWith", "Raise",
                       "Delete", "Assert", "FunctionDef", "AsyncFunctionDef", "ClassDef",
                       "Lambda", "Await", "YieldFrom", "AsyncFor", "Import", "ImportFrom",
                       "For", "While", "ListComp", "SetComp", "DictComp", "GeneratorExp")
            # candidate producers and their local verdicts; then the greatest fixpoint
            _inert257 = set()
            _deps257 = {}
            for _k257, _d257 in _defs257.items():
                if _d257.__class__.__name__ != "FunctionDef":
                    continue
                _own257 = _k257[0]
                if getattr(_d257, "csl_abstract", False):
                    continue
                if getattr(_d257, "csl_trusted", False):
                    _as257 = getattr(_d257, "csl_assigns", None) or []
                    _tg257 = [_t for _a in _as257 for _t in (getattr(_a, "targets", None) or [None])]
                    if (_own257 and _own257 in _empty257 and _tg257
                            and all(_t.__class__.__name__ == "Nothing"
                                    or (_t.__class__.__name__ == "FieldAccess"
                                        and getattr(_t, "object", None) == "self")
                                    for _t in _tg257)):
                        _inert257.add(_k257)
                        _deps257[_k257] = set()
                    continue
                _isgen257 = False
                for _dc257 in _d257.decorator_list or []:
                    if ((_dc257.__class__.__name__ == "Name" and _dc257.id in _cmdeco257)
                            or (_dc257.__class__.__name__ == "Attribute"
                                and _dc257.attr == "contextmanager"
                                and _dc257.value.__class__.__name__ == "Name"
                                and _dc257.value.id in _ctxlib257)):
                        _isgen257 = True
                if len(_d257.decorator_list or []) != (1 if _isgen257 else 0):
                    continue
                _ok257 = True
                _dep257 = set()
                _rets257 = 0
                for _n257 in _pa257.walk(_d257):
                    if _n257 is _d257:
                        continue
                    _nk257 = _n257.__class__.__name__
                    if _nk257 in _bad257:
                        _ok257 = False
                        break
                    if _nk257 == "Return" and _n257.value is not None:
                        _rets257 += 1
                        if _isgen257 or _n257.value.__class__.__name__ != "Call":
                            _ok257 = False
                            break
                    if _nk257 in ("Attribute", "Subscript", "Starred") and getattr(_n257, "ctx", None).__class__.__name__ in ("Store", "Del"):
                        if not (_nk257 == "Attribute"
                                and _n257.value.__class__.__name__ == "Name"
                                and _n257.value.id == "self"
                                and _own257 and _own257 in _empty257
                                and _d257.args.args and _d257.args.args[0].arg == "self"):
                            _ok257 = False
                            break
                    if _nk257 == "Call":
                        _ck257 = _ckey257.get(id(_n257))
                        if _isnull257.get(id(_n257)) or _pure257.get(id(_n257)):
                            continue
                        if _ck257 in _quiet257:
                            continue
                        if _ck257 is not None and _ck257 in _defs257:
                            _dep257.add(_ck257)
                            continue
                        _ok257 = False
                        break
                if not _ok257:
                    continue
                if _isgen257:
                    # EXACTLY ONE `yield`, as a TOP-LEVEL statement: the generator then
                    # yields exactly once (no "generator didn't yield" / "didn't stop"
                    # RuntimeError the model would not see)
                    _ys257 = [_n for _n in _pa257.walk(_d257) if _n.__class__.__name__ == "Yield"]
                    if not (len(_ys257) == 1 and any(
                            _b.__class__.__name__ == "Expr" and _b.value is _ys257[0]
                            for _b in _d257.body)):
                        continue
                else:
                    # W1: the body (docstring aside) is EXACTLY `return <call>`, the call
                    # to a producer or `nullcontext()` — no fall-through to an implicit
                    # `None`, and no generator in disguise
                    _bd257 = [_b for _b in _d257.body
                              if not (_b.__class__.__name__ == "Expr"
                                      and _b.value.__class__.__name__ == "Constant"
                                      and isinstance(getattr(_b.value, "value", None), str))]
                    _v257 = (_bd257[0].value if len(_bd257) == 1
                             and _bd257[0].__class__.__name__ == "Return" else None)
                    if not (_v257 is not None and _v257.__class__.__name__ == "Call"
                            and (_isnull257.get(id(_v257))
                                 or _ckey257.get(id(_v257)) in _defs257)):
                        continue
                _inert257.add(_k257)
                _deps257[_k257] = _dep257
            _grew257 = True
            while _grew257:
                _grew257 = False
                for _k257 in list(_inert257):
                    if not _deps257.get(_k257, set()) <= (_inert257 | _quiet257):
                        _inert257.discard(_k257)
                        _grew257 = True
            # (W1 producers must RETURN producers, not merely call quiet defs)
            _grew257 = True
            while _grew257:
                _grew257 = False
                for _k257 in list(_inert257):
                    _d257 = _defs257[_k257]
                    if getattr(_d257, "csl_trusted", False):
                        continue
                    for _n257 in _pa257.walk(_d257):
                        if (_n257.__class__.__name__ == "Return" and _n257.value is not None
                                and not _isnull257.get(id(_n257.value))
                                and _ckey257.get(id(_n257.value)) not in _inert257):
                            _inert257.discard(_k257)
                            _grew257 = True
                            break

            for _w257, _fn257 in _todo257:
                for _it257 in _w257.items:
                    _ce257 = _it257.context_expr
                    if _w257.__class__.__name__ == "With" and _it257.optional_vars is not None:
                        continue   # #20's `with ... as` refusal (functions.py) owns this
                    _why257 = None
                    if _w257.__class__.__name__ == "AsyncWith":
                        _why257 = "an `async with` (no `__aenter__`/`__aexit__` model)"
                    elif _ce257.__class__.__name__ == "Name":
                        _bs257 = _binds257.get(_ce257.id, [])
                        _lk257 = bool(_bs257) and bool(_thr257)
                        for _b257 in _bs257:
                            _a257 = _par257.get(id(_b257))
                            _v257 = getattr(_a257, "value", None)
                            if not (_b257.__class__.__name__ == "Name"
                                    and _a257 is not None
                                    and _a257.__class__.__name__ in ("Assign", "AnnAssign")
                                    and (_a257.targets if _a257.__class__.__name__ == "Assign"
                                         else [_a257.target]) == [_b257]
                                    and _v257 is not None
                                    and _v257.__class__.__name__ == "Call"
                                    and not _v257.args and not _v257.keywords
                                    and _v257.func.__class__.__name__ == "Attribute"
                                    and _v257.func.attr in ("Lock", "RLock")
                                    and _v257.func.value.__class__.__name__ == "Name"
                                    and _v257.func.value.id == "threading"):
                                _lk257 = False
                        if not _lk257:
                            _why257 = ("the name `%s`, which is not provably a `threading.Lock()`"
                                       % _ce257.id)
                    elif _ce257.__class__.__name__ == "Call" and _ckey257.get(id(_ce257)) in _inert257:
                        for _n257 in _pa257.walk(_ce257):
                            if _n257 is _ce257:
                                continue
                            _nk257 = _n257.__class__.__name__
                            if _nk257 in _bad257 or _nk257 in ("NamedExpr", "Yield"):
                                _why257 = "a context-manager call whose arguments are not effect-free"
                                break
                            if _nk257 == "Call" and not (_ckey257.get(id(_n257)) in _quiet257
                                                         or _isnull257.get(id(_n257))
                                                         or _pure257.get(id(_n257))):
                                _why257 = "a context-manager call whose arguments are not effect-free"
                                break
                    else:
                        _why257 = ("a context expression of kind `%s` that is not an in-file "
                                   "context manager proven inert" % _ce257.__class__.__name__)
                    if _why257 is None:
                        continue
                    from errors import PyCSLSemanticError as _PyCSLSemErr257
                    raise _PyCSLSemErr257(
                        "a `with` item (line %s, in %s) uses %s (ROUTE #257): a bare `with` is "
                        "lowered to its BODY ALONE — the context expression is not evaluated "
                        "and neither `__enter__`/`__exit__` nor a `@contextmanager` "
                        "generator's code around its `yield` is modelled — so it is accepted "
                        "only when the context manager is PROVABLY INERT in the model: a name "
                        "bound only by `threading.Lock()`/`RLock()`, or an in-file "
                        "`@contextmanager` producer whose effects all land in a record with no "
                        "fields. Measured: an imported class whose `__enter__` writes "
                        "`self.n`, and an in-file `@contextmanager` method doing the same, "
                        "both proved `\\result == 0` where Python returns 1. Call the "
                        "setup/teardown explicitly around the block as ORDINARY methods "
                        "(an explicit `__enter__()` call does not carry its contract today), "
                        "or guard the block with a module-level `threading.Lock()`."
                        % (getattr(_w257, "lineno", "?"),
                           ("'%s'" % _fn257.name) if _fn257 is not None else "module scope",
                           _why257),
                        stage="whyml-emit", code="PYCSL-R257-CONTEXT-MANAGER-NOT-INERT")



    # (#49) ROUTE #271 — CALLING A GENERATOR FUNCTION RAN ITS BODY EAGERLY IN THE MODEL.
    #
    #   Module 5 has no generator node: `yield <e>` becomes an `UnknownPyExpr` statement
    #   (Module 6: `let _ = (any int) in ()`), so a function containing `yield` is emitted
    #   as an ORDINARY procedure whose body — and contract — run AT THE CALL. Python's
    #   call only BUILDS the generator; nothing in the body runs until it is iterated.
    #   MEASURED at c9d7f157, default hoare model, no flags, each "All contracts formally
    #   proven" and each false of CPython:
    #     - `def bump(self) -> Iterator[int]: self.n = self.n + 1; yield 0` with
    #       `ensures self.n == \old(self.n) + 1`; `c = C(); c.bump(); return c.n` proved
    #       `\result == 1` (CPython 0) — witnesses-r271/h05;
    #     - `def gen() -> int: yield 1; return 3` with `ensures \result == 3`, and
    #       `return gen()` proved `\result == 3` (CPython: a generator object).
    #   THE RULE, fail-closed, for every generator function (a `def` with its OWN
    #   `yield`/`yield from`) whose body is LOWERED (not `\trusted`/`\abstract`, not
    #   nested in one) and that no dedicated generator model recognizes (Module 6's
    #   R-W2b `_walk_dicts` `.values()` walker, which lowers onto a `list pyval`):
    #     (G1) its OWN contract may not carry an `ensures` other than `True`, a
    #          `raises`, an interface `ensures`, or a `NoReturn`/`Never` return — each
    #          is a claim about the body run eagerly, which the call never does
    #          (`requires` and `assigns` stay: a precondition only burdens the caller,
    #          and any frame over-approximates a call that writes nothing);
    #     (G3) it may not be invoked IMPLICITLY — a special method (`__init__`,
    #          `__iter__`, ...) or one behind a decorator other than `staticmethod`/
    #          `classmethod`/a `contextmanager` (`@property`);
    #     (G2) it may not be CALLED, nor used as a VALUE (`h = gen`, `map(gen, xs)`, a
    #          bound method `h = c.bump`), from lowered code, except as the context
    #          expression of a `with` item — Module 5 lowers a bare `with` to its BODY ALONE (the
    #          call is never emitted) and route #257 already vets that the producer is
    #          inert. A call `self.m(...)` inside class K resolves through K's in-file
    #          bases (a non-generator `m` found first is not a generator call unless an
    #          in-file subclass of K overrides it with one); any other `x.m(...)` is
    #          matched by NAME against every in-file generator method (fail-closed).
    #   `async def` never reaches the IR (route-0974's refusal owns it). An IMPORTED
    #   generator is a `trusted` dependency like every import: its own run refuses it
    #   under (G1)/(G2).
    #
    #   CENSUS before the change (Modules 1-3 over corpus + mirror + `pycsl_lib`): 11
    #   generator defs. Corpus: 1031 `blk`, 2670 `delimit` — called only as `with`
    #   items, no claim (PASS kept); 2661/2664 `bump` — `ensures` (G1), already refused
    #   by #257 (which runs first, so their message is unchanged); python-reference
    #   0061/0141/0175 nested `gen()` called by name (G2), all already `FAIL`;
    #   `multi_file_lib/r257_*lib.py` (G1, imported by #257 witnesses, already refused).
    #   Mirror: `ir_inline._walk_dicts` (recognized, exempt), `pure_ast.iter_fields`
    #   (called only from the `\trusted` `iter_child_nodes`), `iter_child_nodes`
    #   (`\trusted`), `_Unparser.block`/`delimit` (`ensures True`, called only as `with`
    #   items; the `_Parser.block` calls are a DIFFERENT, non-generator method, told
    #   apart by the class resolution). `pycsl_lib/json/encoder.py`: already refused.
    #   CHOKE POINT: `_run_pipeline`'s mirror twin is `\trusted`; inline, no new `def`.
    if unified_ast is not None:
        from frontend import pure_ast as _pa271
        from module6_whyml.generic_fold import (
            recognize_walk_dicts_generator as _rwdg271)
        _modelled271 = {_f["name"] for _f in (ir_data.get("functions") or [])
                        if isinstance(_f, dict) and isinstance(_f.get("name"), str)
                        and _rwdg271(_f)}
        _FN271 = ("FunctionDef", "AsyncFunctionDef")
        # every def with its owner class (direct class-body member) and whether its body
        # is lowered (not `\trusted`/`\abstract`, not nested inside such a def)
        _defs271 = []          # (def, owner class name or None, lowered)
        _bases271 = {}         # class -> in-file base names
        _meth271 = {}          # class -> {method name: is_generator}
        _st271 = [(unified_ast, None, True)]
        while _st271:
            _n271, _o271, _lw271 = _st271.pop()
            _nk271 = _n271.__class__.__name__
            if _nk271 == "ClassDef":
                _bases271.setdefault(_n271.name, set()).update(
                    _b.id for _b in (_n271.bases or []) if _b.__class__.__name__ == "Name")
                for _c271 in _pa271.iter_child_nodes(_n271):
                    _st271.append((_c271, _n271.name if _c271.__class__.__name__ in _FN271
                                   else None, _lw271))
                continue
            if _nk271 in _FN271:
                _lw271 = (_lw271 and not getattr(_n271, "csl_trusted", False)
                          and not getattr(_n271, "csl_abstract", False))
                _defs271.append((_n271, _o271, _lw271))
            for _c271 in _pa271.iter_child_nodes(_n271):
                _st271.append((_c271, None, _lw271))
        _isgen271 = {}
        for _d271, _o271, _lw271 in _defs271:
            _g271 = False
            _st271 = list(_d271.body)
            while _st271:
                _m271 = _st271.pop()
                _mk271 = _m271.__class__.__name__
                if _mk271 in ("Yield", "YieldFrom"):
                    _g271 = True
                    break
                if _mk271 not in _FN271 + ("Lambda", "ClassDef"):
                    _st271.extend(_pa271.iter_child_nodes(_m271))
            # a COUNTED generator: own `yield`, body lowered, no dedicated model
            _isgen271[id(_d271)] = (
                _g271 and _d271.__class__.__name__ == "FunctionDef" and _lw271
                and (_d271.name if _o271 is None
                     else "%s__%s" % (_o271.lower(), _d271.name)) not in _modelled271)
            if _o271 is not None:
                _mm271 = _meth271.setdefault(_o271, {})
                _mm271[_d271.name] = _mm271.get(_d271.name, False) or _isgen271[id(_d271)]
        _genfn271 = set()      # module-level / nested generator function names
        _genm271 = {}          # method name -> classes defining it as a generator
        _bad271 = None
        for _d271, _o271, _lw271 in _defs271:
            if not _isgen271[id(_d271)]:
                continue
            if _o271 is None:
                _genfn271.add(_d271.name)
            else:
                _genm271.setdefault(_d271.name, set()).add(_o271)
            if _bad271 is not None:
                continue
            _why271 = None
            for _e271 in (getattr(_d271, "csl_ensures", None) or []):
                _x271 = getattr(_e271, "expr", None)
                if not (_x271.__class__.__name__ == "CSLBool"
                        and getattr(_x271, "value", None) is True):
                    _why271 = "an `ensures` clause"
            if getattr(_d271, "csl_iface_ensures", None):
                _why271 = "an interface `ensures` clause"
            if getattr(_d271, "csl_raises", None):
                _why271 = "a `raises` clause"
            _rt271 = _d271.returns
            if ((_rt271.__class__.__name__ == "Name" and _rt271.id in ("NoReturn", "Never"))
                    or (_rt271.__class__.__name__ == "Attribute"
                        and _rt271.attr in ("NoReturn", "Never"))):
                _why271 = "a `NoReturn`/`Never` return annotation"
            if _why271 is not None:
                _bad271 = ("G1", _d271.name, getattr(_d271, "lineno", 0) or 0, _why271)
                continue
            # (G3) a generator Python invokes IMPLICITLY has no call site (G2) could
            # check: a special method (`C()` runs a generator `__init__`, measured
            # PROVED where CPython raises TypeError) or one behind a decorator other than
            # `staticmethod`/`classmethod`/a `contextmanager` (`@property`: attribute
            # access calls it)
            _dk271 = None
            if _d271.name.startswith("__") and _d271.name.endswith("__"):
                _dk271 = "the special-method name `%s`" % _d271.name
            for _dc271 in (_d271.decorator_list or []):
                _dn271 = (_dc271.id if _dc271.__class__.__name__ == "Name" else
                          _dc271.attr if _dc271.__class__.__name__ == "Attribute" else None)
                if not (isinstance(_dn271, str) and (
                        _dn271 in ("staticmethod", "classmethod")
                        or _dn271.endswith("contextmanager"))):
                    _dk271 = "a decorator other than `staticmethod`/`classmethod`/`contextmanager`"
            if _dk271 is not None:
                _bad271 = ("G3", _d271.name, getattr(_d271, "lineno", 0) or 0, _dk271)
        if _bad271 is None and (_genfn271 or _genm271):
            # (G2) calls from lowered code; a `with` item's own call is not emitted
            _st271 = [(unified_ast, None, True, None)]
            _callee271 = set()
            while _st271 and _bad271 is None:
                _n271, _k271, _lw271, _fn271 = _st271.pop()
                _nk271 = _n271.__class__.__name__
                if _nk271 == "ClassDef":
                    for _c271 in _pa271.iter_child_nodes(_n271):
                        _st271.append((_c271, _n271.name, _lw271, _fn271))
                    continue
                if _nk271 in _FN271:
                    _lw271 = (_lw271 and not getattr(_n271, "csl_trusted", False)
                              and not getattr(_n271, "csl_abstract", False))
                    _fn271 = _n271
                if (_nk271 == "If" and _fn271 is None
                        and _n271.test.__class__.__name__ == "Compare"
                        and _n271.test.left.__class__.__name__ == "Name"
                        and _n271.test.left.id == "__name__"):
                    continue   # the `__main__` block is never lowered
                if _nk271 in ("With", "AsyncWith"):
                    for _it271 in _n271.items:
                        _ce271 = _it271.context_expr
                        if _ce271.__class__.__name__ == "Call":
                            # the item's own call is never emitted; its arguments are
                            _ch271 = (list(_ce271.args or [])
                                      + [_kw.value for _kw in (_ce271.keywords or [])]
                                      + ([_ce271.func.value]
                                         if _ce271.func.__class__.__name__ == "Attribute"
                                         else []))
                        else:
                            _ch271 = [_ce271]
                        for _c271 in _ch271:
                            _st271.append((_c271, _k271, _lw271, _fn271))
                        if _it271.optional_vars is not None:
                            _st271.append((_it271.optional_vars, _k271, _lw271, _fn271))
                    for _c271 in _n271.body:
                        _st271.append((_c271, _k271, _lw271, _fn271))
                    continue
                if (_nk271 == "Name" and _lw271 and _n271.id in _genfn271
                        and _n271.ctx.__class__.__name__ == "Load"):
                    # the generator function used as a VALUE (`h = gen; h()`, `map(gen,
                    # xs)`) would be called where no check sees it
                    _bad271 = ("G2", _n271.id, getattr(_n271, "lineno", 0) or 0,
                               ("'%s'" % _fn271.name) if _fn271 is not None
                               else "module scope")
                    break
                if (_nk271 == "Attribute" and _lw271 and _n271.attr in _genm271
                        and id(_n271) not in _callee271
                        and _n271.ctx.__class__.__name__ == "Load"):
                    # a generator METHOD taken as a bound-method VALUE (`h = c.bump`)
                    _bad271 = ("G2", _pa271.unparse(_n271), getattr(_n271, "lineno", 0) or 0,
                               ("'%s'" % _fn271.name) if _fn271 is not None
                               else "module scope")
                    break
                if _nk271 == "Call":
                    _callee271.add(id(_n271.func))
                if _nk271 == "Call" and _lw271:
                    _f271 = _n271.func
                    _hit271 = False
                    if _f271.__class__.__name__ == "Name":
                        _hit271 = _f271.id in _genfn271
                    elif (_f271.__class__.__name__ == "Attribute"
                          and _f271.attr in _genm271):
                        _hit271 = True
                        _cls271 = _k271 if _fn271 is not None and _k271 is not None else None
                        if (_cls271 is not None and _f271.value.__class__.__name__ == "Name"
                                and _f271.value.id in ("self", "cls")):
                            # first in-file class along K's bases that defines the method
                            _seen271 = set()
                            _q271 = [_cls271]
                            _found271 = None
                            while _q271 and _found271 is None:
                                _c271 = _q271.pop(0)
                                if _c271 in _seen271:
                                    continue
                                _seen271.add(_c271)
                                if _f271.attr in _meth271.get(_c271, {}):
                                    _found271 = _meth271[_c271][_f271.attr]
                                else:
                                    _q271.extend(sorted(_bases271.get(_c271, ())))
                            if _found271 is False:
                                # ...unless an in-file SUBCLASS of K overrides it with one
                                _hit271 = False
                                for _g271 in _genm271[_f271.attr]:
                                    _seen271 = set()
                                    _q271 = [_g271]
                                    while _q271:
                                        _c271 = _q271.pop(0)
                                        if _c271 in _seen271:
                                            continue
                                        _seen271.add(_c271)
                                        if _c271 == _cls271 and _g271 != _cls271:
                                            _hit271 = True
                                        _q271.extend(sorted(_bases271.get(_c271, ())))
                    if _hit271:
                        _bad271 = ("G2", _pa271.unparse(_f271) if hasattr(_pa271, "unparse")
                                   else getattr(_f271, "attr", getattr(_f271, "id", "?")),
                                   getattr(_n271, "lineno", 0) or 0,
                                   ("'%s'" % _fn271.name) if _fn271 is not None
                                   else "module scope")
                        break
                for _c271 in _pa271.iter_child_nodes(_n271):
                    _st271.append((_c271, _k271, _lw271, _fn271))
        if _bad271 is not None:
            from errors import PyCSLSemanticError as _PyCSLSemErr271
            if _bad271[0] == "G1":
                raise _PyCSLSemErr271(
                    "generator function `%s` (line %d) carries %s (ROUTE #271): a function "
                    "containing `yield` is a GENERATOR — calling it only builds the generator "
                    "and runs NONE of its body — but PyCSL has no generator model and lowers "
                    "the body as an ordinary procedure run at the call, so a postcondition, a "
                    "`raises` or a no-return claim is proven of an execution Python never "
                    "performs. Measured: `bump(self)` doing `self.n += 1; yield 0` proved "
                    "`ensures self.n == \\old(self.n) + 1`, and a caller then proved "
                    "`c.bump(); return c.n` == 1 where CPython returns 0. Drop the clause "
                    "(a generator may keep `requires` and `assigns`), or make the function an "
                    "ordinary one that RETURNS its values (e.g. a `list`)."
                    % (_bad271[1], _bad271[2], _bad271[3]),
                    filename=args.file, line=_bad271[2],
                    stage="ir-semantic", code="PYCSL-SEM-GENERATOR-CONTRACT")
            if _bad271[0] == "G3":
                raise _PyCSLSemErr271(
                    "generator function `%s` (line %d) has %s (ROUTE #271): Python invokes it "
                    "IMPLICITLY, so no call site can be checked, and PyCSL has no generator "
                    "model — it lowers the body as an ordinary procedure run at the "
                    "invocation, while Python only builds a generator there (a generator "
                    "`__init__` makes `C()` raise TypeError; measured, `C()` then "
                    "`return c.n` PROVED the field the body set). Make it an ordinary "
                    "method that RETURNS its values (e.g. a `list`)."
                    % (_bad271[1], _bad271[2], _bad271[3]),
                    filename=args.file, line=_bad271[2],
                    stage="ir-semantic", code="PYCSL-SEM-GENERATOR-IMPLICIT")
            raise _PyCSLSemErr271(
                "a call to (or a use as a value of) the generator function `%s` (line %d, "
                "in %s) is not modelled "
                "(ROUTE #271): calling a function that contains `yield` only BUILDS a "
                "generator — none of its body runs until it is iterated — but PyCSL has no "
                "generator model and lowers the body as an ordinary procedure, so the call "
                "would apply the body's effects and contract AT THE CALL. Measured: "
                "`c.bump()` on a generator method doing `self.n += 1; yield 0` proved "
                "`c.n == 1` where CPython leaves it 0. Make the function an ordinary one "
                "that RETURNS its values (e.g. a `list`) and iterate that, or use the "
                "generator only as a `with` item of an inert `@contextmanager` producer."
                % (_bad271[1], _bad271[2], _bad271[3]),
                filename=args.file, line=_bad271[2],
                stage="ir-semantic", code="PYCSL-SEM-GENERATOR-CALL")

    # ROUTE #37 (relaunch #45) — REFUSE a `try ... else:` whose ELSE BLOCK JUMPS OUT.
    #
    #   Route #21 established that the `TRYFINAL` residue was not merely counted but
    #   EXPLOITABLE, and refused the `finally`-with-handlers half in
    #   `_handle_try_stmt`. THE `else` HALF WAS LEFT COUNTED AND UNREFUSED, and it is
    #   exploitable on exactly the same terms. `_handle_try_stmt` appends the lowered
    #   else to the try body only when `"raise" not in _else_str` — and a `return`
    #   lowers to `raise (Return ...)`, so an else block that RETURNS is DROPPED IN
    #   SILENCE. MEASURED in the default hoare model, no flags:
    #
    #       try:     x = 1
    #       except ValueError: return 3
    #       else:    return 2          <-- absent from the emission entirely
    #       return 1                  #@ ensures \result == 1  -> PROVED
    #
    #   Python runs the `else` when the body raises nothing, so it returns 2.
    #   Witness `pycsl-reference/1028`.
    #
    #   THE RATCHET WAS GREEN THE WHOLE TIME. `check-dropped-mutation` classifies
    #   this shape as TRYFINAL and its ratchet stands at 10 — the drop was COUNTED,
    #   and counting a drop is not the same as establishing that it is safe. That is
    #   #43's own lesson ("probe a green ratchet") applied to the ratchet #43 left.
    #
    #   REFUSED HERE rather than in `_handle_try_stmt`, which is a CONVERTED mirror
    #   method: a raise added there needs a mirror body sync and a whole-file re-proof
    #   of `stmt_control_flow` (12294 goals) to state a refusal the pipeline can make
    #   once, before emission, for nothing. `_run_pipeline` already raises.
    #
    #   SCOPE: an else that CANNOT jump out is still emitted (#33's capability, kept).
    #   The IR test is a conservative approximation of the emitter's own `"raise" not
    #   in <lowered else>`: `return`/`raise`/`break`/`continue` are what put a `raise`
    #   in the lowered text. A non-jumping else whose lowering contained `raise` for
    #   some other reason would still be dropped — no such shape is known, and none
    #   exists in either corpus or the mirror, where `try ... else:` does not occur AT
    #   ALL (measured by an AST census over all four trees).
    for _f37 in ir_data.get("functions", []):
        _s37 = [_f37.get("body", [])]
        _hit37 = None
        while _s37 and _hit37 is None:
            _n37 = _s37.pop()
            if isinstance(_n37, dict):
                if _n37.get("stmt") == "Try" and _n37.get("orelse"):
                    _j37 = [_n37.get("orelse")]
                    while _j37:
                        _x37 = _j37.pop()
                        if isinstance(_x37, dict):
                            if _x37.get("stmt") in ("Return", "Raise", "Break",
                                                    "Continue"):
                                _hit37 = _f37.get("name", "?")
                                break
                            _j37.extend(_x37.values())
                        elif isinstance(_x37, (list, tuple)):
                            _j37.extend(_x37)
                    if _hit37 is not None:
                        break
                _s37.extend(_n37.values())
            elif isinstance(_n37, (list, tuple)):
                _s37.extend(_n37)
        if _hit37 is not None:
            from errors import PyCSLSemanticError as _PyCSLSemErr37
            raise _PyCSLSemErr37(
                f"the `else:` block of a `try` in {_hit37!r} jumps out (ROUTE #37): "
                f"Module 6 appends a lowered `else` to the try body only when that "
                f"lowering contains no `raise`, and a `return`/`raise`/`break`/"
                f"`continue` lowers to one — so the block would be DROPPED and the "
                f"run would still report 'All contracts formally proven' for a "
                f"contract that is FALSE of the program. An `else:` that cannot jump "
                f"out IS modelled; move the jump after the `try`, or fold the block "
                f"into the end of the try body.",
                stage="whyml-emit", code="PYCSL-R37-TRY-ELSE-DROPPED")
    # (#49) ROUTE #156 — ROUTE #21's REFUSAL COVERS A `finally` WITH HANDLERS; THE OTHER
    # HALF OF THE SAME RESIDUE WAS STILL DROPPED IN SILENCE. `_handle_try_stmt` appends a
    # `finally` only when the try has no handlers AND "raise" is not in the lowered body; a
    # `return`/`raise`/`break`/`continue` in the body lowers to a `raise`, so for a
    # handler-less try that JUMPS OUT the block vanishes. MEASURED (gen #29):
    #     x = 0
    #     try:
    #         try:     raise ValueError
    #         finally: x = 7
    #     except ValueError: pass
    #     return x                 #@ ensures \result != 7   <-- PROVED; CPython 7
    # Refused HERE, before emission, for the same reason route #37's twin is:
    # `_handle_try_stmt` is a CONVERTED mirror method (a raise there needs a body sync and
    # a whole-file re-proof). A `finally` whose try body cannot jump out is still emitted.
    for _f156 in ir_data.get("functions", []):
        # a `\trusted` / `\abstract` body (and a trusted parent's lifted helper) is never
        # lowered, so nothing of it can be dropped — and an imported dependency stub arrives
        # marked trusted, so a library's own `try/finally` never refuses its importer.
        if (_f156.get("trusted") or _f156.get("abstract")
                or _f156.get("trusted_parent")):
            continue
        _s156 = [_f156.get("body", [])]
        _hit156 = None
        while _s156 and _hit156 is None:
            _n156 = _s156.pop()
            if isinstance(_n156, dict):
                if (_n156.get("stmt") == "Try" and _n156.get("finalbody")
                        and not _n156.get("handlers")):
                    _j156 = [_n156.get("body")]
                    while _j156:
                        _x156 = _j156.pop()
                        if isinstance(_x156, dict):
                            if _x156.get("stmt") in ("Return", "Raise", "Break", "Continue"):
                                _hit156 = _f156.get("name", "?")
                                break
                            _j156.extend(_x156.values())
                        elif isinstance(_x156, (list, tuple)):
                            _j156.extend(_x156)
                    if _hit156 is not None:
                        break
                _s156.extend(_n156.values())
            elif isinstance(_n156, (list, tuple)):
                _s156.extend(_n156)
        if _hit156 is not None:
            from errors import PyCSLSemanticError as _PyCSLSemErr156
            raise _PyCSLSemErr156(
                f"a `try ... finally:` in {_hit156!r} has no handlers and its body jumps "
                f"out (ROUTE #156): Module 6 appends the `finally` block only when the "
                f"lowered try body contains no `raise`, and a `return`/`raise`/`break`/"
                f"`continue` lowers to one — so the block would be DROPPED on every path "
                f"and the run would still report 'All contracts formally proven'. A "
                f"`finally` whose try body cannot jump out IS modelled; move the jump "
                f"after the `try`.",
                stage="whyml-emit", code="PYCSL-R156-TRY-FINALLY-JUMP-DROPPED")
    # (#49) ROUTE #175 — A USER EXCEPTION SUBCLASS IS NOT CAUGHT BY ITS BASE CLASS HANDLER.
    # Handler matching knows the builtin hierarchy only (`exception_model.EXCEPTION_BASES`);
    # a user `class MyErr(ValueError)` / `class Sub(Base)` raised in a `try` is its own Why3
    # exception, the `with ValueError ->` / `with Base ->` arm never matches it, and it
    # escapes into an added `raises { MyErr }` — so the handler's path is dead in the proof.
    # MEASURED (gen #29): `try: raise MyErr() except ValueError: return 9; return 0` PROVED
    # `\result == 0` (CPython 9); same for `Sub(Base)`. The resolved IR has already cleared
    # the class `bases` (inheritance merged), so the check reads the SOURCE: a handler naming
    # a strict ancestor of an exception raised in its `try` body (a `raise`, or a call to a
    # function whose `#@ raises` names it) is refused in a non-trusted function.
    try:
        import ast as _ast175
        _t175 = _ast175.parse(source_code)
    except Exception:
        _t175 = None
    if _t175 is not None:
        # (#49) ROUTE #181 — THE SOURCE CHECKS OF ROUTES #175 AND #179 READ THE MAIN FILE ONLY.
        # An IMPORTED `class MyErr(ValueError)` raised under `except ValueError`, and an
        # IMPORTED class whose `__init__` raises, constructed under `no_exception ValueError`
        # or inside `except ValueError`, each PROVED (CPython raises / 9). The dependency
        # modules named by the main file's imports (resolved against the main file's
        # directory and `--import-path`, transitively) are parsed too; their classes and
        # functions feed the class/raise maps, while the callers checked stay the main file's.
        import os as _os181
        _tall175 = _ast175.Module(body=list(_t175.body), type_ignores=[])
        _main_ids181 = {id(_z) for _z in _ast175.walk(_t175)}
        _dirs181 = [_os181.path.dirname(_os181.path.abspath(str(args.file)))]
        _dirs181 += [str(_d) for _d in (getattr(args, "import_path", None) or [])]
        _seen181 = set()
        _todo181 = [(_t175, _dirs181[0])]
        while _todo181 and len(_seen181) < 64:
            _tree181, _here181 = _todo181.pop()
            for _im181 in _ast175.walk(_tree181):
                _mods181 = []
                if isinstance(_im181, _ast175.ImportFrom) and _im181.module:
                    _mods181.append((_im181.module, _im181.level or 0))
                elif isinstance(_im181, _ast175.Import):
                    _mods181.extend((_a.name, 0) for _a in _im181.names)
                for _mn181, _lv181 in _mods181:
                    _cands181 = ([_here181] if _lv181 else []) + ([] if _lv181 else [_here181] + _dirs181)
                    for _dd181 in _cands181:
                        for _pp181 in (_os181.path.join(_dd181, *_mn181.split(".")) + ".py",
                                       _os181.path.join(_dd181, *_mn181.split("."), "__init__.py")):
                            if _pp181 in _seen181 or not _os181.path.isfile(_pp181):
                                continue
                            _seen181.add(_pp181)
                            try:
                                _dt181 = _ast175.parse(open(_pp181).read())
                            except Exception:
                                continue
                            _tall175.body.extend(_dt181.body)
                            _todo181.append((_dt181, _os181.path.dirname(_pp181)))
        _bases175 = {}
        for _c175 in _ast175.walk(_tall175):
            if isinstance(_c175, _ast175.ClassDef):
                _bases175[_c175.name] = [
                    (_b175.id if isinstance(_b175, _ast175.Name) else _b175.attr)
                    for _b175 in _c175.bases
                    if isinstance(_b175, (_ast175.Name, _ast175.Attribute))]
        _alias175 = {}
        # a plain name alias of an exception class (`Alias = MyErr`, anywhere) is the same
        # class: measured, `raise Alias()` under `except ValueError` still proved the other path
        for _al175 in _ast175.walk(_tall175):
            if (isinstance(_al175, _ast175.Assign) and len(_al175.targets) == 1
                    and isinstance(_al175.targets[0], _ast175.Name)
                    and isinstance(_al175.value, _ast175.Name)
                    and _al175.value.id in _bases175
                    and _al175.targets[0].id not in _bases175):
                _bases175[_al175.targets[0].id] = [_al175.value.id]
                _alias175[_al175.targets[0].id] = _al175.value.id
        if _bases175:
            _lines175 = source_code.splitlines()
            _decl175 = {}
            for _d175 in _ast175.walk(_tall175):
                if isinstance(_d175, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                    _i175 = min([_d175.lineno] + [_x.lineno for _x in _d175.decorator_list]) - 2
                    if id(_d175) not in _main_ids181:
                        _i175 = -1
                    _rs175 = set()
                    while 0 <= _i175 < len(_lines175) and _lines175[_i175].strip().startswith(("#@", "@")):
                        _ln175 = _lines175[_i175].strip()
                        if _ln175.startswith("#@ raises"):
                            _tok175 = _ln175[len("#@ raises"):].strip().split()
                            if _tok175:
                                _rs175.add(_tok175[0].rstrip(","))
                        _i175 -= 1
                    # an UNANNOTATED callee's own `raise` statements count too (measured: a
                    # method raising `MyErr(ValueError)` with no `#@ raises`, caught by
                    # `except ValueError` in the caller, still proved the other path)
                    for _y175 in _ast175.walk(_d175):
                        if isinstance(_y175, _ast175.Raise) and _y175.exc is not None:
                            _ey175 = (_y175.exc.func if isinstance(_y175.exc, _ast175.Call)
                                      else _y175.exc)
                            if isinstance(_ey175, _ast175.Name):
                                _rs175.add(_ey175.id)
                    _decl175.setdefault(_d175.name, set()).update(_rs175)
            # trusted functions by their IR name: `<class_lower>__<method>` for a method (a
            # name-tail match lost a leading underscore, `x___m`.rsplit("__") -> "m", and let
            # the mirror's trusted `_render_callee_condition` be checked — route #181 census)
            _trusted175 = {str(_f.get("name", ""))
                           for _f in ir_data.get("functions", [])
                           if _f.get("trusted") or _f.get("abstract") or _f.get("trusted_parent")}
            _owner181 = {}
            for _k181 in _ast175.walk(_tall175):
                if isinstance(_k181, _ast175.ClassDef):
                    for _m181 in _k181.body:
                        if isinstance(_m181, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                            _owner181[id(_m181)] = _k181.name
            import builtins as _bi175
            for _fd175 in _ast175.walk(_t175):
                if not isinstance(_fd175, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                    continue
                if ((f"{_owner181[id(_fd175)].lower()}__{_fd175.name}" if id(_fd175) in _owner181
                     else _fd175.name) in _trusted175):
                    continue
                for _tr175 in _ast175.walk(_fd175):
                    if not isinstance(_tr175, _ast175.Try):
                        continue
                    _e175 = set()
                    for _st175 in _tr175.body:
                        for _x175 in _ast175.walk(_st175):
                            if isinstance(_x175, _ast175.Raise) and _x175.exc is not None:
                                _ex175 = _x175.exc.func if isinstance(_x175.exc, _ast175.Call) else _x175.exc
                                if isinstance(_ex175, _ast175.Name):
                                    _e175.add(_ex175.id)
                            if isinstance(_x175, _ast175.Call):
                                _cn175 = (_x175.func.id if isinstance(_x175.func, _ast175.Name)
                                          else _x175.func.attr if isinstance(_x175.func, _ast175.Attribute)
                                          else None)
                                if _cn175:
                                    _e175 |= _decl175.get(_cn175, set())
                    for _s175 in _e175:
                        if _s175 not in _bases175:
                            continue
                        _anc175 = set()
                        _q175 = list(_bases175.get(_s175, []))
                        while _q175:
                            _a175 = _q175.pop()
                            if _a175 in _anc175:
                                continue
                            _anc175.add(_a175)
                            _q175.extend(_bases175.get(_a175, []))
                            _ba175 = getattr(_bi175, _a175, None)
                            if isinstance(_ba175, type) and issubclass(_ba175, BaseException):
                                _anc175.update(_k.__name__ for _k in _ba175.__mro__
                                               if issubclass(_k, BaseException))
                        for _h175 in _tr175.handlers:
                            _hn175 = []
                            if isinstance(_h175.type, _ast175.Name):
                                _hn175 = [_h175.type.id]
                            elif isinstance(_h175.type, _ast175.Tuple):
                                _hn175 = [_e.id for _e in _h175.type.elts if isinstance(_e, _ast175.Name)]
                            for _hh175 in _hn175:
                                if _hh175 != _s175 and (
                                        _hh175 in _anc175
                                        or _alias175.get(_hh175, _hh175) == _alias175.get(_s175, _s175)
                                        or _alias175.get(_hh175, _hh175) in _anc175):
                                    from errors import PyCSLSemanticError as _PyCSLSemErr175
                                    raise _PyCSLSemErr175(
                                        f"`except {_hh175}` in {_fd175.name!r} is meant to catch "
                                        f"the raised `{_s175}`, a user subclass of it (ROUTE #175), "
                                        f"but handler matching knows only the builtin exception "
                                        f"hierarchy: in the proof the raise escapes the handler "
                                        f"while Python runs it, so a contract about the handler's "
                                        f"path would be proved of the other one. Catch `{_s175}` "
                                        f"by its own name.",
                                        stage="whyml-emit", code="PYCSL-R175-USER-EXCEPTION-SUBCLASS")
    # (#49) ROUTE #179 — A CONSTRUCTOR THAT RAISES IS LOWERED AS A RECORD LITERAL, AND THE
    # RAISE IS GONE. `__init__` (and a dataclass `__post_init__`) is synthesised into a record
    # value; a `raise` in it never reaches the model. MEASURED (gen #29): `C(-1)` with
    # `if v < 0: raise ValueError()` in `__init__` PROVED `#@ no_exception ValueError`, and
    # `try: c = C(-1) except ValueError: return 9; return 0` PROVED `\\result == 0` (CPython
    # raises / 9); same through `__post_init__`. Refused: a non-trusted function that calls such
    # a class (directly, or through same-file functions that do, transitively) while declaring
    # `no_exception` for the raised exception (or `\\all`) or holding a handler that catches it.
    if _t175 is not None:
        import builtins as _bi179
        # explicit raises per function name, closed over same-file calls (a constructor that
        # raises through `check(v)` / `self.check()` raises too — measured on the draft)
        _fr179 = {}
        _fc179 = {}
        for _f179 in _ast175.walk(_tall175):
            if not isinstance(_f179, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                continue
            _rs179 = _fr179.setdefault(_f179.name, set())
            _cc179 = _fc179.setdefault(_f179.name, set())
            for _q179 in _ast175.walk(_f179):
                if isinstance(_q179, _ast175.Raise) and _q179.exc is not None:
                    _e179 = _q179.exc.func if isinstance(_q179.exc, _ast175.Call) else _q179.exc
                    _rs179.add(_e179.id if isinstance(_e179, _ast175.Name) else "BaseException")
                if isinstance(_q179, _ast175.Call):
                    _cn179 = (_q179.func.id if isinstance(_q179.func, _ast175.Name)
                              else _q179.func.attr if isinstance(_q179.func, _ast175.Attribute)
                              else None)
                    if _cn179:
                        _cc179.add(_cn179)
        _chg179 = True
        while _chg179:
            _chg179 = False
            for _fn179, _cc179 in _fc179.items():
                for _cn179 in _cc179:
                    if _cn179 != _fn179 and _cn179 in _fr179 and not _fr179[_cn179] <= _fr179[_fn179]:
                        _fr179[_fn179] |= _fr179[_cn179]
                        _chg179 = True
        _cls179 = {}
        for _c179 in _ast175.walk(_tall175):
            if not isinstance(_c179, _ast175.ClassDef):
                continue
            _ex179 = set()
            for _m179 in _c179.body:
                if (isinstance(_m179, (_ast175.FunctionDef, _ast175.AsyncFunctionDef))
                        and _m179.name in ("__init__", "__post_init__", "__new__")):
                    _nest179 = set()
                    for _q179 in _ast175.walk(_m179):
                        if _q179 is not _m179 and isinstance(
                                _q179, (_ast175.FunctionDef, _ast175.AsyncFunctionDef, _ast175.Lambda)):
                            _nest179 |= {id(_z) for _z in _ast175.walk(_q179)}
                    for _q179 in _ast175.walk(_m179):
                        if (isinstance(_q179, _ast175.Call) and id(_q179) not in _nest179):
                            _cn179 = (_q179.func.id if isinstance(_q179.func, _ast175.Name)
                                      else _q179.func.attr if isinstance(_q179.func, _ast175.Attribute)
                                      else None)
                            if _cn179 and _cn179 in _fr179 and _cn179 != _m179.name:
                                _ex179 |= _fr179[_cn179]
                        if (isinstance(_q179, _ast175.Raise) and id(_q179) not in _nest179):
                            _e179 = _q179.exc
                            if isinstance(_e179, _ast175.Call):
                                _e179 = _e179.func
                            _ex179.add(_e179.id if isinstance(_e179, _ast175.Name) else "BaseException")
            if _ex179:
                _cls179[_c179.name] = _ex179
        if _cls179:
            _bases179 = {}
            for _c179 in _ast175.walk(_tall175):
                if isinstance(_c179, _ast175.ClassDef):
                    _bases179[_c179.name] = [
                        (_b.id if isinstance(_b, _ast175.Name) else _b.attr)
                        for _b in _c179.bases if isinstance(_b, (_ast175.Name, _ast175.Attribute))]
            # a subclass without its own raising constructor inherits the base's
            _chg179 = True
            while _chg179:
                _chg179 = False
                for _cn179, _bl179 in _bases179.items():
                    for _b179 in _bl179:
                        if _b179 in _cls179 and not _cls179[_b179] <= _cls179.get(_cn179, set()):
                            _cls179.setdefault(_cn179, set()).update(_cls179[_b179])
                            _chg179 = True
            _lines179 = source_code.splitlines()
            _funcs179 = [_d for _d in _ast175.walk(_tall175)
                         if isinstance(_d, (_ast175.FunctionDef, _ast175.AsyncFunctionDef))]
            _may179 = {}
            _calls179 = {}
            for _d179 in _funcs179:
                _cs179 = set()
                _dir179 = set()
                for _q179 in _ast175.walk(_d179):
                    if isinstance(_q179, _ast175.Call):
                        _fnm179 = (_q179.func.id if isinstance(_q179.func, _ast175.Name)
                                   else _q179.func.attr if isinstance(_q179.func, _ast175.Attribute)
                                   else None)
                        if _fnm179:
                            _cs179.add(_fnm179)
                            if _fnm179 in _cls179:
                                _dir179 |= _cls179[_fnm179]
                _calls179[id(_d179)] = _cs179
                _may179[id(_d179)] = set(_dir179)
            _names179 = {}
            for _d179 in _funcs179:
                _names179.setdefault(_d179.name, []).append(_d179)
            _chg179 = True
            while _chg179:
                _chg179 = False
                for _d179 in _funcs179:
                    for _cn179 in _calls179[id(_d179)]:
                        for _g179 in _names179.get(_cn179, []):
                            if _g179 is not _d179 and not _may179[id(_g179)] <= _may179[id(_d179)]:
                                _may179[id(_d179)] |= _may179[id(_g179)]
                                _chg179 = True
            _trusted179 = {str(_f.get("name", ""))
                           for _f in ir_data.get("functions", [])
                           if _f.get("trusted") or _f.get("abstract") or _f.get("trusted_parent")}
            _owner179 = {}
            for _k179 in _ast175.walk(_tall175):
                if isinstance(_k179, _ast175.ClassDef):
                    for _m179 in _k179.body:
                        if isinstance(_m179, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                            _owner179[id(_m179)] = _k179.name

            for _d179 in _funcs179:
                _ex179 = _may179[id(_d179)]
                if (not _ex179 or id(_d179) not in _main_ids181
                        or (f"{_owner179[id(_d179)].lower()}__{_d179.name}" if id(_d179) in _owner179
                            else _d179.name) in _trusted179):
                    continue
                _i179 = min([_d179.lineno] + [_x.lineno for _x in _d179.decorator_list]) - 2
                _ne179 = set()
                while 0 <= _i179 < len(_lines179) and _lines179[_i179].strip().startswith(("#@", "@")):
                    _ln179 = _lines179[_i179].strip()
                    if _ln179.startswith("#@ no_exception"):
                        _ne179.update(_t.strip(",") for _t in _ln179[len("#@ no_exception"):].split())
                    _i179 -= 1
                _hs179 = set()
                for _q179 in _ast175.walk(_d179):
                    if isinstance(_q179, _ast175.ExceptHandler):
                        if _q179.type is None:
                            _hs179.add("")
                        elif isinstance(_q179.type, _ast175.Name):
                            _hs179.add(_q179.type.id)
                        elif isinstance(_q179.type, _ast175.Tuple):
                            _hs179.update(_z.id for _z in _q179.type.elts if isinstance(_z, _ast175.Name))
                for _e179 in sorted(_ex179):
                    # ancestors of the raised name (user bases, then the builtin MRO); a bare
                    # handler (""), `Exception` and `BaseException` catch it too
                    _anc179 = {"", "Exception", "BaseException"}
                    _qq179 = [_e179]
                    while _qq179:
                        _a179 = _qq179.pop()
                        if _a179 in _anc179:
                            continue
                        _anc179.add(_a179)
                        _qq179.extend(_bases179.get(_a179, []))
                        _ab179 = getattr(_bi179, _a179, None)
                        if isinstance(_ab179, type) and issubclass(_ab179, BaseException):
                            _anc179.update(_k.__name__ for _k in _ab179.__mro__)
                    if ("\\all" in _ne179 or _e179 in _ne179
                            or any(_h179 in _anc179 for _h179 in _hs179)):
                        from errors import PyCSLSemanticError as _PyCSLSemErr179
                        raise _PyCSLSemErr179(
                            f"{_d179.name!r} constructs an object whose `__init__` / "
                            f"`__post_init__` can raise `{_e179}` (ROUTE #179), directly or "
                            f"through a call, and either claims `no_exception` for it or "
                            f"catches it; a construction is lowered to a record value and "
                            f"the raise is not modelled, so the claim or the handler's path "
                            f"would be proved of the wrong program. Validate the argument "
                            f"before constructing, or move the check out of the constructor.",
                            stage="whyml-emit", code="PYCSL-R179-RAISING-CONSTRUCTOR")
    # (#49) ROUTE #187 — `#@ fresh_globals` ASSUMES THE CONSTRUCTOR POST-STATE, AND THE
    # MODULE BODY'S OWN MUTATIONS OF THE GLOBAL ARE INVISIBLE TO IT. The directive
    # re-establishes each module-global singleton's `__init__` post-state as an ASSUMED
    # entry fact; the IR records a global as `{name, class, value}` only, and every OTHER
    # top-level statement is dropped on the floor. MEASURED (gen #29):
    # `counter = Counter(); counter.n = 7` with a `#@ fresh_globals` driver returning
    # `counter.n` PROVED `\result == 0` (CPython 7), and the same with a top-level
    # `counter.bump()` (`ensures self.n == 3`) PROVED `\result == 0` (CPython 3). Without
    # the directive both FAIL (the global is havoc'd), so the assumed fact is the whole gap.
    # The existing PYCSL-SEM-FRESH-GLOBALS confinement checks only that the driver is not a
    # method and is called by nobody — neither sees the module body. FAIL-CLOSED: with a
    # `#@ fresh_globals` driver in the file, the module body may contain only imports,
    # definitions, a docstring, and simple `name = <expr>` bindings that neither rebind a
    # name nor read a global singleton. An attribute/subscript store, a bare call, an `if`
    # or a loop at module level is refused — the assumed constructor state would describe a
    # program state the module body has already left.
    if _t175 is not None and any(_f.get("fresh_globals")
                                 for _f in (ir_data.get("functions", []) or [])):
        _gl187 = {str(_g.get("name")) for _g in (ir_data.get("module_globals", []) or [])
                  if _g.get("name")}
        _seenb187 = set()
        for _s187 in _t175.body:
            if isinstance(_s187, (_ast175.Import, _ast175.ImportFrom, _ast175.ClassDef,
                                  _ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                continue
            if isinstance(_s187, _ast175.Expr) and isinstance(_s187.value, _ast175.Constant):
                continue
            _bad187 = ""
            if isinstance(_s187, (_ast175.Assign, _ast175.AnnAssign)):
                _tg187 = (list(_s187.targets) if isinstance(_s187, _ast175.Assign)
                          else [_s187.target])
                if not all(isinstance(_x187, _ast175.Name) for _x187 in _tg187):
                    _bad187 = ("a module-level attribute or subscript store "
                               "(the write is not in the IR at all)")
                else:
                    for _x187 in _tg187:
                        if _x187.id in _seenb187:
                            _bad187 = (f"the module-level name {_x187.id!r} is bound twice "
                                       f"(the second binding is not in the IR)")
                        _seenb187.add(_x187.id)
                    for _n187 in _ast175.walk(_s187.value) if _s187.value is not None else []:
                        if isinstance(_n187, _ast175.Name) and _n187.id in _gl187:
                            _bad187 = (f"a module-level statement that reads the global "
                                       f"singleton {_n187.id!r}")
            else:
                _bad187 = ("a module-level statement that is not an import, a definition or "
                           "a simple binding (it is not in the IR, so its effect on a global "
                           "is invisible)")
            if _bad187:
                from errors import PyCSLSemanticError as _PyCSLSemErr187
                raise _PyCSLSemErr187(
                    f"this module declares `#@ fresh_globals`, which ASSUMES each "
                    f"module-global singleton's constructor post-state at the driver's "
                    f"entry, but line {getattr(_s187, 'lineno', 0)} is {_bad187} "
                    f"(ROUTE #187). The module body runs at import, after the constructor, "
                    f"so the assumed fact would be proved of a state the program has "
                    f"already left. Move the statement into the driver, or drop "
                    f"`#@ fresh_globals`.",
                    stage="whyml-emit", code="PYCSL-R187-FRESH-GLOBALS-MODULE-BODY")
    # (#49) ROUTE #189 — ONE RECEIVER NAME, TWO CLASSES, ONE CONTRACT. A local bound to a
    # record constructor is mapped to its class by `IRScanner.find_record_var_classes`,
    # which `update()`s every nested scope into ONE FLAT MAP: for
    # `if flag > 0: o = D() else: o = C()` the LAST branch scanned wins, so `o` resolved to
    # `C` and the single call site `o.get()` was emitted as one abstract stub carrying
    # `C.get`'s `ensures`. MEASURED (gen #29): that file PROVED `\result == 1` for EVERY
    # `flag` while CPython returns 2 on the `D` branch — route #166 again, from the other
    # end (there, two call sites and one stub NAME; here, one call site and one CLASS).
    # The scanner itself is the certified `sdict` dict-fold (`recognize_dictfold`), so the
    # marking cannot live there without losing that lowering; the refusal reads the SOURCE,
    # like routes #175/#179/#187. FAIL-CLOSED and measured emission-inert: no function in
    # `src/` or in the reference corpus binds one name to two record classes and then calls
    # a method on it (scanned, zero hits).
    if _t175 is not None:
        _rc189 = {_c189.name for _c189 in _ast175.walk(_tall175)
                  if isinstance(_c189, _ast175.ClassDef)}
        _tr189 = {str(_f.get("name", "")) for _f in (ir_data.get("functions", []) or [])
                  if _f.get("trusted") or _f.get("abstract") or _f.get("trusted_parent")}
        _ow189 = {}
        for _k189 in _ast175.walk(_tall175):
            if isinstance(_k189, _ast175.ClassDef):
                for _m189 in _k189.body:
                    if isinstance(_m189, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                        _ow189[id(_m189)] = _k189.name
        for _fd189 in _ast175.walk(_t175):
            if not isinstance(_fd189, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                continue
            if ((f"{_ow189[id(_fd189)].lower()}__{_fd189.name}" if id(_fd189) in _ow189
                 else _fd189.name) in _tr189):
                continue
            _bd189 = {}
            for _st189 in _ast175.walk(_fd189):
                _tg189 = []
                _v189 = None
                if isinstance(_st189, _ast175.Assign):
                    _tg189, _v189 = list(_st189.targets), _st189.value
                elif isinstance(_st189, _ast175.AnnAssign) and _st189.value is not None:
                    _tg189, _v189 = [_st189.target], _st189.value
                if (isinstance(_v189, _ast175.Call)
                        and isinstance(_v189.func, _ast175.Name)
                        and _v189.func.id in _rc189):
                    for _x189 in _tg189:
                        if isinstance(_x189, _ast175.Name):
                            _bd189.setdefault(_x189.id, set()).add(_v189.func.id)
            _ab189 = sorted(_n for _n in _bd189 if len(_bd189[_n]) > 1)
            if not _ab189:
                continue
            for _ca189 in _ast175.walk(_fd189):
                if (isinstance(_ca189, _ast175.Call)
                        and isinstance(_ca189.func, _ast175.Attribute)
                        and isinstance(_ca189.func.value, _ast175.Name)
                        and _ca189.func.value.id in _ab189):
                    _nm189 = _ca189.func.value.id
                    from errors import PyCSLSemanticError as _PyCSLSemErr189
                    raise _PyCSLSemErr189(
                        f"{_fd189.name!r} binds {_nm189!r} to more than one class "
                        f"({', '.join(sorted(_bd189[_nm189]))}) and then calls "
                        f"`{_nm189}.{_ca189.func.attr}(...)` (ROUTE #189). A record local "
                        f"is mapped to ONE class, the last binding the scanner reaches, so "
                        f"the call would carry that class's contract on every path — "
                        f"measured: a two-branch receiver proved the other class's result. "
                        f"Give each class its own local.",
                        stage="whyml-emit", code="PYCSL-R189-AMBIGUOUS-RECEIVER-CLASS")
    # (#49) ROUTE #233 — `except E as e` BINDS AN EXCEPTION OBJECT THE MODEL DOES NOT CARRY.
    # The handler lowers to `with E ->` (no payload), so a read of `e` in its body fell
    # through Module 6's last-branch opaque `val constant e`, ONE value shared by every
    # handler in the module — measured: two handlers storing `a = e` / `b = e` for two
    # different `ValueError`s PROVED `a == b` (CPython False: two distinct objects). Same
    # mechanism as the unbound `match` capture this route repairs. Refused in a
    # non-trusted function of the main file; census: 0 such reads in either corpus.
    if _t175 is not None:
        _tr233 = {str(_f.get("name", "")) for _f in (ir_data.get("functions", []) or [])
                  if _f.get("trusted") or _f.get("abstract") or _f.get("trusted_parent")}
        _ow233 = {}
        for _k233 in _ast175.walk(_t175):
            if isinstance(_k233, _ast175.ClassDef):
                for _m233 in _k233.body:
                    if isinstance(_m233, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                        _ow233[id(_m233)] = _k233.name
        for _fd233 in _ast175.walk(_t175):
            if not isinstance(_fd233, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                continue
            if ((f"{_ow233[id(_fd233)].lower()}__{_fd233.name}" if id(_fd233) in _ow233
                 else _fd233.name) in _tr233):
                continue
            for _h233 in _ast175.walk(_fd233):
                if not (isinstance(_h233, _ast175.ExceptHandler) and _h233.name):
                    continue
                for _st233 in _h233.body:
                    for _n233 in _ast175.walk(_st233):
                        if (isinstance(_n233, _ast175.Name) and _n233.id == _h233.name
                                and isinstance(_n233.ctx, _ast175.Load)):
                            from errors import PyCSLSemanticError as _PyCSLSemErr233
                            raise _PyCSLSemErr233(
                                f"{_fd233.name!r} reads the exception object "
                                f"{_h233.name!r} bound by `except ... as {_h233.name}` "
                                f"(ROUTE #233). The handler is modelled without its "
                                f"exception object, so every such read would be ONE "
                                f"opaque constant shared by all handlers — measured: "
                                f"two different exceptions compared equal. Do not read "
                                f"the bound exception, or mark the function `\\trusted`.",
                                stage="whyml-emit", code="PYCSL-R233-EXCEPT-AS-READ")
    if "R31_UNMODELLED_LIST_TRUTHINESS" in _mlw:
        # ROUTE #31 (relaunch #45) — the Python truthiness of a list local whose
        # LENGTH the model does not carry. `_to_bool` used to answer `true` for
        # EVERY array local ("always allocated"), and an EMPTY list is FALSY, so
        # `a = []; if a: return 1; return 2` proved `\result == 1` in the default
        # model while Python returns 2 (witness 1015). The faithful answers — the
        # literal size for an unconditionally bound local, the sidecar `X_len` for
        # an append target — are emitted where they exist; this is the residue.
        from errors import PyCSLSemanticError as _PyCSLSemErr31
        raise _PyCSLSemErr31(
            "the truthiness of a list local in this module is not interpreted "
            "(ROUTE #31): the model does not carry that list's length here, and "
            "`true` — which is what the emitter used to answer, on the grounds "
            "that the array is always allocated — is FALSE of an empty list, "
            "which Python treats as falsy. Compare against `len(...)` explicitly, "
            "or bind the list unconditionally to a literal so its size is known.",
            stage="whyml-emit", code="PYCSL-R31-UNMODELLED-LIST-TRUTHINESS")
    if "R30_UNINTERPRETED_PATTERN" in _mlw:
        from errors import PyCSLSemanticError as _PyCSLSemErr30
        raise _PyCSLSemErr30(
            "a `match` pattern in this module is not interpreted (ROUTE #30): "
            "its arm has no faithful lowering, and every literal stand-in makes "
            "a contract that is FALSE of the program provable — an always-true "
            "condition takes the arm whatever the subject is, an always-false "
            "one skips it even when Python matches, and an undeclared "
            "constructor name becomes a Why3 VARIABLE pattern, which matches "
            "everything. Supported today: a literal pattern, `_`, a capture, an "
            "or-pattern of those, and a constructor pattern of a declared "
            "`#@ datatype`. Sequence, mapping, class and as-patterns are not.",
            stage="whyml-emit", code="PYCSL-R30-UNINTERPRETED-PATTERN")
    # (#49) ROUTE #157 — A SLICE ASSIGNMENT RESIZES THE LIST UNLESS THE SOURCE IS EXACTLY
    # AS LONG AS THE SLICE, AND THE MODEL IS A FIXED-LENGTH `Array.blit`. MEASURED (gen #29):
    #     a = [1, 2]; a[2:] = [3, 4]; return len(a)      #@ ensures \result != 4  <-- PROVED
    # (CPython 4): the blit copied `len(a) - 2 = 0` elements and the length stayed 2. The
    # faithful lowering (a resize) is a new value shape; the sound one is to make EQUAL
    # LENGTH a proof obligation, so a length-preserving slice store keeps its model and a
    # resizing one fails to prove. The obligation is added HERE, on the emitted text, because
    # `_handle_array_slice_set_stmt` is a CONVERTED mirror method: the emitter's own
    # per-element hint `assert { forall i : int. (0 <= i /\ i < (W)) -> (D[(L) + i] = S[i]) }`
    # follows every blit and names the width `W` and the (identifier) source `S`, so the
    # length assertion is appended right after it. Census: 0 slice assignments in the
    # mirrors or python-reference; 13 in pycsl-reference (11 files).
    import re as _re157
    _mlw = _re157.sub(
        r"(assert \{ forall i : int\. \(0 <= i /\\ i < \((?P<w>.*)\)\) -> "
        r"\((?P<d>.*)\[\((?P<lo>.*)\) \+ i\] = (?P<s>[A-Za-z_][A-Za-z0-9_']*)\[i\]\) \})",
        lambda _m157: (_m157.group(1) + " ;\n    assert { Array.length "
                       + _m157.group("s") + " = (" + _m157.group("w") + ") }"),
        _mlw)
    # (#49) ROUTE #159 — A PLACEHOLDER-BOUND ARRAY'S WHY3 LENGTH IS NOT THE LIST'S. `xs = []`
    # lowers to the immutable binding `let xs = (Array.make 1024 0) in`, whose Why3 length is
    # 1024 for good, while the Python list — never appended to (an append target is a
    # `ref Seq` or carries an `xs_len` sidecar) — has length 0. So `xs[0] = 5` proved
    # `no_exception IndexError` against 1024 (CPython raises). The Module 6 read handler now
    # uses the faithful length where it knows the size; the STORE handler cannot see it (the
    # size fold is withdrawn by the store itself), so the bounds obligation is corrected
    # here, on the emitted text: inside a `let X = (Array.make 1024 0) in` scope with no
    # `X_len` sidecar and no later rebinding of `X`, `in_bounds ((Array.length X))` becomes
    # `in_bounds (0)` — strictly STRONGER, so no proof can become easier.
    import re as _re159
    for _m159 in list(_re159.finditer(
            r"let ([A-Za-z_][A-Za-z0-9_']*) = \(Array\.make 1024 0\) in", _mlw)):
        _x159 = _m159.group(1)
        _tail159 = _mlw[_m159.end():]
        _stop159 = _re159.search(
            r"\blet " + _re159.escape(_x159) + r"\b|\n  let |\n  val |\nend", _tail159)
        _scope159 = _tail159[:_stop159.start()] if _stop159 else _tail159
        if _re159.search(r"\b" + _re159.escape(_x159) + r"_len\b", _mlw):
            continue
        _fixed159 = _scope159.replace(
            "in_bounds ((Array.length " + _x159 + "))", "in_bounds (0)")
        if _fixed159 != _scope159:
            _mlw = _mlw[:_m159.end()] + _fixed159 + _tail159[len(_scope159):]
    # (#49) gen #31 — THE SAME LIE, ONE FUNCTION FURTHER OUT: A FUNCTION THAT RETURNS THE
    # EMPTY-LIST PLACEHOLDER CERTIFIED `\length(\result) == 1024`.
    #
    #     #@ ensures \length(\result) == 1024
    #     def mk() -> list:
    #         return []
    #     [+] Verification SUCCESS! All contracts formally proven.
    #
    # Python returns a list of length 0. The TRUE clause `== 0` was REFUSED. Both halves
    # hold for `xs = []; return xs` as well. This is a certified FALSE postcondition on
    # ordinary total Python — no `no_exception`, no opt-in, no `\trusted` anywhere.
    #
    # Same mechanism as #159 directly above (`[]` lowers to `(Array.make 1024 0)`, whose
    # Why3 length is 1024 for good), and #159's repair does not reach it: that one corrects
    # ONE obligation (`in_bounds`) inside ONE syntactic scope (a `let` binding). The
    # RETURN carries the false length ACROSS THE FUNCTION BOUNDARY, where a caller assumes
    # it — and `1024 = <the real length>` is contradictory, which makes every downstream
    # goal vacuously provable. That modular false-green is the one recorded in
    # `getting-better/20260718-0633-stmt-list-append-mutation-wall-response.md`, where
    # `--check-vacuity` did not flag it either.
    #
    # WHY THE FIX IS HERE AND NOT AT THE LITERAL. `Array.make 1024 0` is spelled the same
    # for TWO different jobs: the CAPACITY of an append target (whose real length is
    # carried by an `X_len` sidecar, `statements.py`) and the VALUE of an empty list that is
    # never appended to. A Why3 array's length IS its capacity, so one literal cannot serve
    # both, and changing it at the producer breaks the first job. Separating the two uses is
    # the real repair and is recorded as the named capability in
    # `getting-better/open-routes/finding-empty-list-literal-length-is-1024.md`; this is the
    # fail-closed correction of the consequence, in #159's own idiom.
    #
    # STRICTLY STRONGER, SO NO PROOF CAN BECOME EASIER: 0 is the true length, and it is the
    # smallest one, so every `Array.length result`-shaped obligation gets harder. Measured:
    # the false `== 1024` stops proving and the true `== 0` starts.
    #
    # FAIL-CLOSED BY CONSTRUCTION. It fires only when the function's FINAL expression is
    # the placeholder itself, or a local bound ONCE to the placeholder with no `_len`
    # sidecar, no element store and no rebinding. A function that returns the placeholder on
    # only one branch ends in a `try`/`Return` form, does not match, and is left alone.
    # THE IR-LEVEL FILTER, AND THE CENSUS THAT FORCED IT. Keying on the emitted TEXT alone
    # is WRONG, because `[0] * 1024` emits the SAME `(Array.make 1024 0)` as `[]` does —
    # measured in the corpus emission, where a `disk` field initialised to 1024 zeroes and
    # an `audit` field with an `audit_len` sidecar both wear that spelling. Without this
    # filter, `def mk() -> list: return [0] * 1024` with the TRUE clause
    # `\length(\result) == 1024` STOPPED PROVING. Not unsound — it makes a true claim
    # unprovable, the safe direction — but a real completeness regression, and one the
    # corpus byte-diff could not see, because no corpus file happens to return a
    # 1024-element literal from a function carrying a `\length(\result)` contract.
    #
    # So the IR names the functions and the text only LOCATES them: a function qualifies
    # only if its final statement returns an EMPTY `ArrayLit`, directly or through a local
    # bound once to one. `ir_data` is right here; nothing has to be inferred from bytes.
    # The filter can only REDUCE firing, so the byte-inert corpus measurement taken before
    # it was added still stands.
    _el_names = set()
    for _f_el in (ir_data.get("functions", []) or []):
        _b_el = _f_el.get("body") or []
        _last_el = _b_el[-1] if _b_el else None
        if not isinstance(_last_el, dict) or _last_el.get("stmt") != "Return":
            continue
        _rv_el = _last_el.get("value") or {}
        if not isinstance(_rv_el, dict):
            continue
        if _rv_el.get("type") == "ArrayLit" and not (_rv_el.get("elts") or []):
            _el_names.add(_f_el.get("name"))
            continue
        if _rv_el.get("type") != "Var":
            continue
        # the indirect spelling: `xs = []` … `return xs`, with `xs` bound exactly once and
        # to the empty literal. Anything else about `xs` is handled by the body guards
        # below (no sidecar, no store, exactly two textual occurrences).
        _vn_el = _rv_el.get("name")
        _binds_el = [_st_el for _st_el in _b_el
                     if isinstance(_st_el, dict) and _st_el.get("stmt") == "Assign"
                     and _st_el.get("target") == _vn_el]
        if len(_binds_el) == 1:
            _bv_el = _binds_el[0].get("value") or {}
            if (isinstance(_bv_el, dict) and _bv_el.get("type") == "ArrayLit"
                    and not (_bv_el.get("elts") or [])):
                _el_names.add(_f_el.get("name"))
    _el_whyml = set()
    for _n_el in _el_names:
        if not _n_el:
            continue
        _el_whyml.add(str(_n_el))
        _el_whyml.add(str(_n_el).split(".")[-1])
    import re as _reEL
    _PLH_EL = "(Array.make 1024 0)"
    if _el_whyml and _PLH_EL in _mlw and "(Array.length result)" in _mlw:
        _cuts_EL = [_m.start() for _m in
                    _reEL.finditer(r"\n  (?:let|val)\b", _mlw)] + [len(_mlw)]
        _out_EL = [_mlw[:_cuts_EL[0]]] if _cuts_EL else [_mlw]
        for _k_EL in range(len(_cuts_EL) - 1):
            _blk_EL = _mlw[_cuts_EL[_k_EL]:_cuts_EL[_k_EL + 1]]
            _eq_EL = _reEL.search(r"\n  =\n", _blk_EL)
            if not _eq_EL or "(Array.length result)" not in _blk_EL[:_eq_EL.start()]:
                _out_EL.append(_blk_EL)
                continue
            # THE NAME GATE. A method `C.mk` is emitted as `c__mk`, a free function as
            # `mk`; both are matched by comparing the block's WhyML name and its tail after
            # the last `__` against the IR names collected above. No match -> untouched.
            _bn_EL = _reEL.match(r"\n  (?:let|val)\s+(?:function\s+|rec\s+)*"
                                 r"([A-Za-z_][A-Za-z0-9_']*)", _blk_EL)
            _nm_ok_EL = bool(_bn_EL) and (_bn_EL.group(1) in _el_whyml
                                          or _bn_EL.group(1).split("__")[-1] in _el_whyml)
            if not _nm_ok_EL:
                _out_EL.append(_blk_EL)
                continue
            _hdr_EL = _blk_EL[:_eq_EL.end()]
            _body_EL = _blk_EL[_eq_EL.end():]
            _lines_EL = [_l.strip() for _l in _body_EL.splitlines()
                         if _l.strip() and _l.strip() != "end"]
            _hit_EL = False
            if _lines_EL and _lines_EL[-1] == _PLH_EL:
                _hit_EL = True
            elif _lines_EL and _reEL.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*", _lines_EL[-1]):
                _nm_EL = _lines_EL[-1]
                _esc_EL = _reEL.escape(_nm_EL)
                if (_body_EL.count("let %s = %s in" % (_nm_EL, _PLH_EL)) == 1
                        and _body_EL.count("let %s = " % _nm_EL) == 1
                        and not _reEL.search(r"\b" + _esc_EL + r"_len\b", _blk_EL)
                        and not _reEL.search(r"\b" + _esc_EL + r"\s*(?:\[|<-|:=)", _body_EL)
                        # THE OCCURRENCE COUNT IS THE REAL GUARD, and the version without it
                        # was wrong. Excluding stores and sidecars is not enough: a local can
                        # be handed to a CALLEE that appends to it
                        # (`xs = []; fill(xs); return xs`), and then the Python length is not
                        # 0 either — claiming 0 would swap one false length for another, and
                        # the new one is WORSE because it is the provable direction. So the
                        # name must occur EXACTLY TWICE in the body: its binding, and the
                        # final expression. Anything that so much as MENTIONS it elsewhere is
                        # left alone.
                        and len(_reEL.findall(r"\b" + _esc_EL + r"\b", _body_EL)) == 2):
                    _hit_EL = True
            if _hit_EL:
                _hdr_EL = _hdr_EL.replace("(Array.length result)", "(0)")
            _out_EL.append(_hdr_EL + _body_EL)
        _mlw = "".join(_out_EL)
    # (#49) ROUTE #269 — THE DIVERGENCE A STUB FORGOT (R1/R2 + R3), decided on the EMISSION.
    # Route #263 made `_handle_dotted_call`'s stub of a `#@ \diverges` method carry
    # `diverges`, but that is ONE of many stub producers: `C().spin(k)` reaches the generic
    # arm as a receiver-less `val spin_1`, and the Module 5 mirror's bespoke handlers call
    # the `\diverges` dispatcher through the fixed `val self__py_expr_to_ir_1`
    # (`abstract_ops._SELF_DISPATCH_VAL_DECLS`). A bodyless `val` TERMINATES for Why3, so
    # a caller claiming termination got it for free. MEASURED at 8b0bfbbd: `C().spin(k);
    # return 7` PROVED `\result == 7` (CPython: never returns).
    # (1) EVERY plain program `val` whose name is a stub spelling `<...>_<m>_<arity>
    # [_c<h>][_<k>]` of a `\diverges` function or method `m` of this unit carries
    # `diverges` — whichever producer minted it. Matched by NAME (as #263/#167 do): an
    # ambiguous match makes MORE callers owe `\diverges`, never fewer. Logic `val
    # function`/`predicate`/`ghost`/`constant` symbols are model operations, not call
    # stubs, and are left alone.
    # (2) An emitted `let`/`with` of a `\diverges` function carries `diverges` even when a
    # second producer wrote its header (the bespoke mirror scaffolds hard-code it) — the
    # declaration only REMOVES a termination goal the source asked to remove.
    # (3) R3: a call that VANISHES from the emission (an opaque comprehension, generator or
    # lambda lowering: `[self.spin(x) for x in xs]` -> `list_comp 0`, `sum(self.spin(x)
    # for x in xs)` -> `sum_1 (any int)`) carries no obligation at all — PROVED `\result
    # == 7` at 8b0bfbbd; with a RAISING callee it PROVED under `no_exception \all`. Such a
    # call to a `\diverges` callee from a function that is not, or to a callee that may
    # raise, must be visible in what the function's emission reaches; otherwise refused.
    # No `\diverges` function and no comprehension call to a raising one -> byte-identical.
    # INLINE (check-mirror-coverage); `_run_pipeline`'s mirror twin is `\trusted`.
    from module6_whyml.identifiers import whyml_ident as _wid269
    _mn269 = {}
    for _f269 in _fn263:
        _st269 = _f269.get("self_type")
        _mn269[_f269["name"]] = (
            _f269["name"][len(_st269) + 2:]
            if (_f269.get("kind") == "method" and isinstance(_st269, str) and _st269
                and _f269["name"].startswith(_st269.lower() + "__"))
            else _f269["name"])
    _dvm269 = {_mn269[f["name"]] for f in _fn263 if f.get("diverges")}
    _pat269 = [_re.compile(r"(?:^|_)" + _re.escape(_m) + r"_\d+(?:_c\d+)?(?:_\d+)?$")
               for _m in sorted(_dvm269)]
    if _pat269:
        _o269 = []
        _p269 = 0
        for _mv269 in _re.finditer(r"\n  val\s+([A-Za-z_][A-Za-z0-9_']*)", _mlw):
            _v269 = _mv269.group(1)
            if _v269 in ("ghost", "function", "predicate", "constant") or not any(
                    _q.search(_v269) for _q in _pat269):
                continue
            _e269 = _re.compile(r"\n(?!    )").search(_mlw, _mv269.end())
            _end269 = _e269.start() if _e269 else len(_mlw)
            if _end269 < _p269 or _re.search(r"\bdiverges\b", _mlw[_mv269.start():_end269]):
                continue
            _o269.append(_mlw[_p269:_end269])
            _o269.append("\n    diverges")
            _p269 = _end269
        _o269.append(_mlw[_p269:])
        _mlw = "".join(_o269)
        _ins269 = []
        for _f269 in _fn263:
            # (an imported, hence trusted, method a bespoke lowering still emits WITH a body
            # — the Module 5 handlers inside `pycsl.mlw` — is covered too: only an emitted
            # `let`/`with` is touched, never a bodyless `val`)
            if not _f269.get("diverges"):
                continue
            for _mh269 in _re.finditer(r"\n  (?:let|with)\s+((?:(?:rec|function|ghost|lemma)\s+)*)"
                                       + _re.escape(_wid269(_f269["name"])) + r"(?![\w'])", _mlw):
                if _mh269.group(1).strip() not in ("", "rec"):
                    continue
                _eq269 = _mlw.find("\n  =", _mh269.end())
                _nb269 = _re.compile(r"\n  (?:let|val|with)\b").search(_mlw, _mh269.end())
                if _eq269 < 0 or (_nb269 and _nb269.start() < _eq269):
                    continue
                if not _re.search(r"\b(?:diverges|variant)\b", _mlw[_mh269.start():_eq269]):
                    _ins269.append(_eq269)
        for _i269 in sorted(set(_ins269), reverse=True):
            _mlw = _mlw[:_i269] + "\n    diverges" + _mlw[_i269:]
    # (#49) ROUTE #273 — THE DEFAULT THAT NEVER RAN. A nested `def`/`lambda`/`class` is a
    # STATEMENT (an expression, for `lambda`) of the enclosing function, and CPython runs
    # part of it right there: every default-argument expression, every decorator
    # expression, every (non-postponed) annotation, every base/keyword of a class and
    # every statement of a class body. PyCSL lifts the nested def into its own function
    # (Module 5) and lowers a lambda to `{Lambda, params, body}`, and both DROP those
    # expressions, so their raise, effect and divergence vanish. MEASURED at 5a307a33
    # (witnesses-r273/): `def inner(y: int = 10 // x)` under `no_exception \all` with
    # `x == 0` PROVED (CPython: ZeroDivisionError); `def inner(y: int = push(xs))` with
    # `push` writing `xs[0] = 5` PROVED `\result == 0` (CPython 5); `class K: v = 10 // x`
    # and `class K: v = push(xs)` PROVED likewise; `def inner(x: int = spin())` and
    # `lambda x=spin(): x` with a `\diverges` `spin` PROVED termination (CPython: hangs).
    # RULE (fail-closed, AST-level): inside a LOWERED function (not `\trusted`/
    # `\abstract`, together with everything nested in it), every nested def/lambda
    # default must be a literal, a bare name, a signed numeric literal or a display of
    # those; every decorator of a nested def/class a (dotted) name; every annotation and
    # class base a type-shaped expression (names, attributes, subscripts, tuples/lists,
    # string literals, `|`); and a nested class body may hold only defs, nested classes,
    # `pass`, docstrings and name bindings of such literal values. None of those can
    # call, raise (beyond the NameError of an unbound name, route #264's ground) or loop,
    # so nothing the model drops was ever evaluated with effect — which is also why
    # route #269's vanished-call scan has nothing left to walk in these positions.
    # Module-level defs/classes (import time) are not a function's evaluation and are
    # outside this rule. BLAST RADIUS, measured before landing (CPython-`ast` prototype of
    # THIS predicate): pycsl-reference 0, self-annotate mirror 0, pycsl_lib 1
    # (`json/encoder.py::iterencode`, `self.allow_nan`, already refused), python-reference
    # 1 (0078, a class body `x = Desc()`).
    # INLINE (check-mirror-coverage); `_run_pipeline`'s mirror twin is `\trusted`.
    from frontend import pure_ast as _A273
    _FN273 = (_A273.FunctionDef, _A273.AsyncFunctionDef)
    _TY273 = (_A273.Name, _A273.Attribute, _A273.Subscript, _A273.Tuple, _A273.List,
              _A273.Constant, _A273.BinOp, _A273.BitOr, _A273.Load)
    _bad273 = []
    _st273 = [unified_ast]
    _low273 = []
    while _st273:
        _n273 = _st273.pop()
        if isinstance(_n273, _FN273):
            if not (getattr(_n273, "csl_trusted", False)
                    or getattr(_n273, "csl_abstract", False)):
                _low273.append(_n273)
            continue
        _st273.extend(_A273.iter_child_nodes(_n273))
    for _F273 in _low273:
        for _N273 in _A273.walk(_F273):
            if _N273 is _F273:
                continue
            _vals273 = []   # (expression, must-be-literal?) pairs evaluated at definition
            _why273 = ""
            if isinstance(_N273, _FN273 + (_A273.Lambda,)):
                _a273 = _N273.args
                _vals273 += [(_d, True) for _d in list(_a273.defaults or [])
                             + [_k for _k in (_a273.kw_defaults or []) if _k is not None]]
                if not isinstance(_N273, _A273.Lambda):
                    _vals273 += [(_x.annotation, False) for _x in (
                        list(getattr(_a273, "posonlyargs", None) or []) + list(_a273.args or [])
                        + list(_a273.kwonlyargs or []) + [_v for _v in (_a273.vararg, _a273.kwarg)
                                                          if _v is not None])]
                    _vals273.append((_N273.returns, False))
            elif isinstance(_N273, _A273.ClassDef):
                _vals273 += [(_b, False) for _b in list(_N273.bases or [])
                             + [_k.value for _k in (_N273.keywords or [])]]
                for _s273 in _N273.body:
                    if isinstance(_s273, _FN273 + (_A273.ClassDef, _A273.Pass)):
                        continue
                    if (isinstance(_s273, _A273.Expr)
                            and isinstance(_s273.value, _A273.Constant)):
                        continue
                    if (isinstance(_s273, _A273.Assign)
                            and all(isinstance(_t, _A273.Name) for _t in _s273.targets)):
                        _vals273.append((_s273.value, True))
                        continue
                    if (isinstance(_s273, _A273.AnnAssign)
                            and isinstance(_s273.target, _A273.Name)):
                        _vals273 += [(_s273.value, True), (_s273.annotation, False)]
                        continue
                    _why273 = "class body statement `" + _A273.unparse(_s273)[:60] + "`"
                    break
            else:
                continue
            for _d273 in getattr(_N273, "decorator_list", None) or []:
                _q273 = _d273
                while isinstance(_q273, _A273.Attribute):
                    _q273 = _q273.value
                if not _why273 and not isinstance(_q273, _A273.Name):
                    _why273 = "decorator `@" + _A273.unparse(_d273) + "`"
            for _e273, _lit273 in _vals273:
                if _why273 or _e273 is None:
                    continue
                _ok273 = True
                _wk273 = [_e273]
                while _wk273 and _ok273:
                    _x273 = _wk273.pop()
                    if _lit273:
                        if isinstance(_x273, (_A273.Constant, _A273.Name)):
                            continue
                        if (isinstance(_x273, _A273.UnaryOp)
                                and isinstance(_x273.op, (_A273.USub, _A273.UAdd))
                                and isinstance(_x273.operand, _A273.Constant)):
                            continue
                        if isinstance(_x273, (_A273.Tuple, _A273.List, _A273.Set)):
                            _wk273.extend(_x273.elts)
                            continue
                        if (isinstance(_x273, _A273.Dict)
                                and all(_k is not None for _k in _x273.keys)):
                            _wk273.extend(list(_x273.keys) + list(_x273.values))
                            continue
                        _ok273 = False
                    else:
                        if not isinstance(_x273, _TY273 + (_A273.expr_context,)) or (
                                isinstance(_x273, _A273.BinOp)
                                and not isinstance(_x273.op, _A273.BitOr)):
                            _ok273 = False
                        else:
                            _wk273.extend(_A273.iter_child_nodes(_x273))
                if not _ok273:
                    _why273 = ("default value `" if _lit273 else "annotation/base `") \
                        + _A273.unparse(_e273)[:60] + "`"
            if _why273:
                _bad273.append((_F273.name, getattr(_N273, "lineno", 0),
                                getattr(_N273, "name", "lambda"), _why273))
    if _bad273:
        from errors import PyCSLSemanticError as _PyCSLSemErr273
        raise _PyCSLSemErr273(
            f"'{_bad273[0][0]}' defines the nested '{_bad273[0][2]}' (line {_bad273[0][1]}) "
            f"with the {_bad273[0][3]}, which Python EVALUATES when the def/class/lambda "
            f"is executed inside '{_bad273[0][0]}'. PyCSL lifts a nested def/class (and "
            f"lowers a lambda) WITHOUT that evaluation, so its exception, its effect and "
            f"its divergence would vanish from the model. Use a literal default (e.g. "
            f"`None`, then compute the value inside the body), a plain-name decorator, a "
            f"type-shaped annotation, a class body of literal attributes, or move the "
            f"def/class to module level"
            f"{'' if len(_bad273) == 1 else f' (also: {_bad273[1:]})'}.",
            filename=args.file, stage="ir-semantic",
            code="PYCSL-SEM-DEF-TIME-EVALUATION")
    # (3) R3 — the callees that may RAISE: a declared `raises`, or (with a body) an
    # escaping `raise`, closed transitively over call names (an over-approximation).
    from module6_whyml.ir_scanner import IRScanner as _IRS269
    _rf269 = set()
    _cn269 = {}
    for _f269 in _fn263:
        if any(isinstance(_r, dict) and _r.get("exc_type")
               for _r in ((_f269.get("contracts") or {}).get("raises") or [])):
            _rf269.add(_f269["name"])
        if _f269.get("trusted") or _f269.get("abstract"):
            continue
        if _IRS269.collect_escaping_exceptions(_f269.get("body") or []):
            _rf269.add(_f269["name"])
        _cs269 = set()
        _w269 = [_f269.get("body")]
        while _w269:
            _x269 = _w269.pop()
            if isinstance(_x269, dict):
                if _x269.get("type") == "Call" and isinstance(_x269.get("func"), str):
                    _cs269.add(_x269["func"].split(".")[-1])
                _w269.extend(_x269.values())
            elif isinstance(_x269, list):
                _w269.extend(_x269)
        _cn269[_f269["name"]] = _cs269
    _chg269 = True
    while _chg269:
        _chg269 = False
        _rm269 = {_mn269[_n] for _n in _rf269}
        for _n269, _cs269 in _cn269.items():
            if _n269 not in _rf269 and _cs269 & _rm269:
                _rf269.add(_n269)
                _chg269 = True
    _rm269 = {_mn269[_n] for _n in _rf269}
    # ... and a callee with a PRECONDITION: a vanished call is never checked against it, and
    # a violated one is where an implicit exception lives (`[self.inv(x) for x in xs]` with
    # `inv` requiring `k > 0` over `10 // k` PROVED `no_exception \all` at 8b0bfbbd; CPython:
    # ZeroDivisionError). Not transitive: a caller that applies it visibly proves it.
    _rm269 |= {_mn269[f["name"]] for f in _fn263
               if any(_r != {"type": "Bool", "value": True}
                      for _r in ((f.get("contracts") or {}).get("requires") or []))}
    # (#49) ROUTE #274 — THE COMPREHENSION THAT SWALLOWED A WRITE. ... and a callee with a
    # non-empty FRAME: a declared `assigns` other than `\nothing`, or (frame undeclared,
    # body lowered) a body that writes a field/element/slice, deletes an element, or calls
    # a collection mutator on a receiver — closed transitively over undeclared-frame
    # callers. MEASURED at 5a307a33 (witnesses-r274/): `ys = [push(c) for y in xs]`,
    # `{y: push(c) ...}`, `{push(c) ...}`, `sum(push(c) for y in xs)` and the EAGER first
    # iterable `(y for y in range(push(c)))`, with `push` declaring `assigns c.v` and
    # writing `c.v = 5`, all PROVED `\result == c.v == 0` (CPython 5). A visible call to
    # the same callee elsewhere does NOT excuse it here (unlike a raise or a precondition,
    # whose obligation one visible application does discharge for the name): each
    # application is one more write, and `push(c); [push(c) for y in [1, 2]]` PROVED
    # `c.v == 1` (CPython 3). Likewise a receiver mutator (`[out.append(y) for y in xs]`
    # PROVED `len(out) == 0`; CPython 1) in such a position is refused.
    _fx269 = set()
    _fxb269 = {}
    _FR274 = ("DictLit", "ArrayLit", "ListLit", "SetLit", "ListComp", "DictComp", "SetComp")
    for _f269 in _fn263:
        _as269 = (_f269.get("contracts") or {}).get("assigns") or []
        if any(not (isinstance(_a, dict) and _a.get("type") == "Nothing") for _a in _as269):
            _fx269.add(_f269["name"])
            continue
        if _as269 or _f269.get("trusted") or _f269.get("abstract"):
            continue
        # A write into a FRESH LOCAL container (a non-parameter name bound only by
        # `Assign`s of a literal display or comprehension, and by nothing else) stays
        # inside the call: `new: Dict = {}; new[k] = v` is not a frame. Every other
        # write base (a parameter, `self`, a field path, any name bound otherwise) is.
        _fv274 = {}
        _w269 = [_f269.get("body")]
        while _w269:
            _x269 = _w269.pop()
            if isinstance(_x269, dict):
                if _x269.get("stmt") == "Assign" and isinstance(_x269.get("target"), str):
                    _fv274[_x269["target"]] = _fv274.get(_x269["target"], True) and (
                        isinstance(_x269.get("value"), dict)
                        and _x269["value"].get("type") in _FR274)
                else:
                    for _k274 in ("target", "targets"):
                        _tv274 = _x269.get(_k274)
                        for _t274 in (_tv274 if isinstance(_tv274, list) else [_tv274]):
                            if isinstance(_t274, str):
                                _fv274[_t274] = False
                _w269.extend(_x269.values())
            elif isinstance(_x269, list):
                _w269.extend(_x269)
        for _p274 in list(_f269.get("formal_params") or []) + ["self"]:
            _fv274[_p274] = False
        _w269 = [_f269.get("body")]
        while _w269:
            _x269 = _w269.pop()
            if isinstance(_x269, dict):
                _b274 = 0
                if _x269.get("stmt") in ("FieldAssign", "FieldAugAssign", "ArraySet",
                                          "ArraySliceSet", "DelSubscript"):
                    _b274 = _x269.get("object") if _x269.get("stmt") in (
                        "FieldAssign", "FieldAugAssign") else _x269.get(
                            "array", _x269.get("value", _x269.get("target")))
                elif (_x269.get("type") == "Call" and isinstance(_x269.get("func"), str)
                        and "." in _x269["func"]
                        and _x269["func"].rsplit(".", 1)[1] in _IRS269._MUTATING_METHODS):
                    _b274 = _x269["func"].split(".")[0]
                if _b274 != 0:
                    while isinstance(_b274, dict):
                        _b274 = (_b274.get("name") if _b274.get("type") == "Var"
                                 else _b274.get("value", _b274.get("object")))
                    if not (isinstance(_b274, str) and _fv274.get(_b274) is True):
                        _fx269.add(_f269["name"])
                        break
                _w269.extend(_x269.values())
            elif isinstance(_x269, list):
                _w269.extend(_x269)
        if _f269["name"] not in _fx269:
            _fxb269[_f269["name"]] = _cn269.get(_f269["name"], set())
    _chg269 = True
    while _chg269:
        _chg269 = False
        _fm269 = {_mn269[_n] for _n in _fx269}
        for _n269, _cs269 in _fxb269.items():
            if _n269 not in _fx269 and _cs269 & _fm269:
                _fx269.add(_n269)
                _chg269 = True
    _fm269 = {_mn269[_n] for _n in _fx269}
    _viol269 = []
    _vfx269 = []
    _dvh269 = set()
    _blk269 = None
    for _f269 in _fn263:
        if _f269.get("abstract") or _f269.get("lemma"):
            continue
        _hid269 = set()
        _hfx269 = set()
        _irc274 = {}
        _w269 = [(_f269.get("body"), False)]
        while _w269:
            _x269, _in269 = _w269.pop()
            if isinstance(_x269, dict):
                _in2 = _in269 or _x269.get("type") in (
                    "ListComp", "SetComp", "DictComp", "GenExp", "Lambda")
                if _x269.get("type") == "Call" and isinstance(_x269.get("func"), str):
                    _m274 = _x269["func"].split(".")[-1]
                    _irc274[_m274] = _irc274.get(_m274, 0) + 1
                if (_in269 and _x269.get("type") == "Call"
                        and isinstance(_x269.get("func"), str)):
                    _m269 = _x269["func"].split(".")[-1]
                    if _m269 in _dvm269 or _m269 in _rm269:
                        _hid269.add(_m269)
                    if _m269 in _fm269 or ("." in _x269["func"]
                                           and _m269 in _IRS269._MUTATING_METHODS):
                        _hfx269.add(_x269["func"])
                _w269.extend((_v, _in2) for _v in _x269.values())
            elif isinstance(_x269, list):
                _w269.extend((_v, _in269) for _v in _x269)
        if not _hid269 and not _hfx269:
            continue
        if _blk269 is None:
            # name -> identifiers its emitted BODY mentions; `val`s have no body.
            _blk269 = {}
            _vl269 = set()
            _btx274 = {}   # (#274) let/with name -> its emitted body TEXT
            _vtx274 = {}   # (#274) val name -> its whole declaration text
            _ct269 = [_m.start() for _m in _re.finditer(r"\n  (?:let|val|with)\b", _mlw)]
            _ct269.append(len(_mlw))
            for _k269 in range(len(_ct269) - 1):
                _b269 = _mlw[_ct269[_k269]:_ct269[_k269 + 1]]
                _hm269 = _re.match(r"\n  (let|val|with)\s+(?:(?:rec|function|ghost|lemma|"
                                   r"predicate|constant)\s+)*([A-Za-z_][A-Za-z0-9_']*)", _b269)
                if not _hm269:
                    continue
                if _hm269.group(1) == "val":
                    _vl269.add(_hm269.group(2))
                    _vtx274[_hm269.group(2)] = _vtx274.get(_hm269.group(2), "") + _b269
                    continue
                _q269 = _b269.find("\n  =")
                _btx274[_hm269.group(2)] = (_btx274.get(_hm269.group(2), "")
                                            + (_b269[_q269:] if _q269 >= 0 else ""))
                _blk269.setdefault(_hm269.group(2), set()).update(_re.findall(
                    r"[A-Za-z_][A-Za-z0-9_']*", _b269[_q269:] if _q269 >= 0 else ""))
        _wf269 = _wid269(_f269["name"])
        if _f269.get("trusted") and _wf269 not in _blk269:
            # a trusted function is a bodyless `val` — unless a bespoke lowering still
            # emits its body (the imported Module 5 handlers inside `pycsl.mlw`)
            continue
        # (#274) A hidden write is MODELLED only if the function's OWN emitted blocks
        # (itself and its bespoke `<name>__*` walkers — e.g. the Module 5 mirror's
        # concrete `_cc_<k>` comprehension loops) apply the callee at least as many
        # times as its IR calls it: one visible `push(c)` must not cover a second,
        # vanished one. A callee whose every emitted spelling is a `val` WITHOUT a
        # `writes` clause has no modelled effect to lose (its visible application is
        # pure for Why3 too — that is the stub's own frame, not this lowering's).
        # A receiver mutator (`out.append(y)`) has no countable spelling: refused.
        _own274 = "".join(_t for _x, _t in _btx274.items()
                          if _x == _wf269 or _x.startswith(_wf269 + "__"))
        for _c274 in sorted(_hfx269):
            _m274 = _c274.split(".")[-1]
            if _m274 not in _fm269:
                _vfx269.append((_f269["name"], _c274))
                continue
            _cc274 = {_wid269(_n) for _n, _mm in _mn269.items() if _mm == _m274}
            _sp274 = _re.compile(r"(?:^|_)" + _re.escape(_m274) + r"_\d+(?:_c\d+)?(?:_\d+)?$")
            _sv274 = {_v for _v in _vtx274 if _v in _cc274 or _sp274.search(_v)}
            _eff274 = (any(_n in _fx269 and _wid269(_n) in _btx274
                           for _n, _mm in _mn269.items() if _mm == _m274)
                       or any(_re.search(r"\bwrites\b", _vtx274[_v]) for _v in _sv274)
                       or not (_sv274 or any(_x in _btx274 for _x in _cc274)))
            if not _eff274:
                continue
            _n274 = sum(len(_re.findall(r"(?<![\w'.])" + _re.escape(_i) + r"(?![\w'])",
                                        _own274))
                        for _i in (_cc274 | _sv274))
            if _n274 < _irc274.get(_m274, 0):
                _vfx269.append((_f269["name"], _c274))
        _todo269 = [x for x in _blk269 if x == _wf269 or x.startswith(_wf269 + "__")]
        _seen269 = set()
        _ids269 = set()
        while _todo269:
            _x269 = _todo269.pop()
            if _x269 in _seen269:
                continue
            _seen269.add(_x269)
            _ids269 |= _blk269.get(_x269, set())
            _todo269.extend(x for x in _blk269.get(_x269, ()) if x in _blk269)
        for _m269 in sorted(_hid269):
            _cc269 = {_wid269(_n) for _n, _mm in _mn269.items() if _mm == _m269}
            _sp269 = _re.compile(r"(?:^|_)" + _re.escape(_m269) + r"_\d+(?:_c\d+)?(?:_\d+)?$")
            if not (_cc269 & _ids269 or any(_sp269.search(_i) for _i in _ids269 & _vl269)):
                if _m269 in _rm269:
                    _viol269.append((_f269["name"], _m269))
                if _m269 in _dvm269:
                    _dvh269.add(_wf269)
    if _vfx269:
        from errors import PyCSLSemanticError as _PyCSLSemErr274
        raise _PyCSLSemErr274(
            f"'{_vfx269[0][0]}' calls '{_vfx269[0][1]}', which WRITES (a declared `assigns`, "
            f"a body that mutates, or a collection mutator), inside a comprehension, "
            f"generator or lambda that PyCSL lowers OPAQUELY: the call is not applied at "
            f"that point of the emitted WhyML, so its write vanishes from the model and "
            f"what the function claims about the written state is proved of a state that "
            f"never changed. Rewrite it as an explicit loop so each call is modelled"
            f"{'' if len(_vfx269) == 1 else f' (also: {_vfx269[1:]})'}.",
            filename=args.file, stage="ir-semantic",
            code="PYCSL-SEM-VANISHED-CALL-EFFECT")
    if _viol269:
        from errors import PyCSLSemanticError as _PyCSLSemErr269
        raise _PyCSLSemErr269(
            f"'{_viol269[0][0]}' calls '{_viol269[0][1]}', which may RAISE or has a "
            f"precondition, inside a comprehension, generator or lambda that PyCSL lowers "
            f"OPAQUELY: the call does not appear in the emitted WhyML at all, so its "
            f"exception and its precondition vanish from the model. Rewrite it as an "
            f"explicit loop so the call is modelled"
            f"{'' if len(_viol269) == 1 else f' (also: {_viol269[1:]})'}.",
            filename=args.file, stage="ir-semantic",
            code="PYCSL-SEM-VANISHED-CALL-EFFECT")
    # A vanished call to a `\diverges` callee: the function's emitted body first applies
    # an opaque DIVERGING `val`, so Why3 owes it exactly what the call owed — a function
    # not declared `#@ \diverges` fails its termination VC, and an honestly declared one
    # type-checks (Why3 rejects `diverges` on a body it can see terminate).
    _at269 = []
    for _wf269 in sorted(_dvh269):
        _mh269 = _re.search(r"\n  (let|with)\s+(?:(?:rec|function|ghost|lemma)\s+)*"
                            + _re.escape(_wf269) + r"(?![\w'])", _mlw)
        _eq269 = _mlw.find("\n  =", _mh269.end()) if _mh269 else -1
        if _eq269 >= 0:
            _at269.append(((_mlw.rfind("\n  let ", 0, _mh269.start() + 1)
                            if _mh269.group(1) == "with" else _mh269.start()), _eq269 + 4))
    if _at269:
        for _q269 in sorted({_a[1] for _a in _at269}, reverse=True):
            _mlw = _mlw[:_q269] + "\n    pycsl_opaque_call_diverges ();" + _mlw[_q269:]
        _g269 = max(min(_a[0] for _a in _at269), 0)
        _mlw = (_mlw[:_g269] + "\n  val pycsl_opaque_call_diverges (_u: unit) : unit"
                "\n    diverges" + _mlw[_g269:])
    # (#49) ROUTE #263, second half — decided on the EMISSION (see the first half, after
    # the `ir-validate-boundary` check). A method-call edge is SEEN by Why3 only when the
    # caller's emitted body carries no stub for it AND (ii) applies the callee concretely
    # (directly or through helpers of its own `let rec` group), (iii) is one delegation
    # into a variant-carrying `let rec` catamorphism, or (iv) was re-expressed by a bespoke
    # lowering as the function's own variant-carrying `<name>__*` walkers: then the
    # recursion's termination is Why3's to check. Any other candidate edge of a cycle is
    # invisible to Why3, and the cycle is refused unless every function on it is
    # `#@ \diverges`. A declaration this scan cannot read is treated as unseen — the
    # fail-closed direction.
    if _pending263:
        from module6_whyml.identifiers import whyml_ident as _wid263
        _cuts263 = [_m.start() for _m in _re.finditer(r"\n  (?:let|val|with)\b", _mlw)]
        _cuts263.append(len(_mlw))
        _grp263 = {}
        _bod263 = {}
        _gid263 = 0
        _cur263 = 0
        _var263 = set()
        for _k263 in range(len(_cuts263) - 1):
            _blk263 = _mlw[_cuts263[_k263]:_cuts263[_k263 + 1]]
            _hm263 = _re.match(r"\n  (let|val|with)\s+((?:rec|function|ghost|lemma|predicate)"
                               r"\s+)*([A-Za-z_][A-Za-z0-9_']*)", _blk263)
            if not _hm263:
                _cur263 = 0
                continue
            if _hm263.group(1) == "let" and "rec" in (_hm263.group(2) or "").split():
                _gid263 += 1
                _cur263 = _gid263
            elif _hm263.group(1) != "with":
                _cur263 = 0
            if _cur263:
                _grp263[_hm263.group(3)] = _cur263
            _eq263 = _blk263.find("\n  =")
            _bod263[_hm263.group(3)] = _blk263[_eq263:] if _eq263 >= 0 else ""
            if _cur263 and "variant" in _blk263[:_eq263 if _eq263 >= 0 else len(_blk263)]:
                _var263.add(_cur263)
        _vals263 = set(_re.findall(r"\n  val\s+(?:(?:ghost|function|predicate)\s+)*"
                                   r"([A-Za-z_][A-Za-z0-9_']*)", _mlw))
        for _comp263, _cand263 in _pending263:
            _left263 = []
            for _a263, _b263 in _cand263:
                _wa263 = _wid263(_a263) if not _a263.startswith("__init__@") else ""
                _wb263 = _wid263(_b263) if not _b263.startswith("__init__@") else ""
                _ba263 = _bod263.get(_wa263, "") if _wa263 else ""
                _mt263 = _byname263[_b263]["name"][
                    len(str(_byname263[_b263].get("self_type") or "")) + 2:] if (
                    _b263 in _byname263 and _byname263[_b263].get("self_type")) else ""
                # (i) an abstract STUB for this call in the caller's body: unseen. The
                # stub is `<receiver path>_<m>_<arity>`, possibly disambiguated by
                # `_c<hash>` / `_<k>` (`_handle_dotted_call`, routes #166/#188), so any
                # referenced `val` of that shape counts — over-matching only refuses more.
                _stub263 = bool(_mt263) and any(
                    _re.search(r"(?:^|_)" + _re.escape(_mt263) + r"_\d+(?:_c\d+)?(?:_\d+)?$", _v)
                    and _re.search(r"(?<![\w'])" + _re.escape(_v) + r"(?![\w'])", _ba263)
                    for _v in _vals263)
                # (#269 R5) a callee emitted as a bodyless `val` (an IMPORTED stub) is never
                # applied concretely, whatever the text says.
                if _wa263 and _wb263 and not _stub263 and _wb263 not in _vals263:
                    # (ii) a CONCRETE application of the callee — directly, or through
                    # helpers of the SAME `let rec` group (the bespoke pyval walkers:
                    # `irscanner__uses_sum -> irscanner__uses_sum__d -> irscanner__uses_sum`,
                    # each with its own `variant`): Why3 sees the call (corpus 0966).
                    if _re.search(r"(?<![\w'.])" + _re.escape(_wb263) + r"(?![\w'])",
                                  _ba263):
                        continue
                    _g263 = _grp263.get(_wa263)
                    if _g263 and _grp263.get(_wb263) == _g263:
                        _mem263 = [x for x, y in _grp263.items() if y == _g263]
                        _seen263 = set()
                        _todo263 = [x for x in _mem263 if _re.search(
                            r"(?<![\w'.])" + _re.escape(x) + r"(?![\w'])", _ba263)]
                        while _todo263:
                            _x263 = _todo263.pop()
                            if _x263 in _seen263:
                                continue
                            _seen263.add(_x263)
                            _todo263.extend(x for x in _mem263 if _re.search(
                                r"(?<![\w'.])" + _re.escape(x) + r"(?![\w'])",
                                _bod263.get(_x263, "")))
                        if _wb263 in _seen263:
                            continue
                    # (iii) the body is ONE delegation into a `let rec` group carrying a
                    # `variant` — the synthesized catamorphism of corpus 0960 (`app__pp
                    # = pp_term (App …)`): the recursion lives there and Why3 checks it.
                    _dg263 = _re.match(r"\s*=\s*([A-Za-z_][A-Za-z0-9_']*)\s", _ba263)
                    if (_dg263 and _grp263.get(_dg263.group(1)) in _var263
                            and _dg263.group(1) not in _vals263):
                        continue
                    # (iv) a BESPOKE lowering that replaced the body with the function's
                    # own `<name>__<helper>` `let rec` walkers carrying a `variant`
                    # (`irscanner__find_assigned_vars = … irscanner__find_assigned_vars__f
                    # stmts acc …`): the Python recursion is re-expressed there and Why3
                    # checks its termination.
                    if any(x.startswith(_wa263 + "__") and _grp263.get(x) in _var263
                           and _re.search(r"(?<![\w'.])" + _re.escape(x) + r"(?![\w'])",
                                          _ba263)
                           for x in _grp263):
                        continue
                # Anything else — a stub, a call that VANISHED from the emission, a
                # constructor — is treated as unseen: the fail-closed direction.
                _left263.append((_a263, _b263))
            if not _left263:
                continue
            _nondiv263 = [n for n in _comp263 if n in _byname263
                          and not _byname263[n].get("diverges")]
            if not _nondiv263:
                continue
            from errors import PyCSLSemanticError as _PyCSLSemErr263
            _x269 = [e for e in _left263 if set(e) & (imported_names or set())]
            if _x269:
                # (#49) ROUTE #269 (R5) — the cycle leaves this unit through an IMPORTED
                # function (its body is read from the dependency; see the first half).
                raise _PyCSLSemErr263(
                    f"the functions {_comp263} call one another in a cycle that crosses a "
                    f"MODULE boundary ('{_x269[0][0]}' -> '{_x269[0][1]}'): an imported "
                    f"function is a bodyless stub here, and this unit is a stub in the "
                    f"dependency's own verification, so each side ASSUMES the other "
                    f"terminates and satisfies its postcondition — circularly — and Why3 "
                    f"never sees the recursion (CPython: RecursionError). Mark every function "
                    f"of the cycle `#@ \\diverges` in both modules (not yet so marked: "
                    f"{_nondiv263}), or break the import cycle.",
                    filename=args.file, stage="ir-semantic",
                    code="PYCSL-SEM-CROSS-MODULE-RECURSION")
            raise _PyCSLSemErr263(
                f"the functions {_comp263} call one another in a cycle that passes "
                f"through a METHOD or CONSTRUCTOR call ('{_left263[0][0]}' -> "
                f"'{_left263[0][1]}'). PyCSL lowers that call to a bodyless contract stub, "
                f"so Why3 never sees the cycle: it would ASSUME the callee terminates and "
                f"satisfies its postcondition — circularly — and no termination measure "
                f"(`#@ \\variant`) is checked across that edge. Without a termination "
                f"argument this recursion can run forever (CPython: RecursionError). Mark "
                f"EVERY function of the cycle `#@ \\diverges` (partial correctness: the "
                f"contracts then hold IF it returns; not yet so marked: {_nondiv263}), or "
                f"restructure the recursion as module-level functions carrying a "
                f"`#@ \\variant`, whose `let rec` termination Why3 checks.",
                filename=args.file, stage="ir-semantic",
                code="PYCSL-SEM-METHOD-RECURSION-UNCHECKED")
    return _mlw


def _why3_typecheck(mlw_filename: str):
    """Phase D honest gate: parse + typecheck the emitted WhyML with why3 (no proof).
    Returns ``(ok: bool, diagnostic: str)``. A run is only honestly SUCCESS if this
    passes — emitting text that does not even type-check is the silent success the spec
    (refactor.md §1.5 / Phase D) forbids. A missing why3 is NOT a failure (we do not turn
    an absent prover into a false typecheck-PASS) — (#49) gen #36: a missing why3 used to
    return ok=True, and the caller then printed `L3-tc ✓` and "WhyML generated AND
    type-checks" for WhyML nobody had checked (measured: an ill-typed emission reported
    SUCCESS under `env -i`). An unchecked emission is not a checked one, so it FAILS CLOSED;
    `--no-typecheck` is the honest opt-out."""
    try:
        r = subprocess.run(["why3", "prove", "--type-only", mlw_filename],
                           capture_output=True, text=True)
    except FileNotFoundError:
        return False, ("why3 not found on PATH — the type-check could NOT run, so this is "
                       "NOT a pass (fail-closed). Put why3 on PATH, or pass --no-typecheck "
                       "for an explicitly emit-only run.")
    if r.returncode == 0:
        return True, ""
    return False, (r.stderr.strip() or r.stdout.strip())


# ----------------------------------------------------------------------------
# Per-goal best-of-N prover dispatch
# ----------------------------------------------------------------------------
# `why3 prove -P A -P B` is a SINGLE call whose per-goal output reports only the
# LAST `-P` (B) — it is NOT an "A-then-B fallback". So a goal that ONLY A proves
# Valid is masked behind B's Unknown and the file FAILS the default pipeline
# (see getting-better/20260618-1710-...md). To get a SOUND best-of-N — a goal is
# Valid iff ANY first-class prover returns Valid — we run each prover as its own
# `why3 prove` call and merge the per-goal verdicts, keeping the BEST one.
#
# SOUNDNESS (load-bearing): a goal is promoted to Valid ONLY when some prover's
# verdict line for that exact goal literally reads "Valid". Unknown / Timeout /
# Out of memory / Failure / Invalid are NEVER counted as Valid. The merge takes
# the max over provers, where Valid dominates; no aggregate/summary line is ever
# parsed as a per-goal verdict (each goal is keyed by its own File+Sub-goal
# header block).

def _parse_goal_blocks(output: str) -> "List[Tuple[str, str]]":
    """Split goal-block text into per-goal (header, result_line) pairs by COUNTING
    `Prover result is:` lines. Used only by `_check_goal_conservation` over the
    synthesised canonical text (one block per record) to count goals — the live
    verdict/merge logic runs over structured `--json` records, not this text.

    A goal block is::

        File "<f>", line N, characters X-Y:
        Sub-goal <desc> of goal <name>'vc.
        Prover result is: <verdict> (...).

    Returns the blocks in document order; a header with no following result line is
    skipped."""
    blocks: List[Tuple[str, str]] = []
    cur_header: List[str] = []
    for line in output.splitlines():
        if line.startswith("Prover result is:"):
            header = "\n".join(cur_header)
            blocks.append((header, line))
            cur_header = []
        else:
            cur_header.append(line)
    return blocks


class _MergeConservationError(Exception):
    """Raised when the best-of-N merge produces FEWER goal blocks than the first
    full-file prover run — i.e. aggregation LOST a goal. This is the structural
    signature of the false-green class fixed in fa3668d (a Valid sibling masking a
    non-Valid one). It is a trust-free, fail-closed backstop: it depends on NO merge
    implementation being correct, so it survives any future rewrite of the merge.
    See soundness-issue.md (Tier 0)."""
    def __init__(self, expected: int, got: int):
        self.expected = expected
        self.got = got
        super().__init__(
            f"merge dropped goal(s): first full-file run enumerated {expected} "
            f"goal block(s) but the merged result has only {got} — refusing to "
            f"report a verdict (a dropped goal must never silently pass).")


def _check_goal_conservation(first_full_output: str, merged_output: str) -> None:
    """Trust-free fail-closed backstop (soundness-issue.md, Tier 0).

    The first prover attempt runs FULL-FILE and enumerates every goal; later
    attempts only re-prove residual subsets. So the merged best-of-N output must
    contain at LEAST as many goal blocks as that first run. Fewer means aggregation
    dropped a goal (the false-green class fixed in fa3668d) — raise rather than let
    a dropped obligation silently pass. Independent of how the merge is implemented,
    so it survives any future rewrite. Operates on the synthesised canonical text
    (one block per record), counting goal blocks via `_parse_goal_blocks`."""
    first_n = len(_parse_goal_blocks(first_full_output))
    merged_n = len(_parse_goal_blocks(merged_output))
    if merged_n < first_n:
        raise _MergeConservationError(first_n, merged_n)


# --- Structured (`why3 prove --json`) goal handling -------------------------------
# #6 (soundness-issue.md): the verdict/identity/merge logic runs over STRUCTURED JSON
# records — one per sub-goal — instead of re-grepping human stdout. Two split
# sub-goals can be byte-identical (same loc + goal_name + explanations: the exact
# collision that masked the false-green), but as records they are distinct LIST
# elements, so the merge never dedups them and a Valid sibling can never mask a
# non-Valid one. We then SYNTHESISE canonical legacy text from the records so the
# rest of the pipeline (success greps, Rocq replay, display) and the Tier-0
# conservation guard consume it unchanged. The only thing trusted is why3's typed,
# versioned JSON contract — no new TCB (why3 is already trusted), and no fragile
# reverse-engineered text format.

def _parse_why3_json(stdout: str) -> "List[dict]":
    """Parse `why3 prove --json` output into a list of records in document order.
    why3 emits a STREAM of concatenated JSON objects (one per goal), NOT a single
    array — so a plain json.loads fails with 'Extra data'. raw_decode in a loop
    consumes them; a single top-level array (other why3 versions) is also handled."""
    out: "List[dict]" = []
    dec = _json.JSONDecoder()
    s = stdout
    i, n = 0, len(s)
    while i < n:
        while i < n and s[i] in " \t\r\n":
            i += 1
        if i >= n:
            break
        try:
            obj, end = dec.raw_decode(s, i)
        except ValueError:
            break
        if isinstance(obj, list):
            out.extend(x for x in obj if isinstance(x, dict))
        elif isinstance(obj, dict):
            out.append(obj)
        i = end
    return out


def _json_goal_records(stdout: str) -> "List[dict]":
    """The goal-verdict records (those carrying a prover result) from --json output."""
    return [r for r in _parse_why3_json(stdout) if "prover-result" in r]


def _record_answer(rec: dict) -> str:
    return (rec.get("prover-result") or {}).get("answer", "") or ""


def _record_is_valid(rec: dict) -> bool:
    """Soundness chokepoint: ONLY a literal 'Valid' answer counts as proven.
    Invalid / Unknown / Timeout / OutOfMemory / Failure / ... are never proven."""
    return _record_answer(rec) == "Valid"


def _record_key(rec: dict) -> "Tuple":
    """Cross-prover alignment key (everything but occurrence). Two split sub-goals
    can be byte-identical here — the merge disambiguates by occurrence index."""
    term = rec.get("term") or {}
    loc = term.get("loc") or {}
    return ((loc.get("file-name"), loc.get("start-line"), loc.get("start-char"),
             loc.get("end-line"), loc.get("end-char")),
            term.get("goal_name"), tuple(term.get("explanations") or []))


def _merge_records_best_of_n(record_lists: "List[List[dict]]") -> "List[dict]":
    """Best-of-N over structured records. Aligns by (_record_key, occurrence-index)
    — the k-th record of a key in one prover's output is the SAME sub-goal as the
    k-th in another's — and keeps a Valid record if ANY prover proved it. Distinct
    sub-goals are NEVER collapsed (the merge-collapse class is impossible: records
    are list elements, not dict keys)."""
    order: "List[Tuple]" = []
    best: "Dict[Tuple, dict]" = {}
    for records in record_lists:
        occ: "Dict[Tuple, int]" = {}
        for rec in records:
            k = _record_key(rec)
            nseen = occ.get(k, 0)
            occ[k] = nseen + 1
            key = (k, nseen)
            if key not in best:
                order.append(key)
                best[key] = rec
            elif not _record_is_valid(best[key]) and _record_is_valid(rec):
                best[key] = rec
    return [best[key] for key in order]


def _synthesize_block(rec: dict) -> str:
    """Render one record as a legacy why3 goal block (File + Sub-goal + result), so
    the text-based downstream and the Tier-0 guard consume it unchanged. The verdict
    token is 'Valid (...)' ONLY for a real Valid; every non-Valid answer renders with
    a leading token the downstream greps catch (Invalid/Timeout/Unknown), preserving
    the true why3 answer for transparency."""
    term = rec.get("term") or {}
    loc = term.get("loc") or {}
    f = loc.get("file-name", "?")
    line = loc.get("start-line", 0)
    sc = loc.get("start-char", 0)
    ec = loc.get("end-char", 0)
    expl = ", ".join(term.get("explanations") or []) or "goal"
    name = term.get("goal_name", "?")
    pr = rec.get("prover-result") or {}
    ans = pr.get("answer", "") or ""
    t = pr.get("time", 0.0) or 0.0
    steps = pr.get("step", 0) or 0
    if ans == "Valid":
        tok = "Valid"
    elif ans == "Invalid":
        tok = "Invalid"
    elif ans == "Timeout":
        tok = "Timeout"
    elif ans == "Unknown":
        tok = "Unknown"
    else:
        # OutOfMemory / Failure / StepLimitExceeded / HighFailure / ... — treat as
        # unproven (leading 'Unknown' so downstream catches it), keep the truth.
        tok = f"Unknown (why3: {ans})"
    return (f'File "{f}", line {line}, characters {sc}-{ec}:\n'
            f"Sub-goal {expl} of goal {name}.\n"
            f"Prover result is: {tok} ({t:.2f}s, {steps} steps).")


def _synthesize_legacy_text(records: "List[dict]") -> str:
    """Canonical, lossless legacy-format text — ONE block per record, no dedup."""
    return "\n\n".join(_synthesize_block(r) for r in records)


def _residual_selectors_from_records(records: "List[dict]") -> "Optional[List[str]]":
    """`<file>:<line>` selectors for every non-Valid record (deduped). None if any
    residual lacks a locatable loc — caller falls back to a full-file re-run (sound,
    proves only MORE). Empty list iff there are no residuals."""
    sels: "List[str]" = []
    seen: "Set[str]" = set()
    for rec in records:
        if _record_is_valid(rec):
            continue
        loc = (rec.get("term") or {}).get("loc") or {}
        fn, ln = loc.get("file-name"), loc.get("start-line")
        if fn is None or ln is None:
            return None
        s = f"{fn}:{ln}"
        if s not in seen:
            seen.add(s)
            sels.append(s)
    return sels


import re as _re


# --- Non-vacuity gate -------------------------------------------------------------
# A function whose ASSUMED context (its preconditions + the `ensures` it assumes from
# every callee at its call sites) is logically INCONSISTENT proves any postcondition —
# its "green" is vacuous. The gate detects this by re-proving a probe in which every
# body-bearing function carries an extra `ensures { [@expl:vacuity] false }`: that goal
# is provable IFF the context is inconsistent. (Empirically, an `#@ assert false` in the
# BODY is position-sensitive/unreliable; the postcondition form is not — it is the
# reliable probe.) See getting-better/csys-vacuity-investigation/ROOT-CAUSE.md.

# The body-start separator of a top-level `let`/`let function`: a line beginning with
# exactly two spaces then `=` (own line `  =` or inline `  = <expr>`). Nested
# `let … = … in` inside a body is indented deeper and never matches; `val` stubs have
# no `=` body and are correctly left unprobed (they are trusted, not verified).
_BODY_EQ_RE = _re.compile(r'^  =(\s|$)')


# A top-level function definition header: `  let [rec] [function] [ghost] <name>`.
_LET_FN_RE = _re.compile(r'^  let (?:rec )?(?:function )?(?:ghost )?(\w+)\b')


def _function_body_eqs(mlw_code: str) -> "Tuple[List[Tuple[str, int]], List[str]]":
    """Return ([(fname, body_eq_line_index)], lines) for every top-level body-bearing
    function. The body `=` is the first `^  =` line after a `^  let <name>` header
    (only contract clauses sit between them). `val` stubs (no `=`) are skipped."""
    lines = mlw_code.splitlines()
    res: List[Tuple[str, int]] = []
    cur: Optional[str] = None
    for i, line in enumerate(lines):
        m = _LET_FN_RE.match(line)
        if m:
            cur = m.group(1)
        elif cur is not None and _BODY_EQ_RE.match(line):
            res.append((cur, i))
            cur = None
    return res, lines


def _run_vacuity_gate(mlw_code: str, provers: List[str],
                      args: argparse.Namespace,
                      noreturn_names: "Optional[Set[str]]" = None) -> "Optional[List[str]]":
    """Run the non-vacuity gate. Returns the list of vacuous function names (empty = all
    contexts consistent), or None if why3 is absent (skip-not-fail, like the typecheck
    gate).

    PER-FUNCTION probe (no cross-contamination): for each body-bearing function it emits
    a variant in which ONLY that function carries an extra `ensures { false }`, then proves
    JUST that postcondition goal (`-g <probe>:<line>`). A function whose assumed context is
    inconsistent proves `false`; a sound one cannot. Adding `ensures false` to every
    function at once would be wrong — a callee's injected `false` would propagate into every
    caller's assumed context and flag them all.

    NR4 (typing-engagement ty1 / 28-0000-typing-spec-4 §1.2): a function declared
    `-> NoReturn` ALREADY carries a `false` postcondition (NR1 — `ensures { false }`),
    so it is INDISTINGUISHABLE from a vacuous one under the probe. The gate EXEMPTS
    declared-NoReturn functions: ``noreturn_names`` (keyed on the `-> NoReturn`
    annotation → IR `is_noreturn` flag, NOT on the inferred postcondition) is the
    skip-set. A genuinely-vacuous function (inconsistent context, no NoReturn
    annotation) is still probed — the exemption does NOT extend to it."""
    import tempfile
    fns, lines = _function_body_eqs(mlw_code)
    if not fns:
        return []
    skip = noreturn_names or set()
    base_cmd = ["why3", "prove", "-a", "split_vc"]
    if "\n  inductive " in mlw_code:
        base_cmd += ["-a", "induction_pr"]
    tl = str(getattr(args, "vacuity_timelimit", "5"))
    # (#49) route #267: the body-less callees whose `ensures` the call-site probe audits —
    # a `val` with an `ensures`, and none of `raises` / `diverges` / `ensures { false }`
    # (those may legitimately not return normally, so a dead continuation is their spec).
    _vals267: "Set[str]" = set()
    for _vi267, _vl267 in enumerate(lines):
        _vm267 = _re.match(r"^\s+val (?:function |predicate )?(?:ghost )?(\w+)", _vl267)
        if not _vm267:
            continue
        _vc267 = []
        _vj267 = _vi267 + 1
        while (_vj267 < len(lines) and lines[_vj267].strip()
               and not _re.match(r"^\s*(let|val|end|predicate|function|lemma|goal|axiom|"
                                 r"type|use|clone|scope)\b", lines[_vj267])):
            _vc267.append(lines[_vj267])
            _vj267 += 1
        _vt267 = "\n".join(_vc267)
        if (_re.search(r"\bensures\b", _vt267)
                and not _re.search(r"\b(raises|diverges)\b", _vt267)
                and not _re.search(r"\bensures\s*\{\s*(\[@[^\]]*\]\s*)*false\s*\}", _vt267)):
            _vals267.add(_vm267.group(1))
    def _probe_one(fname_idx: "Tuple[str, int]") -> "Tuple[str, Optional[bool]]":
        """Probe one function. Returns (fname, vacuous?) — vacuous? is None if why3 is
        absent (so the caller can degrade the whole gate to skip-not-fail).

        split_vc emits ONE `ensures false` goal per NORMAL-EXIT path. A function is
        vacuous iff EVERY normal exit has an inconsistent context — i.e. EVERY false-goal
        proves Valid. It is NOT vacuous if even one exit is consistent (its false-goal is
        Unknown/Timeout): the real postcondition was genuinely discharged there.

        Two correctness points learned the hard way (a consequence test like
        `mkdir → access(present) → unlink → access(absent)` has a provably-DEAD
        "still-present" branch by design):
          1. FILTER to the injected goal — `why3 -g <file>:<line>` returns the false-goal
             AND sibling goals (the real postcondition, preconditions) at/near that line.
             Keep only records whose `loc.start-line` is the injected line.
          2. ALL, not ANY — the OLD gate flagged a function if ANY selected record was
             Valid. That fired on (a) the always-Valid sibling postcondition and (b) the
             Valid false-goal of a genuinely-DEAD branch — over-reporting every sound
             consequence test as vacuous. Require ALL false-goals Valid (best-of-N across
             provers: a path is inconsistent if ANY prover proves its false-goal)."""
        fname, idx = fname_idx
        # NR4: exempt declared-NoReturn functions — their `false` postcondition is the
        # SPEC (NR1), not a vacuity signal. Keyed on the IR `is_noreturn` flag (which
        # comes from the `-> NoReturn` annotation), NOT on the inferred postcondition.
        if fname in skip:
            return fname, False
        # (#49) ROUTE #267 — AN ABSTRACT CONTRACT THAT IS FALSE AT ONE POINT KILLS ONE
        # BRANCH, AND "ALL EXITS" CANNOT SEE ONE BRANCH. The all-exits criterion below is
        # deliberate (a consequence test's provably-dead branch is dead BY DESIGN), so a
        # path made dead by an `\abstract`/`\trusted` callee's `ensures` was indistinguishable
        # from one made dead by the user's own guards. MEASURED at 283d1033 (witness a04):
        # `\abstract oracle(x)` with `ensures x != 5`, called only under `if x == 5:`, and a
        # caller claiming `\result == 1` while that branch returns 2 — "Verification
        # SUCCESS", CPython 2. A callee with no body, no `raises` and no `diverges` MUST
        # return, so its `ensures` must be satisfiable wherever it is called; if the point
        # just AFTER the call is unreachable while the point just BEFORE it is not, the
        # callee's contract is what made it so, and the green on that branch is vacuous.
        # Per call site of such a `val` in this body, probe `check { false }` after the call
        # (all sites, one run per prover); for each that proves, probe the same before the
        # call, and flag the function iff after proves and before does not. `check` adds no
        # hypothesis, so the probes cannot feed each other. A deadness the program already
        # had before the call (defensive code under a `requires`) is NOT flagged — the gate's
        # dead-by-design philosophy is kept; only callee-INDUCED deadness fails.
        if _vals267:
            _end267 = idx + 1
            while _end267 < len(lines) and not _re.match(
                    r"^  (let|val|predicate|function|lemma|goal|axiom|type|use|clone|"
                    r"scope|exception|constant|inductive|meta)\b|^end\b", lines[_end267]):
                _end267 += 1
            _body267 = "\n".join(lines[idx:_end267])
            _sites267: "List[Tuple[int, int, str]]" = []
            _depth267 = 0
            _i267 = 0
            while _i267 < len(_body267):
                _ch267 = _body267[_i267]
                if _ch267 == "{":
                    _depth267 += 1
                elif _ch267 == "}":
                    _depth267 -= 1
                elif _ch267 == "(" and _depth267 == 0:
                    _m267 = _re.match(r"\((\w+)\b", _body267[_i267:])
                    if _m267 and _m267.group(1) in _vals267:
                        _lvl267 = 0
                        _j267 = _i267
                        while _j267 < len(_body267):
                            if _body267[_j267] == "(":
                                _lvl267 += 1
                            elif _body267[_j267] == ")":
                                _lvl267 -= 1
                                if _lvl267 == 0:
                                    break
                            _j267 += 1
                        if _j267 < len(_body267) and "{" not in _body267[_i267:_j267]:
                            _sites267.append((_i267, _j267 + 1, _m267.group(1)))
                            _i267 = _j267 + 1   # outermost site only (nested: residual)
                            continue
                _i267 += 1
            if _sites267:
                _txt267 = _body267
                for _k267 in range(len(_sites267) - 1, -1, -1):
                    _s267, _e267, _nm267 = _sites267[_k267]
                    _txt267 = (_txt267[:_s267]
                               + f"(\n check {{ [@expl:vacpre {_k267}] false }};\n"
                               + f" let __vac_r{_k267} = " + _txt267[_s267:_e267] + " in\n"
                               + f" check {{ [@expl:vacpost {_k267}] false }};\n"
                               + f" __vac_r{_k267})" + _txt267[_e267:])
                _plines267 = lines[:idx] + _txt267.split("\n") + lines[_end267:]
                _pre267: "Dict[int, int]" = {}
                _post267: "Dict[int, int]" = {}
                for _ln267, _l267 in enumerate(_plines267):
                    _mm267 = _re.search(r"\[@expl:vac(pre|post) (\d+)\]", _l267)
                    if _mm267:
                        (_pre267 if _mm267.group(1) == "pre" else _post267)[
                            _ln267 + 1] = int(_mm267.group(2))
                fd267, _pp267 = tempfile.mkstemp(suffix=".mlw", prefix=".pycsl_vac_")
                try:
                    _fh267 = os.fdopen(fd267, "w")
                    _fh267.write("\n".join(_plines267) + "\n")
                    _fh267.close()
                    _hit267: "Dict[str, Set[int]]" = {"pre": set(), "post": set()}
                    for _kind267, _map267 in (("post", _post267), ("pre", _pre267)):
                        for p in provers:
                            _want267 = [ln for ln, k in _map267.items()
                                        if k not in _hit267[_kind267]
                                        and (_kind267 == "post" or k in _hit267["post"])]
                            if not _want267:
                                break
                            try:
                                r = _run_why3_prove(base_cmd, p, tl, _pp267,
                                                    [f"{_pp267}:{ln}" for ln in _want267])
                            except FileNotFoundError:
                                return fname, None
                            _recs267 = _json_goal_records(r.stdout)
                            if not any(((rec.get("term") or {}).get("loc") or {}).get(
                                    "start-line") in _map267 for rec in _recs267):
                                # why3 surfaced none of the probe goals (it rejected the
                                # rewritten body): say so rather than pass silently.
                                print(f"[!] vacuity call-site probe for '{fname}' could not "
                                      f"be checked (no probe goal surfaced; prover {p}).")
                                break
                            for rec in _recs267:
                                _sl267 = ((rec.get("term") or {}).get("loc") or {}).get(
                                    "start-line")
                                if _sl267 in _map267 and _record_is_valid(rec):
                                    _hit267[_kind267].add(_map267[_sl267])
                    for _k267 in sorted(_hit267["post"] - _hit267["pre"]):
                        return (f"{fname} [the call to `{_sites267[_k267][2]}` makes its "
                                f"continuation unreachable: that callee's assumed "
                                f"`ensures` is unsatisfiable there]"), True
                finally:
                    if os.path.exists(_pp267):
                        os.remove(_pp267)
        probe_lines = lines[:idx] + ["    ensures { [@expl:vacprobe] false }"] + lines[idx:]
        probe_line_no = idx + 1   # 1-based line of the inserted `ensures false`
        fd, probe_path = tempfile.mkstemp(suffix=".mlw", prefix=".pycsl_vac_")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("\n".join(probe_lines) + "\n")
            sel = [f"{probe_path}:{probe_line_no}"]

            def _is_false_goal(rec: dict) -> bool:
                loc = (rec.get("term") or {}).get("loc") or {}
                return loc.get("start-line") == probe_line_no

            per_prover: "List[List[dict]]" = []
            for p in provers:
                try:
                    r = _run_why3_prove(base_cmd, p, tl, probe_path, sel)
                except FileNotFoundError:
                    return fname, None
                # #6: read structured --json records, not re-grepped text. Keep ONLY the
                # injected false-goal(s) — never the sibling real-postcondition goals.
                per_prover.append([rec for rec in _json_goal_records(r.stdout)
                                   if _is_false_goal(rec)])
            # best-of-N: a normal-exit path counts inconsistent if ANY prover proved its
            # false-goal Valid; align the per-path goals by occurrence across provers.
            merged = [rec for rec in _merge_records_best_of_n(per_prover)
                      if _is_false_goal(rec)]
            if not merged:
                # No normal-exit false-goal surfaced (e.g. a function with no normal
                # return, only `raises`) — nothing to flag as vacuous.
                # (#49) ROUTE #260 — UNLESS THE ONLY WAY OUT IS AN UNDECLARED EXCEPTION.
                # Every normal exit was dropped as unreachable, and the spec carries an
                # UNCONDITIONED `raises { E }` arm — one the emitter ADDED because E escapes
                # while no `#@ raises` declares it. Then the normal-return postcondition is
                # discharged by the model's raise alone: measured, `raise KeyError` under an
                # `except LookupError` the model could not match PROVED `\result == 0`
                # (CPython 7) with no goal for this probe to see. A function that really
                # never returns says so (`-> NoReturn`, exempt above) or declares the raise.
                _h260 = idx - 1
                while (_h260 > 0 and not _LET_FN_RE.match(lines[_h260])
                       and not _BODY_EQ_RE.match(lines[_h260])):
                    _h260 -= 1
                if any(_re.match(r"^\s+raises \{ [A-Za-z_0-9', ]+ \}\s*$", _l260)
                       for _l260 in lines[_h260:idx]):
                    return fname, True
                return fname, False
            return fname, all(_record_is_valid(rec) for rec in merged)
        finally:
            if os.path.exists(probe_path):
                os.remove(probe_path)

    # Parallelize the per-function probes (each is an independent why3 subprocess that
    # releases the GIL); a large module (e.g. os) otherwise serializes dozens of probes.
    import concurrent.futures
    try:
        ncpu = os.cpu_count() or 2
    except Exception:
        ncpu = 2
    workers = max(1, min(len(fns), ncpu // 2 if ncpu > 2 else 1))
    vac: List[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for fname, verdict in ex.map(_probe_one, fns):
            if verdict is None:
                return None   # why3 absent — skip the gate (not a failure)
            if verdict:
                vac.append(fname)
    return vac


def _run_why3_prove(base_cmd: "List[str]", prover: str, timelimit: str,
                    mlw_filename: str,
                    goal_selectors: "Optional[List[str]]" = None
                    ) -> "subprocess.CompletedProcess":
    """Run `why3 prove ... -P <prover> --timelimit <t> [-g sel ...] <file>` for ONE
    prover.

    Each prover gets the FULL per-goal timelimit (it is not split across provers).
    `base_cmd` carries the shared transforms (`-a split_vc`, optional
    `-a induction_pr`). When *goal_selectors* is given, only those sub-goals
    (`-g <file>:<line>`) are attempted — the residual-only second-pass path.

    `--json` makes stdout a STRUCTURED stream of per-goal records (#6) — parse it
    with `_json_goal_records`, never by re-grepping human text."""
    cmd = list(base_cmd) + ["-P", prover, "--timelimit", timelimit, "--json"]
    for sel in (goal_selectors or []):
        cmd += ["-g", sel]
    cmd += [mlw_filename]
    r = subprocess.run(cmd, capture_output=True, text=True)
    # (#44) A CONFIGURED PROVER THAT DOES NOT EXIST MUST NOT BE SILENT. why3 answers a
    # `-P Alt-Ergo,2.6.2,` it cannot resolve with one line on stderr — "No prover in
    # ~/.why3.conf corresponds to ..." — and returns; the dispatcher then simply proceeds
    # with whatever provers DID resolve. That is a run with fewer instruments than the one
    # that was asked for, and it looks exactly like a run that legitimately could not
    # prove a goal.
    # MEASURED: `config/agents-config.json` and `_DEFAULT_PROVERS` below both name
    # Alt-Ergo **2.6.2**, and this switch has **2.6.3**. Every DEFAULT run — the entire
    # reference suite included — has therefore been proving with Z3 ALONE, and TEN of the
    # suite's thirty remaining failures pass the moment Alt-Ergo is actually present
    # (0226, 0484, 0714, 0766, 0932, 0938, 0943, 0944, 0948, 0949 — five of which say
    # "STATUS — PROVES." in their own docstrings). The campaign's mirror proofs were
    # unaffected only because they pass `--provers` explicitly, which is why nobody saw it.
    if "No prover in" in (r.stderr or "") and "corresponds to" in (r.stderr or ""):
        for _ln in r.stderr.split("\n"):
            if "No prover in" in _ln and "corresponds to" in _ln:
                print(f"[!] CONFIGURED PROVER NOT AVAILABLE — {_ln.strip()}")
        print(f"[!]     Requested `{prover}`; this run is proceeding with FEWER PROVERS "
              f"than configured, so an unproven goal here may mean the prover is missing "
              f"rather than the goal is hard. Fix the version in "
              f"`config/agents-config.json` / `--provers`, or install the prover.")
    return r


def _dispatch_provers(base_cmd: "List[str]", provers: List[str], timelimit: str,
                      mlw_filename: str) -> "Tuple[str, str, int]":
    """Per-goal best-of-N dispatch. Returns (merged_stdout, merged_stderr, returncode).

    Identity, merge and the verdict run over STRUCTURED `--json` records (#6); the
    returned stdout is canonical legacy text synthesised from the merged records,
    so the rest of the pipeline is unchanged.

    - Single prover: exactly one `why3 prove --json` call.
    - Multiple provers: the FIRST prover runs full-file; each SUBSEQUENT prover runs
      ONLY on the goals still non-Valid (`why3 prove -g <file>:<line>`), merging
      per-goal verdicts (Valid by ANY prover ⇒ Valid). EARLY-EXIT: once every goal
      is Valid, the remaining provers are not invoked. So goals the first prover
      already proves cost exactly ONE call; only the residual goals pay for the next
      prover (the doctrine's "only residual goals pay" — a file with no residuals is
      a single full-file pass, timing unchanged).

    ATTEMPT ORDER preserves legacy TIMING. `why3 prove -P A -P B` (a single call,
    the legacy invocation) runs ONLY the LAST `-P` per goal — it is NOT an
    A-then-B fallback — so the legacy default `[Alt-Ergo, Z3]` effectively ran
    Z3-ONLY. To keep "goals Z3 already proves are ~unchanged in timing", we attempt
    the LAST-listed prover FIRST (the one the legacy call reported), early-exit if
    it clears everything, and only fall to the earlier-listed provers for the
    residual goals. Order is a pure performance/early-exit choice: best-of-N is
    Valid-iff-ANY, so the accepted goal set is identical for every order — only the
    wall-clock differs. (Running Alt-Ergo first instead would make every
    Z3-fast/Alt-Ergo-slow goal pay a full 30s Alt-Ergo timeout before Z3 runs — a
    large, needless slowdown; e.g. the 0665 inode codec goes from ~40s Z3-only to
    minutes.)

    returncode is 0 iff the MERGED result has every goal Valid (or the runs
    produced no goal blocks AND every per-prover rc was 0 — the zero-goal case);
    otherwise it is the last run's nonzero rc (so the legacy `rc == 0` guard still
    means "nothing left unproven")."""
    # #6: identity + merge run over STRUCTURED JSON records (one per sub-goal), then
    # we synthesise canonical legacy text so the downstream is unchanged. record_lists
    # holds each attempt's goal records; record_lists[0] is the first full-file run.
    record_lists: "List[List[dict]]" = []
    stderrs: List[str] = []

    def _finalize(merged_records: "List[dict]", rc: int) -> "Tuple[str, str, int]":
        """Synthesise the merged text and apply the Tier-0 fail-closed conservation
        guard: the first attempt runs FULL-FILE and enumerates every goal, so the
        merged result must not have FEWER goal records than that first run. Fewer =>
        aggregation dropped a goal => raise. Trust-free: holds over the synthesised
        canonical text regardless of how the merge is implemented."""
        merged_text = _synthesize_legacy_text(merged_records)
        if record_lists:
            _check_goal_conservation(_synthesize_legacy_text(record_lists[0]), merged_text)
        return merged_text, "\n".join(stderrs), rc

    if len(provers) == 1:
        r = _run_why3_prove(base_cmd, provers[0], timelimit, mlw_filename)
        if r.stderr.strip():
            stderrs.append(r.stderr.strip())
        record_lists.append(_json_goal_records(r.stdout))
        merged = record_lists[0]
        if merged:
            rc = 0 if all(_record_is_valid(x) for x in merged) else (r.returncode or 1)
        else:
            rc = r.returncode
        return _finalize(merged, rc)

    # Try the legacy-reported (last-listed) prover first; then the rest, in their
    # listed order, restricted to residual goals. Soundness is order-independent.
    attempt_order = [provers[-1]] + provers[:-1]
    last_rc = 0
    any_goals = False

    for idx, prover in enumerate(attempt_order):
        if idx == 0:
            # First prover: full file.
            selectors: Optional[List[str]] = None
        else:
            # Subsequent provers: ONLY the goals still non-Valid in the merge so far.
            selectors = _residual_selectors_from_records(_merge_records_best_of_n(record_lists))
            if selectors == []:
                # No residuals — if the merge is already all-Valid we early-exited
                # above; reaching here means nothing left to do.
                break
            if selectors is None:
                # Could not pin a residual's loc — fall back to a full-file re-run
                # (sound: proves only MORE).
                pass  # selectors already None -> full file
        r = _run_why3_prove(base_cmd, prover, timelimit, mlw_filename, selectors)
        if r.stderr.strip():
            stderrs.append(r.stderr.strip())
        last_rc = r.returncode
        record_lists.append(_json_goal_records(r.stdout))
        merged = _merge_records_best_of_n(record_lists)
        if merged:
            any_goals = True
            if all(_record_is_valid(x) for x in merged):
                # Every goal proven by some prover so far — no need to run the rest.
                return _finalize(merged, 0)
        else:
            # No goals (e.g. zero goals to prove). If this prover succeeded with
            # empty output, the success path accepts it.
            if r.returncode == 0:
                return _finalize(merged, 0)

    merged = _merge_records_best_of_n(record_lists)
    # Final verdict: rc 0 iff every goal is Valid in the merge. If there were
    # genuinely no goals, fall back to the last run's rc.
    if any_goals:
        rc = 0 if all(_record_is_valid(x) for x in merged) else (last_rc if last_rc != 0 else 1)
    else:
        rc = last_rc
    return _finalize(merged, rc)


def _run_proofs(mlw_code: str, mlw_filename: str, provers: List[str], args: argparse.Namespace) -> None:
    """Write *mlw_code* to *mlw_filename*, invoke Why3, handle Rocq proofs and cleanup."""
    with open(mlw_filename, "w") as f:
        f.write(mlw_code)

    if args.no_proof:
        # refactor.md Phase D2: the honest typecheck gate is now DEFAULT-ON. A `--no-proof`
        # run is SUCCESS only if the emitted WhyML at least TYPE-CHECKS (`why3 prove
        # --type-only`) — never merely "text emitted" (§1.5). `--no-typecheck` opts out
        # (fast emit-only, for byte-diff/dev sweeps and when why3 is absent). `--typecheck`
        # is now a harmless no-op alias (the gate is already on). A missing why3 now FAILS
        # CLOSED in `_why3_typecheck` (gen #36): it used to be ok=True, which printed `L3-tc ✓`
        # for an emission nobody checked.
        if not getattr(args, "no_typecheck", False):
            ok, diag = _why3_typecheck(mlw_filename)
            print(f"[level] L1 ✓  L2 ✓  L3-tc {'✓' if ok else '✗'}")
            if not ok:
                print("[!] Emitted WhyML does NOT type-check (L3-tc failed) — NOT a success:")
                print(diag)
                # Structural-only coded diagnostic for the typecheck gate (opt-in).
                # The human lines above are unchanged; the code rides --diagnostics-json.
                if getattr(args, "diagnostics_json", False):
                    print(_json.dumps({
                        "code": "PYCSL-TC-FAIL",
                        "stage": "typecheck",
                        "file": getattr(args, "file", ""),
                        "line": 0,
                        "message": diag,
                    }, sort_keys=True), file=sys.stderr)
                if not args.keep_mlw and os.path.exists(mlw_filename):
                    os.remove(mlw_filename)
                sys.exit(1)
            print("[+] Verification SUCCESS (--no-proof: WhyML generated AND type-checks "
                  "[L3-tc ✓]; proof skipped).")
        else:
            print("[+] Verification SUCCESS (--no-proof --no-typecheck: WhyML generated "
                  "[emit-only, typecheck skipped]).")
        if not args.keep_mlw and os.path.exists(mlw_filename):
            os.remove(mlw_filename)
        sys.exit(0)

    print(f"[*] Running Proof Engine (provers: {' → '.join(provers)})...")
    try:
        # split_vc decomposes each function's monolithic VC into per-invariant/per-branch
        # sub-goals.  Most sub-goals are trivially linear; only genuinely hard arithmetic
        # goals remain, and they benefit from Z3 NIA in isolation (rather than as part of a
        # huge combined query that triggers OOM).
        base_cmd = ["why3", "prove", "-a", "split_vc"]
        # inductive.md: a universally-quantified CONSEQUENCE of an inductive predicate
        # (`#@ lemma … ensures \forall x; p(x) ==> Q`) is proved by induction on the
        # predicate's derivation, which the SMT backend cannot do alone (it times out).
        # `induction_pr` — applied AFTER `split_vc` has introduced the `p(x)` premise into
        # the hypotheses — discharges it. It is a no-op on goals with no inductive-predicate
        # hypothesis, and is added only when the module declares an inductive predicate, so
        # non-inductive files are unaffected.
        if "\n  inductive " in mlw_code:
            base_cmd += ["-a", "induction_pr"]

        # Per-goal best-of-N prover dispatch (see _dispatch_provers): each prover
        # runs as its OWN `why3 prove` call and a goal is Valid iff ANY prover
        # proves it Valid — instead of `why3 prove -P A -P B` reporting only the
        # LAST prover and masking an Alt-Ergo win behind a Z3 Unknown. A single
        # prover (`-p <prover>`) takes the byte-identical legacy single-call path.
        output, merged_stderr, returncode = _dispatch_provers(
            base_cmd, provers, "30", mlw_filename)

        print("\n--- Verification Results ---")
        if output:
            print(output)
        if merged_stderr:
            print("\nWarnings/Errors from Why3:")
            print(merged_stderr)

        unknown_goals = [line for line in output.splitlines()
                         if "Unknown" in line or "Timeout" in line]
        invalid_goals = [line for line in output.splitlines() if "Invalid" in line]
        smt_proved = len([line for line in output.splitlines() if "Valid" in line])

        def _gate_vacuity_then_succeed(success_msg: str) -> None:
            """Run the non-vacuity gate before declaring success. If any function's
            context is vacuous, FAIL the run instead of reporting the (vacuous) green."""
            if getattr(args, "check_vacuity", False):
                # Skip-set of functions whose (sound) green is EXPECTED to be
                # vacuous-looking on the unreachable normal-exit path: declared
                # `-> NoReturn` (NR1/NR4) and `#@ \diverges` functions. Computed in
                # `_run_pipeline` (where the IR is in scope) and stashed on `args`,
                # because here `ir_data` is out of scope (gate runs in `_run_proofs`).
                _nr_names = getattr(args, "_vacuity_exempt", set())
                vac = _run_vacuity_gate(mlw_code, provers, args, _nr_names)
                if vac:
                    print("\n[-] NON-VACUITY GATE FAILED: the following function(s) verify "
                          "VACUOUSLY — their assumed context is logically inconsistent, so "
                          "every postcondition is discharged for free (the 'green' is meaningless):")
                    for name in vac:
                        print(f"    {name}" + ("" if " [" in name
                                                    else "  (proves `ensures false`)"))
                    print("    Root cause is usually several nonlinear integer-division facts "
                          "coexisting in one context (helper `result == …//…` ensures, "
                          "division-bound inequalities, disjunctive value-equalities). See "
                          "getting-better/csys-vacuity-investigation/ROOT-CAUSE.md.")
                    print("    (Opt out with --no-check-vacuity; tune with --vacuity-timelimit.)")
                    if getattr(args, "diagnostics_json", False):
                        print(_json.dumps({
                            "code": "PYCSL-VACUOUS",
                            "stage": "vacuity-gate",
                            "file": getattr(args, "file", ""),
                            "line": 0,
                            "message": "vacuous context: " + ", ".join(vac),
                        }, sort_keys=True), file=sys.stderr)
                    print("\n[-] Verification FAILED (vacuous proof). Check the solver output.")
                    sys.exit(1)
            print(success_msg)

        # (#49) ROUTE #221 — `--fun` PROVES ONE FUNCTION AND CLAIMED THE MODULE.
        # Under `--fun F` only F's goals are discharged; every callee's contract is ASSUMED
        # at the call site and its OWN goals are never built. MEASURED: a callee whose body
        # sets `self.v = 7` and declares NO `#@ assigns` gets the SYNTHESIZED frame
        # `ensures { self.v = old self.v }` — invented by the emitter from the ABSENCE of a
        # clause — and `--fun use` then proves `\result == 0` for a caller CPython answers
        # -7, while the TRUE twin (`== -7`) fails and the SAME FILE WITHOUT `--fun` fails.
        # It is not about dunders: corpus 1817's plain `enter` carries it.
        #
        # THIS IS REPAIR 1 OF THE THREE the route names, and it is the honest one rather
        # than the complete one: the headline stops claiming the module. It does NOT make
        # the claim true — discharging the callees' synthesized frames (repair 2), or
        # refusing to synthesize a frame from silence under `--fun` (repair 3), is a
        # decision about what `--fun` is FOR, and the route record leaves it to the owner of
        # the flag. What changes here is that a reader can no longer take
        # `All contracts formally proven` from a run that proved one function.
        # Every gate in the battery runs the WHOLE-FILE proof, which is correct policy and
        # exactly why nothing had ever measured what `--fun` ALONE certifies.
        _fun221 = ", ".join(sorted(args.fun)) if getattr(args, "fun", None) else ""
        _ok221 = ("\n[+] Verification SUCCESS! All contracts formally proven."
                  if not _fun221 else
                  "\n[+] Verification SUCCESS for %s ONLY (--fun): its own goals are proved, "
                  "and the contract of every function it calls is ASSUMED, including any "
                  "frame the emitter SYNTHESIZED from a missing `#@ assigns`. This is NOT a "
                  "claim about the module — run without `--fun` for that (route #221)."
                  % _fun221)
        if returncode == 0 and not unknown_goals and not invalid_goals and ("Valid" in output or not output):
            _gate_vacuity_then_succeed(_ok221)
        else:
            unproven_count = len(unknown_goals) + len(invalid_goals)
            rocq_proved = 0
            proof_dir = None

            if args.rocq_proofs is not None:
                proof_dir = (os.path.splitext(args.file)[0] + ".proofs"
                             if args.rocq_proofs == "__auto__" else args.rocq_proofs)
            else:
                auto_dir = os.path.splitext(args.file)[0] + ".proofs"
                if os.path.isdir(auto_dir):
                    proof_dir = auto_dir

            if proof_dir and os.path.isdir(proof_dir):
                rocq_proved = _check_rocq_proofs(proof_dir, mlw_filename, unknown_goals)

            remaining = unproven_count - rocq_proved
            if remaining <= 0 and rocq_proved > 0:
                _gate_vacuity_then_succeed(
                    (f"\n[+] Verification SUCCESS! All contracts formally proven "
                     f"({smt_proved} SMT + {rocq_proved} Rocq).") if not _fun221 else
                    (f"\n[+] Verification SUCCESS for {_fun221} ONLY (--fun; {smt_proved} "
                     f"SMT + {rocq_proved} Rocq): its own goals are proved, and the contract "
                     f"of every function it calls is ASSUMED. NOT a claim about the module "
                     f"(route #221)."))
            else:
                if unknown_goals:
                    print(f"\n[-] {len(unknown_goals)} goal(s) remain unproven after all provers:")
                    for g in unknown_goals:
                        print(f"    {g.strip()}")
                if invalid_goals:
                    print(f"\n[-] {len(invalid_goals)} goal(s) are Invalid:")
                    for g in invalid_goals:
                        print(f"    {g.strip()}")
                if rocq_proved > 0:
                    print(f"\n[*] {rocq_proved} goal(s) proved by Rocq, "
                          f"but {remaining} goal(s) still unproven.")
                print("\n[-] Verification FAILED or INCOMPLETE. Check the solver output.")
                if args.rocq:
                    _generate_rocq_obligations(mlw_filename, args.rocq, unproven_count, args.file)
                    sys.exit(2)
                sys.exit(1)

    except _MergeConservationError as e:
        # Tier-0 fail-closed soundness backstop: the prover-result aggregation lost a
        # goal, so the merged output can no longer be trusted to represent every
        # obligation. Refuse to report ANY verdict rather than risk a false green.
        print("\n[-] SOUNDNESS ABORT (merge conservation): " + str(e))
        print("    This is a tool bug in the best-of-N merge, not a proof outcome. "
              "See soundness-issue.md.")
        if getattr(args, "diagnostics_json", False):
            print(_json.dumps({
                "code": "PYCSL-MERGE-DROP",
                "stage": "prover-merge",
                "file": getattr(args, "file", ""),
                "line": 0,
                "message": str(e),
            }, sort_keys=True), file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("\n[!] ERROR: 'why3' command not found. Please ensure Why3 is installed and in your PATH.")
        sys.exit(1)
    finally:
        if not args.keep_mlw and os.path.exists(mlw_filename):
            os.remove(mlw_filename)


def _run_audit_mode(args: argparse.Namespace) -> int:
    """Handle --audit-proof / --audit-proof-rocq / --audit-proof-lean.

    Short-circuits the rest of the pipeline. Returns the exit code.

    With --reverify-proofs, after the namespace-presence audit passes,
    each cited proof file is recompiled via coqc / lake env lean and
    its Print Assumptions / #print axioms output is checked against
    the kernel-axiom allow-list (see sticky-01.md Phase 0).
    """
    from pathlib import Path
    from audit_proof import audit_rocq, audit_lean, AuditReport, print_report, _Directive
    py = Path(args.file)
    rocq_dir = Path(args.rocq_proofs_path) if args.rocq_proofs_path else None
    lean_dir = Path(args.lean_proofs_path) if args.lean_proofs_path else None
    reverify = getattr(args, "reverify_proofs", False)
    project_root = Path(__file__).resolve().parents[2]
    report = AuditReport()
    if args.audit_proof or args.audit_proof_rocq:
        report.extend(audit_rocq(py, rocq_dir, reverify=reverify,
                                  project_root=project_root))
    if args.audit_proof or args.audit_proof_lean:
        report.extend(audit_lean(py, lean_dir, reverify=reverify,
                                  project_root=project_root))
    print_report(report, f"Axiom-attribution audit ({py.name})")
    return report.exit_code


def _resolve_runtime_config(args: argparse.Namespace) -> Tuple[str, List[str]]:
    """Resolve `(memory_model, provers)` from CLI flags and agents-config.json. The CLI
    `--memory-model`/`--prover`/`--provers` flags override the config; the config overrides
    the built-in defaults (hoare; Alt-Ergo then Z3). (Extracted from `main`.)"""
    _config = {}
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "agents", "agents-config.json")
    if os.path.exists(config_path):
        with open(config_path) as _cf:
            _config = _json.load(_cf)

    memory_model = args.memory_model or _config.get("memory-model", "hoare")

    # (#44) 2.6.2 -> 2.6.3. The pinned version did not exist in the installed opam
    # switch, so `why3` answered "No prover ... corresponds to Alt-Ergo,2.6.2," and every
    # default run proceeded with Z3 ALONE — including the whole reference suite, where TEN
    # of the thirty remaining failures pass once Alt-Ergo is actually present. This
    # constant is ENVIRONMENT-COUPLED by nature; the loud banner in `_run_why3_prove` is
    # what makes the next mismatch visible instead of silent.
    _DEFAULT_PROVERS = ["Alt-Ergo,2.6.3,", "Z3,4.13.3,"]
    if args.prover is not None:
        provers = [args.prover]
    elif args.provers is not None:
        provers = [p.strip() for p in args.provers.split(",,") if p.strip()]
    else:
        cfg_provers = _config.get("provers", _DEFAULT_PROVERS)
        provers = ([p.strip() for p in cfg_provers.split(",,") if p.strip()]
                   if isinstance(cfg_provers, str) else cfg_provers)
    return memory_model, provers


def main() -> None:
    args = _parse_args()

    if not os.path.exists(args.file):
        print(f"[!] Error: File '{args.file}' not found.")
        sys.exit(1)

    # Audit-only mode short-circuits the pipeline.
    if args.audit_proof or args.audit_proof_rocq or args.audit_proof_lean:
        sys.exit(_run_audit_mode(args))

    memory_model, provers = _resolve_runtime_config(args)

    with open(args.file, "r") as f:
        source_code = f.read()

    try:
        mlw_code = _run_pipeline(source_code, memory_model, args)
    except PyCSLError as e:
        # Human message line: UNCHANGED (byte-identical to the pre-code text that
        # negative drivers + refactor gates match against).
        print(f"\n[!] PIPELINE ERROR:\n{e}")
        # Structural-only coded diagnostic, opt-in via --diagnostics-json (stderr).
        if getattr(args, "diagnostics_json", False):
            diag = e.as_dict()
            diag["file"] = diag.pop("filename") or args.file
            print(_json.dumps(diag, sort_keys=True), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] UNEXPECTED PIPELINE ERROR:\n{e}")
        sys.exit(1)

    base_name = os.path.splitext(args.file)[0]
    mlw_filename = f"{base_name}.mlw" if args.keep_mlw else _make_temp_mlw_path()
    _run_proofs(mlw_code, mlw_filename, provers, args)


if __name__ == "__main__":
    main()
