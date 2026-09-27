#!/usr/bin/env python3
r"""L-PLANE ORACLE: does every field named in a `#@ assigns` clause REACH the emitted `writes`?

WHY THIS EXISTS (#49, gen #32). Backlog #63's re-port of the three stale `#@ sibling_concrete`
bodies produced a Why3 type error, and the cause was that `_record_field_elem_locals` — a field
the re-ported `_field_type_of` reads — had never been DECLARED on the mirror's
`StatementEmissionMixin`. Fixing that declaration changed the emitted WhyML in a way nobody had
asked for: a `writes` clause GAINED the field. Reading backwards from that one line:

    `statements.py::_emit_body_code` declares `#@ assigns` over NINETY-THREE self-fields.
    Its emitted `writes` clause carried TWENTY-NINE. Sixty-four were SILENTLY DROPPED.

Module 6 builds the `writes` set from the fields of the emitting class's RECORD, so a field the
record does not carry cannot appear in `writes` and is dropped without a word. A `#@ assigns`
clause is a FRAME GUARANTEE in the source, and 3x more of it was being written than emitted.

>>> A `#@ assigns` CLAUSE NAMING A FIELD THE CLASS DOES NOT DECLARE IS A CLAUSE THAT READS AS A
>>> GUARANTEE AND EMITS NOTHING.

WHAT IT MEASURES, and the DISCRIMINATOR that decides whether it is a hole or a trap. For every
emitted function carrying a `writes` clause, the set of `#@ assigns self.<f>` fields declared in
the mirror source is compared against the emitted `writes`. Each dropped field is then classified
against the EMITTING CLASS'S RECORD:

  * **TRAP** — the field is ALSO absent from the record. No caller can mention it, so no caller can
    prove anything about it: the drop is FAIL-CLOSED. It is still a trap, because a human auditing
    the mirror's frames by reading `#@ assigns` believes a guarantee that was never emitted.
  * **HOLE** — the field IS in the record. Then a caller CAN mention it, and it is absent from the
    frame of a function DECLARED to write it, so the caller PROVES IT UNCHANGED across that call.
    That is route #96's shape in a new mechanism (#96: a bodyless `val` drops an array-region
    `assigns`; here: an `assigns` naming an undeclared field drops silently).

FIRST MEASUREMENT (gen #32, at the post-#63 tree): **TRAP 2989, HOLE 0**, over 222 functions. The
drop and the unmentionability turn out to have the SAME cause and to be exactly coextensive, which
is why the whole population is fail-closed. That is a MEASUREMENT, not a theorem — nothing in the
emitter promises it — so `MAX_HOLE = 0` is the invariant worth enforcing, and this plane exists to
enforce it rather than to have observed it once.

>>> THE HOLE ARM HAS AN EMPTY POPULATION, SO IT IS NEGATIVE-TESTED IN-TREE. `--self-test` copies
>>> the emission, injects one field into a class RECORD and into NO `writes` clause, and requires
>>> HOLE to become >= 1 and to name the function. A guard whose population is empty has checked
>>> nothing and looks exactly like a guard that passed; this one is made to fire on demand.

Usage:
    bin/check-assigns-writes-survival.py --emit-dir <dir>     # <dir> from bin/mirror-emit-sweep.sh
    bin/check-assigns-writes-survival.py --emit-dir <dir> --self-test
    bin/check-assigns-writes-survival.py --emit-dir <dir> --verbose
"""
import argparse
import collections
import os
import re
import shutil
import sys
import tempfile

MIRROR_ROOT = "src/self-annotate/src"

# RATCHETS.
#   MAX_HOLE may NEVER rise. A hole is a caller proving a field unchanged across a call declared
#   to write it, and there is no such thing as an acceptable one.
MAX_HOLE = 0
#   MAX_TRAP may only SHRINK. It falls whenever a field named in an `#@ assigns` is actually
#   declared on its class (backlog #63 took it 2991 -> 2989 by declaring ONE field).
#   (#49) gen #32: first measurement, 2989.
MAX_TRAP = 2989
# A zero-input guard: the #44 rule, a gate that cannot tell "nothing is wrong" from "I looked at
# nothing" is not a gate. 200 is below the measured 222 and the mirror only grows.
MIN_FUNCS_WITH_WRITES = 200


def _bare(raw):
    """`statementemissionmixin__record_types` and `_record_types` both -> `record_types`.

    The per-file emission spells a mixin field bare (`_slice_set_tmp_counter`) while the
    aggregate `Module6_WhyMLTranspiler.mlw` prefixes it with the class
    (`statementemissionmixin__slice_set_tmp_counter`). Both spellings must fold to one key or the
    aggregate file reports every field of every class as dropped.
    """
    return (raw.split("__", 1)[1] if "__" in raw else raw).lstrip("_")


def source_assigns(mirror_root=MIRROR_ROOT):
    """(class, def) -> {bare field names} for every `#@ assigns self.<f>, ...` in the mirror.

    Only `self.<name>` items are collected. `\\nothing`, `\\result`, an array region and a
    non-`self` target are all outside this plane's question.
    """
    out = {}
    for dirpath, dirnames, filenames in os.walk(mirror_root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            lines = open(os.path.join(dirpath, fn), encoding="utf-8").read().splitlines()
            pending = None
            for i, ln in enumerate(lines):
                m = re.match(r"^\s*#@\s*assigns\s+(.*)$", ln)
                if m:
                    pending = {mm.group(1) for mm in
                               (re.match(r"^self\.(\w+)$", x.strip())
                                for x in m.group(1).split(",")) if mm}
                    continue
                m2 = re.match(r"^\s*def\s+(\w+)\s*\(", ln)
                if m2:
                    if pending is not None:
                        cls = None
                        for k in range(i, -1, -1):
                            mc = re.match(r"^class\s+(\w+)", lines[k])
                            if mc:
                                cls = mc.group(1)
                                break
                        if cls is not None:
                            out[(cls, m2.group(1))] = pending
                    pending = None
                elif not (re.match(r"^\s*#@", ln) or re.match(r"^\s*@", ln) or not ln.strip()):
                    # any other real line between the clause and a `def` breaks the attachment
                    pending = None
    return out


def measure(emit_dir, src_assigns, want_trap_rows=False):
    """-> (trap_count, hole_rows, n_funcs_with_writes[, trap_rows])."""
    trap = 0
    trap_rows = []
    hole_rows = []
    n_writes = 0
    by_name = collections.defaultdict(list)
    for (cls, fnname), fields in src_assigns.items():
        by_name[f"{cls.lower()}___{fnname.lstrip('_')}"].append((cls, fields))
    for f in sorted(os.listdir(emit_dir)):
        if not f.endswith(".mlw"):
            continue
        text = open(os.path.join(emit_dir, f), encoding="utf-8").read()
        recs = {}
        for m in re.finditer(r"type\s+(\w+)\s*=\s*\{([^}]*)\}", text):
            recs[m.group(1)] = {_bare(x.group(1))
                                for x in re.finditer(r"mutable\s+(\w+)\s*:", m.group(2))}
        for m in re.finditer(r"^\s*(?:let|val)\s+(?:function\s+|rec\s+|ghost\s+)*(\w+)\s*\(",
                             text, re.M):
            name = m.group(1)
            if name not in by_name:
                continue
            seg = text[m.end(): m.end() + 20000]
            stop = re.search(r"^\s*(?:let|val)\s", seg, re.M)
            if stop:
                seg = seg[:stop.start()]
            w = re.search(r"writes\s*\{([^}]*)\}", seg)
            if not w:
                continue
            n_writes += 1
            emitted = {_bare(x.group(1)) for x in re.finditer(r"self\.(\w+)", w.group(1))}
            for cls, fields in by_name[name]:
                rec = recs.get(cls.lower(), set())
                for fld in sorted({x.lstrip("_") for x in fields} - emitted):
                    if fld in rec:
                        hole_rows.append((f, name, fld))
                    else:
                        trap += 1
                        if want_trap_rows:
                            trap_rows.append((f, cls, name, fld))
    if want_trap_rows:
        return trap, hole_rows, n_writes, trap_rows
    return trap, hole_rows, n_writes


def self_test(emit_dir, src_assigns):
    """Negative-test the HOLE arm.

    Takes a field the measurement ALREADY reports as a TRAP — named by some class's `#@ assigns`,
    dropped from that function's `writes`, and absent from that class's record — and injects it
    into that class's RECORD and into no `writes` clause. That is exactly the HOLE shape, so HOLE
    must go from 0 to >= 1 and must name the function. Reusing a measured row is the point: a
    hand-picked field can already be in the record under another spelling, which is how the first
    version of this self-test reported the arm inert when it was not.
    """
    _, _, _, trap_rows = measure(emit_dir, src_assigns, want_trap_rows=True)
    if not trap_rows:
        print("[!] assigns-writes-survival --self-test: no TRAP row to build an injection from, so "
              "the self-test is INCONCLUSIVE and that is a failure.", file=sys.stderr)
        return 1
    tmp = tempfile.mkdtemp(prefix="awsurv_selftest_")
    try:
        for f in os.listdir(emit_dir):
            if f.endswith(".mlw"):
                shutil.copy2(os.path.join(emit_dir, f), os.path.join(tmp, f))
        fname, cls, fnname, fld = trap_rows[0]
        p = os.path.join(tmp, fname)
        t = open(p, encoding="utf-8").read()
        m = re.search(r"type\s+" + re.escape(cls.lower()) + r"\s*=\s*\{\s*mutable\s", t)
        if m is None:
            print("[!] assigns-writes-survival --self-test: no record for %s in %s." % (cls, fname),
                  file=sys.stderr)
            return 1
        # `<cls>__<field>` bares to `<field>` under _bare(), for the per-file and the aggregate
        # spelling alike, so one injection works in both.
        inj = "%s__%s: int; mutable " % (cls.lower(), fld)
        open(p, "w", encoding="utf-8").write(t[:m.end()] + inj + t[m.end():])
        _, holes, _ = measure(tmp, src_assigns)
        if not holes:
            print("[!] assigns-writes-survival --self-test: injected `%s` into %s's record in %s "
                  "and the HOLE arm did NOT fire. The arm is INERT and its zero is meaningless."
                  % (fld, cls, fname), file=sys.stderr)
            return 1
        print("[+] assigns-writes-survival --self-test: injected `%s` into %s's record in %s "
              "(it is named by that class's `#@ assigns` and dropped from `%s`'s writes) -> HOLE "
              "fired on %d row(s), e.g. %s::%s field=%s. The arm is LIVE."
              % (fld, cls, fname, fnname, len(holes), holes[0][0], holes[0][1], holes[0][2]))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", required=True,
                    help="a directory of emitted mirror .mlw files (bin/mirror-emit-sweep.sh)")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="negative-test the HOLE arm by injecting a field into a record")
    args = ap.parse_args()

    if not os.path.isdir(args.emit_dir):
        print("[!] assigns-writes-survival: --emit-dir %s is not a directory." % args.emit_dir,
              file=sys.stderr)
        return 2

    src = source_assigns()
    if args.self_test:
        return self_test(args.emit_dir, src)

    trap, holes, n_writes = measure(args.emit_dir, src)

    if n_writes < MIN_FUNCS_WITH_WRITES:
        print("[!] assigns-writes-survival: only %d emitted function(s) carry a `writes` clause, "
              "below the floor of %d. The emission or the name mapping is broken, and this gate "
              "cannot tell 'nothing is wrong' from 'I looked at nothing'."
              % (n_writes, MIN_FUNCS_WITH_WRITES), file=sys.stderr)
        return 1

    if args.verbose:
        for f, name, fld in holes:
            print("    HOLE  %s::%s  field=%s" % (f, name, fld))

    print("[*] assigns-writes-survival: %d emitted function(s) with a `writes` clause; "
          "%d dropped `#@ assigns` field occurrence(s) — TRAP %d (also absent from the class "
          "record, so unmentionable and fail-closed), HOLE %d (present in the record)."
          % (n_writes, trap + len(holes), trap, len(holes)))

    rc = 0
    if len(holes) > MAX_HOLE:
        print("[!] assigns-writes-survival: %d HOLE(S) > %d — a field is in the class RECORD and "
              "ABSENT from the `writes` of a function DECLARED to write it, so a caller PROVES it "
              "unchanged across that call. This is route #96's shape. Each is listed below; "
              "either declare the field into the frame or drop it from the `#@ assigns`."
              % (len(holes), MAX_HOLE), file=sys.stderr)
        for f, name, fld in holes:
            print("      %s::%s  field=%s" % (f, name, fld), file=sys.stderr)
        rc = 1
    if trap > MAX_TRAP:
        print("[!] assigns-writes-survival: TRAP %d > %d. This ratchet may only SHRINK: it falls "
              "when a field named in an `#@ assigns` is actually DECLARED on its class. A RISE "
              "means a new `#@ assigns` names a field that emits nothing."
              % (trap, MAX_TRAP), file=sys.stderr)
        rc = 1
    if rc == 0:
        print("[+] assigns-writes-survival: OK — HOLE %d (ceiling %d), TRAP %d (ratchet %d, may "
              "only shrink)." % (len(holes), MAX_HOLE, trap, MAX_TRAP))
    return rc


if __name__ == "__main__":
    sys.exit(main())
