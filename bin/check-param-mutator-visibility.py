#!/usr/bin/env python3
r"""IN-PLACE MUTATION OF A COLLECTION **PARAMETER** — a named, EXECUTABLE ratchet.

THE DEFECT CLASS. Python passes a list, dict or set argument BY REFERENCE, so a mutation
inside the callee is visible to the caller. A lowering has exactly three honest answers:

  CALLER-VISIBLE  the callee gets a real mutation frame and the caller sees the change.
  REFUSED         the pipeline raises with a diagnostic — fail-CLOSED, and the honest
                  answer for a shape with no sound lowering.
  DROPPED         the callee mutates a LOCAL COPY, carries no `writes` clause, and the
                  caller therefore PROVES the collection unchanged. **This is the ratchet,
                  and it is a fail-OPEN: the mutation is not merely un-modelled, it is
                  modelled as ABSENT.**

ROUTE #49 was TWO cells of this table and both are now CLOSED. `a.append(x)` on a list
PARAMETER was DROPPED — `g(a);
return len(a)` proved `\result == 0` where Python returns 1 — while its four siblings
`pop` / `insert` / `clear` / `extend` were already REFUSED and the element write `a[0] = v`
and dict write `d[k] = v` were already CALLER-VISIBLE. Nothing in the campaign made that
asymmetry visible: `bin/check-dropped-mutation.py`'s population is Module 5's
ASSIGNMENT-family statements (a statement that produces no IR at all), and route #49's
statement IS in the IR — it is the LOWERING that writes a copy. The two planes are disjoint
by construction, which is why this one exists.

HOW IT MEASURES, and why it is EXECUTABLE rather than static. The answer is not readable
off the source: it depends on seq-promotion, on `_stmt_seq_mut_params`, on
`_mutated_collection_params` and on which branch of a long `if`-chain a receiver reaches.
So the plane GENERATES, for each (receiver type, mutator) pair, a two-function driver in
which the callee mutates the parameter and the caller asserts the collection is UNCHANGED —
a contract that is FALSE of the program — and runs the real pipeline on it:

    pipeline raises            -> REFUSED         (fail-closed)
    verification SUCCEEDS      -> DROPPED         (a false contract proved: A FINDING)
    verification FAILS         -> CALLER-VISIBLE  (the model does not decide it away)

A DROPPED cell not in the baseline is a failure. So is a baseline entry whose cell has
changed answer, and so is a baseline entry that no longer matches any cell — a baseline
that outlives its site hides the next one.

WHAT IT DOES NOT CHECK, stated so nobody reads more into a green run than is there: only
the SHAPES BELOW, only through a plain function call, and only with the collection reaching
the callee as a bare parameter. A mutation through a nested data structure, through a
method on `self`, or through an alias bound inside the callee is outside this table.
`bin/check-dropped-mutation.py` covers the Module-5 statement side; this covers the Module-6
lowering side for the shapes it names.
"""
import argparse
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")

# (receiver-annotation, mutator-call, caller precondition, caller body tail, expected-false
#  postcondition).  Each driver's postcondition is FALSE of the program: it asserts the
#  collection is UNCHANGED after a call that mutates it.
CASES = [
    ("list", "a.append(1)",   "\\length(a) == 2", "return len(a)", "\\result == 2"),
    ("list", "a.pop()",       "\\length(a) == 2", "return len(a)", "\\result == 2"),
    ("list", "a.insert(0, 1)", "\\length(a) == 2", "return len(a)", "\\result == 2"),
    ("list", "a.clear()",     "\\length(a) == 2", "return len(a)", "\\result == 2"),
    ("list", "a.extend([1])", "\\length(a) == 2", "return len(a)", "\\result == 2"),
    ("list", "a.remove(1)",   "\\length(a) == 2", "return len(a)", "\\result == 2"),
    ("list", "a[0] = 99",     "\\length(a) > 0 and a[0] == 1", "return a[0]", "\\result == 1"),
    ("dict", "a[1] = 5",      "True", "return a[1]", "\\result == 0"),
    ("set",  "a.add(3)",      "True", "return 1 if 3 in a else 0", "\\result == 0"),
    ("set",  "a.discard(3)",  "True", "return 1 if 3 in a else 0", "\\result == 1"),
    # (#48) the second batch, added in the same window the plane was written: the
    # remaining ordinary mutators of each receiver type. A table with four cells is a
    # sample; a table with seventeen is a census of the surface Python programs actually
    # use, and the cost is one pipeline run per cell.
    ("list", "a.sort()",      "\\length(a) == 2", "return len(a)", "\\result == 2"),
    ("list", "a.reverse()",   "\\length(a) == 2", "return len(a)", "\\result == 2"),
    ("list", "a += [1]",      "\\length(a) == 2", "return len(a)", "\\result == 2"),
    ("dict", "a.update({1: 5})", "True", "return a[1]", "\\result == 0"),
    ("dict", "a.pop(1)",      "True", "return a[1]", "\\result == 0"),
    ("dict", "a.setdefault(1, 5)", "True", "return a[1]", "\\result == 0"),
    ("dict", "del a[1]",      "True", "return a[1]", "\\result == 0"),
    ("set",  "a.update({3})", "True", "return 1 if 3 in a else 0", "\\result == 0"),
    ("set",  "a.remove(3)",   "True", "return 1 if 3 in a else 0", "\\result == 1"),
    ("set",  "a.clear()",     "True", "return 1 if 3 in a else 0", "\\result == 1"),
]

DRIVER = '''_ = 0  # anchor
#@ requires True
#@ ensures True
#@ assigns a
def g(a: {ann}) -> None:
    {mut}

#@ requires {pre}
#@ ensures {post}
#@ assigns a
def f(a: {ann}) -> int:
    g(a)
    {tail}
'''

# ---------------------------------------------------------------------------
# THE BASELINE.  (receiver, mutator) -> the answer this gate expects.
# A cell whose answer differs, a DROPPED cell that is not recorded here, or an entry
# with no matching cell, is a FAILURE.
# ---------------------------------------------------------------------------
BASELINE = {
    ("list", "a.append(1)"):    "REFUSED",
    ("list", "a.pop()"):        "REFUSED",
    ("list", "a.insert(0, 1)"): "REFUSED",
    ("list", "a.clear()"):      "REFUSED",
    ("list", "a.extend([1])"):  "REFUSED",
    ("list", "a.remove(1)"):    "REFUSED",
    ("list", "a[0] = 99"):      "CALLER-VISIBLE",
    ("dict", "a[1] = 5"):       "CALLER-VISIBLE",
    ("set",  "a.add(3)"):       "CALLER-VISIBLE",
    ("set",  "a.discard(3)"):   "CALLER-VISIBLE",
    ("list", "a.sort()"):       "REFUSED",
    ("list", "a.reverse()"):    "REFUSED",
    ("list", "a += [1]"):       "REFUSED",
    ("dict", "a.update({1: 5})"):   "REFUSED",
    ("dict", "a.pop(1)"):       "REFUSED",
    ("dict", "a.setdefault(1, 5)"): "REFUSED",
    ("dict", "del a[1]"):       "CALLER-VISIBLE",
    ("set",  "a.update({3})"):  "REFUSED",
    ("set",  "a.remove(3)"):    "CALLER-VISIBLE",
    ("set",  "a.clear()"):      "REFUSED",
}


def classify(ann, mut, pre, tail, post, keep):
    src = DRIVER.format(ann=ann, mut=mut, pre=pre, post=post, tail=tail)
    fd, path = tempfile.mkstemp(suffix=".py", prefix="mutvis_", dir=keep)
    with os.fdopen(fd, "w") as fh:
        fh.write(src)
    try:
        out = subprocess.run(
            [sys.executable, PYCSL, path],
            capture_output=True, text=True, timeout=600).stdout
    except subprocess.TimeoutExpired:
        return "TIMEOUT", path
    if "PIPELINE ERROR" in out or "ERROR:" in out:
        return "REFUSED", path
    if "Verification SUCCESS" in out:
        return "DROPPED", path
    return "CALLER-VISIBLE", path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--keep-dir", default=None,
                    help="write the generated drivers here instead of a temp dir")
    args = ap.parse_args()

    keep = args.keep_dir or tempfile.mkdtemp(prefix="mutvis_")
    os.makedirs(keep, exist_ok=True)

    results = []
    for ann, mut, pre, tail, post in CASES:
        verdict, path = classify(ann, mut, pre, tail, post, keep)
        results.append((ann, mut, verdict, path))

    if not results:
        print("[!] param-mutator-visibility: 0 case(s) — that is not a measurement. "
              "NOT A PASS.", file=sys.stderr)
        return 2

    dropped = [r for r in results if r[2] == "DROPPED"]
    changed = [r for r in results
               if BASELINE.get((r[0], r[1])) not in (None, r[2])]
    unknown = [r for r in results if (r[0], r[1]) not in BASELINE]
    stale = sorted(set(BASELINE) - {(r[0], r[1]) for r in results})

    print("[*] param-mutator-visibility: %d case(s) — %d CALLER-VISIBLE, %d REFUSED, "
          "%d DROPPED." % (len(results),
                           sum(1 for r in results if r[2] == "CALLER-VISIBLE"),
                           sum(1 for r in results if r[2] == "REFUSED"),
                           len(dropped)))
    if args.verbose or dropped or changed or unknown:
        for ann, mut, verdict, _p in results:
            exp = BASELINE.get((ann, mut), "(not baselined)")
            mark = "    " if exp == verdict else "CHG "
            print("    %s%-5s %-16s -> %-15s baseline %s"
                  % (mark, ann, mut, verdict, exp))

    rc = 0
    for ann, mut, verdict, path in changed:
        print("[!] param-mutator-visibility: %s `%s` is now %s, baseline says %s. If it "
              "became DROPPED, a mutation the caller must see is now modelled as ABSENT — "
              "read the generated driver at %s and probe it end to end."
              % (ann, mut, verdict, BASELINE[(ann, mut)], path), file=sys.stderr)
        rc = 1
    for ann, mut, verdict, path in unknown:
        print("[!] param-mutator-visibility: %s `%s` -> %s has no baseline entry. Classify "
              "it (driver at %s)." % (ann, mut, verdict, path), file=sys.stderr)
        rc = 1
    for ann, mut in stale:
        print("[!] param-mutator-visibility: baseline entry (%s, %s) matches no case. "
              "Remove it — a baseline that outlives its site hides the next one."
              % (ann, mut), file=sys.stderr)
        rc = 1
    if rc == 0:
        # Report the DROPPED count in the GREEN line too. A gate whose pass message says
        # "0 dropped" while its own table shows one is a gate that reads as safer than it
        # is — the campaign's own lesson that counting a drop is not establishing it is
        # safe, applied to the gate's own prose.
        print("[+] param-mutator-visibility: OK — %d case(s), every one at its baseline; "
              "%d DROPPED, %s." % (
                  len(results), len(dropped),
                  "each one recorded as an OPEN route in getting-better/open-routes/"
                  if dropped else "none"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
