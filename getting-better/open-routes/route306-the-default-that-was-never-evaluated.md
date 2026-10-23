# OPEN ROUTE #306 — `d.get(k, default)` EVALUATES `default` LAZILY (Python evaluates it eagerly): its writes and its raises vanish
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 13; driver-reproduced on main (5/5 rc=0; CPython violates).
Witnesses `witnesses-r306/`: `return d.get(1, 10 // x)` under `no_exception \all`, `requires 1 in d` proves (e22; CPython f({1:4},0)
raises ZeroDivisionError); index default `xs[i]` (e27, in_bounds checked only on the None arm); a callee `bump(xs)` with declared
`assigns xs[0]` passed as the default never runs in the model, so `ensures xs[0] == 0` proves WITHOUT no_exception (e10, e23); aliased
call (e32). e31 (`self.d.get`) lowers the same lazy way (failed only for lack of field knowledge; likely exploitable with an invariant).
Mechanism: expressions.py (~13934) emits `(match Map.get d k with | Some v_ -> v_ | None -> <default> end)`, so every effect and every
exception obligation of `<default>` lives on the None arm only. TypedDict `.get` evaluates eagerly (held); getattr(o,a,dflt) refused.
Repair: bind the default first (`let dflt = <default> in match ... | None -> dflt end`), preserving left-to-right order (receiver, key,
default) — or refuse a non-pure default. Census every lazy-arm lowering of an eagerly-evaluated Python argument (dict.get, dict.pop
default, setdefault, next(it, default), getattr default, min/max default=, str methods with default args).
