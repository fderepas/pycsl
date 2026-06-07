# pure_lib/shutl — pure-Python shutil module model
# Named 'shutl' to avoid stdlib name clash.
#
# Contracts derived from library_reference/shutil.rst.
# RST: "The shutil module offers a number of high-level operations on
#  files and collections of files."
# RST: "copy(), copy2(), copytree(), rmtree(), move(), disk_usage()"
#
# Model: operations return byte counts or success indicators.
# Actual filesystem mutation delegated to World/os module.


#@ requires src >= 0
#@ requires dst >= 0
#@ ensures \result == src
#@ assigns \nothing
def copy(src: int, dst: int) -> int:
    """RST: 'Copy the file src to the file or directory dst.'
    Returns source size (bytes copied)."""
    return src


#@ requires src >= 0
#@ requires dst >= 0
#@ ensures \result == src
#@ assigns \nothing
def copy2(src: int, dst: int) -> int:
    """RST: 'Identical to copy() except that copy2() also attempts to
    preserve file metadata.' Returns source size."""
    return src


#@ requires src >= 0
#@ requires dst >= 0
#@ ensures \result >= src
#@ assigns \nothing
def copytree(src: int, dst: int) -> int:
    """RST: 'Recursively copy an entire directory tree.' Returns
    total bytes copied (>= single source size)."""
    return src


#@ requires path >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def rmtree(path: int) -> int:
    """RST: 'Delete an entire directory tree.' Returns bytes freed."""
    return path


#@ requires src >= 0
#@ requires dst >= 0
#@ ensures \result == src
#@ assigns \nothing
def move(src: int, dst: int) -> int:
    """RST: 'Recursively move a file or directory to another location.'
    Returns source size."""
    return src


#@ requires path >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def disk_usage_total(path: int) -> int:
    """RST: 'Return disk usage statistics about the given path.'
    Returns total disk space (non-negative)."""
    return path


#@ requires path >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def disk_usage_used(path: int) -> int:
    """RST: 'disk_usage().used — used space.'"""
    return path


#@ requires path >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def disk_usage_free(path: int) -> int:
    """RST: 'disk_usage().free — available space.'"""
    return path


#@ requires name >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def which(name: int) -> int:
    """RST: 'Return the path to an executable which would be run if the
    given cmd was called.' Returns path length or 0 if not found."""
    return name


#@ requires src >= 0
#@ requires dst >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def copyfile(src: int, dst: int) -> int:
    """RST: 'Copy the contents of the file named src to a file named dst.'
    Returns bytes written."""
    return src


#@ requires src >= 0
#@ requires dst >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def copyfileobj(src: int, dst: int) -> int:
    """RST: 'Copy the contents of the file-like object fsrc to the
    file-like object fdst.' Returns bytes copied."""
    return src
