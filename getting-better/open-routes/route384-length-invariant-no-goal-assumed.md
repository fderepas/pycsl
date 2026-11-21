# OPEN ROUTE #384 — A `\length` INVARIANT WHOSE CONSTRUCTOR GOAL CANNOT BE STATED IS ASSUMED (post-store mutation / computed initialisers)
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r384 executor off 0a2d8019b — end-state goal + sound refusal, see REPAIR; shared with #384 / #385). Was OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r384/`: `c01_len_inv_init_pop_after_literal.py`, `c04_len_inv_param_rebound.py`, `c05_len_inv_self_pop_in_init.py`, `c12_len_inv_default_factory_lambda.py`, `c13_len_inv_literal_then_slice_store.py`, `c15_len_inv_negative_repeat.py`, `c18_len_inv_restore_slice.py`, `c20_len_inv_clear_after_list_literal.py`, `c22_len_inv_alias_field_pop.py`, `c23_len_inv_local_alias_pop.py`, `c25_len_inv_loop_pop.py`, `c26_len_inv_reverse_ok_then_remove.py`, `c29_len_inv_literal_list_of_lists_repeat.py`, `c38_len_inv_pop_index0.py`, `c40_len_inv_pop_in_if.py`, `c41_len_inv_list_param_ignored.py`, `c42_len_inv_ge_with_pop.py`, `c44_len_inv_param_pop_tok_growth.py`, `k10_len_inv_concat_literal.py`, `k11_len_inv_slice_literal.py`, `k13_len_inv_nested_list_literal.py`, `k15_len_inv_bool_repeat.py`, `k16_len_inv_comprehension.py`, `k17_len_inv_list_call_literal.py`, `k18_len_inv_paren_repeat_sub.py`, `k20_len_inv_sorted_literal.py`, `k21_len_inv_repeat_kwonly_param.py`, `k25_len_inv_walrus_store.py`, `k26_len_inv_list_param_repeat.py`.

When the list field is changed after its store in `__init__` (pop / clear / remove / alias / second store / loop / if) or its initialiser is computed (`default_factory`, `[0]*-1`, concatenation, slices, comprehensions), route #226 increment 2c emits NO `_check_class_inv` goal and the `\length` invariant is assumed (k* = the documented computed-initialiser residual, now measured live). CPython IndexError / count 2 against `ensures <= 1`.

Repair: Fail-closed: an invariant-carrying class whose constructor goal cannot be stated is refused (or FAILs), never assumed — census the goal-less classes first (2c measured 39).

## REPAIR (2026-10-25, r384 executor off 0a2d8019b; code 43ef55ea1 / 06912f666 / 80cb35620, corpus 06912f666, docs 06cf27dd5 (annotations §7.40 / translational §T.6.51), census + carriers 8c37ef315, route docs)
**Design (shared by #384 / #385): the constructor goal reads each list field's END state; an unstatable `\length` goal is
REFUSED, never assumed.** Code 43ef55ea1 / 06912f666 / 80cb35620 (`_run_pipeline` inline + Module 6 `_emit_type_decls` inside route #226
increment 2c's projection, inline, no new def, no new `self` field, ledger 3; both mirror twins `\trusted`), corpus 06912f666, docs
06cf27dd5 (annotations §7.40 / translational §T.6.51), clause-survival ledger 88896db0f, census + carriers 8c37ef315.
RULES. (1) `_run_pipeline`, before `transpile()`, walks each file class's own `__init__` (a class without one takes its first file
base's) top-level statement by statement and gives every stored field an end state `ctor_len_r384[C][f]`: `LEN(n)` for a FRESH list
of literal length — a display, `[..] * K` (`len * max(K, 0)`: `[] * N` and a negative repeat are EMPTY), `bytearray(K)` / `bytes(K)`
/ `list()`, K an int literal or a module constant bound once — then only top-level `self.f.append/insert/extend([..])/pop()/pop(i)/
clear/reverse/sort` with call-free arguments; `PARAM(p)` for `self.f = p` when p and `self.f` are named nowhere else in `__init__`
(beyond `len(..)`, `x[i]` reads, `x[i] = v` element stores) and no call follows the store; `UNKNOWN` otherwise (any other mention,
alias, second / tuple store, loop / branch / walrus effect, `return`, a later `__init__` call). (2) Module 6: `LEN(n)` gives the
premise `(Array.length f) = n` (overriding `field_defaults`, admitting fields Module 5 marks computed); `UNKNOWN`, or 2c's binding
failing for an array field, is a STATE obstacle: no goal, and if the projection found no TERM obstacle Module 6 emits the marker
`(* PYCSL-R384-NO-GOAL <C>: <why> *)`, on which `_run_pipeline` raises NEW `PYCSL-R384-INVARIANT-GOAL-UNSTATABLE` after emission.
(3) NEW `PYCSL-R385-DELEGATED-INIT-REQUIRES-UNCHECKED` (`_run_pipeline`, in route #342's block): a `super().__init__(..)` /
`super(X, self).__init__(..)` / `B.__init__(self, ..)` call reaching a file class whose `__init__` has a `#@ requires` and a
parameter typed other than int / bool / unannotated (route #335 already composes int arguments into the subclass's own goal).
**Census (measured first; the 2b/2c instrumentation, temporary, removed before commit).** Emitter-level, `--no-proof` over the 403
files carrying `#@ class invariant` (both corpora, 53 mirrors, `pycsl_lib`, `open-routes/`): base 236 goals / 79 goal-less classes
(39 outside the red-team-30 witnesses). After: **21** goal-less corpus classes GAIN a goal (0421-0428, 0452, 0459-0461, 0715, 0716,
0719, 0720, 0723-0725, 1248, 1249 — every one `bytearray(<literal | module constant>)`, 2c's "computed container" residual, e.g.
`forall disk : array int. (Array.length disk) = 4096 -> ..`); **0** corpus / mirror / `pycsl_lib` classes are refused; every one
of the 23 red-team classes still goal-less is refused. The 18 remaining goal-less classes stop on a TERM (element / quantifier /
string / predicate / attribute: 0659, 0661-0664, 0706, 0900, 0980, mirrors `Module2_Parser._ContractParser` / `pure_ast._Parser`,
`pycsl_lib` os) or on an INT field (computed: 4574, mirror `errors.py` x4, `pycsl_lib` dt; rt29 a04/a05/a08/a10/a11/a24/a34/a46,
#226 increment 3). OPTIONS MEASURED: refusing every goal-less `\length` class regardless of term obstacles would make the mirror
`Module2_Parser.py` GONE (`_ContractParser.toks` is a call result) — not taken; refusing every goal-less class (2b's option) is
8 corpus PASS files (0659, 0661-0664, 0706, 0900, 4574) + 3 mirror files GONE + 2 `pycsl_lib` modules — not taken; refusing the 21 `bytearray` classes instead of
stating their goal: 21 corpus files (16 PASS) refused — not taken, the goal is stated and discharges. R385 census: 64 files with a
delegating `__init__` call; a blanket "target has a `#@ requires`" rule would refuse 4475 (PASS, `super().__init__(3)`) and
`pycsl_lib` plib `Path` (`super().__init__(path)` under the same requires) — both honest, int-typed, composed by #335 — so the rule
is scoped to non-int parameters: 0 corpus / mirror / library users.
**Probe table** (full pycsl proof via heavy.sh; base = 0a2d8019b worktree; CPython ground truth in each `__main__`):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| c01 `[0] * 4; pop()` | 5240 | IndexError | rc=0 PROVED | rc=1 FAIL (`length = 3 -> length = 4`) |
| c02 `[] * 4` | 5241 | IndexError | rc=0 PROVED | rc=1 FAIL (`length = 0 -> ..`) |
| c15 `[0] * -1` | 5242 | IndexError | rc=0 PROVED | rc=1 FAIL |
| c20 literal then `clear()` | 5243 | IndexError | rc=0 PROVED | rc=1 FAIL |
| c05 `self.toks = toks; self.toks.pop()` | 5244 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| c03 `toks.clear()` after the store | 5245 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| c45 `toks.extend(..)` after the store | 5246 | count 4 | rc=0 PROVED | rc=1 REFUSED R384 |
| c35 tuple re-store `self.disk, self.k = [], 0` | 5247 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| c12 `default_factory=lambda: ..` | 5248 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| c22 field alias `self.other = self.disk; pop` | 5249 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| c25 pop in `for` | 5250 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| c40 pop in `if` | 5251 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| k10 `[0] * 2 + [0]` | 5252 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| k16 comprehension | 5253 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| k25 walrus `(t := self.disk.pop())` | 5254 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| c31 `super().__init__([])` | 5255 | IndexError | rc=0 PROVED | rc=1 REFUSED R385 |
| l04 `super().__init__(toks[1:])` | 5256 | IndexError | rc=0 PROVED | rc=1 REFUSED R385 |
| c04 parameter rebound before the store | 5257 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| k21 `self.disk = self.disk * 0` | 5258 | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| c29 `[0, 0] * 2; pop()` | 5259 | IndexError | rc=0 PROVED | rc=1 FAIL |
| c13, c18, c23, c26, c44, k11, k13, k15, k17, k18, k20, k26 (not filed) | — | IndexError | rc=0 PROVED | rc=1 REFUSED R384 |
| c38, c41, c42 (not filed) | — | IndexError | rc=0 PROVED | rc=1 FAIL (`length = 3 -> ..`) |
| c34 unverified caller clears the aliased list (registered carrier `route385-carrier-unverified-caller-alias.py`) | — | IndexError | rc=0 PROVED | rc=0 PROVED (residual) |
| NEW carrier `route384-carrier-element-term-masks-length-state.py` (an element term masks the field state) | — | IndexError | rc=0 PROVED | rc=0 PROVED (residual) |
| control `[0] * 4`, `append`, `pop()` | 5270 | 0 | rc=0 PROVED | rc=0 PROVED |
| control `[0, 0]` + `extend([0, 0])` | 5271 | 0 | rc=0 PROVED | rc=0 PROVED |
| control `[]` + `append(7)`, `\length >= 1` | 5272 | 7 | rc=0 PROVED | rc=0 PROVED |
| control `bytearray(N)`, module constant `N = 6` | 5273 | 0 | rc=0 PROVED | rc=0 PROVED |
| control `[0] * 4` + element store `self.disk[0] = 9` | 5274 | 0 | rc=0 PROVED | rc=0 PROVED |
| control PARAM field + `self.n = len(toks)` + requires | 5275 | Tok(7) | rc=0 PROVED | rc=0 PROVED |
35 of 36 red-team witnesses closed (8 FAIL, 27 REFUSED); c34 is the recorded residual.
**Blast radius.** byte-diff base 0a2d8019b vs candidate 80cb35620: root **21 MOVED** — exactly the census's 21 `bytearray`
classes, each diff ONLY `+ goal _check_class_inv_<c> : ...` (checked line by line) / 0 GONE / 0 APPEARED (2394 base / 2405 cand, 11
new emitting sources; the 15 refused witnesses do not emit); every mover re-proved to its label (16 SUCCESS; 0460, 0716, 0720,
0724, 0725 expected-FAIL stay FAILED); pyref 0/0/0 (2186/2186, `--min-files 2000`); mirror 53/53 0/0/0 (`--min-files 50`) —
**no OWED proof**. No conformance golden is a mover (the core goldens bypass `_run_pipeline`; no golden class is a state obstacle).
**Gates** (rc, logs in the r384 scratchpad `gates/`): witnesses / controls above; byte-diff-compare root rc=0 (`--expect-moved`
the 21), pyref rc=0, mirror rc=0; check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53);
run-soundness-planes.sh fast **61/61** rc=0 (incl. trusted-raises-honesty, core-only-conformance); check-getattr-erasure rc=0 (DECLARED 0); check-stdlib-modules-verify rc=0 (one command via heavy.sh: 83 VERIFY, the known 21 non-verifying);
doc-coherency --check rc=0; check-assumed-facts rc=0 (ledger 3); check-dropped-mutation rc=0 (0 / 51 / 5 / 0);
check-refusal-witness-coverage rc=0 (310 demonstrated / 5 undemonstrated = ceiling; the 2 new raise sites demonstrated by rows
5244-5258); check-trusted-reasons rc=0 (420 / 420); check-assigns-underdeclaration --transitive rc=0 (TRAP 3, HOLE 0 — a first cut
recorded the refused classes in a new `self.nogoal_r384` field of `_emit_type_decls`, TRAP 4 > 3; replaced by the emission
marker); check-open-route-carriers rc=0 (10 carriers incl. the two new residual ones, SUCCESS as recorded); check-clause-survival
`--emit-dir` candidate rc=0 (8 deficits, all ledgered: KNOWN_DEFICITS +1, control 5275 = 5110's route #15 residue; base's
UNEXPLAINED 4574 is EXPLAINED on main already). `--slow` planes not run.
**Residuals.** (1) An invariant whose goal ALSO stops at an element / quantifier / string / predicate / attribute term is not
refused — its `\length` field's end state is not even examined (registered carrier
`route384-carrier-element-term-masks-length-state.py`, SUCCESS; refusing it would make mirror `Module2_Parser.py` GONE, whose
`_ContractParser.toks` comes from `_lex_contract(source)`). (2) An unverified caller that keeps an alias of the list it passed and
mutates it after construction (c34; carrier `route385-carrier-unverified-caller-alias.py`; in VERIFIED code the mutation is
refused / fails closed, measured: `xs.clear()` refused, an `xs.append(..)` variant failed closed on a WhyML type error). (3) A PARAM field's goal still ignores
a call that mutates the caller's list through a GLOBAL alias before the store (the rule only looks after the store). (4)
`[] * N` / negative repeats are now right in the goal, but Module 5's `field_defaults` (record construction `C()` in verified code,
`_array_init_size`) still reads `[] * N` as N; 0 corpus users, and the class's own goal now fails, so no false proof measured.
(5) R385 over int / bool parameters relies on route #335's composition; an unannotated list parameter (`param_types` "") is not
covered by R385 (R384 still refuses a subclass whose list field has no goal). (6) Over-refusal: a subclass of a `\length` class
that only calls a paramless `super().__init__()` is refused (0 users); calls after a PARAM store (`self.k = int(n)`) poison it
(0 users).
