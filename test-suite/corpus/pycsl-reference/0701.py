"""Test 0701 — strings: IMPORTED fieldless method-bearing class construct + call (Gap 2b).

Gap 2b (10-2006-convergence-spec-2): a class with methods but NO instance fields and NO
bases used to be dropped by Module5's `if fields or bases:` guard, lowering to an opaque
`type fmt = int` whose method stubs were never injected on import — so `f.echo(...)` could
not resolve. The fix (R2, BINDING: ≥1 non-dunder/non-property method AND not a mixin AND no
fields AND no bases) promotes it to a unit-carrying record (`type fmt = { mutable
fmt__unit: int }`, constructed `{ fmt__unit = 0 }`), so the method stub is injected and the
call lowers against the injected `val fmt__echo` (resp. is inlined for a simple-bodied method).

`echo` is simple-bodied (non-trusted, tail-return) so the call routes through inlining without
hitting the deferred trusted-routing path (R4).

STATUS — **PROVES**.
"""
# pycsl-flags: --memory-model hoare
from multi_file_lib.fieldless_stub import Fmt

f = Fmt()


#@ ensures \result == n
#@ assigns \nothing
def construct_and_call(n: int) -> int:
    return f.echo(n)


if __name__ == "__main__":
    print("PASS")
