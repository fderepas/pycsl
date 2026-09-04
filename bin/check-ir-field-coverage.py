#!/usr/bin/env python3
"""check-ir-field-coverage.py — the UNREAD-IR-FIELD plane.

THE DEFECT CLASS THIS CAMPAIGN KEEPS FINDING, stated in one line: *a lowering reads some
of a node's fields and silently drops the rest.* Routes #12 through #21, and #22 and #28,
are all instances. Each was found BY HAND, by reading a handler and noticing a field name
that never appears in it.

This does it mechanically. `src/pycsl/ir_schema.py` declares 111 `StmtIR`/`ExprIR`
subclasses with their fields. For each one, this finds the Module 6 handler(s) that lower
it and reports every declared field whose NAME never appears anywhere in the handler's
source — a field the lowering demonstrably cannot be reading.

WHAT A HIT MEANS, and it is a CANDIDATE and not a verdict. A field can be legitimately
unread: it may be consumed by an earlier pass (Module 3/4/5), by a sibling handler, or it
may be metadata with no run-time meaning. Route #21's `finalbody` and route #20's `items`
were hits of exactly this shape and both were real; the `lineno`/`col_offset` family are
hits of the same shape and are refuted at the value model (#43 checked: the emitted ADT
carries no location payload at all, so nothing can reference them).

So the honest use is: HOLD THE SET, and read anything NEW. The ratchet is on the SET of
(class, field) pairs, not on a count — a new unread field in an existing handler is the
interesting event, and a count would hide it behind a coincidental removal elsewhere.

THE FOUR HITS AT #44, EACH READ AND CLASSIFIED — none is a live erasure:
  `ForStmt.line`, `ForStmt.lineno`, `WhileStmt.line`  — location metadata. The emitted
      ADT carries NO location payload at all (#43 checked: 140+ constructors, not one with
      a lineno/col_offset field), so nothing in a contract can reference them.
  `ForStmt.allow_iteration_mutation` — the `#@ allow_iteration_mutation` opt-out. It is a
      MODULE-4 directive, consumed by the UB-7.1 mutation-during-iteration detector in
      `pycsl.py` and threaded by Module 3 and Module 5. Module 6 has no business reading
      it, and grep confirms all four consumers.

KNOWN LIMIT OF THIS INSTRUMENT, stated because a blind spot that reports "clean" is the
failure this campaign keeps finding: 25 of the 101 classes have NO handler the name-based
matcher can identify — they are lowered inside the big `t == "<Kind>"` dispatcher in
`_expr_to_whyml` rather than by a per-node method. Their fields are NOT checked. The first
version of the matcher missed FORTY, which is why the count is reported on every run.

USAGE
    bin/check-ir-field-coverage.py             # check against the baseline
    bin/check-ir-field-coverage.py --update    # re-baseline (after reading each new one)
    bin/check-ir-field-coverage.py --verbose   # list every unread field
"""
import argparse
import ast
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "src", "pycsl", "ir_schema.py")
M6 = os.path.join(ROOT, "src", "pycsl", "module6_whyml")
BASELINE = os.path.join(ROOT, "getting-better", "ir-field-coverage-baseline.json")

# A field whose name is too generic to look for: it would match text in every handler and
# the result would be meaningless. Recorded rather than silently skipped.
TOO_GENERIC = {"type", "name", "value", "body", "test", "op", "args", "func", "target"}



def _snake(name: str) -> str:
    """`TryStmt` -> `try_stmt`, `AugAssignStmt` -> `aug_assign_stmt`."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def handler_bodies(srcs):
    """{function name: source text} for every def in module6_whyml/."""
    out = {}
    for path, src in srcs.items():
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        lines = src.split("\n")
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(n, "end_lineno", n.lineno)
                out.setdefault(n.name, "")
                out[n.name] += "\n".join(lines[n.lineno - 1:end]) + "\n"
    return out


def handlers_for(cls, handlers):
    """The Module 6 handler(s) that lower `cls`, by the project's naming convention:
    `TryStmt` -> `_handle_try_stmt` / `_py_stmt_try` / `_handle_try_stmt_expr`, etc.
    Returns {name: body}; empty when no handler can be identified, which is reported
    separately rather than silently counted as full coverage."""
    snake = _snake(cls)                      # try_stmt / aug_assign_stmt / bin_op_expr
    stem = re.sub(r'_(stmt|expr)$', '', snake)
    flat = cls.lower()                       # binopexpr / trystmt
    flatstem = re.sub(r'(stmt|expr)$', '', flat)
    cands = {f"_handle_{snake}", f"_handle_{stem}", f"_handle_{stem}_stmt",
             f"_handle_{stem}_expr", f"_py_stmt_{stem}", f"_py_expr_{stem}",
             f"_emit_{snake}", f"_emit_{stem}",
             # The expression side does not use the underscored form: `BinOpExpr` is
             # lowered by `_handle_binop_expr`, not `_handle_bin_op_expr`. Without these
             # the matcher missed FORTY of the 101 classes and silently reported them as
             # fully covered — the "I looked at nothing" failure, in an instrument built
             # to catch exactly that.
             f"_handle_{flat}", f"_handle_{flatstem}", f"_handle_{flatstem}_expr",
             f"_handle_{flatstem}_stmt", f"_emit_{flatstem}", f"_emit_{flatstem}_expr"}
    return {k: v for k, v in handlers.items() if k in cands}

def schema_fields():
    """{class name: [field names]} for every StmtIR/ExprIR subclass."""
    tree = ast.parse(open(SCHEMA).read())
    out = {}
    for c in ast.walk(tree):
        if not isinstance(c, ast.ClassDef):
            continue
        bases = [b.id for b in c.bases if isinstance(b, ast.Name)]
        if not ({"StmtIR", "ExprIR"} & set(bases)):
            continue
        flds = [s.target.id for s in c.body
                if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)]
        if flds:
            out[c.name] = flds
    return out


def module6_sources():
    """{path: source} for every Module 6 lowering file."""
    out = {}
    for fn in sorted(os.listdir(M6)):
        if fn.endswith(".py"):
            p = os.path.join(M6, fn)
            out[os.path.relpath(p, ROOT)] = open(p, errors="replace").read()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    fields = schema_fields()
    srcs = module6_sources()
    all_m6 = "\n".join(srcs.values())

    handlers = handler_bodies(srcs)
    unread = []
    skipped_generic = 0
    unmatched = []
    for cls, flds in sorted(fields.items()):
        hs = handlers_for(cls, handlers)
        if not hs:
            unmatched.append(cls)
            continue
        blob = "\n".join(hs.values())
        for f in flds:
            if f in TOO_GENERIC:
                skipped_generic += 1
                continue
            # A field is READ by THIS handler if its name appears there as an attribute
            # (`.f`), a dict key (`"f"`), or a keyword (`f=`). Searching the WHOLE of
            # Module 6 instead was the first version and it reported ZERO unread fields
            # for the entire schema — a name that appears somewhere says nothing about
            # whether the handler for THAT node reads it, and route #21's `finalbody`
            # would have been invisible.
            pat = re.compile(r'(\.%s\b)|(["\']%s["\'])|(\b%s\s*=)'
                             % (re.escape(f), re.escape(f), re.escape(f)))
            if not pat.search(blob):
                unread.append(f"{cls}.{f}   [handler(s): {', '.join(sorted(hs))}]")

    total_fields = sum(len(v) for v in fields.values())
    print(f"[*] ir-field-coverage: {len(fields)} StmtIR/ExprIR subclass(es), "
          f"{total_fields} declared field(s); {skipped_generic} skipped as too generic "
          f"to search for; {len(unmatched)} class(es) with NO identifiable handler; "
          f"{len(unread)} field(s) never mentioned by their own handler.")
    if args.verbose:
        for u in unread:
            print(f"    UNREAD  {u}")

    if args.update or not os.path.exists(BASELINE):
        with open(BASELINE, "w") as fh:
            json.dump({"unread": sorted(unread), "generic_skipped": sorted(TOO_GENERIC)},
                      fh, indent=2, sort_keys=True)
            fh.write("\n")
        print(f"[+] ir-field-coverage: baseline written ({len(unread)} unread field(s))")
        return 0

    with open(BASELINE) as fh:
        base = set(json.load(fh)["unread"])
    new = [u for u in unread if u not in base]
    gone = [u for u in sorted(base) if u not in set(unread)]
    for u in gone:
        print(f"[+] now read: {u} (re-baseline with --update)")
    if new:
        print(f"[-] ir-field-coverage: {len(new)} NEW unread IR field(s). A field the "
              f"lowering never mentions is the shape of routes #12-#21, #22 and #28: the "
              f"node carries it, the model does not, and nothing else in the battery "
              f"notices. READ each one and decide — it may be consumed by an earlier "
              f"pass, or it may be a live erasure.")
        for u in new:
            print(f"      {u}")
        return 1
    print(f"[+] ir-field-coverage: OK — {len(unread)} unread field(s), all baselined.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
