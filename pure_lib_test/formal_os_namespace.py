# formal_os_namespace.py — os NAMESPACE consequences, through the PUBLIC API ONLY.
#
# This file was REWRITTEN to remove the previous SIMULATION. The prior version
# built a local `disk = [0]*64`, hand-wrote the dirent bytes (`disk[2]=ord(d[0])`),
# and inlined `_dir_lookup`'s scan/decode logic — then asserted that its own
# re-implementation behaved as expected. That proves a TAUTOLOGY about a hand-
# written copy of the syscalls, NOT that os.mkdir / os.access / os.rmdir / … work.
# (The TELL, per the skill: writing it required knowing the internal byte layout.)
#
# Here every theorem CALLS THE REAL PUBLIC API the way a caller does — it imports
# `mkdir`, `rmdir`, `unlink`, `link`, `rename`, `access`, `stat`, `F_OK` from
# pure_lib.os and drives a setup -> operate -> OBSERVE scenario, asserting the
# observation's promised post-state. There is NO `disk`, NO `_dir_lookup`, NO
# `sys_*`, NO `UnixInodeFileSystem(...)`, NO hand-written dirent bytes.
#
# HONEST OUTCOME — these consequences DO NOT PROVE through the API today.
# The os syscalls' public contracts in pure_lib/os/__init__.py are RETURN-CODE
# ONLY: `mkdir`/`rmdir`/`unlink`/`link`/`rename` ensure `\result == 0 or -1`;
# `access` ensures `\result == 0 or 1`; `stat` ensures `\result == -1 or
# (0 <= \result < 32)`. NONE of them ensures any link between a name written by a
# mutator and what an observer later reads under that same name. So after
# `mkdir(d)`, `access(d, F_OK)` reads a post-state the prover sees as fully
# unconstrained, and the PRESENT assertion is Unknown. Verified directly:
# `mkdir(d) -> access(d, F_OK) == 1` => Unknown (0.06s, 186713 steps), matching
# convergence-gap-4 §4a. Each theorem below is therefore the HONEST,
# API-calling form of the consequence; it is expected to report Unknown until the
# MODEL's syscall contracts gain observable post-state `ensures`. The precise
# reproducer, root cause, and proposed model fix are recorded in the dated
# convergence-gap doc that accompanies this rewrite (11-0605-convergence-gap-7.md).
#
# DO NOT make these green by simulating, by weakening to the observer's own
# return-code disjunction, or by touching internals. An Unknown that is documented
# is the correct convergence-loop outcome here, not a simulated green.

from pure_lib.os import (
    mkdir, rmdir, unlink, link, rename, access, F_OK,
)

# NOTE on observers used here. We observe presence/absence with `access`, whose
# path param IS annotated `str` in pure_lib/os/__init__.py. We deliberately do
# NOT use `stat`/`lstat` as the observer: their `filepath` param is left
# un-annotated in the model, so PyCSL's emitted stub types it `int` — passing a
# symbolic `str` name to `stat(name)` is a WhyML type error at emission, before
# any proof runs. That stub-typing friction is recorded in the accompanying
# convergence-gap doc (11-0605-convergence-gap-7.md, §B). `access` is the one
# str-typed observer in the namespace surface, so it is the only API observer
# through which these consequences are even expressible.


# ---------------------------------------------------------------------------
# (1) mkdir(d) -> d is PRESENT.
# Observe absence first, then create d via the REAL mkdir, then OBSERVE d via
# the REAL access. CONSEQUENCE: access reports PRESENT (== 1) after mkdir.
# Returns the post-mkdir observation so the ensures pins the observed value.
#
# HONEST STATUS: Unknown. access's contract (\result == 0 or 1) carries no link
# to mkdir's write — gap-4 §4a / gap-7.
#@ requires True
#@ ensures \result == 1
def mkdir_then_access_present(d: str) -> int:
    before = access(d, F_OK)        # observe: absent initially (return-code 0/1)
    rc = mkdir(d, 0o777)            # the REAL syscall
    if rc != 0:
        return 1                    # mkdir failed: vacuously satisfy (not the case under test)
    return access(d, F_OK)          # observe: now PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# (2) mkdir(d) then rmdir(d) -> d is ABSENT again.
# Create d, then remove it via the REAL rmdir, then OBSERVE via the REAL access.
# CONSEQUENCE: access reports ABSENT (== 0) after rmdir.
#
# HONEST STATUS: Unknown — rmdir's contract (\result == 0 or -1) does not pin the
# post-state access reads (gap-4 §4a / gap-7).
#@ requires True
#@ ensures \result == 0
def rmdir_then_access_absent(d: str) -> int:
    mkdir(d, 0o777)                 # set up: create the directory
    rc = rmdir(d)                   # the REAL removal
    if rc != 0:
        return 0                    # rmdir failed: vacuously ABSENT-consistent
    return access(d, F_OK)          # observe: now ABSENT — ASSERTED == 0


# ---------------------------------------------------------------------------
# (3) unlink(f) -> f is ABSENT.
# Create f, then unlink via the REAL unlink, then OBSERVE via the REAL access.
# CONSEQUENCE: access reports ABSENT (== 0) after unlink.
#
# HONEST STATUS: Unknown (gap-4 §4a / gap-7).
#@ requires True
#@ ensures \result == 0
def unlink_then_access_absent(f: str) -> int:
    mkdir(f, 0o777)                 # set up a name f resolvable by access
    rc = unlink(f)                  # the REAL removal
    if rc != 0:
        return 0                    # unlink failed: vacuously ABSENT-consistent
    return access(f, F_OK)          # observe: now ABSENT — ASSERTED == 0


# ---------------------------------------------------------------------------
# (4) The PRESENT precondition a removal consumes — f IS observable BEFORE the
# removal (so the absence theorems above are a genuine remove, not a vacuous
# miss against a never-present name). Create f, then OBSERVE via the REAL access.
# CONSEQUENCE: access reports PRESENT (== 1) right after mkdir.
#
# HONEST STATUS: Unknown (same wall as (1); gap-4 §4a / gap-7).
#@ requires True
#@ ensures \result == 1
def file_present_after_mkdir(f: str) -> int:
    rc = mkdir(f, 0o777)            # the REAL syscall
    if rc != 0:
        return 1
    return access(f, F_OK)          # observe: PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# (5) link(a, b) -> b is PRESENT (hard-link semantics: the new name resolves).
# Create a, then link a -> b via the REAL link, then OBSERVE b via the REAL access.
# CONSEQUENCE: access(b, F_OK) reports PRESENT (== 1) after link — b now resolves.
# (The deeper hard-link identity "a and b share one inode" can only be observed
# through stat's inode number, which the str/int stub-typing friction blocks at
# emission — see gap-7 §B; access can express PRESENT but not the shared inode.)
#
# HONEST STATUS: Unknown — link's contract (\result == 0 or -1) does not pin
# access(b)'s post-state (gap-4 §4a / gap-7).
#@ requires a != b
#@ ensures \result == 1
def link_then_b_present(a: str, b: str) -> int:
    mkdir(a, 0o777)                 # set up: a exists
    rc = link(a, b)                 # the REAL hard link
    if rc != 0:
        return 1                    # link failed: not the case under test
    return access(b, F_OK)          # observe: b PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# (6a) rename(a, b) -> b is PRESENT.
# Create a, rename a -> b via the REAL rename, then OBSERVE b via the REAL access.
# CONSEQUENCE: access(b, F_OK) reports PRESENT (== 1) after rename.
#
# HONEST STATUS: Unknown (gap-4 §4a / gap-7).
#@ requires a != b
#@ ensures \result == 1
def rename_then_b_present(a: str, b: str) -> int:
    mkdir(a, 0o777)                 # set up: a exists
    rc = rename(a, b)               # the REAL rename
    if rc != 0:
        return 1                    # rename failed: not the case under test
    return access(b, F_OK)          # observe: b PRESENT — ASSERTED == 1


# ---------------------------------------------------------------------------
# (6b) rename(a, b) -> a is ABSENT (the old name no longer resolves).
# Create a, rename a -> b via the REAL rename, then OBSERVE a via the REAL access.
# CONSEQUENCE: access(a, F_OK) reports ABSENT (== 0) after rename.
#
# HONEST STATUS: Unknown — rename's contract does not pin access(a)'s post-state
# (gap-4 §4a / gap-7).
#@ requires a != b
#@ ensures \result == 0
def rename_then_a_absent(a: str, b: str) -> int:
    mkdir(a, 0o777)                 # set up: a exists
    rc = rename(a, b)               # the REAL rename
    if rc != 0:
        return 0                    # rename failed: treat as absent-consistent
    return access(a, F_OK)          # observe: a ABSENT — ASSERTED == 0
