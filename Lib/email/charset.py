"""PyCSL mock for Python's email.charset module — Character Sets."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def add_charset(charset: int, header_enc: int, body_enc: int, output_charset: int) -> int:
    """Mock: Add character properties to the global registry. *charset* is the input character set, and must be the canonical name of..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def add_alias(alias_: int, canonical: int) -> int:
    """Mock: Add a character set alias.  *alias* is the alias name, e.g. ``latin-1``. *canonical* is the character set's canonical na..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def add_codec(charset: int, codecname: int) -> int:
    """Mock: Add a codec that map characters in the given character set to and from Unicode. *charset* is the canonical name of a cha..."""
    return 0
