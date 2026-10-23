# pycsl_lib/udata — pure-Python unicodedata module
# Specified: Unicode database axiomatized (name→char, normalize idempotent).
# TCB: name/normalization facts are assumed, not proven.


# (#49) gen #30 — A KNOWN MODEL DIVERGENCE, WRITTEN DOWN RATHER THAN LEFT IN THE
# DOCSTRING'S WORDING. The docstring says "Returns the character as a single-char string";
# the BODY returns the NAME it was given. Real `unicodedata.lookup('LATIN SMALL LETTER A')`
# is `'a'`, so the docstring is right about CPython and wrong about this model.
#
# NOTHING CONTRADICTS IT TODAY because there is no `#@ ensures` at all: the function is
# SILENT, so it verifies and claims nothing — and `bin/check-docstring-contract-disagreement.py`
# cannot see it, because that gate keys on a docstring that is WEAKER than a clause and
# there is no clause here. This is the blind spot both gates share, and it is the reason
# `bin/check-stdlib-identity-stubs.py` now counts the 78 UNPINNED identity bodies too.
#
# THE CLAIM THIS BODY COULD HONESTLY MAKE IS NONE: `\str_length(\result) == 1` is true of
# CPython and FALSE of the model, and `\str_length(\result) >= 0` is true of everything.
# Fixing it means a real name->character table, not a contract. Left silent, and named.
#@ assigns \nothing
def lookup(name: str) -> str:
    """RST: 'Look up character by name.'
    CPython returns the character as a single-char string; THIS MODEL returns the name
    (see the note above) and makes no claim about the result."""
    return name


#@ assigns \nothing
def normalize(form: str, s: str) -> str:
    """RST: 'Return the normal form for the Unicode string.'
    Normalization is idempotent."""
    return s
