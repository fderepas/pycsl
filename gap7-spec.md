# gap7-spec.md — the method-call-contract-gap: void/mutating method calls on record-instance locals

**Date:** 2026-06-08
**Status:** Spec (for review — no code changed)
**Owner:** PyCSL tool ([TOOL], `src/pycsl/**`)
**Origin:** 07-2333-req-rev2 §1.5 Gap 7 (the lone genuinely-open item of that req), re-confirmed on
`main` (`9cda78f`). Unblocks class-based stub demos (StringIO / ast.NodeVisitor) flagged by the
[[pycsl-method-call-contract-gap]] memory.

---

## 1. The bug

A **void, state-mutating method called in statement position on a record-instance local** does not
mutate the instance — the call lowers to an opaque op with no receiver, no frame, no contract.

Reproducer (`/tmp/gap7.py`, FAILS today):
```python
class Counter:
    #@ assigns self.x
    #@ ensures self.x == 0
    def __init__(self) -> None:
        self.x: int = 0
    #@ assigns self.x
    #@ ensures self.x == \old(self.x) + 1
    def inc(self) -> None:
        self.x = self.x + 1

#@ ensures \result == 1
def driver() -> int:
    c = Counter()
    c.inc()          # <-- statement-position, void, mutating
    return c.x       # proves \result == 0, NOT 1  → postcondition FAILS
```

Emitted WhyML (the smoking gun):
```whyml
  val c_inc_0 () : unit                       (* opaque: NO self param, NO writes, NO ensures *)
  let counter__inc (self: counter) : unit = … (* the REAL method — verified, but NEVER CALLED *)
  let driver () : int =
    …
    let _ = (c_inc_0 ()) in ();               (* calls the opaque op; c is untouched *)
    !(c).x                                     (* still 0 *)
```
`c.inc()` should lower to a call that mutates `c`; instead it's a no-op on an unrelated opaque symbol.

## 2. Why the *value* case already works — and the void case doesn't

A **value-returning** record method already lowers correctly. `b.get()` (`ensures \result == self.x`):
```whyml
  val b_get_0 (self: box) : int               (* takes self; carries the ensures *)
  let driver () : int = … (b_get_0 b)          (* passes b; \result == b.x proves *)
```
The machinery: `_resolve_dotted_signature` (`expressions.py`) detects the record-var receiver and, **iff
the method has a `\result`-referencing field ensures**, sets `field_spec = (receiver, class, field_ens)`
(from `_module_method_field_result_ensures`). `_handle_dotted_call` then (i) prepends `(self: class)` to
the op's params, (ii) passes the receiver, (iii) appends the ensures (`expressions.py:770–780`).

**The void method falls through every check:**
- `inc`'s contract is `assigns self.x` + `ensures self.x == \old(self.x) + 1` — it references
  `self.x` but **NOT `\result`** (it returns `None`). So it is absent from
  `_module_method_field_result_ensures` → `field_ens` empty → **`field_spec` stays `None`**.
- With no `field_spec`, the op gets **no `self` param** (so the receiver isn't passed), **no `writes`
  clause** (so the frame doesn't say `c.x` changes), and **no ensures** (so the +1 is invisible).
- Result: `val c_inc_0 () : unit` — a pure no-op from the caller's perspective.

**Root cause:** the dotted-call resolution only propagates `\result`-referencing ensures. A void
mutating method's contract lives in its **`assigns` (→ Why3 `writes`)** and its **`\old`-relating
ensures** — neither of which is captured or emitted.

## 3. The fix

Make a void/mutating record-method call lower to an op that carries the method's **frame + mutating
contract**, with the receiver passed as `self`:
```whyml
  val counter_inc_0 (self: counter) : unit
    writes  { self.x }                         (* from `assigns self.x` *)
    ensures { self.x = old self.x + 1 }         (* from `ensures self.x == \old(self.x)+1` *)
  …
  let driver () : int = … (counter_inc_0 c); !(c).x   (* c.x is now old+1 = 1 → proves *)
```
`old` in an abstract `val`'s `ensures` refers to the pre-call state; combined with `writes {self.x}`,
the call mutates `c.x` exactly per the method's contract. (Why3 supports `writes` + `old` on abstract
`val`s — this is the standard "specified, not inlined" boundary, the same idea as `#@ no_inline`.)

### What has to change (three captured-and-emitted pieces)
1. **Capture (Module5 / the method-contract maps):** record, per method, its `assigns` targets
   (`_module_method_writes[key]`) and its **field-referencing ensures that do NOT mention `\result`**
   (a new `_module_method_field_ensures`, distinct from the existing `_field_result_ensures`).
2. **Resolve (`_resolve_dotted_signature`):** for a record-var (or `self`-field, or module-global)
   receiver whose method is void/mutating, set `field_spec` from the new map (so `self` is passed) and
   surface the `writes` set + the mutating ensures.
3. **Emit (`_handle_dotted_call`):** when the resolved method has `writes`, add a `writes { self.f; … }`
   clause to the abstract `val`, and add the `old`-relating ensures (translating `\old(self.f)` →
   `old self.f`). This generalizes the existing `field_spec` → `(self: class)` + ensures path.

### Design choice — extend the abstract-op (A) vs emit a real call (B)
- **(A) abstract op with `writes` + `ensures`** *(recommended)* — mirrors the existing value-case
  mechanism (`b_get_0`); smallest, most consistent change. The op is opaque but its contract captures
  the mutation; the real `let counter__inc` is still verified separately, so soundness holds iff the
  op's `writes`+`ensures` equal the method's `assigns`+`ensures` (mechanical translation).
- **(B) real call `counter__inc c`** — emit the actual verified method call (no opaque op), letting
  Why3's modular verification apply the contract. More faithful (no contract duplication), but a larger
  change to the call-emission path and a bigger behavioural diff. This is the record-local analogue of
  the `#@ no_inline` boundary.

Recommend **(A)** for v1 (consistent with the working value case, smaller blast radius); revisit (B) if
contract-duplication bugs appear.

## 4. Soundness
The method body (`let counter__inc (self: counter)`) is verified against its own `assigns`/`ensures`
independently. The call site reuses that contract via the op's `writes`+`ensures`. Soundness gate: the
op's `writes` must equal the method's `assigns` (an under-approximation would unsoundly preserve a
mutated field; an over-approximation only loses precision), and the op's `ensures` must be exactly the
method's field ensures with `\old`→`old`. A deliberately-false method `ensures` must fail the **method's
own** proof (the `let`), not silently propagate — the anti-`\trusted` invariant.

## 5. Blast radius & gating
~19 corpus tests have a statement-position `recordvar.method()` call (upper bound; some may be `self.`
or module-global, already handled). Today many of those calls are silent no-ops that "pass" only
because the caller's contract never depended on the mutation. **Switching to the faithful op may expose
real unproven goals in callers that *should* have depended on the mutation — that is correct, but must
be measured.** Gate: full `bin/run-reference-tests.sh --pycsl` byte-diff/PASS, os formal_0001 18/18,
stdlib-coverage + doc-coherency green.

## 6. Phasing
| Phase | Delivers | Gate |
|---|---|---|
| **P0** | reproducer driver (the `Counter` above) added as an XFAIL corpus test | it FAILS today (documents the gap) |
| **P1** | capture `assigns`→writes + non-result field ensures (Module5 maps) | dump shows the maps populated for `inc` |
| **P2** | resolve + emit `writes`+`ensures` for void/mutating record-var calls (A) | the reproducer PROVES; XFAIL→PASS |
| **P3** | extend to `self.<field>.<method>()` and module-global receivers (same opaque-op path) | targeted drivers prove |
| **P4** | full corpus sweep; triage any newly-exposed caller goals | corpus PASS (or each new fail understood + fixed/annotated) |

## 7. Acceptance criteria
1. `c = Counter(); c.inc(); return c.x` proves `\result == 1` (P2); the real `let counter__inc` is still
   emitted + verified.
2. A void method with a **false** mutating ensures fails the **method's own** proof (not the caller).
3. Corpus byte-identical for files with no statement-position record-var method call; the ~19 with one
   either still PASS or have an understood, fixed/annotated new goal (P4).
4. New corpus driver(s) + traceability; no new `#@` directive (so no doc-coherency surface burden).

## 8. Out of scope / notes
- **Non-void mutating methods** (`x = c.step()` that both returns AND mutates) — combine the value-case
  result-ensures with the new writes+mutating-ensures; fold in once P2 lands.
- **Aliasing**: two record locals `a = b` then `a.inc()` — the seq/array region rules apply; a record
  with mutable fields aliased across locals is a separate concern, flag if a driver hits it.
- This is distinct from (but adjacent to) [[pycsl-method-call-contract-gap]]'s A2c (field-referencing
  *result* ensures), which is already closed for the value case — Gap 7 is the **void/mutating** sibling.

> **In one line:** a void state-mutating method on a record-instance local lowers to an opaque
> `val c_inc_0 () : unit` (no self, no `writes`, no `ensures`) because the resolver only propagates
> `\result`-referencing ensures — so the mutation vanishes; the fix captures the method's `assigns`
> (→ `writes`) and `\old`-relating ensures and emits them on a `(self: class)`-taking op (the same
> field_spec path the working value case uses), gated by a full corpus sweep over the ~19 affected tests.
