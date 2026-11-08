# ROUTE #88 — A SCALAR FIELD'S **LAST** STORE IN `__init__` LOSES TO ITS **FIRST**, AND AN `AugAssign` TO A FIELD IS INVISIBLE

**STATUS: FOUND, REPRODUCED, **CLOSED AND FULLY GATED** 2026-09-12 (gen #11) — AND CLOSED
FAITHFULLY ON THREE OF ITS SIX CARRIERS. BOTH DIRECTIONS MEASURED, FOUR CONTROLS BOUNDING IT.**

> ## CLOSING EVIDENCE — every plane re-reproduced at HEAD, none inherited
>
> | gate | verdict |
> |------|---------|
> | soundness planes | **34/34 green**, rc=0 (`--slow`), `proofs49/w61_planes_route88.log` |
> | byte-diff, pycsl-reference | 1003 baseline / 1003 candidate, **7 MOVED = a SUBSET of this route's own 8 witnesses, ZERO pre-existing files**, 0 GONE, 0 APPEARED |
> | byte-diff, python-reference | **2203/2203 BYTE-IDENTICAL**, SOURCES sets equal (2217 vs 2217) |
> | byte-diff, MIRROR | **53/53 BYTE-IDENTICAL** |
> | zero-byte check | **0 / 0 on BOTH sides of all three sweeps** (/tmp 15–24% throughout) |
> | IR conformance | **38/38 core + 38/38 front-end**, 0 MISMATCH, determinism 10/10, NO golden re-blessed |
> | fidelity | rc=0, **887 verbatim**, no mirror sync and no whole-file re-proof owed |
> | mirror-coverage ratchet | **549 KEPT**, not re-baselined |
> | value-differential | **50 drivers** (grown 45 → 50), 23 AGREE all prove / 27 DISAGREE all refused, rc=0 |
> | reference suite | **3361/3379, ZERO XPASS, rc=1**; failure set **18 vs 18 BYTE-IDENTICAL**, both populations asserted |
> | metric | markers **459** · grep 484 · offset 25 · unattached 0 — UNCHANGED |
>
> **THE WITNESS THAT DID *NOT* MOVE IS THE EVIDENCE.** 1234 — the single-store over-breadth
> control — is byte-identical across the diff, which is the census made executable: a
> constructor that writes each field once must emit exactly what it emitted before, and the
> census found that EVERY real constructor in corpus, mirror, `src/pycsl` and `src/pycsl_lib`
> is that shape. The seven that moved are the seven that had to.
>
> **I CAUGHT A VACUITY TRAP IN MY OWN GATE.** The first version of the "moved set == my
> witnesses" assertion scraped `byte-diff-compare.py`'s STDOUT, but it writes MOVED lines to
> STDERR — so it compared against an EMPTY moved set and passed vacuously. The rerun captures
> both streams and asserts BOTH population sizes (7 and 8) before believing the answer.
> **ALWAYS ASSERT A DIFF'S POPULATION SIZE BEFORE BELIEVING IT — INCLUDING WHEN THE DIFF IS
> YOUR OWN.**
>
> **THE SUITE VERDICT PER WITNESS**, which is what makes the close non-vacuous:
> 1229, 1231, 1234 **PASS** (two completeness gains and the over-breadth bound);
> 1228, 1230, 1232, 1233, 1235 **XFAIL** (every false claim now refused); **ZERO XPASS**.

## THE REPAIR — THREE ADDITIVE EDITS, AND THE CENSUS THAT PRICES THEM

**(A)** `Module5_IREmitter._collect_class_fields` gains a TOP-LEVEL-ONLY, source-ordered second
pass that overrides `field_defaults` from a field's LAST store and POPS the entry when that
store is inexpressible. **(B)** `construction_synth._collect_init_construction`'s capture loop
is keyed by FIELD and last-wins; a superseding store sets the slot to `None` rather than
popping it, so a field's position in `init_body` stays at its FIRST capture and a single-store
constructor emits byte-identically. **(C)** a `self.<f> op= ...` anywhere in `__init__` marks
the field `_init_unknown` → `(any int)`.

**NESTED STORES ARE DELIBERATELY LEFT TO ROUTE #83.** That is what keeps (A) inert over the
five real multi-store sites, every one of which is one-top-level-plus-one-nested — and three
of those live in `src/pycsl_lib`, a tree NO byte-diff corpus contains, so the gate that prices
them is the reference SUITE (route #83's lesson). *(That decision also left route #89 standing,
which is recorded separately and honestly: the collection arms of the nested case are outside
#83's fence.)*

**THE CENSUS:** ZERO fields with two top-level stores and ZERO `AugAssign`-to-field sites
across 1167 pycsl-reference + 2217 python-reference files, the 74-file mirror, `src/pycsl` and
`src/pycsl_lib` — and the census was proved NON-VACUOUS by re-running it against my own probe
directory, where it finds 13 and 2.

## WHAT THE REPAIR COULD AND COULD NOT RECOVER

Three carriers close **FAITHFULLY** — the true twin now PROVES where it was refused (two
literal stores, three literal stores, param-then-literal). Two close **UNCONSTRAINED**: an
augmented store is not reducible to a record literal, so both directions refuse, and that is
recorded rather than hidden. **PREFER A FAITHFUL CAPTURE WHEREVER THE INFORMATION EXISTS AND
FALL BACK TO UNCONSTRAINED ONLY WHERE IT GENUINELY DOES NOT** — this route contains both halves
side by side, like #85 did.

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
