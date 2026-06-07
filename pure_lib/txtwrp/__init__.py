# pure_lib/txtwrp — pure-Python textwrap module model
# Named 'txtwrp' to avoid stdlib name clash.
#
# Models wrap, fill, shorten, dedent, indent as string transforms.
# Body-proven for dedent and indent; contract-only for wrap/fill/shorten.


#@ requires width > 0
#@ requires text >= 0
#@ ensures \result >= 0
def wrap(text: int, width: int) -> int:
    """Wrap text to width. Returns number of lines (list length)."""
    if text == 0:
        return 0
    # At least 1 line, at most ceil(text/width) lines
    return (text + width - 1) // width


#@ requires width > 0
#@ requires text >= 0
#@ ensures \result >= 0
def fill(text: int, width: int) -> int:
    """Fill text to width. Returns total length of joined result."""
    return text


#@ requires width > 0
#@ requires text >= 0
#@ ensures \result >= 0
#@ ensures \result <= text
def shorten(text: int, width: int) -> int:
    """Shorten text to fit in width. Result <= original."""
    if text <= width:
        return text
    return width


#@ requires text >= 0
#@ ensures \result >= 0
#@ ensures \result <= text
def dedent(text: int) -> int:
    """Remove common leading whitespace. Result <= original length."""
    return text


#@ requires text >= 0
#@ requires prefix >= 0
#@ ensures \result >= text
def indent(text: int, prefix: int) -> int:
    """Add prefix to beginning of lines. Result >= original."""
    return text + prefix
