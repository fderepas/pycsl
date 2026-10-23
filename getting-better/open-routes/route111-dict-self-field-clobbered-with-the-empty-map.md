# ROUTE #111 — a `set`/`dict`/`frozenset` self-field assigned from ANY non-alphanumeric
# lowered RHS is SILENTLY REPLACED BY THE EVERYWHERE-EMPTY MAP

**Status: CLOSED AND FULLY GATED by gen #23 (2026-09-15)** — see THE REPAIR AS LANDED at the bottom. Original finding preserved below.
**Severity: SEV-1. First-order. NO ADVERSARIAL NAMING IS REQUIRED** — `self.b = self.a` is
ordinary Python, and that is what makes this worse than #107 and #110.

## PROVENANCE

The **substring-census** generator, second hit. Same family as #110 (`_coerce_to_int`), a
different value domain.

## THE MECHANISM, quoted

`src/pycsl/module6_whyml/statements.py:2604-2613`

```
2604            elif ftype in ("set", "dict", "frozenset"):
2605                # Map-typed field: keep map-shaped values, otherwise
2606                # use empty map. (Same pragma as `_handle_dotted_call`.)
2607                stripped = val.strip()
2608                map_prefixes = ("(map_update_some ", "(map_update_none ",
2609                                "(const (None: option int)", "(Map.get ")
2610                if not any(stripped.startswith(p) for p in map_prefixes):
2611                    if not stripped.replace("_", "").replace("!", "").isalnum():
2612                        val = "(const (None: option int))"
2613            code = f"{indent}{obj}.{safe_field} <- {val}"
```

The decision "is this RHS map-shaped?" is made by (a) a PREFIX TEST over generated text and
(b) **`str.isalnum()` after deleting `_` and `!`**. A bare local (`!t`) survives clause (b). A
field read, a call, a subscript — anything with a dot, a space or a paren — does not, and the
value is **replaced by the everywhere-empty map with no refusal and no warning**.

## BOTH DIRECTIONS MEASURED at HEAD `ee8da689`

**Direction 1 — the false claim PROVES.** `e3_dict.py`:

```python
class C:
    a: Dict[int, int]
    b: Dict[int, int]
    #@ assigns self.a, self.b
    def __init__(self) -> None:
        self.a = {1: 5}
        self.b = {}

    #@ ensures \result == 0
    #@ assigns self.b
    def copy_and_check(self) -> int:
        self.b = self.a
        if 1 in self.b:
            return 1
        return 0
```

`[+] Verification SUCCESS!` (rc=0.) CPython returns **1**.

The emitted body, read in full — note that the record literal in `f` models `a` FAITHFULLY,
so the information exists at the moment it is discarded:

```
  let c__copy_and_check (self: c) : int
    ensures  { (result = 0) }
  =
    self.b <- (const (None: option int));          (* self.a ERASED *)
    if (match Map.get (self.b) (1) with | Some _ -> true | None -> false end)
      then raise (Return 1) else raise (Return 0)

  let f () : int =
    let c = { a = (map_update_some (const (None: option int)) 1 5);
              b = (const (None: option int)) } in
    (c_copy_and_check_0 c)
```

**Direction 2 — route the SAME assignment through a local and it correctly FAILS.**
`e3_ctl.py` differs only in spelling the assignment `t = self.a` / `self.b = t`:

```
    let t = ref self.a in
    self.b <- !t;                                  (* the value SURVIVES *)
```
`rc=1 — [-] Verification FAILED` on the postcondition, the right goal. `!t` is alphanumeric
after stripping `!`, so clause (b) keeps it. The difference between a false proof and an
honest refutation is **whether the lowered RHS happens to be alphanumeric**.

## THE COST OF GETTING HERE — logged because a denominator written only when the result is
## interesting is not a denominator

Two earlier shapes measured NOTHING and are recorded as such:
  1. `self.d2 = src.d` across two objects — died on an UNRELATED Why3 type error (a record
     passed where the method avatar expected `int`).
  2. `self.b = self.a` written in one method and READ from another — **neither the true nor
     the false claim proved**, because the caller sees a value-opaque avatar
     (`val c_copy_over_0 (self: c) : unit writes { self.b }`, no `ensures`). The clobber is
     real in the definition and simply cannot reach a caller's proof.
Only the third shape — write AND read in the SAME method body, so no avatar sits between the
clobber and the proof — is decisive. **THE AVATAR IS THE FENCE FOR THE CROSS-METHOD CASE, AND
NAMING IT IS THE POINT**: this route is exploitable exactly where a method observes its own
write.

## A SECOND FACT, MEASURED, SAME GUARD

`self.b = {1: 5}` written in a NON-`__init__` method is **also** clobbered to the empty map.
Route #85's faithful-dict-literal repair covers the `__init__` RECORD LITERAL only. So the
"prefer faithful wherever the information exists" preference that #85 recorded is not yet
honoured on the method-body path.

## REPAIR SKETCH (to be RE-DERIVED before landing, per the #95 rule)

"Is this RHS map-shaped" is a TYPE question and the emitter knows the answer structurally —
drive it from the IR type of the RHS, not from `isalnum()` over lowered text. And **the
substitution must never be silent**: supplying the empty map is the "completeness fix that
supplies a WITNESS value" shape the campaign has been burned by five times. Where the value
is recoverable (a field read, a literal) it must be KEPT; where it genuinely is not, the
emitter must REFUSE.

---

# REPAIR SCOPE, CENSUSED BY GEN #21 (2026-09-14) — read this before scoping the repair

**THE CLOBBER POPULATION IN ALL FOUR TREES IS FOUR SITES.** AST census: a class-declared
`Dict`/`Set`/`FrozenSet` field assigned from an RHS that is neither a bare `Name` (which
survives the `isalnum()` clause as `!t`) nor a dict/set literal (which starts with a map
prefix):

    test-suite/corpus/pycsl-reference/0941.py:34   self.s = set()
    test-suite/corpus/pycsl-reference/0775.py:28   self.s = set()
    src/self-annotate/src/module6_whyml/statements.py:1660
                                                   self._inline_array_temps = set(array_vars)
    src/self-annotate/src/module6_whyml/statements.py:1730
                                                   self._current_record_var_classes =
                                                       IRScanner.find_record_var_classes(...)

**CAVEAT ON THE CENSUS, STATED SO IT IS NOT OVER-TRUSTED:** it keys on a class-level
annotation, while the emitter resolves the field type through `_field_type_for` /
`_record_types[...]["field_types"]`, which can know a type the annotation does not spell. So
FOUR is a LOWER BOUND, not a theorem. Re-derive it from `_record_types` before landing.

**WHAT THE FOUR SITES MEAN FOR THE REPAIR — and why gen #21 did NOT land one:**

  - The two corpus sites are `self.s = set()`, where collapsing to the empty map is
    ACCIDENTALLY CORRECT. They are not evidence the guard is right.
  - **The two remaining sites are in the SELF-ANNOTATION MIRROR'S OWN SOURCE.** They are real
    value losses, and they are load-bearing: the mirror's whole-file proof of `statements.py`
    currently models both fields as the everywhere-empty map. A repair that makes them
    FAITHFUL changes what that proof is proving, and a repair that REFUSES instead would stop
    the mirror emitting at all — which means editing live mirrored source in
    `src/pycsl/module6_whyml/statements.py` to avoid the shape.

  So the repair is NOT the cheap, provably-inert kind #110's was (#110's population was zero).
  It is a value-model change whose blast radius lands inside the mirror's own proof.

**THE NARROW REPAIR THAT IS AVAILABLE AND SOUND**, if a future generation wants an increment
rather than the whole route: the RHS IR (`stmt.value`) IS in scope at the site, and
`types.py:_field_type_of(attr_ir)` already resolves a `self.<field>` expression to its
declared type tag. Keeping the value when the RHS is itself a map-typed FIELD READ closes the
measured exploit exactly, and is byte-inert (none of the four sites is a field read). It does
NOT close the call-valued RHS direction, and **a partial repair must say so loudly rather than
let the route be marked closed** — a carrier surviving a repair is a second route.

**THE FULL REPAIR** remains as sketched above: drive the decision from the RHS's IR TYPE, and
REFUSE where the value is genuinely unrecoverable instead of inventing the empty map.

---

# THE REPAIR AS LANDED — gen #23 (2026-09-15)

Landed with routes #111–#117 as ONE combined battery (commit recorded in `driver-progress.log`).
Every verdict was PREDICTED in the progress log before it ran:
metric 459/484/25/0 · doc-coherency rc=0 · mirror sync 887 verbatim · mirror-check same 3
pre-existing drifts · trusted-raises 13/62 · trusted-reasons 459↔459 · type-only 53, 0
ill-typed · dropped-mutation 0/51/9/0 · byte-diff pycsl-ref 22 MOVED / GONE only 0996 (an
expected-FAIL witness now refused) · python-ref 6 MOVED · mirror emission 7 MOVED, every hunk
read and attributed · suite 3444/3462, the SAME 18 failures, ZERO XPASS · whole-file proofs of
all 7 moved mirrors SUCCESS, 0 bad (statements 17630, expressions 21347, stmt_control_flow
12284, pure_ast 3372, functions 1199, Module5_IREmitter 2109, preamble 216 Valid) · planes
34/34 `ok` COUNTED (after narrowing `check-singleton-constant-lowering`'s baseline: the split arm orphaned two entries whose justifications #115/#116 had just refuted — removed — and renamed the GenExp half's key; constant arms 14 -> 12; emission re-verified byte-identical).

**What landed.** `statements.py::_handle_fieldassign_stmt` (live + verbatim mirror): a
map-typed field store whose lowered RHS is neither map-prefixed nor alphanumeric now asks the
RHS IR `self._rhs_yields_map(stmt.value.to_dict())` — a map-typed field read, a map-returning
call, a set operator over one — and KEEPS such a value; anything else becomes the polymorphic
unconstrained `(any_map ())`. The everywhere-empty map is never substituted.

**Witnesses.** `e3_dict` / `e3_call` / `e3_lit` false claims PROVED at HEAD and are refused on
the method postcondition; the faithfulness control (`t = {1: 5}; self.a = t; self.b = self.a`,
true `\result == 1`) was REFUSED at the baseline and PROVES now. Corpus 1305 (field read, XFAIL),
1306 (faithful, PASS), 1307 (call, XFAIL). The mirror `statements.py` proof covers the edit.
