"""PyCSL mock for Python's email.utils module — Miscellaneous email package utilities."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def localtime(dt: int) -> int:
    """Mock: Return local time as an aware datetime object.  If called without arguments, return current time.  Otherwise *dt* argume..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_msgid(idstring: int, domain: int) -> int:
    """Mock: Returns a string suitable for an :rfc:`2822`\ -compliant :mailheader:`Message-ID` header.  Optional *idstring* if given,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def quote(str: int) -> int:
    """Mock: Return a new string with backslashes in *str* replaced by two backslashes, and double quotes replaced by backslash-doubl..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unquote(str: int) -> int:
    """Mock: Return a new string which is an *unquoted* version of *str*. If *str* ends and begins with double quotes, they are strip..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def parseaddr(address: int, strict: int) -> int:
    """Mock: Parse address -- which should be the value of some address-containing field such as :mailheader:`To` or :mailheader:`Cc`..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def formataddr(pair: int, charset: int) -> int:
    """Mock: The inverse of :meth:`parseaddr`, this takes a 2-tuple of the form ``(realname, email_address)`` and returns the string ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def getaddresses(fieldvalues: int, strict: int) -> int:
    """Mock: This method returns a list of 2-tuples of the form returned by ``parseaddr()``. *fieldvalues* is a sequence of header fi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parsedate(date: int) -> int:
    """Mock: Attempts to parse a date according to the rules in :rfc:`2822`. however, some mailers don't follow that format as specif..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parsedate_tz(date: int) -> int:
    """Mock: Performs the same function as :func:`parsedate`, but returns either ``None`` or a 10-tuple; the first 9 elements make up..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parsedate_to_datetime(date: int) -> int:
    """Mock: The inverse of :func:`format_datetime`.  Performs the same function as :func:`parsedate`, but on success returns a :mod:..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mktime_tz(tuple: int) -> int:
    """Mock: Turn a 10-tuple as returned by :func:`parsedate_tz` into a UTC timestamp (seconds since the Epoch).  If the timezone ite..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def formatdate(timeval: int, localtime: int, usegmt: int) -> int:
    """Mock: Returns a date string as per :rfc:`2822`, e.g.:: Fri, 09 Nov 2001 01:08:47 -0000 Optional *timeval* if given is a floati..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def format_datetime(dt: int, usegmt: int) -> int:
    """Mock: Like ``formatdate``, but the input is a :mod:`datetime` instance.  If it is a naive datetime, it is assumed to be 'UTC w..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decode_rfc2231(s: int) -> int:
    """Mock: Decode the string *s* according to :rfc:`2231`."""
    return 0

#@ \trusted
#@ ensures \result == 0
def encode_rfc2231(s: int, charset: int, language: int) -> int:
    """Mock: Encode the string *s* according to :rfc:`2231`.  Optional *charset* and *language*, if given is the character set name a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def collapse_rfc2231_value(value: int, errors: int, fallback_charset: int) -> int:
    """Mock: When a header parameter is encoded in :rfc:`2231` format, :meth:`Message.get_param <email.message.Message.get_param>` ma..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decode_params(params: int) -> int:
    """Mock: Decode parameters list according to :rfc:`2231`.  *params* is a sequence of 2-tuples containing elements of the form ``(..."""
    return 0
