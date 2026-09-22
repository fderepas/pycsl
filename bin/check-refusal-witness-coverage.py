#!/usr/bin/env python3
r"""L-PLANE ORACLE: which of the compiler's REFUSALS has a corpus witness proving it can
fire?

WHY THIS EXISTS (gen #30). Route #209 was a trust boundary that READ correctly, had been
reviewed, and **had never fired in its life** — it asked a `pure_ast` matcher about a CSL
node, so its computed set was `{None}` and its intersection with the protected paths was
always empty. Nothing noticed, because the SIBLING form's identical boundary does fire and
has witnesses (0461/0462). An untested inert check sat beside a tested live one and looked
the same from outside.

>>> A REFUSAL YOU CANNOT POINT AT A FILE FOR IS A REFUSAL YOU HAVE NOT TESTED.

WHAT IT MEASURES. Two halves joined:

  * the STATIC half — every `raise PyCSL*Error(...)` site in `src/pycsl/`, with its
    diagnostic `code=` when it has one and the longest literal fragment of its message.
    195 sites at the first measurement, 76 carrying a code, 47 distinct codes.
  * the CENSUS half — `bin/refusal-witness-census.tsv`, produced by running EVERY
    `# pycsl-expected: FAIL` corpus witness (759 of them) and recording, for each, whether
    it is a REFUSAL (a pipeline error) or a VERIFY-FAIL, plus the message. That sweep takes
    about two hours, which is why its RESULT is committed and this gate joins against the
    artifact instead of re-running it. Regenerate with `--regenerate` when the corpus or
    the diagnostics move.

A site is WITNESSED when its message fragment appears in some censused refusal message.

THE FIRST JOINED MEASUREMENT (gen #30): **198 raise sites, 759 witnesses censused (404 of
them refusals), 58 sites DEMONSTRATED to fire and 140 not.** So roughly seven in ten of the
compiler's refusals have no file in the corpus proving they can fire — which is the
population route #209 came out of.

READ THOSE TWO NUMBERS AS BOUNDS, NOT AS FACTS. The join is textual: a site is matched when
the longest literal fragment of its message (first 60 characters) appears in some censused
refusal message, and the committed census truncates each message to 110 characters. A site
whose message is assembled from short pieces, or whose distinctive text falls past that
cut, counts as UNWITNESSED even if a witness exists. So 58 is a FLOOR on the demonstrated
set and 140 a CEILING on the undemonstrated one. `--regenerate` keeps 400 characters per
message and will move both numbers the right way; the ratchets below are set to the
CONSERVATIVE first measurement so that regenerating can only improve them.

THE SECOND JOINED MEASUREMENT (#49, gen #30, the same generation, hours later): **198
raise sites, 164 DEMONSTRATED and 17 not, plus 8 NOT SOURCE-REACHABLE and 9 UNMATCHABLE.**
The four counts now PARTITION the population; the first measurement's two summed to 198
only because everything unexplained was called a debt.

AND THE BOUND STATED DIRECTLY ABOVE WAS RIGHT, WHICH IS THE UNCOMFORTABLE PART. The
paragraph before this one says, in the generation's own words, that the census "truncates
each message to 110 characters", that a site whose distinctive text falls past that cut
"counts as UNWITNESSED even if a witness exists", that the numbers are a FLOOR and a
CEILING, and that `--regenerate` "will move both numbers the right way". Every word of
that is true and it was written down before the ratchets were set.

What happened next is the lesson. The CEILING travelled into
`getting-better/driver-handoff-latest.md` as a work item — "the 113 refusals that still
have no witness ... each costs about five minutes" — and by then it was a FACT about the
compiler rather than a bound on an instrument. Nine hours of corpus files were priced
against it. Repairing the census instead took about forty minutes and moved 85 -> 162; a
third of the witnesses that item would have produced were already in the corpus.

>>> A BOUND SURVIVES IN THE DOCSTRING AND DIES IN THE QUEUE. The hedge is written where
>>> the measurement is made, and the number is read where the work is planned. If a
>>> measurement is a bound, the GATE must say so every time it prints — which is why the
>>> refusals below (truncated census, placeholder fragments, U+FFFD) are now rc=2 instead
>>> of a sentence in a comment nobody re-reads.

FOUR THINGS THIS GATE CANNOT SEE, all found in one evening and all now handled rather than
described (see the constants and guards below): a census message CUT at the writer's cap
or MID-UTF-8 (both now REFUSALS); a raise with no literal of 25+ characters (its fragment
is "" and no witness can ever match — counted as UNMATCHABLE, derived every run); a raise
whose literal contains a `%s` placeholder the compiler never prints (`sites()` now splits
on placeholders, and a surviving one is a REFUSAL); and a refusal not reachable from a
`.py` source at all (`validate_ir`'s eight, demonstrated by
`bin/check-ir-schema-refusals.py` instead).

THREE OF THE REMAINING UNDEMONSTRATED SAY, IN THEIR OWN COMMENTS, THAT THEY WERE TESTED BY
DIRECT INJECTION — and they STAY IN THE DEBT COUNT anyway:

    module6_whyml/functions.py:7870   "Negative-tested by feeding it a pair with an
                                       unresolvable `base_method`."
    module6_whyml/statements.py:3651  "it is NEGATIVE-TESTED by feeding it the mixed
                                       spelling directly."
    module6_whyml/statements.py:3679  "Negative-tested by feeding it a region base that is
                                       not a parameter."

Each is a guard whose LIVE population is empty by construction, so no corpus program can
reach it — the same situation as `validate_ir`'s eight. The difference is that
`validate_ir` takes a dict and can be driven from a plane in ten lines, while these sit
deep in Module 6 emission and need an IR plus emitter state. Excluding them on the strength
of a COMMENT would be an exclusion with no gate behind it, which is exactly what lesson
(f3) is about ("an exclusion you never tested is a guess"), so they stay counted as
undemonstrated until someone builds the harness. THE REOPENING CAPABILITY is a second
executable plane in the shape of `bin/check-ir-schema-refusals.py`, driving the Module 6
emitter directly.

THE RATCHET: the witnessed count may only GROW, and the artifact's own size may only grow
with the corpus. A NEW refusal added without a witness is visible immediately — it lands in
the unwitnessed list and the count of unwitnessed sites rises above the ceiling.

NOT THE SAME AS `bin/check-refusal-reachability.py`, and the difference is worth stating
because the names are close. That plane asks whether a refusal's exception NAME is bound —
whether it raises its own message or a `NameError` — i.e. whether the refusal is
well-FORMED. This one asks whether any program in the corpus has ever MADE it fire. A
refusal can pass that gate perfectly and still be route #209: correctly spelled, correctly
imported, and inert.

THE NEXT REFINEMENT, RECORDED SO IT IS NOT RE-DERIVED. The census classifies a witness as
REFUSAL / VERIFY-FAIL / XPASS. A FOURTH class is worth carving out: **failure by TYPE
ERROR** — a Why3 "This expression has type int, but is expected to have type
array.Array.array". Those are the programs whose rejection is an ACCIDENT of an ill-typed
emission rather than a semantic guard, and gen #30 found one the hard way: making
`bytearray(n)` lower faithfully removed the type error that had been the only thing
stopping `b = bytes(2); b[0] = 7` from proving (witness 1725, lesson (b3)). A census that
separates "refused on purpose" from "rejected by accident" would have named that set in
advance.

WHAT IT IS NOT. Coverage here does not mean "correct"; it means "demonstrated to fire".
Route #209's lesson is precisely that those are different, and that only the second one can
be measured mechanically.

Usage:  bin/check-refusal-witness-coverage.py [--verbose] [--list-unwitnessed]
        bin/check-refusal-witness-coverage.py --regenerate   (runs the 2h sweep)
"""
import argparse
import ast
import glob
import os
import re
import subprocess
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENSUS = os.path.join(ROOT, "bin", "refusal-witness-census.tsv")
MIN_SITES = 150           # 195 at the first measurement
CENSUS_TRUNC = 4000       # the writer's message cap. See the TRUNCATION GUARD below: a
                          # stored message of EXACTLY this length was cut, and a cut
                          # message silently un-witnesses every site whose fragment falls
                          # past the cut.
MIN_WITNESSED = 164       # 58 at the first joined measurement; 67 after TEN witnesses were
                          # written the same day (Final F1/F2, three lemma arms, two
                          # assigns-region arms, `\length` on a dict, `\result` in a
                          # check, the happy `except` typo); 85 after 31 more; then 86
                          # with witness 1762 — and 131 once the CENSUS ITSELF was
                          # repaired. FORTY-FIVE of the "missing" witnesses had been in
                          # the corpus all along. May only grow.
MAX_UNWITNESSED = 17      # 140 -> 131 -> 113 by writing witnesses; 113 -> 67 by fixing
                          # the instrument; 67 -> 59 by DEMONSTRATING the eight that no
                          # corpus witness can reach; 59 -> 50 once the nine this
                          # instrument CANNOT MATCH were counted separately (below).
                          # May only shrink.

# NOT REACHABLE FROM A `.py` SOURCE FILE, and therefore never a corpus witness's job.
# `ir_schema.validate_ir` runs on the IR THE FRONT-END JUST BUILT (pycsl.py:511) and again
# at the JSON boundary (pycsl.py:962). No Python source can make Module 5 emit an IR whose
# `functions` is not a list or whose `contracts` is not a dict — the front-end builds those
# shapes itself. Counting these eight as "undemonstrated" pointed at the wrong work: an
# unwritten witness wants a corpus file, an unreachable-from-source refusal wants a DIRECT
# gate. `bin/check-ir-schema-refusals.py` is that gate — it builds a malformed IR for each,
# calls the real `validate_ir`, asserts the real code fires, and carries a WELL-FORMED
# control so a `validate_ir` that refused everything could not pass it.
#
# THIS IS AN EXCLUSION WITH A GATE BEHIND IT, NOT AN EXCUSE (lesson (f3), (v2)): if that
# plane is deleted or stops passing, these eight stop being demonstrated, and the battery
# says so. They are excluded from the unwitnessed COUNT and listed by `--list-unwitnessed`
# with their reason.
# UNMATCHABLE BY THIS INSTRUMENT, which is a THIRD thing and not a debt either. A site's
# FRAGMENT is the longest string literal in its raise, and a raise built entirely from
# short pieces and f-string interpolations has NO literal of 25+ characters:
#
#     raise PyCSLSemanticError(f"{where}: {name} is not {what}", code=...)
#
# For those, `frag` is "" and `hit` is False FOR EVERY CENSUS, so no witness — present,
# future, or already written — can ever mark them demonstrated. Thirteen sites are in this
# shape; four are also NOT_SOURCE_REACHABLE, leaving nine. Counting them as "no witness"
# pointed at the wrong work a THIRD time, after the 110-char truncation and the eight
# validate_ir checks.
#
# CLOSING THEM is a change to the COMPILER or the CENSUS, not to the corpus: give the raise
# one distinguishing literal, or print the diagnostic CODE alongside the message so the
# census can carry it and matching can key on the code. Printing the code is the better fix
# and moves all 437 census messages, which is why it is RECORDED rather than done here.
#
# A CONCRETE ILLUSTRATION now sits in the corpus. `Module1_Ingestor.py:354` raises
# `f"`{kw} {name}`: empty body"` — every literal in it is under 25 characters, so its
# fragment is "". Corpus witness `1772_gen30_witness_for_range_empty_body.py` MAKES THAT
# REFUSAL FIRE, and its message is in the census. The site is still counted unmatchable,
# because it is: the witness exists, the evidence is recorded, and this instrument cannot
# see the connection. That is the honest shape of the class — not "no witness", but "no
# way for me to tell".
#
# The count is a RATCHET that may only shrink, and the sites are listed by
# `--list-unwitnessed`. It is NOT an exemption list keyed by name: membership is DERIVED
# from the empty fragment every run, so a raise that gains a literal leaves the class
# automatically and rejoins the debt if it still has no witness.
MAX_UNMATCHABLE = 9

NOT_SOURCE_REACHABLE = {
    "PYCSL-IR-NOTDICT", "PYCSL-IR-MISSINGTOP", "PYCSL-IR-VERSION", "PYCSL-IR-FUNCSLIST",
    "PYCSL-IR-FUNCDICT", "PYCSL-IR-MISSINGFUNC", "PYCSL-IR-CONTRACTSDICT",
    "PYCSL-IR-MISSINGCONTRACTS",
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
    """Every `raise PyCSL*Error(...)` in the shipping compiler, with a message fragment."""
    out = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for f in sorted(glob.glob(os.path.join(ROOT, "src", "pycsl", "**", "*.py"),
                                  recursive=True)):
            try:
                tree = ast.parse(open(f, errors="replace").read())
            except SyntaxError:
                continue
            for n in ast.walk(tree):
                if not isinstance(n, ast.Raise) or not isinstance(n.exc, ast.Call):
                    continue
                fn = n.exc.func
                name = getattr(fn, "id", None) or getattr(fn, "attr", None)
                if not name or not str(name).startswith("PyCSL"):
                    continue
                code = None
                for kw in n.exc.keywords:
                    if kw.arg == "code" and isinstance(kw.value, ast.Constant):
                        code = kw.value.value
                # (#49) A LITERAL CONTAINING A `%s` IS NOT A FRAGMENT. Several raises
                # build their message with %-formatting, so the literal in the AST is
                # e.g. "function '%s' binds %s with a `with ... as` clause, and no
                # certified " — and the PLACEHOLDERS never appear in the output, so the
                # whole literal can never be found in a censused message. Three real
                # witnesses (1784/1785/1786) fired their refusals and moved the count by
                # ZERO before this split went in. Same family as the empty-fragment class
                # below: the matcher was looking for text the compiler never prints.
                # So: split every literal on its placeholders and keep the longest
                # PLACEHOLDER-FREE run.
                runs = []
                for p in literal_parts(n.exc):
                    runs.extend(re.split(r"%[-#0-9.]*[sdrifxgeb]|\{[^{}]*\}", p))
                parts = [r.strip() for r in runs if len(r.strip()) >= 25]
                frag = max(parts, key=len)[:80] if parts else ""
                out.append((os.path.relpath(f, ROOT), n.lineno, name, code, frag))
    return out


def census():
    # NOTE (#49): rows are keyed by BASENAME ALONE, and a basename is not unique across
    # the corpus directories — `0508.py` exists in both `corpus/pycsl-reference/` and
    # `corpus/python-reference/`. Matching is by MESSAGE CONTENT, so the ambiguity does
    # not corrupt the verdict here; it does mean any tool that re-runs a row must try
    # EVERY file with that basename, which is how the last 21 rows of the census repair
    # were recovered.
    if not os.path.exists(CENSUS):
        return None
    rows = []
    for line in open(CENSUS, encoding="utf-8", errors="replace"):
        if line.startswith("#") or not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--list-unwitnessed", action="store_true")
    ap.add_argument("--regenerate", action="store_true",
                    help="re-run every expected-FAIL witness (about two hours) and rewrite "
                         "bin/refusal-witness-census.tsv")
    args = ap.parse_args()

    if args.regenerate:
        print("[*] refusal-witness-coverage: regenerating the census — this runs every "
              "`# pycsl-expected: FAIL` corpus witness through the pipeline.")
        files = sorted(subprocess.run(
            ["grep", "-rl", "^# pycsl-expected: FAIL", os.path.join(ROOT, "test-suite",
                                                                    "corpus"),
             "--include=*.py"], capture_output=True, text=True).stdout.split())
        py = os.path.join(ROOT, ".venv", "bin", "python3")
        py = py if os.path.exists(py) else "python3"
        with open(CENSUS, "w", encoding="utf-8") as fh:
            fh.write("# witness\tclass\tmessage — regenerate with --regenerate\n")
            for f in files:
                flags = []
                for line in open(f, errors="replace"):
                    if line.startswith("# pycsl-flags:"):
                        flags = line.split(":", 1)[1].split()
                        break
                p = subprocess.run([py, os.path.join(ROOT, "src", "pycsl", "pycsl.py")]
                                   + flags + [f], capture_output=True, text=True)
                out = (p.stdout or "") + (p.stderr or "")
                if "PIPELINE ERROR" in out:
                    msg = ""
                    lines = out.splitlines()
                    for i, l in enumerate(lines):
                        if "PIPELINE ERROR" in l and i + 1 < len(lines):
                            msg = lines[i + 1].strip()
                            break
                    fh.write("%s\tREFUSAL\t%s\n" % (os.path.basename(f),
                                                    msg.replace("\t", " ")[:CENSUS_TRUNC]))
                elif "Verification SUCCESS" in out:
                    fh.write("%s\tXPASS\t\n" % os.path.basename(f))
                else:
                    fh.write("%s\tVERIFY-FAIL\t\n" % os.path.basename(f))
        print("[+] refusal-witness-coverage: census written to %s" % CENSUS)
        return 0

    st = sites()
    if len(st) < MIN_SITES:
        print("[!] refusal-witness-coverage: REFUSING — only %d raise site(s) found, "
              "expected at least %d. The walk is broken; this is not a pass."
              % (len(st), MIN_SITES), file=sys.stderr)
        return 2

    rows = census()
    if rows is None:
        print("[!] refusal-witness-coverage: REFUSING — no census at %s. Run "
              "`--regenerate` (about two hours) to build it." % CENSUS, file=sys.stderr)
        return 2

    # ---- TRUNCATION GUARD (#49, gen #30). THE GATE USED TO BE MEASURING ITS OWN
    # ARTIFACT. A site counts as demonstrated when its FRAGMENT — the longest string
    # literal in its raise, first 60 characters — appears in some censused message. The
    # committed census had been generated by an older writer that cut every message at
    # 110 characters: 318 of its 437 refusal rows were EXACTLY 110 long. Any fragment
    # beginning past character 110 could therefore never match, however many witnesses
    # existed. `0284`/`0285` fire PYCSL-SEM-CLASSINV and their rows stop at
    # "...should only reference sel", nine characters short of the word the fragment
    # needs; `0304` (GHOSTSTR) and `0556`/`0674` (QUANTBINDER) were cut the same way.
    # Repairing the census moved the count 86 -> 131 demonstrated, 112 -> 67 not: 45 of
    # the "missing" witnesses were in the corpus the whole time, and the handoff had
    # priced writing them at five minutes each.
    #
    # So: a stored message of EXACTLY the writer's cap was CUT, and the matching below is
    # unreliable for it. That is a REFUSAL, not a warning — a coverage gate that cannot
    # tell "this refusal has no witness" from "my own record of the witness is too short"
    # must not report a number.
    # ---- MATCHER SELF-AUDIT (#49). FOUR distinct artifacts turned up in this one
    # instrument in a single evening — the 110-char census truncation, the eight
    # not-source-reachable checks, the nine empty-fragment raises, and a literal whose
    # `%s` placeholders the compiler never prints. Each was found by hand, after the
    # number had already recommended work. So the plane now audits its OWN fragments
    # before it reports: a fragment that still carries a format placeholder is text the
    # compiler cannot print, and matching against it can only ever produce a false
    # "undemonstrated".
    bad_frag = [(rel, line, frag) for rel, line, _e, _c, frag in st
                if frag and re.search(r"%[-#0-9.]*[sdrifxgeb]|\{[^{}]*\}", frag)]
    if bad_frag:
        print("[!] refusal-witness-coverage: REFUSING — %d site fragment(s) still contain "
              "a FORMAT PLACEHOLDER, which the compiler never prints, so they can only "
              "produce false 'undemonstrated' verdicts: %s. Widen the placeholder split "
              "in sites()." % (len(bad_frag),
                               "; ".join("%s:%d %r" % (r, l, f[:40])
                                         for r, l, f in bad_frag[:3])),
              file=sys.stderr)
        return 2

    # A FIFTH TRUNCATION SHAPE, and a sharper detector than length. `1265`'s row was 109
    # characters — not the 110/108/400 the repair passes looked for — and ended
    # `other.transfer(\ufffd`: the old writer cut the message by BYTES, mid-UTF-8, and the
    # decoder left a REPLACEMENT CHARACTER behind. So the site it witnesses read as
    # undemonstrated for three generations and the length-based sweep could not see it.
    # U+FFFD in a censused message is unambiguous evidence of a byte-truncated write (no
    # PyCSL diagnostic contains one), so it is a REFUSAL like the length cut.
    mangled = [w for w, c, m in rows if c == "REFUSAL" and "\ufffd" in m]
    if mangled:
        print("[!] refusal-witness-coverage: REFUSING — %d censused message(s) contain a "
              "U+FFFD REPLACEMENT CHARACTER (%s%s), which means the row was cut mid-UTF-8 "
              "by a byte-truncating write. The tail after the cut can never match a site "
              "fragment. Re-run those witnesses and store the full message."
              % (len(mangled), ", ".join(mangled[:3]), " …" if len(mangled) > 3 else ""),
              file=sys.stderr)
        return 2

    cut = [w for w, c, m in rows if c == "REFUSAL" and len(m) == CENSUS_TRUNC]
    if cut:
        print("[!] refusal-witness-coverage: REFUSING — %d censused message(s) are exactly "
              "%d characters long, the writer's cap, so they were TRUNCATED: %s%s. A "
              "truncated message silently un-witnesses every site whose fragment falls "
              "past the cut. Re-run those witnesses and store the full message."
              % (len(cut), CENSUS_TRUNC, ", ".join(cut[:3]),
                 " …" if len(cut) > 3 else ""), file=sys.stderr)
        return 2

    refusal_msgs = [m for _w, c, m in rows if c == "REFUSAL"]
    xpass = [w for w, c, _m in rows if c == "XPASS"]
    witnessed, unwitnessed, elsewhere, unmatchable = [], [], [], []
    for rel, line, exc, code, frag in st:
        hit = bool(frag) and any(frag[:60] in m for m in refusal_msgs)
        if hit:
            witnessed.append((rel, line, exc, code, frag))
        elif code in NOT_SOURCE_REACHABLE:
            elsewhere.append((rel, line, exc, code, frag))
        elif not frag:
            unmatchable.append((rel, line, exc, code, frag))
        else:
            unwitnessed.append((rel, line, exc, code, frag))

    print("[*] refusal-witness-coverage: %d raise site(s) in the compiler, %d witness(es) "
          "censused (%d refusals); %d site(s) DEMONSTRATED to fire, %d not."
          % (len(st), len(rows), len(refusal_msgs), len(witnessed), len(unwitnessed)))
    if elsewhere:
        print("[*]   plus %d refusal(s) NOT REACHABLE from a `.py` source file, "
              "demonstrated executably by bin/check-ir-schema-refusals.py instead."
              % len(elsewhere))
    if unmatchable:
        print("[*]   plus %d refusal(s) UNMATCHABLE by this instrument: their message has "
              "no string literal of 25+ characters, so no witness can ever mark them "
              "demonstrated. Closing them is a compiler/census change, not a corpus one."
              % len(unmatchable))

    if args.list_unwitnessed or args.verbose:
        for rel, line, exc, code, frag in unwitnessed[:60]:
            print("    unwitnessed  %-44s:%-6d %-22s %s"
                  % (rel, line, code or "-", frag[:50]))
        for rel, line, exc, code, frag in elsewhere:
            print("    elsewhere    %-44s:%-6d %-22s not source-reachable; see "
                  "bin/check-ir-schema-refusals.py" % (rel, line, code or "-"))
        for rel, line, exc, code, frag in unmatchable:
            print("    unmatchable  %-44s:%-6d %-22s no literal of 25+ chars in the raise"
                  % (rel, line, code or "-"))

    rc = 0
    for w in xpass:
        print("[!]   XPASS IN THE CENSUS: %s is `# pycsl-expected: FAIL` and VERIFIED."
              % w, file=sys.stderr)
        rc = 1
    if len(witnessed) < MIN_WITNESSED:
        print("[!]   WITNESSED FLOOR BROKEN: %d < %d — a refusal that used to be "
              "demonstrated no longer is." % (len(witnessed), MIN_WITNESSED),
              file=sys.stderr)
        rc = 1
    if len(unmatchable) > MAX_UNMATCHABLE:
        print("[!]   UNMATCHABLE CEILING BROKEN: %d > %d — a refusal lost the literal that "
              "made it matchable, or a new one landed with none. This count may only "
              "shrink." % (len(unmatchable), MAX_UNMATCHABLE), file=sys.stderr)
        rc = 1
    if len(unwitnessed) > MAX_UNWITNESSED:
        print("[!]   UNWITNESSED CEILING BROKEN: %d > %d — a new refusal landed without a "
              "witness that proves it can fire." % (len(unwitnessed), MAX_UNWITNESSED),
              file=sys.stderr)
        rc = 1

    if rc:
        print("[!] refusal-witness-coverage: NOT OK.", file=sys.stderr)
    else:
        print("[+] refusal-witness-coverage: OK — %d demonstrated, %d undemonstrated "
              "(floor %d / ceiling %d); %d not source-reachable, %d unmatchable "
              "(ceiling %d)."
              % (len(witnessed), len(unwitnessed), MIN_WITNESSED, MAX_UNWITNESSED,
                 len(elsewhere), len(unmatchable), MAX_UNMATCHABLE))
    return rc


if __name__ == "__main__":
    sys.exit(main())
