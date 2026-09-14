# ROUTE #108 — a callee's raise inside a try's `else:` block is CAUGHT by that same try,
# and is ALSO dropped from the enclosing function's `raises` summary

**Status: FOUND, REPRODUCED, EXPLOIT DIRECTION MEASURED. Repair NOT yet landed.**
**Severity: SEV-1.** Companion to route #107 and the OPPOSITE direction of the same code:
#107 is the block being DELETED, #108 is the block being SPLICED WHERE PYTHON DOES NOT PUT IT.

## PYTHON'S RULE

In `try: B except E: H else: O`, an exception raised in `O` is **NOT** caught by this try's
own handlers. It propagates out of the function.

## THE MECHANISM, quoted

1. `stmt_control_flow.py:1809-1810` appends the lowered `else` text to `body_str`, and
   `:1830` wraps `body_str` as the `try` region — so the else runs **inside** the try.
   A raise arriving through a callee's `#@ raises` clause leaves **no literal `raise`** in the
   lowered text (the call lowers to a plain application), so the substring guard permits the
   splice.
2. `stmt_control_flow.py:1860-1861` adds the handler's own base tag **unconditionally**:
   ```
   1860                    candidates = [base] + [
   1861                        e for e in body_raised if handler_catches(base, e)]
   ```
   so `with ValueError -> …` is live regardless of what the try BODY can raise, and it
   catches the else's exception.
3. `_callee_raised_in` (`stmt_control_flow.py:1671-1683`) recurses into a `Try`'s `body` and
   `handlers` and then `continue`s — **it never visits `orelse`**. So the `raises` summary
   `functions.py:6778` computes for the enclosing function OMITS the exception as well.

Defect 3 is why this SURVIVES the route #100 → #105 repair chain: that chain fixed the
RECEIVER KEY used to look a callee's raises set up. Here the key resolves perfectly and
**the set itself is empty**, so `_wrap_call_with_callee_raises_assert` has nothing to assert
and returns `inner` untouched. *A repair that corrects a lookup cannot help when the thing
looked up is what is wrong.*

## EXPLOIT MEASURED at HEAD `113f38a7` — `b_catch.py`

```python
#@ raises ValueError when x0 < 0
#@ ensures \result >= 0
def boom(x0: int) -> int:
    if x0 < 0:
        raise ValueError("neg")
    return x0

#@ assigns \nothing
def wrapper(k: int) -> int:
    y = 0
    try:
        y = 1
    except ValueError:
        y = 9
    else:
        boom(k)
    return y

#@ no_exception ValueError
def caller(k: int) -> int:
    return wrapper(k)
```

`[+] Verification SUCCESS! All contracts formally proven.` (rc=0.)
CPython `caller(-1)` **RAISES ValueError**.

The callee is named `boom` precisely so that its name contributes no `raise` substring and
route #107's deletion cannot be what fires. The emitted `wrapper`, read in full, shows the
else spliced INSIDE the try:

```
  let wrapper (k: int) : int
  =
    let y = ref 0 in
    y := 0;
    try
      y := 1;
      let _ = (boom k) in ()
    with ValueError ->
      y := 9
    end;
    !y
```

## AN AUDIT-SIDE BLIND SPOT OF THE SAME ROOT CAUSE

`bin/check-dropped-mutation.py:384` classifies this exact shape as safe, with a why-string
that is a false claim:

```
384            elif node.orelse and not node.finalbody and not _jumps_out(node.orelse):
385                bucket, why = "HANDLED", "`try/else`, else cannot raise — appended to the try body"
```

`_jumps_out` is again statement-KIND-only. So the ratchet counts a raising-call else as
HANDLED — green by construction. **A control is a measurement about the operation it ran,
never a theorem about the type** (generator #3), and here the control encodes the very
assumption under test.

## ADJACENT, SAME ROOT CAUSE, NOT YET PROBED

`_try_reaches_assert` in `src/pycsl/frontend/desugar.py` scans `for _stmt in node.body` only,
so ROUTE #16's `assert`-inside-a-catching-try fence is likewise blind to an `assert` written
in the `else` block. Logged as a candidate, NOT as a finding — it has not been run.

## REPAIR SKETCH (to be RE-DERIVED before landing, per the #95 rule)

`orelse` must be lowered as a SIBLING of the try/except construct, not inside it, so that
Python's scoping is the emitted scoping; and `_callee_raised_in` must visit `orelse`. Landing
only the second half would be worse than nothing: the summary would then be honest while the
local catch stayed wrong. See route #107 — the two directions must be repaired together.
