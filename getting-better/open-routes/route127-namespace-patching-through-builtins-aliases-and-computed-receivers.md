# ROUTE #127 — namespace patching the #119 fence walked past: `__builtins__`, ALIASES of an object
# root, COMPUTED receivers, and a NON-LITERAL `setattr` on a class passed as a parameter

**Status: CLOSED AND FULLY GATED by gen #24 (2026-09-15), battery-A (cheap legs, emission vs HEAD, suite 3481/3499 same 18 0 XPASS, planes 34/34 — every leg predicted and hit).**
**Severity: SEV-1. Order 2** (carrier = the landed #119 rebinding refusal, rules (3)/(5)/(6), keyed on the
SPELLING of the receiver root: an import alias, a def/class name, `globals()/vars()/locals()`, a literal
`.__dict__`).

## MEASURED at HEAD `0a3d1d2e` (each PROVES; CPython contradicts, run)
1. `__builtins__.len = seven` then `len([1, 2])`, `\result == 2` — CPython 7 (no import needed; `import builtins;
   builtins.len = ...` WAS refused).
2. `setattr(__builtins__, "len", seven)` — same.
3. `bm = __builtins__; bm.len = seven` — same (an ALIAS).
4. `import plainlib; pm = plainlib; pm.inc = abs`, `plainlib.inc(-3) == -2` — CPython 3.
5. `getattr(__builtins__, "__dict__")["len"] = seven` — CPython 7 (a COMPUTED namespace dict).
6. `Base.__init_subclass__(cls): n = "m"; setattr(cls, n, getattr(cls, "n"))`, `C().m() == 1` — CPython 2 (a
   non-literal setattr on a PARAMETER; the fence exempted every plain Name receiver).

## REPAIR (drafted, Module3_Weaver.process)
- `__builtins__` is an object root (rules 3/5/6).
- A name bound anywhere to an expression that REACHES an object root through attribute/subscript steps or a
  dynamic accessor (`getattr`/`vars` of an object, `globals`, `locals`, `type`, `__import__`, `eval`,
  `*.import_module`) is itself an object root, to a fixpoint; an alias is never exempted as a local. A CALL of a
  def/class taints nothing (it yields a value).
- A subscript store / mutating call whose receiver chain reaches an alias, `__builtins__`, or a dynamic accessor
  is refused.
- A NON-LITERAL setattr is exempt only on a local bound solely from ordinary calls in the innermost function (the
  emitter's `out = copy.deepcopy(node)` idiom); parameters are not exempt. pyref 0078 (expected-FAIL) is now
  refused (GONE, predicted).
Witnesses 1349-1352.
