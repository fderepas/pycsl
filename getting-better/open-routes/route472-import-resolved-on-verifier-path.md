# OPEN ROUTE #472 — IMPORT EXISTENCE JUDGED ON THE VERIFIER'S OWN sys.path: route #461 admits `import M` when M is 'installed', tested in the pycsl.py process whose sys.path[0] is src/pycsl, so every module / package of the verifier itself (pycsl, frontend, agents, errors, ir_schema, exception_model, module6_whyml, proof2why3, audit_proof, ...) counts as importable for the verified program -- measured WITHOUT --import-path (ModuleNotFoundError at import)
**Status: OPEN, Severity 1.** Red-team round 38 (2026-10-29, on a9eac4a08 after #460-#462: 688 probes / 155 proved / 142 confirmed; rt37's 83 all closed except #463 / #464). Census TSV `scratchpad/rt38/census.tsv`; the family block below is quoted from `scratchpad/rt38/FINDINGS.txt`.
Witnesses `witnesses-r472/` (12): `g15_r160_import_pycsl_package.py`, `g16_v160_import_pycsl.py`, `g16_v161_import_frontend.py`, `g16_v162_import_agents.py`, `g16_v163_import_errors.py`, `g16_v164_from_frontend_import.py`, `g16_v165_import_exception_model.py`, `g16_v166_import_ir_schema.py`, `g16_v167_import_module6_whyml.py`, `g16_v168_import_proof2why3.py`, `g16_v170_from_errors_name.py`, `g16_v171_import_audit_proof.py`.

Driver repro: 17/17 family exemplars (scratchpad/rt38/verify/, F8 without --import-path) rc=0 Verification SUCCESS on main a9eac4a08 at 2026-10-29T14:55Z, each violating under CPython (scratchpad/rt38/driver-repro.txt).

```
F8 IMPORT EXISTENCE JUDGED ON THE VERIFIER'S OWN sys.path: route #461 admits `import M` when M is 'installed', tested in the pycsl.py process whose sys.path[0] is src/pycsl, so every module / package of the verifier itself (pycsl, frontend, agents, errors, ir_schema, exception_model, module6_whyml, proof2why3, audit_proof, ...) counts as importable for the verified program -- measured WITHOUT --import-path (ModuleNotFoundError at import) (12)
  EXEMPLAR: g16/v161_import_frontend.py (`import frontend` at module level, f claims no_exception \all; proved by `pycsl.py <probe>` with NO --import-path, batchnoip.sh)
  CPYTHON: ModuleNotFoundError: No module named 'frontend' -- 11 of 11 verifier-internal names; control v169 `import lark` (installed in the venv) imports in CPython too
  WHY IT PROVES: the #461 existence test falls back to 'installed' = resolvable by the verifier process (importlib on pycsl.py's sys.path, whose first entry is src/pycsl, plus src/pycsl subpackages); the verified program runs under its OWN sys.path (script dir + site-packages), so generic names like `frontend`, `agents`, `errors` that happen to be verifier modules are admitted (r160 `import pycsl` also proves WITH --import-path).
  PROPOSED SYSTEMATIC REPAIR: Resolve 'installed' against a sys.path COMPUTED FOR THE TARGET, never the verifier's: run `importlib.machinery.PathFinder.find_spec(name, path=[script_dir] + site.getsitepackages() + --import-path roots)` (or a subprocess `python3 -I -c 'import importlib.util,sys; sys.exit(importlib.util.find_spec(M) is None)'` with the target's sys.path), excluding src/pycsl and the repo src/ unless explicitly passed. Witnesses v160-v171 minus v169 (refused); control v169 lark (PASS).
  PROBES: g15/r160_import_pycsl_package.py g16/v160_import_pycsl.py g16/v161_import_frontend.py g16/v162_import_agents.py g16/v163_import_errors.py g16/v164_from_frontend_import.py g16/v165_import_exception_model.py g16/v166_import_ir_schema.py g16/v167_import_module6_whyml.py g16/v168_import_proof2why3.py g16/v170_from_errors_name.py g16/v171_import_audit_proof.py

PROVED BUT NOT COUNTED (declared model assumptions):
  g2/m202_helper_false_ensures.py | imported helper's own (false) ensures assumed: '(trusted stubs)' is a declared modular assumption
  g2/m203_helper_claimed_raises.py | imported helper's own (false) no_exception claim assumed: '(trusted stubs)' declared
  g2/m237_u_recursion.py | RecursionError: 'PyCSL does not model the recursion limit' (declared, #diverges message)
  g21/l215_abstract_no_assigns.py | \abstract with NO assigns whose body appends: the \abstract contract is not checked against the body (declared: the contract IS the definition)
  g5/g533_variant_deep_recursion.py | RecursionError at depth 5000 under \variant: recursion limit not modelled (declared)

NOTES / AXES THAT HELD (no false proof found -- useful negative results for the coordinator):
  g3  (49) requires boundary at explicit AND implicit call sites (sorted key=, map, filter, max key, functools.partial / reduce,
      lambda / alias / keyword / *args / default-arg calls, every operator dunder: __add__ __radd__ __iadd__ __neg__ __getitem__
      __setitem__ __delitem__ __contains__ __len__ __bool__ __iter__ __eq__ __lt__ __hash__ __index__ __str__ __format__ __enter__
      __call__ __getattr__ __new__ __class_getitem__ __missing__ __set_name__ __init_subclass__, setters, getters, descriptors,
      __post_init__, super().__init__, inherited __init__): 0 PROVED -- route #460's reach + #161 / #437 / #441 hold in ONE file.
  g12 (17) #460 named residuals (#347 / #357 / #395 / #402 own-claim sites; constructor rows #432 / #437 / #440 / #443 / #447 /
      #452 in __init__ / __post_init__ / __new__): 0 PROVED (refused by #445 / #349 / #347 / #441 or why3 type errors).
  g19 (13) intra-class self.m() requires (abstract sibling stubs, sibling_concrete, no_inline, inherited, super(), overrides /
      dynamic dispatch): 0 PROVED.
  g4  (48) + g20 (20) hidden mutation under `assigns \nothing` in ONE file (lists, objects, dicts, sets, globals, self, class attrs,
      48 aliasing / unbound-method / operator / callback spellings): 0 PROVED.
  g5  (49) ghost statements on real state (all why3 ghost-typing errors), lemmas proving False (while True, non-decreasing
      recursion / variant, raise, assert False, \diverges callee, requires False), \diverges + RecursionError (refused, with an
      explicit recursion-limit message), loop break / else / continue / finally semantics, \old / \at / aliasing of parameters:
      0 counted PROVED (g533 recursion depth under \variant PROVES but the recursion limit is a declared non-model).
  g7  (34) route #462 complements (__init__ = def / lambda / decorator wrapper / partialmethod / setattr / inherited assignment,
      return in finally, __new__ / metaclass __call__ returning non-instances) and #461 class-creation residuals at MODULE level
      (__set_name__, frozen + __setattr__, total_ordering, enum.unique, singledispatch.register, ABC.register, __mro_entries__,
      decorator expression errors): all refused -- the only PROVED are class statements INSIDE functions (F7).
  g8  (56) r1 leads: Union[int, str] / int | str / Optional / object operands (36 operator / builtin sites) and str += int
      plus 19 mixed augmented operators: 0 PROVED (refused #252 / #325 or why3 type errors) -- r1's leads are closed on a9eac4a08.
  g9  (30) big-int str conversion sites (route #281: format / %s / %i / !r / ',' / str(list) / json.dumps / join(map(str)) / print)
      and int->float OverflowError: 0 PROVED.
  g6  #461 stand-in boundary for RUN-TIME values (cwd, environ, getenv, argv, orig_argv, pid, time, random, secrets, urandom,
      uuid, hash randomisation, set order, id, isatty, listdir, relative open, recursionlimit, __file__ / __spec__ / __loader__ /
      __builtins__ / __cached__ / __path__ / __doc__): all refused -- only __name__ / __package__ (F5) and lazy annotations (F6) leak.
  g10 (7) script file named like a stdlib module it imports (dataclasses.py / heapq.py / json.py ...): refused (#326).
  g15 / g17: imports resolved only through the working directory / repo src/ / the verifier's __main__: refused (#461), except
      `import pycsl` (F8).  g18 (20) run-time creation inside functions other than class statements (namedtuple / Enum / TypedDict
      factories, type(), nested def / lambda defaults and decorators): all refused.
  g2g: non-list arguments written by an imported helper (dict / set / bytearray / deque / object field / nested list): not proved
      (why3 type errors, PYCSL-VAL-ARG-UNFRAMED, or the havoc is seen) -- F4 is specific to the list LENGTH.
  g2h (10) imported callees that are not plain defs (lambda, partial, builtin alias, callable instance, decorated / cached
      def, class constructor, bound __getitem__, rebound name): all refused (#161 / #441 / #443).
  g21 (11) list length through SAME-FILE val boundaries (recursion, mutual recursion, \variant, interface, assigns x,
      verify_module, no_inline global method, sibling abstract stub): refused -- only \abstract leaks (l216 in F4, l215 excluded).
METHOD NOTES: g2 / g10 / g15 / g16 / verify are run in CPython WITHOUT -I (cpy2.sh: -E -s) so the script directory is on
  sys.path as for `python3 probe.py`; g16 is proved WITHOUT --import-path (batchnoip.sh) so the verifier's own sys.path is the
  only source of the false resolution. g6 nondeterministic probes (time / pid / random / hash) record one CPython sample; they are
  all refused, so no verdict depends on the sample.

VERIFY (one exemplar per family re-proved in verify/, same tree):
  F1_c116_in_f_param_global.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level SyntaxError: name 'n' is parameter and global
  F1b_c101_param_global.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level SyntaxError: name 'x' is parameter and global
  F1c_c145_in_f_await.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level SyntaxError: 'await' outside async function
  F1d_e140_ascii_cookie_nonascii_comment.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level SyntaxError: encoding problem: ascii
  F2_m200_helper_toplevel_raises.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level ZeroDivisionError: division by zero
  F2b_m212_helper_name_under_if_false.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level ImportError: cannot import name 'g' from 'h212' (/home/fabrice/git/pycsl/scratchpad/rt3
  F3_m234_u_assert_false.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION AssertionError 
  F3b_m327_getattr_missing.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION AttributeError 'int' object has no attribute 'zz'
  F4_m306_claimed_helper_assigns_list.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 3
  F4b_m270_append.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 3
  F5_s600_name_not_main.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level ZeroDivisionError: division by zero
  F5b_s644_class_module_attr.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level ZeroDivisionError: division by zero
  F6_s649_func_annotations_lazy.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level NameError: name 'UndefZZ' is not defined
  F6b_s651_class_annotations_lazy.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level NameError: name 'UndefZZ' is not defined
  F7_k145_realistic_local_record.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION ValueError mutable default <class 'list'> for field items is not allowed: use de
  F7b_i733_class_in_function_bool_base.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError type 'bool' is not an acceptable base type
  F8_v161_import_frontend.py  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level ModuleNotFoundError: No module named 'frontend'
  re-run: cd /home/fabrice/git/pycsl-rt38 && PYTHONHASHSEED=0 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt38/verify/<probe> --import-path src/pycsl
          (F8: the same WITHOUT --import-path); CPython: cd verify && /home/fabrice/git/pycsl-rt38/.venv/bin/python3 -E -s <probe>
          (helpers h200 h212 h234 h270 h306 h327 sit next to the probes in verify/)

STATUS: 2026-10-29T14:47:12Z -- regenerated by mkfind.py (142 confirmed, 155 proved, 0 pending)
```
