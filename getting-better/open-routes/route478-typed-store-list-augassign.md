# OPEN ROUTE #478 — TYPED / STORE MEMORY MODELS -- AN AUGMENTED ASSIGNMENT ON A LIST PARAMETER IS ARITHMETIC ON ITS HEAP LOCATION
**Status: REPAIRED (driver run #3, executor m2, 2026-10-30), Severity 1.** Red-team round 39 (2026-10-29, on d6abee90b after #463-#473: 918 probes + 1064 mode re-proofs / 141 confirmed (probe, mode) pairs; rt38's 142 counted all closed). Census TSV `scratchpad/rt39/census.tsv`; the family block below is quoted from `scratchpad/rt39/FINDINGS.txt`.
Witnesses `witnesses-r478/` (15): `mm_g4_a403_imul.py`, `g45_m1200_list_imul2.py`, `g45_m1201_list_imul0.py`, `g45_m1202_list_imul_param.py`, `g48b_o1715_list_isub.py`, `g48b_o1717_list_imul_neg_len.py`, `g48b_o1722_list_return_imul_len_ensures.py`, `g52_x2000_list_isub.py`, `g52_x2002_list_iand.py`, `g52_x2003_list_ior_int.py`, `g52_x2004_list_ixor.py`, `g52_x2005_list_ilshift.py`, `g52_x2006_list_irshift.py`, `g52_x2007_list_ipow.py`, `g52_x2303_list_of_lists_isub.py`.

Driver repro: `scratchpad/rp39/repro.sh` (session scratchpad) on d6abee90b, 2026-10-29T23:41Z: all 16 rt39 verify exemplars (2+ per family) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F5 TYPED / STORE MEMORY MODELS -- AN AUGMENTED ASSIGNMENT ON A LIST PARAMETER IS ARITHMETIC ON ITS HEAP LOCATION (30)
  WHAT: under --memory-model typed|store a list parameter is a `loc` plus an immutable `<a>_len`, route #49's in-place-augassign refusal is keyed on the hoare model's array-local sets, so `a *= k` / `a -= 1` / `a &= 1` ... lower to `a := !a * k` (pointer arithmetic: CPython raises TypeError or resizes the list) and `len(a)` keeps the entry length
  EXEMPLAR: g52/x2000_list_isub.py (`#@ no_exception \all` / `#@ assigns \nothing`, `def f(a: List[int]) -> int: a -= 1; return 0`, proved with `--memory-model typed` and with `--memory-model store`); g45/m1200_list_imul2.py (`#@ requires len(a) == 2`, `#@ ensures \result == 2`, `#@ assigns \nothing`, `a *= 2; return len(a)`)
  CPYTHON: x2000: TypeError: unsupported operand type(s) for -=: 'list' and 'int' (same for &= |= ^= <<= >>= **= and a List[List[int]] parameter); m1200: f([0, 0]) returns 4 (also a *= 0 -> 0, a *= n, a *= 2 in a loop, a *= -1; a403 of rt38's g4 set). Under the default hoare model the same files are REFUSED (route #49, #447, #458) or fail Why3 typing.
  WHY IT PROVES: module6_whyml/statements.py:3236-3249: route #49's PYCSL-WHYML-PARAM-LIST-AUGASSIGN refusal is keyed on the HOARE model's sets (`target in _seq_locals or target in _array_locals`); under typed / store a list parameter is a heap location `a: loc` plus an immutable `a_len` (`let f (a: loc) (a_len: int)`, and module6_whyml/preamble.py:3328 declares `type loc = int`), is in neither set, and the augmented assignment falls through to the INT lowering (statements.py:3250ff): `a := !a * 2`, `a := !a - 1` -- pointer arithmetic on the location, which type-checks because `loc` is an int; `len(a)` reads the untouched `a_len`, and `assigns \nothing` holds (`!int_mem = old !int_mem`).
  PROPOSED SYSTEMATIC REPAIR: TYPE-KEYED, MODEL-INDEPENDENT REFUSAL: decide the AugAssign lowering on the TARGET's SOURCE TYPE (an annotated / inferred list, dict, set, bytearray, str or object), never on a memory-model-specific local table: under every model an augmented assignment whose target is not an int / float / bool is either the modelled in-place collection update (`+=` / `*=` on a list, `|=` / `-=` ... on a set / dict, with the length havocked and a `writes` frame) or REFUSED; and make `loc` an abstract type in the typed / store preambles (not an `int` alias) so no arithmetic operator can ever apply to a location. Witness: the 28 F5 (probe, model) pairs; control: `n -= 1` on an int parameter under typed.
  PROBES: mm/g4@typed/a403_imul.py mm/g4@store/a403_imul.py g45@typed/m1200_list_imul2.py g45@typed/m1201_list_imul0.py g45@typed/m1202_list_imul_param.py g45@store/m1200_list_imul2.py g45@store/m1201_list_imul0.py g45@store/m1202_list_imul_param.py g48b@typed/o1715_list_isub.py g48b@typed/o1717_list_imul_neg_len.py g48b@typed/o1722_list_return_imul_len_ensures.py g48b@store/o1715_list_isub.py g48b@store/o1717_list_imul_neg_len.py g48b@store/o1722_list_return_imul_len_ensures.py g52@typed/x2000_list_isub.py g52@typed/x2002_list_iand.py g52@typed/x2003_list_ior_int.py g52@typed/x2004_list_ixor.py g52@typed/x2005_list_ilshift.py g52@typed/x2006_list_irshift.py g52@typed/x2007_list_ipow.py g52@typed/x2303_list_of_lists_isub.py g52@store/x2000_list_isub.py g52@store/x2002_list_iand.py g52@store/x2003_list_ior_int.py g52@store/x2004_list_ixor.py g52@store/x2005_list_ilshift.py g52@store/x2006_list_irshift.py g52@store/x2007_list_ipow.py g52@store/x2303_list_of_lists_isub.py
```

## Repair (driver run #3, m2)

TYPE-KEYED, MODEL-INDEPENDENT ALLOW-LIST, judged once on the IR after emission in `_run_pipeline`
(`src/pycsl/pycsl.py`, block `ROUTE #478`; the mirror twin `_run_pipeline` is `\trusted`, no mirror
body moves): an augmented assignment whose target is a formal parameter of a verified function (not
`\trusted` / `\abstract`) is admitted only when the parameter's DECLARED type (`symbol_table`) is an
immutable scalar -- `int`, `float`, `bool`, `complex`, `str`, `bytes`, a tuple, or unannotated
(`Any`); any other type (`list`, `List[..]`, `List[List[..]]`, `Dict`, `Set`, `bytearray`, a class)
is REFUSED under EVERY memory model (`PYCSL-R478-COLLECTION-PARAM-AUGASSIGN`). It runs after
emission so route #49's own default-model message keeps answering first where it fires.
Witnesses: all 15 in `witnesses-r478/` x {default, typed, store} REFUSED (45/45; at base: default
refused / Why3-type-error, typed + store PROVED); also rt39 `x2300_list_isub_then_len`, driver probes
`a: list` (bare), `Dict` / `Set` / `bytearray` parameters (typed / store) REFUSED. Corpus witnesses
`7530`-`7537`; controls `7538` / `7539` (`n -= 1` on an int parameter, typed / store) and `7546`
(element store `a[0] = 5` beside `k *= 2`, typed) PROVE at base and now. Over-refusal: corpus /
mirror / stdlib census of every augmented assignment on a parameter: 0 non-scalar targets outside
route #49's witness `1083` (refused first by #49); rt39's one honest PROVED probe of the family,
`g52/x2010_list_imul_neg` (`a *= -1`, `return 0`, typed / store), is now refused (its lowering was
arithmetic on the location; the true result was a coincidence). NOT done: making `loc` an abstract
type in the typed / store preambles -- the typed element access itself is `Map.get !int_mem (a + i)`,
so `loc` arithmetic is load-bearing there.
Model-gated census (the brief's second question): every REFUSAL-class witness of
`bin/refusal-witness-census.tsv` (2014) emitted under `--memory-model typed` and `store`
(`--no-proof`): 1927 refused in all three models, 12 refused under default but emitting under typed /
store; proving those 12 under typed / store: 11 NOT PROVED (Why3 errors), 1 PROVED -- `0849`
(route #289's opaque-element store gate keys on the `subscript_set` emission, and under typed /
store `a[i][k] = v` on `List[Dict[int, int]]` lowers to a heap store `int_mem[a[i] + k]` instead):
see the run #3 README entry for its disposition.
