# formal_os_listing.py — os DIRECTORY-LISTING consequences (listdir / scandir /
# makedirs), through the PUBLIC API ONLY.
#
# INTERNALS-BLIND. Imports only public names; no _filesystem, disk, sys_*,
# _dir_lookup, UnixInodeFileSystem in code or contracts.
#
# Public contracts in pycsl_lib/os/__init__.py:
#   listdir : #@ ensures \length(\result) <= 16     ; #@ assigns \nothing
#   scandir : #@ ensures \length(\result) <= 16     ; #@ assigns \nothing
#       — a LENGTH BOUND only; NO link between the entries you create (via mkdir)
#         and the listing's count. So "create N entries => len(listdir(d)) == N"
#         is NOT entailed. The strongest NAMEABLE property is the bound itself,
#         which PROVES as a value theorem (asserted below as len(...) <= 16).
#   makedirs : #@ ensures \result == 0 or -1        ; #@ assigns _filesystem.disk
#       — return-code only. Unlike `mkdir`, makedirs carries NO `dir_lookup`
#         post-state (mkdir has `\result==0 ==> dir_lookup(disk,5,d) >= 0`;
#         makedirs does not), so "makedirs(d); access(d)==present" is Unknown.
#         The model gap: makedirs should propagate mkdir's presence post-state.
#
# Each theorem takes symbolic params, returns int, asserts the observed value.

from pycsl_lib.os import (
    makedirs, listdir, scandir, access, F_OK,
)


# ---------------------------------------------------------------------------
# (1) listdir's length is BOUNDED (<= 16). Operate: listdir(d). OBSERVE: the
# listing has at most 16 entries. PROVES: listdir's contract ensures
# \length(\result) <= 16 directly; the count bound holds for any directory.
#
# NOTE: listdir leaves its `filepath` param UN-ANNOTATED, so the emitted stub
# types it `int` — a str-keyed setup (mkdir d) cannot feed it (WhyML type error
# at emission). So we CANNOT build the entries through the str-keyed mkdir and
# then count them here; the STRONGER consequence (count == entries built) is
# doubly blocked: (a) un-nameable through this int-path stub, and (b) Unknown
# anyway (no link to mkdir's writes, gap-4 §4a). This theorem asserts the
# NAMEABLE bound on the int-typed path the stub accepts.
#@ requires True
#@ ensures \result == 1
def listdir_count_bounded(d: int) -> int:
    entries = listdir(d)            # observe: the directory listing
    if len(entries) <= 16:          # ASSERTED: bounded count — PROVES
        return 1
    return 0


# (2) scandir's length is BOUNDED (<= 16). Analogous to listdir; same int-path
# stub-typing note. PROVES: scandir's contract ensures \length(\result) <= 16.
#@ requires True
#@ ensures \result == 1
def scandir_count_bounded(d: int) -> int:
    items = scandir(d)              # observe: the directory scan
    if len(items) <= 16:            # ASSERTED: bounded count — PROVES
        return 1
    return 0


# (3) makedirs(d) -> d is PRESENT. Setup: none. Operate: makedirs(d).
# OBSERVE: access(d, F_OK) == 1.
#
# HONEST STATUS: Unknown. makedirs's contract is return-code only; it does NOT
# carry mkdir's `\result==0 ==> dir_lookup(disk,5,d) >= 0` presence post-state,
# so access(d) reads a post-state the prover sees as unconstrained. The model
# gap: makedirs must propagate the same dir_lookup presence view mkdir already
# proves (then this theorem PROVES exactly like mkdir_then_access_present).
#@ requires True
#@ ensures \result == 1
def makedirs_then_access_present(d: str) -> int:
    rc = makedirs(d, 0o777)         # operate: create d (single level in this model)
    if rc != 0:
        return 1                    # makedirs failed: not the case under test
    return access(d, F_OK)          # observe: PRESENT — ASSERTED == 1
