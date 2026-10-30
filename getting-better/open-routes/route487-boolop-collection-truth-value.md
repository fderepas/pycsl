# OPEN ROUTE #487 — `x or y` / `x and y` OVER COLLECTION OPERANDS IS LOWERED TO ITS TRUTH VALUE (AN INT 0/1), NOT TO THE SELECTED OPERAND (DEFAULT MODEL)
**Status: OPEN, Severity 1.** Red-team round 40 (2026-10-30, on dcf424f75 after #475-#480 repaired / #474 partial: 624 probes + 1009 mode re-proofs / 129 confirmed (probe, mode) pairs on 103 probes; rt39's 141 all closed). Census TSV `scratchpad/rt40/census.tsv`; the family block below is quoted from `scratchpad/rt40/FINDINGS.txt`.
Witnesses `witnesses-r487/` (7): `g100_z10000_or_imul.py`, `g100_z10002_and_imul.py`, `g100_z10009_or_isub_typeerror.py`, `g100_z10012_or_local_list_alias.py`, `g103_k10302_list_or_lt.py`, `g103_k10306_list_or_neg.py`, `g98_y9805_or_alias_imul.py`.

Driver repro: `scratchpad/rp40/repro.sh` (session scratchpad) on dcf424f75, 2026-10-30T07:30Z: all 16 rt40 verify exemplars (2+ per family, F5 under --memory-model typed / store) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F6 `x or y` / `x and y` OVER COLLECTION OPERANDS IS LOWERED TO ITS TRUTH VALUE (AN INT 0/1), NOT TO THE SELECTED OPERAND (DEFAULT MODEL) (7)
  WHAT: Python's `a or b` returns one of its OPERANDS; when an operand is a list (or str / dict), the default-model lowering replaces it by its truth value `(if Array.length a <> 0 then 1 else 0)`, so `b = a or a` binds an INT: `b *= 2` / `b -= 1` are int arithmetic (no TypeError, no in-place effect on `a`), `x < 3` and `-x` are int operations
  EXEMPLAR: g98/y9805_or_alias_imul.py (`#@ requires len(a) == 2`, `#@ ensures \result == 2`, `#@ assigns \nothing`, `def f(a: List[int]) -> int: b = a or a; b *= 2; return len(a)`); g100/z10009_or_isub_typeerror.py (`b = a or a; b -= 1` under `no_exception \all`)
  CPYTHON: y9805: f([0, 0]) returns 4 (b IS a; `*=` extends it in place) -> VIOLATION contract; z10009: TypeError unsupported operand type(s) for -=: 'list' and 'int'; k10302 (`x = a or a; x < 3`) TypeError '<' list/int; k10306 (`-(a or a)`) TypeError bad operand type for unary -
  WHY IT PROVES: module6_whyml/expressions.py:7283-7284 (the and/or lowering): `_l_val = left if left_b == f"({left} <> 0)" else f"(if {left_b} then 1 else 0)"` -- for an operand whose truth test is not the int `(x <> 0)` (a list: `Array.length a <> 0`), the SELECTED value is replaced by the int encoding of its truth value, then `(let __or_l = _l_val in if __or_l <> 0 then __or_l else _r_val)` (:7349-7353). Emitted for y9805 (emit/y9805_or_alias_imul.mlw): `let b = ref 0 in b := (let __or_l = (if (Array.length a <> 0) then 1 else 0) in ...); b := !b * 2; (Array.length a)`. Routes #279 / #283's alias refusals (module6_whyml/statements.py:751-960) key on the target being a list local (`_seq_locals` / symbol type `list` / `_rhs_yields_array`), and `b` is now an int, so neither fires; appends / element stores / `+=` through `b` are refused or fail typing (z10003-z10008), only int-typed operations survive.
  PROPOSED SYSTEMATIC REPAIR: REFUSE BY DEFAULT: an `and` / `or` whose operand is not a Python bool or an int (any operand whose `_to_bool` is not the int test `(x <> 0)`: lists, str, dicts, sets, records, Optionals) is lowered only in a TRUTH position (an `if` / `while` test, `not`, a contract boolean); in a VALUE position it must select the operand with its own type (`if Array.length a <> 0 then a else b`, both arms of one Why3 type) or be REFUSED (PYCSL-M6-BOOLOP-VALUE); never wrap an operand into `if .. then 1 else 0`. Witness: the F6 probes; control: `x = a == b or c == d` (pure bools) and `n or 5` on ints keep their lowering.
  PROBES: g100/z10000_or_imul.py g100/z10002_and_imul.py g100/z10009_or_isub_typeerror.py g100/z10012_or_local_list_alias.py g103/k10302_list_or_lt.py g103/k10306_list_or_neg.py g98/y9805_or_alias_imul.py

PROVED BUT NOT COUNTED / ENVIRONMENT-DEPENDENT (excluded.txt):
  # ENVIRONMENT-DEPENDENT / DECLARED RESIDUAL (proved, CPython breaches, not counted):
  g81/e8752_local_sitecustomize_ne.py | VIOLATION module-level ImportError: cannot import name 'K' from 'sitecustomize' (/usr/lib/python3.14/sitecustomiz | ENVIRONMENT-DEPENDENT: a local `sitecustomize.py`: CPython imports the INSTALLATION's sitecustomize at startup (Debian/Ubuntu ship /usr/lib/python3.14/sitecustomize.py), so `from sitecustomize import K` reads the preloaded module; route #472-style stdlib-name refusal keys on sys.stdlib_module_names, which does not list it -- real on this interpreter, absent on a vanilla CPython build
  g92/r9606_peer_rebinds_dep_str_ens.py | VIOLATION contract 2 | DECLARED RESIDUAL of route #474 (peer module rebinds an IMPORTED constant `h.S = ...` under an ensures-only claim): proved at base and at the repair, named in route474-imported-constant-flow-insensitive.md -- not counted
  # PROVED, CPython raises, but NO CLAIM COVERS IT (ensures-only claim; an exception is not an ensures breach):
  g91/p9502_dep_patches_builtins_len_ens.py | VIOLATION module-level AssertionError | not a false proof (ensures-only)
  # PROVED and CPython AGREES (controls):
  g81/e8761_dep_u2028_ens.py | result 1 | control
  g84/s8839_type_alias_lazy.py | result 1 | control
  g86/b9032_true_real_plus_ctl.py | result 2 | control
  g95/t9314_star_unpack.py | result 0 | control
  g97/w9715_ctl_nested_elem_isub.py | result 0 | control

NOTES / AXES THAT HELD (no counted false proof -- negative results for the coordinator):
  (B) #474: every namespace-writer spelling in a dependency that is NOT a `__builtins__` MAPPING reach is refused -- self-import attribute
      stores, `sys._getframe(0).f_globals`, `inspect.currentframe().f_globals`, `builtins.globals()` / `builtins.exec`, aliased `globals` /
      `exec` / `vars`, `importlib.import_module(__name__).K`, `importlib.__import__`, `getattr(sys, 'modules')` (route #326), function
      `__globals__` (incl. a decorator), ModuleType `__class__` swap, `operator.setitem(builtins.globals(), ..)`, `getattr(builtins,
      'globals')()` -- by the Weaver's namespace / rebinding rules (a8000-a8119), by #474 itself, or by #466 under no_exception. `import h;
      h.K` attribute reads of a rebound dependency constant are opaque (PYCSL-R325-OPAQUE-INT-FALLBACK, a8200-a8303). A dependency's list /
      dict / set constant mutated in place at import (append / clear / item store / del / pop / update / add / sort, g105) is not folded:
      NOT-PROVED or refused. In-file `builtins.__dict__['exec']` / `vars(builtins)['exec']` (c8900-c8953): refused by route #290.
  (B) #475: main-file latin-1 / cp1252 / shebang+cookie / vim cookie / utf-7 hidden statement (e8700-e8710): REFUSED (#465); `sys.path.insert`
      before the import (e8730 / e8731): REFUSED (#326); local files named like builtin / frozen / preloaded stdlib modules (errno, stat, zlib,
      gc, marshal, math, itertools, abc, codecs, time, genericpath, linecache, _weakref, posixpath): REFUSED (stdlib-name rule) -- except
      `sitecustomize` (environment-dependent, excluded); a `.pyi` beside the `.py`: NOT-PROVED (the `.py` is read); lone-CR newlines in a
      dependency: refused.
  (B) #476: 36 script-order probes (g84) -- frontier spellings that never call f by name (map / sorted key / alias / decorator / class
      decorator / metaclass `__init__` / `__init_subclass__` / `globals()['f']` / getattr(sys.modules[..]) / eval / partial / list / dict
      dispatch / default arguments / class bodies / assert / with / annotated assignment / match / while / try) and rebinding spellings (a
      `global` rebinding in a setup function the driver calls, module-level `_patch()`, `globals()[..]` / setattr / exec / from-import / del
      after the guard, decorator replacement, class-method rebinding) -- 0 PROVED (#476, #461, #290, the Weaver's rebinding rule).
  (B) #477: module `__getattr__` assigned, `__class__` swap, `sys.modules[__name__]` replacement (via getattr) -- refused (a8016 / a8116 /
      a8019 / a8119).
  (B) #478: every `p op= ...` on a collection PARAMETER spelling (Sequence, Optional, list[int], string annotation, type alias, unannotated
      used as a list, `__imul__`, operator.isub / imul, dict `|=`, closures, fields, globals) is refused or fails typing in default / typed /
      store / concurrent -- the residue is the SUBSCRIPT / walrus / ternary targets of F5.
  (B) #479 / #480: 68 + 18 builtin-object spellings (g86 / g96: `from builtins import`, `builtins.x`, getattr, `__builtins__.len`, stdlib
      functions and str constants, `__name__` / `__doc__` / `__spec__`, attributes of builtins and of int / float / bool values and
      expressions, containers / ternaries of builtins, min / max / sum / sorted over builtins, NotImplemented truth in assert / while / if /
      comprehension / filter / default / dunder result, partial, method descriptors, classes, dependency re-exports, class-body `__module__`
      / `__qualname__`, module attributes `h.__file__` / `h.__dict__`, function / class / instance dunders): all refused -- the residue is
      the three implicit module globals of F4. A `from m import *` file (g106) is refused before #480 matters.
  (B) cv6 D4 / route #264: short-circuit definite assignment (u9150-u9154: `or` after `and` walrus, nested BoolOp, walrus read after an
      `or`, ifexp inside `and`) -- all refused; the `open`-patched-through-builtins probe (u9155) does not breach in CPython (no claim broken).
      cv6 D3 / route #316: every F1 frame probe that proves on c3332a57f ALSO proves on d5b93a934 (the parent of 1ad5b816c; base316/summary.tsv:
      37 PROVED/PROVED, 25 REFUSED/REFUSED, 8 NOT-PROVED/NOT-PROVED, 1 TE/TE): F1 is PRE-EXISTING, not a statement-level-SSA regression.
  (C) single-file surfaces closed on c3332a57f: g88 classes (36: class vs instance attributes, shared class lists, __slots__, properties /
      setters, frozen dataclasses, unhashable dataclass / __eq__ keys, dunder protocol results, operator overloading, class __getattr__,
      descriptors, method recursion, type(self).k / __dict__ / setattr writes, subclass class attributes) -- 0 PROVED; g89 closures /
      nonlocal / late binding, generators across functions, zip(it, it), map consumed twice, mutable default arguments (refused: 'Mutable
      default argument'), globals written by callees, walrus leaking from comprehensions, try / finally return / mutation -- 0 PROVED;
      g99 the F1 alias channels inside a VERIFIED (non-\trusted) callee and g95 t9330-t9334 inside VERIFIED methods, g95 t9340 / t9341 in
      IMPORTED functions: all refused (routes #279 / #283 / #290) -- F1 is specific to `\trusted` callees (functions and methods) with no
      `assigns`; g104 global writes through the same channels from a \trusted function: refused (only `self` / parameter targets leak);
      g101 other alias expressions (`None or a`, `0 or a`, max / min / next(iter) of displays, or-chains, annotated / walrus binders,
      sort / reverse / set.add through an `or` alias, `return xs or xs` from a callee): all refused -- F6 is the augmented-assignment / int-
      operator residue; g102 `and` / `or` value semantics on int / str / list operands: NOT-PROVED or WHY3-TYPE-ERROR (fail closed).
  g107 / g108: non-int list elements in Load positions (`a[0] + 1`, `a[0] < 1`, `-a[0]`, `10 // a[0]`, `a[0] = a[0] - 1` on List[str] /
      List[List[int]] / List[Tuple] / List[Dict] / List[Set] / List[Optional[int]]) are refused by route #458 or fail typing in every model;
      only the AUGMENTED element store leaks (F5); in the default model all of g107 is NOT-PROVED / WHY3-TYPE-ERROR.
  g110 / g111: calls of generator / async / @contextmanager / decorated functions whose body raises, before a read of a maybe-unbound local
      or a `1 // 0`: all refused (route #271 generator-call rule, the unknown-callee rule, the decorator rule; `#@ no_exception NameError` is
      not a claimable exception -- Known: IndexError, KeyError, StopIteration, ValueError, ZeroDivisionError).
  g112: SPECIFIC claims (`no_exception ValueError` / KeyError / IndexError / ZeroDivisionError / StopIteration) against operations that raise
      that class or a subclass (decode / encode -> Unicode*Error, set.remove / set.pop / dict.popitem / dict.pop, 0 ** -1, 0.0 ** -1, divmod,
      x % 0.0, list.remove / index, str.index, int(s), chr(-1), bytes.fromhex, math.sqrt(-1), heappop([]), str / range / tuple index, next on an
      empty iterator, unpacking s.split): 0 PROVED (17 refused, 5 NOT-PROVED, 3 WHY3-TYPE-ERROR).
  g113: a DEPENDENCY rebinding its own claimed function after the def (second def, lambda assignment, if / try defs, `__code__` swap,
      decorator replacement, for / walrus / match / with binders, `from operator import neg as g`, a later class g) under an ensures-only
      importer: 0 PROVED (12 refused) -- F3's function rows are specifically PEER-module writes (`import h; h.g = ...` elsewhere).
  Modes: typed / store over the C dirs (g87 / g88 / g89 / g94 / g95: 131 x 2) -> no new PROVED (F1 is a Why3 type error there); over every
      dir with a PROVED row (new.lst: 242 x 2) -> only F2 / F3 rows that are model-independent (g92 / g93 function rebinding, also counted as
      (probe, mode) pairs) and the F5 rows; concurrent on g85 -> as hoare; --fun f on all 87 confirmed probes -> every default-model row still
      proves (77), the 10 F5 rows are typed / store-only (not proved under hoare).
METHOD NOTES: multi-file probes run in CPython WITHOUT -I (cpy2.sh: -E -s) so the script directory is on sys.path. PROCESS NOTE: one foreground
  `timeout 170 heavy.sh run.sh g107` call hit its timeout; the killed heavy.sh released its slot while one orphan pycsl run (g107/e10709, inside
  the MemoryMax=6G scope) finished on its own ~15 s later -- for those seconds my job ran outside the slot accounting; g107 was then re-run
  from scratch with nohup + bounded polling. A base worktree /home/fabrice/git/pycsl-rt40-base (d5b93a934) was added for regression attribution
  (left in place; remove with `git worktree remove /home/fabrice/git/pycsl-rt40-base`).

VERIFY (one to three exemplars per family copied to verify/ with their helper modules, re-proved + re-run on the rt40 tree by verify.sh inside heavy.sh):
  F1_t9102_container_capture_list.py            pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  F1b_t9300_tuple_display_subscript.py          pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  F1c_t9203_nested_def_closure_param.py         pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  F2_a8109_ens_builtins_dict_exec.py            pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 0
  F2b_v9700_bdict_setattr_func_ens.py           pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 0
  F3_a8601_dep_writes_main_ens.py               pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 0
  F3b_c8990_dep_rebinds_main_callee_ens.py      pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 0
  F3c_r9600_peer_rebinds_dep_func_ens.py        pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 0
  F4_b9005_dunder_file_plus.py                  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError can only concatenate str (not "int") to str
  F4b_d9404_file_ens_value.py                   pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract ''
  F5_m8908_nested_elem_isub.py                  pycsl --memory-model typed: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError unsupported operand type(s) for -=: 'list' and 'int'
  F5b_m8923_walrus_alias_imul.py                pycsl --memory-model store: rc=0 Verification SUCCESS  CPython: VIOLATION contract 4
  F6_y9805_or_alias_imul.py                     pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 4
  F1d_g10410_self_display_subscript.py          pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  F5c_e10701_str_elem_isub.py                   pycsl --memory-model store: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError unsupported operand type(s) for -=: 'str' and 'int'
  F6b_k10302_list_or_lt.py                      pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError '<' not supported between instances of 'list' and 'int'
  re-run: cd /home/fabrice/git/pycsl-rt40 && PYTHONHASHSEED=0 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py
          /home/fabrice/git/pycsl/scratchpad/rt40/verify/<probe> --import-path src/pycsl [<flags>]; CPython: cd verify && /home/fabrice/git/pycsl-rt40/.venv/bin/python3 -E -s <probe>

STATUS: 2026-10-30T07:29:16Z -- regenerated by mkfind.py (129 confirmed)
```
