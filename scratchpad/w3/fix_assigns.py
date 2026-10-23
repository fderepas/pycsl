#!/usr/bin/env python3
"""Iterate `#@ assigns` on the mirror's _csl_* family to a Why3 EXACTNESS fixpoint.

Why3 rejects BOTH an under-declared frame (`unlisted write effect`) and an
over-declared one (`this write effect does not happen`).  The set that works can
only be computed from the EMITTED body, so this drives the emitter and reacts to
its errors.  FOREGROUND ONLY; always leaves the tree in the last-tried state.
"""
import re, subprocess, sys, os

ROOT = os.path.abspath(os.path.dirname(__file__) + "/wt")
MIR = sys.argv[1] if len(sys.argv) > 1 else "src/self-annotate/src/frontend/Module5_IREmitter.py"
MLW = MIR[:-3] + ".mlw"
FIELD = sys.argv[2] if len(sys.argv) > 2 else "self._fresh_var_counter"
env = dict(os.environ, PATH="/home/fabrice/.opam/framac-coq8/bin:" + os.environ["PATH"],
           PYTHONHASHSEED="0")

def emit():
    r = subprocess.run(["python3", "src/pycsl/pycsl.py", MIR, "--import-path", "src/pycsl",
                        "--no-proof", "--keep-mlw"], cwd=ROOT, env=env,
                       capture_output=True, text=True)
    return r.stdout + r.stderr

def method_at(line):
    """The mirror method name whose emitted `let` contains .mlw line `line`."""
    txt = open(os.path.join(ROOT, MLW)).read().split("\n")
    for i in range(min(line, len(txt)) - 1, -1, -1):
        m = re.match(r"  (?:let rec |let |val |with )([a-z0-9_]+) ", txt[i])
        if m:
            return m.group(1)
    return None

def set_diverges(pyname, add):
    """Add or remove `#@ \\diverges` on the mirror method."""
    short = pyname.split("__", 1)[1] if "__" in pyname else pyname
    if not short.startswith("_"):
        short = "_" + short
    path = os.path.join(ROOT, MIR)
    lines = open(path).read().split("\n")
    for i, l in enumerate(lines):
        if re.match(r"    def %s\(" % re.escape(short), l):
            j, blk_start, have = i - 1, None, None
            while j >= 0 and (lines[j].lstrip().startswith("#") or lines[j].strip() == ""):
                s = lines[j].strip()
                if s.startswith("#@"):
                    blk_start = j
                if s == "#@ \\diverges":
                    have = j
                j -= 1
            if add:
                if have is not None:
                    return False
                lines.insert(blk_start, "    #@ \\diverges")
            else:
                if have is None:
                    return False
                del lines[have]
            open(path, "w").write("\n".join(lines))
            return True
    return False


def set_raises(pyname, add, exc):
    """Add or remove `#@ raises <exc> when True` on the mirror method."""
    short = pyname.split("__", 1)[1] if "__" in pyname else pyname
    if not short.startswith("_"):
        short = "_" + short
    path = os.path.join(ROOT, MIR)
    lines = open(path).read().split("\n")
    for i, l in enumerate(lines):
        if re.match(r"    def %s\(" % re.escape(short), l):
            j, blk_start, have = i - 1, None, None
            while j >= 0 and (lines[j].lstrip().startswith("#") or lines[j].strip() == ""):
                s = lines[j].strip()
                if s.startswith("#@"):
                    blk_start = j
                if s.startswith("#@ raises " + exc + " "):
                    have = j
                j -= 1
            if add:
                if have is not None:
                    return False
                lines.insert(blk_start, "    #@ raises %s when True" % exc)
            else:
                if have is None:
                    return False
                del lines[have]
            open(path, "w").write("\n".join(lines))
            return True
    return False


def set_assigns(pyname, value):
    """pyname is the WhyML symbol `pycsltojsonemitter___csl_x`; find `def _csl_x`."""
    short = pyname.split("__", 1)[1] if "__" in pyname else pyname
    if not short.startswith("_"):
        short = "_" + short
    path = os.path.join(ROOT, MIR)
    lines = open(path).read().split("\n")
    for i, l in enumerate(lines):
        if re.match(r"    def %s\(" % re.escape(short), l):
            j = i - 1
            while j >= 0 and (lines[j].lstrip().startswith("#") or lines[j].strip() == ""):
                s = lines[j].strip()
                if s.startswith("#@ assigns"):
                    new = "    #@ assigns " + value
                    if lines[j] == new:
                        return False
                    lines[j] = new
                    open(path, "w").write("\n".join(lines))
                    return True
                j -= 1
            return False
    return False

def main():
    seen = {}
    for it in range(300):
        out = emit()
        if "L3-tc ✓" in out:
            print("FIXPOINT after %d iterations" % it)
            return 0
        md = re.search(r'line (\d+), characters [\d-]+:\s*\n'
                       r'this expression (does not diverge|diverges)', out)
        if md:
            line = int(md.group(1))
            name = method_at(line)
            add = md.group(2) == "diverges"
            key = (name, "div", add)
            if seen.get(key, 0) > 2:
                print("OSCILLATION on %s diverges=%s at iteration %d" % (name, add, it))
                return 2
            seen[key] = seen.get(key, 0) + 1
            ok = set_diverges(name, add)
            print("it%-3d %-55s -> diverges %s %s"
                  % (it, name, "ADD" if add else "DROP", "" if ok else "(NO EDIT)"))
            if not ok:
                print(out[-1500:])
                return 3
            continue
        mr = re.search(r'line (\d+), characters [\d-]+:\s*\n'
                       r'this expression (raises unlisted exception|does not raise exception)'
                       r' (\w+)', out)
        if mr:
            line = int(mr.group(1))
            name = method_at(line)
            add = mr.group(2) == "raises unlisted exception"
            exc = mr.group(3)
            key = (name, "raises", add, exc)
            if seen.get(key, 0) > 2:
                print("OSCILLATION on %s raises=%s at iteration %d" % (name, add, it))
                return 2
            seen[key] = seen.get(key, 0) + 1
            ok = set_raises(name, add, exc)
            print("it%-3d %-55s -> raises %s %s %s"
                  % (it, name, "ADD" if add else "DROP", exc, "" if ok else "(NO EDIT)"))
            if not ok:
                print(out[-1500:])
                return 3
            continue
        m = re.search(r'line (\d+), characters [\d-]+:\s*\n(this write effect does not happen'
                      r' in the expression|this expression produces an unlisted write effect)', out)
        if not m:
            m2 = re.search(r"(PIPELINE ERROR:.*|File .*\n[a-z].*)", out)
            print("NO-PROGRESS / different error at iteration %d:" % it)
            print(out[-2500:])
            return 1
        line, kind = int(m.group(1)), m.group(2)
        name = method_at(line)
        want = "\\nothing" if "does not happen" in kind else FIELD
        key = (name, want)
        if seen.get(key, 0) > 2:
            print("OSCILLATION on %s -> %s at iteration %d" % (name, want, it))
            return 2
        seen[key] = seen.get(key, 0) + 1
        ok = set_assigns(name, want)
        print("it%-3d %-55s -> %s %s" % (it, name, want, "" if ok else "(NO EDIT)"))
        if not ok:
            print(out[-1500:])
            return 3
    print("ITERATION CAP")
    return 4

sys.exit(main())
