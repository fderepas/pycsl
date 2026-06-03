# Level up the agents: 0-`\trusted` stdlib stubs as policy + the language reach to verify the literal demos

## Context

Across Phases 1–4 the delegate kept shipping stubs that fail verification, and each time
the reflex was to hand-patch one stub. The user's standing principle: **the durable fix
belongs in the agent + the skills + the toolchain, not in per-stub patches** — and stdlib
stubs should be body-verified with **zero `\trusted`**, modeled concretely like
`unix-filesystem/*.py`.

Two facts from exploration shape everything:
1. **The current policy mandates the opposite.** `pycsl-annotate/references/forbidden-expressions.md`
   *explicitly permits* `\trusted` "for library stubs in `src/pycsl_lib/`",
   `stdlib-stub-awareness.md` says "each stub declares `#@ \trusted`", and
   **`bin/generate_lib_stubs.py:324` emits `#@ \trusted` + `return 0` by default.** So
   `ast.py`'s 15 `\trusted` are by-design, not an oversight. The guideline *reverses* this.
2. **The exemplar reaches 0 `\trusted` via concrete state + cited axioms.**
   `unix-filesystem/UnixInodeFileSystem.py` (835 lines, 0 `\trusted`) body-verifies its
   logic and cites named `#@ proof rocq/lean` lemmas (`UnixFs.Struct.i18.round_trip`,
   `UnixFs.Bitmap.bit_and_one_in_zero_one`) for irreducibly-opaque ops. **"0 trusted" ≠
   "0 axioms"** — the opaque core is an explicit, auditable set of cited lemmas.

**Decisions (from clarifying questions):** render the demos **literally** by *extending
PyCSL* (load-bearing) so they verify; handle the opaque boundary with **Rocq/Lean axiom
citations**; make enforcement **fully durable** (skills + generator + gate lint).

**The idiom that replaces `\trusted`** (verified in the emitter): an **abstract `val`**
(bodyless, uninterpreted — `module6_whyml/abstract_ops.py:_add_abstract_op`) carrying an
`ensures` that is pinned by a named lemma in `preamble.py:_AXIOM_REGISTRY`. This is sound,
opaque, auditable, and is a *different code path* from `\trusted` (`Module3_Weaver` `csl_trusted`).
Every "opaque but 0-trusted" boundary below uses this idiom.

**Outcome:** (1) policy flipped + mechanically enforced (stdlib stubs body-verified by
default); (2) PyCSL extended so the literal NodeVisitor / string-predicate / `literal_eval`
demos verify with 0 `\trusted`; (3) the io-StringIO + ast-check_code + literal_eval demos
land as worked, *verified* exemplars.

---

## Part A — Durable policy & enforcement (the spine; do this first)

- **A1. NEW `config/skills/agent-stdlib-annotate/SKILL.md`** (the dir has only `references/`
  today). Canonical guideline: *stdlib stubs are body-verified with 0 `\trusted`; model
  state concretely (point to `unix-filesystem/UnixInodeFileSystem.py` + corpus 0427/0428);
  for an irreducibly-opaque kernel use an abstract `val` + a named `#@ proof rocq/lean`
  citation registered in `_AXIOM_REGISTRY` — never `\trusted`; every stub ships a
  property-proving `<mod>_demo.py`.* Add `agent-stdlib-annotate` to the L2/L3/L5 rows of
  `project-lifecycle/references/competency-matrix.md` so the delegate receives it.
- **A2. Reverse the contradicting guidance** (one focused edit each):
  - `pycsl-annotate/references/forbidden-expressions.md` — drop the "permitted for
    `src/pycsl_lib/` stubs" carve-out; forbid `\trusted` on stubs; point to the abstract-val
    + axiom-citation idiom.
  - `pycsl-annotate/references/stdlib-stub-awareness.md` — "each stub declares `\trusted`"
    → "each stub is body-verified; opaque ops cite Rocq/Lean".
- **A3. `bin/generate_lib_stubs.py`** — stop emitting `#@ \trusted` by default. Most generated
  stubs are `return 0` under `ensures \result >= 0`, which **already proves** without trust —
  so dropping the `\trusted` line is sufficient for them. Emit a `# TODO: body-verify or cite
  axiom` marker (not `\trusted`) only where the inferred contract isn't trivially provable.
- **A4. NEW gate lint `bin/check-no-trusted-stubs.py`** — fail if any `src/pycsl_lib/**/*.py`
  contains `#@ \trusted`. Wire it into `bin/cmmi-audit.sh` and the supervisor
  `feature_supervisor/gate.py` GATE_STEPS. Makes the policy mechanical, not aspirational.
  *(Scope: hard-fail on the phase's target stub + warn-only tree-wide initially — see Scope.)*
- **A5. Delegate** — extend `feature_supervisor/delegation.py:_PYCSL_SYNTAX_CHEAT` with the
  policy line ("stdlib stubs: 0 `\trusted`; opaque kernels use an abstract call + `#@ proof
  rocq/lean` citation").

## Part B — Language extensions so the LITERAL demos verify (load-bearing; each ends in a corpus test under `hoare`)

Per the reference-corpus convention, each milestone adds a `test-suite/corpus/pycsl-reference/NNNN.py`.

- **B1 — `ast.NodeVisitor` inheritance (effort S).** Inheritance already works
  (`pycsl.py:_apply_inheritance`, corpus 0443/0444/0445). Two gaps: (a) `class X(ast.NodeVisitor)`
  records the base as an `ast.Attribute`, which `Module5_IREmitter.py:~1117` drops (only
  `ast.Name` captured) → widen to take `b.attr` (~3 lines); (b) ship a PyCSL-defined
  `NodeVisitor` base **in `src/pycsl_lib/ast.py`** with static `visit`/`generic_visit` + an
  abstract dispatch `val`, so the existing monomorphizer merges it. Corpus **0446**.
  *Honest limit:* reflective `getattr(self,'visit_'+name)` routing is modeled as one opaque
  dispatch `val` — the demo's class/override contracts are proven, MRO routing is the cited
  boundary.
- **B2 — string predicates `.islower()/.startswith()/.endswith()` (effort S).** Add a dispatch
  branch in `module6_whyml/expressions.py:_handle_call_expr` (mirror the `isinstance` branch)
  emitting an abstract `val str_islower (s:int):int ensures { result=0 \/ result=1 }` etc.
  (return `int` 0/1, not `bool`). No axiom for the minimal case. Corpus **0447**. *Honest limit:*
  predicates are uninterpreted — design demo VCs to depend on the *control-flow consequence*
  of the predicate, not its concrete truth value.
- **B3 — `ast.literal_eval` + dict/list result + `raises ValueError` (effort M, L tail).**
  Reuse the existing `map int (option int)` ghost-dict model. Emit an abstract
  `val literal_eval_safe (src:int) : (int, map int (option int))` returning `(status, value)`;
  the malicious branch (`status=0`) raises `ValueError` through the existing `raises` machinery;
  pin parse-safety with a cited axiom `Pycsl.Ast.LiteralEval.malicious_raises` in
  `_AXIOM_REGISTRY`/`_AXIOM_FUNCTIONS`, and teach `ir_scanner.py` that `literal_eval` is a
  map-producer (pull in `use map.Map`/`use option.Option`). Corpus **0448**. *L-tail risk:*
  a tuple carrying a map may need a new `Return_<arity>` variant (current path assumes int
  components) — validate early. *Honest limit:* the security claim ("`literal_eval` is safe
  where `eval` is not") **is** the cited axiom; PyCSL does not model Python's parser.
- **B4 — the remaining surface the literal `## Formal test drivers` code uses (effort S–M).**
  The pasted drivers need three more constructs beyond B1–B3:
  - **`super().__init__()`** — `super()` calls in `__init__`. Model as a no-op/identity into
    the inherited init (the base `NodeVisitor.__init__` sets no verified state), or desugar to
    the base-init call during the inheritance pass. (`Module5_IREmitter` ctor handling + `_apply_inheritance`.)
  - **`SyntaxError` + tuple-of-exceptions handlers** — add `SyntaxError` to
    `exception_model.py:KNOWN_EXCEPTIONS` (both copies: `src/pycsl/` and `src/self-annotate/src/`),
    and support `except (ValueError, SyntaxError):` (multi-type handler) in `Module5` try
    parsing + `module6_whyml/statements.py` `try…with`.
  - **`print(...)` + f-strings + `type(x)`** — these are runtime decoration, not verifiable
    content. Model `print`/f-string/`type` as abstract no-op `val`s (side-effect-free,
    `assigns \nothing`) so the demo parses and verifies, OR keep them out of the proven surface.
    Decide one policy and document it in the SKILL.md (A1).
  Corpus **0449** (super + multi-except). *Honest limit:* `print`/`type` carry no proof value;
  they're tolerated, not verified.

Sequence 1 → 2 → 3 → 4 (2 establishes the typed-abstract-op-with-`ensures` pattern that 3 reuses;
4 is independent and can land alongside C3).

## Part C — The demos as verified exemplars (acceptance)

- **C1. `io.py`** — add a body-verified `StringIO` class (Buffer: `array int` content + `pos`;
  `write` appends via Array.blit, `getvalue` returns the `[0:pos]` slice, `close`), 0 `\trusted`
  (corpus 0427/0428 pattern). **`io_demo.py`** — the literal StringIO example (`StringIO()`,
  two `.write(...)`, `.getvalue()`, `.close()`), verifiable. (Feasible today — needs no Part B.)
- **C2. `ast.py` → 0 `\trusted`. ✅ DONE.** All 14 `#@ \trusted` directives removed; `check-no-trusted-stubs --strict` passes; `pycsl ast.py` verifies. The stateful `NodeVisitorObj`/`NodeTransformerObj` methods are body-verified (their `self._visited += 1` body proves `ensures self._visited == \old + 1`; malformed contract indentation fixed); the trivial module functions drop `\trusted` (`return 0` proves `ensures True`; `fix_missing_locations`/`copy_location` `return` their arg to prove `\result == node`/`new_node`); the irreducibly-opaque parsers `parse` and `literal_eval` are `#@ \abstract` vals with bounded raises sets (`parse`: `ensures \result >= 0` + `raises SyntaxError`; `literal_eval`: `raises ValueError`/`SyntaxError`). No `#@ proof` axiom was added — as for `literal_eval` (B3), there is no honest non-trivial Why3 fact about the parsed value; the bounded-raises spec + cite-comments are the auditable boundary. `ast_demo.demo_parse` updated to the total safe-parse pattern (`try ast.parse … except SyntaxError: return -1`) since `parse` now raises.
- **C3. `ast_demo.py`** — the two literal drivers from the `## Formal test drivers` section,
  rendered as **annotated functions with contracts** (the `os_demo.py` template — a formal
  driver is `requires/ensures/assigns`-bearing functions, NOT a module-level `print` script;
  keep the literal bodies, but the "formal test" is the contract on the enclosing function).
  - **`check_code`** (FunctionAnalyzer over B1 NodeVisitor + `visit_FunctionDef` + B2 string
    predicates). **What is actually proven:** the analyzer's *logic* — `ensures \result == 0 or
    \result == 1`, and that `everything_fine` ends 1 **iff** every visited `FunctionDef` name
    is `islower ∨ dunder`. The concrete `check_code(source_code) == 1` for the section's
    specific string is **not** a Why3 proof (it rests on the opaque `ast.parse` of that string)
    — surface it as a runtime `assert` and/or a cited parse-fact axiom, the same opacity
    boundary as `literal_eval`. Do NOT write the acceptance as "proves `== 1`" — write it as
    "proves the analyzer is correct; the string outcome is runtime/cited", or the gate claim
    overstates what's proven.
  - **`literal_eval` safety** (via B3): prove the malicious path raises `ValueError` (cited
    axiom) and the safe path returns a dict whose `['threshold']` reads back; `print`/`type`
    (B4) are tolerated runtime decoration.
  `pycsl ast_demo.py exits 0`.

## Critical files
- `config/skills/agent-stdlib-annotate/SKILL.md` (NEW), `…/references/coding-llm-prompt.md`
- `config/skills/pycsl-annotate/references/{forbidden-expressions,stdlib-stub-awareness}.md`
- `config/skills/project-lifecycle/references/competency-matrix.md`
- `bin/generate_lib_stubs.py`; `bin/check-no-trusted-stubs.py` (NEW); `bin/cmmi-audit.sh`; `feature_supervisor/gate.py`; `feature_supervisor/delegation.py`
- `src/pycsl/Module5_IREmitter.py` (base capture, ctor/`super`, multi-except try), `src/pycsl/module6_whyml/{expressions.py,preamble.py,ir_scanner.py,statements.py}`, `src/pycsl/pycsl.py` (`_apply_inheritance`)
- `src/pycsl/exception_model.py` + `src/self-annotate/src/exception_model.py` (add `SyntaxError` to `KNOWN_EXCEPTIONS`, both copies)
- `src/pycsl_lib/{ast.py,io.py,ast_demo.py,io_demo.py}`
- `test-suite/corpus/pycsl-reference/0446.py, 0447.py, 0448.py, 0449.py` (NEW)

## Verification
- Each Part-B milestone: its corpus test verifies under `hoare`; broad corpus regression unaffected.
- `pycsl` on `io.py`, `io_demo.py`, `ast.py`, `ast_demo.py` → "Verification SUCCESS";
  `grep -c '\trusted' src/pycsl_lib/{io,ast,io_demo,ast_demo}.py` == 0.
- `bin/check-no-trusted-stubs.py` passes on the touched modules; cited axioms registered in
  `_AXIOM_REGISTRY` (real lemmas, like the existing i18/bit_and entries).
- `CMMI_AUDIT_NESTED=1 bin/cmmi-audit.sh` → 9/0; agent test-suite green; the new gate step green.
- End-to-end: a `--allow-load-bearing --allow-llm-delegation` run reaches past Phase 3.

## Scope, sequencing & honest caveats
- **Large + load-bearing** (Module2/3/5/6 + grammar + skills + generator + gate). Do Part A
  first (cheap, high-leverage), then B1→B2→B3 each as an independently-mergeable load-bearing
  change with review, then C. C1 (io StringIO) can ship immediately — it needs no Part B.
- **"0 trusted" is bounded by cited axioms** at genuine opacity (NodeVisitor dispatch routing,
  `literal_eval` parse safety, string-predicate truth values) — the unix-filesystem standard.
  Those axioms are the auditable trusted core; they must be REAL, cross-validated lemmas, not
  rubber stamps.
- **Tree-wide enforcement is a migration.** ~270 generated stubs are `\trusted`-by-default;
  flipping all at once is out of scope. The gate lint hard-fails on the *phase's target* stub
  and warns tree-wide; full migration is a follow-up.
- **Out of scope:** faithful modeling of Python's parser / MRO (that's what the axioms stand
  in for); the B3 tuple-of-map `Return` plumbing if it proves L-sized (cut to a status-int +
  separate map accessor if so).

## Formal test drivers

### Usage example
Change `pycsl/src/pycsl_lib/ast_demo.py` to formally test that `check_code(source_code)` return 1:
```
import ast

# The source code we want to analyze
source_code = """
def calculate_total(price, tax):
    return price + (price * tax)

def greet_user(name):
    print(f"Hello, {name}")

class Invoice:
    def __init__(self, amount):
        self.amount = amount
        
    def process_payment(self):
        pass
"""

# 1. Create the custom Visitor class with a state tracker
class FunctionAnalyzer(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        # Assume everything is fine until proven otherwise
        self.everything_fine = True

    def visit_FunctionDef(self, node):
        # RULE: Check if the function name contains uppercase letters 
        # (Excluding standard dunder methods like __init__)
        if not node.name.islower() and not (node.name.startswith('__') and node.name.endswith('__')):
            self.everything_fine = False
        
        # Continue traversing down into child nodes
        self.generic_visit(node)

# 2. Wrap the execution in a function so it can return 1 or 0
#@ requires source == source_code
#@ ensures \result == 1
def check_code(source):
    try:
        tree = ast.parse(source)
        analyzer = FunctionAnalyzer()
        analyzer.visit(tree)
        
        # Return 1 if the flag remained True, otherwise 0
        return 1 if analyzer.everything_fine else 0
        
    except SyntaxError:
        # If the code can't even be parsed, it's not fine
        return 0
```

### JSON example
Here is another example I want you to add in `pycsl/src/pycsl_lib/ast_demo.py` on JSON parsing:
```
import ast

# A string received from an untrusted source
user_input = "{'status': 'active', 'threshold': 42, 'flags': [True, False]}"

# Equivalent formal driver: pin the input, assert the parsed threshold.
#@ requires data == user_input
#@ ensures \result == 42
def get_threshold(data):
    data_dict = ast.literal_eval(data)
    return data_dict['threshold']

# Safe evaluation
try:
    data_dict = ast.literal_eval(user_input)
    print(type(data_dict))  # Output: <class 'dict'>
    print(data_dict['threshold'])  # Output: 42
except (ValueError, SyntaxError):
    print("Malformed string! Cannot safely evaluate.")

# Why it's safe: If someone tries to inject malicious code...
malicious_input = "__import__('os').system('rm -rf /')"
try:
    ast.literal_eval(malicious_input)
except ValueError:
    print("Blocked malicious input!")  # This will trigger, keeping your system safe.
```


---

## Execution status & re-sequencing (live)

**Merged to `main`:**
- **Part A** (`41d261f`) — 0-`\trusted` policy + enforcement (generator, SKILL.md, skill-doc reversals, `check-no-trusted-stubs.py` + gate wiring, delegate cheat).
- **Method-call contract fix** (`ca80087`) — a driver that constructs an object and calls its **own** method now gets the method's `ensures` (corpus 0446). The prerequisite for all class-based demos.
- **B2** (`171842e`) — string predicates `islower/startswith/endswith/…` → `0|1`-constrained op (corpus 0447).

**Four diagnosed sub-gaps (each its own milestone):**
- **B1 — cross-module inherited-method merge. ✅ DONE.** `class FunctionAnalyzer(ast.NodeVisitor)` with the base in `src/pycsl_lib/ast.py` + a driver calling the inherited `a.visit(n)` now verifies (corpus **0448**), 0 `\trusted`. The real blocker was *not* the merge logic: **a field-less class is modeled as `type X = int`, not a record**, so it could never be a base in `_apply_inheritance`'s `records` dict and its `self.method()` wouldn't resolve. Three edits: (1) gave `NodeVisitor` a concrete `_depth` field + invariant (makes it a record; mirrored in corpus `multi_file_lib/visitor_base.py`); (2) widened Module5 base-capture (~line 1117) to take dotted `ast.Attribute` bases (`b.attr`); (3) new `pycsl._resolve_imported_base_classes` (Layer A′) injects a base referenced via a *module* import (`import ast; class X(ast.NodeVisitor)`) — the `from`-import path already handled `from ast import NodeVisitor`. `_apply_inheritance` was already correct once the base was a record. Same-file inheritance (0443/0444) unchanged; full corpus regression = 0 new failures (the 29 reds are all pre-existing: missing `multi_file_lib.arith`/`rel_helper` + annotation-reference tests).
- **B3 — `ast.literal_eval` safety as an `#@ \abstract` val. ✅ DONE (scoped).** New `#@ \abstract` directive (Module2/3/5 + `functions.py`): emits a bodyless WhyML `val` defined solely by its contract — sound (uninterpreted), and crucially **NOT `\trusted`** (no unchecked body), so it passes `check-no-trusted-stubs`. `ast.literal_eval` is now modeled this way with a bounded raises set (`raises ValueError`/`SyntaxError`), 0 `\trusted`. Corpus **0449** proves the real security property: a `try/except (ValueError, SyntaxError)` wrapper is **TOTAL** for *every* input — it never propagates an exception or runs code (the catch is load-bearing; dropping a handled type fails verification). Also fixed `preamble.py` to declare exceptions named only in a `raises` *contract* (not just bodies). **Two deliberate scope cuts (decided with the user):** (a) the tuple-of-map return `(int, map int (option int))` is the L-sized plumbing the plan pre-authorized cutting — tuple slots homogenize to `int` and dict-return-from-call has emitter bugs (param reorder, map-typed local); the **dict read-back** (`data_dict['threshold']`) is **deferred** to a later increment. (b) **No `_AXIOM_REGISTRY` entry** was added: any axiom about the parsed *value* would either model Python's parser (forbidden) or be a tautology/rubber-stamp (which this plan forbids) — the honest 0-trusted safety model is the abstract val's bounded raises-set + documented `cite:` provenance, not a fake Why3 axiom. The `==42` `get_threshold` overclaim is dropped per the plan's own acceptance guidance.
- **B4 — `super().__init__()`, `SyntaxError`, `print`/f-strings/`type`. ✅ DONE (lock + doc; no emitter change).** Every construct already lowered correctly — B4 is a regression-lock + policy decision, corpus **0450**: (1) `super().__init__()` on a subclass of an *imported* base (builds on B1) verifies, inherited init + merged invariant hold; (2) `SyntaxError` is a first-class *explicit* exception (raise/handler/multi-type) via B3's raises-contract machinery — deliberately **NOT** added to `exception_model.KNOWN_EXCEPTIONS`, which is reserved for exceptions with a mathematical *implicit trigger* (the literal B4 sub-item predated B3 and would have violated that invariant); (3) `print`/f-strings/`type` are **tolerated decoration** — no proof obligation, no `assigns` effect, must not feed proven content — policy documented in the agent-stdlib-annotate SKILL. **Deferred to C3:** constructing a record/map/array local *inside a `try` body* mistypes it as `int` (`_handle_try_stmt` pre-declares every try-assigned var as `ref 0`) — the same try/nested-block local-typing family as the deferred B3 dict read-back; `check_code` builds `analyzer = FunctionAnalyzer()` inside its `try`, so C3 must fix this (type-aware default ref initializers).
- **C1 string-content** — the int-model `Buffer` StringIO is verifiable now (method-call fix), but the *literal* `write("Line 1\n")` form needs string-content modeling (writing string literals) — a separate extension beyond B2's predicates.

- **Try-body local typing. ✅ DONE.** `_handle_try_stmt` pre-declared every try-assigned local as `let v = ref 0 in` (int), which type-errored a record/dict local constructed inside a `try`. Now each try-local is classified from its first assignment (`_try_local_decl_kind`, IR-only): **record/array** → skip the outer ref (let-bound in the body, sound when used within the try, as `check_code`'s `analyzer` is); **dict** → `ref (const (None: option int))` (empty map); **else** → `ref 0` (unchanged). Identical output for int locals (zero regression on the common path); fixes `analyzer = FunctionAnalyzer()` inside a `try` (C3's `check_code`) and `d = {}` / dict-returning calls inside a `try` (B3 read-back groundwork). Corpus regression-locked via 0450's `check`-shape probe. *Remaining for C3:* `ast.parse` returning a usable tree + `node.name` string-attribute access; *for B3 read-back:* `d[k] = v` subscript assignment (still unsupported, corpus 0338) + `literal_eval` returning a dict.

- **String-content / C1 (byte form). ✅ DONE.** str literals lower to an opaque hash (no content); **bytes literals lower to char-code arrays** (full content), so the content model is byte-based. Delivered a body-verified `io.BytesIO` (0 `\trusted`) whose `roundtrip` proves the write→read-back round trip `\array_eq(\result, data)`, and `io_demo.py`'s `demo_bytesio_roundtrip` discharges it from a **driver** (cross-module, `from io import BytesIO`). Corpus **0452** (self-contained). Two reusable emitter fixes: **(#2)** record construction from a driver now builds type-correct field defaults — a `list`/array field → `Array.make <len> 0` (len captured by `Module5._array_init_size` from a literal `bytearray(N)`/`[v]*N`/list), a dict/set field → empty map — not the int `0` fallback that broke `\length` invariants; **(#3)** a method's array/param-referencing result-ensures (`\array_eq(\result, data)`) now propagates to the call site (`_build_method_param_result_ensures_map`, params renamed to the stub's `x_i`), extending B1's int-only propagation. *Honest limits:* the literal **str** `write("...")` form is NOT delivered — str content would need a global str→array change (blast radius on str-as-opaque-hash); contracts can't name a `b"..."` literal (byte literals aren't in the contract grammar) so the proof is the universal `\array_eq(\result, payload)` (stronger than one literal); a module-qualified `io.BytesIO()` isn't resolved to the record (use the `from`-import form); cross-call `write(...)`/`getvalue()` content-chaining (field state across calls) is unsupported — the single-call `roundtrip` carries the proof. The `_array_init_size` size capture handles literal sizes only (a module-constant `bytearray(CAP)` is not resolved — use a literal).

**Re-sequenced remainder:** ~~B1~~ → ~~B3~~ → ~~B4~~ → ~~try-body local typing~~ → ~~string-content / C1 (byte form)~~ → ~~C2 (`ast.py` → 0 `\trusted`)~~ → **C3** (next — `ast_demo` check_code + literal_eval; remaining: `node.name` string-attribute access, `d[k]=v` subscript assignment, `literal_eval` returning a dict). New reusable primitives now available: the `#@ \abstract` directive (B3), type-correct try-body locals, type-correct record-field defaults from a driver (#2), and array/param result-ensures propagation (#3).
