# formal_os_listing.py — os DIRECTORY-LISTING consequences (listdir / scandir /
# makedirs), through the PUBLIC API ONLY, under the FAITHFUL EXCEPTION model.
#
# INTERNALS-BLIND. Imports only public names; no _filesystem, disk, sys_*,
# _dir_lookup, UnixInodeFileSystem in code (assigns may name the documented
# _filesystem World global).
#
# Public contracts in pycsl_lib/os/__init__.py (exception model):
#   listdir(path) -> list  : RAISES OSError on absent/not-a-dir ; ensures \length(\result) <= 16
#   scandir(path) -> list  : RAISES OSError on absent/not-a-dir ; ensures \length(\result) <= 16
#       — a LENGTH BOUND only; NO link between the entries you create (via mkdir)
#         and the listing's count. So "create N entries => len(listdir(d)) == N"
#         is NOT entailed. The strongest NAMEABLE property is the bound itself,
#         which PROVES as a value theorem (asserted below as len(...) <= 16).
#         Both now take a `str` path and RAISE on an absent dir, so we mkdir(d)
#         first to reach a non-raising listing.
#   makedirs(name, mode, exist_ok) -> None : RAISES OSError on failure ; on
#         success ensures dir_lookup(dir, 5, name) >= 0 (present after). The raise
#         model strengthened makedirs to pin the same presence post-state mkdir
#         has, so "makedirs(d); access(d) == 1" now PROVES (it was Unknown under
#         the old return-code-only model).
#
# Each theorem takes symbolic params, returns int, asserts the observed value.

from pycsl_lib.os import (
    mkdir, makedirs, listdir, scandir, access, F_OK,
)


# ---------------------------------------------------------------------------
# (1) listdir's length is BOUNDED (<= 16). Setup: mkdir(d) (listdir RAISES on an
# absent dir). Operate: listdir(d). OBSERVE: the listing has at most 16 entries.
# PROVES: listdir's contract ensures \length(\result) <= 16 directly.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def listdir_count_bounded(d: str) -> int:
    mkdir(d, 0o777)                 # setup: create a directory to list
    entries = listdir(d)            # observe: the directory listing (raises if absent)
    if len(entries) <= 16:          # ASSERTED: bounded count — PROVES
        return 1
    return 0


# (2) scandir's length is BOUNDED (<= 16). Analogous to listdir. PROVES: scandir's
# contract ensures \length(\result) <= 16.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def scandir_count_bounded(d: str) -> int:
    mkdir(d, 0o777)                 # setup: create a directory to scan
    items = scandir(d)              # observe: the directory scan (raises if absent)
    if len(items) <= 16:            # ASSERTED: bounded count — PROVES
        return 1
    return 0


# (3) makedirs(d) -> d is PRESENT. Setup: none. Operate: makedirs(d) (raises on
# failure). OBSERVE: access(d, F_OK) == 1.
# PROVES under the exception model: makedirs's success path pins
# dir_lookup(dir,5,d) >= 0, and access reports `\result == 1 <==> dir_lookup >= 0`.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def makedirs_then_access_present(d: str) -> int:
    makedirs(d, 0o777)              # operate: create d (raises on failure)
    return access(d, F_OK)          # observe: PRESENT — ASSERTED == 1
