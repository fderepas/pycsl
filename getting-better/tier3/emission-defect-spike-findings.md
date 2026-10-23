# Emission-defect spike (V3) — resume findings (2026-07-07)

Resumed after the weekly-limit interruption, main-loop, one defect at a time (the user chose menu
option "emission-defect spike, then close"). This records the outcome on the census's **best lead**,
`_call_returns_string_collection`, and the decision.

## Best lead: `_call_returns_string_collection` — a GENUINE emitter bug, but NOT a clean self-verified −1

**The bug is real.** The live body does `ret, _, _, _ = self._resolve_dotted_signature(func_name)` — a
tuple-unpack with **three `_` throwaway targets**. The emitter (`statements.py::_handle_tuple_unpack_stmt`)
lowers each `_` via `whyml_ident("_") == "py_underscore"` → the SAME WhyML name `_tu_py_underscore`
for every `_`, emitting `let (_tu_..., _tu_py_underscore, _tu_py_underscore, _tu_py_underscore) = ...`
→ **Why3 error `duplicate variable _tu_py_underscore`** (`.mlw:315`). Any program with ≥2 `_` in one
tuple-unpack (e.g. `a, _, _ = f()`) hits it. This is a latent **tool-correctness defect** worth fixing.

**The fix is simple and correct:** a Python throwaway `_` should lower to the Why3 **wildcard `_`**
(discard, binds nothing) — collision-free and semantically right. With the fix in the live emitter,
`_call_returns_string_collection` **fully proves** (all VCs Valid, both provers).

**But it cannot land as a self-verified −1 in this campaign.** The fix edits the emitter method
`_handle_tuple_unpack_stmt`, which is itself **un-trusted (verified) in the mirror** — so the
feature-touches-verified-method rule (SKILL §10.4) requires re-porting + re-proving that mirror method
in the same commit. **Three natural formulations of the fix were attempted; all failed to self-verify**,
each on an `int vs string` value-model gap in the self-annotation:
1. conditional string comprehension `["_" if is_throwaway[i] else f"_tu_{...}" ...]` → `.mlw:472` int/string;
2. empty str-list + append (`tmp_names: List[str] = []; ... tmp_names.append("_")`) → `[]` defaults to
   int-list, append(str) clashes;
3. in-place str-overwrite (`tmp_names = [f"_tu_{t}" ...]; ... tmp_names[i] = "_"`) → str-list
   element-assignment still int/string.

Per the SL per-stub attempt budget (3) and the "do not merge a red verified method / do not re-trust"
rule, the changes were **reverted** (clean at 1240, fidelity 90/90).

## The lesson (confirms the census)
Even the *best* emission-defect lead — a genuine, correctly-diagnosed emitter bug with a simple fix —
is **not a clean self-verified −1**, because self-verifying the fix means re-proving a verified emitter
method whose natural formulations hit the **same value-model gaps** (int/string over str-lists) that
block the rest of Tier 5. The tool cannot yet self-verify its own bug-fix. The census's "0–3 clean −1s,
each needs a spike" is vindicated: the honest clean-−1 yield of the emission lever is **~0**.

## Deferred tool-correctness item (NOT a campaign marker)
Fix `_handle_tuple_unpack_stmt` so a `_` target lowers to the Why3 wildcard `_`. This is a real
emitter correctness fix for user programs with multi-`_` tuple-unpacks; land it as a **standalone tool
fix** (byte-diff-gated on the corpus) when the self-annotation can model the re-port — or fix it in the
emitter and re-port the mirror once str-list construction/assignment is modellable. Tracked here; not
counted against the trusted floor.

## Second lead: `iter_length` root cause (`_emit_metatype_tags` + `statements.py::rec`) — ALSO value-model-gap-blocked

Reproduced `_emit_metatype_tags`: the live body is `for nm, v in (("tag_int",0), …, ("tag_object",99)):`
— iteration with tuple-unpack over a **heterogeneous `(str, int)` tuple-of-pairs literal**. The emitted
WhyML (`.mlw:326`) shows the real blocker: the tuple literal is lowered to an **opaque int hash**
(`iter_length 2068068353`), and the loop body emits `int_to_string nm` — i.e. `nm`, which is the string
`"tag_int"`, is **mistyped as int** (unpacking a `(str,int)` pair types both slots int). So the "unbound
`iter_length`" symbol is a *secondary symptom*; the true blocker is the **heterogeneous-tuple-unpack
value-model gap**, and fixing the `iter_length` declaration alone would not make the body prove. Reverted;
clean at 1240. (There *is* a real latent declaration/scoping bug behind `iter_length` for tuple-literal
iterables, deferred with the tuple-unpack fix as a tool-correctness item.)

## Decision — CLOSE at 1240
Both emission leads (`_call_returns_string_collection`, `_emit_metatype_tags`+`rec`) are **genuine
emitter issues that are NOT clean self-verified −1s** — each self-verifying re-port hits the same
`int vs string` / heterogeneous-collection value-model gaps that define Tier 5. **The emission-defect
lever's honest clean yield is 0.** Every Tier-5 lever is now measured dead: F1 (≤3), F-B1 (NO-GO),
emission defects (0). **Marker campaign CLOSED at the honest floor 1240** — durable deliverable: the
certified ADT foundation (3-axiom ledger held); measured residual: ≈125 `Dict[str,Any]` leave-trusted,
the by-ref-mutation boundary, 2 deferred emitter-correctness items (multi-`_` tuple-unpack wildcard;
tuple-literal `iter_length` declaration + heterogeneous-tuple-unpack typing), 4 irreducible floor.
