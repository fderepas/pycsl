# Routes #206 and #208 — a `total` availability policy proved over a helper that never returns

**Status:** BOTH CLOSED (gen #30). SEV-1. One repair, two spellings, and the second one
walked through the first one's patch twenty minutes after it landed.

## The witnesses

`1711_route206_total_target_calls_trusted_stub.py` (expected FAIL):

```python
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ ensures \result >= 0
    #@ \trusted
    def spin(self, n: int) -> int:
        acc: int = 0
        while True:            # cannot terminate
            acc = acc + 1
        return acc

    #@ requires n >= 0
    #@ no_exception \all
    #@ ensures \result >= 0
    def parse(self, n: int) -> int:
        return self.spin(n)
```

`1715_route208_total_target_calls_diverges_helper.py` (expected FAIL) is the identical file
with `#@ \diverges` in place of `#@ \trusted`.

Both printed **"Verification SUCCESS! All contracts formally proven"** — an AVAILABILITY
policy, whose stated purpose is that an attacker-controlled input cannot cause
non-termination, proved of a function that hangs. CPython: `Parser().parse(1)` never
returns.

## The inverted incentive, read off the emission

```whyml
val self_spin_1 (x0: int) : int          (* \trusted callee  *)
  ensures { (result >= 0) }              (* contract CARRIED  *)

val self_step_1 (x0: int) : int          (* verified callee   *)
                                         (* NO contract       *)
```

A `self.<method>()` call lowers to an abstract op, and the callee's contract rides onto
that op ONLY when the callee is a bodyless `val`. So **trusting a helper makes the caller
STRONGER**: it gains the helper's assumed postcondition and loses the helper's termination
VC. That is the whole route in one sentence, and it is why the control (`1712`, a verified
helper) had to be written so its postcondition does NOT depend on the helper's result — a
first version failed for that unrelated propagation gap, and a control that fails for the
wrong reason is worse than no control.

## Where they came from

Route #93 closed "the TARGET is bodyless" and wrote into the source that there were *"two
opt-outs, not one"*. Reading that as a claim and asking which spelling it did not run gives
#206 (a bodyless CALLEE). Then #208 is my own repair's missing spelling: I derived the
callee set from HOW #206's witness happened to be written (bodyless) instead of from WHAT
the rule means (**no termination VC**), so `#@ \diverges` — the most explicit declaration
of non-termination the language has — walked straight through. That is this campaign's own
lesson (i) missed on my own patch, inside an hour.

## The repair

In `Module3_Weaver::_expand_happy_properties` (whose mirror twin is `#@ \trusted reviewer:
pycsl-self-annotate`, so the refusal costs no marker, no mirror edit and no re-proof):
the target's whole MODULE-LOCAL call graph is walked transitively, and any reachable
function that is `\trusted`, `\abstract` **or `\diverges`** is a hard error. An imported
target is already a hard error in that same block, so module-local closure is the whole
graph.

## Controls

`1712` (verified helper) PASSES, `0726` (bounded loop with a variant) PROVES, `0727`
(`\diverges` on the target), `1254`/`1255` (route #93's own witnesses) stay refused, `0728`
still FAILS. `bin/check-trusted-termination-honesty.py`, built alongside, counts the 52
trusted bodies across the repo whose termination is assumed and unverified.
