# Wall: pydict copy-and-set-field / dict-comp CONSTRUCTION

**Status:** OPEN — escalated by the self-tcb-reduction-driver after Phase 1 drained (no_cheap_remaining
at count 721) and a broad ranked taxonomy identified this as the #2 CONTAINED lever (~10-15 estimated
un-co-blocked consumers, a single primitive). The tuple-unpack/items binder front is mined out (0
consumers, `wall-lessons.md`); this is a DIFFERENT capability.

## 1. The wall

The emitter models a `Dict[str, τ]` (faithful-scalar τ) as `map string (option τ)` and already has
READ-ONLY over-approx access (`keys_get`/`values_get`/`Map.get`). It has NO faithful model for
CONSTRUCTING a new/updated map:
- `d[k] = v` used as an updated-map value (in-place set with a caller-visible result);
- dict-comprehension `{k: v for k, v in src.items() if p(k)}` — a FILTERED new map;
- `dict(d, **upd)` / copy-and-update.

These lower today to an opaque facade or type-fail, blocking every stub that builds a map.

## 2. The primitive (make-or-break — must be FAITHFUL, not a facade)

For `map string (option τ)` the faithful primitives are Why3-native:
- set: `Map.set d k (Some v)` — total, faithful, no axiom.
- copy-and-set: same (maps are immutable values in Why3 logic).
- filtered dict-comp: a fold over the key-seq building `Map.set` accumulatively, with the guard `p k`
  gating each set — a bounded loop over `keys_get`, provable variant `(Seq.length keys - !idx)`.

So the primitive itself is expected to be trivially faithful. The RISK is NOT the primitive; it is
(per the tuple-unpack lesson) whether any trusted stub has this as its SOLE blocker.

## 3. Make-or-break = CONSUMER EXISTENCE (the real falsifier)

The banked lesson (`wall-lessons.md`, pytuple + native-map-items both proved but had 0 consumers):
**a provable primitive with 0 un-co-blocked consumers is a Gate-C reject — do NOT build it.** So the
spike is NOT "does Map.set prove" (it trivially does); it is:

> **Does ≥1 trusted stub convert end-to-end with ONLY the dict-construction primitive added
> (verified by whole-body `--fun` SUCCESS), no other co-blocker?**

Census-named candidate consumers (to verify, NOT assume): `substitute` (canonical.py — BUT also
blocked by the Term-ADT recursive walk, wall #1, so likely co-blocked), several `_collect_*`,
`_extract_happy_properties` (dict-param mutation). The overlap with wall #1 (`substitute` needs BOTH)
means the ~10-15 estimate is OPTIMISTIC — the review/spike must find a consumer blocked ONLY by dict
construction.

- Spike finds ≥1 sole-blocked consumer → BUILD the primitive (gated) + convert that stub.
- Spike finds 0 (all dict-construction consumers also need the Term walk / string facades / int-erased
  values) → THIN VEIN, record, pivot to wall #1 (Term recognizer-grammar arms).

## 4. Scope / non-goals
- IN: `map string (option τ)` set / copy-and-set / filtered dict-comp for faithful-scalar τ.
- OUT: Dict[str,Any] heterogeneous-value construction (the pyval root, multi-session); the Term-ADT
  recursive walk (wall #1).
- Ledger 3; contract shape `requires True/ensures True/assigns <tight>`; corpus byte-diff 0 (gate on
  `_uses_/_emitting_<method>`); drift 2; no new axiom (Map.set is native).
