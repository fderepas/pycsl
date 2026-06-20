# formal_os_symlink.py — os SYMLINK consequences (symlink / readlink), through
# the PUBLIC API ONLY.
#
# INTERNALS-BLIND. Imports only public names; no _filesystem, disk, sys_*,
# _dir_lookup, UnixInodeFileSystem in code or contracts.
#
# Public contracts in pycsl_lib/os/__init__.py:
#   symlink : #@ ensures \result == 0 or -1          ; #@ assigns _filesystem.disk
#   readlink : #@ ensures \result == -1 or (0 <= \result < 256)
#
# Each theorem takes symbolic params, returns int, asserts the observed value.
#
# ---------------------------------------------------------------------------
# GAP (readlink target-value consequence — NOT PROVABLE, theorem removed):
#
# readlink's functional consequence — "readlink(dst) returns the target that
# symlink(src,dst) stored" — is NOT provable, so no theorem asserts it here.
# readlink's contract is return-code/geometry only (`\result == -1 or
# 0 <= \result < 256`): it has NO link to what symlink stored, and the target
# bytes are unmodeled (out of scope). Asserting only the `-1 or 0<=result<256`
# geometry bound would be VACUOUS — it merely re-states readlink's own contract.
# A `\result == 1` (valid-target) assertion is logically unprovable, because
# readlink's contract permits `\result == -1` and does not discriminate the
# success target value. So the consequence is documented here and left unasserted.
# (This previously sat as `readlink_after_symlink_valid_target`, an Unknown that
# made Alt-Ergo flail ~30s; removed for CI hygiene.)

from pycsl_lib.os import (
    symlink, access, F_OK,
)


# ---------------------------------------------------------------------------
# (1) symlink(src, dst) -> dst is PRESENT (the link name resolves). Setup: none.
# Operate: symlink(src, dst). OBSERVE: access(dst, F_OK) == 1. Valid.
#@ requires src != dst
#@ ensures \result == 1
def symlink_then_dst_present(src: str, dst: str) -> int:
    rc = symlink(src, dst)          # operate: create the symbolic link
    if rc != 0:
        return 1                    # symlink failed: not the case under test
    return access(dst, F_OK)        # observe: dst PRESENT — ASSERTED == 1
