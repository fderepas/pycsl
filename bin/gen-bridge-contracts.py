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
BRIDGE_PREDICATES = {"size", "wf_ir", "wf_dict", "size_list", "size_dict",
                     # richer-contracts-bridge P2.1 (C2): the DEEP well-formedness
                     # family the substmap fold preserves.
                     "wf_ir_deep", "wf_dict_deep", "wf_list_deep",
                     # richer-contracts-bridge P2.2 (C2): the set-fold relation.
                     "setfold_leaf_empty",
                     # richer-contracts-bridge P2.3 (C2): fragment membership.
                     "in_emitted_fragment", "frag_dict", "frag_list"}

# Catalog of certified facts the generator can turn into an enriched clause.
# Each entry names the export tokens that MUST be present for the fact to be
# certified, and the `#@` clauses it produces.  A clause is {kind, text}; `text`
# may reference `{subject}` (the method's first formal param) for a requires that
# names the input value.
FACT_CATALOG = {
    # Phase2c_PyValDict.v `size_pos`: forall v. size v > 0  (the certified pyval
    # measure; the induction is done once in Rocq/Lean, SMT only applies it).
    "size_pos": {
        "rung": "C1",
        "predicate": "size",
        "clauses": [{"kind": "ensures", "text": r"ensures size(\result) > 0"}],
        "export_tokens": [r"function size", r"lemma size_pos", r"size v > 0"],
    },
    # richer-contracts-bridge P2.1 (C2): wf-PRESERVATION for the substmap (T1)
    # fold.  The CERTIFIED shallow wf_ir (Phase2c) is NOT an inductive invariant
    # of the recursive descent (measured: helper VCs time out); the generator
    # emits a DEEP strengthening `wf_ir_deep` (a bridge-audit predicate, pure
    # definition + deep=>shallow lemmas, NO axiom — emit_substmap_group) and
    # threads it as requires/ensures so Why3 discharges the induction
    # helper-by-helper.  Backed by the certified wf_val/wf_dict/wf_ir predicates.
    "wf_ir_deep_preserve": {
        "rung": "C2",
        "predicate": "wf_ir_deep",
        "clauses": [
            {"kind": "requires", "text": r"requires wf_ir_deep({subject})"},
            {"kind": "ensures",  "text": r"ensures wf_ir_deep(\result)"},
        ],
        "export_tokens": [r"predicate wf_val", r"predicate wf_dict",
                          r"predicate wf_ir"],
    },
    # richer-contracts-bridge P2.2 (C2): a set fold's RELATIONAL leaf->empty fact
    # (output domain drawn only from container structure). A pure bridge-audit
    # predicate over the certified pyval ADT + the purely-defined set model
    # (emit_setfold_group), NO axiom; discharges from the top fold's leaf arm.
    "setfold_leaf_empty_fact": {
        "rung": "C2",
        "predicate": "setfold_leaf_empty",
        "clauses": [{"kind": "ensures",
                     "text": r"ensures setfold_leaf_empty({subject}, \result)"}],
        "export_tokens": [r"type pyval", r"PList", r"PDict"],
    },
    # richer-contracts-bridge P2.3 (C2): emitted-fragment grammar membership,
    # PRESERVED by the type-substitution.  Bridge-audit predicate (pure
    # definition, NO axiom — emit_substmap_group) tying the method to
    # evaluator-axiom-audit.md's boundary by contract.  Backed by the certified
    # pyval ADT.
    "in_emitted_fragment_preserve": {
        "rung": "C2",
        "predicate": "in_emitted_fragment",
        "clauses": [
            {"kind": "requires", "text": r"requires in_emitted_fragment({subject})"},
            {"kind": "ensures",  "text": r"ensures in_emitted_fragment(\result)"},
        ],
        "export_tokens": [r"type pyval", r"PNone", r"PList"],
    },
}

# The eligible-method REGISTRY.  This is the generator-owned declaration of which
# mirror methods carry which certified fact(s).  A method may carry several facts
# (they compose: e.g. the C1 size measure AND the C2 wf-preservation).  `subject`
# names the method's input parameter for a requires-side clause.  The CLAUSE text
# is never written here — it is produced from FACT_CATALOG + the export.
REGISTRY = [
    {
        "file": "frontend/monomorphize.py",
        "method": "_subst_type_in_ir",
        "facts": ["size_pos", "wf_ir_deep_preserve", "in_emitted_fragment_preserve"],
        "subject": "node",
    },
    {
        "file": "module6_whyml/ir_scanner.py",
        "method": "collection_binder_kinds",
        "facts": ["setfold_leaf_empty_fact"],
        "subject": "obj",
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
        for fact in entry["facts"]:
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


def entry_clauses(entry):
    """The ordered list of `#@` clause texts this entry's facts produce.
    `{subject}` is substituted with the entry's declared input parameter.
    Ordered canonically: all requires first, then all ensures (facts in the
    REGISTRY order)."""
    subject = entry.get("subject", "")
    reqs, enss = [], []
    for fact in entry["facts"]:
        for cl in FACT_CATALOG[fact]["clauses"]:
            text = cl["text"].replace("{subject}", subject)
            (reqs if cl["kind"] == "requires" else enss).append(text)
    return reqs, enss


def apply_entry(lines, entry):
    """Rewrite entry's method `#@` block so its requires/ensures are EXACTLY the
    generator-produced bridge clauses (requires replace `#@ requires True`;
    ensures replace any prior ensures), preserving any leading `#@ \\trusted`
    line and the trailing `#@ assigns`. Returns (new_lines, changed:bool)."""
    def_idx = find_def(lines, entry["method"])
    if def_idx is None:
        raise SystemExit("[error] method %s not found in %s" % (entry["method"], entry["file"]))
    indent = re.match(r"(\s*)", lines[def_idx]).group(1)
    block = annotation_block(lines, def_idx)
    reqs, enss = entry_clauses(entry)

    # Partition the existing block, dropping its requires/ensures (we regenerate
    # them); keep trusted, assigns, comments, and decorators. Decorators (`@...`,
    # not `#@`) MUST stay adjacent to the def, so they go last.
    def _is(j, *pfx):
        return lines[j].strip().startswith(pfx)
    trusted = [lines[j] for j in block if _is(j, "#@ \\trusted")]
    assigns = [lines[j] for j in block if _is(j, "#@ assigns")]
    decorators = [lines[j] for j in block
                  if _is(j, "@") and not _is(j, "#")]
    others = [lines[j] for j in block
              if not _is(j, "#@ \\trusted", "#@ requires", "#@ ensures", "#@ assigns")
              and not (_is(j, "@") and not _is(j, "#"))]
    req_lines = ["%s#@ %s" % (indent, r) for r in reqs] or ["%s#@ requires True" % indent]
    ens_lines = ["%s#@ %s" % (indent, e) for e in enss]
    new_block = trusted + others + req_lines + ens_lines + assigns + decorators

    old_block = [lines[j] for j in block]
    changed = (old_block != new_block)
    if changed:
        b0 = block[0] if block else def_idx
        # remove old block lines (descending), then insert the new block at b0.
        for j in sorted(block, reverse=True):
            del lines[j]
        for k, ln in enumerate(new_block):
            lines.insert(b0 + k, ln)
    return lines, changed


def generate(check_only=False):
    validate_export()
    total_changed = 0
    report = []
    for entry in REGISTRY:
        path = os.path.join(MIRROR_ROOT, entry["file"])
        reqs, enss = entry_clauses(entry)
        txt = read(path)
        lines = txt.split("\n")
        lines, changed = apply_entry(lines, entry)
        new_txt = "\n".join(lines)
        report.append((entry, reqs + enss, changed))
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
                if not (s.startswith("#@ ensures") or s.startswith("#@ requires")):
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
        for entry, clauses, ch in report:
            state = ("WOULD-WRITE" if (args.check and ch) else
                     "wrote" if ch else "idempotent")
            print("  %-12s %s::%s  <=  facts %s"
                  % (state, entry["file"], entry["method"], ",".join(entry["facts"])))
            for clause in clauses:
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
            print("  [+] no hand-written enriched bridge clause found.")
        else:
            for path, lineno, method, s in v:
                print("  [!] HAND-WRITTEN bridge clause (not generator-owned):")
                print("      %s:%d  (method %s)" % (os.path.relpath(path, ROOT), lineno, method))
                print("      %s" % s)
            print("\n  A bridge #@ requires/ensures must be produced by gen-bridge-contracts.py")
            print("  (add the method to REGISTRY), never hand-written. See plan §4.")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
