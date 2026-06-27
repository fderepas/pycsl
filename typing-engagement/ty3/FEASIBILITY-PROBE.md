# TY3 Feasibility Probe — Monomorphization

**Probe-agent verdict:** 🟢 **GREEN**
**Date:** 2026-06-27
**Engagement:** PyCSL typing, TY3 tier (typing-global-impl.md §2, §5 step 4).

---

## 1. The claim under test

From `typing-global-impl.md` §5 step 4 and §2 (probe-agent role):

> **TY3 feasibility probe:** prove that a SINGLE monomorphized instantiation
> (e.g. `Stack[int]`) discharges end-to-end before any collection/emission
> machinery is built (the "prove the rebind first" discipline).

The monomorphization approach (per `docs/typing-global-overview.md`): for each
concrete instantiation `Stack[int]`, emit ONE name-mangled specialized WhyML
`let`/`val` with the TypeVar `T` substituted by the concrete type. The probe's
question is narrow: **does PyCSL *already* prove a hand-monomorphized version**
(where `T=int` is substituted by hand)? If yes, the future collection machinery
is automation over a path that already proves — the rebind is sound.

## 2. Probe setup

Three artefacts in this directory:

| File | Role |
|---|---|
| `probe_generic_stack.py` | Step 1 — the generic `class Stack[T]` (PEP 695). Confirms the front-end (commit 8335eede) **parses** generics. |
| `probe_stack_int.py` | Steps 2–4 — the hand-monomorphized `class Stack_int` (the exact WhyML the future machinery would emit for `Stack[int]`) plus a driver whose contract depends on the int instantiation. |

### Step 1 — generic parses

`probe_generic_stack.py` is a literal `class Stack[T]: ...` with `push`/`pop`.
Run with `pycsl --no-proof`:

```
[*] Parsing and Semantic Analysis for 'probe_generic_stack.py'...
[*] Memory model: hoare
[level] L1 ✓  L2 ✓  L3-tc ✗   ← unbound `iter_length` (a list-length lowering gap, NOT a generics gap)
```

The PEP 695 grammar productions land and the front-end accepts `class Stack[T]`
and the `Stack[int]` subscript expression. The L3-tc failure is a pre-existing
list-modelling gap (`len(list)` lowers to an unbound `iter_length` symbol) that
is orthogonal to monomorphization and tracked separately. To isolate the
monomorphization question, the hand-monomorphized driver below uses the
canonical PyCSL array style (`\length(self._items)`, pre-allocated array, index
manipulation) — exactly the shape the monomorphizer would lower `Stack[int]`
to once the list-length helper is wired.

### Step 2 — hand-monomorphized driver (`probe_stack_int.py`)

The future monomorphizer, given `Stack[int]`, would emit:

- a `type stack_int = { mutable _items: array int; mutable _size: int }`
  (TypeVar `T` → `int` substituted into the field type), and
- `let stack_int__push (self: stack_int) (v: int) : unit` and
  `let stack_int__pop (self: stack_int) : int` — name-mangled, `T` substituted.

`probe_stack_int.py` is precisely that, written by hand:

```python
#@ class invariant self._size >= 0 and self._size <= \length(self._items)
class Stack_int:
    def __init__(self):
        self._items = [0, 0, 0, 0, 0, 0, 0, 0]
        self._size = 0

    #@ requires self._size < \length(self._items)
    #@ ensures self._size == \old(self._size) + 1
    #@ ensures self._items[\old(self._size)] == v
    #@ assigns self._items[self._size], self._size
    def push(self, v: int) -> None:
        self._items[self._size] = v
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ ensures \result == \old(self._items[self._size - 1])
    #@ assigns self._size
    def pop(self) -> int:
        self._size = self._size - 1
        return self._items[self._size]

if __name__ == "__main__":
    s = Stack_int()
    s.push(7)
    r = s.pop()
    #@ assert r == 7
```

The driver's contract `assert r == 7` is exactly the per-instantiation theorem
the overview predicts: the `int` specialization carries a concrete `int`
postcondition (`\result == \old(self._items[self._size - 1])`), which the
generic `T` version could not state.

## 3. pycsl result

```
$ source .venv/bin/activate && python3 src/pycsl/pycsl.py \
      typing-engagement/ty3/probe_stack_int.py
[*] Parsing and Semantic Analysis for 'probe_stack_int.py'...
[*] Memory model: hoare
[*] Running Proof Engine (provers: Alt-Ergo,2.6.2, → Z3,4.13.3,)...

Sub-goal type invariant of goal stack_int__pop'vc.        → Valid
Sub-goal postcondition of goal stack_int__pop'vc.          → Valid
Sub-goal postcondition of goal stack_int__pop'vc.          → Valid
Sub-goal index in array bounds of goal stack_int__push'vc. → Valid
Sub-goal type invariant of goal stack_int__push'vc.         → Valid
Sub-goal postcondition of goal stack_int__push'vc.          → Valid
Sub-goal postcondition of goal stack_int__push'vc.          → Valid
... (3 more VCs incl. the driver `assert r == 7`)

[+] Verification SUCCESS! All contracts formally proven.
```

**10 / 10 VCs Valid** (Alt-Ergo 2.6.2). The driver `assert r == 7` discharges;
the per-instantiation int postcondition on `pop` discharges; the class
invariant and bounds obligations on `push`/`pop` discharge.

## 4. Verdict

🟢 **GREEN — the monomorphization approach is feasible.**

A single hand-monomorphized instantiation (`Stack[int]` → `Stack_int`, with
`T` substituted by `int` in field types, method signatures, and contracts)
discharges end-to-end through the *existing* PyCSL pipeline. The
collection/emission machinery the TY3 tier will build — collect concrete
instantiations, emit one name-mangled specialized `let`/`val` per
instantiation with substituted contracts — is **automation over a path that
already proves**. The rebind is sound; the machinery is unblocked.

## 5. Caveats (not blockers)

- The **generic** `class Stack[T]` itself does not yet reach L3-tc because of
  a pre-existing list-modelling gap (`len(list)` → unbound `iter_length`). This
  is unrelated to monomorphization — the hand-monomorphized driver sidesteps it
  by using `\length(self._items)` on an array, which is the lowering shape the
  monomorphizer will emit anyway. Closing the `iter_length` gap is TY1/list-
  modelling work, not a TY3 blocker.
- The probe covered ONE instantiation (`int`). The cost probe (separate probe-
  agent task per the overview) will measure per-instantiation VC volume and
  any relational/doubled-state E-matching cost before the machinery is scaled
  to N instantiations.
- The probe did NOT build the collection/emission machinery — that is the
  core-agent's TY3 work, now unblocked by this verdict.

## 6. Artefacts

- `probe_generic_stack.py` — PEP 695 generic (parses; L3-tc blocked by the
  unrelated `iter_length` list gap).
- `probe_stack_int.py` — hand-monomorphized `Stack[int]`; **10/10 VCs Valid**.
