r"""Test 3029 — route #276 (expected PASS): CONTROLS under `--strict-latin1`.

Dropping LATIN1-STR must not cost the claims that are TRUE in CPython for every str: the 3028
controls (an ASCII literal folds to its code point; the uninterpreted code point is clamped to
[0, 0x10FFFF] by a definition; congruence; body/contract agreement; `len(chr(65)) == 1`), plus
the full-range round trip `ord(chr(n)) == n` for `0 <= n < 0x110000`, which the DEFAULT model
cannot prove (its `Char.chr` round-trips only below 256). The measured cost of the flag is
elsewhere: cited codec lemmas over `Char.code` stop applying (route #276 measurements).
"""
# pycsl-flags: --strict-latin1
# pycsl-expected: PASS


#@ ensures \result == 97
#@ assigns \nothing
def lit() -> int:
    return ord("a")


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


#@ requires 0 <= n and n < 1114112
#@ ensures \result == n
#@ assigns \nothing
def round_trip(n: int) -> int:
    return ord(chr(n))


if __name__ == "__main__":
    print(lit(), bounded("\u20ac"), congruent("x", "x"), at_index("a\u20ac"), chr_len(), round_trip(8364))
