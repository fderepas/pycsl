#!/usr/bin/env python3
"""check-mirror-loop-annotations.py — a RATCHET on the self-annotation mirror's
in-body proof-support directives.

WHY THIS EXISTS (driver window 3, relaunch #44). Route #21's mirror sync copied the
LIVE emitter body over the mirror body — the documented "copy the BODY, keep the
mirror's SIGNATURE" procedure — and thereby DELETED nine `#@ loop invariant` /
`#@ loop variant` lines from `stmt_control_flow._handle_try_stmt`'s three `while`
loops.  The live emitter carries no `#@` annotations, so a verbatim body copy strips
the mirror's silently.

THE POINT IS *WHICH* PLANE CAUGHT IT, AND HOW LATE:

    check-self-annotate-sync.sh   GREEN  — it compares bodies MODULO annotations,
                                           which is precisely why the copy looked right
    self-annotate-mirror-check.sh GREEN  — no def appeared or disappeared
    L3 typecheck                  GREEN  — an invariant is not a type
    byte-diff (both corpora)      GREEN  — no LIVE file was touched at all
    check-emitted-vacuity.py      GREEN  — nothing became vacuous
    count-trusted-directives.py   GREEN  — no `\trusted` marker moved
    the WHOLE-FILE PROOF          RED    — and only after ~30 minutes of prover time

Every cheap plane is blind to a deleted invariant, because each of them measures a
property an annotation does not participate in.  Only the most expensive plane in the
battery can see it.  This script is the cheap plane: it runs in well under a second
and fires on exactly the deletion the proof would have found half an hour later.

THE RATCHET DIRECTION.  A `#@ loop invariant` / `#@ loop variant` line is pure
proof-support: it constrains nothing about the emitter's behaviour and is never a
liability.  Adding one is progress; a file's count going DOWN is either

  (a) the defect above — an annotation stripped by a body copy; or
  (b) a deliberate act: the loop was deleted, or its enclosing function became
      `\trusted` (a `\trusted` body is never lowered, so its invariants are dead).

(b) is rare and intentional, so it pays for a baseline update; (a) is silent and
costly, so it must fail loudly.  Hence: per-file floors, `--update` to re-baseline.

USAGE
    bin/check-mirror-loop-annotations.py            # check against the baseline
    bin/check-mirror-loop-annotations.py --update   # re-baseline (deliberate drops)
    bin/check-mirror-loop-annotations.py --list     # print current per-file counts

EXIT 0 = every file at or above its floor.  EXIT 1 = a file dropped.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
BASELINE = os.path.join(ROOT, "getting-better", "mirror-loop-annotations.json")

# The directive kinds that live INSIDE a function body, and are therefore the ones a
# verbatim body copy from the live emitter can strip. A contract clause
# (`requires`/`ensures`/`assigns`) sits ABOVE the `def` and survives a body copy; these
# do not. All of them are pure proof support: they change no emitted behaviour, so
# their count may rise freely and a fall is always worth a look.
IN_BODY_KINDS = (
    "loop invariant",   # the route-#21 casualty
    "loop variant",
    "assert",           # prove-and-assume (4 live ones in frontend/pure_ast.py)
    "check",            # prove-and-discard
    "reveal",           # opt into a callee's definition contract at this site
    "label",            # program-point annotation
    "ghost",            # ghost declarations/updates
)


def count_file(path):
    """Count `#@ loop invariant` / `#@ loop variant` directive lines in one file."""
    n = 0
    with open(path, errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if not s.startswith("#@"):
                continue
            body = s[2:].strip()
            for kind in IN_BODY_KINDS:
                if body == kind or body.startswith(kind + " "):
                    n += 1
                    break
    return n


def measure():
    """Per-file counts, keyed by path relative to the mirror root. Files with zero
    are omitted — a file that never had any cannot regress, and listing 300 zeros
    would bury the signal."""
    out = {}
    for root, _dirs, files in os.walk(MIRROR):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            p = os.path.join(root, fn)
            n = count_file(p)
            if n:
                out[os.path.relpath(p, MIRROR)] = n
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update", action="store_true",
                    help="rewrite the baseline from the current tree (deliberate drops)")
    ap.add_argument("--list", action="store_true", help="print current per-file counts")
    args = ap.parse_args()

    cur = measure()
    total = sum(cur.values())

    if args.list:
        for k in sorted(cur):
            print(f"{cur[k]:4d}  {k}")
        print(f"{total:4d}  TOTAL ({len(cur)} files)")
        return 0

    if args.update or not os.path.exists(BASELINE):
        with open(BASELINE, "w") as fh:
            json.dump({"_total": total, "files": cur}, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print(f"[+] baseline written: {total} loop-annotation lines across "
              f"{len(cur)} mirror files")
        return 0

    with open(BASELINE) as fh:
        base = json.load(fh)
    floors = base["files"]

    drops = []
    for path, floor in sorted(floors.items()):
        now = cur.get(path, 0)
        if now < floor:
            drops.append((path, floor, now))

    gains = [(p, floors.get(p, 0), n) for p, n in sorted(cur.items())
             if n > floors.get(p, 0)]

    for path, floor, now in gains:
        print(f"[+] {path}: {floor} -> {now} (gain — re-baseline with --update)")

    if drops:
        print(f"[-] MIRROR LOOP ANNOTATIONS DROPPED in {len(drops)} file(s):")
        for path, floor, now in drops:
            print(f"      {path}: {floor} -> {now}   ({floor - now} line(s) LOST)")
        print("[-] An in-body proof-support directive is never a liability.")
        print("    A drop is either a body copy that stripped the mirror's own")
        print("    annotations (the route-#21 defect) or a deliberate `\\trusted`")
        print("    conversion / loop deletion. If deliberate, re-run with --update.")
        return 1

    print(f"[+] mirror loop annotations: {total} lines across {len(cur)} files, "
          f"every file at or above its floor")
    return 0


if __name__ == "__main__":
    sys.exit(main())
