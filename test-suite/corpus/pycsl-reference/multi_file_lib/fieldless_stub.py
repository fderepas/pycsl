"""multi_file_lib.fieldless_stub — fixture for 10-2006-convergence-spec-2 Gap 2b.

`Fmt` mirrors the real `strmod.Formatter` shape: a method-bearing class with NO instance
fields and NO bases. Module5 used to drop such a class (the `if fields or bases:` guard),
so it lowered to an opaque `type fmt = int` and its method stubs were never injected on
import. Gap 2b promotes it to a unit-carrying record (`type fmt = { mutable fmt__unit: int }`)
so the method stub is injected and the call resolves.

`echo` is a SIMPLE-BODIED (non-trusted, tail-return) method so the call routes through
inlining without hitting the deferred trusted-routing path (R4).
"""
_ = 0  # anchor


class Fmt:
    #@ ensures \result == n
    #@ assigns \nothing
    def echo(self, n: int) -> int:
        return n
