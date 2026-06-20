"""PyCSL mock for Python's unicodedata module — Access the Unicode Database."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def lookup(name: int) -> int:
    """Mock: Look up character by name.  If a character with the given name is found, return the corresponding character.  If not fou..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def name(chr: int, default: int) -> int:
    """Mock: Returns the name assigned to the character *chr* as a string. If no name is defined, *default* is returned, or, if not g..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decimal(chr: int, default: int) -> int:
    """Mock: Returns the decimal value assigned to the character *chr* as integer. If no such value is defined, *default* is returned..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def digit(chr: int, default: int) -> int:
    """Mock: Returns the digit value assigned to the character *chr* as integer. If no such value is defined, *default* is returned, ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def numeric(chr: int, default: int) -> int:
    """Mock: Returns the numeric value assigned to the character *chr* as float. If no such value is defined, *default* is returned, ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def category(chr: int) -> int:
    """Mock: Returns the general category assigned to the character *chr* as string. General category names consist of two letters. S..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bidirectional(chr: int) -> int:
    """Mock: Returns the bidirectional class assigned to the character *chr* as string. If no such value is defined, an empty string ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def combining(chr: int) -> int:
    """Mock: Returns the canonical combining class assigned to the character *chr* as integer. Returns ``0`` if no combining class is..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def east_asian_width(chr: int) -> int:
    """Mock: Returns the east asian width assigned to the character *chr* as string. For a list of widths and or more information, se..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def block(chr: int) -> int:
    """Mock: Returns the `block <https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/#G64189>`_ assigned to the charac..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mirrored(chr: int) -> int:
    """Mock: Returns the mirrored property assigned to the character *chr* as integer. Returns ``1`` if the character has been identi..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isxidstart(chr: int) -> int:
    """Mock: Return ``True`` if *chr* is a valid identifier start per the `Unicode Standard Annex #31 <https://www.unicode.org/report..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isxidcontinue(chr: int) -> int:
    """Mock: Return ``True`` if *chr* is a valid identifier character per the `Unicode Standard Annex #31 <https://www.unicode.org/re..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decomposition(chr: int) -> int:
    """Mock: Returns the character decomposition mapping assigned to the character *chr* as string. An empty string is returned in ca..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def grapheme_cluster_break(chr: int) -> int:
    """Mock: Returns the Grapheme_Cluster_Break property assigned to the character. .. versionadded:: 3.15"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def indic_conjunct_break(chr: int) -> int:
    """Mock: Returns the Indic_Conjunct_Break property assigned to the character. .. versionadded:: 3.15"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def extended_pictographic(chr: int) -> int:
    """Mock: Returns ``True`` if the character has the Extended_Pictographic property, ``False`` otherwise. .. versionadded:: 3.15"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def normalize(form: int, unistr: int) -> int:
    """Mock: Return the normal form *form* for the Unicode string *unistr*. Valid values for *form* are 'NFC', 'NFKC', 'NFD', and 'NF..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_normalized(form: int, unistr: int) -> int:
    """Mock: Return whether the Unicode string *unistr* is in the normal form *form*. Valid values for *form* are 'NFC', 'NFKC', 'NFD..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iter_graphemes(unistr: int, start: int, end_: int) -> int:
    """Mock: Returns an iterator to iterate over grapheme clusters. With optional *start*, iteration begins at that position. With op..."""
    return 0
