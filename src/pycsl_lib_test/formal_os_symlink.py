# formal_os_symlink.py — os SYMLINK consequences (symlink / readlink), through
# the PUBLIC API ONLY, under the FAITHFUL EXCEPTION model.
#
# INTERNALS-BLIND. Imports only public names; no _filesystem, disk, sys_*,
# _dir_lookup, UnixInodeFileSystem in code or contracts.
#
# Public contracts in pycsl_lib/os/__init__.py (exception model):
#   symlink(src, dst) -> None ; RAISES OSError on failure ; on success
#       ensures dir_lookup(dir, 5, dst) >= 0  (the link name now resolves)
#   readlink(path) -> int     ; RAISES OSError on failure ; ensures 0 <= r < 256
#   access(path, mode) -> int ; does NOT raise ;
#       ensures (\result == 1) <==> dir_lookup(dir, 5, path) >= 0
#
# symlink no longer returns a code: the SUCCESS path is precisely the
# non-raising path, on which its dir_lookup post-state holds unconditionally.
# So symlink(src, dst); access(dst, F_OK) == 1 is a genuine CONSEQUENCE.
#
# ---------------------------------------------------------------------------
# GAP (readlink target-value consequence — NOT PROVABLE, theorem omitted):
#
# readlink's functional consequence — "readlink(dst) returns the target that
# symlink(src,dst) stored" — is NOT provable, so no theorem asserts it here.
# readlink's contract is geometry only (`0 <= \result < 256`): it has NO link
# to what symlink stored, and the target bytes are unmodeled (out of scope).

from pycsl_lib.os import (
    symlink, access, F_OK,
)


# ---------------------------------------------------------------------------
# (1) symlink(src, dst) -> dst is PRESENT (the link name resolves). Setup: none.
# Operate: symlink(src, dst) (raises on failure — success path reached only when
# the link is created). OBSERVE: access(dst, F_OK) == 1. Valid.
#@ requires src != dst
#@ assigns _filesystem.disk
#@ ensures \result == 1
def symlink_then_dst_present(src: str, dst: str) -> int:
    symlink(src, dst)               # operate: create the symbolic link (raises on failure)
    return access(dst, F_OK)        # observe: dst PRESENT — ASSERTED == 1
