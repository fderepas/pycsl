"""PyCSL mock for Python's shutil module.

Provides trusted stubs for high-level file operations: copying,
moving, removing directory trees, archiving, ownership changes,
path lookup, and terminal size queries.
Side-effect functions ensure result == 0; functions returning
paths, objects, or data ensure result >= 0.
"""
_ = 0  # anchor

# ── Copy operations ─────────────────────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def copyfileobj(fsrc: int, fdst: int, length: int) -> int:
    """Mock: copy contents between file-like objects."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copyfile(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: copy file contents, return destination path."""
    return 0

#@ \trusted
#@ ensures \result == 0
def copymode(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: copy permission bits from src to dst."""
    return 0

#@ \trusted
#@ ensures \result == 0
def copystat(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: copy permission bits, times, and flags from src to dst."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copy(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: copy file data and permissions, return destination path."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copy2(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: copy file data and metadata, return destination path."""
    return 0

# ── Directory tree operations ───────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def ignore_patterns(patterns: int) -> int:
    """Mock: create callable for copytree ignore argument."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copytree(src: int, dst: int, symlinks: int, ignore: int, copy_function: int, ignore_dangling_symlinks: int, dirs_exist_ok: int) -> int:
    """Mock: recursively copy directory tree, return destination."""
    return 0

#@ \trusted
#@ ensures \result == 0
def rmtree(path: int, ignore_errors: int, onerror: int, onexc: int, dir_fd: int) -> int:
    """Mock: recursively delete a directory tree."""
    return 0

# ── Move and rename ─────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def move(src: int, dst: int, copy_function: int) -> int:
    """Mock: recursively move file or directory, return destination."""
    return 0

# ── Disk and ownership ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def disk_usage(path: int) -> int:
    """Mock: return disk usage statistics as named tuple."""
    return 0

#@ \trusted
#@ ensures \result == 0
def chown(path: int, user: int, group: int, dir_fd: int, follow_symlinks: int) -> int:
    """Mock: change owner and group of a path."""
    return 0

# ── Path lookup ─────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def which(cmd: int, mode: int, path: int) -> int:
    """Mock: return path to executable found on PATH."""
    return 0

# ── Archiving ───────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def make_archive(base_name: int, format: int, root_dir: int, base_dir: int, verbose: int, dry_run: int, owner: int, group: int, logger: int) -> int:
    """Mock: create archive file and return its name."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_archive_formats() -> int:
    """Mock: return list of supported archive formats."""
    return 0

#@ \trusted
#@ ensures \result == 0
def register_archive_format(name: int, func: int, extra_args: int, description: int) -> int:
    """Mock: register an archiver for a format."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unregister_archive_format(name: int) -> int:
    """Mock: remove archive format from supported list."""
    return 0

# ── Unpacking ───────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def unpack_archive(filename: int, extract_dir: int, format: int, filter: int) -> int:
    """Mock: unpack an archive to a target directory."""
    return 0

#@ \trusted
#@ ensures \result == 0
def register_unpack_format(name: int, extensions: int, func: int, extra_args: int, description: int) -> int:
    """Mock: register an unpack format with extensions."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unregister_unpack_format(name: int) -> int:
    """Mock: unregister an unpack format."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_unpack_formats() -> int:
    """Mock: return list of registered unpack formats."""
    return 0

# ── Terminal ────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def get_terminal_size(fallback: int) -> int:
    """Mock: return terminal window size as named tuple."""
    return 0
