# OPEN ROUTE #70 — THE SYNTHESIZED `self.<m>(...)` STUB KEEPS THE CALLEE'S `ensures`
# AND DROPS ITS `requires`
# (found 2026-09-11 by relaunch #55, at `b76b331f`)

## THE HEADLINE

```python
@dataclass
class C:
    tag: int = 0

    #@ \trusted reviewer: probe
    #@ requires x > 0
    #@ ensures \result > 0
    #@ assigns \nothing
    def pos_only(self, x: int) -> int:
        return x

    #@ requires True
    #@ ensures \result > 0          # <- FALSE: CPython returns -5
    #@ assigns \nothing
    def caller(self) -> int:
        return self.pos_only(-5)
```

**`[+] Verification SUCCESS! All contracts formally proven.`**
CPython: `C().caller()` returns **-5**.

BOTH DIRECTIONS MEASURED: the FALSE claim proves; the TRUE claim (`\result == -5`) does not.
And the positive control holds — `self.pos_only(5)` proves `\result > 0`, correctly.

## THE EMISSION SHOWS THE METHOD DECLARED **TWICE**, WITH DIFFERENT CONTRACTS

```whyml
  val self_pos_only_1 (x0: int) : int
    ensures { (result > 0) }                 (* <- the stub the CALL SITE uses. NO requires. *)

  val c__pos_only (self: c) (x: int) : int
    requires { (x > 0) }                     (* <- the correct declaration, unused here *)
    ensures  { (result > 0) }
```

The dotted call path synthesizes its OWN stub, builds an `ensures` suffix from the callee's
declared postcondition, and **has no requires suffix at all** — there is no requires registry
anywhere in the emitter, while `_module_method_result_ensures` is built and threaded. So the
callee's POSTCONDITION is assumed UNCONDITIONALLY and its PRECONDITION is silently discarded.

**THIS IS THE ONE DIRECTION THAT IS ALWAYS UNSOUND.** Dropping both clauses would be
fail-closed (nothing could be concluded). Dropping the precondition while KEEPING the
postcondition is the exact combination that turns a conditional guarantee into an
unconditional one.

## SCOPE — MEASURED, AND NARROWER THAN IT LOOKS TODAY

  * A plain cross-module import is **NOT** affected: `from lib import pos_only` emits
    `val pos_only (x: int) : int requires { (x > 0) } ensures { (result > 0) }` and the
    caller correctly FAILS to prove. Measured.
  * A dotted call to an IMPORTED class method drops BOTH clauses (`val h_pos_only_1 (x0: int)
    : int`, no contract at all) — fail-closed. Measured.
  * A SAME-module non-stubbed method is a real `let` and its `requires` is discharged at the
    call site. Measured.
  * **The live carrier is a STUBBED same-module method with a real precondition** — a
    `\trusted` method being the clearest case.

**THE SELF-ANNOTATION MIRROR IS NOT EXPOSED TODAY, AND I CHECKED RATHER THAN ASSUMED:** all
**459** `\trusted` markers in `src/self-annotate/src` carry `requires True`, so there is no
precondition to lose. That is a FRAGILE SAFETY, not a guarantee — the moment any `\trusted`
stub is given a real precondition, every `self.m(...)` call site stops enforcing it, silently
and with no plane to notice.

## THE REPAIR SHAPE

Give the synthesized stub a `requires` suffix built the same way the `ensures` suffix already
is. If a callee's precondition cannot be rendered at the call site (a term the caller cannot
express), the honest fallback is to DROP THE ENSURES TOO — an opaque stub is fail-closed,
which is what the imported-class-method path already does correctly. **Never keep the
postcondition without the precondition.**

A plane is warranted and would be cheap: for every synthesized callee stub, assert that it
carries a `requires` whenever the source contract has a non-trivial one.
