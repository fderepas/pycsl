#!/usr/bin/env python3
"""check-untrusted-emitted.py — INTEGRITY GATE for the self-annotation count.

THE HAZARD THIS CLOSES. Removing a `#@ \trusted` marker is what the TCB-reduction
campaign counts as a conversion. But removing the marker does NOT by itself guarantee
that anything is verified in its place: PyCSL has an AUTO-TRUST SAFETY VALVE, so a body
the emitter cannot lower is silently re-abstracted to an opaque `val` — and the file
still type-checks (L3-tc ✓) and still proves. A stub in that state has had its marker
removed while NOTHING about it is verified: the count improves, the TCB does not.

Discovered 2026-08-27 (relaunch #3) while probing candidate conversions: of 17 candidates
that passed L3-tc after their marker was dropped, **not one** was emitted as a definition
— 6 were dropped from emission entirely and 11 came back as abstract `val`s. L3-tc alone
is therefore NOT a conversion criterion.

WHAT THIS CHECKS. For every mirror function that is neither `#@ \trusted` nor
`#@ \abstract`, emit its file and require the function to appear as a real DEFINITION —
`let` / `let rec` / `let function` / … or a `with` continuation of a mutual-recursion
group (which is a definition with a body, not a `val`). Report:

    LET     - genuinely defined, body emitted        (the only healthy outcome)
    VAL     - silently re-abstracted                 (**the defect this gate exists for**)
    ABSENT  - not emitted as a standalone function

ABSENT is EXPECTED for `__init__` (constructors are inlined into the record's `by`
witness) and for dunders the emitter models structurally; those are allow-listed below by
SHAPE, not by name, so a new one is surfaced rather than hidden.

BASELINE at the time of writing: 687 un-trusted functions, **0 VAL**, and every ABSENT an
`__init__` / `_Tok.__repr__`. The campaign's booked conversions are clean — the count is
NOT inflated by silent re-abstraction.

Usage:  bin/check-untrusted-emitted.py [path-prefix ...]
Exit 1 if any VAL is found, or any unexpected ABSENT.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src/self-annotate/src")
LIVE_IMPORT = os.path.join(ROOT, "src/pycsl")

# ABSENT is expected for these SHAPES: constructors are inlined into the record's `by`
# witness, and the two remaining constructor HOOKS are still skipped by
# `Module5_IREmitter._should_skip_method` for their own measured reasons.
#
# (#49) gen #31 — THE LIST USED TO READ
#     ("__init__", "__repr__", "__str__", "__enter__", "__exit__")
# with the justification "dunders are modelled structurally rather than emitted as
# functions". THAT JUSTIFICATION WAS NOT WHAT THE EMITTER DID: dunders were DROPPED before
# any IR was built, not modelled. The consequence was small in count and sharp in kind —
# TWO un-trusted mirror functions (`errors.py::PyCSLError.__str__`,
# `Module2_Parser.py::_Tok.__repr__`) were counted among the 887 VERBATIM UN-TRUSTED TWINS,
# i.e. in the population this project calls verified, while NEVER BEING EMITTED OR PROVED.
# An allow-list entry with a wrong reason is how that survives a whole campaign.
# Route #219's repair emits every dunder but `__init__`/`__new__`/`__post_init__`, so the
# list narrows to exactly those, and the two mirror methods now carry honest `#@ \trusted`
# markers (459 -> 461) instead of an exemption.
#
# (#49) gen #31 UPDATE — ONE OF THE TWO IS ALREADY RETIRED, 461 -> 460. Backlog #51
# named its capability exactly: `_Tok.__repr__` had no return annotation, so the
# emitter typed it `int` and the f-string body was a Why3 TYPE ERROR. Annotating the
# LIVE twin `def __repr__(self) -> str:` (and the mirror to match, verbatim) makes it
# PROVE, and the marker came off. `errors.py::PyCSLError.__str__` remains, and remains
# `cost-scale:string-field-model` — it needs a faithful string-typed self-field model,
# not an annotation.
MIN_UNTRUSTED = 750         # (#49) gen #31: measured 861. A FLOOR on the POPULATION.

EXPECTED_ABSENT = ("__init__", "__new__", "__post_init__")

# CLUSTER-EMITTED functions. Several recognizers emit a whole GROUP of mirror functions as
# ONE self-contained `let rec` block whose members carry GENERATED names, so the Python
# name never appears in the emission even though the function IS verified. Searching for
# the Python name alone reported the five `_conc_*` checkers as "not emitted" when
# `core_ir_semantic.mlw` in fact contains 12 `conc__*` definitions and 57 references to
# them (`emit_conc_cluster_group`, dispatched from `functions.py` via `_conc_names`).
# Each entry maps a Python name to the PREFIX its cluster emits under, and the gate
# requires that prefix to be present — so a cluster that stops being emitted is still
# caught, and only the RENAMING is excused.
CLUSTER_EMITTED = {
    "_check_concurrency": "conc__",
    "_conc_check_shared_access": "conc__",
    "_conc_check_reads": "conc__",
    "_conc_stmts": "conc__",
    "_conc_stmt": "conc__",
}

# Memory-model accessors that are unreachable in the `hoare` model this mirror is emitted
# under (`_heap_var` raises `ValueError("No heap variable in Hoare model")` on the only
# path the model can take), so there is nothing to emit.
EXPECTED_ABSENT_NAMES = ("_heap_var",)


def annotation_flags(lines, node):
    """(is_trusted, is_abstract) read off the `#@` block above a def.

    BLANK LINES may separate that block from the `def` (audit_proof_reverify.py puts two
    there), so blanks are skipped — stopping at the first non-comment line mis-classified
    12 trusted functions as un-trusted while this gate was being written.
    """
    i = min([d.lineno for d in node.decorator_list] + [node.lineno]) - 2
    trusted = abstract = False
    while i >= 0 and (lines[i].strip().startswith("#") or not lines[i].strip()):
        t = lines[i].strip()
        if t.startswith("#@ \\trusted"):
            trusted = True
        if t.startswith("#@ \\abstract"):
            abstract = True
        if not t and trusted:
            break
        i -= 1
    return trusted, abstract


def candidates(path):
    """Every un-trusted, un-abstract mirror function, as `(class-tuple, name,
    enclosing-def-or-None, enclosing-def-is-trusted)`.

    (#49) gen #31 — DESCENDS INTO NESTED DEFS, AND THROUGH COMPOUND STATEMENTS. This walk
    used to recurse into a ClassDef and stop at a FunctionDef, so a closure was invisible to
    this gate. That is not a cosmetic gap: this plane IS the integrity gate on the conversion
    count — the thing that stops a marker being removed from a body the emitter silently
    re-abstracts to an opaque `val`. The FIDELITY plane descends (see the gen #4 note in
    `check-self-annotate-mirror-sync.py::_walk`, which fixed exactly this walk in exactly
    this way), so every nested un-trusted closure was already counted among the verbatim
    un-trusted twins — the population this project calls verified — while this gate never
    asked whether it was emitted. CENSUSED at the time of the fix: **52** such functions.

    FOUND BY: `pycsl.py::_finalize` is a nested `\trusted` stub whose marker can be removed
    with a BYTE-IDENTICAL emission — it stays `val _finalize (merged_records: int) (rc: int)
    : (int, int, int)` either way. Converting it would drop the marker count by one and prove
    nothing at all, and no plane would have said so.
    """
    src = open(path).read()
    lines = src.split("\n")
    out = []

    def walk(node, cls, encl, encl_trusted):
        for c in ast.iter_child_nodes(node):
            if isinstance(c, ast.ClassDef):
                walk(c, cls + (c.name,), encl, encl_trusted)
            elif isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                trusted, abstract = annotation_flags(lines, c)
                if not trusted and not abstract:
                    out.append((cls, c.name, encl, encl_trusted))
                walk(c, cls, c.name, trusted or encl_trusted)
            else:
                # compound statements (`try:` / `if:` / `with:` / `for:`) hold closures too
                walk(c, cls, encl, encl_trusted)

    walk(ast.parse(src), (), None, False)
    return out


def emit(path):
    mlw = path[:-3] + ".mlw"
    if os.path.exists(mlw):
        os.remove(mlw)
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "src/pycsl/pycsl.py"), path,
         "--import-path", LIVE_IMPORT, "--no-proof", "--keep-mlw"],
        capture_output=True, text=True, cwd=ROOT,
        env={**os.environ, "PYTHONHASHSEED": "0"}, timeout=1800)
    text = open(mlw).read() if os.path.exists(mlw) else ""
    if os.path.exists(mlw):
        os.remove(mlw)
    return text


# A mirror function whose PYTHON name is also a WhyML keyword (`src/self-annotate/src/
# module6_whyml/statements.py` really does contain two nested `def rec`). For these the
# class-mangling prefix is MANDATORY, because otherwise the bare keyword in `let rec ...`
# — which appears in essentially every emitted file — matches and the function is reported
# LET, the benign verdict, whatever the emitter actually did. bin/count-trusted-directives.py
# carries the same set for the same reason; this plane was missing it.
WHYML_KEYWORDS = {"rec", "function", "constant", "predicate", "ghost", "lemma", "type",
                  "val", "let", "with", "partial", "ref", "old", "result"}


def classify(name, text):
    # (#49) gen #31 — KNOWN LIMITATION, RECORDED RATHER THAN SILENTLY LIVED WITH. This
    # matches on the BARE Python name plus a mangling prefix, so it cannot tell two
    # same-named functions in one file apart. `core_ir_semantic.py` defines FIVE nested
    # closures called `walk`, one of them inside a `\trusted` parent; if any one of the
    # five is emitted, all five classify LET. The emitter mangles a lifted closure with its
    # OWNER (`irscanner___has_return`), not with its enclosing function, so there is no
    # name that would separate them — closing this needs the emitter to carry the enclosing
    # scope into the lifted name, which is a lowering change, not a plane change.
    # The population is small and named: `core_ir_semantic.py::walk` x5,
    # `frontend/ir_resolve.py::_walk` x3, `module6_whyml/functions.py::classify` x6,
    # `saw` x4, `rename` x4, `refs_param` x4, `module6_whyml/types.py::_scan` x2.
    b = re.escape(name)
    pre = r"[\w']*__" if name in WHYML_KEYWORDS else r"(?:[\w']*__)?"
    # `with <name>` is a mutual-recursion member of a `let rec … with …` group — a real
    # definition. Omitting it reported 10 false ABSENTs for the converted `_Parser` nest.
    # MANGLING-AWARE PREFIX (gen #4). The bare `[\w']*` here made both searches SUFFIX
    # matches over the whole `.mlw`, so any function whose name merely ENDED another
    # definition's name was reported LET — the benign verdict — whatever the emitter had
    # actually done with it. Demonstrated: classify("foo", "let barfoo (x:int):int") == LET.
    #
    # THE OBVIOUS FIX IS WRONG AND WAS MEASURED BEFORE IT WAS BELIEVED. Replacing the
    # wildcard with a plain `\b` took the plane from "0 unexpectedly absent" to 668 NOT
    # EMITTED lines, because the wildcard is LOAD-BEARING: `classify` is called with the
    # bare PYTHON name while the emitted definition carries the CLASS MANGLING
    # (`_ContractParser.cur` -> `let _contractparser__cur`). The prefix must therefore be
    # allowed, but only when it really is a mangling — i.e. when it ENDS IN `__`. That
    # keeps `_contractparser__cur` matching `cur` and stops `barfoo` matching `foo`.
    #
    # For a name that is itself a WhyML KEYWORD the prefix is made MANDATORY (see
    # WHYML_KEYWORDS above), because `let rec ...` appears in nearly every emitted file and
    # would otherwise match a function named `rec` — of which the mirror has two.
    # bin/count-trusted-directives.py documents this trap and defends against it; this
    # sibling plane did not.
    if re.search(r"\b(let (rec |partial )?|with )"
                 r"(function |predicate |lemma |ghost )?" + pre + b + r"\b", text):
        return "LET"
    if re.search(r"\bval (function |predicate |ghost )?" + pre + b + r"\b", text):
        return "VAL"
    return "ABSENT"


def main():
    prefixes = sys.argv[1:]
    files = sorted(os.path.join(d, f)
                   for d, _, fs in os.walk(MIRROR) for f in fs if f.endswith(".py"))
    bad_val, bad_absent, bad_parent, total, lets, folded = [], [], [], 0, 0, 0
    for path in files:
        rel = os.path.relpath(path, MIRROR)
        if prefixes and not any(rel.startswith(p) for p in prefixes):
            continue
        cands = candidates(path)
        if not cands:
            continue
        text = emit(path)
        for cls, name, encl, encl_trusted in cands:
            total += 1
            status = classify(name, text)
            qn = ".".join(cls + (name,))
            if encl_trusted:
                # (#49) gen #31 — THE STATIC HALF, and it needs no emission at all. An
                # un-trusted closure inside a `\trusted` enclosing function can never be
                # verified: the parent is emitted as an opaque `val`, so no body anywhere
                # carries the closure's claim — yet the FIDELITY plane descends and counts
                # the closure among the verbatim un-trusted twins.
                # WHY STATIC RATHER THAN BY EMISSION: `classify` matches the BARE name, and
                # `core_ir_semantic.py` has FIVE closures called `walk` of which exactly one
                # sits inside a `\trusted` parent. Four of them ARE emitted, so the
                # emission-based verdict for all five is LET and the real one hides behind
                # its siblings. The static question has no such blind spot.
                # MEASURED: 2 — `Module6_WhyMLTranspiler::_sig_val_from_let::_hdr_name`
                # (which the emission check ALSO caught, as a `val`) and
                # `core_ir_semantic::_returns_literal_none::walk` (which it did not).
                bad_parent.append((rel, "%s (inside `\\trusted` %s)" % (qn, encl)))
                continue
            if status == "LET":
                lets += 1
            elif status == "VAL":
                bad_val.append((rel, qn))
            elif name in CLUSTER_EMITTED:
                # Verified under generated names — require the cluster to be present.
                if CLUSTER_EMITTED[name] in text:
                    lets += 1
                else:
                    bad_absent.append((rel, qn + f"  [cluster prefix "
                                                 f"'{CLUSTER_EMITTED[name]}' MISSING]"))
            elif encl is not None and classify(encl, text) == "LET":
                # (#49) gen #31 — FOLDED. A nested closure is ABSENT from the emission
                # because the emitter's RECOGNIZERS consume it into the enclosing
                # function's model rather than lowering it to its own definition.
                # MEASURED on `module6_whyml/functions.py::
                # _build_method_param_result_ensures_map`: the Python body's `classify`,
                # `refs_param` and `rename` closures do not appear, and the parent IS
                # emitted as a `let` whose body is the recognizer's fold, with lifted
                # helpers named after the PARENT (`__lmem`, `__gtype`, `__gnm`, `__gvar`,
                # `__f`). Whether that fold is FAITHFUL is `check-bespoke-model-drift.py`'s
                # question, not this plane's; this plane asks only whether something was
                # emitted that can carry the claim, and for a folded closure the parent's
                # definition is that something.
                # THE CONDITION IS THE WHOLE POINT: the parent must itself be a DEFINITION.
                # A closure inside a `\trusted` parent is folded into a `val` — i.e. into
                # nothing — and still falls through to the refusal below.
                folded += 1
            elif name not in EXPECTED_ABSENT and name not in EXPECTED_ABSENT_NAMES:
                bad_absent.append((rel, qn + ("" if encl is None
                                              else "  [nested inside %s, which is %s]"
                                              % (encl, classify(encl, text)))))

    for rel, qn in bad_parent:
        print(f"[!] UN-TRUSTED INSIDE A TRUSTED PARENT: {rel}::{qn} — the enclosing function "
              f"is emitted as an opaque `val`, so this closure's body is verified NOWHERE, "
              f"while the fidelity plane counts it among the verbatim un-trusted twins. "
              f"Mark it `#@ \\trusted` (honest) or convert the parent.")
    for rel, qn in bad_val:
        print(f"[!] SILENTLY RE-ABSTRACTED: {rel}::{qn} — un-trusted but emitted as `val`. "
              f"Its marker is gone and nothing is verified in its place.")
    for rel, qn in bad_absent:
        print(f"[!] NOT EMITTED: {rel}::{qn} — un-trusted but absent from the emission "
              f"(and not a constructor/dunder).")
    print(f"[{'!' if bad_val or bad_absent or bad_parent else '+'}] untrusted-emitted: {total} un-trusted "
          f"function(s); {lets} emitted as definitions, {folded} nested closure(s) FOLDED "
          f"into an emitted enclosing definition, {len(bad_val)} re-abstracted to "
          f"`val`, {len(bad_absent)} unexpectedly absent, {len(bad_parent)} "
          f"un-trusted inside a `\\trusted` parent.")
    # (#49) gen #31 — ZERO-INPUT GUARD. The verdict is "no `val`, no unexpected absence",
    # and an EMPTY population satisfies both: if the mirror walk or the `.mlw` lookup
    # breaks, `total` is 0, both lists are empty, and this plane prints `[+]` over a
    # measurement nobody made. The floor bounds the POPULATION instead — the #44 rule,
    # already carried by `byte-diff-sweep.sh`, `run-soundness-planes.sh` and
    # `check-directive-enforcement.py`, and missing here until now.
    if total < MIN_UNTRUSTED:
        print(f"[!] untrusted-emitted: REFUSING — only {total} un-trusted function(s) "
              f"found, expected at least {MIN_UNTRUSTED}. The mirror walk is broken, so "
              f"\"0 re-abstracted, 0 absent\" means nothing. THIS IS A REFUSAL, NOT A "
              f"PASS.", file=sys.stderr)
        return 2
    return 1 if (bad_val or bad_absent or bad_parent) else 0


# BASELINE, whole mirror, 2026-08-27: 716 un-trusted · 699 definitions (694 direct + the
# 5 cluster-emitted `_conc_*`) · 0 re-abstracted to `val` · 0 unexpectedly absent.


if __name__ == "__main__":
    sys.exit(main())
