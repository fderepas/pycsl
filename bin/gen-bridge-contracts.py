#!/usr/bin/env python3
r"""gen-bridge-contracts.py — P0.2 of richer-contracts-bridge-plan.md.

The GENERATE-DON'T-WRITE engine for the formal<->mirror bridge.  Enriched (above
C0) mirror `#@` contracts must be PRODUCED from the formal side, never
hand-written, so the bridge cannot silently drift (plan §1.2, §4).

Two pieces:

  1. A generator.  For every ELIGIBLE mirror method (declared in REGISTRY below),
     it produces the enriched `#@ ensures` clause from a CERTIFIED FACT of the
     formal export (`src/formal-semantics/pycsl-formal-export.mlw`) and writes it
     into the mirror `.py`.  It validates that the named fact is actually
     certified in the export (the `size` measure + its `size_pos` positivity
     lemma) before emitting — if the export loses the fact, generation refuses.
     Re-running is IDEMPOTENT: an already-correct clause is rewritten byte-for-byte.

  2. A lint (`--lint`).  Flags any mirror `#@ ensures` that references a bridge
     predicate/measure (`size`, `wf_ir`, `wf_dict`, `size_list`, `size_dict` — the
     certified pyval names S-c1 wired) but is NOT produced by the generator (no
     REGISTRY entry).  A hand-written `#@ ensures size(\result) > 0` is exactly
     the drift vector §4 exists to kill.

Minimum P0 deliverable: regenerate S-c1's exact contract —
  `#@ ensures size(\result) > 0` on frontend/monomorphize.py::_subst_type_in_ir.

Modes:
  gen-bridge-contracts.py              # generate (write) — idempotent
  gen-bridge-contracts.py --check      # verify idempotent (exit 1 if a write is needed)
  gen-bridge-contracts.py --lint       # flag hand-written enriched bridge ensures
  gen-bridge-contracts.py --check --lint
Exit: 0 clean; 1 a write is needed (--check) or a lint violation; 2 setup error.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(ROOT, "src", "formal-semantics", "pycsl-formal-export.mlw")
MIRROR_ROOT = os.path.join(ROOT, "src", "self-annotate", "src")

# The certified pyval names S-c1 wired into the emitter (_CERTIFIED_PYVAL_ARITY,
# expressions.py).  An enriched `#@ ensures` naming one of these is a BRIDGE
# contract and must be generator-owned.
BRIDGE_PREDICATES = {"size", "wf_ir", "wf_dict", "size_list", "size_dict"}

# Catalog of certified facts the generator can turn into a C1 postcondition.
# Each entry names the export tokens that MUST be present for the fact to be
# certified, and the `#@ ensures` clause it produces (applied to \result).
FACT_CATALOG = {
    # Phase2c_PyValDict.v `size_pos`: forall v. size v > 0  (the certified pyval
    # measure; the induction is done once in Rocq/Lean, SMT only applies it).
    "size_pos": {
        "rung": "C1",
        "predicate": "size",
        "clause": r"ensures size(\result) > 0",
        "export_tokens": [r"function size", r"lemma size_pos", r"size v > 0"],
    },
}

# The eligible-method REGISTRY.  This is the generator-owned declaration of which
# mirror methods carry which certified fact.  P0 populates exactly S-c1's method;
# P1 grows this over the pyval/sdict-returning fold population.  The CLAUSE itself
# is never written here — it is produced from FACT_CATALOG + the export.
REGISTRY = [
    {
        "file": "frontend/monomorphize.py",
        "method": "_subst_type_in_ir",
        "fact": "size_pos",
    },
]


def read(path):
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
def validate_export():
    """Return {fact: True} for facts whose certifying tokens are all present in
    the export; raise if a REGISTRY fact is not certified."""
    txt = read(EXPORT)
    ok = {}
    for fact, spec in FACT_CATALOG.items():
        ok[fact] = all(re.search(tok, txt) for tok in spec["export_tokens"])
    for entry in REGISTRY:
        fact = entry["fact"]
        if not ok.get(fact):
            missing = [t for t in FACT_CATALOG[fact]["export_tokens"]
                       if not re.search(t, txt)]
            raise SystemExit(
                "[error] fact %r for %s::%s is NOT certified in the export "
                "(missing tokens: %s). Refusing to generate."
                % (fact, entry["file"], entry["method"], missing))
    return ok


# ---------------------------------------------------------------------------
def find_def(lines, method):
    for i, ln in enumerate(lines):
        if re.match(r"\s*def\s+%s\s*\(" % re.escape(method), ln):
            return i
    return None


def annotation_block(lines, def_idx):
    """Indices of the contiguous #@/decorator/comment block directly above def."""
    i = def_idx - 1
    idxs = []
    while i >= 0:
        s = lines[i].strip()
        if s.startswith("#@") or s.startswith("@") or (s.startswith("#") and idxs):
            idxs.append(i)
            i -= 1
        else:
            break
    return sorted(idxs)


def apply_entry(lines, entry, clause):
    """Rewrite (or insert) the `#@ ensures` line for entry's method to `clause`.
    Returns (new_lines, changed:bool). Preserves the def's leading indentation."""
    def_idx = find_def(lines, entry["method"])
    if def_idx is None:
        raise SystemExit("[error] method %s not found in %s" % (entry["method"], entry["file"]))
    indent = re.match(r"(\s*)", lines[def_idx]).group(1)
    block = annotation_block(lines, def_idx)
    target = "%s#@ %s" % (indent, clause)

    ens_idx = [j for j in block if lines[j].strip().startswith("#@ ensures")]
    changed = False
    if ens_idx:
        j = ens_idx[0]
        if lines[j] != target:
            lines[j] = target
            changed = True
    else:
        # insert after the last #@ requires, else at top of the block, else above def
        req = [j for j in block if lines[j].strip().startswith("#@ requires")]
        ins = (req[0] + 1) if req else (block[0] if block else def_idx)
        lines.insert(ins, target)
        changed = True
    return lines, changed


def generate(check_only=False):
    validate_export()
    total_changed = 0
    report = []
    for entry in REGISTRY:
        path = os.path.join(MIRROR_ROOT, entry["file"])
        spec = FACT_CATALOG[entry["fact"]]
        clause = spec["clause"]
        txt = read(path)
        lines = txt.split("\n")
        lines, changed = apply_entry(lines, entry, clause)
        new_txt = "\n".join(lines)
        report.append((entry, clause, changed))
        if changed:
            total_changed += 1
            if not check_only:
                with open(path, "w") as f:
                    f.write(new_txt)
    return total_changed, report


# ---------------------------------------------------------------------------
def lint():
    """Flag hand-written enriched bridge ensures: a mirror `#@ ensures` naming a
    BRIDGE_PREDICATE that no REGISTRY entry would produce."""
    # owned = set of (abs_path, method) the generator produces
    owned = set()
    for entry in REGISTRY:
        owned.add((os.path.join(MIRROR_ROOT, entry["file"]), entry["method"]))

    pred_re = re.compile(r"\b(%s)\b" % "|".join(sorted(BRIDGE_PREDICATES)))
    violations = []
    for dirpath, _, files in os.walk(MIRROR_ROOT):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            lines = read(path).split("\n")
            for i, ln in enumerate(lines):
                s = ln.strip()
                if not s.startswith("#@ ensures"):
                    continue
                if not pred_re.search(s):
                    continue
                # find the def this ensures decorates (scan downward past the block)
                j = i + 1
                method = None
                while j < len(lines):
                    m = re.match(r"\s*def\s+(\w+)\s*\(", lines[j])
                    if m:
                        method = m.group(1)
                        break
                    t = lines[j].strip()
                    if t and not (t.startswith("#@") or t.startswith("@") or t.startswith("#")):
                        break
                    j += 1
                if (path, method) not in owned:
                    violations.append((path, i + 1, method, s))
    return violations


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify idempotent: exit 1 if a write would be needed")
    ap.add_argument("--lint", action="store_true",
                    help="flag hand-written enriched bridge ensures")
    args = ap.parse_args()

    rc = 0
    if not args.lint or args.check:
        changed, report = generate(check_only=args.check)
        print("=" * 68)
        print("BRIDGE CONTRACT GENERATOR (P0.2)  %s"
              % ("[--check]" if args.check else "[write]"))
        print("  export : %s" % os.path.relpath(EXPORT, ROOT))
        print("=" * 68)
        for entry, clause, ch in report:
            state = ("WOULD-WRITE" if (args.check and ch) else
                     "wrote" if ch else "idempotent")
            print("  %-12s %s::%s  <=  fact %s"
                  % (state, entry["file"], entry["method"], entry["fact"]))
            print("               #@ %s" % clause)
        if args.check and changed:
            print("\n[!] NOT idempotent: %d clause(s) would change (run without --check)."
                  % changed)
            rc = 1
        elif args.check:
            print("\n[+] idempotent: re-running the generator produces no diff.")

    if args.lint:
        v = lint()
        print("\n" + "=" * 68)
        print("BRIDGE CONTRACT LINT (P0.2)")
        print("=" * 68)
        if not v:
            print("  [+] no hand-written enriched bridge ensures found.")
        else:
            for path, lineno, method, s in v:
                print("  [!] HAND-WRITTEN bridge ensures (not generator-owned):")
                print("      %s:%d  (method %s)" % (os.path.relpath(path, ROOT), lineno, method))
                print("      %s" % s)
            print("\n  A bridge #@ ensures must be produced by gen-bridge-contracts.py")
            print("  (add the method to REGISTRY), never hand-written. See plan §4.")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
