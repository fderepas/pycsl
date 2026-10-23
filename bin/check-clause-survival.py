#!/usr/bin/env python3
r"""check-clause-survival.py — THE CLAUSE-SURVIVAL PLANE.

THE QUESTION NO OTHER PLANE ASKS: does every `#@ requires` / `#@ ensures` the author wrote
actually REACH the emitted WhyML? Every other gate looks at what the emission CONTAINS.
This one looks for what it is MISSING, by comparing the source clause count against the
emitted one.

The comparison is sound in one direction and that is the whole trick: **the emitter only
ever ADDS `requires` / `ensures` lines** — frame-preservation postconditions (#34), implicit
exception triggers, class invariants, `\result` refinements, the abstract ops' own
contracts. It never merges two source clauses into one line. So

    emitted count < source count   =>   at least one clause did not survive.

The converse is not true (a clause can be emitted as the literal `true` and still be
counted), so this plane is a LOWER BOUND, exactly like `check-emitted-vacuity.py`.

WHAT IT FOUND ON ITS FIRST RUN (route #15, relaunch #43): 25 of 820 corpus files carry a
deficit, and corpus 0706's was `ensures 1 -> 0` with NO CONSTRUCTOR IN THE EMITTED MODULE
AT ALL. `__init__` is never emitted as a function — it is inlined at each allocation site —
so its `#@ requires` and `#@ ensures` are DISCARDED, and

    #@ ensures self.x == 99      over a body `self.x = 0`
    [+] Verification SUCCESS! All contracts formally proven.

61 `__init__` methods across the corpus, the mirror and `src/pycsl_lib` carry such a
contract. The `init_ensures` IR field exists and IS re-checked — but only for classes with
a module-global singleton (`module6_whyml/preamble.py`).

USAGE
    bin/check-clause-survival.py --emit-dir <dir>

`<dir>` holds the emitted `.mlw` for the corpus, e.g. the output of
`bin/byte-diff-sweep.sh`. THE EMISSION MUST BE FRESH: a stale directory makes this plane a
false green, the same way `--emit` does for `check-emitted-vacuity.py`.

RATCHET: the number of files carrying a deficit. It goes down, never up.
"""
import argparse
import io
import os
import re
import sys
import tokenize

CORPUS = "test-suite/corpus/pycsl-reference"

# (#43) 4, and ALL FOUR ARE ROUTE #15 — a constructor contract that never reaches the
# emission. 0661 and 0662 are the ones that show its size: each writes NINETEEN
# non-trivial `#@ requires` on `Inode.__init__` (`\valid(initial, 18)` and eighteen
# per-field range bounds) and every one of them is discarded. 0705 loses a constructor
# `ensures`, 0706 the same. This plane therefore doubles as route #15's tracker: it goes
# to 0 when constructor contracts start being checked. Every one of these is a file
# whose emitted module carries fewer contract clauses than its author wrote. The bulk are
# constructor contracts (`__init__` is inlined, never emitted, so its clauses go nowhere);
# the rest are `requires True` normalizations. LOWER THIS as route #15 is paid off — the
# fix is a checking-only `let <class>__init` emitted beside the inlining.
# (#43) 4 -> 2. Route #15 is CLOSED: Module 6 now emits a checking-only
# `let <class>__init` carrying the declared constructor clauses, so 0705 and 0706's
# deficits are gone. The two that remain are 0661 and 0662, and they remain HONESTLY:
# their `Inode.__init__(self, initial: list)` binds a LIST field from a parameter, which
# `_call_record_constructor` models as the empty-array default rather than the parameter,
# so a check there would be about the modelling gap and not about the contract. They go to
# 0 when a param-dependent non-scalar field is threaded faithfully — the same
# value-model capability routes #13/#17/#18 need.
# (#49) THE TOTAL RATCHET IS NOW DERIVED, NOT HAND-TUNED. It was 2, then 3, and the first
# corpus file added after the classification landed made it 4 — while UNEXPLAINED stayed 0.
# A hand-maintained total has to be edited every time a witness that PINS the dunder gap is
# added, and editing a constant to make a gate green is exactly what rule (k) forbids, so
# the constant had to stop being a constant. The total is therefore `len(KNOWN_DEFICITS)`:
# it can only grow by ADDING A LEDGER ENTRY, and an entry is only honoured when the plane
# can CONFIRM its evidence (the named def exists, is absent from the emission, and carries
# enough clauses to cover the shortfall). The gate that matters is unchanged and is the
# strict one: MAX_UNEXPLAINED = 0.
MAX_DEFICIT_FILES = None    # derived below from KNOWN_DEFICITS

# (#49) THE LEDGER, AND WHY THE BARE COUNT WAS NOT ENOUGH. The ratchet above was 2 and the
# battery found it BROKEN at 3. The third file was
# `1800_gen30_dunder_call_loses_its_contract.py`, added the same evening, whose deficit is
# THE POINT OF THE FILE: `CM.__enter__` carries `#@ ensures \result == 7`, the dunder is
# not emitted as a `let` at all, and the clause goes with it.
#
# Raising the constant to 3 and saying nothing would be rule (k) — re-baselining a gate to
# make it green. What makes 3 honest is that the count is no longer the gate. Each deficit
# file now names the DEF whose disappearance explains it, and the plane CONFIRMS that
# mechanically: the named def must be absent from the emitted module AND must carry enough
# clauses to cover the shortfall. A deficit with no entry, or an entry whose evidence no
# longer holds, is UNEXPLAINED and the plane refuses. The ratchet that matters is therefore
# `MAX_UNEXPLAINED = 0`, which is strictly stronger than "at most 3 files, cause unknown".
#
# All three are ONE PHENOMENON seen twice: A METHOD THE EMITTER DROPS TAKES ITS CONTRACT
# WITH IT. 0661/0662 lose a constructor's nineteen `requires`; 1800 loses a dunder's single
# `ensures`. The directions of risk differ and both are recorded below.
KNOWN_DEFICITS = {
    # Route #15 residue, already documented above: `Inode.__init__(self, initial: list)`
    # binds a LIST field from a parameter, which `_call_record_constructor` models as the
    # empty-array default rather than the parameter, so the checking-only `let inode__init`
    # route #15 added is not emitted here. Nineteen `requires` go nowhere. Closes when a
    # param-dependent non-scalar field is threaded faithfully (routes #13/#17/#18).
    "0661.py": ("__init__", "route #15 residue: param-dependent list field, no let inode__init"),
    "0662.py": ("__init__", "route #15 residue: param-dependent list field, no let inode__init"),
    # (#49) gen #31 — THE TWO DUNDER ENTRIES THAT USED TO LIVE HERE ARE GONE, AND THAT IS
    # THE POINT OF WRITING A CLOSE CONDITION DOWN. Both said "dunder dropped from
    # emission", both named the same close condition ("emit dunders"), and route #219's
    # build met it in this same generation. MEASURED before removing them, by emitting each
    # driver and reading the `.mlw`:
    #   1807 — `let only____len__ (self: only) : int ensures { (result >= 5) }`. The
    #          clause reaches the module; the deficit is gone.
    #   1800 — `let cm____enter__` is emitted AND the explicit call site's stub now reads
    #          `val c___enter___0 () : int ensures { (result = 7) }`. It is no longer
    #          contractless, which was the whole content of the entry.
    # A stale allow-list entry is a gate tolerating exactly the failure it exists to catch,
    # so they come out and the plane tightens by two. Found by re-reading the allow-lists
    # of every plane rather than by the plane itself — an exemption never goes red on its
    # own.
}
MAX_UNEXPLAINED = 0


def _emitted_idents(text):
    """Every `let` / `val` name in an emitted module."""
    return set(re.findall(r"\b(?:let|val)\s+(?:rec\s+)?(?:ghost\s+)?(?:function\s+)?"
                          r"(?:predicate\s+)?([A-Za-z_][A-Za-z0-9_']*)", text))


def _def_is_emitted(name, idents):
    """Is source `def name` present in the emission?

    Module-level functions keep their name (`_pack_inode`); methods are prefixed with the
    lowercased class (`inode__pack`). A DUNDER CALL SITE is minted as `c___enter___0`,
    which must NOT count as the method being emitted — hence the exact `__`-suffix match
    rather than a substring test.
    """
    return any(i == name or i.endswith("__" + name) for i in idents)


def _source_defs(path):
    """[(def_name, requires, ensures)] — clauses attributed to the def they sit above.

    Same COMMENT-token discipline as `_source_counts`: a `#@` inside a docstring is text,
    not a clause, and counting it is how the route-#12 census reported 95 hits where the
    truth was 0.
    """
    src = open(path, encoding="utf-8").read()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return None
    defs = []          # (lineno, name)
    pending = []       # (lineno, kind)
    prev = None
    for t in toks:
        if t.type == tokenize.NAME and prev == "def":
            defs.append((t.start[0], t.string))
        if t.type == tokenize.NAME:
            prev = t.string
        elif t.type == tokenize.COMMENT:
            st = t.string.strip()
            if st.startswith("#@ requires") and st.split(None, 2)[2:] != ["True"]:
                pending.append((t.start[0], "requires"))
            elif st.startswith("#@ ensures") and st.split(None, 2)[2:] != ["True"]:
                pending.append((t.start[0], "ensures"))
    out = []
    for i, (dline, dname) in enumerate(defs):
        prev_line = defs[i - 1][0] if i else 0
        req = sum(1 for (l, k) in pending if prev_line < l < dline and k == "requires")
        ens = sum(1 for (l, k) in pending if prev_line < l < dline and k == "ensures")
        out.append((dname, req, ens))
    return out


def _source_counts(path):
    src = open(path, encoding="utf-8").read()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return None
    req = ens = 0
    for t in toks:
        if t.type != tokenize.COMMENT:
            continue
        st = t.string.strip()
        # real COMMENT tokens only — a line scan counts `#@` text inside docstrings, which
        # is how the route-#12 census first reported 95 hits where the truth was 0.
        # A `#@ requires True` / `#@ ensures True` carries no information and IS
        # legitimately normalized away (corpus 0950's only contract is exactly that, and
        # its emitted `let rec function has_bad` correctly has no clause at all). Counting
        # them made the plane's ratchet mostly noise. Excluded, so what remains is the
        # signal: a clause that says something and did not arrive.
        if st.startswith("#@ requires") and st.split(None, 2)[2:] != ["True"]:
            req += 1
        elif st.startswith("#@ ensures") and st.split(None, 2)[2:] != ["True"]:
            ens += 1
    return req, ens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", required=True,
                    help="directory of FRESHLY emitted corpus .mlw (bin/byte-diff-sweep.sh)")
    ap.add_argument("--corpus", default=CORPUS)
    ap.add_argument("--max-deficit-files", type=int, default=None,
                    help="override the DERIVED total ratchet (len(KNOWN_DEFICITS))")
    ap.add_argument("--verbose", action="store_true")
    # (#49) TWO SELF-TESTS, because a ledger that cannot be shown to REFUSE is a ledger
    # that only ever makes things green. Each mutates the ledger for one run and the
    # expected outcome is rc=1.
    ap.add_argument("--selftest-forget", metavar="FILE",
                    help="drop FILE's ledger entry (its deficit must become UNEXPLAINED)")
    ap.add_argument("--selftest-misname", metavar="FILE",
                    help="repoint FILE's entry at a def that IS emitted (must be refused)")
    args = ap.parse_args()
    if args.max_deficit_files is None:
        args.max_deficit_files = len(KNOWN_DEFICITS)
    if args.selftest_forget:
        KNOWN_DEFICITS.pop(args.selftest_forget, None)
    if args.selftest_misname:
        _e = KNOWN_DEFICITS.get(args.selftest_misname)
        if _e:
            KNOWN_DEFICITS[args.selftest_misname] = ("pack", _e[1] + " [SELFTEST]")

    deficits = []
    compared = 0
    for f in sorted(os.listdir(args.corpus)):
        if not f.endswith(".py"):
            continue
        mlw = os.path.join(args.emit_dir, f[:-3] + ".mlw")
        if not os.path.exists(mlw):
            continue          # refused on purpose (a `pycsl-expected: FAIL` witness)
        # (#49) A `pycsl-expected: FAIL` WITNESS THAT STILL EMITS IS NOT A CLAIM EITHER.
        # The skip above catches the witnesses refused at EMISSION; a witness that emits
        # and then fails at the PROVER reached this loop and was counted. Its clauses are
        # not claims this project makes — the file asserts the pipeline must NOT prove it —
        # so a deficit there says nothing about a clause being lost from a proof anyone
        # relies on. MEASURED (gen #29): `1315_route116_...` and `1317_route116_...` are
        # exactly that, and counting them had left this ratchet BROKEN (4 > 2) since route
        # #116's witnesses landed, unnoticed, because nothing runs this gate. Excluding
        # them restores the EXISTING ratchet of 2 rather than raising it (rule (k)).
        _src_head = open(os.path.join(args.corpus, f), encoding="utf-8",
                         errors="replace").read(4096)
        if "# pycsl-expected: FAIL" in _src_head:
            continue
        sc = _source_counts(os.path.join(args.corpus, f))
        if sc is None:
            continue
        s_req, s_ens = sc
        text = open(mlw, encoding="utf-8").read()
        # COUNT OCCURRENCES ANYWHERE, NOT AT LINE START. The first version of this
        # plane anchored both patterns at `^\s*` and immediately reported a
        # `ensures 5 -> 0` deficit on corpus 0964 — which was ITS OWN BUG: the emitter
        # writes `requires { true } ensures { true }` on ONE line for a leaf method, so
        # every such `ensures` was invisible to the count. Lesson (bd) on the instrument
        # this very plane was written to embody.
        e_req = len(re.findall(r"\brequires\s*\{", text))
        e_ens = len(re.findall(r"\bensures\s*\{", text))
        compared += 1
        if e_req < s_req or e_ens < s_ens:
            deficits.append((f, s_req, e_req, s_ens, e_ens))

    print("[*] clause-survival: %d corpus file(s) compared; %d carry a DEFICIT "
          "(an emitted clause count below the source count)." % (compared, len(deficits)))
    if args.verbose or len(deficits) > args.max_deficit_files:
        for d in deficits:
            print("    DEFICIT  %-50s requires %d->%d  ensures %d->%d" % d)

    # (#49) CLASSIFY, DON'T JUST COUNT. Each deficit must be EXPLAINED by a ledger entry
    # naming a def that (a) is genuinely absent from the emitted module and (b) carries
    # enough clauses to cover the shortfall. Both halves are checked here rather than
    # believed, so an entry cannot keep a file green after its cause has changed.
    unexplained, explained = [], []
    for d in deficits:
        f, s_req, e_req, s_ens, e_ens = d
        entry = KNOWN_DEFICITS.get(f)
        if entry is None:
            unexplained.append((d, "no KNOWN_DEFICITS entry"))
            continue
        want, why = entry
        text = open(os.path.join(args.emit_dir, f[:-3] + ".mlw"), encoding="utf-8").read()
        idents = _emitted_idents(text)
        sdefs = _source_defs(os.path.join(args.corpus, f)) or []
        named = [(n, r, e) for (n, r, e) in sdefs if n == want]
        if not named:
            unexplained.append((d, "entry names `%s`, which the source does not define" % want))
            continue
        if _def_is_emitted(want, idents):
            unexplained.append((d, "entry names `%s`, but it IS emitted — the clause was "
                                   "lost in place, which is the dangerous case" % want))
            continue
        gone_req = sum(r for (_n, r, _e) in named)
        gone_ens = sum(e for (_n, _r, e) in named)
        if gone_req < max(0, s_req - e_req) or gone_ens < max(0, s_ens - e_ens):
            unexplained.append((d, "`%s` is absent but carries only %d requires / %d "
                                   "ensures, short of the %d / %d missing"
                                % (want, gone_req, gone_ens,
                                   max(0, s_req - e_req), max(0, s_ens - e_ens))))
            continue
        explained.append((d, want, why))

    for (d, want, why) in explained:
        print("    EXPLAINED  %-50s def `%s` absent from the emission — %s"
              % (d[0], want, why))
    for (d, reason) in unexplained:
        print("    UNEXPLAINED  %-48s %s" % (d[0], reason))

    stale = sorted(set(KNOWN_DEFICITS) - {d[0] for d in deficits})
    for f in stale:
        print("[+] clause-survival: %s no longer carries a deficit — delete its "
              "KNOWN_DEFICITS entry." % f)

    if compared == 0:
        print("[!] clause-survival: ZERO files compared — the --emit-dir is empty or "
              "stale. That is a FALSE GREEN, not a pass.")
        return 1
    if len(unexplained) > MAX_UNEXPLAINED:
        print("[!] clause-survival: %d UNEXPLAINED deficit(s) — a clause the author wrote "
              "did not reach the emitted module, and no ledger entry accounts for it. The "
              "run will still report 'All contracts formally proven'. Diagnose it and add "
              "a KNOWN_DEFICITS entry naming the dropped def, or fix the emitter."
              % len(unexplained))
        return 1
    if len(deficits) > args.max_deficit_files:
        print("[!] clause-survival: RATCHET BROKEN — %d > %d. A clause the author wrote "
              "did not reach the emitted module, and the run will still report 'All "
              "contracts formally proven'." % (len(deficits), args.max_deficit_files))
        return 1
    if len(deficits) < args.max_deficit_files:
        # With a DERIVED ratchet this means a ledger entry no longer has a deficit behind
        # it; the stale-entry report above already names which, and deleting it lowers the
        # ratchet automatically. Nothing to hand-edit.
        print("[+] clause-survival: %d deficit(s) against %d ledger entr(ies) — an entry "
              "above is stale; delete it." % (len(deficits), args.max_deficit_files))
    print("[+] clause-survival: OK — measured %d deficit file(s) of %d compared "
          "(%d ledgered, 0 unexplained)."
          % (len(deficits), compared, args.max_deficit_files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
