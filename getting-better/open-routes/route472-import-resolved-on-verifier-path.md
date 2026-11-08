# OPEN ROUTE #472 — IMPORT EXISTENCE JUDGED ON THE VERIFIER'S OWN sys.path: route #461 admits `import M` when M is 'installed', tested in the pycsl.py process whose sys.path[0] is src/pycsl, so every module / package of the verifier itself (pycsl, frontend, agents, errors, ir_schema, exception_model, module6_whyml, proof2why3, audit_proof, ...) counts as importable for the verified program -- measured WITHOUT --import-path (ModuleNotFoundError at import)
**Status: REPAIRED (executor x1, driver run #3, 2026-10-29), Severity 1.** Red-team round 38 (2026-10-29, on a9eac4a08 after #460-#462: 688 probes / 155 proved / 142 confirmed; rt37's 83 all closed except #463 / #464). Census TSV `scratchpad/rt38/census.tsv`; the family block below is quoted from `scratchpad/rt38/FINDINGS.txt`.
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

## REPAIR (executor x1, driver run #3, 2026-10-29, off daf5c3d1f; annotations §7.280, translational §T.6.290)

Route #466's block resolves every import of the verified file on the TARGET's path (this file's directory,
`--import-path`, the interpreter's `sys.path` MINUS src/pycsl and src/), never the verifier's; a name found only on
the verifier's path is REFUSED, `PYCSL-R472-IMPORT-NOT-ON-TARGET-PATH` ('Put the module next to this file, or pass
its root with `--import-path`'). Route #461's own (in-file) existence test is left to its owner (x2's block); this
check runs after it and refuses what it admitted.

Red-team witnesses (`witnesses-r472/`, WITHOUT `--import-path`): 12/12 PROVED on daf5c3d1f, 12/12 REFUSED by #472.
Corpus witnesses 7282-7284 (`import frontend`, `from module6_whyml.expressions import ..`, `import pycsl`): PROVED at
base, REFUSED (with `--import-path src/pycsl` the module IS on the program's path; the three are then judged by #466 and
refused there: `frontend` / `module6_whyml.expressions` / `pycsl` each run non-allow-listed code at import). Control 7288
(`import packaging`, installed in the venv and the system interpreter; a first draft imported `lark`, which
check-corpus-executes' system `python3` does not have): PROVED at base and candidate.

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
- With `--import-path src/pycsl` the verifier's modules ARE on the program's path (declared by the user) and are
  then judged as program modules by route #466.
- The PYTHONPATH of the verifier's process is kept (the user's environment); only src/pycsl and src/ are removed.
