# OPEN ROUTE #243 — A DICT / SET VALUE ALIASED THROUGH A SECOND NAME IS A COPY IN THE MODEL

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Found by the ch16 (W-IPM S-A/S-D) chain agent while
spiking dict/set mutator lowerings; driver-reproduced at HEAD 4b894167: all four witnesses rc=0 "Verification
SUCCESS", CPython prints `True` for each (claims are `\result == False`).

## Witnesses (`witnesses-r243/`)
- `field_set_alias_local.py`: `a = self.s; self.s.add(1); return 1 in a` (existing @mutable_state set-field
  `.add` lowering).
- `field_alias1.py`: `self.d = {}; self.g = self.d; self.d[1] = 5; return 1 in self.g`.
- `field_alias2.py` / `field_alias3.py`: CROSS-METHOD — `link()` does `self.g = self.d`; `m()` stores
  `self.d[1] = 5` (dict) / `self.s.add(1)` (set) and returns `1 in self.g`; `m` proves with no precondition.

## Mechanism
Dict and set values are pure Why3 maps, so every assignment to a second name/field is a COPY; a later
in-place mutation through one name is invisible through the other. Route #59's guard only catches stores
through a LOCAL alias in the same function; the cross-method field alias cannot be caught by a per-function
guard.

## Repair direction (from the agent; needs a spike)
Either a by-reference (region) carrier for dict/set fields, or a CLASS-WIDE field-alias refusal (refuse any
`self.<f> = <expr naming another dict/set field or a local aliasing one>` and any local alias of a dict/set
field that is later read after an in-place mutation of the other name), plus fail-closed treatment of
mutation through an alias. Arrays are not affected (Why3 rejects record fields aliasing an array:
"mismatches regions").
