"""Test 1267 — route #96 EXPLOIT, now REFUSED: a bodyless `val` must transmit an
array-region `assigns` as a `writes` clause.

`scramble` is `\trusted` and declares `#@ assigns a[0..n]`. A `val` has NO body, so Why3
cannot INFER its effect — the frame must be DECLARED. Before the repair,
`_emit_frame_condition`'s `val` branch collected only `Attribute`/`FieldGet` targets and
`continue`d past every `AssignsRegion`, so the emitted val carried NO `writes` at all:

    val scramble (a: array int) (n: int) : int
      requires { (n >= 0) }
      requires { ((Array.length a) > (n + 1)) }

Why3 therefore treated `scramble` as PURE and `driver` kept `arr[0] == 7` across a call to a
stub whose own contract says it writes `arr[0]`. `\result == 7` was PROVED, while CPython
running the stub's declared behaviour returns **0**.

`\trusted` is the DECLARED TCB BOUNDARY: a reviewer certifies the stub's contract, and the
`assigns` clause is part of what they certify. It was the exact part the emitter threw away —
the trust boundary honoured in the review and voided in the proof.

REPAIRED by emitting `writes { a }` for an `AssignsRegion` whose base is an array parameter of
the emitted signature. Over-approximating the region to the whole array is SOUND (more havoc =
strictly less caller knowledge) and is precisely what Why3 infers for a `let` whose body writes
one cell — see 1269, which pins that equivalence.
"""
# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL

#@ requires n >= 0
#@ requires \length(a) > n + 1
#@ assigns a[0..n]
#@ \trusted reviewer: route96
def scramble(a: list, n: int) -> int:
    a[0] = 0
    return 0


#@ requires \length(arr) > 3
#@ requires arr[0] == 7
#@ ensures \result == 7
def driver(arr: list) -> int:
    scramble(arr, 1)
    return arr[0]
