# parser-primitives-wall.md — the pure_ast token-stream parser primitives (highest-COUNT wall)

**For review. State-of-the-art report on the highest-COUNT trusted-stub concentration: `pure_ast.py` (262 stubs =
25% of the whole trusted core). This report targets its cheapest shared cluster — the ~10-16 recursive-descent
parser PRIMITIVES — which convert together from ONE token/parser-record model.**

## 1. Global picture
PyCSL lowers annotated Python to WhyML discharged by Why3/SMT; the self-annotation effort drives its `#@ \trusted`
stub count DOWN. Count is **1013**; ledger **3** (must stay 3). Prior runs built the value-model ADT cascade
(pyval/reflection-node/Set[str]/const-reflection), converting a handful of deep Module5 collectors (each ~10
node-reflection pieces — low count-ROI). REDIRECT: attack the highest-COUNT concentration instead.
`frontend/pure_ast.py` — a pure-Python reimplementation of the stdlib `ast` module (tokenizer + recursive-descent
parser + AST node hierarchy) — holds **262** trusted stubs (25% of 1013). They cluster: ~16 parser PRIMITIVES,
~50+ `visit_X` unparse methods, ~50+ grammar parse-rules, node dunders, lexer. This report targets the CHEAPEST
high-count cluster: the parser primitives, which share ONE model.

## 2. The wall — first seen
The `Parser` class primitives navigate a token stream:
```python
class _Tok: __slots__ = ("type", "string", "start", "end")   # type:int, string:str, start/end:pos-tuples
class Parser:
    def __init__(self, toks, ...): self.toks = toks; self.i = 0
    def peek(self, k=0):  j = self.i + k; return self.toks[j] if j < len(self.toks) else self.toks[-1]
    def cur(self):        return self.toks[self.i]
    def advance(self):    t = self.toks[self.i]; if self.i < len(self.toks)-1: self.i += 1; return t
    def at_op(self, *vals):   t = self.cur(); return t.type == _tokenize.OP and t.string in vals
    def accept_op(self, val): if self.at_op(val): return self.advance(); return None
    # + at_name/at_kw/accept_kw/expect_op/expect_kw ...
```
Each currently int-erases: `self.toks` → `ref 0`, `self.i` → opaque, `self.toks[self.i]` → int-array index,
`t.type`/`t.string` → opaque getters (int-hash), `t.string in vals` → `contains_check (str_hash_op …)`. So all
~16 primitives are `\trusted`.

## 3. The deeper truth — a modeling choice, NOT a fundamental limit
`_Tok` is a RECORD (`type:int`, `string:string`, `start`/`end`); `self.toks` is a `seq _Tok` (or `array`) self-field;
`self.i` is an `int` self-field. The primitives are: list-index (`self.toks[self.i]` → `Seq.get`), record-field
projection (`t.type`/`t.string`), int/string compare (`t.type = OP`, reuse `str_eq_op` for `t.string in vals`),
index mutation (`self.i += 1` → a field write). PyCSL already models RECORDS + stateful `@mutable_state` self-fields
(the mutex/inode subsystems; K1's seq-pyval self-field). This is the STATEFUL-PARSER-RECORD analogue — a record ADT
+ a `seq record` self-field + int self-field, all over sound existing theory. No char-level parsing here (the
primitives operate on the ALREADY-tokenized `self.toks` list — the char-level `_lex` is a SEPARATE, harder cluster).

## 4. SOTA lens — the stateful record + a token-record seq-field
The precedent is direct: PyCSL models `@mutable_state` records with field writes + class invariants, and K1 modelled
a `seq pyval` self-field with faithful append. Here: a `_Tok` record (fields type/string/start/end) + a `seq _Tok`
self-field `toks` + an `int` self-field `i` + `Seq.get`/`Seq.length` list-index. The NEW capability is a
record-typed seq self-field with index-read + a token-record projector set — one model, ~10-16 primitives.

## 5. Honestly-costed routes
- **R-parser (make-or-break): the `_Tok` record + a `seq _Tok` `toks` self-field + `int` `i` self-field + the
  primitive recognisers** (list-index `self.toks[self.i+k]` → `Seq.get toks (i+k)`; `t.type`/`t.string` → record
  projectors; `t.type == OP` → int-eq; `t.string in vals` → `str_eq_op` disjunction [HAVE]; `self.i += 1` → field
  write). Co-land an axiom-free cert IF a new value shape (the `_Tok` record is a plain record — likely reuses the
  existing record machinery, no new cert). Fixture-witness (commit the model + a fixture, then convert the cluster).
  Convert the clean primitives (`peek`/`cur`/`advance`/`at_op`/`at_name`/`at_kw`/`accept_op`/`accept_kw`/`expect_op`/
  `expect_kw` — ~10) first; `_slice`/`_fin`/`error`/`unsupported` carry extra bits (source-line slicing / raises),
  assess per-stub.
- **Deferred (harder clusters):** the ~50 grammar parse-rules (tokens→node, need the AST-node construction model),
  the ~50 `visit_X` unparse (node→string), the char-level `_lex`. Not this increment.

## 6. Honest limits + certificate
The risk is EMISSION + the bounds-guarded list index, not the model: (a) does `self.toks : seq _Tok` self-field emit
(the fieldless-mirror-retrofit / stateful-record shape — K1/K6 precedent) + `Seq.get toks !i` typecheck? (b) the
`self.toks[-1]` / `self.toks[self.i]` reads need an in-bounds guard or a total `Seq.get` — verify no OOB proof
obligation the fixed `ensures True` shape can't discharge; (c) `_Tok` reuses the record machinery (no new axiom;
ledger 3). Each is a spike question.

## 7. The make-or-break question for review
Does a `_Tok` RECORD (`type:int; string:string; start:int; end:int`) + a `seq _Tok` self-field `toks` + an `int`
self-field `i` model the primitives `cur = Seq.get toks i`, `at_op vals = (tok_type (cur) = OP) && str_mem (tok_string
(cur)) vals`, `advance = i := i+1; Seq.get toks i` — **typecheck and PROVE non-vacuously** (a built token seq reads
back the right token/field; an evil-twin field read fails), **axiom-free** (ledger 3), with the `self.toks[self.i]`
index NOT forcing an unprovable OOB obligation under `ensures True`? **An oracle run — a hand `.mlw` with a `_tok`
record, a `seq _tok`, `Seq.get`, a driver proving `tok_string (Seq.get toks 0) = "("` for a built stream ∧ an
evil-twin mismatch fails, `why3 prove -P z3`, + an axiom check — should CONFIRM or REFUTE before any emitter edit.**
