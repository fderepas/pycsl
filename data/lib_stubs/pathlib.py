"""PyCSL mock for Python's pathlib module.

Provides trusted stubs for filesystem path operations.
"""
_ = 0  # anchor

# ── PurePath constructors ───────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def PurePath(pathsegments: int) -> int:
    """Mock: generic class representing the system's path flavour."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePosixPath(pathsegments: int) -> int:
    """Mock: path flavour for non-Windows filesystem paths."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PureWindowsPath(pathsegments: int) -> int:
    """Mock: path flavour for Windows filesystem paths."""
    return 0

# ── PurePath properties ────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def PurePath_parser(self: int) -> int:
    """Mock: the os.path module used for low-level path parsing."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_drive(self: int) -> int:
    """Mock: string representing the drive letter or name, if any."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_root(self: int) -> int:
    """Mock: string representing the local or global root, if any."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_anchor(self: int) -> int:
    """Mock: the concatenation of the drive and root."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_parts(self: int) -> int:
    """Mock: tuple giving access to the path's various components."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_parents(self: int) -> int:
    """Mock: immutable sequence providing access to logical ancestors."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_parent(self: int) -> int:
    """Mock: the logical parent of the path."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_name(self: int) -> int:
    """Mock: final path component, excluding drive and root."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_suffix(self: int) -> int:
    """Mock: the last dot-separated portion of the final component."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_suffixes(self: int) -> int:
    """Mock: list of the path's suffixes (file extensions)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_stem(self: int) -> int:
    """Mock: final path component without its suffix."""
    return 0

# ── PurePath methods ───────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def PurePath_as_posix(self: int) -> int:
    """Mock: return string representation with forward slashes."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_is_absolute(self: int) -> int:
    """Mock: return whether the path is absolute or not."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_is_relative_to(self: int, other: int) -> int:
    """Mock: return whether this path is relative to the other path."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_joinpath(self: int, pathsegments: int) -> int:
    """Mock: combine the path with each of the given path segments."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_full_match(self: int, pattern: int) -> int:
    """Mock: match this path against a glob-style pattern."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_match(self: int, pattern: int) -> int:
    """Mock: match this path against a non-recursive glob-style pattern."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_relative_to(self: int, other: int) -> int:
    """Mock: compute a version of this path relative to other."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_with_name(self: int, name: int) -> int:
    """Mock: return a new path with the name changed."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_with_stem(self: int, stem: int) -> int:
    """Mock: return a new path with the stem changed."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_with_suffix(self: int, suffix: int) -> int:
    """Mock: return a new path with the suffix changed."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PurePath_with_segments(self: int, pathsegments: int) -> int:
    """Mock: create a new path object of the same type."""
    return 0

# ── Path constructors ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Path(pathsegments: int) -> int:
    """Mock: concrete path of the system's path flavour."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PosixPath(pathsegments: int) -> int:
    """Mock: concrete non-Windows filesystem path."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WindowsPath(pathsegments: int) -> int:
    """Mock: concrete Windows filesystem path."""
    return 0

# ── Path class methods ─────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Path_cwd() -> int:
    """Mock: return new path object representing the current directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_home() -> int:
    """Mock: return new path object representing the user's home directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_from_uri(uri: int) -> int:
    """Mock: return a new path object from parsing a file URI."""
    return 0

# ── Path URI and resolution ────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Path_as_uri(self: int) -> int:
    """Mock: represent the path as a file URI."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_expanduser(self: int) -> int:
    """Mock: return new path with expanded ~ and ~user constructs."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_absolute(self: int) -> int:
    """Mock: make the path absolute without normalization."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_resolve(self: int, strict: int) -> int:
    """Mock: make the path absolute, resolving any symlinks."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_readlink(self: int) -> int:
    """Mock: return the path to which the symbolic link points."""
    return 0

# ── Path querying file type and status ─────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Path_stat(self: int, follow_symlinks: int) -> int:
    """Mock: return os.stat_result with information about this path."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_lstat(self: int) -> int:
    """Mock: like stat but return symbolic link's info rather than target's."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_exists(self: int, follow_symlinks: int) -> int:
    """Mock: return True if the path points to an existing file or directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_is_file(self: int, follow_symlinks: int) -> int:
    """Mock: return True if the path points to a regular file."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_is_dir(self: int, follow_symlinks: int) -> int:
    """Mock: return True if the path points to a directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_is_symlink(self: int) -> int:
    """Mock: return True if the path points to a symbolic link."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_is_junction(self: int) -> int:
    """Mock: return True if the path points to a junction."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_is_mount(self: int) -> int:
    """Mock: return True if the path is a mount point."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_is_socket(self: int) -> int:
    """Mock: return True if the path points to a Unix socket."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_is_fifo(self: int) -> int:
    """Mock: return True if the path points to a FIFO."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_is_block_device(self: int) -> int:
    """Mock: return True if the path points to a block device."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_is_char_device(self: int) -> int:
    """Mock: return True if the path points to a character device."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_samefile(self: int, other_path: int) -> int:
    """Mock: return whether this path points to the same file as other_path."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_info(self: int) -> int:
    """Mock: PathInfo object supporting file type queries with caching."""
    return 0

# ── Path reading and writing files ─────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Path_open(self: int, mode: int, buffering: int, encoding: int, errors: int, newline: int) -> int:
    """Mock: open the file pointed to by the path."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_read_text(self: int, encoding: int, errors: int, newline: int) -> int:
    """Mock: return the decoded contents of the file as a string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_read_bytes(self: int) -> int:
    """Mock: return the binary contents of the file as a bytes object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_write_text(self: int, data: int, encoding: int, errors: int, newline: int) -> int:
    """Mock: write text data to the file and return characters written."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_write_bytes(self: int, data: int) -> int:
    """Mock: write binary data to the file and return bytes written."""
    return 0

# ── Path reading directories ──────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Path_iterdir(self: int) -> int:
    """Mock: yield path objects of the directory contents."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_glob(self: int, pattern: int, case_sensitive: int, recurse_symlinks: int) -> int:
    """Mock: glob the given relative pattern in the directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_rglob(self: int, pattern: int, case_sensitive: int, recurse_symlinks: int) -> int:
    """Mock: glob the given relative pattern recursively."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_walk(self: int, top_down: int, on_error: int, follow_symlinks: int) -> int:
    """Mock: generate file names in a directory tree by walking."""
    return 0

# ── Path creating files and directories ────────────────────────────

#@ \trusted
#@ ensures \result == 0
def Path_touch(self: int, mode: int, exist_ok: int) -> int:
    """Mock: create a file at this given path."""
    return 0

#@ \trusted
#@ ensures \result == 0
def Path_mkdir(self: int, mode: int, parents: int, exist_ok: int) -> int:
    """Mock: create a new directory at this given path."""
    return 0

#@ \trusted
#@ ensures \result == 0
def Path_symlink_to(self: int, target: int, target_is_directory: int) -> int:
    """Mock: make this path a symbolic link pointing to target."""
    return 0

#@ \trusted
#@ ensures \result == 0
def Path_hardlink_to(self: int, target: int) -> int:
    """Mock: make this path a hard link to the same file as target."""
    return 0

#@ \trusted
#@ ensures \result == 0
def Path_link_to(self: int, target: int) -> int:
    """Mock: make target a hard link to this path (deprecated)."""
    return 0

# ── Path copying, moving and deleting ──────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Path_copy(self: int, target: int, follow_symlinks: int, preserve_metadata: int) -> int:
    """Mock: copy this file or directory tree to the given target."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_copy_into(self: int, target_dir: int, follow_symlinks: int, preserve_metadata: int) -> int:
    """Mock: copy this file or directory tree into the given target directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_rename(self: int, target: int) -> int:
    """Mock: rename this file or directory to the given target."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_replace(self: int, target: int) -> int:
    """Mock: rename this file or directory, unconditionally replacing target."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_move(self: int, target: int) -> int:
    """Mock: move this file or directory tree to the given target."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_move_into(self: int, target_dir: int) -> int:
    """Mock: move this file or directory tree into the given target directory."""
    return 0

#@ \trusted
#@ ensures \result == 0
def Path_unlink(self: int, missing_ok: int) -> int:
    """Mock: remove this file or symbolic link."""
    return 0

#@ \trusted
#@ ensures \result == 0
def Path_rmdir(self: int) -> int:
    """Mock: remove this directory (must be empty)."""
    return 0

# ── Path permissions and ownership ─────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Path_owner(self: int, follow_symlinks: int) -> int:
    """Mock: return the name of the user owning the file."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Path_group(self: int, follow_symlinks: int) -> int:
    """Mock: return the name of the group owning the file."""
    return 0

#@ \trusted
#@ ensures \result == 0
def Path_chmod(self: int, mode: int, follow_symlinks: int) -> int:
    """Mock: change the file mode and permissions."""
    return 0

#@ \trusted
#@ ensures \result == 0
def Path_lchmod(self: int, mode: int) -> int:
    """Mock: like chmod but change the symbolic link's mode."""
    return 0
