# OPEN ROUTE #440 — ROUTE #161's METHOD ARM ADMITS A METHOD CALL BY ITS NAME, NOT BY (RECEIVER CLASS, METHOD)
**Status: OPEN, Severity 1.** Red-team round 35 (2026-10-28, SYSTEMATIC BUILTIN-PRECONDITION CENSUS after #432-#439 on daaf6ea78: 860 probes / 452 fully proved / 175 confirmed (156 new + 19 inside #432's documented residual); rt34's 63 all closed). Census TSV `scratchpad/rt35/census.tsv`; findings `scratchpad/rt35/FINDINGS.txt` (the family text below is quoted from it).
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
