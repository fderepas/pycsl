"""Test 1269 — route #96 CONTROL: the repaired `val` frame is EXACTLY the `let` frame.

The repair over-approximates `#@ assigns a[lo..hi]` to `writes { a }`. The question that makes
that sound rather than merely strict is: **what does PyCSL already do for the same contract with
a VERIFIED BODY?** Why3 infers the effect of a `let` from its mutations, and in the
value-semantic model it infers exactly the same whole-array write — a caller keeps NOTHING about
`a`, not even cells outside the declared region.

`touch` here has a REAL BODY and `#@ assigns a[0..1]`; `driver` asks about `arr[3]`, OUTSIDE
that region, and the claim does NOT prove. Its `\trusted` twin is 1270, and it does not prove
either. So the repair did not make the bodyless val STRICTER than the verified baseline — it
made it EQUAL to it, which is the only frame a bodyless stub was ever entitled to.

ITS JOB: if some future change re-introduces region PRECISION on one side only, exactly one of
1269/1270 flips and the pair stops agreeing.
"""
# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL

#@ requires \length(a) > 4
#@ assigns a[0..1]
def touch(a: list) -> int:
    a[0] = 0
    return 0


#@ requires \length(arr) > 4
#@ requires arr[3] == 5
#@ ensures \result == 5
def driver(arr: list) -> int:
    touch(arr)
    return arr[3]
