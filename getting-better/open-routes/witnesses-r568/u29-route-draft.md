# DRAFT route — the caller-side frame of a method call is not the frame the callee was verified against

Status: DRAFT by executor u29 (run #5), for the driver to open. Measured on base 9e1fd7c2d
(int38) with the u29base worktree; probes in `scratchpad/u29/probes/` (paNN.py, .mlw, .prove.out).

## Finding (lvD's report, sharpened)

lvD observed that `#@ assigns` is not enforced for methods whose state is modelled as the
coarse `_pyobj_state` cell (`_Unparser`): the definition's frame is DERIVED from the body
(`functions._emit_function`, the "OBJECT-STATE WRITE MODEL" block adds `_pyobj_state` to a
`let` whose body applies a `setattr_*`), so a hidden `self._indent = 7` under a NAMED
`#@ assigns self._precedences, self._source` is absorbed by the cell and never refused.

On its own that is harmless: the `let` frame is honest, and callers that use THAT frame are
sound. The defect is that callers do NOT use it. A method call is lowered to a separate
caller-side `val <recv>_<m>_<k>` minted by `expressions._resolve_dotted_signature` from the
DECLARED clause, filtered to record labels, and that val can omit the cell the definition
writes. Route #213 made attribute reads (`getattr(o, "a"[, d])` on an UNKNOWN receiver)
state-keyed terms `pycsl_getattr_*(!_pyobj_state, o)`, whose soundness rests on EVERY
object-state write being visible as a write of `_pyobj_state`. A call through a frameless (or
cell-less) val is not, so two reads around it are ONE term and the caller proves the
attribute unchanged.

Measured (`#@ ensures \result == 1`; CPython, with `o is c`, returns 2 in every case):

```python
c.m(0); x = getattr(o, "flag", 0)
c.m(5); y = getattr(o, "flag", 0)
if x or not y: return 1
return 2
```

| probe | shape | caller-side val | result |
|---|---|---|---|
| pa16 | record class `C{a}`; `m` declares `assigns self.a`, body also stores `self.flag` (hidden) | `val c_m_1 (self: c) (x0: int) : unit writes { self.a }` (no cell; the `let c__m` has `writes { self.a, _pyobj_state }`) | **Verification SUCCESS** (false) |
| pa18 | as pa16 but the declaration is HONEST: `assigns self.a, self.flag` | same: `writes { self.a }` — the label filter drops `flag`, and the `#32 SPIKE` / route #109 fallback fires only when the filter drops EVERYTHING (`bool(declared) and not filtered`) | **Verification SUCCESS** (false) |
| pa19 | class with NO record (`type c = int`, `\trusted` `__init__`); receiver is a PARAM `c: C` | `val c_m_1 (x0: int) : int` — no receiver, no frame (`_record_param_classes` holds record classes only, so the call is not `matched_instance`) | **Verification SUCCESS** (false) |
| pa22 | as pa19 with `c: Any`, caller `assigns \nothing` | same frameless val; and because the caller is now "pure" the getattr reads take the UNKEYED constant form `pycsl_getattr_unknown_<h> o` (route #213's pure-context arm: the function is pure only because the opaque call is modelled pure) | **Verification SUCCESS** (false) |
| pa21 | CONTROL: same reads, the call is `self.m(..)` in a no-record class (the self-arm's coarse fallback puts `writes { _pyobj_state }` on the avatar) | `val self_m_1 (self: c) (x0: int) : unit writes { _pyobj_state }` | Verification FAILED (caller postcondition Timeout) — correct |

CPython: every probe prints 2 (`python3 -I paNN.py`). Proof logs: `probes/paNN.prove.out`.

The pure `\nothing` case lvD described is NOT reachable on its own: a `let` whose body writes
the cell under `#@ assigns \nothing` gets `writes { }` and Why3 rejects it (pa6: L3-tc
"depends on variable _pyobj_state, which is left out"). Direct reads of a non-record attribute
in a record class are ill-typed (pa3: `c._indent`, L3-tc fails), and getattr of an attribute
the file stores on a KNOWN receiver is refused (pa10, routes #376/#396). The live hole is the
unknown-receiver getattr (`o: Any`) across a call whose val under-states the effect.

## Which plane should catch it

None does today:
- `check-trusted-frame-honesty` / `check-assigns-underdeclaration` compare MIRROR declarations
  with LIVE bodies (TRAP = written-but-not-declared, HOLE only when the field is a record
  label); pa16's hidden attribute is not a record label, so it is a TRAP-class row at most,
  and the corpus is outside both planes' population.
- `check-assigns-writes-survival` measures declared-but-not-emitted for the DEFINITION's
  `writes`, not the caller-side val.
- `check-avatar-frame-parity` checks avatar frames of `self.<m>()` in converted MIRROR methods
  (bucket A same-file = 0), not `<recv>.<m>()` with a param / Any receiver, and not the
  partially-filtered case (pa18's val is non-empty, so it is not "frameless").

## Narrowest sound fix (proposal; not implemented in u29)

All edits are in live methods whose mirror twins are `\trusted`
(`ExpressionEmissionMixin._resolve_dotted_signature`, `FunctionEmissionMixin._emit_function`).

1. (pa18) `_resolve_dotted_signature`, both arms: fire the coarse fallback when the label
   filter drops ANY declared target, not only all of them:
   `_objstate_w = bool(_declared_w) and len(set(_w)) < len(set(_declared_w))` (same for
   `_objstate_rw`). Over-approximation only; the caller loses facts about object state it
   should never have had. COST WARNING: `check-assigns-writes-survival` measures TRAP 2989
   declared-but-not-emitted labels in the mirror, i.e. many mirror avatars are exactly
   pa18's partial-drop shape; rule 1 would add the cell to them, move those mirror
   emissions and owe their whole-file re-proofs (a frame widening can also break a
   converted caller's `writes`). Census the mirror before choosing it — this is why u29
   did not implement it ("fix only if small").
2. (pa16) `_emit_function`, at the point where a NAMED-assigns `let` gains `_pyobj_state`
   from its BODY: if the caller-side val would not carry the cell (every declared target is
   an emitted record label, so rule 1 does not fire), REFUSE: "the body writes object state
   the declared `#@ assigns` does not name; callers read the declared frame" (the route #316
   PYCSL-METHOD-FRAME shape, for attributes instead of parameters). This is the "compare
   declared vs derived frame" rule, and it is exactly lvD's hidden-write case.
3. (pa19 / pa22) a method call whose receiver is NOT resolved to a class contract (param of a
   no-record file class, `Any`, unknown) mints a frameless val, i.e. a PURE call. Either
   resolve the receiver (extend `_record_param_classes` to file classes without a record,
   so the route #109 fallback applies) or give every unresolved method-call val
   `writes { _pyobj_state }` (and make a caller containing one non-pure for route #213's
   keying). The second is the sound default; it is NOT narrow (every opaque method call
   gains an effect) and needs a corpus census before it is chosen.

Witness candidates for corpus ids when the route is opened: pa16, pa18, pa19, pa22, each `# pycsl-expected: FAIL`, plus pa21 as the control (the same false claim, correctly NOT proved when the val carries the cell).
