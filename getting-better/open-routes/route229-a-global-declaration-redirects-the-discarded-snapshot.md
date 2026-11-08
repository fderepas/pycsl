# ROUTE #229 — A `global` DECLARATION REDIRECTS THE "DISCARDED SNAPSHOT" (Sev-1, LIVE, gen #33, 2026-09-29)

    N = 3

    #@ ensures \result == 0
    def rebind() -> int:
        code = "global N\nN = 5"
        exec(code)
        return 0

    #@ ensures \result == 3
    def read() -> int:
        return N

**`[+] Verification SUCCESS! All contracts formally proven.`** CPython, after `rebind()`, returns
**5**. The proved postcondition is FALSE.

## THE CARRIER IS A SCOPE ARGUMENT, AND IT IS ONE OF THE BEST-AUDITED COMMENTS IN THE TREE

`Module3_Weaver.py`'s dynamic-`exec` detector (#136/#138) is not sloppy work. It lists SIX measured
falsehoods it closes, it records that `_has_dynamic_exec`'s docstring claim that eval "does not inject
names" has been false since the walrus, it notes that a first cut keyed on `:=` alone was walked past
by `eval("globals().update({'N': 5})")`, and that even the widened token rule was walked past by
`eval("f.__globals__.__setitem__('N', 5)")`. It then replaced the spelling rule with a structural one.
It carries a CENSUS of every dynamic exec and eval across five trees.

Its one remaining premise is the scope exemption, stated in its own words:

>>> "SCOPED TO WHERE THE BINDING REACHES THE MODULE NAMESPACE: assignments made by a bare
>>> `exec`/`eval` go to the LOCALS mapping, which IS the module globals at module and class-body
>>> scope and **is a discarded snapshot inside a function**. So a bare call in a function body is
>>> left alone (corpus 0638/0639/0644 …); an explicit mapping argument is refused anywhere."

That is true of the binding form it pictures — a plain assignment. **A `global` declaration inside the
exec'd text redirects the assignment away from the locals mapping and into the GLOBALS mapping, and
at function scope `exec`'s globals mapping is still the real module globals.** The snapshot is
discarded; the assignment never went there.

>>> **A SCOPE ARGUMENT ENUMERATES THE BINDING FORMS ITS AUTHOR PICTURED. `global` IS A BINDING FORM
>>> WHOSE WHOLE PURPOSE IS TO DEFEAT THE SCOPE THE ARGUMENT RESTS ON.** The same shape as the
>>> campaign's standing generator about confinement checks keyed on a write target's syntax: key it
>>> on WHERE THE WRITE LANDS, not on where the statement sits.

## THE POPULATION IS EXACTLY ONE SHAPE, AND THREE NEIGHBOURS PROVE IT

Measured, each a separate file in this directory:

| shape | verdict |
|---|---|
| **dynamic bare `exec`, FUNCTION scope, text declares `global`** (`route229-witness.py`) | **PROVES `\result == 3`; CPython 5** |
| the same exec at MODULE scope (`route229-control-module-scope.py`) | **REFUSED** — "a dynamic `exec` that can bind into the module namespace" |
| a CONSTANT `exec("global N\nN = 5")` at function scope (`route229-control-constant-exec.py`) | **REFUSED** — "a constant `exec` naming a builtin, an imported name or a constant" |
| a dynamic bare `eval("globals().update({'N': 5})")` at function scope (`route229-control-eval-globals.py`) | **REFUSED** |

So this is not "exec is unmodelled". Every adjacent shape is already closed, and the asymmetry is
precise: **`eval` has no function-scope exemption and `exec` does.** The hole is that exemption, for a
text the emitter cannot read.

**THE PROBE IS NOT VACUOUS**: three of the four arms are refusals produced by the very detector under
test, so the instrument demonstrably fires.

## WHY A SPELLING FIX WOULD BE WRONG

Refusing a dynamic `exec` whose text contains `"global"` is exactly the spelling rule this detector
already abandoned twice (the `:=` cut, then the token cut). **The text is DYNAMIC — the emitter cannot
read it at all**, so any rule about its contents is unfounded by construction.

## THE REPAIR, AND ITS HONEST COST

**Remove the function-scope exemption for a DYNAMIC bare `exec`, matching how `eval` is already
treated.** The justification is symmetric and does not depend on reading the text: a constant `exec`
is SPLICED IN AS REAL SOURCE (`splice_constant_exec`) and is therefore modelled; a dynamic one cannot
be inspected, so the only sound position is that it may bind anywhere — which is what the detector
already concluded for `eval`.

**COST, and it is real: corpus `0638`, `0639`, `0644` are the three dynamic execs in the reference
corpus, all bare and in a function/method, and the exemption exists to keep them passing** — they
demonstrate the `\in_scope` havoc and the frame taint. Removing the exemption refuses them. Either
they move to a CONSTANT `exec` (spliced and modelled, so they keep demonstrating what they are for),
or they become expected-FAIL witnesses. That choice is the increment, and it must also pay the
LEDGERS lesson (d5) names: the refusal-witness census, the claim-vacuity ceilings, and the suite
totals.

## REPRODUCE

    getting-better/open-routes/route229-witness.py                     # PROVES; CPython 5
    getting-better/open-routes/route229-control-module-scope.py        # REFUSED
    getting-better/open-routes/route229-control-constant-exec.py       # REFUSED
    getting-better/open-routes/route229-control-eval-globals.py        # REFUSED
