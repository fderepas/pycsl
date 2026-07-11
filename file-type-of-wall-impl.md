# file-type-of-wall-impl.md — implementation plan to break the `_field_type_of` wall

*Implementation plan, 2026-07-10. Derived from `file-type-of-wall.md` (the wall report) and
`file-type-of-wall-response.md` (the reviewer's counter, which supersedes the report's §6 routes for THIS
method pair). The reviewer is right and the report over-scoped: `_field_type_of`/`_field_type_for` do NOT
need enumeration — they need a **reverse index** (a second keyed `map`, indexed by the value-field they
search on), because `_record_types` is **write-once** and the search key (`whyml_name`) is computed at the
single population site. This plan implements the reverse-index fix, spike-gated, to lift both `\trusted`
leaves. Discipline as elsewhere: measure before claiming "cleared"; byte-diff-0; ledger stays 3.*

---

## 0. The reframe (why this is not the map-enumeration wall)

`file-type-of-wall.md` correctly showed a Why3 `map` cannot be *enumerated* (`for v in d.values()` is
inexpressible; §3–§5 of the report stand). But `_field_type_of`/`_field_type_for` do not actually need
enumeration — their `for info in self._record_types.values(): if info["whyml_name"] == cls: …` is a
**search for the entry whose `whyml_name` == cls**, i.e. a keyed lookup on a *different* key than the dict's
own. The fix is a **second keyed map** `_record_types_by_whyml_name : Dict[str, <record-info>]`, populated at
the same single write site, read with a plain `.get(cls)`. No enumeration, no re-representation, no `pydict`,
no new theory. **Campaign lesson to carry forward:** a `for x in d.values(): if x.<field>==k` shape is
"missing an index on `<field>`", NOT the map-vs-array wall — check for the index before reaching for `pydict`.

## 1. Preconditions (measured, this plan's grounding)

- `_record_types` is **write-once**: the ONLY mutation is `preamble.py:3586`
  `self._record_types[td["name"]] = {…}`, inside the single-pass record-decl scan; the search key
  `type_name = whyml_ident(td["name"].lower())` is computed at `preamble.py:3584`, immediately before, and
  is stored as the value's `"whyml_name"`. All 21 keyed reads + both `.values()` searches run after the
  scan. (Confirms reviewer Fact A/B against current line numbers; the reviewer cited 3160, the tree is at
  3586 — same site, code shifted.)
- Init site: `Module6_WhyMLTranspiler.py:65` `self._record_types: Dict[str, Any] = {}`.
- Both walled methods live in `TypeInferenceMixin` (mirror `src/self-annotate/src/module6_whyml/types.py`,
  already `@mutable_state @dataclass` with the M2 scaffold); `_field_type_of` is the leaf that
  `_rhs_yields_array`/`_rhs_yields_map` call (the int-hash residual source, §6).

## 2. The change (LIVE emitter + MIRROR, kept fidelity-identical)

This touches the live emitter behavior (the internal lookup path), so it is a feature-class change gated by
corpus byte-diff-0, and the mirror body must equal the live body verbatim.

### 2.1 Init the reverse index (`Module6_WhyMLTranspiler.py:65`, alongside `_record_types`)
```python
self._record_types: Dict[str, Any] = {}
self._record_types_by_whyml_name: Dict[str, Any] = {}   # reverse index: whyml_name -> same record_info
```

### 2.2 One extra insert at the population site (`preamble.py`, after line 3586's assignment)
```python
type_name = whyml_ident(td["name"].lower())
record_info = { "whyml_name": type_name, "fields": …, "field_types": …, … }   # unchanged dict
self._record_types[td["name"]] = record_info
self._record_types_by_whyml_name[type_name] = record_info   # NEW — same object, not a copy
```
(Refactor the inline `{...}` into a named `record_info` local so both inserts share ONE object — nothing to
keep in sync beyond the two adjacent inserts.)

### 2.3 Rewrite the two method bodies (live AND mirror, identical)
```python
def _field_type_for(self, obj: str, field: str) -> Optional[str]:
    if obj != "self":
        return None
    cls = self._current_self_type
    if not cls:
        return None
    info = self._record_types_by_whyml_name.get(cls)
    return info.get("field_types", {}).get(field) if info else None

def _field_type_of(self, attr_ir: "ExprIR") -> Optional[str]:
    ...                       # cls resolution UNCHANGED (Attribute/FieldGet + getattr chains as today)
    if not cls:
        return None
    info = self._record_types_by_whyml_name.get(cls)
    return info.get("field_types", {}).get(field_name) if info else None
```
Remove both `\trusted` markers; add the fixed contract (`#@ requires True / ensures True / assigns \nothing`).

## 3. What the mirror must model (the spike's KEY measurement — do NOT assume)

The reviewer states the reverse index is "the same `map string (option recordinfoview)` model already
certified and used for `_record_types`, so no new theory/cert." **VERIFY this — it is the load-bearing
assumption.** Two sub-questions the spike answers:

- **Q1 — is `_record_types`'s VALUE already modeled as a typed record?** This session's earlier census
  found `_record_types` reads collapse (the value was opaque). If the value type `recordinfoview`
  (`{ whyml_name: string; field_types: map string (option string) }`) is NOT already declared, then the
  reverse-index read `info.get("field_types",{}).get(field)` needs a **closed-key TypedDict view**
  (`RecordInfoView` with `whyml_name`, `field_types`) so the mirror types
  `_record_types_by_whyml_name : map string (option recordinfoview)` and lowers `.get("field_types").get(f)`
  to a nested keyed `Map.get` (→ `option string`). This is bounded (keyed reads only, NO enumeration) but
  is MORE than the reviewer's "2 lines" if the view doesn't exist yet. **Measure it; do not assume it away.**
- **Q2 — is a `map string (option recordinfoview)` a NEW WhyML value shape needing a certificate?** A record
  over already-certified fields (string / `map string (option string)`) is covered by the existing
  record-value certificate (`Phase2b_RecordVal`) by construction — but CONFIRM via the ledger audit
  (`Print Assumptions` / `#print axioms` == 3). If the RecordInfoView introduces a `pyval → record`
  eliminator the meta-theory doesn't cover, that is a coupling-rule obligation — flag it, do not smuggle.

Both `.get` operations in the rewritten bodies are **keyed** (`Map.get`); there is NO fold, NO variant, NO
enumeration. So the proof is the same class already proven for the 21 existing keyed `_record_types` reads —
IF the value view exists. The spike's job is to confirm exactly which of {reverse-index-only,
reverse-index + RecordInfoView-view} is the real scope.

## 4. Behavior preservation & byte-diff-0 (the correctness argument, to be RUN not asserted)

The rewrite is behavior-preserving IFF `whyml_name` is **unique** across records (then reverse-index
`.get(cls)` returns the same `record_info` the `.values()` first-match search returned). `whyml_name =
whyml_ident(td["name"].lower())` — a collision needs two record names that lowercase-and-mangle equal (e.g.
`Foo` vs `FOO`). **The corpus byte-diff-0 gate is the oracle:** if any reference program's emission changes,
`whyml_name` was non-unique for it (or another assumption broke) → the reverse index must become a multimap
(keep first-inserted) or the method reverts. Expected byte-diff-0 (the emitter's *output* for user programs
is unchanged — only its internal lookup path changed), but **run it, do not assume it** (this session's
history has multiple "expected inert" changes that perturbed the corpus).

## 5. Gates (at the single conversion commit)

- **fidelity** — `self-annotate-mirror-check.sh` 52/52; the rewritten live and mirror bodies are verbatim-equal.
- **type-safety** — `--fun` for each of `_field_type_of`, `_field_type_for` SUCCESS, THEN the **whole-file
  proof** of `types.py` SUCCESS (§10.10 sibling check; the 5 already-verified TypeInferenceMixin methods +
  `_split_tuple_type` stay green).
- **corpus byte-diff-0** — authoritative worktree-at-HEAD sweep over the reference set (the live-emitter
  touch's oracle; §4). Any change → diagnose (uniqueness) → multimap-fix or revert.
- **ledger 3** — `Print Assumptions` / `#print axioms` unchanged; no new `axiom`; RecordInfoView (if needed)
  covered by `Phase2b_RecordVal` (confirm, §3-Q2).
- **non-vacuity** — the emitted bodies do real `Map.get self._record_types_by_whyml_name` + the inner
  `field_types` `Map.get` (no opaque `_get_N <hash>`).
- **count** 1226 → **1224** (both leaves).

## 6. Downstream follow-on (a SECOND win, separate increment)

Once `_field_type_of` is verified and returns a proved `Optional[str]` (not a trusted opaque), revisit
`_rhs_yields_array` / `_rhs_yields_map`: their Attribute/FieldGet branches currently compare
`_field_type_of(val_ir)`'s result by an **int-hash** (`self__field_type_of_1 val_ir = 1555321514 || …`)
because the leaf was trusted. With the leaf verified returning `option string`, those branches can route
through `str_eq_op` on the real string — closing the faithfulness residual `file-type-of-wall.md` §6 called
"permanent." Gate: re-port + re-prove both callers (must stay SUCCESS), byte-diff-0 (the caller change is
mirror-side / @mutable_state-gated). Do this as its OWN commit AFTER the leaf lands (not bundled) — it is a
faithfulness upgrade of already-converted methods, count-neutral.

## 7. Reference corpus (per the new-feature discipline)

Add to `test-suite/corpus/pycsl-reference/` (byte-diff-gated, mirror-independent):
- `NNNN.py` — a write-once `Dict[str, <TypedDict>]` populated in a preamble-like pass, then a
  `search-by-value-field` rewritten as a reverse-index `.get(k)` returning a proved `Optional[str]` (the
  `_field_type_of` shape in miniature; positive proof + an `assigns \nothing` twin).
- `NNNN.py` — the negative: a genuine `for x in d.values()` enumeration that MUST stay unprovable
  (auto-trusted), pinning the distinction the reviewer's §5 category makes (search-by-field ≠ enumerate).

## 8. Order & first action

`S-reverse-index spike → (if RecordInfoView needed) add the view → apply the 3 edits (init + insert + 2
bodies), live+mirror → drop both \trusted → full gate battery → single commit → THEN the §6 de-int-hash
follow-on as a separate commit`.

**First action — S-reverse-index spike (measure §3-Q1/Q2 + §4):** on a scratch branch/worktree, add the
init + insert + the two rewritten bodies + the reverse-index field to the mirror scaffold; remove both
`\trusted`; run `--fun` on both methods. Read the FIRST blocker (if any):
- clears immediately → `_record_types` value already typed; scope = reviewer's minimal fix. Proceed to full
  gates.
- blocks on the value read (`field_types` opaque / int) → scope = + RecordInfoView view (still bounded,
  keyed-only). Add it, re-spike.
- blocks on something else (the `cls`-resolution getattr chains, unrelated to the reverse index) → the
  `.values()` wall is cleared but a DIFFERENT recognizer gap remains; report it precisely (the reverse
  index still lifts the enumeration wall; the residual is a separate, smaller build).
Then run corpus byte-diff-0 + ledger audit before claiming cleared.

## 9. Risks & non-goals

- **Uniqueness of `whyml_name`** — the one correctness assumption; caught by byte-diff-0 (§4). Contingency:
  reverse index keeps first-inserted (`setdefault`) to match `.values()` first-match semantics, if a
  collision surfaces.
- **RecordInfoView scope creep** (§3-Q1) — if the value view is needed, keep it MINIMAL (only
  `whyml_name`, `field_types` — the two fields these methods read; the ~8 other `record_info` keys stay
  unmodelled). Do not model the whole heterogeneous dict.
- **No enumeration is introduced** — this plan does NOT make `_record_types` enumerable; the general
  Why3-`map`-enumeration wall (`file-type-of-wall.md` §3–§5) stands untouched for any FUTURE method that
  genuinely aggregates over all values (routes 1/2/3 of the report remain the menu there).
- **All-or-nothing per method** — do not commit a half-rewrite; both bodies + the index land together or revert.
- **Live-emitter touch** — the byte-diff-0 sweep is non-negotiable (a recognizer/refactor touching
  `src/pycsl` is the corpus-perturbation risk this campaign has been burned by).
