#!/usr/bin/env python3
r"""verified-fraction.py — the BODY-VERIFIED FRACTION OF THE LIVE VERIFIER, computed from
PROOF VERDICTS rather than from the absence of a `\trusted` marker.

WHY THIS EXISTS, AND WHY IT DOES NOT AGREE WITH THE NUMBER IT REPLACES.

`ideas-for-convergence-metric.md` §3.5 publishes `914 / 3236 = 28.2 %` and computes the
numerator as `mirror defs - markers` = `1373 - 459 = 914`. That treats **absence of a
`\trusted` marker as evidence of proof**. It is not. An unmarked mirror def is verified only
if its file's whole-file proof actually RAN and returned rc=0 with zero non-Valid goals. A
file never proved, or proved before the emitter that lowers it last changed, contributes
unmarked defs that NOBODY HAS VERIFIED -- and 28.2 % counts every one of them as verified.

That is structurally route #94 (*a guard whose population is empty has checked nothing and
looks exactly like a guard that passed*) and it is the campaign's own vacuity rule, applied
to the campaign's own headline metric.

WHAT THIS REPORTS -- THREE NUMBERS, NEVER ONE:
  1. verified / live      defs inside mirror files that HAVE a fresh passing whole-file
                          proof on record, over all live `src/pycsl` defs.
  2. unproven-perimeter   defs inside mirror files with NO proof on record, or a STALE one.
                          These are NOT verified and are NOT counted in (1)'s numerator.
  3. (MAX_UNMIRRORED_DEFS, MAX_UNMIRRORED_FILES) from check-mirror-coverage.py -- the
                          live defs that have no mirror at all. THE FALSIFICATION GUARD:
                          the fraction must never be allowed to rise because live defs were
                          deleted or moved to an unmirrored file, so these must not rise in
                          the same commit.
plus THE DATE OF THE OLDEST PROOF RELIED ON. A fraction whose tree you cannot establish is
inherited, not measured -- the battery rule applies to this metric exactly as to a gate.

STALENESS. A proof is a verdict about the `.mlw` the emitter produced from a mirror file at
a point in time. It goes stale when that mirror file changes, or when the emitter that
lowers it changes. Two rules are computed and BOTH are printed, because they bound the
answer from opposite sides and neither alone is honest:
  --staleness=file    (default) the proof must postdate the last commit touching the mirror
                      file AND the last commit touching its live `src/pycsl` counterpart.
  --staleness=strict  the proof must postdate the last commit touching ANY of `src/pycsl`.
                      The emitter is one program; a change anywhere in it can move any
                      file's emission. This is the defensible floor and it is brutal.

Usage: bin/verified-fraction.py [--staleness=file|strict|none] [--json] [--per-file]
"""
from __future__ import annotations

import ast
import datetime
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src/self-annotate/src")
LIVE = os.path.join(ROOT, "src/pycsl")
MARKER = re.compile(r"^#@\s*\\trusted\b")

# Directories holding whole-file proof records (a `<slug>.log` beside a `<slug>.rc`).
# `scratchpad/w7/base` and `scratchpad/w8/pre` are GITLINKED SNAPSHOTS OF THE WHOLE REPO --
# their proof dirs are copies, and counting them would double-count evidence.
PROOF_GLOBS = [
    "getting-better/proofs49/*.log",
    "getting-better/proofs48/*.log",
    "getting-better/proofs46/*.log",
    "scratchpad/w4/proofs/*.log",
    "scratchpad/w5/proofs/*.log",
    "scratchpad/w7/proofs/*.log",
    "scratchpad/w9/*.log",
]
SUCCESS = "[+] Verification SUCCESS! All contracts formally proven."
TARGET_RE = re.compile(r"Parsing and Semantic Analysis for '([^']+)'")

# A NON-VALID GOAL LINE. The pipeline prints a per-goal verdict; anything that is not
# `Valid` means the file did not fully prove. The SUCCESS banner already implies zero
# non-Valid goals, but it is checked independently so that a banner printed by a future
# code path cannot alone carry the verdict.
NONVALID_RE = re.compile(r"\b(Timeout|Unknown|Invalid|Failure|StepLimitExceeded|OutOfMemory)\b")


def _defs(path: str) -> int:
    """Number of `def`s in a file, by AST (not grep): matches the mirror/live comparison
    the metric needs and is blind to docstrings and contract text."""
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except SyntaxError:
        return 0
    return sum(1 for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))


def _markers(path: str) -> int:
    return sum(1 for ln in open(path, encoding="utf-8", errors="replace")
               if MARKER.match(ln.strip()))


def _git_last_commit_epoch(paths) -> int:
    """Committer epoch of the last commit touching any of `paths`, or 0."""
    args = ["git", "-C", ROOT, "log", "-1", "--format=%ct", "--"] + list(paths)
    out = subprocess.run(args, capture_output=True, text=True).stdout.strip()
    return int(out) if out.isdigit() else 0


def collect_proofs():
    """{mirror_relpath: [ {slug, rc, ok, epoch, nonvalid} ]} over every proof record."""
    found = {}
    for g in PROOF_GLOBS:
        for log in sorted(glob.glob(os.path.join(ROOT, g))):
            base = log[:-4]
            rcf = base + ".rc"
            txt = open(log, encoding="utf-8", errors="replace").read()
            m = TARGET_RE.search(txt)
            if not m:
                continue
            tgt = m.group(1)
            if "src/self-annotate/" not in tgt:
                continue
            tgt = tgt[tgt.index("src/self-annotate/"):]
            rc_raw = open(rcf).read().strip() if os.path.exists(rcf) else None
            rc = None
            if rc_raw is not None:
                mm = re.search(r"(-?\d+)", rc_raw)
                rc = int(mm.group(1)) if mm else None
            ok = SUCCESS in txt
            # zero non-Valid goals, checked independently of the banner
            tail = txt[txt.rindex(SUCCESS):] if ok else txt
            nonvalid = bool(NONVALID_RE.search(tail)) if not ok else False
            found.setdefault(tgt, []).append({
                "slug": os.path.basename(base), "rc": rc, "ok": ok,
                "epoch": int(os.path.getmtime(log)), "nonvalid": nonvalid,
                "log": os.path.relpath(log, ROOT),
            })
    return found


def main() -> int:
    argv = sys.argv[1:]
    mode = "file"
    for a in argv:
        if a.startswith("--staleness="):
            mode = a.split("=", 1)[1]
    want_json = "--json" in argv
    per_file = "--per-file" in argv

    mirror_files = sorted(glob.glob(os.path.join(MIRROR, "**/*.py"), recursive=True))
    live_files = sorted(glob.glob(os.path.join(LIVE, "**/*.py"), recursive=True))
    if len(mirror_files) < 40:
        print("[!] verified-fraction: REFUSING — only %d mirror .py files. "
              "THIS IS A REFUSAL, NOT A PASS." % len(mirror_files))
        return 2

    live_defs = sum(_defs(p) for p in live_files)
    proofs = collect_proofs()
    strict_epoch = _git_last_commit_epoch(["src/pycsl"])

    rows, verified, unproven, mirror_defs_total, markers_total = [], 0, 0, 0, 0
    oldest_relied = None
    for p in mirror_files:
        rel = os.path.relpath(p, ROOT)
        d, mk = _defs(p), _markers(p)
        mirror_defs_total += d
        markers_total += mk
        live_counterpart = rel.replace("src/self-annotate/src/", "src/pycsl/")
        if mode == "none":
            floor = 0
        elif mode == "strict":
            floor = strict_epoch
        else:
            floor = max(_git_last_commit_epoch([rel]),
                        _git_last_commit_epoch([live_counterpart]))
        cands = [c for c in proofs.get(rel, [])
                 if c["rc"] == 0 and c["ok"] and not c["nonvalid"]]
        fresh = [c for c in cands if c["epoch"] >= floor]
        best = max(fresh, key=lambda c: c["epoch"]) if fresh else None
        if best:
            verified += max(d - mk, 0)
            if oldest_relied is None or best["epoch"] < oldest_relied:
                oldest_relied = best["epoch"]
            status = "PROVED"
        else:
            unproven += d
            status = ("STALE" if cands else
                      ("FAILED" if proofs.get(rel) else "NO-PROOF"))
        rows.append({"file": rel, "defs": d, "markers": mk, "status": status,
                     "proof": best["slug"] if best else None,
                     "proof_date": (datetime.datetime.fromtimestamp(best["epoch"], datetime.timezone.utc)
                                    .strftime("%Y-%m-%d") if best else None)})

    # ratchet floor from check-mirror-coverage.py (the falsification guard)
    cov = open(os.path.join(ROOT, "bin/check-mirror-coverage.py"),
               encoding="utf-8", errors="replace").read()
    mud = re.search(r"MAX_UNMIRRORED_DEFS\s*=\s*(\d+)", cov)
    muf = re.search(r"MAX_UNMIRRORED_FILES\s*=\s*(\d+)", cov)
    mud = int(mud.group(1)) if mud else -1
    muf = int(muf.group(1)) if muf else -1

    oldest = (datetime.datetime.fromtimestamp(oldest_relied, datetime.timezone.utc).strftime("%Y-%m-%d")
              if oldest_relied else "n/a — NO PROOF IS RELIED ON")

    # FALSIFICATION GUARD (§3.5's own falsifier, made executable). The fraction must never
    # be allowed to RISE because live defs were DELETED or moved into an unmirrored file.
    # Pin it with the check-mirror-coverage ratchets: if either rose since the previous
    # commit of that file, a rise in the fraction is an ARTEFACT and is reported as one.
    prev = subprocess.run(["git", "-C", ROOT, "show",
                           "HEAD~1:bin/check-mirror-coverage.py"],
                          capture_output=True, text=True).stdout
    guard = "not evaluated (no previous revision of check-mirror-coverage.py)"
    if prev:
        pd = re.search(r"MAX_UNMIRRORED_DEFS\s*=\s*(\d+)", prev)
        pf = re.search(r"MAX_UNMIRRORED_FILES\s*=\s*(\d+)", prev)
        pd = int(pd.group(1)) if pd else -1
        pf = int(pf.group(1)) if pf else -1
        if mud > pd or muf > pf:
            guard = ("*** RAISED since HEAD~1 (%d/%d -> %d/%d) — ANY RISE IN THE FRACTION "
                     "IS AN ARTEFACT AND MUST BE REPORTED AS ONE ***" % (pd, pf, mud, muf))
        else:
            guard = "OK — MAX_UNMIRRORED_* did not rise since HEAD~1 (%d/%d)" % (pd, pf)
    proved_files = sum(1 for r in rows if r["status"] == "PROVED")

    out = {
        "staleness": mode,
        "verified_defs": verified, "live_defs": live_defs,
        "fraction_pct": round(100.0 * verified / live_defs, 2) if live_defs else 0.0,
        "unproven_perimeter_defs": unproven,
        "mirror_defs": mirror_defs_total, "markers": markers_total,
        "mirror_files": len(mirror_files), "proved_files": proved_files,
        "live_files": len(live_files),
        "MAX_UNMIRRORED_DEFS": mud, "MAX_UNMIRRORED_FILES": muf,
        "oldest_proof_relied_on": oldest,
        "falsification_guard": guard,
        "report_figure_pct": round(100.0 * (mirror_defs_total - markers_total) / live_defs, 2)
        if live_defs else 0.0,
    }
    if want_json:
        print(json.dumps({"summary": out, "files": rows}, indent=2))
        return 0

    print("=" * 78)
    print("BODY-VERIFIED FRACTION OF THE LIVE VERIFIER — FROM PROOF VERDICTS")
    print("staleness rule: --staleness=%s" % mode)
    print("=" * 78)
    print("  (1) verified / live        %d / %d = %.2f %%"
          % (verified, live_defs, out["fraction_pct"]))
    print("  (2) unproven-perimeter     %d defs in %d of %d mirror files"
          % (unproven, len(mirror_files) - proved_files, len(mirror_files)))
    print("  (3) unmirrored ratchets    MAX_UNMIRRORED_DEFS=%d  MAX_UNMIRRORED_FILES=%d"
          % (mud, muf))
    print("      OLDEST PROOF RELIED ON %s" % oldest)
    print("      mirror files with a fresh passing whole-file proof: %d of %d"
          % (proved_files, len(mirror_files)))
    print("      FALSIFICATION GUARD    %s" % guard)
    print("-" * 78)
    print("  FOR CONTRAST, THE FIGURE THIS REPLACES (marker-absence, NOT measured):")
    print("      (mirror defs - markers) / live = (%d - %d) / %d = %.2f %%"
          % (mirror_defs_total, markers_total, live_defs, out["report_figure_pct"]))
    print("      That number assumes every unmarked def in every mirror file is proved,")
    print("      including the %d files with no fresh passing proof on record."
          % (len(mirror_files) - proved_files))
    print("=" * 78)
    if per_file:
        for r in sorted(rows, key=lambda r: (r["status"], r["file"])):
            print("  %-9s %5d defs %4d mk  %-52s %s"
                  % (r["status"], r["defs"], r["markers"], r["file"], r["proof"] or ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
