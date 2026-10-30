# OPEN ROUTE #490 — A str / None LITERAL IN AN INT-TYPED VALUE SLOT IS HASHED TO AN INT (`_coerce_to_int`): MIXED-TYPE TERNARIES, MIXED DICT DISPLAYS, A None / str ARGUMENT OR ANNOTATED BINDING ARE INT ARITHMETIC (DEFAULT MODEL; #486 RESIDUE AND BEYOND)
**Status: OPEN, Severity 1.** Red-team round 41 (2026-10-30, on 973a2755d after #474 / #481-#487: 634 probes + 556 re-runs + 2533 mode re-proofs / 237 confirmed (probe, mode) pairs on 153 probes; rt40's 129 all closed). Census TSV `scratchpad/rt41/census.tsv`; the family block below is quoted from `scratchpad/rt41/FINDINGS.txt`.
Witnesses `witnesses-r490/` (53): `g125_a12506_mixed_dict_value.py`, `g125_a12507_ternary_mixed.py`, `g129_x129000_ternary_aug_add.py`, `g129_x129001_ternary_add.py`, `g129_x129002_ternary_mul_int.py`, `g129_x129003_ternary_lt.py`, `g129_x129004_ternary_neg.py`, `g129_x129005_ternary_floordiv.py`, `g129_x129010_ternary_str_first_aug_add.py`, `g129_x129011_ternary_str_first_add.py`, `g129_x129012_ternary_str_first_mul_int.py`, `g129_x129013_ternary_str_first_lt.py`, `g129_x129014_ternary_str_first_neg.py`, `g129_x129015_ternary_str_first_floordiv.py`, `g129_x129020_dict_value_aug_add.py`, `g129_x129021_dict_value_add.py`, `g129_x129022_dict_value_mul_int.py`, `g129_x129023_dict_value_lt.py`, `g129_x129024_dict_value_neg.py`, `g129_x129025_dict_value_floordiv.py`, `g129_x129030_dict_value_direct_aug_add.py`, `g129_x129031_dict_value_direct_add.py`, `g129_x129032_dict_value_direct_mul_int.py`, `g129_x129033_dict_value_direct_lt.py`, `g129_x129034_dict_value_direct_neg.py`, `g129_x129035_dict_value_direct_floordiv.py`, `g129_x129040_dict_value_str_first_aug_add.py`, `g129_x129041_dict_value_str_first_add.py`, `g129_x129042_dict_value_str_first_mul_int.py`, `g129_x129043_dict_value_str_first_lt.py`, `g129_x129044_dict_value_str_first_neg.py`, `g129_x129045_dict_value_str_first_floordiv.py`, `g129_x129050_dict_get_aug_add.py`, `g129_x129051_dict_get_add.py`, `g129_x129052_dict_get_mul_int.py`, `g129_x129053_dict_get_lt.py`, `g129_x129054_dict_get_neg.py`, `g129_x129055_dict_get_floordiv.py`, `g129_x129080_ternary_none_aug_add.py`, `g129_x129081_ternary_none_add.py`, `g129_x129082_ternary_none_mul_int.py`, `g129_x129083_ternary_none_lt.py`, `g129_x129084_ternary_none_neg.py`, `g129_x129085_ternary_none_floordiv.py`, `g129_x129124_dict_value_none_neg.py`, `g131_s13102_call_int_param_none.py`, `g131_s13103_annot_int_str.py`, `g131_s13110_ternary_return.py`, `g131_s13114_mixed_ternary_compare.py`, `g134_w13421_ternary_tuple_arm.py`, `g134_w13427_dict_mixed_param_default.py`, `g134_w13429_ternary_str_hash_eq.py`, `g134_w13431_call_none_to_int_param_mul.py`.

Driver repro: `scratchpad/rp41/repro.sh` (session scratchpad) on 2223318e5, 2026-10-30T19:49Z: all 12 rt41 verify exemplars (incl. typed / store) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F2 A str / None LITERAL IN AN INT-TYPED VALUE SLOT IS HASHED TO AN INT (`_coerce_to_int`): MIXED-TYPE TERNARIES, MIXED DICT DISPLAYS, A None / str ARGUMENT OR ANNOTATED BINDING ARE INT ARITHMETIC (DEFAULT MODEL; #486 RESIDUE AND BEYOND) (53)
  WHAT: when a ternary's arms (`1 if n > 0 else 'a'`, `'a' if n == 0 else 1`, `None if n == 0 else 1`), a dict display's values (`{'a': 1, 'b': 'x'}`, `{'a': 1, 'b': None}`, `d.get('b', 0)`), a call argument (`g(None)` for `g(x: int)`), an annotated binding (`x: int = 'a'`) or a helper's return (`return 1 if n > 0 else 'a'` in `-> int`) mix an int with a str / None LITERAL, the emitter lowers the whole value as a Why3 `int` and the str / None literal as an int constant, so `y + 1`, `y += 1`, `y * 2`, `y < 3`, `-y`, `y // 1` are int arithmetic that cannot raise. BREAKDOWN (53 probes, default model only; typed / store fail Why3 typing): g129 43 (13 mixed sources x 6 operators: ternary int/str either order, ternary None, dict display int/str either order, `d['b']` direct and through a local, `d.get('b', 0)`, dict int/None under unary minus), g125 2 (#486's own augmented targets a12506 / a12507), g131 4 (s13102 `g(None)` to `g(x: int)`, s13103 `x: int = 'a'  # type: ignore`, s13110 a helper `-> int` returning `1 if n > 0 else 'a'`, s13114 mixed ternary `<`), g134 4 (w13421 tuple arm `1 if n else (1, 2)`, w13427 `for v in {1: 1, 2: 'x'}.values(): s += v`, w13429 mixed ternary `>`, w13431 `g(None)` to `x * 2`). HONESTY NOTE: s13102 / s13103 / w13431 are ILL-TYPED calls / bindings a static type checker would flag; they are counted because pycsl claims `no_exception \all` for them and does not reject the type mismatch.
  EXEMPLAR: g129/x129001_ternary_add.py (`#@ no_exception \all def f(n: int) -> int: y = 1 if n > 0 else 'a'; z = y + 1; return 0`, f(0)); g129/x129021_dict_value_add.py (`d = {'a': 1, 'b': 'x'}; y = d['b']; z = y + 1`); g129/x129081_ternary_none_add.py (`y = None if n == 0 else 1; z = y + 1`); g131/s13102_call_int_param_none.py (`g(None)` with `def g(x: int) -> int: return x + 1`); g125/a12507_ternary_mixed.py (`y = 1 if n > 0 else 'a'; y += 1`, route #486's own surface)
  CPYTHON: TypeError (can only concatenate str (not "int") to str / unsupported operand type(s) for +: 'NoneType' and 'int' / '<' not supported between instances of 'str' and 'int' / bad operand type for unary -) under `#@ no_exception \all`
  WHY IT PROVES: module6_whyml/expressions.py:1159-1172 (`_coerce_to_int`: 'String literals -> int hash', `return str(stable_hash(whyml_str))`; documented there as a 'benign collapse (A7)') is applied to BOTH arms of every ternary outside a string context at expressions.py:19615-19616 (`body = self._coerce_to_int(body)`; `orelse = self._coerce_to_int(orelse)`), and on the same fallback for dict-display values / call arguments in an int slot (57 call sites); a `None` arm / argument lowers to the opaque int `pycsl_none` (`val function pycsl_none : int`, expressions.py:1340). EMITTED (emit/x129001_ternary_add.mlw): `y := (if (n > 0) then 1 else 747471683); z := (!y + 1)`; emit/x129021_dict_value_add.mlw: `map_update_some (map_update_some (const (None: option int)) "a" 1) "b" 976090257` (the dict's value type is `int`, 'x' hashed); emit/x129081_ternary_none_add.mlw: `y := (if (n = 0) then pycsl_none else 1); z := (!y + 1)`. Route #486's judgement (src/pycsl/pycsl.py:16217-16413) types the joined value as UNKNOWN and, in the hoare-family (default) model, leaves an unknown target to Why3 typing (:16376-16386, its named residual) on the premise that a non-int value 'is not a Why3 int, so integer arithmetic on it fails Why3 typing (fail closed)' -- true for lists / dicts / records (x12909x / x12911x: WHY3-TYPE-ERROR), FALSE for a hashed str / None literal; plain BinOp / Compare / UnaryOp reads (not augmented) are not judged by #486 at all, and route #458's element-type check sees only list / tuple subscripts (x12906x / x12907x refused). Typed / store fail Why3 typing (0 PROVED). str VARIABLES / parameters in the same positions are a Why3 type error (s13118 / s13119): the leak is the LITERAL hash.
  PROPOSED SYSTEMATIC REPAIR: REFUSE BY DEFAULT: `_coerce_to_int`'s string-literal hash (and the None-to-int lowering) may only produce a value that NO Python operation observes as a number -- a dict key / abstract-op argument the model never computes with; in a VALUE position (a binding, an argument to a typed parameter, a return, an operand) a str / bytes / None literal whose slot is int-typed is REFUSED (new PYCSL-M6-LITERAL-INT-HASH, naming the arm). Equivalently, type a ternary / dict display / BoolOp by the JOIN of its arms and refuse the join of an int with a str / None (allow-list: int+int, str+str, Optional handled by the option-record path). Extend route #486's judgement to plain BinOp / Compare / UnaryOp operands (not only AugAssign targets), so its 'unknown -> Why3 typing' residual is never relied on for a str / None value. Witness: the F2 probes; control: `y = 1 if n > 0 else 2; y + 1` and `d = {'a': 1, 'b': 2}; d['b'] + 1` stay PROVED; a dict key `{'a': 1}['a']` keeps its hash.
  PROBES: g125/a12506_mixed_dict_value.py g125/a12507_ternary_mixed.py g129/x129000_ternary_aug_add.py g129/x129001_ternary_add.py g129/x129002_ternary_mul_int.py g129/x129003_ternary_lt.py g129/x129004_ternary_neg.py g129/x129005_ternary_floordiv.py g129/x129010_ternary_str_first_aug_add.py g129/x129011_ternary_str_first_add.py g129/x129012_ternary_str_first_mul_int.py g129/x129013_ternary_str_first_lt.py g129/x129014_ternary_str_first_neg.py g129/x129015_ternary_str_first_floordiv.py g129/x129020_dict_value_aug_add.py g129/x129021_dict_value_add.py g129/x129022_dict_value_mul_int.py g129/x129023_dict_value_lt.py g129/x129024_dict_value_neg.py g129/x129025_dict_value_floordiv.py g129/x129030_dict_value_direct_aug_add.py g129/x129031_dict_value_direct_add.py g129/x129032_dict_value_direct_mul_int.py g129/x129033_dict_value_direct_lt.py g129/x129034_dict_value_direct_neg.py g129/x129035_dict_value_direct_floordiv.py g129/x129040_dict_value_str_first_aug_add.py g129/x129041_dict_value_str_first_add.py g129/x129042_dict_value_str_first_mul_int.py g129/x129043_dict_value_str_first_lt.py g129/x129044_dict_value_str_first_neg.py g129/x129045_dict_value_str_first_floordiv.py g129/x129050_dict_get_aug_add.py g129/x129051_dict_get_add.py g129/x129052_dict_get_mul_int.py g129/x129053_dict_get_lt.py g129/x129054_dict_get_neg.py g129/x129055_dict_get_floordiv.py g129/x129080_ternary_none_aug_add.py g129/x129081_ternary_none_add.py g129/x129082_ternary_none_mul_int.py g129/x129083_ternary_none_lt.py g129/x129084_ternary_none_neg.py g129/x129085_ternary_none_floordiv.py g129/x129124_dict_value_none_neg.py g131/s13102_call_int_param_none.py g131/s13103_annot_int_str.py g131/s13110_ternary_return.py g131/s13114_mixed_ternary_compare.py g134/w13421_ternary_tuple_arm.py g134/w13427_dict_mixed_param_default.py g134/w13429_ternary_str_hash_eq.py g134/w13431_call_none_to_int_param_mul.py

PROVED BUT NOT COUNTED / ENVIRONMENT-DEPENDENT (excluded.txt):
  # DECLARED RESIDUAL / DOCUMENTED OUT OF SCOPE / USER-DECLARED (proved, CPython breaches, not counted):
  g123/m12381_dep_rewrites_peer_file.py | VIOLATION contract 0 | DECLARED RESIDUAL of routes #483 / #484 (file-system writes at import changing a module the verifier already read: `os` / `pathlib` are on the allow-list), named in route483-dependency-builtins-mapping.md -- not counted
  g128/d12894_t_list_param_len_of_record_elem_list.py | VIOLATION contract 7 | USER-DECLARED FRAME: the \trusted callee carries `#@ assigns xs`; the implicit `len(o)` write to the other argument contradicts the user's own trusted frame (route #482 judges only defs with NO assigns) -- not counted (the same implicit channel without assigns is F1)
  g215/g533_variant_deep_recursion.py | VIOLATION RecursionError maximum recursion depth exceeded | DOCUMENTED OUT OF SCOPE: RecursionError (annotations.md: "RecursionError is out of scope (route #269) ... a terminating (`\variant`) recursion under `no_exception \all` is proved regardless of its depth") -- not counted
  g225/n100_nan_eq_self.py | VIOLATION contract nan | FLOAT-FINITE declared model assumption (docs/pycsl-static-semantics-reference.md "declared model assumptions"; --strict-float-finite covers it; rt39 excluded the same rows) -- not counted
  g225/n101_nan_trichotomy.py | VIOLATION contract 3 | FLOAT-FINITE declared model assumption (docs/pycsl-static-semantics-reference.md "declared model assumptions"; --strict-float-finite covers it; rt39 excluded the same rows) -- not counted
  # PROVED, CPython raises, but NO CLAIM COVERS IT (ensures-only claim; an exception is not an ensures breach):
  # PROVED and CPython AGREES or does not finish in 20 s (controls / HANG rows; mode twins listed with @mode):
  g125/a12531_bool_add.py | result 2 | control
  g126/o12618_str_or_str_alias.py | result 2 | control
  g126/o12621_and_bool_int_value.py | result False | control
  g126/o12622_and_returns_false.py | result 5 | control
  g130/d13006_t_max_two_gt.py | result 0 | control
  g130/d13007_t_min_two_lt.py | result 0 | control
  g134/w13428_ternary_str_eq_ens.py | result 0 | control
  g134/w13430_ternary_none_is_none.py | result 1 | control
  g140/c14138_combining_len.py | result 2 | control
  g140/c14157_str_mul_neg.py | result 0 | control
  g204/n024_pow_huge.py | HANG (timeout 20s) | HANG: no exception observed in 20 s, not counted
  g205/s023_fstr_x_huge_ok.py | result 2 | control
  g213/z021_round_ndigits_huge_int.py | HANG (timeout 20s) | HANG: no exception observed in 20 s, not counted
  g213/z025_pow_huge_exponent.py | HANG (timeout 20s) | HANG: no exception observed in 20 s, not counted
  g228/k108_ensures_chained_cmp.py | result 5 | control
  g228/k112_old_param_rebound.py | result 2 | control
  g254/z2507_ens_neg_index_oob.py | result 0 | control

NOTES / AXES THAT HELD (no counted false proof -- negative results for the coordinator):
  (B) #482 / #481 beyond F1: the EXPLICIT spellings are closed -- a user method NAMED like a read-only one (`o.get()`, `o.copy()`,
      `o.count(1)`, `o.lower()`, `o.__len__()`) is a lowered call and route #317 refuses it (PYCSL-VAL-ARG-UNFRAMED, d12027-d12031); a
      property getter writing self (d12032 / d12132) is NOT-PROVED; `hash(o)` is refused by route #349; `for _ in o`, `x, = o`,
      `any(o)`, `iter(o)` / `reversed(o)` / `enumerate(o)` / `zip(o)` / `min(o)` fail Why3 typing (fail closed); the same bodies in a
      VERIFIED callee or a VERIFIED caller (g120 d121xx, g134 w1341x) fail Why3 typing; a dunder writing a module global (w13401) is
      refused; `max(o, C())` / `min(o, C())` dispatch to the OTHER instance's dunder (CPython agrees, d13006 / d13007: controls).
      g121 aliasing THROUGH RETURN VALUES (48 probes: a `\trusted` / verified / `assigns \nothing` / ensures-only callee returning its
      list / dict / record parameter, a field, `self`, a tuple holding the parameter, imported) and record FIELDS sharing one list
      (two records on one list, local-then-field, field-to-local, param-into-field, class-level shared list, `[[0]] * 2`, `[a, a]`,
      dict values): 0 PROVED in default / typed / store (routes #283 / #289 / #290 refuse, the rest fail Why3 typing or NOT-PROVED).
      g127: dict-parameter direct store / del / augmented store in a `\trusted` callee fail Why3 typing; `__init__` storing a parameter
      into `self` then mutating it is refused; set.discard / dict.setdefault are refused by #482.
  (B) #483 / #484 (g123, 36 probes): every import-time namespace writer spelled WITHOUT a dunder name (operator.attrgetter('__globals__'),
      attrgetter('__dict__'), methodcaller('__setitem__'), inspect.getmodule, gc.get_objects / get_referrers, attrgetter('f_globals')
      of a frame, importlib.import_module) is refused in a dependency, in the claimed file and in a peer; stdlib-state mutators at import
      are refused under `no_exception` by route #466 (dependency) / #461 (claimed file): warnings.simplefilter('error') + `~bool`,
      sys.setrecursionlimit, sys.set_int_max_str_digits(640); math.pi / string.digits rebinding and attrgetter('__dict__')(math) are
      refused (route #322 float constant / #483); a dependency decorator replacing the claimed callee and an `__init_subclass__` hook
      are refused. The one PROVED row (m12381: a dependency REWRITES a peer's .py file at import) is #483's named residual (excluded).
  (B) #485 (g124, 57 probes): no PROVED row -- every 'bound only where it never binds the module global' spelling is refused (#444,
      #459, #325 origin, #322, #264, #461) or NOT-PROVED; class-scope vs comprehension / genexp / lambda scope refused; the
      comprehension-variable leak probe fails Why3 typing.
  (B) #486 (g125, 49 probes) under typed / store: 0 PROVED (42 refused, 7 type errors); default: the only PROVED breaches are the two
      MIXED-type targets of F2 (a12506 dict value, a12507 ternary); str `%=` / `*=` / `+=` edges refused (#441 / #447); int `<<=` / `>>=`
      / `**=` with negative operands NOT-PROVED; in-place list / dict / set operators through aliases fail typing or are refused (#279).
  (B) #487 (g126, 39 probes): 0 counted -- nested and / or, walrus inside truth tests, comprehensions, lambda, f-strings, mixed operand
      types, `d or {}` alias, defaults and and / or inside requires / ensures / assert are refused or fail typing; the 3 PROVED rows are
      controls (str-or-str, bool-and-int) where CPython agrees. (Over-refusal noted, not a soundness issue: `len(a or b)`, `(a or b) ==
      [1]`, `for e in a or b`, `7 in (a or b)`, `sum(a or b)`, `return a or b` are refused although CPython agrees.)
  (C) g140 (119 probes, default / typed / store): 0 false proofs -- `\old` with run-time aliasing of two parameters / nested lists / a
      record field / dict / set is refused by route #290; ensures / requires that would raise are NOT-PROVED; step slices, bytes /
      bytearray, dict / set equality and key-collapse (`{1: .., True: ..}`), sorted / min / max stability, math domain errors, int() /
      float() parsing, negative / big operands in ensures, unicode length-changing case maps and separators: refused, NOT-PROVED or
      type errors; the 2 PROVED rows (combining-mark len, negative str repetition) are controls where CPython agrees.
  (C) RE-RUN of the rt37 e1 / e2 / e4 / e5 / e6 / e10 / e11 / e13, rt38 g5, rt39 g25 / g26 / g27 / g28 / g54 dirs (556 probes, dirmap.tsv)
      on this tree: default model PROVED 10 / REFUSED 276 / NOT-PROVED 148 / WHY3-TYPE-ERROR 122, and NONE of the 10 PROVED rows is a
      counted breach: 6 controls (CPython agrees), 3 HANG rows (n024 / z021 / z025: huge `**` / `round(5, -n)`, CPython does not
      finish in 20 s), 2 FLOAT-FINITE declared-assumption rows (g225 n100 / n101 NaN, excluded by rt39 too) and 1 RecursionError row
      (g215 g533, documented out of scope, route #269). Under --memory-model typed and store (1112 re-proofs, the FIRST typed / store
      run of the rt37 / rt38 dirs): 0 PROVED (REFUSED 558, WHY3-TYPE-ERROR 550, NOT-PROVED 4).
  Modes: every new dir and every re-run dir proved under typed AND store; F1's imported / `\trusted`-dunder variants (g130 d13050 /
      d13051 / d13060, g132, g133) ALSO prove under typed and store (counted as (probe, mode) pairs); F2 fails Why3 typing under typed
      / store. --fun f: every default-mode confirmed probe re-proved with `--fun f` -> PROVED (identical; not counted separately).
  RecursionError (sys.setrecursionlimit) is out of scope by documentation (annotations.md: route #269), and the probe is refused anyway.

VERIFY (one to three exemplars per family copied to verify/ with their helper modules, re-proved + re-run on the rt41 tree by verify.sh inside heavy.sh):
  a12507_ternary_mixed.py                       pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError can only concatenate str (not "int") to str
  d12000_t_len.py                               pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  d12002_t_if_truth.py                          pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  d12012_t_eq.py                                pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  d12892_t_method_len_self.py                   pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  d13050_imported_trusted_len.py                pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  i13200_imported_unmarked_len.py               pycsl --memory-model store: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  s13102_call_int_param_none.py                 pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError unsupported operand type(s) for +: 'NoneType' and 'int'
  x129001_ternary_add.py                        pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError can only concatenate str (not "int") to str
  x129021_dict_value_add.py                     pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError can only concatenate str (not "int") to str
  x129081_ternary_none_add.py                   pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError unsupported operand type(s) for +: 'NoneType' and 'int'
  d13300_t_len.py                               pycsl --memory-model typed: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  re-run: cd /home/fabrice/git/pycsl-rt41 && PYTHONHASHSEED=0 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py
          /home/fabrice/git/pycsl/scratchpad/rt41/verify/<probe> --import-path src/pycsl [<flags>]; CPython: cd verify && /home/fabrice/git/pycsl-rt41/.venv/bin/python3 -E -s <probe>

STATUS: 2026-10-30T19:45:43Z -- regenerated by mkfind.py (237 confirmed)
```
