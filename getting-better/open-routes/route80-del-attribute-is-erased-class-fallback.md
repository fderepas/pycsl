# ROUTE #80 — `del obj.attr` IS ERASED, AND A CLASS-ATTRIBUTE FALLBACK MAKES IT TOTAL

**STATUS: FOUND 2026-09-11 (gen #8). CLOSED AND FULLY GATED 2026-09-12 (gen #9).**

**CLASS: the #69 class** — a FALSE POSTCONDITION about ordinary, TOTAL Python. No
`no_exception`, no opt-in.

**THIS IS ROUTE #77's RESIDUE (a), UPGRADED BY MEASUREMENT.** #77 recorded `del obj.attr` and
`del name` as the *lower-value* half of its erasure: both are erased to `{"stmt": "Pass"}`, but
reading the deleted binding afterwards RAISES in CPython (`UnboundLocalError` /
`AttributeError`), so the program is not total and the value-differential plane rules it OUT OF
SCOPE. **That reasoning is correct for `del name` and WRONG for `del obj.attr`**, because Python
attribute lookup falls back to the CLASS attribute when the instance attribute is gone. The
program then runs to completion and returns a *different* value.

## THE EXPLOIT

```python
class C:
    x: int = 5                       # class attribute — the fallback
    def __init__(self) -> None:
        self.x = 10                  # instance attribute shadows it

#@ ensures \result == 10
def f() -> int:
    c = C()
    del c.x                          # removes the INSTANCE attribute only
    return c.x                       # falls back to the CLASS attribute
```

    CPython:  5
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

## BOTH DIRECTIONS, MEASURED

| driver | claim | CPython | PyCSL |
|--------|-------|---------|-------|
| k04 | `\result == 10` | **5** | **PROVED** ❌ |
| k04 twin | `\result == 5` | 5 | refused (Unknown) |

The true twin failing is what makes it a route and not a gap.

## THE MECHANISM

The same site as route #77: `frontend/Module5_IREmitter.py::_py_stmt_delete` appends
`{"stmt": "Pass"}` for any non-Subscript target, under the comment *"`del name` / `del obj.attr`
(rebinding / attribute delete) — stays the unmodelled no-op it always was."* #77's repair closed
the SUBSCRIPT-with-slice arm only; this arm is untouched and still erases.

**THE LESSON THIS SHARPENS.** #77 banked *"a prose carve-out upstream of a guard is a route with
a signpost on it"*. #80 adds the sharper form: **when a residue is filed as "out of scope because
the program raises", that classification is itself a claim about Python, and it must be probed
rather than reasoned about.** One language feature — class-attribute fallback — turned a
non-total residue into a total route. The whole `del name` / `del obj.attr` family was written
off in one sentence; half of it was live.

## CLOSED — THE REPAIR, AND WHAT IT COST

Refused at the same site as #77's slice arm (`Module5_IREmitter._py_stmt_delete`), diagnostic
code `PYCSL-M5-ATTR-DELETE-UNMODELLED`. `del name` stays the unmodelled no-op and is safe there
ONLY because a later read raises `UnboundLocalError` — that reasoning is now written down at the
site, since assuming it silently is what produced this route.

**TWO CARRIERS GEN #8 DID NOT HAVE, BOTH MEASURED IN BOTH DIRECTIONS BEFORE THE REPAIR:**

| carrier | claim | CPython | PyCSL |
|---------|-------|---------|-------|
| arithmetic `c.x - 5` | `\result == 5` | **0** | **PROVED** |
| arithmetic, TRUE twin | `\result == 0` | 0 | refused |
| `requires` discharge `g(c.x)` under `requires v == 10` | — | runtime v is **5** | **PROVED** |
| `requires` discharge, TRUE twin | `requires v == 5` | v is 5 | refused |

The third is the ESCALATION: a callee's precondition is discharged from a stale value the caller
never establishes, so the callee's own proof is sound relative to a `requires` that is FALSE at
runtime and the unsoundness is LAUNDERED THROUGH A CORRECT PROOF. The arithmetic carrier matters
separately because it shows the defect is not an artefact of a literal-equality clause being
folded away — the stale field flows into ordinary integer arithmetic.

**BLAST RADIUS: ZERO, MEASURED.** An AST census over `test-suite/corpus/`, `src/self-annotate/`,
`src/pycsl/` and `src/pycsl_lib/` — **3636 files parsed** — found **0 attribute deletes**, 2
`del name` (out of scope) and 19 subscript forms (already handled). The guard only RAISES or
FALLS THROUGH and never alters emitted text, so it is byte-inert BY CONSTRUCTION.

**GATES, ALL GREEN:**
* **byte-inert over BOTH corpora** against a pre-repair worktree baseline at `a5198ee9`
  (`.venv` symlinked into the worktree, gen #8's lesson (q)): pycsl-ref **971/971**, python-ref
  **2204/2204**, **0 MOVED / 0 GONE / 0 APPEARED**, the three new witnesses declared
  `--new-source`.
* mirror-sync rc=0 (**887 un-trusted mirror functions verbatim**); mirror **type-only 53/53,
  0 ILL-TYPED** (rule (j)).
* **IR conformance 38/38 core + 38/38 front-end, 0 MISMATCH**, determinism 10/10 — run
  deliberately (rule (m)).
* **whole-file Module5 mirror re-proof `w59a_m5ir` rc=0 — 2111 goals Valid, ZERO unproved**,
  56 min wall. It proved the NEW model, because the bespoke lowering was edited BEFORE the proof
  was launched.
* **34/34 planes.**
* **reference suite 3328/3347, ZERO XPASS**, rc=1 (the baseline condition), and the 19-failure
  set is **BYTE-IDENTICAL** to gen #8's `suite58_run3` — diffed, not eyeballed, and the
  comparison was verified NON-VACUOUS (19 lines on each side) after a first extraction pattern
  silently matched zero lines on both sides and would have reported a green "identical".

**THE COST SHAPE, BECAUSE IT IS THE REUSABLE PART.** `_py_stmt_delete` is an UN-trusted VERIFIED
BODY PORT in the mirror with a BESPOKE Module6 lowering, so this repair owed all three of: a
verbatim mirror body sync, a co-ordinated edit to
`module6_whyml/functions.py::_emit_py_stmt_delete_bespoke`, and a 56-minute whole-file re-proof.
Contrast #78, whose method was a `#@ \trusted` bodyless stub and cost nothing. **Grep the mirror
for the method and check for `#@ \trusted` BEFORE scoping any Module-5 repair** — it is the
difference between a ten-minute close and a multi-hour one.

**`check-bespoke-model-drift` FIRED, AND WAS DISCHARGED BY EVIDENCE RATHER THAN BY RE-BASELINING.**
The emitted mirror WhyML was diffed against a pre-repair emission: the WHOLE-FILE diff is
**exactly three lines** — the `is_attribute` raise arm inside `_py_stmt_delete`'s loop — with the
contract, the loop invariant, the variant and the `SDelSubscript` arm untouched. Only after the
proof returned rc=0 on that new model was `--update` run, and its fingerprint diff is exactly
one, with the other 26 hand-synthesized models unchanged. This is rule (k)'s notification-gate
distinction: **the test is whether you can SHOW THE ARTIFACT MOVED.**

### THE ORIGINAL REPAIR NOTE

Refuse `del <attribute>` at the same site as #77's slice arm. `del name` stays a recorded
residue (it genuinely raises; it is route **#71**'s missing-obligation class, not this one).

Blast radius was measured before building and came back ZERO (see above).
`src/pycsl_lib/json/encoder.py:20` has a bare `del i` (the `del name` form, out of scope for
this repair), and the subscript forms elsewhere are already handled.

## WITNESSES

Corpus: `test-suite/corpus/pycsl-reference/1201_route80_del_attribute_refused.py`,
`1202_route80_del_attribute_arith_refused.py`,
`1203_route80_del_attribute_discharges_requires_refused.py` — each verified to refuse WITH THE
ATTRIBUTE-DELETE MESSAGE, not merely to refuse (a witness that refuses for the wrong reason is
vacuous). Originals: `scratchpad/w58/c/k04_del_attr_class_fallback.py`, `k04_twin.py`.

## RESIDUE AND REOPENING CONDITIONS

* **`del name` remains an unmodelled no-op.** It is safe TODAY only because a later read raises
  `UnboundLocalError`, which keeps the program non-total and out of the value plane's scope.
  **REOPENING: any change that makes a deleted local's later read TOTAL** — a module-global
  fallback, a class-scope fallback, or a `del` of a name that also exists as a builtin — turns
  it into exactly this route. #80 exists because that same reasoning was applied to
  `del obj.attr` without being probed.
* The repair refuses ALL attribute deletes, including those with no class-level fallback (where
  CPython would raise `AttributeError`). That is deliberately conservative and costs nothing at
  a measured blast radius of zero; if a user ever needs the raising form, it is route #71's
  missing-obligation class, not this one.
