# formal_os_enoent.py — os ENOENT consequence, through the PUBLIC API ONLY.
#
# This fixes the `open_absent` Unknown in formal_os_fd.py. There, open(absent,
# O_RDONLY) -> -1 was Unknown because NOTHING ESTABLISHED absence: a symbolic
# name's dir_lookup post-state is havoc'd, so the prover could not see the path
# as absent, and open's ENOENT discriminant `(\result==-1) <==> dir_lookup<0`
# had no antecedent to fire on.
#
# Here we ESTABLISH absence via the API first: mkdir(d) then rmdir(d). rmdir's
# contract pins `\result==0 ==> dir_lookup(disk,5,d) < 0` (the ABSENCE view), and
# open's ENOENT discriminant pins `(\result==-1) <==> dir_lookup(disk,5,d) < 0`.
# Chaining them, open(d, O_RDONLY) == -1 is ENTAILED — this PROVES through the
# API.
#
# INTERNALS-BLIND. Imports only public names; no _filesystem, disk, sys_*,
# _dir_lookup, UnixInodeFileSystem in code or contracts.

from pure_lib.os import (
    mkdir, rmdir, open, O_RDONLY,
)


# ---------------------------------------------------------------------------
# open(absent, O_RDONLY) -> ENOENT (-1), with absence ESTABLISHED via the API.
# Setup: mkdir(d) (d present), then rmdir(d) (d absent). Operate: open(d, RDONLY).
# OBSERVE: open returns -1.
#
# PROVES: rmdir success pins dir_lookup(d) < 0; open's discriminant maps that to
# \result == -1. We guard on rmdir succeeding (rc == 0) so the absence antecedent
# is live; on the rmdir-failed branch the theorem is vacuously satisfied (not the
# case under test).
#@ requires True
#@ ensures \result == 1
def open_removed_yields_enoent(d: str) -> int:
    mkdir(d, 0o777)                 # set up: d present
    rc = rmdir(d)                   # establish ABSENCE: dir_lookup(d) < 0 on rc==0
    if rc != 0:
        return 1                    # rmdir failed: absence not established — skip
    fd = open(d, O_RDONLY, 0o777)   # operate: open the now-absent name
    if fd == -1:                    # OBSERVE: ENOENT (-1) — ASSERTED == 1
        return 1
    return 0
