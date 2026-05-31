"""PyCSL mock for Python's re module.

Provides trusted stubs for regular expression operations.
Match and Pattern objects are modelled as classes with invariants.
"""
_ = 0  # anchor

# ── Flags ────────────────────────────────────────────────────────────

A = 0
ASCII = 0
DEBUG = 0
I = 0
IGNORECASE = 0
L = 0
LOCALE = 0
M = 0
MULTILINE = 0
NOFLAG = 0
S = 0
DOTALL = 0
U = 0
UNICODE = 0
X = 0
VERBOSE = 0

# ── MatchObj class ──────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._pos >= 0
#@ class invariant self._endpos >= self._pos
#@ class invariant self._lastindex >= 0
class MatchObj:
    def __init__(self):
        self._pos = 0
        self._endpos = 0
        self._lastindex = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def expand(self, template: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def group(self, group1: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def groups(self, default: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def groupdict(self, default: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= self._pos
    #@ assigns \nothing
    def start(self, grp: int) -> int:
        return self._pos

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= self._pos
    #@ assigns \nothing
    def end(self, grp: int) -> int:
        return self._endpos

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def span(self, grp: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._pos
    #@ assigns \nothing
    def pos(self) -> int:
        return self._pos

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._endpos
    #@ assigns \nothing
    def endpos(self) -> int:
        return self._endpos

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._lastindex
    #@ assigns \nothing
    def lastindex(self) -> int:
        return self._lastindex

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def lastgroup(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def re(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def string(self) -> int:
        return 0

# ── PatternObj class ────────────────────────────────────────────────

#@ class invariant self._groups >= 0
#@ class invariant self._flags >= 0
class PatternObj:
    def __init__(self):
        self._groups = 0
        self._flags = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def search(self, string: int, pos: int, endpos: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def match(self, string: int, pos: int, endpos: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def fullmatch(self, string: int, pos: int, endpos: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def split(self, string: int, maxsplit: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def findall(self, string: int, pos: int, endpos: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def finditer(self, string: int, pos: int, endpos: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def sub(self, repl: int, string: int, count: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def subn(self, repl: int, string: int, count: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._flags
    #@ assigns \nothing
    def flags(self) -> int:
        return self._flags

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._groups
    #@ assigns \nothing
    def ngroups(self) -> int:
        return self._groups

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def groupindex(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def pattern(self) -> int:
        return 0

# ── Module-level functions ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def compile(pattern: int, flags: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def search(pattern: int, string: int, flags: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def re_match(pattern: int, string: int, flags: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def fullmatch(pattern: int, string: int, flags: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def split(pattern: int, string: int, maxsplit: int, flags: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def findall(pattern: int, string: int, flags: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def finditer(pattern: int, string: int, flags: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sub(pattern: int, repl: int, string: int, count: int, flags: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def subn(pattern: int, repl: int, string: int, count: int, flags: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def escape(pattern: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def purge() -> int:
    return 0
