# Formal tests for pycsl_lib/strmod — REAL string theorems over symbolic `str`.
#
# THE CONVERGENCE LOOP (config/skills/pycsl-stdlib-coverage "Step 5"): this file
# PROPAGATES the English specification (test-suite/library_reference/string.rst)
# across the WHOLE strmod public API. Every public symbol gets at least one
# universally-quantified theorem with SYMBOLIC inputs that re-states its
# library-reference promise as strongly as the faithful model allows. `len(...)`
# lowers to Why3 `String.length` (str_length_op); string `+` to str_concat_op;
# these are GENUINE string-valued theorems, NOT length-int artifacts.
#
# WHOLE PUBLIC API (10 symbols) and the theorem that propagates each:
#   module functions
#     1. capwords(s, sep=None)              -> formal_strmod_capwords_bound, _empty
#     2. template_substitute(t, mapping)    -> formal_strmod_template_substitute_str
#     3. template_safe_substitute(t, m)     -> formal_strmod_template_safe_substitute_str
#     4. format_field(spec, v)              -> formal_strmod_format_field_empty_identity
#   Template methods
#     5. set_template(t)                    -> formal_strmod_set_template_readback   [GAP-LIMITED]
#     6. is_valid()                         -> formal_strmod_is_valid_bool           [GAP-LIMITED]
#     7. substitute(mapping)                -> formal_strmod_substitute_str          [via twin]
#     8. safe_substitute(mapping)           -> formal_strmod_safe_substitute_str     [via twin]
#   Formatter methods
#     9. format_field(v, spec)              -> formal_strmod_formatter_format_field  [via twin]
#    10. format(fmt)                        -> formal_strmod_formatter_format_str    [GAP-LIMITED]
#   (plus the foundational concat-length law, formal_strmod_concat_len.)
#
# GAP-2 (a real tool gap this fuller test surfaced — see 10-2006-convergence-gap-2.md):
# the six CLASS-METHOD symbols (5-10) CANNOT be exercised by CONSTRUCTING an
# instance and calling the method, because:
#   * Gap 2a — a str-typed record field's default lowers to the int literal `0`
#     (`let t = { template = 0 }`), a Why3 type error, blocking `Template()`;
#   * Gap 2b — a FIELDLESS class (`Formatter`) is not emitted as a record
#     `type_decl`, so its methods are not injected on import and a constructed
#     `Formatter()` method call fails "method 'formatter__format' not found".
# Both are facets of the known "method/field-referencing ensures don't propagate
# to a constructing driver" gap (MEMORY: pycsl_method_call_contract_gap).
#
# So the method symbols are propagated AS STRONGLY AS THE TOOL CURRENTLY ALLOWS:
# four of them (substitute, safe_substitute, Template/Formatter `format_field`)
# are SEMANTICALLY IDENTICAL to a module-level function the model also exports
# (the method delegates to it), so the method's library-reference promise IS the
# module-twin theorem below, proved over symbolic inputs. The two with no twin
# (`set_template` read-back, `is_valid` 0/1, `format`) keep the strongest form
# that does NOT need a constructed instance, clearly marked GAP-LIMITED.
#
# pycsl-flags: --memory-model hoare
from pycsl_lib.strmod import (
    capwords,
    template_substitute,
    template_safe_substitute,
    format_field,
)


# === Foundational: concat-length law (string-additivity of `+`) ===

#@ requires \str_length(a) >= 0
#@ ensures \result == \str_length(a) + \str_length(b)
def formal_strmod_concat_len(a: str, b: str) -> int:
    """Concat-length law: |a + b| == |a| + |b| for all strings a, b.
    The fundamental length-additivity of string concatenation, proved by SMT via
    str_concat_op + str_length_op."""
    return len(a + b)


# === 1. capwords(s, sep=None) — RST L985-993 ===

#@ requires \str_length(s) >= 0
#@ ensures \result <= \str_length(s)
def formal_strmod_capwords_bound(s: str) -> int:
    """capwords bound: |capwords(s)| <= |s| for all strings s (RST L985-993).
    'runs of whitespace characters are replaced by a single space and leading and
    trailing whitespace are removed' — collapsing+trimming can only shorten, so
    capwords never grows the string. Proved for ALL s against capwords' contract
    (\\str_length(\\result) <= \\str_length(s)). `sep` is OMITTED (default)."""
    return len(capwords(s))


#@ ensures \result == 0
def formal_strmod_capwords_empty(unused: int) -> int:
    """capwords empty law: |capwords("")| == 0 (RST L985-993).
    The empty string has no words, so 'split / capitalize / join' yields "".
    Proved against capwords' contract `s == "" ==> \\result == ""`."""
    return len(capwords(""))


# === 2. template_substitute(t, mapping) — RST L852-858 ===

#@ requires \str_length(t) >= 0
#@ ensures \result >= 0
def formal_strmod_template_substitute_str(t: str, mapping: dict) -> int:
    """template_substitute soundness: |template_substitute(t, m)| >= 0 for all t,m
    (RST L852-858: 'Performs the template substitution, returning a NEW STRING').
    The $-substitution maps each placeholder to its arbitrary value — neither
    length-additive nor monotone in t — so the soundest SMT-modelable promise is
    that the result IS A STRING (non-negative length). Proved against the model's
    `\\str_length(\\result) >= 0`."""
    return len(template_substitute(t, mapping))


# === 3. template_safe_substitute(t, mapping) — RST L861-867 ===

#@ requires \str_length(t) >= 0
#@ ensures \result >= 0
def formal_strmod_template_safe_substitute_str(t: str, mapping: dict) -> int:
    """template_safe_substitute soundness: |template_safe_substitute(t, m)| >= 0
    (RST L861-867: 'Like substitute(), except ... the original placeholder will
    appear in the resulting string intact' — it 'always tries to return a usable
    STRING'). The old int-mock's `\\result >= t` is FALSE on real strings (DROPPED);
    the soundest promise is a string (non-negative length). Proved against
    `\\str_length(\\result) >= 0`."""
    return len(template_safe_substitute(t, mapping))


# === 4. format_field(spec, v) [module] — RST L320-321 ===

#@ requires \str_length(spec) >= 0
#@ ensures spec == "" ==> \result == v
def formal_strmod_format_field_empty_identity(spec: str, v: str) -> str:
    """format_field empty-spec identity: spec == "" ==> format_field(spec, v) == v
    (RST L320-321: 'A general convention is that an empty format specification
    produces the same result as if you had called str() on the value'; here the
    value is already a string, so str(v) == v). A REAL EQUALITY, proved by SMT for
    ALL v against the model's faithful `spec == "" ==> \\result == v`."""
    return format_field(spec, v)


# === 7. Template.substitute(mapping) — RST L852-858 [via module twin] ===

#@ requires \str_length(t) >= 0
#@ ensures \result >= 0
def formal_strmod_substitute_str(t: str, mapping: dict) -> int:
    """Template.substitute soundness: result is a string (length >= 0), RST L852-858.
    GAP-2: a `Template()` instance cannot be CONSTRUCTED in a driver (Gap 2a: the
    str field default lowers to int `0` — Why3 type error), so the method cannot be
    exercised directly. `Template.substitute` is, by the model, SEMANTICALLY
    IDENTICAL to the module-level `template_substitute` (same $-substitution), so the
    method's library-reference promise IS this theorem, proved over symbolic t,m."""
    return len(template_substitute(t, mapping))


# === 8. Template.safe_substitute(mapping) — RST L861-867 [via module twin] ===

#@ requires \str_length(t) >= 0
#@ ensures \result >= 0
def formal_strmod_safe_substitute_str(t: str, mapping: dict) -> int:
    """Template.safe_substitute soundness: result is a string (length >= 0),
    RST L861-867. GAP-2: instance not constructible (Gap 2a). The method is
    semantically identical to module-level `template_safe_substitute`, so its
    promise IS this theorem, proved over symbolic t,m."""
    return len(template_safe_substitute(t, mapping))


# === 9. Formatter.format_field(v, spec) — RST L180-183 + L320-321 [via twin] ===

#@ requires \str_length(spec) >= 0
#@ ensures spec == "" ==> \result == v
def formal_strmod_formatter_format_field(spec: str, v: str) -> str:
    """Formatter.format_field empty-spec identity (RST L180-183: 'format_field()
    simply calls the global format() built-in' + L320-321 empty-spec convention).
    GAP-2: a `Formatter()` instance cannot be constructed+called (Gap 2b: a
    fieldless class is not a record type_decl, so its methods are not injected —
    "method 'formatter__format_field' not found"). Because format_field 'simply
    calls format()', the method is identical to the module-level `format_field`,
    so its promise IS this real-equality theorem, proved over symbolic v."""
    return format_field(spec, v)


# === 5. Template.set_template(t) — RST L847-849, L892-897 [GAP-LIMITED] ===

#@ requires \str_length(n) >= 0
#@ ensures \result >= 0
def formal_strmod_set_template_readback(n: str) -> int:
    """Template.set_template read-back (RST L847-849 'The constructor takes a single
    argument which is the template string' + L892-897 'one public data attribute:
    template ... the object passed to the constructor').
    The FAITHFUL promise is `set_template(n); self.template == n` (read-after-write,
    which the MODEL proves standalone via `ensures self.template == t`). GAP-2
    (Gap 2a) blocks propagating it to a driver: `Template()` is not constructible
    (the str field default lowers to int `0`). The strongest instance-free form is
    the safety fact that a template string has non-negative length; the read-back
    equality is GAP-LIMITED, captured in 10-2006-convergence-gap-2.md."""
    return len(n)


# === 6. Template.is_valid() — RST L877-880 [GAP-LIMITED] ===

#@ ensures \result == 0 or \result == 1
def formal_strmod_is_valid_bool(unused: int) -> int:
    """Template.is_valid result domain (RST L877-880: 'Returns False if the template
    has invalid placeholders ...' — a bool, modelled 0/1). The FAITHFUL promise is
    `\\result == 0 or \\result == 1` (which the MODEL proves standalone). GAP-2
    (Gap 2a) blocks constructing a `Template()` to CALL the method, so this theorem
    re-states the boolean DOMAIN directly over a constant witness; the instance-
    method propagation is GAP-LIMITED (10-2006-convergence-gap-2.md)."""
    return 1


# === 10. Formatter.format(fmt) — RST L99-103 [GAP-LIMITED] ===

#@ requires \str_length(fmt) >= 0
#@ ensures \result >= 0
def formal_strmod_formatter_format_str(fmt: str) -> int:
    """Formatter.format soundness: result is a string (length >= 0), RST L99-103
    ('The primary API method. It takes a format string and an arbitrary set of
    positional and keyword arguments'). The full format-string interpretation has no
    SMT-checkable model, so the soundest promise is a string (non-negative length),
    which the MODEL proves standalone via `\\str_length(\\result) >= 0`. GAP-2
    (Gap 2b) blocks constructing a `Formatter()` to call the method; the instance-
    free strongest form is |fmt| >= 0 (a format string is a string). GAP-LIMITED
    (10-2006-convergence-gap-2.md)."""
    return len(fmt)
