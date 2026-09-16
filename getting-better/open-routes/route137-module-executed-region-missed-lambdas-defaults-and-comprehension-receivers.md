# ROUTE #137 — route #135's "module-executed region" missed lambda bodies, def defaults, and every receiver binding form its author did not picture

**Status: CLOSED AND FULLY GATED (gen #26).** Severity 1, order 2 (the carrier IS a campaign
artefact: gen #25's own #135 repair, one day old). Both directions measured at HEAD
`ddab1309`.

## What #135 established, and where its walk stopped

Gen #25 closed route #135 with the right key: **module-scope and class-body code is never
lowered, so the weaver is its only fence**, and an attribute write there is allowed only on
a receiver the file can describe as fresh. Two mechanisms implement that:

* a WALK that decides which nodes belong to the module-executed region, and
* `_nb_fresh_ok`, a map from receiver NAME to "this name is bound only to literals or to
  fresh instances of a class defined in this module".

Both were incomplete, in the two ways the campaign has now seen repeatedly.

### (a) the walk `continue`d on `FunctionDef` and `Lambda`

```python
if isinstance(_nb_y, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
    continue
```

A def's BODY genuinely does not run at module scope — but its **defaults, its keyword
defaults, its annotations and its decorator expressions all do**, and a LAMBDA called in
place runs its body immediately. Three shapes therefore never reached the sink at all:

| witness | shape | model | CPython |
|---|---|---|---|
| 1389 | `(lambda m: setattr(m, "inc", plainlib.dec))(plainlib)` at module scope | `plainlib.inc(3) == 4` | 2 |
| 1391 | the same lambda in a CLASS BODY | `== 4` | 2 |
| 1392 | `def h(z: Any = (lambda m: setattr(m, "inc", plainlib.dec))(plainlib))` | `== 4` | 2 |

1389 also slipped #119 rule (6), which **exempts a parameter receiver** — so the lambda's
`m` was invisible to both fences at once.

### (b) `_nb_fresh_ok` enumerated five binding forms

`Assign`, `AnnAssign`, `NamedExpr`, `For`, `withitem`. A name bound by anything else fell
through to the `not _nb_has_star` DEFAULT — i.e. **FRESH**:

| witness | shape | model | CPython |
|---|---|---|---|
| 1390 | `_junk = [setattr(m, "inc", plainlib.dec) for m in [plainlib]]` | `plainlib.inc(3) == 4` | 2 |

Here the sink DID see the `setattr`; the comprehension target `m` was simply never recorded.

### (c) every namespace guard keys on a builtin's SPELLING

Found by carrier-rerun on THIS route's own first cut, before any verdict was read:

| witness | shape | model | CPython |
|---|---|---|---|
| 1393 | `sa = setattr; sa(plainlib, "inc", plainlib.dec)` | `inc(3) == 4` | 2 |
| 1394 | `ex = exec; ex("N" + " = 5")` | `f() == 3` | 5 |
| 1395 | `import builtins; builtins.setattr(...)` | `inc(3) == 4` | 2 |
| 1396 | `getattr(builtins, "set" + "attr")(...)` | `inc(3) == 4` | 2 |

### (d) the SUBSCRIPT sink enumerated the dict spellings too

#118's namespace-dict rule lists `globals()[k]`, `vars()[k]`, `<mod>.__dict__[k]`. Two more
expressions denote that same dict:

| witness | shape | model | CPython |
|---|---|---|---|
| 1402 | `f.__globals__["N"] = 5` on a module `def` | `f() == 3` | 5 |
| 1403 | `inspect.currentframe().f_globals["N"] = 5` | `f() == 3` | 5 |

A module/class-scope SUBSCRIPT store is now keyed on the PATH being written — its receiver
must be a name the file can describe — exactly like the attribute sink. Census of non-Name
receivers: 2 in pycsl-reference (1326, 1351, both already expected-FAIL), 0 elsewhere.
`D = {}; D["a"] = 1` and `XS = [0, 0]; XS[0] = 7` at module scope still verify.

#118's namespace-dict rule, #119's `setattr`/`delattr` rule, #127's computed `getattr`,
#135's sink and both of this route's new arms all name the builtin. ONE alias defeats all
of them simultaneously.

## The repair

1. The module-executed region now includes **lambda bodies** (fail-closed: whether a lambda
   is called in place cannot be read off the syntax), a def's **defaults / kw_defaults /
   annotations / decorators**, and a class's **decorators / bases / keywords**. A def's
   BODY still stays out.
2. `_nb_fresh_ok` now records `AugAssign`, `comprehension`, `ExceptHandler` / `MatchAs` /
   `MatchStar`, `Import` / `ImportFrom` and **lambda parameters** as NOT fresh.
3. A namespace-reaching builtin (`exec eval setattr delattr globals vars locals getattr`) is
   refused when READ AS A VALUE or reached as an ATTRIBUTE; a `getattr` on
   `__builtins__` or on an IMPORTED name, used as a CALLEE, is refused too.
4. A module/class-scope **subscript** store/delete is keyed on the path, like (3)'s
   attribute sink.

## Two misses, both caught by the mirror emission diff — and both worth keeping

* **draft-4** refused EVERY `getattr(...)(...)`. The prediction "census 0 sites" rested on a
  listing I had **truncated myself**: 333 `<name>(...)(...)` sites, first ten printed, all
  `_N(cls)(...)`. The real `getattr(obj, name)(...)` population is 2 in the mirrors and 5 in
  `src/pycsl` — the emitter's own `getattr(self, handler_name)(node)` dispatch — and the
  sweep came back **FOUR GONE mirrors**. Scoped to a namespace receiver in draft-5.
* **draft-5** used two NESTED `def`s inside `process`. The documented hazard is about
  `check-mirror-coverage`; the *emission* cost is that both were lifted to methods and
  emitted as two extra abstract `val`s — **2 MOVED** in `frontend/__init__` and
  `frontend/ir_resolve`, the two mirrors that ingest Module3. Inlined in draft-6.

## Lessons

> **A REPAIR'S OWN WALK IS A COLLECTOR, AND A COLLECTOR'S SKIP LIST IS A CLAIM.** #135's
> `continue` on `Lambda` and `FunctionDef` read as "function code is out of scope"; what it
> actually said was "a def's defaults and a called lambda's body are not module code", and
> that is false in Python.
>
> **ASSERT A POPULATION SIZE BEFORE BELIEVING IT — INCLUDING A LISTING YOU TRUNCATED
> YOURSELF.** The campaign already had the rule for a gate's own summary and for a `diff`
> hunk header. Add: `print(hits[:10])` after `len(hits)` is the same trap wearing your own
> handwriting.
