# OPEN ROUTE #480 — NON-INT BUILTIN OBJECTS MODELLED AS INTS -- BUILTIN NAMES, SINGLETONS, METHOD ATTRIBUTES (ROUTE #325 RESIDUE)
**Status: REPAIRED (executor o1, driver run #3; see REPAIR below), Severity 1.** Red-team round 39 (2026-10-29, on d6abee90b after #463-#473: 918 probes + 1064 mode re-proofs / 141 confirmed (probe, mode) pairs; rt38's 142 counted all closed). Census TSV `scratchpad/rt39/census.tsv`; the family block below is quoted from `scratchpad/rt39/FINDINGS.txt`.
Witnesses `witnesses-r480/` (58): `g62_b3201_notimplemented_truthiness.py`, `g62_b3202_notimplemented_not.py`, `g62_b3203_notimplemented_var.py`, `g62_b3206_notimplemented_and.py`, `g63_n3312_notimpl_bool_call.py`, `g63_n3314_notimpl_or.py`, `g63_n3316_notimpl_ifexp.py`, `g63_n3317_notimpl_any.py`, `g63_n3318_notimpl_ensures_value.py`, `g64_o3400_ellipsis_plus.py`, `g64_o3401_ellipsis_lit_plus.py`, `g64_o3402_notimpl_plus.py`, `g64_o3403_notimpl_lt.py`, `g64_o3404_ellipsis_lt.py`, `g64_o3405_notimpl_neg.py`, `g64_o3406_ellipsis_mul.py`, `g64_o3412_ellipsis_aug.py`, `g64_o3415_notimpl_pow.py`, `g65_v3500_len_plus.py`, `g65_v3501_int_type_plus.py`, `g65_v3511_builtins_true_div.py`, `g65_v3519_ellipsis_name_plus.py`, `g66_w3600_max_plus.py`, `g66_w3601_str_plus.py`, `g66_w3604_exception_plus.py`, `g66_w3605_id_plus.py`, `g66_w3606_sorted_plus.py`, `g66_w3607_range_plus.py`, `g66_w3608_object_plus.py`, `g66_w3610_isinstance_plus.py`, `g66_w3611_open_plus.py`, `g66_w3612_input_plus.py`, `g66_w3613_abs_plus.py`, `g66_w3614_sum_plus.py`, `g66_w3615_bool_plus.py`, `g66_w3620_len_mul.py`, `g66_w3621_len_neg.py`, `g66_w3622_int_lt.py`, `g66_w3625_len_aug.py`, `g66_w3626_len_bitand.py`, `g66_w3627_int_mod.py`, `g68_e3811_ellipsis_ternary_value_plus.py`, `g70_a4000_len_attr.py`, `g70_a4001_int_attr.py`, `g70_a4002_notimpl_attr.py`, `g70_a4012_int_real_plus.py`, `g70_a4013_str_upper_unbound.py`, `g73_t4303_int_bit_length.py`, `g73_t4304_int_dunder_add.py`, `g74_u4401_int_conjugate_plus.py`, `g74_u4402_int_to_bytes_lt.py`, `g74_u4406_int_as_integer_ratio_plus.py`, `g74_u4407_int_is_integer_mul.py`, `g74_u4410_int_dunder_class_plus.py`, `g75_x4502_bool_bit_length_plus.py`, `g75_x4506_int_param_dunder_mul.py`, `g75_x4507_int_param_real_method_mix.py`, `g75_x4508_int_from_bytes_unbound.py`.

Driver repro: `scratchpad/rp39/repro.sh` (session scratchpad) on d6abee90b, 2026-10-29T23:41Z: all 16 rt39 verify exemplars (2+ per family) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F7 NON-INT BUILTIN OBJECTS MODELLED AS INTS -- BUILTIN NAMES, SINGLETONS, METHOD ATTRIBUTES (ROUTE #325 RESIDUE) (58)
  WHAT: a builtin name used as a VALUE (`max`, `len`, `int`, `str`, `print`, `open`, `Exception`, ...), the `NotImplemented` singleton and `...` / `Ellipsis` are lowered to opaque int constants (`val constant max : int`, `notImplemented`, `pycsl_ellipsis`) that route #325's origin rule does not track (it tracks module-level values of THIS file), and an EXISTING attribute of an int-typed value is read as an int whatever its kind (`n.bit_length`, `n.conjugate`, `n.__add__`, `n.__class__` are method / type objects), so int operators, orderings, augmented assignments, attribute reads (`len.zz`, `int.real + n`) and -- for NotImplemented, a TypeError since CPython 3.14 -- truth tests on them prove under no_exception while CPython raises TypeError / AttributeError
  EXEMPLAR: g66/w3600_max_plus.py (`#@ no_exception \all`, `def f(n: int) -> int: return max + n`); g62/b3201_notimplemented_truthiness.py (`return 1 if NotImplemented else 0`); g64/o3401_ellipsis_lit_plus.py (`return ... + n`)
  CPYTHON: TypeError: unsupported operand type(s) for +: 'builtin_function_or_method' and 'int' (w3600; also `str + n`, `range + n`, `object + n`, `int < n`, `-len`, `len & 1`, `int % 2`, `x = len; x += 1`, `print < n`); TypeError: NotImplemented should not be used in a boolean context (b3201: CPython 3.14 made bool(NotImplemented) an error; also `not`, `bool()`, `and` / `or`, ternary, `any([...])`); TypeError for `... + n`, `NotImplemented < n`, `-NotImplemented`, `NotImplemented ** 2`, `Ellipsis + n`; AttributeError for `len.zz`, `int.zz`, `NotImplemented.zz` and TypeError for `int.real + n`, `str.upper + n` (g70); TypeError for `n.bit_length + 1`, `n.__add__ + 1`, `n.conjugate + 1`, `n.to_bytes < 1`, `n.as_integer_ratio + 1`, `n.is_integer * 2`, `n.__class__ + 1` on an int parameter (g73 / g74; data attributes `n.real` / `n.imag` / `n.numerator` are rightly ints and a missing `n.zz` is refused by route #445).
  WHY IT PROVES: The emitted WhyML for w3600 is `val constant max : int` ... `(max + n)`; for b3201 `(if (notImplemented <> 0) then 1 else 0)`; for o3401 `pycsl_ellipsis + n` (route #40's opaque `val function pycsl_ellipsis : int`); for t4303 (`n.bit_length + 1`) `val get_bit_length (x: int) : int` ... `((get_bit_length n) + 1)` -- the attribute-read fallback over an int PARAMETER. Route #325 (pycsl.py:20522-20545, PYCSL-R325-OPAQUE-INT-FALLBACK) refuses int theory on a fallback only when it stands for an ORIGIN -- a module-level Python value of this file, a component / call / derivation of one -- and keeps the int model for documented int-returning callables; a bare BUILTIN NAME used as a value, the two singletons and an attribute read off a builtin-typed PARAMETER are fallbacks with no origin, so `+ - * % & < -x +=` and truth tests are admitted with no TypeError obligation. (`list + n`, `dict + n`, `type + n`, a user def / class / module, `type(n)`, `zip()` ARE refused: the leak is exactly the builtin-name / singleton fallbacks.)
  PROPOSED SYSTEMATIC REPAIR: ORIGIN = EVERY FALLBACK: make route #325 polarity total -- every `val constant` / `val function` the emitter synthesises for a value it does not model (a builtin name, `NotImplemented`, `Ellipsis`, `...`, any future fallback) is an origin by construction (tag it at emission, not by a name list), so the same bind / pass / return / `=`-against-a-different-value allow-list applies; and give the singletons their own abstract Why3 type (`type pyobj`), not `int`, so no int operator type-checks on them. Truth tests: allow-list the operand types with a modelled truth value and emit an unprovable TypeError obligation for `NotImplemented`. Witness: the F7 probes; control: `len(a) + 1`, `x is NotImplemented`, `x is ...` keep proving.
  PROBES: g62/b3201_notimplemented_truthiness.py g62/b3202_notimplemented_not.py g62/b3203_notimplemented_var.py g62/b3206_notimplemented_and.py g63/n3312_notimpl_bool_call.py g63/n3314_notimpl_or.py g63/n3316_notimpl_ifexp.py g63/n3317_notimpl_any.py g63/n3318_notimpl_ensures_value.py g64/o3400_ellipsis_plus.py g64/o3401_ellipsis_lit_plus.py g64/o3402_notimpl_plus.py g64/o3403_notimpl_lt.py g64/o3404_ellipsis_lt.py g64/o3405_notimpl_neg.py g64/o3406_ellipsis_mul.py g64/o3412_ellipsis_aug.py g64/o3415_notimpl_pow.py g65/v3500_len_plus.py g65/v3501_int_type_plus.py g65/v3511_builtins_true_div.py g65/v3519_ellipsis_name_plus.py g66/w3600_max_plus.py g66/w3601_str_plus.py g66/w3604_exception_plus.py g66/w3605_id_plus.py g66/w3606_sorted_plus.py g66/w3607_range_plus.py g66/w3608_object_plus.py g66/w3610_isinstance_plus.py g66/w3611_open_plus.py g66/w3612_input_plus.py g66/w3613_abs_plus.py g66/w3614_sum_plus.py g66/w3615_bool_plus.py g66/w3620_len_mul.py g66/w3621_len_neg.py g66/w3622_int_lt.py g66/w3625_len_aug.py g66/w3626_len_bitand.py g66/w3627_int_mod.py g68/e3811_ellipsis_ternary_value_plus.py g70/a4000_len_attr.py g70/a4001_int_attr.py g70/a4002_notimpl_attr.py g70/a4012_int_real_plus.py g70/a4013_str_upper_unbound.py g73/t4303_int_bit_length.py g73/t4304_int_dunder_add.py g74/u4401_int_conjugate_plus.py g74/u4402_int_to_bytes_lt.py g74/u4406_int_as_integer_ratio_plus.py g74/u4407_int_is_integer_mul.py g74/u4410_int_dunder_class_plus.py g75/x4502_bool_bit_length_plus.py g75/x4506_int_param_dunder_mul.py g75/x4507_int_param_real_method_mix.py g75/x4508_int_from_bytes_unbound.py

PROVED BUT NOT COUNTED / ENVIRONMENT-DEPENDENT (excluded.txt):
  # ENVIRONMENT-DEPENDENT (proved, CPython raises, but the outcome depends on installed third-party packages):
  g39/l800_lark_type_checking_name.py | VIOLATION module-level ImportError: cannot import name 'InteractiveParser' from 'lark.lark' (/home/f | installed-library import judged by a STATIC scan of the library's source (route #461/#466 role L/I: a name bound only under `if TYPE_CHECKING:` counts as bound; a library submodule whose own imports fail is never imported) -- reproducible on this repo's .venv, but the verdict depends on which third-party packages / versions are installed
  g39/l801_packaging_type_checking_name.py | VIOLATION module-level ImportError: cannot import name 'Unpack' from 'packaging.version' (/home/fabr | installed-library import judged by a STATIC scan of the library's source (route #461/#466 role L/I: a name bound only under `if TYPE_CHECKING:` counts as bound; a library submodule whose own imports fail is never imported) -- reproducible on this repo's .venv, but the verdict depends on which third-party packages / versions are installed
  g39/l802_pygments_sphinxext_import.py | VIOLATION module-level ModuleNotFoundError: No module named 'docutils' | installed-library import judged by a STATIC scan of the library's source (route #461/#466 role L/I: a name bound only under `if TYPE_CHECKING:` counts as bound; a library submodule whose own imports fail is never imported) -- reproducible on this repo's .venv, but the verdict depends on which third-party packages / versions are installed
  g39/l803_from_pygments_import_sphinxext.py | VIOLATION module-level ModuleNotFoundError: No module named 'docutils' | installed-library import judged by a STATIC scan of the library's source (route #461/#466 role L/I: a name bound only under `if TYPE_CHECKING:` counts as bound; a library submodule whose own imports fail is never imported) -- reproducible on this repo's .venv, but the verdict depends on which third-party packages / versions are installed
  g39/l804_lark_tree_rich.py | VIOLATION module-level ImportError: cannot import name 'rich' from 'lark.tree' (/home/fabrice/git/py | installed-library import judged by a STATIC scan of the library's source (route #461/#466 role L/I: a name bound only under `if TYPE_CHECKING:` counts as bound; a library submodule whose own imports fail is never imported) -- reproducible on this repo's .venv, but the verdict depends on which third-party packages / versions are installed
  g39/l805_pluggy_manager_importlib.py | VIOLATION module-level ImportError: cannot import name 'importlib' from 'pluggy._manager' (/home/fab | installed-library import judged by a STATIC scan of the library's source (route #461/#466 role L/I: a name bound only under `if TYPE_CHECKING:` counts as bound; a library submodule whose own imports fail is never imported) -- reproducible on this repo's .venv, but the verdict depends on which third-party packages / versions are installed
  g39/l807_lark_in_f_body.py | VIOLATION ImportError cannot import name 'InteractiveParser' from 'lark.lark' (/home/fabri | installed-library import judged by a STATIC scan of the library's source (route #461/#466 role L/I: a name bound only under `if TYPE_CHECKING:` counts as bound; a library submodule whose own imports fail is never imported) -- reproducible on this repo's .venv, but the verdict depends on which third-party packages / versions are installed
  g39/l808_pygments_in_f_body.py | VIOLATION ModuleNotFoundError No module named 'docutils' | installed-library import judged by a STATIC scan of the library's source (route #461/#466 role L/I: a name bound only under `if TYPE_CHECKING:` counts as bound; a library submodule whose own imports fail is never imported) -- reproducible on this repo's .venv, but the verdict depends on which third-party packages / versions are installed
  # PROVED BUT NOT COUNTED (declared model assumptions / declared modular assumptions):
  g25/n100_nan_eq_self.py | FLOAT-FINITE declared model assumption (docs/pycsl-static-semantics-reference.md 'declared model assumptions'; --strict-float-finite covers it)
  g25/n101_nan_trichotomy.py | FLOAT-FINITE declared model assumption (NaN breaks trichotomy; --strict-float-finite)
  g35/a514_claimed_helper_calls_allowlisted_unbound.py | the imported callee k CLAIMS no_exception: its (false) claim is the declared modular assumption 'verified when its module is' (m203 shape)
  g53/y2400_typed_alias_two_params.py | PARAM-DISJOINT declared model assumption (two list parameters are distinct objects; an external caller passing the same list twice is outside the model; a VERIFIED caller doing so is refused, y2401)
  g53/y2402_typed_alias_frame_other.py | PARAM-DISJOINT declared model assumption (as y2400)
  rerun/g2/m202_helper_false_ensures.py | (A) rt38 row, --fun f: imported helper's own false ensures = declared modular assumption (trusted stub)
  rerun/g2/m203_helper_claimed_raises.py | (A) rt38 row, --fun f: imported helper's own false no_exception claim = declared modular assumption
  rerun/g5/g533_variant_deep_recursion.py | (A) rt38 row, --fun f: recursion limit not modelled (declared)

NOTES / AXES THAT HELD (no counted false proof -- negative results for the coordinator):
  (C) single-file language surfaces are closed on d6abee90b: g22 match (27: guards binding before the test, `case True` identity,
      class / mapping / sequence patterns, __match_args__ arity -- 0 PROVED, refused by #233 / #42 / ... or not proved);
      g23 exception handlers (30: return / break / continue in finally, finally raising, except-variable deletion, empty-loop
      variable, comprehension scope, bare raise, except*, non-exception except class, handler order -- 0 PROVED); g24 iterators
      (25: reused iter / map / filter / enumerate / generators, StopIteration -> RuntimeError, dict / set size change, list
      mutation during iteration, zip strict, len(range) > ssize_t -- 0 PROVED); g26 slicing / min / max / sorted / containers
      (36 -- 0 PROVED); g27 strings (36: unicode case maps that change length, isdigit / isdecimal / isnumeric vs int(), % and
      format-spec errors, encode -- 0 PROVED); g28 + g54 contract semantics (34 + 11: `/` `//` `%` `>>` `&` `~` `**` in ensures with
      Python's floor semantics, \old of aliased / rebound names, quantifier bounds, bool arithmetic, negative indices and empty /
      reversed slices in contracts -- 0 counted PROVED: k108 / k112 prove but their ensures are TRUE in CPython).
  g25 numeric: only n100 / n101 PROVE (NaN), both under the DECLARED FLOAT-FINITE assumption (not counted); inf / overflow /
      int(inf) / round(inf) / huge-int true division / math domain errors / divmod and float-mod signs / digit limit: refused or
      not proved.
  (B) #465: the claimed file in utf-7 (q706), every dependency SyntaxError / bad cookie / BOM+latin-1 (b310-b312, b314) and hidden
      raising code in a utf-7 dependency (q700, q703-q705) are REFUSED -- only the emitter's VALUE view of a dependency leaks (F2).
      #466: importlib.import_module / __import__ / imports in unclaimed callees, nested defs, methods, try/except ImportError,
      sys.modules replacement, __all__ naming a missing name, namespace packages, submodule attribute without import, circular
      import of the main file, package-shadows-module for imports / callees / list length (b300-b305 except values), from-p-import-
      submodule, package __init__ importing a raising sibling, relative import in a top-level helper: all REFUSED -- only PEP 562
      __getattr__ leaks (F4). #467: imported dunders / properties / iterators / callbacks / instance methods of instances returned by
      claimed factories, allow-listed bodies with unbound locals, undefined globals, None globals, negative shifts: all REFUSED (a514
      proves only because the imported callee CLAIMS no_exception -- declared modular assumption). #468: dict / set / nested list /
      object field / tuple element / keyword argument / imported global list / alias inside the helper / sort key: refused, why3
      type errors or not proved. #469 / #470: __wrapped__ / __self__ / __func__ / __qualname__ / decorated __name__ / PEP 695
      __value__ and type-param bounds / globals() / vars() / __doc__: all REFUSED. #471: class statements in generator / async /
      with / try / while / class-in-class / unclaimed callee, slots / kwargs / abstract / protocol / frozen instantiation, patched
      earlier job classes, bases rebound after the main guard: all REFUSED. #472: verifier-path names refused (rt38 set). #473: 28
      empty-list spellings (comprehensions, [0]*0, slices, pop / clear / del, list(()), keyword argument, nested, default_factory,
      returned []) -- 0 PROVED.
  g32 / g36 / g47 in-file name binding and module-level monkey-patching (builtin shadowing, `del` / rebinding of callees by every
      binder, lru_cache / property on f, class attribute / method / __init__ / __code__ / __defaults__ patching, setattr, builtins
      patching, warnings filters, set_int_max_str_digits, constant tables mutated in place): 0 PROVED -- the in-file twins of F1
      (k1400-k1419) are all refused by the Weaver's binding-site guard.
  g43 self-import of the claimed file, g44 `#@ interface` across files (the helpers with an interface weaker than their
      definition are themselves refused): 0 PROVED.
  --fun f: rt38's 147 and the 63 implicit-callee probes of rt38 g3 / g19: no new PROVED.
  --memory-model typed / store over 164 rt38+rt39 probes that are why3-type-errors in hoare, 98 module6-stage refusals and rt38's
      142 single-file frame probes: the only new PROVED rows are the augmented assignments of F5 (a403).
  g53 (hoare!) y2400 / y2402: two list parameters aliased by an UNVERIFIED caller prove -- the DECLARED PARAM-DISJOINT assumption
      (a verified caller passing the same list twice, y2401, is refused), not counted.
  g56 HAPPY region integrity (length-changing slice writes below the region, del, negative indices): `del` spellings REFUSED by
      route #266; the other 7 and the CONTROL (a longer slice write ABOVE the region) are NOT-PROVED (Timeout / Unknown) --
      inconclusive, not a negative result (the shape does not verify even when correct).
  g57 imported defaults (default args / dataclass / __init__ defaults built from a rebound dependency constant), g58 statements
      after the main guard seen by an importer (del / rebinding / clear), g60 imported-class field initialisers and class constants
      under utf-7 / latin-1 / rebinding, g61 list equality in contracts, g69 a typed / store list parameter in int positions, g71
      CLASS statements redefined after the main guard, g72 claimed defs inside the main guard / `if` / `try` / a class under `if` /
      a nested def: 0 PROVED -- F1 / F2 / F3 are specific to module-level constants and plain function defs.
  F7 boundary: builtin-call RESULTS (repr / chr / hex / divmod / vars / iter / map / os.sep / json.dumps ...: g67), `list` / `dict` /
      `type` names, user defs / classes / modules, bound methods of user objects and of str / list / dict / set values, and a
      MISSING attribute (`n.zz`, route #445) are all refused or fail closed.
METHOD NOTES: multi-file probes run in CPython WITHOUT -I (cpy2.sh: -E -s) so the script directory is on sys.path; mode rows
  (--fun / --memory-model) are listed in census_modes.tsv with dir `<dir>@<mode>`; rt38 probes re-proved under a mode were copied
  to mm/<dir>/ with their helpers and their CPython column re-measured (cpy_rt39.tsv). g39 depends on this repo's .venv contents
  (excluded). PROCESS NOTE: while re-ordering the chained queue, killing a WAITING chain shell did not kill a mode.sh leg it had
  just started, so for ~6 min (22:47-22:53Z) two of my heavy.sh jobs ran at once (two slots, each MemoryMax=6G; no kill, no OOM).

VERIFY (one or two exemplars per family copied to verify/ and re-proved + re-run, same tree):
  F1_k1304_x_sub_aug.py                        pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION ZeroDivisionError division by zero
  F1b_c962_if_rebind.py                        pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION ZeroDivisionError division by zero
  F2_b313_dep_latin1_value.py                  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 2
  F2b_q701_utf7_hidden_rebind.py               pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION ZeroDivisionError division by zero
  F3_w103_helper_redefined_after_main.py       pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION ZeroDivisionError division by zero
  F3b_u900_value_redef_after_main.py           pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 2
  F4_b328_helper_module_getattr_raises.py      pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level KeyError: '__path__'
  F4b_q721_getattr_raises_attr_for_g.py        pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION module-level ImportError: cannot import name 'g' from 'h721' (/home/fabrice/git/pycsl/scratchpad/rt39/verify/h721.py)
  F5_x2000_list_isub.py                        pycsl --memory-model typed: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError unsupported operand type(s) for -=: 'list' and 'int'
  F5b_m1200_list_imul2.py                      pycsl --memory-model store: rc=0 Verification SUCCESS  CPython: VIOLATION contract 4
  F6_b3204_ellipsis_truthy.py                  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION ZeroDivisionError division by zero
  F6b_e3308_ellipsis_ifexp_ensures.py          pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 1
  F7_w3600_max_plus.py                         pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError unsupported operand type(s) for +: 'builtin_function_or_method' and 'int'
  F7b_b3201_notimplemented_truthiness.py       pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError NotImplemented should not be used in a boolean context
  F7c_o3401_ellipsis_lit_plus.py               pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError unsupported operand type(s) for +: 'ellipsis' and 'int'
  F7d_t4303_int_bit_length.py                  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION TypeError unsupported operand type(s) for +: 'builtin_function_or_method' and 'int'
  re-run: cd /home/fabrice/git/pycsl-rt39 && PYTHONHASHSEED=0 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py
          /home/fabrice/git/pycsl/scratchpad/rt39/verify/<probe> --import-path src/pycsl [<flags>]; CPython: cd verify && /home/fabrice/git/pycsl-rt39/.venv/bin/python3 -E -s <probe>

STATUS: 2026-10-29T23:40:03Z -- regenerated by mkfind.py (141 confirmed, 0 pending)
```

## REPAIR (executor o1, driver run #3, 2026-10-30, off main 8aaa864ca)

**Builtin objects are origins; refusal polarity is decided on the real object, not on spellings.** Inline in
`_run_pipeline` (`src/pycsl/pycsl.py`, route #325's block and the #445 attribute rule; the mirror twin of
`_run_pipeline` is `\trusted`, no new def in a mirrored file, no axiom, no new diagnostic code):

1. **A builtin name the file does not bind IS that builtin object** (a function, a type, a singleton -- never an
   int), so its `val constant` fallback is an R325 ORIGIN exactly like a module-level value's: bind / pass /
   return / discard / `=` `<>` against a different value only; `+ - * % < -x +=`, a contract term are refused.
   The set is `dir(builtins)` minus every name the file binds / imports (and nothing under `from m import *`);
   `__debug__` (a bool) is the one KNOWN int. `...` / `Ellipsis` (`pycsl_ellipsis`, previously exempt as an
   "internal encoding") is one too. MEASURED: the stronger polarity "EVERY 0-ary fallback is an origin" also
   refused corpus `0534` and `0546` (honest PASS files) whose free name is an emitter-internal pattern variable
   (`size_forest (f: forest)` of a `with` group; an or-pattern `| Some n | Wrapped n ->`) -- those stay non-origins.
2. **An UNCALLED attribute of an int value is not an int** unless it is one of the data attributes `real` /
   `imag` / `numerator` / `denominator` (the only non-callable attributes of `0` besides `__doc__`): the getter
   `get_<attr>` of any other attribute `hasattr(0, attr)` is an origin (`n.bit_length`, `n.__add__`,
   `n.conjugate`, `n.__class__`, `b.bit_length` on a bool), unless a class of this file defines that name.
3. The **bitwise / shift / power model operations** (`bit_and`, `bit_or`, `bit_xor`, `bit_lshift`, `bit_rshift`,
   `py_pow`) are int uses like `+` (`len & 1`, `NotImplemented ** 2` were opaque derivations).
4. The **truth value of `NotImplemented`** is refused (TypeError since CPython 3.14): Module 6 lowers every truth
   test to `(u <> 0)` (if / ternary / `not` / `and` / `or` / `bool(..)`), which W5 admits for other origins; and
   `any` / `all` of a list holding it. `notImplemented` left `_TYPES325` (it is not a type object), and that
   identity-only exemption no longer skips a VALUE binding (`x = int`).
5. **Identity stays faithful**: a builtin object is one fixed object, so the reflexive `x is ...` /
   `r is NotImplemented` W5 refuses for other origins (the NaN reason) is admitted for builtin objects.
6. **#445 on builtin receivers**: under a `no_exception` claim covering AttributeError, an attribute chain rooted
   at an unbound builtin name is walked on the REAL builtin object (`len.zz`, `int.zz`, `NotImplemented.zz` ->
   PYCSL-R445-ATTRIBUTE-NOT-DEFINED; `print.__doc__` admitted).

Witness verdicts on c186b936f: all 58 REFUSED (55 PYCSL-R325-OPAQUE-INT-FALLBACK, 3 route #445 a4000 / a4001 /
a4002). rt39 PASS controls g65/v3513, g69/p3905, g70/a4011, g73/t4308, g74/u4403 / u4404 / u4405 still PROVE.
Corpus witnesses 7496-7510 (PROVED at base, refused now); controls 7515-7522 (`x is ...`, `r is NotImplemented`,
`__debug__ + n`, int data attributes, `len(a) + 1`, `isinstance(n, int)`, `len(print.__doc__) + n`,
`n is NotImplemented`). Over-refusal (measured on c186b936f vs base 8aaa864ca): corpus root 0 MOVED, 1 GONE (`1039_route40_ellipsis_arithmetic`, an expected-FAIL witness: FAIL by proof at base, refused now); pyref 2186/2186 and mirror 53/53 byte-inert: 0 honest files refused. The red team's g62-g75 PASS controls: see the final report table.
Residuals (not measured as holes): a CALL of a method through a builtin type name (`str.upper(s)`, call stub
`str_upper_N`) is not tracked by R325 (receiver propagation is kept for module-level origins only, to bound the blast
radius; such calls are judged by #161 / #458 / why3 typing); an uncalled
method attribute of an int LOCAL read through a name a file class also defines is not an origin; unbound free
names that are not builtins (emitter-internal) stay non-origins (route #444 judges real NameErrors under claims).
