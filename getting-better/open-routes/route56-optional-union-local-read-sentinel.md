# OPEN ROUTE #56 — A `None` OPTIONAL-UNION *LOCAL* READS BACK AS A SENTINEL, SO
# `None == 0` PROVES TRUE
# (found 2026-09-09 by relaunch #51 at HEAD `37403f79`, while scoping the L1 fidelity repair)

## THE DEMONSTRATION (default `hoare` model, no flags, Python run to confirm)

`scratchpad`/`probe56/u3.py` — **`[+] Verification SUCCESS`, Valid in 15 steps**:

```python
from typing import Optional

#@ requires c <= 0
#@ ensures \result == 0          # <-- FALSE OF THE PROGRAM
#@ assigns \nothing
def f(c: int) -> int:
    x: Optional[int] = None
    if c > 0:
        x = 5
    if x == 0:
        return 0
    return 9
```

Python, run: `f(0)` is **9**. `None == 0` is `False`, so the `if` is not taken. The model
proves `\result == 0`.

## THE MECHANISM — THE STORAGE IS FAITHFUL, THE *READ* IS NOT

The emitted WhyML, verbatim (`--no-proof --keep-mlw`):

```whyml
type _union_f_0 = Arm_0_0 int | Arm_0_None
...
let x = ref (Arm_0_None : _union_f_0) in
  x := (Arm_0_0 5)
if ((match !x with Arm_0_0 _v -> _v | _ -> 0 end) = 0) then begin
```

**The representation models `None` EXACTLY** — `Arm_0_None` is a real, distinct
constructor. What erases it is the VALUE-READ PROJECTION
(`_union_local_read_projection` / `_union_read_projection`,
`src/pycsl/module6_whyml/expressions.py:13398` and `:13407`), whose non-Some arm answers
a SENTINEL: `| _ -> <carrier's zero>`. For an `int` carrier the zero is `0`, and `0 = 0`
is true, so the `None` value and a genuine `0` are the same term.

The sentinel table (`expressions.py:13430-13448`) is:

    str / string  -> ""          real / float -> 0.0
    emit_ir       -> (IrOther "")   a declared record -> _record_default_literal(...)
    ANYTHING ELSE (notably `int`, and `bool` which Module 5 maps to `int`) -> 0

**This is route #44's defect (`None` was the integer 0) reaching through a door route
#44's repair does not cover.** #44 installed a shared opaque for `None`; the union-local
carrier projection never consults it.

## WHY IT WAS NOT FOUND BEFORE — TWO REASONS, BOTH WORTH KEEPING

1. **THE `str` CARRIER FAILS CLOSED, AND IT FAILS CLOSED FOR THE WRONG REASON.** The same
   program at `Optional[str]` (`probe56/u2.py`, `x == ""`) does NOT prove — it dies with
   `This expression has type string, but is expected to have type int`. That is a Why3
   TYPE accident, not a guard. Anyone who probed this class at `str` — and this campaign
   probed the `is None` residue class at `str` exhaustively in routes #50 and #51 — would
   have concluded the class was safe. **`int` is the carrier where the sentinel and the
   comparand have the same Why3 type, and it is the only one that decides.**
2. **THE CORPUS HAS NO OPTIONAL-TYPED MUTABLE LOCAL AT ALL.** In-tree comments assert it
   (`module6_whyml/statements.py:5666-5668`, `frontend/Module5_IREmitter.py:4909-4912`)
   and it checks out: the only `: Optional[...]` occurrences under
   `test-suite/corpus/pycsl-reference/` are PARAMETERS (`0349.py:14`, `0891.py:28`). The
   PARAMETER path keeps the faithful `| _ -> false` None arm
   (`expressions.py:5518-5531`). So the entire reachable-but-untested surface is locals.

## THE DOCUMENTATION SAYS THE OPPOSITE, AND IS HALF RIGHT

`docs/pycsl-translational-reference.md:2053-2056` lists `_optional_union_locals` among the
carriers that "each model `None` exactly, so the degeneration this route closes cannot
arise for them." That is TRUE of the stored representation and FALSE of the read
projection. A reader checking whether this class was safe would have been told it was.

## WHAT IS REACHABLE

`_optional_union_locals` is populated in `module6_whyml/statements.py:5709-5714` from any
symbol-table entry whose type is a synthesized `_union_*` and which is NOT a formal
parameter. The `_union_*` type is synthesized by `_normalize_union_annotation`
(`frontend/Module5_IREmitter.py:3841`) from ORDINARY `Union[...]` / `Optional[...]` /
`A | B` annotations — no `#@` directive and no mirror-specific construct required.
Multi-Some-arm unions (`Union[int, str, None]`) are OUT of scope: the projection returns
None for them (`expressions.py:13424`, `:13428`).

## CANDIDATE REPAIRS (not yet built — this file records the route, not its closure)

1. **Route the non-Some arm through route #44's existing `None` opaque** instead of a
   type-keyed zero, so `x == 0` on the `None` path is undecided rather than true. This is
   the campaign's established idiom (#44/#47/#48/#50/#51) and reuses an EXISTING model, so
   lesson (p)'s census answer is "yes, one already does this".
2. **Refuse the value read** of an optional-union local that is not dominated by a
   narrowing guard. Fail-closed and cheap, but it deletes a capability.
3. Adopt the OPTION-TARGET twin `_union_read_option_projection` (`expressions.py:13451`),
   which already returns `| _ -> None` and whose own docstring (`:13460-13469`) says the
   sentinel form "would silently model an ABSENT value as the empty string, which is
   exactly the None-reads-as-'' erasure the campaign has had to repair before". **The tree
   already contains a faithful twin of the defective function, and says so in a comment.**

## THERE IS NO GUARD TODAY

`core_ir_semantic._check_union_narrowing` (`:1671`) fires only on `if` TESTS, only checks
the test's shape against a whitelist, and emits `warnings.warn` — explicitly "not an
error" (`:1690-1694`). It never blocks emission and says nothing about reads. There is no
`no_exception`/UB trigger covering a value read of `None`.
