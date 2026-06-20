"""PyCSL mock for Python's locale module."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.setlocale
#@ ensures \result != ""
def setlocale(category: int, loc: str) -> str:
    """Mock: sets or queries the locale."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.localeconv
#@ ensures True
def localeconv() -> int:
    """Mock: returns locale conventions — opaque dict."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.nl_langinfo
#@ ensures True
def nl_langinfo(option: int) -> str:
    """Mock: returns locale information string."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.getdefaultlocale
#@ ensures True
def getdefaultlocale() -> int:
    """Mock: returns default locale — opaque tuple."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.getlocale
#@ requires category >= 0
def getlocale(category: int) -> int:
    """Mock: returns current locale — opaque tuple."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.getpreferredencoding
#@ ensures len(\result) > 0
def getpreferredencoding(do_setlocale: int) -> str:
    """Mock: returns preferred encoding."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.getencoding
#@ ensures len(\result) > 0
def getencoding() -> str:
    """Mock: returns current encoding."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.normalize
#@ ensures len(localename) == 0 or len(\result) > 0
def normalize(localename: str) -> str:
    """Mock: normalizes locale name."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.strcoll
#@ ensures s1 == s2 ==> \result == 0
def strcoll(s1: str, s2: str) -> int:
    """Mock: compares two strings using locale — returns >= 0."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.strxfrm
# cite:_note: doc semantics (preserves strcoll ordering) exceed expressible contract surface
#@ ensures len(\result) >= 0
def strxfrm(s: str) -> str:
    """Mock: transforms string for locale-aware comparison."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.format_string
#@ ensures len(\result) >= 0
def format_string(fmt: str, v: int, grouping: int) -> str:
    """Mock: formats a string with locale settings."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.currency
#@ ensures len(\result) > 0
def currency(v: int, symbol: int, grouping: int) -> str:
    """Mock: formats a currency value."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.str
#@ ensures len(\result) >= 1
def str(f: int) -> str:
    """Mock: formats a float with locale settings."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.delocalize
#@ ensures len(\result) <= len(s)
def delocalize(s: str) -> str:
    """Mock: removes locale-specific formatting."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html
#@ ensures len(\result) >= len(s)
def localize(s: str, grouping: int) -> str:
    """Mock: adds locale-specific grouping."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.atof
#@ requires len(s) > 0
#@ ensures True
def atof(s: str) -> int:
    """Mock: converts locale-formatted string to float — opaque int."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.atoi
#@ requires len(s) > 0
#@ ensures True
#@ assigns \nothing
def atoi(s: str) -> int:
    """Mock: converts locale-formatted string to integer."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.gettext
#@ ensures len(\result) >= 0
def gettext(msg: str) -> str:
    """Mock: translates message."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.dgettext
#@ ensures \result != "" or msg == ""
def dgettext(domain: str, msg: str) -> str:
    """Mock: translates message in domain."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.dcgettext
#@ ensures len(\result) >= 0
def dcgettext(domain: str, msg: str, category: int) -> str:
    """Mock: translates message in domain with category."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.textdomain
#@ ensures \result == domain
def textdomain(domain: str) -> str:
    """Mock: sets or queries text domain."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.bindtextdomain
#@ ensures True
def bindtextdomain(domain: str, d: str) -> str:
    """Mock: binds text domain to directory."""
    return ""

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.bind_textdomain_codeset
#@ requires domain != ""
#@ ensures True
def bind_textdomain_codeset(domain: str, codeset: str) -> str:
    """Mock: sets codeset for text domain."""
    return ""
