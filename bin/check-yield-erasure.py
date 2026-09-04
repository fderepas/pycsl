#!/usr/bin/env python3
r"""L-PLANE ORACLE: a CONVERTED GENERATOR whose `yield`ed VALUES are dropped on the floor.

WHY THIS EXISTS (relaunch #31). Module 6 has no model for a Python generator. A `yield`
statement lowers to `let _ = 0 in ()` — the yielded expression is evaluated for nothing and
discarded — and the surrounding `def` is emitted as an ordinary function. For a generator
whose ONLY meaning is the sequence it produces, that is a total erasure:

    def iter_child_nodes(node):            let iter_child_nodes (node: int) : unit
        for _name, field in ...:      =>     ...
            if isinstance(field, AST):       if (py_isinstance_AST_int_op field) then
                yield field                    let _ = 0 in ()          <-- the whole method

That method was CONVERTED and PROVED in relaunch #30 and no plane saw it:
  * L3-tc passes — a `unit`-returning body is perfectly well typed;
  * `check-untrusted-emitted` passes — it IS emitted as a definition, not re-abstracted;
  * `check-emitted-vacuity` passes — the body still READS `node` (`iter_fields node`), so
    it is not input-blind, and that probe is explicitly a LOWER BOUND;
  * `check-shadowed-selfcalls` passes — nothing is routed through an avatar;
  * the mirror byte-diff and both fidelity scripts are indifferent.
The proof was real and it established nothing about what the generator yields.

THE RULE. A converted (un-trusted) mirror function whose body contains a VALUE-carrying
`yield` must be emitted in a form that can carry those values. Two mechanical symptoms of
the erasure, either of which fails:
  (1) the emitted definition returns `unit` — a `unit` result cannot carry a sequence;
  (2) the emitted body contains the dropped-value placeholder `let _ = 0 in ()`.
`frontend/ir_inline._walk_dicts` passes both: the emitter has a real recognizer for it and
emits `let rec _walk_dicts (obj: pyval) : list pyval` with a genuine `Cons`.

A VALUELESS `yield` (the `@contextmanager` suspension point in `_Unparser.block` /
`_Unparser.delimit`) drops no value, but it does drop the SUSPENSION: the emitted body runs
the pre-yield and post-yield effects back to back, with the caller's `with`-block nowhere.
That is a weaker, differently-shaped unfaithfulness, so it is reported and RATCHETED rather
than failed — lowering it needs a context-manager model, not a bug fix.

Usage:
    bin/check-yield-erasure.py [--emit-dir DIR] [--max-value N] [--max-void N] [--verbose]

With no `--emit-dir` the mirrors are emitted into a scratch dir under the repo.
"""
import argparse
import ast
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")

MAX_VALUE_YIELD = 0    # a converted generator whose yielded VALUES are erased. HARD 0 —
                       # `iter_child_nodes` was the only one and it is re-trusted.
MAX_VOID_YIELD = 2     # `_Unparser.block`, `_Unparser.delimit` — `@contextmanager`
                       # suspension points. RATCHET, only lower it. Lowering needs a
                       # context-manager model (the caller's `with`-body belongs BETWEEN
                       # the pre- and post-yield effects), not a one-line fix.

DROPPED = "let _ = 0 in ()"


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
            shutil.move(mlw, os.path.join(out_dir, rel + ".mlw"))


def _is_trusted(lines, fn) -> bool:
    """True if a `#@ \\trusted` marker sits in the comment block above `fn`."""
    i = min([d.lineno for d in fn.decorator_list] + [fn.lineno]) - 2
    while i >= 0:
        st = lines[i].strip()
        if not (st.startswith("#") or st.startswith("@") or st == ""):
            return False
        if "\\trusted" in st:
            return True
        i -= 1
    return False


def _own_yields(fn):
    """(value_yields, void_yields) directly in `fn` — a nested `def` has its own."""
    val = void = 0
    stack = list(fn.body)
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if isinstance(n, ast.Yield):
            if n.value is None:
                void += 1
            else:
                val += 1
        elif isinstance(n, ast.YieldFrom):
            val += 1
        for ch in ast.iter_child_nodes(n):
            stack.append(ch)
    return val, void


def collect_generators():
    """[(relpath, qualname, method, value_yields, void_yields)] for CONVERTED generators."""
    out = []
    for src in sorted(glob.glob(os.path.join(MIRROR, "**", "*.py"), recursive=True)):
        text = open(src).read()
        lines = text.split("\n")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        rel = os.path.relpath(src, MIRROR)

        def walk(scope, cls):
            for n in scope:
                if isinstance(n, ast.ClassDef):
                    walk(n.body, n.name)
                elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if _is_trusted(lines, n):
                        continue
                    v, z = _own_yields(n)
                    if v or z:
                        out.append((rel, (cls + "." if cls else "") + n.name, n.name, v, z))
        walk(tree.body, None)
    return out


_DEF_HEAD = re.compile(r"^  (?:let rec|let|with)\s+([A-Za-z_0-9]+)([^\n]*)$", re.M)


def emitted_defs(emit_dir):
    """{mlw-stem: {whyml-name: (signature_line, body_text)}}"""
    out = {}
    for f in sorted(glob.glob(os.path.join(emit_dir, "*.mlw"))):
        s = open(f).read()
        stem = os.path.basename(f)[:-4]
        heads = list(_DEF_HEAD.finditer(s))
        d = {}
        for i, m in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(s)
            d[m.group(1)] = (m.group(2), s[m.start():end])
        out[stem] = d
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir")
    ap.add_argument("--max-value", type=int, default=MAX_VALUE_YIELD)
    ap.add_argument("--max-void", type=int, default=MAX_VOID_YIELD)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    tmp = None
    emit_dir = args.emit_dir
    if not emit_dir:
        scratch = os.path.join(ROOT, ".gate-scratch")
        os.makedirs(scratch, exist_ok=True)
        tmp = tempfile.mkdtemp(prefix="yield-erasure-", dir=scratch)
        emit_dir = tmp
        emit_all(emit_dir)
    try:
        return _run(args, emit_dir)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
        scratch = os.path.join(ROOT, ".gate-scratch")
        if os.path.isdir(scratch) and not os.listdir(scratch):
            os.rmdir(scratch)


MIN_EMITTED_MIRRORS = 40   # a correct sweep emits 53; a corpus/empty dir yields 0

# (#44) THE ZERO-INPUT GUARD. A gate given an `--emit-dir` that holds no mirror emissions
# — an empty directory, a stale one, or a CORPUS emit dir — measures nothing and reports a
# clean bill of health. That is not hypothetical: #43 lowered
# `check-avatar-frame-parity.py`'s INHERITED ratchet from 7 to 1 on the strength of three
# such runs ("twice at HEAD, once at 13c4860b, all three agreeing"), all three pointed at
# directories with zero mirror `.mlw` files in them, and left that plane RED for a whole
# relaunch while the handoff recorded it as tightened. Worse, this gate's own green line
# then reads "N < ratchet — lower the constant", i.e. it actively invites the mistake.
# So: a run that finds no emitted mirror REFUSES to report a verdict (exit 2).


def _run(args, emit_dir) -> int:
    defs = emitted_defs(emit_dir)
    if len(defs) < MIN_EMITTED_MIRRORS:
        print("[!] yield-erasure: found %d emitted mirror(s) in %r, expected at least %d. "
              "That is not a mirror emission — REFUSING to report a verdict rather than "
              "call it green. Emit the mirrors with `--import-path src/pycsl` first."
              % (len(defs), emit_dir, MIN_EMITTED_MIRRORS))
        return 2
    gens = collect_generators()
    bad_value, bad_void, modelled = [], [], []
    for rel, qual, meth, v, z in gens:
        stem = rel[:-3].replace(os.sep, "_")
        table = defs.get(stem, {})
        # Match the emitted WhyML name in PRIORITY order: the exact module-level name,
        # then the class-mangled `<cls>__<meth>`, then a bare `_`-joined tail. A plain
        # "shortest match" is WRONG and was measured wrong: `_Unparser.block` matched
        # `_fin_block` (shorter than `_unparser__block`) and the method was silently
        # reported as absent — a gate that misidentifies its subject reports a clean bill
        # of health, which is the failure mode lesson (bd) is about.
        cls = qual[:-(len(meth) + 1)] if qual.endswith("." + meth) and "." in qual else ""
        # The emitted name is `<class>__<method>` with the class lower-cased
        # (`_Unparser.block` -> `_unparser__block`), or the bare name for a module-level
        # function. Both halves matter: `pure_ast` also defines `_Parser.block`, and an
        # `endswith("__block")` match sorted alphabetically picks `_parser__block` — the
        # WRONG method, whose body has no dropped yield, so the real one is reported clean.
        # A gate that misidentifies its subject issues a clean bill of health, which is
        # exactly the failure mode lesson (bd) is about.
        want = (cls.lower() + "__" + meth) if cls else meth
        name = None
        if want in table:
            name = want
        else:
            cand = sorted(k for k in table if k.endswith("__" + want) or k == want)
            if cand:
                name = cand[0]
        if name is None:
            # not emitted as a definition at all — `check-untrusted-emitted` owns that
            continue
        sig, body = table[name]
        erased = (sig.rstrip().endswith(": unit") or DROPPED in body)
        if v:
            (bad_value if erased else modelled).append((rel, qual, name, v, z))
        elif z and erased:
            bad_void.append((rel, qual, name, v, z))

    print(f"[*] yield-erasure: scanned {len(defs)} emitted mirror(s); "
          f"{len(gens)} CONVERTED generator(s).")
    for rel, qual, name, v, z in modelled:
        print(f"    MODELLED   {rel}::{qual} -> {name} "
              f"({v} value-yield(s) carried by the emitted result)")
    for rel, qual, name, v, z in bad_value:
        print(f"    ERASED     {rel}::{qual} -> {name} "
              f"({v} VALUE-yield(s) dropped; the emitted body computes nothing observable)")
    for rel, qual, name, v, z in bad_void:
        print(f"    SUSPENSION {rel}::{qual} -> {name} "
              f"({z} valueless yield(s); the `with`-body is modelled nowhere)")
    if args.verbose:
        for g in gens:
            print(f"    (all) {g[0]}::{g[1]} value={g[3]} void={g[4]}")

    rc = 0
    if len(bad_value) > args.max_value:
        print(f"[!] yield-erasure: {len(bad_value)} converted generator(s) drop their "
              f"yielded VALUES (max {args.max_value}). A `yield <v>` lowers to "
              f"`{DROPPED}`; a generator emitted this way proves nothing about what it "
              f"produces. Re-trust it, or give the emitter a model that carries the "
              f"sequence (see `_walk_dicts`).")
        rc = 1
    if len(bad_void) > args.max_void:
        print(f"[!] yield-erasure: {len(bad_void)} converted context-manager "
              f"generator(s) (ratchet {args.max_void}) — this is a RATCHET, only lower it.")
        rc = 1
    if rc == 0:
        print(f"[+] yield-erasure: OK ({len(bad_value)} value-erasing, "
              f"{len(bad_void)} suspension-dropping / ratchet {args.max_void}, "
              f"{len(modelled)} genuinely modelled).")
    return rc


if __name__ == "__main__":
    sys.exit(main())
