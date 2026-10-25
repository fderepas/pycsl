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
    g_strict.add_argument("--strict-latin1", action="store_true",
                        help="Drop the LATIN1-STR model assumption (route #276): "
                             "`ord` reads an uninterpreted code point in "
                             "[0, 0x10FFFF] (not Why3's 8-bit `Char.code`), and "
                             "`chr(n)` is not `Char.chr n`, so `ord(s) < 256` and "
                             "`ord(chr(300)) != 300` no longer prove. Off by "
                             "default — every str value is assumed to consist of "
                             "code points 0..255, a declared assumption listed by "
                             "--soundness-report. Costs every proof that feeds "
                             "`ord(..)` into a cited lemma over `Char.code`.")
    g_strict.add_argument("--strict-bare-containers", action="store_true",
                        help="Drop the BARE-CONTAINER-INT model assumption (route "
                             "#330): an element of a parameter annotated with a BARE "
                             "container (`list`, `List`, `Sequence`, `tuple`, ...) — "
                             "or a VALUE of a bare `dict` / `Dict` / `Mapping` (route "
                             "#334) — is of unknown type, so using it as an int (`xs[0] % 1 == 0`, "
                             "`xs[0] * 0 == 0`) is refused (PYCSL-R325-OPAQUE-INT-"
                             "FALLBACK). Off by default — such an element is read as an "
                             "`int`, a declared assumption listed by --soundness-report "
                             "(measured: 90 corpus files rely on it).")
    g_strict.add_argument("--strict-hval-keys", action="store_true",
                        help="Drop the HVAL-STR-KEYS model assumption (route #298): "
                             "the key of a NESTED `PyVal` dict (an `.items()` key or a "
                             "bare `for k in m` over a dict read out of a "
                             "`Dict[str, PyVal]`) is an unknown-typed value, not a "
                             "`str`, so `isinstance(k, str)` no longer proves and a "
                             "string operation on it does not type-check. Off by "
                             "default — `Dict[str, PyVal]` constrains only the "
                             "top-level keys, and every nested dict is assumed to "
                             "have str keys, a declared assumption listed by "
                             "--soundness-report.")
    g_strict.add_argument("--check-behavioral-subtyping", action="store_true",
                        help="Layer D (ON BY DEFAULT since route #277; kept for "
                             "compatibility): emit Liskov refinement goals for "
                             "overriding methods (pre_base ⇒ pre_sub, "
                             "post_sub ⇒ post_base, raise conditions) and refuse "
                             "an override that raises / assigns / renames "
                             "parameters beyond the base. Fails if an override "
                             "strengthens a precondition or weakens a "
                             "postcondition.")
    g_strict.add_argument("--assume-class-exact", action="store_true",
                        help="Turn the default override-refinement check OFF "
                             "(route #277): a value typed with a user class is "
                             "then ASSUMED to be an exact instance of it (a "
                             "subclass override is never seen by a caller). "
                             "This is the declared model assumption CLASS-EXACT, "
                             "listed by --soundness-report.")
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
    # ROUTE #282 — PARAM-DISJOINT. FIELD-DISJOINT's twin for PARAMETERS and ELEMENTS: each
    # mutable parameter (a list/dict/set ref, a record value, the receiver `self`) is its own
    # Why3 region, and a `List[List[int]]` / `List[<record>]` is an array of independent
    # values, so a write through `xs` leaves `ys` unchanged and a write to `xss[0][0]` leaves
    # `xss[1][0]` unchanged (the emitted frame says so). Python promises neither: `f(a, a)`,
    # `x.bump(x)`, `t.m(L)` with `L` held by `t.ys`, and `[r, r]` put ONE object behind two
    # names. A VERIFIED caller that builds the alias is refused or fails closed (Why3's
    # illegal-alias check, route #254, R167 #243/#244, the matrix/array type split); the
    # residue is an alias built in UNVERIFIED code — the ownership rule R1 again. Reported
    # for every function that WRITES through one mutable handle (a parameter or `self`:
    # subscript store/`del`, field store, augmented assignment, any method call on it, or
    # passing it to a non-builtin call, or an `assigns` location rooted at it) while it also
    # reads or writes ANOTHER mutable handle, and for every function that writes an ELEMENT
    # of a container handle (`xss[i][j] = ...`, `xss[i].append(...)`, an element-rooted
    # `assigns`). Conservative (over-, never under-reported): a parameter is a mutable
    # handle unless its annotation names only immutable builtins (int/float/str/bool/bytes/
    # complex/None, tuple/frozenset/Optional of those); handle types are not matched.
    _pd_immut = {"int", "float", "str", "bool", "bytes", "complex", "none", "tuple",
                 "frozenset", "optional", "literal", "final", "typing"}
    _pd_pure = {"len", "abs", "min", "max", "sorted", "sum", "list", "dict", "set", "tuple",
                "str", "int", "float", "bool", "isinstance", "range", "enumerate", "zip",
                "any", "all", "print", "repr", "hash", "id", "iter", "reversed", "ord",
                "chr", "map", "filter", "frozenset", "bytes", "type", "round", "divmod",
                "pow", "format", "callable", "issubclass", "hasattr", "getattr"}
    import re as _re_pd
    _pd_glob_ok: Set[str] = set(_pd_pure) | {"True", "False", "None", "self", "cls"}
    for _pd_f in funcs:
        _pd_glob_ok.add(str(_pd_f.get("name")))
        _pd_glob_ok.add(str(_pd_f.get("name")).split("__")[-1])
    for _pd_td in ir_data.get("type_decls") or []:
        if isinstance(_pd_td, dict):
            _pd_glob_ok.add(str(_pd_td.get("name")))
    for _pd_im in ir_data.get("imports") or []:
        if isinstance(_pd_im, (list, tuple)) and _pd_im:
            _pd_glob_ok.add(str(_pd_im[0]))
    _pd_uses: List[str] = []
    for f in funcs:
        _pd_h: Set[str] = set()
        for _pd_n, _pd_t in (f.get("param_annotations") or {}).items():
            _pd_toks = _re_pd.findall(r"[A-Za-z_][A-Za-z_0-9]*", str(_pd_t or ""))
            if not _pd_toks or any(_pd_k.lower() not in _pd_immut for _pd_k in _pd_toks):
                _pd_h.add(str(_pd_n))
        for _pd_n in f.get("formal_params") or []:
            if (isinstance(_pd_n, str)
                    and _pd_n not in (f.get("param_annotations") or {})):
                _pd_h.add(_pd_n)  # unannotated: may be anything
        if f.get("kind") == "method" or f.get("self_type"):
            _pd_h.add("self")
        # a module-level name the function reads (not a local, parameter, function, type,
        # import or builtin) may be a mutable global: a handle too (`f(G)` aliases it)
        _pd_loc = set(f.get("symbol_table") or {}) | set(f.get("formal_params") or [])
        _pd_gstack: List[Any] = [f.get("body", [])]
        while _pd_gstack:
            _pd_n = _pd_gstack.pop()
            if isinstance(_pd_n, list):
                _pd_gstack.extend(_pd_n)
                continue
            if not isinstance(_pd_n, dict):
                continue
            _pd_gstack.extend(_pd_n.values())
            if isinstance(_pd_n.get("target"), str):
                _pd_loc.add(_pd_n["target"])
            for _pd_k in ("targets", "vars"):
                for _pd_t in _pd_n.get(_pd_k) or [] if isinstance(
                        _pd_n.get(_pd_k), list) else []:
                    if isinstance(_pd_t, str):
                        _pd_loc.add(_pd_t)
            if (_pd_n.get("type") == "Var" and isinstance(_pd_n.get("name"), str)
                    and _pd_n["name"] not in _pd_loc and _pd_n["name"] not in _pd_glob_ok):
                _pd_h.add(_pd_n["name"])
        if not _pd_h:
            continue
        _pd_w: Set[str] = set()
        _pd_ew: Set[str] = set()
        _pd_a: Set[str] = set()

        _pd_stack: List[Any] = [f.get("body", []), f.get("contracts", {})]
        while _pd_stack:
            _pd_n = _pd_stack.pop()
            if isinstance(_pd_n, list):
                _pd_stack.extend(_pd_n)
                continue
            if not isinstance(_pd_n, dict):
                continue
            _pd_stack.extend(_pd_n.values())
            if _pd_n.get("type") == "Var":
                _pd_a.add(str(_pd_n.get("name")))
            elif _pd_n.get("type") == "FieldGet" and isinstance(_pd_n.get("object"), str):
                _pd_a.add(_pd_n["object"].split(".")[0])
            _pd_s = _pd_n.get("stmt")
            # (location node, written-at-an-element) candidates; a str location is a
            # dotted IR object path such as "self.ys"
            _pd_c: List[Tuple[Any, bool]] = []
            if _pd_s in ("ArraySet", "ArraySliceSet", "DelSubscript"):
                _pd_c.append((_pd_n.get("array"), isinstance(_pd_n.get("array"), dict)
                              and _pd_n["array"].get("type") == "Subscript"))
            elif _pd_s in ("FieldAssign", "FieldAugAssign"):
                _pd_c.append((_pd_n.get("object"), False))
            elif _pd_s == "AugAssign" and isinstance(_pd_n.get("target"), str):
                _pd_c.append((_pd_n["target"], False))
            if _pd_n.get("type") == "Call":
                _pd_fn = _pd_n.get("func")
                if isinstance(_pd_fn, str) and "." in _pd_fn:
                    _pd_c.append((_pd_fn.rsplit(".", 1)[0], False))
                elif isinstance(_pd_n.get("receiver"), dict):
                    _pd_c.append((_pd_n["receiver"],
                                  _pd_n["receiver"].get("type") == "Subscript"))
                if not (isinstance(_pd_fn, str) and _pd_fn in _pd_pure):
                    for _pd_g in list(_pd_n.get("args") or []) + [
                            _pd_kw.get("value") if isinstance(_pd_kw, dict) else _pd_kw
                            for _pd_kw in (_pd_n.get("keywords") or [])]:
                        _pd_c.append((_pd_g, False))
            if _pd_n is f.get("contracts"):
                _pd_c.extend((_pd_l, False) for _pd_l in (_pd_n.get("assigns") or []))
            for _pd_x, _pd_e in _pd_c:
                # the root name of the location, and whether it passes through an element
                while isinstance(_pd_x, dict):
                    _pd_k = _pd_x.get("type")
                    if _pd_k == "Var":
                        _pd_x = str(_pd_x.get("name"))
                    elif _pd_k == "FieldGet":
                        _pd_x = str(_pd_x.get("object"))
                    elif _pd_k == "Attribute":
                        _pd_x = _pd_x.get("object")
                    elif _pd_k == "Subscript":
                        _pd_e = _pd_e or (isinstance(_pd_x.get("value"), dict)
                                          and _pd_x["value"].get("type") == "Subscript")
                        _pd_x = _pd_x.get("value")
                    else:
                        _pd_x = None
                if not isinstance(_pd_x, str):
                    continue
                _pd_e = _pd_e or "[" in _pd_x
                _pd_x = _pd_x.split(".")[0].split("[")[0]
                if _pd_x in _pd_h:
                    _pd_w.add(_pd_x)
                    if _pd_e:
                        _pd_ew.add(_pd_x)
        for _pd_x in sorted(_pd_w):
            _pd_o = sorted(((_pd_a | _pd_w) & _pd_h) - {_pd_x})
            if _pd_o:
                _pd_uses.append("%s: writes through %s, also accesses %s" % (
                    f["name"], _pd_x, ", ".join(_pd_o)))
        for _pd_x in sorted(_pd_ew):
            _pd_uses.append("%s: writes an element of %s (its elements may be one object)"
                            % (f["name"], _pd_x))
    # ROUTE #276 — LATIN1-STR. A `str` is a Why3 `string` of `string.Char`s, and Why3's
    # `axiom code` bounds every Char code by 256: `ord(s) < 256` and `ord(chr(300)) != 300`
    # PROVE (CPython: 8364 for "€", 300). Reported for every `ord`/`chr` call (body or
    # contract: they rely on it DIRECTLY — the bound, the `chr` round trip below 256, and
    # every cited codec lemma over `Char.code`), and, because the str SORT itself is the
    # 8-bit string, for every function that reads a str value at all (a str-typed
    # variable, field or `\result`, or a string literal). Conservative (over-, never
    # under-reported).
    _l1_uses: List[str] = []
    for f in funcs:
        _l1_types: Set[str] = set()
        for _l1_src in (f.get("symbol_table") or {}, f.get("param_annotations") or {}):
            for _l1_n, _l1_t in _l1_src.items():
                if isinstance(_l1_t, str) and _l1_t.split("[")[0].strip().lower() == "str":
                    _l1_types.add(_l1_n)
        _l1_ret = str(f.get("return_annotation") or "").split("[")[0].strip().lower()
        _l1_calls: List[str] = []
        _l1_vals: Set[str] = set()
        for _l1_part, _l1_root in (("body", f.get("body", [])),
                                   ("contract", f.get("contracts", {}))):
            _l1_stack: List[Any] = [_l1_root]
            while _l1_stack:
                _l1_n = _l1_stack.pop()
                if isinstance(_l1_n, list):
                    _l1_stack.extend(_l1_n)
                    continue
                if not isinstance(_l1_n, dict):
                    continue
                _l1_stack.extend(_l1_n.values())
                _l1_k = _l1_n.get("type")
                if _l1_k == "Call" and _l1_n.get("func") in ("ord", "chr"):
                    _l1_calls.append("%s: %s(...) in %s" % (
                        f["name"], _l1_n["func"], _l1_part))
                elif _l1_k == "Var" and _l1_n.get("name") in _l1_types:
                    _l1_vals.add(str(_l1_n["name"]))
                elif (_l1_k == "FieldGet"
                      and _ma_fields.get(_l1_n.get("field")) == "str"):
                    _l1_vals.add("%s.%s" % (_l1_n.get("object"), _l1_n.get("field")))
                elif _l1_k == "Result" and _l1_ret == "str":
                    _l1_vals.add("\\result")
                elif _l1_k == "String":
                    _l1_vals.add("a string literal")
        _l1_uses.extend(_l1_calls)
        if _l1_vals:
            _l1_uses.append("%s: str values (8-bit string model) %s" % (
                f["name"], ", ".join(sorted(_l1_vals))))
    # ROUTE #298 — HVAL-STR-KEYS. The `hval` value model (`Dict[str, PyVal]`) keys every
    # NESTED dict by `string` (`HMap` over `hpairs`; the `.items()` key walk
    # `hval_keys_get` returns a `string`, the bare-loop `HMap` arm an `HStr`), but the
    # annotation constrains only the TOP-level keys: `{"xs": {1: 2}}` is a legal argument.
    # Reported for every loop (statement or comprehension) of a function that holds an
    # `Any`-typed (PyVal) value and whose iterable is a key view (`.items()` / `.keys()`)
    # or a bare iteration of a value that is not a declared parameter/field: a local, a
    # subscript or a `.get` read (over-, never under-reported: the carrier is not resolved
    # here; a list carrier is reported too).
    # ROUTE #330 — BARE-CONTAINER-INT. An element of a parameter annotated with a BARE
    # container (`list`, `List`, `Sequence`, `tuple`, ... — no element type) is lowered to
    # an `int` (`xs: list` is `array int`, `xs: List` an `int` read by `subscript_get`),
    # though the annotation admits any element: `xs[0] % 1 == 0` proves of `[0.5]`.
    # Making every such element an R325 origin refused 90 corpus files (measured), so the
    # int reading is DECLARED; `--strict-bare-containers` drops it. ROUTE #334: a VALUE of
    # a bare `dict` / `Dict` / `Mapping` parameter (lowered `map .. (option int)`) is under
    # the same assumption (default-origin measured: 3 corpus + 1 mirror file refused).
    _bc_uses: List[str] = []
    for f in funcs:
        for _bc_n, _bc_t in (f.get("param_annotations") or {}).items():
            if isinstance(_bc_t, str) and _bc_t.strip().split(".")[-1] in (
                    "list", "List", "Sequence", "Iterable", "tuple", "Tuple",
                    "MutableSequence", "Collection", "dict", "Dict", "Mapping",
                    "MutableMapping"):
                _bc_uses.append("%s: parameter %s: %s" % (f["name"], _bc_n, _bc_t.strip()))
    _hk_uses: List[str] = []
    for f in funcs:
        _hk_st = f.get("symbol_table") or {}
        _hk_any = {_n for _n, _t in _hk_st.items()
                   if isinstance(_t, str) and ("Any" in _t or "PyVal" in _t)}
        if not _hk_any:
            continue
        _hk_params = set((f.get("param_annotations") or {}).keys())
        _hk_stack: List[Any] = [f.get("body", [])]
        while _hk_stack:
            _hk_n = _hk_stack.pop()
            if isinstance(_hk_n, list):
                _hk_stack.extend(_hk_n)
                continue
            if not isinstance(_hk_n, dict):
                continue
            _hk_stack.extend(_hk_n.values())
            _hk_it = _hk_n.get("iter")
            if not isinstance(_hk_it, dict):
                continue
            _hk_view = ""
            _hk_rv: Any = _hk_it
            if _hk_it.get("type") == "Call":
                _hk_fn = _hk_it.get("func")
                if isinstance(_hk_fn, str) and _hk_fn.rsplit(".", 1)[-1] in ("items", "keys"):
                    _hk_view = "." + _hk_fn.rsplit(".", 1)[-1] + "()"
                    _hk_rv = (_hk_it.get("receiver") if "." not in _hk_fn
                              else {"type": "Var", "name": _hk_fn.rsplit(".", 1)[0]})
                elif _hk_fn == "get" or (isinstance(_hk_fn, str) and _hk_fn.endswith(".get")):
                    _hk_view = "bare iteration"
                else:
                    continue
            elif _hk_it.get("type") in ("Var", "Subscript", "BoolOp", "BinOp"):
                _hk_view = "bare iteration"
            else:
                continue
            _hk_root = _hk_rv
            while isinstance(_hk_root, dict) and _hk_root.get("type") in (
                    "Subscript", "BoolOp", "BinOp", "Call"):
                _hk_root = (_hk_root.get("value") or _hk_root.get("left")
                            or _hk_root.get("receiver"))
            _hk_nm = (_hk_root.get("name") if isinstance(_hk_root, dict)
                      and _hk_root.get("type") == "Var" else None)
            if (isinstance(_hk_nm, str) and (_hk_nm.startswith("self.")
                                              or (_hk_rv is _hk_root
                                                  and _hk_nm in _hk_params))):
                continue  # a declared parameter/field: its own keys are annotated
            if _hk_view == "bare iteration" and _hk_rv is _hk_root and (
                    not isinstance(_hk_nm, str) or _hk_nm not in _hk_any):
                continue  # a bare typed local (list/str/...): not an hval
            _hk_uses.append("%s: %s over a nested PyVal value (line %s)" % (
                f["name"], _hk_view, _hk_n.get("line", _hk_n.get("lineno", "?"))))
    # ROUTE #277 — CLASS-EXACT, reported only when the default override-refinement check
    # is turned off (`--assume-class-exact`; `_run_pipeline` marks the IR). A method call
    # on a receiver typed with a user class `A` is verified against `A.m`'s contract; a
    # subclass instance runs the override, which nothing then checks. Reported for every
    # override pair of the unit (the refinement that is not checked) and every method
    # call whose method name is a method of a class of the unit (over-, never
    # under-reported: the receiver's class is not resolved here).
    _ce_uses: List[str] = []
    if ir_data.get("class_exact_assumed"):
        _ce_meths: Set[str] = set()
        for f in funcs:
            _ce_st = f.get("self_type")
            if f.get("kind") == "method" and isinstance(_ce_st, str) and _ce_st:
                _ce_pre = _ce_st.lower() + "__"
                if str(f.get("name", "")).startswith(_ce_pre):
                    _ce_meths.add(f["name"][len(_ce_pre):])
        for _ce_o in ir_data.get("overrides") or []:
            if isinstance(_ce_o, dict) and not _ce_o.get("from_conforms_to"):
                _ce_uses.append("override %s of %s: refinement not checked" % (
                    _ce_o.get("sub_method"), _ce_o.get("base_method")))
        for f in funcs:
            _ce_stack: List[Any] = [f.get("body", []), f.get("contracts", {})]
            while _ce_stack:
                _ce_n = _ce_stack.pop()
                if isinstance(_ce_n, list):
                    _ce_stack.extend(_ce_n)
                    continue
                if not isinstance(_ce_n, dict):
                    continue
                _ce_stack.extend(_ce_n.values())
                _ce_fn = _ce_n.get("func") if _ce_n.get("type") == "Call" else None
                if (isinstance(_ce_fn, str) and ("." in _ce_fn or "receiver" in _ce_n)
                        and _ce_fn.rsplit(".", 1)[-1] in _ce_meths):
                    _ce_uses.append("%s: %s(...) on a user-class receiver" % (
                        f["name"], _ce_fn))
    assumptions: List[Dict[str, Any]] = []
    if _ce_uses:
        assumptions.append({
            "name": "CLASS-EXACT",
            "statement": "a value whose static type is a user class is an exact instance "
                         "of it: a method call is verified against that class's method "
                         "contract, and no subclass override's refinement of it is "
                         "checked (the default checks it; this run passed "
                         "--assume-class-exact)",
            "counterexample": "class B(A): m -> 2 against A.m ensures \\result == 1; "
                              "use(a: A) -> a.m() == 1 for a = B() (corpus 3100-3101)",
            "strict_mode": "the default (drop --assume-class-exact)",
            "relied_on_by": sorted(set(_ce_uses)),
        })
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
    if _pd_uses:
        assumptions.append({
            "name": "PARAM-DISJOINT",
            "statement": "two distinct mutable parameters (list/dict/set/record-valued, "
                         "or a parameter and the receiver self or one of its fields) hold "
                         "distinct objects, and distinct elements of a list/dict parameter "
                         "hold distinct objects, so a mutation through one is invisible "
                         "through the other (ownership discipline rule R1; FIELD-DISJOINT "
                         "for parameters and elements)",
            "counterexample": "a = [1]; f(a, a): f writes xs[0] and claims ys[0] unchanged; "
                              "r = [0]; f([r, r]): a write to xss[0][0] is seen at "
                              "xss[1][0] (corpus 3180-3188)",
            "strict_mode": None,
            "relied_on_by": sorted(set(_pd_uses)),
        })
    if _l1_uses:
        assumptions.append({
            "name": "LATIN1-STR",
            "statement": "every str value consists of code points 0..255 (str is modelled "
                         "as the Why3 string of string.Char, whose codes are < 256): "
                         "ord(c) < 256, and chr(n) is modelled only for 0 <= n < 256; "
                         "str values in general rely on it (the str sort is the 8-bit "
                         "string), ord/chr sites directly",
            "counterexample": "s = '\u20ac': ord(s) == 8364, yet ord(s) < 256 proves; "
                              "ord(chr(300)) != 300 proves (corpus 3020-3021)",
            "strict_mode": "--strict-latin1",
            "relied_on_by": sorted(set(_l1_uses)),
        })
    if _bc_uses:
        assumptions.append({
            "name": "BARE-CONTAINER-INT",
            "statement": "an element of a parameter annotated with a bare container "
                         "(list / List / Sequence / tuple / ..., no element type) is an "
                         "int: the element is lowered to the int sort, as if the "
                         "annotation were List[int]; likewise a VALUE of a bare dict / "
                         "Dict / Mapping parameter (as if Dict[K, int], route #334)",
            "counterexample": "def g(xs: list): return xs[0] * 0 == 0 proves \\result == "
                              "True; g(['a']) is False (corpus 4348-4349); def g(d: "
                              "dict): return d['a'] % 1 == 0 proves; g({'a': 0.5}) is "
                              "False (corpus 4443, strict twin 4427)",
            "strict_mode": "--strict-bare-containers",
            "relied_on_by": sorted(set(_bc_uses)),
        })
    if _hk_uses:
        assumptions.append({
            "name": "HVAL-STR-KEYS",
            "statement": "every dict nested inside a PyVal value (Dict[str, PyVal]) has str "
                         "keys: the hval model keys an HMap by string, so a key read off a "
                         "nested dict (.items()/.keys() key, bare iteration of a dict "
                         "carrier) is a str (the annotation constrains only the top-level "
                         "keys)",
            "counterexample": "xs = d['xs']; for k, v in xs.items(): return isinstance(k, str) "
                              "proves \\result == True; f({'xs': {1: 2}}) is False "
                              "(corpus 3550-3551)",
            "strict_mode": "--strict-hval-keys",
            "relied_on_by": sorted(set(_hk_uses)),
        })
    # (#49) ROUTE #292 — A CITED `#@ proof` LEMMA IS EMITTED AS A Why3 `axiom`: the
    # proof's soundness rests on the Rocq/Lean statement AND on the restatement being
    # applied only where it was proved (`UnixFs.Struct.i2.round_trip` was applied to a
    # `>??` format it was never proved for). Every citation is listed as a TCB entry.
    _cited: Dict[str, Dict[str, Any]] = {}
    for f in funcs:
        for _c292 in (f.get("proof") or []):
            if not isinstance(_c292, dict) or not _c292.get("qualname"):
                continue
            _e292 = _cited.setdefault(str(_c292["qualname"]),
                                      {"qualname": str(_c292["qualname"]),
                                       "provers": [], "cited_by": []})
            if _c292.get("prover") and _c292["prover"] not in _e292["provers"]:
                _e292["provers"].append(str(_c292["prover"]))
            if f["name"] not in _e292["cited_by"]:
                _e292["cited_by"].append(f["name"])
    return {"file": filename, "summary": counts, "vcs": vcs,
            "model_assumptions": assumptions,
            "cited_lemmas": [_cited[_k] for _k in sorted(_cited)]}


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
    cl = report.get("cited_lemmas") or []
    if cl:
        print("  --- TCB entries: cited proof-assistant lemmas (emitted as Why3 axioms) ---")
        for c in cl:
            print(f"    {c['qualname']}  [{', '.join(c['provers']) or '?'}]  "
                  f"cited by: {', '.join(c['cited_by'])}")
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
    # (#49) ROUTE #277 — OVERRIDE REFINEMENT IS ON BY DEFAULT. A method call on a receiver
    # typed with a user class `A` uses `A.m`'s contract, and a subclass `B(A)` whose `m`
    # does not refine it made `use(a: A)` prove `\result == 1` while CPython returns 2
    # (witnesses-r277: local and cross-module). The refinement goal existed only under the
    # opt-in `--check-behavioral-subtyping`, and nothing declared the default's
    # assumption. MEASURED (gen #37): default-on adds goals to 11 of 1792 + 2186 corpus
    # files (3 PASS -> FAIL, each a real Liskov violation of the program: 0445, 1348,
    # pyref 0206) and to 2 of 53 mirror files (25 goals, all `true -> true`). So the
    # check is the default; `--assume-class-exact` turns it off and is then a DECLARED
    # model assumption (CLASS-EXACT, listed by `--soundness-report`).
    if not getattr(args, "assume_class_exact", False):
        args.check_behavioral_subtyping = True

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
    # (#49) ROUTE #322 — A FLOAT MODULE CONSTANT HAS NO INT MODEL. `math.pi` lowered to the
    # generic opaque getter `val get_pi (x: int) : int` (and `from math import pi` to an
    # opaque `val constant pi : int`), so every claim true of ALL INTEGERS was proved of
    # pi: `math.pi % 1 == 0` PROVED (CPython 0.14159...). The float constants of `math` /
    # `cmath` and every `sys.float_info.<f>` are refused wherever they are read (body or
    # contract); typing them `real` is the FLOAT-FINITE model's job, not this fold's.
    _r322_floats = {"pi", "e", "tau", "inf", "nan", "infj", "nanj"}
    _r322_mods = {}
    _r322_names = {}
    for _im322 in (ir_data.get("imports") or []):
        if not (isinstance(_im322, list) and len(_im322) == 5):
            continue
        if _im322[4] and _im322[1] in ("math", "cmath", "sys"):
            _r322_mods[str(_im322[0])] = str(_im322[1])
        elif (not _im322[4] and _im322[2] in ("math", "cmath")
                and _im322[1] in _r322_floats):
            _r322_names[str(_im322[0])] = f"{_im322[2]}.{_im322[1]}"
        elif not _im322[4] and _im322[2] == "sys" and _im322[1] == "float_info":
            _r322_names[str(_im322[0])] = "sys.float_info"
        elif not _im322[4] and _im322[1] == "*" and _im322[2] in ("math", "cmath", "sys"):
            # `from math import *` binds every constant by its bare name (MEASURED: `pi % 1
            # == 0` PROVED through `val constant pi : int`); any read of such a name refuses.
            for _f322 in (("float_info",) if _im322[2] == "sys" else sorted(_r322_floats)):
                _r322_names[_f322] = f"{_im322[2]}.{_f322}"
    if _r322_mods or _r322_names:
        _st322 = [_v322 for _k322, _v322 in ir_data.items() if _k322 != "imports"]
        # A MODULE- or CLASS-level binding (`PI = math.pi`) is not in the IR at all: the
        # name then lowers to the opaque `val constant PI : int` (MEASURED: `PI % 1 == 0`
        # PROVED). Read those bindings off the parsed SOURCE (the woven tree is not `ast`).
        import ast as _ast322
        _top322 = list(_ast322.parse(source_code).body)
        _top322 += [_s322 for _c322 in _top322 if isinstance(_c322, _ast322.ClassDef)
                    for _s322 in _c322.body]
        # `sys.float_info.<int field>` (`max_10_exp`, `dig`, ...) is an INT: the opaque-int
        # lowering is faithful there (BUILTIN-EXACT), so only the FLOAT fields (`max`, `min`,
        # `epsilon`) and a bare / unknown-field `float_info` read refuse. (MEASURED: the
        # self-annotation mirror's pure_ast `_INFSTR = '1e' + repr(_sys.float_info.max_10_exp
        # + 1)` was refused, dropping a verified mirror file.)
        _r322_int_fields = {"max_exp", "max_10_exp", "min_exp", "min_10_exp", "dig",
                            "mant_dig", "radix", "rounds"}
        _ok322 = set()
        for _s322 in _top322:
            if not isinstance(_s322, (_ast322.Assign, _ast322.AnnAssign, _ast322.AugAssign)):
                continue
            for _a322 in _ast322.walk(_s322):
                if (isinstance(_a322, _ast322.Attribute) and _a322.attr in _r322_int_fields
                        and isinstance(_a322.value, _ast322.Attribute)
                        and _a322.value.attr == "float_info"):
                    _ok322.add(id(_a322.value))
            for _a322 in _ast322.walk(_s322):
                if id(_a322) in _ok322:
                    continue
                if (isinstance(_a322, _ast322.Attribute)
                        and isinstance(_a322.value, _ast322.Name)):
                    _m322 = _r322_mods.get(_a322.value.id)
                    if _m322 in ("math", "cmath") and _a322.attr in _r322_floats:
                        _st322.append({"type": "Attribute", "attr": _a322.attr,
                                       "object": {"type": "Var", "name": _a322.value.id}})
                    elif _m322 == "sys" and _a322.attr == "float_info":
                        _st322.append({"type": "Attribute", "attr": "float_info",
                                       "object": {"type": "Var", "name": _a322.value.id}})
                elif (isinstance(_a322, _ast322.Name)
                        and isinstance(_a322.ctx, _ast322.Load)
                        and _a322.id in _r322_names):
                    _st322.append({"type": "Var", "name": _a322.id})
                elif (isinstance(_a322, _ast322.Call)
                        and isinstance(_a322.func, _ast322.Name)
                        and _a322.func.id == "getattr" and _a322.args
                        and isinstance(_a322.args[0], _ast322.Name)
                        and _a322.args[0].id in _r322_mods):
                    _st322.append({"type": "Call", "func": "getattr", "args": [
                        {"type": "Var", "name": _a322.args[0].id},
                        ({"type": "String", "value": _a322.args[1].value}
                         if (len(_a322.args) > 1
                             and isinstance(_a322.args[1], _ast322.Constant)
                             and isinstance(_a322.args[1].value, str))
                         else {"type": "Var", "name": "?"})]})
        while _st322:
            _n322 = _st322.pop()
            if isinstance(_n322, list):
                _st322.extend(_n322)
                continue
            if not isinstance(_n322, dict):
                continue
            _hit322 = None
            _o322 = _n322.get("object")
            if (_n322.get("type") == "Attribute" and isinstance(_o322, dict)
                    and _o322.get("type") == "Var"):
                _m322 = _r322_mods.get(_o322.get("name"))
                if _m322 in ("math", "cmath") and _n322.get("attr") in _r322_floats:
                    _hit322 = f"{_m322}.{_n322.get('attr')}"
                elif _m322 == "sys" and _n322.get("attr") == "float_info":
                    _hit322 = "sys.float_info"
            elif _n322.get("type") == "Var" and _n322.get("name") in _r322_names:
                _hit322 = _r322_names[_n322.get("name")]
            elif (_n322.get("type") == "Call" and _n322.get("func") == "getattr"
                    and isinstance(_n322.get("args"), list) and _n322["args"]
                    and isinstance(_n322["args"][0], dict)
                    and _n322["args"][0].get("type") == "Var"
                    and _n322["args"][0].get("name") in _r322_mods):
                # `getattr(math, "pi")` reads the same constant through an opaque
                # `pycsl_getattr_missing_* : int` (MEASURED: `% 1 == 0` PROVED); a
                # non-literal attribute name may name it too.
                _m322 = _r322_mods[_n322["args"][0]["name"]]
                _a2322 = _n322["args"][1] if len(_n322["args"]) > 1 else None
                _an322 = (_a2322.get("value") if isinstance(_a2322, dict)
                          and _a2322.get("type") == "String" else None)
                if (_an322 is None
                        or (_m322 in ("math", "cmath") and _an322 in _r322_floats)
                        or (_m322 == "sys" and _an322 == "float_info")):
                    _hit322 = f"getattr({_m322}, {_an322 or '<non-literal>'})"
            if (_n322.get("type") == "Attribute" and _n322.get("attr") in _r322_int_fields
                    and isinstance(_o322, dict) and _o322.get("type") == "Attribute"
                    and _o322.get("attr") == "float_info"):
                # an INT field of sys.float_info: faithful; do not descend into the
                # `float_info` object (it would refuse), but scan its own object chain.
                _st322.extend([_v322 for _k322, _v322 in _n322.items() if _k322 != "object"])
                _st322.extend([_v322 for _k322, _v322 in _o322.items() if _k322 != "attr"
                               and not (isinstance(_v322, dict) and _v322.get("type") == "Var"
                                        and _r322_mods.get(_v322.get("name")) == "sys")])
                continue
            if _hit322 is not None:
                raise _PyCSLSemanticError(
                    f"{args.file}: PYCSL-R322-FLOAT-MODULE-CONSTANT (route #322) — "
                    f"`{_hit322}` is a Python FLOAT constant and PyCSL has no faithful "
                    f"model of it here: it would lower to an opaque INT, under which "
                    f"every claim true of all integers (`x % 1 == 0`, "
                    f"`x // 1 == x`) is proved of it. Refused (fail closed). Pass the value "
                    f"in as a `float` parameter with an explicit `requires` bound instead.")
            _st322.extend(_n322.values())

    # refactor.md Phase C (C2b): run the four post-Module5 IR-resolution passes — in
    # order: import resolution → inheritance (Layers B+C) → Tier-1 composition →
    # inline-globals — via the front-end's single resolution entry, leaving ir_data the
    # fully RESOLVED IR (the wire Module 6 / the core consumes). Pure relocation: the
    # passes and their order are unchanged, so emission stays byte-identical.
    # (#49) ROUTE #304 — snapshot the program's class bases BEFORE resolution: the
    # inheritance merge clears `td["bases"]`, and Module 6 needs a raised class's ancestry
    # to decide whether a `#@ no_exception <Named>` claim covers an own `raise` of it. Kept
    # OFF the IR (the frozen front-end goldens); handed to the transpiler as an attribute.
    _r304_class_bases = {str(_td304["name"]): [str(_b304) for _b304 in _td304["bases"]]
                         for _td304 in (ir_data.get("type_decls", []) or [])
                         if _td304.get("bases") and _td304.get("name")}
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
                    + " and the override-refinement check is on (the default since route "
                    "#277, or `--check-behavioral-subtyping`), but a DUNDER is "
                    "not emitted as a function, so no override pair is recorded and NO "
                    "refinement goal is built. The run would report `All contracts "
                    "formally proven` with the substitutability obligation silently "
                    "absent (route #216, the same shape as route #97). Refusing instead "
                    "of certifying. FIX: give the method a non-dunder name — the "
                    "identical program spelled `m` instead of `__len__` produces the goal "
                    "`sub__m_refines_base` and is checked — or pass "
                    "`--assume-class-exact`, which then declares the CLASS-EXACT "
                    "assumption for this pair rather than claiming it was checked.",
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

    # (#49) ROUTE #290 — THE MUTATION BY ANOTHER NAME. Route #162's module-function
    # denylist and route #280's computed-receiver guard key on a METHOD NAME at a CALL whose
    # callee is a plain dotted name. Every other spelling of the same in-place mutation
    # walked past both. MEASURED at 7313506b, each under a callee `#@ assigns \nothing`
    # whose caller then PROVED the list unchanged (CPython mutates it):
    #   `xs.__setitem__(0, 9)`, `xs.__delitem__(0)`, `xs.__imul__(2)`, `list.__setitem__(
    #   xs, 0, 9)` (an explicit DUNDER / an UNBOUND type method: lowered to an abstract op
    #   with no `writes`); `getattr(xs, 'reverse')()`, `operator.methodcaller('reverse')(
    #   xs)`, `functools.partial(list.reverse, xs)()`, `(lambda: xs.reverse())()`,
    #   `(xs.reverse if c else xs.sort)()`, `(xs.reverse,)[0]()`, `(h := xs.reverse)()`
    #   (a COMPUTED CALLEE: Module 5's `_py_expr_call` catch-all erases the WHOLE call,
    #   callee and arguments, to `UnknownPyExpr` — a fresh `(any int)` VALUE with NO
    #   EFFECT, so an expression statement vanishes). 22 of 56 census probes PROVED.
    # THE RULE (source AST, inline — `_run_pipeline` is the choke point: its mirror twin
    # is `\trusted` and already raises, so no ledger moves; Module 5's `_py_expr_call`
    # stub is `\trusted` WITHOUT `#@ raises`, lesson d5):
    #   (1) a call whose callee is neither a name nor a dotted attribute is REFUSED, except
    #       the shapes Module 5 resolves to a real node — the class-by-name factory
    #       `F(<lit|name|subscript>)(...)` of a one-line `return G[p]` lookup function,
    #       the `getattr(self, <name>)(...)` dispatch, `type(self)(<pure>)` — and an
    #       immediately-applied `lambda` whose body and arguments are PURE (names,
    #       constants, `+ - *`, comparisons, boolean ops, conditionals, tuples), whose
    #       erasure to an unknown value loses nothing (route #115's 1313);
    #   (2) an explicit call of an in-place DUNDER (`__setitem__ __delitem__ __i<op>__
    #       __setattr__ __delattr__`) on any receiver but `super()`;
    #   (3) an UNBOUND collection-type method that mutates (`list.reverse(xs)`,
    #       `dict.update(d, ..)`, `set.add(s, x)`, `deque.append(q, x)`, ...);
    #   (4) a mutator — collection method, in-place dunder, or `operator.<setitem|delitem|
    #       i<op>>` — referenced as a VALUE rather than called (`h = xs.append`,
    #       `map(xs.append, ys)`, `functools.partial(xs.reverse)`, `partial(
    #       operator.setitem, xs)`): the bound method escapes the call-site recognizers;
    #   (5) `getattr(o, '<mutator>')` (`o` not `self`) and `operator.methodcaller(<name>)`
    #       whose name is a mutator, a dunder above, or not a string literal.
    # The `operator.i<op>` FUNCTIONS called directly are route #162's denylist (Module 6,
    # where the argument's collection type is known), extended with this route.
    _MUT290 = frozenset((
        "append", "extend", "insert", "remove", "pop", "clear", "sort", "reverse",
        "update", "popitem", "setdefault", "add", "discard", "intersection_update",
        "difference_update", "symmetric_difference_update", "appendleft", "popleft",
        "extendleft", "rotate", "move_to_end"))
    _DUN290 = frozenset((
        "__setitem__", "__delitem__", "__iadd__", "__isub__", "__imul__", "__imatmul__",
        "__itruediv__", "__ifloordiv__", "__imod__", "__ipow__", "__ilshift__",
        "__irshift__", "__iand__", "__ixor__", "__ior__", "__setattr__", "__delattr__"))
    _OPM290 = frozenset((
        "setitem", "delitem", "iadd", "iand", "iconcat", "ifloordiv", "ilshift", "imod",
        "imul", "imatmul", "ior", "ipow", "irshift", "isub", "itruediv", "ixor"))
    _TYP290 = frozenset(("list", "dict", "set", "bytearray", "deque", "OrderedDict",
                         "defaultdict", "Counter", "frozenset"))
    _PURE290 = frozenset((
        "Name", "Constant", "BinOp", "UnaryOp", "Compare", "BoolOp", "IfExp", "Tuple",
        "Load", "Add", "Sub", "Mult", "USub", "UAdd", "Not", "And", "Or", "Eq", "NotEq",
        "Lt", "LtE", "Gt", "GtE", "arguments", "arg", "Lambda"))
    _lf290 = set()
    for _st290 in getattr(unified_ast, "body", []) or []:
        if (isinstance(_st290, _ast.FunctionDef) and len(_st290.args.args) == 1
                and len(_st290.body) == 1 and isinstance(_st290.body[0], _ast.Return)
                and isinstance(_st290.body[0].value, _ast.Subscript)
                and isinstance(_st290.body[0].value.value, _ast.Name)
                and isinstance(_st290.body[0].value.slice, _ast.Name)
                and _st290.body[0].value.slice.id == _st290.args.args[0].arg):
            _lf290.add(_st290.name)
    _callee290 = set()
    for _n290 in _ast.walk(unified_ast):
        if isinstance(_n290, _ast.Call):
            _callee290.add(id(_n290.func))
    _hit290 = None
    for _n290 in _ast.walk(unified_ast):
        if _hit290 is not None:
            break
        _ln290 = getattr(_n290, "lineno", 0)
        if isinstance(_n290, _ast.Call):
            _f290 = _n290.func
            if not isinstance(_f290, (_ast.Name, _ast.Attribute)):
                _ok290 = False
                if (isinstance(_f290, _ast.Call) and isinstance(_f290.func, _ast.Name)
                        and len(_f290.args) == 1 and not _f290.keywords
                        and ((_f290.func.id in _lf290
                              and isinstance(_f290.args[0], (_ast.Constant, _ast.Name,
                                                             _ast.Subscript)))
                             or (_f290.func.id == "type"
                                 and isinstance(_f290.args[0], _ast.Name)
                                 and _f290.args[0].id == "self"
                                 and all(type(_y).__name__ in _PURE290
                                         or type(_y).__name__ == "keyword"
                                         for _a in list(_n290.args)
                                         + [_k.value for _k in _n290.keywords]
                                         for _y in _ast.walk(_a))))):
                    _ok290 = True
                if (isinstance(_f290, _ast.Call) and isinstance(_f290.func, _ast.Name)
                        and _f290.func.id == "getattr" and len(_f290.args) == 2
                        and isinstance(_f290.args[0], _ast.Name)
                        and _f290.args[0].id == "self"
                        and isinstance(_f290.args[1], _ast.Name)):
                    _ok290 = True
                if (isinstance(_f290, _ast.Lambda) and not _n290.keywords
                        and all(type(_y).__name__ in _PURE290
                                for _a in [_f290] + list(_n290.args)
                                for _y in _ast.walk(_a))):
                    _ok290 = True
                # A same-file class constructed with NO arguments and called at once
                # (`C()()`, pyref 0090): the erased value is a fresh `(any int)`, and nothing
                # else is lost when neither `__init__` nor `__call__` stores, deletes or calls.
                if (isinstance(_f290, _ast.Call) and isinstance(_f290.func, _ast.Name)
                        and not _f290.args and not _f290.keywords
                        and all(type(_y).__name__ in _PURE290
                                for _a in list(_n290.args) + [_k.value for _k in
                                                              _n290.keywords]
                                for _y in _ast.walk(_a))):
                    for _c290 in _ast.walk(unified_ast):
                        if (isinstance(_c290, _ast.ClassDef)
                                and _c290.name == _f290.func.id):
                            _ok290 = True
                            for _m290 in _c290.body:
                                if (isinstance(_m290, _ast.FunctionDef)
                                        and _m290.name in ("__init__", "__call__")):
                                    for _y in _ast.walk(_m290):
                                        if (isinstance(_y, (_ast.Call, _ast.AugAssign,
                                                            _ast.Delete, _ast.Global,
                                                            _ast.Nonlocal))
                                                or (isinstance(_y, (_ast.Subscript,
                                                                    _ast.Attribute))
                                                    and type(getattr(_y, "ctx", None))
                                                    .__name__ in ("Store", "Del"))):
                                            _ok290 = False
                if not _ok290:
                    _hit290 = ("a call whose CALLEE is a computed expression (`lambda`, "
                               "`getattr(..)`, `operator.methodcaller(..)`, "
                               "`functools.partial(..)`, a subscript, a conditional, a "
                               "walrus, a call result): Module 5 erases the whole call to an "
                               "unknown value with NO EFFECT")
            elif isinstance(_f290, _ast.Attribute):
                if (_f290.attr in _DUN290
                        and not (isinstance(_f290.value, _ast.Call)
                                 and isinstance(_f290.value.func, _ast.Name)
                                 and _f290.value.func.id == "super")):
                    _hit290 = ("an explicit call of the in-place dunder `%s`"
                               % _f290.attr)
                elif (isinstance(_f290.value, _ast.Name) and _f290.value.id in _TYP290
                        and _f290.attr in _MUT290):
                    _hit290 = ("the UNBOUND mutating method `%s.%s(...)`"
                               % (_f290.value.id, _f290.attr))
            if (_hit290 is None and isinstance(_f290, _ast.Name)
                    and _f290.id == "getattr" and len(_n290.args) >= 2
                    and not (isinstance(_n290.args[0], _ast.Name)
                             and _n290.args[0].id == "self")
                    and isinstance(_n290.args[1], _ast.Constant)
                    and (_n290.args[1].value in _MUT290
                         or _n290.args[1].value in _DUN290)):
                _hit290 = "`getattr(.., %r)` of a mutator" % (_n290.args[1].value,)
            if (_hit290 is None
                    and ((isinstance(_f290, _ast.Attribute)
                          and _f290.attr == "methodcaller")
                         or (isinstance(_f290, _ast.Name)
                             and _f290.id == "methodcaller"))
                    and not (_n290.args and isinstance(_n290.args[0], _ast.Constant)
                             and isinstance(_n290.args[0].value, str)
                             and _n290.args[0].value not in _MUT290
                             and _n290.args[0].value not in _DUN290)):
                _hit290 = ("`operator.methodcaller(..)` naming a mutator (or a "
                           "non-literal name)")
        elif (isinstance(_n290, _ast.Attribute) and id(_n290) not in _callee290
                and type(getattr(_n290, "ctx", None)).__name__ not in ("Store", "Del")
                and (_n290.attr in _MUT290 or _n290.attr in _DUN290
                     or (isinstance(_n290.value, _ast.Name)
                         and _n290.value.id == "operator"
                         and _n290.attr in _OPM290))):
            _hit290 = ("the mutator `.%s` referenced as a VALUE (a bound or unbound "
                       "method that escapes every call-site recognizer)" % _n290.attr)
    if _hit290 is not None:
        from errors import PyCSLSemanticError as _PyCSLSemErr290
        raise _PyCSLSemErr290(
            "an in-place mutation reached through another name is out of scope: line %d "
            "has %s. PyCSL models a mutation only at a direct call of a recognized "
            "mutator on a named receiver (`xs.reverse()`, `d[k] = v`); this spelling "
            "reaches the SAME in-place effect, which the model would drop, so a frame or "
            "unchanged-contents claim would be proved of a state that changed (route #290; "
            "measured: `operator.methodcaller('reverse')(xs)`, `xs.__setitem__(0, 9)` and "
            "`getattr(xs, 'reverse')()` under `#@ assigns \\nothing` each let the caller "
            "prove the list unchanged). Call the mutator directly on the named receiver, "
            "or use an explicit element store." % (_ln290, _hit290),
            filename=args.file, line=_ln290,
            stage="ir-semantic", code="PYCSL-SEM-MUTATION-BY-ANOTHER-NAME")

    # (#49) ROUTE #310 — A `raise` WHOSE LOWERING DISCARDS PART OF THE RAISED EXPRESSION.
    # Module 5 keeps the exception CLASS name and its FIRST argument only (Module 6
    # evaluates that argument when it has an effect); a second argument, a keyword, the
    # `from` cause, and a dotted / computed exception (`raise self.err(..)`,
    # `raise errs[i](..)`) are DROPPED, and a call inside them went with them:
    # `try: raise ValueError("m", inc(xs)) except ValueError: pass` would prove
    # `xs[0] == 0` (CPython: 1). Such a discarded part that contains a call outside a few
    # pure builtins, a walrus, a yield or an await is REFUSED (source AST, inline —
    # `_run_pipeline`'s twin is `\trusted` and already raises).
    _PURE310 = frozenset(("str", "repr", "len", "int", "float", "bool", "type", "format",
                          "hex", "oct", "bin", "abs", "isinstance", "chr", "ord"))
    for _n310 in _ast.walk(unified_ast):
        if not isinstance(_n310, _ast.Raise) or _n310.exc is None:
            continue
        _e310 = _n310.exc
        _dr310 = [_n310.cause] if _n310.cause is not None else []
        if isinstance(_e310, _ast.Call) and isinstance(_e310.func, _ast.Name):
            _dr310 += list(_e310.args[1:]) + [_k310.value for _k310 in _e310.keywords]
        elif not isinstance(_e310, _ast.Name):
            _dr310.append(_e310)
        for _x310 in [_y310 for _d310 in _dr310 for _y310 in _ast.walk(_d310)]:
            if (isinstance(_x310, (_ast.NamedExpr, _ast.Await, _ast.Yield, _ast.YieldFrom))
                    or (isinstance(_x310, _ast.Call)
                        and not (isinstance(_x310.func, _ast.Name)
                                 and _x310.func.id in _PURE310))):
                from errors import PyCSLSemanticError as _PyCSLSemErr310
                raise _PyCSLSemErr310(
                    "an effectful expression is erased here (route #310): line %d raises an "
                    "exception whose second/keyword argument, `from` cause or computed "
                    "exception expression contains a call (or a walrus/yield/await), and the "
                    "model keeps only the exception class and its first argument, so that "
                    "call's effects would be dropped. FIX: evaluate it into a local before "
                    "the `raise`." % getattr(_n310, "lineno", 0),
                    filename=args.file, line=getattr(_n310, "lineno", 0),
                    stage="ir-semantic", code="PYCSL-SEM-ERASED-EFFECT-R310")

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
        # ROUTE #277 — tell the report the override-refinement check is off.
        if not getattr(args, "check_behavioral_subtyping", False):
            ir_data["class_exact_assumed"] = True
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

    # (#49) gen #37, ROUTE #341 — A CLASS BASE THAT IS NOT A CLASS NAME DROPPED THE
    # INHERITANCE EDGE. Module 5 records a base only when it is spelled `Name` or `a.b.Name`;
    # every other spelling was silently dropped, and so was an alias's target: `Base = B;
    # class S(Base)` made `S` an UNRELATED record (the name `Base` resolves to no class),
    # so R5 (route #338), the #277/#278 refinement, route #335 and the inherited invariant
    # all skipped it. MEASURED (all PROVED, CPython violates): alias (o09 R5, o10 override
    # contract, o11 invariant), `class S(base())` (o13), `S(me.B if False else B)` (o14),
    # `Base, Other = B, int` (o15), `Base: Type[B] = B` (o16). About twenty independent
    # readers of `ClassDef.bases` (Module 3/5/6, this pipeline) each take `b.id` / `b.attr`,
    # so resolving an alias at ONE of them would leave the others reading the alias name
    # (an unknown, i.e. imported-looking, base: R5 and #278 then skip the pair) — and the
    # census over both corpora, the 53 mirrors and `pycsl_lib` finds ZERO alias, call,
    # conditional or non-`Generic` subscripted bases. So the repair is a sound REFUSAL, not
    # a resolution. RULE, for every base expression of every class of the file:
    #   * a bare name is admitted unless the file ALSO binds that name by anything other
    #     than a `class` statement or an import (assignment / annotated / tuple / `for` /
    #     `with` / walrus target, `del`, a `def`, a parameter, an `except .. as`);
    #   * an attribute chain is admitted when rooted at an imported name never rebound;
    #   * a subscript is admitted only on `Generic` / `Protocol` (no inheritance content);
    #   * anything else (a call, a conditional, an operator, a starred base) is REFUSED.
    # (#49) gen #37, ROUTE #342 — THE CONSTRUCTOR-INVARIANT GOAL READS ONLY STRAIGHT-LINE
    # `self.f = e` STORES. Route #226's goal `_check_class_inv_<C>` is built from Module 5's
    # top-level stores; a field stored under control flow / by `+=` is marked unknown and
    # then NO goal is emitted (annotations.md documented that as "not covered"), and a
    # store by another FORM is not seen at all. Either way the invariant was ASSUMED.
    # MEASURED (all PROVED, CPython violates): `for self.x in ..` (i21, i17 after a leading
    # `super().__init__()`, defeating #335), `(self.x, y) = ..` (i22, i18), `del self.x`
    # (i23, i10), `with .. as self.x` (i24), `setattr(self, "x", 5)` (i20, i12, i26 in a
    # comprehension), `self.x += 5` (i25), `s = self; s.x = 5` (i35), a `while` (i38) or
    # `if` (i39) store; and `d.__class__ = C` retypes an object (x03). RULE: for every class
    # carrying a class invariant (its own or inherited; the resolved IR's merged
    # `class_invariants`) and every file class on its base closure (their constructors
    # run for its instances), the `__init__` / `__post_init__` body may touch an invariant
    # field (every field when the invariant reads `self` otherwise than as `self.f`) only by
    # a TOP-LEVEL `self.f = e` / `self.f: T = e` statement; it may not load `self` other
    # than as an attribute root (an alias, an argument — `setattr(self, ..)`, `vars(self)`
    # — a return; `type` / `isinstance` / `id` of it are reads), rebind `self`, touch
    # `self.__dict__` / `__setattr__` / `__delattr__`, call a method `self.m(..)` (route
    # #150 then makes every field unknown and NO goal is emitted — measured: `self.x = 5;
    # self.helper()` PROVED `x == 0`), use `super()` other than as the leading
    # `super().__init__(..)` (measured: `super().__setattr__("x", 5)` PROVED), or `return`
    # (later top-level stores become conditional). And no code of the file may store `__class__`
    # (`x.__class__ = C`, `setattr(x, "__class__", C)`). Each a REFUSAL; monotone; INLINE
    # (no nested def: check-mirror-coverage); `_run_pipeline`'s mirror twin is `\trusted`.
    import ast as _ast341
    try:
        _t341 = _ast341.parse(source_code)
    except (SyntaxError, ValueError):
        _t341 = None
    if _t341 is not None:
        from errors import PyCSLSemanticError as _PyCSLSemErr341
        _cls341 = {}
        _imp341 = set()
        _bound341 = set()
        for _n341 in _ast341.walk(_t341):
            if isinstance(_n341, _ast341.ClassDef):
                _cls341.setdefault(_n341.name, []).append(_n341)
            elif isinstance(_n341, (_ast341.Import, _ast341.ImportFrom)):
                for _a341 in _n341.names:
                    _imp341.add((_a341.asname or _a341.name).split(".")[0])
            elif isinstance(_n341, _ast341.Name) and not isinstance(_n341.ctx, _ast341.Load):
                _bound341.add(_n341.id)
            elif isinstance(_n341, (_ast341.FunctionDef, _ast341.AsyncFunctionDef)):
                _bound341.add(_n341.name)
            elif isinstance(_n341, _ast341.arg):
                _bound341.add(_n341.arg)
            elif (isinstance(_n341, (_ast341.ExceptHandler, _ast341.MatchAs, _ast341.MatchStar))
                  and isinstance(_n341.name, str)):
                _bound341.add(_n341.name)
        for _ks341 in _cls341.values():
            for _k341 in _ks341:
                for _b341 in _k341.bases:
                    _why341 = ""
                    if isinstance(_b341, _ast341.Name):
                        if _b341.id in _bound341:
                            _why341 = (f"names `{_b341.id}`, which this file also binds "
                                       f"otherwise than by a `class` statement or an import "
                                       f"(an alias such as `{_b341.id} = ...`, a tuple / "
                                       f"annotated / loop target, a `def`, a parameter)")
                    elif isinstance(_b341, _ast341.Attribute):
                        _r341 = _b341
                        while isinstance(_r341, _ast341.Attribute):
                            _r341 = _r341.value
                        if not (isinstance(_r341, _ast341.Name) and _r341.id in _imp341
                                and _r341.id not in _bound341):
                            _why341 = ("is an attribute that is not a dotted name rooted at "
                                       "an imported module")
                        # (#49) ROUTE #345 — THE READERS TAKE AN ATTRIBUTE BASE BY ITS TAIL
                        # (`b.attr`), so `om.B` named THIS file's class `B` whenever the file
                        # defines one: `import rt25other as om; class S(om.B)` inherited the
                        # local B's contract and invariant (CPython runs rt25other.B.m).
                        # The tail is that class only for a SELF-import: `import <stem>` /
                        # `import <stem> as x` of this file's own module name, used as
                        # `x.B`. Any other module's attribute colliding with a class name
                        # of the file is REFUSED (the readers cannot see it as imported).
                        elif _b341.attr in _cls341:
                            _st345 = (os.path.splitext(os.path.basename(str(args.file)))[0]
                                      if getattr(args, "file", None) else "")
                            _self345 = (isinstance(_b341.value, _ast341.Name) and bool(_st345)
                                        and any(isinstance(_n345, _ast341.Import) and any(
                                            _a345.name == _st345
                                            and (_a345.asname or _a345.name) == _b341.value.id
                                            for _a345 in _n345.names)
                                            for _n345 in _ast341.walk(_t341))
                                        and not any(
                                            isinstance(_n345, _ast341.ImportFrom) and any(
                                                (_a345.asname or _a345.name) == _b341.value.id
                                                for _a345 in _n345.names)
                                            or (isinstance(_n345, _ast341.Import) and any(
                                                (_a345.asname or _a345.name.split(".")[0])
                                                == _b341.value.id and _a345.name != _st345
                                                for _a345 in _n345.names))
                                            for _n345 in _ast341.walk(_t341)))
                            if not _self345:
                                _why341 = (f"is an attribute of another module whose tail "
                                           f"`{_b341.attr}` is also the name of a class of "
                                           f"this file (route #345: the base would be read "
                                           f"as this file's `{_b341.attr}`); import the "
                                           f"class under a distinct name "
                                           f"(`from m import {_b341.attr} as Other{_b341.attr}`)")
                    elif isinstance(_b341, _ast341.Subscript):
                        _h341 = _b341.value
                        if not ((isinstance(_h341, _ast341.Name)
                                 and _h341.id in ("Generic", "Protocol"))
                                or (isinstance(_h341, _ast341.Attribute)
                                    and _h341.attr in ("Generic", "Protocol"))):
                            _why341 = ("is a subscripted class other than `Generic[...]` / "
                                       "`Protocol[...]`")
                    else:
                        _why341 = ("is a computed expression (a call, a conditional, an "
                                   "operator, a starred list)")
                    if _why341:
                        raise _PyCSLSemErr341(
                            f"class '{_k341.name}' at line {_k341.lineno}: its base "
                            f"`{_ast341.unparse(_b341)}` {_why341}. The verifier reads a "
                            f"class's bases by NAME, so this base would not be resolved to "
                            f"the class it denotes and '{_k341.name}' would be modelled as "
                            f"unrelated to it: its inherited fields and invariants, the "
                            f"override checks (routes #277/#278/#338) and the constructor "
                            f"chain (route #335) would all be skipped, while CPython "
                            f"inherits (route #341). Write the base class's own name (the "
                            f"`class` statement's name, or `module.Name` for an imported "
                            f"class) in the class header.",
                            stage="ir-semantic", code="PYCSL-R341-CLASS-BASE-NOT-A-NAME")
        for _n341 in _ast341.walk(_t341):
            _cl341 = ""
            if (isinstance(_n341, _ast341.Attribute) and _n341.attr == "__class__"
                    and not isinstance(_n341.ctx, _ast341.Load)):
                _cl341 = _ast341.unparse(_n341)
            elif (isinstance(_n341, _ast341.Call) and len(_n341.args) >= 2
                  and isinstance(_n341.args[1], _ast341.Constant)
                  and _n341.args[1].value == "__class__"
                  and ((isinstance(_n341.func, _ast341.Name)
                        and _n341.func.id in ("setattr", "delattr"))
                       or (isinstance(_n341.func, _ast341.Attribute)
                           and _n341.func.attr in ("__setattr__", "__delattr__")))):
                _cl341 = _ast341.unparse(_n341)
            if _cl341:
                raise _PyCSLSemErr341(
                    f"line {getattr(_n341, 'lineno', 0)}: `{_cl341}` stores an object's "
                    f"`__class__`, which changes the class of an EXISTING instance: its "
                    f"fields were established by another class's constructor, so the "
                    f"model's per-class field types, invariants and methods would be "
                    f"assumed of an object that never met them (route #342). Construct an "
                    f"instance of the target class instead.",
                    stage="ir-semantic", code="PYCSL-R342-CLASS-REASSIGNMENT")
        _ir342 = _json.loads(json_ir)
        _rel342 = {}
        _invf342 = set()
        for _td342 in (_ir342.get("type_decls") or []):
            if not (isinstance(_td342, dict) and _td342.get("class_invariants")
                    and _td342.get("name") in _cls341):
                continue
            _fs342 = set()
            _stk342 = list(_td342.get("class_invariants") or [])
            while _stk342:
                _nd342 = _stk342.pop()
                if isinstance(_nd342, dict):
                    if (_nd342.get("type") == "FieldGet" and _nd342.get("object") == "self"
                            and isinstance(_nd342.get("field"), str)):
                        _fs342.add(_nd342["field"])
                    elif any(_v342 == "self" for _v342 in _nd342.values()):
                        _fs342.add("*")
                    _stk342.extend(_nd342.values())
                elif isinstance(_nd342, list):
                    _stk342.extend(_nd342)
            _invf342 |= {_f342 for _f342 in _fs342 if _f342 != "*"}
            if "*" in _fs342:
                _invf342 |= {_fd342.get("name") for _fd342 in (_td342.get("fields") or [])
                             if isinstance(_fd342, dict) and isinstance(_fd342.get("name"), str)}
            _cs342 = [_td342["name"]]
            _seen342 = set()
            while _cs342:
                _c342 = _cs342.pop()
                if _c342 in _seen342 or _c342 not in _cls341:
                    continue
                _seen342.add(_c342)
                _rel342.setdefault(_c342, set()).update(_fs342)
                for _k342 in _cls341[_c342]:
                    for _b342 in _k342.bases:
                        if isinstance(_b342, _ast341.Name):
                            _cs342.append(_b342.id)
                        elif isinstance(_b342, _ast341.Attribute):
                            _cs342.append(_b342.attr)
        # The same obligation from OUTSIDE: module-level / `__main__` code is not verified,
        # so a store there into an invariant field (`b.x = 5`, `b.x += 1`, `del b.x`,
        # `setattr(b, "x", 5)`; receiver class unknown -> any invariant field of the file)
        # is never checked against the invariant every verified receiver assumes. MEASURED:
        # `b = B(); b.x = 5; f(b)` in `__main__` PROVED `f(b) == 0` (CPython 5). CENSUS: no
        # such store in either corpus, the mirrors or `pycsl_lib`.
        _stk342 = list(_t341.body) if _invf342 else []
        while _stk342:
            _x342 = _stk342.pop()
            if isinstance(_x342, (_ast341.FunctionDef, _ast341.AsyncFunctionDef,
                                  _ast341.ClassDef, _ast341.Lambda)):
                continue
            _st342 = ""
            if (isinstance(_x342, _ast341.Attribute) and _x342.attr in _invf342
                    and not isinstance(_x342.ctx, _ast341.Load)):
                _st342 = _ast341.unparse(_x342)
            elif (isinstance(_x342, _ast341.Call) and len(_x342.args) >= 2
                  and ((isinstance(_x342.func, _ast341.Name)
                        and _x342.func.id in ("setattr", "delattr"))
                       or (isinstance(_x342.func, _ast341.Attribute)
                           and _x342.func.attr in ("__setattr__", "__delattr__")))
                  and not (isinstance(_x342.args[1], _ast341.Constant)
                           and _x342.args[1].value not in _invf342)):
                _st342 = _ast341.unparse(_x342)
            if _st342:
                raise _PyCSLSemErr341(
                    f"line {getattr(_x342, 'lineno', 0)}: module-level code `{_st342}` "
                    f"stores or deletes a field constrained by a `#@ class invariant` "
                    f"({sorted(_invf342)}). Module-level and `__main__` code is not "
                    f"verified, so the invariant every verified receiver assumes would "
                    f"not be checked against this store (route #342). Move the update into "
                    f"a verified method or function of the class.",
                    stage="ir-semantic", code="PYCSL-R342-EXTERNAL-INVARIANT-STORE")
            _stk342.extend(_ast341.iter_child_nodes(_x342))
        for _c342 in sorted(_rel342):
            _fs342 = _rel342[_c342]
            for _k342 in _cls341[_c342]:
                for _m342 in _k342.body:
                    if not (isinstance(_m342, (_ast341.FunctionDef, _ast341.AsyncFunctionDef))
                            and _m342.name in ("__init__", "__post_init__")):
                        continue
                    _pa342 = _m342.args.posonlyargs + _m342.args.args
                    if not _pa342:
                        continue
                    _self342 = _pa342[0].arg
                    _top342 = set()
                    for _s342 in _m342.body:
                        if isinstance(_s342, _ast341.Assign):
                            _top342 |= {id(_t) for _t in _s342.targets
                                        if isinstance(_t, _ast341.Attribute)}
                        elif (isinstance(_s342, _ast341.AnnAssign)
                              and isinstance(_s342.target, _ast341.Attribute)):
                            _top342.add(id(_s342.target))
                    _lead342 = [_st for _st in _m342.body
                                if not (isinstance(_st, _ast341.Expr)
                                        and isinstance(_st.value, _ast341.Constant)
                                        and isinstance(_st.value.value, str))]
                    _roots342 = set()
                    _nest342 = set()
                    _nret342 = set()
                    for _x342 in _ast341.walk(_m342):
                        if isinstance(_x342, _ast341.Attribute):
                            _roots342.add(id(_x342.value))
                        # `type(self)` / `isinstance(self, K)` / `id(self)` read, never
                        # store (the builtin, not a rebinding of its name)
                        if (isinstance(_x342, _ast341.Call)
                                and isinstance(_x342.func, _ast341.Name)
                                and _x342.func.id in ("type", "isinstance", "id")
                                and _x342.func.id not in _bound341 | _imp341
                                and _x342.args and isinstance(_x342.args[0], _ast341.Name)):
                            _roots342.add(id(_x342.args[0]))
                        if _x342 is not _m342 and isinstance(
                                _x342, (_ast341.FunctionDef, _ast341.AsyncFunctionDef,
                                        _ast341.Lambda, _ast341.ClassDef)):
                            _nret342 |= {id(_y) for _y in _ast341.walk(_x342)}
                            if isinstance(_x342, _ast341.ClassDef) or any(
                                    _p.arg == _self342 for _p in (
                                        _x342.args.posonlyargs + _x342.args.args
                                        + _x342.args.kwonlyargs)):
                                _nest342 |= {id(_y) for _y in _ast341.walk(_x342)}
                    for _x342 in _ast341.walk(_m342):
                        if id(_x342) in _nest342:
                            continue
                        _bad342 = ""
                        if (isinstance(_x342, _ast341.Attribute)
                                and isinstance(_x342.value, _ast341.Name)
                                and _x342.value.id == _self342):
                            if _x342.attr in ("__dict__", "__setattr__", "__delattr__"):
                                _bad342 = f"touches `{_self342}.{_x342.attr}`"
                            elif (not isinstance(_x342.ctx, _ast341.Load)
                                  and (_x342.attr in _fs342 or "*" in _fs342)
                                  and id(_x342) not in _top342):
                                _bad342 = (f"stores or deletes the invariant field "
                                           f"`{_self342}.{_x342.attr}` by a form other "
                                           f"than a top-level `{_self342}.{_x342.attr} = "
                                           f"...` statement (a `for` / `with` / tuple / "
                                           f"augmented / `del` target, or a store inside "
                                           f"control flow or a comprehension)")
                        elif isinstance(_x342, _ast341.Name) and _x342.id == _self342:
                            if not isinstance(_x342.ctx, _ast341.Load):
                                _bad342 = f"rebinds `{_self342}`"
                            elif id(_x342) not in _roots342:
                                _bad342 = (f"lets `{_self342}` escape or be aliased (a "
                                           f"bare `{_self342}` as an argument — "
                                           f"`setattr`, `vars`, a helper — an alias "
                                           f"`s = {_self342}`, or a value)")
                        elif (isinstance(_x342, _ast341.Call)
                              and isinstance(_x342.func, _ast341.Attribute)
                              and isinstance(_x342.func.value, _ast341.Name)
                              and _x342.func.value.id == _self342):
                            _bad342 = (f"calls `{_self342}.{_x342.func.attr}(...)`, whose "
                                       f"effect on the fields is not part of the "
                                       f"constructor's obligation")
                        elif (isinstance(_x342, _ast341.Call)
                              and isinstance(_x342.func, _ast341.Attribute)
                              and isinstance(_x342.func.value, _ast341.Call)
                              and isinstance(_x342.func.value.func, _ast341.Name)
                              and _x342.func.value.func.id == "super"
                              and not (_x342.func.attr == "__init__" and _lead342
                                       and isinstance(_lead342[0], _ast341.Expr)
                                       and _lead342[0].value is _x342)):
                            _bad342 = ("uses `super()` other than as its leading "
                                       "`super().__init__(...)` statement")
                        elif isinstance(_x342, _ast341.Return) and id(_x342) not in _nret342:
                            _bad342 = ("contains a `return`, which makes every later "
                                       "top-level store conditional")
                        if _bad342:
                            raise _PyCSLSemErr341(
                                f"class '{_c342}' line {getattr(_x342, 'lineno', 0)}: "
                                f"its `{_m342.name}` {_bad342}. '{_c342}' carries (or its "
                                f"constructor runs for) a `#@ class invariant` over "
                                f"{sorted(_fs342)}, and the constructor's obligation (route "
                                f"#226) is computed from top-level `self.f = e` stores "
                                f"only, so the invariant would be ASSUMED for every "
                                f"instance although the constructor's real effect is "
                                f"not checked against it (route #342). Store each "
                                f"invariant field by a top-level `self.f = e` statement "
                                f"whose value is a literal or an `__init__` parameter "
                                f"(the shapes the constructor goal states), and keep "
                                f"`self` out of calls and aliases in the constructor.",
                                stage="ir-semantic", code="PYCSL-R342-CONSTRUCTOR-STORE-FORM")
        # (#49) gen #37, ROUTES #346 / #347 / #348 / #349 — FOUR CLASS SHAPES WHOSE RUNTIME
        # BEHAVIOUR THE RECORD MODEL DOES NOT HAVE (red team 25; each MEASURED PROVED at
        # b83a217b, CPython violates). Sound REFUSALS on the source, no emission change;
        # INLINE (no nested def: check-mirror-coverage); `_run_pipeline`'s mirror twin is
        # `\trusted`. Shared facts: each class's in-file base names (`_bn346`), a left-to-right
        # depth-first base closure starting at the class itself (`_clo346`, an approximation
        # of the MRO that keeps every ancestor), and each `@dataclass`'s options (`_dc346`;
        # a non-literal option is None = unknown, read in the refusing direction).
        _bn346 = {}
        for _cn346, _ks346 in _cls341.items():
            for _k346 in _ks346:
                for _b346 in _k346.bases:
                    if isinstance(_b346, _ast341.Name):
                        _bn346.setdefault(_cn346, []).append(_b346.id)
                    elif isinstance(_b346, _ast341.Attribute):
                        _bn346.setdefault(_cn346, []).append(_b346.attr)
        _clo346 = {}
        for _cn346 in _cls341:
            _sn346 = []
            _st346 = [_cn346]
            while _st346:
                _c346 = _st346.pop(0)
                if _c346 in _sn346:
                    continue
                _sn346.append(_c346)
                _st346 = list(_bn346.get(_c346, [])) + _st346
            _clo346[_cn346] = _sn346
        _dc346 = {}
        for _cn346, _ks346 in _cls341.items():
            for _k346 in _ks346:
                for _dec346 in _k346.decorator_list:
                    _df346 = _dec346.func if isinstance(_dec346, _ast341.Call) else _dec346
                    if ((isinstance(_df346, _ast341.Name) and _df346.id == "dataclass")
                            or (isinstance(_df346, _ast341.Attribute)
                                and _df346.attr == "dataclass")):
                        _o346 = {"frozen": False, "eq": True, "unsafe_hash": False,
                                 "init": True}
                        for _kw346 in (_dec346.keywords
                                       if isinstance(_dec346, _ast341.Call) else []):
                            if _kw346.arg in _o346:
                                _o346[_kw346.arg] = (
                                    bool(_kw346.value.value)
                                    if isinstance(_kw346.value, _ast341.Constant) else None)
                        _dc346[_cn346] = _o346
        # ROUTE #346 — A `__post_init__` IS NEVER VERIFIED. Route #150 makes a dataclass
        # construction that runs `__post_init__` OPAQUE (no field value known), and an opaque
        # construction gets NO constructor-invariant goal (route #226), so the invariant is
        # ASSUMED of every instance: `__post_init__: self.x = -1` under `invariant x >= 0`
        # PROVED `f(d) >= 0` (k08; CPython -1), and even a no-op `__post_init__` drops the
        # goal for `__main__`'s `D(-5)`; an inherited hook (`B(A)` over `A.__post_init__`)
        # does the same. RULE: a record carrying a class invariant (own or merged) whose base
        # closure holds a `@dataclass` and a class defining `__post_init__` is REFUSED.
        # CENSUS: no invariant-carrying class with a `__post_init__` in either corpus, the
        # mirrors or `pycsl_lib` (7 root files use `__post_init__`, none with an invariant).
        for _td346 in (_ir342.get("type_decls") or []):
            if not (isinstance(_td346, dict) and _td346.get("class_invariants")
                    and _td346.get("name") in _cls341):
                continue
            _cl346 = _clo346.get(_td346["name"], [])
            if not any(_c in _dc346 for _c in _cl346):
                continue
            for _c346 in _cl346:
                for _k346 in _cls341.get(_c346, []):
                    for _m346 in _k346.body:
                        if (isinstance(_m346, (_ast341.FunctionDef, _ast341.AsyncFunctionDef))
                                and _m346.name == "__post_init__"):
                            raise _PyCSLSemErr341(
                                f"class '{_td346['name']}': its construction runs "
                                f"`{_c346}.__post_init__` (line {_m346.lineno}), and it "
                                f"carries a `#@ class invariant`. A `@dataclass`'s "
                                f"`__post_init__` is never emitted or verified: the "
                                f"construction becomes opaque (route #150) and NO "
                                f"constructor-invariant goal is generated, so the "
                                f"invariant would be ASSUMED of every instance although "
                                f"`__post_init__` (or the arguments of an unverified "
                                f"construction) may break it (route #346). Drop the "
                                f"`__post_init__` (validate in a verified factory "
                                f"function), or write an explicit `__init__` whose "
                                f"top-level stores the constructor goal checks.",
                                stage="ir-semantic", code="PYCSL-R346-POST-INIT-INVARIANT")
        # Per-function typing facts for #348 / #349, read from annotations and constructor
        # calls only: `_fn346` lists (def, enclosing class or None); `_at346[id(ann)]` the
        # TOP-LEVEL class names an annotation denotes (through Optional / Union / `|` /
        # string forms), `_ah346[id(ann)]` its head name (`Set`, `list`, `D` ...), and
        # `_ae346[id(ann)]` the top-level names of its FIRST type argument (element / key).
        _fn346 = []
        _seenf346 = set()
        for _cn346, _ks346 in _cls341.items():
            for _k346 in _ks346:
                for _m346 in _k346.body:
                    if isinstance(_m346, (_ast341.FunctionDef, _ast341.AsyncFunctionDef)):
                        _fn346.append((_m346, _cn346))
                        _seenf346.add(id(_m346))
        for _n346 in _ast341.walk(_t341):
            if (isinstance(_n346, (_ast341.FunctionDef, _ast341.AsyncFunctionDef))
                    and id(_n346) not in _seenf346):
                _fn346.append((_n346, None))
        _an346 = []
        for _n346 in _ast341.walk(_t341):
            if isinstance(_n346, _ast341.arg) and _n346.annotation is not None:
                _an346.append(_n346.annotation)
            elif isinstance(_n346, _ast341.AnnAssign):
                _an346.append(_n346.annotation)
            elif (isinstance(_n346, (_ast341.FunctionDef, _ast341.AsyncFunctionDef))
                  and _n346.returns is not None):
                _an346.append(_n346.returns)
        _at346 = {}
        _ah346 = {}
        _ae346 = {}
        _ix346 = 0
        while _ix346 < len(_an346):
            _a346 = _an346[_ix346]
            _ix346 += 1
            if id(_a346) in _at346:
                continue
            _r346 = _a346
            if isinstance(_r346, _ast341.Constant) and isinstance(_r346.value, str):
                try:
                    _r346 = _ast341.parse(_r346.value, mode="eval").body
                except (SyntaxError, ValueError):
                    _r346 = None
            _hd346 = ""
            if isinstance(_r346, _ast341.Subscript):
                _hv346 = _r346.value
                _hd346 = (_hv346.id if isinstance(_hv346, _ast341.Name) else
                          _hv346.attr if isinstance(_hv346, _ast341.Attribute) else "")
                _sl346 = _r346.slice
                _fa346 = (_sl346.elts[0] if isinstance(_sl346, _ast341.Tuple) and _sl346.elts
                          else _sl346)
                _an346.append(_fa346)
                _ae346[id(_a346)] = id(_fa346)
            elif isinstance(_r346, _ast341.Name):
                _hd346 = _r346.id
            elif isinstance(_r346, _ast341.Attribute):
                _hd346 = _r346.attr
            _ah346[id(_a346)] = _hd346
            _tp346 = set()
            _q346 = [_r346] if _r346 is not None else []
            while _q346:
                _x346 = _q346.pop()
                if isinstance(_x346, _ast341.Constant) and isinstance(_x346.value, str):
                    try:
                        _q346.append(_ast341.parse(_x346.value, mode="eval").body)
                    except (SyntaxError, ValueError):
                        pass
                elif isinstance(_x346, _ast341.Name):
                    _tp346.add(_x346.id)
                elif isinstance(_x346, _ast341.Attribute):
                    _tp346.add(_x346.attr)
                elif isinstance(_x346, _ast341.BinOp) and isinstance(_x346.op, _ast341.BitOr):
                    _q346.extend([_x346.left, _x346.right])
                elif isinstance(_x346, _ast341.Subscript):
                    _hv346 = _x346.value
                    _hn346 = (_hv346.id if isinstance(_hv346, _ast341.Name) else
                              _hv346.attr if isinstance(_hv346, _ast341.Attribute) else "")
                    if _hn346 in ("Optional", "Union", "Annotated", "Final", "ClassVar"):
                        _sl346 = _x346.slice
                        _el346 = (list(_sl346.elts) if isinstance(_sl346, _ast341.Tuple)
                                  else [_sl346])
                        _q346.extend(_el346[:1] if _hn346 in ("Annotated", "Final",
                                                              "ClassVar") else _el346)
                    else:
                        _tp346.add(_hn346)
            _at346[id(_a346)] = _tp346
        for _k346, _v346 in list(_ae346.items()):
            _ae346[_k346] = _at346.get(_v346, set())
        # Each class's annotated body fields (`x: T` in the class body): name -> annotation.
        _cf346 = {}
        for _cn346, _ks346 in _cls341.items():
            for _k346 in _ks346:
                for _s346 in _k346.body:
                    if (isinstance(_s346, _ast341.AnnAssign)
                            and isinstance(_s346.target, _ast341.Name)):
                        _cf346.setdefault(_cn346, {})[_s346.target.id] = _s346.annotation
        # ROUTE #348 — NamedTuple / `collections.namedtuple` / FROZEN `@dataclass` ARE LOWERED
        # AS MUTABLE RECORDS (`{ mutable x: int }`), so `n.x = 5` PROVED `\result == 5` under
        # `no_exception \all` (d11, j02, j03, j07; CPython AttributeError /
        # FrozenInstanceError — ANY attribute store or delete on such an instance raises).
        # RULE: in every function / method body, an attribute STORE / augmented store /
        # `del` / `for` / `with` target, or a `setattr` / `delattr` call, whose receiver is
        #   * a name annotated with (or constructed as) an immutable record, or `self` in a
        #     method of one (subclasses of an immutable record included), or
        #   * of UNKNOWN class (not provably a mutable class) and names a field of an
        #     immutable record of the file (any name, when a functional field list is not
        #     literal),
        # is REFUSED. CENSUS: no such store in either corpus, the mirrors or `pycsl_lib`.
        _imm348 = {}
        for _cn346, _ks346 in _cls341.items():
            for _k346 in _ks346:
                _nt348 = any((isinstance(_b, _ast341.Name) and _b.id == "NamedTuple")
                             or (isinstance(_b, _ast341.Attribute) and _b.attr == "NamedTuple")
                             for _b in _k346.bases)
                if _nt348 or (_cn346 in _dc346 and _dc346[_cn346]["frozen"] is not False):
                    _imm348.setdefault(_cn346, set()).update(_cf346.get(_cn346, {}).keys())
        for _n346 in _ast341.walk(_t341):
            if not (isinstance(_n346, _ast341.Assign) and len(_n346.targets) == 1
                    and isinstance(_n346.targets[0], _ast341.Name)
                    and isinstance(_n346.value, _ast341.Call)):
                continue
            _cf348 = _n346.value.func
            if not ((isinstance(_cf348, _ast341.Name) and _cf348.id in ("namedtuple",
                                                                        "NamedTuple"))
                    or (isinstance(_cf348, _ast341.Attribute)
                        and _cf348.attr in ("namedtuple", "NamedTuple"))):
                continue
            _fl348 = set()
            _fa348 = (_n346.value.args[1] if len(_n346.value.args) >= 2 else
                      next((_kw.value for _kw in _n346.value.keywords
                            if _kw.arg in ("field_names", "fields")), None))
            if _fa348 is None:
                _fl348 |= {_kw.arg for _kw in _n346.value.keywords if _kw.arg not in (
                    None, "rename", "defaults", "module", "typename")}
            elif isinstance(_fa348, _ast341.Constant) and isinstance(_fa348.value, str):
                _fl348 |= set(_fa348.value.replace(",", " ").split())
            elif isinstance(_fa348, (_ast341.List, _ast341.Tuple)):
                for _e348 in _fa348.elts:
                    if isinstance(_e348, _ast341.Constant) and isinstance(_e348.value, str):
                        _fl348.add(_e348.value)
                    elif (isinstance(_e348, (_ast341.Tuple, _ast341.List)) and _e348.elts
                          and isinstance(_e348.elts[0], _ast341.Constant)
                          and isinstance(_e348.elts[0].value, str)):
                        _fl348.add(_e348.elts[0].value)
                    else:
                        _fl348.add("*")
            else:
                _fl348.add("*")
            _imm348.setdefault(_n346.targets[0].id, set()).update(_fl348)
        _im0348 = dict(_imm348)
        for _cn346 in _cls341:
            for _a346 in _clo346[_cn346][1:]:
                if _a346 in _im0348:
                    _imm348.setdefault(_cn346, set()).update(_im0348[_a346])
        _immf348 = set()
        for _v346 in _imm348.values():
            _immf348 |= _v346
        # ROUTE #349 — AN UNHASHABLE RECORD AS A SET ELEMENT / DICT KEY. `{d}` lowers to an
        # opaque value, so `s = {d}` PROVED `no_exception \all` (e08 explicit `__hash__ =
        # None`, e09 `@dataclass`; CPython TypeError). Python's rule, per class in base
        # order: an own `__hash__ = None` -> unhashable; an own `__hash__` -> hashable; a
        # `@dataclass` with `unsafe_hash` -> hashable, else with `eq` (default) -> hashable
        # iff `frozen`; an own `__eq__` without `__hash__` -> unhashable; else inherited
        # (`list` / `dict` / `set` / `bytearray` bases unhashable). A hashable NamedTuple /
        # frozen record with a `list` / `dict` / `set` / unhashable-record field still
        # raises on `hash`, so it counts as unhashable.
        _uh349 = {}
        for _cn346 in [_c for _l, _c in sorted((len(_clo346[_c]), _c) for _c in _cls341)]:
            _dec349 = None
            for _a346 in _clo346[_cn346]:
                if _a346 in ("list", "dict", "set", "bytearray"):
                    _dec349 = True
                    break
                if _a346 not in _cls341:
                    continue
                if _a346 != _cn346 and _a346 in _uh349:
                    _dec349 = _uh349[_a346]
                    break
                _own349 = None
                _eq349 = False
                for _k346 in _cls341[_a346]:
                    for _s346 in _k346.body:
                        if (isinstance(_s346, (_ast341.FunctionDef, _ast341.AsyncFunctionDef))
                                and _s346.name == "__hash__"):
                            _own349 = False
                        elif isinstance(_s346, (_ast341.Assign, _ast341.AnnAssign)):
                            _tg349 = (_s346.targets if isinstance(_s346, _ast341.Assign)
                                      else [_s346.target])
                            if any(isinstance(_t, _ast341.Name) and _t.id == "__hash__"
                                   for _t in _tg349):
                                _own349 = (isinstance(_s346.value, _ast341.Constant)
                                           and _s346.value.value is None)
                        if (isinstance(_s346, (_ast341.FunctionDef, _ast341.AsyncFunctionDef))
                                and _s346.name == "__eq__"):
                            _eq349 = True
                if _own349 is None and _a346 in _dc346:
                    _o346 = _dc346[_a346]
                    if _o346["unsafe_hash"] is True:
                        _own349 = False
                    elif _o346["unsafe_hash"] is None:
                        _own349 = True
                    elif _o346["eq"] is not False:
                        _own349 = _o346["frozen"] is not True
                if _own349 is None and _eq349:
                    _own349 = True
                if _own349 is not None:
                    _dec349 = _own349
                    break
            if not _dec349 and _cn346 in _imm348:
                for _a346 in _clo346[_cn346]:
                    for _fan349 in _cf346.get(_a346, {}).values():
                        if ((_ah346.get(id(_fan349)) or "").lower() in (
                                "list", "dict", "set", "bytearray", "defaultdict",
                                "ordereddict", "counter", "deque")
                                or (_at346.get(id(_fan349), set()) & {
                                    _c for _c, _u in _uh349.items() if _u})):
                            _dec349 = True
            _uh349[_cn346] = bool(_dec349)
        _u349 = {_c for _c, _u in _uh349.items() if _u}
        _keyed349 = ("Set", "set", "FrozenSet", "frozenset", "AbstractSet", "MutableSet",
                     "Dict", "dict", "Mapping", "MutableMapping", "DefaultDict",
                     "defaultdict", "OrderedDict", "Counter", "ChainMap")
        if _u349:
            for _a346 in _an346:
                if (_ah346.get(id(_a346)) in _keyed349
                        and _ae346.get(id(_a346), set()) & _u349):
                    raise _PyCSLSemErr341(
                        f"line {getattr(_a346, 'lineno', 0)}: the annotation "
                        f"`{_ast341.unparse(_a346)}` puts an UNHASHABLE class "
                        f"({sorted(_ae346[id(_a346)] & _u349)}) in a set element / dict "
                        f"key position. Its instances have `__hash__ = None` (an explicit "
                        f"`__hash__ = None`, a `@dataclass` with `eq` and without `frozen` "
                        f"/ `unsafe_hash`, or an `__eq__` without `__hash__`), so CPython "
                        f"raises TypeError on any such set or dict, while the model lowers "
                        f"it as an opaque value (route #349). Make the class hashable "
                        f"(`@dataclass(frozen=True)`, or define `__hash__`) or key the "
                        f"collection by a field.",
                        stage="ir-semantic", code="PYCSL-R349-UNHASHABLE-RECORD")
        for _f346, _ec346 in _fn346:
            _pa346 = (_f346.args.posonlyargs + _f346.args.args + _f346.args.kwonlyargs
                      + [_x for _x in (_f346.args.vararg, _f346.args.kwarg) if _x])
            _self346 = (_pa346[0].arg if _ec346 is not None and _pa346
                        and not any(isinstance(_d, _ast341.Name) and _d.id == "staticmethod"
                                    for _d in _f346.decorator_list) else None)
            # name -> top-level class names over ALL its bindings; `_unk346` = names with a
            # binding of unknown class (an un-annotated assignment, a loop target ...).
            _ty346 = {}
            _hh346 = {}
            _unk346 = set()
            for _p346 in _pa346:
                if _p346.annotation is not None:
                    _ty346.setdefault(_p346.arg, set()).update(
                        _at346.get(id(_p346.annotation), set()))
                    _hh346.setdefault(_p346.arg, set()).add(
                        _ah346.get(id(_p346.annotation), ""))
                elif _p346.arg != _self346:
                    _unk346.add(_p346.arg)
            for _n346 in _ast341.walk(_f346):
                if isinstance(_n346, _ast341.AnnAssign) and isinstance(_n346.target,
                                                                        _ast341.Name):
                    _ty346.setdefault(_n346.target.id, set()).update(
                        _at346.get(id(_n346.annotation), set()))
                    _hh346.setdefault(_n346.target.id, set()).add(
                        _ah346.get(id(_n346.annotation), ""))
                elif isinstance(_n346, _ast341.Assign):
                    _v346 = _n346.value
                    _cc346 = (_v346.func.id if isinstance(_v346, _ast341.Call)
                              and isinstance(_v346.func, _ast341.Name)
                              and (_v346.func.id in _cls341 or _v346.func.id in _imm348)
                              else None)
                    for _t346 in _n346.targets:
                        if isinstance(_t346, _ast341.Name):
                            if _cc346:
                                _ty346.setdefault(_t346.id, set()).add(_cc346)
                            elif isinstance(_v346, (_ast341.List, _ast341.ListComp)):
                                _hh346.setdefault(_t346.id, set()).add("list")
                            elif isinstance(_v346, (_ast341.Set, _ast341.SetComp,
                                                    _ast341.Dict, _ast341.DictComp)):
                                _hh346.setdefault(_t346.id, set()).add("set")
                            else:
                                _unk346.add(_t346.id)
                        else:
                            for _y346 in _ast341.walk(_t346):
                                if (isinstance(_y346, _ast341.Name)
                                        and isinstance(_y346.ctx, _ast341.Store)):
                                    _unk346.add(_y346.id)
                elif isinstance(_n346, (_ast341.For, _ast341.AsyncFor, _ast341.With,
                                        _ast341.AsyncWith, _ast341.NamedExpr,
                                        _ast341.comprehension, _ast341.AugAssign)):
                    _tt346 = ([_n346.target] if not isinstance(
                        _n346, (_ast341.With, _ast341.AsyncWith))
                              else [_w.optional_vars for _w in _n346.items if _w.optional_vars])
                    for _t346 in _tt346:
                        for _y346 in _ast341.walk(_t346):
                            if (isinstance(_y346, _ast341.Name)
                                    and isinstance(_y346.ctx, _ast341.Store)):
                                _unk346.add(_y346.id)
            # Expression -> the set of classes it may be (empty = unknown).
            _ex346 = {}
            for _n346 in _ast341.walk(_f346):
                if isinstance(_n346, _ast341.Name):
                    if _self346 is not None and _n346.id == _self346:
                        _ex346[id(_n346)] = {_ec346}
                    elif _n346.id in _ty346:
                        _ex346[id(_n346)] = set(_ty346[_n346.id])
                elif (isinstance(_n346, _ast341.Call) and isinstance(_n346.func, _ast341.Name)
                      and (_n346.func.id in _cls341 or _n346.func.id in _imm348)):
                    _ex346[id(_n346)] = {_n346.func.id}
            for _n346 in _ast341.walk(_f346):
                if (isinstance(_n346, _ast341.Attribute)
                        and isinstance(_n346.value, _ast341.Name)
                        and _ex346.get(id(_n346.value))):
                    for _c346 in _ex346[id(_n346.value)]:
                        for _a346 in _clo346.get(_c346, []):
                            if _n346.attr in _cf346.get(_a346, {}):
                                _ex346.setdefault(id(_n346), set()).update(_at346.get(
                                    id(_cf346[_a346][_n346.attr]), set()))
                                break
            # (#348) stores on immutable records.
            for _n346 in _ast341.walk(_f346):
                _rv348 = None
                _fd348 = None
                if (isinstance(_n346, _ast341.Attribute)
                        and not isinstance(_n346.ctx, _ast341.Load)):
                    _rv348, _fd348 = _n346.value, _n346.attr
                elif (isinstance(_n346, _ast341.Call) and isinstance(_n346.func, _ast341.Name)
                      and _n346.func.id in ("setattr", "delattr")
                      and _n346.func.id not in _bound341 | _imp341
                      and len(_n346.args) >= 2):
                    _rv348 = _n346.args[0]
                    _fd348 = (_n346.args[1].value if isinstance(_n346.args[1], _ast341.Constant)
                              and isinstance(_n346.args[1].value, str) else "*")
                if _rv348 is None or not _imm348:
                    continue
                _kc348 = set(_ex346.get(id(_rv348), set()))
                if (isinstance(_rv348, _ast341.Name) and _rv348.id in _unk346
                        and _rv348.id != _self346):
                    _kc348 = set()
                _why348 = ""
                if _kc348 & set(_imm348):
                    _why348 = (f"its receiver `{_ast341.unparse(_rv348)}` is an instance of "
                               f"the immutable record(s) {sorted(_kc348 & set(_imm348))}")
                elif ((not _kc348 or not (_kc348 <= set(_cls341)))
                      and (_fd348 in _immf348 or "*" in _immf348 or _fd348 == "*")):
                    _why348 = (f"its receiver `{_ast341.unparse(_rv348)}` is of unknown "
                               f"class and `{_fd348}` is a field of an immutable record of "
                               f"this file ({sorted(_imm348)})")
                if _why348:
                    raise _PyCSLSemErr341(
                        f"'{_f346.name}' line {getattr(_n346, 'lineno', 0)}: "
                        f"`{_ast341.unparse(_n346)}` stores or deletes an attribute and "
                        f"{_why348}. A `NamedTuple` / `namedtuple` / frozen `@dataclass` "
                        f"instance is immutable — CPython raises AttributeError / "
                        f"FrozenInstanceError on ANY attribute store or delete — but the "
                        f"record model lowers it as a MUTABLE record, so the store would "
                        f"be verified as succeeding (route #348). Build a new value "
                        f"(`n._replace(x=...)`, `dataclasses.replace(d, x=...)`), or make "
                        f"the class a mutable record (annotate the receiver with it).",
                        stage="ir-semantic", code="PYCSL-R348-IMMUTABLE-RECORD-STORE")
            # (#349) unhashable records in hashing positions.
            if not _u349:
                continue
            for _n346 in _ast341.walk(_f346):
                _hx349 = []
                if isinstance(_n346, _ast341.Set):
                    _hx349 = list(_n346.elts)
                elif isinstance(_n346, _ast341.SetComp):
                    _hx349 = [_n346.elt]
                elif isinstance(_n346, _ast341.Dict):
                    _hx349 = [_k for _k in _n346.keys if _k is not None]
                elif isinstance(_n346, _ast341.DictComp):
                    _hx349 = [_n346.key]
                elif isinstance(_n346, _ast341.Subscript):
                    _hx349 = [_n346.slice]
                elif (isinstance(_n346, _ast341.Compare)
                      and any(isinstance(_o, (_ast341.In, _ast341.NotIn)) for _o in _n346.ops)):
                    _cm349 = [_n346.left] + list(_n346.comparators)
                    for _i349, _o349 in enumerate(_n346.ops):
                        _rr349 = _cm349[_i349 + 1]
                        if (isinstance(_o349, (_ast341.In, _ast341.NotIn))
                                and not isinstance(_rr349, (_ast341.List, _ast341.Tuple,
                                                            _ast341.ListComp))
                                and not (isinstance(_rr349, _ast341.Name)
                                         and _rr349.id not in _unk346
                                         and _hh346.get(_rr349.id)
                                         and {_h.lower() for _h in _hh346[_rr349.id]}
                                         <= {"list", "tuple", "sequence"})):
                            _hx349.append(_cm349[_i349])
                elif isinstance(_n346, _ast341.Call):
                    _fu349 = _n346.func
                    if (isinstance(_fu349, _ast341.Name) and _fu349.id == "hash"
                            and _fu349.id not in _bound341 | _imp341):
                        _hx349 = list(_n346.args[:1])
                    elif ((isinstance(_fu349, _ast341.Name)
                           and _fu349.id in ("set", "frozenset", "Counter")
                           and _fu349.id not in _bound341)
                          or (isinstance(_fu349, _ast341.Attribute)
                              and _fu349.attr == "fromkeys")) and _n346.args:
                        _it349 = _n346.args[0]
                        if isinstance(_it349, (_ast341.List, _ast341.Tuple, _ast341.Set)):
                            _hx349 = list(_it349.elts)
                        elif isinstance(_it349, (_ast341.ListComp, _ast341.GeneratorExp,
                                                 _ast341.SetComp)):
                            _hx349 = [_it349.elt]
                        elif isinstance(_it349, _ast341.Name):
                            for _p346 in _pa346:
                                if (_p346.arg == _it349.id and _p346.annotation is not None
                                        and _ae346.get(id(_p346.annotation), set()) & _u349):
                                    _hx349 = [_it349]
                                    _ex346[id(_it349)] = _ae346[id(_p346.annotation)]
                            for _y349 in _ast341.walk(_f346):
                                if (isinstance(_y349, _ast341.AnnAssign)
                                        and isinstance(_y349.target, _ast341.Name)
                                        and _y349.target.id == _it349.id
                                        and _ae346.get(id(_y349.annotation), set()) & _u349):
                                    _hx349 = [_it349]
                                    _ex346[id(_it349)] = _ae346[id(_y349.annotation)]
                    elif (isinstance(_fu349, _ast341.Attribute)
                          and _fu349.attr in ("add", "discard", "remove", "get", "setdefault",
                                              "pop", "__contains__", "__getitem__")
                          and _n346.args
                          and not (isinstance(_fu349.value, _ast341.Name)
                                   and _fu349.value.id not in _unk346
                                   and _hh346.get(_fu349.value.id)
                                   and {_h.lower() for _h in _hh346[_fu349.value.id]}
                                   <= {"list", "sequence", "mutablesequence"})):
                        _hx349 = list(_n346.args[:1])
                for _h349 in _hx349:
                    _hc349 = _ex346.get(id(_h349), set()) & _u349
                    if _hc349:
                        raise _PyCSLSemErr341(
                            f"'{_f346.name}' line {getattr(_n346, 'lineno', 0)}: "
                            f"`{_ast341.unparse(_h349)}` (an instance of {sorted(_hc349)}) "
                            f"is HASHED by `{_ast341.unparse(_n346)}` (a set element, a dict "
                            f"key, a membership test or subscript of a set / dict, or "
                            f"`hash(...)`). Its class has `__hash__ = None` (an explicit "
                            f"`__hash__ = None`, a `@dataclass` with `eq` and without "
                            f"`frozen` / `unsafe_hash`, an `__eq__` without `__hash__`, or "
                            f"an unhashable field of a NamedTuple / frozen record), so "
                            f"CPython raises TypeError here, while the model lowers the "
                            f"collection as an opaque value (route #349). Make the class "
                            f"hashable (`@dataclass(frozen=True)`, or define `__hash__`) "
                            f"or key by a field.",
                            stage="ir-semantic", code="PYCSL-R349-UNHASHABLE-RECORD")
        # ROUTE #347 — A FIELD STORED ON ONLY SOME CONSTRUCTOR PATHS IS ASSUMED PRESENT.
        # The record model gives every field of the class a value, so a read `r.x` never
        # raises; CPython raises AttributeError when no store reached `x` (k03: `if flag:
        # self.x = 1` in `__init__`; also an early `return`, a store inside `try`, a field
        # stored only by another method, a `field(init=False)` without default) — and
        # `no_exception \all` PROVED it. RULE: DEFINITE ASSIGNMENT over each class's
        # constructor (own `__init__`; else a `@dataclass`'s / NamedTuple's synthesized
        # fields; else the first ancestor's constructor), as GEN sets computed bottom-up
        # (`(gen on fall-through or None, [gen at each return])`): `if` meets its branches,
        # a loop / `with` body / `try` body without handler-covered fall-through counts
        # nothing, `raise` never falls through, a leading `super().__init__()` /
        # `B.__init__(self, ..)` adds the base constructor's set, a `del self.f` anywhere
        # removes `f`. A field of a class (stored on `self` by any of its or its ancestors'
        # methods, or a dataclass field) that is not definitely assigned and not a class
        # attribute is MAYBE-ABSENT; reading an attribute of that name (any receiver but a
        # module) in a function whose `no_exception` covers AttributeError is REFUSED.
        _sr347 = {}
        _da347 = {}
        for _cn346 in [_c for _l, _c in sorted((len(_clo346[_c]), _c) for _c in _cls341)]:
            _gen347 = None
            for _k346 in _cls341[_cn346]:
                _ini347 = [_m for _m in _k346.body
                           if isinstance(_m, (_ast341.FunctionDef, _ast341.AsyncFunctionDef))
                           and _m.name == "__init__"]
                _g347 = None
                if _ini347:
                    _ini347 = _ini347[-1]
                    _pi347 = _ini347.args.posonlyargs + _ini347.args.args
                    _sf347 = _pi347[0].arg if _pi347 else "self"
                    _inh347 = set()
                    for _a346 in _clo346[_cn346][1:]:
                        if _a346 in _da347:
                            _inh347 = _da347[_a346]
                            break
                        if _a346 not in _cls341:
                            break
                    _pre347 = []
                    _q347 = [_ini347]
                    while _q347:
                        _s347 = _q347.pop()
                        _pre347.append(_s347)
                        _bl347 = [getattr(_s347, _fn, None) for _fn in ("body", "orelse",
                                                                        "finalbody")]
                        _bl347 += [_h.body for _h in (getattr(_s347, "handlers", None) or [])]
                        _bl347 += [_c.body for _c in (getattr(_s347, "cases", None) or [])]
                        for _l347 in _bl347:
                            if isinstance(_l347, list):
                                _q347.extend(_x for _x in _l347 if isinstance(_x, _ast341.stmt)
                                             and not isinstance(_x, (
                                                 _ast341.FunctionDef, _ast341.AsyncFunctionDef,
                                                 _ast341.ClassDef)))
                    _sum347 = {}
                    _del347 = set()
                    for _s347 in reversed(_pre347):
                        # sequential summaries of each statement list of _s347
                        _ls347 = []
                        _lists347 = [getattr(_s347, "body", None)
                                     if not isinstance(_s347, _ast341.ExceptHandler) else None,
                                     getattr(_s347, "orelse", None),
                                     getattr(_s347, "finalbody", None)]
                        _lists347 = [(_l if isinstance(_l, list) else []) for _l in _lists347]
                        _lists347 += [_h.body for _h in (getattr(_s347, "handlers", None) or [])]
                        _lists347 += [_c.body for _c in (getattr(_s347, "cases", None) or [])]
                        for _l347 in _lists347:
                            _acc347 = set()
                            _R347 = []
                            _G347 = set()
                            for _x347 in _l347:
                                if id(_x347) not in _sum347:
                                    continue
                                _gx347, _rx347 = _sum347[id(_x347)]
                                _R347.extend(_acc347 | _r for _r in _rx347)
                                if _gx347 is None:
                                    _G347 = None
                                    break
                                _acc347 = _acc347 | _gx347
                            if _G347 is not None:
                                _G347 = _acc347
                            _ls347.append((_G347, _R347))
                        _tg347 = []
                        if isinstance(_s347, (_ast341.Assign, _ast341.AugAssign)) or (
                                isinstance(_s347, _ast341.AnnAssign) and _s347.value is not None):
                            _tg347 = (list(_s347.targets) if isinstance(_s347, _ast341.Assign)
                                      else [_s347.target])
                        elif isinstance(_s347, (_ast341.With, _ast341.AsyncWith)):
                            _tg347 = [_w.optional_vars for _w in _s347.items if _w.optional_vars]
                        _gs347 = set()
                        for _t347 in _tg347:
                            for _y347 in _ast341.walk(_t347):
                                if (isinstance(_y347, _ast341.Attribute)
                                        and isinstance(_y347.value, _ast341.Name)
                                        and _y347.value.id == _sf347):
                                    _gs347.add(_y347.attr)
                        if isinstance(_s347, _ast341.Delete):
                            for _y347 in _ast341.walk(_s347):
                                if (isinstance(_y347, _ast341.Attribute)
                                        and isinstance(_y347.value, _ast341.Name)
                                        and _y347.value.id == _sf347):
                                    _del347.add(_y347.attr)
                        for _y347 in _ast341.walk(_s347):
                            if (isinstance(_y347, _ast341.Call)
                                    and isinstance(_y347.func, _ast341.Name)
                                    and _y347.func.id == "delattr"):
                                _del347.add("*")
                        if isinstance(_s347, _ast341.Expr) and isinstance(_s347.value,
                                                                          _ast341.Call):
                            _cv347 = _s347.value
                            _cf347 = _cv347.func
                            if (isinstance(_cf347, _ast341.Name) and _cf347.id == "setattr"
                                    and len(_cv347.args) >= 2
                                    and isinstance(_cv347.args[0], _ast341.Name)
                                    and _cv347.args[0].id == _sf347
                                    and isinstance(_cv347.args[1], _ast341.Constant)
                                    and isinstance(_cv347.args[1].value, str)):
                                _gs347.add(_cv347.args[1].value)
                            elif (isinstance(_cf347, _ast341.Attribute)
                                  and _cf347.attr == "__init__"):
                                if (isinstance(_cf347.value, _ast341.Call)
                                        and isinstance(_cf347.value.func, _ast341.Name)
                                        and _cf347.value.func.id == "super"):
                                    _gs347 |= _inh347
                                elif (isinstance(_cf347.value, _ast341.Name)
                                      and _cf347.value.id in _da347 and _cv347.args
                                      and isinstance(_cv347.args[0], _ast341.Name)
                                      and _cv347.args[0].id == _sf347):
                                    _gs347 |= _da347[_cf347.value.id]
                        if isinstance(_s347, (_ast341.FunctionDef, _ast341.AsyncFunctionDef)):
                            _sum347[id(_s347)] = _ls347[0]
                        elif isinstance(_s347, _ast341.Raise):
                            _sum347[id(_s347)] = (None, [])
                        elif isinstance(_s347, _ast341.Return):
                            _sum347[id(_s347)] = (None, [set()])
                        elif isinstance(_s347, (_ast341.Break, _ast341.Continue)):
                            _sum347[id(_s347)] = (None, [])
                        elif isinstance(_s347, _ast341.If):
                            _g1347, _r1347 = _ls347[0]
                            _g2347, _r2347 = _ls347[1]
                            _sum347[id(_s347)] = (
                                _g2347 if _g1347 is None else _g1347 if _g2347 is None
                                else _g1347 & _g2347, _r1347 + _r2347)
                        elif isinstance(_s347, (_ast341.For, _ast341.AsyncFor, _ast341.While)):
                            _sum347[id(_s347)] = (set(), _ls347[0][1] + _ls347[1][1])
                        elif isinstance(_s347, (_ast341.With, _ast341.AsyncWith)):
                            _sum347[id(_s347)] = (_gs347, [_gs347 | _r for _r in _ls347[0][1]])
                        elif isinstance(_s347, _ast341.Try) or type(_s347).__name__ == "TryStar":
                            _gb347, _rb347 = _ls347[0]
                            _go347, _ro347 = _ls347[1]
                            _gf347, _rf347 = _ls347[2]
                            _nm347 = None if (_gb347 is None or _go347 is None) else (
                                _gb347 | _go347)
                            _rt347 = list(_rb347) + list(_rf347)
                            if _gb347 is not None:
                                _rt347 += [_gb347 | _r for _r in _ro347]
                            for _gh347, _rh347 in _ls347[3:]:
                                _rt347 += _rh347
                                if _gh347 is not None:
                                    _nm347 = _gh347 if _nm347 is None else (_nm347 & _gh347)
                            _sum347[id(_s347)] = (
                                None if (_nm347 is None or _gf347 is None)
                                else (_nm347 | _gf347), _rt347)
                        elif type(_s347).__name__ == "Match":
                            _mm347 = None
                            _rt347 = []
                            for _gc347, _rc347 in _ls347[3:]:
                                _rt347 += _rc347
                                if _gc347 is not None:
                                    _mm347 = _gc347 if _mm347 is None else (_mm347 & _gc347)
                            _lc347 = _s347.cases[-1] if _s347.cases else None
                            if not (_lc347 is not None and _lc347.guard is None
                                    and type(_lc347.pattern).__name__ == "MatchAs"
                                    and _lc347.pattern.pattern is None):
                                _mm347 = set()
                            _sum347[id(_s347)] = (_mm347, _rt347)
                        else:
                            _sum347[id(_s347)] = (_gs347, [])
                    _G347, _R347 = _sum347[id(_ini347)]
                    for _r347 in ([_G347] if _G347 is not None else []) + list(_R347):
                        _g347 = set(_r347) if _g347 is None else (_g347 & _r347)
                    _g347 = (_g347 or set()) - _del347
                    if "*" in _del347:
                        _g347 = set()
                elif _cn346 in _dc346 and _dc346[_cn346]["init"] is not False:
                    _g347 = set()
                    for _a346 in _clo346[_cn346]:
                        if _a346 not in _dc346:
                            continue
                        for _fn347, _fa347 in _cf346.get(_a346, {}).items():
                            _hd347 = _ah346.get(id(_fa347), "")
                            if _hd347 == "ClassVar":
                                continue
                            _g347.add(_fn347)
                    for _k347 in _cls341[_cn346]:
                        for _s347 in _k347.body:
                            if (isinstance(_s347, _ast341.AnnAssign)
                                    and isinstance(_s347.target, _ast341.Name)
                                    and isinstance(_s347.value, _ast341.Call)
                                    and isinstance(_s347.value.func, (_ast341.Name,
                                                                      _ast341.Attribute))
                                    and (getattr(_s347.value.func, "id", None) == "field"
                                         or getattr(_s347.value.func, "attr", None) == "field")
                                    and any(_kw.arg == "init"
                                            and isinstance(_kw.value, _ast341.Constant)
                                            and _kw.value.value is False
                                            for _kw in _s347.value.keywords)
                                    and not any(_kw.arg in ("default", "default_factory")
                                                for _kw in _s347.value.keywords)):
                                _g347.discard(_s347.target.id)
                elif any((isinstance(_b, _ast341.Name) and _b.id == "NamedTuple")
                         or (isinstance(_b, _ast341.Attribute) and _b.attr == "NamedTuple")
                         for _b in _k346.bases):
                    _g347 = set(_cf346.get(_cn346, {}).keys())
                if _g347 is not None:
                    _gen347 = _g347 if _gen347 is None else (_gen347 & _g347)
            if _gen347 is None:
                _gen347 = set()
                for _a346 in _clo346[_cn346][1:]:
                    if _a346 in _da347:
                        _gen347 = set(_da347[_a346])
                        break
                    if _a346 not in _cls341:
                        break
            _da347[_cn346] = _gen347
        _ma347 = set()
        for _cn346 in _cls341:
            _fs347 = set()
            _ca347 = set()
            for _a346 in _clo346[_cn346]:
                for _k346 in _cls341.get(_a346, []):
                    for _s346 in _k346.body:
                        if isinstance(_s346, (_ast341.FunctionDef, _ast341.AsyncFunctionDef,
                                              _ast341.ClassDef)):
                            _ca347.add(_s346.name)
                        elif isinstance(_s346, _ast341.Assign):
                            for _t346 in _s346.targets:
                                for _y346 in _ast341.walk(_t346):
                                    if isinstance(_y346, _ast341.Name):
                                        _ca347.add(_y346.id)
                        elif (isinstance(_s346, _ast341.AnnAssign)
                              and isinstance(_s346.target, _ast341.Name)):
                            if _a346 in _dc346 or _a346 in _imm348:
                                _fs347.add(_s346.target.id)
                            if _s346.value is not None and not (
                                    isinstance(_s346.value, _ast341.Call)
                                    and (getattr(_s346.value.func, "id", None) == "field"
                                         or getattr(_s346.value.func, "attr", None) == "field")
                                    and not any(_kw.arg in ("default", "default_factory")
                                                for _kw in _s346.value.keywords)):
                                _ca347.add(_s346.target.id)
                        elif isinstance(_s346, (_ast341.Import, _ast341.ImportFrom)):
                            _ca347 |= {(_x.asname or _x.name).split(".")[0]
                                       for _x in _s346.names}
                    for _m346 in _k346.body:
                        if not isinstance(_m346, (_ast341.FunctionDef,
                                                  _ast341.AsyncFunctionDef)):
                            continue
                        _pm347 = _m346.args.posonlyargs + _m346.args.args
                        if not _pm347:
                            continue
                        _sf347 = _pm347[0].arg
                        for _y346 in _ast341.walk(_m346):
                            if (isinstance(_y346, _ast341.Attribute)
                                    and not isinstance(_y346.ctx, _ast341.Load)
                                    and isinstance(_y346.value, _ast341.Name)
                                    and _y346.value.id == _sf347):
                                _fs347.add(_y346.attr)
                            elif (isinstance(_y346, _ast341.Call)
                                  and isinstance(_y346.func, _ast341.Name)
                                  and _y346.func.id == "setattr" and len(_y346.args) >= 2
                                  and isinstance(_y346.args[0], _ast341.Name)
                                  and _y346.args[0].id == _sf347
                                  and isinstance(_y346.args[1], _ast341.Constant)
                                  and isinstance(_y346.args[1].value, str)):
                                _fs347.add(_y346.args[1].value)
            _ma347 |= _fs347 - _da347.get(_cn346, set()) - _ca347
        if _ma347:
            _nx347 = set()
            for _f347 in (_ir342.get("functions") or []):
                if not isinstance(_f347, dict) or _f347.get("trusted") or _f347.get("abstract"):
                    continue
                _ct347 = _f347.get("contracts") or {}
                if _ct347.get("no_exception_all") or set(_ct347.get("no_exception") or []) & {
                        "AttributeError", "Exception", "BaseException"}:
                    _nx347.add(_f347.get("name"))
            for _f346, _ec346 in _fn346:
                _irn347 = (_ec346.lower() + "__" + _f346.name) if _ec346 else _f346.name
                if _irn347 not in _nx347:
                    continue
                _aug347 = {id(_y.target) for _y in _ast341.walk(_f346)
                           if isinstance(_y, _ast341.AugAssign)}
                for _n346 in _ast341.walk(_f346):
                    if not (isinstance(_n346, _ast341.Attribute) and _n346.attr in _ma347):
                        continue
                    if isinstance(_n346.ctx, _ast341.Store) and id(_n346) not in _aug347:
                        continue
                    if isinstance(_n346.value, _ast341.Name) and _n346.value.id in (
                            _imp341 - _bound341):
                        continue
                    raise _PyCSLSemErr341(
                        f"'{_f346.name}' line {getattr(_n346, 'lineno', 0)}: it claims "
                        f"`#@ no_exception` (covering AttributeError) and reads "
                        f"`{_ast341.unparse(_n346)}`, but `{_n346.attr}` is a field some "
                        f"constructor of this file does NOT definitely assign (a store "
                        f"under `if` / a loop / `try` / `with`, after an early `return`, "
                        f"only in another method, or a `field(init=False)` without default; "
                        f"or a `del`). The record model gives every field a value, so the "
                        f"read would be verified as never raising while CPython raises "
                        f"AttributeError when no store reached it (route #347). Assign "
                        f"`self.{_n346.attr}` on every `__init__` path (e.g. a default "
                        f"before the branch), or give the class a class-level default.",
                        stage="ir-semantic", code="PYCSL-R347-FIELD-MAYBE-UNASSIGNED")

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
    # (#49) ROUTE #278 — the sets below (escaping undeclared raises, declared raises,
    # HIDDEN-OUT) are also what an OVERRIDE may raise, so they are computed whenever the
    # override-refinement check has a pair to judge (block after this one).
    _ov278 = [_o for _o in (_ir263.get("overrides") or []) if isinstance(_o, dict)
              and (getattr(args, "check_behavioral_subtyping", False)
                   or _o.get("from_conforms_to"))]
    _dir272 = {}
    _decl272 = {}
    _ho272 = {}
    if _ov278 or any((_f.get("contracts") or {}).get("no_exception")
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

    # (#49) ROUTE #278 — THE OVERRIDE THE CHECK MISSED. The refinement goal
    # (`_render_refinement_goal`) compares requires/ensures only, and a caller of `a.m()`
    # (`a: A`) is lowered against `A.m`'s WHOLE contract: its `raises`/`no_exception`
    # (the route #100/#105/#186 wrap, route #272's hidden set) and its `assigns` (the
    # caller's frame). MEASURED at 78162575 WITH the flag (CPython contradicts each): an
    # override raising an undeclared ValueError under a `no_exception \all` caller (p091);
    # an override writing `self.v` against `assigns \nothing` (probe g2); an override
    # SWAPPING its parameter names (`m(self, y, x)` vs `m(self, x, y)`: the goal renders
    # both contracts over the SUB's names, so it compared the wrong arguments — probe g3).
    # RULE, per recorded pair (sub S.t refines base X.t), each a refusal:
    #   R1 raises: every exception S.t may let escape — its escaping undeclared `raise`s,
    #      its declared `raises`, and route #272's HIDDEN-OUT — must be one X.t DECLARES
    #      (a declared class or subclass of it) and X.t's `no_exception` does not exclude
    #      (`\all` excludes everything). An exception S.t raises WITHOUT a declaration
    #      (no condition) is admitted only when X.t's covering clause has no condition
    #      (`when True`); a declared one owes `(pre_X /\ cond_S) -> cond_X`, built by
    #      `_render_refinement_goal`. An unnameable `raise` (`*`) never refines.
    #   R2 no_exception: X.t's `no_exception` set must be covered by S.t's (a caller
    #      under `--strict-no-exception-propagation` trusts X.t's claim for IMPLICIT
    #      exceptions too).
    #   R3 assigns: if X.t declares `assigns`, S.t must declare one whose every location
    #      X.t's also names (`\nothing` names none) — except a location rooted at a
    #      `self` field class X does not have (no X-typed receiver can observe it).
    #   R4 parameters: S.t takes at least X.t's positional parameters, and every one the
    #      base contract mentions sits at the same position under the same name (extra
    #      trailing parameters are bound to every value by the goal, which
    #      over-approximates their defaults).
    # `\trusted`/`\abstract`/imported subs speak by their declarations only (no body).
    # INLINE (check-mirror-coverage); `_run_pipeline`'s mirror twin is `\trusted`.
    if _ov278:
        from exception_model import handler_catches as _hc278
        _viol278 = []
        # ROUTE #338: the Python annotations of every method (class, name) -> def, and
        # every class's ancestors, for R5 (the IR flattens `Optional[int]` / `List[int]`)
        import ast as _ast338
        _cm338 = {}
        _anc338 = {}
        try:
            _t338 = _ast338.parse(source_code)
        except (SyntaxError, ValueError):
            _t338 = None
        for _c338 in (_ast338.walk(_t338) if _t338 is not None else ()):
            if isinstance(_c338, _ast338.ClassDef):
                _anc338.setdefault(_c338.name, [b.id for b in _c338.bases
                                                if isinstance(b, _ast338.Name)])
                for _m338 in _c338.body:
                    if isinstance(_m338, (_ast338.FunctionDef, _ast338.AsyncFunctionDef)):
                        _cm338.setdefault((_c338.name, _m338.name), _m338)
        for _o278 in _ov278:
            _sf278 = _byname263.get(_o278.get("sub_method"))
            _bf278 = _byname263.get(_o278.get("base_method"))
            if _sf278 is None or _bf278 is None:
                continue  # Module 6 refuses an unresolvable pair (PYCSL-SUBTYPING-PAIR)
            _sn278, _bn278 = _sf278["name"], _bf278["name"]
            _sc278 = _sf278.get("contracts") or {}
            _bc278 = _bf278.get("contracts") or {}
            _bdecl278 = [(_r.get("exc_type"), _r.get("condition"))
                         for _r in (_bc278.get("raises") or [])
                         if isinstance(_r, dict) and _r.get("exc_type")]
            _ball278 = bool(_bc278.get("no_exception_all"))
            _bnamed278 = [a for a in (_bc278.get("no_exception") or []) if isinstance(a, str)]
            # R1 — what the override may let escape: (exception, declared?)
            _sexc278 = [(_e, True) for _e in sorted(_decl272.get(_sn278, set()))]
            _sexc278 += [(_e, False) for _e in sorted(
                (_dir272.get(_sn278, set()) | _ho272.get(_sn278, set()))
                - _decl272.get(_sn278, set()))]
            for _e278, _isdecl278 in _sexc278:
                _cov278 = [_c for (_d, _c) in _bdecl278 if _e278 != "*" and _hc278(_d, _e278)]
                _excl278 = _ball278 or any(_e278 == "*" or _hc278(_a, _e278)
                                           for _a in _bnamed278)
                if _excl278 or not _cov278:
                    _viol278.append((_sn278, _bn278, "may raise `%s`, which `%s` %s" % (
                        _e278, _bn278, "excludes by `no_exception`" if _excl278
                        else "does not declare (`#@ raises`)")))
                elif not _isdecl278 and not any(
                        _c is None or (isinstance(_c, dict) and _c.get("type") == "Bool"
                                       and _c.get("value") is True) for _c in _cov278):
                    _viol278.append((_sn278, _bn278, "raises `%s` without a declared "
                                     "condition, while `%s` declares it only under one"
                                     % (_e278, _bn278)))
            # R2 — the base's no_exception claim must be kept
            _sall278 = bool(_sc278.get("no_exception_all"))
            _snamed278 = [a for a in (_sc278.get("no_exception") or []) if isinstance(a, str)]
            if _ball278 and not _sall278:
                _viol278.append((_sn278, _bn278, "drops `%s`'s `no_exception \\all`" % _bn278))
            for _a278 in ([] if _sall278 else _bnamed278):
                if not any(_hc278(_x, _a278) for _x in _snamed278):
                    _viol278.append((_sn278, _bn278, "drops `%s`'s `no_exception %s`"
                                     % (_bn278, _a278)))
            # R3 — frame: the override may only assign what the base declares
            _bas278 = _bc278.get("assigns") or []
            _sas278 = _sc278.get("assigns") or []
            if _bas278:
                _bset278 = {_json.dumps(_x, sort_keys=True) for _x in _bas278
                            if not (isinstance(_x, dict) and _x.get("type") == "Nothing")}
                if not _sas278:
                    _viol278.append((_sn278, _bn278, "declares no `assigns` while `%s` "
                                     "declares one" % _bn278))
                # A location rooted at a `self` field the BASE class does not have is
                # admitted: a base-typed receiver cannot name it, so no caller holding one
                # can observe the write (aliasing through two differently-typed
                # variables is not modelled at all — FIELD-DISJOINT's residue).
                _bfl278 = set()
                for _tn278, _tf278 in _fields263.items():
                    if _tn278.lower() == str(_o278.get("base_type", "")).lower():
                        _bfl278 |= set(_tf278)
                for _x278 in _sas278:
                    if isinstance(_x278, dict) and _x278.get("type") == "Nothing":
                        continue
                    _rt278 = None
                    _st278 = [_x278]
                    while _st278 and _rt278 is None:
                        _y278 = _st278.pop(0)
                        if isinstance(_y278, dict):
                            if (_y278.get("type") == "FieldGet"
                                    and _y278.get("object") == "self"):
                                _rt278 = _y278.get("field")
                            else:
                                _st278.extend(_v for _v in _y278.values()
                                              if isinstance(_v, (dict, list)))
                        elif isinstance(_y278, list):
                            _st278.extend(_y278)
                    if _rt278 is not None and _rt278 not in _bfl278:
                        continue
                    if _json.dumps(_x278, sort_keys=True) not in _bset278:
                        _viol278.append((_sn278, _bn278, "assigns a location `%s`'s "
                                         "`assigns` does not name" % _bn278))
                        break
            # R4 — parameters, by position. The goal renders the base's contract over the
            # SUB's binders, so a base parameter the base contract mentions must sit at
            # the same position in the override (one it does not mention cannot be
            # misread; one absent from the override is unbound -> Why3 rejects the goal).
            _sp278 = list(_sf278.get("formal_params") or [])
            _bp278 = list(_bf278.get("formal_params") or [])
            _bdump278 = _json.dumps(_bc278, sort_keys=True)
            if len(_sp278) < len(_bp278) or any(
                    _bx != _sx and _bx in _sp278 and ('"%s"' % _bx) in _bdump278
                    for _bx, _sx in zip(_bp278, _sp278)):
                _viol278.append((_sn278, _bn278, "binds its parameters %s where `%s` binds "
                                 "%s (by position)" % (_sp278, _bn278, _bp278)))
            # R5 — annotations (ROUTE #338). The caller's lowering of `b.m()` (`b: X`)
            # TYPES the result by X.m's return annotation, and the override's own proof
            # assumes its parameters' annotations: `X.m -> int` overridden `-> float`
            # made `b.m() % 1 == 0` prove (the goal above was `true -> true`). So the
            # override's return annotation must be a subtype of the base's (covariance)
            # and each base parameter's annotation a subtype of the override's
            # (contravariance). Subtyping, per member of a `Union` / `Optional` / `|`:
            # the same type, `bool` under `int`, a class of this file under one of its
            # ancestors, anything under `Any` / `object`. `int` is NOT taken under
            # `float` (PEP 484's numeric tower; the model types them as `int` / `real`).
            # A missing annotation is `Any` on the wider side (no constraint) and is
            # refused on the narrower side (an unannotated override of `-> int`).
            _sd338 = _cm338.get((_sf278.get("self_type"),
                                 _sn278[len(str(_sf278.get("self_type"))) + 2:]))
            _bd338 = _cm338.get((_bf278.get("self_type"),
                                 _bn278[len(str(_bf278.get("self_type"))) + 2:]))
            # (#49) ROUTE #344 — A CLASS WITH NO OWN DEF RUNS THE ONE ITS MRO PICKS. A pair
            # whose sub (or base) class INHERITS the method (`class C(B, A): pass`, Module 6
            # records `c__m refines a__m` and types `c__m` by B.m) had no def of its own
            # here, so R5 skipped it: `A.m -> int`, `B.m -> float` made `a.m() % 1 == 0`
            # PROVE for `a = C()` (CPython 0.5). Each side without a def of its own is
            # resolved through Python's C3 linearization of the file's classes (bases by
            # name, as `_anc338` holds them) to the first class of its MRO that defines the
            # method. Inline (no new def: `_run_pipeline`'s mirror twin is `\trusted`).
            for _ix344, _fx344 in ((0, _sf278), (1, _bf278)):
                if (_sd338, _bd338)[_ix344] is not None:
                    continue
                _cn344 = _fx344.get("self_type")
                _mn344 = (_sn278, _bn278)[_ix344][len(str(_cn344)) + 2:]
                _lin344 = {}
                _todo344 = [_cn344] if _cn344 in _anc338 else []
                _gd344 = 0
                while _todo344 and _gd344 < 100000:
                    _gd344 += 1
                    _k344 = _todo344[-1]
                    _bs344 = list(_anc338.get(_k344, []))
                    _ms344 = [_b for _b in _bs344 if _b in _anc338 and _b not in _lin344]
                    if _ms344:
                        if any(_b in _todo344 for _b in _ms344):
                            break  # a base cycle (CPython rejects it); stay unresolved
                        _todo344.extend(_ms344)
                        continue
                    _todo344.pop()
                    _sq344 = [list(_lin344.get(_b, [_b])) for _b in _bs344] + [list(_bs344)]
                    _rs344 = [_k344]
                    while True:
                        _sq344 = [_q for _q in _sq344 if _q]
                        if not _sq344:
                            break
                        _cd344 = None
                        for _q344 in _sq344:
                            if not any(_q344[0] in _r344[1:] for _r344 in _sq344):
                                _cd344 = _q344[0]
                                break
                        if _cd344 is None:
                            break  # no consistent MRO (CPython TypeError); stop here
                        _rs344.append(_cd344)
                        for _q344 in _sq344:
                            if _q344[0] == _cd344:
                                _q344.pop(0)
                    _lin344[_k344] = _rs344
                for _k344 in (_lin344.get(_cn344) or []):
                    if (_k344, _mn344) in _cm338:
                        if _ix344 == 0:
                            _sd338 = _cm338[(_k344, _mn344)]
                        else:
                            _bd338 = _cm338[(_k344, _mn344)]
                        break
            if _sd338 is not None and _bd338 is not None:
                _sa338 = _sd338.args.posonlyargs + _sd338.args.args
                _ba338 = _bd338.args.posonlyargs + _bd338.args.args
                _pr338 = [("its return annotation", _sd338.returns, _bd338.returns)]
                _pr338 += [("the annotation of parameter `%s`" % y.arg, x.annotation,
                            y.annotation) for x, y in list(zip(_ba338, _sa338))[1:]]
                for _wh338, _lo338, _hi338 in _pr338:
                    if _hi338 is None:
                        continue
                    _ms338 = []     # [lo members, hi members]
                    for _e338 in (_lo338, _hi338):
                        _mm338 = set()
                        _wl338 = [_e338]
                        while _wl338:
                            _x338 = _wl338.pop()
                            if isinstance(_x338, _ast338.Constant) and isinstance(
                                    _x338.value, str):
                                try:
                                    _x338 = _ast338.parse(_x338.value, mode="eval").body
                                except SyntaxError:
                                    _mm338.add(_x338.value)
                                    continue
                            _h338 = (getattr(_x338.value, "id", getattr(_x338.value, "attr",
                                                                        ""))
                                     if isinstance(_x338, _ast338.Subscript) else "")
                            if _x338 is None:
                                _mm338.add("Any")
                            elif isinstance(_x338, _ast338.BinOp) and isinstance(
                                    _x338.op, _ast338.BitOr):
                                _wl338 += [_x338.left, _x338.right]
                            elif _h338 == "Optional":
                                _wl338 += [_x338.slice, _ast338.Constant(value=None)]
                            elif _h338 == "Union":
                                _wl338 += (list(_x338.slice.elts) if isinstance(
                                    _x338.slice, _ast338.Tuple) else [_x338.slice])
                            elif isinstance(_x338, _ast338.Constant) and _x338.value is None:
                                _mm338.add("None")
                            else:
                                _u338 = _ast338.unparse(_x338).replace("typing.", "")
                                for _p338, _q338 in (("List[", "list["), ("Dict[", "dict["),
                                                     ("Set[", "set["), ("Tuple[", "tuple["),
                                                     ("FrozenSet[", "frozenset[")):
                                    _u338 = _u338.replace(_p338, _q338)
                                _mm338.add(_u338)
                        _ms338.append(_mm338)
                    if _ms338[1] & {"Any", "object"}:
                        continue
                    for _x338 in sorted(_ms338[0]):
                        _up338 = {_x338}
                        _wl338 = [_x338]
                        while _wl338:
                            for _y338 in _anc338.get(_wl338.pop(), []):
                                if _y338 not in _up338:
                                    _up338.add(_y338)
                                    _wl338.append(_y338)
                        if _x338 == "bool":
                            _up338.add("int")
                        if not (_up338 & _ms338[1]):
                            _viol278.append((_sn278, _bn278, "changes %s: `%s` is not a "
                                             "subtype of `%s` (%s)" % (
                                                 _wh338, _ast338.unparse(_lo338)
                                                 if _lo338 is not None else "(none: Any)",
                                                 _ast338.unparse(_hi338),
                                                 "return types are covariant"
                                                 if _wh338.startswith("its return")
                                                 else "parameter types are contravariant")))
                            break
        if _viol278:
            from errors import PyCSLSemanticError as _PyCSLSemErr278
            _v278 = _viol278[0]
            raise _PyCSLSemErr278(
                f"override '{_v278[0]}' of '{_v278[1]}' {_v278[2]}: a caller holding a "
                f"value typed with the base class is verified against the BASE method's "
                f"whole contract (its raises / no_exception / assigns, its parameters by "
                f"position), and a subclass instance runs the override, so the claim would "
                f"be proved while CPython does otherwise (route #278). Make the override "
                f"refine the base (declare at most the base's exceptions and locations, "
                f"keep its parameter names and order, return a subtype of the base's return "
                f"annotation and accept a supertype of each base parameter annotation), "
                f"widen the base's contract, or pass "
                f"`--assume-class-exact` to declare the assumption that values are exact "
                f"instances (CLASS-EXACT, listed by `--soundness-report`)"
                f"{'' if len(_viol278) == 1 else f' (also: {_viol278[1:4]})'}.",
                filename=args.file, stage="ir-semantic",
                code="PYCSL-SEM-OVERRIDE-REFINEMENT")

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

    # (#49) ROUTE #327 — TWO PYTHON NAMES MUST NOT LOWER TO ONE WhyML IDENTIFIER.
    # `whyml_ident` lowercases a leading capital (`N` -> `n`) and prefixes reserved words
    # (`result` -> `py_result`, `model` -> `py_model`) with NO collision check, so
    # `N = len(xs); n = 0; return N == n` emitted three `let n = ref ..` and PROVED
    # `!n = !n` (CPython False); a global `K = mk()` read beside a parameter `k` returned
    # the parameter; `py_model = 7; model = 3` read 3. The mangling is not injective and
    # nothing checked that the names one scope actually uses stay apart.
    # MEASURED (gen #37) before choosing: an INJECTIVE encoding (`N` -> a case-marked
    # name) re-emits every file that uses a capitalised or reserved name — ~1962 of 3077
    # root files, 48 of 510 pyref files and 48 of 53 mirror files; the REFUSAL below moves
    # only programs whose names actually collide. The collision is decided on the
    # final IR (after resolution / monomorphization), per function scope: the formal
    # parameters, every `Var` it reads (locals AND the module-level globals it names),
    # every binding target (assign / tuple / for / comprehension / walrus / quantifier),
    # plus the emitter-reserved tuple binders `_tu_*`. Class constructors (`c = C()`)
    # are calls, not `Var`s, and classes lower to the type namespace, so the idiomatic
    # `c = C()` is NOT a collision (it was 10 of the 12 name-level hits). Two IR
    # functions / classes whose WhyML symbols fold together (`AB.m` / `Ab.m` ->
    # `ab__m`) are refused the same way.
    from module6_whyml.identifiers import whyml_ident as _wid327
    _ir327 = _json.loads(json_ir)
    _cls327: Dict[str, str] = {}
    for _td327 in (_ir327.get("type_decls") or []):
        _tn327 = str((_td327 or {}).get("name") or "") if isinstance(_td327, dict) else ""
        if not _tn327:
            continue
        _tk327 = _tn327.lower()
        if _tk327 in _cls327 and _cls327[_tk327] != _tn327:
            from errors import PyCSLSemanticError as _PyCSLSemErr327c
            raise _PyCSLSemErr327c(
                f"{args.file}: PYCSL-R327-IDENT-COLLISION (route #327) — the classes "
                f"'{_cls327[_tk327]}' and '{_tn327}' lower to ONE WhyML namespace "
                f"('{_tk327}'): their types and method symbols would be confused. "
                f"Rename one of them.",
                filename=args.file, stage="ir-semantic", code="PYCSL-R327-IDENT-COLLISION")
        _cls327[_tk327] = _tn327
    _fns327: Dict[str, str] = {}
    for _f327 in (_ir327.get("functions") or []):
        if not isinstance(_f327, dict):
            continue
        _fname327 = str(_f327.get("name") or "")
        _fk327 = _wid327(_fname327) if _fname327 else ""
        if _fk327 and _fk327 in _fns327 and _fns327[_fk327] != _fname327:
            from errors import PyCSLSemanticError as _PyCSLSemErr327f
            raise _PyCSLSemErr327f(
                f"{args.file}: PYCSL-R327-IDENT-COLLISION (route #327) — the functions "
                f"'{_fns327[_fk327]}' and '{_fname327}' lower to ONE WhyML identifier "
                f"'{_fk327}'. Rename one of them.",
                filename=args.file, stage="ir-semantic", code="PYCSL-R327-IDENT-COLLISION")
        if _fk327:
            _fns327[_fk327] = _fname327
    # Module-level VALUE bindings are not in the IR (a global lowers to one opaque
    # `val constant <ident>` or is inlined), so `k = three(); K = seven()` share ONE
    # constant across every function that reads either. Read them off the source: every
    # Name bound at module level (any statement nesting, outside def/class bodies and the
    # `if __name__ == ...` driver) and every top-level def; imports are excluded.
    import ast as _ast327
    _gst327: List[Any] = list(_ast327.parse(source_code).body)
    while _gst327:
        _g327 = _gst327.pop()
        if isinstance(_g327, (_ast327.FunctionDef, _ast327.AsyncFunctionDef)):
            _gn327 = _g327.name
        elif isinstance(_g327, _ast327.Name) and isinstance(_g327.ctx, _ast327.Store):
            _gn327 = _g327.id
        else:
            _gn327 = ""
            if (isinstance(_g327, _ast327.If) and isinstance(_g327.test, _ast327.Compare)
                    and isinstance(_g327.test.left, _ast327.Name)
                    and _g327.test.left.id == "__name__"):
                continue                       # the `__main__` driver is not verified
            if not isinstance(_g327, (_ast327.ClassDef, _ast327.Lambda, _ast327.ListComp,
                                      _ast327.SetComp, _ast327.DictComp,
                                      _ast327.GeneratorExp)):
                _gst327.extend(_ast327.iter_child_nodes(_g327))
        if not _gn327:
            continue
        _gk327 = _wid327(_gn327)
        if _gk327 in _fns327 and _fns327[_gk327] != _gn327:
            from errors import PyCSLSemanticError as _PyCSLSemErr327g
            raise _PyCSLSemErr327g(
                f"{args.file}: PYCSL-R327-IDENT-COLLISION (route #327) — the module-level "
                f"names '{_fns327[_gk327]}' and '{_gn327}' lower to ONE WhyML identifier "
                f"'{_gk327}', so every function would read one for the other. Rename one "
                f"of them.",
                filename=args.file, line=int(getattr(_g327, "lineno", 0) or 0),
                stage="ir-semantic", code="PYCSL-R327-IDENT-COLLISION")
        _fns327[_gk327] = _gn327
    # (#49) ROUTE #333 — THE R327 NAMESPACES WERE INCOMPLETE. (a) EXCEPTION TAGS:
    # `safe_exc_name` strips leading underscores (so the import alias `_Y` of `Y` shares
    # one `exception Y`), which also MERGED two distinct user classes `_E` / `E` (the first
    # `except` arm caught both: proved `\result == 1`, CPython 2) and a user class
    # `_ValueError` with the BUILTIN `ValueError` (`except ValueError` caught it under
    # `no_exception \all`; CPython propagates). Refused: a user EXCEPTION class (a source
    # `class` whose base is a builtin exception or another such class, or named in a
    # raise / except / raises tag) whose stripped tag equals that of ANOTHER source class,
    # an imported name, or a builtin exception. A class spelled EXACTLY like a builtin is
    # #305's (`PYCSL-R305-BUILTIN-EXCEPTION-NAME-SHADOWED`); a `raises Y` tag that only
    # names the stripped spelling of the class `_Y` (the mirror's `_ContractSyntaxError`)
    # is the same exception and stays accepted. (b) GENERATED BINDERS: the emitter binds
    # its own locals (`_idx_<v>` loop counters, `_len_idx_`, `_any_<v>_<n>` havocs, `_tu_`,
    # `_pycsl_*`, comprehension / lambda / quantifier temporaries ...) in the SAME WhyML
    # scope as the user's names, so a user local `_idx_i` was read as (and overwritten by)
    # the counter. `_rsv333` is the census of those names (route333 REPAIR); a user name in
    # it is refused per scope below. MEASURED: renaming the generated binders instead
    # re-emits 586 / 12 / 37 (root / pyref / mirror) files; this refusal moves none.
    import re as _re333
    _rsv333 = _re333.compile(
        r"^(?:_(?:idx|len_idx|stop_idx|hv_idx|rl_idx|callit_idx|split_idx|seqlit_idx|any"
        r"|all_fold|inl|tu|u|lf|cc|csrc|cdf|mem|dk|h_f|r230|r251|class|union|pf|pycsl"
        r"|wl[0-9]+c)_|__(?:pycsl|and|or|happy)_|_for_target|_(?:alit|u|hl|rec_|row|ci|celt"
        r"|si|csl_forall|s_eq|pyobj_state|mi|hin|kin|pin|lin|hln|lln|sln|fk|cj|ae|ri|swr|fr"
        r"|fi|res|mnk|hfm|sfm|nmap)$|__f[dr]$)")
    # Only a name the USER spelled can collide: the final IR also carries the front end's
    # own generated names (`_for_target`, `_inl_res__inl<k>`, `_pycsl_multi_<k>`), which
    # are the emitter's and are not refused. A user name is an identifier of the source
    # AST (a `Name` or a parameter; a def / method NAME is not a value, measured: the
    # mirror's method `_for_target`) or a token of a `#@` contract line (quantifier and
    # ghost binders).
    _srcid333: Set[str] = set()
    for _a333 in _ast327.walk(_ast327.parse(source_code)):
        if isinstance(_a333, _ast327.Name):
            _srcid333.add(_a333.id)
        elif isinstance(_a333, _ast327.arg):
            _srcid333.add(_a333.arg)
    for _ln333 in source_code.splitlines():
        if _ln333.lstrip().startswith("#@"):
            _srcid333.update(_re333.findall(r"[A-Za-z_][A-Za-z0-9_]*", _ln333))
    import builtins as _bi333
    _bexc333: Set[str] = {_b333 for _b333 in dir(_bi333)
                          if isinstance(getattr(_bi333, _b333), type)
                          and issubclass(getattr(_bi333, _b333), BaseException)}
    _tags333: Set[str] = set()
    _stk333: List[Any] = [_ir327.get("functions") or []]
    while _stk333:
        _n333 = _stk333.pop()
        if isinstance(_n333, list):
            _stk333.extend(_n333)
            continue
        if not isinstance(_n333, dict):
            continue
        if isinstance(_n333.get("exc_type"), str):
            _tags333.update(_t333.strip() for _t333 in _n333["exc_type"].split("|"))
        _stk333.extend(_v333 for _v333 in _n333.values() if isinstance(_v333, (dict, list)))
    _cdefs333: List[Any] = []
    _others333: Set[str] = set(_bexc333)
    for _a333 in _ast327.walk(_ast327.parse(source_code)):
        if isinstance(_a333, _ast327.ClassDef):
            _cdefs333.append(_a333)
            _others333.add(_a333.name)
        elif isinstance(_a333, (_ast327.Import, _ast327.ImportFrom)):
            _others333.update((_al333.asname or _al333.name).split(".")[0]
                              for _al333 in _a333.names)
    _exc333: Set[str] = set(_bexc333)
    _grow333 = True
    while _grow333:
        _grow333 = False
        for _cd333 in _cdefs333:
            if _cd333.name in _exc333:
                continue
            _bn333 = [(_bb333.id if isinstance(_bb333, _ast327.Name) else
                       _bb333.attr if isinstance(_bb333, _ast327.Attribute) else "")
                      for _bb333 in _cd333.bases]
            if _cd333.name in _tags333 or any(_x333 in _exc333 for _x333 in _bn333):
                _exc333.add(_cd333.name)
                _grow333 = True
    for _cd333 in _cdefs333:
        _cn333 = _cd333.name
        if _cn333 not in _exc333:
            continue
        _ck333 = _cn333.lstrip("_") or _cn333
        for _o333 in sorted(_others333):
            if _o333 != _cn333 and (_o333.lstrip("_") or _o333) == _ck333:
                from errors import PyCSLSemanticError as _PyCSLSemErr333
                raise _PyCSLSemErr333(
                    f"{args.file}: PYCSL-R327-IDENT-COLLISION (route #333) — the exception "
                    f"class '{_cn333}' and the "
                    f"{'builtin exception' if _o333 in _bexc333 else 'class' if any(_q333.name == _o333 for _q333 in _cdefs333) else 'imported name'} '{_o333}' lower "
                    f"to ONE WhyML exception tag '{_ck333}' (leading underscores are "
                    f"stripped), so a handler for one would catch the other (measured: "
                    f"`raise _ValueError()` caught by `except ValueError`). Rename the class "
                    f"so its name without leading underscores is unique.",
                    filename=args.file, line=int(getattr(_cd333, "lineno", 0) or 0),
                    stage="ir-semantic", code="PYCSL-R327-IDENT-COLLISION")
    for _f327 in (_ir327.get("functions") or []):
        if not isinstance(_f327, dict):
            continue
        _fname327 = str(_f327.get("name") or "")
        _names327: Set[str] = set(str(_p327) for _p327 in (_f327.get("formal_params") or []))
        _stk327: List[Any] = [_f327.get("body"), _f327.get("contracts")]
        while _stk327:
            _n327 = _stk327.pop()
            if isinstance(_n327, list):
                _stk327.extend(_n327)
                continue
            if not isinstance(_n327, dict):
                continue
            if _n327.get("type") == "Var" and isinstance(_n327.get("name"), str):
                _names327.add(_n327["name"])
            for _key327 in ("target", "targets", "var", "vars"):
                _tv327 = _n327.get(_key327)
                for _t327 in (_tv327 if isinstance(_tv327, list) else [_tv327]):
                    if isinstance(_t327, str) and _t327.isidentifier():
                        _names327.add(_t327)
            _ia327 = _n327.get("args")
            if (_n327.get("type") == "Call" and _n327.get("func") in ("isinstance", "issubclass")
                    and isinstance(_ia327, list) and len(_ia327) == 2
                    and isinstance(_ia327[1], dict)):
                # the CLASS operand of `isinstance(x, C)` lowers to a type tag spelled with
                # the source name (`py_isinstance_C_int_op`), never to a WhyML variable
                # (measured: the mirror's `isinstance(node, Var)` beside a parameter `var`).
                _stk327.append(_ia327[0])
                _ic327 = _ia327[1]
                _stk327.extend([_e327 for _e327 in (_ic327.get("elts") or [])
                                if not (isinstance(_e327, dict) and _e327.get("type") == "Var")]
                               if _ic327.get("type") == "Tuple"
                               else ([] if _ic327.get("type") == "Var" else [_ic327]))
                continue
            for _v327 in _n327.values():
                if isinstance(_v327, (dict, list)):
                    _stk327.append(_v327)
        _seen327: Dict[str, str] = {}
        for _nm327 in sorted(_names327):
            if not _nm327.isidentifier():
                continue
            _w327 = _wid327(_nm327)
            _clash327 = _seen327.get(_w327)
            if _w327.startswith("_tu_"):
                _clash327 = "<the emitter's tuple-unpacking binders `_tu_*`>"
            elif _rsv333.match(_w327) and _nm327 in _srcid333:
                # route #333: the emitter's own binders live in this namespace
                _clash327 = (f"<the emitter's generated binder namespace "
                             f"`{_rsv333.match(_w327).group(0)}...`>")
            if _clash327 is not None and _clash327 != _nm327:
                from errors import PyCSLSemanticError as _PyCSLSemErr327
                raise _PyCSLSemErr327(
                    f"{args.file} (function '{_fname327}'): PYCSL-R327-IDENT-COLLISION "
                    f"(route #327) — the Python names '{_clash327}' and '{_nm327}' are "
                    f"distinct, but both lower to the ONE WhyML identifier '{_w327}' "
                    f"(a leading capital is lowercased and a WhyML keyword gains a `py_` "
                    f"prefix), so the proof would read one variable for the other "
                    f"(measured: `N = len(xs); n = 0; return N == n` proved True). "
                    f"Rename one of them so the names differ after lowercasing the first "
                    f"letter and prefixing keywords.",
                    filename=args.file, line=int(_f327.get("line") or 0),
                    stage="ir-semantic", code="PYCSL-R327-IDENT-COLLISION")
            _seen327[_w327] = _nm327

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
    # ROUTE #276 — opt-in drop of the LATIN1-STR assumption (read by the `ord`/`chr`
    # lowering in `module6_whyml/expressions.py::_call_named_builtins`).
    transpiler.strict_latin1 = bool(getattr(args, "strict_latin1", False))
    # ROUTE #298 — opt-in drop of the HVAL-STR-KEYS assumption (read by the nested-map key
    # views in `module6_whyml/stmt_control_flow.py`: `.items()` keys and the bare-loop
    # `HMap` arm).
    transpiler.strict_hval_keys = bool(getattr(args, "strict_hval_keys", False))
    # ROUTE #304 — the pre-resolution class bases (read by `_emit_function_block`'s
    # own-raise coverage test; a class absent from it is covered, fail-closed).
    transpiler.class_bases_r304 = _r304_class_bases
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
        # (#49) ROUTE #305 — A USER EXCEPTION CLASS NAMED LIKE A BUILTIN IS THE BUILTIN.
        # Handler matching (`exception_model.handler_catches`) reads the builtin hierarchy by
        # NAME and the WhyML exception tag is the bare name, so a user `class KeyError(Exception)`
        # shares the builtin's tag AND its bases: MEASURED (gen #37), raised under `except
        # LookupError` it was "caught" (`no_exception \all` + `\result == 1` PROVED, CPython
        # escapes); a user `class LookupError` "caught" the builtin KeyError; the IMPLICIT
        # KeyError of `d[5]` was "caught" by `except KeyError` naming the user class. Refused:
        # any binding — in the main file or a dependency module it imports — of a name the
        # exception model keys on (`EXCEPTION_BASES`, `KNOWN_EXCEPTIONS`, the OSError aliases):
        # a `class` statement at any depth, and a def / import binding / assignment target /
        # parameter / `except ... as` name in a module or function scope (a class-body binding
        # is an attribute, not the name). `from builtins import KeyError` rebinds the builtin
        # itself and is accepted. CENSUS: 0 such bindings in pycsl-reference (beyond 1375,
        # already refused by #131), python-reference, the mirror and the live tree; pycsl_lib
        # `re/__init__.py` binds `error = PatternError` (not a dependency of any corpus file).
        from exception_model import (EXCEPTION_BASES as _eb305, KNOWN_EXCEPTIONS as _ke305)
        _names305 = set(_eb305) | set(_ke305) | {"EnvironmentError", "IOError"}
        _st305 = [(_x305, False) for _x305 in _tall175.body]
        while _st305:
            _y305, _incls305 = _st305.pop()
            _bd305 = []
            if isinstance(_y305, _ast175.ClassDef):
                _bd305 = [("class", _y305.name)]
            elif _incls305:
                _bd305 = []
            elif isinstance(_y305, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                _bd305 = [("def", _y305.name)]
            elif isinstance(_y305, _ast175.Import):
                _bd305 = [("import", _a305.asname or _a305.name.split(".")[0]) for _a305 in _y305.names]
            elif isinstance(_y305, _ast175.ImportFrom):
                _bd305 = [("import", _a305.asname or _a305.name) for _a305 in _y305.names
                          if _a305.name != "*"
                          and not (_y305.module in ("builtins", "__builtin__") and not _y305.level
                                   and (_a305.asname or _a305.name) == _a305.name)]
            elif isinstance(_y305, _ast175.Name) and isinstance(_y305.ctx, (_ast175.Store, _ast175.Del)):
                _bd305 = [("assignment", _y305.id)]
            elif isinstance(_y305, _ast175.arg):
                _bd305 = [("parameter", _y305.arg)]
            elif isinstance(_y305, _ast175.ExceptHandler) and isinstance(_y305.name, str):
                _bd305 = [("except-as", _y305.name)]
            for _k305, _n305 in _bd305:
                if _n305 in _names305:
                    from errors import PyCSLSemanticError as _PyCSLSemErr305
                    raise _PyCSLSemErr305(
                        f"a {_k305} at line {getattr(_y305, 'lineno', 0)} (of this file or a module it imports) binds `{_n305}`, a name "
                        f"the exception model keys on (ROUTE #305): handler matching and the "
                        f"WhyML exception tag read the BUILTIN `{_n305}` (its hierarchy, its "
                        f"implicit raises) by name, so a user definition under that name would be "
                        f"conflated with the builtin and a handler / `no_exception` claim proved "
                        f"of the wrong class. Give the class (or binding) its own name.",
                        stage="whyml-emit", code="PYCSL-R305-BUILTIN-EXCEPTION-NAME-SHADOWED")
            if isinstance(_y305, _ast175.ClassDef):
                _st305.extend((_c305, True) for _c305 in _y305.body)
                _st305.extend((_c305, _incls305) for _c305 in
                              list(_y305.bases) + list(_y305.keywords) + list(_y305.decorator_list))
            elif isinstance(_y305, (_ast175.FunctionDef, _ast175.AsyncFunctionDef, _ast175.Lambda)):
                _st305.extend((_c305, False) for _c305 in _ast175.iter_child_nodes(_y305))
            else:
                _st305.extend((_c305, _incls305) for _c305 in _ast175.iter_child_nodes(_y305))
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
    # (#49) ROUTE #315 — A CONSTRUCTOR'S BODY IS NEVER EMITTED, SO ITS EFFECTS ON ANYTHING BUT
    # `self` AND ITS CALLEES' PRECONDITIONS ARE NOT IN THE PROOF. `K(xs)` lowers to a record
    # literal built from `__init__`'s recognized `self.<f> = ...` stores (routes #79/#83/#150
    # make the rest UNKNOWN); every other effect of the body is dropped. MEASURED (gen #37):
    # `a[0] += 1` in `__init__`, `self.n = inc(a)` (`inc` assigns `a[0]`), the same call in a
    # list/dict/slice/`sorted` initialiser, in a `print`, in an `if` test, an explicit
    # `#@ assigns a[0]` contract, `self.xs = a; self.xs[0] = 5`, and a user exception `E(xs)`
    # whose `__init__` bumps `xs[0]` — each PROVED the caller's `\result == 0` (CPython 1);
    # `self.n = first(a)` (`requires len(a) >= 1`) under `K([])` PROVED `\result == 1`
    # (CPython IndexError). FAIL-CLOSED: a class's constructor (its own `__init__` /
    # `__post_init__`, else the nearest base's) is MODELLED only when its body is a field
    # initialiser — stores to `self.<f>` or to a local name, `if`/`for`/`match`/`raise`/
    # `return`/`pass` (already modelled by routes #83/#150/#152/#179), calls only to total
    # builtins, builtin exceptions, `setattr(self, ...)`, a `super().__init__(...)` whose bases
    # are modelled, and constructors of modelled classes; no subscript READ (a slice is total)
    # or STORE, no division/shift by a non-literal, no `while`/`try`/`with`/`assert`/`global`/`del` of a
    # non-`self` target. A non-trusted function of the main file (or a `#@ fresh_globals`
    # module body) that constructs any other class is refused.
    if _t175 is not None:
        import builtins as _bi315
        _tot315 = {"len", "isinstance", "issubclass", "bool", "list", "set", "dict", "tuple",
                   "frozenset", "sorted", "reversed", "str", "repr", "range", "sum", "any",
                   "all", "abs", "bytearray", "bytes", "object", "type", "zip", "enumerate",
                   "id", "callable", "super"}
        _cdefs315 = {}
        for _c315 in _ast175.walk(_tall175):
            if isinstance(_c315, _ast175.ClassDef):
                _cdefs315.setdefault(_c315.name, []).append(_c315)
        # per class: the reason its constructor is NOT a field initialiser ("" = modelled),
        # and the user classes it depends on (constructed in its body / its bases)
        _why315 = {}
        _dep315 = {}
        for _cn315, _cl315 in _cdefs315.items():
            _why315[_cn315] = ""
            _dep315[_cn315] = set()
            for _c315 in _cl315:
                _bn315 = [(_b.id if isinstance(_b, _ast175.Name) else _b.attr)
                          for _b in _c315.bases if isinstance(_b, (_ast175.Name, _ast175.Attribute))]
                _hooks315 = [_m for _m in _c315.body
                             if isinstance(_m, (_ast175.FunctionDef, _ast175.AsyncFunctionDef))
                             and _m.name in ("__init__", "__post_init__")]
                if not any(_m.name == "__init__" for _m in _hooks315):
                    # no own `__init__`: the inherited one runs (a dataclass's synthesized one
                    # is a pure field initialiser; its `__post_init__` is checked below)
                    _dep315[_cn315] |= {_b for _b in _bn315 if _b in _cdefs315 and _b != _cn315}
                for _m315 in _hooks315:
                    if isinstance(_m315, _ast175.AsyncFunctionDef):
                        _why315[_cn315] = _why315[_cn315] or "an `async` constructor"
                        continue
                    _st315 = list(_m315.body)
                    while _st315 and not _why315[_cn315]:
                        _s315 = _st315.pop()
                        _ex315 = []
                        _tg315 = []
                        if isinstance(_s315, (_ast175.Pass, _ast175.Break, _ast175.Continue)):
                            pass
                        elif isinstance(_s315, _ast175.Expr):
                            _ex315.append(_s315.value)
                        elif isinstance(_s315, _ast175.Assign):
                            _tg315.extend(_s315.targets)
                            _ex315.append(_s315.value)
                        elif isinstance(_s315, _ast175.AnnAssign):
                            _tg315.append(_s315.target)
                            if _s315.value is not None:
                                _ex315.append(_s315.value)
                        elif isinstance(_s315, _ast175.AugAssign):
                            _tg315.append(_s315.target)
                            _ex315.append(_s315.value)
                            # `xs += [v]` / `s |= {v}` / `xs *= 2` mutate the target IN PLACE,
                            # and the target may alias an argument: only `+=`/`-=` of a number
                            if not (isinstance(_s315.op, (_ast175.Add, _ast175.Sub))
                                    and isinstance(_s315.value, _ast175.Constant)
                                    and type(_s315.value.value) in (int, float)):
                                _why315[_cn315] = (f"the augmented store `{_ast175.unparse(_s315)}`"
                                                   f" (line {_s315.lineno}), which may mutate "
                                                   f"an argument in place")
                                break
                        elif isinstance(_s315, _ast175.Delete):
                            _tg315.extend(_s315.targets)
                        elif isinstance(_s315, _ast175.If):
                            _ex315.append(_s315.test)
                            _st315.extend(_s315.body + _s315.orelse)
                        elif isinstance(_s315, _ast175.For):
                            _tg315.append(_s315.target)
                            _ex315.append(_s315.iter)
                            _st315.extend(_s315.body + _s315.orelse)
                        elif isinstance(_s315, _ast175.Match):
                            _ex315.append(_s315.subject)
                            for _k315 in _s315.cases:
                                if _k315.guard is not None:
                                    _ex315.append(_k315.guard)
                                _st315.extend(_k315.body)
                        elif isinstance(_s315, _ast175.Raise):
                            _ex315.extend(_x for _x in (_s315.exc, _s315.cause) if _x is not None)
                        elif isinstance(_s315, _ast175.Return):
                            if _s315.value is not None:
                                _ex315.append(_s315.value)
                        else:
                            _why315[_cn315] = (f"a `{type(_s315).__name__}` statement "
                                               f"(line {_s315.lineno})")
                            break
                        _tq315 = list(_tg315)
                        while _tq315 and not _why315[_cn315]:
                            _t315 = _tq315.pop()
                            if isinstance(_t315, (_ast175.Tuple, _ast175.List)):
                                _tq315.extend(_t315.elts)
                            elif isinstance(_t315, _ast175.Starred):
                                _tq315.append(_t315.value)
                            elif isinstance(_t315, _ast175.Name):
                                pass
                            elif (isinstance(_t315, _ast175.Attribute)
                                  and isinstance(_t315.value, _ast175.Name)
                                  and _t315.value.id == "self"):
                                pass
                            else:
                                _why315[_cn315] = (f"a store to `{_ast175.unparse(_t315)}` "
                                                   f"(line {_t315.lineno}), which is not a "
                                                   f"field of `self` and may alias an argument")
                        for _e315 in _ex315:
                            if _why315[_cn315]:
                                break
                            for _q315 in _ast175.walk(_e315):
                                if isinstance(_q315, (_ast175.Await, _ast175.Yield,
                                                      _ast175.YieldFrom)):
                                    _why315[_cn315] = f"`{type(_q315).__name__}`"
                                elif (isinstance(_q315, _ast175.Subscript)
                                      and isinstance(_q315.ctx, _ast175.Load)
                                      and not isinstance(_q315.slice, _ast175.Slice)):
                                    _why315[_cn315] = (f"the subscript `{_ast175.unparse(_q315)}`"
                                                       f" (line {_q315.lineno}), whose "
                                                       f"IndexError/KeyError is not modelled")
                                elif (isinstance(_q315, _ast175.BinOp)
                                      and isinstance(_q315.op, (_ast175.Div, _ast175.FloorDiv,
                                                                _ast175.Mod, _ast175.LShift,
                                                                _ast175.RShift))
                                      and not (isinstance(_q315.right, _ast175.Constant)
                                               and type(_q315.right.value) is int
                                               and _q315.right.value > 0)
                                      and not (isinstance(_q315.op, _ast175.Mod)
                                               and isinstance(_q315.left, _ast175.Constant)
                                               and isinstance(_q315.left.value, str))):
                                    _why315[_cn315] = (f"`{_ast175.unparse(_q315)}` (line "
                                                       f"{_q315.lineno}), whose raise is not "
                                                       f"modelled")
                                elif isinstance(_q315, _ast175.Call):
                                    _f315 = _q315.func
                                    _fn315 = (_f315.id if isinstance(_f315, _ast175.Name)
                                              else _f315.attr if isinstance(_f315, _ast175.Attribute)
                                              else None)
                                    _bx315 = getattr(_bi315, _fn315 or "", None)
                                    if (isinstance(_f315, _ast175.Name) and _fn315 in _cdefs315):
                                        _dep315[_cn315].add(_fn315)
                                    elif (isinstance(_f315, _ast175.Name) and _fn315 in _tot315):
                                        pass
                                    elif (isinstance(_f315, _ast175.Name)
                                          and isinstance(_bx315, type)
                                          and issubclass(_bx315, BaseException)):
                                        pass
                                    elif (isinstance(_f315, _ast175.Name) and _fn315 == "setattr"
                                          and _q315.args and isinstance(_q315.args[0], _ast175.Name)
                                          and _q315.args[0].id == "self"):
                                        pass
                                    elif (isinstance(_f315, _ast175.Attribute)
                                          and _f315.attr in ("__init__", "__post_init__")
                                          and isinstance(_f315.value, _ast175.Call)
                                          and isinstance(_f315.value.func, _ast175.Name)
                                          and _f315.value.func.id == "super"):
                                        _dep315[_cn315] |= {_b for _b in _bn315
                                                            if _b in _cdefs315 and _b != _cn315}
                                    else:
                                        _why315[_cn315] = (f"the call `{_ast175.unparse(_f315)}"
                                                           f"(...)` (line {_q315.lineno}), whose "
                                                           f"effects, precondition and raises "
                                                           f"are not modelled")
                                if _why315[_cn315]:
                                    break
        # a class depending on an unmodelled one is unmodelled too
        _chg315 = True
        while _chg315:
            _chg315 = False
            for _cn315 in sorted(_why315):
                if _why315[_cn315]:
                    continue
                for _d315 in sorted(_dep315[_cn315]):
                    if _why315.get(_d315):
                        _why315[_cn315] = f"its use of `{_d315}`, whose constructor is unmodelled"
                        _chg315 = True
                        break
        if any(_why315.values()):
            _trusted315 = {str(_f.get("name", ""))
                           for _f in ir_data.get("functions", [])
                           if _f.get("trusted") or _f.get("abstract") or _f.get("trusted_parent")}
            _owner315 = {}
            for _k315 in _ast175.walk(_tall175):
                if isinstance(_k315, _ast175.ClassDef):
                    for _m315 in _k315.body:
                        if isinstance(_m315, (_ast175.FunctionDef, _ast175.AsyncFunctionDef)):
                            _owner315[id(_m315)] = _k315.name
            _sites315 = []
            for _d315 in _ast175.walk(_t175):
                if (not isinstance(_d315, (_ast175.FunctionDef, _ast175.AsyncFunctionDef))
                        or _d315.name in ("__init__", "__post_init__", "__new__")
                        or (f"{_owner315[id(_d315)].lower()}__{_d315.name}"
                            if id(_d315) in _owner315 else _d315.name) in _trusted315):
                    continue
                _sites315.append((_d315.name, _d315))
            if any(_f.get("fresh_globals") for _f in (ir_data.get("functions", []) or [])):
                _sites315.append(("<module body>", _ast175.Module(
                    body=[_s for _s in _t175.body if not isinstance(
                        _s, (_ast175.FunctionDef, _ast175.AsyncFunctionDef, _ast175.ClassDef))],
                    type_ignores=[])))
            for _sn315, _d315 in _sites315:
                for _q315 in _ast175.walk(_d315):
                    if not isinstance(_q315, _ast175.Call):
                        continue
                    _fn315 = (_q315.func.id if isinstance(_q315.func, _ast175.Name)
                              else _q315.func.attr if isinstance(_q315.func, _ast175.Attribute)
                              else None)
                    if _fn315 and _why315.get(_fn315):
                        from errors import PyCSLSemanticError as _PyCSLSemErr315
                        raise _PyCSLSemErr315(
                            f"{_sn315!r} constructs `{_fn315}` (line {_q315.lineno}), whose "
                            f"constructor is not a field initialiser: {_why315[_fn315]} "
                            f"(ROUTE #315). A construction is lowered to a record literal of "
                            f"the `self.<f>` stores and the rest of the body is never emitted, "
                            f"so its effects on the arguments, its callees' preconditions and "
                            f"its raises would be missing from the proof. Move that work out "
                            f"of the constructor (into a function called before or after it).",
                            stage="whyml-emit", code="PYCSL-R315-UNMODELLED-CONSTRUCTOR")
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
    # ROUTE #340 — A BARE-NAME DEFAULT IS READ AT CALL TIME BY THE MODEL. CPython binds
    # a nested def's / lambda's default VALUE once, when the def/lambda runs; the lifted
    # function is called as `(g !x)`, i.e. with the name's value at the CALL. MEASURED at
    # 5e517ffc (witnesses-r340/): `x = 1; def g(y=x); x = 2; return g()` PROVED
    # `\result == 2` (CPython 1); `x += 1` and a rebound parameter likewise; a rebound
    # `i` turned a `1 // y` with `y = 0` into a proved no_exception. RULE: a bare-name
    # default is admitted only when the name can hold ONE value for the whole run of the
    # enclosing lowered function — it is bound nowhere in that function (any nested
    # scope included: assignment / for / with / walrus / except / import / def / class /
    # match targets, `del`) and is declared `global`/`nonlocal` nowhere in the module, so
    # the def-time and call-time reads coincide (a parameter of the function, a module
    # name). Every other bare-name default is refused with the same code. BLAST RADIUS,
    # measured before landing (CPython-`ast` prototype): the only bare-name defaults of
    # a nested def in pycsl-reference / python-reference / the self-annotate mirror /
    # pycsl_lib are 2967's never-rebound parameter `x` (admitted) and ones already
    # refused for a non-literal default.
    _gn340 = {_g for _x in _A273.walk(unified_ast)
              if isinstance(_x, (_A273.Global, _A273.Nonlocal)) for _g in _x.names}
    for _F273 in _low273:
        _bn340 = set(_gn340)
        for _x340 in _A273.walk(_F273):
            if isinstance(_x340, _A273.Name) and not isinstance(_x340.ctx, _A273.Load):
                _bn340.add(_x340.id)
            elif isinstance(_x340, _FN273 + (_A273.ClassDef,)) and _x340 is not _F273:
                _bn340.add(_x340.name)
            elif isinstance(_x340, (_A273.Import, _A273.ImportFrom)):
                _bn340.update((_al.asname or _al.name).split(".")[0] for _al in _x340.names)
            for _y340 in ("name", "rest"):
                if (isinstance(getattr(_x340, _y340, None), str) and isinstance(
                        _x340, (_A273.ExceptHandler, _A273.MatchAs, _A273.MatchStar,
                                _A273.MatchMapping))):
                    _bn340.add(getattr(_x340, _y340))
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
                        if isinstance(_x273, _A273.Constant):
                            continue
                        if isinstance(_x273, _A273.Name) and not (
                                _x273.id in _bn340 and isinstance(
                                    _N273, _FN273 + (_A273.Lambda,))):
                            continue
                        if isinstance(_x273, _A273.Name):
                            _ok273 = False
                            _why273 = ("bare-name default `" + _x273.id + "`, a name "
                                       "REBOUND in the enclosing function (or declared "
                                       "global/nonlocal) — Python binds the default's "
                                       "VALUE at def time, the model reads the name at "
                                       "call time (route #340) — in `"
                                       + _A273.unparse(_e273)[:60] + "`")
                            break
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
                if not _ok273 and not _why273:
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
    # (#49) ROUTES #350 / #351 — SHARED MODULE-LEVEL ALIAS / CONSTANT MAP. A module name
    # bound EXACTLY ONCE at module level (`Num = int`, `K = 7`, `X: TypeAlias = ...`,
    # `type X = ...`) is followed by both rules below; anything rebound is not.
    # Both rules read the SOURCE as written: Module 5 (already run) rewrites annotations in
    # place (route #336: `Sequence` -> `List`, module aliases resolved), so a fresh parse of
    # `source_code` is walked, restricted to the defs `_low273` lowers (by line and name).
    _lw350 = {(getattr(_n, "lineno", 0), _n.name) for _F in _low273
              for _n in _A273.walk(_F) if isinstance(_n, _FN273)}
    try:
        _src350 = _A273.parse(source_code)
    except Exception:
        _src350 = unified_ast
    _low350 = []
    _st350 = [_src350]
    while _st350:
        _n350 = _st350.pop()
        if isinstance(_n350, _FN273):
            if (getattr(_n350, "lineno", 0), _n350.name) in _lw350:
                _low350.append(_n350)
            continue
        _st350.extend(_A273.iter_child_nodes(_n350))
    _TA350 = getattr(_A273, "TypeAlias", None)
    _nb350: Dict[str, int] = {}
    _mv350: Dict[str, Any] = {}
    for _s350 in getattr(_src350, "body", None) or []:
        _k350, _v350 = None, None
        if isinstance(_s350, _A273.Assign):
            for _t350 in _s350.targets:
                for _w350 in _A273.walk(_t350):
                    if isinstance(_w350, _A273.Name):
                        _nb350[_w350.id] = _nb350.get(_w350.id, 0) + 1
            if len(_s350.targets) == 1 and isinstance(_s350.targets[0], _A273.Name):
                _k350, _v350 = _s350.targets[0].id, _s350.value
        elif isinstance(_s350, _A273.AnnAssign) and isinstance(_s350.target, _A273.Name):
            _nb350[_s350.target.id] = _nb350.get(_s350.target.id, 0) + 1
            _k350, _v350 = _s350.target.id, _s350.value
        elif _TA350 is not None and isinstance(_s350, _TA350) and isinstance(
                getattr(_s350, "name", None), _A273.Name):
            _nb350[_s350.name.id] = _nb350.get(_s350.name.id, 0) + 1
            _k350, _v350 = _s350.name.id, _s350.value
        elif isinstance(_s350, _FN273 + (_A273.ClassDef,)):
            _nb350[_s350.name] = _nb350.get(_s350.name, 0) + 1
        elif isinstance(_s350, (_A273.Import, _A273.ImportFrom)):
            for _al350 in _s350.names:
                _q350 = (_al350.asname or _al350.name).split(".")[0]
                _nb350[_q350] = _nb350.get(_q350, 0) + 1
        if _k350 is not None and _v350 is not None:
            _mv350[_k350] = _v350
    for _x350 in _A273.walk(_src350):
        if isinstance(_x350, (_A273.Global, _A273.Nonlocal)):
            for _g350 in _x350.names:
                _nb350[_g350] = 2   # rebindable from a function: not a constant
        elif isinstance(_x350, _A273.AugAssign) and isinstance(_x350.target, _A273.Name):
            _nb350[_x350.target.id] = 2
    _mv350 = {_k: _v for _k, _v in _mv350.items() if _nb350.get(_k) == 1}
    _cls350 = {_c.name for _c in _A273.walk(_src350) if isinstance(_c, _A273.ClassDef)}
    _tv350 = {_k for _k, _v in _mv350.items()
              if isinstance(_v, _A273.Call) and (
                  getattr(_v.func, "id", None) or getattr(_v.func, "attr", None))
              in ("TypeVar", "ParamSpec", "TypeVarTuple", "NewType")}
    # (#49) ROUTE #350 — A PARAMETER DEFAULT THAT CONTRADICTS ITS ANNOTATION. The body of a
    # lowered function is verified with every parameter of its annotated type, but CPython
    # binds an OMITTED argument to the default VALUE, whatever its type. MEASURED at
    # 78c92b39 / 5c3b3413 (witnesses-r350/): `def f(x: int = 0.5)` PROVED `\result == 0`
    # for `x % 1` (CPython `f()` = 0.5); `def f(s: str = None)` PROVED `len(s)` under
    # `no_exception \all` (CPython TypeError); a method / kw-only / nested-def / alias
    # (`Num = int`) / module-constant (`K = 0.5`) / `Literal[1, 2] = 3` / `str = False`
    # default likewise. RULE (fail-closed, AST-level, every def inside a LOWERED function
    # tree — module-level functions, methods, nested defs; a lambda has no annotation):
    # each annotated parameter's default must be of the annotation's KIND. The annotation is
    # split into ARMS (through module aliases, `Optional`, `Union`, `|`, `Annotated`,
    # string forward references); the default is admitted when ONE arm admits it:
    #   `None` arm / `Any` / `object` / a TypeVar  — `None` admitted only here (or any);
    #   int  <- int / bool literal;  float <- int / float / bool;  complex <- numeric;
    #   bool <- bool;  str <- str;  bytes <- bytes;  `Literal[...]` <- one of its values;
    #   List/list/MutableSequence <- a list display;  tuple/Tuple <- a tuple display;
    #   Sequence/Collection/Iterable/Reversible/Container <- list/tuple display, str/bytes;
    #   Dict/dict/Mapping/MutableMapping/... <- a dict display;  Set/set/FrozenSet/... <- a
    #   set display;  a container / class / other arm <- any NON-literal expression (a
    #   constructor call, a name), never `None` and never a scalar literal for a container
    #   or a class of this file.
    # A signed numeric literal is a literal; a bare-name default resolves to a once-bound
    # module constant, else to the enclosing function's parameter of the SAME annotation
    # (route #340 already guarantees it is never rebound); any other NON-literal default of
    # a scalar / Literal arm (a call, an attribute, arithmetic) is REFUSED: its value is not
    # known to be of the kind (an obligation at the default would need the def-time state).
    # Display elements are checked against the element type when exactly one arm admits the
    # display. `\trusted` / `\abstract` defs are outside (their contract is assumed, the
    # call-site fill of an omitted `None` is part of that trust). BLAST RADIUS, measured
    # before landing (CPython-`ast` prototype over pycsl-reference, python-reference, the
    # self-annotate mirror and pycsl_lib): pycsl-reference 0698 (`sep: str = None`, the
    # call-site `""` fill — the model of the very defect) and mirror
    # `Module2_Parser.expect_name(val: str = None)` (live + mirror default now `""`, every
    # caller passes a literal name or nothing; `Optional[str]` does not type-check there); 23 mirror
    # and 1 pycsl_lib `int`/`str = None` defaults sit on `\trusted` stubs.
    # INLINE (check-mirror-coverage); `_run_pipeline`'s mirror twin is `\trusted`.
    _bad350: List[Any] = []
    for _F350 in _low350:
        _pa350: Dict[str, Set[str]] = {}
        for _x350 in _A273.walk(_F350):
            if isinstance(_x350, _FN273):
                _xa350 = _x350.args
                for _p350 in (list(getattr(_xa350, "posonlyargs", None) or [])
                              + list(_xa350.args or []) + list(_xa350.kwonlyargs or [])):
                    _pa350.setdefault(_p350.arg, set()).add(
                        _A273.unparse(_p350.annotation) if _p350.annotation is not None
                        else "?")
        for _N350 in _A273.walk(_F350):
            if not isinstance(_N350, _FN273) or _bad350:
                continue
            _na350 = _N350.args
            _po350 = list(getattr(_na350, "posonlyargs", None) or []) + list(_na350.args or [])
            _ob350: List[Any] = []
            for _p350, _d350 in (list(zip(_po350[len(_po350) - len(_na350.defaults or []):],
                                          _na350.defaults or []))
                                 + list(zip(_na350.kwonlyargs or [], _na350.kw_defaults or []))):
                if _d350 is not None and _p350.annotation is not None:
                    _ob350.append((_p350.annotation, _d350, _p350.arg, _d350))
            _guard350 = 0
            while _ob350 and not _bad350 and _guard350 < 512:
                _guard350 += 1
                _an350, _dv350, _pn350, _top350 = _ob350.pop()
                # -- the default, with a bare name resolved (module constant / outer parameter)
                _rs350 = _dv350
                _outer350 = None
                if isinstance(_rs350, _A273.Name) and _rs350.id not in ("None", "True", "False"):
                    if _rs350.id in _pa350:
                        _outer350 = _pa350[_rs350.id]
                    elif _rs350.id in _mv350:
                        _rs350 = _mv350[_rs350.id]
                _cv350: Any = ("?",)
                if isinstance(_rs350, _A273.Constant):
                    _cv350 = _rs350.value
                elif (isinstance(_rs350, _A273.UnaryOp)
                        and isinstance(_rs350.op, (_A273.USub, _A273.UAdd))
                        and isinstance(_rs350.operand, _A273.Constant)
                        and type(_rs350.operand.value) in (int, float, complex, bool)):
                    _cv350 = _rs350.operand.value
                elif isinstance(_rs350, _A273.Name) and _rs350.id in ("None", "True", "False"):
                    _cv350 = {"None": None, "True": True, "False": False}[_rs350.id]
                _lit350 = not (isinstance(_cv350, tuple) and _cv350 == ("?",))
                _disp350 = (_A273.List if isinstance(_rs350, _A273.List)
                            else _A273.Tuple if isinstance(_rs350, _A273.Tuple)
                            else _A273.Dict if isinstance(_rs350, _A273.Dict)
                            else _A273.Set if isinstance(_rs350, _A273.Set) else None)
                # -- the annotation's arms
                _arms350: List[Any] = []
                _wk350: List[Any] = [_an350]
                _g2350 = 0
                while _wk350 and _g2350 < 64:
                    _g2350 += 1
                    _a350 = _wk350.pop()
                    if isinstance(_a350, _A273.Constant) and isinstance(_a350.value, str):
                        try:
                            _wk350.append(_A273.parse(_a350.value, mode="eval").body)
                        except Exception:
                            _arms350.append(("Any", None))
                        continue
                    if isinstance(_a350, _A273.Constant) and _a350.value is None:
                        _arms350.append(("None", None))
                        continue
                    if (isinstance(_a350, _A273.BinOp)
                            and isinstance(_a350.op, _A273.BitOr)):
                        _wk350 += [_a350.left, _a350.right]
                        continue
                    if (isinstance(_a350, _A273.Name) and _a350.id in _mv350
                            and _a350.id not in _cls350 and _a350.id not in _tv350):
                        _wk350.append(_mv350[_a350.id])
                        continue
                    _hd350 = (_a350.id if isinstance(_a350, _A273.Name)
                              else _a350.attr if isinstance(_a350, _A273.Attribute)
                              else "")
                    _sa350: Any = None
                    if isinstance(_a350, _A273.Subscript):
                        _v2350 = _a350.value
                        _hd350 = (_v2350.id if isinstance(_v2350, _A273.Name)
                                  else _v2350.attr if isinstance(_v2350, _A273.Attribute)
                                  else "")
                        _sl350 = _a350.slice
                        if type(_sl350).__name__ == "Index":
                            _sl350 = _sl350.value
                        _sa350 = (list(_sl350.elts) if isinstance(_sl350, _A273.Tuple)
                                  else [_sl350])
                        if _hd350 == "Optional":
                            _wk350 += _sa350[:1]
                            _arms350.append(("None", None))
                            continue
                        if _hd350 == "Union":
                            _wk350 += _sa350
                            continue
                        if _hd350 == "Annotated":
                            _wk350 += _sa350[:1]
                            continue
                    if _hd350 in ("None", "NoneType"):
                        _arms350.append(("None", None))
                    elif _hd350 in ("Any", "object") or _hd350 in _tv350 or not _hd350:
                        _arms350.append(("Any", None))
                    else:
                        _arms350.append((_hd350, _sa350))
                # -- which arms admit the default (shallow)
                _ok350: List[Any] = []
                for _hd350, _sa350 in _arms350:
                    _adm350 = False
                    if _hd350 == "Any":
                        _adm350 = True
                    elif _cv350 is None and _lit350:
                        _adm350 = _hd350 == "None"
                    elif _hd350 == "None":
                        _adm350 = False
                    elif _hd350 in ("int", "float", "complex", "bool", "str", "bytes"):
                        _ty350 = {"int": (int, bool), "float": (int, float, bool),
                                  "complex": (int, float, complex, bool), "bool": (bool,),
                                  "str": (str,), "bytes": (bytes,)}[_hd350]
                        if _lit350:
                            _adm350 = type(_cv350) in _ty350
                        elif _outer350 is not None:
                            _adm350 = all(_o350 == _hd350 or (_hd350 == "int"
                                                                and _o350 == "bool")
                                          for _o350 in _outer350)
                    elif _hd350 == "Literal":
                        _adm350 = _lit350 and any(
                            isinstance(_e350, _A273.Constant) and type(_e350.value) is
                            type(_cv350) and _e350.value == _cv350
                            for _e350 in (_sa350 or [])) or (
                            _lit350 and isinstance(_rs350, _A273.UnaryOp) and any(
                                _A273.unparse(_e350) == _A273.unparse(_rs350)
                                for _e350 in (_sa350 or [])))
                    elif _lit350:
                        # a scalar literal for a container / a class of this file is never
                        # of its kind; an unknown (imported, erased) head keeps it
                        _adm350 = not (_hd350 in _cls350 or _hd350 in (
                            "List", "list", "MutableSequence", "Tuple", "tuple", "Dict",
                            "dict", "Mapping", "MutableMapping", "DefaultDict",
                            "defaultdict", "OrderedDict", "Counter", "Set", "set",
                            "MutableSet", "FrozenSet", "frozenset", "AbstractSet",
                            "Callable", "Type", "type")) or (
                            isinstance(_cv350, (str, bytes)) and _hd350 in (
                                "Sequence", "Collection", "Iterable", "Reversible",
                                "Container"))
                        if _hd350 in ("Sequence", "Collection", "Iterable", "Reversible",
                                      "Container") and not isinstance(_cv350, (str, bytes)):
                            _adm350 = False
                    elif _disp350 is not None:
                        _adm350 = (
                            (_hd350 in ("List", "list", "MutableSequence")
                             and _disp350 is _A273.List)
                            or (_hd350 in ("Tuple", "tuple") and _disp350 is _A273.Tuple)
                            or (_hd350 in ("Sequence", "Collection", "Iterable",
                                           "Reversible", "Container")
                                and _disp350 in (_A273.List, _A273.Tuple, _A273.Set,
                                                 _A273.Dict))
                            or (_hd350 in ("Dict", "dict", "Mapping", "MutableMapping",
                                           "DefaultDict", "defaultdict", "OrderedDict",
                                           "Counter") and _disp350 is _A273.Dict)
                            or (_hd350 in ("Set", "set", "MutableSet", "FrozenSet",
                                           "frozenset", "AbstractSet")
                                and _disp350 is _A273.Set)
                            or (_hd350 not in _cls350 and _hd350 not in (
                                "int", "float", "complex", "bool", "str", "bytes",
                                "List", "list", "MutableSequence", "Tuple", "tuple",
                                "Dict", "dict", "Mapping", "MutableMapping", "DefaultDict",
                                "defaultdict", "OrderedDict", "Counter", "Set", "set",
                                "MutableSet", "FrozenSet", "frozenset", "AbstractSet",
                                "Callable", "Type", "type", "Literal")))
                    else:
                        # a non-literal, non-display default (a call, a name, an
                        # attribute) for a container / class / other arm
                        _adm350 = True
                    if _adm350:
                        _ok350.append((_hd350, _sa350))
                if not _ok350:
                    _bad350.append((_N350.name, getattr(_N350, "lineno", 0), _pn350,
                                    _A273.unparse(_an350)[:60], _A273.unparse(_top350)[:60]))
                    break
                # -- element obligations, when exactly one arm admits a display
                if len(_ok350) == 1 and _disp350 is not None and _ok350[0][1]:
                    _hd350, _sa350 = _ok350[0]
                    if _disp350 is _A273.Dict and len(_sa350) == 2:
                        for _ke350, _ve350 in zip(_rs350.keys, _rs350.values):
                            if _ke350 is not None:
                                _ob350.append((_sa350[0], _ke350, _pn350, _top350))
                                _ob350.append((_sa350[1], _ve350, _pn350, _top350))
                    elif _disp350 is not _A273.Dict:
                        _el350 = [_e for _e in _rs350.elts
                                  if not isinstance(_e, _A273.Starred)]
                        if _hd350 in ("Tuple", "tuple") and not (
                                len(_sa350) == 2 and isinstance(_sa350[1], _A273.Constant)
                                and _sa350[1].value is ...):
                            if len(_sa350) == len(_rs350.elts) and len(_el350) == len(
                                    _rs350.elts):
                                _ob350 += [(_t, _e, _pn350, _top350)
                                           for _t, _e in zip(_sa350, _el350)]
                            elif not (len(_sa350) == 1 and isinstance(_sa350[0], _A273.Tuple)):
                                _bad350.append((_N350.name, getattr(_N350, "lineno", 0),
                                                _pn350, _A273.unparse(_an350)[:60],
                                                _A273.unparse(_top350)[:60]))
                                break
                        elif len(_sa350) >= 1:
                            _ob350 += [(_sa350[0], _e, _pn350, _top350) for _e in _el350]
    if _bad350:
        from errors import PyCSLSemanticError as _PyCSLSemErr350
        raise _PyCSLSemErr350(
            f"'{_bad350[0][0]}' (line {_bad350[0][1]}) gives the parameter "
            f"'{_bad350[0][2]}: {_bad350[0][3]}' the default `{_bad350[0][4]}`, which is not "
            f"of the annotation's kind (route #350). The body is verified with "
            f"'{_bad350[0][2]}' of the annotated type, but Python binds an omitted argument "
            f"to the default VALUE, so the call `{_bad350[0][0]}()` would run the body outside "
            f"what was proved. Use a default of the annotated kind (a literal; `None` only for "
            f"an `Optional[...]` / `... | None` annotation), or widen the annotation.",
            filename=args.file, stage="ir-semantic",
            code="PYCSL-SEM-DEFAULT-ANNOTATION-MISMATCH")
    # (#49) ROUTE #351 — A READ-ONLY VIEW ESCAPES THROUGH A MUTABLE-TYPED SLOT. Route #336
    # reads a `Sequence[T]` / `tuple[T, ...]` / `Mapping[K, V]` parameter as a `List` /
    # `Dict` and refuses a STORE on the parameter itself (PYCSL-R336-READONLY-VIEW-STORE);
    # the view could still LEAVE under a mutable type and be stored into elsewhere.
    # MEASURED at 78c92b39 / 5c3b3413 (witnesses-r351/): `as_list(xs: Sequence[int]) ->
    # List[int]: return xs` PROVED, and a separately verified `poke(ys: List[int])` storing
    # `ys[0] = 5` under `no_exception \all` PROVED too (CPython `poke(as_list((1, 2)))`
    # TypeError); `return xs if c else xs` and a `Mapping` returned as `Dict` likewise.
    # RULE (fail-closed, AST-level, every def / lambda inside a LOWERED function tree): the
    # VIEW names of a def are its read-only-view parameters (through module aliases,
    # `Optional`, `Annotated`) and, to a fixpoint, every name bound by `y = E` / `y := E` /
    # `y: <read-only-view> = E` where E's VALUE may be a view. E's value may be a view when
    # it is a view name, a slice of one, `+` / `*` on one, or a conditional / `and` / `or` /
    # walrus / starred / container-display position holding such an E. REFUSED: (a) a
    # `return E` (a lambda body) whose owner's return annotation is not read-only-view-safe
    # (`Sequence` / `Mapping` / `tuple[T, ...]` / `Iterable` / `Collection` / `Any` /
    # `object` / `None`, through `Optional` / `Union`) or whose E wraps the view in a
    # display; (b) E stored into an attribute / subscript target, or bound to a name
    # annotated otherwise; (c) E passed to a call other than the read-only builtins of
    # route #336's list; (d) a store / `del` / augmented assignment / mutating method call
    # through an ALIAS of a view (the parameter itself is route #336's). The view NAME is
    # syntactic (a nested def's parameter shadowing an outer view name is over-refused).
    # BLAST RADIUS, measured before landing: see the route file (pycsl-reference,
    # python-reference, mirror, pycsl_lib).
    # INLINE (check-mirror-coverage); `_run_pipeline`'s mirror twin is `\trusted`.
    _bad351: List[Any] = []
    _ro351h = ("Sequence", "Mapping")
    _safe351h = ("Sequence", "Mapping", "Iterable", "Collection", "Reversible", "Container",
                 "Iterator", "AbstractSet", "Any", "object", "None", "NoneType")
    _bi351 = ("len", "sum", "min", "max", "sorted", "list", "tuple", "set", "frozenset",
              "dict", "enumerate", "zip", "any", "all", "isinstance", "reversed", "iter",
              "str", "repr", "print", "hash", "id", "type", "bool", "map", "filter")
    for _F351 in _low350:
        if _bad351:
            break
        # -- every def of the tree: read-only-view params; owner map (innermost def/lambda)
        _view351: Set[str] = set()
        _own351: Dict[int, Any] = {}
        for _D351 in _A273.walk(_F351):
            if not isinstance(_D351, _FN273 + (_A273.Lambda,)):
                continue
            for _x351 in _A273.walk(_D351):
                if _x351 is not _D351:
                    _own351[id(_x351)] = _D351
            if isinstance(_D351, _A273.Lambda):
                continue
            _da351 = _D351.args
            for _p351 in (list(getattr(_da351, "posonlyargs", None) or [])
                          + list(_da351.args or []) + list(_da351.kwonlyargs or [])):
                _h351 = _p351.annotation
                for _r351 in range(8):
                    if isinstance(_h351, _A273.Constant) and isinstance(_h351.value, str):
                        try:
                            _h351 = _A273.parse(_h351.value, mode="eval").body
                        except Exception:
                            break
                    elif (isinstance(_h351, _A273.Name) and _h351.id in _mv350
                            and _h351.id not in _cls350):
                        _h351 = _mv350[_h351.id]
                    elif (isinstance(_h351, _A273.Subscript) and (
                            getattr(_h351.value, "id", None)
                            or getattr(_h351.value, "attr", None)) in ("Optional",
                                                                       "Annotated")):
                        _h351 = (_h351.slice.elts[0] if isinstance(_h351.slice, _A273.Tuple)
                                 and _h351.slice.elts else _h351.slice)
                    else:
                        break
                if isinstance(_h351, _A273.Subscript):
                    _hn351 = (getattr(_h351.value, "id", None)
                              or getattr(_h351.value, "attr", None))
                    if (_hn351 in _ro351h or (
                            _hn351 in ("tuple", "Tuple") and isinstance(_h351.slice, _A273.Tuple)
                            and len(_h351.slice.elts) == 2
                            and isinstance(_h351.slice.elts[1], _A273.Constant)
                            and _h351.slice.elts[1].value is ...)):
                        _view351.add(_p351.arg)
        if not _view351:
            continue
        _param351 = set(_view351)
        # -- alias fixpoint. `_vx351(E)`: E's value may be a view (inline worklist, twice)
        for _rd351 in range(8):
            _grew351 = False
            for _x351 in _A273.walk(_F351):
                _tg351: List[Any] = []
                _val351 = None
                if isinstance(_x351, _A273.Assign):
                    _tg351, _val351 = list(_x351.targets), _x351.value
                elif isinstance(_x351, _A273.NamedExpr):
                    _tg351, _val351 = [_x351.target], _x351.value
                elif isinstance(_x351, _A273.AnnAssign) and _x351.value is not None:
                    _tg351, _val351 = [_x351.target], _x351.value
                elif isinstance(_x351, (_A273.For, _A273.AsyncFor)):
                    # `for y in (xs, ys)` binds a view
                    if isinstance(_x351.iter, (_A273.Tuple, _A273.List, _A273.Set)):
                        _tg351, _val351 = [_x351.target], _x351.iter
                if _val351 is None:
                    continue
                _hit351 = False
                _wk351: List[Any] = [_val351]
                while _wk351 and not _hit351:
                    _e351 = _wk351.pop()
                    if isinstance(_e351, _A273.Name):
                        _hit351 = _e351.id in _view351
                    elif isinstance(_e351, _A273.IfExp):
                        _wk351 += [_e351.body, _e351.orelse]
                    elif isinstance(_e351, _A273.BoolOp):
                        _wk351 += list(_e351.values)
                    elif isinstance(_e351, (_A273.NamedExpr, _A273.Starred)):
                        _wk351.append(_e351.value)
                    elif isinstance(_e351, (_A273.Tuple, _A273.List, _A273.Set)):
                        _wk351 += list(_e351.elts)
                    elif isinstance(_e351, _A273.Dict):
                        _wk351 += [_k for _k in _e351.keys if _k is not None] + list(
                            _e351.values)
                    elif isinstance(_e351, _A273.Subscript) and isinstance(
                            _e351.slice, _A273.Slice):
                        _wk351.append(_e351.value)
                    elif isinstance(_e351, _A273.BinOp) and isinstance(
                            _e351.op, (_A273.Add, _A273.Mult)):
                        _wk351 += [_e351.left, _e351.right]
                if not _hit351:
                    continue
                for _t351 in _tg351:
                    for _w351 in _A273.walk(_t351):
                        if (isinstance(_w351, _A273.Name) and _w351.id not in _view351
                                and (not isinstance(_x351, _A273.AnnAssign)
                                     or _w351 is _t351)):
                            _view351.add(_w351.id)
                            _grew351 = True
            if not _grew351:
                break
        # -- the escapes
        for _x351 in _A273.walk(_F351):
            if _bad351:
                break
            _esc351: List[Any] = []    # (expression, why)
            if isinstance(_x351, _A273.Return) and _x351.value is not None:
                _O351 = _own351.get(id(_x351))
                _ra351 = getattr(_O351, "returns", None)
                _safe351 = _ra351 is not None
                _wk351 = [_ra351] if _ra351 is not None else []
                _g351 = 0
                while _wk351 and _safe351 and _g351 < 64:
                    _g351 += 1
                    _a351 = _wk351.pop()
                    if isinstance(_a351, _A273.Constant) and isinstance(_a351.value, str):
                        try:
                            _wk351.append(_A273.parse(_a351.value, mode="eval").body)
                        except Exception:
                            _safe351 = False
                        continue
                    if isinstance(_a351, _A273.Constant) and _a351.value is None:
                        continue
                    if isinstance(_a351, _A273.BinOp) and isinstance(_a351.op, _A273.BitOr):
                        _wk351 += [_a351.left, _a351.right]
                        continue
                    if (isinstance(_a351, _A273.Name) and _a351.id in _mv350
                            and _a351.id not in _cls350):
                        _wk351.append(_mv350[_a351.id])
                        continue
                    _hd351 = (getattr(_a351, "id", None) or getattr(_a351, "attr", None)
                              or getattr(getattr(_a351, "value", None), "id", None)
                              or getattr(getattr(_a351, "value", None), "attr", None))
                    if isinstance(_a351, _A273.Subscript):
                        _hd351 = (getattr(_a351.value, "id", None)
                                  or getattr(_a351.value, "attr", None))
                        _sl351 = _a351.slice
                        _el351 = (list(_sl351.elts) if isinstance(_sl351, _A273.Tuple)
                                  else [_sl351])
                        if _hd351 in ("Optional", "Union"):
                            _wk351 += _el351
                            continue
                        if _hd351 == "Annotated":
                            _wk351 += _el351[:1]
                            continue
                        if _hd351 in ("tuple", "Tuple") and len(_el351) == 2 and isinstance(
                                _el351[1], _A273.Constant) and _el351[1].value is ...:
                            continue
                    if _hd351 not in _safe351h and _hd351 not in _tv350:
                        _safe351 = False
                # a view wrapped in a display (`return (xs, 1)`) is not covered by a
                # view-safe annotation of the whole value
                _wrap351 = any(isinstance(_w351, (_A273.Tuple, _A273.List, _A273.Set,
                                                  _A273.Dict))
                               for _w351 in _A273.walk(_x351.value))
                if not _safe351 or _wrap351:
                    _esc351.append((_x351.value, "returned from '%s' %s" % (
                        getattr(_O351, "name", "lambda"),
                        "annotated `-> %s`" % _A273.unparse(_ra351)[:40]
                        if _ra351 is not None else "with no return annotation")))
            elif isinstance(_x351, _A273.Lambda):
                _esc351.append((_x351.body, "returned from a lambda"))
            elif isinstance(_x351, (_A273.Assign, _A273.AnnAssign, _A273.AugAssign)):
                _tg351 = (list(_x351.targets) if isinstance(_x351, _A273.Assign)
                          else [_x351.target])
                if _x351.value is not None and any(
                        isinstance(_w351, (_A273.Attribute, _A273.Subscript))
                        for _t351 in _tg351 for _w351 in _A273.walk(_t351)):
                    _esc351.append((_x351.value, "stored into `%s`"
                                    % _A273.unparse(_tg351[0])[:40]))
                elif (isinstance(_x351, _A273.AnnAssign) and _x351.value is not None
                        and isinstance(_x351.target, _A273.Name)):
                    _ah351 = _x351.annotation
                    if isinstance(_ah351, _A273.Subscript):
                        _ah351 = _ah351.value
                    if (getattr(_ah351, "id", None) or getattr(_ah351, "attr", None)) not in (
                            _safe351h + ("tuple", "Tuple", "Optional")):
                        _esc351.append((_x351.value, "bound to `%s: %s`" % (
                            _x351.target.id, _A273.unparse(_x351.annotation)[:40])))
            elif isinstance(_x351, _A273.Call):
                _cn351 = _x351.func.id if isinstance(_x351.func, _A273.Name) else ""
                if _cn351 not in _bi351:
                    for _aa351 in list(_x351.args) + [_k.value for _k in _x351.keywords]:
                        # a bare view PARAMETER is route #336's (same rule, Module 5)
                        if not (isinstance(_aa351, _A273.Name) and _aa351.id in _param351):
                            _esc351.append((_aa351, "passed to `%s`"
                                            % _A273.unparse(_x351.func)[:40]))
            # (d) a store through an ALIAS
            _st351: List[Any] = []
            if isinstance(_x351, (_A273.Assign, _A273.Delete)):
                _st351 = list(_x351.targets)
            elif isinstance(_x351, (_A273.AugAssign, _A273.AnnAssign)):
                _st351 = [_x351.target]
            for _t351 in _st351:
                for _w351 in _A273.walk(_t351):
                    if (isinstance(_w351, _A273.Subscript) and isinstance(_w351.value, _A273.Name)
                            and _w351.value.id in _view351 and _w351.value.id not in _param351):
                        _bad351.append((_F351.name, getattr(_x351, "lineno", 0),
                                        _w351.value.id, "stored into through the alias"))
            if (isinstance(_x351, _A273.AugAssign) and isinstance(_x351.target, _A273.Name)
                    and _x351.target.id in _view351 and _x351.target.id not in _param351):
                _bad351.append((_F351.name, getattr(_x351, "lineno", 0), _x351.target.id,
                                "updated in place through the alias"))
            if (isinstance(_x351, _A273.Call) and isinstance(_x351.func, _A273.Attribute)
                    and isinstance(_x351.func.value, _A273.Name)
                    and _x351.func.value.id in _view351
                    and _x351.func.value.id not in _param351
                    and _x351.func.attr not in ("count", "index", "get", "keys", "values",
                                                "items", "copy", "__len__", "__contains__",
                                                "__getitem__")):
                _bad351.append((_F351.name, getattr(_x351, "lineno", 0), _x351.func.value.id,
                                "mutated through the alias (`.%s`)" % _x351.func.attr))
            for _ee351, _why351 in _esc351:
                _hit351 = None
                _wk351 = [_ee351]
                while _wk351 and _hit351 is None:
                    _e351 = _wk351.pop()
                    if isinstance(_e351, _A273.Name):
                        _hit351 = _e351.id if _e351.id in _view351 else None
                    elif isinstance(_e351, _A273.IfExp):
                        _wk351 += [_e351.body, _e351.orelse]
                    elif isinstance(_e351, _A273.BoolOp):
                        _wk351 += list(_e351.values)
                    elif isinstance(_e351, (_A273.NamedExpr, _A273.Starred)):
                        _wk351.append(_e351.value)
                    elif isinstance(_e351, (_A273.Tuple, _A273.List, _A273.Set)):
                        _wk351 += list(_e351.elts)
                    elif isinstance(_e351, _A273.Dict):
                        _wk351 += [_k for _k in _e351.keys if _k is not None] + list(
                            _e351.values)
                    elif isinstance(_e351, _A273.Subscript) and isinstance(
                            _e351.slice, _A273.Slice):
                        _wk351.append(_e351.value)
                    elif isinstance(_e351, _A273.BinOp) and isinstance(
                            _e351.op, (_A273.Add, _A273.Mult)):
                        _wk351 += [_e351.left, _e351.right]
                if _hit351 is not None:
                    _bad351.append((_F351.name, getattr(_x351, "lineno", 0), _hit351, _why351))
                    break
    if _bad351:
        from errors import PyCSLSemanticError as _PyCSLSemErr351
        raise _PyCSLSemErr351(
            f"in '{_bad351[0][0]}' (line {_bad351[0][1]}), the value of '{_bad351[0][2]}' — a "
            f"READ-ONLY view parameter (`Sequence`, `tuple[T, ...]`, `Mapping`) or an alias of "
            f"one — is {_bad351[0][3]} (route #351). PyCSL reads the view as a list / dict, so "
            f"once it leaves under a mutable type a store into it would be verified, while "
            f"the argument may be a tuple or a mapping proxy whose store raises TypeError. "
            f"Return / store / pass a copy (`list(xs)`, `dict(d)`), or keep the read-only "
            f"annotation on the receiving slot.",
            filename=args.file, stage="ir-semantic",
            code="PYCSL-SEM-READONLY-VIEW-ESCAPE")
    # (#49) ROUTE #339 — AN ENUM MEMBER IS NOT AN INT. `C.A` of a user enum class lowers
    # to the opaque getter `get_A _class_c : int` (and route #325 keeps it int, its value
    # being an int literal), so every int operation applies to it. MEASURED at 5e517ffc
    # (witnesses-r339/): on a PLAIN `Enum` member `x - x`, `x * 0`, `-x + x`, `x * x`,
    # `x < x` and `a[x]` PROVED under `no_exception \all` (CPython: TypeError), and a
    # user `__eq__` / `__lt__` on an `Enum` / `IntEnum` was ignored (`x == x` PROVED
    # True, CPython's `__eq__` returns False). RULE (fail-closed, AST-level, over every
    # LOWERED function, nested scopes included): a class whose base is (a dotted name
    # ending in) `Enum`/`IntEnum`/`Flag`/`IntFlag`/`StrEnum`/`ReprEnum`, or another
    # such class of this file, is an ENUM. An `IntEnum`/`IntFlag` (or `int`-mixin) enum
    # that defines NO dunder (own or inherited in this file) keeps its int semantics —
    # its members ARE ints and every operator is int's. Every other enum is OPAQUE: an
    # enum-member expression (`C.M`, `C(v)`, `C[k]`, a name bound to one, a parameter /
    # field / callee result annotated `C` or `Optional[C]`, a `for` target over `C`) may
    # only be bound to a name, compared with `is`/`is not` (and `==`/`!=`/`in`/`not
    # in`/`match`, unless `__eq__`/`__ne__` is user-defined), tested for truth (unless
    # `__bool__`/`__len__` is), read as `.value`/`.name`, returned from / passed to a
    # parameter / defaulted where the annotation is `C`, or given to `isinstance`/`id`/
    # `type` (`hash` unless `__hash__` is user-defined). Anything else — arithmetic,
    # unary `-`/`+`/`~`, ordering, an index, an augmented store, a container element, a
    # builtin, a string conversion — is REFUSED (`PYCSL-SEM-ENUM-MEMBER-OPERATION`): the
    # model has no value for it that CPython would compute. BLAST RADIUS, measured
    # before landing: pycsl-reference 1 enum user (4243, `.value` only — admitted, still
    # refused by route #325), the self-annotate mirror's `_Precedence` (an `IntEnum` of no
    # dunder — int semantics kept), python-reference / pycsl_lib 0.
    # INLINE (check-mirror-coverage); `_run_pipeline`'s mirror twin is `\trusted`.
    _EB339 = {"Enum", "IntEnum", "Flag", "IntFlag", "StrEnum", "ReprEnum"}
    _ND339 = {"__init__", "__new__", "__init_subclass__", "__doc__", "__module__",
              "__qualname__", "__slots__", "__set_name__", "__class_getitem__",
              "__annotations__"}
    # (#49) ROUTES #352-#356 (gen #37 red team 26) — the classifier above was blind to five
    # shapes, each MEASURED PROVED at 1a9cfa42 against CPython. #352: a base spelled through
    # an import alias (`from enum import Enum as E`, `import enum as e` + `e.IntEnum`, a
    # module-level `E = Enum`) was not an enum, so `C(E)`'s members kept int laws. RULE: every
    # base is RESOLVED through the file's imports / module-level aliases to a token: a stdlib
    # enum class `E:<X>`, a file class `C:<n>`, a builtin `B:<n>`, a non-enum stdlib import
    # `S`, an unresolved attribute whose tail names an enum class `T:<X>` (an enum of unknown
    # origin: OPAQUE), or UNKNOWN `U` (a non-stdlib import, an unbound name, an expression). A
    # class with `U` in its ancestry and a member-shaped body (a plain non-lambda binding) may
    # be an enum (an imported member-less enum base) and is treated as an OPAQUE enum whose
    # every dunder is assumed user-defined (0 such classes in corpus / pyref / mirror /
    # pycsl_lib, measured). #353: dunders were read from the enum bases only, so a NON-enum
    # mixin's `__sub__` / `__lt__` / `__eq__` was invisible. RULE: the dunders of an enum are
    # those of EVERY file class of its C3 MRO — the linearisation holds exactly the transitive
    # base closure, and any dunder there is treated as overriding (an over-approximation of
    # which one wins, so no ordering is needed) — and an enum is int-like only if its MRO holds
    # nothing but `IntEnum` / `int` / `Enum` / `ReprEnum` / `object` and file ENUM classes; a
    # user `__eq__` without `__hash__` anywhere in it makes `hash` refused (`__hash__ = None`).
    # #354: `IntFlag` / `Flag` override `~` (and STRICT boundaries make `|` `^` `&` raise), so
    # they are NOT int-like (their members are opaque), and a class keyword anywhere in the
    # MRO (`boundary=`, `metaclass=`) makes the enum opaque. #355 / #356: see the checks after
    # the context walk below.
    import sys as _sys352
    import builtins as _bi352
    _STD352 = set(getattr(_sys352, "stdlib_module_names", ())) - {"enum"}
    _im352 = {}     # local name -> "E:<X>" (from enum), "M" (the enum module), "S", "U"
    _star352 = False
    for _x352 in _A273.walk(unified_ast):
        if isinstance(_x352, _A273.ImportFrom):
            _md352 = _x352.module or ""
            for _a352 in _x352.names:
                if _a352.name == "*":
                    _star352 = _star352 or _md352 != "enum" or bool(_x352.level)
                    continue
                _im352[_a352.asname or _a352.name] = (
                    ("E:" + _a352.name if _a352.name in _EB339 else "U")
                    if _md352 == "enum" and not _x352.level else
                    "S" if not _x352.level and _md352.split(".")[0] in _STD352 else "U")
        elif isinstance(_x352, _A273.Import):
            for _a352 in _x352.names:
                _im352[_a352.asname or _a352.name.split(".")[0]] = (
                    "M" if (_a352.asname and _a352.name == "enum")
                    or (not _a352.asname and _a352.name.split(".")[0] == "enum") else
                    "S" if _a352.name.split(".")[0] in _STD352 else "U")
    _al352 = {}     # module-level `Y = <name / attribute>` aliases (bound once)
    _alc352 = {}
    for _s352 in unified_ast.body:
        if isinstance(_s352, (_A273.Assign, _A273.AnnAssign, _A273.AugAssign)):
            for _t352 in (_s352.targets if isinstance(_s352, _A273.Assign) else [_s352.target]):
                if isinstance(_t352, _A273.Name):
                    _alc352[_t352.id] = _alc352.get(_t352.id, 0) + 1
                    _al352[_t352.id] = getattr(_s352, "value", None)
    _cdn352 = {}    # class name -> [ClassDef, ...]
    for _x352 in _A273.walk(unified_ast):
        if isinstance(_x352, _A273.ClassDef):
            _cdn352.setdefault(_x352.name, []).append(_x352)
    _tok352 = {}    # class name -> resolved base tokens (+ "K" for a class keyword)
    _odu352 = {}    # class name -> own user dunders
    _omm352 = {}    # class name -> own member-shaped names
    _onm352 = {}    # class name -> every name its body binds
    _olv352 = {}    # class name -> own member literal values ([] when any is not a literal)
    _onw352 = set()  # classes whose body defines `__new__`
    for _n352, _cs352 in _cdn352.items():
        _tk352 = set()
        _du352 = set()
        _mm352 = set()
        _nm352 = set()
        _lv352 = []
        for _c352 in _cs352:
            if _c352.keywords:
                _tk352.add("K")
            for _b352 in _c352.bases:
                _e352 = _b352
                _r352 = None
                _gd352 = 0
                while _r352 is None and _gd352 < 64:
                    _gd352 += 1
                    if isinstance(_e352, _A273.Subscript):
                        _e352 = _e352.value
                    elif isinstance(_e352, _A273.Name):
                        _i352 = _e352.id
                        if _i352 in _cdn352:
                            _r352 = "C:" + _i352
                        elif _i352 in _al352 and _i352 not in _im352:
                            _e352 = (_al352[_i352] if _alc352.get(_i352) == 1
                                     and isinstance(_al352[_i352], (_A273.Name, _A273.Attribute))
                                     else None)
                            if _e352 is None:
                                _r352 = "U"
                        elif _i352 in _im352:
                            _r352 = "U" if _im352[_i352] == "M" else _im352[_i352]
                        elif _i352 in _EB339:
                            _r352 = ("T:" if _star352 else "E:") + _i352
                        elif hasattr(_bi352, _i352) and not _star352:
                            _r352 = "B:" + _i352
                        else:
                            _r352 = "U"
                    elif isinstance(_e352, _A273.Attribute):
                        _h352 = _e352
                        _d352 = 0
                        while isinstance(_h352, _A273.Attribute):
                            _h352 = _h352.value
                            _d352 += 1
                        _v352 = (_im352.get(_h352.id) if isinstance(_h352, _A273.Name)
                                 else None)
                        if _v352 == "M" and _d352 == 1:
                            _r352 = "E:" + _e352.attr if _e352.attr in _EB339 else "U"
                        elif _v352 == "S" and _e352.attr not in _EB339:
                            _r352 = "S"
                        elif _e352.attr in _EB339:
                            _r352 = "T:" + _e352.attr
                        else:
                            _r352 = "U"
                    else:
                        _r352 = "U"
                _tk352.add(_r352 or "U")
            for _s339 in _c352.body:
                _ts339 = ([_s339.name] if isinstance(_s339, _FN273 + (_A273.ClassDef,)) else
                          [_t.id for _t in _s339.targets if isinstance(_t, _A273.Name)]
                          if isinstance(_s339, _A273.Assign) else
                          [_s339.target.id] if isinstance(_s339, _A273.AnnAssign)
                          and isinstance(_s339.target, _A273.Name) else [])
                _vl352 = getattr(_s339, "value", None)
                for _t339 in _ts339:
                    _nm352.add(_t339)
                    if _t339 == "__new__":
                        _onw352.add(_n352)
                    if _t339.startswith("__") and _t339.endswith("__"):
                        if _t339 not in _ND339:
                            _du352.add(_t339)
                    elif not isinstance(_s339, _FN273 + (_A273.ClassDef,)) and not (
                            _t339.startswith("_") and _t339.endswith("_")):
                        _mm352.add(_t339)
                        if (isinstance(_vl352, _A273.Constant)
                                and type(_vl352.value) in (int, str)):
                            if _lv352 is not None:
                                _lv352.append(_vl352.value)
                        elif not (isinstance(_vl352, _A273.Name)
                                  and _vl352.id in _nm352):
                            _lv352 = None
        _tok352[_n352] = _tk352
        _odu352[_n352] = _du352
        _omm352[_n352] = _mm352
        _onm352[_n352] = _nm352
        _olv352[_n352] = _lv352
    _anc352 = {_n: {_n} for _n in _cdn352}     # file-class ancestry (the MRO's file part)
    _chg352 = True
    while _chg352:
        _chg352 = False
        for _n352 in _cdn352:
            for _t352 in list(_tok352[_n352]):
                if _t352.startswith("C:") and not _anc352[_t352[2:]] <= _anc352[_n352]:
                    _anc352[_n352] |= _anc352[_t352[2:]]
                    _chg352 = True
    _atk352 = {_n: set().union(*[_tok352[_m] for _m in _anc352[_n]]) for _n in _cdn352}
    _den352 = {_n for _n in _cdn352
               if any(_t[:2] in ("E:", "T:") for _t in _atk352[_n])}
    _may352 = {_n for _n in _cdn352 if _n not in _den352 and "U" in _atk352[_n]
               and any(isinstance(_s, (_A273.Assign, _A273.AnnAssign))
                       and getattr(_s, "value", None) is not None
                       and not isinstance(_s.value, _A273.Lambda)
                       and any(isinstance(_t, _A273.Name) and not _t.id.startswith("__")
                               for _t in (_s.targets if isinstance(_s, _A273.Assign)
                                          else [_s.target]))
                       for _c in _cdn352[_n] for _s in _c.body)}
    _cls339 = {}    # enum class name -> [int-like?, user dunders, member names]
    for _n352 in sorted(_den352 | _may352):
        _du339 = set().union(*[_odu352[_m] for _m in _anc352[_n352]])
        _mm339 = set().union(*[_omm352[_m] for _m in _anc352[_n352]])
        if _n352 in _may352:
            _du339 |= {"__eq__", "__ne__", "__bool__", "__len__", "__hash__",
                       "__getattr__", "__getattribute__"}
        _il339 = (bool(_atk352[_n352] & {"E:IntEnum", "B:int"})
                  and all(_t in ("E:IntEnum", "E:Enum", "E:ReprEnum", "B:int", "B:object")
                          or (_t.startswith("C:") and _t[2:] in _den352)
                          for _t in _atk352[_n352]))
        _cls339[_n352] = [_il339, _du339, _mm339]
    _op339 = {_k: _v for _k, _v in _cls339.items() if not (_v[0] and not _v[1])}
    _bad339 = []
    if _op339:
        _par339 = {}
        for _x339 in _A273.walk(unified_ast):
            for _y339 in _A273.iter_child_nodes(_x339):
                _par339[id(_y339)] = _x339
        # annotation -> opaque enum class (`C`, `"C"`, `Optional[C]`, `C | None`);
        # an opaque enum anywhere else inside an annotation (a container) is refused
        _ann339 = {}
        _badann339 = []
        for _x339 in _A273.walk(unified_ast):
            _as339 = []
            if isinstance(_x339, _A273.arg):
                _as339 = [_x339.annotation]
            elif isinstance(_x339, _FN273):
                _as339 = [_x339.returns]
            elif isinstance(_x339, _A273.AnnAssign):
                _as339 = [_x339.annotation]
            for _a339 in _as339:
                if _a339 is None:
                    continue
                _q339 = _a339
                if (isinstance(_q339, _A273.Subscript) and isinstance(_q339.value, _A273.Name)
                        and _q339.value.id == "Optional"):
                    _q339 = _q339.slice
                elif (isinstance(_q339, _A273.BinOp) and isinstance(_q339.op, _A273.BitOr)
                      and isinstance(_q339.right, _A273.Constant)
                      and _q339.right.value is None):
                    _q339 = _q339.left
                _nm339 = (_q339.id if isinstance(_q339, _A273.Name) else _q339.value
                          if isinstance(_q339, _A273.Constant)
                          and isinstance(_q339.value, str) else None)
                if _nm339 in _op339:
                    _ann339[id(_a339)] = _nm339
                elif any((isinstance(_z, _A273.Name) and _z.id in _op339)
                         or (isinstance(_z, _A273.Constant) and _z.value in _op339)
                         for _z in _A273.walk(_a339)):
                    _badann339.append(_a339)
        # callee results and fields annotated with an opaque enum, by (attribute) name
        _ret339 = {}
        _fld339 = {}
        for _x339 in _A273.walk(unified_ast):
            if isinstance(_x339, _FN273) and id(_x339.returns) in _ann339:
                _ret339[_x339.name] = _ann339[id(_x339.returns)]
            if isinstance(_x339, _A273.AnnAssign) and id(_x339.annotation) in _ann339:
                _t339 = _x339.target
                _p339 = _par339.get(id(_x339))
                if isinstance(_t339, _A273.Attribute):
                    _fld339[_t339.attr] = _ann339[id(_x339.annotation)]
                elif isinstance(_t339, _A273.Name) and isinstance(_p339, _A273.ClassDef):
                    _fld339[_t339.id] = _ann339[id(_x339.annotation)]
        _fns339 = {}
        for _x339 in _A273.walk(unified_ast):
            if isinstance(_x339, _FN273):
                _fns339.setdefault(_x339.name, []).append(_x339)
        _scopes339 = [unified_ast] + _low273
        _mod339 = {}
        for _F339 in _scopes339:
            _en339 = dict(_mod339)
            _nodes339 = (list(unified_ast.body) if _F339 is unified_ast
                         else list(_A273.walk(_F339)))
            if _F339 is not unified_ast:
                for _x339 in _nodes339:
                    if isinstance(_x339, _A273.arg) and id(_x339.annotation) in _ann339:
                        _en339[_x339.arg] = _ann339[id(_x339.annotation)]
            _ise339 = {}
            for _it339 in range(len(_nodes339) + 2):
                _ise339 = {}
                for _x339 in (_nodes339 if _F339 is not unified_ast else
                              [_z for _s in _nodes339 for _z in _A273.walk(_s)]):
                    _k339 = None
                    if (isinstance(_x339, _A273.Attribute)
                            and isinstance(_x339.value, _A273.Name)
                            and _x339.value.id in _op339
                            and _x339.attr in _op339[_x339.value.id][2]):
                        _k339 = _x339.value.id
                    elif (isinstance(_x339, (_A273.Call, _A273.Subscript))
                          and isinstance(getattr(_x339, "func", None)
                                         or getattr(_x339, "value", None), _A273.Name)
                          and (getattr(_x339, "func", None)
                               or getattr(_x339, "value", None)).id in _op339):
                        _k339 = (getattr(_x339, "func", None)
                                 or getattr(_x339, "value", None)).id
                    elif isinstance(_x339, _A273.Call):
                        _f339 = _x339.func
                        _fn339 = (_f339.id if isinstance(_f339, _A273.Name) else _f339.attr
                                  if isinstance(_f339, _A273.Attribute) else None)
                        _k339 = _ret339.get(_fn339)
                    elif (isinstance(_x339, _A273.Attribute)
                          and isinstance(_x339.ctx, _A273.Load)):
                        _k339 = _fld339.get(_x339.attr)
                    elif isinstance(_x339, _A273.Name) and isinstance(_x339.ctx, _A273.Load):
                        _k339 = _en339.get(_x339.id)
                    if _k339 is not None:
                        _ise339[id(_x339)] = (_k339, _x339)
                _n0339 = len(_en339)
                for _x339 in (_nodes339 if _F339 is not unified_ast else
                              [_z for _s in _nodes339 for _z in _A273.walk(_s)]):
                    _v339 = None
                    _tg339 = []
                    if isinstance(_x339, (_A273.Assign, _A273.NamedExpr)):
                        _v339 = _x339.value
                        _tg339 = (list(_x339.targets) if isinstance(_x339, _A273.Assign)
                                  else [_x339.target])
                    elif isinstance(_x339, _A273.AnnAssign) and _x339.value is not None:
                        _v339 = _x339.value
                        _tg339 = [_x339.target]
                    elif isinstance(_x339, (_A273.For, _A273.AsyncFor, _A273.comprehension)):
                        _tg339 = [_x339.target]
                        if isinstance(_x339.iter, _A273.Name) and _x339.iter.id in _op339:
                            for _z339 in _A273.walk(_x339.target):
                                if isinstance(_z339, _A273.Name):
                                    _en339.setdefault(_z339.id, _x339.iter.id)
                        continue
                    if _v339 is not None and id(_v339) in _ise339:
                        for _t339 in _tg339:
                            if isinstance(_t339, _A273.Name):
                                _en339.setdefault(_t339.id, _ise339[id(_v339)][0])
                if len(_en339) == _n0339:
                    break
            if _F339 is unified_ast:
                _mod339 = _en339
                continue
            # the CONTEXT of every opaque enum-member expression decides
            for _k339, _x339 in _ise339.values():
                _du339 = _op339[_k339][1]
                _p339 = _par339.get(id(_x339))
                _g339 = _par339.get(id(_p339)) if _p339 is not None else None
                _eq339 = not (_du339 & {"__eq__", "__ne__"})
                _tr339 = not (_du339 & {"__bool__", "__len__"})
                _ok339 = False
                if isinstance(_p339, (_A273.Assign, _A273.NamedExpr)) and _p339.value is _x339:
                    _ok339 = all(isinstance(_t, _A273.Name) for _t in (
                        _p339.targets if isinstance(_p339, _A273.Assign) else [_p339.target]))
                elif isinstance(_p339, _A273.AnnAssign) and _p339.value is _x339:
                    _ok339 = isinstance(_p339.target, _A273.Name)
                elif isinstance(_p339, _A273.Compare):
                    _ok339 = True
                    _xs339 = [_p339.left] + list(_p339.comparators)
                    for _i339, _o339 in enumerate(_p339.ops):
                        if _x339 is not _xs339[_i339] and _x339 is not _xs339[_i339 + 1]:
                            continue
                        if isinstance(_o339, (_A273.Is, _A273.IsNot)):
                            continue
                        if isinstance(_o339, (_A273.Eq, _A273.NotEq)) and _eq339:
                            continue
                        if (isinstance(_o339, (_A273.In, _A273.NotIn)) and _eq339
                                and _x339 is _xs339[_i339]):
                            continue
                        _ok339 = False
                elif (isinstance(_p339, (_A273.Tuple, _A273.List, _A273.Set))
                      and isinstance(_g339, _A273.Compare) and _eq339
                      and _p339 in _g339.comparators
                      and all(isinstance(_o, (_A273.In, _A273.NotIn)) for _o in _g339.ops)):
                    _ok339 = True
                elif isinstance(_p339, _A273.Attribute) and _p339.value is _x339:
                    _ok339 = (_p339.attr in ("value", "name")
                              and not (_du339 & {"__getattr__", "__getattribute__"}))
                elif isinstance(_p339, (_A273.If, _A273.While, _A273.IfExp, _A273.Assert)):
                    _ok339 = _p339.test is _x339 and _tr339
                elif isinstance(_p339, _A273.UnaryOp) and isinstance(_p339.op, _A273.Not):
                    _ok339 = _tr339
                elif isinstance(_p339, _A273.BoolOp):
                    _ok339 = _tr339 and (
                        (isinstance(_g339, (_A273.If, _A273.While, _A273.IfExp, _A273.Assert))
                         and _g339.test is _p339)
                        or (isinstance(_g339, _A273.UnaryOp)
                            and isinstance(_g339.op, _A273.Not)))
                elif isinstance(_p339, _A273.Expr):
                    _ok339 = True
                elif isinstance(_p339, (_A273.MatchValue, _A273.Match)):
                    _ok339 = _eq339
                elif isinstance(_p339, _A273.Return):
                    _h339 = _p339
                    while _h339 is not None and not isinstance(_h339, _FN273 + (_A273.Lambda,)):
                        _h339 = _par339.get(id(_h339))
                    _ok339 = (isinstance(_h339, _FN273)
                              and _ann339.get(id(_h339.returns)) == _k339)
                elif isinstance(_p339, (_A273.Call, _A273.keyword)):
                    _c339 = _p339 if isinstance(_p339, _A273.Call) else _g339
                    if isinstance(_c339, _A273.Call) and _c339.func is not _x339:
                        _f339 = _c339.func
                        _fn339 = (_f339.id if isinstance(_f339, _A273.Name) else _f339.attr
                                  if isinstance(_f339, _A273.Attribute) else None)
                        if isinstance(_f339, _A273.Name) and _fn339 in (
                                "isinstance", "id", "type") and _fn339 not in _fns339:
                            _ok339 = True
                        elif (isinstance(_f339, _A273.Name) and _fn339 == "hash"
                              and _fn339 not in _fns339):
                            # route #353: an `__eq__` without `__hash__` in the MRO
                            # sets `__hash__ = None`; a user `__hash__` is user code
                            _ok339 = not (_du339 & {"__hash__", "__eq__"})
                        elif _fn339 in _fns339:
                            _ok339 = True
                            for _d339 in _fns339[_fn339]:
                                _pa339 = (list(getattr(_d339.args, "posonlyargs", None) or [])
                                          + list(_d339.args.args))
                                if isinstance(_f339, _A273.Attribute) and _pa339 and \
                                        _pa339[0].arg in ("self", "cls"):
                                    _pa339 = _pa339[1:]
                                _tp339 = None
                                if isinstance(_p339, _A273.keyword):
                                    _tp339 = [_a for _a in _pa339 + list(_d339.args.kwonlyargs)
                                              if _a.arg == _p339.arg]
                                    _tp339 = _tp339[0] if _tp339 else None
                                elif _x339 in _c339.args:
                                    _i339 = _c339.args.index(_x339)
                                    _tp339 = _pa339[_i339] if _i339 < len(_pa339) else None
                                if _tp339 is None or _ann339.get(id(_tp339.annotation)) != _k339:
                                    _ok339 = False
                elif isinstance(_p339, _A273.arguments):
                    _pa339 = (list(getattr(_p339, "posonlyargs", None) or [])
                              + list(_p339.args))
                    _tp339 = None
                    if _x339 in _p339.defaults:
                        _tp339 = _pa339[len(_pa339) - len(_p339.defaults)
                                        + _p339.defaults.index(_x339)]
                    elif _x339 in _p339.kw_defaults:
                        _tp339 = _p339.kwonlyargs[_p339.kw_defaults.index(_x339)]
                    _ok339 = (_tp339 is not None
                              and _ann339.get(id(_tp339.annotation)) == _k339)
                if not _ok339:
                    _bad339.append((getattr(_F339, "name", "?"),
                                    getattr(_x339, "lineno", 0), _k339,
                                    _A273.unparse(_p339 if _p339 is not None
                                                  else _x339)[:70]))
            for _x339 in _nodes339:
                if isinstance(_x339, _A273.AugAssign) and isinstance(
                        _x339.target, _A273.Name) and _x339.target.id in _en339:
                    _bad339.append((_F339.name, getattr(_x339, "lineno", 0),
                                    _en339[_x339.target.id], _A273.unparse(_x339)[:70]))
                # the enum CLASS itself handed to a callee (`list(C)`, `sorted(C)`) is a
                # container of its members
                if (isinstance(_x339, _A273.Name) and _x339.id in _op339
                        and isinstance(_x339.ctx, _A273.Load)):
                    _p339 = _par339.get(id(_x339))
                    if (isinstance(_p339, (_A273.Call, _A273.keyword))
                            and getattr(_p339, "func", None) is not _x339
                            and not (isinstance(_p339, _A273.Call)
                                     and isinstance(_p339.func, _A273.Name)
                                     and _p339.func.id in ("isinstance", "issubclass"))):
                        _bad339.append((_F339.name, getattr(_x339, "lineno", 0), _x339.id,
                                        _A273.unparse(_p339)[:70]))
        for _a339 in _badann339:
            _bad339.append(("?", getattr(_a339, "lineno", 0), "",
                            "annotation `" + _A273.unparse(_a339)[:60] + "`"))
    # ROUTE #355 — `C(v)` IS A VALUE LOOKUP THAT RAISES ValueError on a miss (`C(99)` was
    # emitted `any c` and PROVED under `no_exception \all`, IntEnum and plain Enum alike).
    # RULE, for EVERY enum of the file (transparent ones too), in every lowered function:
    # `C(v)` is admitted only when its one positional argument is a member of `C` (`C(C.A)`)
    # or an int / str literal equal (same type) to a literal member value of `C`, `C`'s MRO
    # defines no `__new__`, and the literal's type is the one CPython stores (`int` for an
    # int-mixin enum, `str` for a str-mixin one, either for a plain Enum, never under another
    # mixin or an unresolved base). Anything else is REFUSED — the miss is CPython's
    # ValueError, which the model never raises (a sound refusal; the faithful `C[k]`-style
    # membership goal needs the member values the getter does not carry).
    # ROUTE #356 — the enum CLASS OBJECT's non-member attributes (`C.__members__`,
    # `C._member_map_`, `C._value2member_map_`, `C.mro`, ...) are containers / views of the
    # members whose elements no tracked form sees (`for m in C.__members__.values(): m - m`
    # PROVED). RULE: a load of `C.X` with `X` neither a member nor a name bound in the body of
    # a file class of `C`'s MRO is REFUSED, and so is any store / delete through `C.X`.
    for _F352 in _low273:
        for _x352 in _A273.walk(_F352):
            if (isinstance(_x352, _A273.Call) and isinstance(_x352.func, _A273.Name)
                    and _x352.func.id in _den352):
                _k352 = _x352.func.id
                _a352 = (_x352.args[0] if len(_x352.args) == 1 and not _x352.keywords
                         else None)
                _mx352 = {_t for _t in _atk352[_k352] if not _t.startswith("C:")}
                _ty352 = (None if (_mx352 - {"E:Enum", "E:ReprEnum", "E:IntEnum", "E:IntFlag",
                                             "E:Flag", "E:StrEnum", "B:object", "B:int",
                                             "B:str"})
                          or (_mx352 & {"E:IntEnum", "E:IntFlag", "B:int"}
                              and _mx352 & {"E:StrEnum", "B:str"})
                          or any(_m in _onw352 for _m in _anc352[_k352])
                          else int if _mx352 & {"E:IntEnum", "E:IntFlag", "B:int"}
                          else str if _mx352 & {"E:StrEnum", "B:str"} else "any")
                _ok352 = (isinstance(_a352, _A273.Attribute)
                          and isinstance(_a352.value, _A273.Name)
                          and _a352.value.id == _k352 and _a352.attr in _cls339[_k352][2])
                if (not _ok352 and _ty352 is not None and isinstance(_a352, _A273.Constant)
                        and type(_a352.value) in (int, str) and _olv352[_k352] is not None
                        and (_ty352 == "any" or type(_a352.value) is _ty352)):
                    _ok352 = any(type(_v) is type(_a352.value) and _v == _a352.value
                                 for _v in _olv352[_k352])
                if not _ok352:
                    _bad339.append((_F352.name, getattr(_x352, "lineno", 0), _k352,
                                    _A273.unparse(_x352)[:70]
                                    + " (a value lookup that may raise ValueError)"))
            elif (isinstance(_x352, _A273.Attribute) and isinstance(_x352.value, _A273.Name)
                  and _x352.value.id in _den352):
                _k352 = _x352.value.id
                if not isinstance(_x352.ctx, _A273.Load) or (
                        _x352.attr not in _cls339[_k352][2]
                        and not any(_x352.attr in _onm352[_m] for _m in _anc352[_k352])):
                    _bad339.append((_F352.name, getattr(_x352, "lineno", 0), _k352,
                                    _A273.unparse(_x352)[:70]
                                    + " (an attribute of the enum class object)"))
    if _bad339:
        from errors import PyCSLSemanticError as _PyCSLSemErr339
        _b339 = sorted((_r[1], _i, _r) for _i, _r in enumerate(_bad339))[0][2]
        raise _PyCSLSemErr339(
            f"'{_b339[0]}' uses a member of the enum class '{_b339[2]}' in `{_b339[3]}` "
            f"(line {_b339[1]}): an enum member is NOT an int — a plain Enum/Flag/StrEnum "
            f"member has no arithmetic, ordering or index, and a user-defined dunder "
            f"(e.g. `__eq__`/`__lt__`) on an enum decides that operator — but PyCSL models "
            f"the member as an opaque int, so the operation would be verified against "
            f"int semantics CPython never runs (route #339). Bind it to a name, compare it "
            f"with `is`/`==`, read its `.value`, or pass/return it where the annotation "
            f"names the enum; use an `IntEnum` without dunders for int semantics"
            f"{'' if len(_bad339) == 1 else f' (also: {len(_bad339) - 1} more)'}.",
            filename=args.file, stage="ir-semantic",
            code="PYCSL-SEM-ENUM-MEMBER-OPERATION")
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
    # (#49) ROUTE #289 — THE TUPLE THAT HELD A LIST. A container the model does not
    # represent (a tuple holding a list lowers to `any int`) hands out an element that is
    # an int, and an element store through it reaches `_handle_array_set_stmt`'s last
    # fallback, `subscript_set <int> <i> <v>` against `val subscript_set (x: int) (i: int)
    # (v: int) : unit` — a store with NO `writes` and NO result: a NO-OP. MEASURED at
    # 7313506b, each PROVED (CPython disagrees): `t: Tuple[List[int], int] = (xs, 0);
    # b = t[0]; b[0] = 5; return xs[0]` == `\old(xs[0])`; the local twin; `t[0][0] = 5`;
    # `b[0] += 4`; a nested tuple; an unannotated tuple. Every application of that op is
    # a dropped mutation whatever reached it, so the gate keys on the EMISSION, at the one
    # site every such store produces (a gate, not a raise in the `\trusted`-stubbed
    # handler, which has no `#@ raises`: lesson d5). Measured population at 7313506b: 1
    # corpus file (0849, a map-leaf inner store, `# pycsl-expected: FAIL`, ill-typed),
    # pyref 0, mirror 0 (the mirror's one textual hit is the STRING LITERAL `"subscript_set"`
    # in `stmt_control_flow`, which the quote guard below excludes — measured).
    if (len(_re.findall(r"(?<![\w'.\"])subscript_set(?![\w'\"])", _mlw))
            > len(_re.findall(r"\bval\s+subscript_set(?![\w'])", _mlw))):
        from errors import PyCSLSemanticError as _PyCSLSemErr289
        raise _PyCSLSemErr289(
            "an element store through a value the model does not represent as a list is "
            "out of scope: the store lowers to the abstract `subscript_set` with NO effect "
            "(typically an element taken from a tuple, or another container, that holds a "
            "list — the container is opaque and its element is an int), so the mutation of "
            "the list it aliases would be SILENTLY ABSENT and a claim about that list "
            "proved of a state that never changed (route #289; measured: `t: Tuple["
            "List[int], int] = (xs, 0); b = t[0]; b[0] = 5; return xs[0]` proved "
            "`\\result == \\old(xs[0])`). Store through the list's own name.",
            filename=args.file, stage="ir-semantic",
            code="PYCSL-SEM-STORE-THROUGH-OPAQUE-ELEMENT")
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
    # (#49) ROUTE #325 — AN UNMODELLED VALUE IS NOT AN INT. Every value Module 6 cannot model
    # falls back to an OPAQUE INT — `val constant F : int` for a module-level name, `get_X`
    # over a module / class object, `getattr_<cls>` for a class attribute, `subscript_get`,
    # `val m_f_0 (..) : int` for a call of an imported / builtin callable — whatever its
    # Python type, so every claim true of ALL INTEGERS was proved of floats, strings, lists
    # and modules: `F = 0.5; F % 1 == 0`, `x < E or x >= E + 1 or x == E`, `int(F) == F`,
    # `time.time() // 1 == time.time()`, `os.getcwd() * 0 == 0` all PROVED (CPython False).
    # Route #322's name-keyed refusal covered `math.pi` and was bypassed by a re-export, an
    # alias, `importlib` and `__import__`. The fix is decided on the EMITTED WhyML (the one
    # place every fallback ends up, whichever lowering produced it): a fallback that stands
    # for a module-level Python value (an ORIGIN), and every value derived from one (a local
    # bound to it, a component read off it, a container built from it, a function returning
    # it, a user function's parameter receiving it), may only be bound, passed on, returned,
    # discarded, or compared `=` / `<>` in program code against a DIFFERENT value. Any
    # other use — an int operator or ordering, `%` / `//`, a contract term, a condition, a
    # reflexive comparison — would give it int theory it has only if it IS an int, and is
    # refused (fail closed). A value KNOWN to be an int keeps its model: an int expression
    # bound at module / class level in this file, `sys.maxsize`-style int attributes, and
    # documented int-returning callables (`len`, `id`, `random.randint`, ...); a user
    # function annotated `-> int` keeps its stub unless its body returns a fallback.
    # INLINE (no nested defs: check-mirror-coverage); `_run_pipeline`'s mirror twin is
    # `\trusted`.
    import re as _re325
    import ast as _ast325
    from module6_whyml.identifiers import whyml_ident as _wid325
    # 1. comments, string literals and `[@...]` attributes out (never Python names).
    _t325 = _mlw
    _o325 = []
    _i325 = 0
    _d325 = 0
    _n325 = len(_t325)
    while _i325 < _n325:
        _c325 = _t325[_i325]
        if _d325 == 0 and _c325 == '"':
            _j325 = _i325 + 1
            while _j325 < _n325 and _t325[_j325] != '"':
                _j325 += 2 if _t325[_j325] == "\\" else 1
            _o325.append('"s"')
            _i325 = _j325 + 1
            continue
        if _t325.startswith("(*", _i325) and not _t325.startswith("(*)", _i325):
            _d325 += 1
            _i325 += 2
            continue
        if _d325 and _t325.startswith("*)", _i325):
            _d325 -= 1
            _i325 += 2
            continue
        if _d325 == 0 and _t325.startswith("[@", _i325):
            _j325 = _t325.find("]", _i325)
            _i325 = (_j325 + 1) if _j325 > 0 else _n325
            continue
        if _d325 == 0 or _c325 == "\n":
            _o325.append(_c325)
        _i325 += 1
    # 2. tokens, tagged with their top-level declaration (a line at indent <= 2 opening
    #    with a declaration keyword starts one).
    _toks325 = []
    _decl325 = []
    _dstart325 = []
    _dk325 = -1
    for _ln325 in "".join(_o325).split("\n"):
        if _re325.match(r"^ {0,2}(let|val|type|predicate|function|lemma|axiom|goal|"
                        r"exception|use|clone|scope|constant|end|meta|module|theory)\b",
                        _ln325):
            _dk325 += 1
            _dstart325.append(len(_toks325))
        for _tk325 in _re325.findall(r"!?[A-Za-z_][A-Za-z_0-9']*|\d+(?:\.\d+)?|<>|<=|>=|"
                                     r":=|->|<-|\|\||&&|/\\|\\/|\S", _ln325):
            _toks325.append(_tk325)
            _decl325.append(max(_dk325, 0))
    _N325 = len(_toks325)
    _dstart325.append(_N325)
    # matching brackets
    _mt325 = {}
    _stk325 = []
    for _k325, _tk325 in enumerate(_toks325):
        if _tk325 in ("(", "[", "{"):
            _stk325.append(_k325)
        elif _tk325 in (")", "]", "}") and _stk325:
            _o2325 = _stk325.pop()
            _mt325[_o2325] = _k325
            _mt325[_k325] = _o2325
    _SPEC325 = {"requires", "ensures", "writes", "reads", "raises", "alias", "returns",
                "diverges", "variant", "="}
    # 3. per-declaration header: kind, name, arity, and (for a `val`) whether it is an
    #    UNCONSTRAINED `int` (no `ensures`): the opaque fallback.
    _S325 = {}      # opaque name -> (family, arity)
    _other325 = {}  # unconstrained int model op (not a Python-value fallback) -> arity
    _poly334 = {}   # ROUTE #334: `val` name -> positions of its `'a`-typed parameters
    _dname325 = {}
    _dar325 = {}
    _hdr325 = {}    # decl -> token index where its header ends
    for _dd325 in range(len(_dstart325) - 1):
        _a325, _z325 = _dstart325[_dd325], _dstart325[_dd325 + 1]
        if _a325 >= _z325 or _toks325[_a325] not in ("let", "val", "predicate", "function"):
            continue
        _k325 = _a325 + 1
        _mods325 = []
        while _k325 < _z325 and _toks325[_k325] in ("constant", "function", "ghost", "rec",
                                                    "predicate", "lemma", "partial"):
            _mods325.append(_toks325[_k325])
            _k325 += 1
        if _k325 >= _z325:
            continue
        _nm325 = _toks325[_k325]
        _dname325[_dd325] = _nm325
        _k325 += 1
        _ar325 = 0
        while _k325 < _z325 and _toks325[_k325] == "(" and _k325 in _mt325:
            _ar325 += 1
            _k325 = _mt325[_k325] + 1
        _dar325[_dd325] = _ar325
        if _toks325[_a325] == "val":
            # ROUTE #334: the positions of the `'a`-typed parameters of a `val`
            _j334 = _a325 + 1 + len(_mods325) + 1
            _ix334 = 0
            while _j334 < _z325 and _toks325[_j334] == "(" and _j334 in _mt325:
                if _toks325[_j334 + 1:_mt325[_j334]][-3:] in ([":", "'", "a"], [":", "'", "b"]):
                    _poly334.setdefault(_nm325, set()).add(_ix334)
                _ix334 += 1
                _j334 = _mt325[_j334] + 1
        _rt325 = []
        if _k325 < _z325 and _toks325[_k325] == ":":
            _k325 += 1
            while _k325 < _z325 and _toks325[_k325] not in _SPEC325:
                _rt325.append(_toks325[_k325])
                _k325 += 1
        _hdr325[_dd325] = _k325
        if (_toks325[_a325] == "val" and _rt325 == ["int"]
                and "ensures" not in _toks325[_k325:_z325]
                and "returns" not in _toks325[_k325:_z325]):
            if _nm325.startswith("pycsl_") and "getattr" not in _nm325:
                _fam325 = None      # an internal encoding (None, Ellipsis), not a fallback
            elif _ar325 == 0 or "constant" in _mods325:
                _fam325 = "constant"
            elif _nm325.startswith("get_"):
                _fam325 = "attribute"
            elif "getattr" in _nm325:
                _fam325 = "getattr"
            elif _nm325.startswith("subscript_get"):
                _fam325 = "subscript"
            elif _re325.search(r"_\d+$", _nm325):
                _fam325 = "call"
            else:
                _fam325 = None
            if _fam325:
                _S325[_nm325] = (_fam325, _ar325)
            else:
                _other325[_nm325] = (_ar325, True)
        elif (_toks325[_a325] == "val" and "ensures" not in _toks325[_k325:_z325]
              and "requires" not in _toks325[_k325:_z325]
              and "returns" not in _toks325[_k325:_z325]):
            _other325[_nm325] = (_ar325, False)     # any other opaque operation (no spec)
    # 4. KNOWN-INT values keep their int model (a documented CPython int type or an int
    #    expression in this source); everything else that fell back is of UNKNOWN type.
    _imod325 = {}   # alias -> module
    _inam325 = {}   # local -> (module, name)
    _bind325 = {}   # module/class-level Python name -> [is-known-int, ...]
    try:
        import warnings as _w325
        with _w325.catch_warnings():
            _w325.simplefilter("ignore")
            _tree325 = _ast325.parse(source_code)
    except SyntaxError:
        _tree325 = None
    _KI_ATTR325 = {("sys", "maxsize"), ("sys", "maxunicode"), ("sys", "hexversion"),
                   ("sys", "api_version")}
    _KI_FI325 = {"max_exp", "max_10_exp", "min_exp", "min_10_exp", "dig", "mant_dig",
                 "radix", "rounds"}
    _KI_CALL325 = {("", "id"), ("", "hash"), ("", "len"), ("", "ord"), ("", "int"),
                   ("random", "randint"), ("random", "randrange"),
                   ("random", "getrandbits"), ("os", "getpid"), ("os", "getppid"),
                   ("time", "time_ns"), ("time", "monotonic_ns"),
                   ("time", "perf_counter_ns"), ("math", "gcd"), ("math", "lcm"),
                   ("math", "isqrt"), ("math", "factorial"), ("math", "comb"),
                   ("math", "perm"), ("", "range")}
    _TYPES325 = {"int", "str", "bool", "float", "dict", "list", "set", "frozenset", "tuple",
                 "bytes", "bytearray", "object", "type", "complex", "notImplemented"}
    if _tree325 is not None:
        for _a325 in _ast325.walk(_tree325):
            if isinstance(_a325, _ast325.Import):
                for _al325 in _a325.names:
                    _imod325[_al325.asname or _al325.name.split(".")[0]] = (
                        _al325.name if _al325.asname else _al325.name.split(".")[0])
            elif isinstance(_a325, _ast325.ImportFrom) and _a325.module:
                for _al325 in _a325.names:
                    _inam325[_al325.asname or _al325.name] = (_a325.module, _al325.name)
        # ROUTE #328 — EVERY module / class-level binding form, at ANY nesting (an `if`,
        # `try`, `with`, `for`, `while` or `match` body at module level binds a GLOBAL):
        # Assign / AnnAssign / AugAssign targets (tuple and starred elements included), a
        # `for` / `with` / `except ... as` / walrus / `match` capture target, a nested
        # `def` / `class`. Only function / lambda bodies and comprehension targets are a
        # scope of their own. #325 read the simple top-level `Name = ..` only, so
        # `A, B = 0.5, 1`, `try: A = math.pi`, `if True: A = 0.5`, `for A in [0.5]`,
        # `(A := 0.5)` and `A, *R = [0.5]` left `A` a non-origin int (witnesses 4330-4335).
        # A target paired with a value (`A = e`, `A, B = e1, e2`) is classified by it; any
        # other bound name is of unknown type (not known-int); a `for A in range(..)`
        # target is an int.
        _bl325 = []     # (name, value expression or None, AugAssign operator or None)
        _mdef325 = []   # module / class-level `def` / `class` nodes
        _wk325 = list(_tree325.body)
        while _wk325:
            _n325 = _wk325.pop()
            if isinstance(_n325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef)):
                _mdef325.append(_n325)
                _wk325.extend(_n325.decorator_list)
                continue
            if isinstance(_n325, _ast325.Lambda):
                continue
            if isinstance(_n325, _ast325.ClassDef):
                _mdef325.append(_n325)
                _wk325.extend(_n325.body)
                continue
            if isinstance(_n325, (_ast325.ListComp, _ast325.SetComp, _ast325.GeneratorExp,
                                  _ast325.DictComp)):
                _wk325.extend([_x325 for _x325 in (getattr(_n325, "elt", None),
                                                   getattr(_n325, "key", None),
                                                   getattr(_n325, "value", None))
                               if _x325 is not None])
                for _gn325 in _n325.generators:
                    _wk325.append(_gn325.iter)
                    _wk325.extend(_gn325.ifs)
                continue
            if isinstance(_n325, _ast325.Assign):
                _pr325 = [(_t325, _n325.value) for _t325 in _n325.targets]
                while _pr325:
                    _t325, _v325 = _pr325.pop()
                    if isinstance(_t325, _ast325.Name):
                        _bl325.append((_t325.id, _v325, None))
                    elif (isinstance(_t325, (_ast325.Tuple, _ast325.List))
                          and isinstance(_v325, (_ast325.Tuple, _ast325.List))
                          and len(_t325.elts) == len(_v325.elts)
                          and not any(isinstance(_x325, _ast325.Starred)
                                      for _x325 in _t325.elts + _v325.elts)):
                        _pr325.extend(zip(_t325.elts, _v325.elts))
                    else:
                        _bl325.extend((_x325.id, None, None) for _x325 in _ast325.walk(_t325)
                                      if isinstance(_x325, _ast325.Name)
                                      and isinstance(_x325.ctx, _ast325.Store))
                _wk325.append(_n325.value)
                continue
            if isinstance(_n325, (_ast325.AnnAssign, _ast325.AugAssign)):
                if isinstance(_n325.target, _ast325.Name):
                    _bl325.append((_n325.target.id, _n325.value,
                                   _n325.op if isinstance(_n325, _ast325.AugAssign) else None))
                if _n325.value is not None:
                    _wk325.append(_n325.value)
                continue
            if isinstance(_n325, (_ast325.For, _ast325.AsyncFor)):
                _rg325 = (isinstance(_n325.target, _ast325.Name)
                          and isinstance(_n325.iter, _ast325.Call)
                          and isinstance(_n325.iter.func, _ast325.Name)
                          and _n325.iter.func.id == "range")
                _bl325.extend((_x325.id, _ast325.Constant(value=0) if _rg325 else None, None)
                              for _x325 in _ast325.walk(_n325.target)
                              if isinstance(_x325, _ast325.Name)
                              and isinstance(_x325.ctx, _ast325.Store))
                _wk325.append(_n325.iter)
                _wk325.extend(_n325.body + _n325.orelse)
                continue
            if isinstance(_n325, _ast325.NamedExpr):
                _bl325.append((_n325.target.id, _n325.value, None))
                _wk325.append(_n325.value)
                continue
            if isinstance(_n325, _ast325.Name) and isinstance(_n325.ctx, _ast325.Store):
                _bl325.append((_n325.id, None, None))
            for _x325 in ("name", "rest"):
                if (isinstance(getattr(_n325, _x325, None), str) and isinstance(
                        _n325, (_ast325.ExceptHandler, _ast325.MatchAs, _ast325.MatchStar,
                                _ast325.MatchMapping))):
                    _bl325.append((getattr(_n325, _x325), None, None))
            _wk325.extend(_ast325.iter_child_nodes(_n325))
        # fixpoint: an int expression over int literals and known-int names
        for _it325 in range(3):
            _known325 = {k for k, v in _bind325.items() if v and all(v)}
            _bind325 = {}
            for _t2325, _vv325, _aug325 in _bl325:
                _ok325 = _vv325 is not None
                _wk325 = [_vv325] if _vv325 is not None else []
                while _wk325 and _ok325:
                    _e325 = _wk325.pop()
                    if isinstance(_e325, _ast325.Constant):
                        _ok325 = type(_e325.value) in (int, bool)
                    elif isinstance(_e325, _ast325.UnaryOp) and isinstance(
                            _e325.op, (_ast325.USub, _ast325.UAdd, _ast325.Invert)):
                        _wk325.append(_e325.operand)
                    elif isinstance(_e325, _ast325.BinOp) and isinstance(
                            _e325.op, (_ast325.Add, _ast325.Sub, _ast325.Mult,
                                       _ast325.FloorDiv, _ast325.Mod, _ast325.LShift,
                                       _ast325.RShift, _ast325.BitAnd, _ast325.BitOr,
                                       _ast325.BitXor)):
                        _wk325.extend([_e325.left, _e325.right])
                    elif isinstance(_e325, _ast325.Name):
                        _ok325 = _e325.id in _known325
                    elif (isinstance(_e325, _ast325.Call)
                          and isinstance(_e325.func, _ast325.Name)
                          and _e325.func.id in ("len", "int", "ord", "id", "hash")
                          and _e325.func.id not in _bind325):
                        pass
                    else:
                        _ok325 = False
                if _aug325 is not None and not isinstance(
                        _aug325, (_ast325.Add, _ast325.Sub, _ast325.Mult,
                                  _ast325.FloorDiv, _ast325.Mod)):
                    _ok325 = False
                _bind325.setdefault(_t2325, []).append(_ok325)
        for _s325 in _ast325.walk(_tree325):
            if isinstance(_s325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef,
                                  _ast325.ClassDef)) and _s325 in _mdef325:
                _bind325.setdefault(_s325.name, []).append(False)
            if isinstance(_s325, _ast325.Global):
                for _g325 in _s325.names:
                    _bind325.setdefault(_g325, []).append(False)
    _known325 = {_wid325(k) for k, v in _bind325.items() if v and all(v)}
    _bound325 = {_wid325(k) for k in _bind325} | {_wid325(k) for k in _imod325} | {
        _wid325(k) for k in _inam325}
    _kicall325 = set()
    for _al325, _m325 in _imod325.items():
        for _mm325, _f325 in _KI_CALL325:
            if _mm325 == _m325:
                _kicall325.add(_wid325(f"{_al325}.{_f325}"))
    for _l325, (_mm325, _f325) in _inam325.items():
        if (_mm325, _f325) in _KI_CALL325:
            _kicall325.add(_wid325(_l325))
    for _mm325, _f325 in _KI_CALL325:
        if _mm325 == "" and _f325 not in _bind325:
            _kicall325.add(_wid325(_f325))
    # ORIGINS: a fallback is an origin only when it stands for a Python value reached
    # through a MODULE-LEVEL name of this file (a global, a class, an import / module
    # object) or a call of a module-level callable (an imported module's function, a
    # from-imported name, a builtin); a getter / subscript over an origin is derived from
    # it (step 6). Unresolved free names and method calls on parameters / locals are not.
    import builtins as _bi325
    _origin325 = set(_bound325)
    # `from m import *` binds names this file does not spell: every free fallback name may
    # be one of them
    _star325 = any(n == "*" for n, _m in [(v[1], v[0]) for v in _inam325.values()])
    _mcall325 = set()
    _ocls334 = set()
    if _tree325 is not None:
        _rt334 = getattr(transpiler, "_record_types", None) or {}
        _ocls334 = {c.name for c in _ast325.walk(_tree325) if isinstance(c, _ast325.ClassDef)
                    and not (isinstance(_rt334.get(c.name), dict)
                             and _rt334[c.name].get("whyml_name"))}
        for _a325 in _ast325.walk(_tree325):
            if isinstance(_a325, _ast325.ClassDef):
                _origin325.add(_wid325(_a325.name))
                _origin325.add("_class_" + _wid325(_a325.name))
            if not isinstance(_a325, _ast325.Call):
                continue
            _ch325 = []
            _f325 = _a325.func
            while isinstance(_f325, _ast325.Attribute):
                _ch325.insert(0, _f325.attr)
                _f325 = _f325.value
            if not isinstance(_f325, _ast325.Name):
                continue
            _ch325.insert(0, _f325.id)
            if (_f325.id in _imod325 or _f325.id in _inam325
                    or (hasattr(_bi325, _f325.id) and _f325.id not in _bind325)):
                _mcall325.add(_wid325(".".join(_ch325)))
            # ROUTE #334: constructing an OPAQUE user class (no record type) yields an
            # object of unknown fields: its stub `<cls>_<n>` is an origin (its getters of
            # provably-int fields stay int, step 6)
            if (len(_ch325) == 1 and _f325.id in _ocls334):
                _mcall325.add(_wid325(_f325.id))
    from module6_whyml.identifiers import stable_hash as _sh325
    _clsbad325 = set()
    _clsok325 = set()
    _clsw325 = set()
    if _tree325 is not None:
        for _a325 in _ast325.walk(_tree325):
            if isinstance(_a325, _ast325.ClassDef):
                for _s325 in _a325.body:
                    for _t2325 in ([t for t in _s325.targets if isinstance(t, _ast325.Name)]
                                   if isinstance(_s325, _ast325.Assign) else
                                   [_s325.target] if isinstance(_s325, _ast325.AnnAssign)
                                   and isinstance(_s325.target, _ast325.Name) else []):
                        if not all(_bind325.get(_t2325.id, [False])):
                            _clsbad325.add(str(_sh325(_t2325.id)))
                        else:
                            _clsok325.add(_t2325.id)
                _clsw325.update({_wid325(_a325.name), "_class_" + _wid325(_a325.name)})
    for _nm325 in list(_S325):
        _fam325 = _S325[_nm325][0]
        if _fam325 == "constant" and _nm325 in _known325:
            del _S325[_nm325]
        elif _fam325 == "call" and _re325.sub(r"_\d+$", "", _nm325) in _kicall325:
            del _S325[_nm325]
        elif ((_fam325 == "constant" and _nm325 not in _origin325 and not _star325)
              or _fam325 in ("attribute", "subscript")
              or (_fam325 == "call"
                  and _re325.sub(r"_\d+$", "", _nm325) not in _mcall325)):
            _other325[_nm325] = (_S325[_nm325][1], True)
            del _S325[_nm325]
    # block structure: begin/try/match/... `end`, `do` ... `done`
    _bk325 = {}
    _bst325 = []
    for _k325, _tk325 in enumerate(_toks325):
        if _tk325 in ("begin", "try", "match", "scope", "loop") and not (
                _k325 > 0 and _toks325[_k325 - 1] == "."):
            _bst325.append(_k325)
        elif _tk325 == "end" and _bst325 and _decl325[_bst325[-1]] == _decl325[_k325]:
            _o2325 = _bst325.pop()
            _bk325[_o2325] = _k325
            _bk325[_k325] = _o2325
        elif _tk325 == "end" and _bst325:
            _bst325 = [x for x in _bst325 if _decl325[x] == _decl325[_k325]]
    # innermost enclosing block opener of each token (-1: none)
    _inb325 = []
    _bst325 = []
    for _k325, _tk325 in enumerate(_toks325):
        if _k325 in _bk325 and _tk325 != "end":
            _bst325.append(_k325)
        _inb325.append(_bst325[-1] if _bst325 else -1)
        if _k325 in _bk325 and _tk325 == "end" and _bst325 and _bst325[-1] == _bk325[_k325]:
            _bst325.pop()
    # 5. binders (a WhyML local/param/pattern variable that shares a fallback's name is
    #    NOT the fallback): header parameters declaration-wide, as Python's function scope
    #    is; `let` from its `in` to the end of its group; `fun` / `forall` / `exists` over
    #    their enclosing group; a `match` / `try` ARM's pattern variables over that arm
    #    only, and a `for` index over its `do .. done` (ROUTE #328: both were scoped to the
    #    WHOLE declaration, so the emitter's own `with Return r -> r` hid a global `R`, and
    #    `| Some v_ -> v_` a global `V_`, everywhere in the function: witnesses 4338-4340).
    _bd325 = {}     # decl -> names bound anywhere in it
    _bg325 = []     # (name, start, end) group-scoped binders
    for _k325, _tk325 in enumerate(_toks325):
        _dd325 = _decl325[_k325]
        if _tk325 == "let" or _tk325 == "for":
            _j325 = _k325 + 1
            while _j325 < _N325 and _toks325[_j325] in ("ghost", "rec", "function", "mutable",
                                                         "predicate", "constant", "ref"):
                _j325 += 1
            _nb325 = []
            if _j325 < _N325 and _toks325[_j325] == "(" and _j325 in _mt325:
                _nb325 = [x for x in _toks325[_j325:_mt325[_j325]]
                          if _re325.match(r"[a-z_][A-Za-z_0-9']*$", x)]
            elif _j325 < _N325 and _k325 > _dstart325[_dd325]:
                _nb325 = [_toks325[_j325]]
            if _tk325 == "for" and _nb325:
                _z325 = _dstart325[_dd325 + 1]
                _q325 = _j325 + 1
                while _q325 < _z325 and _toks325[_q325] != "do":
                    _q325 += 1
                _r325 = _q325 + 1
                _dp325 = 0
                while _r325 < _z325:
                    if _toks325[_r325] == "do":
                        _dp325 += 1
                    elif _toks325[_r325] == "done":
                        if _dp325 == 0:
                            break
                        _dp325 -= 1
                    _r325 += 1
                for _x325 in _nb325:
                    _bg325.append((_x325, _q325, _r325))
                continue
            if not _nb325:
                continue
            # a `let` binds from its `in` to the end of the innermost enclosing group /
            # block (WhyML scoping: `let f = (fun () -> f) in` reads the OUTER `f` in its
            # right-hand side, and `F` / `f` fold to one WhyML name)
            _z325 = _dstart325[_dd325 + 1]
            _q325 = _j325 + 1
            _nest325 = 0
            while _q325 < _z325:
                _tq325 = _toks325[_q325]
                if _tq325 in ("(", "[", "{") and _q325 in _mt325:
                    _q325 = _mt325[_q325] + 1
                    continue
                if _tq325 == "let":
                    _nest325 += 1
                elif _tq325 == "in":
                    if _nest325 == 0:
                        break
                    _nest325 -= 1
                _q325 += 1
            _e325 = _k325 - 1
            _dp325 = 0
            _end325 = _z325
            while _e325 >= _dstart325[_dd325]:
                _te325 = _toks325[_e325]
                if _te325 in (")", "]", "}") or (_te325 == "end" and _e325 in _bk325):
                    _dp325 += 1
                elif _te325 in ("(", "[", "{") or (_te325 in ("begin", "try", "match")
                                                   and _e325 in _bk325):
                    if _dp325 == 0:
                        _end325 = (_mt325.get(_e325, _z325) if _te325 in ("(", "[", "{")
                                   else _bk325.get(_e325, _z325))
                        break
                    _dp325 -= 1
                _e325 -= 1
            for _x325 in _nb325:
                _bg325.append((_x325, _q325, _end325))
        elif _tk325 in ("|", "with"):
            _j325 = _k325 + 1
            _pv325 = []
            while (_j325 < _N325 and _toks325[_j325] not in ("->", "=", "}", ";", "in", "|",
                                                             "end", "with")):
                _pv325.append(_toks325[_j325])
                _j325 += 1
            if _j325 < _N325 and _toks325[_j325] == "->":
                _bo325 = _inb325[_k325]
                _ae325 = (_bk325[_bo325] if _bo325 >= 0 and _bo325 in _bk325
                          and _bk325[_bo325] > _k325 else _dstart325[_dd325 + 1])
                _q325 = _j325 + 1
                while _q325 < _ae325:
                    if _toks325[_q325] in ("(", "[", "{") and _q325 in _mt325:
                        _q325 = _mt325[_q325] + 1
                        continue
                    if (_q325 in _bk325 and _toks325[_q325] != "end"
                            and _bk325[_q325] > _q325):
                        _q325 = _bk325[_q325] + 1
                        continue
                    if _toks325[_q325] == "|":
                        break
                    _q325 += 1
                for _x325 in _pv325:
                    if _re325.match(r"[a-z_][A-Za-z_0-9']*$", _x325):
                        _bg325.append((_x325, _k325, _q325))
        elif _tk325 in ("fun", "forall", "exists"):
            _e325 = _k325 - 1
            _dp325 = 0
            while _e325 >= 0:
                if _toks325[_e325] in (")", "]", "}"):
                    _dp325 += 1
                elif _toks325[_e325] in ("(", "[", "{"):
                    if _dp325 == 0:
                        break
                    _dp325 -= 1
                _e325 -= 1
            _end325 = _mt325.get(_e325, _dstart325[_dd325 + 1]) if _e325 >= 0 else (
                _dstart325[_dd325 + 1])
            _j325 = _k325 + 1
            while _j325 < _N325 and _toks325[_j325] not in ("->", "."):
                if (_re325.match(r"[a-z_][A-Za-z_0-9']*$", _toks325[_j325])
                        and (_tk325 != "fun" or _toks325[_j325 - 1] == "(")):
                    _bg325.append((_toks325[_j325], _k325, _end325))
                _j325 += 1
    _dparams325 = {}
    _dbyname325 = {}
    for _dd325, _a325 in _hdr325.items():
        if _toks325[_dstart325[_dd325]] in ("let", "val") and _dd325 in _dname325:
            _dbyname325.setdefault(_dname325[_dd325], _dd325)
        # header parameters `(x: t)` / `(x y: t)` of a declaration, in order
        for _j325 in range(_dstart325[_dd325], _a325):
            if (_toks325[_j325] == ":" and _j325 > 0
                    and _re325.match(r"[a-z_][A-Za-z_0-9']*$", _toks325[_j325 - 1])):
                _q325 = _j325 - 1
                _pn325 = []
                while _q325 >= 0 and _re325.match(r"[a-z_][A-Za-z_0-9']*$", _toks325[_q325]):
                    _bd325.setdefault(_dd325, set()).add(_toks325[_q325])
                    _pn325.insert(0, _toks325[_q325])
                    _q325 -= 1
                if _q325 >= 0 and _toks325[_q325] == "(":
                    _dparams325.setdefault(_dd325, []).extend(_pn325)
    # user functions/methods annotated `-> int` / `-> bool` (their bodies are verified at
    # an int type here, so an unconstrained stub of a call to one is int-typed unless that
    # body returns a fallback, tracked below)
    _udef325 = set()
    if _tree325 is not None:
        for _a325 in _ast325.walk(_tree325):
            if (isinstance(_a325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef))
                    and isinstance(_a325.returns, _ast325.Name)
                    and _a325.returns.id in ("int", "bool")):
                _udef325.add(_wid325(_a325.name))
    _modw325 = {_wid325(k) for k in _imod325}
    _pydefs325 = set()
    if _tree325 is not None:
        for _a325 in _ast325.walk(_tree325):
            if isinstance(_a325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef)):
                _pydefs325.add(_wid325(_a325.name))
    for _x325 in list(_dbyname325):
        if (_x325 in _S325 or _x325 in _other325 or not (
                _x325 in _pydefs325 or any(_x325.endswith("__" + d) for d in _pydefs325))):
            del _dbyname325[_x325]
    # ROUTE #330 — MORE ORIGINS, each a value lowered to an `int` that is NOT an int:
    # (a) an INSTANCE FIELD whose WhyML record label is typed `int` while a class-level or
    #     `self.<f> = ..` initialiser / annotation of it is SHOWN non-int (a float / str /
    #     None / bytes literal, an f-string, a display, `/`, a float / str / repr call, an
    #     imported value, a non-int global, a parameter annotated non-int, an annotation
    #     other than `int` / `bool`): `self.r = 2.5` lowers to `{ r = (any int) }`,
    #     `self.s = "ab"` to `{ s = 0 }`, `self.r = None` to `{ r = pycsl_none }`, and
    #     `c.r % 1 == 0`, `int(c.r) == c.r`, `c.s * 0 == 0` proved (witnesses 4341-4345);
    #     with `no_exception \all`, `c.r * 0` over a None field proved no TypeError (route
    #     #331, 4351-4353). Fields left unshown (an unannotated parameter) stay int (#325
    #     residual 1: making every attribute of a parameter / local an origin refused 13
    #     mirror files).
    # (b) MODEL OPERATIONS that encode a string as an int (`repr_conv`, `format_conv`,
    #     `str_of_int_hash`, `str_of_bool_hash`, `str_of_value_op`, the int `str_concat` /
    #     `join` of the f-string joiner): `repr(n) * 0 == 0`, `f"{n}" * 0 == 0` proved
    #     (4346, 4347). Strings ARE reflexive, so `=` / `<>` stay admitted anywhere for them.
    # (c) the ELEMENTS of a parameter annotated with a BARE container (`list`, `List`,
    #     `Sequence`, `tuple`, ...): element type unknown, lowered int (4348, 4349).
    # (d) a `complex` annotation anywhere is typed `int` (`z * z != -1` proved, 4350):
    #     refused outright below.
    _fld325 = {}    # WhyML field label -> origin
    _el325 = {}     # (decl, parameter) -> origin (its ELEMENTS)
    _cx325 = None
    _lblty325 = {}
    for _dd325 in range(len(_dstart325) - 1):
        _a325, _z325 = _dstart325[_dd325], _dstart325[_dd325 + 1]
        if _a325 < _z325 and _toks325[_a325] == "type":
            for _k325 in range(_a325, _z325 - 2):
                if (_toks325[_k325 + 1] == ":" and _toks325[_k325 - 1] in ("{", ";", "mutable")
                        and _re325.match(r"[a-z_][A-Za-z_0-9']*$", _toks325[_k325])):
                    _q325 = _k325 + 2
                    _ty325 = []
                    while _q325 < _z325 and _toks325[_q325] not in (";", "}"):
                        _ty325.append(_toks325[_q325])
                        _q325 += 1
                    _lblty325.setdefault(_toks325[_k325], []).append(" ".join(_ty325))
    _rt330 = getattr(transpiler, "_record_types", None) or {}
    _NIC330 = {"float", "str", "repr", "complex", "list", "dict", "set", "tuple", "bytes",
               "format", "hex", "oct", "bin", "chr", "ascii", "frozenset", "bytearray",
               "sorted", "reversed", "map", "filter", "zip", "enumerate", "input", "open"}
    _BARE330 = {"list", "List", "Sequence", "Iterable", "tuple", "Tuple", "MutableSequence",
                "Collection"}
    # ROUTE #334: BARE-CONTAINER-INT also covers a bare `dict` / `Dict` / `Mapping`: its
    # values are lowered `option int` whatever their type (k01); strict mode refuses reads
    _BAREDICT334 = {"dict", "Dict", "Mapping", "MutableMapping"}
    _iflo325 = set()    # ROUTE #334: origins of an integral-float field (comparisons only)
    _mvorg325 = set()   # ROUTE #334: origins standing for a dict's VALUES
    _octok334 = {}      # ROUTE #334: opaque class (WhyML name) -> provably-int fields
    if _tree325 is not None:
        _nif330 = {}    # python class name -> fields shown non-int
        _bas330 = {}    # python class name -> base class names
        _ini334 = {}    # python class name -> [(field, annotation, value, def, kind)]
        _meth334 = {}   # id(method def) -> (class name, `self` parameter name)
        _ndv334 = {}    # python class name -> dict fields whose VALUES are not provably int
        _cnt338 = set()  # ROUTE #338: id(store node) already counted as a `self` store
        for _a325 in _ast325.walk(_tree325):
            if isinstance(_a325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef,
                                  _ast325.AnnAssign)):
                for _an325 in ([_a325.returns] + [x.annotation for x in (
                        _a325.args.posonlyargs + _a325.args.args + _a325.args.kwonlyargs
                        + [y for y in (_a325.args.vararg, _a325.args.kwarg) if y])]
                               if isinstance(_a325, (_ast325.FunctionDef,
                                                     _ast325.AsyncFunctionDef))
                               else [_a325.annotation] if isinstance(_a325, _ast325.AnnAssign)
                               else []):
                    for _x325 in (_ast325.walk(_an325) if _an325 is not None else ()):
                        if ((isinstance(_x325, _ast325.Name) and _x325.id == "complex")
                                or (isinstance(_x325, _ast325.Constant)
                                    and isinstance(_x325.value, str)
                                    and "complex" in _x325.value)):
                            _cx325 = getattr(_a325, "name", "?")
            if isinstance(_a325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef)):
                # (c) bare-container parameters: their decl(s) and WhyML name
                for _x325 in (_a325.args.posonlyargs + _a325.args.args
                              + _a325.args.kwonlyargs):
                    _an325 = _x325.annotation
                    if getattr(args, "strict_bare_containers", False) and (
                            (isinstance(_an325, _ast325.Name)
                             and _an325.id in _BARE330 | _BAREDICT334)
                            or (isinstance(_an325, _ast325.Attribute)
                                and _an325.attr in _BARE330 | _BAREDICT334)):
                        for _dd325, _n2325 in _dname325.items():
                            if (_n2325 == _wid325(_a325.name)
                                    or _n2325.endswith("__" + _wid325(_a325.name))):
                                _el325[(_dd325, _wid325(_x325.arg))] = (
                                    ("a value" if getattr(_an325, "id", getattr(
                                        _an325, "attr", "")) in _BAREDICT334
                                     else "an element") + " of '" + _x325.arg + "' (bare `"
                                    + _ast325.unparse(_an325) + "` annotation)")
                                if getattr(_an325, "id", getattr(_an325, "attr", "")) in (
                                        _BAREDICT334):
                                    _mvorg325.add(_el325[(_dd325, _wid325(_x325.arg))])
            if not isinstance(_a325, _ast325.ClassDef):
                continue
            _bas330[_a325.name] = [b.id for b in _a325.bases if isinstance(b, _ast325.Name)]
            # ROUTE #334 — EVERY store of a field of the class, as (field, annotation, value,
            # def, kind): kind "=" a store of the field's value, "[]" a store of one of its
            # (dict) VALUES. A target paired with no single value (an unpaired tuple
            # element, a starred element, a `for` / `with` target) has value None (unknown).
            # `self.r, self.s = 2.5, 1` used to escape the classification (o03).
            _ini330 = _ini334.setdefault(_a325.name, [])
            for _s325 in _a325.body:
                if isinstance(_s325, _ast325.AnnAssign) and isinstance(_s325.target,
                                                                       _ast325.Name):
                    _ini330.append((_s325.target.id, _s325.annotation, _s325.value, None, "="))
                elif isinstance(_s325, _ast325.Assign):
                    _pr334 = [(t, _s325.value) for t in _s325.targets]
                    while _pr334:
                        _t325, _v325 = _pr334.pop()
                        if isinstance(_t325, _ast325.Name):
                            _ini330.append((_t325.id, None, _v325, None, "="))
                        elif (isinstance(_t325, (_ast325.Tuple, _ast325.List))
                              and isinstance(_v325, (_ast325.Tuple, _ast325.List))
                              and len(_t325.elts) == len(_v325.elts)
                              and not any(isinstance(x, _ast325.Starred)
                                          for x in _t325.elts + _v325.elts)):
                            _pr334.extend(zip(_t325.elts, _v325.elts))
                        else:
                            _ini330.extend((x.id, None, None, None, "=")
                                           for x in _ast325.walk(_t325)
                                           if isinstance(x, _ast325.Name)
                                           and isinstance(x.ctx, _ast325.Store))
                elif (isinstance(_s325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef))
                      and _s325.args.args):
                    _sf330 = _s325.args.args[0].arg
                    _meth334[id(_s325)] = (_a325.name, _sf330)
                    for _x325 in _ast325.walk(_s325):
                        _pr334 = []
                        if isinstance(_x325, _ast325.Assign):
                            _pr334 = [(t, _x325.value, None) for t in _x325.targets]
                        elif isinstance(_x325, _ast325.AnnAssign):
                            _pr334 = [(_x325.target, _x325.value, _x325.annotation)]
                        elif isinstance(_x325, _ast325.AugAssign):
                            # the old value is covered by the other stores (induction)
                            _pr334 = [(_x325.target, _ast325.BinOp(
                                left=_ast325.Constant(value=0), op=_x325.op,
                                right=_x325.value), None)]
                        elif isinstance(_x325, (_ast325.For, _ast325.AsyncFor)):
                            _pr334 = [(_x325.target, _ast325.Constant(value=0) if (
                                isinstance(_x325.iter, _ast325.Call)
                                and isinstance(_x325.iter.func, _ast325.Name)
                                and _x325.iter.func.id == "range") else None, None)]
                        elif isinstance(_x325, (_ast325.With, _ast325.AsyncWith)):
                            _pr334 = [(w.optional_vars, None, None) for w in _x325.items
                                      if w.optional_vars is not None]
                        elif isinstance(_x325, _ast325.comprehension):
                            _pr334 = [(_x325.target, None, None)]
                        elif (isinstance(_x325, _ast325.Call)
                              and isinstance(_x325.func, _ast325.Name)
                              and _x325.func.id == "setattr" and len(_x325.args) >= 2
                              and isinstance(_x325.args[0], _ast325.Name)
                              and _x325.args[0].id == _sf330):
                            _cnt338.add(id(_x325))
                            if (isinstance(_x325.args[1], _ast325.Constant)
                                    and isinstance(_x325.args[1].value, str)):
                                _ini330.append((_x325.args[1].value, None, _x325.args[2]
                                                if len(_x325.args) > 2 else None, _s325, "="))
                            else:
                                _ini330.append(("*", None, None, _s325, "="))
                        elif (isinstance(_x325, _ast325.Call)
                              and isinstance(_x325.func, _ast325.Attribute)
                              and isinstance(_x325.func.value, _ast325.Attribute)
                              and isinstance(_x325.func.value.value, _ast325.Name)
                              and _x325.func.value.value.id == _sf330
                              and _x325.func.attr in ("update", "setdefault", "__setitem__",
                                                      "fromkeys", "__ior__")):
                            _cnt338.add(id(_x325))
                            _ini330.append((_x325.func.value.attr, None, _x325.args[1] if (
                                _x325.func.attr in ("setdefault", "__setitem__")
                                and len(_x325.args) == 2) else None, _s325, "[]"))
                        while _pr334:
                            _t325, _v325, _an334 = _pr334.pop()
                            if (isinstance(_t325, _ast325.Attribute)
                                    and isinstance(_t325.value, _ast325.Name)
                                    and _t325.value.id == _sf330):
                                _cnt338.add(id(_t325))
                                _ini330.append((_t325.attr, _an334, _v325, _s325, "="))
                                if isinstance(_x325, _ast325.AugAssign):
                                    _ini330.append((_t325.attr, None, None, _s325, "[]"))
                            elif (isinstance(_t325, _ast325.Subscript)
                                  and isinstance(_t325.value, _ast325.Attribute)
                                  and isinstance(_t325.value.value, _ast325.Name)
                                  and _t325.value.value.id == _sf330):
                                _cnt338.add(id(_t325))
                                _ini330.append((_t325.value.attr, None, _v325, _s325, "[]"))
                            elif isinstance(_t325, (_ast325.Tuple, _ast325.List)):
                                if (isinstance(_v325, (_ast325.Tuple, _ast325.List))
                                        and len(_t325.elts) == len(_v325.elts)
                                        and not any(isinstance(x, _ast325.Starred)
                                                    for x in _t325.elts + _v325.elts)):
                                    _pr334.extend((a, b, None)
                                                  for a, b in zip(_t325.elts, _v325.elts))
                                else:
                                    _pr334.extend((a, None, None) for a in _t325.elts)
                            elif isinstance(_t325, _ast325.Starred):
                                _pr334.append((_t325.value, None, None))
        # ROUTE #334 — a field is classified by whether EVERY value stored into it is
        # PROVABLY an int (type inference over the initialiser: int / bool literals, int
        # operators over int operands, `**` by a non-negative literal, locals of the
        # storing def whose every binding is provably int, int-annotated parameters,
        # known-int globals, other provably-int fields, `len` / `int` / `ord` / `hash` /
        # `id` / `round(x)`, `abs` / `min` / `max` of ints, a user function / method
        # annotated `-> int` / `bool`, a documented int call / attribute of a module).
        # Anything not provably int taints the label: #330 whitelisted non-int SHAPES, so
        # `x = 2.5; self.r = x` (f02), a walrus (f20), `2 ** -1` (f06/f22), a str / None
        # through a local (f18/f24/f25) all left the field an int. Kinds: "none" (a None
        # leaf: `=` admitted, route #331), "ifloat" (an INTEGRAL float literal: only a
        # direct comparison operand is admitted — CPython compares int / float exactly,
        # while `+`, `*`, `str * r`, `range(r)` are not int-faithful: p01, p10), "other".
        # The dict mode classifies a dict field's VALUES (its display values, its `[k] =`
        # stores) the same way (k04). An unannotated parameter stays int (#325 residual
        # 1: the record literal is built from the call-site argument, which WhyML types).
        _env334 = {}    # id(def) -> (parameters {name: annotation | "*"}, locals {name: [v]})
        _top334 = {}    # module-level def name -> returns annotation
        for _a325 in (_tree325.body if _tree325 is not None else []):
            if isinstance(_a325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef)):
                _top334[_a325.name] = _a325.returns
        for _a325 in _ast325.walk(_tree325):
            if not isinstance(_a325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef)):
                continue
            _pp334 = {x.arg: x.annotation for x in (_a325.args.posonlyargs + _a325.args.args
                                                     + _a325.args.kwonlyargs)}
            for _x325 in (_a325.args.vararg, _a325.args.kwarg):
                if _x325 is not None:
                    _pp334[_x325.arg] = "*"
            _ll334 = {}
            _lw334 = list(_a325.body)
            while _lw334:
                _n325 = _lw334.pop()
                if isinstance(_n325, (_ast325.FunctionDef, _ast325.AsyncFunctionDef,
                                      _ast325.ClassDef)):
                    _ll334.setdefault(_n325.name, []).append(None)
                    continue
                if isinstance(_n325, (_ast325.Lambda, _ast325.ListComp, _ast325.SetComp,
                                      _ast325.DictComp, _ast325.GeneratorExp)):
                    _lw334.extend(x for x in _ast325.walk(_n325)
                                  if isinstance(x, _ast325.NamedExpr))
                    continue
                _pr334 = []
                if isinstance(_n325, _ast325.Assign):
                    _pr334 = [(t, _n325.value) for t in _n325.targets]
                elif isinstance(_n325, _ast325.AnnAssign):
                    _pr334 = ([] if (isinstance(_n325.annotation, _ast325.Name)
                                     and _n325.annotation.id in ("int", "bool"))
                              else [(_n325.target, ("ann", _n325.annotation))])
                    if _n325.value is not None:
                        _pr334.append((_n325.target, _n325.value))
                elif isinstance(_n325, _ast325.AugAssign):
                    _pr334 = [(_n325.target, _ast325.BinOp(
                        left=_ast325.Constant(value=0), op=_n325.op, right=_n325.value))]
                elif isinstance(_n325, (_ast325.For, _ast325.AsyncFor)):
                    _pr334 = [(_n325.target, _ast325.Constant(value=0) if (
                        isinstance(_n325.iter, _ast325.Call)
                        and isinstance(_n325.iter.func, _ast325.Name)
                        and _n325.iter.func.id == "range") else None)]
                elif isinstance(_n325, _ast325.NamedExpr):
                    _pr334 = [(_n325.target, _n325.value)]
                elif isinstance(_n325, (_ast325.With, _ast325.AsyncWith)):
                    _pr334 = [(w.optional_vars, None) for w in _n325.items
                              if w.optional_vars is not None]
                elif isinstance(_n325, (_ast325.Global, _ast325.Nonlocal)):
                    _ll334.update({g: [None] for g in _n325.names})
                elif isinstance(_n325, (_ast325.Import, _ast325.ImportFrom)):
                    for _al325 in _n325.names:
                        _ll334.setdefault((_al325.asname or _al325.name).split(".")[0],
                                          []).append(None)
                for _x325 in ("name", "rest"):
                    if (isinstance(getattr(_n325, _x325, None), str) and isinstance(
                            _n325, (_ast325.ExceptHandler, _ast325.MatchAs,
                                    _ast325.MatchStar, _ast325.MatchMapping))):
                        _ll334.setdefault(getattr(_n325, _x325), []).append(None)
                while _pr334:
                    _t325, _v325 = _pr334.pop()
                    if isinstance(_t325, _ast325.Name):
                        _ll334.setdefault(_t325.id, []).append(_v325)
                    elif isinstance(_t325, (_ast325.Tuple, _ast325.List)):
                        if (isinstance(_v325, (_ast325.Tuple, _ast325.List))
                                and len(_t325.elts) == len(_v325.elts)
                                and not any(isinstance(x, _ast325.Starred)
                                            for x in _t325.elts + _v325.elts)):
                            _pr334.extend(zip(_t325.elts, _v325.elts))
                        else:
                            _pr334.extend((a, None) for a in _t325.elts)
                    elif isinstance(_t325, _ast325.Starred):
                        _pr334.append((_t325.value, None))
                _lw334.extend(_ast325.iter_child_nodes(_n325))
            _env334[id(_a325)] = (_pp334, _ll334)
        # an annotation declaring int / bool dict VALUES, or a set (its map values are
        # the presence marker `Some 0`)
        _dia334 = set()
        for _a325 in _ast325.walk(_tree325):
            if not isinstance(_a325, _ast325.Subscript):
                continue
            _x325 = getattr(_a325.value, "id", getattr(_a325.value, "attr", ""))
            if ((_x325 in ("Set", "set", "FrozenSet", "frozenset", "AbstractSet",
                           "MutableSet"))
                    or (_x325 in ("Dict", "dict", "Mapping", "MutableMapping",
                                  "DefaultDict", "defaultdict", "OrderedDict")
                        and isinstance(_a325.slice, _ast325.Tuple)
                        and len(_a325.slice.elts) == 2
                        and isinstance(_a325.slice.elts[1], _ast325.Name)
                        and _a325.slice.elts[1].id in ("int", "bool"))):
                _dia334.add(id(_a325))
        # ROUTE #338 — a field of an instance of a class of this file may be stored from
        # ANY code, not only from the class, its bases and its descendants: module level,
        # `__main__`, another function, a method of another class (`c.r = 0.5`,
        # `setattr(c, "r", .25)`, `c.d["a"] = 0.5`, `del c.r`). Each such store joins the
        # stores of the receiver's class when the receiver is a parameter annotated with a
        # class of this file (or a local every binding of which constructs one), is
        # dropped when that annotation names a type of no class of this file (annotation
        # trust, as for every typed parameter), and otherwise joins EVERY class of this
        # file that stores a field of that name (over-approximation). A deletion is a
        # store of a non-int value; a dynamic attribute name (`setattr(c, n, v)`, a
        # `__dict__` / `vars()` store) taints every field of the classes it may reach.
        _ext338 = []    # (receiver class | None, field | "*", value, def, kind)
        # the names UNVERIFIED code of this module mentions: module-level statements
        # (`if __name__ == "__main__":` included), class bodies, decorators, defaults —
        # everything but the bodies of defs (lowered and verified)
        _uv338 = set()
        _st338 = list(_tree325.body) if _tree325 is not None else []
        while _st338:
            _n338 = _st338.pop()
            if isinstance(_n338, (_ast325.FunctionDef, _ast325.AsyncFunctionDef)):
                _st338.extend(_n338.decorator_list + _n338.args.defaults + [
                    d for d in _n338.args.kw_defaults if d is not None])
                continue
            if isinstance(_n338, _ast325.ClassDef):
                # its bases only NAME classes; its body and decorators run
                _st338.extend(_n338.body + _n338.decorator_list)
                continue
            if isinstance(_n338, _ast325.Name):
                _uv338.add(_n338.id)
            elif isinstance(_n338, _ast325.Attribute):
                _uv338.add(_n338.attr)
            _st338.extend(_ast325.iter_child_nodes(_n338))
        _st338 = [(_n325, None) for _n325 in (_tree325.body if _tree325 is not None else [])]
        while _st338:
            _n338, _fd338 = _st338.pop()
            _pr338 = []     # (target, value)
            if isinstance(_n338, _ast325.Assign):
                _pr338 = [(t, _n338.value) for t in _n338.targets]
            elif isinstance(_n338, _ast325.AnnAssign):
                _pr338 = [(_n338.target, _n338.value)]
            elif isinstance(_n338, _ast325.AugAssign):
                _pr338 = [(_n338.target, _ast325.BinOp(left=_ast325.Constant(value=0),
                                                         op=_n338.op, right=_n338.value)),
                          (("[]", _n338.target), None)]
            elif isinstance(_n338, (_ast325.For, _ast325.AsyncFor)):
                _pr338 = [(_n338.target, _ast325.Constant(value=0) if (
                    isinstance(_n338.iter, _ast325.Call)
                    and isinstance(_n338.iter.func, _ast325.Name)
                    and _n338.iter.func.id == "range") else None)]
            elif isinstance(_n338, (_ast325.With, _ast325.AsyncWith)):
                _pr338 = [(w.optional_vars, None) for w in _n338.items
                          if w.optional_vars is not None]
            elif isinstance(_n338, _ast325.comprehension):
                _pr338 = [(_n338.target, None)]
            elif isinstance(_n338, _ast325.Delete):
                _pr338 = [(t, _ast325.Constant(value="\0del")) for t in _n338.targets]
            elif isinstance(_n338, _ast325.Call) and id(_n338) not in _cnt338:
                _cf338 = _n338.func
                _nm338 = (_cf338.id if isinstance(_cf338, _ast325.Name) else
                          _cf338.attr if (isinstance(_cf338, _ast325.Attribute)
                                          and isinstance(_cf338.value, _ast325.Name)
                                          and _cf338.value.id == "object") else "")
                if _nm338 in ("setattr", "delattr", "__setattr__", "__delattr__") and (
                        len(_n338.args) >= 2):
                    _v338 = (_ast325.Constant(value="\0del") if "del" in _nm338
                             else _n338.args[2] if len(_n338.args) > 2 else None)
                    _pr338 = [(_ast325.Attribute(value=_n338.args[0], attr=(
                        _n338.args[1].value if isinstance(_n338.args[1], _ast325.Constant)
                        and isinstance(_n338.args[1].value, str) else "*")), _v338)]
                elif (isinstance(_cf338, _ast325.Attribute)
                      and isinstance(_cf338.value, _ast325.Attribute)
                      and _cf338.attr in ("update", "setdefault", "__setitem__", "fromkeys",
                                          "__ior__")):
                    _pr338 = [(("[]", _cf338.value), _n338.args[1] if (
                        _cf338.attr in ("setdefault", "__setitem__")
                        and len(_n338.args) == 2) else None)]
            while _pr338:
                _t338, _v338 = _pr338.pop()
                if isinstance(_t338, tuple):
                    # ("[]", field): a store of one of the VALUES of a (dict) field
                    if (isinstance(_t338[1], _ast325.Attribute)
                            and id(_t338[1]) not in _cnt338):
                        _ext338.append((_t338[1].value, "*" if _t338[1].attr == "__dict__"
                                        else _t338[1].attr, _v338, _fd338, "[]"))
                elif isinstance(_t338, _ast325.Attribute) and id(_t338) not in _cnt338:
                    _ext338.append((_t338.value, _t338.attr, _v338, _fd338, "="))
                elif (isinstance(_t338, _ast325.Subscript) and id(_t338) not in _cnt338
                      and isinstance(_t338.value, _ast325.Attribute)):
                    _ext338.append((_t338.value.value, "*" if _t338.value.attr == "__dict__"
                                    else _t338.value.attr, _v338, _fd338, "[]"))
                elif (isinstance(_t338, _ast325.Subscript) and isinstance(
                        _t338.value, _ast325.Call) and isinstance(_t338.value.func,
                                                                  _ast325.Name)
                      and _t338.value.func.id == "vars" and _t338.value.args):
                    _ext338.append((_t338.value.args[0], "*", None, _fd338, "="))
                elif isinstance(_t338, (_ast325.Tuple, _ast325.List)):
                    if (isinstance(_v338, (_ast325.Tuple, _ast325.List))
                            and len(_t338.elts) == len(_v338.elts)
                            and not any(isinstance(x, _ast325.Starred)
                                        for x in _t338.elts + _v338.elts)):
                        _pr338.extend(zip(_t338.elts, _v338.elts))
                    else:
                        _pr338.extend((a, None) for a in _t338.elts)
                elif isinstance(_t338, _ast325.Starred):
                    _pr338.append((_t338.value, None))
            _st338.extend((c, _n338 if isinstance(_n338, (
                _ast325.FunctionDef, _ast325.AsyncFunctionDef, _ast325.Lambda)) else _fd338)
                for c in _ast325.iter_child_nodes(_n338))
        for _r338, _f338, _v338, _fd338, _kd338 in _ext338:
            # the receiver's class: a `self` of a method, a typed parameter, a local
            # constructing a class of this file
            _ev338 = _env334.get(id(_fd338)) if _fd338 is not None else None
            _oc338 = "?"
            if isinstance(_r338, _ast325.Name) and _ev338 is not None:
                if id(_fd338) in _meth334 and _r338.id == _meth334[id(_fd338)][1]:
                    _oc338 = _meth334[id(_fd338)][0]
                elif _r338.id in _ev338[1]:
                    _oc338 = {(v.func.id if isinstance(v, _ast325.Call)
                               and isinstance(v.func, _ast325.Name)
                               and v.func.id in _ini334 else "?") for v in _ev338[1][_r338.id]}
                    _oc338 = next(iter(_oc338)) if len(_oc338) == 1 else "?"
                elif _r338.id in _ev338[0]:
                    # a parameter annotated `K` (a class of this file) holds a K; one
                    # annotated with builtin scalar / container types only holds no
                    # instance of a class of this file (annotation trust); anything
                    # else (unannotated, `object`, `Any`, an imported type) may hold one
                    _a338 = _ev338[0][_r338.id]
                    _a338 = (_ast325.Name(id=_a338.value) if isinstance(_a338, _ast325.Constant)
                             and isinstance(_a338.value, str) else _a338)
                    if isinstance(_a338, _ast325.Name) and _a338.id in _ini334:
                        _oc338 = _a338.id
                    elif isinstance(_a338, _ast325.AST) and all(
                            x.id in ("int", "bool", "str", "float", "bytes", "complex",
                                     "list", "dict", "set", "frozenset", "tuple", "List",
                                     "Dict", "Set", "FrozenSet", "Tuple", "Optional",
                                     "Sequence", "Mapping", "None")
                            for x in _ast325.walk(_a338) if isinstance(x, _ast325.Name)
                    ) and not any(isinstance(x, _ast325.Attribute) or (
                            isinstance(x, _ast325.Constant) and x.value is not None)
                            for x in _ast325.walk(_a338)):
                        _oc338 = "!"
            for _cn338 in ([_oc338] if _oc338 in _ini334 else [] if _oc338 != "?"
                           else [c for c in _ini334 if _f338 == "*" or any(
                               e[0] == _f338 for e in _ini334[c])]):
                _ini334[_cn338].append((_f338, None, None if _f338 == "*" else _v338,
                                        _fd338, _kd338))
        _allc334 = {}   # class -> its stores and its bases' stores
        _mint334 = {}   # class -> methods (own / bases) annotated `-> int` / `bool`
        for _cn334 in _ini334:
            _cl330 = [_cn334]
            _seen330 = set()
            _allc334[_cn334] = []
            _mint334[_cn334] = set()
            while _cl330:
                _x325 = _cl330.pop()
                if _x325 in _seen330:
                    continue
                _seen330.add(_x325)
                _allc334[_cn334].extend(_ini334.get(_x325, []))
                _cl330.extend(_bas330.get(_x325, []))
            # a receiver typed as this class may hold an instance of a SUBCLASS: the
            # stores of every descendant count too (i01: `S(B)` stores `self.r = 0.5`)
            for _d334 in _ini334:
                _cl330 = list(_bas330.get(_d334, []))
                _sd334 = set()
                while _cl330:
                    _x325 = _cl330.pop()
                    if _x325 in _sd334:
                        continue
                    _sd334.add(_x325)
                    _cl330.extend(_bas330.get(_x325, []))
                if _cn334 in _sd334 and _d334 not in _seen330:
                    _allc334[_cn334].extend(_ini334.get(_d334, []))
            for _cd334 in _ast325.walk(_tree325):
                if isinstance(_cd334, _ast325.ClassDef) and _cd334.name in _seen330:
                    _mint334[_cn334].update(m.name for m in _cd334.body if isinstance(
                        m, (_ast325.FunctionDef, _ast325.AsyncFunctionDef))
                        and isinstance(m.returns, _ast325.Name)
                        and m.returns.id in ("int", "bool"))
        _isfield334 = {_a325.asname or _a325.name for _a325 in _ast325.walk(_tree325)
                       if isinstance(_a325, _ast325.alias) and _a325.name == "field"}
        for _cn334 in _ini334:
            for _f330 in sorted({e[0] for e in _ini334[_cn334]} - {"*"}):
                for _md334 in ("=", "[]"):
                    _fl334 = set()
                    _wl334 = []     # (expression, def, "s" scalar value | "d" a dict)
                    _vis334 = set()
                    _wl334.append((_ast325.Attribute(value=_ast325.Name(id="\0self"),
                                                     attr=_f330), None,
                                   "s" if _md334 == "=" else "d"))
                    while _wl334 and "other" not in _fl334:
                        _e325, _fd334, _wm334 = _wl334.pop()
                        _ev334 = _env334.get(id(_fd334)) if _fd334 is not None else None
                        _sl334 = (_meth334[id(_fd334)][1] if _fd334 is not None
                                  and id(_fd334) in _meth334 else None)
                        # the class of an object-valued name: `self`, a parameter
                        # annotated with a class of this file, a local bound to `K(..)`
                        _oc334 = None
                        if (isinstance(_e325, _ast325.Attribute)
                                and isinstance(_e325.value, _ast325.Name)):
                            _x325 = _e325.value.id
                            if _x325 == "\0self":
                                _oc334 = _cn334
                            elif _x325 == _sl334:
                                _oc334 = _meth334[id(_fd334)][0]
                            elif _ev334 is not None and _x325 in _ev334[1]:
                                _oc334 = {(v.func.id if isinstance(v, _ast325.Call)
                                           and isinstance(v.func, _ast325.Name)
                                           and v.func.id in _ini334 else None)
                                          for v in _ev334[1][_x325]}
                                _oc334 = (next(iter(_oc334)) if len(_oc334) == 1
                                          else None)
                            elif _ev334 is not None and _x325 in _ev334[0]:
                                _a334 = _ev334[0][_x325]
                                _a334 = (_a334.id if isinstance(_a334, _ast325.Name)
                                         else _a334.value if isinstance(
                                             _a334, _ast325.Constant) else None)
                                _oc334 = _a334 if _a334 in _ini334 else None
                        if _oc334 is not None:
                            # a FIELD of a class of this file: all of its stores
                            if (_wm334, _oc334, _e325.attr) in _vis334:
                                continue
                            _vis334.add((_wm334, _oc334, _e325.attr))
                            _hit334 = False
                            for _f2334, _an325, _v325, _fd2334, _kd334 in _allc334[_oc334]:
                                if _f2334 == "*":
                                    _fl334.add("other")
                                    continue
                                if _f2334 != _e325.attr:
                                    continue
                                _hit334 = True
                                if _wm334 == "d" and _kd334 == "[]":
                                    _wl334.append((_v325, _fd2334, "s"))
                                    continue
                                if _kd334 != "=":
                                    continue
                                _on330 = (isinstance(_an325, _ast325.Subscript)
                                          and isinstance(_an325.value, _ast325.Name)
                                          and _an325.value.id in ("Optional", "Union")
                                          and all((isinstance(x, _ast325.Name)
                                                   and x.id in ("int", "bool"))
                                                  or (isinstance(x, _ast325.Constant)
                                                      and x.value is None)
                                                  for x in (_an325.slice.elts if isinstance(
                                                      _an325.slice, _ast325.Tuple)
                                                      else [_an325.slice]))) or (
                                    isinstance(_an325, _ast325.BinOp)
                                    and isinstance(_an325.op, _ast325.BitOr)
                                    and all((isinstance(x, _ast325.Name)
                                             and x.id in ("int", "bool"))
                                            or (isinstance(x, _ast325.Constant)
                                                and x.value is None)
                                            for x in (_an325.left, _an325.right)))
                                if _an325 is None:
                                    pass
                                elif _wm334 == "d":
                                    if id(_an325) not in _dia334:
                                        _fl334.add("other")
                                elif _on330:
                                    _fl334.add("none")
                                elif not (
                                        (isinstance(_an325, _ast325.Name)
                                         and _an325.id in ("int", "bool"))
                                        or (isinstance(_an325, _ast325.Constant)
                                            and _an325.value in ("int", "bool"))
                                        or (isinstance(_an325, _ast325.Subscript)
                                            and isinstance(_an325.value, _ast325.Name)
                                            and _an325.value.id in ("Final", "ClassVar")
                                            and isinstance(_an325.slice, _ast325.Name)
                                            and _an325.slice.id in ("int", "bool"))):
                                    _fl334.add("other")
                                if _v325 is None and _an325 is None:
                                    _fl334.add("unk")
                                elif _v325 is not None:
                                    _wl334.append((_v325, _fd2334, _wm334))
                            if not _hit334:
                                _fl334.add("unk")
                        elif isinstance(_e325, tuple):
                            # a local declared `x: T`: only a dict / set of int values
                            if not (_wm334 == "d" and id(_e325[1]) in _dia334):
                                _fl334.add("other")
                        elif _e325 is None:
                            _fl334.add("unk")
                        elif (isinstance(_e325, _ast325.Call) and (
                                (isinstance(_e325.func, _ast325.Name)
                                 and _e325.func.id in _isfield334)
                                or (isinstance(_e325.func, _ast325.Attribute)
                                    and _e325.func.attr == "field"
                                    and isinstance(_e325.func.value, _ast325.Name)
                                    and _imod325.get(_e325.func.value.id) == "dataclasses"))):
                            # `dataclasses.field(default=.. | default_factory=..)`
                            for _kw334 in _e325.keywords:
                                if _kw334.arg == "default":
                                    _wl334.append((_kw334.value, _fd334, _wm334))
                                elif _kw334.arg == "default_factory":
                                    if not (isinstance(_kw334.value, _ast325.Name)
                                            and _kw334.value.id in (
                                                ("int", "bool") if _wm334 == "s" else
                                                ("dict", "set", "frozenset"))):
                                        _fl334.add("unk")
                        elif _wm334 == "d":
                            if isinstance(_e325, _ast325.Constant) and _e325.value is None:
                                pass
                            elif isinstance(_e325, _ast325.Dict):
                                if any(k is None for k in _e325.keys):
                                    _fl334.add("other")
                                _wl334.extend((x, _fd334, "s") for x in _e325.values)
                            elif isinstance(_e325, _ast325.DictComp):
                                _wl334.append((_e325.value, _fd334, "s"))
                            elif isinstance(_e325, (_ast325.Set, _ast325.SetComp)):
                                pass
                            elif (isinstance(_e325, _ast325.Call)
                                  and isinstance(_e325.func, _ast325.Name)
                                  and ((_e325.func.id in ("set", "frozenset"))
                                       or (_e325.func.id == "dict" and not _e325.args
                                           and not _e325.keywords))
                                  and _e325.func.id not in _bind325):
                                pass
                            elif isinstance(_e325, _ast325.Name) and _ev334 is not None and (
                                    _e325.id in _ev334[1]):
                                if ("LD", id(_fd334), _e325.id) not in _vis334:
                                    _vis334.add(("LD", id(_fd334), _e325.id))
                                    _wl334.extend((x, _fd334, "d")
                                                  for x in _ev334[1][_e325.id])
                            elif isinstance(_e325, _ast325.Name) and _ev334 is not None and (
                                    _e325.id in _ev334[0]):
                                if not (_ev334[0][_e325.id] is None
                                        or id(_ev334[0][_e325.id]) in _dia334):
                                    _fl334.add("other")
                            else:
                                _fl334.add("other")
                        elif isinstance(_e325, _ast325.Constant):
                            if _e325.value is None:
                                _fl334.add("none")
                            elif (type(_e325.value) is float and _e325.value.is_integer()
                                  and abs(_e325.value) < 2 ** 53):
                                _fl334.add("ifloat")
                            elif type(_e325.value) not in (int, bool):
                                _fl334.add("other")
                        elif isinstance(_e325, _ast325.UnaryOp):
                            if not isinstance(_e325.op, _ast325.Not):
                                _wl334.append((_e325.operand, _fd334, "s"))
                        elif isinstance(_e325, _ast325.BinOp):
                            if isinstance(_e325.op, (_ast325.Add, _ast325.Sub, _ast325.Mult,
                                                     _ast325.FloorDiv, _ast325.Mod,
                                                     _ast325.LShift, _ast325.RShift,
                                                     _ast325.BitAnd, _ast325.BitOr,
                                                     _ast325.BitXor)):
                                _wl334.extend([(_e325.left, _fd334, "s"),
                                               (_e325.right, _fd334, "s")])
                            elif (isinstance(_e325.op, _ast325.Pow)
                                  and isinstance(_e325.right, _ast325.Constant)
                                  and type(_e325.right.value) is int
                                  and _e325.right.value >= 0):
                                _wl334.append((_e325.left, _fd334, "s"))
                            elif isinstance(_e325.op, _ast325.Div) or (
                                    isinstance(_e325.op, _ast325.Pow)
                                    and isinstance(_e325.right, (_ast325.Constant,
                                                                 _ast325.UnaryOp))):
                                _fl334.add("other")     # `/`, `2 ** -1`: a float (f06, f22)
                            else:
                                _fl334.add("unk")
                        elif isinstance(_e325, _ast325.BoolOp):
                            _wl334.extend((x, _fd334, "s") for x in _e325.values)
                        elif isinstance(_e325, _ast325.Compare):
                            pass
                        elif isinstance(_e325, _ast325.IfExp):
                            _wl334.extend([(_e325.body, _fd334, "s"),
                                           (_e325.orelse, _fd334, "s")])
                        elif isinstance(_e325, _ast325.NamedExpr):
                            _wl334.append((_e325.value, _fd334, "s"))
                        elif isinstance(_e325, _ast325.Name):
                            if _ev334 is not None and _e325.id in _ev334[1]:
                                if ("L", id(_fd334), _e325.id) not in _vis334:
                                    _vis334.add(("L", id(_fd334), _e325.id))
                                    _wl334.extend((x, _fd334, "s")
                                                  for x in _ev334[1][_e325.id])
                            elif _ev334 is not None and _e325.id in _ev334[0]:
                                _an325 = _ev334[0][_e325.id]
                                if _an325 == "*" or _e325.id == _sl334:
                                    _fl334.add("other")
                                elif _an325 is None:
                                    # ROUTE #338 (#325 residual 1): an UNANNOTATED
                                    # parameter takes the type of its argument. A
                                    # VERIFIED caller's argument is typed by WhyML (the
                                    # record literal `{ r = 0.5 }` is rejected), but
                                    # UNVERIFIED code of this module (module level,
                                    # `__main__`, a default, a decorator) is never
                                    # lowered: `U(0.5)` there makes the field a float.
                                    # So the parameter is of unknown type when that
                                    # code names the storing def, its class or a
                                    # descendant of it (the constructor is inherited).
                                    _nm338 = {_fd334.name} if _fd334 is not None else set()
                                    if _fd334 is not None and id(_fd334) in _meth334:
                                        _nm338.add(_meth334[id(_fd334)][0])
                                        for _d338 in _bas330:
                                            _cl330 = list(_bas330.get(_d338, []))
                                            _sd334 = set()
                                            while _cl330:
                                                _x338 = _cl330.pop()
                                                if _x338 not in _sd334:
                                                    _sd334.add(_x338)
                                                    _cl330.extend(_bas330.get(_x338, []))
                                            if _meth334[id(_fd334)][0] in _sd334:
                                                _nm338.add(_d338)
                                    if _nm338 & _uv338:
                                        _fl334.add("unk")
                                elif (
                                        isinstance(_an325, _ast325.Name)
                                        and _an325.id in ("int", "bool")) or (
                                        isinstance(_an325, _ast325.Constant)
                                        and _an325.value in ("int", "bool")):
                                    pass
                                else:
                                    _fl334.add("other")
                            elif (_e325.id in _imod325 or _e325.id in _inam325
                                  or (_e325.id in _bind325 and not all(_bind325[_e325.id]))):
                                _fl334.add("other")
                            elif _e325.id not in _bind325:
                                _fl334.add("unk")
                        elif isinstance(_e325, _ast325.Attribute):
                            if not (isinstance(_e325.value, _ast325.Name)
                                    and _e325.value.id in _imod325
                                    and (_imod325[_e325.value.id], _e325.attr)
                                    in _KI_ATTR325):
                                _cf330 = _e325.value
                                while isinstance(_cf330, _ast325.Attribute):
                                    _cf330 = _cf330.value
                                _fl334.add("other" if isinstance(_cf330, _ast325.Name) and (
                                    _cf330.id in _imod325 or _cf330.id in _inam325) else "unk")
                        elif isinstance(_e325, _ast325.Call):
                            _cf330 = _e325.func
                            _shd334 = isinstance(_cf330, _ast325.Name) and (
                                _cf330.id in _bind325 or (_ev334 is not None and (
                                    _cf330.id in _ev334[0] or _cf330.id in _ev334[1])))
                            _pl334 = (not _e325.keywords and not any(
                                isinstance(x, _ast325.Starred) for x in _e325.args))
                            _rc338 = None   # ROUTE #338: the class of a `k.m()` receiver
                            if (isinstance(_cf330, _ast325.Attribute)
                                    and isinstance(_cf330.value, _ast325.Name)
                                    and _ev334 is not None):
                                if _cf330.value.id in _ev334[1]:
                                    _rc338 = {(v.func.id if isinstance(v, _ast325.Call)
                                               and isinstance(v.func, _ast325.Name)
                                               and v.func.id in _ini334 else None)
                                              for v in _ev334[1][_cf330.value.id]}
                                    _rc338 = next(iter(_rc338)) if len(_rc338) == 1 else None
                                elif isinstance(_ev334[0].get(_cf330.value.id), _ast325.Name):
                                    _rc338 = _ev334[0][_cf330.value.id].id
                            if (isinstance(_cf330, _ast325.Name) and not _shd334
                                    and _cf330.id in ("len", "int", "ord", "hash", "id",
                                                      "bool")):
                                pass
                            elif (isinstance(_cf330, _ast325.Name) and not _shd334 and _pl334
                                  and ((_cf330.id == "abs" and len(_e325.args) == 1)
                                       or (_cf330.id in ("min", "max")
                                           and len(_e325.args) >= 2))):
                                _wl334.extend((x, _fd334, "s") for x in _e325.args)
                            elif (isinstance(_cf330, _ast325.Name) and not _shd334
                                  and _cf330.id == "round" and len(_e325.args) == 1
                                  and not _e325.keywords):
                                pass
                            elif (isinstance(_cf330, _ast325.Name)
                                  and _cf330.id in _top334
                                  and isinstance(_top334[_cf330.id], _ast325.Name)
                                  and _top334[_cf330.id].id in ("int", "bool")
                                  and not (_ev334 is not None and (
                                      _cf330.id in _ev334[0] or _cf330.id in _ev334[1]))):
                                pass
                            elif (isinstance(_cf330, _ast325.Name) and _cf330.id in _inam325
                                  and _inam325[_cf330.id] in _KI_CALL325):
                                pass
                            elif (isinstance(_cf330, _ast325.Attribute)
                                  and isinstance(_cf330.value, _ast325.Name)
                                  and ((_cf330.value.id == _sl334
                                        and _cf330.attr in _mint334.get(
                                            _meth334[id(_fd334)][0], ()))
                                       # ROUTE #338: a receiver typed / constructed as a
                                       # class of this file (`k = K(); k.bump()`): its
                                       # `-> int` is kept by every override (R5)
                                       or _cf330.attr in _mint334.get(_rc338, ())
                                       or (_cf330.value.id in _imod325
                                           and (_imod325[_cf330.value.id], _cf330.attr)
                                           in _KI_CALL325))):
                                pass
                            else:
                                # a non-int builtin (`float`, `str`, ..) or a call of an
                                # imported module is SHOWN non-int; any other call is of
                                # unknown type
                                while isinstance(_cf330, _ast325.Attribute):
                                    _cf330 = _cf330.value
                                _fl334.add("other" if isinstance(_cf330, _ast325.Name) and (
                                    (_cf330.id in _NIC330 and not _shd334
                                     and _cf330 is _e325.func)
                                    or _cf330.id in _imod325 or _cf330.id in _inam325)
                                    else "unk")
                        else:
                            _fl334.add("other" if isinstance(_e325, (
                                _ast325.JoinedStr, _ast325.List, _ast325.Tuple, _ast325.Dict,
                                _ast325.Set, _ast325.ListComp, _ast325.SetComp,
                                _ast325.DictComp, _ast325.GeneratorExp, _ast325.Lambda))
                                else "unk")
                    # a field DECLARED `int` / `bool` (a class-level or `self.f: int`
                    # annotation) takes the annotation-trust stance PyCSL takes for an
                    # `int` parameter: a stored value of UNKNOWN type (an attribute of an
                    # untyped object, an unknown call) is carried under the declaration;
                    # a value SHOWN non-int (a float / str / None literal, `/`, a local
                    # bound to one, ...) still taints. An undeclared field is int only
                    # when every stored value is PROVABLY int.
                    if "unk" in _fl334:
                        _fl334.discard("unk")
                        if not (_md334 == "=" and any(
                                e[0] == _f330 and e[4] == "=" and (
                                    (isinstance(e[1], _ast325.Name)
                                     and e[1].id in ("int", "bool"))
                                    or (isinstance(e[1], _ast325.Constant)
                                        and e[1].value in ("int", "bool"))
                                    or (isinstance(e[1], _ast325.Subscript)
                                        and isinstance(e[1].value, _ast325.Name)
                                        and e[1].value.id in ("Final", "ClassVar")
                                        and isinstance(e[1].slice, _ast325.Name)
                                        and e[1].slice.id in ("int", "bool")))
                                for e in _allc334[_cn334])):
                            _fl334.add("other")
                    _k334 = ("other" if "other" in _fl334 or len(_fl334) > 1
                             else next(iter(_fl334)) if _fl334 else "")
                    if _md334 == "[]":
                        if _fl334:
                            _ndv334.setdefault(_cn334, set()).add(_f330)
                    elif _k334:
                        _nif330.setdefault(_cn334, {})[_f330] = _k334
            if any(e[0] == "*" for e in _allc334[_cn334]):
                _nif330.setdefault(_cn334, {})["*"] = "other"
        for _c330, _r330 in _rt330.items():
            if not isinstance(_r330, dict) or not _r330.get("whyml_name"):
                continue
            _cl330 = [_c330]
            _bad330 = {}
            _seen330 = set()
            while _cl330:
                _x325 = _cl330.pop()
                if _x325 in _seen330:
                    continue
                _seen330.add(_x325)
                for _f330, _kd330 in _nif330.get(_x325, {}).items():
                    if _bad330.get(_f330) != "other":
                        _bad330[_f330] = _kd330
                _cl330.extend(_bas330.get(_x325, []))
            _dvb334 = _ndv334.get(_c330, set())
            for _f330 in _r330.get("fields") or []:
                _kd330 = _bad330.get(_f330) or _bad330.get("*")
                try:
                    _lb330 = transpiler._field_label(_r330["whyml_name"], _f330)
                except Exception:
                    _lb330 = _wid325(_f330)
                if _kd330 and _lblty325.get(_lb330) == ["int"]:
                    _fld325[_lb330] = ("field '" + _c330 + "." + _f330 + "'"
                                       + {"none": " (None / Optional)",
                                          "ifloat": " (integral float)"}.get(_kd330, ""))
                    if _kd330 == "ifloat":
                        _iflo325.add(_fld325[_lb330])
                elif ((_f330 in _dvb334 or "*" in _bad330) and _lblty325.get(_lb330)
                      and all(_re325.match(r"map\b.*\(\s*option\s+int\s*\)$", t)
                              for t in _lblty325[_lb330])):
                    # ROUTE #334: the VALUES of a dict field are not provably int (k04)
                    _fld325[_lb330] = "the values of dict field '" + _c330 + "." + _f330 + "'"
                    _mvorg325.add(_fld325[_lb330])
        # ROUTE #334: an OPAQUE class (no record type: Module 6 lowers `C()` to a stub
        # `c_<n> ()` and `c.r` to an unconstrained getter `get_r`) — its provably-int
        # fields keep the getter's int (o03 `self.r, self.s = 2.5, 1`: `r` is not one)
        for _cn334 in _ini334:
            if not (isinstance(_rt330.get(_cn334), dict) and _rt330[_cn334].get("whyml_name")):
                _octok334[_wid325(_cn334)] = (set() if "*" in _nif330.get(_cn334, {}) else {
                    _wid325(e[0]) for e in _ini334[_cn334] if e[0] != "*"
                    and e[0] not in _nif330.get(_cn334, {})})
    # (b) string-encoding model operations
    for _x325 in list(_other325):
        if (_x325 in ("str_of_int_hash", "str_of_bool_hash", "str_of_value_op", "str_concat")
                or (_x325.endswith("_conv") and _x325[:-5] not in (
                    "abs", "bool", "int", "round", "len", "ord", "hash"))):
            _S325[_x325] = ("string-encoding model operation", _other325.pop(_x325)[0])
    _strorg325 = ({x for x, f in _S325.items() if f[0] == "string-encoding model operation"}
                  | {x for x in _fld325.values() if x.endswith("(None / Optional)")})
    for _x325 in _fld325.values():
        _S325[_x325] = ("non-int field", 0)
    for _x325 in _el325.values():
        _S325[_x325] = ("unknown-type element", 0)
    _INTOP325 = {"+", "-", "*", "<", "<=", ">", ">=", "pycsl_mod", "pycsl_div", "pycsl_pow",
                 "div", "mod", "abs", "power", "py_pow", "min", "max"}
    _KW325 = {"let", "in", "if", "then", "else", "begin", "end", "match", "with", "try",
              "raise", "while", "do", "done", "for", "to", "downto", "fun", "ref", "not",
              "true", "false", "assert", "check", "assume", "old", "at", "forall",
              "exists", "return", "absurd", "any", "ghost", "val", "function", "rec",
              "loop", "result"}
    # model operations whose result is an int of their own (a length, a type tag) or a
    # rendering (`int_to_string`): an opaque argument is a sink there, not a source
    _KIOP325 = {"iter_length", "hval_values_len", "hval_iter_len_other", "hval_len_other",
                "typeof_op", "int_to_string"}
    _PROG325 = {"let", "val", "predicate", "function", "lemma", "axiom", "goal", "constant"}
    # 6. occurrences of a fallback (or of a value derived from one) must stay in the
    #    ALLOWED positions: an argument of another opaque operation; the whole right-hand
    #    side of a local binding (the local is then tracked); a function's return value
    #    (the function is then tracked); a discarded statement; one side of a program
    #    `=` / `<>` whose other side is not the same value (no reflexivity). Any other
    #    position — an int operator or ordering, a contract term, an argument of a
    #    modelled function, a store, a condition — gives the opaque value int theory it
    #    may not have.
    _tl325 = {}     # (decl, local) -> origin
    _tf325 = {}     # tainted function name -> origin
    _pos325 = {}
    for _k325, _tk325 in enumerate(_toks325):
        _pos325.setdefault(_tk325.lstrip("!"), []).append(_k325)
    for _round325 in range(16):
        _new325 = False
        _viol325 = []
        # a call stub `<recv>_<meth>_<n>` (Module 6 drops the receiver) whose receiver
        # carries a fallback, or whose user method returns one, carries it too
        _rv325 = {x[1] for x in _tl325} | {n for n, f in _S325.items()
                                           if f[0] == "constant" and n not in _clsw325}
        for _x325 in list(_other325):
            if not _re325.search(r"_\d+$", _x325) or _x325 in _S325:
                continue
            _bs325 = _re325.sub(r"_\d+$", "", _x325)
            if (any(_bs325.startswith(r + "_") for r in _rv325)
                    or any((_bs325 == u or _bs325.endswith("_" + u))
                           and any(f == u or f.endswith("__" + u) for f in _tf325)
                           for u in _pydefs325)):
                _S325[_x325] = ("call", _other325.pop(_x325)[0])
                _new325 = True
        _cand325 = (set(_S325) | set(_tf325) | {x[1] for x in _tl325} | set(_fld325)
                    | {x[1] for x in _el325})
        for _k325 in sorted(k for c in _cand325 for k in _pos325.get(c, ())):
            _tk325 = _toks325[_k325]
            _nm325 = _tk325.lstrip("!")
            _dd325 = _decl325[_k325]
            if _toks325[_dstart325[_dd325]] not in _PROG325:
                continue
            if _k325 < _hdr325.get(_dd325, _dstart325[_dd325]):
                continue        # a declaration header names, it does not use
            _org325 = None
            _fu325 = None       # (start, end) of a field read / element read unit
            if _k325 > 0 and _toks325[_k325 - 1] == ".":
                # a field / qualified name; ROUTE #330: a read `<recv>.<label>` of a
                # non-int field is a use of that field's value
                if _nm325 not in _fld325 or _tk325 != _nm325 or _k325 < 2:
                    continue
                _s2325 = _k325 - 2
                if _toks325[_s2325] in (")", "]", "}") and _s2325 in _mt325:
                    _s2325 = _mt325[_s2325]
                while _s2325 >= 2 and _toks325[_s2325 - 1] == ".":
                    _s2325 -= 2
                    if _toks325[_s2325] in (")", "]", "}") and _s2325 in _mt325:
                        _s2325 = _mt325[_s2325]
                if _toks325[_s2325][:1].isupper():
                    continue    # a qualified name `Mod.f`
                _org325 = _fld325[_nm325]
                _fu325 = (_s2325, _k325)
            elif (_dd325, _nm325) in _el325 and (_dd325, _nm325) not in _tl325:
                # ROUTE #330 (c): only an ELEMENT read of a bare-container parameter
                if any(b[0] == _nm325 and b[1] <= _k325 < b[2] for b in _bg325):
                    continue
                if _el325[(_dd325, _nm325)] in _mvorg325:
                    _fu325 = (_k325, _k325)     # ROUTE #334: a bare dict (its value reads)
                elif (_k325 + 1 < _N325 and _toks325[_k325 + 1] == "[" and (_k325 + 1) in _mt325
                        and not (_mt325[_k325 + 1] + 1 < _N325
                                 and _toks325[_mt325[_k325 + 1] + 1] == "<-")):
                    _fu325 = (_k325, _mt325[_k325 + 1])
                elif (_k325 >= 2 and _toks325[_k325 - 2] == "(" and (_k325 - 2) in _mt325
                      and _re325.match(r"(subscript_get|iter_get|hval_iter_get|Array\.get)",
                                       _toks325[_k325 - 1])):
                    _fu325 = (_k325 - 2, _mt325[_k325 - 2])
                else:
                    continue
                _org325 = _el325[(_dd325, _nm325)]
            elif (_dd325, _nm325) in _tl325:
                _org325 = _tl325[(_dd325, _nm325)]
            elif _nm325 in _bd325.get(_dd325, ()) or any(
                    b[0] == _nm325 and b[1] <= _k325 < b[2] for b in _bg325):
                continue
            elif _nm325 in _S325:
                _org325 = _nm325
                if (_S325[_nm325][0] == "getattr" and not _nm325.startswith("pycsl_")
                        and not (_k325 > 0 and _toks325[_k325 - 1] == "("
                                 and set(_toks325[_k325:_mt325.get(_k325 - 1, _k325)])
                                 & _clsbad325)):
                    continue    # an instance attribute: not a module-level value
                if _S325[_nm325][0] == "call":
                    _bs325 = _re325.sub(r"_\d+$", "", _nm325)
                    _ok325 = False
                    for _u325 in _udef325:
                        if (_bs325 == _u325 or (_bs325.endswith("_" + _u325)
                                                and _bs325[:-len(_u325) - 1] not in _modw325)):
                            _ok325 = not any(
                                f == _u325 or f.endswith("__" + _u325) for f in _tf325)
                            break
                    if _ok325:
                        continue
            elif _nm325 in _tf325 and _dname325.get(_dd325) != _nm325:
                _org325 = _tf325[_nm325]
            if _org325 is None:
                continue
            if _k325 + 1 < _N325 and _toks325[_k325 + 1] in (":=", "<-"):
                continue        # the target of an assignment
            if _k325 > 0 and _toks325[_k325 - 1] in ("let", "ghost", "rec", "for", "mutable"):
                continue        # a binder
            if _k325 > 0 and _toks325[_k325 - 1] in ("(", ","):
                _e325 = _k325 - 1
                _dp325 = 0
                while _e325 >= 0:
                    if _toks325[_e325] in (")", "]", "}"):
                        _dp325 += 1
                    elif _toks325[_e325] in ("(", "[", "{"):
                        if _dp325 == 0:
                            break
                        _dp325 -= 1
                    _e325 -= 1
                if (_e325 >= 1 and _toks325[_e325] == "(" and _e325 in _mt325
                        and _toks325[_e325 - 1] in ("let", "ghost")
                        and _toks325[_mt325[_e325] + 1:_mt325[_e325] + 2] == ["="]):
                    continue    # a name of a tuple PATTERN `let (a, b) = ..` (a binder)
            # the unit: the application `(f a b)` / `f a b`, or the bare name
            _ua325, _ub325 = _k325, _k325
            _ar325 = (_S325[_nm325][1] if _nm325 in _S325 and _org325 == _nm325 else
                      next((_dar325[d] for d, n in _dname325.items() if n == _nm325), 0)
                      if _nm325 in _tf325 else 0)
            if _k325 > 0 and _toks325[_k325 - 1] == "(" and (_k325 - 1) in _mt325 and _ar325:
                _ua325, _ub325 = _k325 - 1, _mt325[_k325 - 1]
            elif _ar325:
                _j325 = _k325 + 1
                for _r325 in range(_ar325):
                    if _j325 < _N325 and _toks325[_j325] in ("(", "[", "{") and _j325 in _mt325:
                        _j325 = _mt325[_j325] + 1
                    elif _j325 < _N325 and _re325.match(r"!?[A-Za-z_0-9]", _toks325[_j325]):
                        _j325 += 1
                _ub325 = _j325 - 1
            if _fu325 is not None:
                _ua325, _ub325 = _fu325
            # climb through value-transparent wrappers: `( u )`, `begin ...; u end`,
            # `try u with ... end`, and through opaque operations applied to u
            _w1ok325 = False
            _drv325 = False
            _prev325 = ""
            _tix325 = None
            _mvd334 = False
            while True:
                if (_ua325 > 0 and _toks325[_ua325 - 1] == "(" and (_ua325 - 1) in _mt325
                        and _mt325[_ua325 - 1] == _ub325 + 1):
                    _ua325, _ub325 = _ua325 - 1, _ub325 + 1
                    continue
                # ROUTE #334: a dict whose VALUES are an origin (a dict field shown with a
                # non-int value, k04; a bare `dict` parameter under --strict-bare-containers,
                # k01): `match Map.get u k with | Some v -> v ..` READS a value (the match
                # carries the origin: climb to it); `| Some _ -> ..` only tests membership
                if (_org325 in _mvorg325 and not _mvd334 and _ua325 >= 3
                        and _toks325[_ua325 - 3:_ua325] == ["Map", ".", "get"]):
                    _mvd334 = True
                    _a334, _b334 = _ua325 - 3, _ub325 + 1
                    if _b334 < _N325 and _toks325[_b334] in ("(", "[", "{") and _b334 in _mt325:
                        _b334 = _mt325[_b334]
                    if (_a334 >= 1 and _toks325[_a334 - 1] == "("
                            and _mt325.get(_a334 - 1) == _b334 + 1):
                        _a334, _b334 = _a334 - 1, _b334 + 1
                    if (_a334 >= 1 and _toks325[_a334 - 1] == "match"
                            and (_a334 - 1) in _bk325):
                        _j334 = _b334 + 1
                        while _j334 < _bk325[_a334 - 1] and _toks325[_j334] != "with":
                            _j334 = (_mt325[_j334] + 1 if _toks325[_j334] in ("(", "[", "{")
                                     and _j334 in _mt325 else _j334 + 1)
                        if _toks325[_j334 + 1:_j334 + 4] == ["|", "Some", "_"]:
                            _w1ok325 = True
                            break
                        _ua325, _ub325 = _a334 - 1, _bk325[_a334 - 1]
                        continue
                    _ua325, _ub325 = _a334, _b334
                    continue
                if (_ub325 + 1 < _N325 and _toks325[_ub325 + 1] == "end"
                        and (_ub325 + 1) in _bk325 and _ua325 > 0
                        and _toks325[_ua325 - 1] in (";", "begin")
                        and _toks325[_bk325[_ub325 + 1]] == "begin"):
                    _ua325, _ub325 = _bk325[_ub325 + 1], _ub325 + 1
                    continue
                if (_ua325 > 0 and _toks325[_ua325 - 1] == "try"
                        and _ub325 + 1 < _N325 and _toks325[_ub325 + 1] == "with"
                        and (_ua325 - 1) in _bk325):
                    _ua325, _ub325 = _ua325 - 1, _bk325[_ua325 - 1]
                    continue
                # `(let x = e in u)` / `(if c then u else v)`: u IS the group's value
                if (_ua325 > 0 and _toks325[_ua325 - 1] in ("in", "then", "else")
                        and _ub325 + 1 < _N325 and _toks325[_ub325 + 1] in (")", "else")):
                    _e325 = _ua325 - 1
                    _dp325 = 0
                    while _e325 >= 0:
                        if _toks325[_e325] in (")", "]", "}"):
                            _dp325 += 1
                        elif _toks325[_e325] in ("(", "[", "{"):
                            if _dp325 == 0:
                                break
                            _dp325 -= 1
                        _e325 -= 1
                    if (_e325 >= 0 and _toks325[_e325] == "(" and _e325 in _mt325
                            and _toks325[_e325 + 1] in ("let", "if")
                            and (_toks325[_ub325 + 1] == ")"
                                 or _toks325[_ua325 - 1] == "then")):
                        _ua325, _ub325 = _e325, _mt325[_e325]
                        continue
                # a tuple component `( a, u, b )`: the tuple carries u (climb to it)
                if (_ua325 > 0 and (_toks325[_ua325 - 1] == "," or (
                        _ub325 + 1 < _N325 and _toks325[_ub325 + 1] == ","))):
                    _e325 = _ua325 - 1
                    _dp325 = 0
                    while _e325 >= 0:
                        if _toks325[_e325] in (")", "]", "}"):
                            _dp325 += 1
                        elif _toks325[_e325] in ("(", "[", "{"):
                            if _dp325 == 0:
                                break
                            _dp325 -= 1
                        _e325 -= 1
                    if _e325 >= 0 and _toks325[_e325] == "(" and _e325 in _mt325:
                        # ROUTE #328: remember WHICH component u is, for a tuple pattern
                        # `let (a, b) = (u, v) in` (W2)
                        _ix325 = 0
                        _j325 = _e325 + 1
                        while _j325 < _ua325:
                            if _toks325[_j325] in ("(", "[", "{") and _j325 in _mt325:
                                _j325 = _mt325[_j325] + 1
                                continue
                            if _toks325[_j325] == ",":
                                _ix325 += 1
                            _j325 += 1
                        _tix325 = (_e325, _ix325)
                        _ua325, _ub325 = _e325, _mt325[_e325]
                        continue
                # (W1) an argument of an opaque operation, `(op .. u ..)` / `op .. u ..`:
                # an int-valued one yields a value DERIVED from u (climb to it), any other
                # (`setattr`, a `unit` stub) is a sink.
                _h325 = _ua325 - 1
                while _h325 >= 0 and (
                        (_toks325[_h325] in (")", "]") and _h325 in _mt325)
                        or (_re325.match(r"!?[A-Za-z_0-9]", _toks325[_h325])
                            and _toks325[_h325] not in _KW325)):
                    _h325 = _mt325[_h325] - 1 if _toks325[_h325] in (")", "]") else _h325 - 1
                _hn325 = _toks325[_h325 + 1] if _h325 + 1 < _ua325 else ""
                # ROUTE #334: an argument at a POLYMORPHIC (`'a`) parameter of a `val`
                # (`str_mod_op "fmt" (a, u)`) gets no int theory there: a sink (string
                # literal arguments, `"s"` once stripped, are skipped to find the head)
                _g334 = _ua325 - 1
                _ix334 = 0
                while _g334 >= 0 and (
                        (_toks325[_g334] in (")", "]") and _g334 in _mt325)
                        or (_re325.match(r"!?[A-Za-z_0-9]", _toks325[_g334])
                            and _toks325[_g334] not in _KW325)
                        or (_toks325[_g334] == '"' and _g334 >= 2
                            and _toks325[_g334 - 2:_g334] == ['"', "s"])):
                    _g334 = (_mt325[_g334] - 1 if _toks325[_g334] in (")", "]")
                             else _g334 - 3 if _toks325[_g334] == '"' else _g334 - 1)
                    _ix334 += 1
                if (_g334 + 1 < _ua325 and _toks325[_g334 + 1] in _poly334
                        and _ix334 - 1 in _poly334[_toks325[_g334 + 1]]):
                    _w1ok325 = True
                    break
                # ROUTE #328: the KEY of a map read / test / store (`Map.get m u`, `Map.mem
                # u m`, `Map.set m u v`) is compared by equality only (no int theory), and
                # the lookup's result is the map's value, not derived from u: a sink
                if (_hn325 in ("get", "mem", "set") and _h325 >= 1 and _toks325[_h325] == "."
                        and _toks325[_h325 - 1] == "Map"):
                    _ix325 = 0
                    _j325 = _h325 + 2
                    while _j325 < _ua325:
                        _j325 = (_mt325[_j325] + 1 if _toks325[_j325] in ("(", "[", "{")
                                 and _j325 in _mt325 else _j325 + 1)
                        _ix325 += 1
                    if _ix325 == (0 if _hn325 == "mem" else 1) or (
                            _hn325 == "mem" and _org325 in _mvorg325):
                        _w1ok325 = True
                        break
                if (_hn325 and (_hn325[0].isupper() and not _hn325.startswith("Return"))
                        or (_h325 >= 1 and _toks325[_h325] == "."
                            and _toks325[_h325 - 1][:1].isupper())):
                    # a constructor / container builder (`Some u`, `Seq.cons u ..`,
                    # `Array.make n u`): the built value carries u (climb to it)
                    if _toks325[_h325] == ".":
                        _h325 -= 2
                        while _h325 >= 0 and _toks325[_h325] == ".":
                            _h325 -= 2
                    if _h325 >= 0 and _toks325[_h325] == "(" and _h325 in _mt325:
                        _ua325, _ub325 = _h325, _mt325[_h325]
                        continue
                    break
                if (_hn325 in _dbyname325 and _hn325 not in _S325 and _hn325 not in _other325
                        and _h325 + 1 < _ua325):
                    # an argument of a USER function: its parameter now carries the value
                    _ix325 = 0
                    _j325 = _h325 + 2
                    while _j325 < _ua325:
                        _j325 = (_mt325[_j325] + 1 if _toks325[_j325] in ("(", "[", "{")
                                 and _j325 in _mt325 else _j325 + 1)
                        _ix325 += 1
                    _ps325 = _dparams325.get(_dbyname325[_hn325], [])
                    if _ix325 < len(_ps325):
                        if (_dbyname325[_hn325], _ps325[_ix325]) not in _tl325:
                            _tl325[(_dbyname325[_hn325], _ps325[_ix325])] = _org325
                            _new325 = True
                        _w1ok325 = True
                    break
                if _hn325 in _S325 or _hn325 in _other325:
                    if _hn325 in _other325 and (not _other325[_hn325][1]
                                                or _hn325 in _KIOP325):
                        _w1ok325 = True
                        break
                    # a documented INT attribute of a module (`sys.maxsize`, the int fields
                    # of `sys.float_info`) keeps its int model
                    if _hn325.startswith("get_") and (
                            (_org325 in _clsw325 and _hn325[4:] in _clsok325)
                            or (_hn325[4:] in _octok334.get(_re325.sub(r"_\d+$", "",
                                                                       _org325), ()))
                            or (_imod325.get(_org325), _hn325[4:]) in _KI_ATTR325
                            or (_hn325[4:] in _KI_FI325 and _prev325 == "get_float_info"
                                and _imod325.get(_org325) == "sys")):
                        _w1ok325 = True
                        break
                    _prev325 = _hn325
                    if _h325 >= 0 and _toks325[_h325] == "(" and _h325 in _mt325:
                        _ua325, _ub325 = _h325, _mt325[_h325]
                    else:
                        _har325 = (_S325[_hn325][1] if _hn325 in _S325
                                   else _other325[_hn325][0])
                        _j325 = _h325 + 2
                        for _r325 in range(_har325):
                            if (_j325 < _N325 and _toks325[_j325] in ("(", "[", "{")
                                    and _j325 in _mt325):
                                _j325 = _mt325[_j325] + 1
                            elif _j325 < _N325 and _re325.match(r"!?[A-Za-z_0-9]",
                                                                 _toks325[_j325]):
                                _j325 += 1
                        _ua325, _ub325 = _h325 + 1, max(_j325 - 1, _ub325)
                    _drv325 = True
                    continue
                break
            _pv325 = _toks325[_ua325 - 1] if _ua325 > 0 else ""
            _nx325 = _toks325[_ub325 + 1] if _ub325 + 1 < _N325 else ""
            # enclosing group
            _e325 = _ua325 - 1
            _dp325 = 0
            while _e325 >= 0 and _decl325[_e325] == _dd325:
                if _toks325[_e325] in (")", "]", "}"):
                    _dp325 += 1
                elif _toks325[_e325] in ("(", "[", "{"):
                    if _dp325 == 0:
                        break
                    _dp325 -= 1
                _e325 -= 1
            _enc325 = _e325 if (_e325 >= 0 and _decl325[_e325] == _dd325
                                and _toks325[_e325] in ("(", "[", "{")) else None
            _hd325 = _toks325[_enc325 + 1] if _enc325 is not None else ""
            # builtin type objects are compared by identity only (the isinstance tags);
            # a WhyML type of the same spelling is not a use at all
            if (_org325 == _nm325 and _S325.get(_nm325, ("",))[0] == "constant"
                    and _nm325 in _TYPES325 and _nm325 not in _bound325
                    and not (_pv325 in _INTOP325 or _nx325 in _INTOP325
                             or _hd325 in _INTOP325)):
                continue
            if _w1ok325:
                continue
            # a `writes { .. }` / `reads { .. }` / `alias { .. }` item names a location, it
            # does not use a value
            if (_enc325 is not None and _toks325[_enc325] == "{" and _enc325 >= 1
                    and _toks325[_enc325 - 1] in ("writes", "reads", "alias")):
                continue
            # ROUTE #330: the generated FRAME condition `X.f = old X.f` of a method is an
            # identity of the field's value, not a Python `==` (admitted)
            if _fu325 is not None and _org325 in _fld325.values():
                _ut325 = _toks325[_ua325:_ub325 + 1]
                _L325 = len(_ut325)
                if ((_toks325[_ub325 + 1:_ub325 + 3 + _L325] == ["=", "old"] + _ut325
                     and _ub325 + 3 + _L325 < _N325
                     and _toks325[_ub325 + 3 + _L325] in ("}", "/\\", ")"))
                        or (_ua325 >= _L325 + 2 and _toks325[_ua325 - 1] == "old"
                            and _toks325[_ua325 - 2] == "="
                            and _toks325[_ua325 - 2 - _L325:_ua325 - 2] == _ut325
                            and _ub325 + 1 < _N325
                            and _toks325[_ub325 + 1] in ("}", "/\\", ")"))):
                    continue
            # (W2) the whole right-hand side of a local binding
            _lhs325 = None
            _lk325 = ""
            if _pv325 == "ref" and _ua325 >= 3 and _toks325[_ua325 - 2] == "=":
                _lhs325 = _toks325[_ua325 - 3]
                _lk325 = _toks325[_ua325 - 4] if _ua325 >= 4 else ""
            elif _pv325 == "=" and _ua325 >= 2:
                _lhs325 = _toks325[_ua325 - 2]
                _lk325 = _toks325[_ua325 - 3] if _ua325 >= 3 else ""
            if (_lhs325 is not None and _lk325 in ("let", "ghost") and _nx325 == "in"
                    and _re325.match(r"[a-z_][A-Za-z_0-9']*$", _lhs325)):
                if (_dd325, _lhs325) not in _tl325:
                    _tl325[(_dd325, _lhs325)] = _org325
                    _new325 = True
                continue
            # ROUTE #328 — a TUPLE pattern `let (_tu_a, _tu_b) = (u, 1) in`: #325 found no
            # name left of `=` and dropped the taint, so `a, b = F, 1; a % 1 == 0` proved
            # (witness 4336). The component u sits in carries it; a pattern bound to a
            # whole tainted term (`let (a, b) = t in`) taints every name in it.
            if (_pv325 == "=" and _ua325 >= 3 and _toks325[_ua325 - 2] == ")"
                    and _nx325 == "in" and (_ua325 - 2) in _mt325
                    and _mt325[_ua325 - 2] >= 1
                    and _toks325[_mt325[_ua325 - 2] - 1] in ("let", "ghost")):
                _pa325 = _mt325[_ua325 - 2]
                _cm325 = [[]]
                _j325 = _pa325 + 1
                while _j325 < _ua325 - 2:
                    if _toks325[_j325] in ("(", "[", "{") and _j325 in _mt325:
                        _cm325[-1].extend(_toks325[_j325:_mt325[_j325] + 1])
                        _j325 = _mt325[_j325] + 1
                        continue
                    if _toks325[_j325] == ",":
                        _cm325.append([])
                    else:
                        _cm325[-1].append(_toks325[_j325])
                    _j325 += 1
                if (_tix325 is not None and _tix325[0] == _ua325
                        and _tix325[1] < len(_cm325) and len(_cm325) > 1):
                    _cm325 = [_cm325[_tix325[1]]]
                for _x325 in [x for c in _cm325 for x in c]:
                    if (_re325.match(r"[a-z_][A-Za-z_0-9']*$", _x325) and _x325 not in _KW325
                            and (_dd325, _x325) not in _tl325):
                        _tl325[(_dd325, _x325)] = _org325
                        _new325 = True
                continue
            if (_pv325 == ":=" and _ua325 >= 2
                    and _nx325 in (";", "end", "done", "in", "else", "with", "")
                    and _re325.match(r"[a-z_][A-Za-z_0-9']*$", _toks325[_ua325 - 2])):
                if (_dd325, _toks325[_ua325 - 2]) not in _tl325:
                    _tl325[(_dd325, _toks325[_ua325 - 2])] = _org325
                    _new325 = True
                continue
            # (W3) a return value: `raise (Return v)`, or the tail of the declaration
            _fn325 = _dname325.get(_dd325)
            if ((_pv325.startswith("Return") and _ua325 >= 3 and _toks325[_ua325 - 2] == "("
                 and _toks325[_ua325 - 3] == "raise" and _nx325 == ")")
                    or (_enc325 is None and _ub325 + 1 == _dstart325[_dd325 + 1]
                        and _pv325 in ("=", "in", ";", "begin", "->"))):
                if _fn325 and _fn325 not in _tf325:
                    _tf325[_fn325] = _org325
                    _new325 = True
                continue
            # (W4) a discarded statement value
            if _nx325 == ";" and _pv325 in (";", "begin", "do", "in", "then", "else", "->",
                                            "="):
                if not (_pv325 == "=" and _enc325 is not None):
                    continue
            # (W5) one side of a PROGRAM `=` / `<>` (or `pycsl_py_eq`) whose other side is
            #      not the same value: no reflexivity (a NaN is not equal to itself)
            if _pv325 in ("=", "<>") or _nx325 in ("=", "<>") or (
                    _hd325 == "pycsl_py_eq" and _enc325 is not None):
                _c325 = _ua325 - 1
                _dp325 = 0
                _inspec325 = False
                while _c325 >= _dstart325[_dd325]:
                    if _toks325[_c325] == "}":
                        _dp325 += 1
                    elif _toks325[_c325] == "{":
                        if _dp325 == 0:
                            _inspec325 = True
                            break
                        _dp325 -= 1
                    _c325 -= 1
                if _hd325 == "pycsl_py_eq" and not (_pv325 in ("=", "<>")
                                                    or _nx325 in ("=", "<>")):
                    _oa325, _ob325 = _enc325 + 1, _mt325.get(_enc325, _enc325) - 1
                elif _pv325 in ("=", "<>"):
                    _ob325 = _ua325 - 2
                    _oa325 = _mt325.get(_ob325, _ob325) if _toks325[_ob325] in (
                        ")", "]", "}") else _ob325
                else:
                    _oa325 = _ub325 + 2
                    _ob325 = _mt325.get(_oa325, _oa325) if _oa325 < _N325 and _toks325[
                        _oa325] in ("(", "[", "{") else _oa325
                _same325 = False
                for _x325 in range(max(_oa325, 0), min(_ob325 + 1, _N325)):
                    if _ua325 <= _x325 <= _ub325:
                        continue
                    _y325 = _toks325[_x325].lstrip("!")
                    if (_tl325.get((_dd325, _y325)) == _org325 or _y325 == _org325
                            or _tf325.get(_y325) == _org325 or _y325 == "result"
                            or (_fld325.get(_y325) == _org325 and _x325 > 0
                                and _toks325[_x325 - 1] == ".")):
                        _same325 = True
                if _org325.startswith("pycsl_getattr_default_") and "result" not in (
                        _toks325[max(_oa325, 0):_ob325 + 1]):
                    _same325 = False    # one DEFAULT EXPRESSION, one value (route #47)
                if not _inspec325 and not _same325:
                    continue
                if _org325 in _strorg325:
                    continue    # a string is equal to itself (no NaN): `=` / `<>` admitted
            # ROUTE #334: an INTEGRAL float (|v| < 2**53) compares EXACTLY with an int in
            # CPython, so a DIRECT operand of a comparison keeps its int model (1490
            # `c.r > 1`); any arithmetic / argument use of it (`c.r * 10**17`, `"ab" *
            # c.r`, `range(c.r)`) is not int-faithful and stays refused (p01, p10)
            if _org325 in _iflo325 and not _drv325 and (
                    (_nx325 in ("<", "<=", ">", ">=", "=", "<>")
                     and _pv325 in ("(", "if", "then", "else", "in", "&&", "||", "not", "{",
                                    "/\\", "\\/", "->", "begin", ";", "assert", "check"))
                    or (_pv325 in ("<", "<=", ">", ">=", "=", "<>")
                        and _nx325 in (")", "then", "else", "in", "&&", "||", "}", "/\\",
                                       "\\/", "->", ";", "end", "do", "with"))):
                continue
            _viol325.append((_org325, _S325.get(_org325, ("?",))[0], _nm325,
                             " ".join(_toks325[max(_ua325 - 4, _dstart325[_dd325]):
                                               min(_ub325 + 5, _N325)]),
                             _dname325.get(_dd325, "?")))
        if not _new325:
            break
    else:
        _viol325.append(("?", "?", "?", "taint fixpoint not reached", "?"))
    if _cx325 is not None:
        _viol325.insert(0, ("complex", "`complex` annotation", "complex", "a `complex` "
                            "annotation is lowered to `int`", _cx325))
    if _viol325:
        from errors import PyCSLSemanticError as _PyCSLSemErr325
        _v325 = _viol325[0]
        raise _PyCSLSemErr325(
            f"PYCSL-R325-OPAQUE-INT-FALLBACK (route #325) — in '{_v325[4]}', the value "
            f"'{_v325[2]}' comes from '{_v325[0]}', a {_v325[1]} PyCSL has no model of: it "
            f"is lowered to an OPAQUE INT whatever its Python type (a float, a string, a "
            f"module...), and it is used here as an integer (`{_v325[3]}`), where every "
            f"claim true of all integers (`x % 1 == 0`, `x * 0 == 0`, `x < e or x >= e + 1 "
            f"or x == e`) would be proved of it. Refused (fail closed). Give it a modelled "
            f"form: an `int` literal / int expression, or pass it in as a typed parameter "
            f"with an explicit `requires`.",
            filename=args.file, stage="ir-semantic",
            code="PYCSL-R325-OPAQUE-INT-FALLBACK")
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
