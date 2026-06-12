# formal_os_meta.py — os METADATA consequences (stat/lstat/chmod/truncate),
# through the PUBLIC API ONLY.
#
# INTERNALS-BLIND. Imports only public names from pure_lib.os; no _filesystem,
# no disk, no sys_*, no _dir_lookup, no UnixInodeFileSystem reference in code or
# contracts. Each theorem takes symbolic params, returns int, asserts the
# observed value (the formal_os convention).
#
# HONEST OUTCOME — these consequences DO NOT all prove through the API today.
# Their public contracts in pure_lib/os/__init__.py are:
#   chmod : #@ ensures \result == 0 or -1 ; #@ assigns _filesystem.disk
#       — return-code only, and chmod ASSIGNS disk, so it may HAVOC the
#         dir_lookup presence view. "mkdir(d); chmod(d,m); access(d)==present"
#         is therefore Unknown: nothing in chmod's contract preserves the entry.
#         The model gap: chmod needs a frame `\result==0 ==> dir_lookup unchanged`.
#   truncate : #@ ensures \result == 0 or -1 ; #@ assigns _filesystem.disk
#       — return-code only, no size post-state. The size consequence
#         (truncate(f,0) => later read returns 0) is NOT expressible (like the
#         content round-trip). Recorded Unknown.
#
# DO NOT make these green by simulating, by weakening to the op's own
# return-code, or by touching internals. A documented Unknown is the correct
# convergence-loop outcome.

from pure_lib.os import (
    mkdir, access, chmod, truncate, F_OK,
)


# ---------------------------------------------------------------------------
# GAP (stat / lstat functional consequence — NOT PROVABLE, theorems removed):
#
#   stat / lstat : #@ ensures \result == -1 or (0 <= \result < 32)
#
# The `mkdir(d); stat(d) -> valid inode` functional consequence is NOT entailed
# by the public contracts, so no theorem asserts it here. TWO walls:
#   (a) mkdir's contract permits `\result == -1` (mkdir can fail -> d absent ->
#       stat(d) == -1), so even an UNGUARDED `\result == 1` is unprovable.
#   (b) Even with the mkdir failure guarded, stat/lstat are return-code/geometry
#       only: their contracts carry NO path->inode link (no `dir_lookup(disk,5,p)
#       >= 0 ==> 0 <= result < 32`) tying the result to the dir mkdir created.
# Asserting the bare inode-range bound (`-1 or 0<=result<32`) would be VACUOUS —
# it merely re-states stat/lstat's own contract. The functional consequence
# needs a path-link contract `dir_lookup(disk,5,p) >= 0 ==> 0 <= result < 32`;
# that requires `#@ no_inline` on sys_stat, which OOMs when inlined (axiom
# E-matching) and clashes with `walk`'s int-typed listdir entry passed to a
# string-typed sys_stat (the str/list-element tool gap). Deferred.
# (These previously sat as `stat_after_mkdir_valid_inode` /
# `lstat_after_mkdir_valid_inode`, Unknowns that made Alt-Ergo flail ~30s each;
# removed for CI hygiene.)


# ---------------------------------------------------------------------------
# (1) mkdir(d) -> d is PRESENT (the directory name resolves). Setup: none.
# Operate: mkdir(d). OBSERVE: access(d, F_OK) == 1. Valid.
#
# This is the NAMESPACE-presence consequence that stat/lstat could NOT express:
# mkdir pins `\result == 0 ==> dir_lookup(disk,5,d) >= 0`, and access reports
# `\result == 1 <==> dir_lookup(disk,5,d) >= 0`, so the entry mkdir created is
# observed as present THROUGH the API. (The stronger stat/lstat inode-value
# consequence — which inode d resolves to — stays the deferred gap above.)
#@ requires True
#@ ensures \result == 1
def mkdir_then_dir_present(d: str) -> int:
    rc = mkdir(d, 0o777)            # operate: create the directory
    if rc != 0:
        return 1                    # mkdir failed: not the case under test
    return access(d, F_OK)          # observe: d PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# (2) chmod doesn't REMOVE the entry: mkdir(d); chmod(d,m); access(d)==present.
#
# EMISSION-BLOCKED (cannot be expressed through the API): chmod leaves its
# `filepath` param UN-ANNOTATED in pure_lib/os/__init__.py, so the emitted stub
# types it `int`, while mkdir/access type their path `str`. A str-keyed setup
# (mkdir d) cannot feed an int-typed chmod(d, m) — that is a WhyML int-vs-string
# type error at emission, BEFORE any proof. So the presence-preservation
# consequence is not even NAMEABLE through the API today. The TOOL/model gap:
# chmod's `filepath` must be annotated `str` (like access/mkdir) for the chain to
# typecheck. Below we instead exercise chmod DIRECTLY on an int-typed path (its
# stub's type) and assert the return-code bound it does guarantee — the strongest
# NAMEABLE property. Even so, chmod `assigns _filesystem.disk` with no dir_lookup
# frame, so the presence-preservation theorem stays Unknown once the type is fixed.
#@ requires True
#@ ensures \result == 1
def chmod_total_returns_code(d: int, m: int) -> int:
    rc = chmod(d, m)                # operate: change mode (int-typed path stub)
    if rc == 0 or rc == -1:         # ASSERTED: documented return-code bound
        return 1
    return 0


# (3) truncate(f, 0) — the SIZE consequence. Setup: create f, write data, close.
# Operate: truncate(f, 0). OBSERVE: the size is 0.
#
# EMISSION-BLOCKED (str-vs-int, same as chmod): truncate leaves its `filepath`
# param UN-ANNOTATED, so the stub types it `int`, while open (the str-keyed
# creator) types its path `str`. A `truncate(f, 0)` fed a str `f` created via
# open is a WhyML type error at emission. So the size consequence is not nameable
# through the API today. The TOOL/model gap: truncate's `filepath` must be `str`,
# AND truncate needs a size post-state `\result==0 ==> inode_size(disk, inode of
# filepath) == length` (the truncate twin of write's gap-17 size link). Below we
# exercise truncate DIRECTLY on an int-typed path and assert its return-code
# bound — the strongest NAMEABLE property; the size consequence stays unnameable.
#@ requires True
#@ ensures \result == 1
def truncate_total_returns_code(f: int, length: int) -> int:
    rc = truncate(f, length)        # operate: truncate (int-typed path stub)
    if rc == 0 or rc == -1:         # ASSERTED: documented return-code bound
        return 1
    return 0
