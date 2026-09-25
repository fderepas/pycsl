#!/usr/bin/env python3
r"""check-trusted-reasons.py — the `\trusted` REASON TAXONOMY plane (convergence-metric Phase 3).

WHY THIS EXISTS. Every one of the live `#@ \trusted` markers in the self-annotation mirror is
the SAME bytes: `#@ \trusted reviewer: pycsl-self-annotate`. A considered, deliberately spent
assumption (bought to reach rc=0), a stub behind a measured correctness wall, a stub waiting
for a named capability, and a stub nobody ever attempted are INDISTINGUISHABLE. That is why the
451 -> 459 rise could not be read, and why "the floor is N" has been quoted and refuted so often.
The histogram this plane prints is the decomposition of the marker count.

WHY OUT OF BAND (a side file) AND NOT A TOKEN ON THE MARKER LINE. The plan's original design
put `reason: <bucket>` on the `#@ \trusted` line itself. That was PILOTED and REFUTED
(`getting-better/open-routes/finding-reason-token-refuses-the-whole-file.md`): `\trusted` is a
PARSED DIRECTIVE WITH A CLOSED GRAMMAR (`Module2_Parser._parse_trusted` accepts only
`\trusted [reviewer: ID]`), so ANY trailing token makes the parser REFUSE THE WHOLE FILE — no
`.mlw` at all, which a common-files byte diff reads as zero changes: a FALSE GREEN. So:
  * NEVER add a token to a `#@ \trusted` line, and never repurpose `reviewer:`;
  * the reason lives in `getting-better/trusted-reasons.tsv`, and THIS plane holds the side
    file and the markers in lock-step, in BOTH directions, because a side file's failure mode
    is drift.

THE SIDE FILE. `getting-better/trusted-reasons.tsv`: `#` comment lines, then the header
`file<TAB>qualname<TAB>reason<TAB>cite`, then one row per live marker.
  file      path relative to the mirror root `src/self-annotate/src`
  qualname  the FULL nested qualname of the def the marker governs (`Class.method.inner`, no
            `<locals>`). NEVER a line number — lines move on every edit, names do not.
            COLLISION RULE: among ALL defs in the file sharing a qualname (trusted or not), the
            first in source order keeps the bare name, the second gets `#2`, the third `#3`...
            Numbering over all defs, not only trusted ones, means CONVERTING one stub never
            renumbers a still-trusted sibling. (Implemented in `bin/trusted_markers.py`.)
  reason    exactly one of
              correctness:<name>       never convertible; the wall is a correctness wall
              cost-scale:<capability>  convertible once <capability> is built
              spent-rc0                deliberately spent to buy rc=0
              unclassified             the DEFAULT; this bucket is ratcheted toward zero
            `<name>` / `<capability>` match `[a-z0-9][a-z0-9._-]*`.
  cite      `-`, or a reference to a heading of `getting-better/driver-backlog.md`.
            REQUIRED (not `-`) for `correctness:*` and `cost-scale:*`: a boundary tag is a CLAIM,
            and this repo's boundary claims have been refuted repeatedly, so every claim must
            point at the paragraph that measured it. Optional for `unclassified` / `spent-rc0`;
            if one is given anyway it must still resolve.

CITE RESOLUTION RULE (exact). A HEADING is a line of driver-backlog.md, outside a ``` fence,
matching `^#{1,6}\s+(text)` — `text` is everything after the hashes and whitespace, with
trailing whitespace stripped. A cite RESOLVES iff
  (1) it EQUALS the text of exactly one heading, or, failing that,
  (2) it is a case-sensitive SUBSTRING of the text of exactly one heading.
Zero matches -> UNRESOLVED; two or more (at the first rule that matches any) -> AMBIGUOUS.
Both are defects. A substring is allowed because backlog headings are long and carry dates and
counts; uniqueness is what keeps it from silently re-pointing when a similar heading is added
(it goes AMBIGUOUS and red instead).

THE ATTACHMENT WALK IS NOT A SECOND WALK. Markers are enumerated with `bin/trusted_markers.py`
— the module `bin/count-trusted-directives.py` itself counts with — so this plane and the
authoritative count cannot disagree about the population. Two walks that disagree is exactly
the class of bug this repo keeps finding (see the one-vs-two-underscore note in
count-trusted-directives.py).

WHAT IT ENFORCES (exit 0 OK / 1 defect / 2 refusal)
  a. every live marker has exactly one row (MISSING -> 1, prints the row to ADD);
     every row names a live marker (ORPHAN -> 1, prints the row to DELETE);
     a duplicated row key -> 1; a malformed row (not 4 tab-separated fields) -> 1;
     an unattached marker, or a marker governing more than one def -> 1.
  b. the reason grammar above -> 1 on anything else.
  c. the cite rule above -> 1 on an unresolved or ambiguous cite.
  d. ZERO-INPUT GUARD (the #44 rule): fewer than MIN_MIRROR_FILES mirror files, a missing TSV,
     a TSV with no data rows, zero markers, an unparseable marker-bearing mirror file, or a
     missing backlog -> 2, "THIS IS A REFUSAL, NOT A PASS". An empty population has checked
     nothing and must never read as a pass.
  e. RATCHET: unclassified > MAX_UNCLASSIFIED -> 1. A marker with NO row counts as
     unclassified (it is the default).
  f. `--sync` prints the exact rows to add and to delete; `--sync --write` applies them (rows
     that survive keep their reason and cite; order is canonical: file, then source order).
     NOTHING is ever applied without `--write`.
  g. a histogram on EVERY run: per bucket and per `correctness:<name>` / `cost-scale:<cap>`.

A NEWLY ADDED MARKER LANDS AS `unclassified`, AND THAT IS DELIBERATE. `--sync --write` seeds it
`unclassified -`, which RAISES the unclassified count and breaks the ratchet: the driver must
classify the new assumption at the moment it is spent (typically `spent-rc0`, or a cited
`cost-scale:`), rather than let it disappear into 459 identical lines. That friction is what
makes a rise like 451 -> 459 legible. A converted stub leaves an ORPHAN row; delete it (the
unclassified count falls, lower the constant).

NOT WIRED INTO `bin/run-soundness-planes.sh` (yet): that would move the battery from 34 to 35
planes, which many status notes cite. Recorded as a named follow-up in
`getting-better/convergence-metric-implement.md` §Phase 3 amendment.

NEGATIVE TESTS. `--self-test` plants each defect in a TEMP copy (never the real TSV) and checks
the exit code and message: deleted row -> 1, orphan -> 1, duplicate -> 1, bad reason -> 1,
unresolved cite -> 1, ratchet exceeded -> 1, missing/empty TSV -> 2, empty mirror -> 2, the `#2`
collision path on a synthetic mirror copy -> 1 then 0, `--sync --write` round trip -> 0, and the
POSITIVE control (the real TSV) -> 0.

Usage:
  bin/check-trusted-reasons.py [--tsv PATH] [--mirror DIR] [--backlog PATH]
                               [--max-unclassified N] [--verbose]
  bin/check-trusted-reasons.py --sync [--write]      rows to add / delete (apply with --write)
  bin/check-trusted-reasons.py --seed                write a fresh all-`unclassified` TSV
                                                     (refuses if the TSV already has rows)
  bin/check-trusted-reasons.py --self-test
"""
from __future__ import annotations

import argparse
import ast
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trusted_markers import (  # noqa: E402
    ROOT, MIRROR, MIN_MIRROR_FILES, MARKER, iter_trusted_defs)

TSV = os.path.join(ROOT, "getting-better", "trusted-reasons.tsv")
BACKLOG = os.path.join(ROOT, "getting-better", "driver-backlog.md")
HEADER = ("file", "qualname", "reason", "cite")

# RATCHET HISTORY — MONOTONE DOWN ONLY. NEVER RAISE THIS NUMBER TO MAKE THE PLANE PASS.
# A new marker that breaks the ratchet is to be CLASSIFIED (spent-rc0 / cost-scale:<cap> with a
# cite / correctness:<name> with a cite), not absorbed by moving the bound. Itemise every change:
#   458  2026-09-14, first measurement (convergence-metric Phase 3). 459 live markers; 458 seeded
#        `unclassified`; ONE tagged from an unambiguous backlog heading that names the exact
#        function and its boundary tag: Module5_IREmitter `_py_stmts_to_ir` ->
#        `cost-scale:stmt-handler-dispatch`, cite "L2 `_py_stmts_to_ir`".
#   456  2026-09-25, gen #31. Two `unclassified` rows DELETED because their markers were
#        retired by PROOF (`errors.py::PyCSLError.message`,
#        `proof2why3/sertop.py::SertopSession.__exit__`, commit af7f32c1), and two rows ADDED
#        already CLASSIFIED — `Module6_WhyMLTranspiler._sig_val_from_let._hdr_name` and
#        `core_ir_semantic._returns_literal_none.walk`, both
#        `cost-scale:nested-closure-lift`. Those two markers are honest additions for closures
#        inside `\trusted` parents that were verified by nothing; each is retired by
#        converting its enclosing function, and that is behind the lift capability.
#        So the count of markers did not move (460 -> 458 -> 460) and this bucket fell by two
#        at both ends: a classified arrival is as good as a retirement for THIS ratchet, which
#        is the right incentive — it pays for knowing why, not only for removing.
MAX_UNCLASSIFIED = 456

REASON_RE = re.compile(
    r"^(?:(?P<kind>correctness|cost-scale):(?P<val>[a-z0-9][a-z0-9._-]*)|spent-rc0|unclassified)$")
BUCKETS = ("correctness", "cost-scale", "spent-rc0", "unclassified")

TSV_COMMENT = """\
# trusted-reasons.tsv — WHY each live `#@ \\trusted` marker in src/self-annotate/src is trusted.
#
# OUT OF BAND ON PURPOSE. A token on the marker line makes Module2 REFUSE THE WHOLE FILE (no .mlw,
# a false green in a common-files byte diff) — see
# getting-better/open-routes/finding-reason-token-refuses-the-whole-file.md. Never tag the marker.
#
# Held in lock-step with the markers by bin/check-trusted-reasons.py (both directions, grammar,
# cite, zero-input guard, MAX_UNCLASSIFIED ratchet). Fix drift with
#   bin/check-trusted-reasons.py --sync            (print rows to add / delete)
#   bin/check-trusted-reasons.py --sync --write    (apply; surviving rows keep their reason)
#
# SCHEMA: file<TAB>qualname<TAB>reason<TAB>cite, one row per live marker.
#   file      relative to src/self-annotate/src
#   qualname  FULL nested qualname of the governed def (Class.method.inner), NEVER a line number.
#             Collisions within a file: among ALL defs sharing the qualname (trusted or not), the
#             first in source order is bare, the second `#2`, the third `#3`, ...
#   reason    correctness:<name>       never convertible (a correctness wall)      cite REQUIRED
#             cost-scale:<capability>  convertible once <capability> is built     cite REQUIRED
#             spent-rc0                deliberately spent to buy rc=0
#             unclassified             THE DEFAULT; ratcheted toward zero
#   cite      `-`, or a heading of getting-better/driver-backlog.md: the exact heading text, or a
#             substring of exactly ONE heading's text (outside ``` fences).
#
# A correctness:/cost-scale: tag is a CLAIM, and this repo's boundary claims have been refuted
# repeatedly. Tag only with a cite to the paragraph that measured it; when in doubt, unclassified.
"""


def say(msg):
    print(msg)


# ----------------------------------------------------------------------------------------------
# inputs


def live_markers(mirror):
    """Return (rows, problems, nfiles).

    rows      {(file, qualname): (marker_line_1based)} for every live marker
    problems  list of ("refuse"|"defect", message)
    """
    files = sorted(glob.glob(os.path.join(mirror, "**/*.py"), recursive=True))
    rows, problems = {}, []
    if len(files) < MIN_MIRROR_FILES:
        return rows, [("refuse", "only %d mirror .py file(s) found under %s, expected at least "
                       "%d" % (len(files), mirror, MIN_MIRROR_FILES))], len(files)
    for f in files:
        rel = os.path.relpath(f, mirror)
        src = open(f).read()
        lines = src.split("\n")
        marker_idx = {i for i, l in enumerate(lines) if MARKER.match(l.strip())}
        if not marker_idx:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            problems.append(("refuse", "%s does not parse (%s) but carries %d marker(s); its "
                             "population cannot be enumerated" % (rel, e, len(marker_idx))))
            continue
        claimed = {}
        for node, m, q in iter_trusted_defs(tree, lines):
            claimed.setdefault(m, []).append(q)
            rows[(rel, q)] = m + 1
        for m, qs in sorted(claimed.items()):
            if len(qs) > 1:
                problems.append(("defect", "%s:%d marker governs %d defs (%s) — ambiguous "
                                 "attachment" % (rel, m + 1, len(qs), ", ".join(qs))))
        for m in sorted(marker_idx - set(claimed)):
            problems.append(("defect", "%s:%d UNATTACHED marker (annotates nothing; see "
                             "bin/count-trusted-directives.py)" % (rel, m + 1)))
    return rows, problems, len(files)


def read_tsv(path):
    """Return (entries, problems, has_header). entries: list of (tsv_line, file, qual, reason,
    cite) in file order."""
    entries, problems = [], []
    if not os.path.exists(path):
        return None, [("refuse", "TSV %s does not exist" % path)], False
    header_seen = False
    for n, raw in enumerate(open(path).read().split("\n"), 1):
        if raw.strip() == "" or raw.startswith("#"):
            continue
        fields = raw.split("\t")
        if not header_seen:
            if tuple(fields) != HEADER:
                problems.append(("defect", "TSV line %d: expected header %r, got %r"
                                 % (n, "\t".join(HEADER), raw)))
            header_seen = True
            continue
        if len(fields) != 4 or any(x.strip() != x or x == "" for x in fields):
            problems.append(("defect", "TSV line %d: MALFORMED row (need 4 non-empty, "
                             "tab-separated, unpadded fields): %r" % (n, raw)))
            continue
        entries.append((n, fields[0], fields[1], fields[2], fields[3]))
    return entries, problems, header_seen


def backlog_headings(path):
    heads, fence = [], False
    for raw in open(path).read().split("\n"):
        if raw.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^#{1,6}\s+(.*\S)\s*$", raw)
        if m:
            heads.append(m.group(1))
    return heads


def resolve_cite(cite, heads):
    """(ok, detail)."""
    exact = [h for h in heads if h == cite]
    if len(exact) == 1:
        return True, exact[0]
    if len(exact) > 1:
        return False, "AMBIGUOUS — equals %d headings" % len(exact)
    sub = [h for h in heads if cite in h]
    if len(sub) == 1:
        return True, sub[0]
    if not sub:
        return False, "UNRESOLVED — matches no driver-backlog.md heading"
    return False, "AMBIGUOUS — a substring of %d headings, e.g. %r" % (len(sub), sub[:2])


def row_text(f, q, reason="unclassified", cite="-"):
    return "\t".join((f, q, reason, cite))


def write_tsv(path, live, keep):
    """Canonical write: file, then source order. `keep` {(f,q): (reason, cite)}."""
    out = [TSV_COMMENT.rstrip("\n"), "\t".join(HEADER)]
    for (f, q), line in sorted(live.items(), key=lambda kv: (kv[0][0], kv[1], kv[0][1])):
        reason, cite = keep.get((f, q), ("unclassified", "-"))
        out.append(row_text(f, q, reason, cite))
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")


# ----------------------------------------------------------------------------------------------
# histogram


def histogram(live, table):
    """Counts over LIVE markers; a marker with no row is `unclassified` (the default)."""
    buckets = {b: 0 for b in BUCKETS}
    values = {}
    norow = 0
    invalid = 0
    for key in live:
        reason = table.get(key)
        if reason is None:
            buckets["unclassified"] += 1
            norow += 1
            continue
        m = REASON_RE.match(reason)
        if not m:
            invalid += 1
            continue
        if m.group("kind"):
            buckets[m.group("kind")] += 1
            values[reason] = values.get(reason, 0) + 1
        else:
            buckets[reason] += 1
    return buckets, values, norow, invalid


def print_histogram(live, table):
    buckets, values, norow, invalid = histogram(live, table)
    say("[*] trusted-reasons histogram over %d live marker(s):" % len(live))
    for b in BUCKETS:
        extra = " (%d of them have no row yet)" % norow if b == "unclassified" and norow else ""
        say("      %-14s %4d%s" % (b, buckets[b], extra))
    if invalid:
        say("      %-14s %4d (reason fails the grammar)" % ("<invalid>", invalid))
    for v in sorted(values):
        say("        %-40s %4d" % (v, values[v]))
    return buckets


# ----------------------------------------------------------------------------------------------
# main check


def run(args):
    live, mprobs, nfiles = live_markers(args.mirror)
    refusals = [m for k, m in mprobs if k == "refuse"]
    if not refusals and not live:
        refusals.append("ZERO live markers under %s (%d mirror files)" % (args.mirror, nfiles))
    entries, tprobs, has_header = (None, [], False)
    if args.seed:
        return seed(args, live, refusals)
    entries, tprobs, has_header = read_tsv(args.tsv)
    refusals += [m for k, m in tprobs if k == "refuse"]
    if entries is not None and not entries:
        refusals.append("TSV %s has no data rows (empty, or header/comments only)" % args.tsv)
    if not os.path.exists(args.backlog):
        refusals.append("backlog %s does not exist; cites cannot be resolved" % args.backlog)
    if refusals:
        for m in refusals:
            say("[!] trusted-reasons: REFUSING — %s. THIS IS A REFUSAL, NOT A PASS." % m)
        return 2

    defects = [m for k, m in mprobs if k == "defect"] + [m for k, m in tprobs if k == "defect"]
    heads = backlog_headings(args.backlog)

    table, seen_line, dups = {}, {}, []
    for n, f, q, reason, cite in entries:
        key = (f, q)
        if key in seen_line:
            dups.append((n, seen_line[key], f, q))
            continue
        seen_line[key] = n
        table[key] = reason
        m = REASON_RE.match(reason)
        if not m:
            defects.append("TSV line %d: BAD REASON %r for %s::%s — must be exactly one of "
                           "correctness:<name>, cost-scale:<capability>, spent-rc0, "
                           "unclassified" % (n, reason, f, q))
            continue
        if m.group("kind"):
            if cite == "-":
                defects.append("TSV line %d: %s::%s is tagged %r but cites `-`; a boundary tag "
                               "is a claim and must cite a driver-backlog.md heading"
                               % (n, f, q, reason))
                continue
        if cite != "-":
            ok, detail = resolve_cite(cite, heads)
            if not ok:
                defects.append("TSV line %d: CITE %r for %s::%s is %s" % (n, cite, f, q, detail))
            elif args.verbose:
                say("    cite ok  %s::%s -> %s" % (f, q, detail))
    for n, first, f, q in dups:
        defects.append("TSV line %d: DUPLICATE row key %s::%s (first at line %d)"
                       % (n, f, q, first))

    missing = sorted((k for k in live if k not in table), key=lambda k: (k[0], live[k]))
    orphans = [(seen_line[k], k) for k in table if k not in live]
    orphans.sort()

    buckets = print_histogram(live, table)
    say("[*] trusted-reasons: %d live marker(s) in %d mirror file(s) · %d row(s) · missing %d · "
        "orphan %d · duplicate %d" % (len(live), nfiles, len(entries), len(missing),
                                      len(orphans), len(dups)))

    for k in missing:
        defects.append("MISSING row for live marker %s:%d:%s" % (k[0], live[k], k[1]))
    for n, k in orphans:
        defects.append("ORPHAN row at TSV line %d names no live marker: %s::%s" % (n, k[0], k[1]))

    if args.sync:
        say("[*] trusted-reasons --sync: %d row(s) to ADD, %d row(s) to DELETE"
            % (len(missing), len(orphans)))
        if missing:
            say("    ADD (paste into %s; classify at spend time):" % _shown(args.tsv))
            for k in missing:
                print(row_text(k[0], k[1]))
        if orphans:
            say("    DELETE (the marker is gone — converted or renamed):")
            for n, k in orphans:
                print(row_text(k[0], k[1], table[k], _cite_of(entries, n)))
        missing_names = {}
        for k in missing:
            missing_names.setdefault((k[0], k[1].split(".")[-1].split("#")[0]), []).append(k)
        for n, k in orphans:
            cand = missing_names.get((k[0], k[1].split(".")[-1].split("#")[0]))
            if cand and table[k] != "unclassified":
                say("    [*] possible RENAME: orphan %s::%s (%s) vs missing %s — carry the "
                    "reason by hand" % (k[0], k[1], table[k], ", ".join(c[1] for c in cand)))
        if args.write:
            if any(("DUPLICATE" in d or "MALFORMED" in d or "expected header" in d)
                   for d in defects):
                say("[!] trusted-reasons --sync --write: NOT WRITING — the TSV has duplicate, "
                    "malformed or header defects; fix those by hand first.")
                return 1
            keep = {(f, q): (r, c) for _n, f, q, r, c in entries}
            write_tsv(args.tsv, live, keep)
            say("[+] trusted-reasons --sync --write: rewrote %s (%d rows). Re-run without "
                "--sync to check." % (args.tsv, len(live)))
            return 0

    unclassified = buckets["unclassified"]
    for d in defects:
        say("    [!] %s" % d)
    if missing and not args.sync:
        say("    ADD these rows (or run --sync --write):")
        for k in missing:
            print(row_text(k[0], k[1]))
    if orphans and not args.sync:
        say("    DELETE these rows (or run --sync --write):")
        for n, k in orphans:
            print(row_text(k[0], k[1], table[k], _cite_of(entries, n)))

    ratchet_broken = unclassified > args.max_unclassified
    if ratchet_broken:
        say("[-] trusted-reasons: UNCLASSIFIED RATCHET BROKEN — %d > %d. Classify the new "
            "marker(s); NEVER raise MAX_UNCLASSIFIED to make this pass."
            % (unclassified, args.max_unclassified))
    if defects or ratchet_broken:
        say("[!] trusted-reasons: FAIL (%d defect(s)%s)"
            % (len(defects), ", ratchet broken" if ratchet_broken else ""))
        return 1
    if unclassified < args.max_unclassified:
        say("[+] trusted-reasons: unclassified %d < ratchet %d — lower MAX_UNCLASSIFIED."
            % (unclassified, args.max_unclassified))
    say("[+] trusted-reasons: OK — %d marker(s) <-> %d row(s), both directions; unclassified %d "
        "(ratchet %d)" % (len(live), len(entries), unclassified, args.max_unclassified))
    return 0


def _shown(path):
    rel = os.path.relpath(path, ROOT)
    return path if rel.startswith("..") else rel


def _cite_of(entries, n):
    for e in entries:
        if e[0] == n:
            return e[4]
    return "-"


def seed(args, live, refusals):
    if refusals:
        for m in refusals:
            say("[!] trusted-reasons --seed: REFUSING — %s. THIS IS A REFUSAL, NOT A PASS." % m)
        return 2
    if os.path.exists(args.tsv):
        entries, _p, _h = read_tsv(args.tsv)
        if entries:
            say("[!] trusted-reasons --seed: REFUSING to overwrite %s, which already has %d "
                "row(s). Use --sync --write to reconcile instead." % (args.tsv, len(entries)))
            return 2
    write_tsv(args.tsv, live, {})
    say("[+] trusted-reasons --seed: wrote %s with %d `unclassified` row(s)"
        % (args.tsv, len(live)))
    return 0


# ----------------------------------------------------------------------------------------------
# self-test: prove the red before believing the green


def self_test(args):
    me = os.path.abspath(__file__)
    real = open(args.tsv).read()
    lines = real.split("\n")
    data_idx = [i for i, l in enumerate(lines)
                if l and not l.startswith("#") and not l.startswith("file\t")]
    if not data_idx:
        say("[!] self-test: the real TSV has no data rows. THIS IS A REFUSAL, NOT A PASS.")
        return 2
    first = lines[data_idx[0]].split("\t")
    # pick a row with an unclassified reason so the cost-scale plant does not collide
    uncl = next(i for i in data_idx if lines[i].split("\t")[2] == "unclassified")
    tmp = tempfile.mkdtemp(prefix="trusted-reasons-selftest.")
    results = []

    def plant(name, text):
        p = os.path.join(tmp, name + ".tsv")
        with open(p, "w") as fh:
            fh.write(text)
        return p

    def check(label, argv, want_rc, want_msg):
        r = subprocess.run([sys.executable, me] + argv, capture_output=True, text=True)
        out = r.stdout + r.stderr
        hit = [l for l in out.split("\n") if want_msg in l]
        ok = r.returncode == want_rc and bool(hit)
        results.append((label, want_rc, r.returncode, ok, hit[0].strip() if hit else
                        "(expected message %r not found)" % want_msg))
        return ok

    base = ["--backlog", args.backlog, "--mirror", args.mirror]
    try:
        check("positive control: real TSV", ["--tsv", args.tsv] + base, 0,
              "[+] trusted-reasons: OK")
        drop = lines[:data_idx[0]] + lines[data_idx[0] + 1:]
        check("delete one row", ["--tsv", plant("delete", "\n".join(drop))] + base, 1,
              "MISSING row for live marker %s:" % first[0])
        orphan = lines + ["frontend/pure_ast.py\tNoSuchClass.no_such_method\tunclassified\t-"]
        check("orphan row (nonexistent qualname)",
              ["--tsv", plant("orphan", "\n".join(orphan))] + base, 1,
              "ORPHAN row at TSV line")
        dup = lines[:data_idx[0] + 1] + [lines[data_idx[0]]] + lines[data_idx[0] + 1:]
        check("duplicate row", ["--tsv", plant("dup", "\n".join(dup))] + base, 1,
              "DUPLICATE row key")
        bad = list(lines)
        f = bad[uncl].split("\t")
        bad[uncl] = row_text(f[0], f[1], "foo", "-")
        check("bad reason token (reason=foo)", ["--tsv", plant("badreason", "\n".join(bad))]
              + base, 1, "BAD REASON 'foo'")
        cs = list(lines)
        cs[uncl] = row_text(f[0], f[1], "cost-scale:x", "no heading has this text zq9")
        check("cost-scale:x with unresolved cite", ["--tsv", plant("cite", "\n".join(cs))]
              + base, 1, "is UNRESOLVED")
        cs2 = list(lines)
        cs2[uncl] = row_text(f[0], f[1], "cost-scale:x", "-")
        check("cost-scale:x citing `-`", ["--tsv", plant("cite2", "\n".join(cs2))] + base, 1,
              "cites `-`")
        amb = list(lines)
        amb[uncl] = row_text(f[0], f[1], "correctness:x", "2026-08-11")
        check("correctness:x with ambiguous cite", ["--tsv", plant("amb", "\n".join(amb))]
              + base, 1, "is AMBIGUOUS")
        # the ratchet: the measured unclassified count is n; a bound of n-1 must go red
        r = subprocess.run([sys.executable, me, "--tsv", args.tsv] + base, capture_output=True,
                           text=True)
        m = re.search(r"unclassified\s+(\d+)", r.stdout)
        n_uncl = int(m.group(1)) if m else 0
        check("ratchet exceeded (--max-unclassified %d)" % (n_uncl - 1),
              ["--tsv", args.tsv, "--max-unclassified", str(n_uncl - 1)] + base, 1,
              "UNCLASSIFIED RATCHET BROKEN")
        check("empty TSV", ["--tsv", plant("empty", "")] + base, 2, "THIS IS A REFUSAL")
        check("header-only TSV", ["--tsv", plant("hdr", "\t".join(HEADER) + "\n")] + base, 2,
              "THIS IS A REFUSAL")
        check("missing TSV", ["--tsv", os.path.join(tmp, "nope.tsv")] + base, 2,
              "THIS IS A REFUSAL")
        empty_mirror = os.path.join(tmp, "empty-mirror")
        os.makedirs(empty_mirror)
        check("mirror root = empty dir", ["--tsv", args.tsv, "--backlog", args.backlog,
                                          "--mirror", empty_mirror], 2, "THIS IS A REFUSAL")
        # the `#N` collision path, on a synthetic copy of the mirror
        mcopy = os.path.join(tmp, "mirror-copy")
        shutil.copytree(args.mirror, mcopy, ignore=shutil.ignore_patterns("*.mlw", "__pycache__"))
        with open(os.path.join(mcopy, "zz_selftest_collision.py"), "w") as fh:
            fh.write("class K:\n"
                     "    #@ \\trusted reviewer: selftest\n"
                     "    def m(self) -> int:\n        return 1\n\n"
                     "    def m(self) -> int:\n        return 2\n\n"
                     "    #@ \\trusted reviewer: selftest\n"
                     "    def m(self) -> int:\n        return 3\n")
        coll_argv = ["--tsv", args.tsv, "--backlog", args.backlog, "--mirror", mcopy]
        check("collision: 3 defs `K.m`, 1st+3rd trusted -> row `K.m#3` required", coll_argv, 1,
              "MISSING row for live marker zz_selftest_collision.py:9:K.m#3")
        coll_tsv = plant("collision", real.rstrip("\n") + "\n"
                         + row_text("zz_selftest_collision.py", "K.m") + "\n"
                         + row_text("zz_selftest_collision.py", "K.m#3") + "\n")
        check("collision: rows `K.m` + `K.m#3` present",
              ["--tsv", coll_tsv, "--backlog", args.backlog, "--mirror", mcopy,
               "--max-unclassified", str(n_uncl + 2)], 0, "[+] trusted-reasons: OK")
        # --sync --write round trip on a temp copy: a deleted row is restored, reasons kept
        rt = plant("roundtrip", "\n".join(drop))
        check("--sync --write on a deleted-row copy", ["--tsv", rt, "--sync", "--write"] + base,
              0, "--sync --write: rewrote")
        check("after --sync --write: clean", ["--tsv", rt] + base, 0, "[+] trusted-reasons: OK")
        same = open(rt).read() == real
        results.append(("round trip is byte-identical to the real TSV", "-", "-", same,
                        "identical" if same else "DIFFERS"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    say("[*] trusted-reasons --self-test: %d case(s)" % len(results))
    for label, want, got, ok, msg in results:
        say("    %s %-58s want rc %s got rc %s :: %s"
            % ("[+]" if ok else "[!]", label, want, got, msg[:110]))
    if all(r[3] for r in results):
        say("[+] trusted-reasons --self-test: every planted defect went red, controls green")
        return 0
    say("[!] trusted-reasons --self-test: FAIL")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tsv", default=TSV)
    ap.add_argument("--mirror", default=MIRROR)
    ap.add_argument("--backlog", default=BACKLOG)
    ap.add_argument("--max-unclassified", type=int, default=MAX_UNCLASSIFIED)
    ap.add_argument("--sync", action="store_true", help="print rows to add / delete")
    ap.add_argument("--write", action="store_true", help="with --sync: apply them")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--self-test", "--selftest", dest="self_test", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if args.write and not args.sync:
        ap.error("--write only applies with --sync")
    args.mirror = os.path.abspath(args.mirror)
    if args.self_test:
        return self_test(args)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
