# OPEN ROUTE #495 — ROUTE #489 CALLS A DUNDER PURE WHEN THE TEXT `assigns \nothing` OCCURS ANYWHERE IN ITS #@ LINES, WHILE THE VERIFIER PROVES THE DUNDER AGAINST THE UNION OF ITS `assigns` CLAUSES: `#@ assigns \nothing` + `#@ assigns self.v` (CONTIGUOUS, EITHER ORDER, OR SEPARATED BY BLANK LINES) IS A WRITING DUNDER JUDGED PURE (#489 COMPLEMENT)
**Status: OPEN, Severity 1.** Red-team round 42 (2026-10-31, on 77a3818d0 = main + #489 / #490: 818 probes + 715 mode re-proofs / 139 confirmed (probe, mode) pairs on 113 probes; rt41's 237 all closed). Census TSV `scratchpad/rt42/census.tsv`; the family block below is quoted from `scratchpad/rt42/FINDINGS.txt`.
Witnesses `witnesses-r495/` (13): `g311_s3200_t_pure_text_orphan_nothing_above.py`, `g312_w3100_orphan_blank_len.py`, `g312_w3101_orphan_blank_eq.py`, `g312_w3102_orphan_blank_add.py`, `g312_w3110_orphan_two_blanks_len.py`, `g312_w3111_orphan_two_blanks_eq.py`, `g312_w3112_orphan_two_blanks_add.py`, `g312_w3140_two_assigns_contig_len.py`, `g312_w3141_two_assigns_contig_eq.py`, `g312_w3142_two_assigns_contig_add.py`, `g312_w3150_two_assigns_rev_len.py`, `g312_w3151_two_assigns_rev_eq.py`, `g312_w3152_two_assigns_rev_add.py`.

Driver repro: `scratchpad/rp42/repro.sh` (session scratchpad) on ddd542f97, 2026-10-31T03:05Z: all 20 rt42 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F5 ROUTE #489 CALLS A DUNDER PURE WHEN THE TEXT `assigns \nothing` OCCURS ANYWHERE IN ITS #@ LINES, WHILE THE VERIFIER PROVES THE DUNDER AGAINST THE UNION OF ITS `assigns` CLAUSES: `#@ assigns \nothing` + `#@ assigns self.v` (CONTIGUOUS, EITHER ORDER, OR SEPARATED BY BLANK LINES) IS A WRITING DUNDER JUDGED PURE (#489 COMPLEMENT) (39)
  WHAT: a VERIFIED program dunder carries two frame clauses, `#@ assigns \nothing` and `#@ assigns self.v` (contiguous in either order, or the `\nothing` line one or two blank lines above); the verifier attaches both (measured: with `assigns \nothing` ALONE the same body is NOT-PROVED: w3120 / w3130 controls) and proves the body that writes `self.v`, i.e. it reads the frame as their union; #489's classifier reads the same lines as the substring `assigns \nothing` and marks the dunder `pure`, so a `\trusted` callee's `len(o)` / `o == 1` / `o + 1` on it is admitted. The caller's `ensures \result == 0` over `o.v` is proved
  EXEMPLAR: g312/w3140_two_assigns_contig_len.py (`#@ assigns \nothing` / `#@ assigns self.v` / `def __len__(self) -> int: self.v = 7; return 1`; `#@ \trusted def k(o: C) -> int: return len(o)`; f: `#@ ensures \result == 0`, `o = C(); k(o); return o.v`); g312/w3100_orphan_blank_len.py (the `\nothing` line, a blank line, then `#@ assigns self.v`); g312/w3151_two_assigns_rev_eq.py (`assigns self.v` first, `__eq__`)
  CPYTHON: f(0) returns 7 -> VIOLATION contract 7
  WHY IT PROVES: src/pycsl/pycsl.py:27899-27909 (`_bk489`: the #@ AND blank lines above a def joined into one string) and :27953 (`if "assigns \\nothing" in _tx489: _k489 = "pure"` -- a substring test, evaluated BEFORE the verified-frame test that would have classified the dunder `self` / `other`); the dunder's own whole-file proof succeeds with a body that writes `self.v`, so the frame the VERIFIER applies is not `\nothing` (measured; with `assigns \nothing` alone the same file is NOT-PROVED) -- the two components read one contract two ways
  PROPOSED SYSTEMATIC REPAIR: classify from the IR, never from the comment text: a dunder is pure iff its WOVEN contract's frame is empty (`_ir1489['contracts']['assigns']` == [`\nothing`] after union) or, for a verified dunder, its inferred `_r316_frame` writes nothing; independently, Module 3 should REFUSE a contract that states `assigns \nothing` together with another `assigns` clause (a self-contradictory frame) instead of taking the union
  PROBES: g311/s3200_t_pure_text_orphan_nothing_above.py g311@typed/s3200_t_pure_text_orphan_nothing_above.py g311@store/s3200_t_pure_text_orphan_nothing_above.py g312/w3100_orphan_blank_len.py g312@typed/w3100_orphan_blank_len.py g312@store/w3100_orphan_blank_len.py g312/w3101_orphan_blank_eq.py g312@typed/w3101_orphan_blank_eq.py g312@store/w3101_orphan_blank_eq.py g312/w3102_orphan_blank_add.py g312@typed/w3102_orphan_blank_add.py g312@store/w3102_orphan_blank_add.py g312/w3110_orphan_two_blanks_len.py g312@typed/w3110_orphan_two_blanks_len.py g312@store/w3110_orphan_two_blanks_len.py g312/w3111_orphan_two_blanks_eq.py g312@typed/w3111_orphan_two_blanks_eq.py g312@store/w3111_orphan_two_blanks_eq.py g312/w3112_orphan_two_blanks_add.py g312@typed/w3112_orphan_two_blanks_add.py g312@store/w3112_orphan_two_blanks_add.py g312/w3140_two_assigns_contig_len.py g312@typed/w3140_two_assigns_contig_len.py g312@store/w3140_two_assigns_contig_len.py g312/w3141_two_assigns_contig_eq.py g312@typed/w3141_two_assigns_contig_eq.py g312@store/w3141_two_assigns_contig_eq.py g312/w3142_two_assigns_contig_add.py g312@typed/w3142_two_assigns_contig_add.py g312@store/w3142_two_assigns_contig_add.py g312/w3150_two_assigns_rev_len.py g312@typed/w3150_two_assigns_rev_len.py g312@store/w3150_two_assigns_rev_len.py g312/w3151_two_assigns_rev_eq.py g312@typed/w3151_two_assigns_rev_eq.py g312@store/w3151_two_assigns_rev_eq.py g312/w3152_two_assigns_rev_add.py g312@typed/w3152_two_assigns_rev_add.py g312@store/w3152_two_assigns_rev_add.py

PROVED BUT NOT COUNTED / ENVIRONMENT-DEPENDENT (excluded.txt):
  g309/y3130_max_two_len.py | VIOLATION TypeError '>' not supported between instances of 'C' and 'C' | PROVED, but the claim is ensures-only (`ensures \result == 0`) and CPython RAISES (max(o, o) with no __gt__ / __lt__ on C) -- an exception under an ensures-only claim is not counted; the counted twins y400-y413 give C pure ordering dunders
  g309/y3131_max_two_add.py | VIOLATION TypeError '>' not supported between instances of 'C' and 'C' | PROVED, but the claim is ensures-only (`ensures \result == 0`) and CPython RAISES (max(o, o) with no __gt__ / __lt__ on C) -- an exception under an ensures-only claim is not counted; the counted twins y400-y413 give C pure ordering dunders
  g309/y3132_max_two_truth.py | VIOLATION TypeError '>' not supported between instances of 'C' and 'C' | PROVED, but the claim is ensures-only (`ensures \result == 0`) and CPython RAISES (max(o, o) with no __gt__ / __lt__ on C) -- an exception under an ensures-only claim is not counted; the counted twins y400-y413 give C pure ordering dunders
  g309/y3133_max_two_neg.py | VIOLATION TypeError '>' not supported between instances of 'C' and 'C' | PROVED, but the claim is ensures-only (`ensures \result == 0`) and CPython RAISES (max(o, o) with no __gt__ / __lt__ on C) -- an exception under an ensures-only claim is not counted; the counted twins y400-y413 give C pure ordering dunders
  g303/t3210_t_alias_ensures_result.py | (removed before proving) | its claim was a \trusted callee's OWN wrong ensures (\result == 1 while len(o) is 2): a user trust assumption, not a verifier false proof -- dropped from the census
  g300/e3016_t_sorted_lt.py | result 0 | control: CPython does not breach (not proved)
  g300/e3116_d_sorted_lt.py | result 0 | control: CPython does not breach (not proved)
  g300/e3017_t_max_gt.py | result 0 | control: CPython does not breach (not proved)
  g300/e3117_d_max_gt.py | result 0 | control: CPython does not breach (not proved)
  g300/e3018_t_min_lt.py | result 0 | control: CPython does not breach (not proved)
  g300/e3118_d_min_lt.py | result 0 | control: CPython does not breach (not proved)
  g300/e35103_r_del_raises_noexc.py | result 0 | control: CPython does not breach (not proved)
  g304/c30012_init_field_repr_list.py | result 0 | control: CPython does not breach (not proved)
  g311/s3107_t_sub_int_index.py | result 0 | control: CPython does not breach (not proved)
  g320/k32120_float_param_add.py | result 0 | control: CPython does not breach (not proved)
  g320/k32121_float_param_lt.py | result 0 | control: CPython does not breach (not proved)
  g320/k32130_bool_param_add.py | result 0 | control: CPython does not breach (not proved)
  g320/k32131_bool_param_lt.py | result 0 | control: CPython does not breach (not proved)
  g320/k32132_bool_param_idx.py | result 0 | control: CPython does not breach (not proved)
  g320/k32133_bool_param_range.py | result 0 | control: CPython does not breach (not proved)
  g330/o3335_dc_initvar_read.py | result 0 | control: CPython does not breach (not proved)

NOTES / AXES THAT HELD (no counted false proof -- negative results for the coordinator):
  (A) #489 / #490 converged: 237 / 237 rt41 rows refused by the intended route (184 PYCSL-R489-IMPLICIT-DUNDER, 53 route #490).
  (B) #490 HELD on every new flow: g310 (126 probes: globals, fields, class attributes, closures, lambdas, defaults, *args / **kwargs,
      un-annotated returns, generators, dict / list mutators and readers, comprehensions, walrus, exception args, unpacking, for over
      mixed tuples / dict items / values / enumerate / zip, nested containers, str.split / str(n) / f-string, re.match None,
      os.environ.get, mixed max / sorted / sum, rebinding through if / loop / try, fromkeys, repetition, set.pop, min / next / getattr
      defaults): 0 PROVED -- route #490 (32), #325 opaque-int fallback (16), #458 / #440 / #437 / #161 / #443 / #460 / #65 / #178 / #232
      / #441 / #72, 10 refused without a route tag, fail-closed Why3 typing (11) / NOT-PROVED (8). g320 (55 breaching probes: Any / object / Union / Optional /
      `int | None` / unannotated / List[Any] / Dict[str, Any] / Tuple[Any, ...] / bare list, dict / Sequence[Any] / float nan / bool
      parameters used as + 1, < 3, list index, range; json / str / bytes library values): 0 PROVED (#441, #349, #438, #178, #458,
      #440, Why3 typing, Timeout / Unknown).
  (B) #489 HELD on most new channels: g300's t-variants of __setitem__ / __delitem__ / __iadd__ / __isub__ (route #317), __call__ /
      list.count / index / == / operator.* / functools.reduce / map(len) / list(o) / copy.copy / math.floor, trunc / '{}'.format /
      any([o]) (route #482), != / reflected > / >= / reflected == / in / slices / bin / '%s' / float / + ~ ** << % / repr fallback /
      __len__ truth fallback / while / and / `in` -> __iter__ / old-style __getitem__ iteration / reversed (route #489), hash
      channels (#349), sorted(key=len) (#275); the direct (d) and raising (r) variants in the verified f fail Why3 typing (71) or are
      refused (fail closed). Installation by decorator / module-level setattr / lambda class attribute / metaclass, descriptors
      __get__ / __set__, __set_name__ / __init_subclass__ / __del__ writing a global, __iadd__ on a record field: refused. A dunder
      aliased to a MODULE-level def (g301 q32xx), an inherited alias (q3300), imported callees with un-annotated parameters (g303 t31xx):
      fail Why3 typing. __index__ through str-method / list-method / math / itertools / to_bytes arguments (g303 t300x-t301x): route #482.
      g302: globals / self fields NOT-PROVED; field-of-argument, list / dict / tuple element, *args, kw-only, method / staticmethod of
      another class, returned-then-passed, local alias, object / Any / unannotated / Optional parameters: all PYCSL-R489 (42).
      g305: key=o (sorted / max / min) and round(..., ndigits=o) route #275; iter(o, s) inside list(), enumerate start route #482;
      dict-subclass __missing__ route #393. g306: bodyless __eq__ / __add__ / __radd__ / __getitem__ / __contains__ / __setitem__ /
      __call__ / __new__ / reflected __gt__ of another class reached implicitly: Why3 typing / #289 / #290 (only the __init__ forms
      prove, F3). g307: global registry / class attribute / program-call roots and scalar-annotated parameters fed a record via Any:
      refused or Why3 typing (one identity-call row is F4). g308 / g309: `q = ident(o); len(q)` (control) PYCSL-R489; Box(o).o and
      most builtin pass-throughs route #482. g311: program SUBCLASSES of str / int / float / list / dict / bytes passed to
      scalar-annotated parameters: route #393 (subclassing a builtin) -- the `_SC489` annotation skip is not reachable today.
      g314: a dunder def nested in a class-body `try` / `if False: ... else:` is refused (route #387); the `if True:` spelling is F2.
  (C) g330 (41 breaching object-model probes): 0 PROVED (#161, #449, #348, #349, #369, #347, #360, #445, #339, #458, #327, #283,
      Why3 typing, one Timeout).
  MODES: --memory-model typed / store re-proofs of every CPython-breaching g301-g308 probe, the g300 leads and every g309 / g311-g314 confirmed probe: F1-F4 0 PROVED (Why3 typing /
      refused) -- F1-F4 are default-model (hoare) false proofs (0 PROVED under typed / store for any F1-F4 probe); F5 proves in ALL THREE models (13 probes x hoare / typed / store = 39 counted pairs).
      --fun f: every default confirmed probe re-proves (not counted again).
  Hygiene: g301 / g303 / g305 rows.tsv had multi-line construct texts that a `cut -f4` split into words (one an unquoted `*`); the
      resulting junk outputs (111 files, none a probe) were deleted before the census and rows.tsv repaired -- every probe's verdict
      comes from its own .out.

VERIFY (one to three exemplars per family copied to verify/ with their helper modules, re-proved + re-run on the rt42 tree by verify.sh inside heavy.sh):
  b30080_init_abstract_len.py                   pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  c30000_init_field_len.py                      pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  c30307_call_dunder_eq.py                      pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  c3200_imported_unmarked_init_len.py           pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  q3000_t_index_list_mul_r.py                   pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  q3014_t_index_round_ndigits.py                pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  q3100_t_alias_len.py                          pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  q3102_t_alias_eq.py                           pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  t3200_t_alias_len_with_real_dunder.py         pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  u3004_t_next_iter_sentinel.py                 pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  u3005_t_isinstance_cls.py                     pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  p3000_ident_len.py                            pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  p3021_me_eq.py                                pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  p3013_pick_str.py                             pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  y400_max_two_ordered_len.py                   pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  w3140_two_assigns_contig_len.py               pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  w3100_orphan_blank_len.py                     pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  w3151_two_assigns_rev_eq.py                   pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  m3150_self_double_mid_len.py                  pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  n3100_if_true_len.py                          pycsl: rc=0 Verification SUCCESS  CPython: VIOLATION contract 7
  re-run: cd /home/fabrice/git/pycsl-rt42 && PYTHONHASHSEED=0 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py
          /home/fabrice/git/pycsl/scratchpad/rt42/verify/<probe> --import-path src/pycsl [<flags>]; CPython: cd verify && /home/fabrice/git/pycsl-rt42/.venv/bin/python3 -E -s <probe>

STATUS: 2026-10-31T03:01:55Z -- regenerated by mkfind.py (139 confirmed)
```
