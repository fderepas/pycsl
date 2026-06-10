"""Test 0702 — strings: the `ord`/`chr` char<->int bridge (10-2300-spec-5).

The byte side of the dirent name codec needs `b[i] = ord(name[i])` to encode and
`chr(...)` to decode. That requires a char<->int bridge:

  - `ord(<1-char string>)` -> its byte/code-point `int`.
  - `chr(<int>)` -> a 1-char `string`.
  - the round-trip `chr(ord(c)) == c` for a 1-char string `c`.

Before this feature, `ord(name[i])` failed WhyML type-check ("has type string, but is
expected to have type int") — `ord` fell through to the generic unannotated-callee path
which declared `val ord_1 (x: int) : int`, mis-typing the 1-char STRING argument.

The fix adds two TOTAL abstract vals in the preamble (gated on a new `needs_char` flag
that also emits `use string.Char`):

    val ord_op (c: string) : int   ensures { 0 <= result < 256 }
                                   ensures { result = Char.code (Char.get c 0) }
    val chr_op (n: int) : string   ensures { String.length result = 1 }
                                   ensures { result = (Char.chr n).contents }

`string.Char` is a SIBLING module in the SAME trusted `string.mlw` as the already-used
`string.String`. The round-trip comes FREE from its theory axioms `chr_code`
(`chr (code c) = c`) and `code` (`0 <= code c < 256`) — so this is a THEORY LEMMA, NOT a
new PyCSL-owned axiom. No `_AXIOM_REGISTRY` entry, no Rocq/Lean, no TCB growth beyond the
`use`.

STATUS — **PROVES** (pin Alt-Ergo; Z3 is slow on the `string.Char` extensionality goal).
`roundtrip` discharges `chr(ord(name[0])) == name[0:1]` from `chr_code`+`get`; `ord_range`
discharges `0 <= ord(name[0]) <= 255` from the `code` axiom.
"""
# pycsl-flags: --memory-model hoare


#@ requires \str_length(name) >= 1
#@ assigns \nothing
#@ ensures \result == name[0:1]
def roundtrip(name: str) -> str:
    return chr(ord(name[0]))


#@ requires \str_length(name) >= 1
#@ assigns \nothing
#@ ensures 0 <= \result and \result <= 255
def ord_range(name: str) -> int:
    return ord(name[0])


if __name__ == "__main__":
    print("PASS")
