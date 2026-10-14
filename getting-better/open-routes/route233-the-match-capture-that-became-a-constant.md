# OPEN ROUTE #233 — THE `match` CAPTURE NAME THAT BECAME A MODULE CONSTANT

**Status: REPAIRED (gen #36, 2026-10-14), Severity 1.** Was: OPEN (gen #36, 2026-10-14). Found by the route #232 executor (same
mechanism family: a binder the front end fails to scope falls through to `_handle_var_expr`'s
last-branch opaque `val constant`); driver reproduced at HEAD 1362a212.

## Witness (PROVED at HEAD; CPython f(0) returns -1)
`getting-better/open-routes/witnesses-r232/match_capture_read_as_constant.py`:

    #@ ensures \result == 0
    def f(x: int) -> int:
        r = 0; s = 0
        match x:
            case y: r = y
        match x + 1:
            case y: s = y
        return r - s

## Mechanism
The capture `y` is not bound by the `match` lowering; both reads of `y` resolve to ONE opaque
`val constant y`, so `r - s = y - y = 0`.

## Repair direction
Bind capture patterns (`case y:`, `case [a, b]:`, `case C(x=v):`, `case _ as v:`) to the subject
(or the matched component) as real locals, or refuse unbound captures fail-closed. Also audit the
opaque-constant fallback: it is sound ONLY for a genuine immutable module global — any other
unscoped name should be refused.

## Census (at 87ff222f / 75e2ebe8)
`match` statements: pycsl-reference 31 (bare capture 1 — `1520`, route #153's shape; `as` 0;
constructor patterns 55 arms with 25 nested captures; guards 1 — `0531`; or 2; sequence 1 —
`1011`, R30-refused); python-reference 13 (bare capture 3 — `0193`/`0194`/`0198`; `as` 1 —
`0196`, R30-refused; sequence 4; mapping 1 — parse-refused; class 1; guard 1 — `0193`);
mirror 0; `src/pycsl_lib` 0.

## Related shapes probed (87ff222f, corpus language)
| shape | verdict at base |
|-------|-----------------|
| bare capture `case y:` (witness) | **UNSOUND** — PROVED `r - s == 0` (CPython -1) |
| capture read after the `match` | **UNSOUND** — same constant (1989) |
| `case 1 \| 2 as y:` / `case (1 as y) \| (2 as y):` | not bound (opaque `y`), true claims unprovable |
| guarded capture `case y if y > 10:` then `case _: return y` | **UNSOUND** — guard/body read the stale local; PROVED `\result == 0` (CPython 5) (1991) |
| sequence `[a, b]` / mapping `{"k": v}` / `C() as k` alone | refused (R30 poison / parse) |
| constructor capture `case Some(v):` read INSIDE the arm | faithful (Why3 pattern variable) |
| constructor capture read AFTER the `match` | **UNSOUND** — PROVED `r - v == 0` (CPython -1) (1993) |
| constructor capture that is also a local | fail-closed (Why3 type error) |
| guarded constructor arm followed by another constructor arm | **UNSOUND, different mechanism** → route #234 (1996) |

## Fallback audit (`_handle_var_expr` last arm; env-gated logging hook over both corpora, not committed)
86 hits / 53 files. Who reaches it: native-arm constructor captures (`n`, `v`, `m`, `a`, `b`, `l`,
`r`, `t`, `rest`, `f` — bound by the Why3 pattern, sound in-arm), lambda parameters (`a`, `x`, `y`
— bound by `fun`, sound), type names used as values (`int`, `str`, `dict`, `list`, `object`,
`C`), synthesized names (`pycslrsixseven0x`, `a[_fi]`, `(- 1)`, `1`), genuine module/imported
globals (`os`, `http`, `OP`, `_keyword`, `_g`, `NotImplemented`), and the match captures this
route repairs. Probed binders: comprehension vars, walrus, for-target after the loop, star
targets `a, *b`, tuple for-targets — do NOT reach it (scoped); `global`/`nonlocal`/closures and
`with ... as v` — refused upstream; `del` — the accepted UnboundLocalError residue of route #80;
class-body names — no conflation found; **`except E as e` — UNSOUND** (two different exceptions
stored as `a = e` / `b = e` PROVED `a == b`; 1995), repaired here (same mechanism). A blanket
fail-closed fallback for "not a module-level global" is NOT safe: the population above includes
in-arm pattern variables, lambda parameters and type-name values that the emission relies on.

## Repair landed (gen #36, 2026-10-14)
* Module 5 `_build_function_ir` (inline post-pass over the function IR; mirror `\trusted`): a
  capture whose path from the arm head runs only through `as`/or-patterns binds the SUBJECT, and
  becomes `y = <subject>` at the head of the arm body — a real local (read after the `match`
  too). Refused fail-closed: a guarded capture arm, a subject that is not side-effect free
  (Var/literal/BinOp/UnaryOp/Attribute/FieldGet/Subscript/Tuple only), a capture of a `global`
  name. A capture nested in a constructor pattern must be used only inside an arm that binds it
  (read elsewhere, in a contract, or assigned anywhere → refused).
* Module 6 `_render_match_pattern` (mirror `\trusted`): an arm-head capture renders as its inner
  pattern (or `_`) in a native `match`, so it does not shadow the bound local; nested captures
  still bind.
* `pycsl.py::_run_pipeline` (mirror `\trusted`): a read of an `except ... as e` name inside its
  handler, in a non-trusted function, is refused (`PYCSL-R233-EXCEPT-AS-READ`); 0 in either corpus.
* Route #234 (guarded constructor arm fall-through) repaired in the same post-pass.

Witnesses 1986–1999: FAIL 1986/1989 (proof), REFUSED 1991/1992/1993/1994/1995/1996, PASS
1987/1988/1990/1997/1998/1999. At 87ff222f: 1986/1989/1991/1993/1995/1996 PROVED (unsound),
the six PASS witnesses FAILED (unprovable), 1992/1994 FAILED.

Gates (gen #36, base worktree at 75e2ebe8): corpus byte-diff 0 MOVED / 0 GONE / 0 APPEARED over
1442 (+8 new witness emissions; `1520` refused on both sides); pyref 2 MOVED / 1 GONE of 2199 —
`0194`/`0198` now bind the capture (`let n = ref 0 ... n := !x`; both still FAIL as expected and
as at base, on the pre-existing value-`if` without `else` of a one-arm chain), `0193` GONE (guarded
capture refused; expected FAIL either way) — no verdict flipped toward PASS; mirror 2/53 MOVED, 0
GONE (`frontend/__init__`, `frontend/ir_resolve`: the imported, UNCALLED `val
pycsltojsonemitter___build_function_ir` now returns `map string (option int)`, matching its
`Dict[str, Any]` annotation; both type-check; `frontend/__init__` whole-file re-proof VERIFIES at
base and candidate). IR conformance 38/38 + 38/38; mirror sync 905/905, mirror-check 53/53; fast
planes 61/61 rc=0; refusal-witness coverage 216 demonstrated / 5 (census `--append-new`: 8 rows);
advice audit 135/138 (the two new advice-bearing sites FOLLOWABLE); doc-coherency OK.
Whole-file re-proof OWED: `frontend/ir_resolve` (VC-identical — the only diff is the uncalled
`val`'s return type — but timed out at 3000s at base AND candidate under load ~18);
`frontend/Module5_IREmitter` / `pycsl` / `module6_whyml/stmt_control_flow` mirrors are untouched
(all changed live methods are `\trusted` there).

Open residue: a single-arm value chain (`match 5: case x: return x`) still emits a value `if`
without `else` (fail-closed type error, `pyref 0194`/`0198`); a capture read where no arm bound it
is the accepted UnboundLocalError residue (route #80 stance); constructor-arm `case k:` beside
constructor arms binds `k` as an `int` ref (fail-closed type error for a datatype subject).
