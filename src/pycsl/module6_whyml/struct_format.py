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

# Standard-size SCALAR integer format chars modelled FAITHFULLY (cleared-pack):
# the byte codec is proven in the `Pycsl.Struct.Std` Rocq+Lean anchor, so a
# faithful format lowers to the guarded, byte-faithful round-trip family
# (size law + per-field in-range guard + `unpack(pack …) = …`) instead of the
# opaque abstract `struct_{pack,unpack}_iN` symbols.
#   char → (tag, byte_width, signed)
# `tag` is the width/signedness-tagged slot identifier used in the WhyML symbol
# name AND the cited qualname (`Pycsl.Struct.Std.round_trip_<join-of-tags>`), so
# a per-field tag distinguishes `>HH` (u16u16) from `<ii` (i32i32) — closing the
# choices.md S0 collision (the legacy `slot_id` encoded only WhyML *types*, so
# both were `i2`). Signed uses two's complement (range [-2^(8w-1), 2^(8w-1))).
_FAITHFUL_SCALAR = {
    "b": ("i8", 1, True),  "B": ("u8", 1, False),
    "h": ("i16", 2, True), "H": ("u16", 2, False),
    "i": ("i32", 4, True), "I": ("u32", 4, False),
    "l": ("i32", 4, True), "L": ("u32", 4, False),   # standard size: l/L = 4 bytes
    "q": ("i64", 8, True), "Q": ("u64", 8, False),
}
# Explicit STANDARD-size byte-order prefixes only. '' and '@' mean native
# size/alignment, whose calcsize is platform-dependent → excluded from the
# faithful (standard-size) family. '@' is additionally REJECTED (UB-7.4b) — see
# `expressions.py:_handle_struct_call`.
_STD_PREFIXES = {"<", ">", "=", "!"}

# Whitelist of SCALAR shapes routed to the faithful family: EXACTLY the tag-tuples
# that carry a cited, cross-validated Rocq+Lean byte-codec round-trip proof (and a
# matching `_AXIOM_REGISTRY` + `_AXIOM_FUNCTIONS` entry in preamble.py). A faithful
# scalar shape NOT in this set stays on the opaque/legacy path (documented, sound
# boundary) — this is the honest "we claim only what we have proven" gate, and it
# keeps the legacy os shapes (`i2` = u16u16 `>HH`, `i18`, `i1a1`) untouched.
_FAITHFUL_SHAPES = frozenset({
    ("u16",), ("u32",),                       # single unsigned (0753)
    ("i16",), ("i32",), ("i64",),             # single signed
    ("u16", "u32"),                           # multi-slot unsigned
    ("i32", "i32"),                           # multi-slot signed (collision demo vs u16u16)
})

# Whitelist of fixed-bytes `s` widths routed to the faithful array-identity family
# (`struct_{pack,unpack}_fs<N>`, round-trip `unpack(pack d) = d` under `len d = N`).
# Each N carries its own size ensures + cited proof; extensible per-N.
_FAITHFUL_BYTES_N = frozenset({4})


def _scalar_range(width: int, signed: bool) -> Tuple[int, int]:
    """Return the (lo_incl, hi_excl) in-range guard for a scalar of `width`
    bytes. Unsigned: [0, 2^(8w)). Signed (two's complement): [-2^(8w-1),
    2^(8w-1)). Faithful to CPython's out-of-range `struct.error`."""
    bits = 8 * width
    if signed:
        half = 1 << (bits - 1)
        return (-half, half)
    return (0, 1 << bits)


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
    chars: Tuple[str, ...] = ()   # per-slot format char (excludes pad); parallel to slots

    @property
    def arity(self) -> int:
        return len(self.slots)

    def faithful_slots(self) -> Optional[List[Tuple[str, int, int, int]]]:
        """cleared-pack: if this format is a WHITELISTED scalar-integer shape
        (single OR multi-slot) with an EXPLICIT standard byte-order prefix,
        return the per-field list `[(tag, byte_width, lo_incl, hi_excl), …]` for
        the faithful `Pycsl.Struct.Std` family; else None.

        Faithful ⟺ `prefix ∈ _STD_PREFIXES` (`<>=!`), EVERY format char ∈
        `_FAITHFUL_SCALAR`, and the resulting tag-tuple ∈ `_FAITHFUL_SHAPES` (i.e.
        we carry a cited Rocq+Lean round-trip proof for it). Float, array
        (`s`/`c`/`p`), native (`@`/'') and un-whitelisted shapes (incl. the legacy
        os `i2`/`i18`/`i1a1` shapes) stay on the opaque/legacy path — the honest,
        documented boundary."""
        if self.prefix not in _STD_PREFIXES:
            return None
        if not self.chars:
            return None
        fields: List[Tuple[str, int, int, int]] = []
        tags: List[str] = []
        for ch in self.chars:
            spec = _FAITHFUL_SCALAR.get(ch)
            if spec is None:
                return None   # e.g. an `s`/`c`/`p` array field or `f`/`d` float
            tag, width, signed = spec
            lo, hi = _scalar_range(width, signed)
            fields.append((tag, width, lo, hi))
            tags.append(tag)
        if tuple(tags) not in _FAITHFUL_SHAPES:
            return None
        return fields

    def faithful_tag(self) -> Optional[str]:
        """The tag-join naming the faithful symbol / qualname for a scalar shape,
        e.g. `u16`, `u16u32`, `i32i32`; None if not a faithful scalar shape."""
        fields = self.faithful_slots()
        if fields is None:
            return None
        return "".join(f[0] for f in fields)

    def faithful_bytes_slot(self) -> Optional[int]:
        """cleared-pack item 3: if this format is a SINGLE fixed-bytes `s` slot of a
        WHITELISTED width N with an explicit standard prefix, return N (the byte
        count) for the faithful array-identity family `struct_{pack,unpack}_fs<N>`
        (round-trip `unpack(pack d) = d` under `len d = N`); else None."""
        if self.prefix not in _STD_PREFIXES:
            return None
        if len(self.chars) != 1 or self.chars[0] != "s":
            return None
        n = calcsize(self.raw)
        if n is None or n not in _FAITHFUL_BYTES_N:
            return None
        return n

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
    chars: List[str] = []
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
            chars.append(char)
        else:
            slots.extend([slot_type] * count)
            chars.extend([char] * count)
        pos = m.end()

    return StructFormat(raw=fmt, prefix=prefix, slots=tuple(slots),
                        chars=tuple(chars))


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
    # Native size/alignment ('@' prefix) is platform-dependent: standard-size
    # arithmetic here would be UNSOUND (native alignment inserts padding). Refuse
    # to compute a size for it — the faithful/size-law paths must never see a
    # native format (see UB-7.4b; '@' is also rejected in _handle_struct_call).
    if fmt[:1] == "@":
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
