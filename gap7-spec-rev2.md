# gap7-spec-rev2.md — the method-call-contract-gap: void/mutating method calls on record-instance locals

**Date:** 2026-06-08
**Status:** P1.5+P1+P2 IMPLEMENTED (record-var case). O0 region-feasibility PROVEN (P1.5 probe: an
abstract `val … writes {self.x} ensures {self.x = old self.x + 1}` round-trips the mutation to the
caller — records ARE mutable regions). Maps `_module_method_writes` + `_module_method_field_old_ensures`
built from the same `contracts.*` as the method's `let` (O2 no-drift). Reproducer 0652 proves
`c.inc(); return c.x == 1`; value-case companion 0653 unchanged; O3 holds (false ensures fails the
callee); corpus 610/610. **P3 (self.method() / module-global void-mutation) PENDING** — confirmed still
broken (`self.inc()` in a sibling → opaque), but extending the `self.`-branch touches every
`self.method()` call (broad os blast radius) → being measured separately.
**Owner:** PyCSL tool ([TOOL], `src/pycsl/**`)
**Origin:** 07-2333-req-rev2 §1.5 Gap 7 (the lone genuinely-open item), re-confirmed on `main`
(`9cda78f`). Unblocks class-based stub demos (StringIO / ast.NodeVisitor) flagged by the
[[pycsl-method-call-contract-gap]] memory.

**Revision 2 — changes from review.** Three substantive additions, all at the soundness boundary the
original treated as automatic:
1. **A new P1.5 feasibility probe** proves the *genuinely new capability* — mutation **through an
   abstract `val`** (`writes {self.x}` + `old self.x` round-tripping to the caller) — on the minimal
   `Counter` reproducer **before** P3 generalizes. The value case (`b_get_0`) proves the *plumbing*
   (pass self, append ensures) but **writes nothing**, so it gives no evidence the *mutation* works.
   This is the analogue of the seq-model "prove the rebind first" (07-1732 #8): the region story is
   exactly where that work got bitten.
2. **Option (A)'s "mechanical translation" is reframed as a real sync obligation**, with an acceptance
   check that the op's `writes`/`ensures` are *generated from* the method's own contract maps and
   cannot drift — because a mis-translated op passes the method's own proof and still misleads the
   caller (so old acceptance #2 is necessary but **not sufficient**).
3. **Aliased mutable-record locals are reclassified fail-loud-or-defer**, not "a separate concern" —
   under the doctrine "rejected by Why3" is acceptable, "silently wrong" is not, and the spec now
   asserts which.
Plus: the §5 count is split (P2-target record-var calls vs P3 self/module-global), P0 adds a passing
value-case companion, and P1 is required to partition cleanly the method that sits in **both** ensures
maps.

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
- With no `field_spec`, the op gets **no `self` param**, **no `writes`**, **no `ensures`**.
- Result: `val c_inc_0 () : unit` — a pure no-op from the caller's perspective.

**Root cause:** the dotted-call resolution only propagates `\result`-referencing ensures. A void
mutating method's contract lives in its **`assigns` (→ Why3 `writes`)** and its **`\old`-relating
ensures** — neither of which is captured or emitted.

**What the value case does and does NOT establish (rev2).** It establishes the *plumbing*: that
`field_spec` can prepend `(self: class)`, pass the receiver, and append an ensures. It establishes
**nothing** about a `writes` clause taking effect, because `b_get_0` writes nothing. The void fix's
real content — that an abstract `val` with `writes {self.x}` + `old self.x` actually mutates the
caller's `c` — is **new** and is gated by P1.5 (§6), not assumed from the value case.

## 3. The fix

Make a void/mutating record-method call lower to an op that carries the method's **frame + mutating
contract**, receiver passed as `self`:
```whyml
  val counter_inc_0 (self: counter) : unit
    writes  { self.x }                          (* from `assigns self.x` *)
    ensures { self.x = old self.x + 1 }          (* from `ensures self.x == \old(self.x)+1` *)
  …
  let driver () : int = … (counter_inc_0 c); !(c).x   (* c.x is now old+1 = 1 → proves *)
```

### 3.1 The load-bearing precondition (rev2): records must be mutable regions
For `writes {self.x}` + `old self.x` to mutate the caller's `c`, three things must line up — and the
original treated them as automatic:
- **`counter` must lower as a mutable-region record** (a record with a *mutable* field), so `c` holds
  a region Why3 tracks. If it lowers as an immutable value or `x` as a non-region field, `writes
  {self.x}` is rejected or vacuous and `old self.x` does not relate to the post-state the caller reads.
- **`writes {self.x}` must frame the same region** the caller reads at `!(c).x`.
- **`old self.x`** in the abstract `val`'s `ensures` must equal the caller's pre-call `c.x`.

Whether PyCSL's records satisfy this is **the** open question, and it is exactly the region-discipline
wall the seq model hit (07-1732 #8: you cannot rebind a `ref (array int)`). It is decided by P1.5
(§6) on the reproducer **before** any generalization. If records are *not* mutable regions, that is a
fail-loud prerequisite finding that blocks the fix (not something to discover at P4).

### 3.2 What has to change (three captured-and-emitted pieces)
1. **Capture (Module5):** per method, its `assigns` targets (`_module_method_writes[key]`) and its
   **field-referencing ensures that do NOT mention `\result`** (a new `_module_method_field_ensures`,
   distinct from `_field_result_ensures`). **Partition obligation (rev2):** a method with *both* a
   `\result` ensures and an `\old`-relating field ensures (the §8 non-void-mutating case) belongs in
   **both** maps; P1 must file each clause by its kind, not the method wholesale, or P2 sees a partial
   contract.
2. **Resolve (`_resolve_dotted_signature`):** for a record-var (or `self`-field, or module-global)
   receiver whose method is void/mutating, set `field_spec` from the new map (so `self` is passed) and
   surface the `writes` set + the mutating ensures.
3. **Emit (`_handle_dotted_call`):** when the resolved method has `writes`, add a `writes {self.f; …}`
   clause to the abstract `val`, and add the `old`-relating ensures (`\old(self.f)` → `old self.f`),
   generalizing the existing `field_spec` → `(self: class)` + ensures path.

### 3.3 Design choice — extend the abstract-op (A) vs emit a real call (B)
- **(A) abstract op with `writes` + `ensures`** *(recommended for v1)* — mirrors the value-case
  mechanism; smallest, most consistent change. **But the op is a hand-built restatement of the
  method's contract**, so soundness holds only while the op's `writes`+`ensures` *stay equal* to the
  method's `assigns`+`ensures`. That equality is a **standing sync obligation**, not a one-time
  "mechanical translation" (rev2 §4): the op and the verified `let counter__inc` must be generated
  from the *same* contract maps so they cannot drift.
- **(B) real call `counter__inc c`** — emit the actual verified method call; Why3's modular
  verification applies the contract directly. More faithful (no duplication, no drift), larger change
  to the call-emission path. The record-local analogue of the `#@ no_inline` boundary.

Recommend **(A)** for v1 (consistent with the working value case, smaller blast radius); the sync check
(acceptance #2b) bounds (A)'s drift risk. Revisit (B) if drift bugs appear.

## 4. Soundness (rev2 — three obligations, not one)

The method body (`let counter__inc (self: counter)`) is verified against its own `assigns`/`ensures`
independently; the call reuses that contract via the op. Soundness requires **all three**:

- **O1 — frame equality.** The op's `writes` must **equal** the method's `assigns`. An
  under-approximation is **unsound** (it preserves a field the method mutated); an over-approximation
  only loses precision. (As original.)
- **O2 — contract sync (rev2).** The op's `writes`+`ensures` must be **generated from the same
  contract maps** the method's `let` is verified against, so they cannot diverge. A method with a
  *correct* ensures but a *mis-translated op* passes its own proof (O3 below) **and still misleads the
  caller** — so O3 is necessary but not sufficient; O2 closes the gap. The check: re-derive the op's
  clauses from the maps at emit time; assert byte-equality with what the `let` consumed.
- **O3 — anti-`\trusted` invariant.** A deliberately-false method `ensures` must fail the **method's
  own** proof (the `let`), never silently propagate. (As original.)

- **O0 — region feasibility (rev2, prerequisite).** Records lower as mutable regions and the
  `writes`+`old` round-trip actually holds (§3.1). Decided by P1.5 before P2/P3. If O0 fails, the fix
  is blocked and reported fail-loud — not worked around.

## 5. Blast radius & gating (rev2 — count split)

Statement-position `recordvar.method()` calls in the corpus, separated by what each phase targets:
- **P2 target — record-*var* void/mutating calls** (the `c.inc()` shape): *N₂* (to be measured at P1;
  the number that gates P2).
- **P3 target — `self.<field>.<method>()` and module-global receivers:** *N₃*. The original's "~19
  (some may be `self.`/module-global, already handled)" conflated these; reconcile at P1 — if `self.`
  void-mutating calls were truly already handled, P3 would not need to add them, so the "already
  handled" claim must be **verified, not assumed**, and any not-handled cases counted under P3.

Today many such calls are silent no-ops that "pass" only because the caller's contract never depended
on the mutation. **Switching to the faithful op may expose real unproven goals in callers that
*should* have depended on the mutation — that is correct, but must be measured.** Gate: full
`bin/run-reference-tests.sh --pycsl` byte-diff/PASS, os formal_0001 18/18, stdlib-coverage +
doc-coherency green.

## 6. Phasing (rev2 — P1.5 added)

| Phase | Delivers | Gate |
|---|---|---|
| **P0** | reproducer driver (`Counter`) as an XFAIL corpus test **+ a passing value-case companion** (`Box.get`) so a regression in the path being extended is caught | XFAIL FAILS today; companion PASSES |
| **P1** | capture `assigns`→writes + non-result field ensures (Module5 maps); **partition the both-maps method cleanly**; measure *N₂*/*N₃* (§5) | dump shows maps populated for `inc`; counts reported |
| **P1.5** | **feasibility probe (O0):** hand-confirm on the reproducer that `counter` is a mutable-region record and `writes {self.x}` + `old self.x` round-trips so the caller sees `c.x == old+1` | the minimal `counter_inc_0` op PROVES the +1 at the call site; **if records aren't mutable regions, STOP and report (fail-loud)** |
| **P2** | resolve + emit `writes`+`ensures` for void/mutating record-**var** calls (A); wire O2 sync check | reproducer PROVES (XFAIL→PASS); O2 check green |
| **P3** | extend to `self.<field>.<method>()` and module-global receivers | targeted drivers prove; the *N₃* cases covered |
| **P4** | full corpus sweep; triage newly-exposed caller goals | corpus PASS (or each new fail understood + fixed/annotated) |

P1.5 gates P2: no general emission until the round-trip is proven on the minimal case.

## 7. Acceptance criteria (rev2)

1. `c = Counter(); c.inc(); return c.x` proves `\result == 1` (P2); the real `let counter__inc` is
   still emitted + verified.
2. **(O3)** A void method with a **false** mutating ensures fails the **method's own** proof (not the
   caller).
2b. **(O2, rev2)** The emitted op's `writes`/`ensures` are generated from — and assert-equal to — the
   contract maps the method's `let` is verified against (no drift); a synthetic test that perturbs the
   op's clauses away from the method's is caught.
3. **(O0, rev2)** P1.5 demonstrates the `writes`+`old` round-trip on the reproducer; if records are not
   mutable regions, the blocker is reported, not worked around.
4. Corpus byte-identical for files with no statement-position record-var method call; the *N₂*/*N₃*
   affected either still PASS or have an understood, fixed/annotated new goal (P4).
5. **(rev2)** Aliased mutable-record locals (`a = b; a.inc()`) are **fail-loud or deferred**, never
   silently wrong (§8); a driver that aliases is expected to be rejected by Why3 or explicitly
   deferred.
6. New corpus driver(s) + traceability; no new `#@` directive (no user-facing doc-coherency surface),
   though the new internal `_module_method_field_ensures` map + its partition invariant (§3.2) are
   covered by P1's dump check.

## 8. Out of scope / notes (rev2)

- **Non-void mutating methods** (`x = c.step()` that returns AND mutates) — combine the value-case
  result-ensures with the new writes+mutating-ensures; this method sits in **both** ensures maps
  (§3.2), so P1's partition must already file it correctly even though emission is folded in after P2.
- **Aliasing (reclassified):** two record locals `a = b` then `a.inc()` is **not** merely "a separate
  concern." Once (A) makes `c.inc()` mutate `c`'s region, aliasing becomes a *soundness* question: the
  seq-model finding (07-1732 #8 — region-bearing values resist rebinding/aliasing) suggests Why3 may
  **reject** an aliased mutable-record binding outright. Under the doctrine that is the acceptable
  outcome; **silently mutating one alias and not the other is not.** A driver that aliases must
  fail-loud or be deferred — assert which when one appears; do not let it pass quietly.
- Distinct from (but adjacent to) [[pycsl-method-call-contract-gap]]'s A2c (field-referencing *result*
  ensures), already closed for the value case — Gap 7 is the **void/mutating** sibling.

> **In one line (rev2):** a void state-mutating method on a record-instance local lowers to an opaque
> `val c_inc_0 () : unit` because the resolver only propagates `\result`-referencing ensures — so the
> mutation vanishes; the fix captures the method's `assigns`(→`writes`) and `\old`-relating ensures and
> emits them on a `(self: class)`-taking op (the value case's `field_spec` path), but the genuinely new
> capability is **mutation through an abstract `val`**, which the value case never exercised — so rev2
> gates it behind a P1.5 region-feasibility probe (O0), bounds option (A)'s contract-drift with a sync
> check (O2), and reclassifies aliased mutable-record locals as fail-loud-or-defer, never silently wrong.
