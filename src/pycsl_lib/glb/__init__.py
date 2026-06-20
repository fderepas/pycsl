# pycsl_lib/glb — pure-Python glob module model
# Named 'glb' to avoid stdlib name clash.
#
# Contracts derived from library_reference/glob.rst.
# RST: "The glob module finds all the pathnames matching a specified
#  pattern according to the rules used by the Unix shell."
# RST: "glob(), iglob(), escape()"
#
# Model: glob returns a count of matches (non-negative).
# Actual path matching depends on filesystem state.


#@ requires pat >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def glob_count(pat: int) -> int:
    """RST: 'Return a list of pathnames that match pathname.'
    Zero or more matches."""
    return pat


#@ requires pat >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def iglob_count(pat: int) -> int:
    """RST: 'Return an iterator which yields the same values as glob().'
    Same count as glob."""
    return pat


#@ requires pathname >= 0
#@ ensures \result >= pathname
#@ assigns \nothing
def escape(pathname: int) -> int:
    """RST: 'Escape all special characters.' Result >= input
    (escaping adds backslashes)."""
    return pathname


#@ requires pat >= 0
#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def has_magic(pat: int) -> int:
    """Return 1 if pattern contains glob metacharacters."""
    if pat > 0:
        return 1
    return 0
