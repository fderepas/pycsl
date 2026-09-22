#!/usr/bin/env python3
r'''L-PLANE ORACLE: which of the compiler's ADVICE-BEARING refusals has anyone actually
followed the advice of?

WHY THIS EXISTS (#49, gen #30). `getting-better/convergence-metric-implement.md` has
carried this on its unmeasured list for generations:

    "The refusal-text surface stays unmeasured. 62 advice-bearing messages, and #90 came
     from one. No metric in the report or this plan samples English prose for
     exploitability; the advice-audit generator remains manual."

A refusal's advice is a CLAIM THE COMPILER MAKES ABOUT ITSELF, in the one place a user is
guaranteed to read, and it is the only claim in the system with no gate behind it. Route
#90 came out of one such message. Nothing since has checked another.

WHAT IT MEASURES. Every `raise PyCSL*Error(...)` in `src/pycsl/` whose message contains an
advice verb (use / rewrite / declare / add / give / call / drop / remove / replace /
instead / prefer), keyed on (file, line). 93 at the first measurement. Each AUDITED entry
records the verdict of having WRITTEN THE PROGRAM THE MESSAGE TELLS YOU TO WRITE and run
it — the only method that means anything here:

  FOLLOWABLE   the repair the message names produces a file that VERIFIES.
  UNSPELLABLE  the repair's literal text is not valid syntax.
  UNTRIED      the repair does not work; the compiler cannot do what it advises.
  AMBIGUOUS    the repair is true but under-specified — a reader who follows it the
               obvious way still gets the refusal.

THE FIRST MEASUREMENT (#49, gen #30): **198 raise sites, 94 advice-bearing, 10 AUDITED** —
7 FOLLOWABLE, 1 UNSPELLABLE, 1 UNTRIED, 1 AMBIGUOUS. Seven of ten pieces of advice work,
which is better than I expected and is exactly why the three that do not are worth the cost
of finding. The failures are in the three distinct ways advice can fail, and each entry
below records what was written and what happened.

FOUR MORE WERE AUDITED AND ARE NOT IN THIS POPULATION, recorded here so the work is not
lost and the number is not inflated: `Module2_Parser`'s "only .keys()/.values()/.items()
are recognised", `Module5_IREmitter`'s "only int/str/bool/None literals supported" and
"must be `Callable[[A1, ..., An], R]`", and `expressions`'s "a total=True TypedDict literal
must provide every declared key". All four are FOLLOWABLE (each was written and VERIFIES).
They state a RESTRICTION rather than an instruction, so they carry no advice VERB and this
plane's matcher does not see them. Widening the matcher to catch them takes the population
94 -> 121 and dilutes the fraction with messages that mostly say "X is unsupported"; the
narrow definition — the message TELLS YOU WHAT TO DO — is the surface route #90 came from,
so it is the one kept.

THE RATCHET IS THE AUDITED COUNT, AND IT MAY ONLY GROW. This plane cannot check the prose
itself; what it can do is stop the manual work from evaporating. An audit that lives in a
commit message is an audit nobody can build on; an audit that lives in a baseline here is
one the next generation continues rather than repeats.

A NEW advice-bearing refusal does NOT fail this gate — it lands unaudited and the audited
FRACTION falls, which is the honest signal. What fails is the audited count going DOWN,
which means an audited message was edited (and then its verdict is stale and must be
re-derived, exactly as a message edit invalidates a refusal-witness census row).

THE POPULATION GUARD (the #44 rule): rc=2 below MIN_SITES raise sites or MIN_ADVICE
advice-bearing ones, so "everything audited" can never mean "I matched nothing".

WHY THE KEY IS A TEXT SIGNATURE AND NOT A LINE NUMBER. The first version of this plane
keyed on (file, lineno) and went RED the moment an unrelated edit three functions above
shifted seven messages down a line — noise, and the kind that trains a reader to ignore a
gate. The key is now (file, the first 48 characters of the message's concatenated string
literals). That is stable under line movement and CHANGES when the message text changes,
which is exactly right: a message edit SHOULD invalidate the verdict, because the verdict
is about the words.

Usage:  bin/check-refusal-advice-audited.py [--verbose] [--list-unaudited]
'''
import argparse
import ast
import glob
import os
import re
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "pycsl")
MIN_SITES = 150
MIN_ADVICE = 70

ADVICE = re.compile(r"\b(use|rewrite|declare|add|give|call|drop|remove|replace|instead"
                    r"|prefer)\b", re.I)

FOLLOWABLE = "FOLLOWABLE"
UNSPELLABLE = "UNSPELLABLE"
UNTRIED = "UNTRIED"
AMBIGUOUS = "AMBIGUOUS"

def sig(node):
    """Stable, READABLE key for one raise: its unparsed source, normalised, first 64.

    `literal_parts` pops from a stack, so its output order is jumbled — fine for an
    ADVICE keyword match, useless as a human-checkable key. `ast.unparse` gives the
    message in source order and changes exactly when the message text changes."""
    try:
        return " ".join(ast.unparse(node).split())[:64]
    except Exception:                                   # pragma: no cover
        return "<unparse-failed>"


# (file, sig(message)) -> (verdict, what was written and what happened)
AUDITED = {
    ("src/pycsl/frontend/desugar.py",
     "PyCSLParseError('`for ... else` / `while ... else` is not modell"): (FOLLOWABLE,
        "'Rewrite it with an explicit flag' — a `found` flag plus a `while` with an "
        "invariant and a variant VERIFIES."),
    ("src/pycsl/frontend/desugar.py",
     "PyCSLParseError('an EXTENDED slice `x[lo:hi:step]` is not modell"): (FOLLOWABLE,
        "'Use an explicit strided loop' — works. My FIRST attempt failed on MY loop "
        "invariant, not on the advice; recorded because that distinction is the whole "
        "discipline (lesson (i3))."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`#@ lemma` \'{name}\' body must not `return` '): (FOLLOWABLE,
        "'Use `pass` for an immediate arm' — the lemma with a `pass` body VERIFIES."),
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("function \'%s\' writes %s through a `nonlocal` decla'): (FOLLOWABLE,
        "'Return the value from the nested function instead of assigning through the "
        "closure' — VERIFIES."),
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLSemanticError(f'in-place field mutation `{obj}.{field} = .."): (FOLLOWABLE,
        "'Rebuild the record (`p = Pt(...)`) instead' — VERIFIES."),
    ("src/pycsl/module6_whyml/expressions.py",
     "PyCSLSemanticError('array/list with mixed or non-tuple elements "): (FOLLOWABLE,
        "'Use a uniform list of equal-arity tuples' — `[(1, 2), (3, 4)]` VERIFIES."),
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot alias module global \'{node[\'value\']['): (FOLLOWABLE,
        "'call its methods or read its fields directly' — VERIFIES, with a class "
        "invariant my first attempt lacked (my test, not the advice)."),

    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("function \'%s\' writes %s through a `global` declara'): (UNSPELLABLE,
        "'Declare the variable `#@ shared`' — `#@ shared` ALONE IS A SYNTAX ERROR; the "
        "grammar is `#@ shared <name>`. Spelled correctly it works, including under the "
        "DEFAULT memory model. But a `#@ shared` variable is not nameable in a contract, "
        "so `#@ assigns <name>` on the same function is then refused as undefined: you "
        "can take the advice and be unable to FRAME the write. CHECKED that this does NOT "
        "reopen route #129 — the exploit shape leaves the prover at UNKNOWN and the file "
        "FAILS. The message now gives the form and the caveat; its OTHER repair ('pass "
        "and return the value') is FOLLOWABLE."),
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("function \'%s\' binds %s with a `with ... as` clause'): (UNTRIED,
        "'Call `__enter__` explicitly and assign its result' DOES NOT WORK. Two files "
        "identical except for ONE IDENTIFIER — a method returning 7 under "
        "`ensures \\result == 7`, called from a driver claiming the same — VERIFY as "
        "`enter` and FAIL as `__enter__`. `__len__` fails too and `_enter_` verifies: an "
        "explicitly-called DUNDER does not carry its contract to the call site. A "
        "COMPLETENESS gap, not an unsoundness. The message's other repair (a bare "
        "`with <lock>:`) IS followable and is now given FIRST; the broken one was "
        "withdrawn, with its measurement, so nobody re-adds it."),
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot inline \'{callee}\' on \'{recv}\': it ha'): (AMBIGUOUS,
        "'Verify it by contract' is true and under-specified. Adding a contract while "
        "KEEPING the module-global receiver does not help, and neither does "
        "`#@ \\trusted` — the inliner runs on a global-receiver call regardless. What "
        "works is a LOCAL instance (`c = C(); c.m()`), which uses the contract at the "
        "call site instead of splicing the body. The message now says so and names both "
        "things that do not work."),
}


def literal_parts(node):
    out, stack = [], [node]
    while stack:
        n = stack.pop()
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
        elif isinstance(n, ast.JoinedStr):
            stack.extend(n.values)
        elif isinstance(n, ast.BinOp):
            stack.extend([n.left, n.right])
        elif isinstance(n, ast.Call):
            stack.extend(n.args)
    return out


def sites():
    raises, advice = 0, []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for f in sorted(glob.glob(os.path.join(SRC, "**", "*.py"), recursive=True)):
            try:
                tree = ast.parse(open(f, errors="replace").read())
            except SyntaxError:
                continue
            for n in ast.walk(tree):
                if not isinstance(n, ast.Raise) or not isinstance(n.exc, ast.Call):
                    continue
                nm = getattr(n.exc.func, "id", None) or getattr(n.exc.func, "attr", None)
                if not nm or not str(nm).startswith("PyCSL"):
                    continue
                raises += 1
                msg = " ".join(literal_parts(n.exc))
                if ADVICE.search(msg):
                    advice.append((os.path.relpath(f, ROOT), n.lineno, msg[:90],
                                   sig(n.exc)))
    return raises, advice


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--list-unaudited", action="store_true")
    args = ap.parse_args()

    raises, advice = sites()
    if raises < MIN_SITES:
        print("[!] refusal-advice-audited: REFUSING — only %d raise site(s) found, "
              "expected at least %d. The walk is broken; this is not a pass."
              % (raises, MIN_SITES), file=sys.stderr)
        return 2
    if len(advice) < MIN_ADVICE:
        print("[!] refusal-advice-audited: REFUSING — only %d advice-bearing message(s) "
              "matched, expected at least %d. The matcher is broken; this is not a pass."
              % (len(advice), MIN_ADVICE), file=sys.stderr)
        return 2

    keys = {(f, sg) for f, _ln, _m, sg in advice}
    line_of = {(f, sg): ln for f, ln, _m, sg in advice}
    done = sorted(k for k in keys if k in AUDITED)
    todo = sorted(k for k in keys if k not in AUDITED)
    stale = sorted(k for k in AUDITED if k not in keys)
    by = {}
    for k in done:
        by[AUDITED[k][0]] = by.get(AUDITED[k][0], 0) + 1

    print("[*] refusal-advice-audited: %d raise site(s), %d carry ADVICE; %d audited "
          "(%s), %d not."
          % (raises, len(advice), len(done),
             ", ".join("%s %d" % (k, v) for k, v in sorted(by.items())) or "none",
             len(todo)))

    if args.verbose or args.list_unaudited:
        for f, ln, m, sg in sorted(advice):
            if (f, sg) in AUDITED:
                if args.verbose:
                    print("    %-12s %s:%d" % (AUDITED[(f, sg)][0], f, ln))
            else:
                print("    unaudited    %s:%d  %s" % (f, ln, m[:60]))

    rc = 0
    for f, sg in stale:
        print("[!]   AUDITED ENTRY %s / %r NO LONGER MATCHES an advice-bearing raise. The "
              "message moved or was edited, so its verdict is STALE — re-run the audit "
              "and update the entry, exactly as a message edit invalidates a "
              "refusal-witness census row." % (f, sg), file=sys.stderr)
        rc = 1
    if len(done) < MIN_AUDITED:
        print("[!]   AUDITED COUNT FELL: %d < %d. This may only grow." % (len(done),
              MIN_AUDITED), file=sys.stderr)
        rc = 1

    if rc:
        print("[!] refusal-advice-audited: NOT OK.", file=sys.stderr)
    else:
        print("[+] refusal-advice-audited: OK — %d of %d advice-bearing refusal(s) have "
              "had their advice FOLLOWED and run (floor %d). The rest are unaudited, "
              "which is a debt this plane exists to make visible rather than a failure."
              % (len(done), len(advice), MIN_AUDITED))
    return rc


MIN_AUDITED = 10

if __name__ == "__main__":
    sys.exit(main())
