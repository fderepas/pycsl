# Modelling heterogeneous Python values for self-verification — an open problem for external review

*A self-contained problem statement for reviewers in programming-language theory, deductive program
verification, and verified compilation. No prior knowledge of the system is assumed.*

> **Role of this file (read first — the `value-model-wall-stand-alone*` family has four members).**
> This is the **external-reviewer problem statement** — the single *living, reviewer-facing* artifact for
> the value-model wall, kept current per the self-tcb-reduction SKILL §12. It is **NOT a plan**. The
> **build plan** is `value-model-wall-stand-alone-plan-2.md` (rev 2; supersedes the now-obsolete rev-1
> `value-model-wall-stand-alone-plan.md`); the fix-review of rev 1 is `value-model-wall-stand-alone-fix.md`.
> Canonical characterization of the *measured wall* lives HERE (§8); plan-2 §0.5 is the internal
> *execution ledger* (what the build did) and defers to this file for the wall statement.

---

## 0. What we are asking you

A deductive verifier verifies a **mirror of its own compiler back-end**. The back-end is written in a
statically-analysable subset of Python and manipulates the compiler's intermediate representation (IR),
which is a tree of Python **`Dict[str, Any]`** nodes and **`str`** payloads. We have driven the trusted
core of this self-verification down to a residual that is dominated by **two value-model walls**:

1. **Heterogeneous `Dict[str, Any]`** — a dictionary whose values are simultaneously `int`, `str`,
   `bool`, `list`, and nested `dict`, which cannot be given a single monomorphic target-language value
   type, so the emitter collapses the value to `int` and a well-typedness check fails.
2. **String as a character sequence** — strings are modelled as opaque scalars carrying a length and a
   library of faithful *value* operations, but **character-level iteration** (`for ch in s`,
   `enumerate(s)`, `s[i]`, `ch == "("`) has no model, so a pure string-processing method fails to emit
   valid target code.

We want a **state-of-the-art comparison**: which existing techniques (from PL theory, SMT-backed
verification, refinement/gradual typing, verified compilation) bear on giving these two constructs a
**sound, automatically-dischargeable, first-order** model — under a deliberately weak contract
(type-safety + frame + termination, *never* functional value-correctness) — and, equally valuable, a
rigorous argument that under our constraints **no such technique suffices** and the residual is a genuine
trusted boundary. §6 poses the questions with candidate anchors; §7 is a frozen, reproducible benchmark.

---

## 1. The system and its self-verification bootstrap

**PyCSL** is a deductive verifier for a statically-analysable subset of Python. It lowers that subset to
**WhyML** (the input language of the **Why3** platform), which generates verification conditions
discharged automatically by **SMT solvers (Alt-Ergo, Z3, CVC5)**. Contracts are Hoare-style
(`requires` / `ensures` / `assigns`) written in `#@` comments.

Its trusted base is pinned by a **3-axiom ledger**, mechanised in **Rocq 8.20 and Lean 4.29**
(`alt_ergo_correct`, `trusted_contracts_axiom`, `why3_implements_wp_w`), from which a soundness theorem is
proved. **Rule we cannot break:** any extension that introduces a new *target-language value shape* must
**co-land an axiom-free Rocq+Lean certificate**, keeping the ledger at exactly 3 (verified by
`Print Assumptions` / `#print axioms`).

**Self-verification bootstrap.** The WhyML **emitter** (the compiler back-end, "Module 6", ~4 kLOC) is
itself written in the verifiable Python subset. PyCSL verifies a **mirror** of its own emitter: each
emitter method is either **verified** (proved against a contract) or a **`\trusted` stub** (an *assumed*
contract). The campaign minimises the trusted core (currently 1236 `\trusted` markers, ~100 methods
body-verified). The residual is dominated by methods that read/build the IR — represented as
`Dict[str, Any]` with `str` payloads. **The value shapes the verifier cannot yet model about itself are
exactly the ones its own back-end is built to traverse.**

**The scope cut that matters (recurs throughout).** The self-annotation contract is deliberately weak:

```
#@ requires True    #@ ensures True    #@ assigns <tight frame>
```

We verify **type-safety** (well-typedness of every projection — no `int`/`string` confusion), **frame**
(the method mutates only its declared footprint), and **termination** (Why3 requires it) — **never** the
*value* computed. A reviewer from full functional verification should recalibrate: we need the weakest
interesting guarantee. That is exactly why we believe the residual is *engineering-plus-metatheory*
rather than open research — and why we are asking you to confirm or refute that belief for the two value
walls below.

**Where this sits (LINK-3).** PyCSL's soundness rests on three links: **LINK-1** WP ↔ operational-
semantics soundness; **LINK-2** the Module-6 *encoding* faithfulness (Python-subset ⇒ WhyML); **LINK-3**
*emitter self-verification*. Both walls are on LINK-3. They are also a **bootstrap tension**: the
value-modelling capability needed to *verify* the IR-reading back-end is the same capability the back-end
would need to *emit* for a user program that manipulates `Dict[str, Any]` or does character-level string
work. Capability and certificate stay coupled (the certified `pydict` of §2.1 is exactly the deferred
heterogeneous-value model the mechanised metatheory needs).

---

## 2. What is already solved and certified (do not re-solve)

The residual is *not* a greenfield. Two foundations are built, gated, and (where a new value shape was
introduced) mechanically certified axiom-free. A proposal should **build on** these, not re-derive them.

### 2.1 A certified heterogeneous-value datatype — `pydict` / `pyval`

We have a WhyML datatype for exactly the heterogeneous Python value:

```
type pyval  = PInt int | PStr string | PBool bool | PNone
            | PList (list pyval) | PDict pydict
with pydict = DNil | DCons irkey pyval pydict          (* interned string keys *)
```

with a structural `size` measure, a proven lemma pack (sub-term size-decrease, lookup laws), and a
**string-keyed symbol-table variant** `sdict` (`SNil | SCons string pyval sdict` + a total `slookup`).
Both carry **axiom-free Rocq 8.20 + Lean 4.29 certificates** (`Phase2c_PyValDict.v`, `PyValDict.lean`);
the ledger stayed at 3. Proof-by-evaluation over concrete keys uses Why3's `compute_in_goal`.

This datatype **can represent** a `Dict[str, Any]` value faithfully. What is missing is that the emitter
does not **route** generic-dict reads/builds through it (§2.3, wall 1).

### 2.2 A faithful opaque-string model with *value* operations

Strings are modelled as Why3 `string` with `String.length` and a library of **faithful value operations**
carrying the strongest *sound* laws (never over-claiming): `str_strip_op`, `str_sub_op` (substring),
`str_startswith_op` / `str_endswith_op` (with iff-length laws), `str_eq_op`, `replace`/`lower`/`upper`
(literal cases constant-folded to exact Unicode results). Element-indexed split reads
(`s.split(sep)[i]`) lower to `str_split_elem_op` (a substring). **Just landed** (this session): faithful
**whole-list** `str.split(sep)` → `array string` (`str_split_op`, opaque `length >= 0`) for the
comprehension shape `[<str-elt> for t in s.split(sep)]`, byte-diff-0 on 759 reference programs, ledger
unchanged. What is missing is a model of the string **as a sequence of characters** (§2.3, wall 2).

### 2.3 The two walls, precisely

- **Wall 1 — heterogeneous `Dict[str, Any]`.** A single Python dict `{"file": s, "summary": counts,
  "vcs": [d0, d1, …]}` binds keys to values of *different* types (string / `map string int` / list of
  dicts). WhyML has no single map type for it (`map string ?`), and `pyval` (§2.1) is not yet the
  emitter's target for generic-dict construction/read, so the emitter falls back to `int` and the value
  read/built type-clashes. This is the "no-more-int doctrine at scale": lower each Python value to its
  faithful value class instead of coercing to `int`.
- **Wall 2 — string as a character sequence.** `for ch in s` / `enumerate(s)` / `s[i]` (a 1-char string)
  / `ch == "("` have no model: iteration over a string emits undeclared `iter_length` / `enumerate_1` /
  `iter_get`, and a character is hashed to an `int` rather than typed as a 1-character `string`. The
  opaque-scalar model (§2.2) is deliberately blind to character structure.

---

## 3. Measured evidence (verbatim; whole-body proof, never an idiom in isolation)

Our discipline: a stub is "convertible" only if its **entire real body**, transcribed into the mirror,
lowers to well-typed WhyML that discharges. We port → prove → classify → revert. Recent measurements:

**Wall 1 — nested heterogeneous dict (`_build_soundness_report`, a real emitter method).** Body ends
`return {"file": filename, "summary": counts, "vcs": vcs}` where `counts : Dict[str,int]` and
`vcs : List[Dict[str, Any]]`. The mirror already carries the full body as a `\trusted` stub; removing the
`\trusted` marker and type-checking the emitted WhyML:

```
[level] L1 ✓  L2 ✓  L3-tc ✗
[!] Emitted WhyML does NOT type-check
    ...but is expected to have type int
```

The same failure recurs across a family of 10 sibling methods (`_build_method_result_ensures_map`, …)
that return `Dict[str, List[Dict[str, Any]]]`. Census of 26 `Dict[str,Any]`-param methods: **0 convert**;
the class is dominated by string-emission dispatch, self-state composition, and generic Any-tree walkers,
with heterogeneous-value returns as the type-checking blocker.

**Wall 2 — character iteration (`_strip_outer_parens`, a pure string function — the *best* B1-free
lead).** Source:

```python
@staticmethod
def _strip_outer_parens(s: str) -> str:
    s = s.strip()
    if not (s.startswith("(") and s.endswith(")")): return s
    depth = 0
    for i, ch in enumerate(s):
        if ch == "(": depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return s[1:-1].strip() if i == len(s) - 1 else s
    return s
```

Emitted WhyML (abridged) and the type-check verdict:

```
let ..._strip_outer_parens (self: ...) (i: int) (ch: int) : string      (* (1) wrong params *)
  = let s = ref (str_strip_op !s) in                                     (*     !s unbound   *)
    ...
    while !idx < (iter_length (enumerate_1 !s)) do                       (* (2) undeclared   *)
      let ch = ref (iter_get (enumerate_1 !s) !idx) in
      if (ch = 747334986) then depth := !depth + 1                       (* (3) char as int  *)
    ...
[level] L1 ✓  L2 ✓  L3-tc ✗    unbound function or predicate symbol 's'
```

Three distinct defects: **(1)** the emitter took the `for i, ch in …` loop **tuple-target** `i, ch` as
the method's *parameters* and dropped the real parameter `s` (a static-method + tuple-unpack-loop
parameter-extraction bug — pure engineering, not research); **(2)** `enumerate` over a string emits
undeclared `iter_length` / `enumerate_1` / `iter_get`; **(3)** the character `"("` is compared as its
integer hash `747334986` (char typed `int`, not 1-char `string`). Census of the 13 emitter-string /
WhyML-gen methods: **0 convert**; blockers are char-iteration, the recurring `iter_length` opaque-string-
iteration defect, and the parameter bug.

**Corpus-safety datum.** All the string/collection lowerings that DID land are **pattern-gated** and
**byte-diff-0** across the 759 reference programs — evidence that a *narrow, gated* value-model extension
can be introduced without perturbing existing emission (relevant to admissibility, §4).

---

## 4. Constraints bounding admissible solutions

- **Target: WhyML → Why3 → SMT, automatic proof only** (Alt-Ergo/Z3/CVC5, best-of-N), VCs discharging
  within a per-goal budget (~seconds). No interactive proof in the emission path.
- **First-order, monomorphic-friendly.** SMT back-ends want first-order, finitely-instantiable
  encodings; unbounded polymorphism / higher-order values must be defunctionalized or monomorphized.
- **Termination is mandatory and SMT-dischargeable.** Program `let rec` needs an explicit `variant { … }`
  decreasing on a structural sub-term; any iteration-over-value we synthesize must expose such a measure
  (the `pyval`/`size` lemma pack of §2.1 exists for this).
- **The 3-axiom ledger is fixed.** No new trusted axiom; any new value shape or lemma is **mechanically
  certified** (Rocq 8.20 + Lean 4.29, axiom-free). `pyval`/`pydict`/`sdict` + certificates already exist
  and are reusable.
- **Byte-for-byte additivity.** Every emitter change must be **byte-identical** on all 759 reference
  programs (gated). The corpus-safety datum (§3) makes a *pattern-gated* value model admissible.
- **Weakest-guarantee scope (§1).** type-safety + frame + termination only — **never** the value. A model
  of a heterogeneous dict or a character sequence need not be proved I/O-equivalent to Python's; it must
  be **well-typed, framed, terminating**. (A reviewer may note a simulation/refinement obligation is
  *desirable*; under our contract it is not *required*.)
- **Self-hosting reflexivity.** The value model is emitted by the back-end, which is itself verified — the
  model's own emission code must stay in the verifiable subset or be `\trusted`-and-audited.

---

## 5. Open questions for the reviewer (candidate SOTA in brackets)

**Wall 1 — heterogeneous `Dict[str, Any]`.**

1. **Routing generic-dict reads/builds through a tagged-union value.** What is the right discipline for a
   *verifying compiler* to lower `d.get(k)` / `d[k] = v` / `{ "a": x, "b": [ys] }` over a `Dict[str, Any]`
   to operations on a **certified tagged union** (`pyval`/`pydict`, §2.1) such that a subsequent projection
   `d.get(k)` recovers the value's real type (string vs int vs list) instead of collapsing to `int`?
   *[gradual typing & the dynamic type `?` with typed-untyped boundaries (Siek–Taha; Typed Racket's
   `Any`); tag-checked coercions / space-efficient casts; refinement types over a universal value (LiquidHaskell,
   F\*, Dafny); "type-tag reconstruction" in dynamic-language compilers.]*
2. **Per-key heterogeneity without dependent types.** A record `{"file": str, "summary": map, "vcs": list}`
   is really a **dependent** map (value type varies per key). In a first-order SMT target with no
   dependent types, is the right encoding (a) a `pyval` tagged union with projection lemmas, (b) a
   generated *record* type per statically-known key-set, or (c) a row-typed / extensible-record encoding?
   *[extensible records & row polymorphism (Rémy, Leijen); "scrap your boilerplate" / open unions;
   monomorphization of a closed key-set; CompCert-style per-shape struct generation.]*
3. **Do we need value soundness, or only tag well-typedness?** Under the type-safety+frame contract, is it
   sound to model a heterogeneous dict as an *arbitrary* well-typed `pyval` (content unconstrained), the
   way we already model `str_split_op` as an arbitrary `array string`? Where is the line past which a
   projection law (`get k (set k v d) = v`) becomes necessary for a *downstream* method to type-check?
   *[abstract interpretation / type-only abstraction; the "faithful under-approximation" discipline we
   already use for opaque ops.]*

**Wall 2 — string as a character sequence.**

4. **A char-sequence string model that stays SMT-automatable.** What is the right model for
   `for ch in s` / `s[i]` / `enumerate(s)` / `ch == c` that (a) types a character as a 1-character string
   (or a codepoint) rather than an int hash, (b) gives iteration a **structural** termination measure, and
   (c) still discharges automatically? *[the SMT-LIB **theory of strings & sequences** (Z3/cvc5: `str.at`,
   `str.++`, `str.len`, `str.substr`) — directly relevant, since our back-end is Why3/SMT; Why3's own
   `string`/`seq` theories; a `seq char` reduction with a length variant.]*
5. **Loop-over-characters → terminating recursion/loop with a decreasing index.** The `_strip_outer_parens`
   walk is an index loop with early return; the emitter mis-synthesized its parameters and its iterator.
   Independent of the parameter bug, what is the right lowering of a bounded `enumerate(s)` loop to a
   Why3 `while`/`for` with `0 <= i < String.length s` and a `variant`? *[bounded model of string indexing;
   Dafny/Viper string-index loops; the `int`-indexed `String.substring` we already have in §2.2.]*
6. **Is char-level string processing in-scope at all, or a trusted boundary?** Given that the *only*
   self-methods needing it are a handful of pretty-printer helpers, is a full char-sequence theory
   warranted, or is the honest answer to **leave these `\trusted`** and invest the string theory only if a
   user-program need arises? *[cost/benefit of theory adoption; the trusted-boundary discipline.]*

**Both walls.**

7. **Keeping the extension admissible (byte-diff-0 + no new axiom).** Given the corpus-safety datum
   (pattern-gated lowerings are byte-inert on 759 programs), how narrow must a value-model recognizer be to
   stay provably inert on non-matching code while covering the real IR-readers? *[pattern-gated rewriting;
   conservative-extension arguments.]*

---

## 6. Success criteria — the frozen benchmark

A proposal is validated by clearing **any** of these, reproducibly, under the constraints of §4
(automatic SMT proof; ledger stays at 3, verified by `Print Assumptions` / `#print axioms`; byte-diff-0 on
the 759 reference programs; whole-body proof, not an idiom in isolation):

- **B1 (Wall 1, minimal):** the method `_build_soundness_report` — return
  `{"file": str, "summary": Dict[str,int], "vcs": List[Dict[str,Any]]}` — transcribed verbatim into the
  mirror, **type-checks and discharges** its `#@ requires True / ensures True / assigns \nothing` contract.
- **B2 (Wall 1, family):** the same for ≥1 of the `_build_method_*_ensures_map` family
  (`Dict[str, List[Dict[str, Any]]]` return).
- **B3 (Wall 2, minimal):** the pure function `_strip_outer_parens` (verbatim, char-iteration and all)
  **type-checks and discharges** the same weak contract — i.e. `enumerate(s)`/`s[i]`/`ch == "("` acquire a
  model and the parameter emission is correct.
- **B0 (either wall, negative — equally valuable):** a rigorous argument that, under §4's constraints
  (first-order automatic SMT + byte-diff-0 + ledger-3 + weakest-guarantee), **no** technique gives a
  sound model of per-key-heterogeneous dicts (B1/B2) or SMT-automatable char-sequence strings (B3) — so
  these are a principled trusted boundary, not a backlog.

A validated B1/B2/B3 must **co-land its axiom-free Rocq 8.20 + Lean 4.29 certificate** if it introduces a
new value shape (the `pyval`/`sdict` certificates are the template); a validated B0 is accepted as the
honest close-out of the value-model track.

---

## 7. One-paragraph brief + reference artifacts

**Brief.** A deductive verifier (Python-subset → WhyML → Why3 → SMT; 3-axiom Rocq+Lean ledger) verifies a
mirror of its own IR-manipulating compiler back-end under a deliberately weak contract (type-safety +
frame + termination, never value-correctness). Two value-model walls block the residual self-verification:
**heterogeneous `Dict[str, Any]`** (per-key-varying value types, no single WhyML map type → emitter
collapses to `int` → type-check failure) and **string-as-character-sequence** (`for ch in s`/`enumerate`/
`s[i]` unmodelled → undeclared iterators, char-as-int-hash). A certified heterogeneous-value datatype
(`pyval`/`pydict`/`sdict`, axiom-free Rocq+Lean) and a faithful opaque-string value library already exist;
the gap is *routing* generic-dict reads/builds through the datatype and giving strings a char-sequence
model — first-order, SMT-automatable, byte-diff-0, ledger-preserving. We ask for the state-of-the-art
mapping (gradual/tag-checked typing; row/extensible records; the SMT-LIB string/sequence theory;
defunctionalization; refinement types) onto these constraints — or a rigorous impossibility argument that
closes the track.

**Reference artifacts (in the repository).**
- Certified value datatypes + certificates: `src/formal-semantics/rocq/Phase2c_PyValDict.v`,
  `src/formal-semantics/lean/PyCSL/PyValDict.lean` (axiom-free; `pyval`/`pydict`/`sdict`, `size`, lemma pack).
- The emitter (self-verified back-end): `src/pycsl/module6_whyml/` (`expressions.py`, `statements.py`,
  `preamble.py`, `functions.py`); the certified-fold generator `generic_fold.py`.
- Landed value-op lowerings (context for what "faithful, gated, byte-diff-0" looks like): faithful string
  value ops and whole-list `str.split → array string` in `expressions.py`; `str_split_op` + the
  `uses_str_split_comp` array trigger.
- Measured censuses (this campaign): `getting-better/tier3/tier5-value-model-census.md`,
  `getting-better/tier3/emission-defect-spike-findings.md`, and the §8 iteration ledger in
  `self-tcb-reduction.md`.
- The bounded-fold sibling problem (already externalised): `wall-plan-v2-phase2c-stand-alone.md`,
  `ir-traversal-residual-stand-alone.md` (loop→structural-recursion synthesis — the *control*-shape wall,
  distinct from this *value*-shape wall).
- Reproduce a wall in one command: `python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl`
  after removing a `\trusted` marker from `_build_soundness_report` (B1) or `_strip_outer_parens` (B3).

---

## 8. Measured update — 2026-07-09 execution + censuses (sharpens §2/§3/§6; the wall is now precise)

Since this report was written, the bounded plan (`value-model-wall-stand-alone-plan-2.md`) was executed and
several further whole-body censuses run. Two of the walls' faces were **closed as bounded** and the dynamic
face was **sharpened** to a precise, reproducible statement. Net self-annotation `\trusted`: **1236 → 1234**.
All results are byte-diff-0 on the reference corpus, ledger held at 3.

**Newly SOLVED / banked (do not re-solve).**
- **String-as-character-sequence (was Wall 2) — SOLVED, no new theory.** A character is a 1-character
  `str_sub_op` string; `enumerate(s)`/`for ch in s` lowers to an integer-indexed `while` with the arithmetic
  variant `String.length s − i`; `ch == c` is `str_eq_op` compiled as an unconstrained boolean (no SMT
  string theory in any VC). `_strip_outer_parens` proves (loop invariant + variant decrease + postcondition
  all Valid). No new value shape, no certificate.
- **Closed-key records (route R) — CONFIRMED + already certified.** `@dataclass`/`TypedDict` monomorphize to
  native WhyML records with faithful per-field types and thread across a call boundary; the record value
  shape is certified axiom-free on **both** provers (`Phase2b_RecordVal.v` + `RecordVal.lean`). No new
  certificate is needed for a record over certified fields.

**Sharpened dynamic wall (heterogeneous `Dict[str, Any]`) — the read is NOT the blocker; its COMPOSITION is.**
A mirror-only defensive-projection (`d.get("k")` → `slookup "k" d` + a total `match` over `pyval`) was fully
built and measured. It dissolves the read cleanly — but a census of **70** generic-dict-read `\trusted`
methods found **net-new unblocks = 0**: the read is *never the sole blocker*. Every real reader composes the
read with a second wall — string-set membership over an int-modelled set, collection-element/array typing,
self-state mutation, a giant `_expr_to_whyml` sibling call, or a nested-heterogeneous return. Two further
bounded leads were **measured and refuted**, both reducing to this composition:
- **`PList`/`PDict` collection-valued projection** — the collection-valued reads (`get(k, [])`/`{}`,
  `List[Dict]` iteration) are **not over generic pyval** but over the **emit_ir IR-node ADT args**
  (`array emit_ir`), plain **arrays** (`array int`), or **module-constant tuple-keyed maps** — distinct
  shapes, ~0 converted by a pyval-list projection.
- **emit_ir-args reflection** — the arg-count model already exists (`nargs_of : int`, `args_of : array
  emit_ir`); the 3 `\trusted` methods that read emit_ir args all *iterate/index* the args and call
  `_expr_to_whyml` per element + mutate self-state → `nargs_of` converts 0.

**B1′ measured wall (the frozen reproducer, refined).** `_build_soundness_report`, `\trusted` removed, stalls
at its **first statement** `ir_data.get("functions", [])` — a collection-valued read (`List[Dict[str,Any]]`)
whose result is *iterated*, `f["name"]`/`f.get("contracts",{}).get("ensures")` projected, folded into a
variable-key `map string (option int)` (`counts[bucket] += 1`), set-algebra'd and `sorted`, and returned as a
nested-heterogeneous record. A pointwise `pyval` read model does not lift it; the wall is the **composition**.

**Two partial-B0s now established (equally valuable closures, per §6 B0).**
1. **Corpus-facing generic-dict projection is byte-diff-UNSAFE.** The reference corpus itself exercises the
   target shapes (7 `Dict[str,Any]`, 10 `.get("…")`, 4 `.values()/.items()` walks over 844 programs), so no
   recognizer is simultaneously corpus-inert and mirror-covering; the non-mirror walker residue is a
   principled `TRUSTED(essential)`.
2. **A theory-composition boundary.** The certified `pyval.size` measure collides *by name* with the
   `emit_ir.size` IR-node ADT measure, so a mirror file emitting the emit_ir ADT cannot also host the pyval
   theory (a rename would perturb existing emitters' `.mlw`).

**The sharpened open question for the reviewer.** Not "model a heterogeneous dict read" (solved pointwise via
the certified `pyval`/`slookup`) but: **how does a *verifying* compiler discharge the COMPOSITION** — a
generic-dict read whose result is iterated/indexed, threaded through a variable-key homogeneous-map fold,
set-algebra, and a nested-heterogeneous record return — **as one whole-body VC, first-order, automatic,
byte-diff-0, ledger-preserving**, when the same pipeline must also host the emit_ir IR-node ADT (the
`size`-theory-collision constraint)? A rigorous "no technique can, under these constraints" remains an
equally valuable closure. The bounded floor is **1234**; the composition is the wall.

---

## 9. Measured update — 2026-07-10: the composition wall is BOUNDED via the TypedDict route (sharpens §8)

§8 characterized the dynamic `Dict[str,Any]` composition (canonical: `_build_soundness_report` / B-comp) as
the research-grade wall — measured against the **pyval-decoder route** (route the read through `pyval`/`slookup`),
where the read's *composition* with iteration/fold/nested-return is the open problem (SOTA §5).

A spike of the **TypedDict route** (monomorphize each dict to a native WhyML record UP FRONT, sidestepping the
`pyval` decoder) overturns that pessimism **for this route**: B-comp decomposes into **~5 BOUNDED
recognizer/type-plumbing features** — the same family as the shipped record `.get`→field (G1), string-field
`str_eq_op` (G2), option-of-record, `List[dataclass]` (WL-04b), and compound-const-map lowerings that landed
this campaign. Verified walls: (1) `List[<record>]` field + element access (element type dropped to int),
(2) set-comprehension over `List[record]` → an opaque op, needing a comprehension→fold synthesis into the
already-proven `map string bool` A-set model, (3) nested `.get(...).get(...)` + `bool()`, (4) `List[record]`
append/return `materialize` element-type, (5) compound-field TypedDict construction. The variable-key map-fold
(`counts[bucket]+=1`) is ALREADY handled. Wall map: `getting-better/composition-wall/bcomp-typeddict-wallmap.md`.

**Consequence for the open question.** The research-grade framing (SOTA §5 — synthesize records+decoders from
reflective field-access) is specific to the **pyval-decoder route**, which must *infer* the record shape from
`d.get(k)` patterns. The **TypedDict route requires the shape to be DECLARED** (a runtime-inert `TypedDict`
annotation — the annotation IS the "synthesis" input), reducing the problem to bounded lowering. So the honest
statement is: **generic-`Dict[str,Any]`-composition inference is research-grade; the same method with a declared
`TypedDict` shape is a bounded ~5-feature lowering build.** A reviewer's SOTA-synthesis answer buys the
*annotation-free* case; the annotated case is already engineering (in progress). B0 (impossibility) is therefore
NOT warranted for the composition wall under a declared-shape (TypedDict) discipline.

---

## 10. Measured update — 2026-07-25: the Module-5 self-mut collector cluster is the SAME wall (sharpens §3/§8)

**Context.** Canonical `\trusted` floor is now **908** (down from the 1234 of §8; the intervening cut is the
banked `pyval`/term-ADT + string/list/search/flatten walker campaign, [[pyval_walker_vein]]). This session
spiked the **Module-5 IR-emitter "self-mut collector" cluster** — the `_collect_*` / `_synthesize_*` family in
`frontend/Module5_IREmitter.py`, the largest non-parser residual cluster (~2 dozen mirror stubs). Goal:
convert-or-BOUNDARY. Two structurally-disjoint candidates were ported verbatim (live body + real signature)
and run under `--fun` whole-body proof. **Both fail on the value-model wall of §3 — confirming the cluster is
not a new frontier but the SAME `Dict[str,Any]`-composition wall, now compounded with collection-RESULT
modelling.**

**Spike A — `_collect_str_decode_locals` (generic-`Any` IR walker → `Set[str]`).** Verbatim body: a lifted
nested-closure recursion over `.values()` that accumulates `node["target"]` into a `Set[str]` when
`node.get("stmt")=="Assign"` and the value is a `.decode()` call. The nested closure lifts cleanly
(`pycsltojsonemitter__rec` appears as a top-level function — closure-capture is NOT the blocker). Verbatim
Why3 error:

```
This expression has type PyCSL_Program.StrSet.set,
but is expected to have type int -> option.Option.option int
```

Reading: the `Set[str]` result model **exists** (`StrSet.set`), but the generic-`Any` `.values()` recursion
types the heterogeneous dict as the int-erased map `int -> option.Option.option int` (§2.3 wall 1), so
`node["target"]` cannot be given the `string` type the `.add` needs. **Wall 1 (heterogeneous dict) ∧
collection-result (Set) — two stacked capabilities.**

**Spike B — `_collect_2d_params` (IR `List[Dict]` loop → `sorted(Set[str])` = `List[str]`).** Structurally
disjoint from A (flat loop, no closure, delegates to `_scan_2d_in_stmt`, returns a sorted list). Verbatim
Why3 error:

```
This expression has type int -> option.Option.option int,
but is expected to have type int
```

Reading: the loop variable `stmt` drawn from `body_ir: List[Dict[str,Any]]` is the int-erased map
`int -> option int`; it cannot be passed where a faithfully-typed IR node is expected, and `sorted(result)`
is the Set→List collection-result on top. **Same wall 1, again compounded with collection-result.**

**Convergence (the §12-trigger-2 characterization).** Two disjoint collectors — one closure/Set, one
loop/sorted-List — dissolve into the identical `int -> option.Option.option int` heterogeneous-dict typing
that §2.3/§3 already isolate as the research-grade wall. Every remaining member of the cluster reads the same
raw `Dict[str,Any]` IR as its FIRST operation, so each is blocked upstream of anything cluster-specific.
Beyond wall 1 the cluster also needs, per member: **collection-result modelling** (`Set[str]`/`List[str]`
build-and-return, the §8 "B-comp" set-algebra leg), and for the `ast.*`-reflecting members
(`_collect_class_fields`, `_collect_union_arms`, `_synthesize_typeddict_functional`,
`_synthesize_namedtuple_functional`, `_synthesize_overload_guard`) additionally **tuple-return-pyval**,
**Python-`ast`-node construction** (`ast.Constant(value=None)`), and **`type()`/`getattr` annotation
reflection** — i.e. ≥2, typically ≥3, STACKED capabilities per stub. Under the driver's no-stack rule this is
a **CERTIFIED-BOUNDARY**, not a bounded one-feature build.

**Consequence for the open question (unchanged, re-confirmed at floor 908).** The §9 dichotomy stands: the
annotation-free generic-`Dict[str,Any]`-composition read remains research-grade (SOTA §5); the collector
cluster is a concrete, reproducible instance of it (the two verbatim errors above are the frozen benchmark
δ for this cluster). A declared-shape (TypedDict, §9) route would reduce these to bounded lowering, but the
live emitter reads raw `Dict[str,Any]` — so converting the cluster in place is gated on either the
research-grade decoder-synthesis answer OR a live-emitter retype to TypedDict (a separate, larger build).
No spike was left in the tree; floor unchanged at 908; 3-axiom ledger untouched.

## 11. Measured update — 2026-07-27: the READER/WALKER cluster is NOT the value-model wall — it is RECOGNIZER-GATED (sharpens §3/§8/§10; separates two claims that §3 conflated)

**Context.** Floor now **883**. This spike isolation-measured the generic-`Dict[str,Any]` `.values()`/
`.items()` **reader/walker** stubs (the `core_ir_semantic.py` void-checker + bool-predicate family — the ~20
`.values()`-walk pool §8 folds into "wall 1"), asking convert-or-BOUNDARY: does the built `pyval`/`pydict`
model reach any of them, or is the dict typing an intrinsic `int -> option int` floor?

**The decisive datum overturns the "value model is the wall" framing for this cluster.** The value model
already lowers generic `.values()`/`.items()` dict walks **non-vacuously**. Living proof: the ALREADY-CONVERTED
`_cs_descend`/`_pb_descend`/`_sa_walk`/`_contains_result`/`_body_has_return` in `core_ir_semantic.py` emit
`(v: pyval)` parameters, `PDict/PList/PStr` spine matches, and a faithful `values (d: pydict) : list pyval`.
A `Dict[str,Any]` param does **not** intrinsically erase to `option int` — the §2.1 `pyval`/`pydict` datatype
is the working carrier, and `.values()` is modelled as spine traversal.

**What actually blocks the residual is RECOGNIZER coverage, not the value model.** A stub int-erases (the §3
`int -> option int` symptom) precisely when **no bespoke recognizer matches its exact structural shape** — it
then falls through to the default int-hash emitter. Three verbatim-port + emit + read datums (reverted clean):
1. `_pb_stmt` (`.get("stmt")`-dispatch → list-field iteration → else `.values()` descend): emits `s: int`,
   `s.get("stmt")`=`s_get_1 285165683` (key hashed), `"While"`=`1685277026` (literal hashed), the list-fields
   `s.get("invariants") or []` → vacuous `Array.make 1024 0`, `s.values()` → **nullary** `s_values_0 ()`
   disconnected from any real dict. Sound-but-VACUOUS int-hash erasure (the §6 anti-pattern). No recognizer
   covers the "named-tag dispatch + list-field iteration" statement-handler shape.
2. `_gso_walk`: `node: int`, `typeof_op 422` (the `isinstance(node,dict)` test lowered against a **constant**
   unrelated to `node`), `node_values_0 ()` nullary. INT-ERASED — yet this is ONE field-read different from the
   CONVERTED `_sa_walk`; `recognize_sawalk`'s pre-action matcher is tailored to sa_walk's exact two-raise
   nested-isinstance shape and rejects gso_walk's compound single-raise guard.
3. `_union_c8_test_references_union_var` (2-param existence walk `any(self(v,union_vars) for v in test.values())`):
   the existence recognizer **fires** and emits the CORRECT non-vacuous postcondition
   `exists _fk. 0<=_fk<len /\ self(a[_fk] union_vars)` — but L3-tc FAILS `unbound symbol 'union_vars'`: the
   read-only env param is not threaded into the generic-values-loop arm's emitted logical spec. A scoping gap,
   not an erasure.

**Composition (core_ir_semantic.py, 56 trusted).** Every zero-build-reachable shape is ALREADY CONVERTED
(pure-descend `.values()` walkers, thin-fanout body walkers, 1-param `any()` bool-existence, the sawalk
env-threaded walker). The 56 residual each require a DISTINCT bespoke recognizer extension — env-param
threading, compound-pre-action matcher, tag-dispatch+list-field recognizer, nested-closure `found=[False]`
mutable-cell support, plus set-membership/`rsplit`/`warn`/arithmetic secondaries.

**Consequence — the two claims §3 must separate.** (i) For the **reader/walker** cluster the value-model wall
is BROKEN: `pyval`/`pydict` is a sufficient carrier; the boundary is a set of BOUNDED, low-yield (+1-marker
each) recognizer extensions of a shared, non-mirrored emitter (`generic_fold.py`), each carrying only the
mechanical §10c all-importer-mirror L3-tc obligation — **not research-grade**. (ii) The §10 collector /
`_build_method_*_map` **BUILD** family (heterogeneous-dict CONSTRUCTION + collection-result + self-state)
remains the genuine ≥3-stacked research-grade wall — the open question of §5 stands only for the value-
*producing* half. The frozen §6 benchmark is unchanged; the reader-side δ is now known to be recognizer
engineering, not a modelling open-problem. No spike left in the tree; floor unchanged at 883; ledger 3.
