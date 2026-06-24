"""Pure Python os.path — string-only path operations.

Implements the subset of os.path used by pycsl: abspath, basename, dirname,
exists, expanduser, isdir, isfile, join, splitext. All operations work on
path strings; no real filesystem access is performed (exists/isdir/isfile
always return False since there is no filesystem binding).
"""

sep = '/'


#@ \abstract
#@ assigns \nothing
# TOOL GAP: calls normpath (\abstract) — absoluteness of the result is
# unpinnable. Body discarded for verification (zero-TCB val). Logged GAP.
def abspath(path: str) -> str:
    """Return normalized absolute path. Prepends '/' if not absolute."""
    if not path:
        return '/'
    if path[0] != '/':
        path = '/' + path
    return normpath(path)


#@ assigns \nothing
# gap-1 (os.path string ops) — Strategy A: pure-Python reimplementation with a
# tail-scan loop using PyCSL-supported string primitives (len, path[i], slicing).
# Replaces `path.rfind('/')` (which lowered to an opaque no-contract val). The
# loop scans from the end and records the FIRST '/' encountered (== rfind's
# result); returns the suffix after it, or `path` if no '/' is present.
#@ ensures \str_length(\result) <= \str_length(path)
def basename(path: str) -> str:
    """Return the final component of a pathname."""
    n = len(path)
    i = n - 1
    found = -1
    #@ loop invariant -1 <= found
    #@ loop invariant -1 <= i and i <= n - 1
    #@ loop variant i + 1
    while i >= 0:
        if path[i] == '/' and found == -1:
            found = i
        i = i - 1
    if found < 0:
        return path
    return path[found + 1:]


#@ assigns \nothing
# gap-1 (os.path string ops) — Strategy A: pure-Python tail-scan loop replacing
# `path.rfind('/')`. Returns the prefix before the last '/', '/' if the last '/'
# is at index 0, or '' if no '/' is present.
#@ ensures \str_length(\result) <= \str_length(path)
def dirname(path: str) -> str:
    """Return the directory component of a pathname."""
    n = len(path)
    i = n - 1
    found = -1
    #@ loop invariant -1 <= found and found <= n - 1
    #@ loop invariant -1 <= i and i <= n - 1
    #@ loop variant i + 1
    while i >= 0:
        if path[i] == '/' and found == -1:
            found = i
        i = i - 1
    if found < 0:
        return ''
    if found == 0:
        return '/'
    return path[:found]


#@ assigns \nothing
#@ ensures \result == 0
#@ interface ensures \result == 0
def exists(path: str) -> bool:
    """Check if path exists. Always False (no filesystem binding)."""
    return False


#@ assigns \nothing
#@ ensures \result == path
#@ interface ensures \result == path
def expanduser(path: str) -> str:
    """Expand ~ to home directory. Returns path unchanged (no home binding)."""
    return path


#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
#@ ensures (\str_length(path) > 0 and \str_sub(path, 0, 1) == "/") ==> \result == 1
#@ ensures \str_length(path) == 0 ==> \result == 0
#@ interface ensures \result == 0 or \result == 1
#@ interface ensures (\str_length(path) > 0 and \str_sub(path, 0, 1) == "/") ==> \result == 1
#@ interface ensures \str_length(path) == 0 ==> \result == 0
def isabs(path: str) -> bool:
    """Return True if path is absolute."""
    return len(path) > 0 and path[0] == '/'


#@ assigns \nothing
#@ ensures \result == 0
#@ interface ensures \result == 0
def isdir(path: str) -> bool:
    """Check if path is a directory. Always False (no filesystem binding)."""
    return False


#@ assigns \nothing
#@ ensures \result == 0
#@ interface ensures \result == 0
def isfile(path: str) -> bool:
    """Check if path is a regular file. Always False (no filesystem binding)."""
    return False


#@ assigns \nothing
# gap-1 (os.path string ops) — Strategy A: the variadic `*parts` signature
# lowered to an opaque int iterator (iter_get returns int), emitting a
# WhyML string+int type error. Replaced with a BINARY `join(a, b)` (no
# variadic), body-verified with PyCSL-supported string primitives (len,
# indexing, +). The semantics mirror the original two-component case: an
# absolute `b` replaces `a`; otherwise `a` + '/' + `b` (with the separator
# elided when `a` is empty or already ends in '/').
#@ ensures \str_length(\result) >= \str_length(b)
#@ ensures \str_length(\result) <= \str_length(a) + \str_length(b) + 1
def join(a: str, b: str) -> str:
    """Join two path components with '/'.

    If `b` is absolute, it replaces `a`. If `a` is empty or ends in '/',
    `b` is appended directly; otherwise a '/' separator is inserted.
    """
    if len(b) > 0 and b[0] == '/':
        return b
    if len(a) == 0:
        return b
    if a[len(a) - 1] == '/':
        return a + b
    return a + '/' + b


#@ \abstract
#@ assigns \nothing
# TOOL GAP: `path.split('/')` and `'/'.join(...)` lower to opaque abstract
# vals (path_split_1 / join_1) with no contracts, and the `..` resolution
# loop over the split result cannot be proven. Body discarded for
# verification (zero-TCB val). Runtime body retained. Logged GAP.
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


#@ \abstract
#@ assigns \nothing
# TOOL GAP: `base.rfind('.')` lowers to opaque base_rfind_1, AND a
# string-tuple return `(str, str)` is not inferred by PyCSL (tuple component
# type defaults to int — `return (path, '')` emits "expression has type
# (string, string), expected (int, int)"). Both block body verification.
# Body discarded for verification (zero-TCB val). Logged GAP.
def splitext(path: str) -> tuple:
    """Split path into (root, ext). ext includes the leading dot."""
    base = basename(path)
    i = base.rfind('.')
    if i <= 0:
        return (path, '')
    dir_part = path[:len(path) - len(base)]
    return (dir_part + base[:i], base[i:])
