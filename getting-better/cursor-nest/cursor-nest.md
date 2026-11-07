# The `proof2why3` token-cursor nest — state-of-the-art wall report

*Written for an INDEPENDENT reviewer who has never seen the sub-loop's reasoning. Every claim
below is reproducible from the cited command; where a previous window's claim was wrong I say so.*

## 1. Global picture

PyCSL is a deductive verifier for a subset of Python: `#@` contract comments (`requires`,
`ensures`, `assigns`, `loop invariant`, `loop variant`, `\variant`, `class invariant`) are compiled
through a six-module pipeline to WhyML and discharged by Alt-Ergo + Z3 via Why3.

PyCSL is **self-annotated**: `src/self-annotate/src/` is a MIRROR of the live compiler
`src/pycsl/`, and the campaign's metric is the number of `#@ \trusted` stubs left in that mirror —
methods whose contract is *assumed* rather than *proved*. Every conversion must pass three
DISJOINT oracle planes: fidelity (the mirror body is verbatim the live body), whole-file Why3
proof (0 non-Valid), and corpus byte-inertness (emission for the 812-program reference corpus is
unchanged, or the diff is exactly an intended semantic correction and every affected program
re-proves). Axiom ledger must stay at 3.

Count at the time of writing: **639** (`grep -rhF '#@ \trusted' src/self-annotate/src | wc -l`).

## 2. The wall as first seen

`src/self-annotate/src/proof2why3/parser.py` mirrors a recursive-descent parser for the
first-order type-expression surface shared by Rocq, Lean and WhyML axiom bodies. It holds **15**
`\trusted` stubs, **11** of them methods of one token cursor `_Parser`:

    expect  parse_expr  parse_quant  parse_implication  parse_disjunction  parse_conjunction
    parse_comparison  parse_arith_add  parse_arith_mul  parse_atom_application  parse_atom

plus `normalize_surface`, `Token.__repr__`, `lex`, `parse_type_expr`. `peek`, `take` and
`__init__` are already converted. This is the single densest un-converted cluster left.

The previous window reported the first blocker as a `Term`/union typing problem and scoped the
lever as "add a string-form union type alias + honour `@dataclass(frozen=True)`".

## 3. The deeper truth (three corrections to that reading)

**(a) The `term` ADT already exists, immutable, in this very file.** Emitting
`src/self-annotate/src/proof2why3/parser.py` yields `parser.mlw` whose line 19 is already

    type term = App string (list term) | BinOp string term term | BoolLit bool
              | Exists (list string) string term | Forall (list string) string term
              | IntLit int | UnaryOp string term | Unsupported string string | Var string

`needs_term` fires here because the imported `App.pp` method stub triggers
`recognize_term_pp_methods`. `src/self-annotate/src/proof2why3/ir.py` is 0-trusted and already
*builds* it (`mk_arrow_chain__go ... BinOp "->" v_h (mk_arrow_chain__go rest v_conclusion)`).
So the "build a new 9-arm union of immutable records" scope is unnecessary, and honouring
`frozen=True` is MOOT for this target. What is missing is only that (i) the mirror's stub alias
`Term = 0` (ir.py:121) makes every `-> Term` lower to `int`, and (ii) a `BinOp(op, l, r)` call
lowers to a parallel MUTABLE record rather than the ADT constructor. Precedent for (ii) already
exists for the sibling `emit_ir` ADT: `expressions.py::_call_irnode_constructor` (:8320).

**(b) Recursive-method emission already works; MUTUAL recursion did NOT (corrected after Gate R).** A previous window recorded `is_recursive` as a
bare-name matcher that cannot see `self.<name>`. Porting `parse_implication` verbatim emits
`let rec _parser__parse_implication (self: _parser) : int ... variant { Array.length self.toks -
self.pos }`. Both `let rec` and the `#@ \variant` are already correct. **Mutual** recursion was NOT supported, and this
paragraph originally claimed it was, on the strength of READING `functions.py` rather than running it.
The independent Gate-R review refuted it and the driver verified the refutation: the SCC continuation
for PROGRAM functions was emitted as OCaml's `and`, which WhyML rejects outright (`unbound function or
predicate symbol 'g'`, or `unexpected 'variant' clause` when a variant is present). The branch was
DEAD-BUT-WRONG — 0 of 52 mirrors and 0 of 812 corpus programs ever reached it. FIXED (one word,
`and` -> `with`) and pinned by corpus test `0966_mutual_recursion_descent_nest.py`, which proves
SUCCESS with 13/13 sub-goals Valid including both `Variant decrease` goals. So mutual recursion works
NOW, but only because this window fixed it.

**(c) The real obstruction is the SHAPE OF THE NEST, and it was hidden by first-blocker reading.**
The 11 methods form ONE mutual-recursion nest (`parse_expr -> parse_implication -> ... ->
parse_atom -> parse_expr` through the parenthesised-expression rule). The descent chain consumes
NO token, so `\length(self.toks) - self.pos` does NOT decrease along it: a plain integer variant
cannot work, and a LEXICOGRAPHIC variant `(len - pos, <precedence level>)` is mandatory.

## 4. What was actually measured (Gate S spike, PASS)

`getting-better/cursor-nest/cursor-nest-spike.mlw` hand-writes the target representation for a
representative 4-method nest and proves **41/41 sub-goals Valid under Alt-Ergo 2.6.3 alone**
(`why3 prove -a split_vc -P "Alt-Ergo,2.6.3," -t 8`, 0 non-Valid). It exercises simultaneously:
mutual recursion, the lexicographic call variant, a mutable-record `self` with `writes`, the class
invariant `0 <= pos <= Array.length toks` with an auto `by {}` witness, immutable `term`
construction, the `_union_peek_0` Optional carrier, a flag-driven `while`, and `str_eq_op`.

Two annotations are load-bearing and were found only by RUNNING it:
1. the `while` needs a LEXICOGRAPHIC LOOP variant `{ len - pos, (if !continue_ then 1 else 0) }` —
   a plain `len - pos` FAILS `Loop variant decrease` on the flag-clearing exit branches, which
   consume no token;
2. the loop and the postcondition both need `invariant { self.pos >= old self.pos }`, else
   `Variant decrease` and `Postcondition` time out.

**Verdict: the wall is a COST/SCALE boundary, not a correctness one.** The target representation is
sound and provable; what is missing is emitter reach.

## 5. Why MOST of the nest cannot be converted PIECEWISE (corrected after Gate R: 8 of 11, not 11 of 11)

A partial conversion leaves the next level down as a `\trusted` abstract `val`. The driver
separately established (and FIXED, same window) that such a val previously carried NO `writes`
clause, so a caller silently assumed the cursor was unmoved — which is exactly what would let a
partial conversion's variant "prove" vacuously. With the frame honestly declared, a converted
`parse_implication` CANNOT discharge its variant while `parse_disjunction` is trusted, unless the
trusted stub is given a monotonicity postcondition (`ensures self.pos >= \old(self.pos)`) — i.e.
unless the TCB is grown. Therefore for such a member the honest options are exactly two: convert the
WHOLE nest, or grow the assumed interface.

**AMENDED after Gate R (the reviewer supplied a PROVED counter-construction, `piecewise_counter.mlw`).**
The argument above is sound but was OVER-GENERALIZED. It binds only a member that either self-recurses
or runs a loop whose progress depends on a trusted callee. A member with NEITHER — no self-call and no
callee-dependent loop — converts PIECEWISE against honest frames with ZERO TCB growth, and the reviewer
proved one all-Valid. That is roughly 3 of the 11 (`parse_expr`, `parse_quant`, `parse_comparison`);
the other 8 remain genuinely all-or-nothing. This matters for sequencing: those 3 are a legitimate
cheap first slice that does NOT require the full bundle.

## 6. The remaining, precisely-named emitter gaps

**AMENDED after Gate R: this list was INCOMPLETE.** Also required, and not probed by the author:
`" ".join(ty_parts)`; string-set-constant membership tests; KEYWORD-ARGUMENT ADT construction
(`Forall(binders=..., ty=..., body=...)` — the positional `_call_irnode_constructor` path binds by
name but the term route must too); and a STRICT-progress (`>`) postcondition that
`parse_atom_application`'s loop needs from `parse_atom`. A further FACADE HAZARD to gate against:
concrete `self.<m>()` sibling resolution is gated on `_record_array_fields`, so a class whose only
list field is `List[int]` silently degrades to vacuous opaque `self_*_0` vals.

1. `Term` (a module-level string-form union alias in the live source, stubbed `Term = 0` in the
   mirror) must resolve to the existing `term` ADT for returns and locals.
2. A `_call_term_constructor` mapping `BinOp(op, l, r)` -> `(BinOp op l r)` for the 9 ctors, on
   the `_call_irnode_constructor` pattern (spec-driven: `compute_term_adt_spec` already knows the
   ctor set and field order, so no new table and no new certificate).
3. Union-local typing for `Optional[Token]` locals (`t = self.peek()` currently lowers to
   `let t = ref 0` plus the opaque int-hash getters `get_kind`/`get_value` and hashed string
   constants such as `160205502` — a degenerate, value-blind path).
4. ~~A lexicographic `\variant` surface~~ **CLOSED — no new surface needed.** `(<expr>, <ordering>)`
   is a well-founded RELATION, not a tuple; encode the pair as one integer instead,
   `16 * (\length(self.toks) - self.pos) + <level>`. Proved 41/41 in the spike and end-to-end
   through the real surface in corpus test 0966.
5. ~~`\old` inside a `#@ loop invariant`~~ **CLOSED — already supported** and already in use on
   `_parse_lock_order` in the Module2_Parser mirror. (Hazard: loop annotations must PRECEDE the
   `while` line; placed inside the body they are SILENTLY DROPPED.)
6. ~~Exceptions~~ **CLOSED — already supported**: `raise SyntaxError(...)` in a value-returning
   `@mutable_state` method emits `raises { SyntaxError }` (auto-derived) and type-checks.
7. `int(t.value)` **CLOSED** (-> `str_to_int`), and seq accumulation **CLOSED**
   (`args := Seq.snoc !args ...`). **STILL OPEN: `tuple(<seq>)`**, which lowers to the opaque
   `tuple_1 : seq int -> int` and so int-erases the accumulator at the `App string (list term)`
   ctor slot.

## 7. Honest limits of this report

**Correction of record:** an earlier revision of §5 stated the frame-soundness defect was "FIXED, same
window" while the fix existed only in detached worktrees. That was premature. As of this revision the
`and` -> `with` mutual-recursion fix IS landed; the frame fix (L14) is gated but NOT yet landed.

- The spike covers 4 methods, not 11; items 6 and 7 are NOT exercised by it. A reviewer should
  regard "the whole nest is provable" as SUPPORTED for the control-flow/termination/ADT core and
  UNMEASURED for the exception and list-accumulator arms.
- Item 4 is a documentation reading, not a measurement.
- The payoff (11-15 stubs) assumes every member converts; a single member that cannot leaves the
  rest blocked, because the nest is all-or-nothing (section 5).
