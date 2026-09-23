# Route #221 (PARTIALLY CLOSED — the headline is honest; the claim is still assumed) — `--fun` assumes a frame NOBODY WROTE and nothing checks

**Found:** 2026-09-23, gen #31, by the INDEPENDENT fable reviewer of the emit-dunders
report — and explicitly recorded by the reviewer as a finding that is NOT about that build.
It reproduces at base, on ORDINARY methods, and it deserves a route number of its own.

## The decisive pair, under a SHIPPING FLAG

```python
#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    def enter(self) -> int:       # no `#@ assigns`
        self.v = 7
        return 0

#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _r: int = c.enter()
    after: int = c.v
    return before - after
```

    $ pycsl.py <file> --fun use
    [+] Verification SUCCESS! All contracts formally proven.

CPython answers **-7**. The TRUE twin (`== -7`) under the same flag FAILS. And the
IDENTICAL file with no `--fun` FAILS — which is what localises the defect to the flag
rather than to the model.

## The mechanism

A method with no `#@ assigns` gets a SYNTHESIZED frame — `ensures { self.v = old self.v }`
— from the ABSENCE of a clause. Whole-file, that synthesized postcondition is a goal on the
callee, it does not hold, and the file is red. Under `--fun use` only `use` is proved: the
callee's contract is ASSUMED at the call site and its own goal is never discharged.

So the caller proves a claim that rests on an assumption **nobody wrote and nothing
checks**. Assuming a callee's contract is ordinary modular verification and is not the
defect; the defect is that the assumed clause was INVENTED by the emitter from silence, and
that the headline says *All contracts formally proven* rather than *`use` proved, assuming
the contracts of everything it calls*.

That headline is the same one routes #216 and #219 turn on: a sentence about the whole
module printed over a check of part of it.

## Scope — it is about METHODS, not about dunders

The reviewer found it while probing the emit-dunders spike, where a dunder converted from
route #218's BODY-derived frame (an over-approximation, sound) to the ordinary
DECLARED-`assigns` frame. But the control settles the scope: corpus 1817 — a plain
non-dunder `enter`, at base — proves the same false claim under `--fun use`. **Every method
whose body writes self state without declaring `#@ assigns` is a carrier.**

## Why no plane caught it

Every gate in the battery runs the WHOLE-FILE proof; the driver's own discipline says in as
many words that "a `--fun` pass never substitutes for the whole-file proof". That policy is
correct and it is also the reason nothing measures what `--fun` alone certifies. A flag that
prints a verification verdict is a claim surface, and this one had no witness.

## Repairs, un-priced

1. **Say what was assumed.** `--fun` prints a DIFFERENT headline naming the assumed
   contracts. Cheapest; does not make the claim true, makes it honest.
2. **Discharge the synthesized frames of the callees.** In `--fun` mode, also prove the
   frame goals of every method the target calls — the clauses the USER did not write are
   exactly the ones nobody vouched for.
3. **Do not synthesize a frame from silence** under `--fun`: an undeclared `assigns` becomes
   `writes { <everything the receiver has> }` rather than `\nothing`. Sound, and it would
   make this carrier fail; it would also weaken many honest `--fun` runs.

Not priced here, deliberately: the right choice depends on what `--fun` is FOR, and that is
a question for the owner of the flag, not for the reviewer who found the hole.

## Carriers (all three registered in `bin/check-open-route-carriers.py`)

* `route221-carrier-fun-assumes-a-synthesized-frame.py`   — SUCCESS under `--fun use`
* `route221-control-fun-true-twin-still-fails.py`         — FAILED under `--fun use`
* `route221-control-whole-file-still-fails.py`            — FAILED with no `--fun`

Registering them needed a change to that plane: it ran every carrier under one fixed flag
set, so a route whose defect lives under ANOTHER flag could not be held at all. It now
carries a per-carrier `EXTRA_FLAGS` table, keyed the same way as `CARRIERS`, with a refusal
if the two ever disagree — because a flags entry that matches nothing is a carrier running
under the wrong flags and answering a different question. (The first draft keyed the lookup
on the ABSOLUTE path while the table held relative ones, and the #221 carrier silently ran
WITHOUT `--fun`, reported FAILED, and looked exactly like a closed route.)


---

## REPAIR 1 LANDED — 2026-09-23, gen #31: the headline stops claiming the module

`--fun F` now prints

    [+] Verification SUCCESS for F ONLY (--fun): its own goals are proved, and the contract
    of every function it calls is ASSUMED, including any frame the emitter SYNTHESIZED from
    a missing `#@ assigns`. This is NOT a claim about the module — run without `--fun` for
    that (route #221).

instead of `All contracts formally proven.` (and the equivalent for the SMT+Rocq form). The
carrier still reports SUCCESS — the claim it makes is still assumed — and a reader can no
longer take a module-wide sentence from a run that proved one function.

**THIS IS THE HONEST REPAIR, NOT THE COMPLETE ONE, and the distinction is the point.**
Repairs 2 (discharge the callees' synthesized frames under `--fun`) and 3 (do not synthesize
a frame from silence under `--fun`) are decisions about what the flag is FOR, and they belong
to the owner of the flag, not to the reviewer who found the hole. The route stays OPEN with
its three carriers unchanged, because the false proof is still obtainable; what changed is
that the tool no longer describes it as a proof of the module.

VERDICTS UNCHANGED: the six corpus files that carry `# pycsl-flags: ... --fun` (0054, 0055,
0164-0167) all still verify, and the three route carriers still reproduce their ledger rows.
