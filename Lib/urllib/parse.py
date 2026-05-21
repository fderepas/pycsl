"""PyCSL mock for Python's urllib.parse module — Parse URLs into or assemble them from components."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def urlsplit(urlstring: int, scheme: int, allow_fragments: int, missing_as_none: int) -> int:
    """Mock: Parse a URL into five components, returning a 5-item :term:`named tuple` :class:`SplitResult` or :class:`SplitResultByte..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parse_qs(qs: int, keep_blank_values: int, strict_parsing: int, encoding: int, errors: int, max_num_fields: int, separator: int) -> int:
    """Mock: Parse a query string given as a string argument (data of type :mimetype:`application/x-www-form-urlencoded`).  Data are ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parse_qsl(qs: int, keep_blank_values: int, strict_parsing: int, encoding: int, errors: int, max_num_fields: int, separator: int) -> int:
    """Mock: Parse a query string given as a string argument (data of type :mimetype:`application/x-www-form-urlencoded`).  Data are ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urlunsplit(parts: int) -> int:
    """Mock: Construct a URL from a tuple as returned by :func:`urlsplit`. The *parts* argument can be any five-item iterable. This m..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urlparse(urlstring: int, scheme: int, allow_fragments: int, missing_as_none: int) -> int:
    """Mock: This is similar to :func:`urlsplit`, but additionally splits the *path* component on *path* and *params*. This function ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urlunparse(parts: int) -> int:
    """Mock: Combine the elements of a tuple as returned by :func:`urlparse` into a complete URL as a string. The *parts* argument ca..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urljoin(base: int, url: int, allow_fragments: int) -> int:
    """Mock: Construct a full ('absolute') URL by combining a 'base URL' (*base*) with another URL (*url*).  Informally, this uses co..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urldefrag(url: int, missing_as_none: int) -> int:
    """Mock: If *url* contains a fragment identifier, return a modified version of *url* with no fragment identifier, and the fragmen..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unwrap(url: int) -> int:
    """Mock: Extract the url from a wrapped URL (that is, a string formatted as ``<URL:scheme://host/path>``, ``<scheme://host/path>`..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def quote(string: int, safe: int, encoding: int, errors: int) -> int:
    """Mock: Replace special characters in *string* using the :samp:`%{xx}` escape. Letters, digits, and the characters ``'_.-~'`` ar..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def quote_plus(string: int, safe: int, encoding: int, errors: int) -> int:
    """Mock: Like :func:`quote`, but also replace spaces with plus signs, as required for quoting HTML form values when building up a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def quote_from_bytes(bytes: int, safe: int) -> int:
    """Mock: Like :func:`quote`, but accepts a :class:`bytes` object rather than a :class:`str`, and does not perform string-to-bytes..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unquote(string: int, encoding: int, errors: int) -> int:
    """Mock: Replace :samp:`%{xx}` escapes with their single-character equivalent. The optional *encoding* and *errors* parameters sp..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unquote_plus(string: int, encoding: int, errors: int) -> int:
    """Mock: Like :func:`unquote`, but also replace plus signs with spaces, as required for unquoting HTML form values. *string* must..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unquote_to_bytes(string: int) -> int:
    """Mock: Replace :samp:`%{xx}` escapes with their single-octet equivalent, and return a :class:`bytes` object. *string* may be ei..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def urlencode(query: int, doseq: int, safe: int, encoding: int, __errors: int, quote_via: int) -> int:
    """Mock: Convert a mapping object or a sequence of two-element tuples, which may contain :class:`str` or :class:`bytes` objects, ..."""
    return 0
