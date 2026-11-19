"""Test 0864 — WL-06c regression lock (POSITIVE): the user-`requires` escape hatch bounds
an unknown `bytes` PARAMETER's content.

wrong-lowering-to-fix.md §WL-06c. The CONTENT of an unknown `bytes` PARAMETER stays
opaque under the implicit range invariant alone (a specific-value claim does NOT prove —
0863). But a user-supplied `#@ requires b[0] == 65` bounds the unknown, so `\result == 65`
becomes PROVABLE. This locks the de-opacifying escape hatch: the user constrains what the
`bytes` type alone cannot, ON TOP of the implicit `0 <= b[i] < 256` range fact.
"""
_ = 0  # anchor


#@ requires len(b) >= 1
#@ requires b[0] == 65
#@ ensures \result == 65
def user_bounded(b: bytes) -> int:
    """A user `requires` on the byte value makes the specific-value read PROVE."""
    return b[0]


if __name__ == "__main__":
    assert user_bounded(b"Az") == 65  # b"Az"[0] == ord("A") == 65
