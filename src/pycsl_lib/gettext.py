"""PyCSL mock for Python's gettext module — Multilingual internationalization services."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def bindtextdomain(domain: int, localedir: int) -> int:
    """Mock: Bind the *domain* to the locale directory *localedir*.  More concretely, :mod:`!gettext` will look for binary :file:`.mo..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def textdomain(domain: int) -> int:
    """Mock: Change or query the current global domain.  If *domain* is ``None``, then the current global domain is returned, otherwi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettext(message: int) -> int:
    """Mock: Return the localized translation of *message*, based on the current global domain, language, and locale directory.  This..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dgettext(domain: int, message: int) -> int:
    """Mock: Like :func:`.gettext`, but look the message up in the specified *domain*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ngettext(singular: int, plural: int, n: int) -> int:
    """Mock: Like :func:`.gettext`, but consider plural forms. If a translation is found, apply the plural formula to *n*, and return..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dngettext(domain: int, singular: int, plural: int, n: int) -> int:
    """Mock: Like :func:`ngettext`, but look the message up in the specified *domain*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pgettext(context: int, message: int) -> int:
    """Mock: Mock: pgettext"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dpgettext(domain: int, context: int, message: int) -> int:
    """Mock: Mock: dpgettext"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def npgettext(context: int, singular: int, plural: int, n: int) -> int:
    """Mock: Mock: npgettext"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dnpgettext(domain: int, context: int, singular: int, plural: int, n: int) -> int:
    """Mock: Similar to the corresponding functions without the ``p`` in the prefix (that is, :func:`gettext`, :func:`dgettext`, :fun..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def find(domain: int, localedir: int, languages: int, all: int) -> int:
    """Mock: This function implements the standard :file:`.mo` file search algorithm.  It takes a *domain*, identical to what :func:`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def translation(domain: int, localedir: int, languages: int, class_: int, fallback: int) -> int:
    """Mock: Return a ``*Translations`` instance based on the *domain*, *localedir*, and *languages*, which are first passed to :func..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def install(domain: int, localedir: int, names: int) -> int:
    """Mock: This installs the function :func:`!_` in Python's builtins namespace, based on *domain* and *localedir* which are passed..."""
    return 0
