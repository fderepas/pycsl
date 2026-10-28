# OPEN ROUTE #441 — BUILTIN CALL SIGNATURES ARE NOT CHECKED: ARITY AND ARGUMENT TYPES
**Status: REPAIRED (executor h440, driver run #3, 2026-10-28; routes #440 and #441 by ONE signature table), Severity 1.** Red-team round 35 (2026-10-28, SYSTEMATIC BUILTIN-PRECONDITION CENSUS after #432-#439 on daaf6ea78: 860 probes / 452 fully proved / 175 confirmed (156 new + 19 inside #432's documented residual); rt34's 63 all closed). Census TSV `scratchpad/rt35/census.tsv`; findings `scratchpad/rt35/FINDINGS.txt` (the family text below is quoted from it).
Witnesses `witnesses-r441/` (107): `k001_int_base_int.py`, `e001_int_base_param.py`, `e002_int_base_bool.py`, `e003_int_base_expr.py`, `e004_int_base_len.py`, `e005_int_base_lit.py`, `e006_int_base0.py`, `e008_int_base_ensures.py`, `e009_int_base_bad.py`, `e010_int_base_ord.py`, `e017_len_two.py`, `e018_abs_two.py`, `e021_round_three.py`, `e022_hash_two.py`, `e023_int_three.py`, `e024_pow_four.py`, `e026_len_zero.py`, `e028_bit_length_arg.py`, `e033_get_three.py`, `e034_keys_arg.py`, `e035_find_four.py`, `e048_bytes_two.py`, `e053_tuple_int.py`, `e058_sum_int.py`, `e061_enumerate_int.py`, `e063_len_int.py`, `e064_iter_int.py`, `e069_round_str.py`, `e070_pow_str.py`, `e079_bit_length_float.py`, `k094_isinstance_bad_b.py`, `e016_bool_two_args_b.py`, `e031_startswith_none_b.py`, `s000_repr_n_n.py`, `s001_id_n_n.py`, `s008_range.py`, `s009_range_1_2_3_4.py`, `s012_bytearray_n_n.py`, `s015_abs.py`, `s016_hash.py`, `s018_round.py`, `s019_pow_n.py`, `s021_sorted.py`, `s022_sum.py`, `s023_max.py`, `s024_bool_n_n.py`, `s026_int_n_n_n.py`, `s031_s_isdigit_1.py`, `s032_s_isalpha_1.py`, `s033_s_isspace_1.py`, `s034_s_isalnum_1.py`, `s035_xs_copy_1.py`, `s038_d_values_1.py`, `s039_d_items_1.py`, `s042_st_issubset.py`, `s043_xs_count.py`, `s044_s_endswith.py`, `s045_s_rfind.py`, `s049_n_bit_length_1_2.py`, `s050_s_count.py`, `s051_s_find.py`, `s052_s_split_1_1.py`, `s053_st_union_1.py`, `s054_st_intersection_n.py`, `s055_st_difference_n.py`, `s056_st_issuperset_n.py`, `s059_d_get.py`, `s060_d_keys_1_2.py`, `s061_len_n_1.py`, `s062_len_true.py`, `s065_sum_s.py`, `s076_len_n.py`, `s096_isinstance_n_n.py`, `s097_isinstance_n_s.py`, `x006_int_base_realistic.py`, `x007_len_int_realistic.py`, `m007_strip_int.py`, `m011_find_bytes_in_str.py`, `a001_str_strip_int.py`, `a002_str_strip_Union_str_int.py`, `a005_str_strip_bool.py`, `a006_str_strip_List_str.py`, `a008_str_lstrip_int.py`, `a009_str_lstrip_Union_str_int.py`, `a012_str_lstrip_bool.py`, `a013_str_lstrip_List_str.py`, `a015_str_rstrip_int.py`, `a016_str_rstrip_Union_str_int.py`, `a019_str_rstrip_bool.py`, `a020_str_rstrip_List_str.py`, `a021_str_find_bytes.py`, `a022_str_find_int.py`, `a026_str_find_bool.py`, `a029_str_rfind_bytes.py`, `a030_str_rfind_int.py`, `a034_str_rfind_bool.py`, `a037_str_count_bytes.py`, `a038_str_count_int.py`, `a042_str_count_bool.py`, `a046_str_startswith_int.py`, `a050_str_startswith_bool.py`, `a054_str_endswith_int.py`, `a058_str_endswith_bool.py`, `a202_str_find_start_bytes.py`, `a203_str_startswith_tuple_bytes.py`, `x008_strip_int_realistic.py`, `x009_find_bytes_realistic.py`.

Driver repro: 7/7 family exemplars (A1 n002, A2 s106, B1 k001 + e017, B2 a001, C c007, D b000) rc=0 Verification SUCCESS on main f1c249c4e at 2026-10-28T19:25Z, each violating under CPython (scratchpad/rt35/driver-repro.txt).

```
#441 BUILTIN CALL SIGNATURES ARE NOT CHECKED: ARITY AND ARGUMENT TYPES   (107)
  B1 (76): e063 `len(n)` n: int; e017 `len(s, s)`; e026 `len()`; s021 `sorted()`; s022 `sum()`; s016 `hash()`;
     k001 `int(n, 10)` n: int -- all PROVED; CPython TypeError.
  B2 (31): m007 `s.strip(t)` t: Union[str, int]; a021 `s.find(t)` t: bytes -- PROVED; CPython TypeError (the str argument
     is hashed to an int before the opaque val, so any int-typed term fits).
  REPAIR (proposed, allow-list / refuse by default): a per-builtin SIGNATURE TABLE (positional arity range, accepted keywords, accepted static class per argument position)
  checked where route #161 admits the call; any call outside its row refused under no_exception (TypeError).
```

## REPAIR (executor h440, driver run #3, 2026-10-28, off fa7cbb1aa; annotations §7.141, translational §T.6.152) -- routes #440 AND #441 by ONE table

Code inline in `_run_pipeline` (src/pycsl/pycsl.py), right after #432 / #433 / #437 in each function, over the class
derivation of the hashing pass (`_ty383` / `_ei383`, with #432's guard narrowing recorded in `_nr440`); no new def in a
mirrored file (`_run_pipeline` is `\trusted` in the mirror), no axiom, no emission change. ONE SIGNATURE TABLE, allow-list
polarity, refuse by default, consulted in every function that is not `\trusted` / `\abstract` and claims `no_exception`:
  `_FT440` -- 36 rows keyed by builtin name (exactly route #161's `_R161_FUNCS`): len abs bool str repr sorted reversed list
    tuple set frozenset dict enumerate zip range min max sum any all isinstance chr ord int float print hash id type iter
    map filter round bytearray bytes pow.
  `_MT440` -- 100 rows keyed by (receiver class, method), #161's 39 method names on the builtin classes that HAVE them:
    str / bytes / bytearray x {strip lstrip rstrip lower upper isdigit isalpha isalnum isspace startswith endswith find
    rfind count replace join split} (51), bytearray {copy clear reverse} (3), int / bool {bit_length} (2), list / deque
    {append extend count copy clear reverse} (12), list {insert sort} (2), tuple / Sequence {count} (2), dict / Mapping
    {get keys values items} (8), dict {copy clear setdefault update} (4), set / frozenset {union intersection difference
    issubset issuperset copy} (12), set {add discard clear update} (4) -- 136 rows in all.
  Each row = (min positional, max positional or unbounded, keyword -> class code, class code per position, the obligation
  rows that still speak for its value-dependent exceptions: #66 / #163, #72 / #436, #160 / #259, #281, #349 / #438 /
  #439, #433, #434, #437). Class codes: number, int, int-or-None, str, str-or-None, str-or-tuple-of-str, bytes-like (+
  None / tuple / int variants), iterable, sized, reversible, mapping-or-iterable-of-pairs, iterable-of-numbers,
  int-or-bytes-or-iterable-of-int, class-or-tuple-of-classes, callable, any.
ADMITTED: `f(..)` (an unshadowed builtin) iff it matches f's row with every constrained argument DERIVED and accepted (a call
the table admitted contributes its row's result class); `R.m(..)` iff EVERY class R may have here (minus None, #432's) is a
file class whose file MRO defines m (method / class-body binding / field) -- or whose non-file builtin base has a row for m
the call matches -- or a builtin class with a row (class, m) the call matches; `str.m(s, ..)` is str's row with s derived
exactly str. A file name collision never admits a builtin method: an underivable receiver is refused for a name ONLY the
file defines, and a module function `m.f(..)` beside a file `f` is refused unless the program defines `m.f`. REFUSED:
`PYCSL-R440-METHOD-NOT-ADMITTED` (AttributeError claim: the class lacks m; ANY claim: a builtin method without a row --
rindex index partition rpartition rsplit format format_map to_bytes from_bytes fromhex maketrans center ... -- or a file
class whose non-file base has no row), `PYCSL-R441-BUILTIN-SIGNATURE` (TypeError claim: arity, keyword, `*` / `**`, an
argument class outside the row). Derivation precision added for it: `seq * n` is the sequence; `R.m()`'s result is that of
R's non-None classes; an `assert` message is not checked (route #332).

WITNESSES (corpus, expected FAIL): 6650-6659, 6661-6678 (28 red-team witnesses, re-proved at base fa7cbb1aa: all PROVED),
6660 (a file class without `upper`), 6679 (`x: Any; x.rindex(..)` beside a file `rindex`), 6680 (`rindex` collision under
`no_exception ValueError` only), 6682 (`math.factorial(n)` beside a file `factorial` -- an A1 form THROUGH A MODULE
RECEIVER, found while repairing: PROVED at base) -- all PROVED at base; 6681 (`str.strip(n)`, n: int) was already refused
at base by #435 and pins the table's unbound arm. All 33 REFUSED at the candidate by R440 / R441. All 150 route witnesses
(witnesses-r440/ 43, witnesses-r441/ 107) are refused by R440 / R441 at the candidate (--no-proof screen). CONTROLS
(expected PASS, PROVED at base and candidate): 6690 str rows, 6691 builtin rows, 6692 container / int rows, 6693 a file
method on its own class's receiver, 6694 isinstance-narrowed Union receiver and a method result on a narrowed Optional,
6695 an unclaimed function calling `path.rindex("")` (the table is not consulted; the argument never raises, so check-corpus-contract-truth-args and check-vacuous-drivers stay green -- a first `rindex(".")` / `ensures \result == 1` shape turned both RED and was reshaped).

COST (measured, --no-proof screens and the byte-diff sweeps vs v10/ca + v10/ma = c53b5e381 emission): of the 366 corpus
files that carry a `no_exception` claim AND emit at base, 0 expected-PASS files are refused; 4 expected-FAIL files that
already failed to verify (VERIFY-FAIL) are now refused earlier: 4614 / 4622 (`range` row: a file class / `Any` argument,
#343's witnesses), 4826 (`str.startswith` row: an `Any` argument, #358's witness), 6576 (`rsplit` has no row, #436's
collision witness) -- verdict FAIL kept. python-reference 2186/2186, mirror 53/53 byte-inert (none of them, nor
pycsl_lib, carries a `no_exception` claim). Per-row cost: range 2, str.startswith 1, (str, rsplit) no-row 1; every other
row 0.

RESIDUALS (complement forms still admitted, honestly): (1) an underivable / `Any` / `object` receiver calling a method name
that has a builtin row (#443's domain, not judged here); (2) `super().m(..)` and module functions without a file name
collision stay #161's (full name); (3) positions coded "any" (print / str / repr / hash / id / type / bool arguments,
`append(x)`, `get(k)`, `dict(**kw)` values) accept every class -- their exceptions are the hashing / #281 rows or a user
class's own contract; (4) the callable code admits any attribute (`map(o.f, xs)`) and any imported name; the class-spec
code admits any imported name (`isinstance(x, imported_function)`); (5) a TypeError-only claim does not get #432's
narrowing (only an AttributeError claim runs it), so a Union receiver narrowed by isinstance can be over-refused there
(measured 0); (6) element-level checks only for sum (numbers), bytes / bytearray (ints), dict / update (pairs) and
startswith / endswith (tuple components); other element classes are the hashing / #433 / #437 rows' business.
