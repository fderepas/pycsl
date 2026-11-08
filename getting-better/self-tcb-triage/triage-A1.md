# Triage A1 — src/self-annotate/src/frontend/pure_ast.py (262 `\trusted` matches → 261 real stubs)

Transcription source: `src/pycsl/frontend/pure_ast.py` (3827 lines).
(262 raw `\trusted` grep hits; 1 is the module-docstring prose reference at line 4 → **261 real stubs**.)

## What this file IS
A near-verbatim reimplementation of the CPython `ast` module: AST node-class factory (`_build_nodes`,
`_NODE_SPEC`, metaclass `_ABC`), a `tokenize`-backed lexer (`_lex`/`comments`), a **recursive-descent
parser** `_Parser` (~110 mutually-recursive methods building AST nodes), tree helpers (`walk`,
`iter_fields`, `dump`, `literal_eval`, `copy_location`…), `NodeVisitor`/`NodeTransformer`, and a full
**`_Unparser`** (~108 mutually-recursive `visit_*` methods emitting source into a string buffer).

The file is a **single monolithic hard-architectural block**. Its irreducible root blocker is an
**AST-node value ADT** (~90 node types with typed fields) + **mutual recursion over that ADT**. Layered
on top: an external `tokenize` dependency, a `_Tok` token-record list, dynamic `getattr`/`setattr`/`type()`
metaprogramming, and Python generators (`yield`). Essentially **no cheap wins** here.

## Classification (bulk by family)

| family (stub range) | #stubs | bucket | reason |
|---|---|---|---|
| AST/metaclass infra: `AST.__init__/__repr__`, `_build_nodes`, `_const_value_getter/_setter`, `_ABC.__instancecheck__`, `_new`, `Ellipsis.__new__`, `_N` | 9 | hard-architectural | dynamic `type()` class synthesis, `*args/**kwargs`, `zip(_fields, args)` + `setattr`, `getattr` dispatch — metaprogramming, no value model |
| token/lex infra: `_Tok.__init__/__repr__`, `_lex`, `Comment.__init__/__repr__`, `comments`, `_is_aug` | 7 | hard-architectural | external `_tokenize.generate_tokens` (opaque), `_Tok` record list, tuple positions, `.encode` byte-offset math; `comments` is a generator |
| `_Parser.*` (all methods `_slice`…`_fstring_format_spec`) | 110 | hard-architectural | reads `self.toks[self.i]` (`_Tok` record list) + builds AST nodes via `_N(...)`/`self.node` + **mutual recursion**; variadic `*vals`; opaque `_tokenize.*` constants. Even the 1-line predicates (`_stmt_end`, `_name_str`, `_testlist_end`, `_looks_like_type_alias`) read `self.cur().type` → same token+node model |
| string/number decode: `_parse_number`, `_decode_string`, `_decode_escapes`, `_merge_str_constants`, `_set_ctx` | 5 | hard-architectural | `chr`, `int(s, base)`, `.encode('latin-1')`, str\|bytes / int\|float\|complex **union returns**; `_set_ctx` recurses over AST; `_merge_str_constants` mutates `Constant` nodes |
| `_decode_fstring_middle` | 1 | hard-architectural (ordering) | trivial wrapper but calls still-`\trusted` `_decode_escapes` (itself hard) → not a leaf |
| char-iteration string helpers: `_pad_whitespace`, `_fstring_prefix_raw`, `_splitlines_no_ff` | 3 | **needs-recognizer:char-iteration-over-str** | pure str→str / str→list[str]; no AST/token. Blocked on `for c in s` / `s[i]` char-iteration + `c in '<strlit>'` membership (emits `str_contains_op` needing `String.length`/`String.substring` import). SPOT-CHECKED `_pad_whitespace` → fails |
| tree helpers: `parse`, `literal_eval`, `iter_fields`, `iter_child_nodes`, `walk`, `get_docstring`, `copy_location`, `fix_missing_locations`, `increment_lineno`, `dump`, `get_source_segment` | 11 | hard-architectural | AST recursion + generators (`iter_fields`/`walk`) + `getattr(node, field)` + `node._fields`; `dump`/`literal_eval` are recursive over the node ADT |
| `NodeVisitor.visit/generic_visit/visit_Constant`, `NodeTransformer.generic_visit` | 4 | hard-architectural | `getattr(self, 'visit_'+type(node).__name__)` dynamic dispatch + AST recursion |
| `_Unparser.*` (`next`, `__init__`, `interleave`…`visit_MatchOr`) | 108 | hard-architectural | recurse over node ADT, emit into `self._source` list buffer via variadic `self.write(*text)`, precedence stack, generators; `visit_*` are mutually recursive |
| closers: `unparse`, `_self_test`, `main` | 3 | hard-architectural | wrap `_Unparser`/`_Parser`; `main` is CLI/argparse |

Bulk summary: **`_Parser.*` (110) + `_Unparser.*` (108) + tree/visitor/infra (40) = all needs-recognizer:AST-node-value-model,
except the 3 pure char-iteration string helpers (needs-recognizer:char-iteration-over-str) and 0 trivial-leaf.**

## Per-bucket counts
- **trivial-leaf: 0**  (batch-convertible now: **0** — no cheap wins in this file)
- **needs-recognizer: 3**  (all one feature: char-iteration over a `str` param)
- **hard-architectural: 258**
- **floor: 0**  (nothing here is a recursion leaf or D2 axiom; it is architecturally blocked, not irreducible)

## Feature fan-out (this group)
| feature (blocker) | #stubs | example stubs |
|---|---|---|
| AST-node value ADT + mutual recursion over it | ~230 | all `_Parser.*` (110), all `_Unparser.*` (108), `walk`, `literal_eval`, `dump`, `_set_ctx` |
| external `tokenize` module + `_Tok` record list (subset of above, parser/lexer side) | ~117 | `_lex`, `comments`, `_is_aug`, every `_Parser` token accessor (`peek/cur/advance/at_op/…`) |
| dynamic `getattr`/`setattr`/`type()` metaprogramming | ~16 | `AST.__init__`, `_build_nodes`, `_N`, `NodeVisitor.visit`, `dump`, `iter_fields` |
| generators / `yield` | 4 | `iter_fields`, `iter_child_nodes`, `walk`, `comments` |
| str↔number union parse (`chr`/`int(s,base)`, str\|bytes / int\|float\|complex) | 3 | `_parse_number`, `_decode_string`, `_decode_escapes` |
| **char-iteration over a str param (`for c in s`/`s[i]`) + `c in '<strlit>'` membership** | 3 | `_pad_whitespace`, `_fstring_prefix_raw`, `_splitlines_no_ff` |

## Spot-check log
- `_pad_whitespace` ported verbatim + `requires True/ensures True/assigns \nothing` → `--no-proof` type-check
  **FAILED**: `pure_ast.mlw:38 unbound function or predicate symbol 'String.length'` inside the emitted
  `str_contains_op` (triggered by `c in '\f\t'`). Preamble lacks `use string.String`. Reverted clean
  (`git checkout`), removed stray `.mlw`. Confirms the char-iteration string family is NOT trivial.

## Uncertain
- `_splitlines_no_ff` / `_fstring_prefix_raw` classified needs-recognizer by static analogy to the
  spot-checked `_pad_whitespace` (same char-iteration + str-membership shape). `_splitlines_no_ff` also
  builds a `list[str]` with char-index lookahead, so it may need a *second* feature (list-of-string
  build) → borderline hard; confidence medium.

## Bottom line for the orchestrator
This file yields **zero batch-convertible trivial-leaf stubs**. 258/261 are gated behind the same
`ast`-module architecture (an AST-node value ADT + mutual recursion), which is a real modeling feature,
not a recognizer. The only sub-architectural opportunity is a **single bounded recognizer — char-iteration
over a `str` param + fixing `str_contains_op`'s `String` import — which would unblock exactly 3 pure-string
helpers** (`_pad_whitespace`, `_fstring_prefix_raw`, and likely `_splitlines_no_ff`). Not worth prioritizing
over other files unless that recognizer pays off broadly elsewhere.
