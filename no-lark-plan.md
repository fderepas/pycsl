# no-lark-plan.md — Migrate Module2 (the `#@` contract parser) off Lark

**Status:** Plan (awaiting implementation)
**Goal:** Replace the Lark EBNF + Transformer parser in `src/pycsl/frontend/Module2_Parser.py` with a hand-written recursive-descent parser in the `pure_ast` style, so the compiler core has zero 3rd-party dependencies and can self-analyze.
**Blocker being removed:** `lark` is the only 3rd-party import in `src/pycsl/` (Module2_Parser.py:5-6). It blocks PyCSL from analyzing itself (Lark's internals can't be proven).

---

## 0. What Module2 is

`src/pycsl/frontend/Module2_Parser.py` (1779 lines) parses PyCSL contract strings (`#@ requires x > 0`, `#@ ensures \result == y`, `#@ loop invariant ...`, `#@ happy ...`, `#@ act ...`, `#@ assigns ...`) into a `CSLNode` AST tree consumed by Module3/Module5/Module6. It has three parts:

1. **`PYCSL_GRAMMAR`** (lines 949–1376, ~400 lines of EBNF) — the Lark grammar for the contract language.
2. **`PyCSLTransformer`** (lines 1383–1757, 175 methods) — converts Lark's parse tree into `CSLNode` objects. Each method is one grammar rule → one AST node constructor.
3. **`Module2_Parser` class** (lines 1761–1779) — the public API: `parse_contract(str, line) -> CSLNode` and `parse_node_contracts(list, line) -> List[CSLNode]`.
4. **131 `CSLNode` subclasses** (lines 14–948) — the contract AST node classes (`Requires`, `Ensures`, `Assigns`, `LoopInvariant`, `HappyProperty`, `Act`, `ForExpand`, `BinOp`, `Var`, etc.). These are the OUTPUT of the parser, consumed downstream.

**Consumers of the `CSLNode` tree** (these must NOT change): `Module3_Weaver.py`, `Module5_IREmitter.py`, `core_ir_semantic.py`, `module6_whyml/{functions,preamble,statements}.py`, `pure_ast.py`.

---

## 1. The migration principle

**Replace the grammar + transformer with a hand-written recursive-descent parser. Keep everything else identical.**

- The `CSLNode` classes (§0.4) are KEPT UNCHANGED — they are the output contract.
- The `Module2_Parser` public API (`parse_contract`, `parse_node_contracts`) is KEPT UNCHANGED — consumers don't change.
- The Lark `PYCSL_GRAMMAR` EBNF and `PyCSLTransformer` are DELETED — replaced by a hand-written `_ContractParser` class that tokenizes the contract string and builds `CSLNode` trees directly, mirroring how `pure_ast._Parser` works (a token stream + recursive-descent methods + `_fin` position helper).
- The `lark` / `lark.exceptions` imports are DELETED.

The result: Module2 becomes a pure-Python recursive-descent parser with zero 3rd-party deps, in the same style as `pure_ast.py` (which already parses the full Python grammar without Lark).

---

## 2. Why this is mechanical, not risky

The `PyCSLTransformer`'s 175 methods are a 1:1 map from grammar rule to `CSLNode` constructor. Each method is 1–3 lines (e.g. `def precondition(self, expr) -> Ensures: return Ensures(expr)`). A recursive-descent parser replaces each grammar rule with a `def _parse_<rule>(self)` method that does the same construction — the SAME `CSLNode` objects are built, just by direct method calls instead of Lark's rule dispatch.

The contract grammar is much smaller than the Python grammar `pure_ast` already handles:
- No statements, no control flow, no comprehensions, no f-strings — just contract expressions (`requires`/`ensures` clauses, quantifiers, `old`, `assigns` targets, `happy`/`act`/`for` blocks).
- The expression sub-grammar (the hard part of any parser) is ALREADY implemented in `pure_ast._expr` / `_binop` / `_test` — Module2's contract-expression grammar can reuse the SAME precedence/associativity table (`_BINOP` in pure_ast.py:528) and structure.

---

## 3. The plan, step by step

### Step 1 — Tokenizer for contract strings (new, ~60 lines)
Write `_lex_contract(source)` returning a token list, mirroring `pure_ast._lex`. Reuse `tokenize.generate_tokens` (the stdlib pure-Python tokenizer pure_ast already uses). Filter COMMENT/NL/ENCODING. The contract string is a single line, so the token stream is short.

### Step 2 — `_ContractParser` class (new, ~600 lines, mirrors pure_ast._Parser)
A recursive-descent parser over the token list. Methods:
- `_parse_contract` — dispatch on the leading keyword (`requires`/`ensures`/`assigns`/`loop invariant`/`loop variant`/`class invariant`/`function variant`/`happy`/`act`/`for`/`complete`/`disjoint`/`preserves`/`diverges`/`no_inline`/`sibling_concrete`/`propagate_frame`/`fresh_globals`/`trusted`/`abstract`/`lemma`/`uses`/`verify_module`/`interface`/`reveal`/`given`/`footprint`).
- `_parse_expr` — the contract-expression grammar: `Var`, `BinOp`, `UnaryOp`, `Old`, quantifiers (`Forall`/`Exists`), function-call, subscript, attribute, literals, `\\result`, `\\old`, `\\forall`, `\\exists`, `\\length`, `\\valid`, `\\separated`, ghost exprs (`append`/`copy`/`copy_range`/`make`).
- `_parse_assigns_target` — the `assigns` clause target (lvalue with optional `\\at`/`\\old`).
- `_parse_happy_decl` — the `happy` declaration family (the most complex clause: `happy reads/writes/pre/post/total/ni/protects/param`).
- `_parse_act_block` / `_parse_for_block` — the ghost-code blocks.

Each method builds the SAME `CSLNode` the corresponding transformer method built. Position tracking via a `_fin` helper (mirror pure_ast).

### Step 3 — Wire `_ContractParser` into `Module2_Parser`
Replace the `Module2_Parser` class body:
```python
class Module2_Parser:
    def __init__(self) -> None:
        pass  # no Lark parser to build
    def parse_contract(self, contract_str, line_number) -> CSLNode:
        try:
            return _ContractParser(contract_str).parse()
        except _ContractSyntaxError as e:
            raise PyCSLParseError(f"...line {line_number}:\n{contract_str}\n{e}", line=line_number, stage="parse") from e
```
The API is byte-identical; consumers unchanged.

### Step 4 — Delete the Lark layer
- Delete `PYCSL_GRAMMAR` (lines 949–1376).
- Delete `PyCSLTransformer` (lines 1383–1757).
- Delete `from lark import Lark, Transformer, v_args` and `from lark.exceptions import LarkError`.
- Delete `_csl_to_str` if unused (check — it may be used for debug/unparse; if so, keep it, it doesn't depend on Lark).

### Step 5 — Differential test against the old parser
BEFORE deleting the Lark layer, run a differential test: for every `#@` contract in the corpus (`test-suite/corpus/pycsl-reference/*.py`) and in `src/pycsl_lib/`, parse each with BOTH the old Lark parser and the new hand-written parser, and assert the `CSLNode` trees are equal (via a `__eq__` or `repr` comparison). This is the gate: zero mismatches.

### Step 6 — Standing gate
- `bin/run-reference-tests.sh --pycsl` — all green (the corpus proves identically).
- `python3 src/pycsl/pycsl.py src/pycsl_lib/os/__init__.py` — SUCCESS.
- `python3 bin/doc-coherency.py --check` — green.
- Confirm `grep -r "lark" src/pycsl/` returns zero hits — the 3rd-party dep is gone.

---

## 4. Scope boundaries

### In scope
- Module2_Parser.py only — the grammar, the transformer, the parser class.
- A new tokenizer + recursive-descent parser in the same file (or a sibling `module2_rdp.py` if the file gets too large, re-exported from Module2_Parser.py).

### Out of scope
- The `CSLNode` classes (§0.4) — KEPT UNCHANGED (the output contract).
- The `Module2_Parser` public API — KEPT UNCHANGED (consumers don't change).
- `pure_ast.py` — NOT touched (it already works; Module2 reuses its token-stream pattern, not its code).
- The `#@` contract language itself — no syntax changes, just a re-implementation of the same parser.

### Risk
- LOW for the expression sub-grammar (reuse pure_ast's precedence table).
- MEDIUM for the `happy`/`act`/`for` ghost-block family (the most complex clauses — 8 happy variants, act blocks, for-expand). The differential test (Step 5) catches any regression here.
- The migration is purely mechanical: same grammar, same AST nodes, same API — only the parser engine changes.

---

## 5. The self-analysis unlock

After this migration, `src/pycsl/` imports zero 3rd-party modules. The remaining stdlib imports (`tokenize`, `subprocess`, `shutil`, `tempfile`, `hashlib`, etc.) are either pure-Python stdlib (stub-able) or I/O utilities (→ `\abstract` val stubs). The compiler core (frontend + module6_whyml + core_ir_semantic + pycsl.py) becomes analyzable by PyCSL itself — the 29 un-annotated compiler files can then be self-annotated without a Lark stub blocking the proof.

---

## 6. Estimated effort

| Step | Effort | Risk |
|---|---|---|
| 1. Tokenizer | Low — ~60 lines, mirror pure_ast._lex | None |
| 2. _ContractParser | Medium — ~600 lines, mechanical from the 175 transformer methods | Low (differential test gates it) |
| 3. Wire into Module2_Parser | Trivial — ~10 lines | None |
| 4. Delete Lark layer | Trivial — delete + remove imports | None |
| 5. Differential test | Low — one script, runs the corpus | The gate — must be 0 mismatches |
| 6. Standing gate | Trivial — one command | None |

**Total:** ~700 lines of new parser code replacing ~1200 lines of grammar+transformer, ~4–8 hours of agent time. The differential test (Step 5) is the keystone — it proves the new parser produces identical trees before the old one is deleted.
