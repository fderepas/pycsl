# ROUTE #194 — an ERASED COLLECTION was the integer 0, and an int-erased parameter's contract read it

**Status: CLOSED by gen #30 (battery E green: suite 3812/3830, same 18 CONFIRMED FAIL, zero XPASS;
planes --slow 40/40; 3 CHANGED mirrors whole-file prove 3/3).** Severity 1.
Generator: **the argument-coercion plane's own baseline, one hour after that plane landed.**

## Measured at `94e52476`

    @mutable_state
    class P:
        #@ ensures p == 0 ==> \result == 1          <- TRUE of this body
        def f(self, p) -> int:                      <- `p` UN-ANNOTATED, so the val declares `p: int`
            if p == 0: return 1
            return 2

        #@ ensures \result == 1
        def probe(self) -> int:
            xs: List[int] = [3, 1, 2]
            return self.f(sorted(xs))               PROVED   (CPython 2)

emitted as `(p__f self 0)` — the array is gone, and Why3 even warns `unused variable xs`. The TRUE
twin (`\result == 2`) is REFUSED.

`_coerce_to_int` answers the LITERAL `0` for any actual whose lowered text begins with one of seven
array prefixes (`(Array.make`, `(Array.sub `, `(array_slice `, `(sorted_1 `, `(list_new_arr `,
`(any_1 `, `(all_1 `) or three map prefixes. `sorted(xs)` lowers to `(sorted_1 …)`, so it matches.

## How it was found, which is the point of this entry

`bin/check-argument-coercion.py` landed at 16:45Z. Writing it required an honest justification for
every substitution, and the one written for this arm said:

> "It DECIDES nothing about the value — the hash is injective-by-luck only, which is what routes
> #113/#114 measured and fenced — and the receiving param is int-erased, so **no law reads it**."

**A CONTRACT ON AN INT-ERASED PARAM IS A LAW THAT READS IT.** The claim was refuted by 17:35Z. The
baseline entry is not deleted — it is rewritten with the refutation in it, because that is the third
time this generation a baseline justification turned out to be a claim about the code that a
measurement refuted (routes #115/#116 did it to `check-singleton-constant-lowering`, route #191 did
it to that plane's `NoneExpr` entry, and this does it here).

## Repair

The array and map arms answer Why3's `(any int)` — it stands for EVERY int, so the erased collection
decides nothing. Route #115's device, and **declaration-free, which is a hard requirement here**:
this function's mirror is a CONVERTED method carrying `#@ assigns \nothing`, so registering an
abstract op would break its frame. Route #193 paid for that lesson with a red battery; here it was
applied *before* building.

Blast radius, measured with an instrumented emitter before any repair was written (the arms emitted
`0 (* PYCSLMARKARR *)` — a valid Why3 comment, so the sweep still emits and the marker is greppable)
and then confirmed by the real one: **3 corpus files, 0 python-reference, 3 mirrors.** Of the corpus
three, `1539` and `1546` are `pycsl-expected: FAIL` already and stay failing; `1553` is a PASS test
and still passes. Witnesses 1685 (XFAIL carrier), 1686 (PASS control: a genuine `0` still reaches
the same int-erased param and the same contract still discharges).

## Lesson

>>> "NO LAW READS IT" IS A CLAIM ABOUT EVERY CONTRACT THAT COULD EVER BE WRITTEN, AND YOU CANNOT
>>> CHECK IT BY READING THE EMITTER. An int-erased parameter is still a NAMED parameter of the
>>> emitted `val`, so any `requires`/`ensures` mentioning it is a law over exactly the value the
>>> erasure invented. The test is one probe: give the callee a contract that is TRUE of its own body
>>> and READS the erased property, then call it with the erased shape.
>>>
>>> A PLANE PAYS FOR ITSELF THE MOMENT IT FORCES YOU TO WRITE THE JUSTIFICATION DOWN. Nothing about
>>> this arm changed between gen #29 and gen #30. What changed is that someone had to state, in
>>> prose, why it was safe — and the statement was checkable.
