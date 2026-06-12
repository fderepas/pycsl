# formal_os_symlink.py — os SYMLINK consequences (symlink / readlink), through
# the PUBLIC API ONLY.
#
# INTERNALS-BLIND. Imports only public names; no _filesystem, disk, sys_*,
# _dir_lookup, UnixInodeFileSystem in code or contracts.
#
# Public contracts in pure_lib/os/__init__.py:
#   symlink : #@ ensures \result == 0 or -1          ; #@ assigns _filesystem.disk
#       — return-code only; NO `dir_lookup` post-state for the link name `dst`
#         (unlike link/rename, which pin `\result==0 ==> dir_lookup(disk,5,dst)
#         >= 0`). So "symlink(src,dst); access(dst)==present" is Unknown. The
#         model gap: symlink should pin the new name's presence like link does.
#   readlink : #@ ensures \result == -1 or (0 <= \result < 256)
#       — a target-block/-1 BOUND, with NO link to what `symlink` stored. So
#         "readlink(dst) == src's stored target" is NOT entailed; the strongest
#         NAMEABLE property is the geometry bound, asserted as a value theorem.
#
# Each theorem takes symbolic params, returns int, asserts the observed value.

from pure_lib.os import (
    symlink, readlink, access, F_OK,
)


# ---------------------------------------------------------------------------
# (1) symlink(src, dst) -> dst is PRESENT (the link name resolves). Setup: none.
# Operate: symlink(src, dst). OBSERVE: access(dst, F_OK) == 1.
#
# HONEST STATUS: Unknown. symlink's contract is return-code only — it has NO
# `\result==0 ==> dir_lookup(disk,5,dst) >= 0` presence post-state (link and
# rename DO have it; symlink does not). So access(dst) reads an unconstrained
# post-state. The model gap: symlink should pin the new name's presence view,
# exactly like link's gap-9 ensures.
#@ requires src != dst
#@ ensures \result == 1
def symlink_then_dst_present(src: str, dst: str) -> int:
    rc = symlink(src, dst)          # operate: create the symbolic link
    if rc != 0:
        return 1                    # symlink failed: not the case under test
    return access(dst, F_OK)        # observe: dst PRESENT — ASSERTED == 1


# (2) readlink's target value is BOUNDED (-1 or 0 <= block < 256). Setup: create
# the symlink. Operate: readlink(dst). OBSERVE: \result in the documented range.
#
# HONEST STATUS: Unknown for the STRONGER consequence (readlink(dst) == the
# target src stored): readlink's contract has no link to symlink's write. The
# geometry BOUND itself (-1 or 0<=block<256) is what readlink's contract entails;
# asserting `\result==1` requires discriminating the success target value, which
# readlink does not pin (and the actual target bytes are unmodeled). So this
# theorem — asserting a valid, non-error target after symlink — is Unknown.
#@ requires src != dst
#@ ensures \result == 1
def readlink_after_symlink_valid_target(src: str, dst: str) -> int:
    symlink(src, dst)               # set up: dst is a symlink to src
    tgt = readlink(dst)             # observe: the stored target block
    if tgt >= 0 and tgt < 256:      # ASSERTED: valid target (WANT, from symlink)
        return 1
    return 0
