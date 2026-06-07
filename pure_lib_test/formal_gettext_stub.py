# Formal tests for pure_lib/gettext_stub — gettext module
from pure_lib.gettext_stub import gettext, ngettext


#@ requires s >= 0
#@ ensures \result == s
def test_gettext_identity(s: int) -> int:
    """gettext is identity (no translation)."""
    return gettext(s)


#@ requires s >= 0
#@ ensures \result >= 0
def test_ngettext_nonneg(s: int) -> int:
    """ngettext returns non-negative."""
    return ngettext(s, 0, 1)
