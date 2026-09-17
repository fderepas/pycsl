# ROUTE #177 — a comprehension's element operations carry no `no_exception` obligation

**Status: REPAIR DRAFTED by gen #29 (worktree wtX, branch wip/g29-r177, on top of #176 + #175 alias
carrier).** Severity 1. Generator: carrier of #170 (a missing-key read inside a comprehension caught
by `except KeyError` PROVED), then generalized to declared contexts.

## Measured at `162fe9b7`, each PROVED while CPython raises

    #@ no_exception KeyError           xs = [d[k] for k in ["a", "b"]]
    #@ no_exception ZeroDivisionError  ys = [10 // x for x in [0, 1]]
    #@ no_exception IndexError         ys = [xs[i] for i in range(3)]      (xs = [1])
    #@ no_exception ZeroDivisionError  t = sum(10 // x for x in xs)
    #@ no_exception KeyError           e = {k: d[k] for k in ["b"]}

Emitted: `xs := (list_comp 0)` — an opaque value, no per-element obligation. `int(s)` inside a
comprehension is refused (route #161); `any(10 // x > 1 for x in xs)` is unproved.

## Repair (draft)

`_reset_function_state` (trusted), under an active context (declared or #171-widened): a
ListComp/SetComp/DictComp/GenExp whose element/key/value/conditions/iterables contain a subscript
(IndexError/KeyError), a `/`/`div`/`%`/`**` (ZeroDivisionError), or a tuple generator target
(ValueError) is refused.

Emission inert (corpus/pyref/mirrors). Witnesses 1620-1623 (XFAIL), 1624 (PASS control).
Fast planes/conformance/sync measured together with #178 in wtY: green.
