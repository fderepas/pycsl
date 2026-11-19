#!/usr/bin/env python3
r"""check-mirror-clause-survival — does every NON-TRIVIAL `#@ requires` / `#@ ensures` a MIRROR
method declares REACH that method's declaration in its DEFINING module's emission?

WHY IT EXISTS (#49, gen #35 — backlog #74's generalisation). Gen #34 found that Module 6's 25
`*_bespoke` lowerings hard-coded `requires { true } ensures { true }` and silently discarded the
declared contract, and built `check-bespoke-contract-discard.py` to count it. That gate is keyed
on the EMITTER (the bespoke dispatch keys), and the same census found the key incomplete:
`generic_fold.py` carries ~48 `emit_*_group` templaters with the same literal spelling, and
`_emit_term_pp_delegation` is a latent third producer. Gen #34's own conclusion: **stop keying on
the emitter and measure from the EMISSION**, which covers emitter paths nobody has written yet.
This is that plane. It is a MIRROR-population twin of `check-clause-survival.py` (which compares
per-FILE counts over the CORPUS).

WHAT IT MEASURES. For every mirror `def` carrying at least one non-trivial (`!= True`)
`#@ requires`/`#@ ensures`, it locates `<class>__<def>` (the emitter's one naming rule,
`Module5_IREmitter.py`: `f"{cls.lower()}__{node.name}"`) in the emission of THE SAME FILE — the
defining module, never an importer: backlog #60a drops an importer stub's `\result["key"]`
clauses DELIBERATELY and soundly (a `val` with fewer `ensures` assumes less) — and compares
declared vs emitted counts per kind. The emitter only ever ADDS clauses (frame preservation,
class invariants, triggers) and never merges two, so

    emitted non-trivial < declared non-trivial   =>   a declared clause did not survive.

A LOWER BOUND, like its corpus twin: a clause emitted as a different but equally weak formula
is invisible. Emitted `self.f = old self.f` preservation lines are not counted as survivors (the
emitter adds them; counting them would mask a discarded `ensures`).

FIRST MEASUREMENT (gen #35, at 7b1398a9): population 242, located **242**, DISCARD **0**. (A
first cut located 230: the 12 misses were MODULE-LEVEL defs, which the emitter spells either
module-prefixed or bare — both are tried. `MAX_UNLOCATED = 0` keeps a future key drift loud.)
So gen #34's generic_fold residue discards NO requires/ensures in the defining emission — its
one genuine discard is an `assigns`, which is `check-assigns-writes-survival`'s population.

NEGATIVE-TESTED IN-TREE: `--self-test` copies the emission, deletes the first located
declaration's first non-trivial `ensures` line, and requires DISCARD to fire on exactly it. A
gate whose population of defects is empty has checked nothing and looks exactly like one that
passed; this one is made to fire on demand.

Usage:
    bin/check-mirror-clause-survival.py --emit-dir <dir>   # <dir> from bin/mirror-emit-sweep.sh
    bin/check-mirror-clause-survival.py --emit-dir <dir> --self-test
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")

MAX_DISCARD = 0          # may NEVER rise: a declared claim the artifact does not prove
MIN_LOCATED = 220        # measured 242; a key drift shows up here as a collapse
MAX_UNLOCATED = 0        # measured 0 (12 before module-level defs tried bare); a RISE narrows the population

CLAUSE = re.compile(r"^\s*#@\s*(requires|ensures)\s+(.*?)\s*$")
TRIVIAL = {"True", "true"}
PRESERVE = re.compile(r"^self\.\w+\s*=\s*old self\.\w+$")


def source_clauses():
    """-> list of (relpath, key, candidate-symbols, {'requires': n, 'ensures': n})."""
    out = []
    for dp, dn, fns in os.walk(MIRROR):
        dn[:] = sorted(d for d in dn if d != "__pycache__")
        for fn in sorted(fns):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dp, fn)
            rel = os.path.relpath(path, MIRROR)
            key = rel[:-3].replace(os.sep, "__")
            lines = open(path, encoding="utf-8").read().splitlines()
            pend = {"requires": 0, "ensures": 0}
            for i, ln in enumerate(lines):
                m = CLAUSE.match(ln)
                if m:
                    if m.group(2) not in TRIVIAL:
                        pend[m.group(1)] += 1
                    continue
                s = ln.strip()
                if not s or s.startswith("#") or s.startswith("@"):
                    continue
                md = re.match(r"^(\s*)def\s+(\w+)\s*\(", ln)
                if md and (pend["requires"] or pend["ensures"]):
                    cls = None
                    if md.group(1):
                        for k in range(i, -1, -1):
                            mc = re.match(r"^class\s+(\w+)", lines[k])
                            if mc:
                                cls = mc.group(1)
                                break
                    if cls:
                        syms = (f"{cls.lower()}__{md.group(2)}",)
                    else:
                        # A MODULE-LEVEL def is emitted either module-prefixed
                        # (`module5_iremitter__generate_json`) or bare (`ir_has_key`); try both,
                        # prefixed first.
                        syms = (f"{os.path.basename(rel)[:-3].lower()}__{md.group(2)}",
                                md.group(2))
                    out.append((rel, key, syms, dict(pend)))
                pend = {"requires": 0, "ensures": 0}
    return out


def _clauses_of(block):
    """Every `requires { … }` / `ensures { … }` in a contract block, brace-matched (a block
    can put two on one line, and a clause body can contain braces)."""
    res = []
    for m in re.finditer(r"\b(requires|ensures)\s*\{", block):
        depth, j = 1, m.end()
        while j < len(block) and depth:
            depth += {"{": 1, "}": -1}.get(block[j], 0)
            j += 1
        res.append((m.group(1), block[m.end():j - 1].strip()))
    return res


def decl_block(text, syms):
    if isinstance(syms, str):
        syms = (syms,)
    m = None
    for sym in syms:
        m = re.search(r"^\s*(?:let|val|with)\s+(?:function\s+|rec\s+|ghost\s+|predicate\s+)*"
                      + re.escape(sym) + r"\s*\(", text, re.M)
        if m:
            break
    if not m:
        return None
    seg = text[m.end(): m.end() + 40000]
    stop = re.search(r"^\s*(?:=|let\s|val\s|with\s|end\b)|^\s*=\s*$|\n\s*=\n", seg, re.M)
    return seg[:stop.start()] if stop else seg


def measure(emit_dir, src):
    located, unlocated, discards = 0, [], []
    cache = {}
    for rel, key, sym, decl in src:
        if key not in cache:
            # TWO naming conventions are in circulation and both are load-bearing:
            # `bin/mirror-emit-sweep.sh` joins path components with `__`, the shared emission
            # of `bin/run-soundness-planes.sh` with ONE `_`. Accept either (measured: keying
            # on `__` alone located 1 of 242 in the battery's emission — a refusal, rc=2).
            cache[key] = None
            for cand in (key, rel[:-3].replace(os.sep, "_")):
                mf = os.path.join(emit_dir, cand + ".mlw")
                if os.path.exists(mf):
                    cache[key] = open(mf, encoding="utf-8").read()
                    break
        text = cache[key]
        blk = decl_block(text, sym) if text is not None else None
        if blk is None:
            unlocated.append((rel, sym))
            continue
        located += 1
        got = {"requires": 0, "ensures": 0}
        for kind, body in _clauses_of(blk):
            if body == "true" or (kind == "ensures" and PRESERVE.match(body)):
                continue
            got[kind] += 1
        for kind in ("requires", "ensures"):
            if got[kind] < decl[kind]:
                discards.append((rel, sym, kind, decl[kind], got[kind]))
    return located, unlocated, discards


def emit_fresh():
    d = tempfile.mkdtemp(prefix="mcsurv_")
    r = subprocess.run(["bash", os.path.join(ROOT, "bin", "mirror-emit-sweep.sh"), d],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
        return None
    return d


def self_test(emit_dir, src):
    located, _, base = measure(emit_dir, src)
    tmp = tempfile.mkdtemp(prefix="mcsurv_selftest_")
    try:
        for f in os.listdir(emit_dir):
            if f.endswith(".mlw"):
                shutil.copy2(os.path.join(emit_dir, f), os.path.join(tmp, f))
        for rel, key, sym, decl in src:
            if not decl["ensures"]:
                continue
            p = os.path.join(tmp, key + ".mlw")
            if not os.path.exists(p):
                p = os.path.join(tmp, rel[:-3].replace(os.sep, "_") + ".mlw")
            if not os.path.exists(p):
                continue
            t = open(p, encoding="utf-8").read()
            blk = decl_block(t, sym)
            if blk is None:
                continue
            target = next((b for k, b in _clauses_of(blk)
                           if k == "ensures" and b != "true" and not PRESERVE.match(b)), None)
            if target is None:
                continue
            start = t.index(blk)
            # neutralise exactly one clause body: replace it with `true`
            new_blk = blk.replace(target, "true", 1)
            open(p, "w", encoding="utf-8").write(t[:start] + new_blk + t[start + len(blk):])
            _, _, after = measure(tmp, src)
            hit = [d for d in after if d[1] == sym and d[2] == "ensures"]
            if len(after) == len(base) + 1 and hit:
                print("[+] mirror-clause-survival --self-test: neutralised one `ensures` of %s "
                      "in %s.mlw -> DISCARD fired on exactly it (%d -> %d). The arm is LIVE."
                      % (sym[0], key, len(base), len(after)))
                return 0
            print("[!] mirror-clause-survival --self-test: neutralised one `ensures` of %s and "
                  "DISCARD did not fire on it (%d -> %d). The arm is INERT."
                  % (sym[0], len(base), len(after)), file=sys.stderr)
            return 1
        print("[!] mirror-clause-survival --self-test: no located declaration with an `ensures` "
              "to neutralise — INCONCLUSIVE, which is a failure.", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", help="mirror emission (bin/mirror-emit-sweep.sh); emitted "
                                       "fresh into a temp dir when omitted")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    own = None
    emit_dir = a.emit_dir
    if not emit_dir:
        own = emit_dir = emit_fresh()
        if emit_dir is None:
            print("[!] mirror-clause-survival: could not emit the mirror.", file=sys.stderr)
            return 2
    try:
        src = source_clauses()
        if a.self_test:
            return self_test(emit_dir, src)
        located, unlocated, discards = measure(emit_dir, src)
        print("[*] mirror-clause-survival: %d mirror def(s) declare a non-trivial requires/"
              "ensures; %d located in their DEFINING emission, %d unlocated (ceiling %d); "
              "DISCARD %d (ceiling %d)."
              % (len(src), located, len(unlocated), MAX_UNLOCATED, len(discards), MAX_DISCARD))
        if a.verbose:
            for rel, sym in unlocated:
                print("    UNLOCATED  %s  %s" % (rel, sym[0]))
        rc = 0
        if located < MIN_LOCATED:
            print("[!] mirror-clause-survival: only %d located (< %d) — the name key or the "
                  "emission is broken; this gate cannot tell 'nothing is wrong' from 'I looked "
                  "at nothing'." % (located, MIN_LOCATED), file=sys.stderr)
            return 2
        if len(unlocated) > MAX_UNLOCATED:
            print("[!] mirror-clause-survival: %d unlocated > %d — the population narrowed."
                  % (len(unlocated), MAX_UNLOCATED), file=sys.stderr)
            for rel, sym in unlocated:
                print("      %s  %s" % (rel, sym[0]), file=sys.stderr)
            rc = 1
        if len(discards) > MAX_DISCARD:
            print("[!] mirror-clause-survival: %d declared clause kind(s) did not survive into "
                  "the defining emission:" % len(discards), file=sys.stderr)
            for rel, sym, kind, d, g in discards:
                print("      %s  %s  %s declared %d emitted %d" % (rel, sym[0], kind, d, g),
                      file=sys.stderr)
            rc = 1
        if rc == 0:
            print("[+] mirror-clause-survival: OK — DISCARD %d, unlocated %d, located %d."
                  % (len(discards), len(unlocated), located))
        return rc
    finally:
        if own:
            shutil.rmtree(own, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
