#!/usr/bin/env python3
r"""check-assigns-underdeclaration — a NON-EMPTY `#@ assigns` measured against the LIVE
body's DIRECT self-field writes.

WHY IT EXISTS, and it is a POPULATION hole rather than a new defect class.
`bin/check-trusted-frame-honesty.py` is the plane for a mirror contract that claims a
smaller frame than the live method really has. Its docstring explains the hazard in general
terms, but its CODE is scoped to one spelling:

    :634   if stripped == "#@ assigns \\nothing":  nothing = True
    :637   if (trusted == want_trusted) and nothing:

So BOTH of its populations — trusted and converted — are EXACTLY the methods declaring
`#@ assigns \nothing`. **An under-declared NON-EMPTY `assigns` is exactly as false as an
under-declared empty one, and it was in neither arm.** Measured: 1279 mirror methods carry
an `#@ assigns` clause, **498** of them non-empty, i.e. invisible to that plane.

HOW IT WAS FOUND. By the sweep that lesson (a5) prescribes, on the day (a5) was banked:
`bin/check-type-keyed-constant-answers.py` baselines the emit_ir ALWAYS-PRESENT arms and
ends that baseline "THE FRAME HALF IS STILL UNCHECKED and is the named follow-up: a
self-field write on the branch the model DELETES is invisible to the `assigns` proof,
because the proof only sees the paths the model kept." Locating the guard that would cover
it, and quoting its MATCHING RULE from the code rather than its docstring, produced the two
lines above — and none of that baseline's seven methods declares `\nothing`.

WHAT IT MEASURES. For every mirror method with a NON-EMPTY `#@ assigns`, the DIRECT
`self.<f>` writes of its LIVE twin in the same class. Direct only — no call graph — so
every row is a LOWER BOUND and unarguable. Two verdicts, and the second is the ratchet:

  TRAP  the live body writes a self field the `#@ assigns` clause OMITS.
  HOLE  a TRAP whose omitted field is ALSO DECLARED in the emitting mirror class (or one
        of its bases in the same file), hence present in the emitted RECORD, hence
        MENTIONABLE — so a caller could actually read it and rely on the missing write.

FIRST MEASUREMENT (#49, gen #33): **TRAP 18 field-occurrences across 9 methods, HOLE 0.**
All nine are `\trusted`, which is the population whose contract is ASSUMED and never
checked, so the TRAP count is not cosmetic. Every one of the 18 omitted-field occurrences is
UNDECLARED in its mirror class, so it is absent from the record, unmentionable, and no
caller can prove anything about it. **That is the same cause and the same exact coextension
gen #32 measured from the opposite direction** in `check-assigns-writes-survival`
(TRAP 2989 / HOLE 0), where a field named in `#@ assigns` but never DECLARED is dropped from
the emitted `writes`. The two planes now bracket the frame: gen #32's is
declared-but-not-emitted, this one is written-but-not-declared.

HOLE 0 IS A MEASUREMENT AND NOT A THEOREM, which is exactly why it is ratcheted and
negative-tested: `--self-test` declares one measured-TRAP field in its mirror class and
requires HOLE to fire. The "declared" set is deliberately OVER-approximated (every
class-level annotation in the file, plus in-file bases), so HOLE errs toward firing.

EXIT CODES
  0  TRAP <= MAX_TRAP and HOLE == 0
  1  HOLE > 0, or TRAP above its ceiling
  2  refusal: fewer than MIN_NONEMPTY non-empty clauses seen (the walk is broken)
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
LIVE = os.path.join(ROOT, "src", "pycsl")

ASSIGNS = re.compile(r"^\s*#@\s*assigns\s+(.*)$")
TRUSTED = re.compile(r"^\s*#@\s*\\trusted\b")
SELFF = re.compile(r"self\.([A-Za-z_][A-Za-z_0-9]*)")

MIN_NONEMPTY = 400        # 498 at the first measurement; a walk that sees far fewer is broken
MAX_TRAP = 18             # field-occurrences. LOWER it when a clause is corrected.
                          # (#49) gen #33 first measurement: 18 across 9 methods.

# The measured TRAP rows, kept BY NAME so a new one is visible rather than absorbed into a
# count. Every entry is a `\trusted` stub, and every omitted field is undeclared in its
# class (hence HOLE 0). `--self-test` picks its injection target from this table.
TRAP_BASELINE = {
    ("module6_whyml/functions.py", "FunctionEmissionMixin", "_reset_function_state"): [
        "_erased_truthy_locals", "_fold_unsafe_elems", "_fold_unsafe_sizes",
        "_loop_targets_read_outside", "_r51_bound_names", "_rebound_collections"],
    ("module6_whyml/statements.py", "StatementEmissionMixin", "_emit_body_code"): [
        "_literal_rebind_lens", "_literal_rebind_targets"],
    ("module6_whyml/preamble.py", "PreambleEmissionMixin", "_emit_type_decls"): [
        "_emitted_record_field_types", "_formal_params"],
    ("module6_whyml/expressions.py", "ExpressionEmissionMixin", "_handle_dotted_call"): [
        "_r188_stub_names", "ir"],
    ("module6_whyml/expressions.py", "ExpressionEmissionMixin", "_handle_binop"): [
        "_r55_subsumed_name"],
    ("module6_whyml/types.py", "TypeInferenceMixin", "_track_collection_metadata"): [
        "_rebound_collections"],
    ("frontend/Module3_Weaver.py", "PyCSLWeaver", "visit_Module"): [
        "_csl_bound_names", "_csl_star_import"],
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "visit_Module"): [
        "_globals_lookup_funcs"],
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "_collect_class_fields"): [
        "_m5_dc_unknown"],
}


def _mirror_decls(path):
    """(class, func) -> (declared self fields, trusted, lineno), from the `#@` block
    immediately above each def."""
    text = open(path, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}, {}
    out = {}
    for cls in [None] + [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        body = tree.body if cls is None else cls.body
        cname = "" if cls is None else cls.name
        for n in body:
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            i = n.lineno - 2
            fields, trusted, saw = set(), False, False
            while i >= 0:
                ln = lines[i]
                if ln.strip() == "":
                    break
                if not ln.lstrip().startswith(("#", "@")):
                    break
                m = ASSIGNS.match(ln)
                if m:
                    saw = True
                    fields.update(SELFF.findall(m.group(1)))
                if TRUSTED.match(ln):
                    trusted = True
                i -= 1
            if saw:
                out[(cname, n.name)] = (fields, trusted, n.lineno)
    return out, _class_declared_fields(tree)


def _class_declared_fields(tree):
    """class name -> set of CLASS-LEVEL declared attribute names, unioned with every
    in-file base's. OVER-approximated on purpose: a wider `declared` set makes HOLE
    MORE likely to fire, which is the fail-closed direction."""
    direct, bases = {}, {}
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        d = set()
        for st in cls.body:
            if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                d.add(st.target.id)
            elif isinstance(st, ast.Assign):
                for t in st.targets:
                    if isinstance(t, ast.Name):
                        d.add(t.id)
        direct[cls.name] = d
        bases[cls.name] = [b.id for b in cls.bases if isinstance(b, ast.Name)]
    out = {}
    for c in direct:
        seen, stack = set(), [c]
        while stack:
            cur = stack.pop()
            if cur in seen or cur not in direct:
                continue
            seen.add(cur)
            stack.extend(bases.get(cur, []))
        out[c] = set().union(*[direct[x] for x in seen]) if seen else set()
    return out


def _live_direct_writes(path):
    """(class, func) -> {field: kind}, kind in {'rebind', 'mutate'}. A REBIND is
    `self.f = ...`; a MUTATE is `self.f[...] = ...` or `self.f.g = ...`."""
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except SyntaxError:
        return {}
    out = {}
    for cls in [None] + [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        body = tree.body if cls is None else cls.body
        cname = "" if cls is None else cls.name
        for fn in body:
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            w = {}
            for n in ast.walk(fn):
                tgts = []
                if isinstance(n, ast.Assign):
                    tgts = n.targets
                elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
                    tgts = [n.target]
                for t in tgts:
                    cur, depth = t, 0
                    while isinstance(cur, (ast.Subscript, ast.Attribute)):
                        if (isinstance(cur, ast.Attribute)
                                and isinstance(cur.value, ast.Name)
                                and cur.value.id == "self"):
                            kind = "rebind" if depth == 0 else "mutate"
                            if w.get(cur.attr) != "rebind":
                                w[cur.attr] = kind
                            break
                        cur, depth = cur.value, depth + 1
            out[(cname, fn.name)] = w
    return out


def measure(inject=None):
    """inject = (relpath, cls, field): pretend `field` is CLASS-DECLARED in `cls`, which is
    what `--self-test` does to prove HOLE can fire."""
    nonempty = 0
    traps, holes = [], []
    for dirpath, _d, files in os.walk(MIRROR):
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            mp = os.path.join(dirpath, f)
            relp = os.path.relpath(mp, MIRROR)
            lp = os.path.join(LIVE, relp)
            if not os.path.exists(lp):
                continue
            decls, cls_fields = _mirror_decls(mp)
            writes = _live_direct_writes(lp)
            for (cname, fname), (fields, trusted, lineno) in sorted(decls.items()):
                if not fields:
                    continue
                nonempty += 1
                w = writes.get((cname, fname))
                if not w:
                    continue
                for fld, kind in sorted(w.items()):
                    if fld in fields:
                        continue
                    declared_in_class = fld in cls_fields.get(cname, set())
                    if inject and (relp, cname, fld) == inject:
                        declared_in_class = True
                    row = (relp, cname, fname, fld, kind, trusted, declared_in_class)
                    traps.append(row)
                    if declared_in_class:
                        holes.append(row)
    return nonempty, traps, holes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="declare one measured-TRAP field in its class and require HOLE to fire")
    args = ap.parse_args()

    nonempty, traps, holes = measure()

    if nonempty < MIN_NONEMPTY:
        print("[!] assigns-underdeclaration: REFUSING — only %d non-empty `#@ assigns` "
              "clause(s) seen, expected at least %d. The mirror walk is broken, so "
              "\"HOLE 0\" means nothing. THIS IS A REFUSAL, NOT A PASS."
              % (nonempty, MIN_NONEMPTY), file=sys.stderr)
        return 2

    if args.self_test:
        target = None
        for (relp, cname, fname), flds in sorted(TRAP_BASELINE.items()):
            target = (relp, cname, flds[0])
            break
        _n, _t, h2 = measure(inject=target)
        if not h2:
            print("[!] assigns-underdeclaration --self-test: FAILED — declaring %s in %s "
                  "(%s) did NOT make HOLE fire, so the HOLE arm is DEAD and \"HOLE 0\" is "
                  "not evidence of anything." % (target[2], target[1], target[0]))
            return 1
        print("[+] assigns-underdeclaration --self-test: OK — declaring %s in %s (%s) "
              "makes HOLE fire on %d row(s); the HOLE arm has teeth."
              % (target[2], target[1], target[0], len(h2)))
        return 0

    if args.verbose or holes:
        for relp, cname, fname, fld, kind, trusted, dic in sorted(traps):
            print("    %-6s %-32s %-28s %-26s self.%-28s %s%s"
                  % ("HOLE" if dic else "trap", relp, cname, fname, fld,
                     kind, "  [trusted]" if trusted else ""))

    methods = len({(r[0], r[1], r[2]) for r in traps})
    if holes:
        print("[!] assigns-underdeclaration: HOLE %d — a live self-field write is omitted "
              "from a NON-EMPTY `#@ assigns` AND the field is declared in the emitting "
              "class, so it is in the record and a caller can rely on the missing write."
              % len(holes))
        return 1
    if len(traps) > MAX_TRAP:
        print("[!] assigns-underdeclaration: TRAP %d > ceiling %d — a NEW under-declared "
              "`#@ assigns` landed. Add the field to the clause, or record the row in "
              "TRAP_BASELINE with its argument." % (len(traps), MAX_TRAP))
        return 1
    print("[+] assigns-underdeclaration: OK — %d non-empty `#@ assigns` clause(s) "
          "(invisible to check-trusted-frame-honesty, which is scoped to `\\nothing`); "
          "TRAP %d field-occurrence(s) across %d method(s), HOLE %d. Every omitted field "
          "is UNDECLARED in its class, hence absent from the emitted record, hence "
          "unmentionable." % (nonempty, len(traps), methods, len(holes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
