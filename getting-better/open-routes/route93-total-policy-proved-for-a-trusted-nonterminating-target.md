# ROUTE #93 — the H-D `total` (availability / anti-DoS) policy is PROVED for a target whose
# body is an infinite loop, because `\trusted` strips the body and with it the termination VC
# — and the guard's comment says `\diverges` is "the only opt-out"

**STATUS: CLOSED, FAIL-CLOSED, 2026-09-13 (gen #13). SEVERITY 1.**
Third security meta-property of this generation to be provable while violated, and the third
branch of `Module3_Weaver._weave_happy` to be missing a case its siblings cover.

## THE PROPERTY

`#@ happy availability: targets parse total` is macsl's `\context(\total)`: it NAMES PyCSL's
default-on termination guarantee so that an attacker-controlled input cannot cause
non-termination. `test-suite/annotations.md` row 9 states it as *"Names PyCSL's default-on
termination guarantee (Why3 emits a termination VC; each loop needs a `#@ loop variant`) and
forbids the only opt-out: `#@ \diverges` on the target is a hard error."*

## THE MECHANISM

The H-D branch's **entire** enforcement was one loop:

```python
for fn in target_fns:
    if getattr(fn, "csl_diverges", False):
        raise PyCSLSemanticError(... "it opts OUT of termination" ...)
continue
```

The policy does not *emit* anything — it relies wholly on the termination VC that Why3
generates for the target's body. **But `#@ \trusted` (and `#@ \abstract`) make Module 6 emit
the function as a bodyless `val`** — `module6_whyml/functions.py`: `emit_as_val = func_trusted
or func_abstract or func_trusted_parent`, described in its own comment as *"trusted,
UNVERIFIED body — emit it as a bodyless `val` (contract only, no goals)"*. A bodyless `val`
contains no loop, so there is no termination VC, so **the guarantee the policy names is simply
absent** and the policy is vacuously satisfied.

`\diverges` was therefore **not** the only opt-out. It was the only *honest* one — the one
that says out loud what it is doing.

## BOTH DIRECTIONS MEASURED — four drivers, three of them pre-existing corpus files

| driver | claim | verdict |
|---|---|---|
| **0726** — bounded loop with `#@ loop variant n - i` | control: the policy works | **PROVES** |
| **0727** — the target marked `#@ \diverges` | control: the one guarded opt-out | **PIPELINE ERROR** (rejected) |
| **0728** — the target's loop has NO variant | control: the termination VC really fires | **VERIFICATION FAILED** |
| **the exploit** — 0728's shape, target marked `#@ \trusted reviewer: demo`, body `while True: acc = acc + 1` | the policy holds | **VERIFICATION SUCCESS** |

The three controls are what make this non-vacuous, and they are unusually strong because two
of them are *pre-existing corpus files written by the feature's own author*: 0728 proves the
termination VC is live in this exact file shape, and 0727 proves the H-D branch's guard
executes. **The exploit differs from 0728 by one annotation line, and that line flips a
FAILED verdict to SUCCESS while making the body strictly worse** — 0728's loop merely lacked a
variant; the exploit's loop cannot terminate at all.

## WHY IT IS NOT MERELY TCB ACCOUNTING

`\trusted` means "a human reviewed this body", so one could argue any property of a `\trusted`
function is assumed. **The three sibling forms of the same function reject that argument
explicitly**, because every one of them carries a trusted/abstract trust boundary rather than
letting the marker silently satisfy the property:

| happy form | what it does about a `\trusted`/`\abstract` subject |
|---|---|
| `protects <paths>` (R1.1) | must opt in with `#@ \preserves` — **else hard error** |
| region-write (clause C) | must opt in with `#@ \preserves` — **else hard error** |
| `reading` (H-I1, clause iv) | must be listed in `except` — **else hard error** |
| **`total` (H-D)** | **nothing at all — ROUTE #93** |

So the codebase's own settled convention is that **a bodyless subject does not get to satisfy
a HAPPY property by default; it must be declared.** H-D was the one form that had never been
given that clause. And unlike preservation, totality has no meaningful opt-in — there is no
postcondition that expresses "this bodyless `val` terminates" — so the honest resolution is
the `reading` form's: reject.

>>> **A POLICY THAT ONLY *NAMES* A GUARANTEE PRODUCED ELSEWHERE MUST ENUMERATE EVERY WAY THAT
>>> ELSEWHERE CAN BE MADE NOT TO FIRE.** #91 and #92 were collectors that missed a syntactic
>>> shape; #93 is a policy that missed an EMISSION MODE. The failure is the same failure at a
>>> different altitude: **an obligation you did not generate is indistinguishable from an
>>> obligation that was discharged.**

## HOW IT WAS FOUND

The **deferral generator** that route #92 produced, run as a census over `src/pycsl/`: every
comment claiming a case is handled/rejected/checked elsewhere, with the named guard's actual
matching rule checked against the deferred case. This comment deferred to "Why3's termination
VC" and asserted `\diverges` was the only escape; the census flagged it NOT-COVERED, and I
re-verified the structure and then measured all four drivers myself before believing it.

## REPAIR

Sound-by-rejection, in the H-D branch: a `total` target marked `\trusted` or `\abstract` is a
hard error, because it is emitted as a bodyless `val` with no goals and the totality claim
cannot be discharged for it. The message names the two remedies the emitter actually checks —
give the target a verified body with `#@ loop variant`s, or drop the `total` policy — and the
stale "the only opt-out" comment is corrected in the same increment to enumerate both escapes,
so the next reader is not sent down the path that caused this.

## RESIDUE RECORDED, NOT FIXED

`--fun <name>` marks every function outside the requested slice `trusted` (`pycsl.py`:
`f["trusted"] = True`), and that happens **after** Module 3 has already run this check. So a
`--fun` run can still strip a `total` target's body. Not repaired: `--fun` is an explicitly
user-directed partial verification whose whole contract is "prove this one function", and the
whole-file run — the one the gates use — is unaffected. Recorded so it is a known boundary
rather than an unexamined one.
