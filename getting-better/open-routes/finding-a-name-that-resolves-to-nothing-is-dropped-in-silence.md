# FINDING (#49, gen #31) — A NAME THAT RESOLVES TO NOTHING IS DROPPED IN SILENCE
#
# FOUR directives share one defect, and one of them is the feature this generation
# implemented eight hours before the audit that found it. Started from `#@ uses`.

**STATUS: LIVE, DIAGNOSTIC ONLY.** Not a soundness route — `#@ uses` is ordering-only and
"emits no WhyML" (annotations.md row 17) — but a typo'd lemma name produces no message at
all, and the proof that was supposed to rest on the lemma then fails for a reason the user
cannot connect to what they wrote.

## The witness

```python
#@ lemma
#@ requires n >= 0
#@ ensures n + 0 == n
#@ assigns \nothing
def triv(n: int) -> None:
    pass


#@ uses no_such_lemma          # <-- names nothing
#@ ensures \result == 0
#@ assigns \nothing
def go() -> int:
    return 0
```

    [+] Verification SUCCESS! All contracts formally proven.

## Why it is worth a message

This is the THIRD member of one family found in a day, and the family is worth naming:
**a NAME the user wrote that resolves to nothing, and is then dropped in silence.**

  * `Callable[[Rekt], int]` — an unknown class silently becomes `int`
    (`finding-callable-scope-limit-not-enforced.md`);
  * `#@ verify_module leafmod` — a lowercase group name USED to produce a Why3 syntax
    error naming a synthesized module the user never wrote (repaired gen #31);
  * `#@ uses no_such_lemma` — dropped entirely.

In each case the compiler knows the admissible set exactly and says nothing.

## Before landing a refusal — the (u4) test, NOT yet run

The question is whether `#@ uses` can legitimately name a lemma that is not in THIS
module's IR: a lemma defined in an IMPORTED unit. The doc says the directive "forces the
lemma to be emitted before this function so its fact is in scope", which is a statement
about ordering WITHIN an emission — but import injection puts imported functions into the
IR, so an imported lemma may well be present. **Build that program and check it verifies
before adding any rule** — this is exactly where the `#@ datatype` exhaustiveness refusal
died the same day (wall-lesson (u4)), and where the `Callable` rule nearly did.

Measured 2026-09-24. Witness: `$SCRATCH/g31/cm/f.py`.

## THE (u4) TEST WAS RUN, AND IT FOUND SOMETHING BIGGER

The program the test demanded — `#@ uses <lemma>` naming a lemma from an IMPORTED unit:

```python
# lemlib.py
#@ lemma
#@ requires n >= 0
#@ ensures n + 0 == n
#@ assigns \nothing
def triv(n: int) -> None: ...

# main.py
from lemlib import triv
#@ uses triv
#@ ensures \result == 0
#@ assigns \nothing
def go() -> int: return 0
```

    [+] Verification SUCCESS! All contracts formally proven.

and the emitted `.mlw` contains **no `triv` at all**. So the imported lemma is NOT emitted,
its fact is NOT in scope, and the citation is a no-op that reports success. The directive's
documented job — "forces the lemma to be emitted before this function so its fact is in
scope" — is **not done across a module boundary**, and nothing says so.

That is a stronger finding than the typo one and it changes the shape of the repair:

  * a refusal keyed on "the cited name must be a `#@ lemma` IN THE EMISSION" would catch
    BOTH the typo and the cross-module case, and in the cross-module case it would be
    telling the truth — the citation really does nothing there;
  * so the (u4) counter-program does NOT refute the rule here. It sharpens it.

WHAT IS STILL OWED before landing: a census of cross-module `#@ uses` in the corpus and
`src/`. If any verified program cites an imported lemma AND NEEDS IT, then the lemma is
reaching scope by some path this probe did not exercise, and the rule is wrong after all.
If none does, the refusal is right and the cross-module gap becomes its own named
capability (emit an imported cited lemma).

Measured 2026-09-24. Witnesses: `$SCRATCH/g31/cm/f.py`, `$SCRATCH/g31/us/{lemlib,main}.py`.

## THE CENSUS — three sites, all local

`#@ uses` across `test-suite/corpus/`, `src/pycsl/`, `src/self-annotate/src/` and
`src/pycsl_lib/`:

    test-suite/corpus/pycsl-reference/0582.py:35   #@ uses even_nonneg
    test-suite/corpus/pycsl-reference/0582.py:56   #@ uses even_inv
    test-suite/corpus/pycsl-reference/0565.py:47   #@ uses to_int_nonneg

(the other grep hits are the emitter's own comments and the `csl_uses` field). **Three
sites, two files, every cited lemma defined in the SAME file.** Zero cross-module uses
anywhere in the tree.

So both halves are settled:

  * the refusal ("the cited name must be a `#@ lemma` in the emission") has a blast radius
    of ZERO over the existing tree, and the (u4) counter-program — an imported lemma — is
    a program the rule would correctly reject, because the citation genuinely does nothing
    there;
  * the cross-module gap has no user, which is why it has gone unnoticed, and it becomes
    its own named capability: **emit an imported cited lemma**, so `#@ uses` means the same
    thing across a boundary as within a file.

Priced: the rule is a set membership over `ir_data`'s functions at the `_run_pipeline`
choke point (the same place the `Callable` check belongs), plus a witness/control pair.

## WITNESSES DRAFTED AND PRE-VERIFIED

`$SCRATCH/g31/w/1880.py` (`#@ uses no_such_lemma`, expected FAIL) and `1881.py` (the same
file citing the lemma that is actually there, expected PASS). Both VERIFY today — which is
the point of 1880: the route is that it verifies. The patch is
`$SCRATCH/g31/fix_uses.py`, a set membership over `ir_data`'s `#@ lemma` functions at the
`_run_pipeline` choke point (whose mirror twin is `\trusted`, so no re-proof).

## THE FOURTH MEMBER IS MY OWN WORK FROM THIS MORNING

Having written down how to look for the next one — "take each directive whose grammar
admits an identifier, write the version with a name that resolves to nothing, and run it" —
I ran it on the directive I had IMPLEMENTED eight hours earlier:

```python
#@ reveal no_such_function
#@ requires x > 0
#@ ensures \result == x
#@ assigns \nothing
def caller(x: int) -> int:
    return x
```

    [+] Verification SUCCESS! All contracts formally proven.

`#@ reveal` naming nothing is dropped in silence, exactly like `#@ uses`. My repair
collects the module's reveal names into a set and asks whether a function being stubbed is
in it; a name that matches no function anywhere simply never matches, and nothing looks.

`#@ conforms_to NoSuchProtocol` was probed in the same minute and is REFUSED, so the family
is four of five — and the fifth being clean is the useful control: the check IS routine
where someone wrote it.

>>> The lesson I would carry out of this one: **a feature you added today is not exempt
>>> from the audit you invented today.** It was the newest code in the tree and it had the
>>> same hole as the oldest.

## THE SWEEP OVER THE REST OF THE FAMILY — and the result is NOT uniform

Running the same one-line experiment across every directive whose grammar admits an
identifier:

| directive with a name that resolves to nothing | verdict |
|---|---|
| `Callable[[Rekt], int]` | **SUCCESS — silent** |
| `#@ uses no_such_lemma` | **SUCCESS — silent** |
| `#@ reveal no_such_function` | **SUCCESS — silent** (implemented eight hours earlier) |
| `#@ footprint no_such_prop(k)` in a file with NO `#@ happy` declaration | **SUCCESS — silent** |
| `#@ footprint no_such_prop(k)` in a file that HAS one | REFUSED |
| `#@ conforms_to NoSuchProtocol` | REFUSED |
| `#@ verify_module leafmod` (lowercase) | REFUSED (repaired this gen) |
| `\at(x, no_such_label)` | FAILED (fail-closed, not silent) |
| `#@ compose_from NoSuchMixin` | REFUSED |
| `#@ critical no_such_lock` | REFUSED |
| `#@ complete no_such_act, pos` | REFUSED (the documented `_validate_acts` claim CHECKED, not taken on trust) |

FINAL TALLY over the whole directive surface: **four silent, SIX refusing, one failing
closed.** The refusing six are the controls — the check is routine where someone wrote it,
and the four silent ones are four places where nobody did. Note that one of the six
(`#@ complete`) was a DOCUMENTED claim ("unknown names are dropped here and flagged by
Module4 `_validate_acts`"), and it was run rather than believed — which is the discipline
this whole file exists to apply, and the reason the `footprint` row above splits in two.

Two things fall out of the table that a single probe would not have shown:

  * **the check exists where someone wrote it.** `conforms_to` and the happy-gated
    `footprint` both refuse. This is not a design decision anyone took uniformly; it is
    four places where nobody wrote the two lines.
  * **`footprint`'s refusal is GATED ON THE FILE HAVING A HAPPY PROPERTY.** With no
    `#@ happy` declaration at all, an unknown footprint name is silently dropped. Low
    severity — a file with no region discipline has nothing to bypass — but it is the same
    hole, and the fix is to check the name against the (possibly empty) set rather than
    only when the set is non-empty.

The strongest carrier is still `footprint`, and it is worth stating why it is NOT a
soundness route: with a happy property present, a typo is REFUSED, and with none present
there is no obligation to lose. The measured triple is: no footprint -> FAILED; typo'd
footprint -> REFUSED; correct footprint -> SUCCESS.

## THE FAMILY'S PATCHES AND WITNESSES, ALL DRAFTED AND PRE-VERIFIED

| member | patch | witness (FAIL) | control (PASS) | today |
|---|---|---|---|---|
| `Callable[[Rekt], int]` | `fix_callable_scope.py` | 1877 | 1878 | both SUCCESS |
| `#@ uses no_such_lemma` | `fix_uses.py` | 1880 | 1881 | both SUCCESS |
| `#@ reveal no_such_function` | `fix_reveal_name.py` | 1882 | 1883 | both SUCCESS |
| `#@ footprint` with no `#@ happy` in the file | not yet drafted — check the name against the possibly-EMPTY set rather than only when it is non-empty | — | — | SUCCESS |

All in `$SCRATCH/g31` and `$SCRATCH/g31/w`. Every witness VERIFIES today, which is the
route in each case; after the repairs each must be REFUSED and each control must stay
SUCCESS. The three refusals are set memberships over data `ir_data` already carries, all at
the `_run_pipeline` choke point whose mirror twin is `\trusted` — no re-proof, no marker,
no emission move — so they belong in ONE increment.

## THE FOURTH MEMBER'S CAUSE, FOUND — the guard is on the wrong side of an early return

`Module3_Weaver._expand_happy_properties` starts

```python
        if not happy_props:
            return
        funcs = [...]
        # 07-1143 R3 (validation): every `#@ footprint NAME(arg)` must reference a declared
        # PARAMETRIC HAPPY `NAME` — a typo would silently confine nothing (a soundness
        # hole, since the method would appear constrained but get no per-site check).
        param_happy_names = {hp.name for hp in happy_props if hp.param is not None}
        ...
```

**The author already knew — the comment calls it "a soundness hole" — and wrote the guard
two lines below an early return that skips it whenever the file declares no `#@ happy` at
all.** So the one case it misses is a `#@ footprint` written into a file with NO
confinement discipline: exactly the case where the user is most likely to be mistaken about
what they have.

The repair is to hoist the validation above the return; the message already renders an
empty set correctly (`Declared parametric HAPPYs: []`). Patch:
`$SCRATCH/g31/fix_footprint_empty.py`. `_expand_happy_properties`'s mirror twin is
`\trusted`, so the edit owes no re-proof, and the footprint nodes live on the AST
(`fn.csl_footprints`) rather than in the IR, which is why this one stays in place instead
of moving to the `_run_pipeline` choke point with its three siblings.

>>> Worth its own line: **a guard whose comment states the danger is not evidence the guard
>>> runs.** This one has been three lines from a correct implementation, with the right
>>> prose attached, for as long as it has existed.
