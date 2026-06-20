"""PyCSL mock for Python's gettext module — Multilingual internationalization services."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/gettext.html#gettext.bindtextdomain
#@ requires True
#@ ensures True
def bindtextdomain(domain: int, localedir: int) -> int:
    """Mock: Bind the *domain* to the locale directory *localedir*.  More concretely, :mod:`!gettext` will look for binary :file:`.mo..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/locale.html#locale.textdomain
#@ requires True
#@ ensures True
def textdomain(domain: int) -> int:
    """Mock: Change or query the current global domain.  If *domain* is ``None``, then the current global domain is returned, otherwi..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/gettext.html#gettext.gettext
#@ requires True
#@ ensures True
def gettext(message: int) -> int:
    """Mock: Return the localized translation of *message*, based on the current global domain, language, and locale directory.  This..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/gettext.html#gettext.dgettext
#@ requires True
#@ ensures True
def dgettext(domain: int, message: int) -> int:
    """Mock: Like :func:`.gettext`, but look the message up in the specified *domain*."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/gettext.py
#@ requires True
#@ ensures True
def ngettext(singular: int, plural: int, n: int) -> int:
    """Mock: Like :func:`.gettext`, but consider plural forms. If a translation is found, apply the plural formula to *n*, and return..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/gettext.py
#@ requires True
#@ ensures True
def dngettext(domain: int, singular: int, plural: int, n: int) -> int:
    """Mock: Like :func:`ngettext`, but look the message up in the specified *domain*."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/gettext.py
#@ requires True
#@ ensures True
def pgettext(context: int, message: int) -> int:
    """Mock: Mock: pgettext"""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/gettext.py
#@ requires True
#@ ensures True
def dpgettext(domain: int, context: int, message: int) -> int:
    """Mock: Mock: dpgettext"""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/gettext.py
#@ requires True
#@ ensures True
def npgettext(context: int, singular: int, plural: int, n: int) -> int:
    """Mock: Mock: npgettext"""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/gettext.py
#@ requires True
#@ ensures True
def dnpgettext(domain: int, context: int, singular: int, plural: int, n: int) -> int:
    """Mock: Similar to the corresponding functions without the ``p`` in the prefix (that is, :func:`gettext`, :func:`dgettext`, :fun..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/gettext.py
#@ requires True
#@ ensures True
def find(domain: int, localedir: int, languages: int, all: int) -> int:
    """Mock: This function implements the standard :file:`.mo` file search algorithm.  It takes a *domain*, identical to what :func:`..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/gettext.py
#@ requires True
#@ ensures True
def translation(domain: int, localedir: int, languages: int, class_: int, fallback: int) -> int:
    """Mock: Return a ``*Translations`` instance based on the *domain*, *localedir*, and *languages*, which are first passed to :func..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/gettext.html#gettext.install
#@ requires True
#@ ensures True
def install(domain: int, localedir: int, names: int) -> int:
    """Mock: This installs the function :func:`!_` in Python's builtins namespace, based on *domain* and *localedir* which are passed..."""
    return 0
