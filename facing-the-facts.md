# facing-the-facts.md — The ceiling blocking body-faithful self-verification of the PyCSL emitter

**Audience:** anyone — including readers with no prior PyCSL context — who wants to understand, inquire about, or compare against the state of the art the specific wall we hit when trying to make PyCSL formally verify *its own code generator*.

**One-sentence statement of the problem.** To verify PyCSL's WhyML code-generator *with PyCSL itself*, we must verify a body of Python whose functions are **string-producing metaprograms over a dynamically-typed, JSON-shaped intermediate representation**, against a **denotational specification of the strings they emit** — and both halves of that ("metaprogram over `Any`-typed reflective data" and "spec = meaning of the emitted object-language text") sit outside what a Hoare-style deductive verifier with an SMT backend can currently discharge. This document pins down exactly where, with evidence, and lays out the literature to compare against.

This is a companion to — and a level *below* — `src/self-annotate/semantic-ceiling.md`. That document asks "*given* we can write a contract, how do we make a string-shape contract mean the right state transformation?" This document asks the prior question: "*can we even verify the function body against any non-trivial contract at all?*" The answer we found is **not yet** — and the reasons are structural, not a missing lemma.

---

## 1. Background (self-contained)

### 1.1 What PyCSL is
PyCSL is a **deductive verifier for a subset of Python**. You annotate a Python function with a Hoare-style contract — preconditions (`requires`), postconditions (`ensures`), and a frame (`assigns`) — written in special `#@` comments. PyCSL compiles the annotated Python through a six-stage pipeline (ingest → parse → weave annotations → semantic analysis → emit an intermediate representation (IR) → translate to WhyML) into **WhyML**, the input language of the [Why3](https://www.why3.org/) platform. Why3 generates verification conditions (VCs) and discharges them with SMT solvers (Alt-Ergo, Z3) or, when those fail, with proof assistants (Rocq/Coq, Lean). If every VC is proved, the function provably satisfies its contract.

The translation from Python's rich values to WhyML's typed logic is the heart of the tool. A Python `int` becomes a Why3 `int`; a `str` becomes a Why3 `string`; a `list` becomes an `array int`; a class becomes a WhyML **record** type; a dict becomes a `map`; and so on. Crucially, **anything PyCSL cannot model faithfully it must either reject or coarsen** (e.g. an unmodeled value collapses to a placeholder `int`, or an unmodeled function is declared `\trusted` — assumed correct without proof).

### 1.2 The self-verification goal ("self-annotation")
PyCSL's TCB (trusted computing base) includes its own compiler: if the WhyML emitter is buggy, a "proof" is meaningless. The long-term project is to **shrink that trust** by having PyCSL verify its own source. `src/self-annotate/` holds annotated copies of `src/pycsl/` that PyCSL runs on itself. The end goal is a chain that connects a mechanized soundness theorem down to the running compiler:

```
  formal model (Rocq/Lean)                 real compiler (src/pycsl/)
  ┌──────────────────────┐                 ┌──────────────────────────────┐
  │ weakest-precondition  │                 │ Python → IR → WhyML emitter   │
  │ calculus + soundness  │   LINK 1/2/3    │ module6_whyml/statements.py   │
  │ theorem (proved)      │ ──────────────▶ │ (the code generator)          │
  └──────────────────────┘                 └──────────────────────────────┘
```

- **LINK 1** — the formal model's statement AST corresponds to the real IR.
- **LINK 2** — an *empirical* byte-for-byte check that a formally-specified emitter and the Python emitter produce identical WhyML on a corpus (`bin/extraction-byte-diff.sh`).
- **LINK 3** — **the subject of this document**: the Python emitter, annotated, **proves against its own contracts**. Today the emitter functions are `\trusted` stubs (`requires True; ensures True; assigns \nothing`, body elided) — so LINK 3 proves only that the *signatures* type-check, **not** that the emitter computes anything correct. "Body-faithful" means replacing a `\trusted` stub with a *real* contract that the *actual body* is verified against.

### 1.3 What "body-faithful" requires, concretely
For one emitter method, body-faithful verification means PyCSL must:
1. **Model every value the body touches** — the IR node it consumes, the strings it builds, the transpiler state it reads/writes — as a typed WhyML value.
2. **Lower every operation the body performs** — dict lookups, string methods, recursion into sub-nodes, container mutation — into WhyML the SMT backend understands.
3. **Discharge a postcondition** relating the returned WhyML string to a specification of what that string should be.

We made real progress on (1) and (3) for *simple* shapes (see §6). The wall is that the emitter bodies require (2) over operations that have **no faithful WhyML model**, and (3) against a spec whose adequacy is itself an open problem (§5, and `semantic-ceiling.md`).

---

## 2. The artifact under verification

The code generator is `src/pycsl/module6_whyml/statements.py` (the self-annotate copy is `src/self-annotate/src/module6_whyml/statements.py`). It is a class of ~2000 lines whose `_handle_<X>_stmt` methods each take one IR statement node and **return a string of WhyML source**. Example — the dispatch core takes an IR statement and routes it:

```python
def _handle_fieldassign_stmt(self, stmt: FieldAssignStmt, rest, local_refs,
                             declared_refs, indent, in_loop) -> str:
    obj   = stmt.object                       # read IR fields
    field = stmt.field
    val   = self._expr_to_whyml(stmt.value.to_dict(), local_refs)   # recurse (sibling call)
    if val == "true":  val = "1"
    ...
    safe_field = self._field_label(_rec_lower, field)
    decl_fields = self._all_record_fields                           # read transpiler state
    if field in decl_fields:
        ftype = self._field_type_for(obj, field)
        if ftype in ("list", "tuple"):
            val = self._array_coerce_arg(val)
        ...
        code = f"{indent}{obj}.{safe_field} <- {val}"               # build WhyML text
    else:
        hash_field = stable_hash(field)
        self._add_abstract_op(f"val setattr_{self_type} ...")       # mutate transpiler state
        code = f"{indent}setattr_{self_type} {obj} {hash_field} ..."
    if rest:
        code += ";\n" + self._stmts_to_whyml(rest, ...)             # recurse on continuation
    return code
```

This is **representative**, not cherry-picked. These functions are *interpreters that emit code*: they pattern-match a tree, thread a symbol-table-like state, and concatenate target-language text.

---

## 3. The ceiling, measured

A static scan of the single file `module6_whyml/statements.py` (the 12 `_handle_*` methods plus their immediate helpers) quantifies what a body-faithful proof would have to model:

| Construct in the bodies | Count | Why it blocks a faithful proof |
|---|---:|---|
| `.get(...)` on `Dict[str, Any]` IR nodes | 66 | Heterogeneous map lookup returning `Any`; result is then *type-dispatched* (`if val.get("type") == "Call"`). No single WhyML type models a value that is "string here, list there, nested dict elsewhere." |
| `.to_dict()` on an IR node | 25 | Reflection: turns a typed node back into an untyped dict to re-dispatch. The boundary where the typed-IR refactor's benefit is *lost*. |
| f-string assembly | 153 | The output is built by interpolating sub-results into literal templates. Faithful modeling needs string concatenation **plus** a spec of the resulting string (see §5). |
| Distinct `self._*` transpiler-state fields touched | 92 | The emitter is a large mutable object (symbol tables, declared-ref sets, abstract-op accumulators, counters). A sound `assigns` frame must name every field a method may write; modeling 92 fields as one WhyML record is the "B4" problem. |
| String methods: `join`(11) `endswith`(4) `rsplit`(3) `replace`(3) `decode`(3) `strip`(2) `startswith`(2) `split`(2) `lstrip`/`rstrip`/`lower` | ~33 | Rich string algebra over the *contents* of identifiers and templates. WhyML's `string` theory exposes length/concat/equality but **not** `endswith`, `rsplit`, `replace`, `decode`, etc. as discharge-able operations. |

For scale: this one file carries **26 `\trusted` annotations** across **12 `_handle_*` methods** — i.e. essentially the entire emitter is currently assumed-correct, not proved.

### 3.1 The four "blockers" we catalogued (and why they are necessary but not sufficient)
The plan `b14.md` framed the obstacle as four mechanical blockers:
- **B1** the IR node type is opaque, so `stmt.field` is an untyped reflective access;
- **B2** f-string literal segments were lowered to integer hashes, not strings;
- **B3** sibling calls (`_expr_to_whyml`, `_stmts_to_whyml`) are themselves `\trusted` (`ensures True`), so a composed string can't be pinned;
- **B4** the bodies mutate transpiler state, so the frame can't be stated.

We **cleared the foundations for B1 and B2** (see §6) and confirmed B3/B4 are real. But the deeper finding is that **even with B1–B4 fully solved, the bodies still do not verify**, because of two ceilings B1–B4 do not name:

- **Ceiling A — expressiveness/modeling (this document's focus):** the operations themselves (`Any`-typed `dict.get` + type-dispatch, `.to_dict()` reflection, `str.endswith/rsplit/replace/decode`, heterogeneous container navigation) have no faithful WhyML lowering. This is *why the method body cannot be type-checked or framed* once un-`\trusted`, independent of the contract.
- **Ceiling B — semantic adequacy (`semantic-ceiling.md`'s focus):** even a body that verifies against a *string-shape* postcondition (`\result = indent ^ "let " ^ lhs ^ ...`) does not prove the deep property we actually want — that the emitted WhyML, *when evaluated*, performs the state transformation the weakest-precondition rule requires. Closing that needs a formal model of WhyML's own evaluation inside the contract layer.

The two ceilings compound: Ceiling A blocks the *easy* half (verify the body does what it textually does); Ceiling B blocks the *hard* half (show that text means the right thing).

---

## 4. Why this is intrinsically hard (the shape of the problem)

Strip away PyCSL specifics and the task is:

> **Verify, in a Hoare logic with an SMT backend, a higher-order string-producing metaprogram that interprets a dynamically-typed tree and threads a large mutable environment — against a denotational specification of the object-language text it emits.**

Each clause names a well-known hard area:

1. **Dynamically-typed / reflective data (`Dict[str, Any]` + `.to_dict()`).** The IR is effectively JSON. A value's "type" is a *runtime string tag* the code switches on. A monomorphic logic (Why3) has no type for "a value that is sometimes a string, sometimes a list, sometimes a nested record." Faithful modeling needs a **universal sum type** (a `Json`/`Dynamic` ADT) *and* every consumer rewritten to pattern-match it — which is a different program from the one we're trying to verify (and which re-introduces Ceiling B for each arm).

2. **String algebra on contents.** Verification of string-manipulating programs is its own research frontier. SMT string solvers reason about concatenation, length, and (partially) regular constraints; they do **not** robustly discharge programs that branch on `endswith`/`rsplit`/`replace`/`decode` of symbolic strings. These appear because the emitter manipulates *identifiers and templates as data*.

3. **The metacircular/object-language gap (Ceiling B).** The postcondition we ultimately want quantifies over *the semantics of the emitted WhyML*. That requires reifying WhyML's evaluation relation inside WhyML — a reflective/metacircular construction with the usual foundational hazards (you cannot, in general, get a system to fully prove the soundness of its own semantics; partial, audited, or stratified models are the realistic targets).

4. **Large mutable state + higher-order recursion.** The emitter threads ~92 mutable fields and recurses mutually (`_stmts_to_whyml` ↔ `_handle_*` ↔ `_expr_to_whyml`). Sound framing and termination/refinement reasoning over this is the "verify an interpreter with a big store" problem.

None of these is unsolved *in isolation* in the literature — but they are solved by **heavyweight, dedicated techniques** (verified-compiler-grade developments, dependent types, separation logic, custom string decision procedures), not by an SMT-backed Hoare verifier reading the program as-is. That mismatch *is* the ceiling.

---

## 5. The semantic-adequacy half (Ceiling B), in one paragraph

For completeness (it is fully developed in `semantic-ceiling.md`): a string-shape contract like `ensures \result = indent ^ "let " ^ lhs ^ " = ref " ^ rhs ^ " in\n" ^ rest` is *necessary but not sufficient*. `let x = ref 0 in` and `let x = ref 42 in` satisfy the *same* shape predicate, yet only one is correct (the one where `0`/`42` equals the evaluation of the source expression). Full adequacy requires `∀Q. eval(emitted_string) ⊨ Q ⟺ Q[x ↦ eval_expr σ e]` — i.e. an in-logic model `eval_whyml_stmts : string → state → state` of the object language. `semantic-ceiling.md` proposes to **axiomatize** that evaluator (human-audited axioms) and prove a per-handler coherence lemma — which is the realistic route, but it relocates trust into audited axioms rather than eliminating it.

---

## 6. What we *did* establish (so the ceiling is precisely located, not vague)

To be sure the wall is the modeling ceiling and not a trivial gap, we drove the foundations as far as they go and **proved the pieces that are tractable** (all byte-identical across the 624-file regression corpus; see §9 to reproduce):

- A class — including a `@dataclass` — now **registers as a WhyML record** with **typed fields**, including `str → string` (fixes B1 at the language level, plus a latent witness bug where a `string` field's invariant witness used the integer `0`).
- An **all-string-typed f-string** now lowers to a faithful Why3 `string` concatenation (fixes B2) rather than an integer hash.
- **Result:** a *small* function in the emitter's idiom proves body-faithfully end-to-end:
  ```python
  #@ ensures \result == stmt.target          # record-typed param, str field
  def emit_target(stmt: AssignStmt) -> str:
      return stmt.target                       # PROVES
  #@ ensures \result == "let " + name         # all-string f-string
  def let_binding(name: str) -> str:
      return f"let {name}"                      # PROVES
  ```

These prove that the *building blocks* are now expressible. The ceiling is that the **real method bodies** combine those blocks with the §3 operations (`Any`-typed `dict.get` + type-dispatch, `.to_dict()`, `str.endswith/rsplit/replace/decode`, 92-field mutation) that remain unmodeled — so scaling from `let_binding` to `_handle_fieldassign_stmt` is not incremental, it crosses Ceiling A.

---

## 7. State of the art to compare against

This is the list to take to experts or the literature. For each: what it is, and what it would (and would not) buy us.

| Area | Representative work | What it would buy | What it would *not* solve |
|---|---|---|---|
| **Verified compilers** | CompCert (Leroy), CakeML (Myreen et al.), Vellvm (Zdancewic et al.) | The gold standard: a machine-checked proof that *codegen preserves semantics*. Directly the property we want for the emitter. | These are written **in the proof assistant from the start** (Coq/HOL), not retrofitted onto a `Dict[str,Any]` Python metaprogram by an SMT verifier. Adopting this = rewriting the emitter as a verified function in Rocq/Lean — i.e. abandoning self-verification-by-PyCSL in favor of CompCert-style development. |
| **Translation validation** | Pnueli–Siegel–Singerman; Necula (cert. compilation); Sewell–Myreen–Klein (seL4 binary validation) | Per-run certificate that *this* output is correct, sidestepping verifying the generator. This is essentially what LINK 2 (byte-diff) is, weakly. | Validators must themselves be trusted or verified; and a *semantic* validator (not byte-diff) needs the object-language model of Ceiling B. |
| **Proof-producing / certifying code generation** | Magnus Myreen's proof-producing synthesis; certifying extraction | The generator *emits a proof alongside the code*, so the generator need not be verified. A promising reframing for PyCSL. | Requires building the proof-emission machinery; the proof obligations still rest on the object-language semantics (Ceiling B). |
| **Verified extraction / metacircularity** | MetaCoq (Sozeau et al.), CakeML's verified compiler bootstrap, verified Coq extraction | Precedent that a system can reason about *its own* representations and even bootstrap. Most relevant to "PyCSL verifying PyCSL." | Metacircular soundness has foundational limits; these efforts are massive and live inside a single trusted kernel, not across a Python/SMT boundary. |
| **SMT string solvers** | Z3-str / Z3 seq, CVC5 strings (Barrett, Tinelli et al.) | Decision procedures for concat/length/regular constraints — the engine that *could* discharge string-shape VCs. | Branching on `endswith`/`rsplit`/`replace`/`decode` of symbolic strings is outside the robustly-decidable fragment; performance/termination are real risks. |
| **Dynamically-typed data in proofs** | Refinement types (LiquidHaskell), dependent records, `Json`/`Dynamic` ADTs, gradual/typed dicts | A principled type for the `Any`-typed IR (a universal sum), enabling `dict.get`+dispatch to become `match`. | Forces rewriting every consumer as a total match over the universal type — a different program, and each arm still faces Ceiling B. |
| **Verifying interpreters / metaprograms** | Mtac, typed Template Haskell, Idris elaborator reflection; separation logic for interpreters (Iris) | Frameworks where metaprograms/interpreters over rich state are first-class verifiable objects. | Again: these are dependently-typed or separation-logic developments, not SMT-backed Hoare logic over Python. |
| **Self-application limits** | Gödel/Löb; reflection caveats in proof assistants | Tells us *why* full metacircular soundness-of-self is unattainable and where the audited-axiom boundary must sit. | It is a *limit*, not a tool: it bounds the ambition rather than enabling the proof. |

**The synthesis to test with an expert:** the body-faithful self-verification of a string-producing, reflection-using, large-state metaprogram by an SMT-backed Hoare verifier is asking one tool to simultaneously occupy the "verified compiler" *and* "string solver" *and* "dynamic-data refinement" *and* "metacircular reflection" corners at once. The state of the art solves each corner with a *dedicated, heavyweight* method (usually inside a proof assistant), which is precisely the architecture PyCSL's self-verification was trying to avoid. The realistic outcomes are therefore (a) **translation validation / proof-producing codegen** (verify outputs or emit certificates, not the generator), or (b) **stratified trust** (audited object-language axioms à la `semantic-ceiling.md` + a `Json` ADT rewrite), not a straight body-faithful sweep.

---

## 8. Precise questions to inquire about

1. Is there any deductive verifier (SMT-backed, contract-style) that has body-faithfully verified a **code generator / interpreter that branches on `Any`-typed reflective data** (JSON-shaped), without first rewriting it as a total match over a universal sum type?
2. What is the largest **string-manipulating program** (with `endswith`/`split`/`replace`-style branching on symbolic strings) discharged *automatically* by Z3/CVC5 string theories, and where does it break down?
3. For **self-verification of a compiler's code generator**, is the consensus that **translation validation** (per-output certificate) or **proof-producing generation** is strictly more practical than verifying the generator body? (i.e., should LINK 2 be promoted from byte-diff to a semantic validator rather than pursuing LINK 3 body-faithfulness?)
4. What is the accepted way to handle the **object-language-semantics-inside-the-logic** requirement (Ceiling B) — axiomatized evaluator with human audit (our `semantic-ceiling.md` plan), shallow embedding, or a separately-verified evaluator — and what are the soundness caveats of each?
5. Does the **typed-IR (`Dict[str,Any]` → universal ADT) rewrite** have precedent that kept the generator *recognizably the same program*, or does it always amount to a full reimplementation?

---

## 9. Reproduce / verify the claims in this document

```bash
cd <repo-root>
# (A) The building blocks now prove body-faithfully (record str field + all-string f-string):
python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0743.py   # dataclass record str-field read → SUCCESS
python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0744.py   # all-string f-string concat   → SUCCESS

# (B) The real emitter is still trusted, not body-faithful (counts behind §3):
F=src/self-annotate/src/module6_whyml/statements.py
grep -c '#@ .trusted' "$F"                       # ≈26 trusted annotations
grep -oE '\.get\(' "$F" | wc -l                  # ≈66 Any-typed dict lookups
grep -oE '\.to_dict\(' "$F" | wc -l              # ≈25 reflective re-dispatch
grep -oE 'self\._[a-z_]+' "$F" | sort -u | wc -l # ≈92 mutable state fields

# (C) The foundational fixes are additive (no corpus regression):
bash bin/byte-diff-sweep.sh /tmp/after && echo "compare /tmp/after against a clean-tree sweep — byte-identical"
```

---

## 10. Bottom line

The `\trusted` stubs on the PyCSL emitter are **not laziness or a missing lemma** — they mark the boundary where a string-producing, reflection-using, large-state metaprogram exceeds what an SMT-backed Hoare verifier can model (Ceiling A) and specify (Ceiling B). We have moved the language so the *idiomatic building blocks* (typed record fields, faithful string concatenation) now verify, which **localizes** the ceiling precisely: it is the combination of `Any`-typed reflective dispatch, content-level string algebra, ~90-field mutable state, and the object-language-semantics-in-the-logic requirement. Every one of those is, in the literature, a *dedicated heavyweight subfield*. The honest question is therefore not "which lemma unblocks the sweep?" but **"which architecture do we adopt — translation validation, proof-producing generation, or a stratified audited-axiom model — given that body-faithful self-verification by the SMT route asks one tool to be a verified compiler, a string solver, a dynamic-data refinement system, and a metacircular reflector at once?"**
