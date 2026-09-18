#!/usr/bin/env python3
"""RE-ASK EVERY EARLIER PROBE WITH MORE THAN ONE WRONG ANSWER.

The gen #29 lesson that cost a whole fuzzer batch: a differential probe that claims ONE
wrong value only catches a model that answers THAT value. An ERASED value reads as 0, and
0 is this campaign's most common wrong answer (routes #31, #40, #43, #44, #56, #183,
#184, #190).

This walks a directory of earlier probe programs, runs each under CPython to get the real
answer, and then re-runs the pipeline claiming each of a SET of wrong answers. Any
`Verification SUCCESS` is a false proof.

Usage:  reclaim_sweep.py <tree-root> <probe-dir> [more probe dirs...]
"""
import os
import re
import runpy
import subprocess
import sys

ROOT = sys.argv[1]
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")
PY = "/home/fabrice/git/pycsl/.venv/bin/python3"
CLAIMS = (0, 1, -1, 99)
ENS = re.compile(r"^#@ ensures \\result == .*$", re.M)
ENS_INDENT = re.compile(r"^(\s*)#@ ensures \\result == .*$", re.M)


def cpython_answer(path):
    try:
        out = subprocess.run([PY, path], capture_output=True, text=True, timeout=10)
    except Exception:
        return None
    # the probe files do not print; import and call probe()
    src = open(path).read()
    if "def probe(" not in src:
        return None
    harness = (src + '\n\nif __name__ == "__main__":\n'
               '    import sys\n'
               '    try:\n'
               '        print(probe())\n'
               '    except TypeError:\n'
               '        print(probe(1))\n'
               '    except Exception as e:\n'
               '        print("RAISES")\n')
    tmp = path + ".harness.py"
    open(tmp, "w").write(harness)
    try:
        out = subprocess.run([PY, tmp], capture_output=True, text=True, timeout=10)
    except Exception:
        return None
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    s = out.stdout.strip()
    if not s or not s.lstrip("-").isdigit():
        return None
    return int(s)


def main():
    dirs = sys.argv[2:]
    found = 0
    checked = 0
    for d in dirs:
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".py") or ".harness" in fn or fn.startswith("reclaim_"):
                continue
            path = os.path.join(d, fn)
            src = open(path).read()
            if not ENS.search(src) or "def probe(" not in src:
                continue
            real = cpython_answer(path)
            if real is None:
                continue
            checked += 1
            for k in CLAIMS:
                if k == real:
                    continue
                cand = ENS_INDENT.sub(lambda m: "%s#@ ensures \\result == %d"
                                      % (m.group(1), k), src, count=0)
                cpath = os.path.join(d, "reclaim_%d_%s" % (k, fn))
                open(cpath, "w").write(cand)
                try:
                    out = subprocess.run([PY, PYCSL, cpath], capture_output=True,
                                         text=True, timeout=300,
                                         env={**os.environ, "PYTHONHASHSEED": "0"}).stdout
                except Exception:
                    continue
                if "Verification SUCCESS" in out:
                    found += 1
                    print("FALSE-PROOF %s (CPython %d, claim %d)" % (cpath, real, k),
                          flush=True)
    print("RECLAIM-SWEEP-DONE probes=%d false_proofs=%d" % (checked, found), flush=True)


if __name__ == "__main__":
    main()
