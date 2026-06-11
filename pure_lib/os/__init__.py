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

#@ class invariant self._inode_num >= -1 and self._inode_num < 32
class DirEntry:
    """Minimal os.DirEntry returned by scandir()."""

    #@ requires inode_num >= -1 and inode_num < 32
    #@ assigns self.name, self.path, self._inode_num, self._fs
    #@ ensures self._inode_num == inode_num
    def __init__(self, name, inode_num, fs):
        self.name = name
        self.path = name
        self._inode_num = inode_num
        self._fs = fs

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == 1
    def is_dir(self) -> int:
        if self._inode_num < 0 or self._inode_num >= 32:
            return 0
        inode = self._fs._read_inode(self._inode_num)
        if inode[2] == 2:
            return 1
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == 1
    def is_file(self) -> int:
        if self._inode_num < 0 or self._inode_num >= 32:
            return 0
        inode = self._fs._read_inode(self._inode_num)
        if inode[2] == 1:
            return 1
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == 1
    def is_symlink(self) -> int:
        if self._inode_num < 0 or self._inode_num >= 32:
            return 0
        inode = self._fs._read_inode(self._inode_num)
        if inode[2] == 3:
            return 1
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == 0
    def is_junction(self) -> int:
        return 0



# ── Functions delegating to _filesystem ──────────────────────────────

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == 1
#@ ensures (\result == 1) <==> (dir_lookup(_filesystem.disk, 5, filepath) >= 0)
def access(filepath: str, mode, *, dir_fd=None, effective_ids=False,
           follow_symlinks=True):
    """Check file accessibility. Returns 1 if accessible, 0 otherwise."""
    r = _filesystem.sys_access(filepath, mode)
    # gap-9: sys_access ensures `(r == 0) <==> dir_lookup(_filesystem.disk, 5,
    # filepath) >= 0` (the directory-scan presence view). result == 1 iff r == 0,
    # so the observer reflects presence.
    if r == 0:
        return 1
    return 0

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def chmod(filepath, mode, *, dir_fd=None, follow_symlinks=True):
    """Change file mode bits."""
    return _filesystem.sys_chmod(filepath, mode)

#@ requires fd >= 0
#@ assigns _filesystem.fd_open
#@ ensures \result == 0 or \result == -1
def close(fd):
    """Close a file descriptor."""
    return _filesystem.sys_close(fd)

#@ requires fd >= 0
#@ assigns _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.next_fd
#@ ensures \result == -1 or \result >= 3
# gap-15: with the `_filesystem.fd_inode[fd]` (global_field_subscript) grammar, the
# dup SHARED-OPEN-FILE-DESCRIPTION view composes through the public API:
#   - VALIDITY-GIVEN-VALID-SOURCE: a valid open source fd dups to a valid fd (>= 3),
#     so a caller's dup(open(p)) is valid (the gap-14 §5 validity consequence). This
#     rests on sys_dup's interim `\trusted fd-resolution-fidelity` (the no-ENFILE
#     direction the model can't yet derive).
#   - SHARED INODE: the duped fd resolves to the SAME inode as the source —
#     `_filesystem.fd_inode[\result] == _filesystem.fd_inode[fd]` — so dup and the
#     source share one open-file-description (the inode the source resolves to).
#@ ensures (fd < 64 and \old(_filesystem.fd_open[fd]) == 1) ==> \result >= 3
#@ ensures \result >= 3 ==> _filesystem.fd_inode[\result] == \old(_filesystem.fd_inode[fd])
def dup(fd):
    """Duplicate a file descriptor."""
    return _filesystem.sys_dup(fd)

#@ requires fd >= 0
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
# gap-15: with the `_filesystem.fd_inode[fd]` (global_field_subscript) grammar now
# admitted on a wrapper `#@ ensures`, the fd-RESOLUTION view of sys_fstat composes
# through the public API: fstat REPORTS the inode the fd resolves to. This is the
# BODY-PROVEN sys_fstat ensures `(fd < 64 and fd_open[fd]==1 and 0<=fd_inode[fd]<32)
# ==> \result == fd_inode[fd]` (commit 3dec789, ZERO trust) re-stated on the
# module-global filesystem. Composed with open's `fd_inode[result] ==
# dir_lookup(...)` resolution, a caller's fstat(open(p)) reports the inode p
# resolves to (the gap-14 §3 fstat consequence).
#@ ensures (fd < 64 and _filesystem.fd_open[fd] == 1 and 0 <= _filesystem.fd_inode[fd] and _filesystem.fd_inode[fd] < 32) ==> \result == _filesystem.fd_inode[fd]
def fstat(fd):
    """Get file status by file descriptor. Returns inode number."""
    return _filesystem.sys_fstat(fd)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
#@ ensures \result == 0 ==> (dir_lookup(_filesystem.disk, 5, dst) >= 0)
def link(src: str, dst: str, *, src_dir_fd=None, dst_dir_fd=None,
         follow_symlinks=True):
    """Create a hard link."""
    # gap-9: sys_link ensures `rc == 0 ==> dir_lookup(_filesystem.disk, 5, dst)
    # >= 0` (the hard-link mutator establishes the presence view for the new
    # name dst), so access(dst) reports PRESENT after a successful link.
    return _filesystem.sys_link(src, dst)

#@ requires fd >= 0
#@ requires how >= 0 and how <= 2
#@ assigns _filesystem.fd_offset
#@ ensures \result >= -1
# gap-17: SEEK_SET offset post-state propagated to the public API — lseek(fd, pos,
# SEEK_SET) on a valid fd with pos >= 0 sets the offset to pos and returns it. The
# rewind consequence the content round-trip rests on (re-establish offset 0 before
# read-back), and a standalone lseek consequence.
#@ ensures (fd < 64 and _filesystem.fd_open[fd] == 1 and how == 0 and pos >= 0) ==> (_filesystem.fd_offset[fd] == pos and \result == pos)
def lseek(fd, pos, how):
    """Set the position of a file descriptor."""
    return _filesystem.sys_lseek(fd, pos, how)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def makedirs(name: str, mode=0o777, exist_ok=False):
    """Create a directory (single level in this model)."""
    if exist_ok:
        ino = _filesystem.sys_stat(name)
        if ino >= 0:
            return 0
    return _filesystem.sys_mkdir(name, mode)

#@ requires True
#@ assigns \nothing
#@ ensures \length(\result) <= 16
def listdir(filepath='.') -> list:
    """List directory contents. Returns list of entry names (≤ 16; return-arr.md)."""
    ino = _filesystem._dir_lookup(5, filepath) if filepath != '.' else 0
    if ino < 0 and filepath != '.':
        ino = 0
    if ino < 0 or ino >= 32:
        return []
    inode = _filesystem._read_inode(ino)
    if inode[2] != 2:
        return []
    p_block = inode[8]
    if p_block <= 0 or p_block >= 256:
        if ino == 0:
            p_block = 5
        else:
            return []
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
#@ ensures \length(\result) <= 16
def scandir(filepath='.') -> list:
    """Return an iterator of DirEntry inode numbers for the directory (≤ 16; return-arr.md)."""
    ino = _filesystem._dir_lookup(5, filepath) if filepath != '.' else 0
    if ino < 0 and filepath != '.':
        ino = 0
    if ino < 0 or ino >= 32:
        return []
    inode = _filesystem._read_inode(ino)
    if inode[2] != 2:
        return []
    p_block = inode[8]
    if p_block <= 0 or p_block >= 256:
        if ino == 0:
            p_block = 5
        else:
            return []
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
#@ ensures \result == 0 or \result == -1
#@ ensures \result == 0 ==> (dir_lookup(_filesystem.disk, 5, filepath) < 0)
def remove(filepath: str):
    """Remove a file."""
    # gap-11: sys_unlink ensures `rc == 0 ==> dir_lookup(_filesystem.disk, 5,
    # filepath) < 0` (the unlink mutator establishes the ABSENCE view), so
    # access(filepath) reports ABSENT after a successful remove.
    return _filesystem.sys_unlink(filepath)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
#@ ensures \result == 0 ==> (dir_lookup(_filesystem.disk, 5, filepath) < 0)
def unlink(filepath: str, *, dir_fd=None):
    """Remove a file (same as remove)."""
    # gap-11: ABSENCE view propagated from sys_unlink.
    return _filesystem.sys_unlink(filepath)

#@ requires True
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.fd_block, _filesystem.next_fd
#@ ensures \result == -1 or \result >= 3
#@ ensures (\result >= 3) <==> (dir_lookup(_filesystem.disk, 5, filepath) >= 0)
#@ ensures (\result == -1) <==> (dir_lookup(_filesystem.disk, 5, filepath) < 0)
# gap-15: with the `_filesystem.fd_inode[\result]` (global_field_subscript) grammar,
# propagate sys_open's fd-RESOLUTION post-state to the public API so the fd-chain
# composes: on success the returned fd is OPEN and resolves to an in-range inode —
# the inode the path names. This is what lets a caller's fstat(open(p)) / dup(open(p))
# discharge (the fstat/dup wrappers' guards `fd_open[fd]==1`, `0<=fd_inode[fd]<32`
# are established here at the open site).
#@ ensures \result >= 3 ==> (\result < 64 and _filesystem.fd_open[\result] == 1 and 0 <= _filesystem.fd_inode[\result] and _filesystem.fd_inode[\result] < 32 and _filesystem.fd_inode[\result] == dir_lookup(_filesystem.disk, 5, filepath))
def open(filepath: str, flags, mode=0o777, *, dir_fd=None):
    """Open a file. Returns a file descriptor."""
    # gap-14: sys_open carries the fd-RESOLUTION + ENOENT discriminant tied to the
    # namespace view `dir_lookup(_filesystem.disk, 5, filepath)` — a valid fd (>= 3)
    # iff the name resolves, with `fd_inode[result]` resolving to the path's inode
    # (the fd-chain analogue of gap-9, one rung lower). Propagated here so a caller
    # sees: open(existing) >= 3, open(absent O_RDONLY) == -1, and fstat(open(p))
    # reports the resolved inode (composing on the now-proven namespace).
    return _filesystem.sys_open(filepath, flags)

#@ requires fd >= 0
#@ requires n >= 0
#@ assigns _filesystem.fd_offset
#@ ensures \result == -1 or (\result >= 0 and \result <= n)
# gap-16: read's CONTENT LINK propagated — the returned count is bounded by the
# request and (on a whole-file read from offset 0) equals the file's content
# length `inode[0]`. read returns a COUNT, not the bytes, so the full read-back
# equality stays unnameable through the public API (gap-16 §read).
#@ ensures \result >= 0 ==> \result <= n
# gap-17: the SIZE link propagated to the public API. On a whole-file read from
# offset 0 (n >= inode_size, size non-negative), the count EQUALS the reopened
# inode's SIZE field. This is the read end of the content round-trip: with
# write's SIZE post-state and open's reopen frame, read(reopen(p)) == len(data)
# is now derivable THROUGH THE API.
#@ ensures (fd < 64 and _filesystem.fd_open[fd] == 1 and 0 <= _filesystem.fd_inode[fd] and _filesystem.fd_inode[fd] < 32 and \old(_filesystem.fd_offset[fd]) == 0 and inode_size(_filesystem.disk, _filesystem.fd_inode[fd]) >= 0 and n >= inode_size(_filesystem.disk, _filesystem.fd_inode[fd])) ==> \result == inode_size(_filesystem.disk, _filesystem.fd_inode[fd])
# gap-17: the complement — a request within the file (0 <= n <= inode_size)
# returns exactly n. With write's inode_size >= len(data), reading len(data) back
# from offset 0 returns len(data) THROUGH THE API.
#@ ensures (fd < 64 and _filesystem.fd_open[fd] == 1 and 0 <= _filesystem.fd_inode[fd] and _filesystem.fd_inode[fd] < 32 and \old(_filesystem.fd_offset[fd]) == 0 and n >= 0 and n <= inode_size(_filesystem.disk, _filesystem.fd_inode[fd])) ==> \result == n
def read(fd, n):
    """Read from a file descriptor. Returns byte count."""
    return _filesystem.sys_read(fd, n)

#@ requires fd >= 0
#@ assigns _filesystem.disk, _filesystem.fd_offset, _filesystem.fd_block
#@ ensures \result == -1 or \result >= 0
# gap-16: write's CONTENT POST-STATE propagated — the inode_content view. On a
# single-block success from offset 0 (`\result == \length(data)`,
# `\length(data) <= 512`), the written bytes LAND in the file's first data block,
# so the on-disk content view EQUALS `data` element-for-element:
#   \result == \length(data) ==>
#     \forall i; 0<=i<\result ==> _filesystem.disk[_filesystem.fd_block[fd]*512 + i] == data[i]
# This is `inode_content(fd_inode[fd]) == data` made concrete over the data-block
# layout (the content twin of the namespace `dir_lookup` view, one rung lower).
#@ ensures \result == -1 or \result <= \length(data)
# gap-17: the SIZE post-state propagated — a full single-block write from offset 0
# leaves the inode SIZE field at least len(data). With read's count==min link, this
# is the WRITE end of the content round-trip.
#@ ensures (fd < 64 and _filesystem.fd_open[fd] == 1 and 0 <= _filesystem.fd_inode[fd] and _filesystem.fd_inode[fd] < 32 and \old(_filesystem.fd_offset[fd]) == 0 and \length(data) <= 512 and \result == \length(data)) ==> inode_size(_filesystem.disk, _filesystem.fd_inode[fd]) >= \length(data)
# gap-17: the NAMESPACE FRAME propagated — write resolves/links no name, so it
# preserves dir_lookup of every name. This carries A := dir_lookup(disk,5,p) from
# create across write->close->reopen so the reopened fd recovers the same inode.
#@ ensures \forall q: str; dir_lookup(_filesystem.disk, 5, q) == \old(dir_lookup(_filesystem.disk, 5, q))
#@ proof rocq UnixFs.Dir.lookup_frame
#@ proof lean UnixFs.Dir.lookup_frame
def write(fd, data: list):
    """Write to a file descriptor. Returns byte count."""
    return _filesystem.sys_write(fd, data)

#@ requires src != dst
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
#@ ensures \result == 0 ==> (dir_lookup(_filesystem.disk, 5, dst) >= 0)
#@ ensures \result == 0 ==> (dir_lookup(_filesystem.disk, 5, src) < 0)
def rename(src: str, dst: str, *, src_dir_fd=None, dst_dir_fd=None):
    """Rename a file or directory."""
    # gap-9: sys_rename ensures `rc == 0 ==> dir_lookup(_filesystem.disk, 5, dst)
    # >= 0` (the rename mutator establishes the presence view for the new name
    # dst), so access(dst) reports PRESENT after a successful rename.
    # gap-11: `rc == 0 ==> dir_lookup(_filesystem.disk, 5, src) < 0` — the DUAL
    # `src`-ABSENT direction, so access(src) reports ABSENT after rename.
    return _filesystem.sys_rename(src, dst)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
#@ ensures \result == 0 ==> (dir_lookup(_filesystem.disk, 5, filepath) >= 0)
def mkdir(filepath: str, mode=0o777, *, dir_fd=None):
    """Create a directory."""
    rc = _filesystem.sys_mkdir(filepath, mode)
    # gap-9: sys_mkdir ensures `rc == 0 ==> dir_lookup(_filesystem.disk, 5,
    # filepath) >= 0` (the mutator establishes the presence view).
    return rc

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
#@ ensures \result == 0 ==> (dir_lookup(_filesystem.disk, 5, filepath) < 0)
def rmdir(filepath: str, *, dir_fd=None):
    """Remove a directory."""
    # gap-11: sys_rmdir ensures `rc == 0 ==> dir_lookup(_filesystem.disk, 5,
    # filepath) < 0` (the rmdir mutator establishes the ABSENCE view), so
    # access(filepath) reports ABSENT after a successful rmdir.
    return _filesystem.sys_rmdir(filepath)

#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def stat(filepath: str, *, dir_fd=None, follow_symlinks=True):
    """Get file status. Returns inode number."""
    return _filesystem.sys_stat(filepath)

#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def lstat(filepath: str, *, dir_fd=None):
    """Like stat() but does not follow symbolic links."""
    return _filesystem.sys_stat(filepath)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def symlink(src: str, dst: str, target_is_directory=False, *, dir_fd=None):
    """Create a symbolic link."""
    return _filesystem.sys_symlink(src, dst)

#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 256)
def readlink(filepath: str, *, dir_fd=None):
    """Read the target of a symbolic link."""
    return _filesystem.sys_readlink(filepath)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def truncate(filepath, length):
    """Truncate a file to a specified length."""
    return _filesystem.sys_truncate(filepath, length)


# ── Pure-Python functions (no filesystem needed) ─────────────────────

#@ requires True
#@ assigns \nothing
#@ ensures True
def fsdecode(filename):
    """Decode filename — identity in formal model."""
    return filename

#@ requires True
#@ assigns \nothing
#@ ensures True
def fsencode(filename):
    """Encode filename — identity in formal model."""
    return filename

#@ requires True
#@ assigns \nothing
#@ ensures True
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
#@ ensures True
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
#@ ensures True
def walk(top, topdown=True, onerror=None, followlinks=False):
    """Directory tree generator. Simplified: yields one level from root."""
    names = listdir(top)
    dirs = []
    nondirs = []
    #@ loop invariant 0 <= len(dirs) and len(dirs) <= i
    #@ loop invariant 0 <= len(nondirs) and len(nondirs) <= i
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
    yield top, dirs, nondirs
