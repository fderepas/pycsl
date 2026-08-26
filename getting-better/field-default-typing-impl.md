# `field-default-typing-impl.md` — L10 part 1: element-type-aware record field defaults

Gate P: spike-first, refutation exit, three-L-plane battery, honest scope.

## The defect (located, verbatim)
`src/pycsl/module6_whyml/expressions.py::_call_record_constructor` -> nested `_field_default` (~8515):
```python
def _field_default(fn: str) -> str:
    ft = field_types.get(fn, "int")
    if ft in ("list", "array"):
        return f"(Array.make {rec_info['defaults'].get(fn, 0)} 0)"   # (A) element-BLIND: always `int`
    if ft in ("dict", "set", "frozenset"):
        return "(const (None: option int))"
    return f"{rec_info['defaults'].get(fn, 0)}"                       # (B) `string` falls to the int fallback
```
- **(A)** a `List[str]` field defaults to `(Array.make N 0)` = `array int`, against a field typed
  `array string`. Measured on `NoExceptionDecl(exceptions=[], all_form=True)`:
  `This expression has type array int, but is expected to have type array string`.
- **(B)** a *defaulted string* field emits `0`. Measured on `HappyProperty.context: str = "writing"`:
  `This expression has type int, but is expected to have type string`.

A previous bounded spike already confirmed (A) is fixable in ~3 lines and that fixing it cleanly
produced `(Array.make 0 "")`.

## STEP 0 — SPIKE, and the PAYOFF GATE that decides whether anything lands
Fix (A) and (B) with element-type-aware defaults, then **measure how many `\trusted` stubs actually
convert as a result**. Candidates to port-and-measure (verbatim live body, `--no-proof --keep-mlw`,
then revert each):
- `Module2_Parser::_ContractParser._parse_no_exception`
- `Module2_Parser::_ContractParser._parse_happy_targets`
- `Module2_Parser::_ContractParser._parse_happy`
- `Module2_Parser::_ContractParser._parse_contract`
- any other stub your own quick census says constructs a record with a defaulted string or a
  `List[str]` field

**PAYOFF GATE — this is the refutation exit.** If, with (A)+(B) applied, **ZERO** stubs reach a
passing L3-tc + whole-file proof, then **REVERT EVERYTHING AND LAND NOTHING.** A capability that
converts no stub is live-source churn with corpus byte-diff risk and no payoff; record it as
"built, measured, yield 0, reverted" with each candidate's remaining first blocker. That is a
FULLY SUCCESSFUL outcome — I want the measurement, not a diff.

**Known stacked blockers you will hit (do NOT fight them):**
- `_parse_no_exception` also needs a `Return <record>` exception variant for its EARLY RETURN. That
  is a **Why3 TYPE REJECTION** as records are currently emitted (`mutable` + `array` fields):
  driver oracle says `The type of top-level exception Return_record has mutable components`, and
  the proven sufficient condition is an **immutable + `seq`-backed** record (immutable alone is NOT
  enough — `array` is itself mutable). That is a separate capability. If `_parse_no_exception` stops
  there, REFUTE it and move on.
- `_parse_happy_targets` / `_parse_happy` are additionally blocked by the `Optional[X]` value model
  (`None` -> `0` against `emit_ir`/`string`/`seq` fields). Separate capability. REFUTE and move on.

## STEP 1 — if and only if >= 1 stub converts: the full battery
**Provers — the repo default is BROKEN here** (stale `Alt-Ergo,2.6.2,` pin vs installed 2.6.3 =>
bare runs go Z3-only and report FALSE "unproven"):
```bash
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <file> --import-path src/pycsl --provers "Alt-Ergo,2.6.3,,Z3,4.13.3,"
```
1. Whole-file proof of every mirror file you changed = 0 non-Valid.
2. **Corpus byte-diff — HARD GATE, `src/pycsl` is touched and `_field_default` serves EVERY corpus
   record construction.** Worktree-at-HEAD baseline, repo `.venv` symlinked, ONE foreground sweep per
   side, read the `emitted N` line on BOTH sides and assert equal and NONZERO (**812**), `diff -rq`
   exit 0. If non-zero, M1 applies: the diff must be EXACTLY the intended correction AND every
   affected program must re-prove — otherwise tighten the gate until it is 0.
3. §10c importer sweep: L3-tc EVERY mirror file, not just the one you changed (52 expected).
4. Fidelity baseline (both scripts exit 1 — ACCEPTED, do not "fix"): sync = exactly 2 DIVERGED
   (`expressions.py::_handle_var_expr`, `stmt_control_flow.py::_handle_for_stmt`); mirror-check =
   exactly 3 drifted (`expr_ghost_collections`, `statements`, `stmt_control_flow`), and your file
   must NOT appear.
5. Ledger == 3; no new axiom; no new *trusted* val.
6. Vacuity: `bin/check-emitted-vacuity.py --emit`, assert population **52**. **HEAD baseline is
   EXIT=1** with 6 known gated + 2 input-blind + 1 pre-existing `Module3_Weaver::pycslweaver___const_int`.
   Your gate is NO NEW finding beyond those. (Without `--emit` it reuses existing `.mlw`; after a
   cleanup that means a population of ZERO and a FALSE EXIT=0.)
7. Count: `grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l`, currently **671**.
