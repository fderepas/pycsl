# The string closure retired ONE of 103 candidates, and the amended criterion refused it in five minutes

Generation #31, 2026-09-26T02:55Z.

## The prediction and the measurement

`finding-the-whole-conversion-frontier-measured.md` put 144 of 230 emitter type errors in the
`int`/`string` buckets and 174 in a wall it called "the FIELD value model". The string CLOSURE
(`900ff447` — field truthiness, `__str__` classification, the fixpoint re-ordering) was landed
against exactly that population.

**RE-SCREENED, all 103 markers whose recorded verdict was `string` or `int`:**

| list | candidates | still TYPE | now PORTS+LOWERS |
|---|---|---|---|
| `rescreen_facade.txt` (facade ports) | 76 | 73 | **1** |
| `rescreen_differs.txt` (`--replace` ports) | 27 | 27 | **0** |

One. `frontend/pure_ast.py::NodeVisitor.generic_visit`, whose prior verdict was
`but is expected to have type int`.

So the "~174 witnesses" bucket was a bucket of SYMPTOMS sorted by the type the emitter
expected, and three string rules cleared one of them. The symptom is shared; the cause is not.
That is the second time this session a frontier number attributed to one capability turned out
to be a spray (`finding-the-field-value-model-already-landed.md` was the first), and the
correction is the same: **a distribution of error messages is not a distribution of causes.**

## And the one it unlocked is refused — by the criterion, not by the prover

`generic_visit`'s live body is

    for _field, value in iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, AST):
                    self.visit(item)
        elif isinstance(value, AST):
            self.visit(value)

L3-tc passes, so the old screen would have queued it for a proof — and `pure_ast.py` costs
**two and a half hours of prover time**. Instead the four oracles ran on the ported tree in
five minutes and one of them said no:

    [!] shadowed-selfcalls: 15 > allowed 14 — a conversion landed whose body no caller can see.
        2 bypassing use(s)   frontend_pure_ast.mlw::self_visit_1 shadows `_unparser__visit`

Converting `generic_visit` routes its two `self.visit(...)` calls through the synthesized
abstract `val self_visit_1`. The body would be proved and nothing that calls it would be able
to see a thing it computes — the same LOST CONVERSION the session had just re-trusted three
instances of.

`emitted-vacuity` 0 new, `yield-erasure` 0 value-erasing, `untrusted-emitted` 923 with 0 `val`:
the other three oracles pass. One says no, and one is enough.

## What this is worth

Five minutes of screening replaced two and a half hours of proving followed by a revert. That
is the whole argument for the amended criterion in
`finding-check-one-is-a-quarter-of-the-criterion.md`, and it paid on its first application.

The marker count did not move. **A generation that measures honestly will have increments whose
yield is zero, and recording one is cheaper than the alternative, which is not looking.**
