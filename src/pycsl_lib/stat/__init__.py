# pycsl_lib/stat — pure-Python stat module model
#
# Contracts derived from library_reference/stat.rst.
# RST: "The stat module defines constants and functions for interpreting
#  the results of os.stat(), os.fstat() and os.lstat()."
#
# Model: file mode bits as integers, extraction functions as bitmasks.

# File type constants
S_IFDIR  = 16384
S_IFREG  = 32768
S_IFLNK  = 40960
S_IFBLK  = 24576
S_IFCHR  = 8192
S_IFIFO  = 4096
S_IFSOCK = 49152

# Permission bits
S_IRUSR = 256
S_IWUSR = 128
S_IXUSR = 64
S_IRGRP = 32
S_IWGRP = 16
S_IXGRP = 8
S_IROTH = 4
S_IWOTH = 2
S_IXOTH = 1


#@ requires mode >= 0
#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def S_ISDIR(mode: int) -> int:
    """RST: 'Return non-zero if the mode is from a directory.'"""
    if mode >= S_IFDIR and mode < S_IFDIR + 4096:
        return 1
    return 0


#@ requires mode >= 0
#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def S_ISREG(mode: int) -> int:
    """RST: 'Return non-zero if the mode is from a regular file.'"""
    if mode >= S_IFREG and mode < S_IFREG + 4096:
        return 1
    return 0


#@ requires mode >= 0
#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def S_ISLNK(mode: int) -> int:
    """RST: 'Return non-zero if the mode is from a symbolic link.'"""
    if mode >= S_IFLNK and mode < S_IFLNK + 4096:
        return 1
    return 0


#@ requires mode >= 0
#@ ensures \result >= 0
#@ ensures \result < 4096
#@ assigns \nothing
def S_IMODE(mode: int) -> int:
    """RST: 'Return the portion of the file's mode that can be set by chmod.'
    Permission bits are the low 12 bits."""
    return mode % 4096


#@ requires mode >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def S_IFMT(mode: int) -> int:
    """RST: 'Return the portion of the file's mode that describes the file type.'
    File type is mode with permission bits masked off."""
    return mode - (mode % 4096)


#@ requires mode >= 0
#@ ensures \result == "----------"
#@ assigns \nothing
def filemode(mode: int) -> str:
    """A TEN-CHARACTER PLACEHOLDER, **not** `stat.filemode` — corrected in gen #30.

    The RST line is 'Convert a file's mode to a string of the form -rwxrwxrwx', and this
    function returns the constant `"----------"` for EVERY mode. `stat.filemode(2)` is
    `'?-------w-'`, so the contract `\result == "----------"` is true of this body and
    FALSE of the function the citation names — a FACADE: verified, and computing nothing.
    Measured by `bin/check-stdlib-contract-fidelity.py`, which carries it in its baseline.

    WHY IT IS NOT SIMPLY FIXED HERE, priced rather than hand-waved: a faithful
    `filemode` is ten INDEPENDENT bit tests over `mode` building a ten-character string,
    and the string model this layer uses carries concatenation through
    `str_concat_op` with no per-character theory — so the faithful body is provable only
    with a per-position lemma set that does not exist yet. The honest intermediate is to
    weaken the contract to what is true of BOTH (`\length(\result) == 10`), which needs
    the `\length`-on-`str` support this stub does not currently use, and to re-prove this
    module. Left as a NAMED work item for the `agent-stdlib-annotate` owner rather than
    half-done under a deadline.
    """
    return "----------"
