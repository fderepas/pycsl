# OPEN ROUTE #602 — A MODULE ALIAS OF A BUILTIN EXCEPTION USED AS A HANDLER (`Err = ValueError; except Err:`) IS LOWERED TO A DISTINCT `exception Err`, SO THE RAISED ValueError ESCAPES IN THE MODEL
**Status: REPAIRED (driver run #7, executor u44, branch run7-u44 off 952bf7891; annotations §7.602). Mechanism: a fail-closed front-end refusal in `pycsl.py::_run_pipeline` (twin `\trusted`), after Module 6 and routes #590 / #597: a handler name bound in the module or the enclosing function by anything but its `class` statement, an import of that same name, or a module-level alias `A = E` of a class of the file (route #175's) is refused (`PYCSL-R602-HANDLER-NAME-REBOUND`).** Opened as: Status OPEN, Severity 1, PRE-EXISTING (proves at base and at L9). Found by red team rt58.**

## Exemplar (witnesses-r602/)
- d08_handler_name_alias.py: proves; CPython returns 1.

## The repair (driver run #7, executor u44)

RULE (annotations §7.602, `PYCSL-R602-HANDLER-NAME-REBOUND`), same place and population as §7.601: a name used as a
handler (alone or in a tuple) must not be bound in the module (including `global N` stores from any function) or
in the enclosing function by anything but its `class` statement, an import of that same name, or a module-level
`A = E` where `E` is a class of the file bound only by its `class` statement (an alias of a USER class is route
#175's: corpus 1619 is refused there, control 9612 `A = E; raise A(..); except A:` keeps proving). Refused: an
assignment of anything else (rt58 d08 `Err = ValueError`), a local alias, a parameter, a `for` / `with` / walrus /
comprehension / `match` / `except ... as` target, a `def`, an `import ... as` rename. Ordering: judged AFTER routes
#590 / #597, so a raised name rebound the same way keeps route #597's refusal (corpus 9670-9677 unchanged).
Advice: name the exception class itself in the handler (control 9965: `except ValueError:`).

## Witnesses and measurements (u44)

- rt58 d08 (and corpus 9955) REFUSED PYCSL-R602-HANDLER-NAME-REBOUND in default / typed / store; 9956 (local
  alias), 9957 (alias inside a tuple), 9958 (a parameter holding the class) likewise, each PROVED at base 952bf7891
  (full proof, default). Control 9965 PROVED x3 at HEAD; corpus 9612 (`A = E`, user class) still emits identically.
- Probes refused EARLIER by other routes (not R602 witnesses): p602b `from builtins import ValueError as Err`
  (import-rename route), p602d `global KeyError; KeyError = ValueError` (the global-write refusal), p602e a `for`
  target over `(ValueError,)` (PYCSL-R559-BUILTIN-OBJECT-ELEMENT).
- Over-refusal: corpus root / pyref 0 / 0 / 0; mirror 53 / 53 identical. Logs: `/home/fabrice/git/pycsl-u44/scratchpad/u44/`.
