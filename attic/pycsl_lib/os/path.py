"""PyCSL mock for Python's os.path module — Operations on pathnames."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def abspath(path: int) -> int:
    """Mock: Return a normalized absolutized version of the pathname *path*. On most platforms, this is equivalent to calling ``normp..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def basename(path: int) -> int:
    """Mock: Return the base name of pathname *path*.  This is the second element of the pair returned by passing *path* to the funct..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def commonpath(paths: int) -> int:
    """Mock: Return the longest common sub-path of each pathname in the iterable *paths*.  Raise :exc:`ValueError` if *paths* contain..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def commonprefix(list: int) -> int:
    """Mock: Return the longest string prefix (taken character-by-character) that is a prefix of all strings in *list*.  If *list* is..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dirname(path: int) -> int:
    """Mock: Return the directory name of pathname *path*.  This is the first element of the pair returned by passing *path* to the f..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def exists(path: int) -> int:
    """Mock: Return ``True`` if *path* refers to an existing path or an open file descriptor.  Returns ``False`` for broken symbolic ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def lexists(path: int) -> int:
    """Mock: Return ``True`` if *path* refers to an existing path, including broken symbolic links.   Equivalent to :func:`exists` on..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def expanduser(path: int) -> int:
    """Mock: On Unix and Windows, return the argument with an initial component of ``~`` or ``~user`` replaced by that *user*'s home ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def expandvars(path: int) -> int:
    """Mock: Return the argument with environment variables expanded.  Substrings of the form ``$name`` or ``${name}`` are replaced b..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getatime(path: int) -> int:
    """Mock: Return the time of last access of *path*.  The return value is a floating-point number giving the number of seconds sinc..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getmtime(path: int) -> int:
    """Mock: Return the time of last modification of *path*.  The return value is a floating-point number giving the number of second..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getctime(path: int) -> int:
    """Mock: Return the system's ctime which, on some systems (like Unix) is the time of the last metadata change, and, on others (li..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsize(path: int) -> int:
    """Mock: Return the size, in bytes, of *path*.  Raise :exc:`OSError` if the file does not exist or is inaccessible. .. versioncha..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isabs(path: int) -> int:
    """Mock: Return ``True`` if *path* is an absolute pathname.  On Unix, that means it begins with a slash, on Windows that it begin..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isfile(path: int) -> int:
    """Mock: Return ``True`` if *path* is an :func:`existing <exists>` regular file. This follows symbolic links, so both :func:`isli..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isdir(path: int) -> int:
    """Mock: Return ``True`` if *path* is an :func:`existing <exists>` directory.  This follows symbolic links, so both :func:`islink..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isjunction(path: int) -> int:
    """Mock: Return ``True`` if *path* refers to an :func:`existing <lexists>` directory entry that is a junction.  Always return ``F..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def islink(path: int) -> int:
    """Mock: Return ``True`` if *path* refers to an :func:`existing <exists>` directory entry that is a symbolic link.  Always ``Fals..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def ismount(path: int) -> int:
    """Mock: Return ``True`` if pathname *path* is a :dfn:`mount point`: a point in a file system where a different file system has b..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isdevdrive(path: int) -> int:
    """Mock: Return ``True`` if pathname *path* is located on a Windows Dev Drive. A Dev Drive is optimized for developer scenarios, ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isreserved(path: int) -> int:
    """Mock: Return ``True`` if *path* is a reserved pathname on the current system. On Windows, reserved filenames include those tha..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def join(a: int, b: int) -> int:
    """Mock: Join two path segments. `os.path.join` is variadic; this stub
    models the common two-argument case so demos can exercise it (a unary
    signature caused `int -> int applied to 2 arguments` in path_demo.py)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def normcase(path: int) -> int:
    """Mock: Normalize the case of a pathname.  On Windows, convert all characters in the pathname to lowercase, and also convert for..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def normpath(path: int) -> int:
    """Mock: Normalize a pathname by collapsing redundant separators and up-level references so that ``A//B``, ``A/B/``, ``A/./B`` an..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def realpath(path: int, strict: int) -> int:
    """Mock: Return the canonical path of the specified filename, eliminating any symbolic links encountered in the path (if they are..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def relpath(path: int, start: int) -> int:
    """Mock: Return a relative filepath to *path* either from the current directory or from an optional *start* directory.  This is a..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def samefile(path1: int, path2: int) -> int:
    """Mock: Return ``True`` if both pathname arguments refer to the same file or directory. This is determined by the device number ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def sameopenfile(fp1: int, fp2: int) -> int:
    """Mock: Return ``True`` if the file descriptors *fp1* and *fp2* refer to the same file. .. versionchanged:: 3.2 Added Windows su..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def samestat(stat1: int, stat2: int) -> int:
    """Mock: Return ``True`` if the stat tuples *stat1* and *stat2* refer to the same file. These structures may have been returned b..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def split(path: int) -> int:
    """Mock: Split the pathname *path* into a pair, ``(head, tail)`` where *tail* is the last pathname component and *head* is everyt..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def splitdrive(path: int) -> int:
    """Mock: Split the pathname *path* into a pair ``(drive, tail)`` where *drive* is either a mount point or the empty string.  On s..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def splitroot(path: int) -> int:
    """Mock: Split the pathname *path* into a 3-item tuple ``(drive, root, tail)`` where *drive* is a device name or mount point, *ro..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def splitext(path: int) -> int:
    """Mock: Split the pathname *path* into a pair ``(root, ext)``  such that ``root + ext == path``, and the extension, *ext*, is em..."""
    return 0
