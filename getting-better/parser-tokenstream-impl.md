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

## OPTIONAL-TRUTHINESS-IN-CONDITION build (2026-07-25, Phase-2 emitter executor) — GAP #1b BUILT; count 912 (no stub converts standalone)

**Feature (this commit):** extended `module6_whyml/expressions.py::_to_bool` (the boolean-context
lowering used by every if/while guard + and/or/not operand) so an `Optional[OBJECT]` `<e>` (a
record-payload option — `_Tok`, NO `__bool__`) in CONDITION position lowers to the is-Some
discriminant `(match <e> with <None-arm> -> false | _ -> true end)` instead of the int `(<e> <> 0)`
coercion (the observed `_parse_qualname` `.mlw` line-973 `_union_accept_op_9` vs `int` L3-tc error).
New helper `_optional_object_union_none_ctor(ir_expr)` recognizes two shapes: (a) a `Var` whose
symbol-table type is a `_union_*`, (b) a same-class `self.<m>(...)` `Call` whose synthesized
`-> Optional[τ]` return union `_union_<m>_<idx>` is resolved by the METHOD-SCOPE prefix from
`_variant_types` (the cross-reference `_module_method_return_types` map DEFAULTS a union return to
`int`, so it can't serve this lookup). **Record-payload gate** (single Some-arm whose payload names
a declared `_record_types` class) DEFERS `Optional[int]`/`Optional[str]` (falsy-zero/empty — a
different rule), per task scope.

**GATE S (all green, feature corpus-inert):** FULL corpus byte-diff **0** (812/812 vs detached-HEAD
`b7a8da8e` worktree baseline) → M1-clean, no verdict re-run needed. §10c shared-emitter: ALL 23
emitting self-annotate MIRROR files byte-IDENTICAL baseline-vs-feature (incl. Module2_Parser) → no
changed emissions ANYWHERE. MUTATION TEST **PASS**: flipping the discriminant sense
(`-> false | _ -> true` → `-> true | _ -> false`) moved the emitted `_parse_qualname` while-cond in
the `.mlw` — not a facade. Vacuity `--emit` exit 0; mirror-check 52/52; sync.py output byte-identical
to baseline (no new drift). count 912; drift 2; ledger 3 (untouched).

**CERTIFIED-BOUNDARY — Optional-truthiness converts ZERO parser stubs STANDALONE (a THIRD gap found).**
The task's reopen note expected this feature (+default-arg) to free `_parse_qualname`/`_parse_dotted_path`.
It does NOT, because the sole `accept_op` guard is used two ways, each with an INDEPENDENT second/third
blocker:
- **`while self.accept_op(X):` (qualname, dotted_path, dotted_path_list, act_names, compose_from,
  conforms_to, variant_def, mixin_type/params, …):** the loop TERMINATION variant
  `\length(self.toks) - self.i` cannot discharge. The strict per-iteration increment happens IN THE
  GUARD (`accept_op` advances when it matches), but `accept_op`/`expect_name` both `ensures True`, so
  the modular caller sees no progress (whole-file proof: 3 goals unproven = variant + the `self.i >=
  \old` / bounds loop invariants). Fixing it needs `accept_op` to expose
  `ensures \result != None ==> self.i > \old(self.i)` — but `\result != None` on a union return
  lowers in a SPEC/formula to `(result <> 0)` (union-vs-int L3-tc error): the SAME union-vs-None gap
  but in `\result`/BinOp-`!=` position, NOT condition position. `_union_none_ctor_for` (the existing
  spec union-None handler) only resolves a symbol-table `Var`, never `\result`. This is **GAP #1c =
  spec-position `\result` union-None discriminant** — a distinct emitter feature, DEFERRED (scope:
  build only condition-position). Progress: `advance` already exposes `\old < len-1 ==> +1`, so once
  GAP #1c lands, `accept_op`'s strict-on-Some ensures is a provable in-scope MIRROR annotation and the
  pure-string qualname/dotted_path convert; the list ones still also need family-B (list-append).
- **`if self.accept_op(X):` (mixin_param, ghost, for_block, quantifier, ctor \is_ctor/\payload):**
  the Optional-truthiness `if`-guard needs NO variant and lowers cleanly with THIS feature, but every
  then-branch calls a trusted `_parse_expr`/`_parse_mixin_type` (unit return, GAP #2 unit-local in an
  f-string/value) and/or constructs a `CSLNode` (family-B). Blocked on GAP #2 / family-B, not on this.

So the necessary-but-insufficient pattern of the default-arg run repeats one layer deeper. Revised
reopen order for the parser string cluster: (1) **GAP #1c spec-`\result`-union-None** [with #1b+default-arg,
frees `_parse_qualname`/`_parse_dotted_path` — the smallest next cut], (2) GAP #2 unit-local inference
[frees the `if accept_op` + trusted-`_parse_expr` methods], (3) family-B emit_ir variants + list-append
[the bulk]. Gate battery this run: corpus byte-diff 0; mirror emission 23/23 identical; `git diff`
src/pycsl = the ~60-line feature only; vacuity exit 0; mirror-check 52/52; no new drift; count 912;
drift 2; ledger 3 (untouched); formal-semantics untouched; zero scope-creep live changes.

## GAP #1c BUILT + parser-string cluster OPENED (2026-07-25, Phase-2 executor) — count 912 -> 910 (2 REAL conversions)

**VERDICT: the bounded convert-or-BOUNDARY shot CONVERTS.** GAP #1c is the last gap the
`while self.accept_op("."):` pure-string sub-cluster needed, and it is a SMALL emitter feature
(24 lines) + two faithful mirror contract strengthenings. Two stubs converted, whole-file proven.

**GAP #1c feature (commit `5c8b83f4`, `module6_whyml/expressions.py::_union_none_ctor_for`):**
extended the spec union-None handler so a `\result` operand (IR `type == "Result"`) whose
`_func_return_type` is a synthesized `_union_*` resolves the nullary `Arm_*_None` ctor. `\result
!= None` / `\result == None` in an `ensures` of an `-> Optional[<object>]` method now lowers to the
is-None ctor DISCRIMINANT `(not (result = Arm_9_None))` instead of the `(result <> 0)` int coercion
(the observed union-vs-int L3-tc error). The spec/formula-position analogue of #1b — #1b handles
condition position (`_to_bool`), #1c handles BinOp-`!=`/`==`-in-spec (`_union_none_ctor_for`).
Corpus byte-diff 0 (812/812); the ENTIRE mirror has exactly one `\result`/None spec (accept_op), so
the feature's emission surface is provably confined to that one method. Mutation test PASS (`!=`->`==`
flips the emitted discriminant). Vacuity 0; drift 2; ledger 3.

**The stacked-gap chain, fully resolved for the pure-string sub-cluster (3 enabling + 1 feature):**
- default-arg filling (#1a, `fc43f946`) — `self.expect_name()` -> total application.
- Optional-truthiness-in-condition (#1b, `165d6a82`) — `while self.accept_op(".")` guard truthiness.
- GAP #1c (`5c8b83f4`) — `accept_op`'s `\result != None` strict-increment ensures lowers in spec.
- **accept_op contract** (mirror, `b03b6ae0`): `ensures \result != None ==> self.i > \old(self.i)`
  (strict increment on match — EOF-sentinel: at_op=>OP=>not-EOF=>i<len-1=>advance +1) AND `ensures
  self.i >= \old(self.i)` (the None branch is where the loop EXITS; without a lower bound there the
  exit guard-eval havocs self.i and the postcondition fails — this was the "4th blocker" the REFUTES
  route anticipated, resolved by a faithful monotone-in-both-branches ensures, NOT a 4th feature).
- **expect_name contract** (mirror, `b03b6ae0`): `ensures self.i >= \old(self.i)` — the loop BODY
  helper must not decrease self.i (only advance moves it, monotone). Same monotonicity the
  expression-chain RHS helpers (`_parse_impl_rhs`, ...) already carry.

**CONVERTED (verbatim live ports, whole-file proof SUCCESS 0-unproven each, foreground):**
- `_parse_qualname` (`b03b6ae0`, 912->911) — `name=expect_name(); while accept_op("."): name+="."+expect_name(); return name`.
- `_parse_dotted_path` (`92e3b8dc`, 911->910) — identical shape over `path`.

**Reachable cluster EXHAUSTED at 2 with this machinery.** The remaining `while self.accept_op(X):`
methods (`_parse_dotted_path_list`, `_parse_act_names`, `_parse_variant_def`, `_parse_compose_from`,
`_parse_conforms_to`, ...) all build LISTS (`names.append(...)` / `paths.append(...)`) = family-B
(list-append), or construct CSLNode records = family-B (emit_ir variants). Reopen order for the rest:
(1) family-B list-append + emit_ir node variants [the bulk], (2) GAP #2 unit-local for the trusted
`_parse_expr`-calling methods. GAP #1c is banked and reusable for any future `-> Optional[<object>]`
strict-monotonicity ensures.

## GAP #2 BUILT + parser mixin-sig cluster CONVERTED (2026-07-25, Phase-2 executor) — count 910 -> 908 (2 REAL conversions)

**VERDICT: the bounded convert-or-BOUNDARY shot CONVERTS.** GAP #2 (unit-local type
inference) is a SMALL, corpus-inert emitter completeness fix, and it converts the two
string-returning mixin-signature methods that were blocked only by their trusted `-> str`
deps emitting `: unit`.

**Root cause (empirically pinned on `_parse_mixin_method_sig`):** the emitter ALREADY
types a local assigned from a `-> str` self-method call as `string` (`_collect_str_call_result_locals`)
and a `-> "ExprIR"` self-call local as `emit_ir` (`_collect_emit_ir_result_locals`). The
gap was on the CALLEE side: a `\trusted` `-> str` stub with a bare `pass` body yields
`find_return_type -> "unit"`, and the `ann == "str" and return_type == "int"` overrides in
BOTH `_compute_return_type` (the main `val` return type) AND `_build_method_return_type_map`
(the `self.<m>(...)` abstract-`val` at the call site) only fire on `int`, never `unit`. So
the trusted stub's two emitted `val`s (`_contractparser___parse_mixin_type` and the
synthesized forward-decl `self__parse_mixin_type_0`) announced `: unit`, and the converted
caller's `ret := (self__parse_mixin_type_0 self)` (with `ret : string`) failed L3-tc
("type () expected string"). The `-> "ExprIR"` branch had ALREADY been extended to cover
`"unit"` (the node-ctor trusted-stub case); the primitive `str` branch had not.

**Feature (commit `ba2777da`, `module6_whyml/functions.py`):** extend BOTH str-branches with a
`return_type/ret == "unit" and func.get("trusted")` disjunct — the string-return sibling of
the `-> "ExprIR"` unit-stub → `emit_ir` promotion. Gated on `func["trusted"]`: a real corpus
`-> str` function has a return statement so `return_type`/`ret` is never `"unit"` — provably
byte-inert. FULL corpus byte-diff **0** (812/812 vs detached-HEAD `2ea5920e` worktree).
MUTATION TEST **PASS**: mapping the target type `string`→`real` moves BOTH the call-site
abstract `val self__parse_mixin_type_0 () : real` AND the main `val ... : real` in the emitted
`.mlw`, and L3-tc then fails — the emission is load-bearing, not a facade. §10c: exactly **2**
trusted `-> str` unit-body stubs exist mirror-wide (both in `Module2_Parser`, the two deps I
annotated), and a same-mirror-source 52/52 emission sweep (baseline emitter vs feature emitter)
shows **ONLY `Module2_Parser.mlw` changes** → the feature's emission surface is confined to the
one file proven whole-file. Vacuity exit 0 (no new erasure). Feature converts **0** stubs
standalone (enabling capability).

**CONVERTED (verbatim live ports, whole-file proof SUCCESS 0-unproven each, foreground):**
- `_parse_mixin_method_sig` (`5ae4be79`, 910→909) — `params = self._parse_mixin_params(); ret =
  self._parse_mixin_type(); return f"({params}) -> {ret}"` (params is an Optional[str] local:
  `params = None` then a conditional string self-call).
- `_parse_mixin_param` (`2c912843`, 909→908) — `if self.accept_op(":"): return f"{name}:
  {self._parse_mixin_type()}"; return str(name)` (f-string segment from a `-> str` self-call +
  `str(name)` on a string local).

Both enabled by faithful `-> str` return annotations on the two **still-`\trusted`** deps
`_parse_mixin_type` / `_parse_mixin_params` (each builds a LOCAL LIST → family-B, so they stay
trusted — the annotation just makes the trusted interface precise, the pattern the
`accept_op`/`expect_name` ensures-strengthenings already established).

**Reachable str-local cluster EXHAUSTED at 2. The residual is family-B or a hard boundary:**
- `_parse_mixin_type` / `_parse_mixin_params` / `_parse_dotted_path_list` / `_parse_act_names` /
  … build a LOCAL LIST (`args.append(...)`, `', '.join(args)`) = family-B (list-append).
- `_parse_mutex_expr_str` = **CERTIFIED BOUNDARY**: its `index = self._parse_expr()` callee
  `_parse_expr` is an UN-ANNOTATED trusted stub → emits `unit`, AND the value flows to
  `_csl_to_str(index)` whose `node: CSLNode` param lowers to `int`. These two trusted stubs
  disagree on the type of the value between them (unit vs int) — an irreducible two-trusted-stub
  mismatch that GAP #2 cannot bridge (inferring `index`'s type from either callee still clashes
  with the other). This is exactly the task's "callee returns a trusted/unmodeled type that
  genuinely can't be inferred" case.
- All other `_parse_*` construct CSLNode records = family-B (`emit_ir` variants).

GAP #2 (str) is banked and reusable for any future trusted `-> str` stub. The symmetric
`-> _Tok`-record and unit branches are un-needed by any reachable stub (no non-family-B method
returns/consumes them), so they were NOT built (avoiding a neutral feature). **Next parser cut
= family-B (list-append + emit_ir node variants) — corpus-reaching / deliberate multi-session
build, per the frontier-exhaustion doctrine.**

## Family-B emit_ir-child clause parsers BUILT (2026-07-26)

Extends the `_parse_proof`→`IrProofDecl` string-leaf template (37f0ae3c) to the FIRST
**emit_ir-child** clause parsers. Per clause node kind, all gated on `_uses_clause_ir`
(true only for the file defining the parser clause classes → byte-inert everywhere else):

1. `preamble.py` `_emit_exprir_theory`: `| IrX <fields>` ctor + `| IrX _ … -> "X"` kind_of
   arm + `| IrX … e -> 1 + size e` size arm (recurse the emit_ir child; leading strings
   not counted).
2. `expressions.py` `_IRNODE_CTORS["X"] = ("IrX", [__init__ field names])`.
3. mirror method: drop `\trusted`, give a faithful body ending in a GUARANTEED `return X(...)`.

The emit_ir child comes from `self._parse_expr()`. That call lowers to an emit_ir value only
because `_parse_expr` carries a `-> "ExprIR"` return annotation (added here; the stub STAYS
`\trusted` — this is the GAP #2 typed-trusted-return machinery, same as the `_parse_impl_rhs`/
`_parse_or_rhs` precedence RHS stubs). `_call_irnode_constructor` then binds the ctor's emit_ir
field to the lowered argument by `__init__` field order.

CONVERTED (each: whole-file Module2_Parser.py proof SUCCESS 0-unproven [foreground], FULL corpus
byte-diff 0 [812/812, byte-INERT], mutation test PASS, vacuity exit 0, mirror-check 52/52, drift 2,
ledger 3 — NO new cert, the IrBinOp/IrForallItems emit_ir-child precedent):

- **`_parse_class_invariant`** → `IrClassInvariant emit_ir` (e09c8dcd, 907→906) — single emit_ir
  child `ClassInvariant(self._parse_expr())`.
- **`_parse_raises`** → `IrRaisesDecl string emit_ir` (026f38c1, 906→905) — leaf-string `exc`
  (`self.expect_name()`, ProofDecl precedent) + emit_ir condition child.

**DEFERRED `_parse_loop`** (edits reverted clean): the live body ends in `self._err(...)` with NO
following return, so the neither-`invariant`-nor-`variant` path falls off the end returning unit
while the two branch arms `return LoopInvariant/LoopVariant(...)` return emit_ir → L3-tc
`"This expression has type emit_ir, but is expected to have type ()"`. The faithful fix requires
modelling `_err` as diverging/raising (it lives at the leaf of `expect_name`/`expect_op`/`expect_bs`
which are ALREADY proven with `_err: assigns \nothing; ensures True` — changing it re-opens their
proofs) OR an unfaithful control-flow restructure. Both violate the no-stack / faithful-semantics
discipline. **The trailing-`_err` fall-through is the shared blocker** for `_parse_loop`,
`_parse_function_variant`, `_parse_ghost`, `_parse_interface`, and every other `_parse_X` whose live
body ends in `_err`. REOPEN this sub-cluster only alongside a deliberate `_err`-divergence-model
build. Clean next candidates = clause `_parse_X` with a guaranteed terminal `return`.

## _err-DIVERGENCE MODEL BUILT + _parse_loop/_parse_interface CONVERTED (2026-07-26, Phase-2 executor) — count 905 -> 903 (2 REAL conversions)

**VERDICT: SPIKE PASSES NON-VACUOUSLY — the `_err`-divergence model is SOUND and BANKED.**
The trailing-`self._err(...)` fall-through (the shared blocker deferred by the prior batch)
is resolved by modelling `_err`'s UNCONDITIONAL-raise faithfully, NOT a blanket `ensures False`
massage. Two trailing-`_err` clause parsers converted, whole-file proven, corpus byte-diff 0.

**The model (commit `56d871b6`, emitter + mirror stmt_control_flow re-port):**
- `_err` annotated `-> NoReturn` in the mirror (live body is `t = self.cur(); raise
  _ContractSyntaxError(...)` — unconditional raise; STAYS `\trusted`, the annotation only
  makes the trusted interface precise). Module5 sets `is_noreturn` (NR1).
- `Module6_WhyMLTranspiler._module_method_noreturn` set (callee IR-names with is_noreturn).
- `expressions._handle_dotted_call`: a `self.<noreturn>(...)` call gets the abstract op
  `ensures { false }` (faithful never-returns, justified by the raise body) and lowers to
  `(let _ = <call> in absurd)` (bottom-typed `'a`) — continuation UNREACHABLE.
- `statements._handle_expr_stmt`: a bare-statement noreturn self-call emits the
  self-terminating absurd form (not `let _ = e in ()`, which would force `unit`).
- `stmt_control_flow._handle_if_stmt`: a one-armed-if body ending in `absurd)` diverges
  like a `raise` → no-else form, not the `else 0` value-if.
- `core_ir_semantic` NR2a: exempt `\trusted`/`\abstract` stubs (bodyless `val`; the
  `ensures { false }` is a reviewer-vouched INTERFACE assumption, not a body claim).

**SOUNDNESS (the decisive gate):** (a) `_err`'s live+mirror body IS an unconditional raise
— no non-raising path — so the divergence is JUSTIFIED, not assumed. (b) `check-emitted-vacuity
--emit` exit 0, NO new erasure on either converted method. (c) both converted bodies are
NON-VACUOUS: read self.i / at_name / advance / real emit_ir children; mutation-test-sensitive.
The `ensures { false }` poisons ONLY the genuinely-raising arm; each caller's real postcondition
(`self.i >= \old`) still holds on every RETURNING arm (proven). NOT a caller-contract massage.

**Family-B emit_ir ctors added (gated `_uses_clause_ir`, additive structural-variant, no cert):**
- `IrLoopInvariant`/`IrLoopVariant emit_ir` (commit `56d871b6`) — for `_parse_loop`.
- `IrInterfaceClause string emit_ir` + `IrEnsures`/`IrRequires emit_ir` (commit `8aecc3b9`) —
  for `_parse_interface`; `_parse_assigns` gains a `-> "ExprIR"` return annotation (stays trusted).

**CONVERTED (each: whole-file Module2_Parser proof SUCCESS 0-unproven [foreground, read];
FULL corpus byte-diff 0 [812/812 vs clean-HEAD b6574af0 worktree]; MUTATION TEST PASS; vacuity
--emit exit 0; mirror-sync drift 2; ledger 3):**
- `_parse_loop` (`a661a482`, 905->904) — LoopInvariant/LoopVariant arms + trailing `_err`.
- `_parse_interface` (`331623f1`, 904->903) — InterfaceClause(Ensures/Requires/`_parse_assigns`)
  arms + trailing `_err`.

**expect_op/expect_name/expect_bs re-prove (§10.4):** all three call `_err`; the model changes
their emission (the `_err` call now lowers to `(let _ = <call> in absurd)`). ALL re-proven by
the whole-file Module2_Parser proof SUCCESS (they are in the same file). expect_name's one-armed
`if not at_name: _err(...)` now routes to the no-else divergence form — proves.

**§10c shared-emitter:** only TWO mirror files carry the clause-IR theory (Module2_Parser,
Module5_IREmitter). Module5_IREmitter emission changes by EXACTLY the additive ctor lines (type
decl + total kind_of/size arms — NO function body changed); L3-tc SUCCESS confirms exhaustiveness
intact (wildcard matches). Whole-file Module5_IREmitter proof is a pre-existing HEAVY-file timeout
(171KB .mlw, like stmt_control_flow); the additive extension is structurally proof-neutral
(base-Valid⟹new-Valid, base-timeout⟹new-timeout — the IrClassInvariant/IrRaisesDecl precedent).

**REMAINING siblings (NOT divergence-model work — separate family-B builds):** `_parse_ghost`
(terminal returns; needs `IrGhostAssignDecl`/`IrGhostArraySetDecl` with keyword/default-arg ctor
binding — `_call_irnode_constructor` does not yet handle kwargs/arg-count-variance) and
`_parse_function_variant` (terminal returns; needs FunctionVariant class-construction → optfield
`iropt_str` wrapping, distinct from the existing dict-based `_recognize_functionvariant_builder`).
Both have a GUARANTEED terminal return, so they do NOT exercise the `_err`-divergence model — they
are pure node-ctor family-B, fundable independently. The `_err`-divergence model is banked and
reusable for ANY future trailing-`_err` clause parser.

## Family-B clause batch: 7 more clause parsers CONVERTED (2026-07-26, Phase-2 executor) — count 903 -> 894 (9 REAL conversions this run + 2 earlier same-day)

**VERDICT: the reachable simple-CLAUSE-parser frontier is now EXHAUSTED.** Nine
single-terminal-return contract-clause `_parse_*` builders converted this run, each a
verbatim live port gated by a fresh foreground whole-file proof. Three small, reusable,
byte-inert emitter capabilities banked (optfield `iropt_str` wrap, string-default fill,
explicit-`None`-arg → `IrSNone`); the rest reuse existing precedents.

**Emitter capabilities BUILT (module6_whyml, all @mutable_state / `_uses_clause_ir`-gated → corpus byte-inert):**
- **optfield `iropt_str` wrap** (`_IRNODE_CTOR_OPTFIELDS` + `_call_irnode_constructor`):
  an `Optional[str] = None` ctor field — a BOUND string actual wraps to `(IrSSome <v>)`,
  an OMITTED field is `IrSNone`. The parser class-construction analog of the dict-based
  `_lower_functionvariant_optfield`.
- **string-default fill** (`_IRNODE_CTOR_STRDEFAULTS`): an OMITTED required string slot is
  filled from its class field's concrete string default (`declared_type: str = 'int'` →
  the literal `"int"`), since Module5 `field_defaults` captures only int/float defaults.
- **explicit-`None`-arg → `IrSNone`** (`none_arg_indices`/`none_kwargs` threaded from
  `_handle_call_expr`): an EXPLICIT `None` literal bound to an `iropt_str` optfield slot
  (`SharedDecl(name, None)`) maps to `IrSNone` instead of the ill-typed `IrSSome 0`
  (`None` lowers to the int witness `0`). Mutation-verified load-bearing.

**CONVERTED (each: whole-file Module2_Parser proof SUCCESS 0-unproven [foreground, read];
FULL corpus byte-diff 0 [812/812 vs clean-HEAD 969feaa2 worktree]; MUTATION TEST PASS;
vacuity --emit exit 0; Module5_IREmitter L3-tc SUCCESS [additive ctors, exhaustiveness
intact — whole-file M5 proof a pre-existing heavy timeout, additive extension proof-neutral];
mirror-check 52/52; drift 2; ledger 3):**
- `_parse_function_variant` (67953136, 903→902) — `IrFunctionVariant emit_ir iropt_str`
  (ADT ctor ALREADY existed for the dict recognizer; only the optfield wiring added).
- `_parse_ghost` (81a5ba30, 902→901) — `IrGhostAssignDecl string emit_ir string string`
  (declared_type string-default fill) + `IrGhostArraySetDecl string emit_ir emit_ir`.
- `_parse_footprint` (680bb4ef, 901→900) — `IrFootprint string emit_ir` (RaisesDecl shape).
- `_parse_mutex_invariant` (7dd9e426, 900→899) — `IrMutexInvariant string emit_ir`
  (`_parse_mutex_expr_str` gains `-> str`, stays trusted).
- `_parse_shared` (894945a7, 899→898) — `IrSharedDecl string iropt_str` (explicit-None optfield).
- `_parse_assigns_region` (71391489, 898→897) — existing `IrAssignsRegion string emit_ir
  emit_ir` ctor; ZERO emitter change, pure-mirror conversion.
- `_parse_shared_state` (ead9e192, 897→896) — `IrSharedStateDecl string string` (2 leaf strings).
- `_parse_touches_field` (12ff3cfb, 896→895) — `IrTouchesFieldDecl string string`.
- `_parse_depends_method` (93a1ec39, 895→894) — `IrMethodDependencyDecl string string string`
  (`kind: str` method param + `sig` from the converted `-> str` `_parse_mixin_method_sig`).

**REMAINING trusted `_parse_*` = two disjoint deferred veins (NOT simple-clause wins):**
- **LIST-building clause parsers** (`.append(...)` / `', '.join(...)` / clause-list loops):
  `_parse_datatype` (+ `_parse_variant_def` tuple), `_parse_lock_order`, `_parse_happy`
  (+ region/targets/opt_except), `_parse_act_block`, `_parse_for_block`, `_parse_act_names`,
  `_parse_compose_from`, `_parse_conforms_to`, `_parse_dotted_path_list`, `_parse_assigns_target`
  (+ `_try` higher-order), `_parse_no_exception` [SKIP, List[str]], `_parse_inductive*`. Need the
  family-B **list-append** capability — a deliberate build.
- **EXPRESSION-grammar cluster** (`_parse_membership`→CSLIn/CSLNotIn, `_parse_unary`→UnaryOp,
  `_parse_atom`→StrConcatExpr, `_parse_atom_name`/`_parse_atom_bs`→CSLBool/CSLNone/
  SubscriptFieldAccess/FieldAccess/Result/…): each constructs MULTIPLE mutually-recursive
  ExprIR node kinds; needs the per-node emit_ir variants co-landed as an interconnected set
  (the IrBinOp precedent × many). A larger deliberate build, not single-shot.
- **Hard boundaries** (stay trusted): `_parse_mutex_expr_str`/`_parse_mixin_type`/`_parse_mixin_params`
  (string list-join, annotated `-> str`), `_parse_assigns`/`_parse_expr`/`_parse_quantifier`
  (annotated trusted returns), `_parse_impl_rhs`/`_parse_or_rhs`/`_parse_and_rhs` (quantifier-
  monotonicity trust-widen — reviewer), `_parse_contract`/`_parse_trusted`/`_grab_reviewer_id`/
  `_lex_contract`/`_csl_to_str` (char-lexer / recursive-dispatch boundaries).

## LIST-append clause vein: 5 string-list clause parsers CONVERTED; emit_ir-list DEFERRED (2026-07-26, Phase-2 executor) — count 894 -> 889

**VERDICT: the reachable LIST-append frontier is the STRING-element list clause parsers
(5 converted, verbatim ports). The EMIT_IR-element list parsers (`_parse_act_block`/
`_parse_for_block`) are a proof-COST boundary at the 30s SMT budget — the seq_to_irlist
bridge capability is BUILT and proves, but their converted-body VC deterministically times
out (see below).**

### CENSUS (list-string vs list-emit_ir vs list-of-records)
- **list-STRING (`list string`) — CONVERTED (5):** `_parse_act_names`, `_parse_dotted_path_list`
  (direct `list string` return); `_parse_compose_from`, `_parse_conforms_to`, `_parse_lock_order`
  (wrap the `list string` in a clause node).
- **list-EMIT_IR (`irlist`) — DEFERRED (2):** `_parse_act_block`, `_parse_for_block` (clauses =
  list of Given/Requires/Ensures/Assigns emit_ir nodes). Capability BUILT, VC-cost blocked.
- **list-of-RECORDS/tuples — DEFERRED (element value shape):** `_parse_datatype`
  (variants = list of `(ctor, list string)` tuples), `_parse_variant_def` (returns a bare
  tuple), `_parse_inductive`/`_parse_inductive_rules` (list of `(name, expr)` / 3-tuples),
  `_parse_mixin_params`/`_parse_mixin_type` (`list string` then `', '.join(...)` -> a STRING;
  needs faithful list-string join), `_parse_happy*` (multi-field HappyProperty with list +
  optional fields). Need a NEW element value shape (list-of-tuple ADT / string-join).

### CONVERTED — list-string (each: whole-file Module2_Parser proof SUCCESS 0-unproven
[foreground, read]; corpus byte-diff 0; vacuity --emit exit 0; MUTATION TEST PASS;
mirror-check 52/52; drift 2; ledger 3):
- `_parse_act_names` (485d1d11, 894->893) — ZERO emitter change. `names=[expect_name()];
  while accept_op(','): names.append(expect_name()); return names`. The `seq string`
  list-local + `array string` return + `materialize_str` bridge machinery ALREADY existed;
  the faithful `-> List[str]` annotation (item34.md CF5 `return_value_type=string`) is all
  that was needed. **This is the whole capability for direct `list string` returns.**
- `_parse_dotted_path_list` (c9025d93, 893->892) — ZERO emitter change; same shape over the
  already-converted `-> str` `_parse_dotted_path`.
- **list-string CLAUSE CTORS BUILT** (24497b02, with `_parse_compose_from` 892->891):
  `IrComposeFromDecl (seq string)` / `IrConformsToDecl (seq string)` / `IrLockOrder
  (seq string)` (preamble `_emit_exprir_theory` ctor + kind_of arm; NO size arm — the
  growable `seq string` is not an emit_ir child, size's `_ -> 1` catch-all covers it) +
  `_IRNODE_CTORS` (mixins/protocols/order) + `_CLAUSE_IR_NODES` registration. Gated
  `_uses_clause_ir` (True ONLY for Module2_Parser, grep-verified sole clause-class definer
  -> corpus byte-diff 0 [812/812], emission surface confined to the proven file). The
  in-body list local lowers to a growable `seq string` (Seq.cons/snoc); `_call_irnode_
  constructor` binds it to the ctor's `seq string` field. Conversion carries `-> "ExprIR"`.
- `_parse_conforms_to` (c81ce926, 891->890) — pure-mirror (reuses `IrConformsToDecl`).
- `_parse_lock_order` (37e41441, 890->889) — pure-mirror (reuses `IrLockOrder`). Elements
  from the trusted `-> str` `_parse_mutex_expr_str` (stays trusted). SOUNDNESS (first
  trusted-val-in-loop): termination is accept_op-driven (its proven strict-on-Some increment
  advances self.i every iteration INDEPENDENT of the trusted call); `self.i >= \old` faithful.

### DEFERRED — emit_ir-element list (`_parse_act_block`, `_parse_for_block`): capability BUILT, 30s VC-COST blocked
The full capability was built and REVERTED (uncommitted, clean) after the proof-cost wall:
- **`seq_to_irlist` bridge** (preamble, after `irnth`): `let rec function seq_to_irlist_from
  (s: seq emit_ir) (i: int) : irlist requires {0<=i<=length} variant {length s - i} = if
  i>=length then ILNil else ILCons (Seq.get s i) (seq_to_irlist_from s (i+1))`. The
  `seq_to_sl` (stmt_ir) precedent verbatim — materializes the growable `seq emit_ir` a
  clause-list LOCAL builds into the monomorphic `irlist` (Why3 rejects a direct `seq emit_ir`
  ctor field of emit_ir, non-strictly-positive). **The bridge + all its VCs PROVE.**
- **ctors** `IrGiven emit_ir` / `IrAct string irlist` / `IrForExpand string emit_ir emit_ir
  irlist` (+ kind_of arms; IrGiven size `1+size e`; IrAct/IrForExpand fall to size's `_->1`
  catch-all, the IrMkTupleN irlist precedent) + `_IRNODE_CTORS` (Act/ForExpand/Given) +
  `_IRNODE_CTOR_IRLISTFIELDS = {Act:{clauses}, ForExpand:{clauses}}` (wraps a seq actual in
  `seq_to_irlist` at an irlist-field ctor slot in `_call_irnode_constructor`).
- **THE BLOCKER (proof-cost, not capability):** `_parse_act_block`'s converted body
  type-checks and emits a faithful non-vacuous body (`clauses = ref Seq.empty; while
  <4-way at_name guard>: ...Seq.snoc !clauses (IrGiven/IrRequires/IrEnsures/parse_assigns...);
  if not clauses: _err; IrAct !name (seq_to_irlist !clauses)`), but its whole-file proof has
  ONE deterministic 30s TIMEOUT (98-100M steps) on the **loop-invariant-INIT of the BOUNDS
  invariant `0 <= self.i < length`** — a class-invariant fact that is trivially Valid (0.03s)
  in every other converted loop. Isolation confirmed: (a) with the emitter ctors present but
  act_block trusted, the file proves SUCCESS -> the added theory does NOT bloat other goals;
  (b) even a single-`at_name` guard still times out -> not the guard breadth. The cost is
  intrinsic to act_block's converted body (the `seq emit_ir` LOCAL + expanded clause theory
  pollute the solver context so a trivial bounds fact drowns). No faithful annotation change
  clears a 98M-step init. `_parse_for_block` is strictly heavier (tuple-unpack + `Number(0)`
  ctor + 4-field wrapper). **REOPEN with a raised SMT budget for this file OR a lighter
  `at_name`/bounds model; the seq_to_irlist bridge + IrAct/IrForExpand/IrGiven ctor design
  above is the drop-in build (it type-checks and the bridge proves).**

## LIST-OF-RECORDS vein: CENSUS + SPIKE — 1 cert-free win, rest = BOUNDARY (2026-07-26, Phase-2 executor) — count 889 -> 888

**VERDICT: the list-of-records vein yields ONE clean cert-free conversion
(`_parse_mixin_params`, a list-string JOIN); the genuine list-of-records/tuple
members are a CERTIFIED/INFRASTRUCTURE BOUNDARY (per convert-or-BOUNDARY, do-not-over-build).**

### CENSUS — element shapes of the deferred `_parse_*`
- **list-string JOIN → STRING (no ADT, no cert):** `_parse_mixin_params` (`', '.join(list str)`),
  `_parse_mixin_type` (recursive, `f"{name}[{', '.join(args)}]"`). Result type is a bare `string`.
- **bare TUPLE `(string, seq string)`:** `_parse_variant_def` (`return (ctor, types)`).
- **list of `(string, seq string)` tuples:** `_parse_datatype` (`variants=[variant_def]; while '|': append`,
  → `DatatypeDecl(name, variants, type_params)`).
- **list of `(string, emit_ir)` pairs:** `_parse_inductive_rules` (`rules.append((rname, self._parse_expr()))`).
- **nested list-of-3-tuples-with-inner-rule-list:** `_parse_inductive` (`members.append((wname, wsig, wrules))`).

### CONVERTED — `_parse_mixin_params` (0af25459, 889->888)
The emitter ALREADY lowers `", ".join(params)` over a **VARIABLE** `seq string` local to
`(str_join_seq ", " !params)` — `str_join_seq` is a pre-existing abstract `val` in the preamble.
So the direct list-string-join return needs **ZERO new machinery, ZERO emitter change
(`src/pycsl` untouched → corpus byte-inert BY CONSTRUCTION), NO certificate**. Verbatim live
port (`params=[_parse_mixin_param()]; while accept_op(','): params.append(_parse_mixin_param());
return ", ".join(params)`). Gate battery: whole-file Module2_Parser.py proof **SUCCESS 0-unproven**
(foreground, read); vacuity `--emit` exit 0 (no NEW erasure); MUTATION TEST **PASS** (join sep
`", "`→`"MUTSEP"` moves the emitted `str_join_seq` arg); mirror-check 52/52; drift 2; ledger 3.
Enabled by a faithful `ensures self.i >= \old(self.i)` on the loop-body callee `_parse_mixin_param`
(a CONVERTED method — proves it) and its still-`\trusted` dep `_parse_mixin_type` (the accepted
**`_parse_unary` precedent**: a trusted parser stub MAY carry a real structural monotonicity ensures
with a justifying comment — monotonicity is a genuine property of the recursive-descent cursor).

### BOUNDARY — the rest of the vein
- **`_parse_mixin_type` (recursive) — PROOF-INFRASTRUCTURE BOUNDARY.** Spiked FULLY as a
  converted `let rec` (emitter emits `let rec … variant { (Array.length self.toks) - self.i }`,
  L3-tc ✓; recursion + `str_join_seq` + f-string all lower). Whole-file proof gets to **1
  stubborn unproven goal**: the FIRST recursive call `[self._parse_mixin_type()]` sits OUTSIDE
  any loop, and its termination-variant decrease needs `advance` to strictly increment, which
  needs `self.i < \length-1`, which needs the **EOF-sentinel class invariant to be ambient**
  (`toks[i]=="OP" ∧ toks[len-1]=="EOF" ⟹ i≠len-1`). Every converted precedence **loop** proves
  this — but only because the sentinel is RE-STATED as a loop invariant there; it is NOT ambient
  mid-body outside a loop. `#@ assert` (can't re-prove the non-ambient sentinel) and a
  `#@ requires <sentinel>` (proves inside the body but **cascades an unprovable caller obligation
  to every non-loop call site** across the mixin call graph) both fail cleanly. Threading class
  invariants as ambient mid-body hypotheses is a general, risky emitter change = over-build.
  Reverted clean; left `\trusted` with the faithful monotonicity ensures.
- **`_parse_variant_def` — CLASS-O TUPLE-SLOT BOUNDARY.** Spiked: a `(string, seq string)` bare
  tuple return emits the signature as the homogeneous `(int, array int)` (the `auto_trust.py`
  `_should_auto_trust_tuple_return` "class O" gap: per-slot tuple type inference not landed), AND
  the empty-list branch `(ctor, [])` lowers the `[]` to `array int` (`Array.make 1024 0`) while the
  built-up branch is `seq string` — two stacked type bugs. Needs per-slot tuple type inference +
  empty-list-literal-in-tuple typing = a real emitter build (1 stub standalone).
- **`_parse_datatype` / `_parse_inductive_rules` / `_parse_inductive` — NEW-SHAPE BOUNDARY.**
  Datatype needs `seq (string, seq string)` (depends on the variant_def tuple capability);
  inductive_rules needs `seq (string, emit_ir)` and inductive a nested member-list+rule-list —
  and a `seq`-of-tuple-containing-`emit_ir` ctor field of emit_ir is non-strictly-positive
  (Why3-rejected, the same wall `irlist` was built for), so these need NEW monomorphic certified
  inductives (rule_list / member_list) with emit_ir children = ≥2 stacked new shapes + co-landing
  certs. Per the decision rule (≥2 stacked shapes / new cert for a 1-2 stub cluster) = CERTIFIED-BOUNDARY.

**Net:** list-of-records vein = 1 conversion (`_parse_mixin_params`), count 889→888. The tuple/
list-of-tuple/inductive members are a deliberate multi-feature (tuple-slot-typing + monomorphic
list-of-tuple ADTs + co-landing certs) build — authorize before funding.

## EXPRESSION-GRAMMAR cluster = CERTIFIED PROOF-COST BOUNDARY (parser-vein TERMINUS) (2026-07-26, Phase-2 executor) — count STAYS 888

**VERDICT: the contract expression-grammar cluster is the honest parser-vein TERMINUS. The
CHEAPEST possible member — `_parse_expr`, a pure dispatch with ZERO new machinery — is itself a
PROOF-COST boundary; every other member is strictly harder. Convert-or-BOUNDARY → BOUNDARY, reverted
clean, count 888 held.**

### CENSUS — the 7 expr-grammar stubs (node kinds constructed + existing ctor? + blocker)
- **`_parse_expr`** — constructs NOTHING; pure dispatch `if at_bs(\forall|\exists|\exist):
  _parse_quantifier() else _parse_implication()`. Zero new emit_ir variant, zero machinery. Needs
  only `_parse_quantifier` annotated `-> "ExprIR"` (stays trusted, GAP #2 banked). NO live-parser
  change (single-token `at_bs` guards, no `peek`). **The simplest conceivable conversion.**
- **`_parse_quantifier`** — `cls = Exists if is_exists else Forall` then `cls(var, ...)`
  (CLASS-VALUED variable construction — emitter recognizes ctor calls BY NAME, cannot lower a class
  held in a variable) + `ForallItems`, `_mk_in`→`BinOp(CSLIn(Var(var),domain),op,body)`, `isinstance`/
  `DictView.kind` checks, `raise`, `reversed(names)` nested-node loop. Class-valued + multi-node = BOUNDARY.
- **`_parse_atom`** — `StrConcatExpr(node, right)` (new emit_ir variant needed) + RECURSIVE
  `_parse_atom()` OUTSIDE any loop → the EOF-sentinel-not-ambient proof-infra boundary (identical to
  the `_parse_mixin_type` recursion boundary). BOUNDARY (proof-infra).
- **`_parse_atom_primary`** — `Number(float(t.string))` / `Number(int(t.string))` = string→number
  conversion (the str_to_int / str_to_float oracle CORRECTNESS boundary) + `StringLiteral`, delegates.
  BOUNDARY (correctness).
- **`_parse_atom_name`** — ~13 node kinds (CSLBool/CSLNone/FieldAccess/SubscriptFieldAccess/
  FieldSubscript/DictView/GlobalFieldSubscript/CallExpr/CSLSlice/ChainedSubscript/NestedSubscript/
  SubscriptAccess/Var) + class-valued `cls` (genexp all/any→Forall/Exists) + list-append (args) + `raise`.
  Massive interconnected multi-variant + class-valued + list-append. BOUNDARY.
- **`_parse_atom_bs`** — ~50 DISTINCT backslash-atom node kinds (Result/Old/Nothing/ArrayLength/Valid/
  Separated/all map/set/list ghost exprs/…) + `int(idx_tok.string)`. Interconnected ~50-variant co-land
  + str_to_int. BOUNDARY (the bulk).
- **`_parse_expr_list`** — returns `list of emit_ir` = `irlist`; needs the `seq_to_irlist` bridge
  that is the DOCUMENTED proof-COST wall (`_parse_act_block`/`_parse_for_block`, 30s/98M-step timeout).
  BOUNDARY (proof-cost).

### SPIKE (`_parse_expr`, the simplest) — measured, then REVERTED
Ported the verbatim live body, annotated `_parse_quantifier -> "ExprIR"` (stayed `\trusted`), dropped
`\trusted` on `_parse_expr`. **`--no-proof --keep-mlw`: L3-tc ✓** — emits a faithful NON-VACUOUS body
(`if ((at_bs "\forall")<>0 || (at_bs "\exists")<>0 || (at_bs "\exist")<>0) then Return(_parse_quantifier
self) else Return(_parse_implication self)`), zero int-hash/opaque.

**Whole-file Module2_Parser.py proof (FOREGROUND, read by me): FAILED — 6 goals unproven.** The 6 are
ALL POSTCONDITIONs of the ALREADY-CONVERTED clause-parser CALLERS — `_parse_class_invariant`
(Timeout 103M steps), `_parse_interface` (×2 Unknown), `_parse_loop` (×2 Unknown), `_parse_raises`
(Timeout 102M steps) — NOT `_parse_expr` itself. Those callers embed `_parse_expr self` as an emit_ir
CHILD (`IrClassInvariant (_parse_expr self)`, ~20 call sites across the clause parsers). Pre-conversion
these callers all proved SUCCESS 0-unproven (documented above); converting `_parse_expr` from an opaque
`\trusted val` to a concrete `let` body puts its definition (→ transitively `_parse_implication` → the
WHOLE precedence chain) into the module's solver context, and even the TRIVIAL `ensures True`
postconditions of `_parse_class_invariant`/`_parse_raises` then DROWN at 100M+ steps. This is the exact
**solver-context-pollution proof-COST wall** documented for `_parse_act_block` ("the seq emit_ir LOCAL +
expanded clause theory pollute the solver context so a trivial bounds fact drowns; no faithful annotation
change clears a 98M-step init").

**`#@ no_inline` PROBED and does NOT clear it** — the documented anti-inlining-blowup directive
("avoids re-proving a large body in every caller's context, the os `sys_write` blow-up"): the SAME 6
goals still time out (class_invariant 107M, raises 112M steps). So the pollution is the module-level
PRESENCE of the concrete `_parse_expr` definition in the whole-file solver context, NOT call-site
splicing — `no_inline` prevents IR splicing but the `let _parse_expr = body` still lives in the .mlw and
the solver context still explodes. No faithful annotation clears a 100M-step postcondition drown.

### TERMINUS argument
The gate (whole-file proof SUCCESS 0-unproven) FAILS → REVERTED clean (single file
`src/self-annotate/src/frontend/Module2_Parser.py` via `git checkout -- <exact path>`), count 888 held,
`_parse_quantifier` back to no-annotation `\trusted`. The decisive point: `_parse_expr` is the
**cheapest conceivable** expr-grammar conversion (pure dispatch, no node built, no new variant, no new
machinery, no live-parser change). It is a proof-COST boundary. Every OTHER member is strictly harder
(builds nodes, embeds `_parse_expr`, needs new machinery / class-valued lowering / str_to_int / the
irlist proof-cost bridge) — so ALL 7 are blocked by AT LEAST the same clause-parser-caller pollution
PLUS their own blockers. The contract expression-grammar cluster is the parser-vein TERMINUS. Reopen
only with a per-file raised SMT budget for Module2_Parser.py OR a modular-boundary mechanism that
removes a converted method's body definition from OTHER goals' solver context (a deliberate emitter/
proof-harness build, authorize first). ZERO live-parser changes; foregrounded every proof; zero orphans.

## REOPENED-TAIL run: 5 expr-grammar conversions — the "proof-cost terminus" was TWO more misdiagnoses (2026-07-27, Phase-2 executor) — count 887 -> 882

**VERDICT: the expr-grammar "CERTIFIED PROOF-COST BOUNDARY" (parser-vein TERMINUS at 888) was WRONG on
two further counts, exactly as the proof-scale wall was.** With `_parse_expr` already converted (the
contract-gap fix, 887), FIVE more expr-grammar stubs convert cleanly, each whole-file-proven foreground.

**CONVERTED (each: whole-file Module2_Parser proof SUCCESS 0-unproven [foreground, read]; corpus
byte-diff 0; MUTATION TEST PASS; vacuity --emit exit 0; mirror-check 52/52; drift 2; ledger 3):**
- `_parse_membership` (0f78d22a, 887->886) — `CSLIn`/`CSLNotIn` (2 emit_ir children each). NEW ctors
  `IrCSLIn`/`IrCSLNotIn emit_ir emit_ir` (`_uses_clause_ir`-gated; IrGhostArraySetDecl precedent);
  `_IRNODE_CTORS` CSLIn/CSLNotIn. Module5_IREmitter L3-tc ✓ (additive, exhaustiveness intact).
- `_mk_in` (47c14e80, 886->885) — MIRROR-ONLY (all ctors existed: IrBinOp/IrVar + the just-landed
  IrCSLIn); `BinOp(CSLIn(Var(var),domain), op, body)`. Faithful param annotations, byte-inert.
- `_parse_unary` (b6472469, 885->884) — RECURSIVE, `IrUnaryOp` (pre-existing). The census's
  "EOF-sentinel-not-ambient recursion boundary" was TWO misdiagnoses: (1) self-recursion emitted `let`
  not `let rec` -> the `#@ \variant \length(self.toks)-self.i` directive fixes it (NO emitter change);
  (2) the variant PROVES directly from the EOF-sentinel class invariant + advance's strict-increment on
  the guarded branch (cur NAME/OP => not EOF => self.i<len-1). MIRROR-ONLY. `_parse_atom` stays trusted
  with a FAITHFUL monotonicity ensures (only-advances; `_try` sole site = `_parse_assigns_region` L1481)
  + `-> "ExprIR"` (GAP #2).
- `_parse_atom` (f9bf09f2, 884->883) — RECURSIVE, `IrStrConcat` (pre-existing base ctor). Same
  `#@ \variant` pattern. Emitter: 1 line `_IRNODE_CTORS["StrConcatExpr"]` -> the existing IrStrConcat
  (Module5 uses "StrConcat" wire key; parser names the class). Corpus byte-diff 0. `_parse_atom_primary`
  stays trusted (faithful monotonicity + `-> ExprIR`; itself a str_to_int/float boundary).
- `_parse_expr_list` (825c6406, 883->882) — returns `List[ExprIR]`. NEW emitter capability (NOT a
  contract-gap): a `-> List[ExprIR]` return -> `seq emit_ir` + DIRECT `!exprs` return (the `seq hval`
  List[PyVal] precedent), replacing the mistyped `array int`+int-`materialize`. functions.py
  (return_value_type=="emit_ir") + stmt_control_flow.py (`_func_return_type=="seq emit_ir"` direct
  return). Confined: `_parse_expr_list` is the SOLE `-> List[ExprIR]` method mirror+corpus-wide
  (Module5_IREmitter.mlw byte-IDENTICAL; corpus byte-diff 0).

**Capabilities banked (all `_uses_clause_ir`/sentinel-gated, corpus byte-inert):** IrCSLIn/IrCSLNotIn
2-child ctors; StrConcatExpr class->ctor alias; the `#@ \variant` recursive-descent-parser recursion
key (`let rec` + EOF-sentinel variant, reusable for ANY guarded self-recursive parser rule incl. the
prior `_parse_mixin_type` boundary); the `seq emit_ir` List[ExprIR] return.

**REMAINING tail = GENUINE boundaries (convert-or-DEFER -> DEFER):**
- `_parse_quantifier` — class-valued `cls = Exists if is_exists else Forall` then `cls(var,...)` (the
  emitter recognizes ctor calls BY NAME; a class held in a variable can't be lowered) + ForallItems +
  `isinstance(domain, DictView)`/`domain.kind` + `reversed(names)` nested-node loop + raise. CLASS-VALUED-CTOR BOUNDARY.
- `_parse_atom_primary` — `Number(int(t.string))`/`Number(float(t.string))` = str_to_int/str_to_float
  oracle CORRECTNESS boundary. (Now trusted with faithful monotonicity + `-> ExprIR`.)
- `_parse_atom_name` (~13 node kinds + class-valued all/any->Forall/Exists + list-append) /
  `_parse_atom_bs` (~50 node kinds + int(idx)) — interconnected multi-variant + class-valued + str_to_int BULK BOUNDARY.
- `_parse_act_block` / `_parse_for_block` — need the `irlist` ctor-FIELD (Why3 REJECTS a `seq emit_ir`
  ctor field as non-strictly-positive -> the bespoke monomorphic `ILNil|ILCons emit_ir irlist` inductive
  + seq_to_irlist bridge, BUILT-and-REVERTED prior run). Their converted body hits a deterministic
  30s/98M-step TIMEOUT on the bounds-invariant-INIT `0 <= self.i < length` — a goal at LOOP ENTRY,
  BEFORE any `_parse_expr` call, so NOT the shared clause-caller contract-gap; a genuine clause-theory
  SMT proof-COST boundary. Reopen with a per-file raised SMT budget OR a lighter clause-theory model.

**LESSON (third time): a parser "proof-cost / recursion boundary" reached without an isolating
measurement is a HYPOTHESIS, not a floor.** The `#@ \variant` directive + faithful trusted-callee
monotonicity ensures cleared what the census called an intrinsic EOF-sentinel-ambient proof-infra wall.

## LIST-OF-RECORDS vein RE-SPIKED: `_parse_variant_def` = EARLY-RETURN TUPLE-EXCEPTION BOUNDARY (2026-07-27, Phase-2 executor) — count STAYS 883

**VERDICT: CERTIFIED-BOUNDARY, sharpened by measurement (the prior "class-O tuple-slot" census was
STALE in one direction and INCOMPLETE in another).** Convert-or-BOUNDARY on the 4 remaining
list-of-records members (`_parse_variant_def`, `_parse_datatype`, `_parse_inductive_rules`,
`_parse_inductive`) → BOUNDARY, reverted clean (emitter `functions.py` + mirror both `git checkout`).

### CENSUS — element shapes (all PURE for the first two, emit_ir-bearing for the last two)
- `_parse_variant_def` → bare tuple `(string, seq string)` (`ctor = expect_name(); … return (ctor, types)`
  / `return (ctor, [])`). NO record class exists — the live body returns a raw 2-tuple, so a faithful
  port MUST emit a tuple, not a `{ctor; fields}` record. PURE (no emit_ir) → no non-strict-positivity,
  **no certificate**.
- `_parse_datatype` → `DatatypeDecl(name: string, variants: seq (string, seq string), type_params: seq string)`.
  PURE → no cert; needs a `seq (string, seq string)` LOCAL build + an `IrDatatypeDecl` ctor with a
  `seq (string, seq string)` field.
- `_parse_inductive_rules` → `seq (string, emit_ir)`; `_parse_inductive` → nested `seq (string, string, seq (string, emit_ir))`.
  emit_ir INSIDE a tuple inside a seq → a `seq (string, emit_ir)` ctor field of emit_ir is
  **non-strictly-positive (Why3-rejected, the `irlist` wall)** → needs NEW monomorphic **certified**
  inductives (`rule_list = RLNil | RLCons string emit_ir rule_list` + `seq_to_rulelist` bridge) with
  emit_ir children = ≥2 stacked new shapes + co-landing certs → §10.5 CERTIFIED-BOUNDARY.

### SPIKE (`_parse_variant_def`, verbatim port + loop invariants) — MEASURED gap stack
The prior census said "per-slot tuple type inference NOT landed" — **STALE**: `_refine_tuple_return_type`
+ `_infer_tuple_slot_type` (functions.py) DO refine per-slot signatures (string/array/emit_ir). A small
byte-inert emitter add (string-call-result-local + `seq_value_types` seq-string-local slot recognition,
`_mutable_state_classes`-gated) refined the signature `(int,int)` → `(string, array int)` (the `ctor`
string slot landed). BUT `--no-proof --keep-mlw` then exposes the REAL, DEEPER stack — three MORE gaps,
each non-trivial, for this ONE standalone stub (its only caller `_parse_datatype` stays trusted → does
not consume the tuple, so variant_def is standalone-reachable but standalone-boundaried):
1. **seq-string SLOT at map-build time.** The `types` slot stayed `array int` — `func["seq_value_types"]`
   (which drives the body's correct `seq string` Seq.cons/snoc) is not populated at return-type-MAP-build
   time, so the slot refinement can't see it. (The BODY lowers `types` right; only the SIGNATURE lags.)
2. **empty-list-in-tuple-slot.** The second branch `return (ctor, [])` lowers `[]` via the generic
   `expressions.py` Tuple path to `(Array.make 1024 0)` (array int), with NO slot-type context — needs a
   per-slot return lowering that maps an empty ListLit in a `seq string` slot to `(Seq.empty: seq string)`.
3. **DECISIVE — the tuple-return EXCEPTION is all-int, keyed only by ARITY.** `_parse_variant_def` has a
   CONDITIONAL (early) return → `_has_early_ret` → the raise/catch path: `raise (Return_2 …)` caught by
   `with Return_2 r -> r`, where preamble.py declares `exception Return_2 (int, int)` (`", ".join(["int"]*arity)`,
   line ~2474). The refined-tuple-return feature only ever covered **TAIL-return** functions (`_unpack_direntry`
   `(int, array int)` has a single tail return → no exception). Extending it to early-return refined tuples
   needs a **per-slot-typed** `Return_{arity}` exception (name keyed on slot types, not arity — else two
   arity-2 functions with different slot types collide on one global exception), touching the preamble
   declaration + every raise + every catch = a cross-cutting exception-model change that also risks corpus
   byte-diff. This is the hard blocker measured this run (`.mlw` line-1482: body `(string, seq string)` vs
   `Return_2 (int, int)`).

### DECISION
`_parse_variant_def` = **1 standalone stub needing ≥3 stacked new emitter shapes** (seq-string-slot at
map-time + empty-list-in-tuple + per-slot-typed early-return tuple exception). `_parse_datatype` adds a
4th (seq-of-tuple element typing + `IrDatatypeDecl` ctor). `_parse_inductive*` add certified monomorphic
inductives (emit_ir-in-tuple). Per the convert-or-BOUNDARY rule (1 stub / ≥2 stacked shapes / new cert →
CERTIFIED-BOUNDARY, do-not-over-build), the whole vein is a BOUNDARY. Reverted BOTH edited files by exact
path (`git checkout -- src/self-annotate/src/frontend/Module2_Parser.py src/pycsl/module6_whyml/functions.py`);
count held 883, drift 2, ledger 3, formal-semantics untouched, zero live-parser changes, zero orphans.
**REOPEN key:** the *sharpest single next feature* is the **per-slot-typed early-return tuple-return
exception** (gap #3) — it is what distinguishes this from the already-landed tail-return refined tuple;
build it (+ gaps #1/#2, both small) and `_parse_variant_def` converts, then `_parse_datatype` needs only
the seq-of-tuple + `IrDatatypeDecl` add (pure, no cert); `_parse_inductive*` stay behind the certified
`rule_list` inductive. NOTE: this is a MEASURED gap stack, not a census hypothesis — the emission was
read at each layer.

## PER-SLOT-TYPED EARLY-RETURN TUPLE EXCEPTION BUILT + `_parse_variant_def` CONVERTED (2026-07-27, Phase-2 executor) — count 883 -> 882

**VERDICT: the reopen key CONVERTS.** The three measured gaps were built (gap #3 the decisive one,
gaps #1/#2 small); `_parse_variant_def` converts under the standard whole-file-proof gate; the rest of
the early-return refined-tuple cluster is DEFERRED with INDEPENDENT secondary blockers (not the tuple
exception).

### Feature (commit `872635f4`) — per-slot-typed early-return tuple exception
The all-int early-return tuple keeps the legacy arity-keyed `Return_<arity> (int,…)` EXACTLY (byte-
identical). A tuple with ANY non-int slot gets a PER-SLOT-TYPED exception carrying the faithful slot
types, keyed on the slot signature so two arity-N functions with different slot types don't collide.
- **`_tuple_slot_types` / `_tuple_return_exc`** (`functions.py`): split a refined tuple type paren-aware;
  emit `Return_<arity>` for all-int, else `Return_tuple_<arity>_<slot-tokens> (<slot types>)`
  (`re.sub([^A-Za-z0-9]+,_)` token key + arity prefix). Computed IDENTICALLY at the decl, `raise` and
  `catch` sites.
- **Gap #1 slot typing** (`_infer_tuple_slot_type` + `_refine_tuple_return_type`): a `-> str`-call-result
  slot (`ctor = self.expect_name()`) → `string`, a growable string-list slot (`types = [expect_name()]`)
  → `seq string` — reusing the BODY's own `_collect_str_call_result_locals`/`_collect_array_elem_types`
  so the SIGNATURE agrees with the emitted local types (the body already lowered `ctor: ref ""` /
  `types: seq string` correctly; only the signature/exception lagged).
- **Post-map declaration** (`preamble.py::_emit_tuple_return_exceptions`, wired in
  `Module6_WhyMLTranspiler` after BOTH the return-type + return-ANNOTATION maps — a `-> str` self-call
  slot needs the annotation map to resolve to `string`): the non-int tuples are DEFERRED here (parallel
  to `_emit_union_return_exceptions`), the all-int ones stay in `_emit_preamble_exceptions` (unchanged
  position → byte-identical). The scan-time refinement is a reliable BINARY all-int-vs-not classifier;
  a passing corpus tuple is all-int (a non-int slot at emission would already fail the legacy
  `Return_<arity>` L3-tc, so none is in a passing baseline).
- **Gap #2 slot-aware raise value** (`stmt_control_flow.py::_tuple_raise_value`): an empty `[]` in a
  `seq string` slot → `(Seq.empty: Seq.seq string)`, a seq-string local → `!local`.
- **Mirror re-port** (`self-annotate .../module6_whyml/stmt_control_flow.py::_handle_return_stmt`, §10.4):
  the one un-trusted mirror method the live edit touched; drift held at 2.

**GATE S (all green):** FULL corpus byte-diff **0** (812/812 vs baseline) → feature corpus-inert.
MUTATION TEST **PASS**: forcing the `string` scalar slot → `real` moved the emitted exception name AND
payload at the declaration, both `raise` sites AND the `catch` — all four in lockstep (load-bearing, not
a facade). Vacuity `--emit` exit 0 (no new erasure). mirror-check 52/52; drift 2; ledger 3 (no cert;
additive structural).

### CONVERTED `_parse_variant_def` (commit `4ce8e418`, 883 -> 882)
Verbatim live port: `ctor = expect_name(); if at_op("("): advance(); types = [expect_name()]; while
accept_op(","): types.append(expect_name()); expect_op(")"); return (ctor, types); return (ctor, [])`.
The early `(ctor, types)` (inside the `if`) + tail `(ctor, [])` both raise/catch through
`Return_tuple_2_string_seq_string (string, seq string)`; the `[]` slot lowers to `(Seq.empty: seq string)`.
Also strengthens the ALREADY-CONVERTED `expect_op` with the faithful cursor-monotonicity ensures
`self.i >= \old(self.i)` (advance-only, `_err` diverges — the same justification `expect_name` carries):
the if-branch ends in `expect_op(")")`, so without it the caller's own `self.i >= \old` postcondition
havocs (this was the single unproven goal on the first proof pass; the whole-file proof then re-proves
`expect_op` in-file). Whole-file Module2_Parser.py proof **SUCCESS 0-unproven** (FOREGROUND, read, 6m25s);
corpus byte-diff 0; vacuity exit 0; mirror-check 52/52; drift 2; ledger 3.

### Cluster census — DEFERRED members all have INDEPENDENT secondary blockers (not the tuple exception)
- `_parse_datatype` → `DatatypeDecl(name, variants: seq (string, seq string), type_params)`: needs a
  `seq (string, seq string)` LOCAL build + an `IrDatatypeDecl` ctor with that field (pure, no cert) —
  a family-B build, the tuple exception is a prerequisite but not sufficient.
- `_parse_inductive_rules` (`seq (string, emit_ir)`) / `_parse_inductive` (nested): a `seq (…, emit_ir)`
  ctor field of emit_ir is non-strictly-positive (Why3-rejected, the `irlist` wall) → needs a NEW
  certified monomorphic `rule_list` inductive = §10.5 CERTIFIED-BOUNDARY.
- `parse_rocq_assumptions_block` (`tuple[bool, list[str]]`): STRING-OP BOUNDARY —
  `block.splitlines()` + `line.startswith((tuple))` + `line.split(" : ", 1)[0]` are unmodeled string ops.
- pycsl.py `_why3_typecheck` / `_run_vacuity_gate` / `_dispatch_provers` / `_probe_one`: SUBPROCESS/I/O
  BOUNDARY (invoke `subprocess`/why3, parse output) — trusted for I/O, not the tuple exception.

So the feature unblocks EXACTLY `_parse_variant_def` standalone; every other early-return refined-tuple
stub is gated by a distinct boundary. The per-slot-typed early-return tuple exception is banked and
reusable for any future non-int early-return tuple (once its OTHER blockers clear). Zero live-parser
changes; foregrounded every proof; zero orphans; jobs empty.
