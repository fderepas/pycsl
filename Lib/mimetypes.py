"""PyCSL mock for Python's mimetypes module — Mapping of filename extensions to MIME types."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def guess_type(url: int, strict: int) -> int:
    """Mock: .. index:: pair: MIME; headers Guess the type of a file based on its filename, path or URL, given by *url*. URL can be a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def guess_file_type(path: int, strict: int) -> int:
    """Mock: .. index:: pair: MIME; headers Guess the type of a file based on its path, given by *path*. Similar to the :func:`guess_..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def guess_all_extensions(type_: int, strict: int) -> int:
    """Mock: Guess the extensions for a file based on its MIME type, given by *type*. The return value is a list of strings giving al..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def guess_extension(type_: int, strict: int) -> int:
    """Mock: Guess the extension for a file based on its MIME type, given by *type*. The return value is a string giving a filename e..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def init(files: int) -> int:
    """Mock: Initialize the internal data structures.  If given, *files* must be a sequence of file names which should be used to aug..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def read_mime_types(filename: int) -> int:
    """Mock: Load the type map given in the file *filename*, if it exists.  The type map is returned as a dictionary mapping filename..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def add_type(type_: int, ext: int, strict: int) -> int:
    """Mock: Add a mapping from the MIME type *type* to the extension *ext*. When the extension is already known, the new type will r..."""
    return 0
