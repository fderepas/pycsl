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
def access(filepath: str, mode, *, dir_fd=None, effective_ids=False,
           follow_symlinks=True):
    """Check file accessibility. Returns 1 if accessible, 0 otherwise."""
    r = _filesystem.sys_access(filepath, mode)
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
def dup(fd):
    """Duplicate a file descriptor."""
    return _filesystem.sys_dup(fd)

#@ requires fd >= 0
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def fstat(fd):
    """Get file status by file descriptor. Returns inode number."""
    return _filesystem.sys_fstat(fd)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def link(src, dst, *, src_dir_fd=None, dst_dir_fd=None,
         follow_symlinks=True):
    """Create a hard link."""
    return _filesystem.sys_link(src, dst)

#@ requires fd >= 0
#@ requires how >= 0 and how <= 2
#@ assigns _filesystem.fd_offset
#@ ensures \result >= -1
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
def remove(filepath: str):
    """Remove a file."""
    return _filesystem.sys_unlink(filepath)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def unlink(filepath: str, *, dir_fd=None):
    """Remove a file (same as remove)."""
    return _filesystem.sys_unlink(filepath)

#@ requires True
#@ assigns _filesystem.disk, _filesystem.fd_open, _filesystem.fd_inode, _filesystem.fd_offset, _filesystem.fd_flags, _filesystem.next_fd
#@ ensures \result == -1 or \result >= 3
def open(filepath: str, flags, mode=0o777, *, dir_fd=None):
    """Open a file. Returns a file descriptor."""
    return _filesystem.sys_open(filepath, flags)

#@ requires fd >= 0
#@ requires n >= 0
#@ assigns _filesystem.fd_offset
#@ ensures \result == -1 or (\result >= 0 and \result <= n)
def read(fd, n):
    """Read from a file descriptor. Returns byte count."""
    return _filesystem.sys_read(fd, n)

#@ requires fd >= 0
#@ assigns _filesystem.disk, _filesystem.fd_offset
#@ ensures \result == -1 or \result >= 0
def write(fd, data: list):
    """Write to a file descriptor. Returns byte count."""
    return _filesystem.sys_write(fd, data)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def rename(src, dst, *, src_dir_fd=None, dst_dir_fd=None):
    """Rename a file or directory."""
    return _filesystem.sys_rename(src, dst)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def mkdir(filepath: str, mode=0o777, *, dir_fd=None):
    """Create a directory."""
    return _filesystem.sys_mkdir(filepath, mode)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def rmdir(filepath, *, dir_fd=None):
    """Remove a directory."""
    return _filesystem.sys_rmdir(filepath)

#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def stat(filepath, *, dir_fd=None, follow_symlinks=True):
    """Get file status. Returns inode number."""
    return _filesystem.sys_stat(filepath)

#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 32)
def lstat(filepath, *, dir_fd=None):
    """Like stat() but does not follow symbolic links."""
    return _filesystem.sys_stat(filepath)

#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 0 or \result == -1
def symlink(src, dst, target_is_directory=False, *, dir_fd=None):
    """Create a symbolic link."""
    return _filesystem.sys_symlink(src, dst)

#@ requires True
#@ assigns \nothing
#@ ensures \result == -1 or (\result >= 0 and \result < 256)
def readlink(filepath, *, dir_fd=None):
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
