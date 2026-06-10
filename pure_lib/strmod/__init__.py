# pure_lib/strmod — pure-Python `string` module model on REAL Python `str`.
# Named 'strmod' to avoid stdlib name clash.
#
# Faithfulness (no-more-int doctrine): a Python `str` is a real Why3 `string`
# (use string.String; \str_length is String.length), NEVER an int. No value is
# coerced to an integer for convenience. Every contract below is derived from a
# cited sentence of the CPython documentation and is SOUND-ONLY: we never assert
# a postcondition that is false on real strings.
#
# Spec source: test-suite/library_reference/string.rst
#   - capwords ~L985-993
#   - Template / substitute / safe_substitute / is_valid ~L843-880
#   - Formatter / format / format_field ~L99/L180/L321
#
# Two mechanisms are used:
#   * FAITHFUL-PROVABLE: a real body whose contract Why3/SMT discharges
#     (set_template, is_valid, format_field empty-spec identity).
#   * ABSTRACT-FAITHFUL: an arbitrary string transform (.split/.join/.replace/
#     case-conversion / $-substitution / format-spec interpretation) has NO
#     SMT-checkable body, so it is modelled as a `#@ \trusted` leaf emitting an
#     abstract `val` whose contract IS its ensures. Such contracts state ONLY
#     facts universally true of an arbitrary result string (length non-negative,
#     length non-growing for capwords, empty maps to empty).
#
# HONESTY NOTE (verified by SMT spike): the previous int-mock asserted
#   substitute:        \result == template + mapping
#   safe_substitute:   \result >= template
# These are FALSE on real strings ($-substitution is neither length-additive nor
# monotone — the monotone claim is SMT-Unknown). They are DROPPED, not ported.


#@ \trusted reviewer: python-stdlib
#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) <= \str_length(s)
#@ ensures s == "" ==> \result == ""
#@ assigns \nothing
def capwords(s: str, sep: str = None) -> str:
    """RST L985-993: 'Split the argument into words using str.split(),
    capitalize each word using str.capitalize(), and join the capitalized words
    using str.join(). If the optional second argument sep is absent or None,
    runs of whitespace characters are replaced by a single space and leading and
    trailing whitespace are removed ...'

    SOUND-ONLY contract: collapsing runs of whitespace to a single space and
    trimming can only shorten (never grow) the string, so
    \\str_length(\\result) <= \\str_length(s); the empty string has no words, so
    capwords("") == "". The word-by-word case-conversion and re-joining are an
    arbitrary string transform with no SMT-checkable model, so this is a trusted
    leaf (emits as an abstract `val` pinned by the contract above)."""
    return s


#@ \trusted reviewer: python-stdlib
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def template_substitute(t: str, mapping: dict) -> str:
    """RST L843-880: 'Performs the template substitution, returning a new
    string. mapping is any dictionary-like object with keys that match the
    placeholders in the template.'

    SOUND-ONLY contract: the result is a string, so its length is non-negative.
    The $-substitution maps each placeholder to its (arbitrary) value, which is
    neither length-additive nor monotone in the template, so NO stronger fact is
    SMT-modelable. Trusted leaf (abstract `val`)."""
    return t


#@ \trusted reviewer: python-stdlib
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def template_safe_substitute(t: str, mapping: dict) -> str:
    """RST L843-880: 'Like substitute(), except that if placeholders are missing
    from mapping and kwds, instead of raising a KeyError exception, the original
    placeholder will appear in the resulting string intact.'

    SOUND-ONLY contract: the result is a string, length non-negative. (The
    int-mock's \\result >= template is FALSE on real strings — DROPPED.) The
    content is an arbitrary substitution with no SMT-checkable model. Trusted
    leaf (abstract `val`)."""
    return t


#@ \trusted reviewer: python-stdlib
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def _format_field_nonempty(spec: str, v: str) -> str:
    """RST L321: a non-empty format specification typically modifies the result.
    The interpretation of a standard format specifier (fill/align/sign/width/
    precision/type) is an arbitrary string transform with no SMT-checkable
    model, so the non-empty branch is a trusted leaf (abstract `val`); the only
    sound fact is that the result is a string (length non-negative)."""
    return v


#@ requires \str_length(spec) >= 0
#@ ensures spec == "" ==> \result == v
#@ assigns \nothing
def format_field(spec: str, v: str) -> str:
    """RST L321: 'A general convention is that an empty format specification
    produces the same result as if you had called str() on the value.'

    FAITHFUL-PROVABLE: the empty-spec branch is the identity v == str(v) (the
    value is already a string here), proved by SMT; the non-empty branch
    delegates to the trusted `_format_field_nonempty` leaf. Written as a
    conditional expression (single tail return) so the str result flows through
    without an early-return."""
    return v if spec == "" else _format_field_nonempty(spec, v)


# --- Template class ---

""  # pycsl
class Template:
    """RST L843: 'The constructor takes a single argument which is the template
    string.' The single public data attribute is `template` (RST: 'Template
    instances also provide one public data attribute: template')."""

    def __init__(self):
        # Real `str` field (no integer length surrogate). The empty default has
        # no integer invariant to carry, so there is no class invariant.
        self.template: str = ""

    #@ ensures self.template == t
    #@ assigns self.template
    def set_template(self, t: str) -> None:
        """Set the template string. FAITHFUL-PROVABLE: after the assignment the
        field equals the argument (read-after-write), proved by SMT."""
        self.template = t

    #@ ensures \result == 1 or \result == 0
    #@ assigns \nothing
    def is_valid(self) -> bool:
        """RST L860+: 'is_valid() — Returns False if the template has invalid
        placeholders that will cause substitute() to raise ValueError.'

        FAITHFUL-PROVABLE (bool model = 0/1): the result is a boolean. The actual
        validity check parses the template for malformed $-placeholders (an
        arbitrary string scan, not SMT-modelable), so the proved fact is only
        that the result is a boolean; the constant body witnesses it."""
        return True

    #@ \trusted reviewer: python-stdlib
    #@ ensures \str_length(\result) >= 0
    #@ assigns \nothing
    def substitute(self, mapping: dict) -> str:
        """RST L843-880: 'Performs the template substitution, returning a new
        string.' SOUND-ONLY: result is a string (length non-negative). The
        int-mock's \\result == self._len + mapping is FALSE on real strings —
        DROPPED. Trusted leaf (abstract `val`)."""
        return self.template

    #@ \trusted reviewer: python-stdlib
    #@ ensures \str_length(\result) >= 0
    #@ assigns \nothing
    def safe_substitute(self, mapping: dict) -> str:
        """RST L843-880: 'Like substitute(), except ... the original placeholder
        will appear in the resulting string intact.' SOUND-ONLY: result is a
        string (length non-negative). The int-mock's \\result >= self._len is
        FALSE on real strings — DROPPED. Trusted leaf (abstract `val`)."""
        return self.template


# --- Formatter class ---

""  # pycsl
class Formatter:
    """RST L99: 'The Formatter class ... allows you to create and customize your
    own string formatting behaviors using the same implementation as the
    built-in str.format() method.'"""

    #@ requires \str_length(spec) >= 0
    #@ ensures spec == "" ==> \result == v
    #@ assigns \nothing
    def format_field(self, v: str, spec: str) -> str:
        """RST L321 + L180: 'format_field() simply calls the global format()
        built-in.' Empty format specification produces str(value).

        FAITHFUL-PROVABLE: empty-spec branch is the identity; non-empty branch
        delegates to the trusted `_format_field_nonempty` leaf. (Argument order
        is (value, format_spec), matching the RST `format_field(value,
        format_spec)` signature.)"""
        return v if spec == "" else _format_field_nonempty(spec, v)

    #@ \trusted reviewer: python-stdlib
    #@ ensures \str_length(\result) >= 0
    #@ assigns \nothing
    def format(self, fmt: str) -> str:
        """RST L180: 'format(format_string, /, *args, **kwargs) — The primary API
        method. It takes a format string and an arbitrary set of positional and
        keyword arguments.' SOUND-ONLY: result is a string (length
        non-negative). The full format-string interpretation is an arbitrary
        string transform with no SMT-checkable model. Trusted leaf (abstract
        `val`)."""
        return fmt
