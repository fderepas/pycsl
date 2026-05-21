"""PyCSL mock for Python's locale module — Internationalization services."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def setlocale(category: int, locale: int) -> int:
    """Mock: If *locale* is given and not ``None``, :func:`setlocale` modifies the locale setting for the *category*. The available c..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def localeconv() -> int:
    """Mock: Returns the database of the local conventions as a dictionary. This dictionary has the following strings as keys: .. tab..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nl_langinfo(option: int) -> int:
    """Mock: Return some locale-specific information as a string.  This function is not available on all systems, and the set of poss..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getdefaultlocale(envvars: int) -> int:
    """Mock: Tries to determine the default locale settings and returns them as a tuple of the form ``(language code, encoding)``. Ac..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getlocale(category: int) -> int:
    """Mock: Returns the current setting for the given locale category as a tuple containing the language code and encoding. *categor..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpreferredencoding(do_setlocale: int) -> int:
    """Mock: Return the :term:`locale encoding` used for text data, according to user preferences.  User preferences are expressed di..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getencoding() -> int:
    """Mock: Get the current :term:`locale encoding`: * On Android and VxWorks, return ``'utf-8'``. * On Unix, return the encoding of..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def normalize(localename: int) -> int:
    """Mock: Returns a normalized locale code for the given locale name.  The returned locale code is formatted for use with :func:`s..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def strcoll(string1: int, string2: int) -> int:
    """Mock: Compares two strings according to the current :const:`LC_COLLATE` setting. As any other compare function, returns a nega..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def strxfrm(string: int) -> int:
    """Mock: Transforms a string to one that can be used in locale-aware comparisons.  For example, ``strxfrm(s1) < strxfrm(s2)`` is ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def format_string(format: int, val_: int, grouping: int, monetary: int) -> int:
    """Mock: Formats a number *val* according to the current :const:`LC_NUMERIC` setting. The format follows the conventions of the `..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def currency(val_: int, symbol: int, grouping: int, international: int) -> int:
    """Mock: Formats a number *val* according to the current :const:`LC_MONETARY` settings. The returned string includes the currency..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def str(float: int) -> int:
    """Mock: Formats a floating-point number using the same format as the built-in function ``str(float)``, but takes the decimal poi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def delocalize(string: int) -> int:
    """Mock: Converts a string into a normalized number string, following the :const:`LC_NUMERIC` settings. .. versionadded:: 3.5"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def localize(string: int, grouping: int, monetary: int) -> int:
    """Mock: Converts a normalized number string into a formatted string following the :const:`LC_NUMERIC` settings. .. versionadded:..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def atof(string: int, func: int) -> int:
    """Mock: Converts a string to a number, following the :const:`LC_NUMERIC` settings, by calling *func* on the result of calling :f..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def atoi(string: int) -> int:
    """Mock: Converts a string to an integer, following the :const:`LC_NUMERIC` conventions."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettext(msg: int) -> int:
    """Mock: Mock: gettext"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dgettext(domain: int, msg: int) -> int:
    """Mock: Mock: dgettext"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dcgettext(domain: int, msg: int, category: int) -> int:
    """Mock: Mock: dcgettext"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def textdomain(domain: int) -> int:
    """Mock: Mock: textdomain"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bindtextdomain(domain: int, dir: int) -> int:
    """Mock: Mock: bindtextdomain"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bind_textdomain_codeset(domain: int, codeset: int) -> int:
    """Mock: Mock: bind_textdomain_codeset"""
    return 0
