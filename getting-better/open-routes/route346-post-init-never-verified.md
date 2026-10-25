# OPEN ROUTE #346 — A DATACLASS `__post_init__` IS NEVER EMITTED / VERIFIED — THE INVARIANT IS ASSUMED AFTER IT BREAKS IT
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r346 executor off b83a217b — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r346/`: `k08_dataclass_post_init.py`.

`@dataclass class D: x: int`, `#@ invariant x >= 0`, `__post_init__: self.x = -1` (a top-level store, admitted by R342). The generated `__init__` is checked (d01/m01/m05/m06 FAIL correctly) but `__post_init__` produces no goal: `f(d)` with `ensures d.x >= 0` PROVES; CPython -1.

Repair: Emit and verify `__post_init__` as part of construction (invariant goal after it), or refuse `__post_init__` on invariant-carrying classes.

## REPAIR (2026-10-25, r346 executor off b83a217b; code 2054301b, corpus + docs ff6941ee, census 44f8d480 + route docs)
**Design: sound refusal, no emission change** — one inline block appended to the #341/#342 block of `_run_pipeline` (mirror twin
`\trusted`; no new def; ledger 3), shared by routes #346-#349 (annotations §7.28, translational §T.6.39). Base closure: each class's
in-file base names, left-to-right depth-first (an over-approximation of the MRO's class set).
**Why a refusal.** Route #150 makes a construction that runs `__post_init__` OPAQUE (every field unknown) and route #226's
constructor goal is skipped for an opaque construction, so the invariant was assumed. A faithful repair would emit
`__post_init__` as a body composed after the synthesized `__init__` and state the invariant goal after it; but an invariant on a
dataclass whose fields are `__init__` parameters is never establishable anyway (control-shaped `q346f`: the goal
`forall x. x >= 0` FAILS without a `__post_init__`), and the census finds **0** invariant-carrying classes with a `__post_init__`
in the corpora, mirrors or `pycsl_lib` (7 root files use `__post_init__`, none with an invariant), so the refusal costs nothing.
RULE `PYCSL-R346-POST-INIT-INVARIANT`: a record with merged `class_invariants` whose base closure holds a `@dataclass` and a class
defining `__post_init__` (own or inherited) is REFUSED.
**Probe table** (full pycsl proof via heavy.sh; base = b83a217b):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| k08 `__post_init__: self.x = -1`, invariant `x >= 0` | 4660 | -1 | rc=0 PROVED | rc=1 REFUSED R346 |
| (new) no-op `__post_init__`, `D(-5)` in a verified fn | 4661 | -5 | rc=1 FAILED (call-site precondition) | rc=1 REFUSED R346 |
| (new) `B(A)` invariant on B, `A.__post_init__` stores -1 | 4662 | -1 | rc=0 PROVED | rc=1 REFUSED R346 |
| control: `__post_init__` without invariant, `no_exception` read | 4686 | 3 | rc=0 | rc=0 PROVED |
| control: invariant class with explicit `__init__` | 4687 | 0 | rc=0 | rc=0 PROVED |
Scratch, not filed: a raising `__post_init__` under `no_exception` is REFUSED at base by route #179 (unchanged); `D(3).x` read
straight off a constructor call is a Why3 type error at base and after (pre-existing, unrelated).
**Census / blast radius.** Before landing, every class-bearing file of the root corpus, pyref, the 53 mirrors and `pycsl_lib`
(1286 files) was screened `--no-proof` with the candidate: **0 hits outside the new witnesses** (no latent false proof in the
corpora; nothing newly refused). Root / pyref / mirror byte-diffs 0 MOVED / 0 GONE / 0 APPEARED (below).
**Gates** (logs in the executor scratchpad; rc): witnesses / controls above (full proof via heavy.sh, base b83a217b vs
candidate); byte-diff-compare root rc=0 (2289 base / 2300 candidate: 0 MOVED / 0 GONE / 0 APPEARED, 11 new control sources),
pyref rc=0 (2192/2192 0/0/0, `--min-files 2000`), mirror rc=0 (53/53 0/0/0, `--min-files 50`: **no OWED proof**) — the first
parallel sweep showed 2 root GONE (4280/4281 shadow-import) and 5 pyref MOVED + 1 GONE (stdlib/json drivers): each re-emitted
singly is byte-identical base vs candidate (the json driver's verdict depends on the CWD — a `json/` directory at the repo root —
identically in both trees), i.e. parallel-sweep / CWD artefacts, not movers; check-self-annotate-sync.sh rc=0 (926 verbatim);
self-annotate-mirror-check.sh rc=0 (53); check-getattr-erasure rc=0; check-stdlib-modules-verify @@STDLIB@@; run-soundness-planes.sh
fast @@PLANES@@; doc-coherency --check rc=0; check-assumed-facts rc=0 (ledger 3); check-dropped-mutation rc=0 (0 / 51 / 5 / 0);
check-refusal-witness-coverage rc=0 (293 demonstrated / 5 not, ceiling 5; rows 4660-4685 via `_census_row`); check-trusted-reasons
rc=0 (420 / 420); check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61); check-assigns-underdeclaration --transitive rc=0 (TRAP 3,
HOLE 0); check-mirror-coverage rc=0 (549 / 41).
**Residuals.** (1) An imported dataclass base's `__post_init__` is not seen (per-file check). (2) Without an invariant a
`__post_init__` keeps route #150's opacity (fields unknown) — sound, not refused. (3) Over-refusal: an invariant dataclass whose
`__post_init__` only validates (0 users).
