# pure_lib/strmod — pure-Python string module model
# Named 'strmod' to avoid stdlib name clash.
#
# Contracts derived from library_reference/string.rst.
# RST: "Split the argument into words using str.split(), capitalize each word
#  using str.capitalize(), and join the capitalized words using str.join()."


#@ requires s >= 0
#@ ensures \result >= 0
#@ ensures \result <= s
#@ ensures s == 0 ==> \result == 0
def capwords(s: int) -> int:
    """RST: 'Split into words, capitalize each word, and join.'
    Split+join may remove duplicate whitespace → result <= input.
    Empty input → empty output."""
    return s


#@ requires template >= 0
#@ requires mapping >= 0
#@ ensures \result >= 0
#@ ensures template == 0 ==> \result == mapping
def template_substitute(template: int, mapping: int) -> int:
    """RST: 'The substitute() method substitutes $-variables.'
    Empty template with mapping produces just the mapping values."""
    return template + mapping


#@ requires template >= 0
#@ requires mapping >= 0
#@ ensures \result >= 0
#@ ensures \result >= template
def template_safe_substitute(template: int, mapping: int) -> int:
    """RST: 'Like substitute() but leaves unresolved $-variables intact.'
    Result >= template (unresolved vars stay, resolved ones may grow)."""
    return template + mapping


#@ requires fmt >= 0
#@ requires val >= 0
#@ ensures \result >= 0
def format_field(fmt: int, val: int) -> int:
    """Format a single field value.
    Model: result is non-negative length."""
    if fmt == 0:
        return val
    return fmt + val
