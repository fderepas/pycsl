#!/usr/bin/env python3
r"""check-declaration-conformance.py — DECLARATION ⊑ DEFINITION, as a pure-AST plane (R2a).

WHY (wall `cross-mixin-declaration-stubs`, driver run #3). Each self-annotation mirror file is
transpiled ON ITS OWN, so a method that calls a SIBLING MIXIN's method carries a local bodyless
DECLARATION of it -- a `#@ \trusted` stub whose live twin class has no such `def`, or a
`#@ requires_method m: <sig>` window. Module 6 emits it as an abstract `val` and every caller
in the file ASSUMES its contract. Nothing compared that contract with the DEFINITION the live
composite's MRO actually dispatches to: the 2026-10-30 census found 12 declarations whose frame
was NARROWER than their definition's, three of them load-bearing for 30 verified frames that
were false at runtime (route #488). `bin/check-trusted-frame-honesty.py`'s declaration arm
compares a declaration with the LIVE closure; THIS plane compares it with the MIRROR
definition's contract, clause by clause, so a declaration can never again claim more than its
definition promises.

POPULATION. `bin/lib_declarations.py::declarations` (shared with the frame-honesty arm): every
`\trusted` mirror stub inside a class whose live twin has no `def <name>`, every
`#@ requires_method` window, and every stub carrying `#@ declared_in` (the R4 directive, which
is exactly a declaration this plane has checked). Resolution is through the C3 MRO of every live
class containing the declaring class; it must give EXACTLY ONE definition (else RED).

THE RULES, for declaration DECL and the mirror twin DEF of its resolved definition:
  (a) FRAME     frame(DECL) ⊇ frame(DEF) PROJECTED onto the declaring class's record (its
                annotated class-body fields, which ARE the emitted record of a `@dataclass`
                mixin): a field no unit can mention emits nothing and may be omitted (naming it
                would raise check-assigns-writes-survival's TRAP). When the declaration is
                MRO-SELECTED in a mirror composite's unit (`lib_declarations.mirror_selected_in`:
                it is applied to the COMPOSITE's record there) the projection is onto the union
                of those records; and a writing definition may never
                be declared frameless (`\nothing`/absent: route #488's shape). `\nothing` and
                an absent clause are both the empty frame (both emit a `val` with no `writes`).
  (b) RAISES    raises(DECL) ⊇ raises(DEF).
  (c) PRE/POST  requires / ensures must be TRIVIAL (`True`, or absent) on BOTH sides. A
                text-equal non-trivial clause is NOT accepted here: the two `self`s are
                different record types, so equal text is not equal meaning. Any non-trivial
                pre/post is routed to R2b (a generated Why3 clone-refinement unit, not built)
                and FAILS the plane.
  (d) OTHER     any other clause on DECL (`no_exception`, `pure`, `terminates`, ...) must also
                appear, text-equal, on DEF (a declaration may only claim LESS); `sibling_concrete`
                / `declared_in` / `\trusted` are not contract clauses and are ignored.
  (e) SIGNATURE positionally: the declaration may omit only trailing DEFAULTED parameters of
                the definition (a call through it takes the default); a parameter name that
                differs is a NOTE (calls are positional and, (c) being trivial, no clause names
                a parameter). Each annotation must be equal, or a documented TYPE-LAYER pair
                (`ExprIR` ~ `Dict` / `Dict[str, Any]`: the same runtime IR dict; `set` ~
                `Set[str]`), or an ERASED parameter (the definition's mirror annotates it `int`,
                an opaque handle its proof quantifies over, or leaves it unannotated). A RESULT
                type may never be narrower than the definition's. Every accepted mapping is
                PRINTED (`type-layer mappings in use`), never silently equal.
  (f) DEF       DEF must exist in the mirror (a declaration of a method the mirror does not
                carry has nothing to conform to).
Row 16 of the census (`StatementEmissionMixin._handle_return_stmt`) is a BASE-CLASS
declaration: the declaring class INHERITS the definer. Routes #277/#278 (override ⊑ base, the
`goal <sub>__m_refines_base`) only fire when base and override are in ONE unit; here the base is
imported from the un-annotated live tree and NO refines goal is emitted (measured: 0 `refines`
in statements.mlw). It is reported in its own `base-override` bucket, checked by the same
rules (the callers' assumption must be implied by the definition), and it is NOT eligible for
`#@ declared_in` (it stays `\trusted`) until the override path covers it.

RATCHETS (may only shrink): FAIL_RATCHET (declarations violating a rule) and R2B_RATCHET
(declarations needing R2b). A floor MIN_DECLARATIONS refuses an empty/broken walk.
`--root DIR` checks another tree (negative tests run on a scratch copy).
Exit: 0 green, 1 a ratchet broken / unresolved declaration, 2 refusal.
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_declarations as L  # noqa: E402

# Each NON-CONFORMING declaration is NAMED here with why it is not repaired in the landing
# commit; an unnamed one is RED, a named one that conforms again is a STALE entry (RED). One
# is a SIGNATURE residual and one a base-override residual (run #6 lvN repaired two); each repair moves the
# emission of a big mirror file (a whole-file proof each). None is eligible for
# `#@ declared_in` while it is listed.
KNOWN_NONCONFORMING = {
    "module6_whyml/expressions.py::ExpressionEmissionMixin._field_type_of":
        "requires_method window declares `-> str`; the definition (types.py, VERIFIED) returns "
        "Optional[str]. Repair = `-> Optional[str]` in the window (expressions.py emission moves).",
    "module6_whyml/statements.py::StatementEmissionMixin._handle_return_stmt":
        "BASE-CLASS declaration (census row 16): `stmt: ExprIR` over the verified base's "
        "`ReturnStmt`; routes #277/#278 do not reach it (no refines goal is emitted: the base is "
        "imported from the un-annotated live tree). Stays `\\trusted`.",
}
# The EXACT violation each ledgered declaration is recorded with (the plane's own messages).
KNOWN_FAILURES = {
    "module6_whyml/expressions.py::ExpressionEmissionMixin._field_type_of":
        ["(e) return annotation: decl str / def Optional[str] (the declaration may not claim a "
         "narrower result type)"],
    "module6_whyml/statements.py::StatementEmissionMixin._handle_return_stmt":
        ["(e) `stmt` annotation: decl ExprIR / def ReturnStmt (not a documented type-layer "
         "pair)"],
}
FAIL_RATCHET = len(KNOWN_NONCONFORMING)   # 5 at landing, 4 after lvI (run #5), 3 -> 2 after lvN (run #6); may only SHRINK
R2B_RATCHET = 0
MIN_DECLARATIONS = 20        # measured 26 at 8fdfce794 (24 stubs + 2 windows)

# The documented TYPE-LAYER: the mirror spells an IR node as the typed facade `ExprIR` /
# `"ExprIR"` where the live/sibling code (and some mirror definitions) spell the same runtime
# object `Dict[str, Any]`; both lower to `emit_ir` in the WhyML (measured in the emitted vals).
# A set parameter is spelled `set` in a `requires_method` signature and `Set[str]` in the def:
# both lower to `map int (option int)` (functions.py's cross-mixin set lowering).
TYPE_LAYER = {
    frozenset({"ExprIR", "Dict"}): "IR facade: the same runtime IR dict, both lower to emit_ir",
    frozenset({"ExprIR", "Dict[str, Any]"}): "IR facade: the same runtime IR dict",
    frozenset({"set", "Set[str]"}): "cross-mixin set spelling, both lower to map int (option int)",
}


def _layer(ta, tb, param):
    """Why decl type `ta` may stand for def type `tb`, or None (a FAIL).

    Besides the TYPE_LAYER pairs, one ERASURE rule: a PARAMETER the definition's mirror
    annotates `int` is an opaque handle there (the definition is proved for EVERY int under a
    trivial precondition), so any declared argument type is a restriction of it. Never for a
    result: a declaration may not narrow what the definition returns."""
    if ta is None and tb is None:
        return "both unannotated"
    if ta is not None and tb is not None and frozenset({ta, tb}) in TYPE_LAYER:
        return TYPE_LAYER[frozenset({ta, tb})]
    if param and tb == "int":
        return "ERASED: the definition's mirror types it as an opaque int handle"
    if param and tb is None:
        return "the definition leaves it unannotated (Any)"
    return None


_NON_CONTRACT = ("sibling_concrete", "declared_in", "\\trusted")


def _norm_ann(a):
    if a is None:
        return None
    s = ast.unparse(a) if not isinstance(a, str) else a
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        s = s[1:-1]
    return re.sub(r"\s+", " ", s)


def _params(fn):
    a = fn.args
    pos = a.posonlyargs + a.args
    nd = len(pos) - len(a.defaults)
    out = [(p.arg, _norm_ann(p.annotation), i >= nd) for i, p in enumerate(pos)]
    out += [(p.arg, _norm_ann(p.annotation), d is not None)
            for p, d in zip(a.kwonlyargs, a.kw_defaults)]
    return out, _norm_ann(fn.returns)


def _window_fn(sig):
    try:
        return ast.parse("def _w%s: pass" % sig).body[0]
    except SyntaxError:
        return None


def check(root):
    decls = L.declarations(root, marker_re=re.compile(r"^declared_in\b"))
    rows = []
    for d in decls:
        q = "%s::%s.%s" % (d["rel"], d["cls"], d["name"])
        if d["kind"] == "window":
            q += " (requires_method window on %s)" % d["host"]
        fails, r2b, notes = [], [], []
        defs = d["defs"]
        if len(defs) != 1:
            rows.append((d, q, None, ["UNRESOLVED: %s" % (defs or "dead (no live definition)")],
                         [], notes, "?"))
            continue
        dcls, dpath = defs[0]
        md = L.mirror_def(root, dpath, dcls, d["name"])
        dq = "%s.%s" % (dcls, d["name"])
        lgraph_bases = []
        bucket = "other-mixin"
        if md is None:
            rows.append((d, q, dq, ["(f) no mirror twin of the definition %s" % dq], [], notes,
                         bucket))
            continue
        dfn, _dlines, dclauses, dtrusted, dmpath = md
        notes.append("def %s (%s, %s)" % (dq, dmpath.split(L.MIRROR_REL + "/")[-1],
                                          "trusted" if dtrusted else "VERIFIED"))
        # bucket: base-class declaration (the declaring class inherits the definer)
        if dcls in L.c3_mro(d["cls"], _GRAPH[0]):
            bucket = "base-override"
        # (g) `#@ declared_in` (B4): the NAMED target must EQUAL the live-MRO resolution, the
        # stub must carry exactly one such line and no `\trusted` marker, and it may not sit
        # on a ledgered (KNOWN_NONCONFORMING) or base-override declaration.
        if d.get("declared_in"):
            want = "%s::%s" % (os.path.relpath(dpath, os.path.join(root, L.LIVE_REL)), dq)
            if len(d["declared_in"]) != 1:
                fails.append("(g) %d `declared_in` lines (exactly one allowed)"
                             % len(d["declared_in"]))
            elif d["declared_in"][0] != want:
                fails.append("(g) `declared_in %s` names a target other than the live-MRO "
                             "definition %s" % (d["declared_in"][0], want))
            if d.get("trusted_marker"):
                fails.append("(g) `declared_in` together with a `\\trusted` marker")
            if bucket != "other-mixin":
                fails.append("(g) `declared_in` on a %s declaration (only other-mixin "
                             "declarations are eligible)" % bucket)
            if q.split(" (")[0] in KNOWN_NONCONFORMING:
                fails.append("(g) `declared_in` on a LEDGERED non-conforming declaration")
        dc = d["clauses"]
        # (a) frame
        dfr, _ = L.frame(dc)
        efr, _ = L.frame(dclauses)
        mc = _GRAPH[1]
        sel = L.mirror_selected_in(d["cls"], d["name"], mc) if d["kind"] == "stub" else []
        rec = set(mc.get(d["cls"], (None, [], set(), set(), []))[3])
        for _c in sel:
            rec |= L.composite_record(_c, mc)
        if sel:
            notes.append("MRO-SELECTED in mirror composite(s) %s: projected onto the union "
                         "record" % sel)
        need = {t for t in efr if not (t.startswith("self.") and t[5:] not in rec)}
        unm = sorted(efr - need - dfr)
        if unm:
            notes.append("PROJECTED: %d definition field(s) absent from every record the "
                         "declaration reaches (no unit can mention them): %s"
                         % (len(unm), unm[:4]))
        miss = sorted(need - dfr)
        if miss:
            fails.append("(a) frame misses %d target(s) of the definition: %s"
                         % (len(miss), ", ".join(miss[:5]) + (" ..." if len(miss) > 5 else "")))
        if efr and not dfr:
            fails.append("(a) frameless declaration of a writing definition (a frameless `val` "
                         "where the definition's frame would emit `writes`/`_pyobj_state`: "
                         "the route #488 shape)")
        # (b) raises
        rmiss = sorted(L.raises(dclauses) - L.raises(dc))
        if rmiss:
            fails.append("(b) raises misses %s" % ", ".join(rmiss))
        # (c) pre/post
        for kw in ("requires", "ensures"):
            a, b = L.prepost(dc, kw), L.prepost(dclauses, kw)
            if a or b:
                r2b.append("(c) non-trivial %s (decl %s / def %s) -> R2b" % (kw, a, b))
        # (d) other clauses
        dk, ek = L.by_kw(dc), L.by_kw(dclauses)
        for kw, vals in dk.items():
            if kw in ("requires", "ensures", "assigns", "raises") or kw in _NON_CONTRACT:
                continue
            for v in vals:
                if v not in ek.get(kw, []):
                    fails.append("(d) declaration claims `%s %s` the definition does not"
                                 % (kw, v))
        # (e) signature
        fn = d["node"] if d["kind"] == "stub" else _window_fn(d.get("sig", ""))
        if fn is None:
            fails.append("(e) unparsable requires_method signature %r" % d.get("sig"))
        else:
            (pa, ra), (pb, rb) = _params(fn), _params(dfn)
            if len(pa) > len(pb):
                fails.append("(e) declaration has %d parameter(s), definition %d"
                             % (len(pa), len(pb)))
            for (nb, _tb, db) in pb[len(pa):]:
                if not db:
                    fails.append("(e) definition parameter `%s` has no default and the "
                                 "declaration omits it" % nb)
                else:
                    notes.append("ARITY: definition's defaulted `%s` not declared (a call "
                                 "through the declaration always takes the default)" % nb)
            for i, ((na, ta, da), (nb, tb, db)) in enumerate(zip(pa, pb)):
                if na != nb:
                    notes.append("NAME: position %d `%s` ~ `%s` (positional; pre/post are "
                                 "trivial so no clause names it)" % (i, na, nb))
                if da and not db and d["kind"] == "stub":
                    fails.append("(e) `%s` is defaulted in the declaration only" % na)
                if na == "self" or ta == tb:
                    continue
                why = _layer(ta, tb, param=True)
                if why:
                    notes.append("TYPE-LAYER `%s`: decl %s ~ def %s (%s)" % (na, ta, tb, why))
                else:
                    fails.append("(e) `%s` annotation: decl %s / def %s (not a documented "
                                 "type-layer pair)" % (na, ta, tb))
            if ra != rb:
                why = _layer(ra, rb, param=False)
                if why:
                    notes.append("TYPE-LAYER return: decl %s ~ def %s (%s)" % (ra, rb, why))
                else:
                    fails.append("(e) return annotation: decl %s / def %s (the declaration "
                                 "may not claim a narrower result type)" % (ra, rb))
        rows.append((d, q, dq, fails, r2b, notes, bucket))
    return decls, rows


_GRAPH = [None, None]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--fail-ratchet", type=int, default=FAIL_RATCHET)
    ap.add_argument("--r2b-ratchet", type=int, default=R2B_RATCHET)
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    _GRAPH[0] = L.live_graph(os.path.join(root, L.LIVE_REL))
    _GRAPH[1] = L.mirror_classes(root)
    decls, rows = check(root)
    if len(decls) < MIN_DECLARATIONS:
        print("[!] declaration-conformance: REFUSING — only %d declaration(s) found under %s, "
              "expected at least %d. THIS IS A REFUSAL, NOT A PASS."
              % (len(decls), root, MIN_DECLARATIONS), file=sys.stderr)
        return 2
    n_fail = sum(1 for r in rows if r[3])
    n_r2b = sum(1 for r in rows if r[4])
    n_ok = sum(1 for r in rows if not r[3] and not r[4])
    layer = sorted({n.split(": ", 1)[1] for r in rows for n in r[5] if n.startswith("TYPE-LAYER")})
    for d, q, dq, fails, r2b, notes, bucket in rows:
        st = "FAIL" if fails else ("R2B " if r2b else "ok  ")
        if args.verbose or fails or r2b:
            print("  %s %-14s %s" % (st, bucket, q))
            for f in fails + r2b:
                print("         %s" % f)
            if args.verbose:
                for n in notes:
                    print("         . %s" % n)
    print("[*] declaration-conformance: %d declaration(s) (%d stubs, %d requires_method windows, "
          "%d `declared_in`); %d CONFORM (frame ⊇, raises ⊇, trivial pre/post, signature), "
          "%d FAIL, %d need R2b; buckets: %s."
          % (len(decls), sum(1 for d in decls if d["kind"] == "stub"),
             sum(1 for d in decls if d["kind"] == "window"),
             sum(1 for d in decls if d["kind"] == "stub"
                 and any(c.startswith("declared_in") for c in d["clauses"])),
             n_ok, n_fail, n_r2b,
             {b: sum(1 for r in rows if r[6] == b) for b in sorted({r[6] for r in rows})}))
    print("[*] declaration-conformance: type-layer mappings in use (accepted, not equal): %s"
          % ("; ".join(layer) if layer else "none"))
    rc = 0
    failing = {q.split(" (")[0] for _d, q, _dq, fails, _r, _n, _b in rows if fails}
    for q in sorted(failing - set(KNOWN_NONCONFORMING)):
        print("[!] declaration-conformance: UNNAMED non-conforming declaration %s — repair it "
              "(give it its definition's contract) or name it in KNOWN_NONCONFORMING." % q)
        rc = 1
    # A LEDGERED declaration must fail EXACTLY as recorded (KNOWN_FAILURES): a new or a
    # changed violation on an already-named declaration is not hidden by its ledger entry.
    for _d, q, _dq, fails, _r, _n, _b in rows:
        k = q.split(" (")[0]
        if fails and k in KNOWN_NONCONFORMING and sorted(fails) != sorted(KNOWN_FAILURES.get(k, [])):
            print("[!] declaration-conformance: LEDGERED declaration %s fails DIFFERENTLY than "
                  "recorded: %s (recorded: %s)." % (k, fails, KNOWN_FAILURES.get(k)))
            rc = 1
    for q in sorted(set(KNOWN_NONCONFORMING) - failing):
        print("[!] declaration-conformance: STALE KNOWN_NONCONFORMING entry %s — it conforms "
              "now; remove it and lower FAIL_RATCHET in the same commit." % q)
        rc = 1
    eligible = [q for d, q, _dq, fails, r2b, _n, b in rows
                if d["kind"] == "stub" and not fails and not r2b and b == "other-mixin"
                and not d.get("declared_in")]
    print("[*] declaration-conformance: %d `\\trusted` declaration stub(s) are CHECKED here "
          "(conforming, other-mixin): the population a `#@ declared_in` marker may carry."
          % len(eligible))
    # `#@ declared_in` (B4) population: every marker in the mirror must govern a declaration
    # of THIS census (a marker on a def that has a live twin, a nested / module-level def, or
    # no def at all would otherwise be skipped by every fidelity plane and checked by none).
    din_rows = [r for r in rows if r[0].get("declared_in")]
    din_ok = [r for r in din_rows if not r[3] and not r[4]]
    pop = {(r[0]["path"], "%s.%s" % (r[0]["cls"], r[0]["name"])) for r in din_rows}
    for path, qn, line, tgt in L.declared_in_markers(root):
        if qn is None or (path, qn) not in pop:
            print("[!] declaration-conformance: `#@ declared_in %s` at %s:%d governs %s, which "
                  "is NOT a cross-mixin declaration of this census (it has a live twin, is not "
                  "a class method, or annotates nothing): REFUSED." % (tgt, path, line,
                                                                      qn or "no def"))
            rc = 1
    print("[*] declaration-conformance: %d `#@ declared_in` stub(s), %d CONFORM (each is a "
          "certified cross-mixin declaration, counted apart from `\\trusted`)."
          % (len(din_rows), len(din_ok)))
    for label, got, want in (("fail", n_fail, args.fail_ratchet),
                             ("r2b", n_r2b, args.r2b_ratchet)):
        if got > want:
            print("[!] declaration-conformance: %s RATCHET BROKEN — %d > %d. A declaration is "
                  "ASSUMED by every caller in its file; one that claims more than its "
                  "definition proves is an unchecked assumption (route #488)." % (label, got, want))
            rc = 1
        elif got < want:
            print("[+] declaration-conformance: %s %d < ratchet %d — lower the constant."
                  % (label, got, want))
    if rc == 0:
        print("[+] declaration-conformance: OK — %d/%d declarations conform." % (n_ok, len(decls)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
