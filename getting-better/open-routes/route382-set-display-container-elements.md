# OPEN ROUTE #382 — CONTAINER VALUES AS SET-DISPLAY ELEMENTS ARE NEVER CHECKED
**Status: OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r382/`: `h34_deque_param.py`, `h35_typing_deque_param.py`, `h36_set_param.py`, `h37_simplens_param.py`, `h39_userlist_param.py`, `h40_ordereddict_param.py`, `h41_defaultdict_param.py`, `h42_array_param.py`, `h43_counter_param.py`, `h44_mutableset_param.py`, `h45_list_builtin_param.py`, `h46_dict_builtin_param.py`, `h54_typing_list_param.py`, `h55_typing_dict_param.py`, `h60_list_local_display.py`, `h61_list_of_list_elem.py`, `h62_list_loop_elem.py`.

`{xs}` with `xs` annotated list / List / dict / Dict / Set / MutableSet / deque / Deque / SimpleNamespace / UserList / OrderedDict / defaultdict / array / Counter, a list local display, `{xs[0]}` over `List[List[int]]`, `for y in xs: {y}`: proves under no_exception; CPython TypeError. (`hash(xs)`, `{xs: 1}`, `xs in {..}`, `s.add(xs)`, `frozenset(..)` are correctly refused.)

Repair: Apply the hash()/add/in container-type test in the set-display element position.

## gen #37 (2026-10-25) — r381 executor WIP (NOT landed, ungated)
Candidate WIP in `../pycsl-r381` (9cb374e71 #381 stdlib-base table + #383 aliases; 18acf06af #382 container test + #383 type
propagation; 5b063cdd0): `--no-proof` screen refuses all 47 #381-#383 witnesses (R349); no full proofs, sweeps or gates run;
over-refusal risk of the #383 `#UNK` rule unmeasured (mirror emit sweep required before landing). Measured live at base and NOT
yet witnessed: `s.add(d)` and `{d: 1}` with `d: deque` PROVE (contrary to this route's note); `types.MappingProxyType` is
classed hashable. Next: sweep 9cb374e71 alone first, then the full candidate.
