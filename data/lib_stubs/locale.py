"""PyCSL mock for Python's locale module."""
_ = 0  # anchor

#@ \trusted
def setlocale(category: int, loc: str) -> str:
    """Mock: sets or queries the locale."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def localeconv() -> int:
    """Mock: returns locale conventions — opaque dict."""
    return 0

#@ \trusted
def nl_langinfo(option: int) -> str:
    """Mock: returns locale information string."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def getdefaultlocale() -> int:
    """Mock: returns default locale — opaque tuple."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getlocale(category: int) -> int:
    """Mock: returns current locale — opaque tuple."""
    return 0

#@ \trusted
def getpreferredencoding(do_setlocale: int) -> str:
    """Mock: returns preferred encoding."""
    return ""

#@ \trusted
def getencoding() -> str:
    """Mock: returns current encoding."""
    return ""

#@ \trusted
def normalize(localename: str) -> str:
    """Mock: normalizes locale name."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def strcoll(s1: str, s2: str) -> int:
    """Mock: compares two strings using locale — returns >= 0."""
    return 0

#@ \trusted
def strxfrm(s: str) -> str:
    """Mock: transforms string for locale-aware comparison."""
    return ""

#@ \trusted
def format_string(fmt: str, v: int, grouping: int) -> str:
    """Mock: formats a string with locale settings."""
    return ""

#@ \trusted
def currency(v: int, symbol: int, grouping: int) -> str:
    """Mock: formats a currency value."""
    return ""

#@ \trusted
def str(f: int) -> str:
    """Mock: formats a float with locale settings."""
    return ""

#@ \trusted
def delocalize(s: str) -> str:
    """Mock: removes locale-specific formatting."""
    return ""

#@ \trusted
def localize(s: str, grouping: int) -> str:
    """Mock: adds locale-specific grouping."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def atof(s: str) -> int:
    """Mock: converts locale-formatted string to float — opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def atoi(s: str) -> int:
    """Mock: converts locale-formatted string to integer."""
    return 0

#@ \trusted
def gettext(msg: str) -> str:
    """Mock: translates message."""
    return ""

#@ \trusted
def dgettext(domain: str, msg: str) -> str:
    """Mock: translates message in domain."""
    return ""

#@ \trusted
def dcgettext(domain: str, msg: str, category: int) -> str:
    """Mock: translates message in domain with category."""
    return ""

#@ \trusted
def textdomain(domain: str) -> str:
    """Mock: sets or queries text domain."""
    return ""

#@ \trusted
def bindtextdomain(domain: str, d: str) -> str:
    """Mock: binds text domain to directory."""
    return ""

#@ \trusted
def bind_textdomain_codeset(domain: str, codeset: str) -> str:
    """Mock: sets codeset for text domain."""
    return ""
