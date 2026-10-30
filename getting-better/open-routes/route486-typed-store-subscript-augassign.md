# OPEN ROUTE #486 — TYPED / STORE MEMORY MODELS: AN AUGMENTED ASSIGNMENT WHOSE TARGET IS A NON-INT VALUE REACHED THROUGH A SUBSCRIPT (A LIST / str / tuple / dict / set ELEMENT, A TUPLE SLOT) OR THROUGH A WALRUS / TERNARY ALIAS IS INT ARITHMETIC ON A HEAP CELL (ROUTE #478 RESIDUE)
**Status: REPAIRED (executor y3, driver run #3; see REPAIR below), Severity 1.** Red-team round 40 (2026-10-30, on dcf424f75 after #475-#480 repaired / #474 partial: 624 probes + 1009 mode re-proofs / 129 confirmed (probe, mode) pairs on 103 probes; rt39's 141 all closed). Census TSV `scratchpad/rt40/census.tsv`; the family block below is quoted from `scratchpad/rt40/FINDINGS.txt`.
Witnesses `witnesses-r486/` (14): `g107_e10701_str_elem_isub.py`, `g107_e10702_tuple_elem_isub.py`, `g107_e10703_dict_elem_isub.py`, `g107_e10708_set_elem_isub_int.py`, `g85_m8907_tuple_elem_imul.py`, `g85_m8908_nested_elem_isub.py`, `g85_m8923_walrus_alias_imul.py`, `g97_w9700_nested_isub_i.py`, `g97_w9701_nested_iand.py`, `g97_w9702_nested_ipow.py`, `g97_w9710_tuple_list_elem_isub.py`, `g97_w9714_nested_ior.py`, `g98_y9801_walrus_in_if_imul.py`, `g98_y9804_ternary_alias_imul.py`.

Driver repro: `scratchpad/rp40/repro.sh` (session scratchpad) on dcf424f75, 2026-10-30T07:30Z: all 16 rt40 verify exemplars (2+ per family, F5 under --memory-model typed / store) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F5 TYPED / STORE MEMORY MODELS: AN AUGMENTED ASSIGNMENT WHOSE TARGET IS A NON-INT VALUE REACHED THROUGH A SUBSCRIPT (A LIST / str / tuple / dict / set ELEMENT, A TUPLE SLOT) OR THROUGH A WALRUS / TERNARY ALIAS IS INT ARITHMETIC ON A HEAP CELL (ROUTE #478 RESIDUE) (28)
  WHAT: route #478 refuses `p op= ...` only when the TARGET is a bare formal parameter of a collection type; under `--memory-model typed` / `store` every list element is an `int_mem` cell, so `a[0] -= 1` on `a: List[List[int]]` / `List[str]` / `List[Tuple[int, int]]` / `List[Dict[int, int]]` / `List[Set[int]]`, `t[0] *= 2` / `t[0] -= 1` on `t: Tuple[List[int], int]`, and `(b := a); b *= 2` / `b = a if c else a; b *= 2` (a local alias of a list parameter) lower to integer arithmetic on the cell / the location
  EXEMPLAR: g85/m8908_nested_elem_isub.py (`#@ requires len(a) == 1`, `#@ no_exception \all`, `def f(a: List[List[int]]) -> int: a[0] -= 1; return 0`, --memory-model typed / store); g85/m8923_walrus_alias_imul.py (`(b := a); b *= 2; return len(a)` under `requires len(a) == 2`, `ensures \result == 2`, `assigns \nothing`)
  CPYTHON: m8908 / w9700-w9714: TypeError: unsupported operand type(s) for -= (&=, **=, |=): 'list' and 'int'; e10701 / e10702 / e10703 / e10708: TypeError for 'str' / 'tuple' / 'dict' / 'set' and 'int'; m8907: TypeError: 'tuple' object does not support item assignment; m8923 / y9801 / y9804: f([0, 0]) returns 4 -> VIOLATION contract
  WHY IT PROVES: pycsl.py:15867-15890 (route #478): the walk keys on `stmt == 'AugAssign'` with a `str` target that is a FORMAL PARAMETER (`_tg478 in _fp478`); an augmented store through a subscript is another statement kind (its target is not a str), and a local alias is not a parameter. Under typed / store the element of a `List[List[int]]` (or a tuple slot) is itself a `loc` in `int_mem`, so `a[0] -= 1` becomes `int_mem[a+0] := int_mem[a+0] - 1` (pointer arithmetic, type-correct because `type loc = int`, module6_whyml/preamble.py); route #279's alias refusal catches `b = a; b *= 2` (m8900) but not the walrus binder (m8923). In the default model the same files are refused or fail Why3 typing. The Load-position twins (`a[0] + 1`, `a[0] < 1`, `10 // a[0]`, `a[0] = a[0] - 1` on the same element types, g108) ARE refused by route #458 (the operand-class judgement, pycsl.py:11447-11570, derives `str` / `list` for a LOADED `a[0]`) or fail Why3 typing; the augmented element store is not judged there. Emitted for m8908 (emit/m8908_nested_elem_isub.mlw): `let f (a: loc) (a_len: int) ... int_mem := Map.set !int_mem (a + 0) ((Map.get !int_mem (a + 0)) - 1)`.
  PROPOSED SYSTEMATIC REPAIR: TYPE-KEYED ON THE TARGET EXPRESSION, NOT ON THE PARAMETER LIST: judge every augmented store (name, subscript, attribute target) by the SOURCE TYPE of the target expression (`a[0]` of `List[List[int]]` is a list, a tuple slot is not assignable at all) and admit only int / float / bool / str / bytes targets of a MUTABLE container (refuse any item store into a tuple / str / bytes); extend route #279's alias refusal to every binder (walrus, unpacking, for, with) or, better, make `loc` abstract in the typed / store preambles so no arithmetic applies to a location (route #478 measured this is load-bearing for `Map.get !int_mem (a + i)`: introduce `loc_offset : loc -> int -> loc` instead). Witness: the F5 (probe, model) pairs; control: `a[0][0] -= 1` on `List[List[int]]` (an int element) keeps proving.
  PROBES: g107@typed/e10701_str_elem_isub.py g107@store/e10701_str_elem_isub.py g107@typed/e10702_tuple_elem_isub.py g107@store/e10702_tuple_elem_isub.py g107@typed/e10703_dict_elem_isub.py g107@store/e10703_dict_elem_isub.py g107@typed/e10708_set_elem_isub_int.py g107@store/e10708_set_elem_isub_int.py g85@typed/m8907_tuple_elem_imul.py g85@store/m8907_tuple_elem_imul.py g85@typed/m8908_nested_elem_isub.py g85@store/m8908_nested_elem_isub.py g85@typed/m8923_walrus_alias_imul.py g85@store/m8923_walrus_alias_imul.py g97@typed/w9700_nested_isub_i.py g97@store/w9700_nested_isub_i.py g97@typed/w9701_nested_iand.py g97@store/w9701_nested_iand.py g97@typed/w9702_nested_ipow.py g97@store/w9702_nested_ipow.py g97@typed/w9710_tuple_list_elem_isub.py g97@store/w9710_tuple_list_elem_isub.py g97@typed/w9714_nested_ior.py g97@store/w9714_nested_ior.py g98@typed/y9801_walrus_in_if_imul.py g98@store/y9801_walrus_in_if_imul.py g98@typed/y9804_ternary_alias_imul.py g98@store/y9804_ternary_alias_imul.py
```

## REPAIR (executor y3, driver run #3, 2026-10-30, off main 0c61bfc3f)

**Every augmented assignment is judged by the static type of its TARGET expression.** Inline in `_run_pipeline`
(`src/pycsl/pycsl.py`, right after route #478's parameter check; mirror twin `\trusted`, no new def / lambda, no axiom;
new code PYCSL-R486-NONSCALAR-AUGASSIGN-TARGET). On the Python AST of every verified function (IR functions not
`\trusted` / `\abstract`) a def-free judgement types the target: parameter annotations; each local's bindings
(assignment, tuple unpacking, annotated, walrus, `for` element, `with` / `except` targets) joined to a 4-round fixpoint;
displays, arithmetic, ternary, `and` / `or`; container element types (`List[E]` / `Sequence[E]` / `Dict[K, V]` /
tuple slots / str items); user-function return annotations; class field annotations. Decision:
- a scalar target (int / float / bool / complex) is admitted; a str / bytes target only for `+=` / `*=` / `%=` and,
  under typed / store, only as a NAME (a str element / field is an int cell there);
- `--memory-model typed` / `store` (`loc = int`): EVERY other target -- known non-scalar OR of unknown type -- is REFUSED
  (allow-list);
- hoare-family models: a list / dict / record value is not a Why3 `int`, so integer arithmetic on it fails Why3 typing
  (fail closed, re-measured on every witness); there only what CPython itself rejects on the known type is refused --
  an item store into a tuple / str / set, an operator the type lacks (`list -= ..`, `dict += ..`, `str -= ..`); a type's
  own in-place operators (`list +=` / `*=`, `dict |=`, set `|= &= -= ^=`) stay with the emitter.
A bare formal-parameter target stays #478's.

Witnesses x {default, typed, store} (42 runs): typed 14/14 and store 14/14 REFUSED (all 28 PROVED at base); default
10 REFUSED + 4 NOT-PROVED (Why3 type error: e10708 set `-=`, m8923 / y9801 / y9804 alias `*=`) -- 0 PROVED. Corpus
7600-7610 (expected FAIL; 7610 = the default-model refusal), controls 7612-7616 (int element / nested int element /
local list element / str local; PASS at base and now). Advice ("a local with a scalar annotation `x: int = len(a); x *=
2`, or an int element through the element store `a[i] = a[i] - 1`") followed: both VERIFY under default, typed, store.
RESIDUAL (named): the hoare-family judgement leaves unknown-type targets to Why3 typing rather than refusing them.

OVER-REFUSAL / INERTNESS (measured on HEAD d92f4c97d vs base 0c61bfc3f, one battery for #485-#487): byte-diff root
2673 base / 2684 candidate .mlw, 0 MOVED, 0 GONE, 1 APPEARED (1723, an expected-PASS `--verify-imports` control whose
emission is load/timeout-dependent: re-emitted in one job at base AND candidate, identical `.mlw`, identical to the
sweep's -- not a repair effect), 10 new = this route set's controls; pyref 2186 / 2186, 0 MOVED / GONE / APPEARED;
mirror 53 / 53 byte-inert (an earlier candidate moved 4 mirror files -- nested `and` / `or` in truth positions -- and was
fixed to select a nested marked operand raw before the gate). So 0 previously-proved corpus / pyref / mirror files are
refused. Red-team rt40 PASS controls (e8761, s8839, b9032, t9314, w9715): 5/5 PROVED at base and at the repair.
