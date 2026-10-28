# OPEN ROUTE #440 — ROUTE #161's METHOD ARM ADMITS A METHOD CALL BY ITS NAME, NOT BY (RECEIVER CLASS, METHOD)
**Status: REPAIRED (executor h440, driver run #3, 2026-10-28; routes #440 and #441 by ONE signature table), Severity 1.** Red-team round 35 (2026-10-28, SYSTEMATIC BUILTIN-PRECONDITION CENSUS after #432-#439 on daaf6ea78: 860 probes / 452 fully proved / 175 confirmed (156 new + 19 inside #432's documented residual); rt34's 63 all closed). Census TSV `scratchpad/rt35/census.tsv`; findings `scratchpad/rt35/FINDINGS.txt` (the family text below is quoted from it).
Witnesses `witnesses-r440/` (43): `n002_str_rindex.py`, `n006_str_partition_empty.py`, `n007_str_rpartition_empty.py`, `n010_center_fill.py`, `n013_int_to_bytes.py`, `n026_str_rsplit_empty.py`, `n031_int_from_bytes_type.py`, `n032_bytes_fromhex.py`, `n035_str_maketrans.py`, `r001_mod_partition.py`, `r002_mod_format.py`, `r004_mod_fromhex.py`, `r021_format_map.py`, `r023_bytes_partition.py`, `r030_rpartition_bytes.py`, `r031_str_rindex_param.py`, `r032_str_rindex_ensures.py`, `r033_int_to_bytes_neg.py`, `r036_from_bytes_order.py`, `x001_realistic_rindex.py`, `x002_realistic_to_bytes.py`, `s102_s_bit_length.py`, `s104_xs_upper.py`, `s106_n_upper.py`, `s107_n_keys.py`, `s108_x_bit_length.py`, `s112_xs_split.py`, `s113_d_strip.py`, `s120_st_keys.py`, `s121_s_items.py`, `s122_xs_lower.py`, `s127_n_copy.py`, `s132_s_values.py`, `s109_xs_get_1.py`, `s110_st_get_1.py`, `s114_n_join_xs.py`, `s115_xs_find_1.py`, `s116_d_count_1.py`, `s118_n_count_1.py`, `s123_n_startswith_a.py`, `s124_d_replace_a_b.py`, `s126_s_union_s.py`, `s129_xs_issubset_xs.py`.

Driver repro: 7/7 family exemplars (A1 n002, A2 s106, B1 k001 + e017, B2 a001, C c007, D b000) rc=0 Verification SUCCESS on main f1c249c4e at 2026-10-28T19:25Z, each violating under CPython (scratchpad/rt35/driver-repro.txt).

```
#440 ROUTE #161's METHOD ARM ADMITS A METHOD CALL BY ITS NAME, NOT BY (RECEIVER CLASS, METHOD)   (43)
  Mechanism: functions.py:1269-1275 admits `R.m(..)` when m is in _R161_METHODS OR when ANY function / method of the
  file has the same tail name (_tails161), whatever R's class; the call lowers to an opaque `val` with no raises.
  A1 NAME COLLISION (21): x001  class Buffer: def rindex(..); `path.rindex(".")` PROVED; CPython ValueError.
  A2 RECEIVER CLASS LACKS THE METHOD (22): s106  `n: int`; `len(n.upper())` PROVED; CPython AttributeError.
  REPAIR (proposed, allow-list / refuse by default): an allow-list of PAIRS: admit `R.m(..)` only for (class(R), m) in a table {str: {..}, list: {..}, dict: {..}, set: {..},
  int: {bit_length}} with class(R) DERIVED as exactly that builtin, or m a method the file DEFINES on class(R) itself; a
  name collision never admits a builtin method; everything else refused under no_exception.
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
6695 an unclaimed function (the table is not consulted).

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
