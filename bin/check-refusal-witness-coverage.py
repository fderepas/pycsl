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
import subprocess
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENSUS = os.path.join(ROOT, "bin", "refusal-witness-census.tsv")
MIN_SITES = 150           # 195 at the first measurement
MIN_WITNESSED = 68        # 58 at the first joined measurement; 67 after TEN witnesses were
                          # written the same day (Final F1/F2, three lemma arms, two
                          # assigns-region arms, `\length` on a dict, `\result` in a
                          # check, the happy `except` typo); may only grow
MAX_UNWITNESSED = 130     # 140 -> 131 with those ten; may only shrink


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
                parts = [p.strip() for p in literal_parts(n.exc) if len(p.strip()) >= 25]
                frag = max(parts, key=len)[:80] if parts else ""
                out.append((os.path.relpath(f, ROOT), n.lineno, name, code, frag))
    return out


def census():
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
                                                    msg.replace("\t", " ")[:400]))
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

    refusal_msgs = [m for _w, c, m in rows if c == "REFUSAL"]
    xpass = [w for w, c, _m in rows if c == "XPASS"]
    witnessed, unwitnessed = [], []
    for rel, line, exc, code, frag in st:
        hit = bool(frag) and any(frag[:60] in m for m in refusal_msgs)
        (witnessed if hit else unwitnessed).append((rel, line, exc, code, frag))

    print("[*] refusal-witness-coverage: %d raise site(s) in the compiler, %d witness(es) "
          "censused (%d refusals); %d site(s) DEMONSTRATED to fire, %d not."
          % (len(st), len(rows), len(refusal_msgs), len(witnessed), len(unwitnessed)))

    if args.list_unwitnessed or args.verbose:
        for rel, line, exc, code, frag in unwitnessed[:60]:
            print("    unwitnessed  %-44s:%-6d %-22s %s"
                  % (rel, line, code or "-", frag[:50]))

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
    if len(unwitnessed) > MAX_UNWITNESSED:
        print("[!]   UNWITNESSED CEILING BROKEN: %d > %d — a new refusal landed without a "
              "witness that proves it can fire." % (len(unwitnessed), MAX_UNWITNESSED),
              file=sys.stderr)
        rc = 1

    if rc:
        print("[!] refusal-witness-coverage: NOT OK.", file=sys.stderr)
    else:
        print("[+] refusal-witness-coverage: OK — %d demonstrated, %d undemonstrated "
              "(floor %d / ceiling %d)."
              % (len(witnessed), len(unwitnessed), MIN_WITNESSED, MAX_UNWITNESSED))
    return rc


if __name__ == "__main__":
    sys.exit(main())
