# FINDING w65 — `#@ fresh_globals`'s confinement check DEFERS the cross-module case to
# itself, and the pipeline order makes that impossible: the check runs BEFORE imports
# are resolved, and the dependency sub-pipeline runs no semantic checks at all

**STATUS: STRUCTURE VERIFIED AT HEAD BY READING THE PIPELINE; EXPLOIT NOT CONSTRUCTED.**
Recorded as a lead, not claimed as a route. Found by the deferral generator; the structural
half is confirmed by me independently, the exploit half is honestly unfinished.

## WHAT `fresh_globals` BUYS

`#@ fresh_globals` re-establishes the module-global constructor post-state as an **assumed
entry fact**. `core_ir_semantic._check_fresh_globals` is the confinement that makes that
assumption sound, and it has exactly two clauses: the function (1) must not be a method, and
(2) must not be called by any other function in the unit — *"a callee inherits its caller's
(possibly already-mutated) global, so assuming the fresh state would be UNSOUND."*

## THE DEFERRAL

Its docstring then covers the cross-module case by deferring to its own clause (2):

> *"(A library function that another module imports and calls **would also be rejected by (2)
> once that call is in scope**; a top-level driver that nothing calls is the only admissible
> site.)"*

and `frontend/Module2_Parser.py` states it unhedged: *"Module4 REJECTS it on `self`-methods,
**library functions**, and any function that is a callee of another verified function in the
same unit."*

## WHY "ONCE THAT CALL IS IN SCOPE" NEVER HAPPENS — verified at HEAD

Clause (2) scans `call_targets`, built only from `ir["functions"]`:

```python
fresh = [f for f in funcs if f.get("fresh_globals")]
if not fresh:
    return                      # early exit
for f in funcs:
    _collect_call_targets(f.get("body", []), call_targets)
```

and the pipeline order in `src/pycsl/pycsl.py` is:

* **line 504** `run_ir_semantic_checks(ir_data)` — the only call site (grep-confirmed);
* **line 533** `_ir_resolve(...)` — import resolution, which is what INJECTS a dependency's
  functions into `ir_data["functions"]` (`frontend/ir_resolve.py`:
  `ir_data["functions"].insert(0, func_ir)`), and stamps them `func["trusted"] = True`.

So: verifying module **A** alone, nothing in A calls `f`, and clause (2) does not fire.
Verifying module **B** (which calls `A.f`), `A.f` is inserted into `ir_data["functions"]`
**after** the check already returned — and if B has no `fresh_globals` function of its own, the
check returns at the early exit before even looking. And the dependency sub-pipeline runs no
semantic checks at all: `frontend/ir_resolve.py` says *"Module 4 DROPPED (B-final): … the dep
sub-pipeline goes straight from the woven AST to Module 5."*

**So the case the docstring says is "also rejected by (2)" is rejected by nothing.** Aggravating
factor: the injected dependency function is stamped `trusted`, i.e. in B's run it is a bodyless
`val` carrying a contract that was proved under the assumed fresh-global entry fact.

## WHY I AM NOT CALLING IT A ROUTE

I did not construct the witness. It needs a module-level mutable global in A, a `fresh_globals`
function in A whose contract depends on that global's fresh value, and B mutating that global
before calling — and I have not established that cross-module global mutation is even
expressible in PyCSL today. **A structural gap I have verified and an exploit I have not built
are two different claims, and this campaign's currency is the second one.** Three routes were
already measured end-to-end this generation; this one is handed over honestly unfinished rather
than dressed up.

## WHAT THE NEXT GENERATION SHOULD DO FIRST

Build the positive control BEFORE the exploit: a single-file `fresh_globals` driver that
PROVES, plus the clause-(1) and clause-(2) rejections firing, so that any cross-module refusal
can be told apart from an ordinary completeness wall. **This is the probe most likely to be
vacuous** — a cross-module setup has many independent ways to refuse, and four probes this
campaign have already died of exactly that.
