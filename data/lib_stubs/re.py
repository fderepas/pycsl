"""PyCSL mock for Python's re module.

Provides trusted stubs for regular expression operations.
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

# ── Module-level functions ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def compile(pattern: int, flags: int) -> int:
    """Mock: compile a regular expression pattern."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def search(pattern: int, string: int, flags: int) -> int:
    """Mock: search for pattern in string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def prefixmatch(pattern: int, string: int, flags: int) -> int:
    """Mock: match pattern at start of string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def match(pattern: int, string: int, flags: int) -> int:
    """Mock: match pattern at beginning of string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fullmatch(pattern: int, string: int, flags: int) -> int:
    """Mock: match pattern against entire string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def split(pattern: int, string: int, maxsplit: int, flags: int) -> int:
    """Mock: split string by pattern occurrences."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def findall(pattern: int, string: int, flags: int) -> int:
    """Mock: find all non-overlapping matches."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def finditer(pattern: int, string: int, flags: int) -> int:
    """Mock: return iterator of all matches."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sub(pattern: int, repl: int, string: int, count: int, flags: int) -> int:
    """Mock: substitute pattern matches in string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def subn(pattern: int, repl: int, string: int, count: int, flags: int) -> int:
    """Mock: substitute and return (new_string, count)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def escape(pattern: int) -> int:
    """Mock: escape special characters in pattern."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def purge() -> int:
    """Mock: clear the regular expression cache."""
    return 0

# ── Pattern object methods ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Pattern_search(self: int, string: int, pos: int, endpos: int) -> int:
    """Mock: Pattern.search — scan for first match."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_prefixmatch(self: int, string: int, pos: int, endpos: int) -> int:
    """Mock: Pattern.prefixmatch — match at start."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_match(self: int, string: int, pos: int, endpos: int) -> int:
    """Mock: Pattern.match — match at beginning."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_fullmatch(self: int, string: int, pos: int, endpos: int) -> int:
    """Mock: Pattern.fullmatch — match entire string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_split(self: int, string: int, maxsplit: int) -> int:
    """Mock: Pattern.split — split string by pattern."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_findall(self: int, string: int, pos: int, endpos: int) -> int:
    """Mock: Pattern.findall — find all matches."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_finditer(self: int, string: int, pos: int, endpos: int) -> int:
    """Mock: Pattern.finditer — iterate over all matches."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_sub(self: int, repl: int, string: int, count: int) -> int:
    """Mock: Pattern.sub — substitute matches."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_subn(self: int, repl: int, string: int, count: int) -> int:
    """Mock: Pattern.subn — substitute and return count."""
    return 0

# ── Pattern object attributes ──────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Pattern_flags(self: int) -> int:
    """Mock: Pattern.flags — regex matching flags."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_groups(self: int) -> int:
    """Mock: Pattern.groups — number of capturing groups."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_groupindex(self: int) -> int:
    """Mock: Pattern.groupindex — symbolic group name mapping."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Pattern_pattern(self: int) -> int:
    """Mock: Pattern.pattern — the pattern string."""
    return 0

# ── Match object methods ───────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Match_expand(self: int, template: int) -> int:
    """Mock: Match.expand — backslash substitution on template."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_group(self: int, group1: int) -> int:
    """Mock: Match.group — return one or more subgroups."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match___getitem__(self: int, g: int) -> int:
    """Mock: Match.__getitem__ — index access to groups."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_groups(self: int, default: int) -> int:
    """Mock: Match.groups — return all subgroups as tuple."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_groupdict(self: int, default: int) -> int:
    """Mock: Match.groupdict — return dict of named subgroups."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_start(self: int, group: int) -> int:
    """Mock: Match.start — start index of matched group."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_end(self: int, group: int) -> int:
    """Mock: Match.end — end index of matched group."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_span(self: int, group: int) -> int:
    """Mock: Match.span — (start, end) tuple of matched group."""
    return 0

# ── Match object attributes ────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Match_pos(self: int) -> int:
    """Mock: Match.pos — start index passed to search/match."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_endpos(self: int) -> int:
    """Mock: Match.endpos — end index passed to search/match."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_lastindex(self: int) -> int:
    """Mock: Match.lastindex — index of last matched group."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_lastgroup(self: int) -> int:
    """Mock: Match.lastgroup — name of last matched group."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_re(self: int) -> int:
    """Mock: Match.re — the regex object that produced this match."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Match_string(self: int) -> int:
    """Mock: Match.string — the string passed to search/match."""
    return 0
