"""WL-06c USER-REQUIRES (T9) — a user `requires` bounds the unknown `bytes` param
content, ON TOP of the implicit range. Verdict: PROVEN.

The content of an unknown `bytes` PARAMETER stays opaque (the range invariant does not
pin a value — see the false-twin), but a user-supplied `#@ requires b[0] == 65` lets the
solver prove `\result == 65`. This locks the de-opacifying escape hatch: the user bounds
what the type alone cannot."""
_ = 0


#@ requires len(b) >= 1
#@ requires b[0] == 65
#@ ensures \result == 65
def user_bounded(b: bytes) -> int:
    """A user `requires` on the byte value makes the specific-value read PROVE."""
    return b[0]
