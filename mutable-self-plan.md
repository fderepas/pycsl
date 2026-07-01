# mutable-self-plan.md — make `assigns` a CHECKED frame on shared mutable state

> **Purpose.** Make PyCSL model a method's mutation of persistent state as a
> **shared mutable location** whose writes are **visible to callers** and **checked
> against a `writes`/`assigns` frame**. Today a record `self`/param is value-
> semantic: a method's field write mutates a local copy, is invisible to callers,
> and satisfies any `assigns` (even `\nothing`). This plan is the prerequisite
> `a3-plan.md §9` identified for A3 (transpiler-state framing) — and, independently,
> it **closes a soundness hole**: `assigns` is presently an *unchecked declaration*.
>
> **Where it sits.** `a3-plan.md` Slice-0 falsified the "reuse the existing
> `assigns self.field` machinery" premise: that machinery
> (`_build_method_writes_map`) emits `writes {self.x}` onto a method's **abstract-op
> stub** (so callers frame it), but the **concrete `let` body** is emitted with a
> value `self` and is never checked to write only its declared locations. So a
> state-mutating handler's `assigns` is vacuous. This plan makes the frame real.
>
> **Two motivations, ranked.**
> 1. **Soundness (primary).** `assigns \nothing` currently VERIFIES on a method that
>    mutates `self.n` *or a global* (`a3-plan.md §9`). A caller trusting that frame
>    is misled. Checked `assigns` removes the hole.
> 2. **Capability (secondary).** It unblocks A3 → scaling L5 to state-mutating
>    emitter handlers.
>
> **Convention.** Named repo-root plan file. Opt-in (a marker), so default emission
> and every existing proof stay **byte-identical**; `writes`-checking + non-vacuity
> gates on witnesses. Slice-0 falsifiable PoC first.

---

## 0. Grounding (measured)

- **Value-semantic self/params.** `functions.py:68` — "mutating a record param is
  out of scope (value semantics)"; a method emits `(self: <class>)` (a value param,
  `functions.py:298`). A field write `self.x = …` lowers to a **local** mutable
  binding — allowed by Why3, invisible to callers, needing no `writes`.
- **`assigns→writes` exists only on the stub.** `_build_method_writes_map`
  (`functions.py:1293`) maps `#@ assigns self.x → writes {self.x}` and attaches it
  to the method's **abstract-op** `val` (`gap7-spec-rev2`, the OS `assigns self.disk`
  path). The concrete `let` body carries **no** `writes`, so Why3 never checks it.
- **Falsification (`a3-plan.md §9`).** `assigns \nothing` PASSES on a body that
  mutates `self.n` and on one mutating a global; the mutation does **not** escape to
  a caller (`s=St(0); s.bump(); \result==s.n==1` FAILS). Value-semantics, confirmed.

**Why3 already supports the target.** A record with `mutable` fields (or a global
`ref`) is a real, aliasable, writable location; a function writing it MUST declare
`writes { r.f }`, and Why3 **checks** the body writes only what it declares. The gap
is purely that PyCSL emits value records + omits the body `writes` clause.

---

## 1. Objective & success criterion

**Objective.** For a class/state marked mutable, PyCSL emits (a) a record with
`mutable` fields (or global `ref`s), (b) `self.x = v` as a real write to that
shared location, and (c) a `writes { self.x }` clause **on the concrete method
body**, derived from `#@ assigns self.x` — so Why3 **checks** the frame.

**Done =**
- a witness method that writes `self.n` verifies with `#@ assigns self.n`, and the
  mutation **escapes** (`s.bump(); \result == s.n` proves the new value);
- **non-vacuity holds**: the same body with `#@ assigns \nothing` (or omitting a
  written field) now **FAILS** — the soundness hole is closed for the marked class;
- **byte-diff 0** across the 627-file corpus (the feature is opt-in; unmarked
  records stay value-semantic, byte-identical);
- no new axioms; the residual trust base is unchanged.

---

## 2. Design

### 2.1 The core (independent of representation)
Three coordinated changes for a mutable-marked location:
1. **A shared mutable location** for the state (so a write is not local).
2. **`self.x = v` → a write to that location** (`<-` on a mutable field / `:=` on a ref).
3. **`writes { … }` on the concrete `let`** (reuse `_build_method_writes_map`), so
   Why3 checks the body writes only its declared frame → sound + non-vacuous.

### 2.2 Two representations (pick per §7)

| | **A — mutable record** | **B — global refs (singleton)** |
|---|---|---|
| Model | record type with `mutable` fields; `self` passed by reference | one Why3 global `ref` per state field; `self.x` → that ref |
| `self.x = v` | `self.x <- v` | `x_ref := v` |
| Frame | `writes { self.x }` | `writes { x_ref }` |
| Escapes to caller | yes (aliased region) | yes (global) |
| Generality | any object, multiple instances | singleton state only |
| **Why3 cost** | **regions/aliasing** — no two mutable aliases of one region; a method taking a mutable record + calling another that writes it needs care | none — globals are unaliased; simplest |

**Recommendation.** The transpiler/emitter is a **singleton** (one instance drives a
file), so **B (global refs)** is the faithful, simplest first target — it sidesteps
Why3's region system entirely and directly makes `assigns self._x` a checked
`writes { _x_ref }`. Ship B first (it fully unblocks A3 for the singleton emitter);
pursue A (general mutable objects, with region handling) only if a multi-instance
use case appears.

### 2.3 Opt-in marker (byte-safety)
A class-level `#@ mutable_state` (or reuse an existing marker) opts a class into
this model. **Unmarked classes are unchanged** — value-semantic, byte-identical, so
the 627-corpus and every existing proof are untouched. This is mandatory: turning
checked-`assigns` on globally would fail every corpus method that currently
under-declares its frame (a proof regression, not just a byte diff).

---

## 3. Work items

| WI | Item | Gate |
|---|---|---|
| **M.1** | **Slice-0 PoC** (§6): a `#@ mutable_state` class + `self.n = self.n+1`, global-ref (B) lowering + `writes` on the body. Confirm: mutation ESCAPES; `assigns self.n` proves; `assigns \nothing` FAILS. | PoC flips the §9 falsification |
| **M.2** | The `#@ mutable_state` marker (front-end parse + IR flag); default off. | marker parsed; absent ⇒ unchanged |
| **M.3** | Global-ref (B) emission for a marked class's fields (`val … : ref <ty>` per field, initialized); `self.x` read/write → ref deref/assign. | reads/writes lower to the ref |
| **M.4** | Emit `writes { … }` on the **concrete** method `let` from `_build_method_writes_map` (today it feeds only the abstract-op stub). | Why3 checks the body frame |
| **M.5** | **Witnesses** (`mutable-state-witnesses.py`): escape, non-vacuity (`\nothing` fails), multi-field, a method calling a framed mutator inherits the write. | all SUCCESS/FAIL as intended |
| **M.6** | **Byte-diff gate**: unmarked records/corpus byte-identical; marked class emission is new. | corpus byte-diff 0 |
| **M.7** | Hand off to A3: mark the transpiler-state class, re-run `a3-plan.md` Slice-0 — the mutation-only witness now proves a CHECKED `assigns`. | A3 Slice-0 flips to green |
| **M.8** | (Deferred) Representation A (mutable record + Why3 regions) for general multi-instance objects. | separate; not required for A3 |

---

## 4. Gate criteria

1. **Byte-identical** on the 627-file sweep — opt-in; unmarked code unchanged.
2. **Escape**: a marked-class mutation is visible to the caller (the §9 escape probe
   flips FAILED→SUCCESS).
3. **Non-vacuity / soundness**: `assigns \nothing` (or an omitted field) on a
   mutating marked-class body now **FAILS** — the hole is closed for marked classes.
4. **Frame inheritance**: a method calling a framed mutator inherits its `writes`.
5. **No new axioms**; `Print Assumptions`-style residual unchanged.

---

## 5. Non-goals / honest boundaries

- **Not** a global switch — `assigns`-checking stays **opt-in** (marked classes).
  Making it universal is a soundness upgrade for the whole language but a large,
  proof-breaking migration (every under-declared corpus method) — out of scope here.
- **Not** representation A (general mutable objects) first — Why3 **regions/aliasing**
  make multi-instance mutable records genuinely hard; the singleton global-ref model
  (B) is sufficient for the emitter and avoids that. A is deferred (M.8).
- **Not** A3 itself — this plan delivers *checked mutation frames*; A3 then models
  the specific transpiler-state fields on top (M.7 is the handoff, not A3).
- **Not** value-faithful `ensures` — orthogonal (that's the B3 sibling-value work).

---

## 6. Smallest first experiment (Slice 0)

`mutable-state-witnesses.py`:
```
#@ mutable_state
class St:
    n: int

    #@ assigns self.n
    def bump(self) -> None:
        self.n = self.n + 1        # → n_ref := !n_ref + 1 ; body carries writes { n_ref }

#@ ensures \result == 1
def check() -> int:
    s = St(0); s.bump(); return s.n   # must now PROVE (mutation escapes)
```
plus a non-vacuity twin `#@ assigns \nothing` on `bump` that **must FAIL**.
1. Marker + global-ref lowering + body `writes`.
2. `check` proves (escape); the `\nothing` twin FAILS (soundness).
3. Corpus byte-diff 0.

If 1–3 close, checked mutation-framing is validated and A3 resumes on top (M.7). If
Why3 rejects the shared-ref write pattern (e.g. init/aliasing of the global ref),
that is the precise next scope — still bounded (globals have no region system), and
the fallback (state-mutating handlers stay `\trusted`, enumerated) is unchanged.

---

## 7. Why this is the right foundation

`a3-plan.md §9` proved the emitter-frame route rests on this, and the probes showed
it is *also* a live soundness gap (`assigns \nothing` passes on real mutation). A
checked, opt-in mutable-state model fixes the hole where it matters, is **byte-safe**
by construction (marker-gated), and is **bounded** (global refs, no Why3 regions).
It converts "`assigns` is an unchecked declaration" into "`assigns` is a proven
frame — for state that opts in," which is exactly what A3 and every future
state-mutating verified method need.

---

## 8. SLICE-0 EXECUTION RESULT (2026-07-01) — approach VALIDATED at the Why3 level; PyCSL emission gap located

Ran the §6 Slice-0. **The mutable-state approach is sound** — validated directly at
the Why3 level — and PyCSL's exact emission gap is now pinned.

### 8.1 The target shape PROVES (representation B, global ref) — hand-written `.mlw`, Z3
```
val n : ref int
let bump () : unit  writes { n }  ensures { !n = old !n + 1 }  = n := !n + 1
let chk  () : int   writes { n }  ensures { result = old !n + 1 } = bump (); !n
```
- **Escape**: `chk`'s goal is **Valid** — `bump`'s write is visible to the caller
  (`result = old !n + 1`). A shared module-level `ref` gives caller-visible mutation.
- **Non-vacuity / soundness**: the same `bump` with `writes { }` is **REJECTED** by
  Why3 — *"this expression produces an unlisted write effect."* So a body `writes`
  clause is a **checked** obligation: the very thing `a3-plan.md §9` found missing.

⇒ The plan's premise holds: shared `ref` + a **body** `writes` clause = escape +
checked, non-vacuous frame, with **no Why3 region system** (globals are unaliased).

### 8.2 PyCSL emission gap (why §9's vacuity happens)
- A plain module global `g` is emitted as a **per-function local** `let g = ref 0 in`
  (re-initialized each call), **not** shared state, with **no `writes`** — so a
  mutation is local/invisible and `assigns` is vacuous. This is the direct root of
  the §9 falsification.
- PyCSL **does** have a module-level shared-ref emitter — `_emit_shared_state`
  emits `val g : ref int` — **but** it is the **concurrency** model (`#@ shared g
  protected_by lock_g`, havoc'd at calls per `Module2_Parser:359`, mutex-coupled),
  not clean persistent single-threaded state.
- Records are value-semantic (`functions.py:68`).

### 8.3 Verdict
**Slice-0 succeeds as a proof-of-approach and a gap-locator, not (yet) as PyCSL
emission.** The sound target is confirmed; the remaining work (**M.2–M.4**) is a
bounded, byte-safe feature build:
1. a `#@ mutable_state` marker (opt-in; unmarked code byte-identical);
2. emit a marked class's fields (or a marked global) as **module-level shared
   `ref`s** — either a *new* path or by **de-concurrency-coupling** `_emit_shared_state`
   (drop the havoc/mutex for a non-`protected_by` mutable global);
3. emit `writes { … }` on the **concrete** `let` body from `_build_method_writes_map`
   (today it feeds only the abstract-op stub).
Then re-run this §6 witness in PyCSL: `chk` must prove (escape) and the `\nothing`
twin must FAIL (soundness). That is the M.5/M.7 handoff to A3.

**No code landed** (Why3 target validation + PyCSL probes only). The falsifiable
Slice-0 did its job: the approach is **sound and byte-safe by construction**, the
Why3 mechanics are **confirmed** (escape + checked non-vacuous writes), and the
build is now a precise, bounded M.2–M.4 — no longer an open question.
