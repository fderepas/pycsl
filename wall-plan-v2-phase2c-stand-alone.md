# Emitting a verified recursion from an imperative dict-walk — an open compilation problem for external review

*Self-contained problem statement, 2026-07-07. For an external programming-languages / deductive-
verification / verified-compilation reviewer. No prior knowledge of the host system assumed.*

---

## 0. What we are asking you

We have a self-verifying deductive verifier. Its one remaining unverifiable construct — a method that
walks a generic heterogeneous dictionary — has been **decomposed by experiment into three layers, two of
which we have solved and mechanically certified**. The residual is now a **pure code-generation problem**,
and it is well-posed:

> Our verifier's back-end emits **one target-language declaration per source function** and lowers a
> Python `for`-loop to a **`while`-loop**. We have *proved* (machine-checked, both SMT solvers) that the
> **target** shape for a generic dict-walk — a mutually-recursive `walk`/`walk_dict`/`walk_list` group
> over an inductive "universal value" type, with a structural `size` **variant**, a by-reference frame,
> and interned-key reads — discharges type-safety + termination + frame. **But our emitter cannot
> *produce* that shape from the imperative source**: it has no pass that turns an imperative generic-
> iteration loop into a **structural recursion**, and no pass that **synthesizes the auxiliary helper
> functions** the recursion needs. **Which state-of-the-art techniques (recursion extraction /
> imperative→functional transformation, fold/catamorphism recognition, defunctionalization, verified-
> compiler loop-to-recursion, deductive helper synthesis) let a *verifying compiler* emit a
> structurally-recursive, terminating, framed lowering of `for k,v in d.items(): rec(v)` — under a
> type-safety-only obligation, byte-for-byte inert on all code that does not match the pattern, and with
> no new trusted axiom?**

§7 lists the concrete questions with prior-art anchors; §8 is the frozen benchmark any proposal must clear.
This is **not** a semantics or SMT question (those layers are solved, §2); it is a **verifying-code-
generation** question.

---

## 1. The system and its self-verification bootstrap (architecture)

**PyCSL** is a deductive verifier for a statically-analysable subset of Python. It lowers that subset to
**WhyML** (the input language of the **Why3** platform), which generates verification conditions
discharged automatically by **SMT solvers (Alt-Ergo, Z3, CVC5)**. Contracts are Hoare-style
(`requires`/`ensures`/`assigns`) in `#@` comments.

Its trusted base is pinned by a **3-axiom ledger**, mechanised in **Rocq 8.20 and Lean 4.29**
(`alt_ergo_correct`, `trusted_contracts_axiom`, `why3_implements_wp_w`), from which a soundness theorem is
proved. Rule we cannot break: any extension that introduces a new target-language value shape must
**co-land an axiom-free Rocq+Lean certificate**, keeping the ledger at exactly 3.

**Self-verification bootstrap.** The WhyML **emitter** (the compiler back-end, "Module 6", ~4 kLOC) is
itself written in the verifiable Python subset. PyCSL verifies a **mirror** of its own emitter: each
emitter method is either **verified** (proved against a contract) or a **`\trusted` stub** (an *assumed*
contract). The campaign minimises the trusted core. The residual is dominated by methods that read the
compiler's **IR** — which is represented as Python `Dict[str, Any]` (string keys; values int/str/bool/
list/nested-dict). The construct the verifier cannot verify about itself is thus the one its own back-end
is built to traverse. This report is about the **last barrier** to verifying those methods.

**The scope cut that matters (recurs throughout).** The self-annotation contract is deliberately weak:

```
#@ requires True   #@ ensures True   #@ assigns <tight frame>
```

We verify **type-safety** (well-typedness of every projection, no `int`/`string` confusion) **+ frame**
(the method mutates only its declared footprint) **+ termination** (Why3 requires it) — **never** the
*value* computed. Functional correctness of the walk is out of scope. A reviewer from full functional
verification should recalibrate: we need the weakest interesting guarantee, which is exactly why we
believe the residual is *engineering-plus-metatheory*, not open research.

---

## 2. The three-layer decomposition — two solved & certified, one remaining

A multi-phase experiment (all artifacts committed; see §8, §9) decomposed the wall:

| layer | question | status | evidence |
|---|---|---|---|
| **L1 — value modeling** | represent a heterogeneous `Dict[str,Any]` in WhyML so key-lookup & dispatch discharge on **both** SMT solvers, with a **program-usable** termination measure, and **no new axiom** | **SOLVED & CERTIFIED** | §2.1 |
| **L2 — target-shape provability** | does the generic dict-walker, *hand-written* as its target WhyML, prove (type-safety + termination + frame)? | **SOLVED** | §2.2 |
| **L3 — verifying code-generation** | can the **emitter** *produce* that target shape from the verbatim imperative source? | **NO — the residual wall** | §3–§4 |

### 2.1 L1 solved (for context — do not re-solve)
The naive universal-value encoding (a `pyval` ADT with an association-list dict) is *sound* but its
finite-map refinement is **strict-positivity-rejected** and its key-lookup **times out on Z3 even for a
2-element map** (an abstract-map-theory / e-matching pathology). We fixed it the CompCert way — **concrete
data + evaluation, interned keys, proven lemmas, never abstract theories**:

```whyml
type irkey  = K_type | K_left | K_op | …          (* interned from the IR schema — constructors, not strings *)
type pyval  = PInt int | PStr string | PBool bool | PNone | PList (list pyval) | PDict pydict
with pydict = DNil | DCons irkey pyval pydict     (* strictly positive; get/mem/size are logic functions *)
```

Key-lookup on a literal map is discharged by **Why3's `compute_in_goal`** (proof by evaluation, *before*
any solver), so `get d K_z = None` reduces to `True` solver-independently; general laws are **proven
lemmas** (induction); key (dis)equality is **constructor** reasoning (zero string theory). Verified: the
two goals that timed out on the finite-map version are now **Valid on Alt-Ergo AND Z3, no new axiom**, and
the Rocq certificate is `Print Assumptions` = **"Closed under the global context"** (fully axiom-free), the
Lean twin `#print axioms` = only kernel axioms (no `sorryAx`). **The value type is not the problem.**

### 2.2 L2 solved (this defines the target the emitter must hit)
Hand-written as their **target** WhyML, the two benchmark walkers whole-body-prove — **all VCs Valid on
both provers, no axiom, false twins unproven**:
- **The generic-iteration walker** (`find_named_expr_targets`): a mutually-recursive
  `walk`/`walk_dict`/`walk_list` group over `pyval`/`pydict` carrying, together: **generic `.items()`
  iteration** (as a cons-spine recursion over `pydict`), **unbounded recursion** into each heterogeneous
  value, **by-reference set mutation** (`writes { targets }`), a **structural `size` variant**, and the
  frame. This is the shape the emitter must emit.
- **The read+build walker** (`find_return_type`): recursion over `List[pydict]` reading keys via
  monomorphic constructor-spine accessors and building the result string as a **document-ADT `DCat` fold**
  (so no VC touches SMT string theory), termination via a **proven** sub-term lemma.

**So both the value type (L1) and the exact target program (L2) are proven. The only thing missing is the
compiler pass that emits L2 from the source.**

---

## 3. The exact L3 problem — the emitter cannot emit the proven shape

### 3.1 The source (what the emitter is given)
```python
def find_named_expr_targets(obj: Any, targets: Set[str]) -> None:
    if isinstance(obj, dict):
        if obj.get("type") == "NamedExpr": targets.add(obj["target"])
        for k, v in obj.items():                 # generic iteration over a heterogeneous dict
            if k == "stmt": continue
            find_named_expr_targets(v, targets)   # unbounded recursion into each value
    elif isinstance(obj, list):
        for item in obj:
            find_named_expr_targets(item, targets)
```

### 3.2 The target (proven in L2, §2.2) — a multi-helper structural recursion
```whyml
let rec walk (v: pyval) (targets: ref …) : unit  writes { targets }  variant { size v } =
  match v with
  | PDict d -> (if get_type d = … then set_add targets (get_target d));  walk_dict d targets
  | PList l -> walk_list l targets
  | _ -> ()
with walk_dict (d: pydict) (targets: ref …) : unit  writes { targets }  variant { size_dict d } =
  match d with DNil -> () | DCons k v rest -> (if k <> K_stmt then walk v targets); walk_dict rest targets
with walk_list (l: list pyval) … variant { size_list l } = …
```

### 3.3 Why the emitter cannot bridge source → target (verified, §4)
Three architectural facts, each a distinct piece of the missing pass:

1. **One source function → one target declaration.** The emitter's *only* multi-declaration mechanism is
   cross-function SCC grouping (emitting `let rec … with …` across *distinct source functions* that call
   each other). There is **no mechanism to synthesize auxiliary helpers from a single method.** The proven
   target needs **≥5 synthesized symbols from one source method** (`walk`, `walk_dict`, `walk_list`,
   `get_target`, `set_add`).
2. **`for` lowers to `while`, and termination *requires* the recursion.** The back-end lowers
   `for x in it` to `while !i < iter_length it: … iter_get it !i …`. Under a `while`-loop, the walked value
   `v = iter_get obj i` is an **opaque** SMT term, so the recursive call's `size v < size obj` decrease is
   **underivable** — there is no structural sub-term. The proven target splits out `walk_dict` **precisely
   to make iteration a structural cons-spine recursion** (`DCons _ v rest`), so `size_dict_mem` supplies the
   decrease. Turning the loop into that recursion is a **transformation the emitter does not perform**; a
   proposed "add a `variant` to the existing recursion" cannot help, because there is no recursion to
   annotate — there is a loop.
3. **Iteration variables are erased at IR construction.** A non-trivial `for` target (`for k, v in …`)
   collapses to a single opaque name at IR-emission time (the tuple `(k,v)` is not destructured), so even
   the source iteration variables do not survive to the back-end intact.

**Net:** the residual wall is a **verifying-compiler transformation** — recognise an imperative generic-
iteration walk and *emit* it as a terminating, framed, structural recursion with synthesized helpers —
not a value-modeling or SMT problem.

---

## 4. The measured evidence

Porting the verbatim method into the mirror and emitting it yields WhyML with four verified defects, each
a piece of the missing pass:
1. **universal value int-collapsed** (`obj: int`; the L1 `pydict` theory is present but *unwired* — nothing
   in the back-end routes to it);
2. **`.items()` collapse**: a `while` over an opaque int-iterator; the tuple target `k,v` leak into the
   function signature as **phantom `(k:int)(v:int)` parameters**;
3. **self-recursion emitted as an opaque abstract `val`** (wrong arity/type) — a single `while` function,
   **not a `let rec`** — the hard type error;
4. **no `variant`** — termination unprovable even after type-checking (the opaque-`iter_get` argument).

**Corpus-safety datum (important for admissibility):** across the 756-program reference test-corpus,
**0** programs use a tuple-target `.items()` walk. So a *precise* recognizer for this pattern fires on
**nothing** in existing code ⇒ a gated synthesis path is **byte-for-byte inert** on the whole corpus
(our hard additivity gate). The transformation may therefore be **pattern-gated** rather than universal.

---

## 5. Constraints bounding admissible solutions

- **Target: WhyML → Why3 → SMT.** Automatic proof only (Alt-Ergo/Z3/CVC5, best-of-N); VCs must discharge
  within a per-goal budget (~seconds). No interactive proof in the emission path.
- **Termination is mandatory and must be SMT-dischargeable.** Why3 accepts (i) *syntactic* structural
  recursion for **logic functions**, and (ii) an explicit `variant { … }` for **program `let rec`**. The
  emitted walk is program code ⇒ regime (ii) ⇒ the synthesized recursion must expose a **structural
  sub-term** for the measure decrease (this is *why* a loop does not suffice, §3.3-2).
- **The 3-axiom ledger is fixed.** No new trusted axiom; any new value/lemma is **mechanically certified**
  (Rocq 8.20 + Lean 4.29, axiom-free). L1's `pydict`/`size`/lemma-pack + certificate already exist and are
  reusable.
- **Byte-for-byte additivity.** Any emitter change must be **byte-identical** on all 756 reference programs
  (we gate on this). The corpus-safety datum (§4) makes a *pattern-gated* synthesis admissible.
- **Weakest-guarantee scope (§1).** type-safety + frame + termination only — never the value. The
  synthesized recursion need not be proved *equivalent* to the source loop's I/O; it must be *well-typed,
  framed, and terminating*. (Though a reviewer may note that a soundness argument relating the two is
  desirable; under our contract it is not *required*.)
- **Self-hosting.** The synthesizer is part of the emitter, which is itself verified — a mild reflexivity
  constraint (the synthesizer's own code must stay in the verifiable subset or be `\trusted`-and-audited).

---

## 6. Where L3 sits in the global architecture

PyCSL's soundness rests on three links (LINK-1/2/3): WP↔operational-semantics soundness; the Module-6
*encoding* faithfulness (Python-subset ⇒ WhyML); and *emitter self-verification*. L3 is on **LINK-3**: the
~125 IR-reading emitter methods self-verification cannot yet discharge. Breaking it (a) closes the LINK-3
gap for those methods, (b) resolves a **bootstrap tension** — the code-gen capability needed to *verify*
the dict-reading back-end is the same capability the back-end would need to *emit* for user programs that
use `Dict[str,Any]` — and (c) since L1's certified `pydict` is exactly the deferred heterogeneous-value
model the mechanised metatheory needs, capability and certificate stay coupled. The prize is the
**capability** (a verifying compiler that emits structural recursions for generic walks), not the raw stub
count.

---

## 7. Open questions for the reviewer (candidate SOTA in brackets)

1. **Recognizing and extracting the recursion.** What is the right way for a *verifying* compiler to turn
   an imperative `for k,v in d.items(): rec(v)` walk over an inductive dict into a **structural recursion /
   catamorphism** over that inductive type, so the termination measure decreases on a syntactic sub-term?
   *[recursion extraction / imperative→functional transformation; fold/catamorphism recognition &
   "recursion-scheme" compilation; worker/wrapper & tupling transformations; Coq `Function`/`Program
   Fixpoint`/Equations deriving well-founded recursion from a spec.]*
2. **Synthesizing the auxiliary helpers from one method.** How should the emitter *synthesize* the
   `walk`/`walk_dict`/`walk_list` group (and `get_<key>`, `render`) as a verified `let rec … with …` from a
   single source method — a code generator, not a routing rule? *[deductive program synthesis; syntax-
   guided synthesis (SyGuS); defunctionalization (Reynolds) to turn higher-order/looping control into first-
   order recursion; template-based helper synthesis.]*
3. **Loop→recursion in verified compilers specifically.** Which verified-compilation pipelines already
   transform loops into terminating recursions we can borrow the *proof architecture* from? *[CompCert (we
   already use its `PTree`/`ident`-interning idea for L1); CakeML (fuel + a verified compiler);
   Vellvm/VST; Why3's own transformations; Dafny's loop `decreases` — though we must *synthesize* the
   recursion, not annotate an existing one.]*
4. **Termination measure synthesis.** Given the synthesized recursion, is the structural `size`/`size_dict`
   sub-term measure (with our proven lemma pack) sufficient, or is a synthesized ranking function / sized-
   type discipline more robust across walk shapes? *[sized types; ordinal/`decreases` measures — ACL2,
   Dafny; ranking-function synthesis.]*
5. **Framing the by-reference mutation through the synthesized recursion.** The accumulator (`targets`) is
   a by-ref set threaded through the whole synthesized group. Is the light `ref`+`writes` framing (which we
   proved on a minimal example) enough at synthesis scale, or is a compositional separation-logic framing
   warranted? *[implicit dynamic frames / permissions — Viper, Nagini; separation logic — Iris/RustBelt;
   store-passing.]*
6. **Keeping the transformation admissible (byte-diff-0 + no axiom).** Given the corpus-safety datum
   (0/756 programs match), is a **pattern-gated** synthesis the right discipline, and how narrow must the
   recognizer be to stay provably inert on non-matching code while covering the real walkers?
7. **Do we even need source-equivalence?** Under a type-safety+frame-only contract, the synthesized
   recursion need not be proved I/O-equivalent to the source loop. Is that scope cut sound to lean on, or
   does a minimal simulation/refinement obligation between loop and recursion belong in the certificate?

---

## 8. Success criteria — the frozen benchmark

A proposed technique is evaluated against these exact, reproducible artifacts (spikes + phase write-ups in
`test-suite/corpus/conformance/spikes/` and `getting-better/tier3/`):

1. The **emitter**, given the verbatim `find_named_expr_targets(obj, targets: Set[str])`, emits a WhyML
   `let rec … with …` group that **whole-body-proves** (`--fun`, all VCs Valid, no timeout) under
   `requires True / ensures True / assigns targets` — i.e. it *produces* the L2-proven shape (target in
   `test-suite/corpus/conformance/spikes/v2_iter_mutate_spike.mlw`).
2. Same for `find_return_type(stmts: List[Dict[str,Any]]) -> str`
   (`v2_listdict_recurse_spike.mlw`).
3. **Byte-diff 0** across the 756-program reference corpus (the synthesis is pattern-gated + inert
   elsewhere), plus a poisoned control that turns the gate red once.
4. **Ledger == 3** (`Print Assumptions` / `#print axioms`) — no new trusted axiom; any synthesized lemma
   is machine-certified.
5. Discharge within the automatic per-goal SMT budget.

Clearing (1)–(5) breaks the wall in practice. A rigorous argument that **no** verifying-compiler
transformation can produce a provable recursion here under these constraints is equally valuable — it
would justify leaving the ~125 methods `TRUSTED(essential)` with a closed question.

---

## 9. One-paragraph brief + reference artifacts

*A self-verifying Why3/SMT-backed deductive verifier can prove type-safety + frame of almost all of its own
WhyML emitter, except ~125 methods that walk a generic heterogeneous `Dict[str,Any]`. We have machine-
certified (axiom-free, Rocq 8.20 + Lean 4.29, ledger==3) a concrete universal-value dictionary that clears
the SMT pathologies (L1), and we have proved (both solvers) that the target recursion for such a walk —
mutually-recursive `walk`/`walk_dict`/`walk_list` over the inductive value with a structural `size` variant,
a by-ref frame, and interned-key reads — discharges (L2). The residual wall (L3) is purely code-generation:
the emitter is one-source-function-to-one-declaration and lowers `for` to a `while`-loop, whose opaque
`iter_get v` gives no structural sub-term for the termination measure, so it cannot *emit* the proven
recursion; it also has no pass to synthesize the auxiliary helpers from one method. Constraints: automatic
SMT (Alt-Ergo/Z3/CVC5), mandatory SMT-dischargeable termination, a fixed 3-axiom Rocq/Lean ledger (no new
axioms), byte-identical output on 756 existing programs (0 of which match the pattern, so a gated synthesis
is admissible), and a type-safety+frame-only obligation (no source-equivalence required). Which combination
of recursion-extraction / fold-recognition, deductive helper synthesis, defunctionalization, verified-
compiler loop-to-recursion, and termination-measure synthesis produces a provable, framed, terminating
recursion from the imperative walk?*

### Reference artifacts
- L1 encoding + certificate (axiom-free): `getting-better/tier3/wall-plan-v2-phase0.md`,
  `src/formal-semantics/rocq/Phase2c_PyValDict.v`, `src/formal-semantics/lean/PyCSL/PyValDict.lean`,
  `test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw`
- L2 proven target shapes: `getting-better/tier3/wall-plan-v2-phase2a.md`,
  `test-suite/corpus/conformance/spikes/v2_iter_mutate_spike.mlw`, `.../v2_listdict_recurse_spike.mlw`
- L3 localization + the emitter defects + scoped subsystem: `getting-better/tier3/wall-plan-v2-phase2b.md`,
  `.../wall-plan-v2-phase2c.md`
- The value-modeling predecessor problem statement (L1, now solved): `generic-dict-str-any-2.md`
- Soundness ledger + LINK-1/2/3: `src/formal-semantics/` (Rocq 8.20 + Lean 4.29)
- Prior-art anchors: CompCert (`PTree`/`ident` interning; verified compilation), CakeML (fuel + verified
  compiler), Reynolds defunctionalization, Coq `Function`/`Equations` (well-founded recursion from a spec),
  SyGuS / deductive synthesis, Viper/Nagini (framing), sized types / Dafny `decreases` (termination),
  fold/catamorphism-based compilation.
