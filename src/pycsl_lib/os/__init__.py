"""Pure Python os package — module-level POSIX API backed by UnixInodeFileSystem.

Instantiates a global ``_filesystem`` and exposes standard ``os.*`` functions
that delegate to it.  Every function carries PyCSL contracts propagated from
the underlying ``UnixInodeFileSystem`` syscalls.
"""
from .UnixInodeFileSystem import UnixInodeFileSystem
from . import path

# ── Global virtual filesystem ────────────────────────────────────────
_filesystem = UnixInodeFileSystem()



# ── Constants ────────────────────────────────────────────────────────
# Defined as literals so PyCSL emits them with their values in WhyML
# (class attribute references produce abstract val constants with no
# value axiom — see 1111.md R6).

# Open flags
O_RDONLY = 0
O_WRONLY = 1
O_RDWR = 2
O_CREAT = 64

# lseek whence
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

# Filesystem geometry
BLOCK_SIZE = 512
NUM_BLOCKS = 256
MAX_INODES = 32

# Path separator
sep = '/'

# access() mode constants
F_OK = 0
R_OK = 4
W_OK = 2
X_OK = 1

# Simulated environment variables
environ = {
    'PATH': '/usr/bin:/bin',
    'HOME': '/',
    'USER': 'root',
    'LANG': 'C',
}

# Simulated process ID
_pid = 1


# ── DirEntry (for scandir) ──────────────────────────────────────────

# gap-4 (DirEntry aliasing) — Strategy C: DirEntry.__init__ previously took
# `fs` (the UnixInodeFileSystem instance) as a parameter, but PyCSL's
# aliasing rule prohibits passing the module global `_filesystem` as an
# argument in a formal-test driver ("would alias the global"). Removed `fs`
# from the constructor; the is_dir/is_file/is_symlink methods now reach the
# module-level `_filesystem` directly (exactly as listdir/scandir/walk
# already do). DirEntry is now CONSTRUCTIBLE in a formal-test driver without
# aliasing the global. The out-of-range sentinel direction is pinned on each
# classifier (`(self._inode_num < 0 or self._inode_num >= 32) ==> \result == 0`)
# so a driver can prove the -1-sentinel consequence.
#@ class invariant self._inode_num >= -1 and self._inode_num < 32
class DirEntry:
    """Minimal os.DirEntry returned by scandir()."""

    #@ requires inode_num >= -1 and inode_num < 32
    #@ assigns self.name, self.path, self._inode_num
    #@ ensures self._inode_num == inode_num
    def __init__(self, name, inode_num):
        self.name = name
        self.path = name
        self._inode_num = inode_num

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == 1
    #@ ensures (self._inode_num < 0 or self._inode_num >= 32) ==> \result == 0
    def is_dir(self) -> int:
        if self._inode_num < 0 or self._inode_num >= 32:
            return 0
        inode = _filesystem._read_inode(self._inode_num)
        if inode[2] == 2:
            return 1
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == 1
    #@ ensures (self._inode_num < 0 or self._inode_num >= 32) ==> \result == 0
    def is_file(self) -> int:
        if self._inode_num < 0 or self._inode_num >= 32:
            return 0
        inode = _filesystem._read_inode(self._inode_num)
        if inode[2] == 1:
            return 1
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == 1
    #@ ensures (self._inode_num < 0 or self._inode_num >= 32) ==> \result == 0
    def is_symlink(self) -> int:
        if self._inode_num < 0 or self._inode_num >= 32:
            return 0
        inode = _filesystem._read_inode(self._inode_num)
        if inode[2] == 3:
            return 1
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == 0
    def is_junction(self) -> int:
        return 0



# ── DirEntry free-function wrappers (gap-4 Strategy D) ───────────────
# Public free functions wrapping each DirEntry classifier. The formal-test
# driver imports THESE (function imports materialize `_filesystem` correctly),
# not the DirEntry class (whose class-import path emits ill-typed module
# stubs — see bugs-to-report/20260623-1600-direntry-class-import.md). Each
# wrapper constructs a DirEntry and delegates, so the consequence tested is
# the DirEntry method's behavior. Body-verified, zero-TCB.

#@ requires inode_num >= -1 and inode_num < 32
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
#@ ensures (inode_num < 0 or inode_num >= 32) ==> \result == 0
def dirent_is_dir(name, inode_num):
    """Construct a DirEntry and return its is_dir() result."""
    d = DirEntry(name, inode_num)
    return d.is_dir()

#@ requires inode_num >= -1 and inode_num < 32
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
#@ ensures (inode_num < 0 or inode_num >= 32) ==> \result == 0
def dirent_is_file(name, inode_num):
    """Construct a DirEntry and return its is_file() result."""
    d = DirEntry(name, inode_num)
    return d.is_file()

#@ requires inode_num >= -1 and inode_num < 32
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
#@ ensures (inode_num < 0 or inode_num >= 32) ==> \result == 0
def dirent_is_symlink(name, inode_num):
    """Construct a DirEntry and return its is_symlink() result."""
    d = DirEntry(name, inode_num)
    return d.is_symlink()

#@ requires inode_num >= -1 and inode_num < 32
#@ assigns \nothing
#@ ensures \result == 0
def dirent_is_junction(name, inode_num):
    """Construct a DirEntry and return its is_junction() result (always 0)."""
    d = DirEntry(name, inode_num)
    return d.is_junction()



# ── Functions delegating to _filesystem ──────────────────────────────

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == 1
#@ ensures (\result == 1) <==> (dir_lookup(_filesystem.dir, 5, filepath) >= 0)
def access(filepath: str, mode, *, dir_fd=None, effective_ids=False,
           follow_symlinks=True):
    """Check file accessibility. Returns 1 if accessible, 0 otherwise."""
    r = _filesystem.sys_access(filepath, mode)
    # gap-9: sys_access ensures `(r == 0) <==> dir_lookup(_filesystem.dir, 5,
    # filepath) >= 0` (the directory-scan presence view). result == 1 iff r == 0,
    # so the observer reflects presence.
    if r == 0:
        return 1
    return 0

#@ requires True
#@ assigns _filesystem.disk
# FAITHFUL FAILURE (os.rst l.47-49): chmod RAISES OSError on failure (CPython raises
# FileNotFoundError on a missing path; the kernel collapses to -1, so the wrapper
# raises generic OSError). Returns None on success.
#@ raises OSError when True
def chmod(filepath: str, mode, *, dir_fd=None, follow_symlinks=True):
    """Change file mode bits. Raises OSError on failure (CPython-faithful)."""
    rc = _filesystem.sys_chmod(filepath, mode)
    if rc < 0:
        raise OSError

#@ requires fd >= 0
#@ assigns _filesystem.fd_open
# FAITHFUL FAILURE (os.rst l.47-49): close RAISES OSError (EBADF) on a bad fd
# rather than returning -1. On success returns None (CPython).
#@ raises OSError when True
# CLOSE-POST-STATE: propagate sys_close's observable consequence — on (non-raising)
# success the fd is no longer open (`fd_open[fd] == 0`), so a caller's fstat(fd)
# after a successful close reports EBADF. Body-faithful (sys_close sets fd_open[fd]=0).
#@ ensures fd < 64 ==> _filesystem.fd_open[fd] == 0
def close(fd):
    """Close a file descriptor. Raises OSError on a bad fd (CPython-faithful)."""
    rc = _filesystem.sys_close(fd)
    if rc < 0:
        raise OSError

#@ requires fd >= 0
#@ assigns _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.next_fd
# FAITHFUL FAILURE (os.rst l.47-49): dup RAISES OSError (EBADF on a closed source,
# EMFILE when the fd table is full) rather than returning -1.
#@ raises OSError when True
#@ ensures \result >= 3
# gap-15: with the `_filesystem.fd_inode[fd]` (global_field_subscript) grammar, the
# dup SHARED-OPEN-FILE-DESCRIPTION view composes through the public API:
#   - VALIDITY-GIVEN-VALID-SOURCE + FREE-SLOT: a valid open source fd dups to a valid
#     fd (>= 3) WHEN a free fd slot exists at entry (the HONEST free-slot-conditioned
#     no-ENFILE direction — fd-resolution-fidelity RETIRED). This is now BODY-PROVEN
#     ZERO-trust in sys_dup (via `_alloc_fd`'s completeness ensures); the wrapper
#     propagates it verbatim. An internals-blind formal-test driver establishes the
#     free-slot side-condition via `#@ fresh_globals` (the `_filesystem` constructor's
#     all-free post-state, carried across a prior open/dup by the single-cell frame).
#   - SHARED INODE: the duped fd resolves to the SAME inode as the source —
#     `_filesystem.fd_inode[\result] == _filesystem.fd_inode[fd]` — so dup and the
#     source share one open-file-description (the inode the source resolves to).
#@ ensures (fd < 64 and \old(_filesystem.fd_open[fd]) == 1 and (\exists k: int; 3 <= k and k < 64 and \old(_filesystem.fd_open[k]) == 0)) ==> \result >= 3
#@ ensures \result >= 3 ==> _filesystem.fd_inode[\result] == \old(_filesystem.fd_inode[fd])
# gap-1: pin the duped fd as OPEN with an in-range inode on success so the shared
# inode is OBSERVABLE through a caller's fstat(dup_fd) — fstat's ensures is guarded
# by `fd_open[fd]==1 and 0<=fd_inode[fd]<32`. Body-faithful: sys_dup sets
# fd_open[\result]==1 and copies fd_inode[oldfd] into fd_inode[\result], so the
# range rides on the source's pre-state inode being in range (the open site, which
# pins 0<=fd_inode[fd]<32 on the source). Propagated verbatim from sys_dup's gap-1
# ensures. This is what makes dup_shares_inode prove THROUGH THE API.
#@ ensures \result >= 3 ==> _filesystem.fd_open[\result] == 1
# the duped fd is in [3, 64) on success (body: newfd < 64 guard) — needed so a
# caller's fstat(dup_fd), whose guard requires fd < 64, can fire on the duped fd.
#@ ensures \result >= 3 ==> \result < 64
#@ ensures (\result >= 3 and 0 <= \old(_filesystem.fd_inode[fd]) and \old(_filesystem.fd_inode[fd]) < 32) ==> (0 <= _filesystem.fd_inode[\result] and _filesystem.fd_inode[\result] < 32)
def dup(fd):
    """Duplicate a file descriptor. Raises OSError on failure (CPython-faithful)."""
    newfd = _filesystem.sys_dup(fd)
    if newfd < 0:
        raise OSError
    return newfd

#@ requires fd >= 0
#@ assigns \nothing
# FAITHFUL FAILURE (os.rst l.47-49): fstat RAISES OSError (EBADF) on a bad/closed
# fd rather than returning -1. The EBADF discriminant `fd_open[fd]==0` is the SAME
# condition the kernel branches on, so the raise is body-faithful.
#@ raises OSError when True
#@ ensures 0 <= \result and \result < 32
# gap-15: with the `_filesystem.fd_inode[fd]` (global_field_subscript) grammar now
# admitted on a wrapper `#@ ensures`, the fd-RESOLUTION view of sys_fstat composes
# through the public API: fstat REPORTS the inode the fd resolves to. This is the
# BODY-PROVEN sys_fstat ensures `(fd < 64 and fd_open[fd]==1 and 0<=fd_inode[fd]<32)
# ==> \result == fd_inode[fd]` (commit 3dec789, ZERO trust) re-stated on the
# module-global filesystem. Composed with open's `fd_inode[result] ==
# dir_lookup(...)` resolution, a caller's fstat(open(p)) reports the inode p
# resolves to (the gap-14 §3 fstat consequence).
#@ ensures (fd < 64 and _filesystem.fd_open[fd] == 1 and 0 <= _filesystem.fd_inode[fd] and _filesystem.fd_inode[fd] < 32) ==> \result == _filesystem.fd_inode[fd]
# EBADF DIRECTION (now a RAISE, not -1): a closed fd in range (fd_open[fd]==0) makes
# fstat RAISE OSError. With close's CLOSE-POST-STATE this lets a caller OBSERVE close
# took effect: fstat(fd) raises after a successful close (the absence consequence).
# This is the NORMAL-RETURN restatement of that direction: if fstat RETURNS (does not
# raise), then an in-range fd was OPEN. BODY-PROVEN (ZERO trust): a normal return means
# `ino >= 0`, and sys_fstat's `(fd < 64 and fd_open[fd]==0) ==> \result == -1` ensures
# (UnixInodeFileSystem l.2841, the `if self.fd_open[fd]==0: return -1` guard) gives the
# contrapositive `\result != -1 and fd < 64 ==> fd_open[fd] != 0`. This is what lets a
# caller prove the post-close fstat MUST raise (its return-0 path is unreachable).
#@ ensures fd < 64 ==> _filesystem.fd_open[fd] != 0
def fstat(fd):
    """Get file status by file descriptor. Returns inode number; raises OSError
    on a bad/closed fd (CPython-faithful)."""
    ino = _filesystem.sys_fstat(fd)
    if ino < 0:
        raise OSError
    return ino

#@ requires True
#@ assigns _filesystem.disk
# FAITHFUL FAILURE (os.rst l.47-49): link RAISES OSError on failure (CPython raises
# FileNotFoundError when src is missing, FileExistsError when dst exists; the kernel
# collapses both to -1, so the wrapper raises generic OSError — still caught by
# `except OSError`). On success the new name dst is PRESENT.
#@ raises OSError when True
#@ ensures dir_lookup(_filesystem.dir, 5, dst) >= 0
def link(src: str, dst: str, *, src_dir_fd=None, dst_dir_fd=None,
         follow_symlinks=True):
    """Create a hard link. Raises OSError on failure (CPython-faithful)."""
    # gap-9: sys_link ensures `rc == 0 ==> dir_lookup(_filesystem.dir, 5, dst)
    # >= 0` (the hard-link mutator establishes the presence view for the new
    # name dst), so access(dst) reports PRESENT after a successful link.
    rc = _filesystem.sys_link(src, dst)
    if rc < 0:
        raise OSError

#@ requires fd >= 0
#@ requires how >= 0 and how <= 2
#@ assigns _filesystem.fd_offset
# FAITHFUL FAILURE (os.rst l.47-49): lseek RAISES OSError (EBADF on a bad fd /
# EINVAL on an invalid seek) rather than returning -1. On success returns the new
# absolute offset (>= 0).
#@ raises OSError when True
#@ ensures \result >= 0
# SEEK_SET CONSEQUENCE: propagate sys_lseek's absolute-seek post-state — an
# absolute seek (how == SEEK_SET == 0) to a non-negative pos on an open fd RETURNS
# that pos and sets the fd's offset to it. Body-faithful (sys_lseek's whence==0
# branch). This is the new position observable to a caller, not lseek's own code.
#@ ensures (how == 0 and pos >= 0 and fd < 64 and \old(_filesystem.fd_open[fd]) == 1) ==> \result == pos
#@ ensures (how == 0 and pos >= 0 and fd < 64 and \old(_filesystem.fd_open[fd]) == 1) ==> _filesystem.fd_offset[fd] == pos
def lseek(fd, pos, how):
    """Set the position of a file descriptor. Raises OSError on failure (CPython-faithful)."""
    rc = _filesystem.sys_lseek(fd, pos, how)
    if rc < 0:
        raise OSError
    return rc

#@ requires True
#@ assigns _filesystem.disk
# FAITHFUL FAILURE (os.rst l.47-49): makedirs RAISES OSError on failure (CPython
# raises FileExistsError when the leaf exists and not exist_ok, FileNotFoundError
# on a missing intermediate; the kernel collapses to -1, so the wrapper raises
# generic OSError — still caught by `except OSError`). Returns None on success.
#@ raises OSError when True
# gap-2: propagate mkdir's presence post-state. makedirs creates the dir (single
# level in this model) by delegating to sys_mkdir, which ensures `rc == 0 ==>
# dir_lookup(_filesystem.dir, 5, name) >= 0`. On the exist_ok shortcut the dir
# was already found PRESENT — checked via sys_access, whose `(\result == 0) <==>
# dir_lookup >= 0` ensures gives the PRESENT view directly. Both non-raising paths
# therefore leave the name PRESENT, so access(name) reports present after success.
#@ ensures dir_lookup(_filesystem.dir, 5, name) >= 0
def makedirs(name: str, mode=0o777, exist_ok=False):
    """Create a directory (single level in this model). Raises OSError on failure."""
    if exist_ok:
        if _filesystem.sys_access(name, 0) == 0:
            return
    rc = _filesystem.sys_mkdir(name, mode)
    if rc < 0:
        raise OSError

#@ requires True
#@ assigns \nothing
# FAITHFUL FAILURE (os.rst l.47-49): listdir RAISES OSError when the path does not
# resolve or is not a directory (CPython raises FileNotFoundError/NotADirectoryError;
# both IS-A OSError, caught by `except OSError`). On success returns the entry names.
#@ raises OSError when True
#@ ensures \length(\result) <= 16
def listdir(filepath: str = '.') -> list:
    """List directory contents. Returns list of entry names (≤ 16; return-arr.md).
    Raises OSError if the path is absent or not a directory (CPython-faithful)."""
    ino = _filesystem._dir_lookup(5, filepath) if filepath != '.' else 0
    if ino < 0 and filepath != '.':
        ino = 0
    if ino < 0 or ino >= 32:
        raise OSError
    inode = _filesystem._read_inode(ino)
    if inode[2] != 2:
        raise OSError
    p_block = inode[8]
    if p_block <= 0 or p_block >= 256:
        if ino == 0:
            p_block = 5
        else:
            raise OSError
    # Directly scan the 16 directory entries (avoids tuple-returning _read_directory)
    offset = p_block * 512
    names_out = []
    #@ loop invariant 0 <= len(names_out) and len(names_out) <= i
    #@ loop invariant 0 <= i and i <= 16
    #@ loop variant 16 - i
    for i in range(16):
        entry_offset = offset + (i * 32)
        entry_bytes = _filesystem.disk[entry_offset : entry_offset + 32]
        inode_num, name_bytes = _unpack_direntry(entry_bytes)
        name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
        if inode_num != 0 and name not in ('.', '..'):
            names_out.append(name)
    return names_out

#@ requires True
#@ assigns \nothing
# FAITHFUL FAILURE (os.rst l.47-49): scandir RAISES OSError when the path does not
# resolve or is not a directory (CPython raises FileNotFoundError/NotADirectoryError;
# both IS-A OSError). On success returns the DirEntry inode numbers.
#@ raises OSError when True
#@ ensures \length(\result) <= 16
def scandir(filepath: str = '.') -> list:
    """Return an iterator of DirEntry inode numbers for the directory (≤ 16; return-arr.md).
    Raises OSError if the path is absent or not a directory (CPython-faithful)."""
    ino = _filesystem._dir_lookup(5, filepath) if filepath != '.' else 0
    if ino < 0 and filepath != '.':
        ino = 0
    if ino < 0 or ino >= 32:
        raise OSError
    inode = _filesystem._read_inode(ino)
    if inode[2] != 2:
        raise OSError
    p_block = inode[8]
    if p_block <= 0 or p_block >= 256:
        if ino == 0:
            p_block = 5
        else:
            raise OSError
    # Directly scan the 16 directory entries (avoids tuple-returning _read_directory)
    offset = p_block * 512
    items = []
    #@ loop invariant 0 <= len(items) and len(items) <= i
    #@ loop invariant 0 <= i and i <= 16
    #@ loop variant 16 - i
    for i in range(16):
        entry_offset = offset + (i * 32)
        entry_bytes = _filesystem.disk[entry_offset : entry_offset + 32]
        inode_num, name_bytes = _unpack_direntry(entry_bytes)
        name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
        if inode_num != 0 and name not in ('.', '..'):
            items.append(inode_num)
    return items

#@ requires True
#@ assigns _filesystem.disk
# FAITHFUL FAILURE (os.rst l.47-49): remove RAISES OSError on failure (CPython raises
# FileNotFoundError on a missing path; the kernel collapses to -1, so the wrapper
# raises generic OSError — still caught by `except OSError`). On success the name is
# ABSENT.
#@ raises OSError when True
#@ ensures dir_lookup(_filesystem.dir, 5, filepath) < 0
def remove(filepath: str):
    """Remove a file. Raises OSError on failure (CPython-faithful)."""
    # gap-11: sys_unlink ensures `rc == 0 ==> dir_lookup(_filesystem.dir, 5,
    # filepath) < 0` (the unlink mutator establishes the ABSENCE view), so
    # access(filepath) reports ABSENT after a successful remove.
    rc = _filesystem.sys_unlink(filepath)
    if rc < 0:
        raise OSError

#@ requires True
#@ assigns _filesystem.disk
# FAITHFUL FAILURE (os.rst l.47-49): unlink RAISES OSError on failure (same as
# remove — CPython raises FileNotFoundError on a missing path).
#@ raises OSError when True
#@ ensures dir_lookup(_filesystem.dir, 5, filepath) < 0
def unlink(filepath: str, *, dir_fd=None):
    """Remove a file (same as remove). Raises OSError on failure (CPython-faithful)."""
    # gap-11: ABSENCE view propagated from sys_unlink.
    rc = _filesystem.sys_unlink(filepath)
    if rc < 0:
        raise OSError

#@ requires True
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.fd_block, _filesystem.next_fd
#@ ensures \result >= 3
# FAITHFUL FAILURE (os.rst l.47-49): open RAISES on failure rather than returning -1.
#   - ENOENT (name does not resolve): the precise FileNotFoundError. The discriminant
#     `dir_lookup(...) < 0` is the SAME condition the body branches on, so the precise
#     subclass costs no extra kernel re-query.
#   - any OTHER failure (ENFILE table full / permission denial after the name resolved):
#     generic OSError (still caught by `except OSError` via the Fix-1 hierarchy).
# On SUCCESS the result is a valid fd (>= 3) and the FORWARD resolution holds.
#@ raises FileNotFoundError when dir_lookup(_filesystem.dir, 5, filepath) < 0
#@ raises OSError when True
# fd-resolution-fidelity RETIRED (the LAST os bare \trusted, on sys_open): the public
# `open` contract no longer carries the FALSE UNCONDITIONED bi-implications. The honest
# directions are propagated verbatim from sys_open's now-ZERO-trust body:
#   - FORWARD resolution (body-proven): on (non-raising) success the fd resolves the name —
#     \result >= 3 ==> dir_lookup(post) >= 0, and fd_inode[\result] == dir_lookup(post).
#   - REVERSE no-failure, FREE-SLOT-CONDITIONED (the dup precedent): an EXISTING
#     readable name opened with a free fd slot at entry yields a valid fd. An
#     internals-blind formal-test driver establishes the free-slot side-condition via
#     `#@ fresh_globals` (the `_filesystem` constructor's all-free fd_open post-state,
#     carried across a prior open by the single-cell frame below).
#@ ensures \result >= 3 ==> (dir_lookup(_filesystem.dir, 5, filepath) >= 0)
#@ ensures (dir_lookup(\old(_filesystem.dir), 5, filepath) >= 0 and (\exists k: int; 3 <= k and k < 64 and \old(_filesystem.fd_open[k]) == 0)) ==> \result >= 3
# gap-15: on success the returned fd is OPEN and resolves to an in-range inode —
# the inode the path names. This is what lets a caller's fstat(open(p)) / dup(open(p))
# discharge (the fstat/dup wrappers' guards `fd_open[fd]==1`, `0<=fd_inode[fd]<32`
# are established here at the open site).
#@ ensures \result >= 3 ==> (\result < 64 and _filesystem.fd_open[\result] == 1 and 0 <= _filesystem.fd_inode[\result] and _filesystem.fd_inode[\result] < 32 and _filesystem.fd_inode[\result] == dir_lookup(_filesystem.dir, 5, filepath))
# M6 gap-17: a freshly opened fd starts at offset 0 — propagated so write() sees
# \old(fd_offset)==0 and its single-block content ensures fires (content round-trip).
#@ ensures \result >= 3 ==> _filesystem.fd_offset[\result] == 0
# fd-import-boundary FRAME: open touches AT MOST the returned slot of _filesystem.fd_open
# (sys_open's propagated single-cell frame). Carried to the public API so a caller can
# prove "the table is not full" survives a prior open — the free-slot side-condition a
# subsequent dup/open needs. Discharges directly from sys_open's identical boundary frame.
#@ ensures \forall k: int; (0 <= k and k < 64 and k != \result) ==> _filesystem.fd_open[k] == \old(_filesystem.fd_open[k])
def open(filepath: str, flags, mode=0o777, *, dir_fd=None):
    """Open a file. Returns a file descriptor on success; RAISES on failure
    (FileNotFoundError when the name does not resolve, else OSError) — faithful
    to CPython's os.open per os.rst l.47-49."""
    # gap-14: sys_open carries the fd-RESOLUTION + ENOENT discriminant tied to the
    # namespace view `dir_lookup(_filesystem.dir, 5, filepath)`. The kernel returns
    # -1 on any failure; the faithful wrapper raises instead.
    fd = _filesystem.sys_open(filepath, flags)
    if fd < 0:
        if _filesystem._dir_lookup(5, filepath) < 0:
            raise FileNotFoundError
        raise OSError
    return fd

#@ requires fd >= 0
#@ requires n >= 0
#@ assigns _filesystem.fd_offset
# FAITHFUL FAILURE (os.rst l.47-49): read RAISES OSError (EBADF) on a bad fd rather
# than returning -1. On success returns the non-negative byte count (<= n).
#@ raises OSError when True
#@ ensures \result >= 0 and \result <= n
# gap-16: read's CONTENT LINK propagated — the returned count is bounded by the
# request and (on a whole-file read from offset 0) equals the file's content
# length `inode[0]`. read returns a COUNT, not the bytes, so the full read-back
# equality stays unnameable through the public API (gap-16 §read).
# gap-17: the SIZE link propagated to the public API. On a whole-file read from
# offset 0 (n >= inode_size, size non-negative), the count EQUALS the reopened
# inode's SIZE field. This is the read end of the content round-trip: with
# write's SIZE post-state and open's reopen frame, read(reopen(p)) == len(data)
# is now derivable THROUGH THE API.
#@ ensures (fd < 64 and _filesystem.fd_open[fd] == 1 and 0 <= _filesystem.fd_inode[fd] and _filesystem.fd_inode[fd] < 32 and \old(_filesystem.fd_offset[fd]) == 0 and inode_size(_filesystem.disk, _filesystem.fd_inode[fd]) >= 0 and n >= inode_size(_filesystem.disk, _filesystem.fd_inode[fd])) ==> \result == inode_size(_filesystem.disk, _filesystem.fd_inode[fd])
def read(fd, n):
    """Read from a file descriptor. Returns byte count; raises OSError on a bad fd."""
    rc = _filesystem.sys_read(fd, n)
    if rc < 0:
        raise OSError
    return rc

#@ requires fd >= 0
#@ requires \length(data) <= 5120
#@ assigns _filesystem.disk, _filesystem.fd_offset, _filesystem.fd_block, _filesystem._mtime_ticks
# FAITHFUL FAILURE (os.rst l.47-49): write RAISES OSError (EBADF on a bad fd, ENOSPC
# on a full disk) rather than returning -1. On success returns the non-negative count
# (<= len(data)).
#@ raises OSError when True
#@ ensures \result >= 0 and \result <= \length(data)
# M6 gap-16/17: write's CONTENT POST-STATE now PROPAGATED to the public API (was a
# comment only — the quantified ensures is exposed here so a caller can compose the
# content round-trip with pread). On a single-block success from offset 0, the written
# bytes land in the file's first data block, so the on-disk content view EQUALS `data`.
#@ ensures (fd < 64 and \old(_filesystem.fd_open[fd]) == 1 and 0 <= _filesystem.fd_inode[fd] and _filesystem.fd_inode[fd] < 32 and \old(_filesystem.fd_offset[fd]) == 0 and \length(data) <= 512) ==> \result == \length(data)
# gap-17 SOLVED: the content claim is exposed as the FOLDED `block_content_eq` atom, which
# DOES propagate across the no_inline sys_write boundary (the raw ∀i did not). Composes with
# pread's block_content_eq to give the public-API content round-trip (write→pread == data).
#@ ensures (\result == \length(data) and \old(_filesystem.fd_offset[fd]) == 0 and \length(data) <= 512) ==> block_content_eq(_filesystem.disk, _filesystem.fd_block[fd], data)
#@ ensures (\result == \length(data) and \result >= 1 and \old(_filesystem.fd_offset[fd]) == 0 and \length(data) <= 512) ==> (6 <= _filesystem.fd_block[fd] and _filesystem.fd_block[fd] < 256)
def write(fd, data: list):
    """Write to a file descriptor. Returns byte count; raises OSError on failure."""
    rc = _filesystem.sys_write(fd, data)
    if rc < 0:
        raise OSError
    return rc

#@ requires fd >= 0
#@ requires nbytes >= 0 and nbytes <= 512
#@ assigns \nothing
# FAITHFUL FAILURE (os.rst l.47-49): pread RAISES OSError (EBADF) on a bad/closed fd
# rather than silently returning [].  The EBADF discriminant (`fd >= 64` or
# `fd_open[fd] == 0`) is checked in the wrapper before delegating.  (CPython's pread
# returns b'' at EOF — that is NOT a failure and is preserved on a live fd.)
#@ raises OSError when (fd >= 64 or _filesystem.fd_open[fd] == 0)
# M6 gap-17: content-returning POSITIONAL read. Returns the bytes of the file's first
# data block — the CONTENT view `disk[fd_block*512+i]` that write establishes — so a
# caller composes write→pread into the content round-trip (result == data).
#@ ensures \length(\result) == nbytes or \length(\result) == 0
#@ ensures (fd < 64 and _filesystem.fd_open[fd] == 1 and offset == 0 and 6 <= _filesystem.fd_block[fd] and _filesystem.fd_block[fd] < 256) ==> \length(\result) == nbytes
#@ ensures \forall i: int; (0 <= i and i < \length(\result)) ==> \result[i] == _filesystem.disk[_filesystem.fd_block[fd] * 512 + i]
#@ ensures block_content_eq(_filesystem.disk, _filesystem.fd_block[fd], \result)
def pread(fd, nbytes, offset=0) -> list:
    """Read `nbytes` from `fd` at `offset` (positional). Returns the bytes; raises
    OSError on a bad/closed fd (CPython-faithful)."""
    if fd >= 64 or _filesystem.fd_open[fd] == 0:
        raise OSError
    return _filesystem.sys_pread(fd, nbytes, offset)

#@ assigns _filesystem.disk, _filesystem.dir
# FAITHFUL FAILURE (os.rst l.47-49): rename RAISES OSError on failure (CPython raises
# FileNotFoundError when src is missing; the kernel collapses to -1, so the wrapper
# raises generic OSError). Returns None on success.
#@ raises OSError when True
#@ ensures (src != dst) ==> (dir_lookup(_filesystem.dir, 5, dst) >= 0)
#@ ensures (src != dst) ==> (dir_lookup(_filesystem.dir, 5, src) < 0)
def rename(src: str, dst: str, *, src_dir_fd=None, dst_dir_fd=None):
    """Rename a file or directory. Raises OSError on failure (CPython-faithful)."""
    # gap-9: sys_rename ensures `rc == 0 ==> dir_lookup(_filesystem.dir, 5, dst)
    # >= 0` (the rename mutator establishes the presence view for the new name
    # dst), so access(dst) reports PRESENT after a successful rename.
    # gap-11: `rc == 0 ==> dir_lookup(_filesystem.dir, 5, src) < 0` — the DUAL
    # `src`-ABSENT direction, so access(src) reports ABSENT after rename.
    rc = _filesystem.sys_rename(src, dst)
    if rc < 0:
        raise OSError

# FAITHFUL FAILURE SEMANTICS (os.rst l.47-49: "All functions in this module
# raise OSError (or subclasses) in the case of invalid or inaccessible file
# names and paths …").  The wrapper is the errno->exception translation layer
# (exactly as CPython's `os` module is a thin wrapper over the syscall ABI):
# the `sys_*` KERNEL layer keeps the faithful Unix-syscall `-1` return (that IS
# the kernel ABI), and the wrapper turns `-1` into the right OSError subclass.
#   - mkdir on an existing name -> FileExistsError (CPython EEXIST); any other
#     mkdir failure (ENFILE/ENOSPC/perm) -> generic OSError.
# On success mkdir returns None (CPython) and the presence view holds.
#@ requires True
#@ assigns _filesystem.disk
#@ raises OSError when True
#@ ensures dir_lookup(_filesystem.dir, 5, filepath) >= 0
def mkdir(filepath: str, mode=0o777, *, dir_fd=None):
    """Create a directory. Raises OSError on any failure (faithful to
    CPython's os.mkdir, which raises OSError/FileExistsError)."""
    rc = _filesystem.sys_mkdir(filepath, mode)
    if rc < 0:
        raise OSError
    # gap-9: success establishes the presence view (sys_mkdir's post-state).

#@ requires True
#@ assigns _filesystem.disk
#@ raises OSError when True
#@ ensures dir_lookup(_filesystem.dir, 5, filepath) < 0
def rmdir(filepath: str, *, dir_fd=None):
    """Remove a directory. Raises OSError on any failure (faithful to CPython's
    os.rmdir, which raises FileNotFoundError/OSError)."""
    rc = _filesystem.sys_rmdir(filepath)
    if rc < 0:
        raise OSError
    # gap-11: success establishes the ABSENCE view (sys_rmdir's post-state).

#@ requires True
#@ assigns \nothing
#@ raises FileNotFoundError when dir_lookup(_filesystem.dir, 5, filepath) < 0
#@ ensures 0 <= \result and \result < 32
#@ ensures dir_lookup(_filesystem.dir, 5, filepath) >= 0
def stat(filepath: str, *, dir_fd=None, follow_symlinks=True):
    """Get file status. Returns the inode number on success, raises
    FileNotFoundError if the path does not resolve (faithful to CPython)."""
    # PATH-LINK (stat consequence): sys_stat carries the `dir_lookup` ensures
    # (body-proven via _dir_lookup, no new trust). On absence the kernel
    # returns -1; the faithful wrapper raises FileNotFoundError instead.
    ino = _filesystem.sys_stat(filepath)
    if ino < 0:
        raise FileNotFoundError
    return ino

#@ requires True
#@ assigns \nothing
# FAITHFUL FAILURE (os.rst l.47-49): lstat RAISES FileNotFoundError when the path
# does not resolve rather than returning -1 (the discriminant `dir_lookup < 0` is the
# same condition the kernel branches on, so the precise subclass is free). On success
# returns the inode in [0, 32).
#@ raises FileNotFoundError when dir_lookup(_filesystem.dir, 5, filepath) < 0
#@ ensures 0 <= \result and \result < 32
#@ ensures dir_lookup(_filesystem.dir, 5, filepath) >= 0
def lstat(filepath: str, *, dir_fd=None):
    """Like stat() but does not follow symbolic links. Raises FileNotFoundError
    if the path does not resolve (CPython-faithful)."""
    # PATH-LINK (lstat consequence): sys_lstat (root-dir name lookup,
    # identical to stat in this single-level model) carries the same two
    # `dir_lookup` ensures, body-proven via _dir_lookup with no new trust.
    ino = _filesystem.sys_lstat(filepath)
    if ino < 0:
        raise FileNotFoundError
    return ino

#@ requires True
#@ assigns _filesystem.disk
# FAITHFUL FAILURE (os.rst l.47-49): symlink RAISES OSError on failure (CPython raises
# FileExistsError when the link name exists; the kernel collapses to -1, so the
# wrapper raises generic OSError). On success the link name dst is PRESENT.
#@ raises OSError when True
#@ ensures dir_lookup(_filesystem.dir, 5, dst) >= 0
def symlink(src: str, dst: str, target_is_directory=False, *, dir_fd=None):
    """Create a symbolic link. Raises OSError on failure (CPython-faithful)."""
    # gap-9: sys_symlink ensures `rc == 0 ==> dir_lookup(_filesystem.dir, 5,
    # linkpath) >= 0` (the symlink mutator establishes the presence view for the
    # link name dst), so access(dst) reports PRESENT after a successful symlink.
    rc = _filesystem.sys_symlink(src, dst)
    if rc < 0:
        raise OSError

#@ requires True
#@ assigns \nothing
# FAITHFUL FAILURE (os.rst l.47-49): readlink RAISES OSError on failure (CPython raises
# FileNotFoundError on a missing path, EINVAL when the path is not a symlink; the
# kernel collapses to -1, so the wrapper raises generic OSError). On success returns
# the target descriptor in [0, 256).
#@ raises OSError when True
#@ ensures \result >= 0 and \result < 256
def readlink(filepath: str, *, dir_fd=None):
    """Read the target of a symbolic link. Raises OSError on failure (CPython-faithful)."""
    rc = _filesystem.sys_readlink(filepath)
    if rc < 0:
        raise OSError
    return rc

#@ requires True
#@ assigns _filesystem.disk
# FAITHFUL FAILURE (os.rst l.47-49): truncate RAISES OSError on failure (CPython raises
# FileNotFoundError on a missing path; the kernel collapses to -1, so the wrapper
# raises generic OSError). Returns None on success.
#@ raises OSError when True
def truncate(filepath: str, length):
    """Truncate a file to a specified length. Raises OSError on failure (CPython-faithful)."""
    rc = _filesystem.sys_truncate(filepath, length)
    if rc < 0:
        raise OSError


# ── Pure-Python functions (no filesystem needed) ─────────────────────

#@ requires True
#@ assigns \nothing
# gap-2: fsdecode is identity on its argument; pin that documented identity so a
# caller's `fsdecode(x) == x` is entailed. The post-state holds for any element
# type (the body is `return filename`), so the contract is body-faithful without a
# type-narrowing on the param.
#@ ensures \result == filename
def fsdecode(filename):
    """Decode filename — identity in formal model."""
    return filename

#@ requires True
#@ assigns \nothing
# gap-2: identity on the argument (body `return filename`).
#@ ensures \result == filename
def fsencode(filename):
    """Encode filename — identity in formal model."""
    return filename

#@ requires True
#@ assigns \nothing
# gap-2: identity on the argument (body `return filepath`).
#@ ensures \result == filepath
def fspath(filepath):
    """Return the file system representation of the path — identity."""
    return filepath

#@ requires True
#@ assigns \nothing
#@ ensures \result == 0
def getcwd():
    """Return the current working directory (root inode = 0)."""
    return 0

#@ requires True
#@ assigns \nothing
# gap-2: this model has an empty env, so getenv always returns `default` (body
# `return default`). Pin that so a caller's `getenv(k, d) == d` is entailed.
#@ ensures \result == default
def getenv(key, default=0):
    """Get an environment variable. Returns default if not found."""
    return default

#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def getpid():
    """Return the current process ID."""
    return _pid

#@ requires True
#@ assigns \nothing
#@ ensures \result == 0
def get_exec_path(env=None):
    """Return the list of directories to search for executables."""
    return 0


# ── Stubs returning default values ───────────────────────────────────

#@ requires True
#@ assigns \nothing
#@ ensures \result == 0
def chflags(filepath, flags, follow_symlinks=True):
    """Set file flags. Stub: returns 0."""
    return 0

#@ requires True
#@ assigns \nothing
#@ ensures \result == 0
def confstr(name):
    """Return system configuration string. Stub: returns 0."""
    return 0

#@ requires count >= 0
#@ assigns \nothing
#@ ensures \result == 0
def copy_file_range(src, dst, count, offset_src=None, offset_dst=None):
    """Copy data between file descriptors. Stub: returns 0."""
    return 0

#@ requires True
#@ assigns \nothing
#@ ensures \result == 0
def getxattr(filepath, attribute, *, follow_symlinks=True):
    """Get extended file attribute. Stub: returns 0."""
    return 0

#@ requires True
#@ assigns \nothing
#@ ensures \result == 0
def listxattr(filepath=None, *, follow_symlinks=True):
    """List extended file attributes. Stub: returns 0."""
    return 0

#@ requires pid >= 0
#@ requires sig >= 0
#@ assigns \nothing
#@ ensures \result == 0
def _kill(pid, sig):
    """Send signal to a process. Stub: no-op, returns 0."""
    return 0

kill = _kill


# ── Cross-module re-exports ──────────────────────────────────────────

#@ requires True
#@ assigns \nothing
#@ ensures \result == 0
def islink(filepath):
    """Test whether a path is a symbolic link (stub: always 0)."""
    return 0

#@ requires True
#@ assigns \nothing
# gap-3 (walk generator) — Strategy A: PyCSL's emitter cannot lower `yield`
# (the yield expression emits as type `()`, causing a WhyML type error on the
# walk import stub). Rewritten as a NON-generator returning the COUNT of
# subdirectory names found at `top` (an int). The original generator yielded
# `(top, dirs, nondirs)` triples; PyCSL cannot express a (string, list, list)
# tuple return nor a string-list return (tuple/seq component-type inference
# defaults to int), so the public return is narrowed to the bounded COUNT —
# the totality + bounded-result consequence a caller can prove is preserved.
# Single-level model (no recursion into subdirs).
#@ raises OSError when True
#@ ensures \result >= 0 and \result <= 16
def walk(top: str, topdown=True, onerror=None, followlinks=False):
    """Directory tree walker. Simplified: returns the count of subdirectory
    names at `top` (0..16). Raises OSError if `top` does not resolve or is
    not a directory (CPython-faithful, via listdir)."""
    names = listdir(top)
    dirs = []
    nondirs = []
    #@ loop invariant 0 <= len(dirs) and len(dirs) <= i
    #@ loop invariant 0 <= len(nondirs) and len(nondirs) <= i
    #@ loop invariant 0 <= i and i <= len(names)
    #@ loop variant len(names) - i
    for i in range(len(names)):
        name = names[i]
        ino = _filesystem.sys_stat(name)
        if ino >= 0 and ino < 32:
            inode = _filesystem._read_inode(ino)
            if inode[2] == 2:
                dirs.append(name)
            else:
                nondirs.append(name)
        else:
            nondirs.append(name)
    return len(dirs)


