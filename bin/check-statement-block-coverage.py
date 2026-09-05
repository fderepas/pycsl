#!/usr/bin/env python3
"""FRONT-END STATEMENT-BLOCK COVERAGE — does Module 5 carry every SUB-BLOCK of a
Python statement into the IR?

THE DEFECT CLASS. `bin/check-ir-field-coverage.py` asks the same question one stage
later: "does the Module 6 handler for this IR node read every field the node
declares?". It has nothing to say about the stage BEFORE the IR, and route #38 lived
exactly there — `Module5_IREmitter._py_stmt_with` reads `stmt.body` and the mutex
annotation and NOTHING ELSE, so the context-manager protocol never reaches the IR at
all. A `with c: pass` arrives at Module 6 as a bare `Pass`, and the emission for

    c = CM(); with c: pass; return c.n        # __exit__ sets n = 5

was `let c = { n = 0 } in (); c.n`, which proved `\\result == 0` while Python
returns 5.

A sub-block that never reaches the IR cannot be recovered downstream, and NOTHING in
the battery could see it: the mirror-sync plane compares bodies, the proof sees the
emission, the byte-diff sees files, and `check-dropped-mutation` counts the shapes
somebody thought to enumerate. This gate reads the AST-node CONTRACT — the sub-block
fields CPython's grammar gives each statement — and asks whether the handler mentions
each one.

WHAT A HIT MEANS. It means the handler never names that block, so whatever the user
wrote there is absent from the model. That is not automatically an unsoundness — it is
only one if nothing REFUSES the shape — which is why the population is held by a ratchet
rather than pinned at zero.

THE THREE BASELINED HITS, all real and all currently fail-closed:
  For.orelse / While.orelse   `for ... else:` / `while ... else:` — REFUSED at the
      front end with a message naming the drop ("the IR emitter reads only the loop
      body, so the clause would be silently DROPPED").
  With.items                  the context-manager protocol — ROUTE #38. Refused as of
      relaunch #45 for a class that defines `__enter__`/`__exit__`; a `@contextmanager`
      generator is still admitted, which is a SCOPING decision recorded in
      `docs/pycsl-translational-reference.md` §T.5.10b, not a soundness claim.
So the honest reading of a green run is: every sub-block the front end drops is a
sub-block something else refuses. A NEW hit means that pairing has been broken.

DELEGATION. Module 5 hands most compound statements to a helper (`_py_stmt_for` is one
line: `ir_stmts.append(self._process_for(stmt))`), so the search follows `self.<method>`
calls transitively. Without that the first version reported TEN hits, seven of them
false — and relaunch #44 removed a fallback in `check-ir-field-coverage.py` for exactly
that reason: a baseline of false positives trains the reader to ignore the gate, which
is strictly worse than the blind spot it closes.

SOUND IN ONE DIRECTION, like the other coverage planes: a handler that mentions a
field may still mishandle it, so a green run is not a proof of faithfulness. A handler
that never mentions it cannot possibly be carrying it.
"""
import argparse
import ast
import json
import textwrap
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M5 = os.path.join(ROOT, "src", "pycsl", "frontend", "Module5_IREmitter.py")
BASELINE = os.path.join(ROOT, "bin", ".statement-block-coverage.json")

# The sub-block fields of every compound Python statement, from the CPython ASDL.
# `items` is included for `With`: it is where the context managers live, and route #38
# is precisely the case of a handler reading `body` and not `items`.
BLOCKS = {
    "FunctionDef":      ["body", "decorator_list"],
    "AsyncFunctionDef": ["body", "decorator_list"],
    "ClassDef":         ["body", "decorator_list", "bases", "keywords"],
    "For":              ["body", "orelse"],
    "AsyncFor":         ["body", "orelse"],
    "While":            ["body", "orelse"],
    "If":               ["body", "orelse"],
    "With":             ["items", "body"],
    "AsyncWith":        ["items", "body"],
    "Try":              ["body", "handlers", "orelse", "finalbody"],
    "TryStar":          ["body", "handlers", "orelse", "finalbody"],
    "Match":            ["cases"],
}

# Module 5 dispatches by an explicit table (`ast.With: "_py_stmt_with"`) and by
# `visit_<Name>`. Both spellings are accepted.
def handlers_for(stmt_name, funcs, dispatch):
    out = {}
    for cand in (dispatch.get(stmt_name), "_py_stmt_" + stmt_name.lower(),
                 "visit_" + stmt_name):
        if cand and cand in funcs:
            out[cand] = funcs[cand]
    return out


# DELEGATION IS THE RULE HERE, NOT THE EXCEPTION, and the first version of this gate
# reported ten hits because of it: `_py_stmt_for` is one line — `ir_stmts.append(
# self._process_for(stmt))` — so the sub-block names live in `_process_for`. A gate whose
# baseline is mostly false positives trains the reader to ignore it, which is strictly
# worse than the blind spot it closes (relaunch #44 REMOVED a fallback for exactly that
# reason). So the search follows `self.<method>(...)` calls transitively.
def stmt_field_reads(seed, funcs, trees, depth=4):
    """Every `<stmt-param>.<field>` read reachable from a handler, FOLLOWING THE
    PARAMETER rather than the text.

    The first version unioned the SOURCE TEXT of every transitively reachable method
    and asked whether the field name appeared anywhere in it. That gate could not
    fail: renaming `stmt.body` to `stmt.XbodyX` inside `_py_stmt_with` left it GREEN,
    because `.body` occurs in some other delegate. It is the same mistake relaunch #44
    made in the first version of `check-ir-field-coverage.py` — "a name appearing
    somewhere says nothing about whether the handler for THAT node reads it" — and it
    is worth restating, because the second time it arrived disguised as a fix for false
    positives.

    So the walk carries the NAME OF THE STATEMENT PARAMETER. `_py_stmt_for(self, stmt,
    ...)` reads `stmt.<f>`; when it calls `self._process_for(stmt)`, the callee's FIRST
    non-self parameter becomes the statement parameter there. A call that does not pass
    the statement along does not extend the search.
    """
    reads = set()
    seen = set()
    frontier = list(seed)                      # (func_name, param_name)
    while frontier and depth > 0:
        depth -= 1
        nxt = []
        for fname, pname in frontier:
            if (fname, pname) in seen:
                continue
            seen.add((fname, pname))
            node = trees.get(fname)
            if node is None or not pname:
                continue
            for n in ast.walk(node):
                if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                        and n.value.id == pname):
                    reads.add(n.attr)
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and isinstance(n.func.value, ast.Name)
                        and n.func.value.id == "self"
                        and n.func.attr in trees):
                    callee = trees[n.func.attr]
                    cargs = [a.arg for a in callee.args.args if a.arg != "self"]
                    for i, a in enumerate(n.args):
                        if (isinstance(a, ast.Name) and a.id == pname
                                and i < len(cargs)):
                            nxt.append((n.func.attr, cargs[i]))
        frontier = nxt
    return reads


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update", action="store_true",
                    help="rewrite the baseline from the current measurement")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    src = open(M5).read()
    tree = ast.parse(src)
    funcs = {n.name: ast.get_source_segment(src, n) or ""
             for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    trees = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

    # The dispatch table: `ast.With: "_py_stmt_with"`.
    dispatch = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Dict):
            for k, v in zip(n.keys, n.values):
                if (isinstance(k, ast.Attribute) and isinstance(k.value, ast.Name)
                        and k.value.id == "ast" and isinstance(v, ast.Constant)
                        and isinstance(v.value, str)):
                    dispatch[k.attr] = v.value

    unread, unmatched = [], []
    checked = 0
    for stmt_name, blocks in sorted(BLOCKS.items()):
        hs = handlers_for(stmt_name, funcs, dispatch)
        if not hs:
            unmatched.append(stmt_name)
            continue
        seed = []
        for nm in hs:
            node = trees.get(nm)
            if node is None:
                continue
            ps = [a.arg for a in node.args.args if a.arg != "self"]
            if ps:
                seed.append((nm, ps[0]))
        reads = stmt_field_reads(seed, funcs, trees)
        for b in blocks:
            checked += 1
            if b not in reads:
                unread.append("%s.%s   [handler(s): %s]"
                              % (stmt_name, b, ", ".join(sorted(hs))))

    print("[*] statement-block-coverage: %d compound statement kind(s), %d sub-block "
          "field(s) checked; %d kind(s) with NO Module 5 handler; %d sub-block(s) the "
          "handler never names."
          % (len(BLOCKS), checked, len(unmatched), len(unread)))
    if unmatched:
        print("    NO HANDLER  " + ", ".join(sorted(unmatched)))
    if args.verbose or args.update:
        for u in unread:
            print("    UNCARRIED  " + u)

    if args.update or not os.path.exists(BASELINE):
        with open(BASELINE, "w") as fh:
            json.dump({"uncarried": sorted(unread)}, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print("[+] statement-block-coverage: baseline written (%d uncarried)"
              % len(unread))
        return 0

    base = json.load(open(BASELINE)).get("uncarried", [])
    new = sorted(set(unread) - set(base))
    gone = sorted(set(base) - set(unread))
    for g in gone:
        print("    FIXED      " + g)
    if new:
        for n in new:
            print("    NEW        " + n)
        print("[-] statement-block-coverage: %d NEW uncarried sub-block(s). A block the "
              "front end never names cannot reach the IR, and nothing downstream can "
              "recover it — route #38 was exactly this." % len(new))
        return 1
    print("[+] statement-block-coverage: OK — %d uncarried sub-block(s), all baselined."
          % len(unread))
    return 0


if __name__ == "__main__":
    sys.exit(main())
