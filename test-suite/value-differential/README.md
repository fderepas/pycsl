# VALUE DIFFERENTIAL DRIVERS

Each driver here states a literal value in its own `#@ ensures \result == <int>` and, under
`if __name__ == "__main__":`, RUNS the function it makes the claim about. The plane
`bin/check-value-differential.py` executes both halves and compares them.

## WHY THIS EXISTS

The most serious defect class this campaign has found is **not** an exception hole. It is a
**FALSE POSTCONDITION ABOUT ORDINARY, TOTAL PYTHON** — a claim needing no `no_exception`, no
memory-model flag and no opt-in of any kind. Routes **#53** (a `float` modelled as an exact
real, so `0.1 + 0.2 == 0.3` proved), **#58** (int true-division likewise), **#73** and
**#74** (a hand-added oracle shadowing the user's own function) and **#76** (`==` on a class
instance decided STRUCTURALLY where Python decides by IDENTITY) are all of that shape.

Every one of them was found by a human-authored probe. This corpus makes that mechanical:
**it curates nothing.** The expected value is not asserted by whoever wrote the driver — it
is MEASURED by running the program under CPython on every single run. A driver whose claim
drifts from Python's real behaviour reclassifies itself automatically.

## THE VERDICTS

    claim DISAGREES with CPython + PyCSL PROVES   -> RED. A postcondition proved about a
                                                    program that demonstrably refutes it.
    claim DISAGREES with CPython + PyCSL refuses  -> green (the honest answer), and this is
                                                    the population that gives the gate teeth.
    claim AGREES with CPython    + PyCSL PROVES   -> green, and this is the direction that
                                                    stops the gate being satisfiable by
                                                    refusing every program.
    claim AGREES with CPython    + PyCSL refuses  -> INCOMPLETE. Reported, never fatal.
    CPython RAISES / prints no int                -> OUT OF SCOPE. Reported, never fatal.
                                                    These drivers are meant to be TOTAL.

**THE POPULATION GUARD** (the #44 rule — a gate that cannot tell "nothing is wrong" from "I
looked at nothing" is not a gate): the plane REFUSES with rc=2 unless the corpus holds BOTH
at least one AGREEING driver that actually PROVES and at least one DISAGREEING driver.

**PARSING IS FAIL-CLOSED.** Exactly one `#@ ensures \result == <int>` line per driver; a
driver whose claim cannot be parsed is an ERROR, never a silent skip.

## THE NEGATIVE TEST — WHY A GREEN RUN MEANS SOMETHING

**A gate that has never been observed to fail is not known to be a gate.**
`negative-test/n01_trusted_assumption_is_red.py` makes the RED path fire on a REAL program:
a `#@ \trusted` stub's `ensures` is ASSUMED rather than proved (the documented, opt-in
trusted-stub mechanism — not a soundness route), which lets PyCSL prove `\result == 99`
about a program CPython evaluates to `1`. Run it with

    python3 bin/check-value-differential.py --negative-test

and it FAILS unless this plane rules that driver UNSOUND. The standing run SKIPS the
`negative-test/` subdirectory, so it cannot make a normal run red.

## THE SEED POPULATION (gen #7)

**Twenty-two drivers, twelve AGREE / ten DISAGREE**, pinning semantics that are easy to
regress to a "reasonable" wrong answer. Each DISAGREE driver is the twin of an AGREE one:
it states the plausible WRONG answer, and the gate requires PyCSL to keep refusing it.

  * **Floor division and modulo with a NEGATIVE DIVISOR.** `identifiers.py`'s `OP_MAP`
    comments still say `//` -> `div` and `%` -> `mod` (Why3 `int.EuclideanDivision`), and
    Euclidean genuinely disagrees with Python: `7 // -2` is **-4** in Python and -3
    Euclidean; `7 % -2` is **-1** and 1; `-7 // -2` is **3** and 4. v01-v03 pin Python's
    answers, v07-v09 are the Euclidean twins that must stay refused.
  * **`and`/`or` return an OPERAND, not a bool.** `0 or 5` is **5**, `5 and 3` is **3**.
    v04/v05 pin that; v10/v11 are the boolean-collapse twins that must stay refused.
  * **Container truthiness.** The empty string is FALSY. v06 pins it; v12 is the twin.
  * **FLOOR division vs C-STYLE TRUNCATION, the other classic wrong model.** `-1 // 2` is
    **-1** in Python (floor) where truncation toward zero gives 0; `-1 % 2` is **1** and
    `-7 % 3` is **2**, where a C remainder gives -1 for both. v13-v15 pin Python's answers,
    v19-v21 are the C twins that must stay refused.
  * **A `bool` IS an `int`.** `True + True` is **2**, not a collapsed 1 (v16 / v22).
  * **`2 ** 10` is 1024** (v17, pins the power operator against an XOR reading) and
    **`len("abc")` is 3** (v18).

## KNOWN UNMODELLED, DELIBERATELY NOT ADDED AS DRIVERS (gen #7, measured)

`round()` and `int(<float>)` are Why3 TYPE-REJECTED today (`real` where an `int` is
expected), so BOTH directions fail and they would only ever report as OUT OF SCOPE. They are
worth revisiting the moment either is modelled, because Python's rules are exactly the kind a
model gets wrong: `round(2.5)` is **2**, not 3 (BANKER'S rounding — ties go to even), and
`int(-3.7)` is **-3** (truncation toward zero), not the floor -4.

Grow it. Every raising-free Python operation whose value the model could plausibly get
wrong is one more permanent, self-measuring check.
