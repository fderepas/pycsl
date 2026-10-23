# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1280 — (#49) ROUTE #98's FAIL-CLOSED CO-LANDING HALF, NEGATIVE-TESTED.

The comment that used to guard route #96's frame repair said a region base which is not an
array parameter "contributes NOTHING … Any such residue stays visible as an un-framed val."
That sentence was wrong twice, and this witness pins both corrections:

  (1) "FAIL-CLOSED" WAS A CLAIM ABOUT THE EMITTER, NOT THE PROVER. Emitting nothing is
      fail-closed for the emitter (no ill-typed `writes` is produced) and fail-OPEN for the
      verifier, which is then told the stub is PURE. Dropping a frame clause is NEVER
      conservative — an un-framed `val` is the STRONGEST possible claim about a function.
  (2) "STAYS VISIBLE" NAMED NO OBSERVER. No gate, no plane and no ratchet counted an
      un-framed `val` carrying a region `assigns`. Visible to whom?

Here `a` is UNANNOTATED, so it is `Any`-typed and emits as `(a: int)` — not an `array`
parameter, so no `writes` target can be built for it. MEASURED AT a32ec69e the emission was

    val scramble (a: int) (n: int) : int
      requires { (n >= 0) }

an un-framed val that happened to be caught downstream by a Why3 TYPE rejection of the
caller's array argument — i.e. saved by an accident of typing, not by a guard.

It is now REFUSED at the point of the loss, with the reason stated:
`PYCSL-UNFRAMED-REGION-ASSIGNS`. This file is the negative test of that refusal — it is the
thing the guard should catch, and it proves the guard's population is NOT EMPTY.
"""


#@ requires n >= 0
#@ assigns a[0..n]
#@ \trusted reviewer: route98
def scramble(a, n: int) -> int:
    a[0] = 0
    return 0


#@ requires \length(arr) > 3
#@ ensures \result == 0
def driver(arr: list) -> int:
    return scramble(arr, 1)
