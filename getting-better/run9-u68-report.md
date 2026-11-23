# run #9 u68: re-witness the two R327 raise sites (rt77 F3)

Branch `run9-u68`, worktree `/home/fabrice/git/pycsl-u68`, based on `run9-u65` (474fd000d; src state
f43343311). No `src/` change. `\trusted` 366, ledger 3 (`src/pycsl/proof_axiom_allowlist.py` not
touched). Corpus IDs used: 10400, 10401 (block [10400, 10404]).

## 1. Defect (F3) confirmed

The real `_census_row` (`scratchpad/u68/CR.py`, a copy of u65's `tools/CR.py`: it imports
`bin/check-refusal-witness-coverage.py` and calls its `_census_row`; cwd = tree root, relative path)
at f43343311 gives (`scratchpad/u68/rows.tsv`):

- `4307_gen37_r327_function_casefold.py`: REFUSAL `PYCSL-SEM-WHYML-NAME-CLASH (route #620) ... 'F'
  (function, line 6), 'f' (function, line 10)`
- `4308_gen37_r327_class_casefold.py`: REFUSAL `PYCSL-SEM-WHYML-NAME-CLASH (route #620) ... 'ab__m'
  (method, line 9), 'ab__m' (method, line 16)`

The committed census still had the R327 text for both. They were the only rows that demonstrated the
two R327 sites, `the classes ...` (pycsl.py:17861) and `the functions ...` (pycsl.py:17876).

## 2. Fix

1. `bin/refusal-witness-census.tsv`: the stale 4307 / 4308 rows were deleted, and the rows the real
   `_census_row` produced were appended. No row was hand-edited.
2. Two new corpus FAIL witnesses. Each has `# pycsl-expected: FAIL` and a docstring that names the site
   it witnesses. Their real `_census_row` rows were appended too.
   - `test-suite/corpus/pycsl-reference/10400_r327_function_site_lifted_casefold_witness.py`. This is
     rt77's c327b: nested `def f` in `p` and in `q`, plus a module `def F`. #620 skips a lifted-name
     collision, so the R327 function site fires. Row: `PYCSL-R327-IDENT-COLLISION (route #327) — the
     functions 'f' and 'F' lower to ONE WhyML identifier 'f'.`
   - `test-suite/corpus/pycsl-reference/10401_r327_class_site_dataclass_casefold_witness.py`. Two
     `@dataclass` classes, `Ab` (field `x`) and `AB` (field `y`), with no methods. Both lower to type
     declarations, and no two functions share a WhyML name. Row: `PYCSL-R327-IDENT-COLLISION (route
     #327) — the classes 'Ab' and 'AB' lower to ONE WhyML namespace ('ab') ...`

**The class site is REACHABLE at head.** These are the `--no-proof` probes at head (HEAVY_QUICK,
`scratchpad/u68/q.sh`, probes in `scratchpad/u68/probes/`):

| probe | shape | head |
|---|---|---|
| k1_dataclass_fields | `@dataclass` Ab.x / AB.y, no methods | R327 classes |
| k2_distinct_methods | `__init__` + `m1` / `m2` (distinct method names) | R327 classes |
| k3_methods_noinit | methods `m1` / `m2`, no `__init__`, no fields | admitted (no type decl, like rt77 c327a) |
| k4_dataclass_same_field | `@dataclass` Ab.x / AB.x | R327 classes |
| rt77 c327a | class attributes only | admitted (as rt77 found) |
| rt77 c327b | lifted pair + `def F` | R327 functions |

k2 is worth noting. Two classes that both define `__init__` get the identical IR name `ab____init__`,
but `self_type` differs, so I expected #620 to fire. It does not. R327 is what refuses k2. This
suggests the constructors are not separate IR functions in this shape. It does not change the fix, and
I did not investigate it further.

Both witnesses run clean under CPython: rc 0, and their `__main__` asserts pass
(`scratchpad/u68/sw/cpython.txt`).

## 3. Gates (all on the final tree state; oom_kill 15 before and after)

| gate | result | log |
|---|---|---|
| check-refusal-witness-coverage, BEFORE (stale rows) | rc 0, 488 / 5, but dishonest: 4307 / 4308 were the stale demonstrators | `scratchpad/u68/cov-before.txt` |
| check-refusal-witness-coverage, AFTER (run alone) | **rc 0**, see the full output below | `scratchpad/u68/cov-after.txt` |
| counterfactual: AFTER census minus the 10400 / 10401 rows, `--list-unwitnessed` (census restored, `cmp` identical) | rc 1, **486 demonstrated, 7 not, UNWITNESSED CEILING BROKEN 7 > 5**. The 2 extra are exactly pycsl.py:17861 (classes) and :17876 (functions). So the two new rows, and only they, demonstrate the R327 sites | `scratchpad/u68/cov-counterfactual.txt` |
| byte-diff root: base `run9-u65` (detached tree `/home/fabrice/git/pycsl-u68b`) vs head, cwd = each tree root, NORMAL heavy | rc 0: 3329 / 3329 .mlw, 0 MOVED, 0 GONE, 0 APPEARED. New sources 10400 / 10401 are both refused (no .mlw) | `scratchpad/u68/sw/C-root.txt`, `sw/base.log`, `sw/head.log` |
| byte-diff pyref | rc 0: 2185 / 2185, 0 / 0 / 0 | `scratchpad/u68/sw/C-pyref.txt` |
| check-corpus-executes | rc 0: 2608 / 2616 load (the 8 known), 1704 / 1704 self-checks | `scratchpad/u68/sw/ce.txt` |
| run-soundness-planes.sh (fast, teed in full) | rc 0, **62 / 62** ok | `scratchpad/u68/sw/planes.txt` |
| full verdict of each new witness (`_census_row` runs the full pipeline, no `--no-proof`) | 10400 REFUSAL (R327 functions), 10401 REFUSAL (R327 classes). Both match the `FAIL` header | `scratchpad/u68/rows.tsv` |
| `\trusted` count (`grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py'`) | 366 | -- |
| `git diff run9-u65 -- src bin` | only `bin/refusal-witness-census.tsv` (+4 / -2) | -- |

Full output of check-refusal-witness-coverage AFTER:

```
[*] refusal-witness-coverage: 517 raise site(s) in the compiler, 3889 witness(es) censused (3003 refusals); 488 site(s) DEMONSTRATED to fire, 5 not.
[*]   plus 14 refusal(s) NOT REACHABLE from a `.py` source file, demonstrated executably by bin/check-ir-schema-refusals.py and bin/check-frontend-ir-backstop-refusals.py instead.
[*]   plus 10 refusal(s) UNMATCHABLE by this instrument: their message has no string literal of 25+ characters, so no witness can ever mark them demonstrated. Closing them is a compiler/census change, not a corpus one.
[+] refusal-witness-coverage: OK — 488 demonstrated, 5 undemonstrated (floor 208 / ceiling 5); 14 not source-reachable, 10 unmatchable (ceiling 10).
```

Corpus-ID note (rule 38): `ls test-suite/corpus/pycsl-reference | cut -c1-4 | sort | uniq -d` was not
empty before this change (62 lines). It is 63 now, because a 4-character cut of a 5-digit ID collides
with an older 4-digit ID (`1040_route40_...` vs `10400_` / `10401_`), as 10360-10364 already do with
1036. Full-ID uniqueness (`cut -d_ -f1 | sort | uniq -d`) shows only the pre-existing `r613z`.

## 4. Commands

```
heavy.sh .venv/bin/python3 scratchpad/u68/CR.py scratchpad/u68/rows.tsv <4307> <4308> <10400> <10401>
heavy.sh .venv/bin/python3 bin/check-refusal-witness-coverage.py
scratchpad/u68/sweeps.sh   (heavy.sh bin/byte-diff-sweep.sh, base tree then head tree)
.venv/bin/python3 bin/byte-diff-compare.py sw/base sw/head --new-source 10400_... 10401_...
.venv/bin/python3 bin/byte-diff-compare.py sw/base/pyref sw/head/pyref --min-files 2000
heavy.sh .venv/bin/python3 bin/check-corpus-executes.py
heavy.sh bin/run-soundness-planes.sh | tee sw/planes.txt
```

The sweep emission dirs (`scratchpad/u68/sw/{base,head}`) are not committed because of their size. They
stay on disk in the u68 worktree. The detached base tree `/home/fabrice/git/pycsl-u68b` can be removed
with `git worktree remove`.
