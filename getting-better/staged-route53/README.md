# STAGED — ROUTE #53 (a Python `float` is an EXACT REAL), REPAIR DECIDED AND SPIKED

Route file: `getting-better/open-routes/route53-float-is-a-real.md`.
RE-CONFIRMED LIVE at `37403f79` by relaunch #51: both recorded witnesses still prove a
contract false of their own program (`fl3.py`, `ensures \result == 0.3` for
`return 0.1 + 0.2`, Valid in 26 steps; `fl4.py`, the parameter form, Valid in 31).
Python answers `0.30000000000000004`.

## THE DEFECT IS ONE `ensures`, WHICH IS WHY THE REPAIR IS SMALL

`module6_whyml/expressions.py`, the float arithmetic bridge, emitted:

```python
self._add_abstract_op(
    f"val float_{nm}_op (a b: real) : real\n"
    f"    ensures {{ result = (a {rop} b) }}")
```

and the `self._in_spec` path returned the RealInfix `+.` directly. So the model was not
merely imprecise about floats, **it was EXACT about them**, in a language where the exact
answer is wrong.

## THE REPAIR, AS SPIKED AND MEASURED

Make the bridge a DETERMINISTIC OPAQUE and route the SPEC path through the SAME symbol:

```python
self._add_abstract_op(f"val function float_{nm}_op (a b: real) : real")
return f"(float_{nm}_op {left} {right})"
```

`val function` (not bare `val`) is LOAD-BEARING and is the campaign's existing idiom
(`val function pycsl_none`, `val function path_join_op`): a bare `val` is not
deterministic across calls, so two occurrences of `x + x` would not be equal and EVERY
float postcondition would die.

Routing the SPEC path through the same symbol is equally load-bearing — it is what keeps
congruence proofs alive. Emitting `+.` on one side and the opaque on the other would break
every float postcondition instead of only the false ones.

MEASURED (isolated worktree, why3 on PATH):
  * route #53 CLOSES — `fl3.py` and `fl4.py` both go `[+] SUCCESS` -> `[-] FAILED`;
  * CONGRUENCE SURVIVES — `ensures \result == x + x` for `return x + x` still proves
    (Valid, 6 steps), and so does the nested `ensures \result == (a + b) * c`;
  * of the ten float-annotated corpus files, seven are unchanged.

## THE COST, STATED HONESTLY

**`0517` REGRESSES.** Its `#@ ensures \result >= 0.0` under `#@ requires x >= 0.0` no
longer proves, because an opaque tells you NOTHING about ordering. That clause is TRUE of
IEEE 754 (a sum of two non-negative binary64 values is non-negative), so this is a real
COMPLETENESS loss, not a false claim being withdrawn. Note `0517`'s own docstring says it
"proves the additive relationship and a non-negativity bound OVER THE REALS" — over the
reals is exactly the unsoundness, so the file documents the defect it locks in. It must be
rewritten in the same increment.

## THE REFINEMENT THAT LOOKS FREE AND IS REFUTED — DO NOT RE-DERIVE IT

The obvious way to keep `0517` whole is to add IEEE-true SIGN-PRESERVATION clauses to the
bridge. **REFUTED FOR `*`.** The clauses a reader would write are
`a >=. 0 /\ b >=. 0 -> r >=. 0` with `a <=. 0 /\ b <=. 0 -> r >=. 0` and
`a >=. 0 /\ b <=. 0 -> r <=. 0`. Take `a = 0.0`: BOTH antecedents hold, so the model
derives `r >=. 0 /\ r <=. 0`, i.e. **`r = 0.0` — a decided EQUALITY out of clauses that
are individually only inequalities.** And Python disagrees: `0.0 * float("inf")` is
**`nan`**, confirmed by running it. `+` survives the same analysis, but a rule sound for
`+` and unsound for `*` is a per-operator argument, and routes #42/#52 are this campaign's
record of what happens to a rule that holds for some operands and not others.

**GENERAL LESSON, worth more than this route: a conjunction of inequality axioms DECIDES
an equality at the point where their antecedents overlap.** `>= 0` and `<= 0` are each
harmless; at `a = 0.0` they meet and pin the result exactly. Check any "harmless bound"
added to an opaque at the BOUNDARY values where its guards coincide, not in the interior.

## WHAT IS NOT DONE

**THE L3 COST IS UNMEASURED.** Run `bin/mirror-emit-sweep.sh` (mirror) and
`bin/byte-diff-sweep.sh` (corpus) on both sides and compare with
`bin/byte-diff-compare.py`. Four mirror files carry a float annotation, so this is
unlikely to be byte-inert. Do it when no other battery owns the machine.
