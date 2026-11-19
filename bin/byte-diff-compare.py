#!/usr/bin/env python3
"""THE BYTE-DIFF COMPARISON, MADE EXECUTABLE — and it fails in the direction that let a
CLOSED SOUNDNESS ROUTE REOPEN.

`bin/byte-diff-sweep.sh` only EMITS a corpus into a directory. Comparing two such
directories has always been an AD-HOC DRIVER PROCEDURE — a shell loop written afresh each
window — and every version of it compared the files present in BOTH directories. That is
the whole bug:

    A file that is REFUSED emits NO `.mlw` at all. It therefore has NO COUNTERPART on the
    baseline side, so a diff-the-common-files sweep reports ZERO CHANGES while a REFUSAL
    HAS SILENTLY BECOME AN EMISSION.

That direction can only ever be a soundness LOSS — a program the emitter used to reject now
gets proved — and it is exactly how route #52 landed on a recorded "corpus byte-diff ZERO
over 887" while reopening route #42. Three of route #42's own negative witnesses went from
REFUSED to PROVING and no plane said a word; it took the first full reference-suite run in
two windows to notice, via the XPASS rule.

So this script reports THREE classes, and by default any of them is a failure:

    MOVED       present both sides, bytes differ      — the classic byte-diff
    GONE        emitted on the baseline, not now      — a new refusal (often intended)
    APPEARED    NOT emitted on the baseline, now is   — A REFUSAL BECAME AN EMISSION

`--expect-moved NAME [...]` whitelists an INTENDED emission change for a named file — a
SOURCE repair rather than an emitter change. A declared name that does not move is an
error too: the repair you think you landed is not in the emission.

`--expect-gone NAME [...]` whitelists an INTENDED new refusal (a route being closed
legitimately removes emissions — route #42's re-closure removes exactly three). There is
deliberately NO `--expect-appeared`: if a refusal becomes an emission you must say so in a
route file and argue it, not pass a flag.

Usage:  bin/byte-diff-compare.py <baseline-dir> <candidate-dir> [--expect-gone N ...]
"""
from __future__ import annotations

import argparse
import filecmp
import os
import sys


def _mlw(d):
    if not os.path.isdir(d):
        print(f"[!] byte-diff-compare: {d} is not a directory. NOT A PASS.", file=sys.stderr)
        sys.exit(2)
    return {f for f in os.listdir(d) if f.endswith(".mlw")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("baseline")
    ap.add_argument("candidate")
    ap.add_argument("--expect-moved", nargs="*", default=[],
                    help="basenames (with or without .mlw) whose emission is INTENDED to "
                         "change — a SOURCE repair, not an emitter change. (#49) gen #31: "
                         "a corpus driver that is not a loadable Python program has to be "
                         "repairable, and repairing its SOURCE moves its .mlw. Naming it "
                         "here is the same contract `--expect-gone` already makes: the "
                         "mover must be declared, one name per file, and a declared name "
                         "that does NOT move is itself an error — the repair you think you "
                         "landed is not in the emission.")
    ap.add_argument("--expect-gone", nargs="*", default=[],
                    help="basenames (with or without .mlw) whose emission is INTENDED to "
                         "disappear, e.g. a route being closed by a new refusal")
    ap.add_argument("--new-source", nargs="*", default=[],
                    help="corpus files ADDED since the baseline was emitted; only needed "
                         "when the baseline directory has no SOURCES.txt manifest")
    ap.add_argument("--min-files", type=int, default=500,
                    help="a gate that cannot tell 'nothing is wrong' from 'I looked at "
                         "nothing' is not a gate (the #44 rule)")
    args = ap.parse_args()

    base, cand = _mlw(args.baseline), _mlw(args.candidate)
    if len(base) < args.min_files:
        print(f"[!] byte-diff-compare: baseline has only {len(base)} .mlw file(s), below "
              f"--min-files {args.min_files}. The sweep is broken, not clean. NOT A PASS.",
              file=sys.stderr)
        return 2

    expect_gone = {n if n.endswith(".mlw") else n + ".mlw" for n in args.expect_gone}

    # A corpus file ADDED since the baseline also "appears", and that is benign. The
    # baseline's SOURCES.txt (written by `byte-diff-sweep.sh`) is what tells the two apart
    # EXACTLY; without it the caller must name the new sources, because guessing here is
    # how the dangerous direction gets waved through.
    base_sources = None
    man = os.path.join(args.baseline, "SOURCES.txt")
    if os.path.isfile(man):
        with open(man, encoding="utf-8") as fh:
            base_sources = {ln.strip()[:-3] for ln in fh if ln.strip().endswith(".py")}
    new_sources = {n[:-3] if n.endswith(".py") else n for n in args.new_source}

    gone = sorted(base - cand)
    appeared = sorted(cand - base)
    if base_sources is not None:
        benign = [n for n in appeared if n[:-4] not in base_sources]
        appeared = [n for n in appeared if n[:-4] in base_sources]
    else:
        benign = [n for n in appeared if n[:-4] in new_sources]
        appeared = [n for n in appeared if n[:-4] not in new_sources]
    moved = sorted(n for n in (base & cand)
                   if not filecmp.cmp(os.path.join(args.baseline, n),
                                      os.path.join(args.candidate, n), shallow=False))

    expect_moved = {n if n.endswith(".mlw") else n + ".mlw" for n in args.expect_moved}
    unexpected_moved = [n for n in moved if n not in expect_moved]
    missing_moved = sorted(expect_moved - set(moved))
    unexpected_gone = [n for n in gone if n not in expect_gone]
    missing_gone = sorted(expect_gone - set(gone))

    print(f"[*] byte-diff-compare: {len(base)} baseline / {len(cand)} candidate .mlw; "
          f"{len(moved)} MOVED ({len(unexpected_moved)} unexpected), "
          f"{len(gone)} GONE ({len(unexpected_gone)} unexpected), "
          f"{len(appeared)} APPEARED"
          + (f", {len(benign)} new source file(s) ignored" if benign else "")
          + ("." if base_sources is not None else " [no SOURCES.txt manifest — new corpus "
             "files must be named with --new-source]."))

    for n in appeared:
        print(f"[!]   APPEARED {n} — a REFUSAL BECAME AN EMISSION. This is the direction "
              f"that reopened route #42: a program the emitter used to reject is now being "
              f"proved. Justify it in a route file or fix the lowering.", file=sys.stderr)
    for n in unexpected_gone:
        print(f"[!]   GONE {n} — it emitted before and does not now. If that is an intended "
              f"new refusal, pass --expect-gone {n[:-4]}.", file=sys.stderr)
    for n in unexpected_moved:
        print(f"[!]   MOVED {n} — if that is an intended SOURCE repair, pass "
              f"--expect-moved {n[:-4]}.", file=sys.stderr)
    for n in missing_moved:
        print(f"[!]   --expect-moved {n[:-4]} was declared but its emission is UNCHANGED. "
              f"The repair you think you landed is not in the emission.", file=sys.stderr)
    for n in missing_gone:
        print(f"[!]   --expect-gone {n[:-4]} was declared but it still emits. The refusal "
              f"you think you landed is NOT firing.", file=sys.stderr)

    if appeared or unexpected_gone or unexpected_moved or missing_gone or missing_moved:
        print("[!] byte-diff-compare: NOT BYTE-INERT.", file=sys.stderr)
        return 1

    if moved or gone:
        print("[+] byte-diff-compare: OK — byte-inert in all three directions apart from "
              "%d DECLARED mover(s) and %d declared refusal(s), each named on the command "
              "line." % (len(moved), len(gone)))
    else:
        print("[+] byte-diff-compare: OK — byte-inert in all three directions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
