# OPEN ROUTE #467 — UNCLAIMED IMPORTED CALLEE's exceptions: the #460 reached claim does not cross files and #178's raising-body walk misses assert / next() / unbounded self-recursion / pow(.., -1, m) / attribute of an int / a further helper, so `f` claiming `no_exception \all` that calls an un-contracted helper of another module proves (AssertionError / StopIteration / ValueError / AttributeError)
**Status: REPAIRED (executor x1, driver run #3, 2026-10-29), Severity 1.** Red-team round 38 (2026-10-29, on a9eac4a08 after #460-#462: 688 probes / 155 proved / 142 confirmed; rt37's 83 all closed except #463 / #464). Census TSV `scratchpad/rt38/census.tsv`; the family block below is quoted from `scratchpad/rt38/FINDINGS.txt`.
Witnesses `witnesses-r467/` (17): `g2_m225_helper_unclaimed_assert.py`, `g2_m233_u_next_empty.py`, `g2_m234_u_assert_false.py`, `g2_m235_u_chain_assert.py`, `g2_m238_u_pow_neg_mod.py`, `g2_m240_u_dict_get_attr.py`, `g2_m324_str_index.py`, `g2_m327_getattr_missing.py`, `g2_m328_len_of_int.py`, `g2_m329_call_int.py`, `g2_m330_iter_int.py`, `g2_m335_json_loads_bad.py`, `g2_m336_open_missing.py`, `g2_m338_str_plus_int.py`, `g2_m340_bytes_decode.py`, `g2_m342_struct_pack.py`, `g2_m345_range_step_zero.py`.

Driver repro: 17/17 family exemplars (scratchpad/rt38/verify/, F8 without --import-path) rc=0 Verification SUCCESS on main a9eac4a08 at 2026-10-29T14:55Z, each violating under CPython (scratchpad/rt38/driver-repro.txt).

```
F3 UNCLAIMED IMPORTED CALLEE's exceptions: the #460 reached claim does not cross files and #178's raising-body walk misses assert / next() / unbounded self-recursion / pow(.., -1, m) / attribute of an int / a further helper, so `f` claiming `no_exception \all` that calls an un-contracted helper of another module proves (AssertionError / StopIteration / ValueError / AttributeError) (17)
  EXEMPLAR: g2/m234_u_assert_false.py (h234: un-contracted `def g(x): assert x != x; return x`; f: `#@ no_exception \all` `return g(n)`)
  CPYTHON: AssertionError from g; also StopIteration (next(iter([]))), ValueError (pow(2, -1, 4*x)), AttributeError (x.zz on an int), an assert in a SECOND helper of the imported file (m235), AttributeError of `h.g` bound only under if False (m256); g2f: str.index ValueError, getattr(x,'zz'), len(int) / int() / iter(int) TypeError, json.loads JSONDecodeError, open() FileNotFoundError, 'a' + int TypeError, bytes.decode UnicodeDecodeError, struct.error, range step 0 ValueError
  WHY IT PROVES: an imported def is a trusted stub; route #460's reached claim stops at the file boundary ('Not reached: #439 (another file's defs)') and #178's walk of the imported body is a DENY-list of raising constructs (it refuses KeyError / ZeroDivisionError / int('x') / index / math.sqrt / unpacking -- m204 m205 m230 m231 m232 m236 m241) that misses assert, next(), pow-mod, attribute loads and nested callees.
  PROPOSED SYSTEMATIC REPAIR: ALLOW-LIST AT THE IMPORT BOUNDARY: under a caller claim covering E, a call of an imported def that carries no claim covering E is REFUSED (PYCSL-R460-IMPORTED-UNCLAIMED), unless the def's body is verified under the reached claim in this run -- i.e. extend #460's closure through the import graph and judge the imported body exactly as a local reached def (trigger assertions in its body, discharged by its own requires). Do not grow #178's construct list. Witnesses m225 m233 m234 m235 m238 m240 m256; control: a helper with `#@ no_exception \all` and a body that proves (PASS).
  PROBES: g2/m225_helper_unclaimed_assert.py g2/m233_u_next_empty.py g2/m234_u_assert_false.py g2/m235_u_chain_assert.py g2/m238_u_pow_neg_mod.py g2/m240_u_dict_get_attr.py g2/m324_str_index.py g2/m327_getattr_missing.py g2/m328_len_of_int.py g2/m329_call_int.py g2/m330_iter_int.py g2/m335_json_loads_bad.py g2/m336_open_missing.py g2/m338_str_plus_int.py g2/m340_bytes_decode.py g2/m342_struct_pack.py g2/m345_range_step_zero.py
```

## REPAIR (executor x1, driver run #3, 2026-10-29, off daf5c3d1f; annotations §7.281, translational §T.6.291)

Same block, after route #466's imports succeed: for each def with a claim C (`_rc444`, own or reached), every
function of a PROGRAM module it reaches -- a call or value of an imported name, `M.g`, a constructor of an imported
class (`__init__` / `__new__` / `__post_init__` / every dunder of its program-module MRO, also through a class of this
file deriving from it, and a dataclass `default_factory`), every method of an imported class with the name of an
attribute the def reads -- must CLAIM `#@ no_exception` covering C itself (a declared modular assumption: the callee is
verified when its module is), or have a body on the exception-free allow-list (returns / assignments / augmented
`+ - * & | ^` / `if` over `int` / `bool` parameters, comparisons, boolean operators; no call, subscript, attribute);
otherwise REFUSED, `PYCSL-R467-IMPORTED-UNCLAIMED`. #178's deny-list is not grown.

Red-team witnesses (`witnesses-r467/`): 17/17 PROVED on daf5c3d1f, 17/17 REFUSED by #467. Corpus witnesses 7270-7274
(assert, next of an empty iterator, getattr of a missing attribute, json.loads, a second helper's assert): PROVED at
base, REFUSED. Control 7286 (the callee claims `no_exception \all`, its `assert` discharged by its own `requires`) and
corpus 6642 (route #439's control: `inc(n): return n + 1`, on the allow-list): PROVED at base and candidate.

GATES (worktree pycsl-x1 off daf5c3d1f; bases = v13/ca, v13/ma, the emission of 33f7ac681, docs-only since):
fidelity check-self-annotate-sync rc=0 (938 un-trusted mirror functions verbatim), self-annotate-mirror-check rc=0
(53); doc-coherency rc=0. Byte-diff root 2604 -> 2609 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new controls); pyref
2186 / 2186 0/0/0; mirror 53 / 53 0/0/0 (no OWED proof). Planes / ledgers: see the x1 commit message (fast planes
61/61 after naming the import-raising fixtures in check-corpus-executes; trusted-reasons, assumed-facts,
refusal-witness-coverage, refusal-advice-audited, dropped-mutation, getattr-erasure, open-route-carriers,
frame-honesty, raises-honesty, clause-survival, stdlib-modules-verify all rc=0; trusted 437 unchanged).
OVER-REFUSAL COST, measured: the 24 claimed corpus files that import a non-standard-library module (23 expected
FAIL, 1 PASS = 6642) -- 6642 still PROVES (its un-claimed `inc` is on the #467 allow-list); 0 pyref / mirror /
pycsl_lib files carry a claim, so #466 / #467 / #472 cannot fire there. #466's judge run over every multi_file_lib
helper imported under a claim: 51 of 58 accepted, 1 refused by #466 (`circ_b` imported first: CPython raises
ImportError too, the plane's KNOWN_LOAD_FAILURES says so), 6 refused by older routes. #468 (no claim gate): a wide
first cut refused corpus 3382 (a `\trusted` `tid(x): return x`) and 11 mirror files (all through explicit
`\trusted` stubs or stubs no verified code of the file calls) -> narrowed (returning the list is a read; an explicit
`\trusted` def is a declared assumption; only vals the verified code references are judged): 0 GONE.

## RESIDUALS
- A callee's OWN `#@ no_exception` claim is assumed (a declared modular assumption, as its contract already is:
  rt38 m202 / m203); it holds when its module is verified.
- The method-tail match is by NAME over every class of the program modules (a reference `.m` judges every
  imported `m`): an over-approximation, so over-refusal only.
- Functions of INSTALLED packages are library code (#161 / #178 judge calls to them, as before).
