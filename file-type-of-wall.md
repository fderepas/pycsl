# The `_field_type_of` wall — a reviewer's map of a representation limit in self-verifying PyCSL

*External-review statement, 2026-07-10. Self-contained: assumes no prior PyCSL knowledge. It reports one
concrete "wall" hit during PyCSL's self-verification TCB-reduction campaign — a method that cannot be
proven — and, more usefully, dissects WHY, distinguishing a genuine impossibility from a representation
choice. The finding is a clean instance of a classic tension in SMT-based deductive verification
(extensional arrays vs. enumerable finite maps), so it is a good lens on the state of the art. Every
claim here is reproducible from the cited evidence.*

---

## 1. The global picture (what PyCSL is, and where this sits)

**PyCSL** is a deductive verifier for a subset of Python: it compiles annotated Python
(`#@ requires/ensures/assigns`, loop invariants) through a 6-module pipeline into **WhyML** (the input
language of the [Why3](http://why3.org) platform), which generates verification conditions discharged by
SMT solvers (Alt-Ergo, Z3) and, when those fail, by the Rocq (Coq) and Lean proof assistants. Soundness
rests on a **fixed 3-axiom ledger** cross-checked in both Rocq and Lean.

PyCSL **verifies a mirror of its own emitter** — the WhyML-generation code is itself annotated Python that
PyCSL proves type-safe, frame-correct, and terminating. This is the self-verification / TCB-reduction
campaign: a self-annotation "mirror" of the compiler carries ~1226 `\trusted` stubs (methods whose
contracts are *assumed*, not proven), and the campaign converts them, one at a time, into verified bodies —
each conversion held to three disjoint oracles (the mirror body is textually faithful to the live emitter;
its VC discharges under Why3; and it perturbs no reference-program output). The metric is the shrinking
`\trusted` count.

Most conversions are routine transcription. A minority hit **walls** — methods whose real body cannot be
expressed as a discharging VC. Characterizing those walls precisely is the scientifically interesting part:
each is either a genuine limit of the approach or a lifted-able consequence of a modeling choice, and
telling the two apart is exactly what a reviewer can help sharpen. `_field_type_of` is one such wall, and a
representative one.

---

## 2. The method

`_field_type_of` resolves a record-field access (`self.<field>` / `global.<field>`) to the field's declared
type tag. Stripped to its essential shape, over the emitter's `self._record_types` — a dictionary mapping a
class-name key to a small info-record (`{whyml_name: str, field_types: {str: str}, …}`):

```python
def _field_type_of(self, attr_ir) -> Optional[str]:
    ...
    gcls_info = self._record_types[gcls]          # (a) KEYED lookup by class-name
    cls = gcls_info["whyml_name"]
    for info in self._record_types.values():      # (b) ITERATE all values
        if info["whyml_name"] == cls:             #     linear search by a different field
            return info["field_types"].get(field) #     nested read -> Optional[str]
    return None
```

The two operations on the **same** object `self._record_types` are the crux:
- **(a)** a **keyed subscript** `d[k]` — "give me the value at key k";
- **(b)** a **values-enumeration** `for v in d.values()` — "walk every value."

A twin method, `_field_type_for`, has the identical `for info in self._record_types.values()` search (two
call sites). Both are `\trusted`.

---

## 3. The wall as first encountered: a Why3 `map` cannot be iterated

PyCSL models a `Dict[str, V]` as a WhyML `map string (option V)`. In Why3, **`map α β` is literally the
function type `α → β`** — a total, extensional McCarthy array. It supports keyed read (`Map.get d k`, O(1),
total) but has **no reified domain, no cardinality, no enumeration**. Consequently operation (b) has no
executable model. This is not a soft limit; it is a syntax-level one. The minimal witness
(`getting-better/composition-wall/sr2-values-spike.mlw`, independently re-proven, 4/4 goals Valid):

```
  (* part (a) — keyed lookup over `map string (option recordinfoview)` — proves trivially. *)
  (* part (b) — attempt to iterate the map's values: *)
  for v in m.values() do ... done
  --> File ".../for_map_test.mlw", line 6: syntax error
```

WhyML's `for` is **int-range only** (`for i = lo to hi do … done`); there is no `for x in <expr>` form in
the target language at all — that sugar exists only in the *source* languages Why3 front-ends translate
*from*. And the `map` theory (`why3/stdlib/map.mlw`, verified by inspection) exposes zero
domain/cardinality/fold operations. So `for info in self._record_types.values()` is inexpressible.

This is corroborated three independent ways inside PyCSL: (i) the emitter's own `auto_trust.py` (a safety
valve that *deliberately leaves methods trusted* when they cannot be soundly lowered) special-cases exactly
"a `for` loop whose iterable yields a map," with the comment *"WhyML maps don't have a natural iteration
model (they're functions, not collections)… the only sound option is to auto-trust the enclosing
function"*; (ii) two prior hand-spikes (`fb1_fmap_spike.mlw`, `v2_setfold_spike.mlw`) recorded the same
wall for the richer `fmap.Fmap` theory and worked around it with a bespoke inductive type; (iii) a grep of
all 217 `.mlw` files in the repository finds **zero** that iterate a `map.Map`.

**First-order verdict:** `_field_type_of` is not provable — leave-trusted.

---

## 4. The deeper truth: this is a REPRESENTATION CHOICE, not an impossibility

The interesting part for a reviewer is that PyCSL **already has** a data type that supports *both*
operations — it just is not the one `_record_types` uses. For generic reflection, PyCSL models dictionaries
as an **inductive association list** `pydict` (`preamble.py`):

```
  type pydict = DNil | DCons irkey pyval pydict
  function get    (d: pydict) (k: irkey) : option pyval   (* keyed lookup, O(n) structural *)
  function values (d: pydict) : list pyval                (* ENUMERATION, structural fold *)
  predicate mem_key (d: pydict) (k: irkey)                (* membership *)
```

`pydict` supports keyed `get`, `mem_key`, **and `values`** — the very enumeration a `map` cannot express —
because it is a finite, inductively-defined structure with a `size` measure that discharges termination.
An executable (program-level) fold over a `pydict` **is** writable and provable. So `_field_type_of`'s
operation (b) is *not* fundamentally unverifiable: it is unverifiable **only because `_record_types` is
modeled as a Why3 `map` rather than as a `pydict`-style inductive assoc-list.**

Why the `map`, then? Because operation (a) — keyed lookup — is the *common* case: `_record_types` is read
by keyed subscript in **21 sites across 7 emitter methods**, almost all of which want the O(1), total
`Map.get`, never iteration. The `map` model is the right global choice for those; it is `_field_type_of`
and `_field_type_for` (the only two that *also* iterate) that fall outside it.

So the wall is a **keyed-vs-enumerable representation tension on a single object**:

| Model | keyed `d[k]` | `for v in d.values()` | cost |
|---|---|---|---|
| Why3 `map α β = α→β` (extensional array) | **O(1), total** | **impossible** (no domain) | PyCSL's current choice for `_record_types` |
| inductive assoc-list (`pydict`) | O(n) structural | **native** (structural fold) | enumerable, but keyed read is O(n) |
| dual view (map + explicit key-list/set) | O(1) | via the key-list | two structures kept in sync (an invariant to prove) |

`_field_type_of` is the one method that needs *both columns* on *one* object, so no single row satisfies it.

---

## 5. State of the art — why this is a fair lens

The `map`-vs-finite-collection split is not a PyCSL quirk; it is a fault line across SMT-based verifiers:

- **Why3 / SMT arrays.** The SMT-LIB `Array` theory (and Why3's `map`) is *extensional*: an array is a
  total function with McCarthy `select`/`store`. It is deliberately domainless — there is no `keys`, no
  `size`, no iteration — because that is what makes the array decision procedure efficient and complete.
  Iteration/folding over such a structure is simply outside the theory.
- **Dafny / Viper.** By contrast, Dafny's `map<K,V>` and Viper carry a **finite domain** (`m.Keys`,
  `|m|`), so one *can* quantify/iterate over the keys — at the price of a heavier model (domain sets,
  finiteness side-conditions, well-formedness) and correspondingly harder proof obligations. This is the
  same trade the table above shows, made once at the language level.
- **Inductive / functional encodings.** Verifiers built on proof assistants (or that drop to them) model a
  finite map as an inductive assoc-list or a balanced tree with a fold/eliminator — enumerable and
  induction-friendly, but with O(n) lookup and structural-recursion obligations. This is exactly PyCSL's
  `pydict`.

PyCSL sits at the Why3 end (extensional `map`) for the bulk of its dictionaries because keyed read
dominates, and it keeps an inductive `pydict` in reserve for the reflective code that must fold. The
`_field_type_of` wall is therefore a crisp, minimal instance of a **known, principled** limitation:
*a structure optimized for keyed read cannot also be enumerated without either changing its representation
or maintaining a second, synchronized one.* It is not evidence of a soundness gap or a tooling defect; it
is the representation trade-off surfacing on a single method that happens to want both sides of it.

---

## 6. The open question for the reviewer (the design decision)

Given the above, `_field_type_of`/`_field_type_for` staying `\trusted` is a **defensible local optimum**,
not a defect. But the reviewer's judgment is wanted on whether lifting it is worth the cost. The three
routes, honestly costed:

1. **Re-represent `_record_types` as an inductive assoc-list** (`pydict`-style, with executable `get`/
   `values`/`mem_key` carrying a `size` variant). Lifts both methods. **Cost:** ripples across the 21
   keyed-read sites / 7 methods (each O(1) `Map.get` becomes an O(n) structural search — a real *runtime*
   cost in the emitter, not just proof cost), and requires promoting `pydict`'s currently-*logic* `get`/
   `values` to *program* functions with termination proofs. High blast radius for two leaves.
2. **Dual view** — keep the `map` for keyed reads, carry an explicit `key list` alongside for the two
   iterators, and prove the sync invariant (`k ∈ keylist ↔ Map.get m k ≠ None`). Lifts both methods with
   O(1) keyed reads preserved, at the cost of a maintained invariant and the emitter constructing/threading
   the key-list. Medium blast radius; a real invariant-engineering task.
3. **Accept the wall** — leave both trusted, documented as the map-enumeration class. Zero cost; the
   `\trusted` count keeps two irreducible-by-choice entries. The int-hash faithfulness residual that these
   trusted leaves induce in two *already-converted* callers (`_rhs_yields_array`/`_rhs_yields_map`, which
   compare `_field_type_of`'s result by an opaque integer hash rather than by string) then becomes
   **permanent**, bounded by the trusted leaf.

**The question:** is the cross-emitter re-representation (route 1) or the dual-view invariant (route 2)
justified to remove two `\trusted` leaves and their downstream faithfulness residual — or is route 3
(accept a principled representation limit) the honest terminus? Our current position is route 3, but the
trade is a design call where an outside perspective on the state of the art is exactly what helps.

---

## 7. Honest limits of this report

- The claim "impossible in Why3" is scoped to Why3's `map`/SMT-`Array` model and to *executable* iteration;
  it is **not** a claim that the method is unverifiable in principle (§4 shows the opposite). Any framing of
  this as a fundamental limit of deductive verification would be overclaiming.
- The costs in §6 are estimated from static call-site counts (21 sites / 7 methods) and the known `pydict`
  logic-vs-program gap; they are not a measured migration.
- The finding does not touch soundness: the 3-axiom ledger is unchanged, and a `\trusted` leaf is an
  *assumption made explicit*, not a hidden gap. Converting it would shrink what is assumed; leaving it does
  not enlarge it.
- Evidence to reproduce: `getting-better/composition-wall/sr2-values-spike.mlw` (the map-vs-array spike,
  `why3 prove -P alt-ergo` → 4/4 Valid); `for v in m.values()` → parser syntax error; `preamble.py` `pydict`
  theory (`get`/`values`/`mem_key`/`size_dict`); `auto_trust.py` map-iteration auto-trust rule;
  `gap-c-or-par.md` (the refuted build plan and its S-R2 make-or-break record).
