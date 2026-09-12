# ROUTE #88 — A SCALAR FIELD'S **LAST** STORE IN `__init__` LOSES TO ITS **FIRST**, AND AN `AugAssign` TO A FIELD IS INVISIBLE

**STATUS: FOUND AND REPRODUCED 2026-09-12 (gen #11). BOTH DIRECTIONS MEASURED ON SIX
CARRIERS, WITH FOUR CONTROLS THAT BOUND IT — TWO OF THEM SHOWING THE COLLECTION ARMS ARE
ALREADY LAST-WINS AND FAITHFUL.**

**CLASS: the #69 class** — a FALSE POSTCONDITION about ordinary, TOTAL Python. No
`no_exception`, no opt-in, no `\trusted`.

## THE EXPLOIT

```python
class C:
    n: int
    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 1
        self.n = 2

#@ ensures \result == 1
def f() -> int:
    c = C()
    return c.n
```

    CPython:  2
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

The TRUE twin (`\result == 2`) is REFUSED. The emitted WhyML is literally `let c = { n = 1 } in c.n`.

## THE CARRIER TABLE — BOTH DIRECTIONS

| carrier | shape | claim | CPython | PyCSL |
|---------|-------|-------|---------|-------|
| c1 | `self.n = 1` then `self.n = 2` | `\result == 1` | **2** | **PROVED** ❌ |
| c1 twin | same | `\result == 2` | 2 | refused |
| c7 | THREE literal stores `1;2;3` | `\result == 1` | **3** | **PROVED** ❌ |
| c4 | `self.n = k` then `self.n = 3` | `\result == 7` for `C(7)` | **3** | **PROVED** ❌ |
| c4 twin | same | `\result == 3` | 3 | refused |
| p3 | `self.n = 0` then `self.n += 5` (TOP-LEVEL AugAssign) | `\result == 0` | **5** | **PROVED** ❌ |
| c6 | `self.n = 0` then `if k > 0: self.n += 5` (NESTED AugAssign) | `\result == 0` | **5** | **PROVED** ❌ |
| c5 | **CROSS-CALL** — stale `1` discharges callee `requires m == 1` | runtime `m` is **2** | **PROVED** ❌ |

**c4 IS THE ONE THAT MATTERS MOST**, because it is the defect running in the OTHER
direction: there the model takes the *parameter-dependent* store and the real program takes
the *later literal*. So this is not "the emitter prefers literals"; it is "the emitter has no
notion of store ORDER at all". c5 is the escalation: the stale value crosses the call graph
and discharges a precondition the program never establishes.

## THE CONTROLS — AND THEY BOUND IT TIGHTLY

| control | shape | verdict |
|---------|-------|---------|
| ctl_single | ONE store `self.n = 2` | `== 2` PROVED, faithful ✔ |
| c3 | `self.n = 1` then `self.n = k` | `== 1` refused, `== 7` PROVED — **FAITHFUL** ✔ |
| c9 | LIST field, `self.xs = [1,2]` then `[3,4]`, element read | `== 1` refused, `== 3` PROVED — **FAITHFUL** ✔ |
| c10 | DICT field, `self.d = {1:5}` then `{1:9}` | `== 5` refused ✔ |

**c9/c10 ARE THE IMPORTANT CONTROLS: THE COLLECTION ARMS ARE ALREADY LAST-WINS.** Route
#85's dict/set capture and route #87's list capture both key a dict by field name, so a later
literal simply overwrites the earlier one and the model is right. **Only the SCALAR
`field_defaults` path is first-wins.** That is what makes this route's blast radius small,
and it is why probing the collection shape first would have produced a false "no finding".

## THE MECHANISM — TWO FUNCTIONS DISAGREE ABOUT WHICH STORE IS THE UNIT

1. `Module5_IREmitter._collect_class_fields` walks `__init__` and guards every store with
   **`target.attr not in field_names_seen`**. The first store to a field decides its type AND
   its `field_defaults` entry; every LATER store is skipped outright.
2. `module5/construction_synth.py::_collect_init_construction` **APPENDS** to `init_body` for
   every top-level param-dependent store, so an EARLIER param store survives a LATER literal
   one (carrier c4).
3. Neither path looks at `ast.AugAssign` at all, so `self.n += 5` is invisible — **including
   nested inside control flow, which means it is also a SURVIVOR OF ROUTE #83's REPAIR.**
   #83's `_init_unknown` walk tests only `ast.Assign` / `ast.AnnAssign`, so a nested
   *augmented* store does not mark the field unknown (carrier c6). Generator 2 in action: a
   carrier that survives a landed repair is a second route, not a failed repair.

**THE SHARPEST PART:** route #79's own comment in `construction_synth.py` already states the
rule — *"THE UNIT IS THE FIELD'S **LAST** TOP-LEVEL STORE, NOT THE STORE. A field written
twice must be judged by the write that decides its value"* — and `_last79` implements it
correctly for the *unknown-marking* decision. The VALUE-supplying paths never got the same
treatment. **A RULE STATED IN A COMMENT IS NOT A RULE THE OTHER FUNCTIONS OBEY.**

## HOW IT WAS FOUND

Generator 1 from gen #10's handoff, applied to the `__init__` field-capture family that has
now yielded six routes (#79, #82, #83, #85, #87 and this one): every one of those controls
ran exactly ONE store per field. **"Which single operation did that control actually run?"
— it ran a constructor that writes each field ONCE.** The second store is a different
operation and nobody had run it. First probe batch of the generation, four files, one hit.
