"""Pure Python os package — module-level POSIX API backed by UnixInodeFileSystem.

Instantiates a global ``_filesystem`` and exposes standard ``os.*`` functions
that delegate to it. Functions without a filesystem equivalent return
sensible defaults.
"""
from .UnixInodeFileSystem import UnixInodeFileSystem
from . import path

# ── Global virtual filesystem ────────────────────────────────────────
_filesystem = UnixInodeFileSystem()

# ── Constants ────────────────────────────────────────────────────────

# Open flags
O_RDONLY = UnixInodeFileSystem.O_RDONLY
O_WRONLY = UnixInodeFileSystem.O_WRONLY
O_RDWR = UnixInodeFileSystem.O_RDWR
O_CREAT = UnixInodeFileSystem.O_CREAT

# lseek whence
SEEK_SET = UnixInodeFileSystem.SEEK_SET
SEEK_CUR = UnixInodeFileSystem.SEEK_CUR
SEEK_END = UnixInodeFileSystem.SEEK_END

# Filesystem geometry
BLOCK_SIZE = UnixInodeFileSystem.BLOCK_SIZE
NUM_BLOCKS = UnixInodeFileSystem.NUM_BLOCKS
MAX_INODES = UnixInodeFileSystem.MAX_INODES

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

class DirEntry:
    """Minimal os.DirEntry returned by scandir()."""

    def __init__(self, name, inode_num, fs):
        self.name = name
        self.path = '/' + name if name not in ('.', '..') else name
        self._inode_num = inode_num
        self._fs = fs

    def is_dir(self) -> bool:
        if self._inode_num < 0 or self._inode_num >= 32:
            return False
        inode = self._fs._read_inode(self._inode_num)
        return inode[2] == 2

    def is_file(self) -> bool:
        if self._inode_num < 0 or self._inode_num >= 32:
            return False
        inode = self._fs._read_inode(self._inode_num)
        return inode[2] == 1

    def is_symlink(self) -> bool:
        if self._inode_num < 0 or self._inode_num >= 32:
            return False
        inode = self._fs._read_inode(self._inode_num)
        return inode[2] == 3

    def is_junction(self) -> bool:
        return False

    def __repr__(self):
        return f"<DirEntry '{self.name}'>"


# ── Functions delegating to _filesystem ──────────────────────────────

def access(filepath, mode, *, dir_fd=None, effective_ids=False,
           follow_symlinks=True):
    """Check file accessibility. Delegates to _filesystem.sys_access."""
    return _filesystem.sys_access(filepath, mode) == 0


def chmod(filepath, mode, *, dir_fd=None, follow_symlinks=True):
    """Change file mode bits."""
    return _filesystem.sys_chmod(filepath, mode)


def close(fd):
    """Close a file descriptor."""
    return _filesystem.sys_close(fd)


def dup(fd):
    """Duplicate a file descriptor."""
    return _filesystem.sys_dup(fd)


def fstat(fd):
    """Get file status by file descriptor. Returns inode number."""
    return _filesystem.sys_fstat(fd)


def link(src, dst, *, src_dir_fd=None, dst_dir_fd=None,
         follow_symlinks=True):
    """Create a hard link."""
    return _filesystem.sys_link(src, dst)


def lseek(fd, pos, how):
    """Set the position of a file descriptor."""
    return _filesystem.sys_lseek(fd, pos, how)


def makedirs(name, mode=0o777, exist_ok=False):
    """Create a directory (single level in this model)."""
    if exist_ok:
        ino = _filesystem.sys_stat(name)
        if ino >= 0:
            return None
    return _filesystem.sys_mkdir(name, mode)


def listdir(filepath='.'):
    """List directory contents. Returns list of entry names."""
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
    entries = _filesystem._read_directory(p_block)
    return [name for name, inum in entries
            if name not in ('.', '..') and inum != 0]


def scandir(filepath='.'):
    """Return an iterator of DirEntry objects for the directory."""
    ino = _filesystem._dir_lookup(5, filepath) if filepath != '.' else 0
    if ino < 0 and filepath != '.':
        ino = 0
    if ino < 0 or ino >= 32:
        return iter([])
    inode = _filesystem._read_inode(ino)
    if inode[2] != 2:
        return iter([])
    p_block = inode[8]
    if p_block <= 0 or p_block >= 256:
        if ino == 0:
            p_block = 5
        else:
            return iter([])
    entries = _filesystem._read_directory(p_block)
    result = []
    for name, inum in entries:
        if name not in ('.', '..') and inum != 0:
            result.append(DirEntry(name, inum, _filesystem))
    return iter(result)


def remove(filepath):
    """Remove a file."""
    return _filesystem.sys_unlink(filepath)


def unlink(filepath, *, dir_fd=None):
    """Remove a file (same as remove)."""
    return _filesystem.sys_unlink(filepath)


def open(filepath, flags, mode=0o777, *, dir_fd=None):
    """Open a file. Returns a file descriptor."""
    return _filesystem.sys_open(filepath, flags)


def read(fd, n):
    """Read from a file descriptor. Returns byte count."""
    return _filesystem.sys_read(fd, n)


def write(fd, data):
    """Write to a file descriptor. Returns byte count."""
    if isinstance(data, (bytes, bytearray)):
        data = list(data)
    return _filesystem.sys_write(fd, data)


def rename(src, dst, *, src_dir_fd=None, dst_dir_fd=None):
    """Rename a file or directory."""
    return _filesystem.sys_rename(src, dst)


def mkdir(filepath, mode=0o777, *, dir_fd=None):
    """Create a directory."""
    return _filesystem.sys_mkdir(filepath, mode)


def rmdir(filepath, *, dir_fd=None):
    """Remove a directory."""
    return _filesystem.sys_rmdir(filepath)


def stat(filepath, *, dir_fd=None, follow_symlinks=True):
    """Get file status. Returns inode number."""
    return _filesystem.sys_stat(filepath)


def lstat(filepath, *, dir_fd=None):
    """Like stat() but does not follow symbolic links."""
    return _filesystem.sys_stat(filepath)


def symlink(src, dst, target_is_directory=False, *, dir_fd=None):
    """Create a symbolic link."""
    return _filesystem.sys_symlink(src, dst)


def readlink(filepath, *, dir_fd=None):
    """Read the target of a symbolic link."""
    return _filesystem.sys_readlink(filepath)


def truncate(filepath, length):
    """Truncate a file to a specified length."""
    return _filesystem.sys_truncate(filepath, length)


# ── Pure-Python functions (no filesystem needed) ─────────────────────

def fsdecode(filename):
    """Decode filename from bytes to str."""
    if isinstance(filename, bytes):
        return filename.decode('utf-8', errors='surrogateescape')
    return filename


def fsencode(filename):
    """Encode filename from str to bytes."""
    if isinstance(filename, str):
        return filename.encode('utf-8', errors='surrogateescape')
    return filename


def fspath(filepath):
    """Return the file system representation of the path."""
    if isinstance(filepath, str):
        return filepath
    if isinstance(filepath, bytes):
        return filepath
    if hasattr(filepath, '__fspath__'):
        return filepath.__fspath__()
    raise TypeError(f'expected str, bytes or os.PathLike, not '
                    f'{type(filepath).__name__}')


def getcwd():
    """Return the current working directory."""
    return '/'


def getenv(key, default=None):
    """Get an environment variable."""
    return environ.get(key, default)


def getpid():
    """Return the current process ID."""
    return _pid


def get_exec_path(env=None):
    """Return the list of directories to search for executables."""
    if env is None:
        env = environ
    path_str = env.get('PATH', '/usr/bin:/bin')
    return path_str.split(':')


# ── Stubs returning default values ───────────────────────────────────

def chflags(filepath, flags, follow_symlinks=True):
    """Set file flags. Stub: returns 0."""
    return 0


def confstr(name):
    """Return system configuration string. Stub: returns empty string."""
    return ''


def copy_file_range(src, dst, count, offset_src=None, offset_dst=None):
    """Copy data between file descriptors. Stub: returns 0."""
    return 0


def getxattr(filepath, attribute, *, follow_symlinks=True):
    """Get extended file attribute. Stub: returns empty bytes."""
    return b''


def listxattr(filepath=None, *, follow_symlinks=True):
    """List extended file attributes. Stub: returns empty list."""
    return []


def kill(pid, sig):
    """Send signal to a process. Stub: no-op, returns None."""
    return None


# ── Cross-module re-exports ──────────────────────────────────────────

islink = path.islink if hasattr(path, 'islink') else (lambda p: False)


def walk(top, topdown=True, onerror=None, followlinks=False):
    """Directory tree generator. Simplified: yields one level from root."""
    names = listdir(top)
    dirs = []
    nondirs = []
    for name in names:
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
