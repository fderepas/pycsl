# 07-1732-findings — Why faithful `array_concat` cannot be built as specified (P0 gate result)

**Date:** 2026-06-07
**Author:** PyCSL tool track
**Subject:** Result of the `07-1705-spec-rev3.md` **P0 feasibility gate** for a faithful
`array += array` / `array_concat` lowering.
**Verdict:** **STOP.** The mechanism specified in `07-1705` (rev1–rev3) is **not viable in Why3**.
A viable alternative exists but is a **different, larger design** (a `seq`-typed list model) that
must be specified afresh before any emitter work. No emitter code was changed.
**Reproducible artifact:** `docs/probes/07-1705-P0-array-concat.mlw`
(run: `why3 prove -a split_vc -P alt-ergo -P z3 --timelimit 30 <file>`).
**Environment:** Why3 1.8.2, Alt-Ergo 2.6.2, Z3 4.13.3.

---

## 1. What we were trying to do (self-contained background)

Python list/`bytes` concatenation `a += b` (and `a + b`) is lowered by the PyCSL WhyML emitter.
Today it emits an **effect-opaque** `array_extend`:

```whyml
val array_extend (dst: array int) (src: array int) : unit   (* no postcondition about dst *)
...
array_extend !dst src        (* a += b *)
```

This is **type-correct** (it removed an earlier integer-`+`-on-arrays type error, 07-1321 S4) but
**not faithful**: nothing is known about the result afterwards, so a program cannot prove e.g.
`\length(a + b) == \length(a) + \length(b)` or that element `i` landed where it should. The
`_pack_inode`-style byte-packing code (`parts = bytearray(); parts += _pack(...); ...`) can be
type-checked but its assembled length cannot be **proven**.

The goal of `07-1705` was to make concatenation **faithful** under the no-more-int / EXTREME-RIGOR
doctrine: a list is `array int`, and the result of concatenation must carry a provable
length-additive, element-preserving contract.

PyCSL's WhyML arrays use Why3's `array.Array` theory: a `array int` is a **mutable, fixed-length**
structure with a region. Element write is `a[i] <- v`; `Array.length a` is fixed at creation.
PyCSL wraps a list local that is element-mutated in a `ref` and dereferences at use sites
(`(!a)[i] <- v`) — the "arity-2b" pattern.

---

## 2. The design under test (07-1705 rev3)

Because `array.Array` is fixed-length, concatenation cannot grow an array in place — it must build
a **new** array and make the variable point to it. rev3 specified:

```
a += b   ≡   a := materialize (snapshot !a ++ snapshot b)
```

with a `snapshot : array int -> seq int` bridge, a pure `seq.Seq` concat `++`, and a
`materialize : seq int -> array int` returning a **fresh** array — the key claim being that the
fresh result lets the ref `a` be **rebound** without aliasing. rev3 added a **P0 gate**:
prove this rebind in hand-written WhyML *before* touching the emitter, and **STOP if it fails.**

It failed. Below is exactly what was tested and what Why3 said.

---

## 3. What was tested, and the exact Why3 errors

All snippets are minimal hand-written `.mlw` (no emitter involved). The two Why3 region-discipline
errors that recur are:

- **"This application creates an illegal alias"** — a function application Why3 cannot accept
  because two mutable arguments (or an argument and the result) might share a region it requires
  separated.
- **"This expression prohibits further usage of the variable a …"** — Why3 considers the variable
  *consumed* by the expression; using it afterward is forbidden.

| # | Snippet (essence) | Why3 result |
|---|-------------------|-------------|
| 1 | `val array_concat (x y: array int): array int` ; `a := array_concat !a b` | **illegal alias** |
| 2 | **Concrete** `let array_concat … = make+blit` (proven body) ; `a := array_concat !a b` | **illegal alias** |
| 3 | `array_concat arr b` with two **plain params**, no ref, no rebind (`let r = array_concat arr b`) | **OK** ✅ |
| 4 | `let c = ref (array_concat arr b)` (rebind a *different*, fresh ref) | **OK** ✅ |
| 5 | `val snapshot (a: array int): seq int` ; `let s1 = snapshot !a in … a := materialize (s1 ++ s2)` | **prohibits usage of a** |
| 6 | `snapshot` as a **logic `function`** ; `materialize (a_to_seq !a ++ …)` | **logical symbol used in non-ghost context** |
| 7 | `let snap = Array.copy !a in a := array_concat snap b` (copy to break the link) | **prohibits usage of a** |
| 8 | **Trivial:** `let a = ref arr in a := Array.make 5 0` | **prohibits usage of a** |
| 9 | **`ref (seq int)`:** `let a = ref s0 in a := (!a) ++ t` | **OK + PROVES** ✅✅ |

### Reading the table

- **#3 and #4 prove the two-array signature is *not* the core problem.** A concat function taking
  two `array int` arguments type-checks fine when the result is bound to a *fresh* local/ref —
  read-only array arguments do not need region separation.
- **#1, #2, #5, #7, and #8 isolate the real problem to the *rebind*:** assigning back into the very
  ref whose contents fed the computation. It is not specific to abstract-vs-concrete (#1 vs #2),
  not fixed by sequential `let`-binding (#5), and not fixed by copying the operand first (#7).
- **#8 is the decisive minimal case.** Even `let a = ref arr in a := Array.make 5 0` — rebinding a
  `ref (array int)` to a brand-new array that *demonstrably shares nothing* with the old one — is
  rejected with "prohibits further usage of a." **Why3 simply does not allow a `ref` holding a
  mutable, regioned value (`array int`) to be reassigned to a different such value.** This is a
  fundamental property of Why3's region/ownership typing, not a quirk of our contracts.
- **#6** shows the obvious escape (make `snapshot` a pure logic function) is closed: logic
  functions cannot be applied in executable program code ("non-ghost context").

### The one thing that works (#9)

```whyml
let a = ref s0 in            (* s0, t : seq int *)
a := (!a) ++ t;
assert { Seq.length !a = Seq.length s0 + Seq.length t };               (* Valid *)
assert { Seq.length t > 0 -> Seq.get !a (Seq.length s0) = Seq.get t 0 } (* Valid — seam *)
```

`seq int` (Why3's `seq.Seq`) is **immutable** — it has **no region**. A `ref (seq int)` is therefore
like a `ref int`: reassigning it is unrestricted, and `++` is a pure, total concatenation whose
length and indexing axioms are in the standard theory. All three goals (length-additive, seam
element placement, self-concat `a := !a ++ !a`) discharge in Alt-Ergo/Z3 in <0.02 s each.

---

## 4. Root cause, stated plainly

A faithful concatenation **must rebind the list variable to a new value** (Why3 arrays are
fixed-length; you cannot extend in place). rev3 assumed the variable stays `array int` and only the
*rebind* needed care. **P0 disproves that assumption:** rebinding a `ref (array int)` is forbidden
outright by Why3 (#8), so *no* amount of snapshot/materialize/copy machinery around an `array int`
variable can work — the failure is at the `:=`, independent of the right-hand side.

The property that makes rebinding legal is **immutability of the held value**. Only an immutable
element type (`seq int`) gives a `ref` that can be reassigned. Therefore a faithful concat
**requires the concatenated variable to be modelled as `seq int`, not `array int`.**

---

## 5. Why I must stop (rather than push a fix)

1. **The spec's own gate says so.** `07-1705` rev3 §P0 states: *"If any [P0 goal] fails, **stop** —
   the snapshot/materialize mechanism is not viable as specified and the design must be revisited
   … before P1."* P0 failed (the rebind is rejected at the most trivial level). Proceeding to P1/P2
   would be building on a foundation Why3 has already rejected.

2. **The discipline forbids a fake-faithful fix.** The no-more-int / EXTREME-RIGOR doctrine (and
   this project's repeated practice) is: model faithfully or **defer with an honest reason** — never
   ship something that *looks* faithful but isn't. The opaque `array_extend` already on `main` is
   honestly type-correct-only; replacing it with a mechanism that does not type-check in Why3 would
   be strictly worse (it would not even compile), and dressing it up would violate the doctrine.

3. **The viable path is a different, larger design — not a patch.** Making the concatenated variable
   a `seq int` end-to-end changes how that variable is **modelled everywhere it appears**: element
   read becomes `Seq.get`, element write becomes a functional `Seq.set`/rebuild, length becomes
   `Seq.length`, the literal initialiser produces a seq, and passing it to a function makes the
   parameter a `seq int`. It also needs a **bridge** at the boundary with `array int`-modelled code
   (and a decision about *which* locals get the seq model — only those ever concatenated, tracked by
   analysis). That is a new value-model layer, explicitly **out of scope** in rev3, and well beyond
   the "array-snapshot patch" the spec assumed. It deserves its own specification and gating, not an
   in-flight pivot.

Stopping here is the correct, in-doctrine outcome: the cheap P0 probe (a few hand-written `.mlw`
files, no emitter change) **did its job** — it killed an unviable design before any code was written
and pointed precisely at the viable one.

---

## 6. Recommendation

Write **`07-1705-spec-rev4.md`** (or a fresh number) specifying the **`seq`-typed list model** that
P0 proved viable:

- **Scope by need.** Only a list local/param that is *ever* concatenated (`+=` or `+`) is modelled
  as `ref (seq int)`; others stay `array int`. Requires a small whole-function analysis to mark
  such variables (analogous to the existing array1d/`+=`-target detection).
- **Operations on a seq-modelled variable:** init (`[…]` → a seq literal / `Seq.cons` chain),
  `len` → `Seq.length`, read `a[i]` → `Seq.get`, write `a[i]=v` → functional `Seq.set` + rebind,
  concat `a += b` / `a + b` → `!a ++ snapshot(b)` (the proven P0 form), membership/iteration over
  the seq.
- **Boundary bridge.** Where a seq-modelled value meets `array int`-modelled code (a callee taking
  `array int`, or a `\valid`/2-D context), define a single materialise/snapshot bridge and state
  exactly when it fires.
- **Gate.** Re-use this finding's P0 artifact as the feasibility anchor; then the full
  reproduce→fix→sweep→byte-diff discipline.
- Until rev4 lands, **`array_extend` stays** — type-correct, on `main`, honest about its opacity.

---

## 7. Reproduction

```bash
why3 prove -a split_vc -P alt-ergo -P z3 --timelimit 30 \
  docs/probes/07-1705-P0-array-concat.mlw
# Viable (seq) module: 3 sub-goals, all "Valid".
# Uncomment the `Dead` (ref array int) module to observe the rejection firsthand.
```

The probe file contains both the **dead** path (`ref (array int)` rebind, commented out to keep the
file proving) and the **viable** path (`ref (seq int)`), with inline notes matching this document.
