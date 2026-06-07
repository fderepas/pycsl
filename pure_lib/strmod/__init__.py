# pure_lib/strmod — pure-Python string module model
# Named 'strmod' to avoid stdlib name clash.
#
# Models string.capwords and Template basics.
# capwords is body-proven; Template is contract-only.


#@ requires s >= 0
#@ ensures \result >= 0
#@ ensures \result <= s
def capwords(s: int) -> int:
    """Capitalize words in string s.
    Model: result length <= input (split+capitalize+join preserves or shrinks)."""
    return s


#@ requires template >= 0
#@ requires mapping >= 0
#@ ensures \result >= 0
def template_substitute(template: int, mapping: int) -> int:
    """Substitute $-variables in template string.
    Model: result depends on template + mapping sizes."""
    return template + mapping


#@ requires template >= 0
#@ requires mapping >= 0
#@ ensures \result >= 0
def template_safe_substitute(template: int, mapping: int) -> int:
    """Like substitute but leaves unresolved $-variables intact.
    Model: result >= template (unresolved vars stay as-is)."""
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
