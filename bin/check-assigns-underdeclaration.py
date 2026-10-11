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

THE TRANSITIVE ARM (added the same generation, after the direct one measured clean). Direct
writes alone are a LOWER BOUND, and the finding that produced this plane named the residue
explicitly: "a transitively-written field that is class-declared is the ONE way HOLE could
become non-zero without any source change, so it is the next measurement, not a nicety." So
`--transitive` adds a call-graph fixpoint over `self.<m>()` edges within the class and its
in-file bases:

    non-empty clauses 498   TRAP-T 148   HOLE-T 0        (direct: TRAP 18, HOLE 0)

**EIGHT TIMES the population, and still HOLE 0** -- every transitively-written omitted field
is UNDECLARED in its class, hence absent from the record, hence unmentionable.

AND IT IS A STRONGER NEGATIVE THAN THE DIRECT ONE, not a weaker one. The graph resolves by
attribute NAME and can attribute a callee's write to a caller that never reaches it on any
real path, so it OVER-approximates -- which makes HOLE-T MORE likely to fire, never less. A
zero under an over-approximating net is worth more than a zero under a precise one. TRAP-T is
therefore REPORTED and not ratcheted (some of its rows are unreachable by construction);
HOLE-T is the ratchet, and it is the same ratchet as the direct arm's.

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
MAX_TRAP = 3              # field-occurrences. LOWER it when a clause is corrected.
                          # (#49) gen #35, backlog #76: 5 -> 3. `_emit_type_decls`'s clause now
                          # names `_emitted_record_field_types` and `_formal_params` (both written
                          # by the live body). CLAUSE ONLY, measured: declaring them on
                          # PreambleEmissionMixin was EMISSION-INERT (that class-level annotation
                          # does not reach a record — lesson (f5)(i)), so the declaration would
                          # be liability with no honesty. Mirror emission byte-identical.
                          # (#49) gen #33 first measurement: 18 across 9 methods.
                          #
                          # (#49) gen #34 — 18 -> 5, OPTION 3 LANDED FOR THE THIRTEEN FIELDS WHOSE
                          # TYPE IS ESTABLISHED RATHER THAN GUESSED. Each clause repair is paired
                          # with a CLASS DECLARATION wherever the declaration actually reaches the
                          # emitted RECORD, which is what makes the `writes` clause honest instead
                          # of merely making this ratchet fall:
                          #   TypeInferenceMixin      4 fields (types.py, class level)
                          #   StatementEmissionMixin  2 fields (statements.py, class level)
                          #   PyCSLToJSONEmitter      1 field  (Module5 `__init__` -- a class-level
                          #                                    annotation on THAT class is
                          #                                    collected only for a @dataclass and
                          #                                    is otherwise silently inert)
                          # and the six `FunctionEmissionMixin` fields + the two `PyCSLWeaver`
                          # fields get the CLAUSE only: their classes emit no record that carries
                          # them, so a declaration there would be emission-inert AND would create
                          # HOLE/HOLE-T risk for nothing. THE CLAUSE IS WHAT THIS PLANE MEASURES;
                          # THE DECLARATION IS WHAT `check-assigns-writes-survival` NEEDS. They are
                          # NOT the same repair and pairing them blindly is what made gen #33's
                          # half-landed patch raise TRAP 2989 -> 3000.
                          #
                          # AND THE TRANSITIVE ARM HAD TO BE REPAIRED IN THE SAME BREATH: declaring
                          # a field makes every OTHER clause that omits it a HOLE-T, whose ceiling
                          # is 0. Measured before touching a line: 32 TRAP-T rows carry one of the
                          # 13 fields and only 13 are direct, so 19 would have fired. The 19 are
                          # now declared too (`_emit_function`, `_emit_subtyping_goals`,
                          # `_render_refinement_goal`, `visit_ClassDef`), taking TRAP-T 148 -> 116.
                          #
                          # THE FIVE THAT REMAIN EACH NEED A JUDGEMENT, NOT A TYPE (see the plan):
                          #   expressions.py `ir`                      a CONTAINER mutation of the
                          #                                           whole IR mapping
                          #   expressions.py `_r188_stub_names`        initialised from another map
                          #   expressions.py `_r55_subsumed_name`      an Optional (route #227)
                          #   preamble.py    `_formal_params`          `= list(params)`
                          #   preamble.py    `_emitted_record_field_types`
                          #                                           `Dict[str, Dict[str, str]]` --
                          #                                           the plan said `Dict[str, str]`
                          #                                           and the live shape is NESTED;
                          #                                           a guessed container type is a
                          #                                           fabricated witness value.
                          # Plan: getting-better/open-routes/option3-declare-the-written-fields-PLAN.md
TRAP_BASELINE = {
    ("module6_whyml/expressions.py", "ExpressionEmissionMixin", "_handle_dotted_call"): [
        "_r188_stub_names", "ir"],
    ("module6_whyml/expressions.py", "ExpressionEmissionMixin", "_handle_binop"): [
        "_r55_subsumed_name"],
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


def _transitive_writes(live_path):
    """(cls, fn) -> set of self fields written DIRECTLY or through a `self.<m>()` callee
    resolved within the class and its in-file bases. Over-approximating on purpose."""
    try:
        tree = ast.parse(open(live_path, encoding="utf-8", errors="replace").read())
    except SyntaxError:
        return {}
    facts = {}
    for cls in [None] + [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        body = tree.body if cls is None else cls.body
        cname = "" if cls is None else cls.name
        for fn in body:
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            w, calls = set(), set()
            for n in ast.walk(fn):
                tgts = []
                if isinstance(n, ast.Assign):
                    tgts = n.targets
                elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
                    tgts = [n.target]
                for t in tgts:
                    cur = t
                    while isinstance(cur, (ast.Subscript, ast.Attribute)):
                        if (isinstance(cur, ast.Attribute)
                                and isinstance(cur.value, ast.Name)
                                and cur.value.id == "self"):
                            w.add(cur.attr)
                            break
                        cur = cur.value
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and isinstance(n.func.value, ast.Name)
                        and n.func.value.id == "self"):
                    calls.add(n.func.attr)
            facts[(cname, fn.name)] = (w, calls)
    out = {}
    for (cname, fname), (w, _c) in facts.items():
        seen, stack, acc = set(), [fname], set(w)
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            cw, cc = facts.get((cname, cur), (set(), set()))
            acc |= cw
            for nxt in cc:
                if (cname, nxt) in facts:
                    stack.append(nxt)
        out[(cname, fname)] = acc
    return out


def measure(inject=None):
    """inject = (relpath, cls, func, field): pretend `field` is BOTH absent from that
    method's `#@ assigns` clause AND class-DECLARED, which is what `--self-test` does to
    prove HOLE can fire.

    (#49) gen #33 — THE INJECTION NEEDED BOTH HALVES ONCE TRAP REACHED 0. It used to force
    only `declared_in_class = True` for a field that was ALREADY a measured TRAP. That
    worked while 18 clauses were under-declared; the moment they were all repaired there
    was no TRAP left to promote, so the self-test would have passed by testing NOTHING —
    the exact shape of a guard whose population is empty. It now SUBTRACTS the field from
    the clause as well, so it synthesises the whole condition instead of half of it.""" 
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
                _fields = fields
                if inject and (relp, cname, fname) == inject[:3]:
                    _fields = fields - {inject[3]}       # pretend the clause omits it
                for fld, kind in sorted(w.items()):
                    if fld in _fields:
                        continue
                    declared_in_class = fld in cls_fields.get(cname, set())
                    if inject and (relp, cname, fname, fld) == inject:
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
    ap.add_argument("--transitive", action="store_true",
                    help="also report the call-graph arm (TRAP-T / HOLE-T); HOLE-T is the "
                         "same ratchet and must stay 0")
    args = ap.parse_args()

    nonempty, traps, holes = measure()

    if nonempty < MIN_NONEMPTY:
        print("[!] assigns-underdeclaration: REFUSING — only %d non-empty `#@ assigns` "
              "clause(s) seen, expected at least %d. The mirror walk is broken, so "
              "\"HOLE 0\" means nothing. THIS IS A REFUSAL, NOT A PASS."
              % (nonempty, MIN_NONEMPTY), file=sys.stderr)
        return 2

    if args.self_test:
        # Pick a method whose LIVE body writes a field its clause DOES name, then pretend
        # the clause omits it and the class declares it. Both halves are required now that
        # every real clause is honest (TRAP 0) — see `measure`'s docstring.
        target = None
        for dirpath, _d, files in os.walk(MIRROR):
            for f in sorted(files):
                if target or not f.endswith(".py"):
                    continue
                mp = os.path.join(dirpath, f)
                relp = os.path.relpath(mp, MIRROR)
                lp = os.path.join(LIVE, relp)
                if not os.path.exists(lp):
                    continue
                decls, _cf = _mirror_decls(mp)
                writes = _live_direct_writes(lp)
                for (cname, fname), (fields, _t, _l) in sorted(decls.items()):
                    if target or not fields:
                        continue
                    w = writes.get((cname, fname)) or {}
                    both = sorted(set(w) & set(fields))
                    if both:
                        target = (relp, cname, fname, both[0])
        if target is None:
            print("[!] assigns-underdeclaration --self-test: REFUSING \u2014 found no method whose "
                  "live body writes a field its own clause names, so the injection cannot be "
                  "built and a PASS would mean nothing.")
            return 2
        _n, _t2, h2 = measure(inject=target)
        if not h2:
            print("[!] assigns-underdeclaration --self-test: FAILED \u2014 pretending %s is absent "
                  "from %s.%s's clause AND declared in %s did NOT make HOLE fire, so the HOLE "
                  "arm is DEAD and \"HOLE 0\" is not evidence of anything."
                  % (target[3], target[1], target[2], target[1]))
            return 1
        print("[+] assigns-underdeclaration --self-test: OK \u2014 pretending %s is absent from "
              "%s.%s's clause AND class-declared makes HOLE fire on %d row(s); the HOLE arm "
              "has teeth." % (target[3], target[1], target[2], len(h2)))
        return 0

    if args.transitive:
        t_traps, t_holes, t_nonempty = [], [], 0
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
                tw = _transitive_writes(lp)
                for (cname, fname), (fields, trusted, _ln) in sorted(decls.items()):
                    if not fields:
                        continue
                    t_nonempty += 1
                    for fld in sorted(tw.get((cname, fname), set()) - fields):
                        row = (relp, cname, fname, fld, trusted)
                        t_traps.append(row)
                        if fld in cls_fields.get(cname, set()):
                            t_holes.append(row)
        if t_holes:
            print("[!] assigns-underdeclaration --transitive: HOLE-T %d \u2014 a field written "
                  "THROUGH A CALLEE is omitted from a non-empty `#@ assigns` AND is declared "
                  "in the emitting class, so it is in the record and mentionable."
                  % len(t_holes))
            for r in sorted(t_holes)[:20]:
                print("    %-32s %-26s %-26s self.%s" % (r[0], r[1], r[2], r[3]))
            return 1
        print("[*] assigns-underdeclaration --transitive: %d non-empty clause(s), TRAP-T %d, "
              "HOLE-T 0 \u2014 8x the direct population and still every omitted field is "
              "UNDECLARED in its class. The graph OVER-approximates (it resolves by attribute "
              "name), which makes HOLE-T MORE likely to fire, so a zero here is a STRONGER "
              "negative than the direct arm's." % (t_nonempty, len(t_traps)))

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
