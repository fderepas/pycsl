# ROUTE #77 — A SLICE DELETE `del xs[i:j]` IS ERASED TO `Pass`, AND THE READ IS THEN CONSTANT-FOLDED

**STATUS: FOUND AND REPRODUCED 2026-09-11 (gen #8). BOTH DIRECTIONS MEASURED. OPEN — repair
scoped below.**

**CLASS: the #69 class, the serious one** — a FALSE POSTCONDITION about ordinary, TOTAL
Python. No `no_exception`, no memory-model flag, no opt-in of any kind. The program runs to
completion under CPython and returns a different number from the one PyCSL proves.

## THE EXPLOIT IN SIX LINES

```python
from typing import List
#@ ensures \result == 1
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return xs[0]
```

    CPython:  3
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

Why3 even *says so* in a warning on the same run: `unused variable xs`. The delete is erased
and the read is then constant-folded, so the list never reaches the solver at all.

## THIS IS ROUTE #17's DEFECT, ONE STEP OVER — AND THE STEP CROSSES A MODULE BOUNDARY

Route #17/#43 found exactly this for the *element* delete and closed it, in
`module6_whyml/statements.py` (~line 2247), with a refusal whose own comment spells out the
hazard:

> emitting `(); 1` — the delete is a no-op and the read is then constant-folded. ... MEASURED,
> before this refusal: `xs = [1,2,3]; del xs[0]; return xs[0]` proved `\result == 1` while
> Python returns 2.

That refusal is a **blocklist keyed on the emitted string**:

```python
if code.strip() == "()":
    raise PyCSLIRError("`del ...[...]` on a non-dict/set receiver is not modelled: ...")
```

It never fires for the slice form, because the slice form **never reaches Module 6 as a
delete at all**. `frontend/Module5_IREmitter.py::_py_stmt_delete` excludes it one stage
earlier:

```python
if isinstance(tgt, ast.Subscript) and not isinstance(slice_node, ast.Slice):
    ir_stmts.append({"stmt": "DelSubscript", ...})
else:
    # `del name` / `del obj.attr` / `del seq[i:j]` (slice delete) — stays the
    # unmodelled no-op it always was (outside the dict/set item-delete scope).
    ir_stmts.append({"stmt": "Pass"})
```

By the time Module 6 could refuse it, the statement is a literal `Pass`, byte-indistinguishable
from a user's `pass`. **The guard and the hazard ended up in different modules.**

**THE LESSON, BANKED FOR THE SEVENTH TIME AND NOW WITH A NEW EDGE.** Gen #7 wrote: *an
allowlist keyed on syntax fails CLOSED when the hazard moves; a blocklist keyed on syntax
fails OPEN.* Route #17's guard is a blocklist (`code == "()"`), and it failed open exactly as
predicted. The new edge is that **the escape hatch was written down in a comment**: Module 5's
`else` branch names `del seq[i:j]` in prose, four lines under a docstring calling the blanket
no-op "UNSOUND ... a severity-1 fail-OPEN". **A prose carve-out in the module UPSTREAM of a
guard is an unexploited route with a signpost on it.** Grep for them.

## BOTH DIRECTIONS, MEASURED (this is what makes it a route and not a gap)

| # | driver | claim | CPython | PyCSL |
|---|--------|-------|---------|-------|
| d02/e — `del xs[0:2]; return xs[0]` | `\result == 1` | **3** | **PROVED** ❌ |
| e01 — the TRUE twin of the same program | `\result == 3` | 3 | refused (Timeout) |
| e02 — `del xs[0:2]; return len(xs)` | `\result == 3` | **1** | **PROVED** ❌ |
| e03 — the TRUE twin of the len carrier | `\result == 1` | 1 | refused (Timeout) |
| e04 — `del xs[:]; return len(xs)` | `\result == 3` | **0** | **PROVED** ❌ |

The true twin failing in **both** carriers is the point: the emitter does not merely fail to
know the answer, it proves the *wrong* one and refuses the right one.

## CARRIER CENSUS

| carrier | verdict |
|---------|---------|
| LOCAL list, `del xs[i:j]`, element read | **PROVES the false claim** — the exploit |
| LOCAL list, `del xs[i:j]`, `len()` read | **PROVES the false claim** — second carrier |
| LOCAL list, `del xs[:]` (full clear) | **PROVES the false claim** — third carrier |
| SELF-FIELD list, `del self.xs[0:2]` | refused (Timeout) — fails closed, **not** by a guard |
| `del name` (`x = 1; del x; return x`) | **PROVES `\result == 1`**; CPython raises `UnboundLocalError` — see residue (a) |
| `del d[1:2]` on a dict | **PROVES `\result == 1`**; CPython raises `KeyError` — see residue (a) |
| `del obj.attr` then read the attr | refused (Unknown) |

## BLAST RADIUS OF A REFUSAL: MEASURED AT ZERO

    grep -rnE "^\s*del\s+[A-Za-z_][A-Za-z0-9_.\[\]]*\[[^]]*:" --include=*.py \
         test-suite/corpus/ src/self-annotate/ src/pycsl/ src/pycsl_lib/
    -> 0 hits

Zero slice-deletes in either verified corpus, in the self-annotation mirror, in `src/pycsl/`
and in `src/pycsl_lib/`. (There are 5 in the tree overall — `bin/ir-to-rocq-ast.py`,
`bin/pycsl-ir-dump.py`, `lib/inspect.py`, `lib/re/_constants.py`, `lib/re/_parser.py` — none
of which is a verified artifact.) So a refusal is byte-inert **by construction**: the guard
only RAISES or FALLS THROUGH, it never alters emitted text, and no verified program reaches it.

## THE REPAIR, SCOPED

Refuse at the site that erases it — `Module5_IREmitter._py_stmt_delete` — rather than
teach Module 6 to recognise a `Pass` it cannot distinguish. Fail CLOSED with a diagnostic that
names the route, mirroring route #17's wording (Python's slice `del` shifts every later element
left and shrinks the sequence, so a no-op keeps a sequence the run demonstrably does not have).

**The honest cost, stated up front.** `frontend/Module5_IREmitter.py` is MIRRORED
(`src/self-annotate/src/frontend/Module5_IREmitter.py`), and the mirror's `_py_stmt_delete` is
a **verified body port, not a `\trusted` stub**, with a hand-written bespoke Module 6 lowering
(`module6_whyml/functions.py::_emit_py_stmt_delete_bespoke`). So the repair owes:

  1. the identical body change in the mirror;
  2. a `raise` arm in the bespoke WhyML lowering, plus the mirror annotations
     `#@ raises PyCSLIRError when True` / `#@ \diverges` / `#@ sibling_concrete`;
  3. `why3 prove --type-only` on the mirror edit (rule (j));
  4. a whole-file re-proof of the Module5_IREmitter mirror;
  5. the 34-plane battery + IR conformance + the reference suite.

**The capability for step 2 already exists and is documented in the mirror** — `_csl_proj`
(mirror line ~618) is a verified body carrying exactly this annotation triple, and its comment
states the contract: *"the err-divergence arm (message DROPPED, raise takes the exc name only;
the raise path never reaches `ensures`)."* This is a re-use, not a new capability.

**A ONE-TOKEN ALTERNATIVE WAS CONSIDERED AND REJECTED.** Dropping the `and not
isinstance(slice_node, ast.Slice)` conjunct would route the slice form into the existing
`DelSubscript` path and let route #17's `code == "()"` refusal fire, with a one-line change to
the bespoke WhyML (`&& not (is_slice ...)` removed) and no new capability at all. **Rejected:**
for a LOCAL *dict* receiver that path does not fall through to the `()` no-op — it emits a
faithful `map_update_none` keyed on a coerced slice, i.e. it would MODEL `del d[i:j]` as a
key delete. CPython raises there (`KeyError: slice(1, 2, None)`), so that is a new wrong model
traded for an old one. Refuse explicitly instead.

## RESIDUES, WITH REOPENING CONDITIONS

  * **(a) `del name` AND `del obj.attr` ARE ALSO ERASED, and they are a DIFFERENT class.**
    `x: int = 1; del x; return x` proves `\result == 1` where CPython raises
    `UnboundLocalError`; `del d[1:2]` on a dict proves where CPython raises `KeyError`. These
    are route **#71**'s class ("an erased operation trivially satisfies `no_exception`"), not
    #77's — the program is not total, so the value-differential plane rules it OUT OF SCOPE
    and the claim is not a false statement about a terminating run. `#@ no_exception NameError`
    does **not** express the obligation today (pipeline error). **Reopening condition:** any
    change that gives the unbound-name read an exception trigger row, or that admits
    `UnboundLocalError`/`NameError` in `no_exception`, makes these carriers live and they must
    be re-probed together — they share the single `{"stmt": "Pass"}` erasure site.
  * **(b) THE SELF-FIELD CARRIER IS HELD BY A TIMEOUT, WHICH IS NOT A GUARD.** `del
    self.xs[0:2]` is refused, but by a solver Timeout, not by a refusal and not by a type
    error. A Timeout is a *resource* verdict: a faster solver, a smaller VC or a tighter
    trigger set could make it Valid at any time. **Reopening condition:** any prover upgrade or
    VC-volume reduction. It must be covered by the same refusal as the local carrier, not left
    to the clock.
  * **(c) THE SLICE-ASSIGN SIBLING `xs[i:j] = [...]` IS A SEPARATE IR NODE** (`ArraySliceSet`)
    on a different code path and is NOT covered by this route's repair. Probed separately.

## WITNESSES

`scratchpad/w58/b/d02_del_slice.py`, `scratchpad/w58/r77/e0{1,2,3,4,5}*.py`,
`scratchpad/w58/r77/g0{1,2,4}*.py`. Corpus witnesses land with the repair.
