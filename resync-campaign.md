# resync-campaign.md — re-sync the `statements.py` self-annotation mirror to the current emitter

**Purpose.** Restore true body-faithfulness for the 12 reflecting-family `_handle_*` handlers.
`bin/check-module6-mirror-sync.py` proved that `src/self-annotate/src/module6_whyml/statements.py`
DRIFTED from the live emitter (`src/pycsl/module6_whyml/statements.py`): 10 of its un-`\trusted`
handlers no longer match the code they claim to reflect, so verifying them proves a STALE mirror,
not the current emitter. This campaign makes the mirror a VERBATIM copy of the live emitter AND
keeps it verifying, then wires the checker in as a permanent hard gate.

**Doctrine.** [no-more-int] + small-trusted-core. Every emitter change is `@mutable_state`-gated →
**byte-diff 0** across the 627-corpus (the corpus has no `@mutable_state` class, no emit_ir
reflection). Feature-vs-refactor: this is a **self-annotation extension** (adds emit_ir model +
recognizers so the current emitter can self-verify) — it must NOT change corpus emission.

**Companion:** `item34.md §8` (the finding). Reference corpus: add a `@mutable_state` witness per
new emit_ir projection to `test-suite/corpus/pycsl-reference/` + a mirror witness (see §5).

---

## 0. Verdict — what drifted and why (measured in the re-sync attempt)

The drift has two causes:

1. **Typed-IR migration (pre-session, dominant).** The live emitter moved `_expr_to_whyml` to
   take a typed `ExprIR` node (`self._expr_to_whyml(stmt.value, …)`); the mirror still passes the
   pre-migration `stmt.value.to_dict()`. Affects ~7 handlers (ghost_array_set, array_slice_set,
   array_set, critical_section, fieldassign, fieldaugassign, assign).
2. **This session (3).** The CF4/CF5 tool changes to the live `_handle_tuple_unpack_stmt` (CF4),
   `_handle_augassign_stmt` (CF5 union), `_handle_expr_stmt` (CF5 str-key hash) were not
   back-ported.

**The split (established).** The CODE re-sync is trivial; the VERIFICATION is the campaign:
- **Code:** a body-swap + 4 field decls + 3 sibling stubs makes the mirror verbatim →
  `check-module6-mirror-sync.py` PASSES (all 19 methods). *This was proven, then reverted to keep
  the tree green.*
- **Verification:** the CURRENT emitter reflects on emit_ir features the mirror's emit_ir ADT does
  not model — the wall is `val_ir.get("args")` (the args LIST; the ADT carries only `arg0_of`/
  `nargs_of`, not an `array emit_ir`). Re-ported bodies drove the type error 436 → 564 with ~7
  fixes before hitting this ADT gap.
- **A real emitter bug** was found + fixed en route (already committed, byte-diff 0): line-2651
  `_call_named_builtins` re-lowered already-lowered `args` → crash on `<computed>.endswith(…)`.

---

## 1. Stages (each: apply → type-check → prove → byte-diff 0)

### R0 — code re-sync (CODE-trivial; ~30 min). *Re-apply what the attempt established.*
- **R0.1** Body-swap the 10 drifted handlers from the live emitter into the mirror, preserving
  each handler's `#@` contract block AND inline `#@ loop invariant`s (only
  `_handle_tuple_unpack_stmt` has inline ones: 3 invariants + 1 variant before `while i_tu`).
- **R0.2** Declare the 4 state fields the re-ported bodies read, on the mirror class
  `StatementEmissionMixin`: `_current_self_type: str`, `_heap_var: str`,
  `_todict_aliases: Dict[str,str]`, `_getattr_self_dict_aliases: Dict[str,str]`.
- **R0.3** Add the 3 `\trusted` sibling stubs: `_call_returns_string_collection(func_name:str)
  -> bool`, `_resolve_dotted_signature(func_name:str) -> Tuple[str,List[str],int,int]` (returns
  `("",[],0,0)`), `_str_operand_to_int(s:str) -> str`.
- **Gate:** `check-module6-mirror-sync.py` → "OK: all 19 … verbatim copies". (Reached in the attempt.)

### R1 — extend the emit_ir ADT for the args list (the verification WALL).
- **R1.1** Add `val args_of (e: emit_ir) : array emit_ir` (opaque; sound — no length/content law
  beyond the type) to the emit_ir theory (`preamble.py::_emit_exprir_theory`, near `arg0_of`/
  `nargs_of`); add `"args": "args_of"` to `_EMIT_IR_PROJ` (expressions.py). So `val_ir.get("args")`
  / `val_ir["args"]` → `(args_of val_ir)`.
- **R1.2** Handle the operations the emitter applies to `.get("args")`:
  - `not val_ir.get("args")` (emptiness) → array truthiness (`Array.length … = 0`);
  - `(val.get("args") or [{}])[0]` → array-or-default then index (or recognize the whole idiom →
    `arg0_of`, the existing first-arg projection);
  - `len(val_ir.get("args"))` → `Array.length` (should already route via `nargs_of`-consistency).
- **Gate:** `_handle_assign_stmt` + `_handle_expr_stmt` (the two `.get("args")` users) type-check.

### R2 — per-handler verification fixes (the tail; cascades like the CF campaign).
- Drive the type error through the 10 re-ported bodies, fixing each evolved construct with a
  `@mutable_state`-gated recognizer (the established pattern). Known so far:
  - **string-typed getattr-dict get:** `self_field_name_alias = getattr(self,
    "_getattr_self_dict_aliases", {}).get(var_name)` → string local (fixed in the attempt by
    declaring the field so §14 fires — verify it still holds after R0).
  - **emit_ir subscript projection:** `val_ir["func"]`/`["value"]` already route via
    `_handle_subscript` §26 (line ~3502) — confirm no gaps for the newly-exercised keys.
- Expect further constructs (each a targeted, byte-clean recognizer). Log each in the ledger.
- **Gate:** `statements.py --no-proof` → Verification SUCCESS (type-checks).

### R3 — prove + wire the gate.
- **R3.1** Full proof: `statements.py` (add any loop bounds/variant the re-ported loops need —
  the tuple_unpack ones are already carried; watch for new while-loops).
- **R3.2** Byte-diff 0 across the 627-corpus for all emitter changes (R1 + R2).
- **R3.3** Wire `check-module6-mirror-sync.py` into `bin/check-self-annotate-sync.sh` (call it,
  propagate its exit code) so drift is a HARD gate going forward.
- **Gate:** `statements.py` proves; byte-diff 0; suite green; sync-checker green + gated.

---

## 2. Critical files

- `src/self-annotate/src/module6_whyml/statements.py` — mirror: body-swap (R0.1), field decls
  (R0.2), sibling stubs (R0.3).
- `src/pycsl/module6_whyml/preamble.py::_emit_exprir_theory` — `args_of` decl (R1.1).
- `src/pycsl/module6_whyml/expressions.py` — `_EMIT_IR_PROJ` "args" entry (R1.1); `_handle_subscript`
  / `_handle_call_expr` / `_handle_binop` recognizers (R1.2, R2); `_is_string_expr` shapes (R2).
- `src/pycsl/module6_whyml/statements.py` — `_val_elem_ty` / string-local collector recognizers (R2).
- `bin/check-module6-mirror-sync.py` — the checker (done); `bin/check-self-annotate-sync.sh` —
  wire-in (R3.3).

---

## 3. Out-of-scope / soundness boundary

- **Corpus untouched** — every emitter change `@mutable_state`/emit_ir-reflection-gated; byte-diff
  0 is the gate. The line-2651 fix is already banked (byte-diff 0).
- **`args_of` is opaque** — `array emit_ir`, no length/content law (a sound under-approximation).
  It exists for TYPE-safety of the reflection, not a value claim.
- **Type-safety + frame only** — same as the 17 landed handlers (`requires True / ensures True /
  assigns <frame>`), NOT value-faithful `ensures \result == <string>` (that is item 3, Ceiling B).
- **CF family untouched** — the 5 CF handlers are already verbatim-in-sync (checker green); this
  campaign is `statements.py` only.

---

## 4. Verification (exact commands)

```bash
python3 bin/check-module6-mirror-sync.py            # R0 gate: all 19 methods verbatim
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl --no-proof   # R2
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl              # R3 proof
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after && diff -rq <clean-baseline> /tmp/after
bash bin/run-self-annotation-suite.sh              # suite green
bash bin/check-self-annotate-sync.sh               # R3.3: sync-check gated (incl. module6_whyml)
```

---

## 5. Reference corpus (required)

Per feature-plan convention, add a `@mutable_state` witness exercising the new emit_ir surface to
`test-suite/corpus/pycsl-reference/` + a mirror witness:
- `args-reflection-witness.py` — a `@mutable_state` method doing `if not node.get("args"): …` and
  `node.get("args")[0]` on an ExprIR param (exercises `args_of` + emptiness + index), verifying
  SUCCESS and byte-clean absent from the corpus.

---

## 6. Progress ledger (live)

| Stage | Status |
|---|---|
| (found) emitter bug line-2651 | ✅ FIXED + committed (byte-diff 0) |
| (found) checker `check-module6-mirror-sync.py` | ✅ committed |
| R0 code re-sync (swap + 4 fields + 3 stubs) | ◻ TODO (proven reachable in the attempt; reverted) |
| R1 emit_ir `args_of` list projection | ◻ TODO (the verification wall) |
| R2 per-handler verification recognizers | ◻ TODO (cascading tail) |
| R3 prove + byte-diff 0 + wire the hard gate | ◻ TODO |

---

## 7. Definition of done

- `statements.py` mirror is a VERBATIM copy of the live emitter (checker green) AND proves
  (type-safety + frame); byte-diff 0; suite green.
- `check-module6-mirror-sync.py` wired into `check-self-annotate-sync.sh` as a HARD gate — no
  reflecting handler can silently drift from the emitter again.
- Result: all 17 body-faithful handlers (12 reflecting + 5 CF) verify the CURRENT emitter, not a
  stale copy — the integrity gap `item34.md §8` flagged is closed.
