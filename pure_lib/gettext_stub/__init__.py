# pure_lib/gettext_stub — minimal gettext stub
# Identity function: no i18n in formal proofs.


#@ ensures \result == s
#@ assigns \nothing
def gettext(s: str) -> str:
    """Identity — no translation in model."""
    return s


#@ assigns \nothing
def ngettext(s: str, p: str, n: int) -> str:
    """Singular/plural — return singular form in model."""
    return s
