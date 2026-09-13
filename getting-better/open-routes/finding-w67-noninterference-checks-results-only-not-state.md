# FINDING w67 — H-I2 noninterference compares only the two RESULTS, never `self` state,
# so a leak into a FIELD is outside the property — but the channel is fenced upstream,
# and I could not exhibit it

**CERTIFIED BOUNDARY. THE HAZARD IS REAL IN THE SYNTHESIS; THE EXPLOIT IS UNREACHABLE TODAY.**
Recorded with a sharp reopening condition, because this one is a *completeness gap holding a
confidentiality property up*, which is route #89's shape and the most re-armable kind.

## THE MECHANISM — WHAT THE PROPERTY ACTUALLY OBLIGES

`#@ happy ni: targets f noninterference secret s` is macsl's self-composition, automated.
`Module3_Weaver._synthesize_selfcomp` builds a twin `f__selfcomp` taking the PUBLIC params once
and each SECRET param twice (`_a`/`_b`), calling the target twice, and attaching **exactly one
obligation**:

```python
pred = self.parser_module.parse_contract("check (ra == rb)", line).expr
ret.csl_checkpoints = [CheckPoint("assert", pred, origin=f"happy {hp.name} noninterference ra==rb")]
```

`ra` and `rb` are the two **return values**. **NOTHING IN THE SYNTHESIZED TWIN COMPARES `self`
ACROSS THE TWO CALLS.** So the property as realised is *"the RESULT does not depend on the
secret"*, while its name, and its docstring's framing ("if the result depends on a secret,
`ra == rb` is unprovable — **a leak**"), invite the reader to hear *"the secret does not
leak"*. A target that returns something secret-independent and writes the secret verbatim into
an observable field satisfies the obligation as written.

>>> **A SELF-COMPOSITION IS ONLY AS STRONG AS THE RELATION IT ASSERTS BETWEEN THE TWO RUNS.
>>> ASSERTING `ra == rb` BUYS RESULT-NONINTERFERENCE, NOT NONINTERFERENCE.** The two differ
>>> exactly on the state channel, and the state channel is the one an attacker reads later.

## WHY I AM NOT CALLING IT A ROUTE — THE PROBE WAS VACUOUS AND I CHECKED

Exploit attempted: `summarize` returns `public_id * 2` (secret-independent) while its body does
`self.log = balance`. It **FAILED**. Before concluding "fail-closed", I ran the control that
decides whether the channel is alive at all:

| driver | verdict |
|---|---|
| **0729** (result secret-independent, no state) — positive control | **PROVES** |
| **0730** (result depends on the secret) — negative control | **FAILS** |
| exploit: `self.log = balance`, result secret-independent | **FAILS** |
| exploit without the leak stated in the contract | **FAILS** |
| **control: `self.log = 0` — a CONSTANT, no secret anywhere** | **FAILS** |
| **control: target READS `self.log`, `assigns \nothing`** | **PROVES** |

**THE FIFTH ROW IS THE WHOLE ANSWER.** A noninterference target that writes *any* field — a
literal `0`, with no secret in sight — already fails, on the twin's own postcondition
(`acct__summarize__selfcomp'vc`). So **every** state-mutating NI target is refused regardless of
leakage, my exploit's refusal carried no information about leaks, and the probe measured
nothing. The sixth row sharpens the boundary: the form works for targets that READ state, so it
is specifically **WRITING** that is fenced.

## THE BOUNDARY, STATED PRECISELY

**H-I2 noninterference is usable only for targets that do not mutate state; a state-mutating
target cannot be verified at all.** That completeness gap — not any guard — is what stands
between the result-only obligation and a field leak.

## REOPENING CONDITION

**The day a state-mutating noninterference target can be verified, the state channel is
unguarded**, because the synthesized twin's only obligation is `assert (ra == rb)` over the two
RESULTS and nothing compares `self`. Making self-composition work through state is an obvious,
attractive completeness improvement — and whoever makes it will be extending the twin, not
reading the confidentiality property, which is precisely how route #89 happened.

**The fix to co-land with that capability is already known and is one line of the same kind:**
the twin must also assert equality of the PUBLIC (non-secret) state after the two calls, not
just of the results. Anything less makes the property's name a lie.

## NOT PROBED

Whether the *number of calls*, termination, or exception behaviour can carry the secret — the
twin asserts nothing about those either. Same reasoning applies, same unreachability caveat.

---

## UPDATE — GEN #14: THE CO-LANDING FIX IS LANDED, AS A REJECTION, NOT AS A STRONGER TWIN.

This finding prescribed *"the twin must also assert equality of PUBLIC state after the two
calls"*. **That is not expressible in this synthesis, and the reason is worth recording:** the
twin calls the target twice on the SAME `self`, sequentially. There is no second initial state,
so there is no pair of final states to relate. A genuine 2-run state relation needs a second
`self`, which `_synthesize_selfcomp` does not have and cannot cheaply acquire.

So the fix landed as the sibling forms' discipline instead — **sound-by-rejection**: a
noninterference target that can WRITE state is refused, naming the field and, when the write is
reached through a helper, the call chain. It is REACHABILITY-based over in-module
`self.<m>(…)` calls, because a guard that scanned only the target's own body would be routes
#91/#92 in a third guard. `__init__` needs no carve-out here — it is simply not reachable from
the target, so the carve-out that #91, #92 and #94 each needed by hand falls out for free.

**What this buys:** the accidental fence (a state-mutating NI target cannot be verified at all)
is replaced by a NAMED one that says why. The day self-composition works through state, the
rejection fires and whoever lifts it is pointed straight at the obligation that has to grow —
instead of silently inheriting a property whose name is a lie.

**Residue, stated honestly:** the rejection covers direct `self.<f>` stores, a non-`\nothing`
`assigns` clause naming `self.`, and both of those reached transitively through in-module
`self` calls. Mutation through a NON-`self` receiver is not traversed — it is opaque in the
model and propagates nothing (finding w68), and w68's own co-landing rejection now refuses the
guarded-call case of that shape. Witnesses 1262, 1263, 1264.
