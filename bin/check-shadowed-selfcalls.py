#!/usr/bin/env python3
"""L-PLANE ORACLE: a CONVERTED method whose CALL SITES still go through an abstract val.

`bin/check-untrusted-emitted.py` asks whether an un-trusted (converted) function is
EMITTED AS A DEFINITION rather than re-abstracted to a `val`. That is necessary and not
sufficient. Module 6 lowers `self.<m>(...)` two ways:

  * the CONCRETE sibling application `(<class>__<m> self args)`, which gives the caller the
    callee's real BODY and contract; and
  * a synthesized receiver-less abstract op `val self__<m>_<n> ... : <ret>`, whose result is
    UNCONSTRAINED.

When a method is converted but its call sites take the second route, the `let` is emitted,
it is proved, `check-untrusted-emitted` is green, the mirror byte-diff is 0, fidelity is
unchanged and emitted-vacuity sees nothing — yet no caller can see a single thing the body
computes. `_Parser._if_tail`, `_else_block`, `_import_as_names`, `block` and `statement`
were all in exactly that state when this check was written: `if_stmt`'s `orelse` child was
an ARBITRARY array rather than the parsed one.

That is not UNSOUND (an unconstrained result is an over-approximation, exactly like a
`\trusted` stub), but it is a LOST CONVERSION: the proof was paid for and the faithfulness
gain never reached any caller. This check MEASURES it, so it can only shrink.

Usage:
    bin/check-shadowed-selfcalls.py [--emit-dir DIR] [--max N]

With no `--emit-dir` it emits every mirror under `src/self-annotate/src` itself (requires
`why3` on PATH; see wall-lessons (aa)). `--max N` fails when more than N shadowed methods
are found; the default is the recorded baseline, so the check is a RATCHET.
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
BASELINE = 13          # 55 at first measurement, 50 after the `array <t>` concrete-
                       # sibling capability landed (relaunch #9), 43 after the first
                       # `#@ sibling_concrete` marker wave (relaunch #10: `_deref` and its
                       # 28 call sites, `_rhs_yields_array`, and five ExpressionEmissionMixin
                       # helpers), 35 after wave 2 (statements, functions,
                       # stmt_control_flow, Module5_IREmitter), 32 after wave 3 (the
                       # `Optional[str]`-return call-site unwrap that unblocked
                       # `_field_type_of`), 27 after wave 4 (relaunch #11: the
                       # sibling-concrete SELF-RECURSION fix — a marked callee that calls
                       # ITSELF emits as a real `let rec`, which `IRScanner.is_recursive`
                       # missed because the self-call's IR node carries the DOTTED
                       # `self.<m>` — plus the kind-local discriminant carve-out that lets
                       # `_rhs_yields_map`'s structural recursion discharge its variant)
                       # 26 after wave 5 (relaunch #15: `_py_op_to_str`, whose SIXTH and
                       # last call site lives in a SYNTHESIZED body — the bespoke
                       # `_py_expr_compare` lowering in functions.py had the avatar
                       # HARD-CODED, so the generic `#@ sibling_concrete` route in
                       # `_handle_dotted_call` never saw it and the per-METHOD ratchet
                       # could not move even with the other five concrete), 23 after
                       # wave 6 (relaunch #15: `stmt_ir` added to the concrete-route
                       # RETURN-TYPE allowlist in `expressions._handle_dotted_call` — the
                       # certified statement-node ADT was simply missing beside `emit_ir`,
                       # so `_process_for`/`_process_if`/`_process_while` snoc'd an
                       # UNCONSTRAINED node onto `ir_stmts` at their only call site), 15
                       # after wave 7 (relaunch #15: the VOID sibling — `unit` — admitted
                       # OPT-IN ONLY. A void mutator's avatar carries no `writes`, so it is
                       # modelled as a NO-OP and the caller of a CONVERTED void helper sees
                       # nothing it does. Measured: admitting `unit` on the shared
                       # `_record_array_fields` proxy BREAKS `pure_ast` outright, because
                       # `_Parser` passes that proxy and its `-> NoReturn` `error` is
                       # `\trusted` — so the marker is required. Eight methods:
                       # `_array_coerce_arg`, `_is_null_byte_lit` (both `@staticmethod`,
                       # which an earlier triage regex had skipped), `_materialize_bridge` /
                       # `_materialize_str_bridge` x2, and the three `_Unparser` writers),
                       # 14 after wave 8 (relaunch #17: the MAP-KEY MODEL SPLIT —
                       # `map <k> <v>` admitted to the same OPT-IN allowlist, plus a
                       # PER-CALLEE StrSet retype of `_build_method_return_type_map`.
                       # `_module_binding_names` is a CONVERTED `-> Set[str]` method the
                       # set-union catamorphism emits as the faithful `map string bool`,
                       # while that map recorded the generic `map int (option int)` — so
                       # `name in self._module_binding_names()` int-HASHED its key against
                       # an unconstrained int-keyed map. This is backlog 1b(A)'s rejected
                       # GLOBAL `Set[str]` retype, made safe by using the marker as the
                       # PER-CONSUMER gate that attempt lacked), 13 after wave 9
                       # (relaunch #19: the `_csl_to_ir` CERTIFIED-BOUNDARY BROKEN — 92 of
                       # the 125 bypassing sites, the largest single item this metric ever
                       # held, in ONE increment. Not a new capability: the recorded blocker
                       # said the 75-member family's effect summary "cannot be made exact BY
                       # CONSTRUCTION", and that is true of exactly TWO of them. Driving
                       # `#@ assigns`/`#@ raises`/`#@ \diverges` to a fixpoint against Why3's
                       # OWN error text — the recorded reopening capability, built as a loop
                       # rather than an analysis — converged in 57 iterations and the whole
                       # family became one concrete `let rec ... with` group, 1481/1481 Valid)
                       # — a RATCHET, only lower it
MIRROR_COUNT = 52      # mirrors that emit a .mlw; a smaller population is NOT a pass

_DEF = re.compile(r'^  (?:let rec|let|with) ([A-Za-z_0-9]+)', re.M)
_VAL = re.compile(r'^  val (self__([A-Za-z_0-9]+)_(\d+)) ', re.M)


def emit_all(out_dir: str) -> None:
    py = os.path.join(ROOT, ".venv", "bin", "python3")
    if not os.path.exists(py):
        py = sys.executable
    env = dict(os.environ, PYTHONHASHSEED="0")
    for src in sorted(glob.glob(os.path.join(MIRROR, "**", "*.py"), recursive=True)):
        mlw = src[:-3] + ".mlw"
        if os.path.exists(mlw):
            os.remove(mlw)
        subprocess.run(
            [py, os.path.join(ROOT, "src", "pycsl", "pycsl.py"), src,
             "--import-path", os.path.join(ROOT, "src", "pycsl"),
             "--no-proof", "--keep-mlw"],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(mlw):
            rel = os.path.relpath(src, MIRROR)[:-3].replace(os.sep, "_")
            # `shutil.move`, NOT `os.replace`: the emitted `.mlw` lands next to the SOURCE
            # (under the repo) while the default scratch dir may be on another filesystem,
            # and `os.replace` then dies with `Invalid cross-device link` — BEFORE the
            # check reports anything. A gate that raises before it reports is
            # indistinguishable from a gate that found nothing (lesson (hh)'s sibling), and
            # this one exists precisely to catch a defect no other plane sees.
            shutil.move(mlw, os.path.join(out_dir, rel + ".mlw"))


def scan(emit_dir: str):
    """(shadowed, call_sites) — shadowed methods and the call sites that bypass them."""
    shadowed, sites = [], 0
    for f in sorted(glob.glob(os.path.join(emit_dir, "*.mlw"))):
        s = open(f).read()
        defs = set(_DEF.findall(s))
        for full, meth, _ar in _VAL.findall(s):
            hit = [d for d in defs if d.endswith("__" + meth)]
            if not hit:
                continue        # the callee really is a `\trusted` stub — expected
            uses = len(re.findall(r"\b" + re.escape(full) + r"\b", s)) - 1
            if uses <= 0:
                continue        # declared but never applied — no bypass
            concrete = len(re.findall(r"\(" + re.escape(hit[0]) + r" ", s))
            shadowed.append((os.path.basename(f), full, hit[0], uses, concrete))
            sites += uses
    return shadowed, sites


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", help="directory of already-emitted mirror .mlw files")
    ap.add_argument("--max", type=int, default=BASELINE)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    try:
        return _run(args)
    finally:
        _cleanup()


_TMP: list = []


def _cleanup() -> None:
    for d in _TMP:
        shutil.rmtree(d, ignore_errors=True)
    scratch = os.path.join(ROOT, ".gate-scratch")
    if os.path.isdir(scratch) and not os.listdir(scratch):
        os.rmdir(scratch)


def _run(args) -> int:
    tmp = None
    emit_dir = args.emit_dir
    if not emit_dir:
        # Default the scratch dir UNDER THE REPO, so the emitted `.mlw` files never have
        # to cross a filesystem boundary at all (belt and braces with `shutil.move`).
        _scratch = os.path.join(ROOT, ".gate-scratch")
        os.makedirs(_scratch, exist_ok=True)
        tmp = tempfile.mkdtemp(prefix="shadowed-selfcalls-", dir=_scratch)
        _TMP.append(tmp)
        emit_all(tmp)
        emit_dir = tmp
    if not glob.glob(os.path.join(emit_dir, "*.mlw")):
        print("[!] shadowed-selfcalls: no .mlw files found — nothing measured "
              "(is `why3` on PATH? see wall-lessons (aa))")
        return 1

    n_files = len(glob.glob(os.path.join(emit_dir, "*.mlw")))
    shadowed, sites = scan(emit_dir)
    if args.verbose:
        for f, val, definition, uses, concrete in sorted(
                shadowed, key=lambda r: -r[3]):
            print(f"    {uses:3d} bypassing use(s), {concrete} concrete   "
                  f"{f}::{val} shadows `{definition}`")
    print(f"[*] shadowed-selfcalls: scanned {n_files} emitted mirror(s); "
          f"{len(shadowed)} CONVERTED method(s) whose call sites go through an abstract "
          f"`val self__<m>_<n>`; {sites} bypassing call site(s).")
    if n_files < MIRROR_COUNT:
        print(f"[!] shadowed-selfcalls: only {n_files} of {MIRROR_COUNT} mirrors emitted — "
              f"the population is INCOMPLETE, so this measurement is not a gate result. "
              f"(is `why3` on PATH? see wall-lessons (aa))")
        return 1
    if len(shadowed) > args.max:
        print(f"[!] shadowed-selfcalls: {len(shadowed)} > allowed {args.max} — a "
              f"conversion landed whose body no caller can see.")
        return 1
    print(f"[+] shadowed-selfcalls: OK (ratchet {args.max}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
