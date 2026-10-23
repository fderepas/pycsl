# OPEN ROUTE #323 — THE itertools LENGTH MODEL DROPS KEYWORDS, MATCHES BY SHORT NAME, AND COUNTS A STARRED ARG AS ONE OPERAND
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Red-team round 18 (stdlib/builtin model); driver-reproduced on main 3b07a838 (rc=0; CPython violates).
Witnesses `witnesses-r323/`: `_iter_len_expr` (expressions.py ~7168): `len(list(itertools.product(xs, repeat=2)))` modelled as `len(xs)` (k01;
keywords dropped on the dotted path); a user-defined `product`/`chain` returning [0] is modelled as itertools' (k02, k03; `fn.rsplit(".", 1)[-1]`
short-name match); `len(list(chain(*xss)))` -> `Array.length xss` (k06; product(*xss) k09).
Repair: resolve the callee to the real itertools binding (refuse when shadowed/unresolved); refuse any keyword or starred argument in the length
model; census other short-name oracles (#75/#305 class).

## REPAIR (2026-10-23, r321 executor, detached off 67edf13c; shared with route #321: commits 9f153cc6, 40e2c287 + docs)
Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`):

| shape | 67edf13c | after |
|---|---|---|
| `len(list(itertools.product(xs, repeat=2))) == 2`, \|xs\|=2 (k01 / 4164; CPython 4) | PROVED | REFUSED (keyword) |
| user `def product(a, b): return [0]`, `len(list(product([1,2],[3,4]))) == 4` (k02 / 4165; CPython 1) | PROVED | FAIL (goal unproven: the user's function) |
| user `def chain(..)`, same (k03 / 4166) | PROVED | FAIL |
| `len(list(itertools.chain(*xss))) == len(xss)` (k06 / 4167) | PROVED | REFUSED (starred) |
| `len(list(itertools.product(*xss))) == 2`, xss=[[1,2,3],[4]] (k09 / 4168; CPython 3) | PROVED | REFUSED (starred) |
| NEW: user `def list(a): return [0]`, `len(list([1,2,3])) == 3` (4169; CPython 1) | PROVED | FAIL (L3-tc: the user's `list` is lowered as a call) |
| control: `import itertools as it` / `from itertools import chain as ch` (4174) | FAIL (alias `ch` unmatched, L3-tc) | PASS |
| corpus 0530 (chain), 0547 (product), 0548 (islice) | PASS | PASS (byte-identical) |

Rules (inline in `_iter_len_expr`, mirror twin `\trusted`, now declares `#@ raises PyCSLIRError`; no new def/field;
ledger 3): the callee is resolved through `self.ir["imports"]` (Module 5's `(local, original, module, level, is_module)`
table): bare `list` only when no user definition (`_module_method_return_types`) or import binds `list`; a bare name only
when EVERY import binding it is `from itertools import <orig> [as name]` (level 0) and no user definition shadows it (the
original name is used, so `chain as ch` resolves); `M.<attr>` only when every import binding `M` is `import itertools
[as M]` and `M` is not user-defined. An unresolved callee returns None (the generic call path lowers the user's own
function — fall through as route #75 does). A resolved `chain`/`product`/`islice` with any keyword or `Starred` argument
is REFUSED; `list(..)` with one returns None.
CENSUS of nearby short-name oracles (reported, not changed — outside this route's local edit scope):
`_os_path_split_slot` (~3477) keys on the receiver PREFIX `os.path.` / `_os.path.` / `ospath.` (a user module
imported `as ospath` would be taken for `os.path`); `_IR_DISPATCHERS` suffix matches in `_slice_bound_to_iropt_ir` (~4350/~4387) and `_disp_call_over_target` (~19405) (`fn.rsplit(".",
1)[-1]` — emitter-internal IR-dispatcher names, self-annotation only); the str-predicate suffix oracle at ~11608 is
already guarded by route #74. `islice(it, n)` with a negative `n` (CPython ValueError): under `no_exception \all` the call
is refused ("not a function of the verified program"), so no false proof was found (probe k10).
Blast radius (shared run with #321): corpus root 1 MOVED (1076, #321's), 0 GONE, 0 APPEARED; pyref 0/0/0; mirror 2 MOVED
(raises clauses only, L3-tc OK, whole-file proofs OWED — commands in route #321's REPAIR).
Gates (logs under `.r321tmp/`, removed at hand-off): witnesses table above + route #321's; byte-diff-sweep base rc=0
(2157 of 2969 root / 2186 of 2217 pyref) and after rc=0 (2166 of 2995 / 2186 of 2217); byte-diff-compare root rc=0 with
`--expect-moved 1076_route48_counter_seed_dropped` (rc=1 without it, that single mover), pyref rc=0; mirror-emit-sweep
base/after rc=0 (53/53), compare `--min-files 50` rc=0 with `--expect-moved Module6_WhyMLTranspiler
module6_whyml__expressions`; both movers L3-tc rc=0; check-self-annotate-sync.sh rc=0 (926 verbatim);
self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast rc=0 (61/61); doc-coherency --check rc=0;
check-assumed-facts rc=0; check-trusted-raises-honesty rc=0 (17 declared / 61 silent, ratchet 61 — it read 63 > 61
until the two mirror stubs declared `#@ raises`); check-refusal-witness-coverage (no flags) rc=0 (270 demonstrated, 5
undemonstrated = ceiling) after 21 rows appended via `_census_row` (16 REFUSAL, 5 VERIFY-FAIL).
Residuals: `islice`'s length model still trusts a non-negative `stop` outside `no_exception` (a raising path, not a
returned value); local rebinding of an imported itertools name (`chain = f`) inside a function body is not seen by the
import-table resolution (none in the corpus); `itertools.chain.from_iterable` is not modelled (opaque).
