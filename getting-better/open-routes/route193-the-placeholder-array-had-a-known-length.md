# ROUTE #193 — the PLACEHOLDER array for an unrepresentable iterable had a KNOWN LENGTH

**Status: CLOSED by gen #30 (battery C2 green: suite 3810/3828, same 18 CONFIRMED FAIL, zero XPASS;
planes --slow 39/39; 6 CHANGED mirrors whole-file prove 6/6).** Severity 1.
Generator: the census route #192's lesson demanded — "every change to what something lowers to owes a
census of who was reading the old spelling" — widened to *every DEFINITE stand-in for an UNKNOWN value*.

## Measured at `c1140918`

    #@ ensures \result == 1
    def probe() -> int:
        xs: List[int] = sorted(x for x in [3, 1, 2])
        return len(xs)                                  PROVED   (CPython 3)

emitted, in full, as

    val sorted_1 (a: array int) : array int
      ensures { Array.length result = Array.length a }
      …
    let xs = (sorted_1 (Array.make 1 0)) in
    Array.length xs

`_array_coerce_arg` answers `(Array.make 1 0)` whenever the actual's lowered text is the bare `"0"` —
which is what the IR leaves behind when it drops an iterable shape it cannot represent (a generator
expression, a comprehension, variadic `*args`). The function's own docstring defends the choice:

> "A length-1 placeholder array works because the abstract vals have no axioms about their input
> contents."

That is a statement about **contents**. `sorted_1` carries a law about **length**, and
`array_to_seq`'s `ensures { Seq.length result = Array.length a }` is the same law one step further on.
So the placeholder did not merely lose the iterable — it answered a question about it, wrongly. The
TRUE twin (`\result == 3`, CPython's answer) is REFUSED, which is the decisive signature.

## Carrier census

Only the `sorted(<generator expression>)` shape carries it. `sum(<genexp>)`, `list(reversed(...))`, a
varargs `*args` fold and `sorted([<comprehension>])` all fail closed, and `sorted(<real list>)` still
proves its length. `any_1` / `all_1` — the only consumers the placeholder actually has in the tree —
carry NO `ensures` at all, which is why this survived: measured from the emitted baseline, the
placeholder appears in exactly three corpus files (all route #158 `any`/`all` witnesses) and five
mirrors, and every live use goes through `any_1`/`all_1`.

## Repair, and the first attempt that the planes caught

The honest placeholder is Why3's `any (array int)` — it stands for EVERY array of ints, so neither
length nor contents is decidable. Witness 1683 is refuted, witness 1684 shows a REAL list still keeps
its length through `sorted_1`, and the true twin stays honestly unproven (the model genuinely does not
know the length).

**The first attempt declared an abstract `val pycsl_unknown_array (_u: unit) : array int` instead**, and
BATTERY C WENT RED on three fidelity planes — `check-self-annotate-mirror-sync`,
`check-mirror-signature-drift`, `check-trusted-frame-honesty`. Registering an abstract op means calling
`self._add_abstract_op(...)`, which means `_array_coerce_arg` stops being a `@staticmethod` and becomes
EFFECTFUL — and its mirror is a CONVERTED (proven, non-`\trusted`) method whose contract is
`#@ assigns \nothing`. The declaration was the whole cost, and `any` needs no declaration, so the
function stays pure, the mirror edit is a verbatim one-line body change, and the contract is untouched.

## Lessons

>>> A DEFENCE THAT NAMES ONE PROPERTY IS NOT A DEFENCE OF THE OTHERS. "The abstract vals have no
>>> axioms about their input CONTENTS" was true, and was written beside a placeholder whose LENGTH was
>>> the thing being read. Read what the consumer's `ensures` actually decides, not what the comment
>>> says the placeholder is safe for.
>>>
>>> A REPAIR THAT NEEDS A NEW ABSTRACT `val` MAKES ITS EMITTER FUNCTION EFFECTFUL, AND IF THAT FUNCTION
>>> IS A CONVERTED MIRROR METHOD ITS PROVEN `assigns \nothing` IS THE BUDGET YOU JUST SPENT. Check the
>>> mirror's contract BEFORE choosing between `_add_abstract_op` and a declaration-free Why3 construct.
