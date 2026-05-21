"""PyCSL mock for Python's shutil module — High-level file operations, including copying."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def copyfileobj(fsrc: int, fdst: int, length: int) -> int:
    """Mock: Copy the contents of the :term:`file-like object <file object>` *fsrc* to the file-like object *fdst*. The integer *leng..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copyfile(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: Copy the contents (no metadata) of the file named *src* to a file named *dst* and return *dst* in the most efficient way..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copymode(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: Copy the permission bits from *src* to *dst*.  The file contents, owner, and group are unaffected.  *src* and *dst* are ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copystat(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: Copy the permission bits, last access time, last modification time, and flags from *src* to *dst*.  On Linux, :func:`cop..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copy(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: Copies the file *src* to the file or directory *dst*.  *src* and *dst* should be :term:`path-like objects <path-like obj..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copy2(src: int, dst: int, follow_symlinks: int) -> int:
    """Mock: Identical to :func:`~shutil.copy` except that :func:`copy2` also attempts to preserve file metadata. When *follow_symlin..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ignore_patterns() -> int:
    """Mock: This factory function creates a function that can be used as a callable for :func:`copytree`\'s *ignore* argument, ignor..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copytree(src: int, dst: int, symlinks: int, ignore: int, __copy_function: int, ignore_dangling_symlinks: int, __dirs_exist_ok: int) -> int:
    """Mock: Recursively copy an entire directory tree rooted at *src* to a directory named *dst* and return the destination director..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def rmtree(path: int, ignore_errors: int, onerror: int, onexc: int, dir_fd: int) -> int:
    """Mock: .. index:: single: directory; deleting Delete an entire directory tree; *path* must point to a directory (but not a symb..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def move(src: int, dst: int, copy_function: int) -> int:
    """Mock: Recursively move a file or directory (*src*) to another location and return the destination. If *dst* is an existing dir..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def disk_usage(path: int) -> int:
    """Mock: Return disk usage statistics about the given path as a :term:`named tuple` with the attributes *total*, *used* and *free..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def chown(path: int, user: int, group: int, dir_fd: int, __follow_symlinks: int) -> int:
    """Mock: Change owner *user* and/or *group* of the given *path*. *user* can be a system user name or a uid; the same applies to *..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def which(cmd: int, mode: int, path: int) -> int:
    """Mock: Return the path to an executable which would be run if the given *cmd* was called.  If no *cmd* would be called, return ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_archive(base_name: int, format: int, root_dir: int, base_dir: int, verbose: int, dry_run: int, owner: int) -> int:
    """Mock: Create an archive file (such as zip or tar) and return its name. *base_name* is a string or :term:`path-like object` spe..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_archive_formats() -> int:
    """Mock: Return a list of supported formats for archiving. Each element of the returned sequence is a tuple ``(name, description)..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def register_archive_format(name: int, function_: int, extra_args: int, description: int) -> int:
    """Mock: Register an archiver for the format *name*. *function* is the callable that will be used to unpack archives. The callabl..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unregister_archive_format(name: int) -> int:
    """Mock: Remove the archive format *name* from the list of supported formats."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unpack_archive(filename: int, extract_dir: int, format: int, filter: int) -> int:
    """Mock: Unpack an archive. *filename* is the full path of the archive. *extract_dir* is the name of the target directory where t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register_unpack_format(name: int, extensions: int, function_: int, extra_args: int, description: int) -> int:
    """Mock: Registers an unpack format. *name* is the name of the format and *extensions* is a list of extensions corresponding to t..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unregister_unpack_format(name: int) -> int:
    """Mock: Unregister an unpack format. *name* is the name of the format."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_unpack_formats() -> int:
    """Mock: Return a list of all registered formats for unpacking. Each element of the returned sequence is a tuple ``(name, extensi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_terminal_size(fallback: int) -> int:
    """Mock: Get the size of the terminal window. For each of the two dimensions, the environment variable, ``COLUMNS`` and ``LINES``..."""
    return 0
