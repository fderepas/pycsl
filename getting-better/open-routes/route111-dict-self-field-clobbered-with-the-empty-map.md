# ROUTE #111 — a `set`/`dict`/`frozenset` self-field assigned from ANY non-alphanumeric
# lowered RHS is SILENTLY REPLACED BY THE EVERYWHERE-EMPTY MAP

**Status: FOUND, REPRODUCED, BOTH DIRECTIONS MEASURED. Repair NOT yet landed.**
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
