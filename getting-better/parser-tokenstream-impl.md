# parser-tokenstream-impl.md — Gate-S spike verdict (token-level `_ContractParser` cluster)

**Spike executor run, 2026-07-25.** Target: the token-level `_parse_*`/`cur`/`peek`/`advance`/
`expect_*` cluster in `src/self-annotate/src/frontend/Module2_Parser.py`. Canonical count at start
**917**; at exit **915** (−2, `expect_op` + `expect_bs` converted). Drift 2, ledger 3.

## VERDICT: SPIKE PASSES — subsystem BUILDABLE (WALL BROKEN for the state-only sub-family)

The prior census (`driver-progress.log`, "RUN FLOOR CONFIRMED … Module2_Parser 69 = int-AST
boundary", "parser token-stream model = new subsystem needed") was **too pessimistic**. The concrete
token-stream model is **already built and proven** — a prior `parser-primitives-wall` campaign
(see `parser-primitives-wall-impl.md`) landed it. This spike converts 2 more methods with **zero new
machinery, no new axiom, no certificate touch**, and maps the remaining cluster into three exact
sub-families.

## The concrete model (ALREADY IN THE TREE — not built by this spike)

- `_Tok` record `{ py_type: string; _tok_string: string; _tok_start: int }` (mirror `.type`→`py_type`,
  `.string`→`_tok_string`).
- `_ContractParser` is a `@mutable_state` stateful record: `mutable toks: array _tok` + `mutable i: int`
  (the cursor). `self.toks[j]` → `Array.get`; `self.i += 1` → `i := i+1`.
- **Class invariants (already present, lines ~808-818):** `0 <= self.i`, `self.i < \length(self.toks)`,
  `\length(self.toks) >= 1`, and the **EOF-sentinel** invariant
  `self.toks[\length(self.toks)-1].py_type == "EOF"` — this is what makes the `while self.at_op(...)`
  loops terminate (variant `\length(self.toks) - self.i`).
- **Already CONVERTED & proving (non-trusted):** `cur`, `peek`, `advance`, `at_op`, `at_name`, `at_bs`,
  `at_eof`, `accept_op`, and the ENTIRE precedence chain `_parse_implication` → `_parse_logical_or`
  → `_parse_logical_and` → `_parse_equality` → `_parse_comparison` → `_parse_term` → `_parse_factor`
  (each proves `ensures self.i >= \old(self.i)` with the EOF-sentinel loop invariant + the
  `\length - i` variant). `Module2_Parser.__init__`.

## Census of the 69 (now 67) `\trusted` stubs in the file

- **CHAR-level lexer (EXCLUDED per task):** `_lex_contract` — **1**. Iterates the source string
  char-by-char (string-char-op boundary).
- **Non-cursor helpers (out of scope):** `_Tok.__init__`, `_Tok.__repr__`, `_csl_to_str`,
  `Module2_Parser.parse_contract`, `Module2_Parser.parse_node_contracts`, `_ContractParser.__init__`
  (lexer-coupled — sets `self.toks` from `_lex_contract`) — **6**.
- **TOKEN-LEVEL cursor cluster (the target): ~62** — read/advance over `self.tokens`/`self.pos`.

### The token-level cluster splits into three sub-families

- **(A) State-only / already-modeled-return → CONVERT NOW, zero new machinery (~5-7 methods).**
  Read the cursor and return either a `_Tok`, a token field `.string`, or delegate to an
  already-converted method. **DEMONSTRATED THIS SPIKE: `expect_op` (→`_Tok`), `expect_bs` (→`string`).**
  Identified further cheap follow-ons (same shape, NOT yet done — for the driver to fund):
  `expect_name` (→`string`; trickier: `val=None` default + ternary f-string), `parse` (delegates to
  `_parse_contract`, `at_eof`, `_err`), `_grab_reviewer_id`.

- **(B) Node-constructing `_parse_X` → BUILDABLE but COST (§10.5 coupling per node family, ~50-55
  methods).** Each builds a distinct `CSLNode` subclass (e.g. `_parse_membership` → `CSLIn`/`CSLNotIn`).
  The emitter already RECOGNIZES these constructions by name and lowers them to a record literal
  (`{ cslin_element = …; cslin_collection = … }`), but the corresponding `emit_ir` variant is not yet
  defined → L3-tc type error. Converting them faithfully requires **adding the node's `emit_ir` variant
  (the well-established `IrBinOp` precedent — the ADT comment already documents dozens of such 1-/2-/3-
  child additions) + a co-landing axiom-free certificate update + coqchk (ledger 3).** No new axiom
  needed (structural variants, same as `IrBinOp`). This is the bulk of the cluster and is the
  fundable full-build.

- **(C) Hard boundaries (leave `\trusted`):** `_try` (higher-order — takes a callee `fn`, backtracks
  `self.i = saved`; its true frame is `{self.i} ∪ frame(fn)`); `_err` (raises `_ContractSyntaxError` —
  works fine as a trusted `val`, `assigns \nothing`); `_ContractParser.__init__` + `_lex_contract`
  (char-lexer boundary). **~3-4 methods.**

## What this spike DID (proof-of-reachability, full gate battery)

Converted **`expect_op`** (`val:str`→`_Tok`) and **`expect_bs`** (`val:str`→`string`), both verbatim
ports of the live bodies:
```
def expect_op(self, val: str) -> _Tok:
    if not self.at_op(val): self._err(f"expected {val!r}")
    return self.advance()
```
Faithfulness fixes required (all faithful, mirror-sync-clean): annotate `val: str`, return `-> _Tok`/
`-> str`, and type the trusted `_err` stub's `msg: str` (it stays trusted). F-strings lower cleanly
(`str_concat_op` + arg). Emitted bodies are **non-vacuous**: real `at_op`/`at_bs`/`advance` over
`self.toks`/`self.i`, no int-hash / `any_1` / opaque.

- **Whole-file proof:** SUCCESS, 0 unproven (`--import-path src/pycsl`, foreground). NOTE: `--fun` is
  spuriously INCOMPLETE here — abstract-`val` dependencies are emitted with `ensures self.i >= old`
  but WITHOUT a `writes {self.i}` clause, so a caller's declared write "does not happen"; whole-file
  emits converted deps as `let` bodies and is authoritative.
- **Mutation test (§10.8):** DECISIVE. Mutating `at_op`→`at_name` and `advance`→`cur` changed the
  emitted `.mlw` exactly (both call sites) → faithful emission, not a facade.
- **Corpus byte-diff:** 0 **by construction** — `git diff HEAD -- src/pycsl` is EMPTY (only the mirror
  `.py` changed; the emitter is byte-identical and does not import `src/self-annotate`).
- **Mirror-check:** 52/52 in sync. **Vacuity (`--check-vacuity`):** clean, no new erasure.
- Count 917→915, drift 2, ledger 3, formal-semantics untouched (no cert needed for family A).

## Reopening capability for family (B)

Fund the emit_ir-variant coupling: for each node family the `_parse_*` methods construct
(`CSLIn`/`CSLNotIn`, and the CSL-AST nodes the other rules build), add the variant to `emit_ir`
(IrBinOp precedent), extend the size/helper folds, co-land the axiom-free cert + coqchk (ledger 3).
Then the ~50-55 family-B methods convert as verbatim ports. `_try` needs a higher-order-frame feature
(or stays boundary).
