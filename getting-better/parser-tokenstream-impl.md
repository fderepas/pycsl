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

## CHEAP-DRAIN pass (2026-07-25, Phase-2 executor) — count 914 → 912

Marker-removal drain of the ~66 `\trusted` methods in the mirror. **Result: 2 converted; the
string/list-returning cluster is BLOCKED by two live EMITTER gaps (deferred → (B)).**

**CONVERTED (+0 machinery, verbatim live bodies, mirror-only, byte-inert by construction):**
- `_Tok.__repr__` → `return f"_Tok({self.type}, {self.string!r})"` (`!r` lowers cleanly; `assigns \nothing`, reads fields only).
- `_Tok.__init__` → field-init body un-trusted (`assigns \nothing` sound for a fresh constructor).

**FAILED-and-stay-trusted + the exact blocker (this scopes the deferred (B) vein):**
- **Whole string/list cluster** — `_parse_qualname`, `_parse_dotted_path`, `_parse_dotted_path_list`,
  `_parse_act_names`, `_parse_opt_except`, `_parse_mixin_type/_param/_params/_method_sig`,
  `_parse_mutex_expr_str`, `_parse_variant_def`, `_parse_compose_from`, `_parse_conforms_to`, …:
  **EMITTER GAP #1 — no default-argument filling for method calls.** Every one calls
  `self.expect_name()` (no arg; 74 such call sites live). `expect_name(self, val=None)` emits as a
  2-param `let (self)(py_val:string)`, so `self.expect_name()` lowers to a PARTIAL application
  (`string -> string`, type error). Working around it in the mirror (`expect_name("")`) is exactly
  the forbidden default-sentinel massage (cf. the prohibited live `peek()`→`peek(1)`), so left trusted.
- **`parse`** — `node = self._parse_contract(); … return node`: **EMITTER GAP #2 — local-var type
  inference from a unit-returning trusted call.** The emitter defaults the local `node` to `int`
  (`let node = ref 0`) but trusted `_parse_contract` returns `()`, so `node := ()` is a type error.
- **`parse_node_contracts`** — `for contract_str in raw_contracts: parsed_nodes.append(...)`:
  **EMITTER GAP #3 — no auto termination-variant for a `for … in LIST` loop outside a
  `@mutable_state` class / the psl-loop.** The loop index (`_idx_contract_str`) is emitter-internal
  and unnameable, so no explicit `#@ loop variant` can be written; the two VCs (`termination`,
  `index in array bounds`) time out. (`_Tok.__init__` in the same batch proved; only these 2 goals failed.)
- **`_parse_impl_rhs` / `_parse_or_rhs` / `_parse_and_rhs`** — delegate to `_parse_quantifier` (record,
  trusted); their own contract needs `ensures self.i >= \old(self.i)` but the quantifier's trusted
  contract gives no monotonicity — strengthening a trusted stub's *assumed* ensures is a trust-widen
  (needs reviewer), not cheap.
- **`_try`** (higher-order, callee-frame boundary), **`_err`** (raises; deliberately left trusted, and
  making it diverge would perturb the already-converted `expect_*` proofs), **`_grab_reviewer_id`**
  (`self.source` + `_re.match`), **`_lex_contract` / `_ContractParser.__init__`** (char-lexer boundary),
  **`_csl_to_str`** (recursive CSL dispatch): all pre-existing (A)/(B) boundaries.
- **All remaining `_parse_*`** construct CSLNode records → family (B) (needs the `emit_ir`-variant coupling).

**Verdict:** the pure marker-removal drain is EXHAUSTED at 2 wins. The next parser cut is gated on
EMITTER work (default-argument filling; for-in-list termination variant; unit-local inference) — a
deliberate (B) build, not a cheap win. Gate battery: whole-file proof SUCCESS 0-unproven (foreground);
`git diff` mirror-only (src/pycsl clean); vacuity exit 0 (no new erasure); mirror-check 52/52; drift 2;
ledger 3 (untouched).

## DEFAULT-ARG-FILLING build (2026-07-25, Phase-2 emitter executor) — GAP #1 BUILT; count 912 (no stub converts standalone)

**Feature (commit `fc43f946`):** extended 1111-spec R7 default-argument filling to the SELF-METHOD
path (`module6_whyml/expressions.py::_handle_dotted_call`). A same-class `self.<m>(...)` call passing
FEWER positional args than the callee's arity now fills the missing trailing params from the callee's
positional DEFAULTS — keyed on the MANGLED callee name (`<self_type>__<m>`, the `_module_method_*`
maps' method key), a `None` default on a non-int param filled at its faithful zero (Gap 3), a param
with no default left a shortfall. `self.expect_name()` on `expect_name(self, val=None)` NO LONGER
lowers to the partial application `(<c>__expect_name self) : string -> string` (L3-tc error, the
observed `.mlw` line-972 failure); it lowers to the TOTAL `(<c>__expect_name self "")`.

**GATE S (all green):** FULL corpus byte-diff **0** (812/812 both sides vs detached-HEAD worktree
baseline) → feature corpus-inert. MUTATION TEST **PASS** (filled `""` → `"__MUT__"` moves the emitted
`.mlw`; not a facade). §10c shared-emitter check: **3 mirror files** change emission
(`pure_ast`/`statements`/`stmt_control_flow`) — ALL pure abstract-op-arity widening on UNCONSTRAINED
`val`s (no param-referencing ensures, verified by grep) → logically **proof-neutral**; `pure_ast`
whole-file SUCCESS, `statements` 3/5 changed fns `--fun` SUCCESS, both heavy files L3-tc ✓ (the other 2
+ `_handle_match_stmt` are heavy but provably-neutral; driver re-verifies uncapped). The feature is
STRICTLY MORE FAITHFUL: it unifies `fill(self, text='')` from two independent oracles
(`self_fill_0 ()` / `self_fill_1 <arg>`) into one (`self_fill_1`). Vacuity exit 0; mirror-sync exit 0.

**CERTIFIED-BOUNDARY — default-arg filling converts ZERO parser stubs STANDALONE.** A full census of the
32 `self.expect_name()`-callers (`ast.unparse` scan) shows EVERY one hits a SECOND, independent emitter
gap on top of GAP #1:
- **Optional[_Tok]-truthiness-in-condition** (`while`/`if self.accept_op(X):`) — `_parse_qualname`,
  `_parse_dotted_path`, `_parse_dotted_path_list`, `_parse_act_names`, `_parse_variant_def`,
  `_parse_compose_from`, `_parse_conforms_to`, `_parse_mixin_type/_param`. `accept_op` returns
  `Optional[_Tok]`, emitted as a union `_union_accept_op_N`; the loop/if condition lowers as
  `(... ) <> 0` (int compare) → L3-tc "type `_union_accept_op_N` expected int" (observed `_parse_qualname`
  `.mlw` line-973). This is the SMALLEST next feature — it alone (over the now-built default-arg) frees
  the pure-string `_parse_qualname`/`_parse_dotted_path` sub-cluster.
- **GAP #2 record/unit-local from a trusted `_parse_*` call** — `_parse_mutex_expr_str` (tested
  empirically: `index = self._parse_expr()` → `.mlw` "type () expected int"), `_parse_footprint`,
  `_parse_happy`, and every `parse_call=True` method.
- **family (B) node construction / list-append** — the `return <CamelCase>(...)` / `.append(...)` methods.

So GAP #1 is a NECESSARY enabling capability for the entire parser string/list cluster but SUFFICIENT for
none of it. Reopen order: (1) Optional-truthiness-in-condition [unblocks `_parse_qualname`/`_parse_dotted_path`
first, +default-arg], (2) GAP #2 record/unit-local inference, (3) family-B emit_ir variants. Gate battery
this run: corpus byte-diff 0; `git diff` src/pycsl = the 28-line feature only; vacuity exit 0; mirror-sync
exit 0; count 912; drift 2; ledger 3 (untouched).
