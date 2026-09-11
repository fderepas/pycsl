"""n01 — THE NEGATIVE TEST FOR THE PLANE ITSELF. It MUST be reported RED.

A gate that has never been observed to fail is not known to be a gate. This driver exists
only to trigger the plane's UNSOUND path with a REAL program, so that "all green" on the
standing corpus means something.

`g` is `#@ \trusted`, so its `ensures` is ASSUMED rather than proved — that is the
documented, OPT-IN trusted-stub mechanism, NOT a soundness route. But it lets PyCSL PROVE
`\result == 99` about a program CPython evaluates to 1, which is exactly the
(claim disagrees with CPython) + (PyCSL proves) combination the plane must rule RED.

It lives under `negative-test/` and the standing plane SKIPS this directory, so it cannot
make the normal run red. `--negative-test` runs it and FAILS if the plane does NOT rule it
unsound.

`g`'s clause is written REVERSED (`99 == \result`) on purpose: the plane accepts exactly
one `#@ ensures \result == <int>` per driver and fails closed on anything else, so the
assumed stub must not present a second parseable claim. The two spellings mean the same
thing to PyCSL.
"""


#@ \trusted reviewer: value-differential-negative-test
#@ ensures 99 == \result
#@ assigns \nothing
def g() -> int:
    return 1


#@ ensures \result == 99
#@ assigns \nothing
def f() -> int:
    return g()


if __name__ == "__main__":
    print(f())
