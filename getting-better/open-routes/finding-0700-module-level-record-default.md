# FINDING (not a route) — THE `why3 --type-only` POPULATION RE-MEASURED, AND IT IS ONE FILE
# (2026-09-09, relaunch #50, ladder item 5)
#
# ## RESOLVED 2026-09-12 (gen #10) — AND THE DOCUMENTED FIX WOULD HAVE BEEN A SOUNDNESS ROUTE
#
# **0700 NOW PROVES. The suite's failure baseline moved 19 -> 18**, the first change to that
# set in three generations, and the diff shows exactly one line removed. Gates: 34/34 planes;
# IR conformance 38/38 + 38/38 with NO golden moved; fidelity rc=0; python-reference
# 2203/2203 and MIRROR 53/53 inert; pycsl-reference 995 compared with 3 MOVED, asserted
# mechanically to be 0700 plus this fix's own two witnesses; suite **3353/3371, ZERO XPASS**.
#
# **BUT NOT THE FIX THIS FILE DESCRIBES.** The quoted Gap 2a says *"the `str` field defaults
# to the empty-string witness `{ template = "" }`"*. An empty-string witness is a **DEFINITE
# value**, so a field really initialised to `"abc"` would then make `\result == ""` PROVABLE
# — a brand-new severity-1 route of exactly the family routes #85/#86/#87 close. Measured, not
# feared: witness 1227 is that claim and it must refuse.
#
# What landed instead is a **FAITHFUL CAPTURE** — the field carries its OWN literal, so the
# true claim `\result == "abc"` PROVES and the empty-string claim refuses. A `str` field
# WITHOUT a constant literal keeps its ill-typed int and **keeps refusing**, so the change
# turns a refusal into an emission ONLY where the emission is provably the right one. Blast
# radius measured first: a sweep of all 993 pycsl-ref + 2203 python-ref emissions found
# **exactly one** `string`/`real` field defaulted to an int literal, and it was 0700's — so no
# expected-FAIL witness depended on this type accident, which was the real risk.
#
# **THE RULE THIS EARNED, AND IT IS THE MOST PORTABLE THING IN THIS FILE:**
# **A COMPLETENESS FIX THAT SUPPLIES A *WITNESS* VALUE IS A SOUNDNESS ROUTE WAITING TO HAPPEN.**
# "Type-correct default" and "true value" are different requirements, and only the second is
# safe to make DECIDABLE. Every arm of `_field_default` this campaign has had to repair — #79
# (scalar), #83 (conditional store), #85 (dict/set), #87 (list) and now the `str` arm — was a
# witness value that someone had justified as sound. **That one function is the same mistake
# made five times, and the next person to add an arm to it should read this sentence first.**
#
# Witnesses 1226 (faithful, must prove) and 1227 (the empty-string witness, must NOT prove).
# The observation below that "fail-closed *by type accident* is fragile" is exactly right and
# is what made this worth doing.

## THE POPULATION IS 21, NOT 17 — AND TWENTY OF THEM ARE DELIBERATE

`why3 prove --type-only` over all **907** emitted `pycsl-reference` modules at `04f4f26f`:

    0050  0303  0386  0557  0560  0563  0575  0601  0639  0700  0793  0794  0807
    0814  0849  1013  1014  1076  1077  1078  1088                          = 21

The handoff carries "the seventeen", measured over 858 modules in an earlier window. The
growth is entirely **route witnesses added since** — `1013`/`1014` (routes #32/#33),
`1076`–`1078` (route #48) and `1088` (route #50's control).

**TWENTY of the 21 carry `# pycsl-expected: FAIL`.** For those, an ill-typed emission IS the
fail-closed mechanism, and the corpus harness is what would notice if it ever stopped being
one (a witness that started proving would be an XPASS, which has counted as a failure since
relaunch #44). So they are working as intended, and **ladder item 5 is far smaller than its
headline** — it is not seventeen files of work, it is one.

**Worth keeping in view, though**: fail-closed *by type accident* is fragile, and this window
met the same pattern twice more outside the corpus — `\result != None` on a lying `-> str`
(`scratchpad/w51/p3.py`) and a callee returning `None` implicitly by falling off the end
(`scratchpad/w51/q6.py`) both fail ONLY because Why3 expects `()` or `int` where a `string`
is supplied. Nothing intends those refusals.

## THE ONE REAL GAP: `0700`, AND IT IS THE DRIVER FOR THE FIX THAT IS MISSING

`0700` carries **no expectation header**, so the harness expects it to PASS, and its own
docstring says `STATUS — **PROVES**`. It does not. It fails with **exactly the error its
docstring describes as fixed**:

> *"Before the fix `Tmpl()` lowered to the ill-typed `{ template = 0 }` (int default against a
> `string`-typed field, L3-tc ✗); after the fix the `str` field defaults to the empty-string
> witness `{ template = "" }`. (Gap 2a fixes `_call_record_constructor._field_default` so a
> `str`/`real` field defaults to `""`/`0.0`.)"*

Emitted at HEAD:

```whyml
  type tmpl = { mutable template: string }

  let t : tmpl = { template = 0 }        (* <- the exact defect the fix removed *)
```

**MECHANISM — THE FIX LANDED ON THE PATH THE DRIVER DOES NOT TAKE.** `_field_default` is a
NESTED helper inside `_call_record_constructor` (`module6_whyml/expressions.py:11898`) and is
consulted from exactly one place, its own record-literal builder at line 12000 — the
**in-function** construction path. `0700` constructs at **MODULE level** (`t = Tmpl()` at top
level), which is emitted by `_emit_module_globals` (`module6_whyml/preamble.py`), a separate
emitter that never consults `_field_default` and still writes the int default.

So the driver written to prove Gap 2a exercises the one path Gap 2a did not reach, and it has
been failing inside the standing suite-failure count ever since, undiagnosed. This is the
same shape as the window-#49 finding that `bin/check-trusted-raises-honesty.py` had been RED
at HEAD with nobody looking — **a red signal inside an accepted total is not a signal.**

## NOT A SOUNDNESS ROUTE

It is a COMPLETENESS gap and it fails CLOSED: the module does not type-check, so nothing is
proved about it and no false contract is admitted. It is recorded here rather than in the
route files for that reason.

## VERIFIED NOT MINE

`0700` fails identically at the window-start HEAD `d1cc975b`, checked in an isolated worktree
before any of this window's landings — so it is pre-existing, not a regression introduced by
routes #51/#55.

## THE REPAIR (scoped, not built)

Give `_emit_module_globals` the same per-type default `_call_record_constructor` already has.
The honest spelling is to LIFT `_field_default` out of the nested scope so both paths consult
ONE function — two copies of a per-type default table is how this defect happened. **Note the
cost before building**: `_call_record_constructor` is a mirrored method, and lifting a nested
`def` out of it MOVES `bin/check-mirror-coverage.py` (a new top-level def is a new unmirrored
def until it is mirrored), which is the exact ratchet that caught route #51's Module 4
functions. Budget for mirroring the lifted helper in the same increment.
