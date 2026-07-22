#!/usr/bin/env python3
r"""Vacuity gate: find CONVERTED mirror methods whose emitted WhyML ignores their inputs.

Why this exists (wall-lessons (l)). The campaign's anti-facade check is a MUTATION TEST:
perturb a discriminant in the body, and the emitted `.mlw` must change. That test is
necessary but NOT sufficient, and it misses an entire facade family. When a body is
int-hash-erased, a Python literal is emitted as `stable_hash("String") = 1153884070`, so
changing the literal DOES change the emitted `.mlw` — the mutation test passes — while the
body still never touches its parameter:

    def uses_string(obj):                     let irscanner__uses_string (obj: int) : int =
        if isinstance(obj, dict):               if ((typeof_op 315) = 4) then
            if obj.get("type") == "String":       if ((obj_get_1 1342639453) = 1153884070) then
                return True                         raise (Return 1)
            return any(... for v in obj.values())  else raise (Return (if any_1 (Array.make 1 0) ...
        ...                                     ^^ `obj` appears NOWHERE in the body

`typeof_op 315` and `obj_get_1 1342639453` are applied to HASH CONSTANTS, not to `obj`. The
proof is then vacuous with respect to the input: it establishes nothing about what the
function computes, yet the method is booked as converted.

The test here is structural and cannot be fooled that way: a function whose executable body
never mentions a parameter cannot compute anything about it.

FALSE POSITIVES ARE EXCLUDED BY CROSS-CHECK, not by a denylist. Plenty of emitter methods
legitimately ignore their argument (`_csl_nil(node)` returns the empty-list literal; the
ghost `_handle_*_empty_expr` handlers emit a constant). So a function is reported ONLY when
the LIVE Python body USES the parameter and the emitted WhyML does not. That difference is
the erasure.

Usage:  bin/check-emitted-vacuity.py [--emit]
        --emit   regenerate the .mlw files first (slow; otherwise reuses existing ones)
Exit 1 if any erased function is found.
"""
import ast
import os
import re
import subprocess
import sys

MIRROR_ROOT = "src/self-annotate/src"
LIVE_ROOT = "src/pycsl"
SKIP_PARAMS = {"self"}

# ---------------------------------------------------------------------------
# KNOWN, ACCEPTED erasures — enumerated so a NEW one fails the gate.
#
# This is a ledger, not an excuse list: each entry is a function that is currently booked as
# CONVERTED while its emitted body ignores an input its live body uses. They are gated here so
# the exit status stays meaningful; removing an entry (by making the function real) is progress,
# adding one requires a recorded reason.
#
# Root cause for all of these: `any(genexp)` lowers to the unconstrained `val any_1 (a: array
# int) : bool` applied to a fabricated `Array.make 1 0`, and `obj: Any` int-erases. See
# getting-better/genexp-erasure-wall.md and its review. Route R2 (a bounded, iff-specified
# any/all fold) is expected to clear the IRScanner block.
#
# NOTE (review §4c): this probe is a LOWER BOUND. It is a whole-FUNCTION test, so a function that
# erases one read while still using its other parameters is invisible to it. At least two more
# verified functions carry a live, branch-controlling `any_1` and are NOT listed here because the
# probe cannot see them: `statements.py::_handle_fieldassign_stmt` and
# `Module5_IREmitter.py::_union_arm_tag`.
KNOWN_ERASURES = {
    # IRScanner generic-`Any`-tree predicates — fully erased (`obj` absent from the body).
    "irscanner___check", "irscanner__uses_array_lit", "irscanner__uses_minmax",
    "irscanner__uses_ord_chr", "irscanner__uses_set_card", "irscanner__uses_string",
    "irscanner__uses_subscript", "irscanner__uses_sum",
    # Partial erasures.
    "irscanner__is_recursive",                              # keeps `name`, erases `obj`
    "pycsltojsonemitter___collect_class_constants",         # erases `field_names`
    "ghostspecopsmixin___handle_mktuple_expr",              # erases `lr`
    # `Set[str].add(param)` emits a literal `()` — a DIFFERENT, live-tool faithfulness bug in the
    # wall-lessons (h) family (param-collection mutation), not genexp erasure. Filed there.
    "statementemissionmixin___emit_new_ghost_ref",          # erases `target`
}


def emitted_functions(mlw_text):
    """{whyml_fn_name: (params, executable_body)} for every `let` (VERIFIED) function.

    The body starts at the first top-level `=`, so one-line definitions
    (`let function is_pdict (v: pyval) : bool = match v with ...`) are handled — reading the
    body from the NEXT line instead reports every such definition as ignoring its parameter.
    `val` declarations are skipped: they are the trusted stubs, which have no body by design.
    """
    lines = mlw_text.split("\n")
    out = {}
    i = 0
    stop = re.compile(r"  (let|val|end\b|type |exception |predicate |function |axiom |lemma |clone |use )")
    while i < len(lines):
        m = re.match(r"  let (?:rec |function |ghost )*(\w+)\b", lines[i])
        if not m:
            i += 1
            continue
        name = m.group(1)
        chunk = [lines[i]]
        k = i + 1
        while k < len(lines) and not stop.match(lines[k]):
            chunk.append(lines[k])
            k += 1
        txt = "\n".join(chunk)
        head, _, body = txt.partition("=")
        params = re.findall(r"\((\w+)\s*:", head)
        body = re.sub(r"^\s*(requires|ensures|writes|reads|raises|variant|returns)\s*\{.*$",
                      "", body, flags=re.M)
        out[name] = (params, body)
        i = k
    return out


class _BlankStrings(ast.NodeTransformer):
    """Replace every string constant with a fixed placeholder.

    Without this the probe reports false positives: `_py_stmt_break(stmt, ir_stmts)` has the
    body `ir_stmts.append({"stmt": "Break"})`, and a naive `\\bstmt\\b` search matches the
    dict KEY, concluding the live body "uses" the `stmt` parameter when it does not. Only
    identifier occurrences count as a use."""

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return ast.copy_location(ast.Constant(value="\x00str"), node)
        return node


def live_functions(path):
    """{fn_name: (params, body_text)} for the live Python source, string literals blanked."""
    out = {}
    for n in ast.walk(ast.parse(open(path).read())):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            params = [a.arg for a in n.args.args if a.arg not in SKIP_PARAMS]
            body = "\n".join(
                ast.unparse(ast.fix_missing_locations(_BlankStrings().visit(s)))
                for s in n.body)
            out[n.name] = (params, body)
    return out


def uses(ident, text):
    return re.search(r"\b" + re.escape(ident) + r"\b", text) is not None


def main():
    if "--emit" in sys.argv:
        files = [os.path.join(r, f) for r, _, fs in os.walk(MIRROR_ROOT)
                 for f in fs if f.endswith(".py")]
        subprocess.run(
            ["xargs", "-P", "7", "-I", "{}", "sh", "-c",
             "PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py {} --import-path src/pycsl "
             "--no-proof --no-typecheck --keep-mlw >/dev/null 2>&1"],
            input="\n".join(files), text=True, check=False)

    full, partial = [], []
    for root, _dirs, files in os.walk(MIRROR_ROOT):
        for fn in sorted(files):
            if not fn.endswith(".mlw"):
                continue
            mlw = os.path.join(root, fn)
            live = os.path.join(root.replace(MIRROR_ROOT, LIVE_ROOT, 1),
                                fn[:-4] + ".py")
            if not os.path.exists(live):
                continue
            emitted = emitted_functions(open(mlw).read())
            lf = live_functions(live)
            for wname, (wparams, wbody) in emitted.items():
                real = [p for p in wparams if p not in SKIP_PARAMS]
                if not real:
                    continue
                pyname = wname.split("__")[-1]
                cand = lf.get(pyname) or lf.get("_" + pyname)
                if cand is None:
                    continue                      # no live counterpart to compare against
                lparams, lbody = cand
                # a param is ERASED when the live body uses it and the emitted body does not
                erased = [p for p in real
                          if p in lparams and uses(p, lbody) and not uses(p, wbody)]
                if not erased:
                    continue
                rel = os.path.relpath(mlw)
                (full if len(erased) == len(real) else partial).append(
                    (rel, wname, pyname, erased, real))

    new = [r for r in full + partial if r[1] not in KNOWN_ERASURES]
    known = [r for r in full + partial if r[1] in KNOWN_ERASURES]
    fixed = KNOWN_ERASURES - {r[1] for r in full + partial}

    for tier, rows, what in ((0, full, "EVERY parameter"), (1, partial, "SOME parameters")):
        rows = [r for r in rows if r[1] in KNOWN_ERASURES]
        if not rows:
            continue
        print(f"[~] emitted-vacuity (KNOWN, gated): {len(rows)} verified function(s) ignore "
              f"{what} the live body uses:")
        for rel, wname, pyname, erased, real in rows:
            print(f"    {rel}::{wname}  erased={erased} of {real}  (live `{pyname}`)")

    if fixed:
        print(f"[+] emitted-vacuity: {len(fixed)} known erasure(s) NO LONGER erased — remove from "
              f"KNOWN_ERASURES: {', '.join(sorted(fixed))}")

    if new:
        print(f"[!] emitted-vacuity: {len(new)} NEW erasure(s) — a verified function's emitted "
              f"body ignores an input its live body uses, and it is not in the known ledger:")
        for rel, wname, pyname, erased, real in new:
            print(f"    {rel}::{wname}  erased={erased} of {real}  (live `{pyname}`)")
        print("    A mutation test does NOT catch these: the changed literal's hash still moves "
              "the emitted output. See getting-better/genexp-erasure-wall.md.")
        return 1

    print(f"[+] emitted-vacuity: no NEW erasure ({len(known)} known, gated). NOTE: this probe is a "
          f"LOWER BOUND — a whole-function test cannot see a function that erases one read while "
          f"still using its other parameters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
