"""PyCSL mock for Python's textwrap module.

Provides trusted stubs for text wrapping and filling.
"""
_ = 0  # anchor

# ── Module-level functions ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def wrap(text: int, width: int, initial_indent: int, subsequent_indent: int, expand_tabs: int, replace_whitespace: int, fix_sentence_endings: int, break_long_words: int, drop_whitespace: int, break_on_hyphens: int, tabsize: int, max_lines: int, placeholder: int) -> int:
    """Mock: wrap text into a list of lines."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fill(text: int, width: int, initial_indent: int, subsequent_indent: int, expand_tabs: int, replace_whitespace: int, fix_sentence_endings: int, break_long_words: int, drop_whitespace: int, break_on_hyphens: int, tabsize: int, max_lines: int, placeholder: int) -> int:
    """Mock: wrap text and return a single filled string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shorten(text: int, width: int, fix_sentence_endings: int, break_long_words: int, break_on_hyphens: int, placeholder: int) -> int:
    """Mock: collapse and truncate text to fit a given width."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dedent(text: int) -> int:
    """Mock: remove common leading whitespace from all lines."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def indent(text: int, prefix: int, pred_fn: int) -> int:
    """Mock: add prefix to the beginning of selected lines."""
    return 0

# ── TextWrapper constructor ─────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def TextWrapper(width: int, expand_tabs: int, tabsize: int, replace_whitespace: int, drop_whitespace: int, initial_indent: int, subsequent_indent: int, fix_sentence_endings: int, break_long_words: int, break_on_hyphens: int, max_lines: int, placeholder: int) -> int:
    """Mock: create a TextWrapper instance — opaque."""
    return 0

# ── TextWrapper methods ─────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_wrap(self: int, text: int) -> int:
    """Mock: TextWrapper.wrap — wrap text into a list of lines."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_fill(self: int, text: int) -> int:
    """Mock: TextWrapper.fill — wrap text and return a single string."""
    return 0

# ── TextWrapper attributes ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_width(self: int) -> int:
    """Mock: TextWrapper.width — maximum line length."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_expand_tabs(self: int) -> int:
    """Mock: TextWrapper.expand_tabs — expand tab characters."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_tabsize(self: int) -> int:
    """Mock: TextWrapper.tabsize — tab stop spacing."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_replace_whitespace(self: int) -> int:
    """Mock: TextWrapper.replace_whitespace — replace whitespace chars."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_drop_whitespace(self: int) -> int:
    """Mock: TextWrapper.drop_whitespace — drop leading/trailing whitespace."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_initial_indent(self: int) -> int:
    """Mock: TextWrapper.initial_indent — prefix for first line."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_subsequent_indent(self: int) -> int:
    """Mock: TextWrapper.subsequent_indent — prefix for subsequent lines."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_fix_sentence_endings(self: int) -> int:
    """Mock: TextWrapper.fix_sentence_endings — ensure two-space sentence gaps."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_break_long_words(self: int) -> int:
    """Mock: TextWrapper.break_long_words — break words exceeding width."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_break_on_hyphens(self: int) -> int:
    """Mock: TextWrapper.break_on_hyphens — break at hyphens in compound words."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_max_lines(self: int) -> int:
    """Mock: TextWrapper.max_lines — maximum number of output lines."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TextWrapper_placeholder(self: int) -> int:
    """Mock: TextWrapper.placeholder — truncation indicator string."""
    return 0
