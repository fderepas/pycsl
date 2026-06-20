"""INTERNAL-LEVEL smoke test (NOT a public-API consequence formal test).

THIS FILE IS DELIBERATELY *NOT* a `formal_os_*` consequence test, and is named
`internal_os_io.py` to say so loudly. Two honest disclosures, both required by the
formal-test doctrine (`[[feedback_test_calls_api]]`, `[[feedback_formal_test_consequence]]`):

1. IT REACHES INTERNALS, BY NECESSITY. The ops exercised here — dup2, getdents,
   fsync, ftruncate, creat, chown, utimensat — are NOT exposed as public `os.*`
   symbols in `pycsl_lib/os/__init__.py` (only `dup` is). A public-API formal test
   is therefore IMPOSSIBLE for them today: there is no `os.<op>` to call. So this
   driver constructs `UnixInodeFileSystem` directly and calls its `sys_*` methods.
   That is a physical-barrier crossing; it is allowed here ONLY because this file is
   explicitly reclassified as an internal-level test, never counted in the public
   `formal_os_*` family. (`internal_os_dup` does call the public `dup`, but is kept
   here because — like the rest — it can only assert a return-code bound, below.)

2. THE ASSERTIONS ARE RETURN-CODE SAFETY BOUNDS, NOT CONSEQUENCES. Each `#@ ensures`
   below pins only the op's own return code (`0/-1`, `>=3/-1`, `newfd/-1`). That is
   NOT the observable consequence (write-back equality, alias established, size
   reflected, owner reflected). The real CONSEQUENCE we WANT is written as a
   `# CONSEQUENCE:` comment on each function and is UNPROVABLE today: the fd-mutating
   syscalls' contracts pin only the return code, never the resulting fd-table columns
   or disk bytes (`sys_creat`/`sys_open` are `#@ no_inline` with return-code-only
   ensures; `sys_read` bounds the byte COUNT, not the bytes), so an observation call
   reads an unconstrained post-state. See `10-2204-convergence-gap-4.md` (§4b, §4c)
   and the os ledger in `config/skills/pycsl-monitoring/SKILL.md`.

WHAT THIS FILE IS GOOD FOR: it confirms these internal `sys_*` ops EMIT, TYPECHECK,
and that their return-code contracts are self-consistent (the driver proves with
0 non-Valid / 0 `\trusted`). It is a smoke/typecheck artifact, NOT evidence that any
op's consequence holds. The proven public-API consequences live in the genuine
`formal_os_*` files (e.g. `formal_os_content`, `formal_os_close`, `formal_os_lseek`).
"""
from pycsl_lib.os import dup
from pycsl_lib.os.UnixInodeFileSystem import UnixInodeFileSystem


# dup -> read via the new fd (PUBLIC os.dup). CONSEQUENCE we want: dup(fd) yields nd;
# reading via nd sees the SAME bytes the original fd's file holds. UNPROVABLE
# (gap-4 §4b: dup's ensures pins only \result >= 3). Asserted: return-code bound only.
#@ requires fd >= 0
#@ ensures \result == -1 or \result >= 3
def internal_os_dup(fd: int) -> int:
    return dup(fd)                   # want: read(nd) sees the same data as fd


# dup2 -> alias. CONSEQUENCE we want: dup2(oldfd, newfd) makes newfd alias oldfd
# (fstat(newfd) == fstat(oldfd)). UNPROVABLE (gap-4 §4b/§4c). Asserted: return-code bound only.
#@ requires oldfd >= 0
#@ requires newfd >= 0
#@ ensures \result == newfd or \result == -1
def internal_os_dup2(oldfd: int, newfd: int) -> int:
    fs = UnixInodeFileSystem()
    rc = fs.sys_dup2(oldfd, newfd)
    # want: fs.sys_fstat(newfd) == fs.sys_fstat(oldfd) (alias established)
    return rc


# getdents -> directory entries. CONSEQUENCE we want: getdents on a dir fd succeeds
# and entries match listdir. UNPROVABLE (gap-4 §4b/§4c). Asserted: return-code bound only.
#@ requires fd >= 0
#@ ensures \result == 0 or \result == -1
def internal_os_getdents(fd: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_getdents(fd)       # want: 0 and entries == listdir


# fsync -> durability. CONSEQUENCE we want: after write+fsync, read-back is UNCHANGED.
# fsync is a flush with no functional effect to round-trip. Asserted: return-code bound only.
#@ requires fd >= 0
#@ ensures \result == 0 or \result == -1
def internal_os_fsync(fd: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_fsync(fd)          # flush: read-back stays equal (durability)


# ftruncate -> size. CONSEQUENCE we want: ftruncate(fd, n) => inode size field == n
# (via fstat/stat). UNPROVABLE (gap-4 §4b: no size accessor). Asserted: return-code bound only.
#@ requires fd >= 0
#@ ensures \result == 0 or \result == -1
def internal_os_ftruncate(fd: int, length: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_ftruncate(fd, length)   # want: stat(file).size == length


# creat -> presence + valid fd. CONSEQUENCE we want: creat(f) => f PRESENT and
# fstat(fd) reports a valid inode (0<=ino<32). UNPROVABLE (gap-4 §4a/§4b). Asserted: return-code bound only.
#@ requires True
#@ ensures \result == -1 or \result >= 3
def internal_os_creat(name: str, mode: int) -> int:
    fs = UnixInodeFileSystem()
    fd = fs.sys_creat(name, mode)
    # want: fs.sys_fstat(fd) in [0,32) and access(name) present
    return fd


# chown -> owner/group. CONSEQUENCE we want: chown(f, u, g) => stat(f).uid/gid == u/g.
# UNPROVABLE (gap-4 §4a + no owner accessor). Asserted: return-code bound only.
#@ requires True
#@ ensures \result == 0 or \result == -1
def internal_os_chown(name: str, owner: int, group: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_chown(name, owner, group)   # want: stat owner/group == u/g


# utimensat -> times. CONSEQUENCE we want: utimensat(f, a, m) => stat(f).atime/mtime == a/m.
# UNPROVABLE (gap-4 §4a + no time accessor). Asserted: return-code bound only.
#@ requires True
#@ ensures \result == 0 or \result == -1
def internal_os_utimensat(name: str, atime: int, mtime: int) -> int:
    fs = UnixInodeFileSystem()
    return fs.sys_utimensat(name, atime, mtime)   # want: stat times == a/m
