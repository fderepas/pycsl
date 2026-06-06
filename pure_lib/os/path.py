"""Pure Python os.path — string-only path operations.

Implements the subset of os.path used by pycsl: abspath, basename, dirname,
exists, expanduser, isdir, isfile, join, splitext. All operations work on
path strings; no real filesystem access is performed (exists/isdir/isfile
always return False since there is no filesystem binding).
"""

sep = '/'


def abspath(path: str) -> str:
    """Return normalized absolute path. Prepends '/' if not absolute."""
    if not path:
        return '/'
    if path[0] != '/':
        path = '/' + path
    return normpath(path)


def basename(path: str) -> str:
    """Return the final component of a pathname."""
    i = path.rfind('/')
    if i < 0:
        return path
    return path[i + 1:]


def dirname(path: str) -> str:
    """Return the directory component of a pathname."""
    i = path.rfind('/')
    if i < 0:
        return ''
    if i == 0:
        return '/'
    return path[:i]


def exists(path: str) -> bool:
    """Check if path exists. Always False (no filesystem binding)."""
    return False


def expanduser(path: str) -> str:
    """Expand ~ to home directory. Returns path unchanged (no home binding)."""
    return path


def isabs(path: str) -> bool:
    """Return True if path is absolute."""
    return len(path) > 0 and path[0] == '/'


def isdir(path: str) -> bool:
    """Check if path is a directory. Always False (no filesystem binding)."""
    return False


def isfile(path: str) -> bool:
    """Check if path is a regular file. Always False (no filesystem binding)."""
    return False


def join(a: str, *parts: str) -> str:
    """Join path components with '/'.

    If a component is absolute, it replaces everything before it.
    """
    result = a
    for p in parts:
        if p and p[0] == '/':
            result = p
        elif not result or result[-1] == '/':
            result = result + p
        else:
            result = result + '/' + p
    return result


def normpath(path: str) -> str:
    """Normalize path: collapse '//', '/./', and resolve '..' components."""
    if not path:
        return '.'
    absolute = path[0] == '/'
    parts = path.split('/')
    normalized = []
    for part in parts:
        if part == '' or part == '.':
            continue
        if part == '..':
            if normalized and normalized[-1] != '..':
                normalized.pop()
            elif not absolute:
                normalized.append('..')
        else:
            normalized.append(part)
    result = '/'.join(normalized)
    if absolute:
        result = '/' + result
    if not result:
        return '/' if absolute else '.'
    return result


def splitext(path: str) -> tuple:
    """Split path into (root, ext). ext includes the leading dot."""
    base = basename(path)
    i = base.rfind('.')
    if i <= 0:
        return (path, '')
    dir_part = path[:len(path) - len(base)]
    return (dir_part + base[:i], base[i:])
