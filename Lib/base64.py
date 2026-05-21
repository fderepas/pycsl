"""PyCSL mock for Python's base64 module — RFC 4648: Base16, Base32, Base64 Data Encodings;."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def b64encode(s: int, altchars: int, padded: int, wrapcol: int) -> int:
    """Mock: Encode the :term:`bytes-like object` *s* using Base64 and return the encoded :class:`bytes`. Optional *altchars* must be..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b64decode(s: int, altchars: int, validate: int, padded: int, canonical: int) -> int:
    """Mock: Decode the Base64 encoded :term:`bytes-like object` or ASCII string *s* and return the decoded :class:`bytes`. Optional ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def standard_b64encode(s: int) -> int:
    """Mock: Encode :term:`bytes-like object` *s* using the standard Base64 alphabet and return the encoded :class:`bytes`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def standard_b64decode(s: int) -> int:
    """Mock: Decode :term:`bytes-like object` or ASCII string *s* using the standard Base64 alphabet and return the decoded :class:`b..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urlsafe_b64encode(s: int, padded: int) -> int:
    """Mock: Encode :term:`bytes-like object` *s* using the URL- and filesystem-safe alphabet, which substitutes ``-`` instead of ``+..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urlsafe_b64decode(s: int, padded: int) -> int:
    """Mock: Decode :term:`bytes-like object` or ASCII string *s* using the URL- and filesystem-safe alphabet, which substitutes ``-`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b32encode(s: int, padded: int, wrapcol: int) -> int:
    """Mock: Encode the :term:`bytes-like object` *s* using Base32 and return the encoded :class:`bytes`. If *padded* is true (defaul..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b32decode(s: int, casefold: int, map01: int, padded: int, ignorechars: int, canonical: int) -> int:
    """Mock: Decode the Base32 encoded :term:`bytes-like object` or ASCII string *s* and return the decoded :class:`bytes`. Optional ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b32hexencode(s: int, padded: int, wrapcol: int) -> int:
    """Mock: Similar to :func:`b32encode` but uses the Extended Hex Alphabet, as defined in :rfc:`4648`. .. versionadded:: 3.10 .. ve..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b32hexdecode(s: int, casefold: int, padded: int, ignorechars: int, canonical: int) -> int:
    """Mock: Similar to :func:`b32decode` but uses the Extended Hex Alphabet, as defined in :rfc:`4648`. This version does not allow ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b16encode(s: int, wrapcol: int) -> int:
    """Mock: Encode the :term:`bytes-like object` *s* using Base16 and return the encoded :class:`bytes`. If *wrapcol* is non-zero, i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b16decode(s: int, casefold: int, ignorechars: int) -> int:
    """Mock: Decode the Base16 encoded :term:`bytes-like object` or ASCII string *s* and return the decoded :class:`bytes`. Optional ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def a85encode(b: int, foldspaces: int, wrapcol: int, pad: int, adobe: int) -> int:
    """Mock: Encode the :term:`bytes-like object` *b* using Ascii85 and return the encoded :class:`bytes`. *foldspaces* is an optiona..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def a85decode(b: int, foldspaces: int, adobe: int, ignorechars: int, canonical: int) -> int:
    """Mock: Decode the Ascii85 encoded :term:`bytes-like object` or ASCII string *b* and return the decoded :class:`bytes`. *foldspa..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b85encode(b: int, pad: int, wrapcol: int) -> int:
    """Mock: Encode the :term:`bytes-like object` *b* using base85 (as used in e.g. git-style binary diffs) and return the encoded :c..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b85decode(b: int, ignorechars: int, canonical: int) -> int:
    """Mock: Decode the base85-encoded :term:`bytes-like object` or ASCII string *b* and return the decoded :class:`bytes`. *ignorech..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def z85encode(s: int, pad: int, wrapcol: int) -> int:
    """Mock: Encode the :term:`bytes-like object` *s* using Z85 (as used in ZeroMQ) and return the encoded :class:`bytes`. The input ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def z85decode(s: int, ignorechars: int, canonical: int) -> int:
    """Mock: Decode the Z85-encoded :term:`bytes-like object` or ASCII string *s* and return the decoded :class:`bytes`. *ignorechars..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def decode(input: int, output: int) -> int:
    """Mock: Decode the contents of the binary *input* file and write the resulting binary data to the *output* file. *input* and *ou..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decodebytes(s: int) -> int:
    """Mock: Decode the :term:`bytes-like object` *s*, which must contain one or more lines of base64 encoded data, and return the de..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def encode(input: int, output: int) -> int:
    """Mock: Encode the contents of the binary *input* file and write the resulting base64 encoded data to the *output* file. *input*..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def encodebytes(s: int) -> int:
    """Mock: Encode the :term:`bytes-like object` *s*, which can contain arbitrary binary data, and return :class:`bytes` containing ..."""
    return 0
