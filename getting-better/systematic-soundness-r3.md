# Systematic soundness repair — measurement report (driver run #3, executor sys1)

**Status: FINAL (2026-10-26; interim committed e2a5342cf at ~23:45Z).** Base: main `7bf752d4e`. Evidence and
scripts: `getting-better/systematic-soundness-r3/` (`classify.py`, `routes.tsv`, `probes.tsv`,
`families.txt`, `proto_rules.py`, `screen.sh`, `head-*-verdicts.tsv`, `live-at-7bf752d4e.txt`).

## 1. The question

For ~25 red-team rounds every confirmed false proof was repaired one route at a time and the
confirmed count per round did not converge (rt23..rt30: 6*, 61, 27, 35, 31, 67, 75, 60 by this
census; *rt23 recorded 5 combined files). Is there a SYSTEMATIC rule — an allow-list with
refuse-by-default, or one central "is this modelled?" predicate — that catches the families
that produce most findings at an acceptable over-refusal cost?

## 2. Root-cause families (scripted: `classify.py`)

Families: **a** construct ignored / partially modelled · **b** stdlib/builtin semantics assumed ·
**c** erased value treated as known · **d** class machinery (MRO, metaclass, descriptors,
decorators, dataclass, enum, hashing, constructors/invariants) · **e** aliasing / effects /
frames · **f** contract plumbing · **g** name resolution / shadowing.

Two levels. ROUTE level = every root cause the README opened from red teams 6..30 (104 routes,
hand-labelled once in `routes.tsv`). PROBE level = every confirmed false proof that has a probe
file: rt25..rt30 exact (the red team's FINDINGS section -> route), rt11..rt24 from the
`<<<<< FALSE PROOF` lines mapped to the round's routes by the red team's own probe-prefix
grouping (`PREFIX` in `classify.py`; approximate inside mixed rounds). rt6..rt10 have prose
logs only (route level only).

| level | a | b | c | d | e | f | g | total |
|---|---|---|---|---|---|---|---|---|
| routes rt6..rt30 | 14 | 12 | 16 | **45** | 9 | 2 | 6 | 104 |
| routes rt24..rt30 | 3 | 0 | 6 | **40** | 1 | 0 | 2 | 52 |
| probes rt11..rt30 | 69 | 42 | 182 | **294** | 20 | 21 | 34 | 662 |
| probes rt23..rt30 (last 8) | 25 | 5 | 47 | **278** | 2 | 0 | 5 | 362 |

Per round (probes): see `families.txt`. The drift is stark: rt11..rt21 are spread over a/b/c/e/f/g
(erasure c peaks at rt19..rt21 = 94 probes, then collapses after #325's opaque-int fallback); from
rt24 on, class machinery is **77% of all confirmed findings** (278 / 362).

Class-machinery subfamilies (294 probes): constructor / invariant goal (`ctor`, incl. route #226
`\length`) 89 · hashability 75 · enum 43 · dataclass specifiers 29 · MRO walks 19 · getattr
default 12 · `__slots__` 10 · class-body bindings 10 · metaclass / typing constructs 5 ·
subtyping 2.

**The 2-4 families that produce most findings:** (d) class machinery — dominantly hashability,
constructor/invariant goals, enum and dataclass models; (c) erased values (now mostly closed by
#325); (a) partially modelled constructs (eval order, starred args).

## 3. Live census: what is still a false proof at `7bf752d4e`

Every confirmed probe (662) plus every file of the open `witnesses-r381..r391` dirs (107) was run
on `7bf752d4e` (`screen.sh`, one heavy.sh job, `--no-proof` then full proof of the type-checking
ones; verdicts committed in `head-*-verdicts.tsv`):

* 426 REFUSED at `--no-proof`, 343 type-check; of those 199 FAIL and **144 PROVED**;
* deduplicated by content (open dirs copy rt29/rt30 probes): **82 distinct live false proofs**
  (`live-at-7bf752d4e.txt`).

| route | live | what |
|---|---|---|
| #381 | 14 | stdlib base (UserList, deque, OrderedDict, Counter, defaultdict, SimpleNamespace, array, argparse.Namespace, collections.abc.Set/Mapping) hashed |
| #382 | 17 | container-typed parameter / local hashed |
| #383 | 16 | element class not derived (alias, get, values(), comprehension, Any, object, TypeVar) |
| #226 | 8 | documented not-covered `\length`/int-field invariant shapes (rt29 a04..a46) |
| #388 / #389 | 3 / 4 | getattr default folded past an exception / ABC / NamedTuple base; past setattr / mangling / init=False |
| #391 | 5 | Protocol / TypedDict construction and isinstance |
| #390 | 2 | `**` into sorted / sum |
| #385 | 1 | mutable default shared |
| older | 12 | #304 x3, #306, #321, #325, #326, #330 x2, #334, #342, #351 (documented residuals of repaired routes) |

So **47 of the 82 live false proofs are hashability (#381-#383)**, all open and owned by the r381
executor (WIP not landed, see route #382).

## 4. Candidate systematic rules and their measured cost

Cheap prototype: `proto_rules.py` is the AST predicate each rule would test in a Module-3 /
`_run_pipeline` pre-pass (program text only; `__main__` driver excluded as PyCSL excludes it). It
was run over the four PASS populations and the probes:

* corpus = `test-suite/corpus/pycsl-reference` without `# pycsl-expected: FAIL` (1421 files),
* pyref = `test-suite/corpus/python-reference` (recursive) without FAIL marker (2173 files),
* mirror = `src/self-annotate/src/**.py` (53), lib = `src/pycsl_lib/**.py` (104);
* hist = confirmed probes rt11..rt30 flagged (662), live = distinct live false proofs flagged (82).

| rule | refuses | corpus | pyref | mirror | lib | hist | live | cost |
|---|---|---|---|---|---|---|---|---|
| **RA** unmodelled outside base (stdlib/builtin base not in a BASE-MODEL table; class referenced outside `__main__`) | `class D(collections.UserList)` | **0** | **0** | **0** | **0** | 14 | **14** | one inline block at the single base-resolution point (#341) |
| RA (refuse on definition, no reference filter) | | 2 (4634, 4832) | 0 | 0 | 0 | 14 | 14 | |
| RAm typing-construct bases (NamedTuple / Protocol / TypedDict / ABC) | | 11 | 0 | 5 | 0 | 11 | 7 | refuses modelled features: NO |
| R2 class keywords (metaclass=, ...; literal TypedDict `total=` allowed) | | 1 (5171) | 2 (0080, 0082) | 0 | 0 | 3 | 0 | small, no live catch |
| R3 class decorators outside {dataclass(literal opts), mutable_state} | | 0 | 0 | 0 | 0 | 0 | 0 | no catch at all |
| R4 method decorators outside the modelled set | | 0 | 0 | 0 | 0 | 0 | 0 | no catch at all |
| R5 class-body statement allow-list (generalises #387; literal `if True:` kept) | `for`/`try`/`with`/`import`/expr in a class body | **0** | **0** | **0** | **0** | 15 | 0 | prevention only; 12 fresh latent probes (`l01..l13`) are ALL already refused/ill-typed at base by #132/#377/#387 |
| R5v computed class-attribute values | | 1 | 0 | 6 | 0 | 13 | 0 | mirror dispatch tables: NO |
| R6 / R6h dunder allow-list / class-machinery hooks (`__new__`, `__del__`, `__call__`, `__instancecheck__`, ...) | | 4 | 2 | 1 | 1-2 | 1 | 0 | no catch |
| R7 dunder/sunder class attributes (`__slots__`, `_ignore_`, `__hash__ = ..`) | | 10 | 1 | 3 | 1 | 31 | 0 | refuses modelled features: NO |
| R8 reflection (getattr/setattr/hasattr/vars/`__dict__`/`__class__`/super(X, o)) | | 12 | 4 | 14 | 3 | 22 | 7 | mirror uses getattr: NO |
| R8g 3-arg getattr in a file with a dynamic attribute store, or a literal private (`__x`) name | | 0 | 0 | 0 | 0 | — | 3-4 | partial #389 only |
| RH hash allow-list (admit an element / key only if its static type is POSITIVELY hashable; unknown -> refuse) | | in-tool, not prototyped here (r381 WIP `#UNK` rule) | | | | 75 | **47** | type-directed; owned by r381 |
| GD getattr-default flip (fold the default only when every MRO class is a file class or `object` and no dynamic store) | | in-tool | | | | 12 | 7 | #376/#388/#389 code |

**Finding 1 — syntax allow-lists have small leverage.** The union of the class-GRAMMAR rules (RA, RAm,
R2, R5, R5c, R6h, R7) flags only **70 of the 294** class-machinery findings, and every rule with
real catch (RAm, R7, R8) refuses MODELLED features used by PASS corpus / mirror files. Decorators,
hooks and dunder definitions produced essentially no findings (R3/R4/R6: 0-1). Most class-machinery
findings are not "an unrecognised construct slipped through" but "a RECOGNISED construct whose model
is a deny-list": hashability refused only when unhashability was proved (#349 -> #364 -> #365 ->
#366 -> #371 -> #372 -> #381 -> #382 -> #383), the constructor goal emitted only when statable and
otherwise ASSUMED (#226 -> #342 -> #384 -> #385), enum members recognised by spelling (#339 ->
#352 -> #353 -> #355 -> #356 -> #367 -> #370), dataclass specifiers by spelling (#361 -> #369 ->
#378), getattr default folded unless a binding was found (#309 -> #376 -> #388 -> #389).

**Finding 2 — the systematic repair is a POLARITY FLIP per modelled construct**, at the one point where
the model decides: admit only what is positively recognised as modelled, refuse everything else.
Measured instances: RA (bases; 0 over-refusal, 14 live), RH (hashability; 47 live), GD (getattr
defaults; 7 live). Route #384 (refuse an unstatable `\length` goal instead of assuming the
invariant) was such a flip and closed its family's assumption path.

## 5. Recommendation (interim)

1. **Land RA now** (this executor): one inline block where #341 resolves every base, a BASE-MODEL
   table, refuse-by-default; measured 0 over-refusal over 3751 PASS files, catches all 14 live #381
   witnesses and closes the stdlib-base share of EVERY MRO reader (hash, getattr default,
   constructor arity, R5, invariants) instead of one reader.
2. **RH (hash allow-list) is the highest-value rule (47 / 82 live)** but is type-directed and is the
   r381 executor's open WIP — recommend it be landed as an allow-list ("element type positively
   hashable, else refuse"), not as further deny-list sources; its over-refusal must be measured by
   the sweeps before landing (not done here to avoid a parallel competing implementation).
3. **GD (getattr default flip)** next (7 live), then a typing-construct flip for #391.
4. Do NOT land R3/R4/R6/R7/R8/RAm as blanket refusals: zero catch, or they refuse modelled features
   used by PASS files and the mirror.

Per-rule in-tool measurement of RA (byte-diff sweeps root / pyref / mirror vs base) and its gate
battery follow in the FINAL section.

## 6. FINAL — what was built (four polarity flips), measured in-tool

All four are sound refusals, inline (no new def; `_run_pipeline`'s mirror twin is `\trusted`; the
`expressions.py` text edit is outside the mirror), no emission change, no new axiom, `\trusted`
count 448 unchanged. Witnesses / controls are in this executor's ID block.

| rule | where | refuses | witnesses (PROVED at 7bf752d4e -> REFUSED) | controls (PROVED both) |
|---|---|---|---|---|
| **S1** unmodelled base (= RA) | `_run_pipeline`, after route #341's base walk | a base resolving to a stdlib / builtin class outside the BASE-MODEL table; main-file classes when named outside `__main__`, every class of a dependency module (route #181 resolution, transitive); an unresolved base in a file with a stdlib star import. `PYCSL-S1-UNMODELLED-BASE` | 5420-5433 (all 14 #381 witnesses), 5434/5435 (new two-level latents), 5448-5452 (driver probes a1 star, a4 dependency, a11 re-bound import, b1 star in dependency, b5 transitive re-export) | 5460-5463 |
| **GD** getattr default | `_run_pipeline`'s route #376 map | the default answered when the MRO reaches a stdlib / builtin base (`object` excepted), when the file stores attributes dynamically (`setattr` / `delattr` / `vars` / `__dict__` / `__setattr__` outside `__main__`), or for the mangled `_C__x` of a `self.__x` store. Existing `PYCSL-R376-GETATTR-CLASS-BINDING` | 5436-5442 (all 7 #388/#389 witnesses) | 5464, 5465 |
| **TC** typing constructs | after S1 | a `Protocol` / `TypedDict` class used as a value (call, isinstance, binding) — only annotation / base / cast positions admitted. `PYCSL-TC-TYPING-CONSTRUCT-VALUE` | 5443-5447 (all 5 #391 witnesses) | 5466 |
| **SB** starred args to builtins | route #379's call walk | a `*` / `**` argument at a call of a builtin name. Existing `PYCSL-R379-STARRED-CALL-ARGUMENT` | 5453, 5454 (both #390 witnesses), 5455 (`max(*xs)`, ill-typed at base) | 5467 |

**Over-refusal, measured in-tool** (emission sweeps vs a base worktree at `7bf752d4e`, logs in
`systematic-soundness-r3/gates-v3/`): root corpus 2411 -> 2419 .mlw, 0 MOVED / 0 GONE / 0 APPEARED
(8 new controls); python-reference 2186 -> 2186, 0 / 0 / 0; mirror 53 / 53, 0 / 0 / 0 (no OWED
proof). Every over-refusal the prototype predicted was removed by a justified refinement, not
by re-labelling a PASS file: 4634 / 4832 (stdlib-base classes named only by `__main__`) and 4772
(`int` mixin of an enum) stay PASS. One measured over-refusal was REJECTED: GD's first cut also
treated a USER-module base as unknown and GONE'd mirrors `module6_whyml/expressions` and
`statements` (emitter mixins from sibling modules) — that part is a residual, not landed.

**Live census after the four rules** (`--no-proof` screen of the 82 live false proofs): 26 now
REFUSED (S1 14, GD 7, TC 5) + the 2 #390 ones refused by SB as corpus witnesses 5453 / 5454 = **28
of 82**. Remaining 54: #382 / #383 hashability 33 (r381s owns it; RH allow-list recommended to it),
#226 not-covered invariant shapes 8, #385 1, older documented residuals 12.

**Gate battery** (commit `c19787b5c` + census `SB` rows; the S1-only battery for `3e69a82b8` is
in `gates-s1/`): check-self-annotate-sync rc 0; self-annotate-mirror-check rc 0 (53/53);
byte-diff root rc 0 and pyref rc 0 (counts above); mirror sweep compare rc 0; refusal-witness
coverage rc 0 (312 demonstrated, 5 undemonstrated = ceiling 5); refusal-advice audit rc 0;
doc-coherency rc 0; fast soundness planes rc 0, 61/61 green (`gates-v3/planes.log`; the
first v2 run was RED 2/61 on control 5466's vacuous helper, fixed in 5466 and re-run green);
no new axiom; `\trusted` 448.

**Residuals (not closed):** (1) user-module bases are still not read by the getattr map
(#376/#388 residual); (2) S1 trusts route #341 for unresolved names outside a stdlib star import
(e.g. names created by `globals()` writes) and `exec`-built classes; (3) TC admits a
`@runtime_checkable` protocol nowhere (sound, but would over-refuse a future user of it; 0 today);
(4) RH (type-directed hash allow-list) not built here by agreement with the driver.
