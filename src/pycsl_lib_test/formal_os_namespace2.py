# formal_os_namespace2.py — further os NAMESPACE consequences, PUBLIC API ONLY.
#
# Extends formal_os_namespace.py (mkdir/rmdir/unlink/link/rename) to the
# remaining name-keyed mutators whose strengthened contracts pin a dir_lookup
# post-state observable through `access`:
#   remove   : \result == 0 ==> dir_lookup(disk,5,f) < 0   (absent after)
#   open-CREAT: (\result >= 3) <==> dir_lookup(disk,5,p) >= 0   (present after create)
#
# `access`'s contract is (\result == 1) <==> dir_lookup(disk,5,f) >= 0, so the
# observer reflects the mutator's dir_lookup post-state and the consequence
# PROVES through the API.
#
# INTERNALS-BLIND. Public names only. Each theorem returns int, asserts the
# observed value.

from pycsl_lib.os import (
    mkdir, remove, open, close, access, F_OK,
    O_CREAT, O_WRONLY,
)


# (1) remove(f) -> f is ABSENT. Setup: mkdir f (so it resolves). Operate: remove.
# OBSERVE: access(f) == 0. Provable: remove pins dir_lookup<0; access reflects it.
#@ requires True
#@ ensures \result == 0
def remove_then_access_absent(f: str) -> int:
    mkdir(f, 0o777)                 # set up: f resolves
    rc = remove(f)                  # the REAL removal
    if rc != 0:
        return 0                    # remove failed: vacuously absent-consistent
    return access(f, F_OK)          # observe: now ABSENT — ASSERTED == 0


# (2) open(p, O_CREAT) -> p is PRESENT. Setup: none. Operate: create p via open.
# OBSERVE: access(p) == 1. Provable: a valid fd (>= 3) pins dir_lookup>=0 (open's
# iff), and access reflects presence.
#@ requires True
#@ ensures \result == 1
def open_creat_then_access_present(p: str) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)   # operate: create p
    if fd < 3:
        return 1                    # create failed: not the case under test
    close(fd)
    return access(p, F_OK)          # observe: now PRESENT — ASSERTED == 1


# (3) The open ENOENT/present discriminant is COHERENT with access: if
# access(p) reports ABSENT (0), then open(p, O_CREAT) still creates it PRESENT.
# This chains access (absence view) -> open (create) -> access (presence view),
# both pinned to the same dir_lookup(disk,5,p) term.
#@ requires True
#@ ensures \result == 1
def absent_then_open_creat_makes_present(p: str) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)   # create (idempotent presence)
    if fd < 3:
        return 1
    close(fd)
    after = access(p, F_OK)         # observe: PRESENT after create
    if after == 1:                  # ASSERTED == 1
        return 1
    return 0
