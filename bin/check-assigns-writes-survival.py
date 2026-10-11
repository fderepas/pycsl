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
#   (#49) gen #34: **2989 -> 3070, AND THIS IS NOT A LOOSENING.** The old figure was measured
#   through a BROKEN NAME KEY (see `source_assigns` below) that could never match 346 of 1066
#   source entries, so the plane was counting over 457 declarations where the correct key finds
#   **583**. 2989 was therefore never a measurement of the invariant this plane states; there is
#   no comparable old number to shrink from. **The load-bearing fact is that `MAX_HOLE = 0`
#   HOLDS UNDER THE CORRECTED, LARGER POPULATION** — measured, HOLE 0 both before and after —
#   which makes the corrected zero a STRONGER negative than the one it replaces. The gate was
#   GREEN at 2989 when this was fixed, so nothing was accommodated: a bigger honest number was
#   chosen over a smaller wrong one. From here the rule stands unchanged — may only SHRINK.
MAX_TRAP = 3070
#   (#49) gen #35, backlog #75 — THE POPULATION WAS GATED ON THE PROPERTY IT MEASURES, AND IS NOW
#   SPLIT RATHER THAN RE-BASELINED. Module 6 used to emit a method's `#@ assigns` as `writes` ONLY
#   for a `@mutable_state` class, so every non-`@mutable_state` symbol had no `writes` and was
#   SKIPPED here (`if not w: continue`) — a 100%-dropped clause was invisible, its worst case.
#   Gen #35 made the emitter carry the frame on a bodyless `val` of ANY class whose record emits
#   the field as mutable. That admits 41 functions and 1549 occurrences that were always dropped
#   and never counted. Folding them into `MAX_TRAP` would have meant moving a "may only SHRINK"
#   ratchet UP, so the population is SPLIT on the one fact that created it — whether the source
#   class carries `@mutable_state` — and each arm has its own ratchet:
#     TRAP     (`@mutable_state` classes): measured 3058 at the split (3070 = 3058 + 12; the 12
#              non-`@mutable_state` occurrences the old population held move to the other arm)
#     TRAP-NMS (every other class):        measured 1549 at the split, FIRST MEASUREMENT
#   Both may only SHRINK. The sum is NOT comparable to the old 3070 and must never be quoted as
#   a rise.
#   (#49) gen #35, backlog #77 batch 1: 3058 -> **2643** and 1549 -> **1529** — FIVE fields
#   (`_frame_trigger_active`, `_comp_content_counter`, `_needs_array_init`, `_obj_state_written`,
#   `_todict_arg_wants_pymap`, types read off the live initialisers) DECLARED on
#   ExpressionEmissionMixin, so the `_handle_dotted_call` cluster's clauses EMIT them. The first
#   time this ratchet has fallen by declaration at scale; HOLE stayed 0 and the underdeclaration
#   plane's HOLE-T stayed 0 (the chain of three, measured before landing).
MAX_TRAP = 2643
MAX_TRAP_NMS = 1529
#   (#49) gen #35, backlog #75 — THE ARM THAT LOOKS AT THE SKIPPED SET. A symbol with NO `writes`
#   clause whose source `#@ assigns` names a field its class's record emits as MUTABLE is a
#   HOLE in waiting: no frame at all, the field mentionable, so a caller proves it unchanged.
#   Gen #34 counted 35 such rows by hand; restricted to bodyless `val`s the arm measures **505**
#   at 7c431aa2 (the hand count saw one file). The gen #35 emitter repair takes it to **8**, and
#   the 8 are a DIFFERENT mechanism, named so nobody re-derives it: all in
#   `frontend____init__.mlw`, the importer stubs of `ConcurrencyChecker` (`check`,
#   `_check_function`, `_walk_body`, `_walk_stmt`, `_warn_if_unprotected`). A mirror's import
#   resolves to the LIVE module (lesson (c5)), whose methods carry NO `#@ assigns`, so the stub
#   is a frame-free `val` — route #212's shape (probes.tsv 2026-10-11: an UN-ANNOTATED imported
#   mutator lets an importer PROVE a false `\result == 0`). Fail-closed here TODAY only by ZERO
#   call sites in that file — a measurement. Ceiling, may only SHRINK.
MAX_HOLE_NOWRITES = 8
# A zero-input guard: the #44 rule, a gate that cannot tell "nothing is wrong" from "I looked at
# nothing" is not a gate. (#49) gen #34: raised 200 -> 500. The old floor of 200 was set below the
# then-measured 222 and could NOT notice the broken key, which cost 126 declarations — a floor
# chosen under a defect inherits the defect. 500 is below the corrected 583.
#
# AND A SECOND GUARD ON THE KEY ITSELF, because a floor on the RESULT cannot catch a key that is
# wrong for a whole NAME SHAPE. `MAX_UNRESOLVED_KEYS` bounds how many source (class, def) keys
# match NO emitted symbol anywhere. Measured at the corrected key: see the printout. A rise means
# either the key drifted again or methods stopped being emitted, and both deserve a look.
MIN_FUNCS_WITH_WRITES = 500
#   MAX_UNRESOLVED_KEYS — source `(class, def)` keys matching NO emitted symbol. (#49) gen #34
#   first measurement under the CORRECTED key: **134**, and they are a known residue rather than
#   a mystery: `__init__` (inlined into the emitted record's `by` witness, so no `<cls>____init__`
#   spelling exists anywhere), nested closures FOLDED into their emitted parent, and typing-only
#   Protocol / `*View` classes that never produce a declaration at all. A RISE means either the key
#   drifted from the emitter's rule again or methods stopped being emitted, and BOTH narrow this
#   plane's population silently, which is the failure this constant exists to make loud.
MAX_UNRESOLVED_KEYS = 134


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


def unresolved_keys(emit_dir, src_assigns):
    """(#49) gen #34 — THE GUARD ON THE KEY ITSELF, not on the result.

    A floor on the number of declarations found cannot catch a key that is wrong for an entire
    NAME SHAPE: the old key missed every `transpile`-like name and the floor of 200 sat happily
    below the 222 it produced. So this counts the source `(class, def)` keys that match NO
    emitted symbol ANYWHERE in the emission. A rise means either the key drifted again or
    methods stopped being emitted, and both deserve a look rather than a silently smaller
    number.
    """
    present = set()
    for f in sorted(os.listdir(emit_dir)):
        if not f.endswith(".mlw"):
            continue
        text = open(os.path.join(emit_dir, f), encoding="utf-8").read()
        for m in re.finditer(r"^\s*(?:let|val|with)\s+(?:function\s+|rec\s+|partial\s+|ghost\s+)*(\w+)\s*\(",
                             text, re.M):
            present.add(m.group(1))
    out = []
    for (cls, fnname) in sorted(src_assigns):
        if f"{cls.lower()}__{fnname}" not in present:
            out.append((cls, fnname))
    return out


def mutable_state_classes(mirror_root=MIRROR_ROOT):
    """(#49) gen #35 — the source classes decorated `@mutable_state` (the population key)."""
    out = set()
    for dirpath, dirnames, filenames in os.walk(mirror_root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            lines = open(os.path.join(dirpath, fn), encoding="utf-8").read().splitlines()
            for i, ln in enumerate(lines):
                mc = re.match(r"^class\s+(\w+)", ln)
                if mc and any(re.match(r"^@mutable_state\b", lines[k])
                              for k in range(max(0, i - 4), i)):
                    out.add(mc.group(1))
    return out


MEASURE_EXTRA = {}


def measure(emit_dir, src_assigns, want_trap_rows=False):
    """-> (trap_count, hole_rows, n_funcs_with_writes[, trap_rows]).

    (#49) gen #35: also fills MEASURE_EXTRA with `trap_nms` (the non-`@mutable_state` arm, NOT
    included in the returned `trap_count`) and `nowrites_holes`.
    """
    trap = 0
    trap_nms = 0
    nowrites_holes = []
    ms_classes = mutable_state_classes()
    trap_rows = []
    hole_rows = []
    n_writes = 0
    by_name = collections.defaultdict(list)
    for (cls, fnname), fields in src_assigns.items():
        # (#49) gen #34 — THE KEY WAS WRONG FOR EVERY NAME WITHOUT EXACTLY ONE LEADING `_`.
        # It used to be `f"{cls.lower()}___{fnname.lstrip('_')}"`: three underscores plus a
        # strip, which happens to be right for `_emit_body_code` and is WRONG for `transpile`,
        # `__init__`, `extend`, `audit_rocq`, … The emitter's rule is ONE spelling, at
        # `src/pycsl/frontend/Module5_IREmitter.py:6070`:
        #     func_name = f"{self._current_class.lower()}__{node.name}"
        # i.e. TWO underscores and the name AS WRITTEN. Measured cost of the old key: of 1066
        # source entries, **346** produced a key that can never match an emitted symbol (320
        # with no leading underscore, 26 dunders), and the plane saw **457** declarations
        # where it should see **583**.
        by_name[f"{cls.lower()}__{fnname}"].append((cls, fields))
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
                # (#49) gen #35: the skipped set is no longer unexamined. A declared field
                # that the record emits as MUTABLE, on a BODYLESS `val` with NO frame at all,
                # is a caller-provable preservation the source never promised. A concrete
                # `let` is excluded: Why3 INFERS its write effect from the body and callers
                # see the inferred effect, so a missing clause there drops no frame.
                if not re.match(r"\s*val\b", m.group(0)):
                    continue
                for cls, fields in by_name[name]:
                    rec = recs.get(cls.lower(), set())
                    for fld in sorted({x.lstrip("_") for x in fields} & rec):
                        nowrites_holes.append((f, name, fld))
                continue
            n_writes += 1
            emitted = {_bare(x.group(1)) for x in re.finditer(r"self\.(\w+)", w.group(1))}
            for cls, fields in by_name[name]:
                rec = recs.get(cls.lower(), set())
                for fld in sorted({x.lstrip("_") for x in fields} - emitted):
                    if fld in rec:
                        hole_rows.append((f, name, fld))
                    elif cls not in ms_classes:
                        trap_nms += 1
                    else:
                        trap += 1
                        if want_trap_rows:
                            trap_rows.append((f, cls, name, fld))
    MEASURE_EXTRA["trap_nms"] = trap_nms
    MEASURE_EXTRA["nowrites_holes"] = nowrites_holes
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

    unres = unresolved_keys(args.emit_dir, src)
    print("[*] assigns-writes-survival: %d source (class, def) key(s) match NO emitted symbol "
          "(ceiling %d) — the guard on the KEY, added after the old key silently missed 346 of "
          "1066." % (len(unres), MAX_UNRESOLVED_KEYS))
    if len(unres) > MAX_UNRESOLVED_KEYS:
        print("[!] assigns-writes-survival: %d unresolved key(s) > %d. Either the name key drifted "
              "from the emitter's `f\"{cls.lower()}__{node.name}\"` rule, or these methods stopped "
              "being emitted. Both narrow this plane's population silently."
              % (len(unres), MAX_UNRESOLVED_KEYS), file=sys.stderr)
        for cls, fn in unres[:25]:
            print("      %s.%s" % (cls, fn), file=sys.stderr)
        return 1

    if n_writes < MIN_FUNCS_WITH_WRITES:
        print("[!] assigns-writes-survival: only %d emitted function(s) carry a `writes` clause, "
              "below the floor of %d. The emission or the name mapping is broken, and this gate "
              "cannot tell 'nothing is wrong' from 'I looked at nothing'."
              % (n_writes, MIN_FUNCS_WITH_WRITES), file=sys.stderr)
        return 1

    if args.verbose:
        for f, name, fld in holes:
            print("    HOLE  %s::%s  field=%s" % (f, name, fld))

    trap_nms = MEASURE_EXTRA.get("trap_nms", 0)
    nowrites = MEASURE_EXTRA.get("nowrites_holes", [])
    print("[*] assigns-writes-survival: %d emitted function(s) with a `writes` clause; "
          "%d dropped `#@ assigns` field occurrence(s) — TRAP %d (`@mutable_state` classes) + "
          "TRAP-NMS %d (other classes; both absent from the class record, so unmentionable and "
          "fail-closed), HOLE %d (present in the record); HOLE-NOWRITES %d (no frame at all, "
          "field mutable in the record)."
          % (n_writes, trap + trap_nms + len(holes), trap, trap_nms, len(holes), len(nowrites)))

    rc = 0
    if len(nowrites) > MAX_HOLE_NOWRITES:
        print("[!] assigns-writes-survival: HOLE-NOWRITES %d > %d — a symbol with NO `writes` "
              "clause declares `#@ assigns self.<f>` and its class record emits `f` as mutable, "
              "so a caller can mention the field and PROVE it unchanged across the call."
              % (len(nowrites), MAX_HOLE_NOWRITES), file=sys.stderr)
        for f, name, fld in nowrites[:40]:
            print("      %s::%s  field=%s" % (f, name, fld), file=sys.stderr)
        rc = 1
    if trap_nms > MAX_TRAP_NMS:
        print("[!] assigns-writes-survival: TRAP-NMS %d > %d. This ratchet may only SHRINK."
              % (trap_nms, MAX_TRAP_NMS), file=sys.stderr)
        rc = 1
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
        print("[+] assigns-writes-survival: OK — HOLE %d (ceiling %d), HOLE-NOWRITES %d (ceiling "
              "%d), TRAP %d (ratchet %d) + TRAP-NMS %d (ratchet %d), both may only shrink."
              % (len(holes), MAX_HOLE, len(nowrites), MAX_HOLE_NOWRITES, trap, MAX_TRAP,
                 trap_nms, MAX_TRAP_NMS))
    return rc


if __name__ == "__main__":
    sys.exit(main())
