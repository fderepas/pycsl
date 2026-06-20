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
    g_proof.add_argument("--check-vacuity", action="store_true",
                        help="Run the NON-VACUITY GATE. After a file verifies, the gate "
                             "re-proves, per body-bearing function, a probe with an extra "
                             "`ensures false`: if that goal proves Valid the function's "
                             "assumed context is INCONSISTENT and its 'green' is VACUOUS "
                             "(every postcondition, axiom-backed or not, is discharged for "
                             "free) — the gate then FAILS the run, naming the function(s). A "
                             "vacuous context proves `false` near-instantly, so the probe "
                             "uses a short per-goal timelimit. Currently OPT-IN (it surfaces "
                             "pre-existing vacuities, e.g. csys yiq_to_rgb); intended to "
                             "become default-on once the corpus is swept clean. A missing "
                             "why3 skips the gate (not a failure).")
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
    return {"file": filename, "summary": counts, "vcs": vcs}


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


def _run_pipeline(source_code: str, memory_model: str, args: argparse.Namespace) -> str:
    """Run Modules 1–6 on *source_code*. Returns WhyML code string."""
    print(f"[*] Parsing and Semantic Analysis for '{args.file}'...")
    print(f"[*] Memory model: {memory_model}")

    # [Modules 1-3] Ingest, Parse, and Weave
    ingestor = Module1_Ingestor(source_code)
    extracted_data = ingestor.process()

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
    imported_names = _ir_resolve(ir_data, unified_ast, args.file, deep=args.deep)

    # 07-1143 R4: the Soundness Ledger is a provenance view of the fully-resolved IR
    # (after imports/inheritance/composition), so it runs here and short-circuits before
    # WhyML emission / proving.
    if getattr(args, "soundness_report", False):
        _print_soundness_report(_build_soundness_report(ir_data, args.file))
        sys.exit(0)

    json_ir = _json.dumps(ir_data)

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
    return transpiler.transpile()


def _why3_typecheck(mlw_filename: str):
    """Phase D honest gate: parse + typecheck the emitted WhyML with why3 (no proof).
    Returns ``(ok: bool, diagnostic: str)``. A run is only honestly SUCCESS if this
    passes — emitting text that does not even type-check is the silent success the spec
    (refactor.md §1.5 / Phase D) forbids. A missing why3 is NOT a failure (we do not turn
    an absent prover into a false typecheck-fail) — it is reported as skipped."""
    try:
        r = subprocess.run(["why3", "prove", "--type-only", mlw_filename],
                           capture_output=True, text=True)
    except FileNotFoundError:
        return True, "(why3 not found — typecheck skipped)"
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

# Verdict ranks: higher is better. Anything not Valid is non-Valid (unproven).
_VERDICT_VALID = 2
_VERDICT_NONVALID = 1  # Unknown / Timeout / Out of memory / Failure / Invalid / unparsed

def _verdict_rank(result_line: str) -> int:
    """Rank a Why3 `Prover result is: ...` line. ONLY a literal 'Valid' is Valid.

    Soundness: this is the single chokepoint that decides whether a goal counts
    as proven. It accepts ``Valid`` ONLY when the verdict token is exactly
    ``Valid`` (Why3 prints ``Valid (...)`` for a proven goal). ``Invalid`` and
    every other status (``Unknown``, ``Timeout``, ``Out of memory``,
    ``Failure``, ...) rank as non-Valid and can never be promoted."""
    # The verdict token follows "Prover result is: ". Why3 emits e.g.
    #   "Prover result is: Valid (0.03s, 20 steps)."
    #   "Prover result is: Unknown (unknown) (0.04s, 17627 steps)."
    #   "Prover result is: Timeout (30.0s)."  / "... Out of memory ..." / "... Failure ..."
    marker = "Prover result is:"
    idx = result_line.find(marker)
    token = result_line[idx + len(marker):].strip() if idx != -1 else result_line.strip()
    # Guard against "Invalid" (whose substring is "valid"): require the verdict to
    # START with the exact word "Valid".
    if token.startswith("Valid (") or token == "Valid" or token.startswith("Valid\t"):
        return _VERDICT_VALID
    return _VERDICT_NONVALID


def _parse_goal_blocks(output: str) -> "List[Tuple[str, str]]":
    """Split a `why3 prove` stdout into per-goal (header, result_line) pairs.

    A goal block is::

        File "<f>", line N, characters X-Y:
        Sub-goal <desc> of goal <name>'vc.
        Prover result is: <verdict> (...).

    The header (everything up to and including the line that PRECEDES the
    `Prover result is:` line) is the stable goal KEY — it is byte-identical across
    provers because it is derived from the same .mlw. The `Prover result is:` line
    is the per-prover verdict. Returns the blocks in document order; a header with
    no following result line (should not happen for a real goal) is skipped."""
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


def _merge_best_of_n(outputs: "List[str]") -> str:
    """Merge per-prover `why3 prove` outputs into ONE best-of-N output string.

    For each goal (keyed by its header block) keep the BEST verdict across
    provers (Valid dominates). The merged string has the SAME shape as a single
    `why3 prove` run, so the existing downstream success/parse logic consumes it
    unchanged. Goal order follows the first run that mentions the goal."""
    order: List[str] = []
    best: Dict[str, str] = {}        # header -> best result line
    best_rank: Dict[str, int] = {}   # header -> rank of best result line
    for out in outputs:
        for header, result_line in _parse_goal_blocks(out):
            r = _verdict_rank(result_line)
            if header not in best:
                order.append(header)
                best[header] = result_line
                best_rank[header] = r
            elif r > best_rank[header]:
                best[header] = result_line
                best_rank[header] = r
    parts: List[str] = []
    for header in order:
        block = (header + "\n" + best[header]) if header else best[header]
        parts.append(block)
    return "\n\n".join(parts)


def _all_goals_valid(output: str) -> bool:
    """True iff every parsed goal block is Valid (used for early-exit). An output
    with no goal blocks is NOT 'all valid' here (callers handle the empty case)."""
    blocks = _parse_goal_blocks(output)
    return bool(blocks) and all(_verdict_rank(r) == _VERDICT_VALID for _, r in blocks)


import re as _re

# Matches the goal-header location line `File "<path>", line <N>, characters X-Y:`.
_GOAL_LOC_RE = _re.compile(r'^File "(?P<file>.*)", line (?P<line>\d+), characters')


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
                      args: argparse.Namespace) -> "Optional[List[str]]":
    """Run the non-vacuity gate. Returns the list of vacuous function names (empty = all
    contexts consistent), or None if why3 is absent (skip-not-fail, like the typecheck
    gate).

    PER-FUNCTION probe (no cross-contamination): for each body-bearing function it emits
    a variant in which ONLY that function carries an extra `ensures { false }`, then proves
    JUST that postcondition goal (`-g <probe>:<line>`). A function whose assumed context is
    inconsistent proves `false`; a sound one cannot. Adding `ensures false` to every
    function at once would be wrong — a callee's injected `false` would propagate into every
    caller's assumed context and flag them all."""
    import tempfile
    fns, lines = _function_body_eqs(mlw_code)
    if not fns:
        return []
    base_cmd = ["why3", "prove", "-a", "split_vc"]
    if "\n  inductive " in mlw_code:
        base_cmd += ["-a", "induction_pr"]
    tl = str(getattr(args, "vacuity_timelimit", "5"))
    def _probe_one(fname_idx: "Tuple[str, int]") -> "Tuple[str, Optional[bool]]":
        """Probe one function. Returns (fname, vacuous?) — vacuous? is None if why3 is
        absent (so the caller can degrade the whole gate to skip-not-fail)."""
        fname, idx = fname_idx
        probe_lines = lines[:idx] + ["    ensures { false }"] + lines[idx:]
        probe_line_no = idx + 1   # 1-based line of the inserted `ensures { false }`
        fd, probe_path = tempfile.mkstemp(suffix=".mlw", prefix=".pycsl_vac_")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("\n".join(probe_lines) + "\n")
            sel = [f"{probe_path}:{probe_line_no}"]
            for p in provers:
                try:
                    r = _run_why3_prove(base_cmd, p, tl, probe_path, sel)
                except FileNotFoundError:
                    return fname, None
                if any(_verdict_rank(rl) == _VERDICT_VALID
                       for _, rl in _parse_goal_blocks(r.stdout)):
                    return fname, True
            return fname, False
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


def _residual_selectors(merged_output: str, mlw_filename: str) -> "List[str]":
    """Return the DISTINCT `<file>:<line>` Why3 sub-goal selectors for every goal in
    *merged_output* that is NOT yet Valid. Used to re-run the next prover ONLY on the
    residual goals (`why3 prove -g <file>:<line> ...`), so goals the first prover
    already proved do NOT pay for a second prover pass (the doctrine's "only residual
    goals pay"). Duplicate lines collapse: `-g file:line` selects every sub-goal at
    that line, which is a sound superset (re-proving an already-Valid sub-goal is
    cheap and the merge keeps the best verdict)."""
    sels: List[str] = []
    seen: Set[str] = set()
    for header, result_line in _parse_goal_blocks(merged_output):
        if _verdict_rank(result_line) == _VERDICT_VALID:
            continue
        # Find the `File "...", line N, ...` location ANYWHERE in the header block
        # (the block may carry a leading blank-line separator before the File line).
        m = None
        for hl in header.splitlines():
            m = _GOAL_LOC_RE.match(hl.strip())
            if m:
                break
        if not m:
            # Cannot locate this residual goal precisely — fall back to whole-file
            # (sound: a broader re-run can only prove MORE). Signal with empty list.
            return []
        sel = f"{m.group('file')}:{m.group('line')}"
        if sel not in seen:
            seen.add(sel)
            sels.append(sel)
    return sels


def _run_why3_prove(base_cmd: "List[str]", prover: str, timelimit: str,
                    mlw_filename: str,
                    goal_selectors: "Optional[List[str]]" = None
                    ) -> "subprocess.CompletedProcess":
    """Run `why3 prove ... -P <prover> --timelimit <t> [-g sel ...] <file>` for ONE
    prover.

    Each prover gets the FULL per-goal timelimit (it is not split across provers).
    `base_cmd` carries the shared transforms (`-a split_vc`, optional
    `-a induction_pr`). When *goal_selectors* is given, only those sub-goals
    (`-g <file>:<line>`) are attempted — the residual-only second-pass path."""
    cmd = list(base_cmd) + ["-P", prover, "--timelimit", timelimit]
    for sel in (goal_selectors or []):
        cmd += ["-g", sel]
    cmd += [mlw_filename]
    return subprocess.run(cmd, capture_output=True, text=True)


def _dispatch_provers(base_cmd: "List[str]", provers: List[str], timelimit: str,
                      mlw_filename: str) -> "Tuple[str, str, int]":
    """Per-goal best-of-N dispatch. Returns (merged_stdout, merged_stderr, returncode).

    - Single prover: exactly one `why3 prove` call (behaviour byte-identical to
      the legacy path — same flags, same output).
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
    if len(provers) == 1:
        r = _run_why3_prove(base_cmd, provers[0], timelimit, mlw_filename)
        return r.stdout.strip(), r.stderr.strip(), r.returncode

    # Try the legacy-reported (last-listed) prover first; then the rest, in their
    # listed order, restricted to residual goals. Soundness is order-independent.
    attempt_order = [provers[-1]] + provers[:-1]

    outputs: List[str] = []
    stderrs: List[str] = []
    last_rc = 0
    any_goal_blocks = False
    for idx, prover in enumerate(attempt_order):
        if idx == 0:
            # First prover: full file.
            selectors: Optional[List[str]] = None
        else:
            # Subsequent provers: ONLY the goals still non-Valid in the merge so far.
            selectors = _residual_selectors(_merge_best_of_n(outputs), mlw_filename)
            if selectors == []:
                # No precisely-locatable residuals OR none at all. If the merge is
                # already all-Valid we would have early-exited; reaching here with an
                # empty selector means we could not pin the residuals — fall back to a
                # full-file re-run (sound: only proves MORE), preserving correctness.
                if _all_goals_valid(_merge_best_of_n(outputs)):
                    break
                selectors = None
        r = _run_why3_prove(base_cmd, prover, timelimit, mlw_filename, selectors)
        out = r.stdout.strip()
        outputs.append(out)
        if r.stderr.strip():
            stderrs.append(r.stderr.strip())
        last_rc = r.returncode
        merged = _merge_best_of_n(outputs)
        if _parse_goal_blocks(merged):
            any_goal_blocks = True
            if _all_goals_valid(merged):
                # Every goal proven by some prover so far — no need to run the rest.
                return merged, "\n".join(stderrs), 0
        else:
            # No goal blocks (e.g. zero goals to prove). If this prover succeeded
            # with empty output, the legacy success path accepts it.
            if r.returncode == 0:
                return merged, "\n".join(stderrs), 0

    merged = _merge_best_of_n(outputs)
    # Final verdict: rc 0 iff every goal is Valid in the merge. If there were
    # genuinely no goal blocks, fall back to the last run's rc.
    if any_goal_blocks:
        rc = 0 if _all_goals_valid(merged) else (last_rc if last_rc != 0 else 1)
    else:
        rc = last_rc
    return merged, "\n".join(stderrs), rc


def _run_proofs(mlw_code: str, mlw_filename: str, provers: List[str], args: argparse.Namespace) -> None:
    """Write *mlw_code* to *mlw_filename*, invoke Why3, handle Rocq proofs and cleanup."""
    with open(mlw_filename, "w") as f:
        f.write(mlw_code)

    if args.no_proof:
        # refactor.md Phase D2: the honest typecheck gate is now DEFAULT-ON. A `--no-proof`
        # run is SUCCESS only if the emitted WhyML at least TYPE-CHECKS (`why3 prove
        # --type-only`) — never merely "text emitted" (§1.5). `--no-typecheck` opts out
        # (fast emit-only, for byte-diff/dev sweeps and when why3 is absent). `--typecheck`
        # is now a harmless no-op alias (the gate is already on). A missing why3 is treated
        # as skip-not-fail by `_why3_typecheck` (ok=True), so the gate never turns an absent
        # prover into a false failure.
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
                vac = _run_vacuity_gate(mlw_code, provers, args)
                if vac:
                    print("\n[-] NON-VACUITY GATE FAILED: the following function(s) verify "
                          "VACUOUSLY — their assumed context is logically inconsistent, so "
                          "every postcondition is discharged for free (the 'green' is meaningless):")
                    for name in vac:
                        print(f"    {name}  (proves `ensures false`)")
                    print("    Root cause is usually several nonlinear integer-division facts "
                          "coexisting in one context (helper `result == …//…` ensures, "
                          "division-bound inequalities, disjunctive value-equalities). See "
                          "getting-better/csys-vacuity-investigation/ROOT-CAUSE.md.")
                    print("    (Opt out with --no-vacuity-check; tune with --vacuity-timelimit.)")
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

        if returncode == 0 and not unknown_goals and not invalid_goals and ("Valid" in output or not output):
            _gate_vacuity_then_succeed("\n[+] Verification SUCCESS! All contracts formally proven.")
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
                    f"\n[+] Verification SUCCESS! All contracts formally proven "
                    f"({smt_proved} SMT + {rocq_proved} Rocq).")
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
    from audit_proof import audit_rocq, audit_lean, AuditReport, print_report
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

    _DEFAULT_PROVERS = ["Alt-Ergo,2.6.2,", "Z3,4.13.3,"]
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
