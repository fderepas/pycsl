# OPEN ROUTE #57 — `d.get(k)` ON A MISSING KEY IS THE INTEGER ZERO, NOT `None`
# (found 2026-09-09 by relaunch #51 at HEAD `37403f79`, one probe after route #56)

## WHY THIS IS THE MOST REACHABLE ROUTE IN THE LEDGER

Route #56 needs an `Optional`-typed mutable local, a shape the reference corpus does not
contain a single instance of. **This one needs `d.get(k)`** — everyday Python, and the
single most common way anyone reads a dict defensively.

## THE DEMONSTRATION (default `hoare` model, no flags, Python run to confirm)

Both `[+] Verification SUCCESS` at HEAD:

```python
from typing import Dict

#@ ensures \result == 1            # <-- FALSE OF THE PROGRAM
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 2}
    if d.get(5) == 0:              # Python: None == 0 is False
        return 1
    return 0
```

Python returns **0**. And the stronger shape, exactly as in route #56:

```python
#@ ensures \result == 1            # <-- FALSE OF THE PROGRAM
def f() -> int:
    d: Dict[int, int] = {1: 2}
    v = d.get(5)
    return v + 1                   # Python: TypeError: 'NoneType' + 'int'
```

Python **raises**. The model proves `\result == 1`.

## THE MECHANISM — FAITHFUL STORAGE, ERASING READ (route #56's shape again)

Emitted WhyML, verbatim:

```whyml
let d = ref (map_update_some (const (None: option int)) 1 2) in
if ((match Map.get !d 5 with | Some v_ -> v_ | None -> 0 end) = 0) then begin
```

The map is `map 'k (option 'v)` — **`None` is a real, distinct value in the model**. The
read collapses it: `| None -> 0`. This is the THIRD member of one family:

  * route #44  `None` was the integer 0
  * route #56  a `None` Optional-union LOCAL read back as the carrier's zero
  * route #57  a missing `.get` reads back as the value type's zero

## THE JUSTIFICATION THAT WAS BORROWED FROM A PLACE IT DOES NOT APPLY

The zero comes from `_dv_missing_default` (`src/pycsl/module6_whyml/expressions.py:1062`),
whose docstring says it is the

> "`None ->` placeholder for a dict SUBSCRIPT read (typed per ν; **proven dead under
> `#@ no_exception KeyError`**, the ambient default otherwise)."

That justification is coherent **for a subscript**: `d[k]` on a missing key RAISES, so
under `#@ no_exception KeyError` the arm is genuinely unreachable and the placeholder only
has to type-check.

**`d.get(k)` NEVER RAISES.** It is a total function that returns `None`. There is no
exception for `no_exception` to discharge, so there is nothing that can ever make this arm
dead — and the value it answers is not a placeholder standing in for unreachable code, it
is the model's actual answer for a perfectly ordinary, non-raising Python call. The
sentinel was reused from a path where an exception justifies it into a path where no
exception exists.

`_dv_missing_default` is called for `.get` with no explicit default at
`expressions.py:10459` and `:10502` (the self-field-dict twin and the local/param dict).

## MEASURED SCOPE

  * `d.get(k, 7)` — an EXPLICIT default — is **CORRECT** and must stay correct:
    `d.get(5, 7) == 7` proves and Python agrees. Any repair must preserve it.
  * `d[5]` on a missing key also proves `== 0` where Python raises `KeyError`. That is the
    language's DOCUMENTED opt-in exception stance (`#@ no_exception KeyError`,
    README:906-909) and is the same position taken for `IndexError`, `ZeroDivisionError`
    and the rest — so it is NOT claimed here as a new route. It is recorded because it is
    the path whose justification `.get` borrowed.
  * **THE `str` CODOMAIN IS ALSO LIVE — MEASURED, NOT ASSUMED, AND THIS MAKES #57
    STRICTLY BROADER THAN #56.** `d: Dict[int, str] = {1: "a"}` with `if d.get(5) == "":`
    proves `\result == 1` where Python returns 0. So does the string-KEY form,
    `d: Dict[str, int] = {"a": 2}` with `d.get("zz") == 0`.
    **AND THE REASON IS THE POINT.** Route #56 was confined to the `int` carrier because
    its sentinel (`""` for a str carrier) was ILL-TYPED against the comparand and died on
    a Why3 type error — a type ACCIDENT that masked it. Here there is no such accident:
    the `.get` lowering picks the sentinel FROM THE CODOMAIN TYPE ν, so it is
    type-correct by construction at every codomain, and every codomain decides.
    The `hval` codomain `(HInt 0)` remains unprobed and must not be assumed either way.

## CANDIDATE REPAIR

Route #56's, unchanged, and it reuses an EXISTING model (lesson (p): yes, one already does
this): when `.get` is called with ONE argument, the `| None ->` arm answers route #44's
`val function pycsl_none : int` instead of `_dv_missing_default(nu)`. `pycsl_none = 0` is
undecided, `pycsl_none + 1 = 1` is undecided, and the two-argument form is untouched, so
the positive control keeps proving. The `str`/`hval`/`emit_ir` codomains need their own
opaques (route #50's `pycsl_none_str` already exists for `string`).

**COST NOT YET MEASURED.** `.get` is used heavily by the emitter itself, so this is very
unlikely to be byte-inert on the mirror and will probably owe mirror re-proofs. That
measurement is the next step and it must not be skipped.

---

## THE NON-SCALAR CODOMAINS ARE NOW MEASURED (gen #4, 2026-09-10)

The landed repair deliberately left `hval` / `seq` / `map` / `array` / `emit_ir` on the old
`_dv_missing_default` placeholder, with the honest note that "they were NOT measured, and
route #56's lesson is that a carrier must be measured rather than assumed". That sentence
was the whole reason to probe them. **They are measured now, and they FAIL CLOSED.**

Probes run (each a `# pycsl-expected: FAIL` shape whose contract is FALSE of the program):

  * `Dict[int, List[int]]`, missing key, via `len(d.get(5)) == 0` — Python `len(None)`
    RAISES. Emission dies: *"This expression has type seq.Seq.seq int, but is expected to
    have type int"*.
  * the same through a declared local `v: List[int] = d.get(5)`, then `len(v) == 0`, and
    again through `v[0] == 0`. Same type error, same place.
  * `Dict[int, Dict[int, int]]`, missing key, via `v[2] == 0` — *"This expression has type
    int -> option.Option.option int"*.

**THE CONTROL IS WHAT MAKES THIS PRECISE, AND IT MOVES THE BOUNDARY OFF `.get` ENTIRELY.**
A plain SUBSCRIPT on the same type — `v: List[int] = d[1]; return v[0]`, with no `.get`
anywhere — fails with the IDENTICAL type error. So this is not a property of the `.get`
lowering at all: **a dict whose VALUE type is non-scalar is not readable from corpus Python
in the first place.** The placeholder those codomains carry cannot be reached from source,
which is why leaving it in place was harmless — but the reason is not the one the note
guessed.

**CLASSIFICATION: CERTIFIED BOUNDARY, and a FRAGILE one.** It is a Why3 TYPE ACCIDENT, not
a guard — and this campaign has already paid for that distinction twice (route #56 was
confined to the `int` carrier by exactly such an accident, and route #57 exists because
`.get` picks its sentinel from the codomain and so has NO such accident). A `SAFE-TYPED`
verdict is not protection.

**REOPENING CAPABILITY — the condition to watch, stated so it can be checked mechanically:**
the moment `Dict[K, V]` with a non-scalar `V` becomes READABLE (subscript or `.get`) without
a Why3 type error, every one of these codomains inherits route #57's original defect
immediately, because `_dv_missing_default` still answers them with a total placeholder
(`(Seq.empty: seq int)`, `(const (None: option ...))`, `(HInt 0)`, `(IrOther "")`) where
Python answers `None`. Anyone who lifts that type limitation MUST route the one-argument
`.get` arm through an opaque for the new codomain in the same change, exactly as the
`int`/`str` arms already are.
