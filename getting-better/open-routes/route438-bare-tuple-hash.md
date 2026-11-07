# OPEN ROUTE #438 — HASHING A BARE / UNPARAMETERISED tuple (ELEMENTS UNKNOWN) OWES NO TypeError
**Status: REPAIRED (executor g6, driver run #3), Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r438/` (11): `u1_ret_tuple_bare.py`, `w00_hash_bare_tuple.py`, `w04_ifexp_bare_tuple.py`, `w05_tuple_in_tuple.py`, `w06_walrus_bare_tuple.py`, `w07_typing_Tuple_ret.py`, `w11_method_bare_tuple.py`, `y00_param_bare_tuple.py`, `y01_param_typing_Tuple.py`, `y13_ret_bare_tuple_local.py`, `y14_field_bare_tuple.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#438 HASHING A BARE / UNPARAMETERISED tuple (ELEMENTS UNKNOWN) OWES NO TypeError   (11)
  w00  t: tuple; hash(t) PROVED; f(([1],))                                                     CPython TypeError
  y00 / y01 {t} for a parameter `tuple` / `typing.Tuple`   u1 / y13 / w07 a callee returning `-> tuple`   w04 IfExp
  w05 a tuple inside a tuple   w06 walrus   w11 method return   y14 a field annotated `tuple`
  REPAIR (proposed, allow-list / refuse by default): The hash allow-list (rh1 / #407) admits a tuple only with every component class admitted; `tuple`, `Tuple`, `tuple[Any, ...]`
  and `Tuple[()]`-less spellings have UNKNOWN components and are #UNK: refused in a hashing position under `no_exception`.
```

## REPAIR (executor g6, driver run #3, 2026-10-28, off 1c083dcbe; annotations §7.139, translational §T.6.150)

Allow-list polarity on the R-gate side. In the #349-#383 hashing pass of `_run_pipeline` (src/pycsl/pycsl.py, `\trusted`
in the mirror), the `#UNKT` marker (an un-parameterised `tuple` / `Tuple` that is not a file class, at any depth of an
annotation, components included) now counts as UNDERIVABLE in route R-gate's leaf test and in its hashed-iterable test:
a hashed leaf holding it is REFUSED in a function claiming TypeError (`PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM`), and
the function joins the #430 set, so a `\all` caller of an un-claimed holder is refused (`PYCSL-R430-CALLEE-UNDERIVABLE-HASH`).
Admitted set: a parameterised tuple whose components are all admitted classes; any tuple hashed in an un-claimed
function (its TypeError is ambient and ends the function abnormally, §7.131 / route #431). Why not `#UNK` (refused
everywhere, the expected direction): §7.47 measured that it refuses the self-annotation mirror `pycsl.py`
(`_merge_records_best_of_n` keyed by `_record_key(..) -> Tuple` of why3 JSON values) in an UN-claimed function, where no
false proof exists; the claim-gated rule closes every witness at zero mirror cost. The R-gate message now names the new
source and its advice adds `Tuple[int, str]` (re-audited: advice probes a438_typed_tuple / a438_drop_claim VERIFY).

Witnesses 6600-6613 (the 11 red-team probes 6600-6610, NEW latents 6611 `Tuple[int, tuple]` component and 6613 the #430
channel, PROVED at base; NEW probe 6612 `set(xs)` over `List[tuple]`, FAIL at base on another goal) are all REFUSED;
control 6640 (parameterised tuples under `\all`, a bare tuple hashed un-claimed) PROVED at base and candidate.
Gates and cost: see route439's REPAIR (one landing) and getting-better/systematic-soundness-r3/g6-r438-439/SUMMARY.txt.

## RESIDUALS (honest)

A bare tuple hashed in an un-claimed function stays admitted by design (ambient TypeError). `Tuple[()]` / `tuple[()]`
(the empty-tuple spelling) is read through the generic component walk, not special-cased.
