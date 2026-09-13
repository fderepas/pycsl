# ROUTE #101 — A SINGLE-INDEX `assigns seq[idx]` ON A BODYLESS `val` EMITS **NO FRAME AT ALL**

**Severity 1. OPEN. Found gen #17 (2026-09-13) by the `continue`-census.**
**It ships in the standard library today: `src/pycsl_lib/oper/__init__.py:175`.**

## THE ONE-LINE STATEMENT

A `\trusted` / `\abstract` / **imported** function whose `assigns` target is a SINGLE-INDEX
subscript (`seq[idx]`) is emitted as a `val` with **no `writes` clause**, and a `val` with no
`writes` is the STRONGEST possible claim: Why3 is told the stub is PURE. A caller then proves the
array UNCHANGED across a stub contracted to write it.

## THE MECHANISM, READ OFF THE EMITTED WhyML (not inferred)

`module6_whyml/statements.py::_emit_frame_condition`, inside `if self._emitting_val_contract:`,
builds the `val`'s frame from TWO collector loops and nothing else:

  * `:3411` — `if not isinstance(a, dict) or a.get("type") not in ("Attribute", "FieldGet"): continue`
    → builds `field_targets` (the `self.f` / `_global.f` spelling).
  * `:3479` — `if not isinstance(a, dict) or a.get("type") != "AssignsRegion": continue`
    → builds `region_targets` (the `arr[lo..hi]` spelling), and the NON-parameter residue
    into `_unframed_regions`, which route #98's co-landing half REFUSES at `:3498`.

`#@ assigns seq[idx]` is **neither**. `Module2_Parser._parse_assigns_region` (`:1527`) requires a
`..` range — it does `expect_op("[")`, `_parse_expr()`, **`expect_op("..")`** — so a single index
fails that `_try` and falls through to `exprs = [self._parse_expr()]` (`:1521`), landing in the IR
as `{"type": "Subscript", ...}`.

So the `Subscript` spelling matches NEITHER loop:
  - it contributes nothing to `field_targets`,
  - it contributes nothing to `region_targets`,
  - **and nothing to `_unframed_regions`, so route #98's refusal never fires.**

`_val_targets` is therefore empty, the `if _val_targets and not nothings:` return at `:3513` is
skipped, control reaches `if self._value_semantic: return []` (`:3518`, and the default model is
`hoare` ⇒ `_value_semantic` is True), and the `val` is emitted **pure**.

## THE MINIMAL PAIR — ONE SPELLING OF THE SAME INTENT, TWO FRAMES

Identical `\trusted` stub, identical body, identical `requires`; only the `assigns` spelling differs.

| `#@ assigns …` | emitted `val` frame | `ensures \result == 7` |
|---|---|---|
| `seq[idx]`  (single index → IR `Subscript`)     | **ABSENT** | **`Verification SUCCESS! All contracts formally proven.`** |
| `seq[0..1]` (range → IR `AssignsRegion`)        | `writes   { seq }` | FAILS (`Unknown`) — the honest frame |

Emitted verbatim for the index spelling:

```
  val setitem2 (seq: array int) (idx: int) (py_val: int) : unit
    requires { ((Array.length seq) > 0) }
    requires { (idx >= 0) }
    requires { (idx < (Array.length seq)) }
```

…and for the range spelling, the SAME four lines plus `writes   { seq }`.

## BOTH DIRECTIONS MEASURED

| arm | verdict |
|---|---|
| FALSE fact `ensures \result == 7` (index spelling) | **PROVES** |
| TRUE fact `ensures \result == 5` (index spelling)  | FAILS (`Unknown`) |

So the model is wrong in the SILENT direction: it proves what Python contradicts and refuses what
Python does. That is the unsound direction, not a noisy one.

## CPYTHON GROUND TRUTH

```
CPython d([7,7,7]) = 5 | a after = [5, 7, 7]
```
PyCSL proves `\result == 7`.

## IT SHIPS — THE EXPLOIT NEEDS NO HAND-WRITTEN STUB

`src/pycsl_lib/oper/__init__.py:175` ships exactly this shape:

```python
#@ requires \length(seq) > 0
#@ requires idx >= 0
#@ requires idx < \length(seq)
#@ assigns seq[idx]
def setitem(seq: list, idx: int, val: int) -> None:
    seq[idx] = val
```

`frontend/ir_resolve.py:201` stamps every imported function `func["trusted"] = True`, so an
ordinary user program gets the pure `val` with no `\trusted` marker of its own anywhere in sight:

```python
from pycsl_lib.oper import setitem

#@ requires \length(a) > 0
#@ requires a[0] == 7
#@ ensures \result == 7
def d(a: list) -> int:
    setitem(a, 0, 5)
    return a[0]
```
→ `[+] Verification SUCCESS! All contracts formally proven.`  CPython returns **5**.

## WHY THE #98 OBSERVER DID NOT CATCH IT — AND THE LESSON

Route #98's co-landing half exists *precisely* to stop a bodyless `val` silently losing its frame,
and its refusal message even names routes #96 and #98. It is keyed on `a.get("type") !=
"AssignsRegion"`. So the observer covers ONE of the THREE spellings of "this stub writes through a
parameter", and the one it does not cover is the one the standard library ships.

>>> **A REFUSAL INSTALLED TO OBSERVE A RESIDUE IS KEYED ON THE SPELLING ITS AUTHOR WAS LOOKING AT.
>>> THE OBLIGATION IS ABOUT THE *PATH BEING WRITTEN*; THE GUARD WAS WRITTEN ABOUT THE *NODE TYPE
>>> THAT HAPPENED TO CARRY IT*.** This is ranked generator #9 ("a confinement check keyed on the
>>> SYNTACTIC SHAPE of a write target enumerates the shapes its author happened to picture — key it
>>> on the PATH being written") landing on the campaign's own hardening.

ORDER: **1** (first-order). The `Subscript` spelling was unframed BEFORE routes #96/#98 and after
them; the campaign's repairs neither introduced nor widened it. Recorded as first-order deliberately
— inflating the second-order column would corrupt the metric the campaign steers by. What IS
campaign-shaped is the *false sense of coverage*: #98 installed the observer and covered one third
of the population.

## THE REPAIR, SCOPED (NOT YET LANDED)

Third collector arm over `assigns_list` for `{"type": "Subscript"}`, resolving the subscript BASE
(walking `value` down through nested `Subscript`/`Attribute`/`FieldGet` to a `Var`), then:
  - base is an array PARAMETER of the emitted signature → append `whyml_ident(base)` to
    `region_targets` (route #98's name-space rule applies IN FULL — compare in the EMITTED name
    space, never the source one);
  - base is `self.<f>` / `<global>.<f>` → it is a field target, route it to `field_targets`;
  - otherwise → append to `_unframed_regions` so the EXISTING #98 refusal fires.

**PREDICT BEFORE SWEEPING.** `#@ assigns <x>[<i>]` on a bodyless val is the population; census it
first. Expect HONEST FAILURES: `pycsl_lib` stubs that start telling the truth about their frames can
legitimately break callers that were relying on the pure `val`, and that cost is the finding, not a
reason to narrow the repair. Note `src/pycsl_lib/oper/__init__.py:175` is itself in the population.

**CO-LANDING HALF (do not skip):** a bare `#@ assigns g` on a bodyless val emits IR `{"type":
"Var"}` — a FOURTH spelling, matching neither loop and not reaching `_unframed_regions` either.
Census candidate 8 of the same sweep is a FIFTH carrier: `Module5_IREmitter.py:5882` flattens all
`#@ assigns` clauses into one list, so a stray `#@ assigns \nothing` beside a real target makes
`nothings` non-empty and drops the whole `writes` clause silently at `:3513`.

## REPRODUCE

```
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
python3 src/pycsl/pycsl.py <exploit.py> --import-path src --memory-model hoare
# add --no-proof --keep-mlw to read the emitted `val` and see the missing `writes`
```

## REOPENING / CLOSING CONDITION

CLOSED when the index spelling emits `writes { seq }` (or is refused), the true/false arms swap
verdicts, and a corpus witness pins it. This route REOPENS if any future change keys a frame
collector on a node type rather than on the resolved write path.
