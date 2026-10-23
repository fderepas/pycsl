#!/usr/bin/env python3
"""SOUNDNESS PLANE — every `exception_model.TRIGGERS` row must actually be REACHABLE.

WHY THIS EXISTS (route #65, relaunch #55). `TRIGGERS` maps an IR operation to the
obligations that must hold for it NOT to raise. Every row reads like coverage. Four of them
were consulted by NOTHING:

    ("call", "divmod")  ("attr_call", "index")  ("attr_call", "pop")  ("call", "next")

`divmod(a, 0)[0]` under `#@ no_exception ZeroDivisionError` PROVED while CPython raises,
because the row that would have caught it is never looked up. The contrast that makes it
crisp: `d[5]` under `#@ no_exception KeyError` correctly does NOT prove, through the
`("map_get", None)` row — same machinery, same exception family, same shape of condition.
The only difference is whether the emitter asks for the row.

A row that is never consulted is a soundness claim that is never checked. So is a row whose
condition is the literal `"true"`: the `.index` row was exactly that, and `xs.index(5)` on a
list NOT containing 5 proved exactly as readily as `xs.index(1)` on one that does — zero
discrimination.

WHAT IT CHECKS. Every key in `TRIGGERS` must be either
  (a) CONSULTED — passed as an op-key to `_wrap_with_no_exception_assert` or
      `_maybe_emit_no_exception_assert` somewhere in `src/pycsl/`, or
  (b) REFUSED   — listed in the route #65 orphan map in
      `module6_whyml/functions.py`, which raises rather than discharge a claim
      nothing checks.
and additionally: a row whose condition is the literal `"true"` must be in (b), never in (a),
because a tautology discharges unconditionally.

METHOD AND ITS LIMITS. Both scans are textual over `src/pycsl/**/*.py`, matching the
`("x", "y")` / `("x", None)` tuple literals near the two injection helpers and inside the
orphan map. A key assembled dynamically at run time would be missed — none is today, and a
dynamic key would itself be worth a finding. The zero-input guard below is the #44 rule: a
gate that cannot tell "nothing is wrong" from "I looked at nothing" is not a gate.
"""
import io
import os
import re
import sys
import tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "pycsl"))

from exception_model import TRIGGERS  # noqa: E402

SRC = os.path.join(ROOT, "src", "pycsl")
INJECTORS = ("_wrap_with_no_exception_assert", "_maybe_emit_no_exception_assert")
ORPHAN_MARKER = "_R65_ORPHANS"
KEY_RE = re.compile(r'\(\s*"([A-Za-z_]+)"\s*,\s*(?:"([^"]*)"|None)\s*\)')
# A key whose SUBKIND is a variable — `("binop", raw_op)` — consults every row of that KIND,
# because the variable ranges over the operator at run time. Without this the plane reports
# all seven arithmetic rows as dead, which is the opposite of the truth. Found by running the
# plane against a tree where those rows are demonstrably live (`a // 0` under
# `no_exception ZeroDivisionError` correctly fails to prove).
#
# **THIS APPROVAL IS A KIND-LEVEL ASSUMPTION, AND IT IS THE PLANE'S SHARPEST LIMIT.** It is
# sound only if EVERY emission path for that kind wraps. That was NOT true when it was
# written: `div`/`mod` wrapped, but the bitwise/power path did not, so the `("binop","<<")`
# and `("binop",">>")` rows — which have carried `non_neg_shift` all along — were never
# injected, and `1 << -1` PROVED under `#@ no_exception \all` while CPython raises
# `ValueError`. The plane called them live because ONE binop site used a dynamic key. Route
# #68 fixed the EMITTER (that path now wraps) rather than weakening the check, so the
# assumption is now true rather than merely convenient. If a new binop emission path is ever
# added, it must wrap too, or this approval silently starts lying again.
DYNKEY_RE = re.compile(r'\(\s*"([A-Za-z_]+)"\s*,\s*([a-z_][A-Za-z0-9_]*)\s*\)')


def _norm(m):
    return (m.group(1), m.group(2) if m.group(2) is not None else None)


def _strip_comments(src: str) -> str:
    """Return `src` with `#` COMMENTS removed, string literals preserved.

    THIS IS LOAD-BEARING, and it was found the hard way: the first version of this plane
    scanned raw text, and the big explanatory comment in `module6_whyml/functions.py` — which
    names both injector helpers and then lists the very op-keys they do NOT consult — was
    read as EVIDENCE OF CONSULTATION. The plane reported green with the route #65 refusal
    deliberately removed. **A gate that counts its own documentation as coverage is worse
    than no gate**, which is precisely the defect class this plane exists to catch, so it had
    to stop doing it itself.
    """
    try:
        out, last = [], (1, 0)
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                continue
            (srow, scol), (erow, ecol) = tok.start, tok.end
            if srow > last[0]:
                out.append("\n" * (srow - last[0]))
                last = (srow, 0)
            if scol > last[1]:
                out.append(" " * (scol - last[1]))
            out.append(tok.string)
            last = (erow, ecol)
        return "".join(out)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        # Never let a tokenizer hiccup turn into a silent pass.
        return src


def main():
    blobs = []
    for dirpath, _dirs, files in os.walk(SRC):
        for fn in files:
            if fn.endswith(".py"):
                with open(os.path.join(dirpath, fn), encoding="utf-8") as fh:
                    blobs.append(_strip_comments(fh.read()))
    if len(blobs) < 20:
        print("[!] trigger-rows-live: only %d source file(s) scanned — the walk is broken, "
              "NOT A PASS." % len(blobs), file=sys.stderr)
        return 2

    consulted, refused, dyn_kinds = set(), set(), set()
    for text in blobs:
        for inj in INJECTORS:
            # `inj(` — an actual CALL, not a mention.
            for hit in re.finditer(re.escape(inj) + r"\s*\(", text):
                window = text[hit.end():hit.end() + 240]
                for m in KEY_RE.finditer(window):
                    consulted.add(_norm(m))
                for m in DYNKEY_RE.finditer(window):
                    if m.group(2) not in ("None",):
                        dyn_kinds.add(m.group(1))
        idx = text.find(ORPHAN_MARKER)
        if idx != -1:
            for m in KEY_RE.finditer(text[idx:idx + 800]):
                refused.add(_norm(m))

    if not consulted:
        print("[!] trigger-rows-live: no op-key was found at ANY injection site — the scan "
              "is broken, NOT A PASS.", file=sys.stderr)
        return 2

    dead, tautologies = [], []
    for key, rows in TRIGGERS.items():
        covered = key in consulted or key in refused or key[0] in dyn_kinds
        if not covered:
            dead.append(key)
        for exc, cond in rows:
            if cond.strip() == "true" and key not in refused:
                # A tautology is only acceptable when the construct is refused outright.
                tautologies.append((key, exc))

    _dyn = {k for k in TRIGGERS if k[0] in dyn_kinds and k not in consulted}
    print("[*] trigger-rows-live: %d row(s); %d consulted by a literal op-key, %d via a "
          "dynamic key (kinds: %s), %d refused outright."
          % (len(TRIGGERS), len(consulted & set(TRIGGERS)), len(_dyn),
             ",".join(sorted(dyn_kinds)) or "-", len(refused & set(TRIGGERS))))
    rc = 0
    for key in sorted(map(str, dead)):
        print("[!]   DEAD ROW (consulted by nothing, refused by nothing): %s" % key,
              file=sys.stderr)
        rc = 1
    for key, exc in sorted(map(lambda t: (str(t[0]), t[1]), tautologies)):
        print("[!]   TAUTOLOGY (condition is literally `true`, so it always discharges): "
              "%s -> %s" % (key, exc), file=sys.stderr)
        rc = 1
    if rc:
        print("[!] trigger-rows-live: a row that is never consulted, or whose condition is "
              "`true`, is a soundness claim that is never checked (route #65). Wire it at "
              "the emitter, give it a real condition, or refuse the construct.",
              file=sys.stderr)
        return rc
    print("[+] trigger-rows-live: OK — every trigger row is consulted or refused, and no "
          "row discharges on a tautology.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
