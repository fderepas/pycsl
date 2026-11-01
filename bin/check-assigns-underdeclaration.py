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

THE DISPATCH ARM (HOLE-V) AND `__init__` DECLARATIONS (plane-gap-visitor-dispatch). Every
arm above resolved callees by NAME within one class and read CLASS-LEVEL declarations only,
so NodeVisitor dispatch (`self.generic_visit(node)` -> `visit_*`), handler tables
(`getattr(self, self._T[...])`), mixin-to-mixin calls and every `__init__`-built record were
invisible; a verified probe PROVED a field unchanged across `visit_Module` that CPython
changes. The arm (see `dispatch_rows`) over-approximates all four, and `declared` now
includes `__init__` targets for every arm. Measured at 3964201f: HOLE / HOLE-T unchanged (0),
HOLE-D 0 + HOLE-DI 4 (own ratchet), HOLE-V 33 (own baseline, 30 on `\trusted` frames); one
row (`StatementEmissionMixin._handle_return_stmt` omitting `_abstract_ops`) reproduces a
FALSE PROOF. Census: getting-better/plane-gap-visitor-dispatch.md. `--self-test-dispatch`
is its negative test.

EXIT CODES
  0  TRAP <= MAX_TRAP, HOLE == 0, HOLE-D == 0, HOLE-DI and HOLE-V within their baselines
  1  HOLE > 0, TRAP above its ceiling, HOLE-T/HOLE-D > 0, or a HOLE-DI/HOLE-V row outside
     its baseline
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
TRUSTED = re.compile(r"^\s*#@\s*(?:\\trusted|declared_in)\b")   # B4: declared_in = same val
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


def _class_declared_fields(tree, include_init=True):
    """class name -> set of declared attribute names, unioned with every in-file base's.
    OVER-approximated on purpose: a wider `declared` set makes HOLE MORE likely to fire,
    which is the fail-closed direction.

    (#49) plane-gap-visitor-dispatch: `include_init` (the default) adds every `self.<f>`
    (Ann)Assign target of the class's `__init__`. It used to read CLASS-LEVEL names only,
    but Module 5 builds a NON-dataclass record from `__init__` (live `_collect_class_fields`;
    lesson (g5)(i)), so e.g. PyCSLToJSONEmitter's whole record (`_final_registry`,
    `program_ir`, `_fresh_var_counter`, `_m5_dc_unknown`) was invisible to every HOLE arm.
    Measured: the direct and transitive arms are UNCHANGED by it (0 -> 0); the declared-callee
    arm gains 4 rows, ratcheted separately as HOLE-DI (see MAX_HOLE_DI)."""
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
            elif (include_init and isinstance(st, ast.FunctionDef)
                    and st.name == "__init__"):
                for n in ast.walk(st):
                    tg = n.targets if isinstance(n, ast.Assign) else (
                        [n.target] if isinstance(n, ast.AnnAssign) else [])
                    for t in tg:
                        if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                                and t.value.id == "self"):
                            d.add(t.attr)
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


# (#49) gen #35 — THE DECLARED-CALLEE ARM (HOLE-D). Both arms above read the LIVE body; the
# transitive one follows `self.<m>()` only within the class and its in-file bases. Neither
# consults what Module 6 actually uses for a call's effect: the CALLEE's DECLARED
# `#@ assigns`. Measured the day it was built: declaring `_abstract_ops`/`_dict_locals` on
# ExpressionEmissionMixin made `why3 --type-only` reject 23 CONVERTED methods ("unlisted write
# effect") whose clauses omitted fields their callee `_expr_to_whyml` declares writing, and one
# more (`_materialize_if_seq`, `\nothing`, reaching `_materialize_bridge` receiver-less) PROVED a
# false preservation postcondition. HOLE-D = 54 on that tree, 0 after the repair; HOLE and
# HOLE-T were 0 throughout. So: for every mirror def carrying an `#@ assigns` (including
# `\nothing`), every `self.<m>()` in its MIRROR body is resolved to the callee's declared frame
# (same file + class first, else a unique frame across the mirror; ambiguous frames are skipped
# and counted), and each callee field the caller's clause omits is HOLE-D when the caller's class
# declares it (mentionable) and TRAP-D otherwise. HOLE-D is a ceiling of 0.
MAX_HOLE_D = 0
# (#49) plane-gap-visitor-dispatch — HOLE-DI: the same arm once `__init__`-declared fields
# count as declared (Module 5 builds a non-dataclass record from `__init__`). It is a NEW
# population behind its OWN ratchet; MAX_HOLE_D stays 0. Measured at 3964201f: 4 rows, all on
# VERIFIED callers, all `_fresh_var_counter`. Module 6 WIDENS a converted method's emitted
# `writes` by its callees' declared frames (emitted: `_py_stmt_with ... writes {
# self._fresh_var_counter, ir_stmts }`), so the EMITTED frame is honest and these are
# source-clause AUDIT debt, not a false proof. Remove a row when its clause is repaired.
HOLE_DI_BASELINE = frozenset({
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "_py_stmt_match",
     "_py_stmts_to_ir", "_fresh_var_counter"),
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "_py_stmt_try",
     "_py_stmts_to_ir", "_fresh_var_counter"),
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "_py_stmt_with",
     "_get_mutex_invariant_ir", "_fresh_var_counter"),
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "_py_stmt_with",
     "_py_stmts_to_ir", "_fresh_var_counter"),
})
MAX_HOLE_DI = len(HOLE_DI_BASELINE)


def declared_callee_rows(omit=None):
    """-> (hole_d_rows, trap_d_count, ambiguous). `omit=(relp, cls, fn, field)` pretends that
    def's clause lacks `field` (the self-test)."""
    decl_all, cls_fields_all, calls = {}, {}, {}
    by_name = {}
    for dirpath, _d, files in os.walk(MIRROR):
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            mp = os.path.join(dirpath, f)
            relp = os.path.relpath(mp, MIRROR)
            decls, cf = _mirror_decls(mp)
            for (c, fn), v in decls.items():
                decl_all[(relp, c, fn)] = v
                by_name.setdefault(fn, []).append((relp, c, fn))
            for c, flds in cf.items():
                cls_fields_all[(relp, c)] = flds
            try:
                tree = ast.parse(open(mp, encoding="utf-8", errors="replace").read())
            except SyntaxError:
                continue
            for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
                for fn in cls.body:
                    if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        cs = set()
                        for n in ast.walk(fn):
                            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                                    and isinstance(n.func.value, ast.Name)
                                    and n.func.value.id == "self"):
                                cs.add(n.func.attr)
                        calls[(relp, cls.name, fn.name)] = cs
    init_only = {}
    for (relp, c), flds in cls_fields_all.items():
        mp = os.path.join(MIRROR, relp)
        init_only[(relp, c)] = _mirror_init_declared(mp)[1].get(c, set())
    holes, trap, amb = [], 0, 0
    for key, (fields, trusted, _ln) in sorted(decl_all.items()):
        relp, c, fn = key
        if omit is not None and key == omit[:3]:
            fields = fields - {omit[3]}
        for callee in sorted(calls.get(key, ())):
            cands = [k for k in by_name.get(callee, []) if k[0] == relp and k[1] == c] \
                or by_name.get(callee, [])
            if not cands:
                continue
            frames = {tuple(sorted(decl_all[k][0])) for k in cands}
            if len(frames) > 1:
                amb += 1
                continue
            for fld in sorted(set(decl_all[cands[0]][0]) - fields):
                if fld in cls_fields_all.get((relp, c), set()):
                    holes.append((relp, c, fn, callee, fld, trusted,
                                  fld in init_only.get((relp, c), set())))
                else:
                    trap += 1
    return holes, trap, amb


# (#49) plane-gap-visitor-dispatch — THE DISPATCH ARM (HOLE-V). Every arm above resolves a
# callee by the NAME of a `self.<m>()` call inside ONE class. Measured by the driver, that is
# blind to the way an `ast.NodeVisitor` reaches its handlers: `self.generic_visit(node)` /
# `self.visit(x)` / `super().visit(x)` / `_Unparser.traverse` / `getattr(self, 'visit_' + ..)`
# are not named calls of the handler, so `PyCSLToJSONEmitter.visit_Module`'s `\trusted` frame
# omitted `_cur_func_name` (written by visit_FunctionDef -> _build_function_ir) and a VERIFIED
# probe caller PROVED it unchanged while CPython changes it. And `declared` read CLASS-LEVEL
# annotations only, while Module 5 builds a non-dataclass record from `__init__`'s
# `self.<f> [: T] = ...` targets (lesson (g5)(i)), so those classes were half-invisible.
#
# This arm OVER-approximates on every axis (sound: a row can be spurious, never missing):
#   receiver family   `self` in a method of C is an instance of some D <= C, so `self.m` may
#                     resolve to ANY `m` defined in up*(D) for ANY D in down*(C); classes are
#                     matched by NAME (Name id or Attribute tail) across the whole live tree,
#                     so `ast.NodeVisitor` resolves to pure_ast's NodeVisitor;
#   dispatch          `self.visit` / `self.generic_visit` / `super().visit|generic_visit` /
#                     `X.visit|generic_visit(self, ..)` expand to every family method whose
#                     name starts with `visit` plus `generic_visit`; `getattr(self, e)` with
#                     `e` a constant -> that method, a constant-prefixed concat/f-string (also
#                     through one local) -> every family method with that prefix, a local read
#                     from a class-level str-valued dict table (`self.T.get(..)` / `self.T[..]`)
#                     -> the table's values, anything else -> EVERY family method;
#   references        any `self.<m>` load naming a family method is an edge (callbacks,
#                     `getattr(self, m, self.generic_visit)` defaults);
#   container writes  `self.f.append/extend/insert/pop/remove/clear/add/discard/update/
#                     setdefault/popitem(..)` count as writes of `f` (the old arms only see
#                     assignment targets);
#   population        EVERY mirror def carrying `#@ assigns`, `\nothing` included;
#   declared          class-level (Ann)Assign names UNION every `self.<f>` (Ann)Assign target
#                     in `__init__`, over the class and its in-file bases.
# Row verdicts mirror the transitive arm: TRAP-V (omitted, any) and HOLE-V (omitted AND
# declared, i.e. in the record and mentionable). HOLE-V is ratcheted at its MEASURED count:
# it is real debt (census: getting-better/plane-gap-visitor-dispatch.md), NOT a re-baseline of
# HOLE-T, which stays 0. Lower MAX_HOLE_V when a frame is repaired; never raise it.
# HOLE_V_BASELINE: (relp, class, method, field) -> "trusted" | "verified", measured at HEAD
# 3964201f (census in getting-better/plane-gap-visitor-dispatch.md). A row OUTSIDE it is red;
# a baseline row that stops firing is printed so it can be removed (the ratchet only shrinks).
# "verified" rows are AUDIT debt (Module 6 widens a converted method's emitted `writes` with
# its callees' declared frames, so the emitted frame is honest); "trusted" rows are SOUNDNESS
# debt (a `\trusted` frame is the caller-side assumption verbatim -- lesson (g5)(ii)).
HOLE_V_BASELINE = {
    ("Module6_WhyMLTranspiler.py", "Module6_WhyMLTranspiler",
     "_emit_prefunctions_infra", "ir"): "trusted",
    ("Module6_WhyMLTranspiler.py", "Module6_WhyMLTranspiler",
     "_render_callee_condition", "ir"): "trusted",
    ("Module6_WhyMLTranspiler.py", "Module6_WhyMLTranspiler",
     "_transpile_modular", "ir"): "trusted",
    ("Module6_WhyMLTranspiler.py", "Module6_WhyMLTranspiler",
     "_wrap_call_with_callee_raises_assert", "ir"): "trusted",
    ("Module6_WhyMLTranspiler.py", "Module6_WhyMLTranspiler",
     "transpile", "ir"): "trusted",
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter",
     "_py_stmt_match", "_fresh_var_counter"): "verified",
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter",
     "_py_stmt_try", "_fresh_var_counter"): "verified",
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter",
     "_py_stmt_with", "_fresh_var_counter"): "verified",
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter",
     "visit_FunctionDef", "_m5_dc_unknown"): "trusted",
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter",
     "visit_Module", "_m5_dc_unknown"): "trusted",
    ("module6_whyml/statements.py", "StatementEmissionMixin",
     "_handle_return_stmt", "_abstract_ops"): "trusted",
    ("module6_whyml/statements.py", "StatementEmissionMixin",
     "_handle_return_stmt", "_dict_locals"): "trusted",
    ("module6_whyml/statements.py", "StatementEmissionMixin",
     "_handle_return_stmt", "_get_return_raw_option"): "trusted",
    ("module6_whyml/statements.py", "StatementEmissionMixin",
     "_handle_return_stmt", "_quant_record_binders"): "trusted",
    ("module6_whyml/statements.py", "StatementEmissionMixin",
     "_handle_return_stmt", "_quant_scalar_binders"): "trusted",
    ("module6_whyml/statements.py", "StatementEmissionMixin",
     "_track_collection_metadata", "_known_collection_elements"): "trusted",
    ("module6_whyml/statements.py", "StatementEmissionMixin",
     "_track_collection_metadata", "_known_collection_sizes"): "trusted",
    ("module6_whyml/statements.py", "StatementEmissionMixin",
     "_track_collection_metadata", "_record_array_locals"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_expr_to_whyml", "_dict_locals"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_expr_to_whyml", "_quant_record_binders"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_expr_to_whyml", "_quant_scalar_binders"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_comp_content_counter"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_current_params"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_current_self_type"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_dict_locals"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_frame_trigger_active"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_func_return_type"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_in_spec"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_needs_array_init"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_quant_record_binders"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_quant_scalar_binders"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_string_local_vars"): "trusted",
    ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin",
     "_match_pattern_cond", "_todict_arg_wants_pymap"): "trusted",
}
_MUTATORS = {"append", "extend", "insert", "pop", "remove", "clear", "add", "discard",
             "update", "setdefault", "popitem"}
_DISPATCH_NAMES = {"visit", "generic_visit"}
# the library dispatchers (pure_ast's NodeVisitor/NodeTransformer, which `ast.NodeVisitor`
# resolves to by name): their `visit`/`generic_visit` are MODELLED by the edge kinds below.
_LIB_VISITORS = {"NodeVisitor", "NodeTransformer"}
# `mod` nodes: the ROOT of a tree, never a child, so `generic_visit` cannot reach them
_CONST_ALIASES = ("visit_Num", "visit_Str", "visit_Bytes", "visit_NameConstant",
                  "visit_Ellipsis")
_MOD_ROOT_VISITORS = {"visit_Module", "visit_Interactive", "visit_Expression",
                      "visit_FunctionType"}


def _is_self(n):
    return isinstance(n, ast.Name) and n.id == "self"


def _is_super_call(n):
    return (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "super")


def _const_prefix(e, local_prefix):
    """-> str prefix (possibly '') when `e` is a constant-prefixed string expression, else
    None. '' means 'no usable prefix' only when e is non-constant (caller decides)."""
    if isinstance(e, ast.Constant) and isinstance(e.value, str):
        return e.value
    if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Add):
        p = _const_prefix(e.left, local_prefix)
        return p
    if isinstance(e, ast.JoinedStr) and e.values and isinstance(e.values[0], ast.Constant):
        return str(e.values[0].value)
    if isinstance(e, ast.Name) and e.id in local_prefix:
        return local_prefix[e.id]
    return None


def _method_facts(fn, class_tables):
    """-> (writes{field: tag}, edges[(kind, payload)]) for one live def. kinds: 'name' m,
    'ref' m, 'prefix' p, 'table' T, 'any' None, 'visitor' None."""
    writes, edges = {}, []
    local_prefix, local_table, local_consts = {}, {}, {}
    # a getattr(self, e) result is a DISPATCH only when it is CALLED: directly, or through a
    # local that is later called, passed as an argument, or returned. Otherwise it is a FIELD
    # READ (`getattr(self, _tset, None)` over a tuple of field names) and is no edge.
    called_names, called_ids = set(), set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                called_names.add(n.func.id)
            called_ids.add(id(n.func))
            for a in list(n.args) + [k.value for k in n.keywords]:
                if isinstance(a, ast.Name):
                    called_names.add(a.id)
        elif isinstance(n, ast.Return) and isinstance(n.value, ast.Name):
            called_names.add(n.value.id)
        elif isinstance(n, ast.For) and isinstance(n.iter, (ast.Tuple, ast.List, ast.Set)):
            # for x in ("a", "b") / for x, y in (("a", 1), ...): x ranges over constants
            tg = n.target
            names = [tg] if isinstance(tg, ast.Name) else (
                list(tg.elts) if isinstance(tg, ast.Tuple) else [])
            for pos, tn in enumerate(names):
                if not isinstance(tn, ast.Name):
                    continue
                vals = set()
                for el in n.iter.elts:
                    v = el if isinstance(tg, ast.Name) else (
                        el.elts[pos] if isinstance(el, ast.Tuple) and len(el.elts) > pos
                        else None)
                    if isinstance(v, ast.Constant) and isinstance(v.value, str):
                        vals.add(v.value)
                    else:
                        vals = None
                        break
                if vals:
                    local_consts[tn.id] = vals
    getattr_called = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Call) \
                and n.targets[0].id in called_names:
            getattr_called.add(id(n.value))
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name):
            v, nm = n.value, n.targets[0].id
            p = _const_prefix(v, {}) if not (isinstance(v, ast.Constant)) else None
            if p:
                local_prefix[nm] = p
            # x = self.T.get(..) / self.T[..] / T.get(..)
            base = None
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) \
                    and v.func.attr == "get":
                base = v.func.value
            elif isinstance(v, ast.Subscript):
                base = v.value
            if isinstance(base, ast.Attribute) and _is_self(base.value):
                local_table[nm] = base.attr
            elif isinstance(base, ast.Name):
                local_table[nm] = base.id
    for n in ast.walk(fn):
        tgts = []
        if isinstance(n, ast.Assign):
            tgts = n.targets
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
            tgts = [n.target]
        for t in tgts:
            for cur in ([t] if not isinstance(t, (ast.Tuple, ast.List))
                        else list(ast.walk(t))):
                while isinstance(cur, (ast.Subscript, ast.Attribute, ast.Starred)):
                    if isinstance(cur, ast.Attribute) and _is_self(cur.value):
                        writes.setdefault(cur.attr, "assign")
                        break
                    cur = cur.value
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute):
                # self.f.append(..) and friends: a container write of f
                if (f.attr in _MUTATORS and isinstance(f.value, ast.Attribute)
                        and _is_self(f.value.value)):
                    writes.setdefault(f.value.attr, "mutcall")
                if f.attr in _DISPATCH_NAMES and (
                        _is_self(f.value) or _is_super_call(f.value)
                        or (n.args and _is_self(n.args[0]))):
                    # generic_visit(node) -- and `self.visit(child)` INSIDE a generic_visit --
                    # only ever reaches CHILD nodes, and a `mod` node is never a child
                    edges.append(("visitor", "generic" if (
                        f.attr == "generic_visit" or fn.name == "generic_visit")
                        else "visit"))
                    edges.append(("name", f.attr))     # a project-local override, if any
                elif _is_super_call(f.value) or _is_self(f.value):
                    edges.append(("name", f.attr))
            if (isinstance(f, ast.Name) and f.id == "getattr" and len(n.args) >= 2
                    and _is_self(n.args[0])
                    and (id(n) in called_ids or id(n) in getattr_called)):
                a = n.args[1]
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    edges.append(("name", a.value))
                elif isinstance(a, ast.Name) and a.id in local_consts:
                    edges.extend(("name", v) for v in sorted(local_consts[a.id]))
                else:
                    p = _const_prefix(a, local_prefix)
                    if p:
                        edges.append(("prefix", p))
                    elif isinstance(a, ast.Name) and a.id in local_table:
                        # resolved against the FAMILY's tables at closure time; an unknown
                        # table falls back to EVERY family method
                        edges.append(("table", local_table[a.id]))
                    else:
                        edges.append(("any", None))
        if isinstance(n, ast.Attribute) and _is_self(n.value) \
                and isinstance(n.ctx, ast.Load):
            edges.append(("ref", n.attr))
    return writes, edges


def _base_names(cls):
    out = []
    for b in cls.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        elif isinstance(b, ast.Attribute):
            out.append(b.attr)
    return out


def _live_index():
    """class name -> {'bases': set, 'methods': {fname: [(writes, edges)]}, 'tables': {T:
    set(str)}} over the WHOLE live tree, same-named classes UNIONED (over-approximation)."""
    idx = {}
    for dirpath, _d, files in os.walk(LIVE):
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            try:
                tree = ast.parse(open(os.path.join(dirpath, f), encoding="utf-8",
                                      errors="replace").read())
            except SyntaxError:
                continue
            for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
                e = idx.setdefault(cls.name, {"bases": set(), "methods": {}, "tables": {}})
                e["bases"].update(_base_names(cls))
                for st in cls.body:
                    tg = None
                    if isinstance(st, ast.Assign) and len(st.targets) == 1 \
                            and isinstance(st.targets[0], ast.Name):
                        tg, val = st.targets[0].id, st.value
                    elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                        tg, val = st.target.id, st.value
                    if tg and isinstance(val, ast.Dict):
                        vs = {v.value for v in val.values
                              if isinstance(v, ast.Constant) and isinstance(v.value, str)}
                        if vs:
                            e["tables"].setdefault(tg, set()).update(vs)
                for fn in cls.body:
                    if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        e["methods"].setdefault(fn.name, []).append(fn)
    for e in idx.values():
        e["methods"] = {m: [_method_facts(fn, e["tables"]) for fn in fns]
                        for m, fns in e["methods"].items()}
    return idx


def _family(idx, cname):
    up = {}

    def ups(c):
        if c in up:
            return up[c]
        seen, st = set(), [c]
        while st:
            x = st.pop()
            if x in seen:
                continue
            seen.add(x)
            st.extend(idx.get(x, {}).get("bases", ()))
        up[c] = seen
        return seen
    down, st = set(), [cname]
    while st:
        x = st.pop()
        if x in down:
            continue
        down.add(x)
        st.extend(c for c, e in idx.items() if x in e["bases"])
    fam = set()
    for d in down:
        fam |= ups(d)
    return {c for c in fam if c in idx}


def _dispatch_closure(idx, cname, fname, use=frozenset({"dispatch", "ref", "mutcall",
                                                         "family"})):
    """-> {field: tag} written by `cname.fname` or anything it may reach. `use` toggles the
    four over-approximations (for the census's cause attribution)."""
    fam = _family(idx, cname) if "family" in use else ({cname} & set(idx))
    meths = {}
    for c in fam:
        for m, facts in idx[c]["methods"].items():
            if c in _LIB_VISITORS and m in _DISPATCH_NAMES:
                continue        # modelled by the "visitor" edge kinds, not by its body
            if c in _LIB_VISITORS and m == "visit_Constant":
                # its `getattr(self, 'visit_' + type_name)` ranges over the deprecated
                # constant aliases only, then falls back to generic_visit
                facts = [({}, [("name", a) for a in _CONST_ALIASES]
                          + [("visitor", "generic"), ("name", "generic_visit")])]
            meths.setdefault(m, []).extend(facts)
    tables = {}
    for c in fam:
        for t, vs in idx[c]["tables"].items():
            tables.setdefault(t, set()).update(vs)
    acc, seen, stack = {}, set(), [fname]
    while stack:
        m = stack.pop()
        if m in seen:
            continue
        seen.add(m)
        for writes, edges in meths.get(m, ()):
            for fld, tag in writes.items():
                if tag == "mutcall" and "mutcall" not in use:
                    continue
                acc.setdefault(fld, tag)
            for kind, p in edges:
                if kind == "name":
                    stack.append(p)
                elif kind == "ref":
                    if "ref" in use and p in meths:
                        stack.append(p)
                elif "dispatch" not in use:
                    continue
                elif kind == "visitor":
                    stack.extend(x for x in meths
                                 if (x.startswith("visit_") and not (
                                     p == "generic" and x in _MOD_ROOT_VISITORS))
                                 or x in _DISPATCH_NAMES)
                elif kind == "prefix":
                    stack.extend(x for x in meths if x.startswith(p))
                elif kind == "table":
                    stack.extend(tables[p] if p in tables else meths)
                elif kind == "any":
                    stack.extend(meths)
    return acc


_INIT_CACHE = {}


def _mirror_init_declared(path):
    if path not in _INIT_CACHE:
        _INIT_CACHE[path] = _mirror_init_declared_uncached(path)
    return _INIT_CACHE[path]


def _mirror_init_declared_uncached(path):
    """-> (class-level declared, __init__-ONLY declared) per class, over in-file bases."""
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except SyntaxError:
        return {}, {}
    base = _class_declared_fields(tree, include_init=False)
    full = _class_declared_fields(tree, include_init=True)
    return base, {c: full[c] - base.get(c, set()) for c in full}


ALL_USE = frozenset({"dispatch", "ref", "mutcall", "family"})


def dispatch_rows(idx=None, perturb=None):
    """-> (rows, old_keys). rows: dicts with relp, cls, fn, fld, trusted, nothing, hole,
    init_decl, causes. `perturb=(relp, cls, fn, fld)` deletes `fld` from that def's clause
    (the negative test). old_keys = the (relp, cls, fn, fld) rows the OLD --transitive arm
    already reports, so the census lists only NEW rows."""
    idx = idx or _live_index()
    rows, old_keys = [], set()
    for dirpath, _d, files in os.walk(MIRROR):
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            mp = os.path.join(dirpath, f)
            relp = os.path.relpath(mp, MIRROR)
            lp = os.path.join(LIVE, relp)
            if not os.path.exists(lp):
                continue
            decls, _cf = _mirror_decls(mp)
            base_decl, init_only = _mirror_init_declared(mp)
            tw = _transitive_writes(lp)
            for (cname, fname), (fields, trusted, _ln) in sorted(decls.items()):
                if fields:
                    for fld in tw.get((cname, fname), set()) - fields:
                        old_keys.add((relp, cname, fname, fld))
                if cname not in idx or fname == "__init__":
                    # a constructor's `self` is FRESH: its writes are the record's
                    # initialisation, not a frame a caller relies on
                    continue
                _fields = fields
                if perturb and (relp, cname, fname) == perturb[:3]:
                    _fields = fields - {perturb[3]}
                full = _dispatch_closure(idx, cname, fname, ALL_USE)
                omitted = sorted(set(full) - _fields)
                if not omitted:
                    continue
                abl = {u: _dispatch_closure(idx, cname, fname, ALL_USE - {u})
                       for u in ("dispatch", "ref", "mutcall", "family")}
                for fld in omitted:
                    causes = sorted(u for u, w in abl.items() if fld not in w)
                    in_base = fld in base_decl.get(cname, set())
                    in_init = fld in init_only.get(cname, set())
                    rows.append({"relp": relp, "cls": cname, "fn": fname, "fld": fld,
                                 "trusted": trusted, "nothing": not fields,
                                 "hole": in_base or in_init, "init_decl": in_init,
                                 "causes": causes or ["combined"]})
    return rows, old_keys


def dispatch_report(verbose=False, rows=None):
    rows = dispatch_rows()[0] if rows is None else rows
    holes = {(r["relp"], r["cls"], r["fn"], r["fld"]): r for r in rows if r["hole"]}
    n_tr = sum(1 for r in holes.values() if r["trusted"])
    print("[*] assigns-underdeclaration DISPATCH arm: TRAP-V %d, HOLE-V %d (%d on `\\trusted` "
          "frames, %d on verified; baseline %d/%d) \u2014 visitor/getattr/table dispatch, "
          "receiver-family resolution, container-mutator writes, `\\nothing` clauses, "
          "`__init__`-declared fields."
          % (len(rows), len(holes), n_tr, len(holes) - n_tr,
             sum(1 for v in HOLE_V_BASELINE.values() if v == "trusted"),
             sum(1 for v in HOLE_V_BASELINE.values() if v == "verified")))
    if verbose:
        for k, r in sorted(holes.items()):
            print("    %-36s %-24s %-30s self.%-26s %s %s" % (
                k[0], k[1], k[2], k[3], "trusted " if r["trusted"] else "verified",
                "+".join(r["causes"])))
    new = sorted(k for k in holes if k not in HOLE_V_BASELINE)
    gone = sorted(k for k in HOLE_V_BASELINE if k not in holes)
    if gone:
        print("[*] assigns-underdeclaration: %d HOLE-V baseline row(s) no longer fire \u2014 "
              "REMOVE them from HOLE_V_BASELINE (the ratchet only shrinks):" % len(gone))
        for k in gone:
            print("    %-36s %-24s %-30s self.%s" % k)
    if new:
        print("[!] assigns-underdeclaration: HOLE-V %d NEW row(s) \u2014 a field written through "
              "dispatch / a family method / a container mutator is omitted from an `#@ assigns` "
              "AND is in the emitting class's record (mentionable):" % len(new))
        for k in new[:40]:
            r = holes[k]
            print("    %-36s %-24s %-30s self.%-26s %s %s" % (
                k[0], k[1], k[2], k[3], "trusted " if r["trusted"] else "verified",
                "+".join(r["causes"])))
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="declare one measured-TRAP field in its class and require HOLE to fire")
    ap.add_argument("--self-test-declared", action="store_true",
                    help="pretend one caller omits a field its callee declares, require HOLE-D")
    ap.add_argument("--self-test-dispatch", action="store_true",
                    help="drop a dispatch-only record field from one clause, require HOLE-V")
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

    if args.self_test_dispatch:
        # Find a clause that NAMES a record field which the live method reaches ONLY through
        # dispatch (absent once dispatch is ablated), drop it from the clause, and require
        # HOLE-V to fire on a row outside the baseline.
        idx = _live_index()
        target = None
        for dirpath, _d, files in os.walk(MIRROR):
            for f in sorted(files):
                if target or not f.endswith(".py"):
                    continue
                mp = os.path.join(dirpath, f)
                relp = os.path.relpath(mp, MIRROR)
                if not os.path.exists(os.path.join(LIVE, relp)):
                    continue
                decls, _cf = _mirror_decls(mp)
                base_decl, init_only = _mirror_init_declared(mp)
                for (c, fn), (fields, _t, _l) in sorted(decls.items()):
                    if target or not fields or c not in idx or fn == "__init__":
                        continue
                    declared = base_decl.get(c, set()) | init_only.get(c, set())
                    full = _dispatch_closure(idx, c, fn, ALL_USE)
                    nod = _dispatch_closure(idx, c, fn, ALL_USE - {"dispatch"})
                    cand = sorted((fields & declared & set(full)) - set(nod))
                    if cand:
                        target = (relp, c, fn, cand[0])
        if target is None:
            print("[!] assigns-underdeclaration --self-test-dispatch: REFUSING \u2014 no clause "
                  "names a dispatch-only record field, so the injection cannot be built.")
            return 2
        rows, _old = dispatch_rows(idx=idx, perturb=target)
        fired = [r for r in rows if r["hole"] and (r["relp"], r["cls"], r["fn"], r["fld"])
                 not in HOLE_V_BASELINE]
        if not any((r["relp"], r["cls"], r["fn"], r["fld"]) == target for r in fired):
            print("[!] assigns-underdeclaration --self-test-dispatch: FAILED \u2014 dropping %s "
                  "from %s.%s's clause did NOT make HOLE-V fire; the dispatch arm is DEAD."
                  % (target[3], target[1], target[2]))
            return 1
        print("[+] assigns-underdeclaration --self-test-dispatch: OK \u2014 dropping %s from "
              "%s.%s's clause (%s; reached ONLY through dispatch) makes HOLE-V fire on %d new "
              "row(s); the arm has teeth." % (target[3], target[1], target[2], target[0],
                                              len(fired)))
        return 0

    if args.self_test_declared:
        holes0, _t, _a = declared_callee_rows()
        target = None
        # find a caller whose clause names a field that a callee ALSO declares, in a class
        # that declares it: omitting it must fire HOLE-D.
        for dirpath, _d, files in os.walk(MIRROR):
            for f in sorted(files):
                if target or not f.endswith(".py"):
                    continue
                mp = os.path.join(dirpath, f)
                relp = os.path.relpath(mp, MIRROR)
                decls, cf = _mirror_decls(mp)
                for (c, fn), (fields, _t2, _l) in sorted(decls.items()):
                    if target:
                        break
                    for fld in sorted(fields & cf.get(c, set())):
                        h, _x, _y = declared_callee_rows(omit=(relp, c, fn, fld))
                        if len(h) > len(holes0):
                            target = (relp, c, fn, fld, len(h) - len(holes0))
                            break
        if target is None:
            print("[!] assigns-underdeclaration --self-test-declared: REFUSING \u2014 no "
                  "injection found, so a PASS would mean nothing.")
            return 2
        print("[+] assigns-underdeclaration --self-test-declared: OK \u2014 pretending %s.%s's "
              "clause omits %s makes HOLE-D fire on %d row(s); the arm has teeth."
              % (target[1], target[2], target[3], target[4]))
        return 0

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

    d_all, d_trap, d_amb = declared_callee_rows()
    d_holes = [r for r in d_all if not r[6]]
    d_init = [r for r in d_all if r[6]]
    print("[*] assigns-underdeclaration DECLARED-CALLEE arm: HOLE-D %d (ceiling %d), HOLE-DI %d "
          "(ceiling %d: field declared in `__init__` only), TRAP-D %d (callee field absent from "
          "the caller's class), %d ambiguous callee frame(s) skipped."
          % (len(d_holes), MAX_HOLE_D, len(d_init), MAX_HOLE_DI, d_trap, d_amb))
    bad_di = sorted({r[:5] for r in d_init} - HOLE_DI_BASELINE)
    if bad_di:
        print("[!] assigns-underdeclaration: HOLE-DI %d NEW row(s) outside HOLE_DI_BASELINE \u2014 a "
              "caller's `#@ assigns` omits an `__init__`-declared (record) field its callee's "
              "DECLARED frame writes." % len(bad_di))
        for r in bad_di[:30]:
            print("    %-32s %-26s %-30s -> %-24s self.%s" % r)
        return 1
    gone_di = sorted(HOLE_DI_BASELINE - {r[:5] for r in d_init})
    if gone_di:
        print("[*] assigns-underdeclaration: %d HOLE-DI baseline row(s) no longer fire \u2014 "
              "REMOVE them from HOLE_DI_BASELINE (the ratchet only shrinks):" % len(gone_di))
        for r in gone_di:
            print("    %-32s %-26s %-30s -> %-24s self.%s" % r)
    if len(d_holes) > MAX_HOLE_D:
        print("[!] assigns-underdeclaration: HOLE-D %d \u2014 a caller's `#@ assigns` omits a "
              "field its callee's DECLARED frame writes, and the caller's class declares it, so "
              "it is mentionable: a concrete caller fails why3 type-check or, reaching the callee "
              "receiver-less, PROVES the field unchanged." % len(d_holes))
        for r in d_holes[:30]:
            print("    %-32s %-26s %-30s -> %-24s self.%s" % r[:5])
        return 1

    rc_v = dispatch_report(args.verbose)
    if rc_v:
        return rc_v

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
