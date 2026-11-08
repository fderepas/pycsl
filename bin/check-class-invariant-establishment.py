#!/usr/bin/env python3
r"""L-PLANE ORACLE: is every corpus `#@ class invariant` TRUE of the object its own
constructor builds? Measured under CPython, not argued.

WHY THIS EXISTS. ROUTE #226 is "a `#@ class invariant` the CONSTRUCTOR never establishes is
assumed by every method". The emitter now emits the constructor's obligation as
`goal _check_class_inv_<C>` — but only where it can be STATED exactly: a paramless
`__init__` storing int literals. THREE shapes stay open by design:

    a field from an `__init__` PARAMETER      `def __init__(self, n): self.n = n`
    a COMPUTED or control-flow store          `self.n = three()`, or a store inside an `if`
    a `@dataclass` with field defaults        `n: int = 0` under `invariant self.n >= 5`

All three are RUNNABLE. Construct the object and evaluate the invariant on it. This plane is
the executable oracle for exactly the part of route #226 the emitter cannot state, and it is
free: it needs no drivers, only the corpus that is already there.

WHAT A FAILURE HERE MEANS, and it is the same verdict as `check-corpus-contract-truth`'s: a
class whose own declared invariant is FALSE of the object its own `__init__` produces, in a
file the suite calls green. Every method of that class is verified under an assumption no
instance satisfies.

FIRST MEASUREMENT (gen #31): 75 C()-constructible PASS-expected classes across both corpora,
84 evaluable clauses, **0 FALSE**, 3 clauses not evaluable here. So the corpus is clean —
which is the result, and the point is that nothing had been measuring it.

SENSITIVITY, because a green corpus proves REACH and not SENSITIVITY. Pointed at a directory
holding one file per open shape, it reports all three FALSE:

    FALSE  zz1.py  C  ->  self.n >= 5     (paramless literal — the closed shape)
    FALSE  zz2.py  D  ->  self.n >= 5     (@dataclass)
    FALSE  zz3.py  E  ->  self.n >= 5     (computed)

WHAT IT DOES NOT CHECK. A class whose `__init__` REQUIRES an argument has no canonical
instance to test, so it is skipped rather than constructed with a guess — `C(0)` and `C(9)`
are different programs and neither is "the" object. That shape's obligation is
`forall <params>. <inv>` and belongs in the emitter (route #226 increment 2), not here.
Clauses using quantifiers, `\\old`, `\\result` or operators this file does not translate are
counted and reported, never silently dropped.

THE POPULATION GUARD (the #44 rule). A gate of this shape is trivially satisfiable by
evaluating nothing, so it REFUSES (rc=2) if fewer than MIN_CHECKED clauses actually
evaluate.

Usage:  bin/check-class-invariant-establishment.py [--verbose]
"""
import argparse
import ast
import contextlib
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPORA = [os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference"),
           os.path.join(ROOT, "test-suite", "corpus", "python-reference")]
MIN_CHECKED = 75     # first measurement 84 clauses across both corpora; they only grow


def invariants_above(lines, lineno):
    """The `#@ class invariant` lines attached to the class at `lineno`.

    Walks UPWARD and stops at the first line that is not a `#@` directive, a decorator, or
    blank — so a decorator between the block and the `class` keyword does not hide it, and
    the block above the PREVIOUS definition cannot answer for this one."""
    out = []
    i = lineno - 2
    while i >= 0:
        t = lines[i].strip()
        if t.startswith("#@ class invariant"):
            out.append(t[len("#@ class invariant"):].strip())
            i -= 1
        elif t.startswith("#@") or t.startswith("@") or t == "":
            i -= 1
        else:
            break
    return out


def to_python(expr):
    """The contract sublanguage this plane can evaluate, or None.

    `\\length(x)` is `len(x)` and `&&`/`||` are `and`/`or`. Anything still carrying a
    backslash operator, an implication, or a quantifier is REFUSED rather than guessed at —
    a plane that mistranslates a clause reports a false route, which is worse than
    reporting a gap."""
    e = re.sub(r"\\length\(([^()]*)\)", r"len(\1)", expr)
    e = e.replace("&&", " and ").replace("||", " or ")
    if "\\" in e or "==>" in e or "forall" in e or "exists" in e:
        return None
    return e


def candidates():
    rows = []
    files = []
    for c in CORPORA:
        files += sorted(glob.glob(os.path.join(c, "*.py")))
        files += sorted(glob.glob(os.path.join(c, "**", "*.py"), recursive=True))
    for f in sorted(set(files)):
        src = open(f, errors="replace").read()
        if "# pycsl-expected: FAIL" in src or "#@ class invariant" not in src:
            continue
        lines = src.split("\n")
        try:
            tree = ast.parse(src)
        except Exception:
            continue
        for cls in ast.walk(tree):
            if not isinstance(cls, ast.ClassDef):
                continue
            ivs = invariants_above(lines, cls.lineno)
            if not ivs:
                continue
            init = next((x for x in cls.body
                         if isinstance(x, ast.FunctionDef) and x.name == "__init__"), None)
            if init is not None:
                need = (len(init.args.args) + len(init.args.posonlyargs)
                        - len(init.args.defaults))
                if need > 1 or init.args.kwonlyargs or init.args.vararg:
                    continue
            rows.append((f, cls.name, ivs))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    rows = candidates()
    ok = 0
    false = []
    skipped = []
    unconstructible = []
    for f, cname, ivs in rows:
        src = open(f, errors="replace").read()
        ns = {"__name__": "class_invariant_probe"}
        d = os.path.dirname(f)
        sys.path.insert(0, d)
        try:
            with contextlib.redirect_stdout(io.StringIO()), \
                 contextlib.redirect_stderr(io.StringIO()):
                exec(compile(src, f, "exec"), ns)
                obj = ns[cname]()
        except Exception as e:
            unconstructible.append((os.path.basename(f), cname, type(e).__name__))
            continue
        finally:
            if sys.path and sys.path[0] == d:
                sys.path.pop(0)
        for iv in ivs:
            e = to_python(iv)
            if e is None:
                skipped.append((os.path.basename(f), cname, iv, "not translatable"))
                continue
            try:
                val = eval(e, {"__builtins__": {"len": len, "abs": abs}},  # noqa: S307
                           {"self": obj})
            except Exception as ex:
                skipped.append((os.path.basename(f), cname, iv, type(ex).__name__))
                continue
            if val:
                ok += 1
                if args.verbose:
                    print("    ok  %s::%s  %s" % (os.path.basename(f), cname, iv))
            else:
                false.append((os.path.basename(f), cname, iv))

    print("[*] class-invariant-establishment: %d C()-constructible class(es) — %d clause(s) "
          "TRUE of the constructed object, %d FALSE, %d not evaluable, %d class(es) not "
          "constructible."
          % (len(rows), ok, len(false), len(skipped), len(unconstructible)))
    if args.verbose:
        for s in skipped:
            print("    skipped  %s::%s  %s  (%s)" % s)
        for u in unconstructible:
            print("    unconstructible  %s::%s (%s)" % u)

    if ok + len(false) < MIN_CHECKED:
        print("[!] class-invariant-establishment: REFUSING — only %d clause(s) actually "
              "evaluated, expected at least %d. A gate that cannot tell 'nothing is wrong' "
              "from 'I evaluated nothing' is not a gate."
              % (ok + len(false), MIN_CHECKED), file=sys.stderr)
        return 2

    if false:
        for b in false:
            print("[!]   INVARIANT FALSE OF ITS OWN CONSTRUCTOR: %s::%s declares "
                  "`#@ class invariant %s`, and the object `%s()` builds does not satisfy "
                  "it" % (b[0], b[1], b[2], b[1]), file=sys.stderr)
        print("[!] class-invariant-establishment: NOT OK — every method of such a class is "
              "verified under an assumption no instance satisfies. That is ROUTE #226, in a "
              "file the suite calls green.", file=sys.stderr)
        return 1

    print("[+] class-invariant-establishment: OK — every evaluable corpus class invariant "
          "is true of the object its own constructor builds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
