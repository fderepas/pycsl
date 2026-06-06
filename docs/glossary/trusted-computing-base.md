The **trusted computing base (TCB)** is the set of components whose correctness
cannot be verified by PyCSL itself and must therefore be assumed.

If any TCB component is wrong, a verification run can report a proof without the
code actually satisfying its contract. The TCB is not an implementation flaw — it
is an explicit accounting of what the tool is allowed to trust.

---

## Why the TCB matters in PyCSL

PyCSL aims to be a _sound_ verifier: a successful run should guarantee that every
contract really holds for all inputs. Soundness is only as strong as the TCB.

Listing the TCB makes the guarantee precise: the code is correct **given that** the
trusted components behave as documented. Shrinking the TCB makes the guarantee
stronger.

---

## Concrete TCB inventory

PyCSL's TCB has three layers.

### 1. External tool trust

| Axiom | File | What is assumed |
|---|---|---|
| `module6EncodesMlw` | `VcgEmission.lean` (Lean only) | Module6 emits a `.mlw` file whose [verification conditions](verification-condition.md) match the formal specification `vcProp` exactly (emission fidelity), and Why3's provers are sound for those goals. **Eliminated on the Rocq side (2026-05-29)** — `module6_encodes_mlw` is now a PROVED Lemma in `Phase6m_VcgSemBridge.v`. The Lean mirror retains the axiom pending Sub-β port to Lean. |
| `altErgoCorrect` | `Soundness.lean` | Alt-Ergo and Z3 are sound for the non-linear arithmetic goals they discharge |
| `trustedContractsAxiom` | `Soundness.lean` | Functions annotated `\trusted` satisfy their stated contracts |
| `whyCertConstruction` | `Why3Trust.lean` (Lean only) | Whoever constructs a `Why3Certificate` (e.g., Lean's `Why3Trust.check` invoking Why3 externally) has done the work to validate every emitted VC. **Note:** in Rocq this is *not* an axiom — it is structurally enforced by the cert type (`why3_certificate ws Q` directly demands the eval_vc_formula witness for every VC). The trust line is at construction, not projection. |

### 2. Deprecated axiom (scheduled for deletion)

| Axiom | File | Status |
|---|---|---|
| `why3ImplementsWpW` | `SoundnessVerified.lean` | Superseded by `module6EncodesMlw` + `vcgSound`; kept only for backward compatibility until all callers migrate. **Rocq-side:** eliminated 2026-05-29 (now proved). |
| `why3_validates_emitted` | `Phase6m_VcgSemBridge.v` (Rocq, removed) | **Removed 2026-05-29.** Previously was an axiom asserting "Why3 verdicts implies eval_vc_formula"; now proved directly via the cert-as-witness restructure. |
| `enrich_main_cert` | `Phase6m_VcgSemBridge.v` (Rocq, removed) | **Removed 2026-05-29.** Was an intermediate axiom bridging the opaque sealed-unit cert to a witness Record; eliminated by making the cert itself BE the witness. |

### 3. Lean and Rocq kernel trust

The Lean 4 kernel and the Rocq kernel are themselves trusted.  Their correctness is
outside PyCSL's scope and is handled by the respective upstream communities.

---

## How the TCB is being reduced

The history of TCB reduction for the VCG chain illustrates the approach:

**Before Phase 6A:** One broad silent axiom.
```lean
axiom why3ImplementsWpW : Why3Certificate ws Q → wpW ws Q preEs es
-- trusted: Why3's VCG algorithm AND Why3's provers
```

**After Phase 6A (vcgSound):** VCG algorithm correctness is proved as a theorem.
```lean
theorem vcgSound : vcProp ws Q preEs es ↔ wpW ws Q preEs es
-- proved — no domain axioms beyond propext / Classical.choice / Quot.sound
```

**After Phase 6B (vcgBridge):** The sorry is named and documented.
```lean
def vcgBridge ... : vcProp ws Q preEs es := sorry
-- #print axioms vcgBridge → sorryAx  (visible proof obligation)
```

**After Phase 6C (module6EncodesMlw):** The sorry is replaced by a named axiom.
```lean
axiom module6EncodesMlw : Why3Certificate ws Q → vcProp ws Q preEs es
def vcgBridge ... cert := module6EncodesMlw ws Q preEs es cert
-- #print axioms vcgBridge → module6EncodesMlw  (no sorryAx)
```

At each step, the trusted claim becomes narrower and more precisely stated.

The planned next steps (`VcgSemBridge` / Phase 6C-β) will further split
`module6EncodesMlw` into two proved theorems plus one smaller residual axiom about
the Python emitter.

---

## Checking the TCB yourself

In Lean 4, `#print axioms <theorem>` lists every axiom (including `sorryAx`) that
a theorem ultimately depends on.  Running this on the main soundness theorems gives
an exact TCB audit:

```lean
#print axioms pycsl_soundness
-- Expected: [propext, Classical.choice, Quot.sound]
--   (no domain axioms — the WP soundness chain is fully proved)

#print axioms why3ImplementsWpW_derived
-- Expected: [module6EncodesMlw, propext, Classical.choice, Quot.sound]
--   (one named axiom — the sole remaining trust in the VCG path)
```

In Rocq, the equivalent command is `Print Assumptions <lemma>`.

---

## Related terms

- [verification condition](verification-condition.md)
- [trusted stub](trusted-stub.md)
- [theorem prover](theorem-prover.md)
- [proof companion](proof-companion.md)

> **In short:** the TCB is the explicit list of what PyCSL is allowed to assume
> without proof. Shrinking it makes the soundness guarantee stronger.
