# Pure model for urllib.parse — URL parsing
# Models as component-length based parsing.


#@ requires url_len >= 0
#@ ensures \result >= 0
#@ ensures \result <= url_len
def urlparse_scheme(url_len: int) -> int:
    """Extract scheme component length from URL."""
    return 0


#@ requires url_len >= 0
#@ ensures \result >= 0
#@ ensures \result <= url_len
def urlparse_netloc(url_len: int) -> int:
    """Extract netloc component length from URL."""
    return 0


#@ requires url_len >= 0
#@ ensures \result >= 0
#@ ensures \result <= url_len
def urlparse_path(url_len: int) -> int:
    """Extract path component length from URL."""
    return url_len


#@ requires base_len >= 0
#@ requires rel_len >= 0
#@ ensures \result >= 0
def urljoin(base_len: int, rel_len: int) -> int:
    """Join base URL with relative URL."""
    return base_len + rel_len


#@ requires length >= 0
#@ ensures \result >= length
def quote(length: int) -> int:
    """Percent-encode special chars. Output >= input."""
    return length


#@ requires length >= 0
#@ ensures \result >= 0
#@ ensures \result <= length
def unquote(length: int) -> int:
    """Decode percent-encoded chars. Output <= input."""
    return length


#@ requires query_len >= 0
#@ ensures \result >= 0
def parse_qs(query_len: int) -> int:
    """Parse query string. Returns number of key-value pairs."""
    return 0
