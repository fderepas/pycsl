# value-model-wall-stand-alone-plan-2.md — Breaking the two value-model walls: revised plan

*Revision 2, 2026-07-09. Supersedes `value-model-wall-stand-alone-plan.md` (rev 1), incorporating every
required change in `value-model-wall-stand-alone-fix.md` (C1–C9) and turning its six doubts into owned
spikes/decisions. Companion to the problem statement `value-model-wall-stand-alone.md`; sibling of
`ir-traversal-residual-stand-alone-plan.md`. Discipline references: `config/skills/self-tcb-reduction/
SKILL.md` (§10.1 measure-don't-assert, §10.2 measure-before-build, §10.5 coupling, §10.7 VALUE-not-count).*

**Revised thesis (C9).** Two wins are demonstrable now and should be banked: **W2** (string-as-character-
sequence dissolves into shipped machinery — correct as written in rev 1, per review verdict) and
**route R on genuinely closed-key shapes** (record monomorphization — right idea, but rev 1 attached it to
the wrong headline benchmark). **Route U's admissibility at corpus scale is the open question of the
campaign**, not a settled step: generic-dict reads are pervasive, and no gate has yet been exhibited that
is simultaneously corpus-inert and mirror-covering. Rev 2 therefore (i) re-scopes the benchmarks (C1),
(ii) re-orders the build around the real dependency graph (C2), (iii) scopes U's first increment to the
self-annotation mirror, where corpus-inertness holds **by construction** (C3b), and (iv) gates the R and U
commitments on two measured spikes (S1, S2) before any full build. If S2 fails both ways — no recognizer
is both inert and covering — the dynamic-walker residue closes as a **partial B0**: a principled
`TRUSTED(essential)` boundary for exactly that sub-class.

---

## 0. Change log against rev 1

| Fix | Disposition in rev 2 |
|---|---|
| C1 (B1 mis-classified) | §2: B1 re-authored as a *pure-R* fixture; old B1 renamed **B1′ (R+U integration)**, moved after U. |
| C2 (order bug) | §1: build order `E0 → W2 → S1 → R-pure → S2 → U0(mirror) → B1′`; B2 family re-classified per live body. |
| C3 (U gate unspecified) | §5: U0 scoped to mirror (inert by construction); corpus-facing U gated on the S2 sweep; poisoned controls specified. |
| C4 (asserted VC profiles) | §7: uniform measured acceptance gate; all VC-profile language demoted to *hypotheses*. |
| C5 (no yield projection) | §8: VALUE-not-count table; U/traversal yield counted **once**. |
| C6 (vague certificate) | §4: two-branch resolution with the Rocq/Lean check as part of S1; mixing boundary named. |
| C7 (`counts[bucket] += 1`) | §6: variable-key option-map update skeleton; acceptance by measurement. |
| C8 (audit note wrong) | §9: branch-accurate note (`ghost-assign-bc6`, commit `7615e287`); corpus pinned at **759**. |
| C9 (over-strong thesis) | Header + §10: thesis softened; partial-B0 path defined for the U sub-class. |
| Doubts 1–6 | §3 (S1), §5 (S2), §2.2/W2 caveat, §2.3 (B1′ chain), §4 (certificate check), §1/E0 (blast radius) — each owned. |

---

## 1. Build order and the two decision spikes (C2; doubts 1, 2, 6)

```
E0   param-extraction fix + corpus sweep + Wall-2 re-census        (blast radius measured, not assumed)
W2   char/enumerate lowering  → banks B3 (+ string-slice methods surviving re-census)
S1   SPIKE: pure-R producer+consumer pair proved end-to-end        (decides R's feasibility — doubt 1)
R    record route on closed-key, U-free shapes → banks B1 (new), B2-subset (re-classified)
S2   SPIKE: candidate U recognizer swept for corpus-inertness      (decides U's shape — doubt 2)
U0   U scoped to the self-annotation mirror (corpus-inert by construction)
B1′  R+U integration: _build_soundness_report whole-body           (the old "B1", now last)
```

- **E0 blast radius (doubt 6).** Rev 1's stance stands — any corpus diff E0 produces is a bug it was
  masking — but rev 2 adds the reviewer's point: the *size* of that diff is unknown until the sweep runs.
  E0's deliverable is therefore fix **+ sweep + adjudication log**; if many files perturb, adjudication is
  scheduled work, and W2 measurement waits for it.
- **Nothing downstream of a spike is committed before the spike reports.** S1 and S2 are days each; they
  are the cheap instruments that decide whether R and U are bounded features or the wall itself.

---

## 2. Benchmarks, re-scoped (C1)

### 2.1 B1 (new) — pure route R

A minimal producer/consumer pair with **no generic IR-dict reads and no variable-key map updates**, e.g. a
reference fixture `test-suite/corpus/pycsl-reference/08NN.py` (number per current corpus tail) or a mirror
method of the shape:

```python
def _mk_entry(name: str, arity: int) -> Dict[str, Any]:
    return {"name": name, "arity": arity}          # closed keys, already-typed locals

def _entry_arity(e: Dict[str, Any]) -> int:
    return e["arity"]                              # literal-key reader, other method
```

This is the honest closed-row-monomorphization unit: build from typed locals, read by literal key,
**across a call boundary** (which makes it double as S1's artifact, §3). Acceptance per §7.

### 2.2 B3 — unchanged (W2), one caveat carried (doubt 3)

`_strip_outer_parens` per rev 1 (E0 + chars-as-`str_sub_op` + indexed `while`). Caveat now explicit: the
"no string theory in any VC" profile holds only while every `str_eq_op` guard is an **unconstrained**
boolean. `str_eq_op (str_sub_op s i (i+1)) "("` couples a substring term to an equality; if any downstream
VC (loop invariant, later projection) depends on which branch fired, the substring/length axioms are
pulled in and the arithmetic-only profile breaks. Believed for `_strip_outer_parens`; **not assumed** for
the other string methods — the E0 re-census classifies each of the ≤13 per method (guard-dominance check,
shared with the traversal plan's mechanism C) before any is claimed for W2.

### 2.3 B1′ — `_build_soundness_report`, an R+U *integration* benchmark (last)

The measured live body is dominated by route-U work, not the record return:

- `f["name"]`, `f.get("trusted")`, `f.get("contracts", {}).get("ensures")`, `f.get("body", [])` — generic
  IR-node reads (**U**), including a nested `.get` chain;
- `counts[bucket] += 1` — **variable-key** option-map update (§6, C7);
- `_collect_calls(...) & trusted_names - {name}` then `sorted(...)` — a set-algebra chain over
  `map string bool` into `array string` (**doubt 4**: plausible, unproven; part of why B1′ is not
  "near-empty" — it is decomposed and measured piecewise in U0, never assumed);
- the element dicts `{"function": name, "bucket": bucket, ...}` are themselves **closed-key** — a candidate
  for R applied to the *element* type (`vc_entry` record, giving `sr_vcs : list vc_entry`), which would
  remove `pyval` from B1′'s return entirely. Whether the element route survives the S1 threading question
  is decided by measurement, not by this document.

B1′ clears only when the whole verbatim body proves after **both** R and U0 land. It is the integration
test of the campaign, not a milestone of either route.

### 2.4 B2 family — re-classified per live body, not by return type (C2)

Several `_build_method_*_ensures_map` methods also *read* IR dicts to build their maps; those are R+U and
move after U0. The classification is per-method against the live body (the SKILL §10.1/§10.3 over-count
trap is exactly classifying by signature). The R milestone banks only the **U-free subset**; the census
that determines that subset is part of the R milestone's definition of done.

---

## 3. S1 — the record-threading spike (doubt 1: R's deciding feasibility question)

**Question.** Does a generated record type survive a call boundary? `_mk_entry` builds the record;
`_entry_arity` reads it as a parameter. For R to work beyond single bodies, the emitter must assign the
**same generated record type** to the dict at the producer's return and the consumer's parameter —
type identity across methods, not per-body inference.

**Spike.** Implement the minimal threading (a per-key-set type table keyed by the sorted literal key-set +
field types; both sites look up the same entry), emit §2.1's pair, whole-file prove. **Outcomes:**
- *Pass* → R proceeds; the type-table becomes R's specification.
- *Pass-within-body only* → R is re-scoped to single-body returns (clears nothing that has a consumer in
  the mirror); its yield line in §8 drops accordingly, and the honest write-up says so.
- *Fail* → R is not a bounded feature; closed-key shapes stay `\trusted` and the record insight is filed
  as future work. (No sunk full build — that is what the spike is for.)

S1 also carries the certificate check of §4 (doubt 5), since the Rocq/Lean question is answered by the
same minimal artifact.

---

## 4. Route-R certificate, tightened (C6; doubt 5)

Rev 1's "template-level product certificate (schema well-formedness)" was under-specified against the
coupling rule (statement §1; SKILL §10.5). Rev 2 resolves it as a two-branch decision **inside S1**:

- **Branch (a) — preferred, to be verified on the Rocq/Lean side, not assumed:** a WhyML record whose
  fields are already-certified types introduces **no new value shape** — records are primitive products;
  the metatheory's value universe is compositional over them — hence **no new certificate**, ledger
  trivially 3. If the Rocq/Lean check confirms this, the plan *strengthens* (one less obligation).
- **Branch (b) — if (a) fails:** the certificate's exact proposition is stated and proved:
  *for each generated record shape `T = {f₁:τ₁; …; fₙ:τₙ}` with each `τᵢ` certified, `T`'s values are
  sound (well-formed, sized if recursive) and projections `fᵢ` are total at `τᵢ`* — one schematic
  Rocq 8.20 + Lean 4.29 development in the `Phase2c_PyValDict.v` style, `Print Assumptions` /
  `#print axioms` closed.
- **The mixing boundary (doubt 5's sting):** if a record participates in the `pyval` embedding (e.g. a
  `vc_entry` record inside `list pyval`, or a `pyval` field inside a record as in `sr_vcs : list pyval`),
  the embedding direction needs a stated lemma or an explicit injection constructor — this is checked in
  S1 with a two-field record containing one `pyval` field, the worst small case.

---

## 5. Route U, re-scoped: mirror-first, corpus-facing only behind a measured gate (C3; doubt 2)

**The honest risk, adopted from the review:** generic-dict reads are pervasive in the corpus; the landed
byte-diff-0 lowerings succeeded because their gates matched **0/759** corpus programs, and U has no
exhibited gate with that property. Any recognizer broad enough to cover the walker class may fire on
corpus programs; any recognizer narrow enough to be inert may cover too little to matter. Rev 2 therefore
splits U:

- **U0 — mirror-only (first increment, corpus-inert *by construction*).** The defensive tag-checked
  projection emission (total `match slookup k d with Some (PInt i) -> i | _ -> …`) is enabled **only for
  self-annotation mirror files**, which are not members of the 759-program reference corpus. Byte-diff-0
  is then a tautology, not a claim; the poisoned control inverts: a corpus program deliberately compiled
  with the mirror flag must show the gate *would* fire (proving the gate is live), while the normal sweep
  shows 759/759 byte-identical (proving it is scoped).
- **S2 — the corpus-inertness sweep (before any corpus-facing U).** Write the candidate structural
  predicate for corpus-facing U (e.g. "subscript/`.get` on a value whose declared or inferred type is
  `Dict[str, Any]` *and* whose result flows into a typed context"), run the `str_split_op`-style
  before/after sweep, and report the match count. **Outcomes:** 0 matches → corpus-facing U is admissible
  as gated; >0 matches → corpus-facing U is *not* byte-diff-0-safe as a rewrite, U stays mirror-only, and
  the walker sub-class outside the mirror closes as the **partial B0** of §10.
- **Yield honesty (C5):** U0's payoff is the walker class *shared with the traversal plan* — T1–T3 give
  those methods recursion shapes, U0 gives their reads a value model; the class is **counted once**
  across the two plans (§8).

---

## 6. The variable-key option-map update (C7)

`counts[bucket] += 1` with `bucket` a variable over `counts : map string (option int)` is not a record
update and was unspecified in rev 1. Lowering skeleton:

```whyml
(* counts[bucket] += 1  over  map string (option int) *)
counts := Map.set !counts bucket
            (Some (match Map.get !counts bucket with
                   | Some v -> v + 1
                   | None   -> 1        (* Python KeyError-free counter idiom: default 0 + 1 *)
                   end))
```

Total (defensive default), no laws needed under the contract, frame = `counts` only. **Acceptance by
measurement (C4):** this may already fall out of existing dict-augassign machinery — confirmed or refuted
by the U0 milestone's whole-body runs, never assumed. If the Python idiom in the live body is instead
guarded (`if bucket not in counts: …`), the recognizer maps the guarded form to the same total update.

---

## 7. Uniform measured acceptance gate (C4)

Every benchmark and every mechanism milestone uses one acceptance sentence, replacing all projected VC
profiles (which rev 2 demotes to *hypotheses to be confirmed by the run*):

> **Cleared ⟺** the verbatim live body, `\trusted` marker removed, whole-file proves via
> `python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl`; **and** the frozen 759-program
> corpus is byte-identical (with each mechanism's poisoned control flipping red exactly once); **and**
> the ledger reads exactly 3 (`Print Assumptions` / `#print axioms` in CI).

Port → prove → classify → revert remains the loop; type-check-clean is never reported as proof-clean
(SKILL §10.1/§10.2 — the 5× over-count is the campaign's most expensive repeated mistake, and rev 1's
"discharge immediate" language re-committed it on paper).

---

## 8. Yield projection — VALUE, not count (C5)

| Mechanism | Population | Honest expected delta | Shared? |
|---|---|---|---|
| W2 (after E0 re-census) | ≤13 string/pretty-printer methods | TBD by re-census: 13 minus other-blocked minus guard-dominated (doubt 3) | no |
| R-pure (after S1 + C2 re-classification) | new B1 fixture + U-free subset of the ~10 `_build_*_map` family | small; possibly ~half the family if U-free; **drops to ≈0 beyond single bodies if S1 pass-within-body only** | no |
| U0 (mirror-only) + traversal T1–T3 | the Any-tree walker class + B1′ + R+U members of the B2 family | the campaign's main mass — **counted once across both plans** | **yes** (with `ir-traversal-residual-stand-alone-plan.md`) |

No mechanism is built before its population is measured (SKILL §10.2); the table is updated after E0's
re-census, S1, and S2, and the totals quoted anywhere else must cite this table to avoid double-counting.

---

## 9. Audit note, corrected (C8)

For an external reviewer cloning the repository as of 2026-07-09:
- The §2.2 string value ops (`str_sub_op`, `str_eq_op`, `str_strip_op`, `str_startswith_op`;
  `str_split_op` + the `uses_str_split_comp` trigger added this session in commit `7615e287`) are on
  branch **`ghost-assign-bc6`**, pushed to `origin/ghost-assign-bc6`, **not merged to `main`**.
- Not reachable on `main`: `src/formal-semantics/rocq/Phase2c_PyValDict.v` (+ Lean mirror),
  `getting-better/tier3/tier5-value-model-census.md`, `emission-defect-spike-findings.md`,
  `generic_fold.py`. Present on `main`: `self-tcb-reduction.md`.
- **Action before circulating the problem statement:** merge or commit the above, and pin the corpus by
  naming the exact frozen set — **759** reference programs per this session's sweep (earlier documents
  froze 756; a stale clone of `main` shows 781 under a different tree state; the number quoted must be
  the one the byte-diff gate actually runs against).

---

## 10. Honest close-out positions (C9)

- **W2:** breaks, demonstrably, pending only per-method guard confirmation from the E0 re-census.
  B0 not warranted.
- **R:** breaks for genuinely closed-key, U-free shapes **if S1 passes across call boundaries**; degrades
  gracefully (single-body returns) or closes as future work otherwise. B0 not warranted either way — the
  question is yield, not possibility.
- **U:** **the open question, kept open.** U0 (mirror-only) is admissible by construction and banks the
  self-verification value. Corpus-facing U is admissible only if S2 exhibits an inert-and-covering gate;
  if no such gate exists, the dynamic-walker residue outside the mirror is a **partial B0** — a
  principled, documented `TRUSTED(essential)` boundary for exactly that sub-class, which is the
  statement's own "equally valuable closure" and should be posed to the external reviewer in precisely
  that form.
- **The recurring brick** (type-safety dominated by a semantic guard) stands as in rev 1: mechanically
  detectable by guard-dominance; per-method close-out by source normalization, defensive shape change, or
  documented `TRUSTED(essential)`.

---

## 11. One-paragraph brief (rev 2)

*Two of the walls' faces break now and are banked: character-level strings dissolve into shipped
machinery (a char is a 1-char `str_sub_op` string; `enumerate` is an indexed `while` with an arithmetic
variant; no new shapes, no certificates), and statically-closed, literal-keyed dict shapes monomorphize
to generated records with faithful field types — pending one measured spike on whether record types
thread across call boundaries, which also settles whether records need any certificate at all. The
genuinely dynamic residue — generic `Dict[str, Any]` reads — is re-scoped honestly: defensive tag-checked
projection lands first for the self-annotation mirror only, where byte-diff-0 holds by construction; its
extension to corpus programs is gated on a measured sweep showing an inert-and-covering recognizer
exists. If none does, that sub-class closes as a partial impossibility under the byte-identity
constraint — a principled trusted boundary, stated as such. Every benchmark is accepted only by the
whole-body port→prove→revert gate; no VC profile is asserted ahead of its run; yields are projected
value-first and the walker class is counted once across this plan and its traversal sibling.*
