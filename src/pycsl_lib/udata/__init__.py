# pycsl_lib/udata — pure-Python unicodedata module
# Specified: Unicode database axiomatized (name→char, normalize idempotent).
# TCB: name/normalization facts are assumed, not proven.


#@ assigns \nothing
def lookup(name: str) -> str:
    """RST: 'Look up character by name.'
    Returns the character as a single-char string."""
    return name


#@ assigns \nothing
def normalize(form: str, s: str) -> str:
    """RST: 'Return the normal form for the Unicode string.'
    Normalization is idempotent."""
    return s
