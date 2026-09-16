# ROUTE #155 — a COMPOSED constant binding in a parameterless constructor is never applied

**Status: OPEN. Found by gen #29 (2026-09-16), carrier-rerun on its own landed route #150.** Severity 1.

## Measured at `52a02d5a` (and at `8b91a93b`)

    class A:
        def __init__(self, k: int = 5) -> None: self.x = k      # (or `*, k: int = 5`)
    class B(A):
        def __init__(self) -> None: super().__init__()
    B().get() == 0     PROVED   (record literal { b_x = 0 }; CPython 5)

Route #150 composes `x = 5` into `B.init_body`, but `_call_record_constructor` only enters its
binding block when the class HAS parameters (`init_params or kwonly_params`), so a parameterless
constructor's init_body is ignored and every field takes its witness.

## Scoped repair (not landed)

Enter the binding block for a zero-argument call whenever `init_body` is non-empty; an entry whose
free names are not bound keeps being skipped (unchanged), so only closed (constant) entries — which
only the composition produces — are newly applied.
