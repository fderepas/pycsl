# challenging-the-plan.md — probing the A/B/C/D plan before committing to sub-specs

**Date:** 2026-06-08
**Status:** Probe report (two experiments run; no production code changed)
**Subject:** `opaque-and-refine.md` proposes four tracks (A lemma-extraction, B opaque-on-export,
C data-refinement, D Rocq/Lean bridge) to put the inode round-trip into the os model without the
proof-cost bloat. Its recommended near-term sequencing is **"A now (cheapest) → C as the principled
target."** Before authoring four detailed sub-specs, I challenged that sequencing with two
quick experiments. **Both premises failed.** This document presents exactly what was probed and what
I observed.

---

## 0. Why probe at all

The whole `try.md` arc established that the hard facts here — the SMT array-state wall, the proof-cost
ceiling, the module-granularity bloat — were only understood by **running the transpiler**, never by
reasoning. `opaque-and-refine.md` §4/§5 (refinement dissolves the wall; HAPPY makes the coupling
invariant affordable) and §6 (A is cheapest) are **reasoning that had not been run.** A probe is one
small input file plus one `pycsl.py` invocation; a sub-spec is hours. So: probe first.

Two claims were tested:
- **A-claim:** "0657/0658 *are* that lemma; the missing piece is citing it inside a syscall proof
  without putting it on the stub" → A keeps the exported contract light, states the round-trip as a
  separate `#@ lemma`, **cheapest, little new tool work.**
- **C-claim:** a ghost abstract inode + coupling invariant lets syscalls reason abstractly; refinement
  **dissolves** wall #3; HAPPY confines each write so the coupling invariant stays affordable.

---

## 1. The A-probe — "is the round-trip lemma a cheap, standalone escape?"

### 1.1 What was probed
Whether the round-trip can be a `#@ lemma` (a separately-proved, citable fact) **while the pack
function keeps a LIGHT exported contract** — which is the only way A avoids the bloat (the bloat is the
rich contract riding the import stub into every call site). Two minimal files, identical except for
pack16's contract.

**Test 1 — pack16 carries its RICH (value) contract; round-trip stated as a `#@ lemma`:**
```python
#@ requires 0 <= a and a <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures \result[0] * 256 + \result[1] == a          # ← RICH value ensures
def pack16(a: int) -> list:
    return bytes([a // 256, a % 256])

#@ requires \valid(data, offset + 2) … 0 <= data[offset] <= 255 …
#@ ensures \result == data[offset] * 256 + data[offset + 1]
def unpack16(data: list, offset: int) -> int:
    return data[offset] * 256 + data[offset + 1]

#@ lemma
#@ requires 0 <= x and x <= 65535
#@ assigns \nothing
#@ ensures unpack16(pack16(x), 0) == x                  # ← the round-trip, as a quantified lemma
def rt_lemma(x: int) -> None:
    pass
```

**Test 2 — identical, except pack16's value ensures are REMOVED** (the light contract A wants to
export): drop the three `\result[...]` lines, keep `\length == 2`.

### 1.2 What I observed
```
A-probe 1 (RICH pack16  + round-trip lemma):  SUCCESS! All        ← the quantified lemma proves
A-probe 2 (LIGHT pack16 + round-trip lemma):  Verification FAILED ← no field-value info to compose from
```

### 1.3 Outcome
- The round-trip **lemma form works** — the quantified `∀x. unpack(pack(x)) == x` proves (Test 1), so
  the concern "maybe the quantified form re-hits the array-state wall" did **not** bite at the uint level.
- **BUT the lemma proves only because pack16 carries its rich value contract** (Test 2 fails the
  instant that contract is light). And pack16's rich contract is **exactly what rides the import stub
  into every call site** — the os bloat.
- Therefore **Track A cannot keep the exported contract light *and* prove the round-trip.** To have
  both, the rich contract must be **verified in the unit but hidden from importers** — which is
  **opacity = Track B**. **A reduces to B.** The doc's "A is cheapest, little new tool work" is wrong:
  there is no by-hand A that escapes the bloat without B's contract-narrowing-on-import.

---

## 2. The C-probe — "is the coupling invariant affordable through a confined write?"

### 2.1 What was probed
The smallest honest instance of the refinement: several inodes, each coupled to its disk slice by a
class invariant, and one write that touches a single inode — so the proof must show **the other
inodes' couplings are preserved by frame** (§5's per-write-over-the-whole-disk obligation, the affordability
risk I flagged). 8 inodes (uint16 each) in a 16-byte disk:

```python
#@ class invariant \length(self.disk) == 16
#@ class invariant self._v0 == self.disk[0] * 256 + self.disk[1]
#@ class invariant self._v1 == self.disk[2] * 256 + self.disk[3]
#@ … (self._v2 … self._v7, each coupling _v{n} to disk[2n], disk[2n+1]) …
class FS:
    def __init__(self) -> None:
        self.disk: list = [0] * 16
        self._v0: int = 0 …                              # _v0 … _v7

    #@ requires 0 <= val and val <= 65535
    #@ assigns self.disk, self._v0
    #@ ensures self._v0 == val
    def write0(self, val: int) -> None:
        self.disk[0] = val // 256                        # touches ONLY inode 0's slice
        self.disk[1] = val % 256
        self._v0 = val
```
Expected hard part: after `write0`, prove all 8 couplings — `_v0` by the div/mod identity, and
`_v1…_v7` **by frame** (disk[2..15] untouched). The affordability question: does that frame proof stay
cheap as the inode count / disk size grows?

### 2.2 What I observed
```
C-probe:  Verification FAILED   (in 2s — a genuine failure, NOT a timeout)
Why3 error:  File "…mlw", line 19, characters 26-39:
             unbound function or predicate symbol 'subscript_get'
```
Line 19 is a class-invariant line. The emitted invariant used `subscript_get` for `self.disk[n]`, and
that symbol is **unbound** in the type-invariant scope.

### 2.3 Outcome
- The affordability question was **never reached** — the coupling invariant **does not even compile.**
- Cause: **array-FIELD element access in a class invariant** (`self.disk[n]`) lowers to the opaque
  `subscript_get` (and isn't declared in the invariant's scope → "unbound"). This is the **L0 gap
  recurring in a new position.** L0 (commit `1a38500`) fixed `\result[i]` in contracts (a `Result`
  node) → `Array.get`; it did **not** cover array-field access inside a *class invariant*.
- Therefore **Track C is blocked on a tool prerequisite** before its central claim (refinement +
  HAPPY are affordable) can be tested at all. The coupling invariant `ginode[n] == unpack(disk[slice])`
  is the heart of refinement, and it is currently **inexpressible**.

---

## 3. What the probes changed about the plan

| Plan claim (`opaque-and-refine.md`) | Probe verdict |
|---|---|
| "A now — cheapest, little new tool work" | ✗ **A reduces to B.** The lemma needs the rich contract (A-probe 2 fails light); the rich contract bloats the import; only opacity (B) hides it. No cheap standalone A. |
| "C is the principled target (a refactor)" | ✗ **C is blocked earlier than the refactor.** Its coupling invariant can't be expressed — array-field access in a class invariant → unbound `subscript_get` (an L0-style tool gap). Affordability (the real risk) is **unreachable** until that's fixed. |
| "A now → C target → B if recurs → D" sequencing | ✗ **Inverted.** A needs B; C needs an L0′ tool fix *first*. Neither near-term track is cheap-and-validated as written. |

**The two prerequisites differ in size:**
- C's blocker is a **small, known-shape tool fix** — "array-field access in a class invariant →
  `Array.get`," the direct analogue of the L0 `Result`-node fix already shipped.
- A's blocker is **Track B itself** — contract narrowing on import, a real feature.

So the genuinely cheapest *validated-next-step* is **the L0′ class-invariant field-subscript fix**,
because it is small **and** it unblocks the C-probe's affordability test — which is the one open
question that decides whether the principled target (refinement) is even reachable.

## 4. Revised near-term path (probe-grounded)

1. **L0′ [TOOL] (small):** array-field element access in class invariants/contracts →
   `Array.get` (extend the L0 `Result`-node fix to `Attribute`/`FieldGet` objects in spec context).
   Gate: corpus byte-identical; the C-probe coupling invariant *compiles*. **(Concrete patch in §4.1.)**
2. **Re-run the C-probe (affordability):** with the coupling expressible, measure whether the frame
   proof (other inodes preserved) stays cheap as inode count grows — plain array-frame first, HAPPY if
   needed. **This is the decisive experiment for the whole refinement track.**
   - If affordable → **C is viable**; write `C-*.md` and pursue refinement.
   - If it blows up over the disk → refinement is *not* reachable without more (e.g. HAPPY is
     mandatory, or a different abstraction) — recorded honestly, and **B becomes the path** instead.
3. **B (opacity)** is the prerequisite for A *and* the general force-multiplier (every codec/serializer
   hits the same import-bloat). It is the larger feature; spec it once a recurrence beyond the inode
   case is confirmed (it will recur).
4. **D (Rocq/Lean)** remains the durability/opacity layer over A or C — never a substitute (`try.md`/
   `opaque-and-refine.md` §2): it does not solve the bloat, which is about *what propagates to call
   sites*, not *how a fact was established*.

## 4.1 The L0′ fix, concretely (root cause + patch)

The C-probe's `unbound subscript_get` is **not** a missing branch in the subscript handler — that
handler *already* has a field branch (`expressions.py:_handle_subscript`):

```python
# (existing) self.<field>[k] where the field is set/dict/array-typed
if not is_array and not is_dict and value.get("type") in ("Attribute", "FieldGet"):
    ft = self._field_type_of(value)
    if ft in ("set", "dict", "frozenset"):           is_dict = True
    elif ft in ("list", "tuple", "bytes", "bytearray"): is_array = True   # ← should fire for disk
```

**Root cause — `_field_type_of` returns `None` during class-invariant emission**, because that emission
never sets `_current_self_type`. In `preamble.py` (~872):

```python
if class_invs:
    self._in_spec = True
    self._emit_record_ctx = type_name          # set
    # self._current_self_type is NOT set here   ← the bug
    for inv in class_invs:
        out.append(f"    invariant {{ {self._expr_to_whyml(inv, set(), invariant_ctx=True)} }}")
    self._emit_record_ctx = None
    self._in_spec = False
```

and `_field_type_of` resolves a `self.<field>` only via `_current_self_type` (`types.py:_field_type_for`):

```python
cls = self._current_self_type          # ← None during class-invariant emission
if not cls:
    return None                        # ⇒ ft = None ⇒ is_array stays False ⇒ subscript_get
```

So `self.disk[n]` → `ft = None` → the field branch doesn't set `is_array` → fall-through to the opaque
`val subscript_get`, which is additionally **unbound** in the type-invariant scope.

**The patch (two small parts):**

1. **Set `_current_self_type` during class-invariant emission** (`preamble.py`, the `if class_invs:`
   block) so field types resolve:
   ```python
   if class_invs:
       self._in_spec = True
       self._emit_record_ctx = type_name
       _prev_self = self._current_self_type
       self._current_self_type = type_name        # ← L0′: so _field_type_of resolves self.<field>
       for inv in class_invs:
           out.append(f"    invariant {{ {self._expr_to_whyml(inv, set(), invariant_ctx=True)} }}")
       self._current_self_type = _prev_self        # restore
       self._emit_record_ctx = None
       self._in_spec = False
   ```
   (`type_name` is the whyml record name — exactly what `_field_type_for` matches against
   `info["whyml_name"]`.)

2. **For an array-field access in SPEC context, emit `Array.get` directly — no bounds-assert wrapper**
   (mirror the L0 `Result`-node early return; an invariant/`ensures` is a logic term and must not carry
   a runtime `assert`). In `_handle_subscript`, beside the existing L0 `Result` early-return:
   ```python
   # L0′: self.<array-field>[i] in a contract/invariant → Array.get (logic term, no assert wrapper)
   if (self._in_spec and value.get("type") in ("Attribute", "FieldGet")
           and self._field_type_of(value) in ("list", "tuple", "bytes", "bytearray")):
       return f"({value_str}[{index}])"
   ```
   (With part 1 in place, `_field_type_of(value)` now returns `"list"` for `self.disk`.)

**Gates:** corpus byte-identical (the new path fires only in spec context where the field's array type
is known; body reads and opaque cases are unchanged); the C-probe's coupling invariant compiles and
its `self.disk[n]` lowers to `self.disk[n]` (`Array.get`), not `subscript_get`. Only **then** is the
C-affordability re-probe (§4 step 2) meaningful.

**Why it's "small":** it is the *same shape* as the shipped L0 fix (`1a38500`) — recognise an
array-typed object in spec context and emit `Array.get` — extended from the `Result` node to
`Attribute`/`FieldGet`, plus the one-line `_current_self_type` set that makes the field type resolvable
in the invariant scope.

## 5. The meta-point

Both probes cost one file and one `pycsl.py` run each, and **both overturned a reasoned-but-unrun
premise** of a four-track plan — exactly as the leaf-first arc kept doing (L0 and the L2 arg-materialize
gaps were both invisible until generation was run). The lesson stands: **in this codebase, reason to
*design* the probe, then run the probe to decide the plan.** A/B/C/D are still the right *concepts*;
their *ordering and cost* are now corrected by evidence rather than estimated.

> **In one line:** A-probe — the round-trip lemma proves only with the rich pack contract, so **A
> reduces to B** (opacity is unavoidable); C-probe — the coupling invariant doesn't even compile
> (`self.disk[n]` in a class invariant → unbound `subscript_get`, an **L0-recurrence**), so **C's
> affordability is unreachable until a small L0′ tool fix lands.** Revised path: **L0′ → re-probe C
> affordability → C if green, else B.**
