# Formal tests for pycsl_lib/gettext_stub — gettext module
from pycsl_lib.gettext_stub import gettext, ngettext


#@ ensures \result == "hello"
def test_gettext_identity() -> str:
    """gettext is identity (no translation)."""
    return gettext("hello")


def test_ngettext_returns_str() -> str:
    """ngettext returns a string."""
    return ngettext("one", "many", 1)
