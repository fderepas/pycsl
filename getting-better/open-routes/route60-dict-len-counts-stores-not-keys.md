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
