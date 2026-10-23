# OPEN ROUTE #307 — EFFECTFUL OPERANDS ARE EVALUATED RIGHT-TO-LEFT (Why3 application order), PYTHON IS LEFT-TO-RIGHT
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1 (broad).** Red-team round 14; driver-reproduced on main (g06b, o01b, q10, q01b rc=0;
CPython violates). 20 witnesses in `witnesses-r307/`.
Minimal witness (no calls): `x = 0; return x - (x := 1) + 1` with `ensures \result == 1` proves (CPython returns 0): emitted
`(!x - (begin x := 1; !x end)) + 1`, and Why3 evaluates application arguments right-to-left. Also: walrus (q16, t05 if-condition,
q18 call arg), binop/comparison of two effectful calls (o01b, o02b, o12), call arguments (o10), if-condition (q05), read then
call (q08b, r08 `xs[0] + inc(xs)`, q14 `d[1] + setd(d)`), method/field (g04, g05), dict literal key/value (r01 `{inc(): inc()}`),
builtin args (r02 min), returned tuple (t04), augmented assignment (q10 `xs[0] += inc(xs)`, q11 `k.n += k.bump()`); exception
order (q01b: `boom(ys) + inc(xs)` in try/except — Python raises before inc runs; the model runs inc first, a never-happening write
is proved). Near-miss q17: `range(f(), g())` let-binds end before start.
Repair: in the emitter, whenever an expression has >= 2 operands of which any later one is effectful (writes, raises, walrus,
call with non-empty assigns/raises, or a read of a location a later operand may write), let-bind the operands LEFT-TO-RIGHT into
fresh temporaries (`let a1 = <op1> in let a2 = <op2> in f a1 a2`), or refuse. Census all n-ary emission sites (binops, compare,
calls/method calls incl. receiver, subscripts, dict/list/tuple/set literals, f-strings, builtins, range args, aug-assign).

## REPAIR (2026-10-23, r307 executor off f48adff0; commits 1a4ffe70 + 68928c2f + 48c1bbf1 + 8935a114 + 8210ed7d + 8e7d8f44 + e149b828 + route docs)
**Why3 order spike (Why3 1.8.2, alt-ergo/z3):** `sub (x := 1; !x) (!x)` = 1 and `(begin x := 1; !x end) - !x` = 1 (RIGHT-TO-LEFT
application arguments and infix operands); `((x := 1; !x), !x)` = (1, 0) (tuples RTL); `try (raise E) + (x := 1; !x) with E -> !x`
= 1 (the later operand's write happens BEFORE the earlier operand's raise); `a[(x := 1; !x)] <- !x` stores the pre-write value
(value before index). `let a = e1 in let b = e2 in f a b` is left-to-right. So the repair let-binds.

Probe table (`pycsl.py` whole-file, rc; CPython ground truth in each corpus file's `__main__`):

| witness | f48adff0 | after |
|---|---|---|
| 3890 g04 `k.bump() - k.bump()` | PROVED | FAIL |
| 3891 g05 `k.n + k.bump()` | PROVED | FAIL |
| 3892 g06b `x - (x := 1) + 1` | PROVED | FAIL |
| 3893 o01b `setten(xs) + settwenty(xs)` | PROVED | FAIL |
| 3894 o02b `inc(xs) - inc(xs)` | PROVED | FAIL |
| 3895 o10 `sub(inc(xs), inc(xs))` | PROVED | FAIL |
| 3896 o12 `inc(xs) < inc(xs)` | PROVED | FAIL |
| 3897 q01b `boom(ys) + inc(xs)` in try/except (raise must preempt the write) | PROVED | FAIL |
| 3898 q05 if-cond `inc(xs) > inc(xs)` | PROVED | FAIL |
| 3899 q08b `xs[0] + inc(xs) * 2` | PROVED | FAIL |
| 3900 q10 `xs[0] += inc(xs)` | PROVED | FAIL |
| 3901 q11 `k.n += k.bump()` | PROVED | FAIL |
| 3902 q14 `d[1] + setd(d)` | PROVED | FAIL |
| 3903 q16 `(x := 5) + x` | PROVED | FAIL |
| 3904 q17 `for i in range(inc(c), inc(c))` (near-miss) | FAIL | REFUSED |
| 3905 q17b `range(inc(c), inc(c) + 5)` first iteration | FAIL | REFUSED |
| 3906 q17c `len(range(inc(c), inc(c)))` | FAIL | FAIL (now sequenced) |
| 3907 q18 `sub(x, (x := 5))` | PROVED | FAIL |
| 3908 r01 `{inc(xs): inc(xs)}` | PROVED | FAIL (dict fold sequenced) |
| 3909 r02 `min(inc(xs) * 10, inc(xs))` | PROVED | FAIL |
| 3910 r08 `ys[xs[0]] + inc(xs) * 0` | PROVED | FAIL |
| 3911 t04 `return c[0], inc(c)` | PROVED | FAIL |
| 3912 t05 if-cond `x < (x := 1)` | PROVED | FAIL |
| 3925 `has1(mk(xs), inc(xs))`, effectful dict-returning first argument | FAIL (contract unprovable through the dropped dict) | REFUSED |
| CONTROLS (CPython values): 3913 walrus, 3914 calls, 3915 read-then-call, 3918 aug elem, 3919 field read, 3920 call args, 3921 tuple, 3923 min, 3924 walrus lhs | FAIL (model was RTL) | PASS |
| CONTROL 3916 exception order (`boom` returns only when `b[0] != 0`) | FAIL | PASS |
| CONTROLS 3917 pure operands / ordinary arithmetic (emission unchanged), 3922 `range(0, inc(c))` not refused | PASS | PASS |

All 20 route witnesses rc=0 -> rc!=0; the q17 near-misses are now REFUSED; every control passes.

Rule (inline in `_expr_to_whyml`, the one choke point every operand passes through, whose mirror twin is `\trusted`; no new
def/field; one new raise site; ledger 3; no IR change):
- n-ary program nodes: BinOp (not the lazy `and`/`or`), StrConcat, Subscript (value, index), Slice, Call (receiver, args,
  keyword values), Tuple/ArrayLit/SetLit/MkTuple, DictLit (k0, v0, k1, ...), FString. Spec contexts untouched.
- EFFECTFUL operand: contains a walrus/yield/await, or a call not known pure. Known pure = a module function or `self.` method
  whose contract is `assigns \nothing` with no `raises` (not `diverges`), or a builtin (`len abs isinstance issubclass getattr
  hasattr callable type id range sorted list tuple set frozenset dict sum any all enumerate zip reversed`, `min`/`max` with >= 2
  positional args, `bool` absent a user `__bool__`/`__len__`) or str/dict query method no user function shadows. Arguments of a
  pure call are still walked.
- With k the last effectful operand, operands 0..min(k, n-2) that are not INERT (literal, unary op on a numeric literal, a
  literal display, or a name read when the node has no walrus and the name is not `#@ shared`) and are followed by a non-inert
  operand are bound to `_pycsl_seq<hash>_<i>` and the node is re-emitted with them MARKED (a marked operand emits as its binder).
- REFERENCE vs VALUE: an operand with container-type evidence (field / getattr field / dict element / call annotated
  dict/list/set/Mapping/...) is left INLINE, where Python observes a container's contents; if it is itself effectful -> REFUSED.
- An operand the lowering DROPS (e.g. `(any_map ())`, an opaque stub ignoring keywords) keeps only its binder; one RE-DERIVED
  from its shape (binder unused but its text present) -> REFUSED.
- Sites outside the choke point: the dict-literal assignment folds (`_build_dict_literal_map`, `_build_pyval_inner_map`, no
  mirror twin) let-bind every lowered key/value in Python order when the choke point finds the display order-sensitive;
  `for ... in range(start, stop)` (`_classify_iterable`, `\trusted` twin, now raising only via `_expr_to_whyml`) is REFUSED when
  order-sensitive (the header binds `stop` first). Refusals share one site: "operand evaluation order is not modelled here".

CENSUS of n-ary emission sites (probe-measured, `scratchpad/r307/census/` of the executor): binop / compare / compare chain
(`_pycsl_cmp` temps + sequencing) / call args incl. method receiver / builtin args (min, max, abs, len, sum, divmod, pow,
round, int, str.format) / f-string / str concat / list / tuple / set literal / record constructor / `list.append` arg /
while- and if-conditions / ternary branches / returned tuples / aug-assign value (`xs[0] += v`, `k.n += v` lower to a store
of a sequenced BinOp) — SEQUENCED. Dict literal (fold) — SEQUENCED. range(start, stop) header — REFUSED. Plain store
`a[i()] = v()`: Why3 order (v, i, a) equals Python's (v, a, i) for a name target — faithful. Slice bounds inside a subscript
(`ys[a:f()]`) are decomposed by the slice lowering without reaching the choke point — RESIDUAL (the measured probe is an
L3-tc failure, fail-closed, at base and after).

Blast radius: corpus root 18 MOVED / 0 GONE / 0 APPEARED (2049 base / 2082 candidate, 33 new sources): 0057 0063 0170 0171 0175 0177 0181 0185 0839 0878 0880 2162 2183 2781 3570 3571 3575 3810; pyref 0/0/0 (2186/2186); mirror 10 MOVED / 0 GONE / 0 APPEARED (53/53): errors, Module3_Weaver, Module5_IREmitter, monomorphize, pure_ast, expressions, statements, stmt_control_flow, struct_format, proof2why3/parser — 9 explained by binder inlining, Module5_IREmitter by binders + one unused `val ast_Name_0` declaration (a dropped keyword operand); all 10 L3-tc OK. Every root mover is explained mechanically
(inlining every `_pycsl_seq`/`_pycsl_dk`/`_pycsl_dv` binder reproduces the base text byte-for-byte; 3 also gain one unused
abstract `val` declaration from the order probe). Movers re-proved base vs after: 13 PASS -> PASS (0057 0063 0170 0171 0175 0177 0181 0185 0839 0878 0880 2781, 3575), 5 expected-FAIL FAIL -> FAIL (2162 2183 3570 3571 3810). No previously-proved corpus file
now fails; no latent false proof surfaced.
Gates: witnesses rc=0 -> rc=1 (table); controls PASS; byte-diff-compare root rc=0 with the 18 movers declared `--expect-moved`, pyref rc=0; mirror-emit-sweep base/after rc=0, compare `--min-files 50` rc=0 with the 10 movers declared; check-self-annotate-sync.sh rc=0 (926 un-trusted methods verbatim; `_expr_to_whyml` / `_classify_iterable` twins `\trusted`, the dict-fold builders have no twin); self-annotate-mirror-check.sh rc=0; run-soundness-planes.sh fast 61/61 rc=0 (first run 60/61: core-only golden 0057 moved by design, regenerated in e149b828); doc-coherency --check rc=0; check-assumed-facts rc=0; trusted-raises-honesty rc=0 (61 silent, ratchet 61 — the range refusal raises from `_expr_to_whyml`); trusted-frame-honesty rc=0 (no new field); check-refusal-witness-coverage rc=0 (252 demonstrated / 5; census rows for 3890-3912 and 3925 measured by `_census_row`). Ledger 3. Docs: translational reference §T.6.18.
OWED: whole-file proofs of the 8 long mirror movers — `cd <worktree> && HEAVY_LOW=1 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/<f>.py --import-path src/pycsl` for <f> in frontend/Module3_Weaver, frontend/Module5_IREmitter, frontend/monomorphize, frontend/pure_ast, module6_whyml/expressions, module6_whyml/statements, module6_whyml/stmt_control_flow, proof2why3/parser. Proved here: errors.py rc=0, module6_whyml/struct_format.py rc=0.
Residuals: (1) unknown-typed alias operands (`Any` field/element/call result) are BOUND — a value-modelled container behind
an unknown type would be snapshotted; (2) a container left inline is read late, which is wrong only if a later operand REBINDS
the field/name holding it (identity change); (3) `@mutable_state` dict literals (IR-node constructions, mirror-only) keep
their unsequenced emission; (4) slice bounds; (5) user dunder dispatch of an operator (`a + b` -> `__add__` with effects) is not
classified effectful; (6) implicit-exception ORDER between two non-call operands (`xs[i] + d[k]` under a try that catches only
one of IndexError/KeyError) is unchanged; (7) aug-assign / subscript-store with an effectful INDEX is route #308's site.
SUSPECTED (not this route): `t = (inc(xs), 0)` assigns the havoc `(any int)` and DROPS the call's effect — `xs[0] == 0`
PROVED at f48adff0 (CPython returns 1): a NEW false proof, effect erasure rather than order (repro `/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/r307/census/base/e_tuple_drop.py`).
