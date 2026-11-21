# value-model-wall-stand-alone-fix.md — requested fixes to the value-model-wall plan

*Review of `value-model-wall-stand-alone-plan.md` (2026-07-09). The plan is technically strong and its
Wall-2 insight is build-ready. This document lists the changes it needs before it is executable, ranked
by severity, each as **CHANGE / WHY / HOW**, followed by the doubts I cannot resolve from the plan alone
and that the author must settle. Cross-references are to the plan's section numbers unless noted "statement"
(= `value-model-wall-stand-alone.md`) or "SKILL" (= `config/skills/self-tcb-reduction/SKILL.md`).*

**One-line verdict.** Ship **W2** (after E0) as written — it is correct. **Route R** is the right idea with
the wrong headline benchmark and a sequencing bug. **Route U's byte-diff-0 at scale** is the real open
risk and is the least-specified part of the plan; the thesis "both walls fully break, B0 not warranted"
is over-strong until U is *demonstrated*, not asserted.

---

## Required changes (ranked)

### C1 — Re-scope B1: `_build_soundness_report` is NOT pure route R (BLOCKER)

**CHANGE.** §0, §3.1, §6.1 present B1 (`_build_soundness_report`) as route R with a "near-empty VC
profile, discharge immediate." Re-classify it as an **R + U integration test**, and introduce a *separate,
genuinely pure* route-R benchmark as the R milestone's headline.

**WHY.** The measured body (whole-body proof-probed this session; it fails today) reads generic IR
function-dicts and does map/set work, none of which is a record literal:

```python
trusted_names = {f["name"] for f in funcs if f.get("trusted") or f.get("abstract")}   # U: reads Dict[str,Any] IR nodes
ens  = bool(f.get("contracts", {}).get("ensures"))                                     # U: nested Dict[str,Any] read
counts[bucket] += 1                                                                    # variable-key map update (bucket is a VAR)
deps = sorted((_collect_calls(f.get("body", [])) & trusted_names) - {name})            # set algebra + sibling + sorted
vcs.append({"function": name, "bucket": bucket, "has_contract": ens, ...})             # closed-key element dicts -> list of records/pyval
return {"file": filename, "summary": counts, "vcs": vcs}                               # R: the only record-literal part
```

`funcs` elements are the system's core `Dict[str, Any]` IR nodes — reading them (`f["name"]`,
`f.get("trusted")`, `f.get("contracts",{}).get("ensures")`, `f.get("body")`) is route U, the wall itself.
So B1's failure today is NOT (only) the return type; the "records wearing a dict costume" narrative does
not apply to the parts of B1 that actually block. Claiming B1 discharges under pure R contradicts the
measured evidence and would send the build in circles.

**HOW.** (a) Rename the current B1 to **B1′ (R+U integration)** and move it to *after* route U lands.
(b) Author a new **B1 (pure R)**: a mirror method (or a minimal reference fixture, `test-suite/corpus/
pycsl-reference/08NN.py`) that constructs and returns a record from **already-typed locals** — no generic
IR-dict reads, no map update — e.g. `def f(a: str, n: int) -> Dict[str,Any]: return {"name": a, "arity": n}`
with literal-key readers. That is the honest "closed-row monomorphization" unit test the plan's §3 argues
for. (c) Update the §0 solution map and §6 discharge plan so the R milestone is measured on B1, not B1′.

---

### C2 — Fix the build-order dependency: U is a prerequisite of B1′, not a successor (BLOCKER)

**CHANGE.** §0 build order (`E0 → W2 → R → U`) puts R before U, but the plan's *own* headline R benchmark
(the current B1) depends on U. Reconcile the ordering with the real dependency graph.

**WHY.** Sequencing R before U while B1 needs U is internally inconsistent; a builder following the plan
literally would attempt B1 at the R milestone and fail on the U-shaped reads.

**HOW.** Adopt: `E0 → W2 (banks B3 + string slice) → R-pure (banks new B1, B2) → U (banks B1′ + walker
class)`. State explicitly that **B2 (`_build_method_*_ensures_map`) must be re-checked for the same U
contamination** — several of that family also *read* IR dicts to build their maps; if so, they are R+U too
and belong after U. Do the classification per-method against the live body, not by return type (the same
over-count trap as SKILL §10.1/§10.3).

---

### C3 — Specify Route U's byte-diff-0 discipline; it is the campaign's real risk (BLOCKER)

**CHANGE.** §4 defers U's corpus-safety to "dovetails with the traversal plan." Give U its own explicit
gate, poisoned-control design, and a demonstrated (not asserted) byte-diff-0 story — or scope U down to a
provably-inert subset.

**WHY.** Today `.get`/subscript over `Dict[str, Any]` lowers to **int-hash** operations *pervasively across
the corpus*. Rerouting them to `pyval` defensive projection is a large emission change; the corpus is
pinned byte-for-byte. This is exactly where a build stalls, and it is the least-argued part of the plan.
The landed lowerings that WERE byte-diff-0 (string ops, `str_split_op`) succeeded because they were gated
on shapes **no corpus program hits** (e.g. the string-split comprehension: 0/759 match). U does not obviously
have that property — generic-dict reads are everywhere. "Pattern-gated, fail-closed" is asserted but the
gate that keeps U inert on 759 programs is not exhibited.

**HOW.** Either (a) exhibit the gate: state the precise structural predicate under which U fires, and show
(by the same before/after sweep used for `str_split_op`) that it matches **0** corpus programs while
covering the target mirror methods; or (b) concede that U is *not* byte-diff-0-safe as a blanket rewrite
and restrict the first U increment to the self-annotation mirror only (mirror files are not in the corpus),
making corpus-inertness true by construction — and say so. Do not carry "pattern-gated" as an unbacked
claim.

---

### C4 — Replace asserted VC profiles with a measured per-benchmark gate (SKILL §10.1) (MAJOR)

**CHANGE.** §6 states "B1, B2, B3 all clear" with projected VC profiles ("near-empty," "discharge
immediate"). Make each benchmark's acceptance a `port → whole-body prove → revert` result *after* the
minimal mechanism is built — never an a-priori estimate.

**WHY.** The campaign's most expensive repeated mistake (SKILL §10.1/§10.2) is projecting yield;
`--no-proof`/idiom-in-isolation over-counted 5×. I *measured* B1/B3 failing this session. A plan that
asserts they "clear" re-commits the exact error the SKILL warns against. Type-check-clean ≠ proof-clean;
a projected VC profile is neither.

**HOW.** For each B, add an acceptance line: "cleared ⟺ the verbatim live body, `\trusted` removed,
full-file proves (`python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl`), byte-diff-0, ledger==3."
State the VC-profile paragraphs as *hypotheses to be confirmed by that run*, not conclusions.

---

### C5 — State a yield projection (VALUE-not-count); mark U's payoff as shared, not additive (MAJOR)

**CHANGE.** The plan gives no marker-delta estimate. Add one, and flag that route U's yield is **shared
with the traversal plan, not additive**.

**WHY.** SKILL §10.7 (VALUE-not-count) and §10.2 (measure before build): a multi-mechanism build must be
justified against a real payoff. Without a number, "both walls break" reads as a capability claim with no
cost/benefit. And double-counting U's walker-class yield across this plan and
`ir-traversal-residual-stand-alone-plan.md` would inflate the apparent return.

**HOW.** Add a table: W2 ≈ ≤13 string methods (minus other-blocked, TBD by the E0 re-census); R-pure +
R-family (`_build_method_*_map`) ≈ ~10 *if* they are U-free (per C2); U + traversal dovetail ≈ the walker
class, **counted once across both plans**. Total honest delta, with the shared portion called out.

---

### C6 — Tighten the Route-R certificate claim (MODERATE)

**CHANGE.** §3.3's "one template-level product certificate (schema well-formedness)" is vaguer than the
bar the `pyval`/`sdict` certificates meet. State precisely what it proves and why one template covers every
generated shape.

**WHY.** The coupling rule (SKILL §10.5, statement §1) requires a new value shape to co-land an *axiom-free*
certificate proving the value is *sound*, not merely well-formed. A per-shape WhyML record is a product of
certified component types, but "schema well-formedness" does not obviously state the soundness lemma the
metatheory needs. If the claim is that a product of certified types is certified *by construction* (no new
lemma), say that and cite the compositionality argument; if a lemma is needed, write it.

**HOW.** Either (a) argue that a Why3 record over already-certified field types introduces **no new value
shape** (records are primitive; the fields are certified) ⇒ **no new certificate at all**, ledger trivially
3 — which would *strengthen* the plan; or (b) if a certificate is genuinely needed, state its exact
proposition and its `Print Assumptions`/`#print axioms` obligation, matching the `Phase2c_PyValDict.v`
template.

---

### C7 — `counts[bucket] += 1`: specify the variable-key option-map update (MODERATE)

**CHANGE.** §3 treats the inner homogeneous dict as a solved "faithful `map string int`." Specify the
read-modify-write on a **variable** key over an **option-valued** map.

**WHY.** The existing model is `map string (option int)` (per the nested-list work); `counts[bucket]`
returns `option int`, so `+= 1` must unwrap (`match … with Some v -> v+1 | None -> 1` or a defaulting
read). `bucket` is a variable, not a literal key, so this is not a record-field update. "No interesting
VCs" is not established here.

**HOW.** Add the lowering skeleton for variable-key `m[k] += 1` over `map string (option int)`, and its
acceptance under `--fun` proof. (This may already work via existing dict-augassign machinery — confirm by
measurement, per C4, rather than assuming.)

---

### C8 — Correct the §7 audit note: the string library is on the branch, not `main` (MINOR)

**CHANGE.** §7 states the §2.2 string ops (`str_sub_op`, `str_eq_op`, `str_split_op`, …) "**are** present"
implying on `main`. They are on `ghost-assign-bc6` (`str_split_op` was added this session and pushed to
`origin/ghost-assign-bc6`), **not merged to `main`**.

**WHY.** The audit note's value is telling a reviewer what a fresh clone can reach. Mis-stating the branch
defeats that. `str_split_op`/`uses_str_split_comp` are in commit `7615e287` on the branch only.

**HOW.** Reword to name the branch: "present on `ghost-assign-bc6` (unmerged to `main`)," and fold the
string library into the same "commit the missing artifacts before circulating" instruction as the
certificates/censuses. Re-pin the corpus count (§6.5) in the same pass — name the exact frozen set (the
sweep this session emitted **759**).

---

### C9 — Soften the thesis to match what is demonstrated vs asserted (MODERATE)

**CHANGE.** §0/§8's "Both walls break; no B0 impossibility argument is warranted" is stronger than the
evidence. Restate as: **W2 and closed-key route R break** (demonstrable now); **route U's admissibility at
scale (byte-diff-0 over generic-dict reads) is the open question** — the very question the standalone
*statement* should keep posing to the external reviewer.

**WHY.** Declaring the walls broken before U-at-scale is shown risks the SKILL §12 failure mode in reverse:
closing a research-grade boundary on assertion. The honest position strengthens the deliverable — it banks
the two provable wins and keeps the sharp open question open.

**HOW.** Edit §0 thesis and §8 brief; keep §7's "B0 not warranted for W2/R" but change the U claim to "U's
corpus-scale admissibility is unproven; if it fails to gate inertly, the dynamic-walker residue is the
principled `TRUSTED(essential)` boundary — a partial B0 for exactly that sub-class."

---

## My doubts (things I could not settle from the plan; the author must)

1. **Does route R survive crossing method boundaries?** `_build_soundness_report` builds the record in one
   method; `_print_soundness_report` *reads* it (`report["summary"]`, `report["vcs"]`) in another. For R to
   type-check, the **same generated record type** must be threaded to the reader's parameter. Does the
   emitter infer a consistent record type for a dict that flows across a call boundary, or only within one
   body? If only within a body, R clears B1's *return* but not the *consumer*, and the pair does not
   self-verify together. I don't know the answer; the plan doesn't address it. **This may be the deciding
   feasibility question for R.**

2. **Is U's defensive totalization actually byte-diff-0-gateable at all?** My honest fear (C3): generic-dict
   reads are so pervasive that *any* recognizer broad enough to cover the walker class also fires on corpus
   programs, and *any* recognizer narrow enough to be corpus-inert covers too few mirror methods to matter.
   I cannot rule this out. If it is true, U is not a bounded feature but the research wall itself, and the
   plan's "U dovetails" becomes "U is the open problem."

3. **W2's "no string theory in any VC" — fully robust?** The argument depends on every `str_eq_op` guard
   being an *unconstrained* boolean (mechanism C). But `str_eq_op(str_sub_op s i (i+1), "(")` couples a
   substring term to an equality; if *any* downstream VC (a loop invariant, a later projection) depends on
   which branch fired, the substring/String.length axioms get pulled in and the "arithmetic-only" profile
   breaks. The plan asserts guards never dominate type-safety here; I believe it for `_strip_outer_parens`
   specifically, but not obviously for all 13 string methods. Needs the E0 re-census to confirm per method.

4. **Does `_collect_calls` (used in B1) actually compose cleanly?** It is cited as an already-converted
   sibling (GenericFold A-set → `map string bool`). But B1 does `_collect_calls(...) & trusted_names`
   where `trusted_names` is a set-comprehension result. Set-intersection of two `map string bool` values,
   then `- {name}`, then `sorted(...)` to `array string`: this chain of set→set→array ops over string
   elements is plausible but unproven. It is part of why B1 is not "near-empty."

5. **The R certificate: new value shape or not?** I lean toward "a Why3 record over certified field types
   is no new value shape ⇒ no certificate" (which would *help* the plan — see C6a). But I am not certain the
   metatheory treats a generated record as transparently certified; if the record participates in the
   `pyval` embedding (e.g. `vcs : list pyval` mixing record and union), the boundary may need a lemma. The
   plan should not assume the cheap answer without checking the Rocq/Lean side.

6. **E0's blast radius.** The param-extraction bug (static-method + tuple-unpack-loop) — is it truly inert
   on the corpus, or does it currently *mask* wrong emission that some corpus program relies on? The plan
   says "any diff it produces is a bug it was masking," which is the right stance, but the size of that diff
   is unknown until the sweep runs. If E0 perturbs many corpus files, each perturbation needs adjudication
   before W2 can even be measured.

---

## Summary of the ask

- **C1, C2, C3** are blockers: fix the B1 mis-classification, the R-before-U ordering, and specify U's
  byte-diff-0 gate (or scope U to the mirror). Without these the plan is not executable as written.
- **C4, C5, C9** align the plan with the SKILL's hard-won discipline: measure don't assert, project the
  yield, and don't declare the walls broken before U is shown.
- **C6, C7, C8** are correctness/precision fixes.
- The **doubts** (esp. #1 cross-method record threading and #2 U-gateability) are the two questions whose
  answers determine whether route R and route U are bounded features or the research wall — resolve them by
  a *measured spike* (one pure-R method proved end-to-end incl. its consumer; one U recognizer swept for
  corpus-inertness) **before** committing to the full build.
