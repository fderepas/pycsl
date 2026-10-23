# FABLE-oracle response: the variadic content-law comprehension op is NOT a facade

*Independent external review, 2026-07-15. Blind to the sub-loop's internals; judged from
`variadic-content-law-wall.md` + my own Why3 spike (Why3 1.8.2, Alt-Ergo 2.6.2, cross-checked Z3 4.13.3).
I attacked vacuity first, per instructions. Spike files:
`/tmp/claude-1346829620/-home-fabrice-derepas-canonical-com-git-pycsl/9dd932d0-43ec-4eaf-b2b4-3686bbb5f588/scratchpad/oracle_content_law.mlw`
and `.../oracle_length_only_negctl.mlw`. `grep -cE '^\s*axiom'` on both: **0**. I did not read the
pre-existing probe files found in the scratch directory (independence).*

## VERDICT (one word): **SANCTIONED**

— non-vacuous, the same fidelity level as the accepted projection comprehension, variadic buildable —
**with the three conditions in §6**. The load-bearing subtlety: the wall's §5c litmus test as literally
stated ("if a constant-returning implementation can satisfy the law, it is vacuous") is the **wrong
test** — my spike proves a constant model satisfies the *already-accepted* projection `get_x` law just
as well (M4), so that literal test retroactively condemns the campaign's own baseline. The correct
discriminator is the **non-functional hostile** (an output that is not the pointwise image of *any*
single function), and against that hostile the content law is a proven refuter while length-only is a
proven admitter. Full run below.

---

## 1. The spike

### 1.1 Design

Five modules, **zero `axiom` declarations**: every law lives as an `ensures` on an abstract program
`val` (the campaign-sanctioned mechanism), and every claimed model is an *executable* `let` that Why3
must **prove** against the relevant contract — so each "X can satisfy law L" claim is a machine-checked
refinement witness, not hand reasoning, and each "no interpretation of disp explains X" claim is proven
against an **uninterpreted** `disp` (validity for an uninterpreted symbol = validity for every
interpretation).

| Module | Role |
|---|---|
| `ContentLawPositive` | what the per-index law FORCES: congruence T1, cross-call determinism T2, non-nil T3, pointwise image T4 |
| `HostileNonFunctional` | hostile that RETURNS `[IrConst 0; IrConst 1]` regardless of input: satisfies length-only (`hostile2`), provably explained by **no** per-element function (R1 first-order over uninterpreted `disp`; R2 explicit `forall f: emit_ir -> emit_ir`) |
| `ConstantModelSatisfiesContentLaw` | the §5c literal test: constant-returning `const_impl` **does** prove the full content law when `disp := λ_. IrConst 42` |
| `ConstantModelSatisfiesProjectionLaw` | **parity control**: the same constant model proves the accepted projection law (`get_x := λ_. 0`, `Array.make n 0`) |
| `SharedDispCrossSite` | what symbol-sharing buys: two comprehension ops + one fixed-arity consumer pinned to the same `disp` cohere (T5, T6) |

### 1.2 `oracle_content_law.mlw` (verbatim)

```why3
(* ============================================================
   FABLE-oracle spike: variadic content-law comprehension op
   vs length-only facade. Zero `axiom` declarations by design:
   all laws live as `ensures` on abstract program vals (the
   campaign-sanctioned mechanism), all models are executable
   `let`s that Why3 must PROVE against their contracts.
   ============================================================ *)

module ContentLawPositive
  use int.Int
  use option.Option
  use array.Array
  use list.List
  use list.Length
  use list.Nth

  type emit_ir = IrConst int | IrPair emit_ir emit_ir

  (* the FRESH abstract per-element function (NOT the program's
     dispatcher symbol) — exactly the wall's emit_ir_disp *)
  val function disp (e: emit_ir) : emit_ir

  val list_content_comp (src: array emit_ir) : list emit_ir
    ensures { length result = Array.length src }
    ensures { forall i. 0 <= i < Array.length src ->
                nth i result = Some (disp src[i]) }

  let t1_congruence (src: array emit_ir)
    requires { Array.length src >= 2 }
    requires { src[0] = src[1] }
  = let r = list_content_comp src in
    assert { nth 0 r = nth 1 r }

  let t2_determinism (src: array emit_ir)
    requires { Array.length src >= 1 }
  = let r1 = list_content_comp src in
    let r2 = list_content_comp src in
    assert { nth 0 r1 = nth 0 r2 }

  let t3_not_nil (src: array emit_ir)
    requires { Array.length src >= 1 }
  = let r = list_content_comp src in
    assert { r <> Nil }

  let t4_pointwise_image (src: array emit_ir)
    requires { Array.length src >= 3 }
  = let r = list_content_comp src in
    assert { nth 2 r = Some (disp src[2]) }
end

module HostileNonFunctional
  use int.Int
  use option.Option
  use array.Array
  use list.List
  use list.Length
  use list.Nth

  type emit_ir = IrConst int | IrPair emit_ir emit_ir

  val function disp (e: emit_ir) : emit_ir

  (* hostile: ignores element values, emits two DIFFERENT constants *)
  let hostile2 (src: array emit_ir) : list emit_ir
    requires { Array.length src = 2 }
    ensures  { length result = Array.length src }   (* length-only law: SATISFIED *)
    ensures  { result = Cons (IrConst 0) (Cons (IrConst 1) Nil) }
  = Cons (IrConst 0) (Cons (IrConst 1) Nil)

  let r1_content_law_refutes_hostile (src: array emit_ir)
    requires { Array.length src = 2 }
    requires { src[0] = src[1] }
  = let r = hostile2 src in
    assert { not (nth 0 r = Some (disp src[0])
               /\ nth 1 r = Some (disp src[1])) }

  let r2_no_function_explains_hostile (src: array emit_ir)
    requires { Array.length src = 2 }
    requires { src[0] = src[1] }
  = let r = hostile2 src in
    assert { forall f: emit_ir -> emit_ir.
               not (nth 0 r = Some (f src[0])
                 /\ nth 1 r = Some (f src[1])) }
end

module ConstantModelSatisfiesContentLaw
  use int.Int
  use option.Option
  use array.Array
  use list.List
  use list.Length
  use list.Nth

  type emit_ir = IrConst int | IrPair emit_ir emit_ir

  let function disp_c (_e: emit_ir) : emit_ir = IrConst 42

  let rec replicate42 (n: int) : list emit_ir
    requires { n >= 0 }
    ensures  { length result = n }
    ensures  { forall i. 0 <= i < n -> nth i result = Some (IrConst 42) }
    variant  { n }
  = if n = 0 then Nil else Cons (IrConst 42) (replicate42 (n - 1))

  (* constant-returning op PROVES the per-index content law *)
  let const_impl (src: array emit_ir) : list emit_ir
    ensures { length result = Array.length src }
    ensures { forall i. 0 <= i < Array.length src ->
                nth i result = Some (disp_c src[i]) }
  = replicate42 (Array.length src)
end

module ConstantModelSatisfiesProjectionLaw
  use int.Int
  use array.Array

  type rec_t = { mutable dummy: int }

  let function get_x_c (_r: rec_t) : int = 0

  (* constant-returning op PROVES the ACCEPTED projection law *)
  let const_proj_impl (src: array rec_t) : array int
    ensures { Array.length result = Array.length src }
    ensures { forall i. 0 <= i < Array.length src ->
                result[i] = get_x_c src[i] }
  = Array.make (Array.length src) 0
end

module SharedDispCrossSite
  use int.Int
  use option.Option
  use array.Array
  use list.List
  use list.Length
  use list.Nth

  type emit_ir = IrConst int | IrPair emit_ir emit_ir

  val function disp (e: emit_ir) : emit_ir

  val list_content_comp_A (src: array emit_ir) : list emit_ir
    ensures { length result = Array.length src }
    ensures { forall i. 0 <= i < Array.length src ->
                nth i result = Some (disp src[i]) }

  val list_content_comp_B (src: array emit_ir) : list emit_ir
    ensures { length result = Array.length src }
    ensures { forall i. 0 <= i < Array.length src ->
                nth i result = Some (disp src[i]) }

  val single_disp_call (e: emit_ir) : emit_ir
    ensures { result = disp e }

  let t5_cross_site (s1 s2: array emit_ir)
    requires { Array.length s1 >= 1 /\ Array.length s2 >= 1 }
    requires { s1[0] = s2[0] }
  = let ra = list_content_comp_A s1 in
    let rb = list_content_comp_B s2 in
    assert { nth 0 ra = nth 0 rb }

  let t6_consumer_coherence (s: array emit_ir)
    requires { Array.length s >= 1 }
  = let r = list_content_comp_A s in
    let v = single_disp_call s[0] in
    assert { nth 0 r = Some v }
end
```

### 1.3 `why3 prove -P alt-ergo oracle_content_law.mlw` — 12/12 Valid

```
Goal t1_congruence'vc.                    Prover result is: Valid (0.03s, 28 steps).
Goal t2_determinism'vc.                   Prover result is: Valid (0.03s, 26 steps).
Goal t3_not_nil'vc.                       Prover result is: Valid (0.03s, 9 steps).
Goal t4_pointwise_image'vc.               Prover result is: Valid (0.03s, 12 steps).
Goal hostile2'vc.                         Prover result is: Valid (0.03s, 19 steps).
Goal r1_content_law_refutes_hostile'vc.   Prover result is: Valid (0.04s, 89 steps).
Goal r2_no_function_explains_hostile'vc.  Prover result is: Valid (0.04s, 92 steps).
Goal replicate42'vc.                      Prover result is: Valid (0.05s, 102 steps).
Goal const_impl'vc.                       Prover result is: Valid (0.04s, 19 steps).
Goal const_proj_impl'vc.                  Prover result is: Valid (0.03s, 19 steps).
Goal t5_cross_site'vc.                    Prover result is: Valid (0.04s, 36 steps).
Goal t6_consumer_coherence'vc.            Prover result is: Valid (0.04s, 12 steps).
```

Z3 4.13.3 cross-check: **12/12 Valid** (all < 0.02s). `grep -cE '^\s*axiom' oracle_content_law.mlw` = **0**.

### 1.4 Negative control — the same asserts under LENGTH-ONLY (`oracle_length_only_negctl.mlw`)

```why3
module LengthOnlyNegativeControl
  use int.Int
  use option.Option
  use array.Array
  use list.List
  use list.Length
  use list.Nth

  type emit_ir = IrConst int | IrPair emit_ir emit_ir

  val list_len_comp (src: array emit_ir) : list emit_ir
    ensures { length result = Array.length src }

  let n1_congruence (src: array emit_ir)
    requires { Array.length src >= 2 } requires { src[0] = src[1] }
  = let r = list_len_comp src in
    assert { nth 0 r = nth 1 r }

  let n2_determinism (src: array emit_ir)
    requires { Array.length src >= 1 }
  = let r1 = list_len_comp src in
    let r2 = list_len_comp src in
    assert { nth 0 r1 = nth 0 r2 }

  let n3_not_nil (src: array emit_ir)
    requires { Array.length src >= 1 }
  = let r = list_len_comp src in
    assert { r <> Nil }
end
```

```
Goal n1_congruence'vc.    Prover result is: Timeout (10.00s, 36402 steps).
Goal n2_determinism'vc.   Prover result is: Timeout (10.00s, 39667 steps).
Goal n3_not_nil'vc.       Prover result is: Valid (0.04s, 7 steps).
```

N1/N2 are not merely "solver gave up": `hostile2` (proven, §1.3) is a machine-checked **model witness**
— an implementation that refines the length-only contract and whose output R1/R2 prove is explained by
no per-element function whatsoever. So N1/N2 are *semantically* unprovable under length-only, and the
gap between the two laws is model-theoretic, not heuristic. `^axiom` count on this file: **0**.

---

## 2. Answer to §5(c) — the constant/nil vacuity test, both ways

**Nil:** cannot satisfy either law for non-empty `src` — the length conjunct alone kills it (T3 *and*
N3 both Valid). Nil-refutation is therefore **not a discriminator** and says nothing about the content
conjunct.

**Constant:** a constant-returning implementation **CAN** satisfy the per-index content law —
`const_impl` proves the full contract with `disp` interpreted as the constant function (M3, Valid).
Read literally, §5c would now say FACADE. But the parity control (M4) proves the **identical** constant
model against the campaign's already-accepted projection law: `Array.make n 0` refines
`result[i] = get_x_c src[i]` with `get_x_c := λ_. 0`. This is forced by first-order semantics: any
content law over a *fresh uninterpreted* per-element symbol is satisfied by the constant model, because
constant functions are functions. **A test that condemns the construct under review and the accepted
baseline equally is not a criterion — it is a proof that the criterion was mis-stated.** The
discriminating hostile is not "constant" (a degenerate *member* of the pointwise-image family) but
"non-functional" (an output *outside* that family), and there the two laws provably diverge:

| Hostile implementation | Length-only law | Per-index content law |
|---|---|---|
| `nil` on non-empty src | refuted (length) | refuted (length) |
| constant list, right length | admitted | admitted (with constant `disp`) — same for accepted `get_x` |
| **non-functional** (`[0;1]` on `src[0]=src[1]`; or two calls, same src, different outputs) | **admitted** — `hostile2` proves | **refuted for every `disp`** — R1/R2 prove |

What the content law adds over length-only, proven (T1/T2/T4 vs N1/N2 + hostile2): the result is pinned
to be **the pointwise image of the source under one fixed, global, deterministic function** — per-index
element-determinedness, congruence (`src[i]=src[j] → nth i r = nth j r`), cross-call and cross-index
coherence, exact `map disp src` shape. Length-only pins a cardinal number. These are different
model classes, with a machine-checked witness in the gap. **The law is NOT the length-only facade in
disguise.**

## 3. Answer to §5(a) — does the FRESH `disp` degrade the law to a facade?

No, for three reasons, one of them specific to this campaign's baseline:

1. **Freshness is exactly the `get_x` precedent.** `get_x` is also a fresh uninterpreted `val function`
   pinned to no concrete field-read implementation. Structurally the two laws are isomorphic (my M1 and
   M4 differ only in the element type and list-vs-array carrier). Whatever content freshness leaves in
   one, it leaves in the other.
2. **There is nothing to tie `disp` to.** The program-side dispatcher `csl_to_ir` is an opaque program
   `val ... : emit_ir` under the campaign's `ensures True` regime: (i) a program val cannot appear in a
   logic `ensures` formula at all, and (ii) it carries no value law to inherit — its result is
   unconstrained and, being a program val, not even provably equal across two calls on the same
   argument. Identifying `disp` with it is both syntactically impossible and semantically empty.
3. **The fresh `val function` is *stronger* than the accepted baseline, not weaker.** In the accepted
   fixed-arity handlers (§2 of the wall), the child value `csl_to_ir node.left` is a nondeterministic
   opaque call — zero coherence guarantees. The comprehension's elements, pinned to a logic-level
   `disp`, get determinism and congruence the fixed-arity children never had. The variadic lowering
   cannot be a facade *relative to a baseline it strictly dominates on value coherence*.

Also decisive for the anti-facade rule as written ("reads real accessors; no NEW opaque trusted val to
force a proof"): the mirror body stays the real Python `[self._csl_to_ir(e) for e in node.elts]`
reading the real accessor `node.elts`; `list_content_comp_0` is not a hand-introduced trusted val
bolted on to make a stuck proof pass — it is the **tool's own corpus-proven comprehension lowering**
(0769/0770) applied uniformly, and under `ensures True` nothing needed forcing (the body type-checks
regardless; the content law is surplus rigor). The reverted attempts failed the rule because their op
carried a length-only contract — i.e., they were facades by §2's table, not because an abstract
comprehension op is inherently a facade.

## 4. Answer to §5(b) — the sharing asymmetry, and whether it matters here

The projection precedent **does** have extra content the one-site variadic lacks, and the spike
quantifies exactly what it is: T6 proves that a consumer pinned to the same symbol
(`single_disp_call e ensures { result = disp e }` — the analogue of `a[k].x` lowering to `get_x`)
provably agrees with the comprehension's elements, and T5 proves two comprehension sites sharing one
`disp` cohere with each other. That is *observational cross-checkability*: the abstract symbol is
answerable to more than one occurrence.

**Does its absence matter for NON-VACUITY under `ensures True`? No.** Under the type-safety-only
regime no proof anywhere consumes the handler's value, so cross-site observability is never exercised —
for the accepted `get_x` case included. Non-vacuity must therefore be a property of the law's
*intrinsic* model-class restriction, and §2 proved that restriction is real. The sharing asymmetry
matters precisely when the campaign later moves to value-faithful contracts — and T5/T6 show it is
recoverable there *additively* (share the symbol; optionally add `ensures { result = disp e }` to the
hub) rather than by reworking the comprehension law. Hence it is a **condition to impose now cheaply**
(§6), not a reason to reject.

## 5. The derived non-vacuity criterion

> **A comprehension abstract op is non-vacuous iff its contract refutes some implementation that the
> length-only contract admits — concretely, for a map comprehension: iff the law pins the result to the
> pointwise image of the source under a single, global, logic-level (deterministic) per-element symbol
> (length-preserving + per-index + element-determined), so that any non-functional hostile (unequal
> outputs on equal elements, or unequal results across calls on the same source) is provably excluded
> for every interpretation of the symbol.**
>
> Executable form (this spike): prove T1/T2 from the law; exhibit hostile2 against length-only; prove
> R1/R2 against the law with the symbol left uninterpreted. Non-discriminators to avoid: nil-refutation
> (follows from length alone) and constant-satisfiability (a constant is a function — every
> fresh-symbol content law admits it, including the accepted precedent).

Tested against both cases: the projection `get_x` law and the variadic `disp` law both satisfy the
criterion (identical law shape; M1 goals go through verbatim with `get_x`/`array int`), and both admit
the constant model (M3/M4) — **same side of the line**. The length-only op fails the criterion
(N1/N2 + hostile2) — the reverted attempts were correctly reverted. The criterion also cleanly
separates the two failure modes the campaign has actually seen: "abstract op with structure-pinning
law" (sanctioned) vs "abstract op that only counts" (facade).

## 6. Verdict and conditions

**SANCTIONED.** The per-index content-law abstract op over a fresh abstract `disp` is non-vacuous,
strictly stronger than the length-only facade (machine-checked gap witness), structurally identical to
the accepted projection-comprehension lowering, and strictly stronger on element coherence than the
accepted fixed-arity baseline it extends. The ~13 variadic handlers are a **buildable lever**, subject to:

1. **Law shape is load-bearing.** The op's contract must carry BOTH conjuncts (length + per-index
   content) and the per-element symbol must be a logic-level `val function` (deterministic), never a
   program val and never dropped to length-only. Any emission path that can degrade to length-only
   re-creates the reverted facade.
2. **One symbol per program callee, shared across sites.** Emit a single `emit_ir_disp__csl_to_ir`
   shared by every comprehension site that maps `self._csl_to_ir` (`_csl_mktuple`, `_py_expr_tuple`,
   `_py_expr_list`, ...), per callee — not one fresh symbol per site. T5 shows this is what restores the
   `get_x`-style cross-site observational content; it costs nothing now and is required for parity with
   the precedent's sharing property.
3. **Honest labeling + upgrade path.** The law pins *map structure*, not dispatcher semantics; nothing
   may present it as value-faithful. When the campaign moves past `ensures True`, the tie-in is
   `csl_to_ir : ... ensures { result = emit_ir_disp__csl_to_ir arg }` on the hub (T6 proves this yields
   full consumer coherence) — an additive change, no rework of the comprehension law.

The standing hard gates (byte-diff-0 on the 767-program corpus; whole-file discharge) remain in force
and are orthogonal to this adjudication.
