# Triage A8 — top-level driver + misc (READ-ONLY probe)

Group: `pycsl.py` + `exception_model.py` + `proof_axiom_allowlist.py` + `errors.py` + `ir_schema.py`.
Classified from the LIVE bodies in `src/pycsl/…` (mirror stubs carry the verbatim body + a preceding
`#@ \trusted`). Method: static pattern-match against the recognizer stack + one confirming spot-check.

**Actual stub count = 49, not 52.** `pycsl.py` has **36** `\trusted` markers, not 39 — the extra 3
"trusted" hits are string literals inside argparse `--help` text (lines 255/260/327), not stubs.
Per-file: pycsl 36, exception_model 6, proof_axiom_allowlist 4, errors 2, ir_schema 1.

---

## pycsl.py  (36 stubs) — ALL hard-architectural
The CLI driver. Every stub is I/O / subprocess / argparse / orchestration OR untyped-JSON-record
dict modeling. None convert with a bounded recognizer; all need a real modeling feature or are
irreducibly I/O-bound. Summarized by sub-family:

| stub(s) | bucket | reason |
|---|---|---|
| _parse_args | hard-architectural | argparse.ArgumentParser construction |
| _make_temp_mlw_path, _generate_rocq_obligations, _sha256_file, _find_coqc, _find_why3_coq_lib, _check_rocq_proofs, _proof_reference_mlw_name | hard-architectural | tempfile / hashlib / shutil / os.path.* / os FS-probing / file I/O (external stdlib syscalls) |
| _why3_typecheck, _run_why3_prove, _dispatch_provers, _finalize, _run_vacuity_gate, _probe_one, _run_proofs, _gate_vacuity_then_succeed, _run_audit_mode, _run_pipeline, main | hard-architectural | subprocess.run(why3/coqc) + ThreadPoolExecutor + sys.exit orchestration; call the whole Module1-6 pipeline |
| _record_answer, _record_is_valid, _record_key, _merge_records_best_of_n, _synthesize_block, _synthesize_legacy_text, _residual_selectors_from_records, _is_false_goal, _json_goal_records, _parse_why3_json | hard-architectural | untyped nested why3-JSON-record `dict.get(...)` chains with `or {}`/`or []` unions, heterogeneous tuple/list values, JSONDecoder.raw_decode; needs a typed JSON-record value model (the `else {}`-fallback DEFER row) |
| _parse_goal_blocks, _function_body_eqs | hard-architectural | regex `.match`/`.group` + `splitlines()` iteration accumulating `List[Tuple[str,int]]` (list-of-tuple growth) |
| _build_soundness_report, _print_soundness_report | hard-architectural | IR-func reflection + set ops (`& trusted_names`) + heterogeneous dict-list building + `_json.dumps` I/O |
| _resolve_runtime_config | hard-architectural | reads agents-config.json (open + `_json.load`) + `str.split(",,")` list-comp |
| _check_goal_conservation | hard-architectural | ordering: depends on `_parse_goal_blocks` (regex/list-of-tuple) + raises _MergeConservationError |
| __init__ (_MergeConservationError) | hard-architectural | `super().__init__` on Exception + f-string; external base |

## exception_model.py  (6 stubs)
| stub | bucket | reason |
|---|---|---|
| bases_closure | hard-architectural | set-local build (`seen=set()`, `.add`, list `.extend`) + `frozenset` return + `EXCEPTION_BASES.get` on a module-const `Dict[str,Tuple[str,...]]` (dict-of-tuple values) — ≥2 unmodeled features |
| handler_catches | hard-architectural | `in bases_closure(x)` — depends on a set-returning stub (ordering) + frozenset membership |
| subclasses_of | needs-recognizer:set/frozenset modeling | `frozenset(c for c in candidates if …)` — set-comprehension over untyped iterable |
| triggers_for | hard-architectural | module-const `Dict[Tuple[str,Opt[str]], List[Trigger]]` `.get(key, [])` — tuple keys + list-of-tuple values |
| predicate_definitions | hard-architectural | `PREDICATE_LIBRARY.items()` iteration + `Optional[set]` param membership + list-comp |
| all_phase1_exceptions | needs-recognizer:set/frozenset modeling | `sorted(KNOWN_EXCEPTIONS)` — frozenset iteration → array string |

## proof_axiom_allowlist.py  (4 stubs)
| stub | bucket | reason |
|---|---|---|
| is_rocq_assumption_allowed | needs-recognizer:module-const str-set membership | `name.strip() in ROCQ_KERNEL_AXIOM_ALLOWLIST` — SPOT-CHECKED: leaks `string expected int` (set unmodeled) |
| is_lean_axiom_allowed | needs-recognizer:module-const str-set membership | same shape over LEAN_…_ALLOWLIST — same feature |
| parse_lean_axioms_line | hard-architectural | `str.split(sep)`→array + list-comp over split + `in`/startswith/endswith/slice chain |
| parse_rocq_assumptions_block | hard-architectural | `splitlines()` iteration + `Tuple[bool, List[str]]` return + `startswith(tuple)` |

## errors.py  (2 stubs)
| stub | bucket | reason |
|---|---|---|
| message | hard-architectural | `super().__str__()` — external builtin Exception dispatch |
| as_dict | hard-architectural | heterogeneous dict literal (str fields + int `line`) + `self.message()` (depends on the super() stub); needs class as @mutable_state record |

## ir_schema.py  (1 stub)
| stub | bucket | reason |
|---|---|---|
| validate_ir | hard-architectural | IR-structure validation: set-difference on `dict.keys()` (`_REQUIRED_TOP - ir.keys()`), `isinstance(...).__name__` reflection, `enumerate` over list-of-dicts (IR nodes), `sorted(set)` — IR-node structural modeling |

---

## Per-bucket counts (this group, 49 stubs)
| bucket | count |
|---|---|
| trivial-leaf | **0** |
| needs-recognizer | **4** |
| hard-architectural | **45** |
| floor | 0 |

**Batch-convertible now (trivial-leaf): 0.**

## Feature fan-out (needs-recognizer only)
| feature | #stubs | example stubs |
|---|---|---|
| set/frozenset value modeling (§5 OPEN gap #2, extended to module-const sets: membership / iteration+sorted / set-comprehension) | 4 | is_rocq_assumption_allowed, is_lean_axiom_allowed, all_phase1_exceptions, subclasses_of |
| ↳ of which "module-const str-set membership" (`x in CONST_SET`) | 2 | is_rocq_assumption_allowed, is_lean_axiom_allowed |

## Dominant hard-architectural sub-families (NOT recognizer-reachable; each needs a real modeling feature)
| sub-family | ~#stubs | blocker |
|---|---|---|
| subprocess/why3/coqc + FS/tempfile/argparse/orchestration (pycsl.py CLI) | ~24 | irreducible I/O; the driver's job is to shell out — hard architectural / near-floor |
| untyped nested why3-JSON-record dict `.get` (`or {}`/`or []` unions, hetero tuple/list values) | ~10 | needs a typed JSON-record value model (the `else {}` DEFER row) |
| regex `.match`/`.group` + `splitlines()` list-of-tuple accumulation | ~3 | regex modeling + growable list-of-tuple |
| module-const dict-of-collection `.get` (tuple keys / list-of-tuple / dict-of-tuple values) | ~3 | value model beyond the flat constant-dict recognizer (triggers_for, bases_closure, predicate_definitions) |
| set-ops on `dict.keys()` + isinstance reflection over IR nodes | ~2 | IR-node structural model (validate_ir, _build_soundness_report) |
| `super().__str__` / `super().__init__` on Exception base | ~3 | external builtin base dispatch (errors.message/as_dict, _MergeConservationError.__init__) |

## Notes / honesty
- No stub in this group is a cheap win. This is expected: `pycsl.py` is the CLI/proof-orchestration
  driver (self-annotate-sync explicitly warns its functions are argparse/I/O-bound), and the four misc
  modules are constant tables + set/frozenset helpers + Exception base methods.
- The only bounded, leverage-positive feature here is **set/frozenset value modeling** (4 stubs, and it
  is already the recorded §5 OPEN gap #2). Building it would also unblock `bases_closure`/`handler_catches`
  partially, but those additionally need dict-of-tuple modeling.
- Spot-check performed (1): un-trusted `is_rocq_assumption_allowed` → L3-tc FAIL `string expected int`
  at the `in CONST_SET` site, confirming the set-membership leak. Reverted; git clean.
- No conversions, edits, or commits made (read-only). One temporary patch applied for the spot-check
  and reverted from backup.
