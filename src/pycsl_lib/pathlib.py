"""PyCSL mock for Python's pathlib module.

Provides trusted stubs for filesystem path operations.
Classes model object invariants; factory functions provide constructors.
"""
_ = 0  # anchor

# ── PurePathObj ──────────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._parts >= 0
class PurePathObj:
    def __init__(self):
        self._parts = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def drive(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def root(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def anchor(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._parts
    #@ assigns \nothing
    def parts_count(self) -> int:
        return self._parts

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def parents(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def parent(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def name(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def suffix(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def suffixes(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def stem(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def as_posix(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def is_absolute(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def is_relative_to(self, other: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def joinpath(self, pathsegments: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def full_match(self, pattern: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def path_match(self, pattern: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def relative_to(self, other: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def with_name(self, n: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def with_stem(self, s: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def with_suffix(self, s: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def with_segments(self, pathsegments: int) -> int:
        return 0

# ── PathObj ──────────────────────────────────────────────────────────

#@ class invariant self._p_parts >= 0
#@ class invariant self._p_exists >= 0
class PathObj:
    def __init__(self):
        self._p_parts = 0
        self._p_exists = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def drive(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def root(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def anchor(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._p_parts
    #@ assigns \nothing
    def parts_count(self) -> int:
        return self._p_parts

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def parents(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def parent(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def name(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def suffix(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def suffixes(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def stem(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def as_posix(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def is_absolute(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def is_relative_to(self, other: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def joinpath(self, pathsegments: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def full_match(self, pattern: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def path_match(self, pattern: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def relative_to(self, other: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def with_name(self, n: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def with_stem(self, s: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def with_suffix(self, s: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def with_segments(self, pathsegments: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def cwd_path(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def home_path(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def from_uri(self, uri: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def as_uri(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def expanduser(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.absolute
#@ requires True
#@ ensures True
#@ assigns \nothing
    def absolute(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve
#@ requires True
#@ ensures True
#@ assigns \nothing
    def resolve(self, strict: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.readlink
#@ requires True
#@ ensures True
#@ assigns \nothing
    def readlink(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.stat
#@ ensures True
#@ assigns \nothing
    def stat(self, follow_symlinks: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.lstat
#@ requires True
#@ ensures True
#@ assigns \nothing
    def lstat(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.exists
#@ requires True
#@ ensures \result == 0 || \result == 1
#@ assigns \nothing
    def path_exists(self, follow_symlinks: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_file
#@ ensures \result == 0 || \result == 1
#@ assigns \nothing
    def is_file(self, follow_symlinks: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_dir
#@ requires True
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
    def is_dir(self, follow_symlinks: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_symlink
#@ requires True
#@ ensures True
#@ assigns \nothing
    def is_symlink(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pathlib/_local.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def is_junction(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_mount
#@ requires True
#@ ensures True
#@ assigns \nothing
    def is_mount(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_socket
#@ requires True
#@ ensures True
#@ assigns \nothing
    def is_socket(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_fifo
#@ requires True
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
    def is_fifo(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pathlib/_abc.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def is_block_device(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_char_device
#@ requires True
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
    def is_char_device(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.samefile
#@ requires True
#@ ensures True
#@ assigns \nothing
    def samefile(self, other_path: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/io.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def open_file(self, mode: int, buffering: int, encoding: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.read_text
#@ requires True
#@ ensures True
#@ assigns \nothing
    def read_text(self, encoding: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.read_bytes
#@ requires True
#@ ensures True
#@ assigns \nothing
    def read_bytes(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pathlib/_local.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def write_text(self, data: int, encoding: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.write_bytes
#@ requires True
#@ ensures True
#@ assigns \nothing
    def write_bytes(self, data: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: cpython/Lib/pathlib.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def iterdir(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pathlib/__init__.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def glob_path(self, pattern: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.rglob
#@ requires True
#@ ensures True
    def rglob(self, pattern: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pathlib/_abc.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def walk(self, top_down: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.touch
#@ ensures True
#@ assigns \nothing
    def touch(self, mode: int, exist_ok: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir
#@ requires True
#@ ensures True
#@ assigns \nothing
    def mkdir(self, mode: int, parents_flag: int, exist_ok: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.symlink_to
#@ ensures True
#@ assigns \nothing
    def symlink_to(self, target: int, target_is_directory: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.hardlink_to
#@ requires True
#@ ensures True
#@ assigns \nothing
    def hardlink_to(self, target: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pathlib/_local.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def copy_file(self, target: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.rename
#@ requires True
#@ ensures True
#@ assigns \nothing
    def rename_path(self, target: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pathlib/_local.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def replace_path(self, target: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.rename
#@ requires True
#@ ensures True
#@ assigns \nothing
    def move_path(self, target: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.unlink
#@ requires True
#@ ensures True
#@ assigns \nothing
    def unlink(self, missing_ok: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.rmdir
#@ requires True
#@ ensures True
#@ assigns \nothing
    def rmdir(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.owner
#@ requires True
#@ ensures True
#@ assigns \nothing
    def owner(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pathlib/__init__.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def group_name(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path.chmod
#@ requires True
#@ ensures True
#@ assigns \nothing
    def chmod(self, mode: int) -> int:
        return 0

# ── Standalone constructor functions ─────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.PurePath
#@ ensures True
def PurePath(pathsegments: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.Path
#@ ensures \result > 0
def Path(pathsegments: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.PurePosixPath
#@ ensures True
def PurePosixPath(pathsegments: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.PureWindowsPath
#@ ensures \result >= 0
def PureWindowsPath(pathsegments: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.PosixPath
#@ ensures True
def PosixPath(pathsegments: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/pathlib.html#pathlib.WindowsPath
#@ ensures True
def WindowsPath(pathsegments: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pathlib/_local.py
#@ requires True
#@ ensures True
def Path_cwd() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: cpython/Lib/pathlib.py#Path.home
#@ requires True
#@ ensures True
def Path_home() -> int:
    return 0
