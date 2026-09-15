# ROUTE #113 — `_coerce_to_int` REPLACES A CALL WITH A HASH OF ITS TEXT when the call's
# lowered text merely CONTAINS A COMMA — and a comma inside a STRING-LITERAL ARGUMENT counts

**Status: CLOSED AND FULLY GATED by gen #23 (2026-09-15)** — see THE REPAIR AS LANDED at the bottom. Original finding preserved below.
**Severity: SEV-1. First-order.** A false postcondition is PROVED; the trigger is a comma in
an ordinary string argument (`g(y, "a,b")`).

## PROVENANCE

Generator `substring-census`. Gen #21's census listed it ("a COMMA in a string-literal
argument replaces the term with a text hash") and never ran it to a verdict. Gen #23 ran it.

## THE MECHANISM, quoted

`src/pycsl/module6_whyml/expressions.py`, the last arm of `_coerce_to_int`:

```
        # Tuple literals (a, b, c) → hash to int
        if "," in whyml_str and whyml_str.startswith("(") and whyml_str.endswith(")"):
            return str(stable_hash(whyml_str))
```

"Is this term a tuple?" is decided by a SUBSTRING TEST over generated text. A call lowers to
`(g !y "a,b")` — it starts with `(`, ends with `)`, and contains a comma inside the string
literal. It is classified as a tuple and **the whole call is replaced by the constant
`stable_hash("(g !y \"a,b\")")`**. The value, the callee's contract, and the dependence on
`y` are all discarded — and two calls with IDENTICAL TEXT over DIFFERENT VALUES get the SAME
constant.

## BOTH DIRECTIONS MEASURED at baseline worktree `21d5029e` (source == HEAD `6f36d67f`)

`c_comma2.py`:

```python
#@ ensures \result == x
#@ assigns \nothing
def g(x: int, s: str) -> int:
    return x

#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    y = x
    xs: List[int] = [g(y, "a,b")]
    a = xs[0]
    y = y + 1
    ys: List[int] = [g(y, "a,b")]
    b = ys[0]
    return b - a
```

- FALSE `\result == 0` — `[+] Verification SUCCESS` (rc=0). **CPython returns 1** (run).
  Emitted: `Array.make 1 (1542663842)` for BOTH literals.
- TRUE twin `\result == 1` — rc=1 (refused).
- CONTROL `c_nocomma2.py` — identical but the string is `"ab"`: emission keeps
  `(g !y "ab")`, the false claim is REFUSED on `f'vc` postcondition (read).

**The only difference between a false proof and an honest refutation is a comma inside a
string literal.** The first probe (`c_comma.py`, `g(x, ...)` vs `g(x + 1, ...)`) fired the
mechanism but the two TEXTS differed, so the hashes differed and the claim was refused — logged
as FAIL-CLOSED because the shape, not a fence, defeated it.

## REPAIR SKETCH (re-derive before landing)

Classify a tuple STRUCTURALLY: a comma at paren-depth 1 OUTSIDE string literals — or better,
from the IR node (`TupleLit`) rather than the text. A call is never a tuple and must pass
through (fail-closed: if it is not int-typed, Why3 rejects it). NOTE this alone does NOT close
route #114: a GENUINE tuple is still replaced by a hash of its TEXT.

---

## SECOND CARRIER — NO STRING NEEDED, AND A PINNED CORPUS FILE ALREADY STANDS ON IT

The instrumented census of the tuple arm (gen #23; baseline worktree, emission of all four
trees: pycsl-reference, python-reference, the mirror, `pycsl_lib`) recorded **10 hits**: 9 real
tuples (population of route #114) and **1 NON-tuple**:

    test-suite/corpus/pycsl-reference/0607.py   (let (_, _r1_) = a[i] in _r1_)

A TUPLE-COMPONENT PROJECTION `a[i][1]` lowers to a `let`-destructuring whose PATTERN contains
a comma. Returned from inside a `try` (`raise (Return ...)` coerces its payload), the whole
projection became `raise (Return 1780430539)`. **0607 is a positive corpus file and passes on
that constant** (`ensures \result >= 0` — true of the hash).

`t_proj.py` (0607's `at_second` with `ensures \result > 1000`, `--memory-model hoare`):
`[+] Verification SUCCESS` rc=0; **CPython returns 20 / 40** (run). The true
`\result == 20 or \result == 40` is refused on the `at_second` postcondition.

So the classifier's population is not exotic: any lowered term that CONTAINS a comma anywhere —
a string literal, a destructuring pattern — and is wrapped in parentheses.

Tuple-arm census rows (the 9 genuine tuples, for #114's blast radius):
`pyref 0150 (1, 2)`; mirror `pure_ast` ×2 (`Seq.snoc !parts <hash>`); mirror `expressions`
×1 (`_pg2_get_1 <hash>` keyed by `(self._current_self_type, !field)`); `pycsl_lib`
`json/scanner` ×2, `json/tool` ×1, `os/UnixInodeFileSystem` ×1, `warn/__init__` ×1.

---

# THE REPAIR AS LANDED — gen #23 (2026-09-15)

Landed with routes #111–#117 as ONE combined battery (commit recorded in `driver-progress.log`).
Every verdict was PREDICTED in the progress log before it ran:
metric 459/484/25/0 · doc-coherency rc=0 · mirror sync 887 verbatim · mirror-check same 3
pre-existing drifts · trusted-raises 13/62 · trusted-reasons 459↔459 · type-only 53, 0
ill-typed · dropped-mutation 0/51/9/0 · byte-diff pycsl-ref 22 MOVED / GONE only 0996 (an
expected-FAIL witness now refused) · python-ref 6 MOVED · mirror emission 7 MOVED, every hunk
read and attributed · suite 3444/3462, the SAME 18 failures, ZERO XPASS · whole-file proofs of
all 7 moved mirrors SUCCESS, 0 bad (statements 17630, expressions 21347, stmt_control_flow
12284, pure_ast 3372, functions 1199, Module5_IREmitter 2109, preamble 216 Valid) · planes
34/34 `ok` COUNTED (after narrowing `check-singleton-constant-lowering`'s baseline: the split arm orphaned two entries whose justifications #115/#116 had just refuted — removed — and renamed the GenExp half's key; constant arms 14 -> 12; emission re-verified byte-identical).

**What landed.** `_coerce_to_int` (live + verbatim mirror): a paren-wrapped term containing a
comma whose HEAD TOKEN is a bare identifier or keyword (`(g ...`, `(let ...`, `(if ...`) is an
application or binder, never a tuple, and passes through unchanged (a non-int term is a Why3
type error). Both carriers are closed and FAITHFUL: `c_comma2_pos` (true `b - a == 1`) and
`t_proj_true` (`\result == 20 or 40`) PROVE where they were refused, 0607 still PASSES — now on
the real projection. Corpus 1309 (XFAIL), 1310 (PASS), 1311 (XFAIL).
