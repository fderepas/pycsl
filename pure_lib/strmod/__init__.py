# pure_lib/strmod — pure-Python string module model
# Named 'strmod' to avoid stdlib name clash.
#
# Contracts derived from library_reference/string.rst.
# RST: "Split the argument into words using str.split(), capitalize each word
#  using str.capitalize(), and join the capitalized words using str.join()."
# RST: "The Formatter class... format strings."
# RST: "Template class for $-substitutions."


#@ requires s >= 0
#@ ensures \result >= 0
#@ ensures \result <= s
#@ ensures s == 0 ==> \result == 0
def capwords(s: int) -> int:
    """RST: 'Split into words, capitalize each word, and join.'
    Split+join may remove duplicate whitespace -> result <= input.
    Empty input -> empty output."""
    return s


#@ requires template >= 0
#@ requires mapping >= 0
#@ ensures \result >= 0
#@ ensures \result == template + mapping
def template_substitute(template: int, mapping: int) -> int:
    """RST: 'The substitute() method substitutes $-variables.'
    Empty template with mapping produces just the mapping values."""
    return template + mapping


#@ requires template >= 0
#@ requires mapping >= 0
#@ ensures \result >= 0
#@ ensures \result >= template
#@ ensures \result == template + mapping
def template_safe_substitute(template: int, mapping: int) -> int:
    """RST: 'Like substitute() but leaves unresolved $-variables intact.'
    Result >= template (unresolved vars stay, resolved ones may grow)."""
    return template + mapping


#@ requires fmt >= 0
#@ requires val >= 0
#@ ensures \result >= 0
#@ ensures fmt == 0 ==> \result == val
#@ ensures fmt > 0 ==> \result == fmt + val
def format_field(fmt: int, val: int) -> int:
    """Format a single field value.
    Model: result is non-negative length."""
    if fmt == 0:
        return val
    return fmt + val


# --- Template class ---

""  # pycsl
#@ class invariant self._len >= 0
class Template:
    """RST: 'The class takes a template string as its constructor argument.'"""

    def __init__(self):
        self._len = 0

    #@ requires n >= 0
    #@ ensures self._len == n
    #@ assigns self._len
    def set_template(self, n: int) -> None:
        """Set the template string length."""
        self._len = n

    #@ requires mapping >= 0
    #@ ensures \result >= 0
    #@ ensures \result == self._len + mapping
    #@ assigns \nothing
    def substitute(self, mapping: int) -> int:
        """RST: 'Performs substitution, returning a new string.'"""
        return self._len + mapping

    #@ requires mapping >= 0
    #@ ensures \result >= self._len
    #@ ensures \result == self._len + mapping
    #@ assigns \nothing
    def safe_substitute(self, mapping: int) -> int:
        """RST: 'Like substitute(), except placeholders are kept.'"""
        return self._len + mapping

    #@ ensures \result == 1 or \result == 0
    #@ assigns \nothing
    def is_valid(self) -> int:
        """RST: 'Returns false if the template has invalid placeholders.'"""
        return 1


# --- Formatter class ---

""  # pycsl
#@ class invariant self._depth >= 0
class Formatter:
    """RST: 'The Formatter class has format_field, get_value, etc.'"""

    def __init__(self):
        self._depth = 0

    #@ requires fmt >= 0
    #@ requires val >= 0
    #@ ensures \result >= 0
    #@ assigns \nothing
    def format_field(self, fmt: int, val: int) -> int:
        """RST: 'format_field() simply calls the global format() built-in.'"""
        return fmt + val

    #@ requires fmt >= 0
    #@ ensures \result >= 0
    #@ assigns \nothing
    def format(self, fmt: int) -> int:
        """RST: 'The primary API method. Takes a format string.'"""
        return fmt
