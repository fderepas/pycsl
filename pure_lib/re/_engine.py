"""Pure-Python regex engine covering only the patterns used by lib/json.

Supported patterns (identified by their normalised source string):

  decoder.py:
    WHITESPACE    r'[ \\t\\n\\r]*'
    HEXDIGITS     r'[0-9A-Fa-f]{4}'
    STRINGCHUNK   r'(.*?)([\"\\\\\\x00-\\x1f])'

  scanner.py:
    NUMBER_RE     r'(-?(?:0|[1-9][0-9]*))(\\.‌[0-9]+)?([eE][-+]?[0-9]+)?'

  encoder.py:
    ESCAPE        r'[\\x00-\\x1f\\\\\"\\b\\f\\n\\r\\t]'
    ESCAPE_ASCII  r'([\\\\"]|[^\\ -~])'
    HAS_UTF8      b'[\\x80-\\xff]'

  tool.py:
    _color_pattern  (verbose, multi-group alternation for JSON colorising)

Any other pattern raises PatternError at compile time.
"""


# ── flags (int bit-masks, same values as CPython) ────────────────────
VERBOSE = 64
MULTILINE = 8
DOTALL = 16
DEBUG = 128


class PatternError(Exception):
    """Raised when an unsupported pattern is compiled."""


# ── Match object ─────────────────────────────────────────────────────

class Match:
    """Minimal Match compatible with json's usage."""

    __slots__ = ('_string', '_start', '_end', '_groups')

    def __init__(self, string, start, end, groups):
        self._string = string
        self._start = start
        self._end = end
        # groups is a tuple of (value_or_None, ...) for captured groups.
        # Group 0 (the whole match) is derived from start/end.
        self._groups = groups

    def group(self, n=0):
        if n == 0:
            return self._string[self._start:self._end]
        return self._groups[n - 1]

    def groups(self):
        return self._groups

    def start(self):
        return self._start

    def end(self):
        return self._end


# ── Pattern object ───────────────────────────────────────────────────

class Pattern:
    """Wraps a hand-written matcher function."""

    __slots__ = ('_match_fn', '_sub_fn', 'pattern', 'flags')

    def __init__(self, match_fn, sub_fn, pattern_src, flags):
        self._match_fn = match_fn
        self._sub_fn = sub_fn
        self.pattern = pattern_src
        self.flags = flags

    def match(self, string, pos=0):
        return self._match_fn(string, pos)

    def sub(self, repl, string, count=0):
        if self._sub_fn is None:
            raise PatternError("sub() not supported for this pattern")
        return self._sub_fn(repl, string, count)


# ── Hand-written matchers ────────────────────────────────────────────

_WHITESPACE_CHARS = set(' \t\n\r')


def _match_whitespace(s, pos=0):
    """r'[ \\t\\n\\r]*'  — match zero or more whitespace chars."""
    i = pos
    n = len(s)
    while i < n and s[i] in _WHITESPACE_CHARS:
        i += 1
    return Match(s, pos, i, ())


def _match_hexdigits(s, pos=0):
    """r'[0-9A-Fa-f]{4}'  — match exactly 4 hex digits."""
    if pos + 4 > len(s):
        return None
    chunk = s[pos:pos + 4]
    for c in chunk:
        if c not in '0123456789abcdefABCDEF':
            return None
    return Match(s, pos, pos + 4, ())


_STRINGCHUNK_TERMINATORS = set('"\\') | {chr(i) for i in range(0x20)}


def _match_stringchunk(s, pos=0):
    """r'(.*?)([\"\\\\\\x00-\\x1f])'  — scan until quote, backslash, or ctrl."""
    n = len(s)
    i = pos
    while i < n:
        c = s[i]
        if c in _STRINGCHUNK_TERMINATORS:
            content = s[pos:i] if i > pos else ''
            return Match(s, pos, i + 1, (content, c))
        i += 1
    return None


def _match_number(s, pos=0):
    """r'(-?(?:0|[1-9][0-9]*))(\\.‌[0-9]+)?([eE][-+]?[0-9]+)?'"""
    n = len(s)
    i = pos

    # integer part: -?(0|[1-9][0-9]*)
    start_int = i
    if i < n and s[i] == '-':
        i += 1
    if i >= n or not s[i].isdigit():
        return None
    if s[i] == '0':
        i += 1
    else:
        while i < n and s[i].isdigit():
            i += 1
    integer = s[start_int:i]

    # fraction: (\.[0-9]+)?
    frac = None
    if i < n and s[i] == '.':
        j = i + 1
        if j >= n or not s[j].isdigit():
            # no digits after dot → no fraction
            pass
        else:
            while j < n and s[j].isdigit():
                j += 1
            frac = s[i:j]
            i = j

    # exponent: ([eE][-+]?[0-9]+)?
    exp = None
    if i < n and s[i] in 'eE':
        j = i + 1
        if j < n and s[j] in '+-':
            j += 1
        if j >= n or not s[j].isdigit():
            pass
        else:
            while j < n and s[j].isdigit():
                j += 1
            exp = s[i:j]
            i = j

    if i == pos or (i == pos + 1 and s[pos] == '-'):
        return None

    return Match(s, pos, i, (integer, frac, exp))


_ESCAPE_CHARS = {chr(i) for i in range(0x20)} | {'\\', '"'}


def _sub_escape(repl, s, count=0):
    """r'[\\x00-\\x1f\\\\\"\\b\\f\\n\\r\\t]' .sub(repl, s)"""
    parts = []
    i = 0
    n = len(s)
    subs = 0
    while i < n:
        c = s[i]
        if c in _ESCAPE_CHARS:
            m = Match(s, i, i + 1, ())
            parts.append(repl(m))
            subs += 1
            if count and subs >= count:
                parts.append(s[i + 1:])
                break
        else:
            parts.append(c)
        i += 1
    return ''.join(parts)


def _match_escape(s, pos=0):
    """r'[\\x00-\\x1f\\\\\"\\b\\f\\n\\r\\t]' .match(s, pos)"""
    if pos < len(s) and s[pos] in _ESCAPE_CHARS:
        return Match(s, pos, pos + 1, ())
    return None


def _sub_escape_ascii(repl, s, count=0):
    r"""r'([\\\\"]|[^\\ -~])' .sub(repl, s)
    Matches: backslash, double-quote, or any char outside 0x20..0x7e."""
    parts = []
    i = 0
    n = len(s)
    subs = 0
    while i < n:
        c = s[i]
        o = ord(c)
        if c == '\\' or c == '"' or o < 0x20 or o > 0x7e:
            m = Match(s, i, i + 1, (c,))
            parts.append(repl(m))
            subs += 1
            if count and subs >= count:
                parts.append(s[i + 1:])
                break
        else:
            parts.append(c)
        i += 1
    return ''.join(parts)


def _match_escape_ascii(s, pos=0):
    r"""r'([\\\\"]|[^\\ -~])' .match(s, pos)"""
    if pos < len(s):
        c = s[pos]
        o = ord(c)
        if c == '\\' or c == '"' or o < 0x20 or o > 0x7e:
            return Match(s, pos, pos + 1, (c,))
    return None


def _match_has_utf8(s, pos=0):
    """b'[\\x80-\\xff]' .match(s, pos) — bytes pattern."""
    if pos < len(s) and s[pos] >= 0x80:
        return Match(s, pos, pos + 1, ())
    return None


# ── tool.py color pattern ────────────────────────────────────────────
#
# The verbose pattern from tool.py matches JSON tokens for colorising:
#   (?P<key>"(\\.|[^"\\])*")(?=:)   |
#   (?P<string>"(\\.|[^"\\])*")     |
#   (?P<number>NaN|-?Infinity|[0-9\-+.Ee]+) |
#   (?P<boolean>true|false)         |
#   (?P<null>null)


def _scan_json_string(s, i):
    """Match a JSON string starting at s[i] == '"'. Returns end index."""
    n = len(s)
    i += 1  # skip opening quote
    while i < n:
        c = s[i]
        if c == '\\':
            i += 2
        elif c == '"':
            return i + 1
        else:
            i += 1
    return -1


def _match_color_pattern(s, pos=0):
    """Match one JSON token at pos for colorising."""
    n = len(s)
    if pos >= n:
        return None
    c = s[pos]

    if c == '"':
        end = _scan_json_string(s, pos)
        if end < 0:
            return None
        text = s[pos:end]
        # key if followed by ':'
        if end < n and s[end] == ':':
            return Match(s, pos, end,
                         (text, None, None, None, None))
        return Match(s, pos, end,
                     (None, text, None, None, None))

    if c == 't' and s[pos:pos + 4] == 'true':
        return Match(s, pos, pos + 4,
                     (None, None, None, 'true', None))
    if c == 'f' and s[pos:pos + 5] == 'false':
        return Match(s, pos, pos + 5,
                     (None, None, None, 'false', None))
    if c == 'n' and s[pos:pos + 4] == 'null':
        return Match(s, pos, pos + 4,
                     (None, None, None, None, 'null'))

    # NaN / -?Infinity / number
    if c == 'N' and s[pos:pos + 3] == 'NaN':
        return Match(s, pos, pos + 3,
                     (None, None, 'NaN', None, None))
    if c == 'I' and s[pos:pos + 8] == 'Infinity':
        return Match(s, pos, pos + 8,
                     (None, None, 'Infinity', None, None))
    if c == '-' and s[pos:pos + 9] == '-Infinity':
        return Match(s, pos, pos + 9,
                     (None, None, '-Infinity', None, None))

    # [0-9\-+.Ee]+
    if c in '0123456789-+.eE':
        i = pos
        while i < n and s[i] in '0123456789-+.eE':
            i += 1
        if i > pos:
            return Match(s, pos, i,
                         (None, None, s[pos:i], None, None))

    return None


def _color_match_group(self, n=0):
    """Extended group() that supports named groups for tool.py."""
    if isinstance(n, str):
        _names = ('key', 'string', 'number', 'boolean', 'null')
        if n in _names:
            return self._groups[_names.index(n)]
        return None
    return Match.group(self, n)


class _ColorMatch(Match):
    """Match subclass with named-group support for tool.py."""
    group = _color_match_group


def _match_color(s, pos=0):
    m = _match_color_pattern(s, pos)
    if m is None:
        return None
    return _ColorMatch(s, m._start, m._end, m._groups)


def _sub_color(repl, s, count=0):
    """re.sub for the color pattern — find all JSON tokens and replace."""
    parts = []
    i = 0
    n = len(s)
    subs = 0
    while i < n:
        m = _match_color(s, i)
        if m is not None:
            parts.append(repl(m))
            i = m.end()
            subs += 1
            if count and subs >= count:
                parts.append(s[i:])
                break
        else:
            parts.append(s[i])
            i += 1
    return ''.join(parts)


# ── Pattern registry ─────────────────────────────────────────────────

# Normalise pattern source → (match_fn, sub_fn)
_PATTERN_KEY_ESCAPE = r'[\x00-\x1f\\"\b\f\n\r\t]'
_PATTERN_KEY_ESCAPE_ASCII = r'([\\"]|[^\ -~])'

def _normalise(source):
    """Collapse whitespace so VERBOSE patterns can be recognised."""
    if isinstance(source, bytes):
        return source.replace(b' ', b'').replace(b'\n', b'').replace(b'\t', b'')
    return source.replace(' ', '').replace('\n', '').replace('\t', '')


def compile(pattern, flags=0):
    """Compile a pattern into a Pattern object.

    Only the patterns used by lib/json are supported.
    """
    src = pattern if isinstance(pattern, (str, bytes)) else str(pattern)

    # HAS_UTF8 (bytes) — check before normalising
    if isinstance(src, bytes):
        if b'\x80' in src or b'\\x80' in src:
            return Pattern(_match_has_utf8, None, src, flags)
        raise PatternError(
            f"pure_lib.re: unsupported bytes pattern: {src!r}"
        )

    norm = _normalise(src)

    # Whitespace
    if norm in (r'[\t\n\r]*', '[\\t\\n\\r]*'):
        return Pattern(_match_whitespace, None, src, flags)

    # Hexdigits
    if norm in ('[0-9A-Fa-f]{4}',):
        return Pattern(_match_hexdigits, None, src, flags)

    # Stringchunk
    if '(.*?)' in src and '["\\\\' in norm:
        return Pattern(_match_stringchunk, None, src, flags)

    # Number
    if '(?:0|[1-9]' in src or '(?:0|[1-9]' in norm:
        return Pattern(_match_number, None, src, flags)

    # Escape (exact char-class for control chars + backslash + quote)
    if src == _PATTERN_KEY_ESCAPE:
        return Pattern(_match_escape, _sub_escape, src, flags)

    # Escape ASCII
    if src == _PATTERN_KEY_ESCAPE_ASCII:
        return Pattern(_match_escape_ascii, _sub_escape_ascii, src, flags)

    # tool.py color pattern (verbose, contains (?P<key>...)
    if '(?P<key>' in src or '(?P<string>' in src:
        return Pattern(_match_color, _sub_color, src, flags)

    raise PatternError(
        f"pure_lib.re: unsupported pattern: {src!r}"
    )


def sub(pattern, repl, string, count=0, flags=0):
    """re.sub() — compile then delegate to Pattern.sub."""
    p = compile(pattern, flags) if not isinstance(pattern, Pattern) else pattern
    return p.sub(repl, string, count)
