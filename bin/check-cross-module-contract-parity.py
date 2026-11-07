#!/usr/bin/env python3
r"""L-PLANE ORACLE: may an IMPORTING module assume a clause its DEFINER does not prove?

WHY THIS EXISTS (#49, gen #31). A mirror function is emitted TWICE: as a `let` DEFINITION in
the module that owns it, where its `ensures` are PROVED, and as a bodyless `val` STUB in every
module that imports it, where they are ASSUMED. Nothing compared the two.

    module6_whyml/statements.mlw     let statementemissionmixin___f … ensures { P }     PROVED
    Module6_WhyMLTranspiler.mlw      val statementemissionmixin___f … ensures { Q }     ASSUMED

If `Q` is `P`, or weaker, the importer is sound and possibly incomplete. **If `Q` carries a
clause the definer never proves, the importer is assuming a fact this repository has not
established — and every caller obligation discharged with it rests on nothing.** That is a
fail-OPEN, and it is invisible to every other plane: both files type-check, both prove, the
mirror byte-diff is inert, and the emitted-vacuity probe looks at bodies, not at stubs.

IT WAS NOT HYPOTHETICAL WHEN THIS WAS WRITTEN. Generation #31 added 72 postconditions to
`frontend/Module5_IREmitter.py`'s IR constructors (`\result["type"] == "<tag>"` →
`kind_of result = "<tag>"`), and `pycsl.mlw` — which imports them — re-emitted all 72 against
a stub typed `map int (option int)` instead of `emit_ir`, producing 72 UNBOUND symbols. The
repair DROPS a clause the importing context cannot state, which is the safe direction; this
plane is what makes "the safe direction" a checked fact rather than an intention. The same
mechanism could as easily have produced the unsafe one.

THE RULE, and it is a HARD ZERO, not a ratchet:

    a `val` stub's non-trivial `ensures` set must be a SUBSET of the union of what the `let`
    definition(s) of that same symbol prove.

A clause that is literally `true` claims nothing and is normalised out of both sides before
comparing — otherwise a stub carrying `ensures { true }` beside a definition carrying real
clauses would read as an EXTRA.

THE OTHER DIRECTION IS REPORTED, NOT RATCHETED. A stub with FEWER clauses than its definer
proves is sound and merely incomplete, and the number RISES whenever a definition is
strengthened — which is the thing the campaign is trying to do. Ratcheting it would punish
the improvement, so it is printed as a measurement. (Same reasoning as
`bin/price-the-conversions.py`.)

WHAT IT DOES NOT SEE, stated because the first negative test found it. The population is
symbols that appear BOTH as a `val` and as a `let`. A synthesized AVATAR — `val
self__<m>_<n>`, the receiver-less op a shadowed self-call goes through — has NO `let`
counterpart under that name, so a clause on an avatar is outside this plane entirely.
(Injecting `ensures { 99 = 100 }` on `val self__py_expr_to_ir_1` was NOT caught; injecting
the same clause on `val _contractparser___mk_in` was, naming the symbol, the assuming file
and the defining file.) Avatars are `bin/check-shadowed-selfcalls.py`'s population, and the
honest statement is that the two planes partition the stub surface rather than that either
covers it.

USAGE
    bin/check-cross-module-contract-parity.py [--emit-dir DIR] [--verbose]

With no `--emit-dir` the 53 mirrors are emitted into a scratch directory first (needs `why3`
on PATH; see `. scratchpad/g29/env.sh`).
"""
import argparse
import collections
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from lib_plane_lock import refuse_if_battery_running as _refuse_if_battery_running
except ImportError:
    def _refuse_if_battery_running(_plane):
        return None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")

# The #44 rule: a gate that cannot tell "nothing is wrong" from "I looked at nothing" is not a
# gate. Both floors are well below the measured population (53 files, 248 shared symbols at
# the first measurement) and both only grow as the mirror does.
MIN_FILES = 40
MIN_SHARED_SYMBOLS = 180

_HEAD = re.compile(r"^  (val|let)(?: rec| function| ghost)* ([A-Za-z_][A-Za-z_0-9']*) ")
_CLAUSE = re.compile(r"^\s+(ensures|requires)\s+\{ (.*) \}\s*$")
# A clause that claims nothing. `false` is NOT here: `ensures { false }` is the `-> NoReturn`
# divergence model and a stub carrying it while the definer does not would be a real EXTRA.
_TRIVIAL = {"true", "True"}
_EFFECT = re.compile(r"^\s+(writes|raises|diverges|variant|reads|alias)\b")


def _emit_mirrors(out_dir):
    """Emit every mirror `.mlw` into out_dir with the ONE-underscore naming every consumer
    of an `--emit-dir` uses (`relpath[:-3].replace(os.sep, '_')`). Getting this wrong is not
    a loud failure — see the note in bin/run-soundness-planes.sh."""
    py = os.path.join(ROOT, ".venv", "bin", "python3")
    if not os.access(py, os.X_OK):
        py = "python3"
    srcs = []
    for dirpath, _dirs, files in os.walk(MIRROR):
        for f in files:
            if f.endswith(".py"):
                srcs.append(os.path.join(dirpath, f))
    env = dict(os.environ, PYTHONHASHSEED="0")
    for src in sorted(srcs):
        rel = os.path.relpath(src, MIRROR)
        name = rel[:-3].replace(os.sep, "_")
        mlw = src[:-3] + ".mlw"
        if os.path.exists(mlw):
            os.unlink(mlw)
        subprocess.run([py, os.path.join(ROOT, "src", "pycsl", "pycsl.py"), src,
                        "--import-path", os.path.join(ROOT, "src", "pycsl"),
                        "--no-proof", "--keep-mlw"],
                       cwd=ROOT, env=env, capture_output=True)
        if os.path.exists(mlw):
            shutil.move(mlw, os.path.join(out_dir, name + ".mlw"))


def _scan(emit_dir):
    """symbol -> {file: (kind, [non-trivial ensures])}"""
    sym = collections.defaultdict(dict)
    nfiles = 0
    for f in sorted(os.listdir(emit_dir)):
        if not f.endswith(".mlw"):
            continue
        nfiles += 1
        lines = io.open(os.path.join(emit_dir, f), encoding="utf-8").read().split("\n")
        i = 0
        while i < len(lines):
            m = _HEAD.match(lines[i])
            if not m:
                i += 1
                continue
            kind, name = m.group(1), m.group(2)
            ens = []
            j = i + 1
            while j < len(lines):
                c = _CLAUSE.match(lines[j])
                if c:
                    if c.group(1) == "ensures":
                        ens.append(c.group(2).strip())
                    j += 1
                    continue
                if _EFFECT.match(lines[j]):
                    j += 1
                    continue
                break
            sym[name][f] = (kind, [e for e in ens if e not in _TRIVIAL])
            i = j
    return sym, nfiles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    # The battery lock exists because an EMITTING plane and a READING plane must not overlap.
    # With `--emit-dir` this plane emits NOTHING — it reads a directory somebody else produced —
    # so the lock does not apply and refusing on it would make the battery unable to hand it
    # the shared emission. Checked only on the self-emitting path.
    if not args.emit_dir:
        refusal = _refuse_if_battery_running("check-cross-module-contract-parity")
        if refusal:
            print(refusal)
            return 2

    tmp = None
    emit_dir = args.emit_dir
    if not emit_dir:
        if not shutil.which("why3"):
            print("[!] cross-module-contract-parity: REFUSING — `why3` is not on PATH and the"
                  " emission type-checks with it. THIS IS A REFUSAL, NOT A PASS.",
                  file=sys.stderr)
            return 2
        tmp = tempfile.mkdtemp(prefix="pycsl-xmod-")
        emit_dir = tmp
        _emit_mirrors(emit_dir)
    try:
        sym, nfiles = _scan(emit_dir)
        shared = {n: v for n, v in sym.items()
                  if any(k == "val" for k, _ in v.values())
                  and any(k == "let" for k, _ in v.values())}
        if nfiles < MIN_FILES or len(shared) < MIN_SHARED_SYMBOLS:
            print("[!] cross-module-contract-parity: REFUSING — %d emitted file(s) and %d"
                  " shared symbol(s), expected at least %d and %d. THIS IS A REFUSAL, NOT A"
                  " PASS." % (nfiles, len(shared), MIN_FILES, MIN_SHARED_SYMBOLS),
                  file=sys.stderr)
            return 2

        extra, fewer, same = [], [], 0
        for name in sorted(shared):
            per_file = shared[name]
            proved = set()
            definers = []
            for f, (kind, ens) in sorted(per_file.items()):
                if kind == "let":
                    proved |= set(ens)
                    definers.append(f)
            for f, (kind, ens) in sorted(per_file.items()):
                if kind != "val":
                    continue
                s = set(ens)
                if s - proved:
                    extra.append((name, f, sorted(s - proved), definers))
                elif proved - s:
                    fewer.append((name, f, len(proved - s)))
                else:
                    same += 1

        print("[*] cross-module-contract-parity: %d emitted mirror(s); %d symbol(s) appear as"
              " BOTH a `val` stub and a `let` definition." % (nfiles, len(shared)))
        print("    %5d stub(s) carry EXACTLY what the definition proves" % same)
        print("    %5d stub(s) carry FEWER clause(s) — sound, merely incomplete (a"
              " MEASUREMENT, not a ratchet: it rises when a definition is strengthened)"
              % len(fewer))
        if args.verbose:
            for n, f, k in fewer[:60]:
                print("        FEWER  %-58s in %-38s (-%d)" % (n, f, k))
        if extra:
            print("[!] cross-module-contract-parity: %d stub(s) ASSUME a clause no definition"
                  " proves. This is a FAIL-OPEN: every caller obligation discharged with it"
                  " rests on nothing." % len(extra), file=sys.stderr)
            for n, f, cl, definers in extra:
                print("    [!] %s\n        assumed in %s: %s\n        defined in %s"
                      % (n, f, cl[:3], definers), file=sys.stderr)
            print("    Either prove the clause where the function is DEFINED, or stop"
                  " emitting it on the stub. HARD ZERO — never baseline this.",
                  file=sys.stderr)
            return 1
        print("[+] cross-module-contract-parity: OK — 0 stub(s) assume a clause no definition"
              " proves (hard zero).")
        return 0
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
