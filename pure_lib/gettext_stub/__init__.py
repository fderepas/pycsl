# pure_lib/gettext_stub — minimal gettext stub
# Identity function: no i18n in formal proofs.


#@ requires s >= 0
#@ ensures \result == s
def gettext(s: int) -> int:
    """Identity — no translation in model."""
    return s


#@ requires s >= 0
#@ ensures \result == s
def ngettext(s: int, p: int, n: int) -> int:
    """Singular/plural — return singular form in model."""
    return s
