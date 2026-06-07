# Formal tests for pure_lib/url — urllib.parse module
from pure_lib.url import quote, unquote, urljoin


#@ requires length >= 0
#@ ensures \result >= length
def test_quote_nondecreasing(length: int) -> int:
    """quote never shrinks."""
    return quote(length)


#@ requires length >= 0
#@ ensures \result >= 0
def test_unquote_nonneg(length: int) -> int:
    """unquote returns non-negative."""
    return unquote(length)


#@ requires base >= 0
#@ requires rel >= 0
#@ ensures \result >= 0
def test_urljoin_nonneg(base: int, rel: int) -> int:
    """urljoin returns non-negative."""
    return urljoin(base, rel)
