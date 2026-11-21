"""Test 1226 — finding-0700 / Gap 2a: a `str` FIELD now carries its OWN literal, not a
witness, and the TRUE claim proves.

`_field_default`'s fallback is `rec_info['defaults'].get(fn, 0)` — an INT — so a
`string`-typed field emitted `{ template = 0 }`, which is ill-typed and therefore a REFUSAL.
Fail-closed, and measured to cost exactly ONE corpus file: a sweep of all 993 pycsl-reference
and 2203 python-reference emissions found exactly one `string`/`real` field defaulted to an
int literal, and it was 0700's — the file the finding calls "the one real gap".

**THE DOCUMENTED FIX WAS "default a `str` field to the EMPTY-STRING WITNESS `\"\"`", AND
BUILDING IT AS WRITTEN WOULD HAVE MANUFACTURED A SOUNDNESS ROUTE.** An empty-string witness is
a DEFINITE value: a field really initialised to `"abc"` would then make `\\result == ""`
provable — route #85's shape exactly, created by a completeness fix. 1227 is that negative
test, and it refuses.

So the capture is FAITHFUL — the literal's own text — and a `str` field WITHOUT a constant
literal keeps its ill-typed int and KEEPS REFUSING. The change turns a refusal into an
emission ONLY where the emission is provably the right one, which is why its whole corpus
cost is 0700 starting to pass.

**A GENERAL RULE THIS EPISODE EARNED: A COMPLETENESS FIX THAT SUPPLIES A *WITNESS* VALUE IS A
SOUNDNESS ROUTE WAITING TO HAPPEN.** "Type-correct default" and "true value" are different
requirements, and only the second is safe to make DECIDABLE. Check every remaining
`_field_default` arm against that sentence before adding another witness.
"""


class C:
    s: str

    #@ assigns self.s
    def __init__(self) -> None:
        self.s: str = "abc"


#@ requires True
#@ ensures \result == "abc"
#@ assigns \nothing
def f() -> str:
    c = C()
    return c.s
