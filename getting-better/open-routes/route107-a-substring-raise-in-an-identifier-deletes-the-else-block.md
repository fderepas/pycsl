# ROUTE #107 — a try's `else:` block is SILENTLY DELETED when its lowered text merely
# CONTAINS the substring `raise`, INCLUDING from an ordinary identifier's name

**Status: FOUND, REPRODUCED, BOTH DIRECTIONS MEASURED. Repair NOT yet landed.**
**Severity: SEV-1.** A false postcondition is PROVED, the trigger is a variable NAME, and
route #37's refusal — which exists precisely to stop a dropped `else` — does not fire.

## THE MECHANISM, quoted

`src/pycsl/module6_whyml/stmt_control_flow.py:1805-1810`

```
1805        _else = [s.to_dict() for s in stmt.orelse]
1806        if _else:
1807            _else_str = self._stmts_to_whyml(_else, local_refs, declared_refs.copy(),
1808                                             indent + "  ", in_loop)
1809            if _else_str.strip() and "raise" not in _else_str:
1810                body_str = body_str + ";\n" + _else_str
```

The test is a **Python substring test on the LOWERED WhyML TEXT**. When it is false there is
**no `else` branch at all** — the block is simply never appended to `body_str`, with no
refusal, no warning, and no diagnostic. `"raise" not in _else_str` is true for a real `raise`
statement, and equally true for the letters `r-a-i-s-e` occurring **anywhere** in the lowered
text: inside a local variable's name, a callee's name, a field's name.

`praiseworthy`, `appraisal`, `raised_total`, `raiser`, `misraised` — any of these in an
`else:` block deletes the entire block from the model.

## THE FENCE THAT DOES NOT COVER IT — named and quoted, per the deferral rule

`src/pycsl/pycsl.py:1013-1046`, `PYCSL-R37-TRY-ELSE-DROPPED`, exists to catch exactly a
dropped `else`. Its test:

```
1017                if _n37.get("stmt") == "Try" and _n37.get("orelse"):
1018                    _j37 = [_n37.get("orelse")]
1019                    while _j37:
1020                        _x37 = _j37.pop()
1021                        if isinstance(_x37, dict):
1022                            if _x37.get("stmt") in ("Return", "Raise", "Break",
1023                                                    "Continue"):
```

**Four statement KINDS only.** An `Assign` is none of them, so the refusal never fires. And
the fence's own comment asserts the very premise this route breaks
(`pycsl.py:1006-1010`):

```
1006    #   in <lowered else>`: `return`/`raise`/`break`/`continue` are what put a `raise`
1007    #   in the lowered text. A non-jumping else whose lowering contained `raise` for
1008    #   some other reason would still be dropped — no such shape is known, and none
1009    #   exists in either corpus or the mirror, where `try ... else:` does not occur AT
1010    #   ALL (measured by an AST census over all four trees).
```

"No such shape is known" was a claim about a CENSUS OF TWO CORPORA, not a theorem about the
lowering. The shape is one identifier away.

## BOTH DIRECTIONS MEASURED at HEAD `113f38a7`

**Direction 1 — the false claim PROVES.** `a_exp2.py`:

```python
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    y = 0
    try:
        y = 1
    except ValueError:
        y = 9
    else:
        y = 5
        praiseworthy = 0        # <-- the ONLY exploit-bearing token
    return y
```

`[+] Verification SUCCESS! All contracts formally proven.` (rc=0, Valid, 20 steps.)
CPython returns **5**. The emitted WhyML, read in full, has no else branch whatsoever:

```
  let f () : int
    ensures  { (result = 1) } (* linear *)
  =
    let y = ref 0 in
    y := 0;
    try
      y := 1
    with ValueError ->
      y := 9
    end;
    !y
```

**Direction 2 — rename the identifier and the SAME claim correctly FAILS.** `a_ctl2.py` is
byte-identical except that the `praiseworthy` line is absent:

```
rc=1 — Prover result is: Unknown — [-] Verification FAILED or INCOMPLETE.
```

The else survives, `y` is 5, and `ensures \result == 1` is refuted. So the proof in
direction 1 is caused by the substring and by nothing else. The instrument is not vacuous:
the control PROVES nothing and REFUSES for the right reason (the postcondition), which is
the distinction route #105's VACUOUS note was paid for.

## THE GENERATOR THIS CAME FROM

Generator #9 and the `continue`-census, sharpened:

>>> **A GUARD IMPLEMENTED AS A SUBSTRING TEST OVER GENERATED TEXT IS KEYED ON SPELLING, NOT
>>> ON STRUCTURE, AND THE SPELLING IS ATTACKER-CHOSEN THE MOMENT A USER NAMES A VARIABLE.**

It is also the campaign's recurring shape one more time: the drop is SILENT, so a guard that
did nothing looks exactly like a guard that passed.

## REPAIR SKETCH (not yet landed, and to be RE-DERIVED before landing per the #95 rule)

The test must be STRUCTURAL, not textual: decide from the IR whether the `else` block can
transfer control out (a `Return`/`Raise`/`Break`/`Continue` anywhere in its statement tree,
**or** a call to a callee with a non-empty `raises` set), and otherwise splice it. And the
drop must never be silent: if the block cannot be modelled faithfully the emitter must
REFUSE the file, not delete the block. Note route #108 (companion file): making the splice
fire more often is NOT by itself safe, because the splice direction is unsound too.
