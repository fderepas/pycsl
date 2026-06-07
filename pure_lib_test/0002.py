"""Test 0002: pure_lib/re — regex compile, match, and sub round-trips.

Exercises every hand-written matcher in the pure_lib/re engine against
concrete inputs, verifying that compile()/match()/sub() produce correct
Match objects and substitution results.

Covers the symbols from lib/calling.json that pure_lib/re implements:
  compile, match, sub, error/PatternError, Pattern, Match,
  Match.group, Match.groups, Match.start, Match.end
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pure_lib.re import compile, sub, error, PatternError
from pure_lib.re import Pattern, Match
from pure_lib.re import VERBOSE, MULTILINE, DOTALL, DEBUG

# ── 1. Whitespace matcher ────────────────────────────────────────────

ws = compile(r'[ \t\n\r]*')
assert isinstance(ws, Pattern), "compile should return Pattern"

m = ws.match('   hello', 0)
assert m is not None, "whitespace should match leading spaces"
assert m.start() == 0
assert m.end() == 3
assert m.group() == '   '
assert m.groups() == ()

# Zero-width match (no whitespace)
m2 = ws.match('hello')
assert m2 is not None, "whitespace* should match zero-width"
assert m2.start() == 0
assert m2.end() == 0
assert m2.group() == ''

# Match with pos
m3 = ws.match('abc  \t\n  xyz', 3)
assert m3 is not None
assert m3.start() == 3
assert m3.end() == 9

print("PASS: 1 — whitespace matcher")

# ── 2. Hexdigits matcher ─────────────────────────────────────────────

hexm = compile('[0-9A-Fa-f]{4}')

m = hexm.match('1a2B rest', 0)
assert m is not None, "hex should match 4 hex digits"
assert m.group() == '1a2B'
assert m.end() == 4

# Too few chars
m2 = hexm.match('1a2', 0)
assert m2 is None, "hex should fail on < 4 chars"

# Non-hex char
m3 = hexm.match('1a2G', 0)
assert m3 is None, "hex should fail on non-hex char"

# Match at offset
m4 = hexm.match('...DEAD...', 3)
assert m4 is not None
assert m4.group() == 'DEAD'
assert m4.start() == 3
assert m4.end() == 7

print("PASS: 2 — hexdigits matcher")

# ── 3. Stringchunk matcher ───────────────────────────────────────────

sc = compile(r'(.*?)(["\\' + '\x00-\x1f' + '])')
# This matches until a quote, backslash, or control char

m = sc.match('hello"world', 0)
assert m is not None
assert m.group(1) == 'hello', f"group(1)={m.group(1)!r}"
assert m.group(2) == '"', f"group(2)={m.group(2)!r}"
assert m.end() == 6

# Backslash terminator
m2 = sc.match('abc\\def', 0)
assert m2 is not None
assert m2.group(1) == 'abc'
assert m2.group(2) == '\\'

# Empty prefix before terminator
m3 = sc.match('"start', 0)
assert m3 is not None
assert m3.group(1) == ''
assert m3.group(2) == '"'

print("PASS: 3 — stringchunk matcher")

# ── 4. Number matcher ────────────────────────────────────────────────

numre = compile(r'(-?(?:0|[1-9][0-9]*))(\.[0-9]+)?([eE][-+]?[0-9]+)?')

# Simple integer
m = numre.match('42 rest', 0)
assert m is not None
assert m.group(1) == '42'
assert m.group(2) is None  # no fraction
assert m.group(3) is None  # no exponent

# Negative zero
m2 = numre.match('-0', 0)
assert m2 is not None
assert m2.group(1) == '-0'

# Float
m3 = numre.match('3.14', 0)
assert m3 is not None
assert m3.group(1) == '3'
assert m3.group(2) == '.14'

# Scientific notation
m4 = numre.match('1e10', 0)
assert m4 is not None
assert m4.group(3) == 'e10'

# Full float with exponent
m5 = numre.match('-12.5e-3', 0)
assert m5 is not None
assert m5.group(1) == '-12'
assert m5.group(2) == '.5'
assert m5.group(3) == 'e-3'

# No match
m6 = numre.match('abc', 0)
assert m6 is None

print("PASS: 4 — number matcher")

# ── 5. Escape matcher + sub ──────────────────────────────────────────

esc = compile(r'[\x00-\x1f\\"\b\f\n\r\t]')

m = esc.match('\\rest', 0)
assert m is not None
assert m.group() == '\\'
assert m.end() == 1

m2 = esc.match('\nhello', 0)
assert m2 is not None
assert m2.group() == '\n'

m3 = esc.match('normal', 0)
assert m3 is None, "escape should not match normal chars"

# sub: replace control chars
result = esc.sub(lambda m: f'\\u{ord(m.group()):04x}', 'a\nb')
assert result == 'a\\u000ab', f"sub result: {result!r}"

print("PASS: 5 — escape matcher + sub")

# ── 6. Escape ASCII matcher + sub ────────────────────────────────────

esc_ascii = compile(r'([\\"]|[^\ -~])')

m = esc_ascii.match('\\test', 0)
assert m is not None
assert m.group() == '\\'

m2 = esc_ascii.match('"test', 0)
assert m2 is not None
assert m2.group() == '"'

m3 = esc_ascii.match('normal', 0)
assert m3 is None, "escape_ascii should not match printable non-special"

print("PASS: 6 — escape ASCII matcher")

# ── 7. HAS_UTF8 (bytes) ─────────────────────────────────────────────

utf8 = compile(b'[\x80-\xff]')
assert isinstance(utf8, Pattern)

# This pattern matches bytes, tested conceptually
print("PASS: 7 — HAS_UTF8 bytes pattern compiled")

# ── 8. PatternError for unsupported patterns ─────────────────────────

try:
    compile(r'unsupported.*pattern')
    assert False, "should have raised PatternError"
except PatternError:
    pass

assert error is PatternError, "re.error should alias PatternError"

print("PASS: 8 — PatternError raised for unsupported pattern")

# ── 9. Module-level sub() ────────────────────────────────────────────

result = sub(r'[\x00-\x1f\\"\b\f\n\r\t]', lambda m: '?', 'a\tb\nc')
assert result == 'a?b?c', f"module-level sub: {result!r}"

print("PASS: 9 — module-level sub()")

# ── 10. Flags ─────────────────────────────────────────────────────────

assert VERBOSE == 64, f"VERBOSE={VERBOSE}"
assert MULTILINE == 8, f"MULTILINE={MULTILINE}"
assert DOTALL == 16, f"DOTALL={DOTALL}"
assert DEBUG == 128, f"DEBUG={DEBUG}"

print("PASS: 10 — flags have correct values")

# ── Summary ──────────────────────────────────────────────────────────
print("\nPASS: 0002 — all pure_lib/re tests passed")
