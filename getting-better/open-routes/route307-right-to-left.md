# OPEN ROUTE #307 — EFFECTFUL OPERANDS ARE EVALUATED RIGHT-TO-LEFT (Why3 application order), PYTHON IS LEFT-TO-RIGHT
**Status: OPEN (gen #37, 2026-10-23), Severity 1 (broad).** Red-team round 14; driver-reproduced on main (g06b, o01b, q10, q01b rc=0;
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
