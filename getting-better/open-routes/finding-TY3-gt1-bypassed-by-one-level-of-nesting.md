# FINDING (NOT A ROUTE) — THE **GT1 `Any` REFUSAL IS BYPASSED BY ONE LEVEL OF NESTING**,
# BUT THE PATH IT OPENS IS FAIL-CLOSED AT THE PROOF LEVEL TODAY

**CLASSIFIED AS A CERTIFIED BOUNDARY WITH A NAMED, DATED REOPENING CONDITION — NOT a
soundness route, and the reason is measured, not argued.** Found by the `continue`-census
generator (its ranked candidate #2). Gen #16.

>>> **"I COULD NOT EXPLOIT IT" IS NOT "IT IS SAFE" — SO HERE IS THE FENCE, NAMED.**

## WHAT IS TRUE (all measured at HEAD, PEP 695 syntax)

`frontend/monomorphize.apply_monomorphization` collects `instantiations` ONCE and that one
set feeds FIVE consumers: GT4 polymorphic-recursion, the **GT1 `Any` refusal**, the **GT2
bounds check**, STEP D emit-specializations, and STEP E classification. `_type_str`
(`monomorphize.py:248-249`) answers **`None`** for a `Subscript`, i.e. a NESTED generic
argument, because nested instantiation "is not supported in this delivery" — a skip written
for the BUILD step. The `continue`-census signature again: the skip is correct for what it
was written for and silently narrows four other consumers.

Instrumented the two collectors from a wrapper (no source edit):

| program | `instantiations` collected | verdict |
|---|---|---|
| `b: Box[int]` | `[('Box','int')]` | verifies; **`\result == 5` PROVES** |
| `b: Box[Any]` | `[('Box','Any')]` | **REFUSED — `PYCSL-TY3-GT1`** (the guard is ALIVE) |
| `outer: Wrap[Box[int]]` | `[('Box','int')]` — **`Wrap` ABSENT** | type-checks |
| **`outer: Wrap[Box[Any]]`** | `[('Box','int')]` — **the `Any` IS NOWHERE** | **NOT refused** |

So the exact `Any` that GT1 rejects at the top level **passes unseen one level down**, and
with it the GT2 bound obligation and the GT8 classification for `Wrap`.

## WHY IT IS **NOT** A ROUTE — THE MEASUREMENT THAT STOPPED ME CLAIMING ONE

The bypassed program **cannot prove anything at all**. With the prover ON (not
`--no-proof`):

* `Wrap[Box[Any]]` driver asserting the **TRUE** fact `\result == 5` (CPython agrees:
  `Wrap(Box(5)).unwrap().get() == 5`) → **FAILS**.
* the **FALSE** twin `\result == 99` → **FAILS**.

**A channel that cannot prove a TRUE fact cannot prove a FALSE one**, so no unsoundness is
reachable through this bypass today. The fence is structural and named: a nested
instantiation gets **no specialization emitted** (STEP D never sees it), so the chained call
`outer.unwrap().get()` resolves to something the prover cannot use.

>>> **AND NOTE HOW NEARLY THIS WAS MIS-REPORTED.** The nested cases show
>>> `Verification SUCCESS` under `--no-proof`, which is a TYPE-CHECK, not a proof. Read
>>> alone it looks exactly like "the exploit verifies". The rule that caught it is the
>>> campaign's own: **build the TRUE-claim control and check the channel can prove
>>> ANYTHING before believing a pass.**

## REOPENING CONDITION — THIS IS THE PART THAT MATTERS

**The moment nested generic instantiation is IMPLEMENTED, this bypass becomes LIVE, and it
becomes live SILENTLY.** Whoever lifts the `Subscript -> return None` restriction inherits a
GT1 refusal and a GT2 bound check that have never seen a nested argument. The order is not
optional:

1. Make `_type_str` (or its replacement) **recurse into nested subscripts and surface EVERY
   type argument at every depth** into `instantiations`, BEFORE any specialization for
   nested generics is emitted.
2. Re-run the four-row table above. `Wrap[Box[Any]]` MUST become `PYCSL-TY3-GT1`.
3. Then, and only then, implement the emit half.

Doing (3) before (1) ships the `Any` bypass with a working prover behind it — which is
precisely route #96's shape (*the one cell of the 2×2 nobody writes is the cell no test
covers*), one feature ahead of time.

## TWO COLLATERAL FACTS WORTH THE NEXT GENERATION'S TIME

* **`_collect_instantiations` — the IR-side collector — returned `[]` in EVERY shape
  tested.** Every instantiation found came from `_collect_instantiations_ast`. One of the
  two collectors contributed nothing at all here; whether it is dead in general, or merely
  blind to the annotation forms tested, is **UNMEASURED** and worth a census before anyone
  relies on it.
* **PEP 484 `class Box(Generic[T])` DOES NOT REGISTER AS GENERIC AT ALL.** It produces no
  `type_params`, so `_collect_generic_decls` returns empty and `apply_monomorphization`
  early-returns: the whole TY3 machinery — GT1, GT2, GT3, GT4 included — is a **silent
  no-op** for the PEP 484 spelling. Only PEP 695 `class Box[T]:` activates it. Measured:
  `Box(Generic[T])` with `b: Box[Any]` **verifies and proves `\result == 5`** with no GT1
  refusal, while the PEP 695 spelling of the same program is refused. That asymmetry is
  undocumented, and a user writing the older, far more common spelling gets none of the
  typing gates. **It is not exploited here and is NOT claimed as a route** — it needs the
  same TRUE-claim control this file's main finding needed.

## COVERAGE NOTE — WHY NONE OF THIS WAS EVER GOING TO BE CAUGHT BY A GATE

**There is not one file in the entire test-suite using `TypeVar` or `Generic[`** (measured:
`grep -rln` over `test-suite/`, zero hits in both corpora). The monomorphization machinery —
five gates, ~700 lines — has **ZERO in-tree corpus coverage**, so every one of its guards is
a guard whose population is empty. That is the route-#96 lesson stated as a standing
condition rather than as a past event.
