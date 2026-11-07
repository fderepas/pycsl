r"""Test 3028 — route #276 (expected PASS): CONTROLS under the default model (LATIN1-STR).

Claims TRUE in CPython for every str (any code point): the [0, 0x10FFFF] range, congruence
(`s == t` gives `ord(s) == ord(t)`), body/contract agreement on `ord(s[i])`, and
`len(chr(65)) == 1` with the `chr` ValueError obligation. Twin 3029 runs them under
`--strict-latin1`. (`ord("a") == 97` is NOT a default-mode control: the provers do not
evaluate `Char.code (Char.get "a" 0)` — measured Timeout; the strict mode folds an ASCII literal.)
"""
# pycsl-model-assumption: LATIN1-STR
# pycsl-expected: PASS


#@ requires len(s) == 1
#@ ensures 0 <= \result and \result <= 1114111
#@ assigns \nothing
def bounded(s: str) -> int:
    return ord(s)


#@ requires s == t and len(s) == 1
#@ ensures \result == ord(t)
#@ assigns \nothing
def congruent(s: str, t: str) -> int:
    return ord(s)


#@ requires len(s) >= 2
#@ ensures \result == ord(s[1])
#@ assigns \nothing
def at_index(s: str) -> int:
    return ord(s[1])


#@ ensures \result == 1
#@ no_exception ValueError
#@ assigns \nothing
def chr_len() -> int:
    return len(chr(65))


if __name__ == "__main__":
    print(bounded("\u20ac"), congruent("x", "x"), at_index("a\u20ac"), chr_len())
