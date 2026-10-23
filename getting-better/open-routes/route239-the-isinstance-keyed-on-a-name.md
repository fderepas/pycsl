# ROUTE #239 (REPAIRED) — `isinstance(<Any>, T)` IS KEYED ON THE VARIABLE'S NAME, NOT ITS VALUE

**Status: REPAIRED (gen #36, 2026-10-15; opened the same day), Severity 1.** Named as an unprobed residual by the #237/#238 repair
executor; the driver wrote the exploit and reproduced it at HEAD 4b049d8b.

## Witness (PROVED at HEAD rc=0; CPython `f(1, "s")` = 0)
`witnesses-r239/isinstance_any_rebound_name.py`:

    def f(x: Any, y: Any) -> int:      # ensures \result == 1  <-- PROVED
        a = 0
        if isinstance(x, int): a = 1
        x = y
        b = 0
        if isinstance(x, int): b = 1
        if a == b: return 1
        return 0

Emission: both tests are `(typeof_op 120) = 0` — `typeof_op` is a `val function` applied to a constant
derived from the NAME `x`, so rebinding `x` cannot change the answer. Control
`witnesses-r239/control_two_names.py` (`isinstance(y, int)` -> `typeof_op 121`) does not prove (Unknown).

## Repair direction
The type test must be a function of the VALUE (e.g. `typeof_op` applied to the lowered value when it is an
int-erased Any, or a fresh opaque bool per evaluation `(any bool)`), never of the name. Census every
`typeof_op` emission site and any other name-keyed opaque (hashing a variable NAME into an opaque
function's argument is the general shape — grep for it).

## Census — every NAME-keyed opaque (a pure `val function` whose argument, or whose SYMBOL, is
derived from a variable name, so two values bound to one name are one term)
Probed: same name rebound in one function; same parameter name across two calls; loop variable across
iterations; non-`Var` subjects. Ground truth = CPython on every program.

| site (live emitter) | key | exploit at f926a808 | verdict |
|---|---|---|---|
| `_tag_of_value` -> `typeof_op <sum(ord(name))>` (program `isinstance`) | name / `0` for non-Var | rebinding PROVED (2200), loop var PROVED (2204), `xs[0]`/`xs[1]` both `typeof_op 0` PROVED (2203) | **REPAIRED** |
| same, in a CONTRACT (`subtag (typeof_op 120) t`) | name, argument never mentioned | callee precondition discharged by the caller's fact about ANOTHER value PROVED (2201); one postcondition for every actual PROVED (2202) | **REPAIRED** |
| `_lower_getattr` `pycsl_getattr_missing_<hash(repr(expr))>` (pure ctx: constant; else `!_pyobj_state`) | call IR = receiver NAME | `getattr(o,"a"); o = p; getattr(o,"a")` PROVED `x - y == 0` (2205) | **REPAIRED** |
| `_lower_getattr` `pycsl_getattr_unknown_<hash>` (route #197/#213 state-keyed) | receiver NAME + state; a rebinding writes no state | 3-arg form, rebound receiver PROVED (2206) | **REPAIRED** |
| `_expr_to_whyml` read `pycsl_erased_<x>` / `pycsl_erased_str_<x>` (routes #41/#46/#50), binding `x := 0` | name | `x = (1,2); a = x; x = (3,4); b = x; a == b` PROVED (2207); AMBIG `None`/int local read the same constant after `x = 5` and `x = 6` PROVED (2208) | **REPAIRED** |
| `_to_bool` `pycsl_nonempty_<d>` (route #55, `@mutable_state` dict/set param truthiness) | name | not reachable with two different values: a rebinding re-routes the next guard to the value-applied `map_nonempty !d`, an in-place store to a dict PARAM is refused (`in-place mutation of dict/set parameter`), a dict loop variable is an L3-tc refusal, a dict LOCAL takes `map_nonempty` | refused-only / unreachable (unchanged) |
| `in_globals_op <sum(ord(name))>`, `in_scope_op <sum(ord(name))>` (`\in_globals`, `\in_scope`) | name, BY DESIGN (a property of the name) | spec-only, no defining axiom and no decided occurrence of the op anywhere: the only fact ever available is the function's own `requires`, which a caller can discharge only from another occurrence of the same op — a chain that bottoms out at no call site | not exploitable (recorded) |
| `{base}_mem`, `{base}_get`, `{base}_{lit}` (opaque self-map readers) | self-FIELD name | mirror-gated (`_compute_return_type` file / `@mutable_state` aliases); sound while the method does not write that field between reads | mirror-only, not user-reachable (recorded) |
| `pycsl_seeded_map_<hash(repr(seed))>` (`Counter(xs)`, route #48) | seed IR = NAME `xs` | `a = Counter(xs); xs = ys; b = Counter(xs)`: every observable read is refused — `a[1]`, `a == b`, `len(a)`, `1 in a` are L3-tc errors; `a.get(1, 0)` is the effectful `a_get_2` | refused-only (recorded; becomes a route the day a seeded-map read type-checks) |
| `pycsl_getattr_default_<hash(default IR)>` | the DEFAULT's IR, not a name | route #214, OPEN, blocked on local-type inference | out of scope (unchanged) |
| `getattr_2 obj <stable_hash(field)>`, `node_get_1 <hash>`, `<x>_get_N`, `py_isinstance_<C>_<t>_op` | value-applied, or effectful `val` (fresh per call) | — | not name-keyed |

## Repair landed (gen #36, 2026-10-15)
- `isinstance` (`_tag_of_value` + `_handle_isinstance`): `typeof_op` is now POLYMORPHIC
  (`val function typeof_op (x: 'a) : int`) and is APPLIED TO THE LOWERED SUBJECT in both program and
  spec context (`typeof_op !x`, `typeof_op x`, `typeof_op (xs[0])`). Two tests of one unchanged value stay
  one term (control 2211; same actual through a contract, 2212); a rebinding, another actual, another
  iteration or another element are different terms. Chosen over a fresh `(any bool)` because the SPEC side
  needs a logic term that mentions the argument (a fresh value cannot be stated in a contract, and a
  program-only fresh test would have made `requires isinstance(x, int)` unusable by the body).
- `getattr` devices (`pycsl_getattr_missing_*`, `pycsl_getattr_unknown_*`): one more POLYMORPHIC argument,
  the lowered receiver (`args[0]`), in both the constant (pure context) and the `!_pyobj_state` form.
  Route #213's state key is kept (two reads across a write still differ, 1859; no write still agree, 1727,
  2214).
- Erased locals (`statements.py` + `_expr_to_whyml`): a tuple/set/generator binding that lowered to the
  literal `0` now stores a FRESH `(any int)` (per execution — a loop body's binding is a new value each
  iteration), and the per-name read arm is DELETED, so every read is the ordinary `!x`. An AMBIG
  (`None` on one path) local's bindings already stored the real value or the shared `pycsl_none` /
  `pycsl_none_str`, so `!x` is faithful there too — and a COMPLETENESS gain: `x = None; if c: x = 5;
  x = 6; return x` now proves `\result == 6` (2215, FAIL at base). NaN (route #45) and `None#empty`
  (route #44's shared `pycsl_none`) are untouched.
No new axiom, no new refusal or raise; `proof_axiom_allowlist` untouched; ledger stays 3. Live-only edits
(`_tag_of_value`, `_handle_isinstance`, `_expr_to_whyml`, `_handle_assign_stmt` have `\trusted` mirror
twins; `_lower_getattr` has none), all inline.

## Witnesses (corpus, `gen36_r239`)
False claims, each PROVED at f926a808 and FAILING after on exactly the unproved goal named:
2200 (post), 2201 (`m`'s call precondition), 2202 (post of `m`), 2203 (post), 2204 (loop invariant
preservation), 2205 (post), 2206 (post), 2207 (post), 2208 (post). Controls: 2210 two distinct names
(FAIL at base and after — independence kept), 2211/2212/2213/2214 (PASS at base and after), 2215
(value-faithful, FAIL -> PASS). CPython ground truth run for all fifteen.

## Gates (logs: `/tmp/claude-1000/.../scratchpad/r239/`)
- Witnesses: 9/9 false claims PROVED at f926a808 and FAIL after; controls as recorded above (`new_base.log`,
  `m1_after.log`, `ground.py`).
- Corpus byte-diff vs a fresh f926a808 worktree: root 1535 baseline / 1550 candidate `.mlw`, 19 MOVED, 0 GONE,
  0 APPEARED, 15 new sources (2200-2215); pyref 2198/2198, 3 MOVED (0046, 0048, 0138). Every hunk is one of the
  three corrections (`typeof_op <value>`; getattr device + receiver; erased `(any int)` binding + `!x` read).
  M1: all 22 moved files re-proved at base and after, verdicts identical (0634, 0884, 1041-1046, 1072, 1085, 1086,
  1088, 1089, 1543, 1691, 1859, 1860 FAIL/FAIL; 1727, 1913, pyref 0046, 0138 PASS/PASS; pyref 0048 FAIL/FAIL — a
  pre-existing L3-tc error, `int` vs `int -> option`, identical at base; 1088 fails closed on its pre-existing
  type error both sides).
- Mirror: 12 MOVED (`frontend/{Module2_Parser,Module5_IREmitter,desugar,exec_splice,module_collect,monomorphize,
  pure_ast}`, `module6_whyml/{expressions,functions,statements,stmt_control_flow,types}`), each `why3 --type-only`
  clean; the 25 functions holding a moved line re-proved per function (`why3 prove -a split_vc -P z3 -t 30 -G`):
  29403 goals, 0 non-Valid. One mirror hunk is a side effect worth naming: in `desugar`/`exec_splice`,
  `isinstance(getattr(x, "func", None), ast.Name)` was the CONTENTLESS `isinstance_op 0 0`; the getattr
  device is now an application, so route-#16 widening 5 reads its declared return type and the test becomes the
  receiver-carrying (effectful) `py_isinstance_Name_int_op (pycsl_getattr_unknown_N !sub)`.
- Planes 61/61. `check-constant-fallthrough` objected to `_tag_of_value`'s new `""` fall-through; the ratchet
  was right to ask, the use site was checked (its one caller replaces `""` before emitting), row added with that
  evidence. Slow plane `check-getattr-erasure`: re-measured (`--emit-baseline`): +3 witness rows (2205, 2206,
  2214); `desugar`/`exec_splice` UNKNOWN 3->4 is ONE more lowering of the SAME source site (the widening-5 trial
  now accepts, census measured line by line); `stmt_control_flow` ABSENT 1->2 was ALREADY RED at f926a808
  (measured in the baseline worktree), not this change. `check-open-route-carriers` OK (route #214's carrier is
  the default-keyed device, untouched). `check-hashed-literal-purity` OK over the after-emission. Sync + mirror
  check rc=0. Ledger 3.

## Residuals and further unsound shapes found while probing (NOT name-keyed; not repaired here)
- **`isinstance(x, bool)` is `isinstance(x, int)`** (decision A: `bool` collapses to `tag_int`). PROVED at the
  repaired tree: `def f(x: int)`, `if isinstance(x, bool): return 1`, `\result == 1`; CPython `f(5)` = 0
  (`scratchpad/r239/w/e/extra/q_bool.py`). A typed `int` subject decides `bool` TRUE. Needs its own route.
- **A generator argument to an `Any` parameter is the literal `0`** at the call site (`g(v for v in [1])` emits
  `g 0`), so a callee contract over `x == 0` is discharged for a generator: `m() == 1` PROVED, CPython 0
  (`extra/q_genexp_arg.py`). Route #41's erasure, one position over (call actual, not local binding). Needs its
  own route.
- `pycsl_getattr_default_<hash(default IR)>` (route #214) remains open as recorded there.
- Value-application is sound only while no two Python values of different types reach `typeof_op` as the SAME
  int: `True`/`1` collide (harmless while `bool` collapses to `int`, see above — it would matter the day that is
  fixed), `None` is the opaque `pycsl_none`, erased values are fresh `(any int)`; a string literal to an `Any`
  parameter is refused (routes #200/#202). The generator-actual `0` above is the one live collision, and it is
  unsound without `isinstance` already.
