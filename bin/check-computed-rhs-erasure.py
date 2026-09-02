#!/usr/bin/env python3
r"""L-PLANE ORACLE: a CONVERTED method whose COMPUTED right-hand side was erased to `0`,
or whose PARAMETER'S COLLECTION FIELD was materialised as a fresh constant array.

WHY THIS EXISTS (relaunch #32). Two facade classes were found on the SAME whole-tree
re-census, and neither the probe's regex marker list nor any existing gate plane could see
either one. Both were found by comparing the LIVE SOURCE's shape against the EMITTED body,
which is the only place they are visible: each emits perfectly well-typed WhyML that still
LOOKS like real work.

  (A) COMPUTED RHS ERASED TO 0. A source assignment whose right-hand side is a
      COMPUTATION — a call, an attribute read, a subscript, a comprehension — that the
      emitter has no lowering for is not abstracted to an opaque op (which every existing
      marker would catch); it is replaced by the LITERAL `0`:

          v = getattr(node, "value", None)        ==>   v := 0

      Nothing downstream can tell that apart from a faithful `v = 0`, so every guard that
      consumes `v` is decided by a constant. `Module3_Weaver._region_bound_str` was
      reported CLEAN by the repaired probe in exactly this state: its `!v <> 0` test is
      FALSE on every path, so the whole method collapses to `return "<expr>"`.

  (B) PARAM-FIELD MATERIALISED AS A FRESH CONSTANT ARRAY. A collection field of a
      NON-`self` object has no lowering, so the emitter binds a FRESH local:

          node.csl_invariants.append(c)    ==>   let node_csl_invariants = Array.make 1024 0 in
                                                 ... append into that empty local ...

      The reads AND the mutations both land in a local that is then discarded.
      `PyCSLWeaver._attach_loop_contracts`, whose ENTIRE body is three such appends, was
      also reported CLEAN — because the parameter name `node` DOES appear in the emitted
      body, inside the fresh local's own name. That is the PARAM-side twin of the
      SELF-FIELD ERASURE check the probe already carries.

SUPPRESSION for (A): if the SOURCE itself ever assigns that name a falsy literal, `:= 0`
is a faithful emission and is not reported.

THE RATCHETS are baselined at the honest measurement taken when this gate was written, and
the derivation is recorded beside the constant. Only ever lower them.

Usage:
    bin/check-computed-rhs-erasure.py [--emit-dir DIR] [--max-rhs N] [--max-param N]
                                      [--verbose]

With no `--emit-dir` the mirrors are emitted into a scratch dir under the repo (~40 s).
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

# --------------------------------------------------------------------------------------
# RATCHETS — the honest measurement at the tree that introduced this gate (relaunch #32,
# after the `getattr(self, "<scalar field>", <default>)` capability landed).
#
#   (A) COMPUTED RHS ERASED TO 0 ......... 6
#         frontend/pure_ast.py            copy_location            value
#         frontend/pure_ast.py            unparse_inner            unparser
#         module6_whyml/expressions.py    _handle_field_get_expr   _pg2
#         module6_whyml/expressions.py    _handle_setlit_expr      _poly
#         module6_whyml/functions.py      _refine_tuple_return_type
#                                           _saved_cef _saved_cs _saved_st _saved_teisl
#         module6_whyml/stmt_control_flow.py _infer_return_value_type  symtab
#       FIVE of the six are `getattr(self, "<field>", None|{})` on a NON-scalar modelled
#       field; lowering the ratchet on those needs the three ADJACENT mechanisms recorded
#       in the #32 handoff (map/string truthiness in `_to_bool`, and first-assign local
#       kind inference seeing through `getattr`). `copy_location` is different in kind: its
#       attribute name is a LOOP VARIABLE, so there is no field to resolve, and it is the
#       honest re-trust candidate.
#   (B) PARAM-FIELD MATERIALISED ......... 0  — HARD 0. `_attach_loop_contracts` is the
#       only known instance and it is (correctly) still `\trusted`.
# --------------------------------------------------------------------------------------
MAX_RHS_ERASED = 6
MAX_PARAM_MATERIALIZED = 0

_BLOCK = re.compile(
    r"^  (?:let(?: rec)?(?: partial)?(?: function)?|val|with)\s+([A-Za-z0-9_']+)[^\n]*\n"
    r"(?:(?!^  (?:let|val|with|type|exception|axiom|goal|lemma|predicate|function)\b).*\n)*",
    re.M)


def emit_all(out_dir):
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


def _is_trusted(lines, fn):
    i = min([d.lineno for d in fn.decorator_list] + [fn.lineno]) - 2
    while i >= 0:
        st = lines[i].strip()
        if not (st.startswith("#") or st.startswith("@") or st == ""):
            return False
        if re.match(r"^#@\s*\\trusted\b", st):
            return True
        i -= 1
    return False


def _blocks(path):
    """{whyml-name: block-text} for one emitted .mlw. `val` blocks are kept so a
    re-abstracted method is recognised and SKIPPED (it has no body to erase)."""
    s = open(path).read()
    out = {}
    for m in _BLOCK.finditer(s):
        out.setdefault(m.group(1), m.group(0))
    return out


def _resolve(blocks, cls, name):
    """Resolve a mirror method to its emitted block by the EXACT `<class>__<method>`
    symbol (instrument fact #31/3 — a suffix match makes `_Unparser.block` resolve to
    `_fin_block`, and a gate that misidentifies its subject issues a clean bill of health).
    A module-level function resolves by its bare name."""
    if cls:
        return blocks.get(cls.lower() + "__" + name)
    return blocks.get(name)


def scan(emit_dir, verbose=False):
    rhs_hits, param_hits = [], []
    for src in sorted(glob.glob(os.path.join(MIRROR, "**", "*.py"), recursive=True)):
        rel = os.path.relpath(src, MIRROR)
        mlw = os.path.join(emit_dir, rel[:-3].replace(os.sep, "_") + ".mlw")
        if not os.path.exists(mlw):
            continue
        text = open(src).read()
        lines = text.split("\n")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        blocks = _blocks(mlw)

        def walk(scope, cls):
            for n in scope:
                if isinstance(n, ast.ClassDef):
                    walk(n.body, n.name)
                    continue
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if _is_trusted(lines, n):
                    continue
                blk = _resolve(blocks, cls, n.name)
                if blk is None or blk.lstrip().startswith("val "):
                    continue
                qual = (cls + "." if cls else "") + n.name

                # (B) PARAM-FIELD MATERIALISED AS A FRESH CONSTANT ARRAY
                params = [a.arg for a in n.args.args if a.arg != "self"]
                pf = sorted({(x.value.id, x.attr) for x in ast.walk(n)
                             if isinstance(x, ast.Attribute)
                             and isinstance(x.value, ast.Name)
                             and x.value.id in params})
                mat = [o + "." + f for o, f in pf
                       if re.search(r"\blet %s_%s = \(?Array\.make\b"
                                    % (re.escape(o), re.escape(f)), blk)]
                if mat:
                    param_hits.append((rel, qual, mat))

                # (A) COMPUTED RHS ERASED TO 0
                erased = []
                for a in ast.walk(n):
                    if not isinstance(a, ast.Assign) or len(a.targets) != 1:
                        continue
                    t = a.targets[0]
                    if not isinstance(t, ast.Name):
                        continue
                    if not isinstance(a.value, (ast.Call, ast.Attribute, ast.Subscript,
                                                ast.ListComp, ast.DictComp, ast.SetComp,
                                                ast.GeneratorExp)):
                        continue
                    if any(isinstance(o, ast.Assign) and len(o.targets) == 1
                           and isinstance(o.targets[0], ast.Name)
                           and o.targets[0].id == t.id
                           and isinstance(o.value, ast.Constant)
                           and not o.value.value
                           for o in ast.walk(n)):
                        continue
                    if re.search(r"(?m)^\s*%s := 0\s*;?\s*$" % re.escape(t.id), blk):
                        erased.append(t.id)
                if erased:
                    rhs_hits.append((rel, qual, sorted(set(erased))))
                # A NESTED `def` is emitted as its own WhyML definition under the same
                # class prefix (`_unparser__unparse_inner`), so it is scanned too —
                # `_Unparser.unparse_inner`'s `unparser = type(self)(...)` erases to 0 and
                # the whole closure then operates on the constant.
                walk([c for c in n.body
                      if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef))], cls)

        walk(tree.body, None)
    return rhs_hits, param_hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir")
    ap.add_argument("--max-rhs", type=int, default=MAX_RHS_ERASED)
    ap.add_argument("--max-param", type=int, default=MAX_PARAM_MATERIALIZED)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    tmp = None
    edir = args.emit_dir
    if edir is None:
        tmp = tempfile.mkdtemp(prefix="rhs-erasure-", dir=os.path.join(ROOT, "scratchpad"))
        emit_all(tmp)
        edir = tmp
    try:
        rhs, param = scan(edir, args.verbose)
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)

    print("[*] computed-rhs-erasure: %d converted method(s) with a COMPUTED RHS erased to "
          "0; %d with a PARAM-FIELD materialised as a fresh constant array."
          % (len(rhs), len(param)))
    if args.verbose or len(rhs) > args.max_rhs or len(param) > args.max_param:
        for rel, qual, names in rhs:
            print("    RHS-ERASED       %-38s %-44s %s" % (rel, qual[:44], names))
        for rel, qual, names in param:
            print("    PARAM-MATERIAL   %-38s %-44s %s" % (rel, qual[:44], names))

    rc = 0
    for label, got, want, why in (
            ("computed-RHS-erased", len(rhs), args.max_rhs,
             "The source's read NEVER HAPPENS and every guard consuming it is decided by "
             "a constant."),
            ("param-field-materialised", len(param), args.max_param,
             "The parameter's collection is a FRESH empty local; reads and mutations are "
             "both discarded.")):
        if got > want:
            print("[!] computed-rhs-erasure: %s RATCHET BROKEN — %d > %d. %s"
                  % (label, got, want, why))
            rc = 1
        elif got < want:
            print("[+] computed-rhs-erasure: %s %d < ratchet %d — lower the constant."
                  % (label, got, want))
    if rc == 0:
        print("[+] computed-rhs-erasure: OK (ratchets %d/%d)."
              % (args.max_rhs, args.max_param))
    return rc


if __name__ == "__main__":
    sys.exit(main())
