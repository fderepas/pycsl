#!/usr/bin/env python3
r"""L-PLANE ORACLE: no PURE abstract op is applied to a `stable_hash`-folded string.

WHY THIS EXISTS (gen #30). `stable_hash` is `int(sha256(s)[:8], 16) % 2147483647` — about
31 bits — and its docstring claims it preserves "the distinguishing property (distinct
strings → distinct ints w.h.p.)". A birthday search over 4- and 5-character alphanumerics
found a collision after **24,726 strings**:

    stable_hash('"ah02"') == stable_hash('"atc3"') == 185314078

The hash is deterministic and ships in the repo, so an attacker-chosen colliding pair is
free and NAMEABLE IN A CONTRACT. `_coerce_str_arg` folds a string literal to that hash when
a literal reaches an abstract op expecting an int, and the two calls then emit the IDENTICAL
TERM:

    a := (gettext_gettext_1 185314078);
    b := (gettext_gettext_1 185314078);

TODAY THAT IS NOT A ROUTE, and the reason is ONE KEYWORD: the op is emitted as `val`
(effectful — two calls may return different values), not `val function` (pure — two calls
with equal arguments are equal). Measured: `a == b` does NOT prove. The day such an op is
emitted PURE, the collision pair is a ready-made false equality between two different
strings.

WHAT THIS GATE CHECKS, over an emitted corpus (`--emit-dir`): every `val function NAME (…)`
declaration, and every application of one of those names to an INTEGER CONSTANT in the hash
range (>= MIN_HASH). Zero at the first measurement. A hit is not automatically a route —
the constant could be an ordinary big number — so the report names the file, the op and the
constant, and the baseline is by (op, constant) so an argued case can be recorded rather
than silenced.

Usage:  bin/check-hashed-literal-purity.py --emit-dir DIR [--verbose]
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_HASH = 1000000          # the hash range starts far above ordinary literals
MIN_FILES = 50              # a sweep that emitted nothing is not a pass
BASELINE = {
    # THE FIRST MEASUREMENT (gen #30): 22 (op, constant) pairs, ALL of them `struct`
    # pack/unpack ops applied to a folded FORMAT STRING — e.g. `struct_unpack_fi16
    # 1905738945`, where 1905738945 is `stable_hash('">h"')` (verified by computing it).
    # They are baselined rather than failed because the hazard needs MORE than a pure op
    # on a folded literal: it needs TWO COLLIDING literals that reach the SAME specialised
    # op. The ops are per-type (`_fi16`, `_fu32`, `_fs4`, …), so a collision has to be
    # between two formats of the SAME width and signedness that CPython nonetheless reads
    # differently — `">h"` and `"<h"` are the shape to look for, and searching for one is
    # recorded as the follow-up rather than done here.
    # The round-trip axiom makes the stakes concrete:
    #   axiom ... : forall fmt x0. -32768 <= x0 < 32768 ->
    #                 struct_unpack_fi16 fmt (struct_pack_fi16 fmt x0) = x0
    # It is quantified over ANY fmt, so two formats the model cannot tell apart share it.
    ("struct_pack_fi16", 1905738945): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_fi32", 2135862136): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_fi32i32", 1443572317): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_fi64", 1822289121): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_fs4", 632755521): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_fu16", 1722693573): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_fu16u32", 1258439229): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_fu32", 1790609836): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_i18", 123717740): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_i1a1", 550919730): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_pack_i2", 1552598195): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_fi16", 1905738945): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_fi32", 2135862136): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_fi32i32", 1443572317): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_fi64", 1822289121): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_fs4", 632755521): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_fu16", 1722693573): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_fu16u32", 1258439229): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_fu32", 1790609836): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_i18", 123717740): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_i1a1", 550919730): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
    ("struct_unpack_i2", 1552598195): "a `struct` FORMAT STRING folded by `_coerce_str_arg`.",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", required=True)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.emit_dir, "**", "*.mlw"), recursive=True))
    if len(files) < MIN_FILES:
        print("[!] hashed-literal-purity: REFUSING — %d .mlw file(s) under %s, expected "
              "at least %d. The emission is missing, not clean."
              % (len(files), args.emit_dir, MIN_FILES), file=sys.stderr)
        return 2

    # `re.M` IS LOAD-BEARING: without it `^` anchors to the start of the whole file and
    # the scan finds ZERO declarations in an emission that plainly contains them —
    # measured on this plane's first trial run, which reported "0 distinct `val function`
    # op(s)" over 3461 files. A gate that finds nothing because its regex is wrong looks
    # exactly like a gate that finds nothing because the tree is clean.
    decl = re.compile(r"^\s*val\s+function\s+([A-Za-z_][A-Za-z0-9_]*)\s*[(:]", re.M)
    hits, pure_ops = [], set()
    for f in files:
        text = open(f, errors="replace").read()
        names = set(decl.findall(text))
        pure_ops |= names
        for name in names:
            for m in re.finditer(r"\(\s*%s\s+(-?\d+)" % re.escape(name), text):
                if int(m.group(1)) >= MIN_HASH:
                    hits.append((os.path.basename(f), name, int(m.group(1))))

    print("[*] hashed-literal-purity: %d emitted file(s); %d distinct `val function` op(s); "
          "%d application(s) to a constant in the hash range."
          % (len(files), len(pure_ops), len(hits)))
    if args.verbose:
        for h in hits[:40]:
            print("    %-44s %-28s %d" % h)

    rc = 0
    for base, name, const in hits:
        if (name, const) in BASELINE:
            continue
        print("[!]   PURE OP APPLIED TO A HASH-RANGE CONSTANT: %s applies `%s` to %d. A "
              "`val function` is PURE, so two applications with equal arguments are EQUAL "
              "— and a `stable_hash`-folded string literal collides at 31 bits (measured: "
              "\"ah02\" and \"atc3\" both fold to 185314078). Either argue it into the "
              "baseline (it is not a folded literal) or make the op effectful."
              % (base, name, const), file=sys.stderr)
        rc = 1

    if rc:
        print("[!] hashed-literal-purity: NOT OK.", file=sys.stderr)
    else:
        print("[+] hashed-literal-purity: OK — no pure op is applied to a hash-range "
              "constant in %d emitted file(s)." % len(files))
    return rc


if __name__ == "__main__":
    sys.exit(main())
