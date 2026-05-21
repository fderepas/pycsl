"""PyCSL mock for Python's textwrap module — Text wrapping and filling."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def wrap(text: int, width: int, initial_indent: int, __subsequent_indent: int, expand_tabs: int, __replace_whitespace: int, fix_sentence_endings: int) -> int:
    """Mock: Wraps the single paragraph in *text* (a string) so every line is at most *width* characters long.  Returns a list of out..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def fill(text: int, width: int, initial_indent: int, __subsequent_indent: int, expand_tabs: int, __replace_whitespace: int, fix_sentence_endings: int) -> int:
    """Mock: Wraps the single paragraph in *text*, and returns a single string containing the wrapped paragraph.  :func:`fill` is sho..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shorten(text: int, width: int, fix_sentence_endings: int, __break_long_words: int, break_on_hyphens: int, __placeholder: int) -> int:
    """Mock: Collapse and truncate the given *text* to fit in the given *width*. First the whitespace in *text* is collapsed (all whi..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def dedent(text: int) -> int:
    """Mock: Remove any common leading whitespace from every line in *text*. This can be used to make triple-quoted strings line up w..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def indent(text: int, prefix: int, predicate_: int) -> int:
    """Mock: Add *prefix* to the beginning of selected lines in *text*. Lines are separated by calling ``text.splitlines(True)``. By ..."""
    return 0
