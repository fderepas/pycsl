# formal_os_namespace2.py — further os NAMESPACE consequences, PUBLIC API ONLY.
#
# Extends formal_os_namespace.py (mkdir/rmdir/unlink/link/rename) to the
# remaining name-keyed mutators whose contracts pin a dir_lookup post-state
# observable through `access`, under the FAITHFUL EXCEPTION model:
#   remove(f)              : on success (non-raising) dir_lookup(dir,5,f) < 0  (absent after)
#   open(p, O_CREAT) -> fd : on success (non-raising) fd >= 3 AND
#                            dir_lookup(dir,5,p) >= 0  (present after create)
#
# remove/open no longer return -1 on failure: they RAISE OSError (open raises
# FileNotFoundError/OSError). The SUCCESS path is the non-raising path, on which
# the dir_lookup post-state holds unconditionally. `access`'s contract is
# (\result == 1) <==> dir_lookup(dir,5,f) >= 0, so the observer reflects the
# mutator's dir_lookup post-state and the consequence PROVES through the API.
#
# INTERNALS-BLIND. Public names only. Each theorem returns int, asserts the
# observed value.

from pycsl_lib.os import (
    mkdir, remove, open, close, access, F_OK,
    O_CREAT, O_WRONLY,
)


# (1) remove(f) -> f is ABSENT. Setup: mkdir f (so it resolves). Operate: remove
# (raises on failure). OBSERVE: access(f) == 0. Provable: remove pins
# dir_lookup<0 on the success path; access reflects it.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0
def remove_then_access_absent(f: str) -> int:
    mkdir(f, 0o777)                 # set up: f resolves
    remove(f)                       # the REAL removal (raises on failure)
    return access(f, F_OK)          # observe: now ABSENT — ASSERTED == 0


# (2) open(p, O_CREAT) -> p is PRESENT. Setup: none. Operate: create p via open
# (raises on failure). OBSERVE: access(p) == 1. Provable: a successful open
# returns fd >= 3 and pins dir_lookup>=0; access reflects presence.
#@ requires True
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.fd_block, _filesystem.next_fd
#@ ensures \result == 1
def open_creat_then_access_present(p: str) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)   # operate: create p (raises on failure)
    close(fd)
    return access(p, F_OK)          # observe: now PRESENT — ASSERTED == 1


# (3) The open present view is COHERENT with access: open(p, O_CREAT) creates p
# PRESENT, observed via access — both pinned to the same dir_lookup(dir,5,p) term.
#@ requires True
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.fd_block, _filesystem.next_fd
#@ ensures \result == 1
def absent_then_open_creat_makes_present(p: str) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)   # create (raises on failure)
    close(fd)
    after = access(p, F_OK)         # observe: PRESENT after create
    if after == 1:                  # ASSERTED == 1
        return 1
    return 0
