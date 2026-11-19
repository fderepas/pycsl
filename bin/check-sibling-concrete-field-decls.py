#!/usr/bin/env python3
r"""L-PLANE ORACLE: does a `#@ sibling_concrete` relocation bring the FIELD DECLARATIONS its body reads?

WHY THIS EXISTS (#49, gen #32, backlog #67). `#@ sibling_concrete` copies a method BODY from the
mixin that owns it into a destination mirror file, so that file's `self._m(...)` sites lower to a
real body instead of a receiver-less abstract `val` with an unconstrained result (wall-lesson (ay)).
**It does not copy the class-level FIELD DECLARATIONS that body reads.**

Backlog #63 paid for this. The re-ported `_field_type_of` reads `_record_field_elem_locals`; the
mirror's `types.py` — the body's ORIGINAL home — declares it `Dict[str, str]`; `statements.py`, the
destination, did not. The untyped `getattr` therefore took its default of an opaque INT map and the
destination file failed L3-tc (`int` where `string` was expected) while the original home was
modelling the same field correctly all along. One declaration fixed it.

>>> A DECLARATION IS THE MIRROR'S MODELLING LAYER. A MISSING ONE IS A LATENT INT-ERASURE THAT LOOKS
>>> EXACTLY LIKE THE EMITTER'S TYPE-INFERENCE SEAM IN THE ERROR MESSAGE, AND DIFFERS FROM IT BY ONE
>>> LINE VERSUS A CAMPAIGN.

NEITHER EXISTING PLANE CAN SEE IT, and that is the whole reason this one exists:

  * `check-mirror-field-parity.py` compares mirror-vs-LIVE **class-level** annotations — it walks
    `ClassDef` bodies for `AnnAssign` with a `Name` target. The live `_record_field_elem_locals` is
    never annotated at all, and many live fields are annotated as `self.X: T = ...` INSIDE
    `__init__` (an `AnnAssign` on an `Attribute`, inside a `FunctionDef`), so they are outside its
    335-field population entirely. Its "0 NEW drift" is honest about what it compared and is read as
    a stronger claim than it makes.
  * `check-sibling-concrete-fidelity.py` compares BODIES, and was GREEN on the #63 defect right up
    until the re-port made the body USE the missing field.

So the hole is visible only when a relocated body happens to read a field its destination lacks —
i.e. **the check fires on the next re-port rather than on the drift**, which is the worst possible
schedule. This plane moves it to the drift.

WHAT IT MEASURES. For every def in `src/self-annotate/src/` whose preceding `#@` block carries
`sibling_concrete`, it collects every `self.<f>` the body READS (including `getattr(self, "<f>",
...)`) that some mirror file declares as a class-level field, and reports:

  * **MISSING** — the DESTINATION file does not declare it, while another mirror file does. A latent
    int-erasure. Ratcheted; may only shrink.
  * **MISMATCH** — the destination declares it with a DIFFERENT annotation than another mirror file
    gives the same field. The same body is then modelled two ways in two files and at most one is
    right. Allowed only BY NAME in `JUSTIFIED_MISMATCH`, each entry carrying why.

FIRST MEASUREMENT (gen #32): **47 reads OK, 5 MISSING, 2 MISMATCH.** The two mismatches are one
field in one file and are DELIBERATE — `stmt_control_flow.py` narrows `_record_types` from the live
`Dict[str, Any]` to `Dict[str, Dict[str, str]]` so the emitter models it as a nested string map
rather than an int-erased `ref 0`, and the file reads only `whyml_name` (a string) out of it. That
justification is written in the mirror at the declaration, it was checked against every read in the
file, and it holds. It is allowlisted rather than tolerated by a count, so the NEXT narrowing — which
may not be justified — fails.

Usage:  bin/check-sibling-concrete-field-decls.py [--verbose]
"""
import argparse
import ast
import collections
import os
import sys

ROOT = "src/self-annotate/src"

# RATCHET: a relocated body reading a field its destination file does not declare. Each is a
# latent int-erasure. May only SHRINK.
# (#49) gen #32: first measurement, 5.
MAX_MISSING = 5

# A destination annotation that DIFFERS from another mirror file's for the same field is allowed
# only by name, with the reason. A count would let the next one in silently.
JUSTIFIED_MISMATCH = {
    # `stmt_control_flow.py` narrows the live `Dict[str, Any]` so the emitter models the field as
    # `map string (option (map string (option string)))` and `_rt` is a nested string map rather
    # than an int-erased `ref 0`. CHECKED against every read in that file: only `whyml_name` is
    # projected, and it is a string. The justification is written at the declaration itself.
    ("src/self-annotate/src/module6_whyml/stmt_control_flow.py", "_record_types"),
}

# A zero-input guard (the #44 rule): a gate that cannot tell "nothing is wrong" from "I looked at
# nothing" is not a gate. 30 is below the measured 47+5+2 and the population only grows.
MIN_READS = 30


def class_level_fields(path):
    """{field -> annotation text} for class-level `X: T` in this file."""
    out = {}
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for st in node.body:
                if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                    out[st.target.id] = ast.unparse(st.annotation)
    return out


def relocated_defs(path):
    """Yield (def_node, lines) for each def whose preceding `#@` block says `sibling_concrete`."""
    lines = open(path, encoding="utf-8").read().splitlines()
    tree = ast.parse("\n".join(lines))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        i = node.lineno - 2
        while i >= 0:
            s = lines[i].strip()
            if not (s.startswith("#") or s.startswith("@") or not s):
                break
            if "sibling_concrete" in s:
                yield node
                break
            i -= 1


def self_reads(node):
    """Every `self.<f>` READ in this body, plus `getattr(self, "<f>", ...)`."""
    out = set()
    for n in ast.walk(node):
        if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                and n.value.id == "self" and isinstance(n.ctx, ast.Load)):
            out.add(n.attr)
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "getattr" and len(n.args) >= 2
                and isinstance(n.args[0], ast.Name) and n.args[0].id == "self"
                and isinstance(n.args[1], ast.Constant)
                and isinstance(n.args[1].value, str)):
            out.add(n.args[1].value)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(ROOT):
        print("[!] sibling-concrete-field-decls: %s is not a directory." % ROOT, file=sys.stderr)
        return 2

    files = []
    for dp, dn, fns in os.walk(ROOT):
        dn[:] = [d for d in dn if d != "__pycache__"]
        files.extend(os.path.join(dp, f) for f in sorted(fns) if f.endswith(".py"))

    decl = {p: class_level_fields(p) for p in files}
    elsewhere = collections.defaultdict(dict)
    for p, d in decl.items():
        for f, ann in d.items():
            elsewhere[f][p] = ann

    ok = 0
    missing, mismatch = [], []
    for p in files:
        for node in relocated_defs(p):
            for f in sorted(self_reads(node)):
                if f.startswith("__") or f not in elsewhere:
                    continue                       # a method, or a name no mirror models as a field
                here = decl[p].get(f)
                others = {v for k, v in elsewhere[f].items() if k != p}
                if here is None:
                    missing.append((p, node.name, f, sorted(others)))
                elif others and here not in others:
                    mismatch.append((p, node.name, f, here, sorted(others)))
                else:
                    ok += 1

    total = ok + len(missing) + len(mismatch)
    if total < MIN_READS:
        print("[!] sibling-concrete-field-decls: only %d field read(s) found across the relocated "
              "defs, below the floor of %d. The `sibling_concrete` scan or the declaration scan is "
              "broken, and this gate cannot tell 'nothing is wrong' from 'I looked at nothing'."
              % (total, MIN_READS), file=sys.stderr)
        return 1

    if args.verbose:
        for p, fn, f, anns in missing:
            print("    MISSING   %s::%s  reads self.%s  (declared elsewhere as %s)"
                  % (p, fn, f, anns))
        for p, fn, f, here, anns in mismatch:
            print("    MISMATCH  %s::%s  self.%s  here=%r  elsewhere=%s" % (p, fn, f, here, anns))

    unjustified = [r for r in mismatch if (r[0], r[2]) not in JUSTIFIED_MISMATCH]

    print("[*] sibling-concrete-field-decls: %d field read(s) across `#@ sibling_concrete` "
          "relocations — %d resolve to a declaration in their own file, %d MISSING, %d MISMATCH "
          "(%d unjustified)." % (total, ok, len(missing), len(mismatch), len(unjustified)))

    rc = 0
    if len(missing) > MAX_MISSING:
        print("[!] sibling-concrete-field-decls: %d MISSING > %d. A relocated body reads a field "
              "its own file does not DECLARE, so the untyped `getattr` default makes it an opaque "
              "INT map — a latent int-erasure that surfaces as a Why3 type error the next time the "
              "body is re-ported (backlog #63). Declare the field with the annotation the other "
              "mirror file gives it." % (len(missing), MAX_MISSING), file=sys.stderr)
        for p, fn, f, anns in missing:
            print("      %s::%s  self.%s  -> declare as %s" % (p, fn, f, anns), file=sys.stderr)
        rc = 1
    if unjustified:
        print("[!] sibling-concrete-field-decls: %d UNJUSTIFIED MISMATCH(ES). The same field is "
              "modelled two ways in two mirror files and at most one is right. Either make them "
              "agree, or add the (file, field) pair to JUSTIFIED_MISMATCH with the reason AND write "
              "that reason at the declaration." % len(unjustified), file=sys.stderr)
        for p, fn, f, here, anns in unjustified:
            print("      %s::%s  self.%s  here=%r  elsewhere=%s" % (p, fn, f, here, anns),
                  file=sys.stderr)
        rc = 1
    if rc == 0:
        print("[+] sibling-concrete-field-decls: OK — MISSING %d (ratchet %d, may only shrink), "
              "MISMATCH %d, all justified by name." % (len(missing), MAX_MISSING, len(mismatch)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
