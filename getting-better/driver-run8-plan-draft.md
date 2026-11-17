# Driver run #8 plan (DRAFT): written by the run #7 driver

**Status:** DRAFT for the user. Nothing in it is approved. It builds on these sources:
- `getting-better/driver-run7-final-report.md` (§§5, 8, 10);
- `getting-better/run7-capability-census-3.md` (cv14);
- the two post-L13 measurement branches: `run7-sp5` (`getting-better/run8-spike-typed-tuple-return.md`) and `run7-u48` (`getting-better/run8-refusal-residuals.md`). Their numbers are folded in at §6 when they return.

The plan of record stays `driver-run5-plan.md`, with run #6's and run #7's lessons. This draft changes only what run #7 showed should change.

## 1. Where run #7 leaves things

- `\trusted` is **367** after L13 (389 at the start of run #7). 22 conversions were landed in five landings. The proof-axiom ledger is 3. There is one CERTIFIED-DEFINITIONAL WhyML family (the r4 `pairs_get` pair).
- **Main lever.** Run #7's yield came from small, measured capabilities built from the cv14 one-link rows:
  - external world models (lvQ, lvU, lvV);
  - generator-as-seq (lvT);
  - typed-local lowering (lvR).

  The dict value model r4 gave three conversions directly. Its value is mostly as infrastructure: hval maps, `or`-truthiness and isinstance narrowing.
- **What cv14 has left that is cheap:**
  - ONE-LINK: only `_why3_typecheck`, which needs a typed tuple-return exception in the VERIFIED return handlers (sp5 measures it).
  - TWO-LINK, measured: `SertopSession.type_of_batch`, `_synthesize_block`, `_to_cache_payload`, `parse_format`.
  - `_sig_val_from_let` is CORRECT. It is not convertible without a contract change.
- **Large families still blocking most stubs:**
  - CSL record vs `emit_ir` (the Module2 parser family);
  - pyast attribute write-back (Module3);
  - in-place IR-dict mutators (cv13 O11);
  - hval values at builtin call slots (O5);
  - hval `str.join` (O7);
  - `{x:.2f}` of an hval float (O18).

## 2. Changes to the loop (from run #7's incidents)

1. **Red team before the batch lands, not after.** Run #7's wrap-up round (rt61) found 6 INTRODUCED false proofs in two batches (#610). They had to be repaired under time pressure in the last 20 h. For run #8, each new world model or value-model extension gets a small red-team round on its integration tree, **before** the battery. The batch is "done" only when that round has returned (plan line 92 stays).
2. **A generic guard for world models.** The #610 rule is the template for every future `<mod>.<f>` model. The head name must be the module import and must be bound nowhere in the function scope. A new model reuses `shadow_r610`; it does not write its own check.
3. **WIP checkpoints every 2 h** in every executor brief. lvU's silent 8.5 h was recovered only because the driver salvaged its tree.
4. **Sweep cwd = repo root**, always. Import resolution depends on the cwd.
5. **The proof map is the main time saver.** Start the movers' whole-file proofs on a snapshot as soon as src is believed final. Carry them over when the tip's mirror emission is byte-identical (L10 step M; L13).

## 3. Candidate batches (cheapest first; to confirm with a census-4 at hour 0-4)

| batch | capability | stubs (cv14) | cost driver | gate |
|---|---|---|---|---|
| A | typed tuple-return exception (`Return_<k>` per tuple codomain) | `_why3_typecheck`; a link of `_rewrite_annotation_str` | **statements / stmt_control_flow re-proof plus every moved corpus file**: blast radius from sp5 (§6) | Gate S on sp5's numbers. No-go if the corpus blast radius cannot be re-proved within ~24 h of slot time |
| B | the u48 refusal rules (q05, q06, negative slice bound, rfind) | none (soundness) | corpus diff (§6) | land as refusal-only repairs; mirror-inert, or the movers proved |
| C | `type_of_batch` (Optional[Path] dataclass field + omitted `Optional[str] = None` argument as the union arm) | `SertopSession.type_of_batch` | sertop.py (small) | standard |
| D | hval `str.join` + `{t:.2f}` of an hval float (O7 + O18) | `_synthesize_block`; further hval rows | pycsl.py (~45 min) | standard; red team on the hval ops |
| E | hval wrap selection by static type + a comprehension of triples into `HArr` | `_to_cache_payload` | audit_proof_reverify (small) | standard |
| F | `tuple(<list>)` into a variadic `Tuple[str, ...]` field + an `Optional[<record>]` return | `parse_format` | struct_format | standard |

A realistic run #8 target: 367 → ~360. The stretch target depends on whether batch A is a go.

## 4. Heavy queue

- **2 proof slots stay** (user decision). PRIO for driver battery / batch-gate jobs only. `PYTHON_CPU_COUNT` ≤ 6 (4 for big `--fun`).
- **The --slow planes are the battery's longest step (~4 h).** Start the battery as soon as the integration tree is final. Run the movers' whole-file proofs on the other slot in parallel.
- expressions.py and statements.py whole-file proofs never run at the same time. Batch A must schedule its statements / stmt_control_flow proofs around this.

## 5. Open decisions for the user

1. Red team per batch, before landing (proposed in §2.1), instead of one round per two batches.
2. Batch A go / no-go, given sp5's blast radius.
3. The items still pending from earlier runs (unchanged):
   - #497 (`\abstract` policy);
   - #429 (Latin-1);
   - #414 (MemoryError);
   - `PyCSLError.__init__` `requires line >= 0`;
   - #461 top-level execution, and the #461 / #488 severities;
   - `#@ \diverges`.
4. Whether the pre-existing gap "a `str` subscript has no IndexError VC outside `no_exception`" should become an obligation. This would make the obvious subscript mutants fail. It is a corpus-wide emission change.

## 5b. First item for run #8 (added after L14)

- **Route #611 r12 is OPEN.** The case: a forged `__pycache__` pyc beside a stdlib-identical local copy. Refuse it, or validate the pyc against the source, before any new world model lands.
- **Add a resolver red-team axis** to every world-model batch. The question it asks: which file does CPython actually load?

## 6. Measurements from the post-L13 branches

All three post-L13 measurement branches returned. Nothing on them is landed. Their reports live on the branches.

**sp5 — typed tuple-return exception (branch `run7-sp5` 6b0d5ecae, `getting-better/run8-spike-typed-tuple-return.md`): GO.**
- **The capability.** A tuple return whose slots are all int / bool / string / real, and not all int, gets its own `exception Return_tup_<types>`. All-int tuples keep `Return_<arity>`.
- **The edit.** It sits in `_handle_return_stmt` (raise) and `_wrap_body_with_return_catch` (catch). The declaration comes from preamble.py, whose twin is `\trusted`.
- **Blast radius vs L13:**
  - corpus root 3275 / 3275 and pyref 2185 / 2185, **0 MOVED / 0 GONE / 0 APPEARED**;
  - mirror: **3 / 53 move** (statements, stmt_control_flow, pycsl).
- **Proofs under the spike:**

  | Proof | Goals Valid | Wall time |
  |---|---|---|
  | stmt_control_flow, whole file | 16326 / 16326 (+224) | 29,666 s, on a loaded machine |
  | statements `--fun _wrap_body_with_return_catch` | 1088 / 1088 | 514 s |
  | `--fun _handle_return_stmt` | 3534 / 3534 | 2,893 s |
  | `--fun _why3_typecheck`, with its `\trusted` removed | 761 / 761 | — |

  For `_why3_typecheck`, a true `\result` postcondition proves and a mutant fails (762 / 768).
- **Not run:** the whole-file statements.py proof (~10.5 h).
- **Run #8 cost:** ~17-19 h serial heavy time, or ~11 h wall with statements and stmt_control_flow in parallel. It converts one stub, `_why3_typecheck`.
- **Limit.** hval / record / union slots are not covered. `_rewrite_annotation_str` still needs the exception declared after the PyVal theory.

**u48 — refusal rules for the residuals (branch `run7-u48` e4e1bea94, `getting-better/run8-refusal-residuals.md`).** All four rules are in `_run_pipeline` (twin `\trusted`). Newly refused files, root / pyref / mirror:
- **R1** `PYCSL-R608-PYVAL-SLICE` (q05): 0 / 0 / 0.
- **R2** `PYCSL-R608-LAUNDER-OWN-RESULT-CLAUSE` (q06): 0 / 0 / 0. This is after narrowing; the first version over-refused 8 expected-PASS files.
- **R4** `PYCSL-CV14-STR-RFIND-RECEIVER-DROPPED`: 0 / 0 / 0.
- **R3** `PYCSL-CV14-STR-SLICE-NEGATIVE-BOUND`: **2 / 0 / 3**. It refuses corpus 0885 and 0887, and the verified mirror functions `expressions._strip_outer_parens`, `types._split_tuple_type` and `proof_axiom_allowlist.parse_lean_axioms_line`. Recommendation: MODEL the bound in `_handle_slice_access_expr` instead of refusing it.

None of the four is a live false proof today. **Proposed:** land R1 / R2 / R4 early in run #8 as one batch B. Their corpus and mirror diff is already 0 / 0 / 0, so they need only witnesses, planes and a battery.

The driver ran the fast planes on run7-u48 e4e1bea94 (all four rules): **59 / 62 green, 3 RED**. All three reds are expected and say what batch B must do:
- `check-untrusted-emitted` and `check-shadowed-selfcalls` are red because R3 refuses 3 mirror files, so those files are not emitted. So R3 must be split out of batch B (model the bound instead).
- `check-refusal-witness-coverage` is red because 9 raise sites are not demonstrated: the new codes have no census rows yet. Batch B needs corpus witnesses plus `_census_row` rows for each new code.

The log is in `scratchpad/run7/evidence/u48/fast-planes-driver.log`.

**cv15 — census seed (branch `run7-cv15` 3f00cac03, `getting-better/run8-census-seed.md`).**
- **One chain moved at L13.** pycsl.py's `_sha256_file` is now ONE link away: `Path(<str>)` falls to the generic `path_1`. It ranks first.
- **`type_of_batch`** closes TC-OK with its 2 measured links.
- **`_to_cache_payload`** needs a large second link: the `qualname_results` field is erased.
- **Receiver-dropping generic method fallback (`_handle_dotted_call`):** ~212 sites, all fresh-per-call. That makes them input-blind but not unsound. 9 of the sites are in verified mirror bodies (`str.count`, self-field `startswith`).

**Re-ranked run #8 order (replaces §3's table order):**

| # | increment | links |
|---|---|---|
| 1 | `_sha256_file` in pycsl.py | `Path(<str>)` |
| 2 | batch B: u48's R1 / R2 / R4 | 0 / 0 / 0 diff |
| 3 | batch A: `_why3_typecheck`, typed tuple Return | sp5: GO, ~11 h wall |
| 4 | `type_of_batch` | 2 links |
| 5 | model the negative slice bound | expressions.py re-proof |
| 6 | receiver-reading `str.count` / `rfind` / `startswith` | — |
| 7 | `_to_cache_payload` | — |
| 8 | `parse_format` | — |
| 9 | `_synthesize_block` | — |
| 10 | `bases_closure` | — |
| 11 | `subprocess.run` `cwd=` / `timeout=` extension | the shared first wall of six stubs |
