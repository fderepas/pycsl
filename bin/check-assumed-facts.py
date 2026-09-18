#!/usr/bin/env python3
r"""EVERY FACT THE MODEL ASSUMES RATHER THAN PROVES — a named, EXECUTABLE ratchet.

THE DEFECT CLASS. A verified program is only as good as the facts its proof rests on that
nobody proved. In the emitted WhyML those are exactly two syntactic forms:

  `assume { P }`   P is taken as true at that program point, unconditionally.
  `axiom  n : P`   P is taken as true everywhere in the module.

Route #187 is what an unreviewed one costs: `#@ fresh_globals` emits
`assume { counter.n = 0 }` — the module-global's CONSTRUCTOR post-state — and the module
body's own `counter.n = 7`, which the IR does not carry at all, made that assumed fact
FALSE of the program. `\result == 0` proved while CPython returned 7.

WHAT THIS PLANE DOES. It reads the shared corpus emission and classifies every `assume`
and every `axiom` into the families this campaign has reviewed:

  CONCURRENT-MUTEX-ENTRY   `assume { lock_<m>_inv <vars> }` — the critical-section entry
                           havoc+assume of the monitor invariant. Sound only with the
                           matching RELEASE obligation, which corpus 0256 (an XFAIL) pins.
  FRESH-GLOBALS-CTOR       `assume { (<g>.<f> = <n>) }` — route #187's constructor
                           post-state. Required to be PROOF-BACKED: the same file must
                           emit the `<g>_fresh_init` function that proves it.
  PROOF-IMPORT             `axiom pycsl_axiom_<Rocq|Lean qualname>` — the `#@ proof`
                           import, audited elsewhere by construction.
  DERIVABLE-LIST-LEMMA     `axiom mem_head : forall x: int, l: list int. mem x (Cons x l)`
                           — a THEOREM of `list.Mem`, redundant rather than assumed.
  HASH-EQ-CONSISTENCY      `axiom hash_eq_consistent_<cls> : forall a b. <cls>_eq_ a b =
                           True -> <cls>_hash_ a = <cls>_hash_ b` — UB-7.2, emitted for any
                           class defining BOTH `__hash__` and `__eq__`. This one is a
                           REVIEWED ASSUMPTION, not a theorem: Python lets a user write an
                           inconsistent pair, and then the axiom is FALSE of the program
                           and the `a == b` branch is contradictory in the model, so any
                           postcondition holds on it. `--strict-hash-eq-consistency` turns
                           it into a goal (corpus 0411 documents both modes). It is not
                           reachable today for an accidental reason worth writing down:
                           every spelling that could satisfy the antecedent — `a == b`,
                           `a.__eq__(b)`, `K.__eq__(a, b)`, even with `other: K` — fails to
                           TYPE, because the model wants an int where the record goes
                           (measured, gen #29). That fence is INCIDENTAL; if the record
                           comparison ever types, this family becomes a live route.

Anything else is UNCLASSIFIED and FAILS. A new assumed-fact family is exactly the thing
that must not arrive without a route review, and the census that found route #187's was
done by hand; this is that census, executable.

WHAT IT DOES NOT CHECK, stated so nobody reads more into a green run than is there: it
does not audit the CONTENT of a classified fact (whether a given `#@ proof` theorem really
says what its name claims is the audit's job, and whether a mutex invariant is
re-established at release is `0256`'s job) — only that no fact outside the reviewed
families has appeared. Nor does it see `val` declarations: a bodyless `val` with an
`ensures` is also an assumption, and the planes that watch those are
`count-trusted-directives.py` and `check-untrusted-emitted.py`.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSUME_FAMILIES = [
    ("CONCURRENT-MUTEX-ENTRY", re.compile(r"^assume \{ lock_[A-Za-z0-9_]+_inv[ !A-Za-z0-9_]*\}$")),
    ("FRESH-GLOBALS-CTOR", re.compile(r"^assume \{ \([A-Za-z0-9_]+\.[A-Za-z0-9_]+ = -?\d+\) \}$")),
]
AXIOM_FAMILIES = [
    ("PROOF-IMPORT", re.compile(r"^axiom pycsl_axiom_[A-Za-z0-9_']+ ")),
    ("DERIVABLE-LIST-LEMMA",
     re.compile(r"^axiom mem_head : forall x: int, l: list int\. mem x \(Cons x l\)$")),
    ("HASH-EQ-CONSISTENCY",
     re.compile(r"^axiom hash_eq_consistent_[A-Za-z0-9_]+ ?: forall a b: [A-Za-z0-9_]+\. ")),
]


def classify(line, families):
    for name, rx in families:
        if rx.match(line):
            return name
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", default=None,
                    help="a directory of already-emitted .mlw files (the shared sweep)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    emit = args.emit_dir
    tmp = None
    if not emit:
        tmp = tempfile.mkdtemp(prefix="assumedfacts_")
        emit = tmp
        rc = subprocess.run([os.path.join(ROOT, "bin", "byte-diff-sweep.sh"), emit],
                            cwd=ROOT, capture_output=True, text=True).returncode
        if rc != 0:
            print("[!] assumed-facts: the emission sweep failed (rc=%d); that is not a "
                  "measurement. NOT A PASS." % rc, file=sys.stderr)
            return 2

    mlws = []
    for dp, _dn, fns in os.walk(emit):
        for fn in fns:
            if fn.endswith(".mlw"):
                mlws.append(os.path.join(dp, fn))
    if not mlws:
        print("[!] assumed-facts: 0 emitted .mlw file(s) under %s — that is not a "
              "measurement. NOT A PASS." % emit, file=sys.stderr)
        return 2

    counts = {}
    unclassified = []
    unbacked = []
    for path in mlws:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for raw in text.splitlines():
            line = raw.strip().rstrip(";")
            if line.startswith("assume {"):
                fam = classify(line, ASSUME_FAMILIES)
                if fam is None:
                    unclassified.append((path, line))
                    continue
                counts[fam] = counts.get(fam, 0) + 1
                if fam == "FRESH-GLOBALS-CTOR":
                    # PROOF-BACKED OR NOT AT ALL: the constructor post-state is admissible
                    # only because the same file emits the function that proves it.
                    g = line.split("{", 1)[1].strip().lstrip("(").split(".", 1)[0]
                    if ("let %s_fresh_init" % g) not in text:
                        unbacked.append((path, line))
            elif line.startswith("axiom "):
                fam = classify(line, AXIOM_FAMILIES)
                if fam is None:
                    unclassified.append((path, line))
                else:
                    counts[fam] = counts.get(fam, 0) + 1

    total = sum(counts.values())
    print("[*] assumed-facts: %d emitted file(s), %d assumed fact(s) — %s."
          % (len(mlws), total,
             ", ".join("%d %s" % (v, k) for k, v in sorted(counts.items())) or "none"))
    if args.verbose:
        for k, v in sorted(counts.items()):
            print("    %-24s %d" % (k, v))

    rc = 0
    for path, line in unclassified:
        print("[!] assumed-facts: an UNCLASSIFIED assumed fact in %s:\n        %s\n"
              "    A new assumed-fact family is a TCB change. Review it as a route, then "
              "add its family here." % (path, line), file=sys.stderr)
        rc = 1
    for path, line in unbacked:
        print("[!] assumed-facts: the fresh-globals fact in %s is NOT proof-backed — no "
              "`_fresh_init` function in the same file proves it:\n        %s"
              % (path, line), file=sys.stderr)
        rc = 1
    if rc == 0:
        print("[+] assumed-facts: OK — every assumed fact is in a reviewed family; "
              "%d fresh-globals fact(s), each proof-backed."
              % counts.get("FRESH-GLOBALS-CTOR", 0))
    return rc


if __name__ == "__main__":
    sys.exit(main())
