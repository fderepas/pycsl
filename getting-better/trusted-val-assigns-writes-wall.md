# Wall: trusted method-val drops its `#@ assigns self.<field>` frame (no `writes` clause)

**Status:** OPEN — Phase 2 escalation (Phase 1 returned `no_cheap_remaining` at count 877).
**Slug:** `trusted-val-assigns-writes`. **Author:** driver-coordinator (tainted — see the independent review).

## The measured symptom
Converting `parse` (mirror `frontend/Module2_Parser.py`) refutes on the whole-file proof:

```
line ~1548: this write effect does not happen in the expression
  on:  let _contractparser__parse (self: contractparser) : ... writes { self.i }
```

`parse`'s only body effects are: a call to the **trusted** `_parse_contract` (`#@ assigns self.i`),
`at_eof` (no write), and `_err` (`-> NoReturn`, `absurd`). So in the emitted model, `parse`'s body
writes **nothing** — its faithful frame `assigns self.i` (→ `writes { self.i }`) is unprovable, and
`assigns \nothing` would be a **false** frame (the live `parse` transitively advances `self.i`; lesson 13).

## The confirmed mechanism (code-read, not assumed)
A trusted method emitted as an abstract `val` gets **no** `writes { self.i }`, because BOTH emission
paths exclude the self-field case:

1. `statements.py::_emit_frame_condition` (val branch, ~L1837-1856): for `_emitting_val_contract`,
   emits `writes` ONLY for **global**-field assigns (`objname != "self"`, e.g. `_filesystem.fd_open`);
   it deliberately **skips** a method's `self.<field>` assigns (L1851), with the comment:
   *"A method's `self.<field>` assigns is already turned into the val's `writes` by the existing
   method-writes machinery; re-emitting it produces an unbound/duplicate target (regressed
   formal_coll/formal_que: `self._size`)."*
2. `functions.py` method-writes machinery (~L3278-3283): emits `writes { self.x }` from
   `_module_method_writes` ONLY when `is_method and **not emit_as_val** and self_type ∈ _mutable_state_classes`.
   The `and not emit_as_val` clause means a **trusted val is excluded**.

⇒ The statements.py:1849 comment's assumption is **stale/wrong** for the trusted-val case: the
"existing machinery" it defers to explicitly excludes vals. Net: a trusted method-val with
`#@ assigns self.<field>` is emitted **effect-free** — its declared frame is **decorative** (the same
class of gap as lesson-10's derived-frame-vs-declared-frame hole, but here the frame is DROPPED, not derived).

## Soundness reading
The current effect-free trusted-val is **unsound-permissive**: a caller composing it sees `self.i`
as unchanged across the call, when the live method advances it. Emitting `writes { self.i }` (from the
declared `#@ assigns`) makes the model **faithful**. This is a soundness-CLOSING change in intent.

## Blast radius — NOT mirror-only (this is why it is RISKY, not cheap)
4 reference-corpus programs have trusted methods with `#@ assigns self.<field>`:
`0661.py, 0662.py, 0900.py, 0901.py`. Emitting the previously-dropped `writes` clause **changes their
generated WhyML** → this is an **M1 semantics change** (corpus byte-diff ≠ 0), requiring re-proof of
every affected program, NOT byte-diff-0. It also globally changes trusted-val frame semantics.

## The candidate fix
Allow the `emit_as_val` + `is_method` + `@mutable_state` path to emit `writes { self.<field> }` from
`_module_method_writes` (or the declared `#@ assigns`), GUARDED against the unbound/duplicate-target
regression the statements.py:1849 comment warns about (`formal_coll`/`formal_que` `self._size`).

## Make-or-break spike (measure before build — Gate S)
Apply the fix, convert `parse`, then require ALL of:
1. `parse` / Module2_Parser whole-file proof: SUCCESS.
2. `formal_coll` / `formal_que` still prove (the exact regression the comment warns about — do NOT
   reintroduce the unbound/duplicate `self._size` target).
3. The 4 corpus programs (0661/0662/0900/0901) **re-prove** (M1: the diff is exactly the added
   writes clauses AND every affected program stays green).
4. §10c all-7-importer L3-tc (shared-emitter change).
5. Ledger stays 3.

**Refutation exit:** any of (1)-(4) fails → CERTIFIED-BOUNDARY (record + the reason) — do NOT force it.

## Potential upside if BROKEN
Not just `parse`: a VEIN of caller stubs whose frame is justified transitively through a trusted
callee's `#@ assigns` (parser: `parse`, `parse_contract`, `parse_node_contracts`, …) may unlock.

## Risk classification
SOUNDNESS-SENSITIVE + CORPUS-PERTURBING (4 programs) → per the safe-vs-risky-bricks discipline this
is a RISKY brick: it is landed ONLY if the spike passes AND an independent fable review blesses the
soundness AND all 4 corpus programs re-prove. Otherwise it is recorded as a well-evidenced boundary
and FLAGGED for the user — not force-landed autonomously.

---
## SPIKE VERDICT (2026-07-27): REFUTE → CERTIFIED-BOUNDARY
Measured, then reverted clean (count 877). The fix makes `parse`'s own VC Valid but refutes on:
- **4a**: 4 new unproven goals in siblings `_parse_lock_order`/`_parse_interface` — they were green
  only because trusted callees (`_parse_assigns`/`_parse_mutex_expr_str`) were effect-free; the
  faithful `writes {self.i}` havocs `self.i` and the callees lack monotonicity/bound `ensures`.
  **Latent-unsoundness finding.**
- **4b**: Module5_IREmitter L3-tc — `unbound ... '_cur_func_symtab'`; a trusted method's
  `#@ assigns self._cur_func_symtab` field isn't a bound mutable record field.
- **4e CORRECTION**: corpus byte-diff = 0 (no corpus program has trusted-val ∧ @mutable_state ∧
  assigns self.field); the blast-radius premise above was inaccurate — the change is corpus-inert.

**Resolution:** the simple single-method fix is a CERTIFIED-BOUNDARY. The real win requires a
multi-method faithful-frame campaign (strengthen affected trusted callees with monotonicity/bound
`ensures`; make assigned self-fields bound mutable record fields). FLAGGED for the user, not
autonomously undertaken.
