"""Format-string parser for `struct.pack` / `struct.unpack`.

Per missing-bytes-struct-feature.md Phase 2. Pure utility — no
Module6 mixin dependencies. Used by `expressions.py:_handle_struct_call`
to convert a compile-time `struct` format string into an arity-aware
list of WhyML param/return types.

Supported format chars (Python `struct` standard):
  x       pad byte         (arity contribution: 0)
  b/B     int8/uint8       → int
  h/H     int16/uint16     → int
  i/I/l/L int32/uint32     → int
  q/Q     int64/uint64     → int
  f       float32          → int  (PyCSL has no float; modeled as int)
  d       float64          → int
  ?       bool             → int
  s       fixed-length bytes → array int (arity 1 per N-prefixed slot)
  c       single byte char → array int (1-element)
  p       Pascal string    → array int

Count multipliers: `10I` = 10 × I, `30s` = 1 × (30-byte bytes).
Byte-order prefix (optional): `@`, `=`, `<`, `>`, `!` — recorded
but doesn't affect arity.

Out of scope (treated as error → caller falls back to opaque
abstract emission):
  e (float16), n/N (native size_t), P (native pointer)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


# Each format char (after count multiplier) maps to a WhyML param/return type
# AND a per-slot arity contribution.
_CHAR_TO_TYPE = {
    "x": None,         # pad — no slot
    "b": "int", "B": "int",
    "h": "int", "H": "int",
    "i": "int", "I": "int",
    "l": "int", "L": "int",
    "q": "int", "Q": "int",
    "f": "int",        # PyCSL models float as int
    "d": "int",
    "?": "int",
    "s": "array int",  # fixed-length bytes — N-prefix is bytes count, not arity
    "c": "array int",  # single char as 1-element bytes
    "p": "array int",
}

_VALID_PREFIXES = {"@", "=", "<", ">", "!"}


@dataclass(frozen=True)
class StructFormat:
    """Parsed `struct` format-string descriptor.

    Attributes
    ----------
    raw : str
        Original format string (no prefix-strip).
    prefix : str
        Byte-order prefix or '' if absent.
    slots : list[str]
        WhyML type per packed/unpacked slot, in order. Pad bytes are
        excluded.  E.g. for `'>IHHHHHII10Ixx'` this is
        `['int', 'int', 'int', 'int', 'int', 'int', 'int', 'int',
         'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int',
         'int', 'int']` (18 ints).
    """
    raw: str
    prefix: str
    slots: Tuple[str, ...]

    @property
    def arity(self) -> int:
        return len(self.slots)

    def slot_id(self) -> str:
        """Compact identifier for use in WhyML symbol names.

        Encodes only the slot types (not prefix, not pad), so two
        format strings that pack/unpack the same shape share the
        same abstract symbol. `'>IHHHHHII10Ixx'` and `'<IHHHHHII10I'`
        both give id `i18` (18 ints).
        """
        if not self.slots:
            return "empty"
        # Run-length encode for compactness
        out: List[str] = []
        run_type = self.slots[0]
        run_count = 1
        for t in self.slots[1:]:
            if t == run_type:
                run_count += 1
            else:
                out.append(_short_type(run_type) + str(run_count))
                run_type, run_count = t, 1
        out.append(_short_type(run_type) + str(run_count))
        return "".join(out)


def _short_type(t: str) -> str:
    if t == "int":
        return "i"
    if t == "array int":
        return "a"
    return "x"


_TOKEN_RE = re.compile(r"(\d*)([A-Za-z?])")


def parse_format(fmt: str) -> Optional[StructFormat]:
    """Parse a struct format string. Returns None on unsupported chars.

    The format is `[prefix] (count? char)*` where:
      - prefix ∈ `@`, `=`, `<`, `>`, `!`  (optional)
      - count is a decimal integer; default 1
      - char is one of the format chars in `_CHAR_TO_TYPE`

    Special cases:
      - `Ns` is a SINGLE slot of type `array int` (the N is the byte
        length, not arity). Similarly `Nc` and `Np`.
      - `Nx` is N pad bytes; arity contribution 0.
      - `NX` for any other X means N consecutive X slots.
    """
    if not isinstance(fmt, str) or not fmt:
        return None

    cursor = 0
    prefix = ""
    if fmt[0] in _VALID_PREFIXES:
        prefix = fmt[0]
        cursor = 1

    slots: List[str] = []
    pos = cursor
    while pos < len(fmt):
        m = _TOKEN_RE.match(fmt, pos)
        if not m:
            return None
        count_str, char = m.group(1), m.group(2)
        count = int(count_str) if count_str else 1
        slot_type = _CHAR_TO_TYPE.get(char)
        if slot_type is None and char != "x":
            # Unsupported char
            return None
        if char == "x":
            # Pad bytes — no slot
            pass
        elif char in ("s", "c", "p"):
            # N-prefix is byte length, not arity; one array-int slot
            slots.append("array int")
        else:
            slots.extend([slot_type] * count)
        pos = m.end()

    return StructFormat(raw=fmt, prefix=prefix, slots=tuple(slots))


def calcsize(fmt: str) -> Optional[int]:
    """Compute the byte size of a format string (struct.calcsize semantics).

    Returns None on unsupported chars. Uses standard sizes (not native).
    """
    sizes = {
        "x": 1, "b": 1, "B": 1, "?": 1, "c": 1,
        "h": 2, "H": 2,
        "i": 4, "I": 4, "l": 4, "L": 4, "f": 4,
        "q": 8, "Q": 8, "d": 8,
    }
    if not isinstance(fmt, str) or not fmt:
        return None
    pos = 1 if fmt[:1] in _VALID_PREFIXES else 0
    total = 0
    while pos < len(fmt):
        m = _TOKEN_RE.match(fmt, pos)
        if not m:
            return None
        count_str, char = m.group(1), m.group(2)
        count = int(count_str) if count_str else 1
        if char in ("s", "p"):
            total += count   # N-byte fixed bytes
        elif char in sizes:
            total += sizes[char] * count
        else:
            return None
        pos = m.end()
    return total
