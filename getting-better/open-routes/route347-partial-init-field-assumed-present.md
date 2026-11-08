# OPEN ROUTE #347 — A FIELD STORED ON ONLY SOME `__init__` PATHS IS ASSUMED PRESENT
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r346 executor off b83a217b — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r347/`: `k03_branch_init_field.py`.

`__init__(self, flag): if flag: self.x = 1`; `f(r)` under `no_exception` returns `r.x` and PROVES; CPython `f(R(False))` raises AttributeError. Route #342 checks store forms only for invariant-carrying classes.

Repair: Refuse (or obligate) a field read under `no_exception` when some constructor path does not store it (definite-assignment over `__init__`).

## REPAIR (2026-10-25, r346 executor off b83a217b; code 2054301b, corpus + docs ff6941ee, census 44f8d480 + route docs)
**Design: sound refusal, no emission change** — one inline block appended to the #341/#342 block of `_run_pipeline` (mirror twin
`\trusted`; no new def; ledger 3), shared by routes #346-#349 (annotations §7.28, translational §T.6.39). Base closure: each class's
in-file base names, left-to-right depth-first (an over-approximation of the MRO's class set).
**Why a refusal.** "Obligate" would need a presence bit per field in the record model (every read guarded, every store setting
it) — an emission change over every record of the corpus. Refusing the READ under an AttributeError-covering `no_exception`
is local and measured inert (0 hits). RULE `PYCSL-R347-FIELD-MAYBE-UNASSIGNED`: definite assignment over each class's constructor
(own `__init__`, as bottom-up GEN summaries: `if` meets both branches, loops / `with` bodies / `try` bodies not covered by every
handler count nothing, an early `return` exits with what was stored so far, `raise` builds no instance, a leading
`super().__init__()` / `B.__init__(self, ..)` adds the base constructor's set, `del self.f` removes `f`; else a dataclass's /
NamedTuple's synthesized fields minus `field(init=False)` without default; else the first ancestor's). A field (stored on `self`
by any method of the class or its ancestors, or declared by a dataclass) that is neither definitely assigned nor a class-level
binding is MAYBE-ABSENT; an attribute load / `del` / augmented target of that NAME (any receiver except an imported module) in a
non-trusted function whose `no_exception` is `\all` or names AttributeError / Exception / BaseException is REFUSED.
**Probe table** (full pycsl proof via heavy.sh; base = b83a217b):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| k03 `if flag: self.x = 1` | 4663 | AttributeError | rc=0 PROVED | rc=1 REFUSED R347 |
| (new) early `return` before the store | 4664 | AttributeError | rc=0 PROVED | rc=1 REFUSED R347 |
| (new) store inside `try` with a swallowing handler | 4665 | AttributeError | rc=0 PROVED | rc=1 REFUSED R347 |
| (new) field stored only by another method | 4666 | AttributeError | rc=1 FAILED (Why3 unbound field) | rc=1 REFUSED R347 |
| (new) `no_exception` METHOD reads `self.x` | 4667 | AttributeError | rc=0 PROVED | rc=1 REFUSED R347 |
| (new) `field(init=False)` without default | 4668 | AttributeError | rc=0 PROVED | rc=1 REFUSED R347 |
| controls: both branches 4688; class-level default 4689; leading `super().__init__()` 4690; the storeless path raises 4691 | 4688-4691 | ok | rc=0 | rc=0 PROVED |
Scratch, not filed: `del self.x` in a method is REFUSED at base by the attribute-`del` rule (unchanged); a read in an UNANNOTATED
helper called from a `no_exception` function still PROVES (`q347d`) — implicit exceptions of callees are ambient by the
documented exception model (`--strict-no-exception-propagation` flips it), not a new hole.
**Census / blast radius.** Before landing, every class-bearing file of the root corpus, pyref, the 53 mirrors and `pycsl_lib`
(1286 files) was screened `--no-proof` with the candidate: **0 hits outside the new witnesses** (no latent false proof in the
corpora; nothing newly refused). Root / pyref / mirror byte-diffs 0 MOVED / 0 GONE / 0 APPEARED (below).
**Gates** (logs in the executor scratchpad; rc): witnesses / controls above (full proof via heavy.sh, base b83a217b vs
candidate); byte-diff-compare root rc=0 (2289 base / 2300 candidate: 0 MOVED / 0 GONE / 0 APPEARED, 11 new control sources),
pyref rc=0 (2192/2192 0/0/0, `--min-files 2000`), mirror rc=0 (53/53 0/0/0, `--min-files 50`: **no OWED proof**) — the first
parallel sweep showed 2 root GONE (4280/4281 shadow-import) and 5 pyref MOVED + 1 GONE (stdlib/json drivers): each re-emitted
singly is byte-identical base vs candidate (the json driver's verdict depends on the CWD — a `json/` directory at the repo root —
identically in both trees), i.e. parallel-sweep / CWD artefacts, not movers; check-self-annotate-sync.sh rc=0 (926 verbatim);
self-annotate-mirror-check.sh rc=0 (53); check-getattr-erasure rc=0; check-stdlib-modules-verify rc=0-equivalent (run in 5 foreground chunks with its own `classify` + BASELINE: 104 modules, 83 VERIFY, 0 newly not verifying, 0 baseline now verifying); run-soundness-planes.sh
fast **61/61** rc=0; `--slow` NOT run; doc-coherency --check rc=0; check-assumed-facts rc=0 (ledger 3); check-dropped-mutation rc=0 (0 / 51 / 5 / 0);
check-refusal-witness-coverage rc=0 (293 demonstrated / 5 not, ceiling 5; rows 4660-4685 via `_census_row`); check-trusted-reasons
rc=0 (420 / 420); check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61); check-assigns-underdeclaration --transitive rc=0 (TRAP 3,
HOLE 0); check-mirror-coverage rc=0 (549 / 41).
**Residuals.** (1) Ambient callees (above). (2) By-NAME over-approximation: a maybe-absent field name refuses reads of the same
attribute name on any receiver (0 users). (3) Over-refusal: a store reached through `self.m()` in `__init__`, a `with` body, a
`while True` constructor, `hasattr`-guarded reads (0 users). (4) An imported base's constructor is not analysed (its fields are
not in the file's field set, so they are not refused either: per-file check, like #342's residual (3)). (5) `getattr(r, "x")`
without default and `vars()` / `__dict__` paths are not this rule's (other refusals cover `__dict__`).
