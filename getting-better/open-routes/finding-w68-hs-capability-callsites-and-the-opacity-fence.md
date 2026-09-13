# FINDING w68 — H-S's capability check is injected ONLY at `self.<target>(...)` call sites,
# so a call through any other receiver gets none — fenced only because such a call is
# OPAQUE in the model; probe VACUOUS, recorded as measuring nothing about the capability

**CERTIFIED BOUNDARY. FOURTH VACUITY CATCH OF THE GENERATION.**

## THE SHAPE

`#@ happy authn: targets transfer precond self.session_authenticated == 1` makes a capability a
precondition of the guarded operation. Two halves:
* the TARGET **assumes** it — `fn.csl_requires.append(Requires(copy.deepcopy(hp.formula)))`;
* every CALL SITE must **prove** it — a `#@ check` injected by `_collect_self_call_sites`,
  which matches **only** `self.<target>(...)`:

```python
if (isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)
        and isinstance(child.func.value, ast.Name)
        and child.func.value.id == "self"
        and child.func.attr == target):
```

So a call through **any other receiver** (`other.transfer(...)`) is not a site and gets no check
— while the target keeps assuming the capability. That asymmetry is the hazard.

## WHAT I MEASURED — AND WHY IT PROVES NOTHING ABOUT THE CAPABILITY

| driver | verdict |
|---|---|
| **0721** positive control | **PROVES** |
| **the target assumes it?** `transfer` with `ensures self.session_authenticated == 1` | **PROVES** — so yes, the assumption is real |
| `attack(self, other)` calling `other.transfer(amount)`, no grant, claiming nothing | **VERIFIES** |
| the contradiction: `requires other.session_authenticated == 0`, `ensures \result == 1` after `other.transfer(...)` | **FAILS** |
| **ALIVENESS CONTROL: does a non-`self` call propagate ANY postcondition?** `ensures \result == amount` on the callee, `ensures \result == 5` on `other.transfer(5)` | **FAILS** |

**THE LAST ROW IS THE WHOLE ANSWER AND IT INVALIDATES MY PROBE.** A call through a non-`self`
receiver propagates **no postcondition at all** — it is entirely opaque in the model. So the
contradiction driver's failure says only *"non-self calls are opaque"*, not *"the capability is
enforced"*, and the third row's success says only *"it claimed nothing"*. **I measured nothing
about the capability.**

>>> Row 2 is what makes this worth a file rather than a deletion: **the target's assumption is
>>> REAL and MEASURED.** So the only thing standing between "the guarded operation assumes a
>>> capability nobody checked" and an exploitable route is the OPACITY of a non-self call.

## REOPENING CONDITION

**The day a call through a non-`self` receiver carries its callee's contract** — an obvious and
frequently-wanted completeness gain, since today it makes every cross-object call useless for
proof — the H-S capability becomes assumable at a call site that is never checked, and the
contradiction driver above (already written, in this file) becomes live. The fix to co-land is
in the collector: match the guarded call by its RESOLVED TARGET, not by the literal receiver
name `self`. That is route #91's lesson in a different guard — **key on what is being called,
not on the syntactic shape of the caller's expression.**

## THE PATTERN ACROSS w66, w67 AND w68 — THE MOST IMPORTANT THING IN THESE THREE FILES

Three independent security meta-properties, three different guards, and **all three are held up
not by the guard but by a COMPLETENESS GAP in exactly the shape an attacker would use**:

| property | the gap in the guard | what actually fences it |
|---|---|---|
| `compose_from` provider refinement (w66) | S2b has NO implementation | flatten-and-re-verify, a *performance* mechanism |
| `noninterference` (w67) | the twin asserts `ra == rb` on RESULTS only, never state | state-mutating NI targets cannot be verified at all |
| H-S capability (w68) | call-site check only at `self.<target>(...)` | non-self calls are opaque |

>>> **EVERY ONE OF THOSE FENCES IS SOMETHING SOMEBODY WANTS TO REMOVE.** Lazier flattening,
>>> self-composition through state, and cross-object contract propagation are all ordinary,
>>> attractive completeness work that nobody would think of as touching a security property.
>>> **THIS IS ROUTE #89's LESSON AT SCALE: PyCSL's security meta-properties are currently
>>> load-bearing on the incompleteness of its value model, and the incompleteness is on the
>>> roadmap.** Each of the three has its co-landing fix written down in its finding; the fixes
>>> are cheap, and they are cheap *now*, while the exploits are unreachable and the guards can
>>> still be changed without a corpus fight.

---

## UPDATE — GEN #14: THE CO-LANDING FIX IS LANDED, AND IT IS A REJECTION FOR A SHARP REASON.

This finding prescribed *"match the guarded call by its RESOLVED TARGET, not by the literal
receiver name `self`"*. Resolution is not available where the check lives — `_expand_happy_
properties` runs in the WEAVER, before IR resolution, so there is no class for `other`. More
importantly, **injecting the check at a foreign-receiver site would be UNSOUND, not merely
incomplete**: the guarding formula speaks about `self`, so discharging
`self.session_authenticated == 1` at `other.transfer(…)` proves the capability of the WRONG
OBJECT — a check that looks like enforcement and enforces nothing, which is strictly worse than
the hole it replaces.

So the landed fix keys on the CALLEE (`func.attr == hp.target`) — route #91's lesson, kept —
and REJECTS the call. `self.<target>(…)` is unaffected; a call to any OTHER method on a foreign
receiver is unaffected (witness 1266, the rule-(l) narrowness test). The accidental fence
(non-`self` calls are opaque) is now a named one, so the day cross-object calls carry their
callee's contract, the rejection fires instead of the capability silently becoming assumable at
an unchecked site. Witnesses 1265, 1266.
