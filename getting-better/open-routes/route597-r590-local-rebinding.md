# OPEN ROUTE #597 — R590 RESIDUAL: A RAISED CLASS NAME REBOUND INSIDE THE FUNCTION (local assignment, parameter, import alias of a module / function, walrus, annotated assignment) TO A NON-EXCEPTION PROVES no_exception WHILE CPYTHON RAISES TypeError
**Status: REPAIRED (driver run #6, executor u42, branch run6-u42 off ghost-assign-bc6 bfe0e38fb; annotations §7.597). Mechanism (front end, route #590's raise loop in `pycsl.py::_run_pipeline`, twin `\trusted`; inline, no new def, no axiom, no emission change): the raised name (and a `from` cause name) is resolved by Python's scoping -- the innermost enclosing def that binds it, unless it declares it `global` / `nonlocal`, else the module -- and every binding of it in that scope must be an exception class; otherwise new `PYCSL-R597-RAISE-NAME-REBOUND`.** Opened as: Status OPEN, Severity 1, pre-existing (red team rt57 F2, 30 probes; all prove on 822621340). R590 (route #590, run #6) resolves the module-level class and misses function-local rebinding.** Witnesses witnesses-r597/.


## The defect

Route #590 (annotations §7.590) judged the raised name by the module-level classes only (`_vd590`), so a name REBOUND
inside the function passed it:

    class E(Exception): pass
    #@ no_exception \all
    #@ ensures \result == 1
    def f(k: int) -> int:
        E = int                 # or a parameter `E: Any = int`, `if (E := dict):`, `E: Any = dict`, `E, F = 1, 2`
        try:  raise E("a")      # or module-level `import os as E` / `from os import getcwd as E`
        except E: return 1
        return 2                # PROVED; CPython raises TypeError

(rt57 F2, 30 probes; all PROVED on pycsl-base6 822621340.)

## The repair

RULE (annotations §7.597), in route #590's loop over the main file's raises, after §7.590's enclosing-handler
exemption (`raise e` inside `except ... as e`), for the raised name and for a `from` cause name:

- SCOPE: the enclosing defs, innermost first, then the module. A def that binds the name owns it (stop), unless it
  declares it `global` (its bindings are judged, then the module's) or `nonlocal` (judged, then the next def).
- BINDINGS judged in a scope (not descending into nested def / class / lambda bodies, but into their decorators,
  defaults and bases): parameters; every `Name` store / `del` (assignment, augmented, annotated, walrus, `for`,
  `with`, comprehension and tuple targets); `import` (always a module); `from m import X [as N]`; `except ... as N`;
  `match` captures (`case N`, `as N`, `*N`, `**N`); a nested `def N`. A nested or module `class N` is left to §7.590's
  class verdict.
- ADMITTED: `N = <exception class>` (a name whose §7.590 verdict is an exception, a builtin exception, or a stdlib
  `module.Attr` that is one -- the module is imported to look); for a bare `raise N` also `N = <exception class>(...)`
  (an instance); `from m import <exception class>` (a dependency file's class by its §7.590 verdict, or a stdlib module
  imported to look; antigravity / this / turtle / tkinter never imported). Anything else is refused with
  `PYCSL-R597-RAISE-NAME-REBOUND`, naming the binding and its line. Advice: rename the local / parameter / import and
  raise the exception class by its own name (audited FOLLOWABLE: advice/a597_rename_local.py = control 9684).

## Witnesses and measurements

- rt57 F2 (default model, `--no-proof`, base = `git archive bfe0e38fb` vs HEAD): all 30 family probes plus hr1855 /
  hr1856 / hr1866 EMITTED at base and are REFUSED R597 at HEAD; the route's witnesses (hr1856, hs1930, hs1955)
  REFUSED R597 x default / typed / store.
- u42 probes `witnesses-r597/u42-probes/` (all CPython-breaching unless `c`): a `match` capture (p597e), a `from`
  cause bound by a parameter (p597h), an augmented assignment of a parameter (p597i): REFUSED R597 (p597e / p597i
  EMITTED at base; p597h was R591). A `with ... as E` (p597a), an `except ... as E` elsewhere in the def (p597b), a
  local `import json as E` (p597c), a local `def E` (p597d), `global E; E = str` (p597f) and a module-level `E = int`
  (p597g) are refused by EARLIER rules at base and HEAD alike (with-as, definite assignment, shadowed import,
  nested-def lift, rebound class name). Controls: a local `E = ValueError` raised under `except ValueError` (c597a)
  and a bare `raise err` of a local `err = E("a")` (c597b) still EMIT (Python-scope resolution: a module-level
  `except Exception as err` does not reach a def that binds `err` itself).
- rt56 / rt57 raise families (511 probes containing `raise`, g17xx / g18xx, default model, HEAD vs base): every
  probe whose verdict changed was EMITTED at base and is CPython-breaching (the F2 / F3 probes above, ha1791 `raise k`,
  ha1793 `raise c(..)` of `c = k`); refused -> refused with a new code: hr1870 / hs1968 / hs1969 / ha1787 (R591 ->
  R597, the cause name is rebound), hi1768 / ha1794 (R590 -> R597, `raise mk()` of a def), hr1867, hi1762 (an
  `E if k else F` local). No honest probe changed verdict.
- CORPUS (expected FAIL, PROVED at base bfe0e38fb in the default model, full proof; REFUSED R597 x default / typed /
  store at HEAD): 9670 (hs1930 `E = int`), 9671 (hr1856 parameter), 9672 (hs1955 `import os as E`), 9673 (hs1956
  `from os import getcwd as E`), 9674 (hs1961 walrus), 9675 (hs1964 annotated), 9677 (tuple target `E, F = 1, 2`).
  (A `for E in [1]` target after `E = ValueError` was NOT proved at base: not used.) CONTROL (expected PASS, PROVED
  at base and HEAD): 9684 (the advice: the local renamed `T = int`, `\result == k + 1` from the handler).
- RESIDUAL (named): a raise in a DEPENDENCY module is not judged by R597 (route #590's population: the main file).
  A raised name bound by a class-body statement and raised inside that class body is judged by the module scope.
