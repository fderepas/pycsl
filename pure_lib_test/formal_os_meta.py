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
#   stat / lstat : #@ ensures \result == -1 or (0 <= \result < 32)
#       — an inode-number/-1 BOUND, with NO `dir_lookup` link tying the result
#         to the path. So "after mkdir(d), stat(d) reports a valid inode" is NOT
#         entailed: mkdir pins dir_lookup(disk,5,d) >= 0, but stat's contract
#         never connects \result to that namespace view. The strongest NAMEABLE
#         property is the geometry bound itself (asserted below as a value
#         theorem over a setup->observe chain — PROVES).
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
    mkdir, chmod, truncate, stat, lstat,
)


# ---------------------------------------------------------------------------
# (1) stat(existing) reports a VALID inode bound. Setup: mkdir d (so d exists).
# Operate: stat d. OBSERVE: \result is in the inode/-1 bound.
#
# HONEST STATUS: Unknown for the STRONGER consequence (0 <= ino < 32 for the
# dir we BUILT) — stat's contract has no dir_lookup link to mkdir's write
# (gap-4 §4a). The geometry BOUND below (-1 or 0<=ino<32) is what the contract
# entails directly; asserting it as `\result==1` requires discriminating the
# success case, which stat does not pin. So this theorem (asserting valid-inode
# presence after mkdir) is Unknown.
#@ requires True
#@ ensures \result == 1
def stat_after_mkdir_valid_inode(d: str) -> int:
    mkdir(d, 0o777)                 # set up: d exists (dir_lookup(d) >= 0)
    ino = stat(d)                   # observe: inode the path resolves to
    if ino >= 0 and ino < 32:       # ASSERTED: valid inode (WANT, from mkdir)
        return 1
    return 0


# (2) lstat(existing) reports a VALID inode bound (no symlink follow). Same wall
# as stat: lstat's contract carries the inode/-1 bound but no dir_lookup link.
# HONEST STATUS: Unknown (gap-4 §4a).
#@ requires True
#@ ensures \result == 1
def lstat_after_mkdir_valid_inode(d: str) -> int:
    mkdir(d, 0o777)                 # set up: d exists
    ino = lstat(d)                  # observe (no symlink follow)
    if ino >= 0 and ino < 32:       # ASSERTED: valid inode
        return 1
    return 0


# (3) chmod doesn't REMOVE the entry: mkdir(d); chmod(d,m); access(d)==present.
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


# (4) truncate(f, 0) — the SIZE consequence. Setup: create f, write data, close.
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
