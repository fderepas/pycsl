#!/usr/bin/env python3
"""Sync-check for the ENTIRE self-annotation mirror (`src/self-annotate/src/`).

The mirror reflects the live emitter `src/pycsl/` (same layout, incl. `frontend/`). It is
HETEROGENEOUS — a whole-file diff is the WRONG tool:

  * un-`\trusted` methods (the body-faithful `_handle_*` handlers) are ported VERBATIM from the
    live emitter — only `#@` contract/loop-invariant annotations are added; and
  * `\trusted` methods are intentionally-divergent bodyless STUBS (the recursion-leaf / sibling
    boundary), which the live emitter implements in full.

So the load-bearing, function-level invariant is what this checks, across EVERY function copied
from `src/pycsl` into the mirror — `self`-methods, module-level helpers, AND the `pycsl.py`
driver functions:

    EVERY un-`\trusted` mirror function has a body byte-IDENTICAL (modulo `#@` lines and blank
    lines) to the same-qualified-named live function.

That is what makes "verify the mirror" mean "the real code is body-faithful": the proof runs on
the ACTUAL emitter code, machine-checked to be a verbatim copy. `\trusted` stubs, mirror-only
functions (no live counterpart), and files with no live counterpart are skipped by design.

Coverage boundary: the mirror is intentionally a SUBSET of the live tree — a live function may be
absent from the mirror (≈147 are, off the verification path), so "live function missing from the
mirror" is NOT treated as drift. Module-level statements (imports, constants) are not diffed;
the load-bearing content is the function bodies. What IS enforced: any function present in BOTH
and un-`\trusted` in the mirror must match live verbatim — this is what catches a stale copy
(e.g. a `pycsl.py` CLI change the mirror didn't track).

This SUPERSEDES the old whole-file `rocq/`/`lean/` tier (empty, abandoned, stale paths) — see
`resync-campaign.md` §Tier-1 and `src/self-annotate/README.md`.

Exit 1 on any drift.
"""
import ast
import os
import sys
import difflib

# Every mirror `.py` under here is checked against its `src/pycsl/` counterpart (same relative
# path — the mirror follows the live layout, including `frontend/` and `module6_whyml/`).
MIRROR_ROOT = "src/self-annotate/src"
LIVE_ROOT = "src/pycsl"


def _normalize(node):
    """A comparison form for a function body that is invariant under the mirror's PERMITTED,
    semantics-preserving additions, and under nothing else.

    Comparing raw source text was the original design and it made this gate USELESS: it fired on
    every `#@` sibling comment, every omitted docstring, and every quote-style difference, so it
    reported 81+ divergences for months and every actor learned to ignore it (wall-lessons (i)).
    A gate that is always red enforces nothing.

    What is permitted, and why each is semantics-preserving:
      * `#@` contract lines and plain `#` comments — comments; `ast.unparse` drops both.
      * a docstring the mirror omits — dropped explicitly below. (Only `__doc__` observes it, and
        nothing in the verification path reads `__doc__`.)
      * string quote style and whitespace/line-wrapping — `ast.unparse` normalizes both.
      * TYPE ANNOTATIONS, which are handled by the caller, not here: the mirror's annotations are
        its modelling layer (`dict` -> `Dict[str, PyVal]`, `ast.expr` -> `"ExprIR"`) and are
        SUPPOSED to differ. Parameter names, order, `*args`/`**kwargs` and defaults are still
        compared, so a renamed or dropped parameter is still drift.

    Everything else — any change to a statement, an operator, a literal value, a call — survives
    normalization and is reported. The mutation test in `--self-test` pins that.
    """
    body = list(node.body)
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        body = body[1:]                      # leading docstring
    return [ast.unparse(_deannotate(stmt)) for stmt in body]


class _DropLocalAnnotations(ast.NodeTransformer):
    """`x: T = v` -> `x = v` for LOCAL variable annotations inside a body.

    Same rationale as parameter annotations: a local annotation is the mirror's modelling layer
    (`new_pat: Dict[str, PyVal] = {...}`), and PEP 526 does not evaluate annotations on local
    variables at runtime, so adding one is semantics-preserving. An ANNOTATION-ONLY statement
    (`x: T` with no value) is a declaration, not an assignment, and is kept — dropping it would
    hide a real body difference."""

    def visit_AnnAssign(self, node):
        self.generic_visit(node)
        if node.value is None:
            return node
        return ast.copy_location(
            ast.Assign(targets=[node.target], value=node.value, type_comment=None), node)


def _deannotate(stmt):
    return ast.fix_missing_locations(_DropLocalAnnotations().visit(stmt))


def _signature(node):
    """Parameter names/order/defaults, WITHOUT annotations (see `_normalize`)."""
    a = node.args
    names = ([p.arg for p in getattr(a, "posonlyargs", [])] + [p.arg for p in a.args]
             + ([f"*{a.vararg.arg}"] if a.vararg else [])
             + [p.arg for p in a.kwonlyargs]
             + ([f"**{a.kwarg.arg}"] if a.kwarg else []))
    defaults = [ast.unparse(d) for d in a.defaults] + \
               [ast.unparse(d) if d is not None else None for d in a.kw_defaults]
    return (names, defaults)


def methods(path):
    """{qualified_name: (stripped_body_lines, is_trusted)} for EVERY function in a file —
    `self`-methods, module-level helpers (`whyml_ident`, `stable_hash`, `_short_type`, …),
    AND the driver functions in `pycsl.py` (`main`, `_run_pipeline`, `_run_proofs`, and their
    nested closures). Every `.py` copied from `src/pycsl` into the mirror is covered, not just
    the emitter's `self`-methods — so a drift in a module-level helper or in the CLI driver
    (a live `pycsl.py` change the mirror didn't track) is caught, not silently missed.

    Names are QUALIFIED (`Class.method`, `outer.inner` for nested defs) so same-named functions
    in different scopes don't collide. `is_trusted` iff a `#@ \\trusted` marker sits in the
    contiguous annotation/decorator/blank block immediately above the `def`."""
    src = open(path).read().split("\n")
    tree = ast.parse("\n".join(src))
    out = {}

    def _trusted_above(lineno):
        # The block above a `def` is `#@` contract lines, decorators, blank lines AND plain `#`
        # comments. Omitting plain `#` from this walk was a real defect: a `\trusted` marker
        # separated from the `def` by a justification comment (as every frame-correction note in
        # the run-#5 soundness pass is) stopped being seen, and the stub was then compared as if
        # it were a claimed-verbatim body. The `#@` parser in `src/pycsl` does NOT have this bug
        # (verified: the affected stubs still emit as `val`, not `let`) — it was local to here.
        i = lineno - 2
        trusted = False
        while i >= 0 and (src[i].strip().startswith("#")
                          or src[i].strip().startswith("@")
                          or src[i].strip() == ""):
            if "\\trusted" in src[i]:
                trusted = True
            i -= 1
        return trusted

    def _walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qn = prefix + child.name
                body = (_signature(child), _normalize(child))
                out[qn] = (body, _trusted_above(child.lineno))
                _walk(child, qn + ".")        # nested closures
            elif isinstance(child, ast.ClassDef):
                _walk(child, prefix + child.name + ".")

    _walk(tree, "")
    return out


def main():
    diverged = 0
    checked = 0
    for root, _dirs, files in os.walk(MIRROR_ROOT):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            mpath = os.path.join(root, fn)
            lpath = mpath.replace(MIRROR_ROOT, LIVE_ROOT, 1)
            if not os.path.exists(lpath):
                continue   # mirror-only file (no live counterpart) — skip
            rel = os.path.relpath(mpath, MIRROR_ROOT)
            mm = methods(mpath)
            lm = methods(lpath)
            for name, (mbody, mtrusted) in mm.items():
                if mtrusted:
                    continue  # intentionally-divergent stub
                if name not in lm:
                    continue  # mirror-only function (e.g. the `mutable_state` decorator,
                              # @dataclass modeling infra) — intentional, not drift
                (msig, mstmts) = mbody
                (lsig, lstmts) = lm[name][0]
                if msig != lsig or mstmts != lstmts:
                    what = ("signature" if msig != lsig else "body")
                    print(f"DIVERGED: {rel}::{name} — un-trusted mirror {what} != live emitter "
                          f"{what}:")
                    if msig != lsig:
                        print(f"  live   params: {lsig[0]} defaults {lsig[1]}")
                        print(f"  mirror params: {msig[0]} defaults {msig[1]}")
                    for dl in list(difflib.unified_diff(
                            lstmts, mstmts, "live", "mirror", lineterm=""))[:30]:
                        print("  " + dl)
                    print("  ---")
                    diverged = 1
                else:
                    checked += 1
    if diverged == 0:
        print(f"OK: all {checked} un-trusted self-annotate mirror functions (self-methods, "
              f"module-level helpers, and pycsl.py driver functions) are verbatim copies of "
              f"the live source")
    sys.exit(diverged)


if __name__ == "__main__":
    main()
