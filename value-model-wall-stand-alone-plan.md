# value-model-wall-stand-alone-plan.md — Breaking the two value-model walls: plan

*Self-contained plan, 2026-07-09. Companion and answer to the open-problem statement
"Modelling heterogeneous Python values for self-verification" (`value-model-wall-stand-alone.md`).
Assumes its §1–§2 context: the certified `pyval`/`pydict`/`sdict` datatypes (axiom-free Rocq 8.20 +
Lean 4.29), the faithful opaque-string value-op library (landed, byte-diff-0), the 3-axiom ledger,
per-instance re-proof, pattern-gated byte-for-byte additivity, and the
type-safety+frame+termination-only scope cut. Sibling of
`ir-traversal-residual-stand-alone-plan.md` (the control-shape half of the same residual; this is
the value-shape half — the two dovetail in §6).*

**Thesis.** Both walls break; no B0 impossibility argument is warranted. **Wall 2 dissolves almost
entirely into machinery already shipped**: a character is a 1-character string obtained by the
existing `str_sub_op`, and `enumerate(s)` is an integer-indexed `while` with an arithmetic variant —
zero new value shapes, zero new theory, ledger untouched. **Wall 1 is a classification, not a
choice**: dict literals with statically-known key-sets (the entire B1/B2 benchmark family) are
records wearing a dict costume and monomorphize to generated WhyML record types with *faithful*
per-field types (no tags, no laws, no SMT cost); only the genuinely dynamic residue (computed keys,
Any-tree walkers) routes through the certified `pyval` with defensive tag-checked projections.
One small template-level product certificate co-lands; everything else reuses existing certified
artifacts. The answer to the statement's Q3 is: **under this contract, projection laws are needed
nowhere in this campaign** — build-side injection is total, and defensive totalization makes every
read well-typed regardless of content.

---

## 0. Solution map (walls → mechanisms → benchmark)

| Wall / question | Mechanism | Benchmark cleared |
|---|---|---|
| Wall 2: char typed as int hash (defect 3) | **W2a** — char = `str_sub_op s i (i+1)` (1-char string); `ch == c` = `str_eq_op` | B3 (with W2b, E0) |
| Wall 2: `enumerate`/`for ch in s` unmodelled (defect 2) | **W2b** — integer-indexed `while`, `variant { length s - !i }` | B3 |
| Wall 2: parameter-extraction bug (defect 1) | **E0** — engineering fix; re-run census (de-noise) | unblocks B3 measurement |
| Wall 1: statically-known key-sets | **R** — generated record per key-set (closed-row monomorphization) | B1, B2 |
| Wall 1: dynamic keys / Any-tree walkers | **U** — `pyval` routing + defensive tag-checked casts | census walker class |
| Q3: are projection laws needed? | **No** — total injection + defensive totalization; laws only under value-faithfulness, which §4 waives | (soundness argument) |

Build order: **E0 → W2 (a+b) → R (+ product template certificate) → U.** E0 is cheap and
de-noises the Wall-2 census; W2 has the smallest certificate story (none); R clears two benchmark
items with one small template certificate; U dovetails with the traversal plan's T1–T3.

---

## 1. E0 — Fix the parameter-extraction bug first (engineering, blocks measurement)

Defect (1) of the B3 evidence — the `for i, ch in enumerate(s)` **tuple-target promoted to method
parameters** while the real parameter `s` is dropped (static-method + tuple-unpack-loop
interaction) — is a front-end emission bug, not a modelling question. It contaminates the Wall-2
census: some of the 13 "0 convert" string methods may convert on parameter emission alone, and none
can be measured honestly until it is fixed. Fix, add a regression (a static method whose body opens
with a tuple-unpack loop), **re-run the census**, then apply W2. No gate interaction: the fix is a
correctness repair to existing emission, validated by byte-diff on the corpus (any diff it produces
on reference programs is a bug it was masking).

---

## 2. W2 — String as a character sequence, from parts already shipped (Wall 2)

### 2.1 W2a — A character IS a 1-character string, and the op already exists

No char type, no `seq char` reduction, no new theory. SMT-LIB's own string theory made this design
choice (`str.at` returns a string of length ≤ 1; there is no character sort) — strong precedent that
1-char strings are the right model. The project does not even need `str.at`:

- `s[i]` (Python char read) → **`str_sub_op s i (i + 1)`** — already landed in `expressions.py`.
- `ch == "("` → **`str_eq_op ch "("`** — already landed.
- Guard classification (traversal plan, mechanism C) applies verbatim: such comparisons *select
  branches*, never justify projections, so their truth value is **unconstrained in every VC** — the
  SMT string theory is never exercised. The only VCs are bounds/invariant, variant, and typing.

**New value shapes: none. Certificates: none. Ledger: untouched.**

### 2.2 W2b — `enumerate(s)` / `for ch in s` → integer-indexed while with arithmetic variant

```whyml
(* for i, ch in enumerate(s): ...  — lowering skeleton *)
let i = ref 0 in
while !i < String.length s do
  invariant { 0 <= !i <= String.length s }
  variant   { String.length s - !i }
  let ch = str_sub_op s !i (!i + 1) in
  (* ... body: guards via str_eq_op, unconstrained booleans ... *)
  i := !i + 1
done
```

- Termination is **integer subtraction** — SMT-trivial; no structural measure, no `size` pack needed.
- The undeclared `iter_length` / `enumerate_1` / `iter_get` symbols are never emitted (defect 2 gone).
- `for ch in s` is the same lowering without the index binding.
- Slices like `s[1:-1]` → `str_sub_op s 1 (String.length s - 1)`: under the faithful
  under-approximating (total) op discipline of §2.2 of the statement, **no bounds VC** arises.
- Early `return` inside the loop reuses whatever the statement machinery already does for
  return-in-loop elsewhere in the emitter (exception with `raises`, or done-flag) — a solved
  problem, not a new one.

**Gate:** pattern-gated on "`for`-loop over a `str`-typed iterable (direct or `enumerate`)";
fail-closed; poisoned control; byte-diff-0 on the re-pinned corpus (§7).

### 2.3 Q6 answered — in scope, narrowly

The pre-analysis cost/benefit ("leave ~13 pretty-printer helpers `\trusted`") flips once W2a/W2b are
seen to reuse shipped ops: the marginal cost is **one pattern-gated loop lowering**, cheaper than
maintaining 13 trusted stubs plus their audit burden. Build the narrow pattern. Explicitly do
**not** adopt a full character-sequence theory (`seq char`, codepoint conversions, `str.to_code`):
that is the over-solve that would reintroduce SMT string-theory cost for VCs this contract never
generates.

---

## 3. R — The record route: closed key-sets monomorphize to products (Wall 1, B1/B2)

### 3.1 The classification insight

The failing benchmark family is not "heterogeneous dictionaries" — it is **records wearing a dict
costume**. `_build_soundness_report` returns `{"file": …, "summary": …, "vcs": …}`: a dict literal
whose key-set is statically known and whose access sites all use literal keys. Row-type theory
(Rémy; Leijen) says exactly when a closed row monomorphizes to a plain product; CompCert-style
per-shape struct generation is the verified-compiler precedent. So:

```whyml
type soundness_report = {
  sr_file    : string;
  sr_summary : map string int;   (* homogeneous inner dict: faithful map, NOT pyval *)
  sr_vcs     : list pyval;       (* genuinely dynamic elements: certified union     *)
}
```

- Every field keeps its **faithful** type: no injection, no tags, no projection lemmas, and **zero
  SMT cost** — type-safety is discharged by WhyML's type checker at emission.
- The build is a record literal; a pure return makes `assigns \nothing` trivial; no recursion ⇒ no
  variant. **B1 should discharge with no interesting VCs at all.** B2
  (`Dict[str, List[Dict[str, Any]]]`) is the same route with `map string (list pyval)` or
  list-valued fields.
- Note what this *avoids*: extending `pyval` with a string-keyed-map constructor (`PSDict`) — which
  **would** be a new value shape demanding a new certificate. The homogeneous inner dict never
  touches the union.

### 3.2 Recognizer gate (Q7)

Route R fires only when: (i) the dict literal's key-set is fully literal at the build site;
(ii) every access site reachable in the mirror uses literal keys from that set; (iii) every
component type lowers to an existing faithful type (string, int, bool, `map string τ`, `list τ`,
`pyval`). Otherwise fall through to U or stay `\trusted` (fail-closed). Poisoned control: a dict
literal with one computed key must leave emission byte-identical.

### 3.3 Certificate co-landing (the campaign's only one)

A per-shape record is a **plain product of already-certified component types** — no interesting
laws, no recursion. Co-land one **template-level product certificate** (Rocq 8.20 + Lean 4.29,
axiom-free: well-formedness of the schema, trivially closed under `Print Assumptions` /
`#print axioms`) covering all generated record shapes, in the style of the `pyval`/`sdict`
certificates. **Ledger stays at 3.**

---

## 4. U — The union route: defensive tag-checked casts for the dynamic residue (Wall 1)

For dicts with computed keys and the census's generic Any-tree walkers, route through the certified
`pyval`/`pydict`/`sdict` that already exist. The discipline is gradual typing's boundary semantics
(Siek–Taha; Typed Racket's `Any`) compiled the cheapest way the contract permits:

- **Build / injection is total.** `d[k] = v`, `{ "a": x, "b": [ys] }` lower to constructor
  application (`DCons`, `PList`, `PStr`, …) — well-typed by construction, zero laws, exactly the
  precedent of modelling `str_split_op` as an arbitrary `array string`.
- **Read / projection is a defensive tag-checked match.**
  `d.get(k)` → `slookup k d : option pyval`; a read expected at type `int` emits
  `match slookup k d with Some (PInt i) -> i | _ -> <default | raise>` — a space-efficient cast
  (Herman–Siek) degenerated to a **total match**, which is all type-safety needs (defensive
  totalization, shared with the traversal plan). A defensive arm the Python lacks is admissible
  because §4 of the statement explicitly waives I/O-equivalence.

### 4.1 Q3 answered — where projection laws become necessary: nowhere in this campaign

Build-side injection needs zero laws (total). Read-side defensive totalization makes every
projection well-typed **regardless of content**, so `get k (set k v d) = v` is never required for
type-safety. The law becomes necessary only under a *value*-faithfulness obligation the contract
waives — and even then, the §2.1 lemma pack already contains the lookup laws. The
content-arbitrary-`pyval` model is therefore sound under this contract; this is the confirmation
Q3 requested, with the `str_split_op` discipline as the governing precedent.

---

## 5. Rejected alternatives (Q1/Q2/Q4 brackets that would damage the constraints)

- **Refinement types over a universal value (LiquidHaskell, F\*, Dafny-style).** Imports a new
  trusted inference/solving engine to prove tag facts these VCs never need — the same Q7-ledger
  violation rejected in the traversal plan.
- **SYB / open unions.** Higher-order machinery; excluded by the first-order SMT constraint.
- **Genuine row *polymorphism*.** No first-order SMT story; only its **closed-row
  monomorphization** limit is used (route R), which is finitely-instantiable by construction.
- **Full character-sequence theory (`seq char`, codepoints).** Over-solve; reintroduces string-
  theory SMT cost for VCs the contract never generates (§2.3).
- **Space-efficient cast *calculi* as implemented machinery.** Only their degenerate total-match
  form is needed; a coercion IR would be structure the SMT back-end pays for without any VC
  getting easier.

---

## 6. Per-benchmark discharge plan (frozen criteria, statement §6)

1. **B1 `_build_soundness_report`** = **R**. Generate `soundness_report`; emit the record literal;
   pure return ⇒ `assigns \nothing` trivial; no recursion ⇒ no variant; type-safety by WhyML
   type-checking. Expected VC profile: near-empty; discharge immediate.
2. **B2 `_build_method_*_ensures_map` family (≥1)** = **R** with `map string (list pyval)` /
   list-valued fields; same profile as B1.
3. **B3 `_strip_outer_parens`** = **E0 + W2a + W2b**: correct parameters; `enumerate` →
   indexed `while` (invariant + arithmetic variant); `ch` = 1-char `str_sub_op`; literal
   comparisons via `str_eq_op` as unconstrained booleans; `s[1:-1]` total substring (no bounds VC);
   early return via existing return-in-loop machinery. Discharges under
   `requires True / ensures True / assigns \nothing`.
4. **Ledger == 3**: one co-landed template-level product certificate (route R); W2 and U introduce
   **no** new value shape (chars are strings; `pyval`/`sdict` already certified). CI
   `Print Assumptions` / `#print axioms` unchanged.
5. **Byte-diff-0 + poisoned controls**: E0 validated by corpus byte-diff; W2/R/U pattern-gated,
   fail-closed, one poisoned control each. **Re-pin the corpus count first** — the statement says
   759, an earlier statement froze 756, and public `main` currently holds 781 reference programs;
   "byte-diff-0" must name a fixed set.
6. **SMT budget**: R contributes ~zero solver load (typing only); W2 contributes arithmetic
   invariant/variant VCs; U contributes total matches over `pyval` (same profile as the certified
   fold work). No string theory anywhere by construction.

**Dovetail with the traversal plan.** The census's Any-tree walkers need *both* halves: T1–T3
(`ir-traversal-residual-stand-alone-plan.md`) give them their certified recursion shapes; route U
gives their reads/builds a value model. Route R, meanwhile, **removes** the record-shaped methods
from the walker class entirely — shrinking the population the traversal templates must cover.

---

## 7. Honest residual & bootstrap dividend

**The one recurring brick (shared with the traversal plan).** A method whose *type-safety* depends
on **which** semantic guard fired (a projection dominated only by a runtime comparison) defeats both
the unconstrained-boolean move and defensive totalization's shape-preservation. It is detected
mechanically (guard-dominance on the recognizer parse) and resolved per method by source
normalization (self-hosting makes this legitimate), by accepting the defensive shape change, or by a
documented `TRUSTED(essential)` — the statement's own well-posed close-out. **B0 is not warranted**
for either wall: both benchmark families clear without it.

**Bootstrap dividend (statement §1's coupling).** Both routes are user-facing capabilities, not just
self-verification unblocks: R = "verified functions may return typed record-like dicts"; W2 =
"verified character-level string processing"; U = "verified generic-value manipulation." The
coupling rule pays double — the certificates co-landed here are exactly the deferred user-program
value models.

**Audit-trail note for the external reviewer.** As of 2026-07-09, public `main` does **not** contain
`src/formal-semantics/rocq/Phase2c_PyValDict.v` (or the Lean mirror),
`getting-better/tier3/tier5-value-model-census.md`, `emission-defect-spike-findings.md`, or
`generic_fold.py` — all cited as reference artifacts — while the §2.2 string ops
(`str_sub_op`, `str_eq_op`, `str_strip_op`, `str_startswith_op`, `str_split_op`) **are** present in
`src/pycsl/module6_whyml/expressions.py` and `self-tcb-reduction.md` is present. Commit the missing
artifacts and re-pin the corpus (§6.5) before circulating: a reviewer who clones `main` today can
reach the string library this plan reuses but not the certificates and censuses the statement
builds on.

---

## 8. One-paragraph brief (mirror of the statement's §7)

*Both value-model walls fall to classification plus reuse, not new theory. Wall 2: a character is a
1-character string produced by the already-shipped `str_sub_op` (the SMT-LIB `str.at` convention),
`ch == c` is the already-shipped `str_eq_op` compiled as an unconstrained boolean, and
`enumerate(s)` lowers to an integer-indexed `while` with `variant { length s − i }` — zero new value
shapes, zero certificates, no string theory in any VC. Wall 1 stratifies by key-set knowledge:
statically-closed, literal-keyed dict literals (the whole B1/B2 family) monomorphize to generated
WhyML records with faithful per-field types — type-safety by type-checking, one template-level
axiom-free product certificate, ledger held at 3 — while genuinely dynamic dicts and Any-tree
walkers route through the certified `pyval` with total injections and defensive tag-checked
projections (gradual-typing boundaries in their cheapest sound form). Projection laws are needed
nowhere under the type-safety+frame contract: injection is total and defensive totalization makes
every read well-typed regardless of content. The single honest residual — type-safety dominated by
a semantic guard — is mechanically detectable and closes as documented `TRUSTED(essential)`. B0 is
not warranted; B1, B2, and B3 all clear.*
