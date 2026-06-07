# pure_lib/txtwrp — pure-Python textwrap module model
# Named 'txtwrp' to avoid stdlib name clash.
#
# Models wrap, fill, shorten, dedent, indent as string transforms.
# Contracts derived from library_reference/textwrap.rst.


#@ requires width > 0
#@ requires text >= 0
#@ ensures \result >= 0
#@ ensures text == 0 ==> \result == 0
#@ ensures text > 0 ==> \result >= 1
#@ ensures text > 0 ==> \result == (text + width - 1) // width
def wrap(text: int, width: int) -> int:
    """Wrap text to width. Returns number of lines (list length).
    RST: 'Returns a list of output lines' — empty text → empty list,
    non-empty text → at least one line."""
    if text == 0:
        return 0
    return (text + width - 1) // width


#@ requires width > 0
#@ requires text >= 0
#@ ensures \result >= 0
#@ ensures text == 0 ==> \result == 0
def fill(text: int, width: int) -> int:
    """Fill text to width. Returns total length of joined result.
    RST: 'shorthand for join(wrap(text))' — empty text → empty string."""
    return text


#@ requires width > 0
#@ requires text >= 0
#@ ensures \result >= 0
#@ ensures \result <= text
#@ ensures \result <= width
#@ ensures text <= width ==> \result == text
#@ ensures text > width ==> \result == width
def shorten(text: int, width: int) -> int:
    """Shorten text to fit in width.
    RST: 'Collapse and truncate the given text to fit in the given width.'
    Result fits in width AND is at most original length."""
    if text <= width:
        return text
    return width


#@ requires text >= 0
#@ ensures \result >= 0
#@ ensures \result <= text
def dedent(text: int) -> int:
    """Remove common leading whitespace.
    RST: 'Remove any common leading whitespace from every line.'
    Result ≤ original (whitespace removed, never added)."""
    return text


#@ requires text >= 0
#@ requires prefix >= 0
#@ ensures \result >= text
#@ ensures \result == text + prefix
def indent(text: int, prefix: int) -> int:
    """Add prefix to beginning of lines.
    RST: 'Add prefix to the beginning of selected lines.'
    Result ≥ original (prefix added, never removed)."""
    return text + prefix
