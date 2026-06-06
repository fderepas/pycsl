"""Pure Python os package — re-exports UnixInodeFileSystem and constants."""
from .UnixInodeFileSystem import UnixInodeFileSystem
from . import path

# Re-export open flags as module-level constants
O_RDONLY = UnixInodeFileSystem.O_RDONLY
O_WRONLY = UnixInodeFileSystem.O_WRONLY
O_RDWR = UnixInodeFileSystem.O_RDWR
O_CREAT = UnixInodeFileSystem.O_CREAT

# Re-export lseek whence flags
SEEK_SET = UnixInodeFileSystem.SEEK_SET
SEEK_CUR = UnixInodeFileSystem.SEEK_CUR
SEEK_END = UnixInodeFileSystem.SEEK_END

# Filesystem constants
BLOCK_SIZE = UnixInodeFileSystem.BLOCK_SIZE
NUM_BLOCKS = UnixInodeFileSystem.NUM_BLOCKS
MAX_INODES = UnixInodeFileSystem.MAX_INODES

# Path separator
sep = '/'

# Access mode constants
F_OK = 0
R_OK = 4
W_OK = 2
X_OK = 1
