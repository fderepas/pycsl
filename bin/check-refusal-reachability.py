#!/usr/bin/env python3
"""REFUSALS THAT CRASH INSTEAD OF REFUSING — a hard 0.

THE DEFECT CLASS. A refusal is the campaign's main instrument: when a construct
cannot be modelled faithfully, the pipeline REFUSES it rather than emitting something
that lets a false contract prove. A refusal that raises `NameError` instead of its own
message is still fail-closed — the process exits 1 — but it reports
`[!] UNEXPECTED PIPELINE ERROR` and tells the reader nothing, and "a crash is only
fail-closed while nothing catches it".

TWO INSTANCES WERE FOUND BY HAND IN ONE WINDOW, both by running a construct that was
SUPPOSED to be refused and reading what actually came out:
  * `pycsl-reference/0540` — a parametric `#@ datatype`: `'str' object has no attribute
    'get'`, an IR-key collision reached before the refusal.
  * `module6_whyml/preamble.py` — an unknown `#@ proof` citation:
    `name 'PyCSLIRError' is not defined`, because that module never imports it.

This gate makes the second shape mechanical: every `raise PyCSL*Error(...)` in the live
tree whose exception NAME is bound neither at module level nor by a local import in the
enclosing function. The ratchet is a hard 0 — there is no legitimate instance.

SOUND IN ONE DIRECTION. A bound name does not make the refusal reachable or correct; an
UNBOUND one guarantees the message is never delivered.
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "pycsl")


def scan():
    hits = []
    for d, _dirs, fs in os.walk(SRC):
        if "self-annotate" in d or "__pycache__" in d:
            continue
        for f in sorted(fs):
            if not f.endswith(".py"):
                continue
            p = os.path.join(d, f)
            tree = ast.parse(open(p, errors="replace").read())
            modlevel = set()
            for n in tree.body:
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    for a in n.names:
                        modlevel.add(a.asname or a.name.split(".")[0])
                elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
                    modlevel.add(n.name)
                elif isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            modlevel.add(t.id)
            for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
                local = set()
                for n in ast.walk(fn):
                    if isinstance(n, (ast.Import, ast.ImportFrom)):
                        for a in n.names:
                            local.add(a.asname or a.name.split(".")[0])
                    elif isinstance(n, ast.Assign):
                        for t in n.targets:
                            if isinstance(t, ast.Name):
                                local.add(t.id)
                for n in ast.walk(fn):
                    if (isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call)
                            and isinstance(n.exc.func, ast.Name)):
                        nm = n.exc.func.id
                        if (nm.startswith("PyCSL") and nm not in modlevel
                                and nm not in local):
                            hits.append((os.path.relpath(p, ROOT), fn.name,
                                         n.lineno, nm))
    return hits


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    hits = scan()
    print("[*] refusal-reachability: %d `raise PyCSL*Error` site(s) whose exception "
          "name is UNBOUND where it is raised." % len(hits))
    for p, fn, ln, nm in hits:
        print("    UNBOUND  %-22s %-38s %s  L%d" % (nm, p, fn, ln))
    if hits:
        print("[-] refusal-reachability: a refusal that raises NameError reports "
              "'UNEXPECTED PIPELINE ERROR' and delivers none of its message. Hard 0.")
        return 1
    print("[+] refusal-reachability: OK — 0 (hard ratchet).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
