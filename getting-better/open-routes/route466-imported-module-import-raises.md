# OPEN ROUTE #466 — IMPORTED USER MODULE not imported: route #461 runs only the claimed file's own top level; a locally-resolved dependency (or package __init__) whose import raises -- module-level raise / 1 // 0 / assert / {}['k'], class-creation errors (MRO, dataclass mutable default), a missing module or name it imports, a compile-time SyntaxError, a transitive dependency that raises -- and import-statement semantics the resolver does not follow (a name bound only under `if False:` / in a `for` body / after a raising statement in `try`, `del`-eted, circular imports, `from .x import` in a script) all prove (ImportError / ZeroDivisionError / ... at import)
**Status: REPAIRED (executor x1, driver run #3, 2026-10-29), Severity 1.** Red-team round 38 (2026-10-29, on a9eac4a08 after #460-#462: 688 probes / 155 proved / 142 confirmed; rt37's 83 all closed except #463 / #464). Census TSV `scratchpad/rt38/census.tsv`; the family block below is quoted from `scratchpad/rt38/FINDINGS.txt`.
Witnesses `witnesses-r466/` (18): `g2_m200_helper_toplevel_raises.py`, `g2_m201_helper_toplevel_raises_unused.py`, `g2_m210_circular_import.py`, `g2_m212_helper_name_under_if_false.py`, `g2_m219_helper_imports_missing.py`, `g2_m220_helper_syntaxerror.py`, `g2_m222_helper_mro_conflict.py`, `g2_m250_pkg_init_raises.py`, `g2_m251_helper_dataclass_mutable_default.py`, `g2_m252_helper_assert_toplevel.py`, `g2_m253_helper_raise_toplevel.py`, `g2_m254_transitive_helper_raises.py`, `g2_m255_helper_import_from_missing_name.py`, `g2_m256_import_mod_attr_g_missing.py`, `g2_m257_from_import_name_in_for.py`, `g2_m258_circular_import_module_attr.py`, `g2_m260_relative_import_in_script.py`, `g2_m261_helper_name_bound_in_try_raising.py`.

Driver repro: 17/17 family exemplars (scratchpad/rt38/verify/, F8 without --import-path) rc=0 Verification SUCCESS on main a9eac4a08 at 2026-10-29T14:55Z, each violating under CPython (scratchpad/rt38/driver-repro.txt).

```
F2 IMPORTED USER MODULE not imported: route #461 runs only the claimed file's own top level; a locally-resolved dependency (or package __init__) whose import raises -- module-level raise / 1 // 0 / assert / {}['k'], class-creation errors (MRO, dataclass mutable default), a missing module or name it imports, a compile-time SyntaxError, a transitive dependency that raises -- and import-statement semantics the resolver does not follow (a name bound only under `if False:` / in a `for` body / after a raising statement in `try`, `del`-eted, circular imports, `from .x import` in a script) all prove (ImportError / ZeroDivisionError / ... at import) (18)
  EXEMPLAR: g2/m200_helper_toplevel_raises.py (`from h200 import g`, h200.py = `X = 1 // 0` + def g) ; g2/m212_helper_name_under_if_false.py (h212 binds g only under `if False:`)
  CPYTHON: ZeroDivisionError: division by zero at import of h200 / ImportError: cannot import name 'g' from 'h212' -- f never becomes callable
  WHY IT PROVES: route #461 runs ONLY the verified file's top level; an import of a locally-resolved module is admitted when the module EXISTS (and a `from` name is bound by it somewhere), the dependency's own top level is never run, and a dependency of a dependency is not looked at (m254). Name binding inside the dependency is read flow-insensitively (m212 `if False:`, m257 `for _ in []:`, m261 after a raising statement in `try`), circular imports (m210 / m258) and a relative import in a script (m260) are not modelled.
  PROPOSED SYSTEMATIC REPAIR: RECURSE #461 ACROSS THE IMPORT GRAPH in CPython's order: when a claimed file imports a locally-resolved module (and, for `a.b.c`, each package __init__), run that module's top level through the SAME m1 interpreter (allow-list, refuse by default) with its own module dict, memoised per module and with CPython's partial-module semantics (a module enters sys.modules BEFORE its body runs, so a cycle reaches a partially-initialised module and a `from M import n` whose n is not yet bound is ImportError); a `from M import n` is admitted only if n is bound in M's resulting dict (not 'somewhere in M's AST'); `from . import` / `from .x import` in the verified script (no __package__) is refused; plus the F1 compile() gate per dependency. Witnesses m200 m201 m210 m212 m219 m220 m222 m250-m261 (refused); control: the same with a clean helper (PASS).
  PROBES: g2/m200_helper_toplevel_raises.py g2/m201_helper_toplevel_raises_unused.py g2/m210_circular_import.py g2/m212_helper_name_under_if_false.py g2/m219_helper_imports_missing.py g2/m220_helper_syntaxerror.py g2/m222_helper_mro_conflict.py g2/m250_pkg_init_raises.py g2/m251_helper_dataclass_mutable_default.py g2/m252_helper_assert_toplevel.py g2/m253_helper_raise_toplevel.py g2/m254_transitive_helper_raises.py g2/m255_helper_import_from_missing_name.py g2/m256_import_mod_attr_g_missing.py g2/m257_from_import_name_in_for.py g2/m258_circular_import_module_attr.py g2/m260_relative_import_in_script.py g2/m261_helper_name_bound_in_try_raising.py
```

## REPAIR (executor x1, driver run #3, 2026-10-29, off daf5c3d1f; annotations §7.280, translational §T.6.290)

Code inline at the end of `_run_pipeline`, AFTER route #461 / #462's in-file evaluation (which it does not touch;
mirror twin `\trusted`; no new def, no axiom, no emission change). Gate: `_rc444` (a claimed def in the file). The
imported modules are resolved on the TARGET's path -- this file's directory, the `--import-path` roots, then the
interpreter's `sys.path` minus the verifier's own tree (src/pycsl, src/) -- and a module found in the first two (the
PROGRAM) is IMPORTED here, in CPython's order: a frame machine runs the import statements of the verified file (module
level, class bodies, `if` / `try` / `with` / loop bodies, the bodies of the claimed defs), suspends a statement whose
module is not loaded yet, and loads it -- each package `__init__` first; the module enters the table in state LOADING
before its body runs (CPython's partial module), `compile()` must accept its source (symbol-table SyntaxErrors
included), and its top level and class bodies are run statement by statement over REAL values with CPython's own `eval`
after a safety scan (every call names a side-effect-free standard-library callable or a builtin-type method, resolved
now), defs as placeholders that refuse if import-time code calls them, classes by `types.new_class` with their
allow-listed decorators applied for real (dataclass / total_ordering / unique ...). `from M import n` needs `n` bound
in M's namespace AT THAT MOMENT (or a submodule); a claimed def's `M.n` needs `n` bound once M is imported; a relative
import in the verified file (a script) is refused. An installed module (site-packages) must exist; its top level is not
run (declared library, like the standard library). Code `PYCSL-R466-IMPORTED-MODULE-RAISES`.

Red-team witnesses (`witnesses-r466/`, run from their directory, `--import-path src/pycsl`): 18/18 PROVED on daf5c3d1f
except m260 (already refused by #161 at base); candidate 17 REFUSED by #466, m260 by #161. Corpus witnesses 7260-7265,
7267-7269 (div-zero top level, `if False:` name, dataclass mutable default, MRO conflict, missing module, circular
import, `h.g` unbound, transitive, name after a raising `try` statement): PROVED at base, REFUSED. (7266, a package
whose `__init__` raises, was dropped: the package cannot be named in check-corpus-executes' basename-keyed
KNOWN_LOAD_FAILURES -- `__init__.py` -- and red-team m250 already witnesses it, REFUSED.) The seven helpers whose import
raises by design are named in check-corpus-executes' KNOWN_LOAD_FAILURES with their reason, as `circ_b.py` is. Controls
7285 (constants, a `field(default_factory=list)` dataclass, a def) and 7289 (a circular import whose name is bound before
the cycle closes): PROVED at base and candidate.

GATES (worktree pycsl-x1 off daf5c3d1f; bases = v13/ca, v13/ma, the emission of 33f7ac681, docs-only since):
fidelity check-self-annotate-sync rc=0 (938 un-trusted mirror functions verbatim), self-annotate-mirror-check rc=0
(53); doc-coherency rc=0. Byte-diff root 2604 -> 2609 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new controls); pyref
2186 / 2186 0/0/0; mirror 53 / 53 0/0/0 (no OWED proof). Planes / ledgers: see the x1 commit message (fast planes
61/61 after naming the import-raising fixtures in check-corpus-executes; trusted-reasons, assumed-facts,
refusal-witness-coverage, refusal-advice-audited, dropped-mutation, getattr-erasure, open-route-carriers,
frame-honesty, raises-honesty, clause-survival, stdlib-modules-verify all rc=0; trusted 437 unchanged).
OVER-REFUSAL COST, measured: the 24 claimed corpus files that import a non-standard-library module (23 expected
FAIL, 1 PASS = 6642) -- 6642 still PROVES (its un-claimed `inc` is on the #467 allow-list); 0 pyref / mirror /
pycsl_lib files carry a claim, so #466 / #467 / #472 cannot fire there. #466's judge run over every multi_file_lib
helper imported under a claim: 51 of 58 accepted, 1 refused by #466 (`circ_b` imported first: CPython raises
ImportError too, the plane's KNOWN_LOAD_FAILURES says so), 6 refused by older routes. #468 (no claim gate): a wide
first cut refused corpus 3382 (a `\trusted` `tid(x): return x`) and 11 mirror files (all through explicit
`\trusted` stubs or stubs no verified code of the file calls) -> narrowed (returning the list is a read; an explicit
`\trusted` def is a declared assumption; only vals the verified code references are judged): 0 GONE.

## RESIDUALS
- An INSTALLED module (site-packages) is a declared library: it must exist and bind a `from` name somewhere in its
  source, but its top level is not run (the standard library's standing).
- The allow-list refuses real code it cannot judge: a module top-level `for` / `while` / `with`, a
  `try: import X / except ImportError:` fallback whose body raises, a call of file code or of a non-allow-listed
  library function (`dataclasses.fields(..)`, `_build_nodes(globals())`: `frontend.pure_ast`,
  `module6_whyml.expressions` are refused if a claimed file imports them -- no claimed corpus / mirror file does).
- Import-time effects are judged on the verifier's interpreter (`sys.version_info`, `os.sep`, `sys.platform`); a
  relative import in the VERIFIED file is refused (it is judged as a script, as #461 judges it as `__main__`).
- PYTHONPATH entries of the verifier's own process are kept on the target path (they are the user's environment).
