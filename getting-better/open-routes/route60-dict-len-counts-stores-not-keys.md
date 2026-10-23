# OPEN ROUTE #60 — `len()` ON A DICT COUNTS **STORE SITES**, NOT DISTINCT KEYS
# (found 2026-09-10 by relaunch #55, at `cf3d7474`)

## THE HEADLINE

    d: Dict[int,int] = {1: 1}
    d[1] = 2
    return len(d)                 # CPython: 1.   `\result == 2` **PROVES** (Valid, 0.00s).

BOTH DIRECTIONS MEASURED: the FALSE claim proves, the TRUE twin (`== 1`) is Unknown.
Unsound in the SILENT direction — the false claim proves — which is why no gate went red.

## WHERE IT COMES FROM — THE DOCUMENTATION STATES THE FALSE PREMISE OUT LOUD

`docs/pycsl-translational-reference.md` (the §T.5.12q neighbourhood, ~line 2532), describing
the relaunch-#45 fold-invalidation pre-pass:

> "A plain indexed store poisons only the ELEMENT fold (**it does not change the length**),
> which keeps the deliberate dict-store size tracking working."

**"An indexed store does not change the length" is TRUE FOR LISTS AND FALSE FOR DICTS.**
`a[0] = 9` leaves `len(a)` alone; `d[k] = v` ADDS A KEY whenever `k` is absent and leaves the
length alone whenever it is present. The size tracker resolves that by incrementing on every
store site unconditionally — right when the key is new, wrong when it is not.

## THIS IS ROUTE #54's SEMANTICS ON A PATH #54's REPAIR DID NOT EDIT

Route #54 (CLOSED) was the dict **LITERAL** counted by syntactic entries, and its repair gave
the literal fold *Python's own key equality*: keys normalised to their values, size = count of
DISTINCT normalised keys, later entry shadows earlier. **The STORE tracker never got that
equality.** Carrier 3 below is literally #54's bool/int example moved from the literal into a
store, and it is broken again. This is the banked lesson — *a repair covers the PATH it edits,
not the SEMANTICS it means to fix* — recurring on the same route family.

## CARRIER CENSUS (all `--memory-model hoare`, probes in `scratchpad/w55/probe/`)

| # | shape | model | CPython | verdict |
|---|-------|-------|---------|---------|
| 1 | `d={1:1}; d[1]=2; len(d)`            | 2 | 1 | **BROKEN** (`N4`) |
| 2 | `d={}; d[1]=1; d[1]=2; len(d)`       | 2 | 1 | **BROKEN** (`C3`) |
| 3 | `d={1:1}; d[True]=2; len(d)`         | 2 | 1 | **BROKEN** (`C4`) — #54's key equality, store path |
| 4 | `d={1:1}; d[k]=2; len(d)`, `k` param | 2 | 1 when `k==1` | **BROKEN** (`N6`) — unconditional |
| 5 | **`def f(d: Dict, k)`: `d[k]=1; len(d)`** | 1 | caller's size + 0 or 1 | **BROKEN, WORST** (`C6`) |
| — | `d={}; d[1]=1; len(d)`               | 1 | 1 | correct (control, `C5`) |
| — | `d={1:1}; d[2]=2; len(d)`            | 2 | 2 | correct (control, `N1`/`N2`) |
| — | bare `len(d)` on a param, no store   | — | — | REFUSED, type error (`C7`) |

**CARRIER 5 IS THE ONE TO READ.** It is not a key-equality subtlety; the incoming dict is
ignored entirely. The emitted body is the whole argument:

```whyml
  let f (d: ref (map int (option int))) (k: int) : int
    requires { true }
    ensures  { (result = 1) }
    writes { d }
  =
    d := map_update_some !d k 1;
    1                                  (* <- `len(d)` *)
```

`len(d)` is the constant `1`. The map `!d` — which is faithful, and which the caller filled —
is never consulted. `f({5: 5, 6: 6}, 7)` returns **3** in CPython and the model proves 1.

Note the asymmetry that makes this survivable-looking: a bare `len(d)` on a parameter with NO
store is REFUSED (it type-errors reaching for `Array.length`). **A store is what CREATES the
tracker**, so adding a mutation to a function makes an unmodellable read answerable — and
answerable with a constant. A guard that fires *more* the *less* the function does.

## CARRIERS 6 AND 7 — CONTROL FLOW, NOT KEY EQUALITY (added minutes later, same session)

The first census framed this as a key-equality defect. **It is worse than that: the tracker
counts SYNTACTIC STORE SITES, so it is wrong even when every key is distinct.**

| # | shape | model | CPython | verdict |
|---|-------|-------|---------|---------|
| 6 | `d={1:1}; if c>0: d[2]=2; len(d)` | 2 (for ALL `c`) | 1 when `c<=0` | **BROKEN** (`F1`) |
| 7 | `d={}; for i in range(n): d[i]=i; len(d)` | **1 (for ALL `n`)** | `n` | **BROKEN** (`F2`) |

**CARRIER 7 IS THE MOST DAMAGING SHAPE IN THE ROUTE**, because building a dict in a loop and
then asking its size is one of the commonest idioms in Python. The store site inside the loop
body is counted ONCE, so `len(d)` folds to `1` no matter how many iterations run — the emitted
body even warns `unused variable i`. `\result == 1` proves Valid with `requires n > 0`.

Carrier 6 makes the same point on a branch: a store the run never executes is still counted.

**THIS INVALIDATES THE "CARRIERS 1-3 COULD BE FOLDED EXACTLY" READING BELOW.** Exact folding
would have to be sound under key equality AND reachability AND iteration count. Only the
last line of the section below survives: the fold has to become a REFUSAL, or a real
`Map`-cardinality model. Refusal is the only cheap correct answer, and the safe direction.

## CARRIER 4 CANNOT BE FIXED BY FOLDING AT ALL

`d[k] = 2` with `k` a parameter: whether the length grows is undecidable at emission. Any
constant is wrong on some input. So the repair cannot be "make the fold smarter" the way
#54's was — the fold has to become a REFUSAL (or a real `Map`-cardinality model) for every
store whose key is not a literal provably distinct from all keys already tracked. Carriers 1-3 looked foldable
until carriers 6 and 7 (above) showed the fold is also blind to reachability and iteration
count; 4 and 5 were never foldable. REFUSAL is the only cheap correct answer.

## WHAT IS NOT YET MEASURED (next steps, in order)

1. **CORPUS + MIRROR CENSUS.** How many corpus files, and how many of the 53 self-annotation
   mirror files, read `len()` on a dict after a store? If any mirror does, the mirror's own
   proofs may rest on this. THIS IS THE FIRST THING TO RUN — it sizes the repair.
2. `len()` in a SPEC position (an `ensures` over `len(d)`) rather than a body read.
3. The `Set` twin — `annotations.md` §1841 lists `len(s)` as forbidden for sets, so it is
   probably refused, but "probably" is not a measurement.
4. Whether `\length` / the dict truthiness guard (`if d:`) share the tracker — route #55 is
   the truthiness neighbour and may be the same cache.

## STATUS: **CLOSED** at `612013d2` (repair) + `30a4f5e7` (witnesses)

**REPAIRED AS A WHITELIST, per route #42's rule** — the size fold survives a store only
where the emitter can SHOW the post-store size:

  * the name is bound EXACTLY ONCE, to a TOP-LEVEL dict literal (excludes carrier 5, the
    parameter — a dict param has no literal binding, and the `else` branch that INVENTED a
    size of 1 for such a name is gone);
  * EVERY store to it is at the function's TOP LEVEL (excludes carriers 6 and 7 — a store
    inside an `if`/`for`/`while`/`try` is not counted at all, so reachability and iteration
    count are never in question);
  * EVERY store key is a LITERAL (excludes carrier 4 — a symbolic key is undecidable at
    emission, so no constant is defensible);
  * the literal's keys and the store keys are PAIRWISE DISTINCT under **Python's own key
    equality** — route #54's normalisation, so a `Bool` key is the int `1`/`0` (excludes
    carriers 1, 2 and 3).

Anything else is added to the EXISTING `_fold_unsafe_sizes` channel in
`_reset_function_state`, is therefore never registered by `_track_collection_metadata`, and
`len(d)` falls through and FAILS CLOSED — the same behaviour `len(d)` on a dict parameter
WITHOUT a store already had. No new emitter attribute, so no declared frame changed.

**BOTH EDIT HOMES ARE `\trusted` MIRROR STUBS** (`_handle_array_set_stmt`,
`_reset_function_state`), so the fidelity cost is zero — the opposite of route #59's sixth
carrier, whose home is verified verbatim. That asymmetry is worth carrying forward: check
which side of the mirror a guard's home sits on BEFORE costing the repair.

### GATES

  * ALL **31 PLANES GREEN** under `--slow` with `why3` on PATH (includes the fidelity plane
    and `check-mirror-type-only`).
  * **BYTE-INERT ON BOTH CORPORA**: 923/923 `pycsl-reference` and 2204/2204
    `python-reference`, zero differing, zero APPEARED, zero GONE. Because every corpus
    emission is byte-identical, no corpus proof outcome can change by construction.
  * Metric UNCHANGED at markers 459 / grep 484 / offset 25 / unattached 0 — correct, the
    repair adds and removes no `\trusted`.
  * Witnesses `1133`-`1142`, **anti-vacuity verified in BOTH directions**: each of the seven
    negatives PROVES with the two emitter files checked out to the pre-repair commit and
    REFUSES with the repair restored.

### THE GATE DEFECT THIS ROUTE EXPOSED — MORE TRANSFERABLE THAN THE ROUTE

The first repair attempted here was a blunt one (poison the size fold on EVERY dict store).
It measured **byte-inert over "the whole corpus"** — and that was TRUE AND INCOMPLETE.
`bin/byte-diff-sweep.sh` globs ONLY `test-suite/corpus/pycsl-reference/*.py`. The whole
`test-suite/corpus/python-reference` tree — **2217 files, a live proved suite** — is outside
every byte-diff this plane has ever run. The blunt repair broke `python-reference/0050.py`,
a PROVED driver, and the byte-diff could not see it. Measured both ways: `0050` proves at
HEAD and is refused under the blunt patch.

That is route #52's lesson in a new place (*a green byte-diff that examined the wrong
population is not evidence*), and it is a live gap in the plane set right now — the
whitelist that landed is byte-inert on `python-reference` too, but only because I swept it
BY HAND. **A plane that sweeps `python-reference` does not exist. That is the named
follow-up.**

### RESIDUALS, STATED RATHER THAN HIDDEN

  * A dict whose literal has a repeated key and is then stored to (`d={1:1,2:2}; d[1]=9`)
    has an exactly computable size (2) and is nonetheless REFUSED. Completeness loss in the
    safe direction; a follow-up could compute `len(set(keys))` instead of incrementing.
  * A store nested in control flow is refused even when it is provably reachable exactly
    once. Same direction, same remedy available.
  * `del`, a SPEC-position `\length`, and the SET twin all REFUSE independently of this
    repair (measured), so the route's extent really was body-position dict `len` after at
    least one store.
