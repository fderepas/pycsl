# OPEN ROUTE #394 — §7.47 ALLOW-LIST HAS NO SOURCE FOR MODULE GLOBALS, CLASS ATTRIBUTES, DICT VIEWS PASSED TO set()/frozenset(), AND copy
**Status: REPAIRED for every witness and source family, candidate (gen #37, 2026-10-26; e1 executor off 3b2d2e763 -- sound refusal, see REPAIR; the full unknown-is-refused flip MEASURED at 27/53 mirrors and NOT landed; repaired with routes #392 / #394 / #395). Was OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r394/`: `c01_D_set_dict_values.py`, `c02_D_set_items.py`, `b05_set_of_dict_values.py`, `b24_set_of_items_list_values.py`, `h32_items_set_list_vals.py`, `h33_frozenset_values.py`, `h36_set_keys_of_listkey.py`, `c03_D_classattr.py`, `b51_set_of_list_classattr.py`, `h27_class_attr_via_self.py`, `h40_frozenset_classattr.py`, `h38_class_attr_list_in.py`, `c04_D_module_global.py`, `b52_set_of_module_list.py`, `h24_global_list_elem.py`, `h25_global_dict_value.py`, `h39_set_of_global_list.py`, `h41_global_dict_list_value.py`, `h43_tuple_with_global.py`, `c27_D_copy_copy.py`, `c28_D_replace.py`, `h30_copy_method.py`.

```
#394 §7.47 ALLOW-LIST HAS NO SOURCE FOR MODULE GLOBALS, CLASS ATTRIBUTES, DICT VIEWS PASSED TO set()/frozenset(), AND copy  [slips past #383 addendum]
  set()/frozenset() over a dict view (the argument is a Call, so `_hx349` stays empty):
    c01 set(d.values()) d: Dict[str, D];  c02 set(d.items());  b05 / h36 set(d.values()) of List[int];  b24 / h32 set(d.items());
    h33 frozenset(m.values())                                                                    all CPython TypeError
  class attributes:  c03 {C.K} (K = D(1)), b51 {C.XS} (XS = [1]), h27 {self.K}, h40 frozenset(C.XS), h38 `C.XS in s`
  module globals:    c04 {K} (K = D(1)), b52 {XS} (XS = [1]), h24 {G[0]}, h25 {G["a"]}, h39 set(G), h41 {G["a"]} of a list,
                     h43 {(G, 1)}
  copies:            c27 {copy.copy(x)}, c28 {dataclasses.replace(x)}, h30 b = copy.copy(a); {b}      (x: D, unhashable)
  WhyML: every one lowers the hashed value to `any int` / an abstract `set_1 (..)`, so `no_exception` holds trivially.
  These are not the §7.47 "underivable" residual: the values have a literal initialiser in the file (or are copies of a
  typed parameter). The allow-list polarity is still a deny-list in practice: an element whose class the propagation does
  not DERIVE is admitted.
  REPAIR: make "class not derived" mean UNKNOWN => refused in a hashing position (true allow-list), with sources added for
  module-level / class-level bindings (type of their initialisers, any store), `copy.copy` / `copy.deepcopy` /
  `dataclasses.replace(x, ..)` = class of x, and `set` / `frozenset` / `Counter` / `fromkeys` / `dict` over ANY iterable
  argument (views `.values()` / `.items()` / `.keys()`, names, calls) checked by the iterable's element class.
```

## REPAIR (2026-10-26, e1 executor off 3b2d2e763, with routes #392 / #394 / #395; code + corpus + census + docs in commit 3445dc472; docs annotations §7.49 / translational §T.6.60)
**Design: sources added to the #383 derivation, inline (mirror twin `\trusted`, no emission change).** Module globals bound once and class-body names bound once type as their initializer (literal, tuple, file-class constructor, primitive builtin call, class / def / lambda = hashable, primitive arithmetic; a list / set / dict display has its elements' classes only when the name is READ-ONLY, else UNKNOWN elements, refused when hashed); `C.k` along C's MRO and `o.k` over o's class and every file subclass when no field `k` exists; stdlib imports / builtin names by their real object; `copy.copy` / `copy.deepcopy` / `dataclasses.replace` = class of the argument; `set` / `frozenset` / `Counter` / `fromkeys` / `dict` over ANY iterable hash its element types.
**The full allow-list flip was built, MEASURED and NOT landed** (log-mode scans, evidence in `getting-better/systematic-soundness-r3/e1-r392-395/`): refusing every underivable (`#UND`) hashed value refuses 27 / 53 mirrors (679 sites, `mirflipA.tsv`: `Dict[str, Any]` IR reads such as `node.get('name')`, values derived from them, un-annotated parameters), 7 root / pyref PASS files in the first scan (0882, 0883, 1318, 3600, pyref 0091, 0212, stdlib/collections/counter_proves) and `pycsl_lib/syscfg`; refusing only values with NO source at all still refuses 7 mirrors (19 sites, `mirflipB.tsv`: attributes of `ast` nodes / imported user-module records, un-annotated parameters). A refused mirror loses a proved file, so the polarity stays a deny-list for UNDERIVABLE values (residual, as §7.47); every value with a recognised source is now precisely typed.
Witnesses 5555-5576 (all 22). Control 5591.
Gates (candidate vs base worktree at 3b2d2e763): root byte-diff 2423 -> 2426 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (+3 controls); pyref 2186 -> 2186, 0/0/0; mirror 53/53 0/0/0 (no OWED proof); `pycsl_lib` --no-proof screen identical (104 files). Every witness PROVED at base (rc=0) and is REFUSED on the candidate (rc=1); controls 5590-5592 PROVED at base and candidate. Census rows written with `_census_row` (31 new; the 90 `is HASHED by` rows re-measured: message extended, prefix identical).
