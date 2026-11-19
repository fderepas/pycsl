# Response to the Term-rewriter wall — independent external review

*Independent reviewer, 2026-07-11. Evidence base: Why3 1.8.2 (Alt-Ergo 2.6.2, Z3 4.13.3), run by
me on a hand-written spike; plus a direct read of the two emitter files the report cites. I did
not consult any prior campaign material beyond the report itself. No source file was edited; no
commit was made. The spike is left in place at
`getting-better/composition-wall/term-rewriter-spike.mlw` for the coordinator to re-verify.*

---

## 1. The report's §3 framing — agree, with one correction

**Agree** that the open question is well-posed and that (C)+(L)+(T) *jointly* is the right unit of
doubt: readers over the ADT are demonstrated, constructors exist in Why3, and the only honest
uncertainty was whether construction, the list-child map, and structural termination *compose*
under an SMT-discharged contract with no axiom. That is exactly the question a hand `.mlw` can
answer, and §7's insistence that a prose-only review adds nothing is correct.

**One correction to §3/§4.1:** the claim "the emit_ir ADT is used only for *reads*; no emitter
path emits a constructor application" is slightly too strong. See §4 below — a narrow
constructor-emission path already exists (`_lower_irnode_construction`), but only for five
leaf-ish kinds and only from inline dict literals, so the *substantive* claim (no converted
method constructs a recursive Term and returns it; no dataclass-ctor → WhyML-ctor path) stands.

## 2. The spike — oracle evidence

### 2.1 What I wrote

`/home/fabrice.derepas@canonical.com/git/pycsl/getting-better/composition-wall/term-rewriter-spike.mlw`
— a single module, hand-written, containing:

- `type term = Var string | IntLit int | Binop string term term | App string (list term) | Unary string term`
  — both a fixed-arity recursive constructor (`Binop`) and the report's fault line (L), a
  **list-of-children** constructor (`App` over `list term`).
- A mutually-recursive structural measure `size : term -> int` (`ensures { result >= 1 }`) `with`
  `size_list : list term -> int` (`ensures { result >= 0 }`), each with a *structural* variant
  (`variant { t }` / `variant { l }`); `size_list (Cons x rest) = 1 + size x + size_list rest`.
- The §4.3 element-of-list-child decrease, **as a proved `let rec lemma`, not an axiom**:
  `size_mem : mem x l -> size x < size_list l`, plus the corollary
  `lemma size_app_child : mem x args -> size x < size (App h args)`.
- The rewriter itself — the report's §2 `_flip_comparisons` witness shape verbatim:
  `let rec flip (t: term) : term requires { true } ensures { true } variant { size t }`
  (leaves identity; `Binop` REBUILT with args swapped under an abstract `is_cmp`/`flip_op`
  table; `Unary` rebuilt; `App h (flip_list args)`), `with`
  `flip_list (l: list term) : list term variant { size_list l }` mapping `flip` down the list
  and REBUILDING it with `Cons`.
- **No `axiom` anywhere.** The only unaxiomatized symbols are the two abstract `val function`s
  (`is_cmp`, `flip_op`), which carry zero assumed properties — they only stand in for the
  `_FLIP_COMPARISON` dict, whose content is irrelevant to the type-safety+frame contract shape.

### 2.2 Full prover output

`cd /home/fabrice.derepas@canonical.com/git/pycsl && why3 prove -P alt-ergo getting-better/composition-wall/term-rewriter-spike.mlw`:

```
Warning, file "getting-better/composition-wall/term-rewriter-spike.mlw", line 95, characters 15-19: unused variable result
Warning, file "getting-better/composition-wall/term-rewriter-spike.mlw", line 81, characters 15-19: unused variable result
File getting-better/composition-wall/term-rewriter-spike.mlw:
Goal size'vc.
Prover result is: Valid (0.06s, 302 steps).

File getting-better/composition-wall/term-rewriter-spike.mlw:
Goal size_list'vc.
Prover result is: Valid (0.04s, 51 steps).

File getting-better/composition-wall/term-rewriter-spike.mlw:
Goal size_mem'vc.
Prover result is: Valid (0.05s, 93 steps).

File "getting-better/composition-wall/term-rewriter-spike.mlw", line 65, character 4 to line 66, character 46:
Goal size_app_child.
Prover result is: Valid (0.04s, 14 steps).

File getting-better/composition-wall/term-rewriter-spike.mlw:
Goal flip'vc.
Prover result is: Valid (0.04s, 80 steps).

File getting-better/composition-wall/term-rewriter-spike.mlw:
Goal flip_list'vc.
Prover result is: Valid (0.03s, 29 steps).
```

**6/6 Valid, all under 0.1 s.** (The two warnings are the harmless `ensures { true }` on the
rewriter pair — the mandated contract shape mentions no `result`.)

Cross-check, `why3 prove -P z3` on the same file: **6/6 Valid** as well
(`size'vc` 0.02s / 20559 steps, `size_list'vc` 0.01s, `size_mem'vc` 0.01s, `size_app_child`
0.02s, `flip'vc` 0.01s / 15545 steps, `flip_list'vc` 0.01s). No goal needed a fallback prover,
a transformation, or an interactive step.

**Negative control (oracle non-vacuity).** I mutated the leaf case to the non-terminating
`| Var v -> flip (Var v)` (scratchpad copy, not the committed spike): `flip'vc` then fails —
`Prover result is: Timeout (5.00s, 22619 steps)` — as it must, since `size (Var v) < size (Var v)`
is false. The termination check is real, not rubber-stamped.

**Robustness probe (measure shape).** A variant of the spike with the *bare-sum* measure
(`size_list (Cons x rest) = size x + size_list rest`, no `+1` per cons) still discharges
`flip'vc`/`flip_list'vc` — Why3's lexicographic clique rule accepts the non-strict
`size x <= size_list (Cons x rest)` on the `flip_list -> flip` call because `flip` is earlier in
the `with`-clique. But the *strict* element lemma `size_mem` then correctly fails (it is false
for a singleton list under the bare sum: `size x < size x + 0`). Consequence for the emitter: the
generated list measure should count cons cells (`1 +` per element) if the strict element-decrease
lemma is wanted as a standalone reusable fact; the rewriter's own termination is robust to either
measure.

### 2.3 Per-fault-line verdict

| Fault line | Verdict | Evidence |
|---|---|---|
| **(C) construction** | **PASS** | `flip` builds `Var v`, `IntLit n`, `Unary op (flip a)`, both `Binop` forms (including the swapped-args comparison flip), and `App h (flip_list args)`, and returns them; `flip'vc` Valid on both provers. Why3 variant constructors are first-class in programs; nothing about *constructing* resisted. |
| **(L) list-child map** | **PASS** | `flip_list` type-checks (`list term -> list term`), rebuilds the list with `Cons (flip x) (flip_list rest)`, composes with the constructor (`App h (flip_list args)`), and `flip_list'vc` is Valid. The report's §4.2 worry does not bite: the child list is a *pure* `list term` inside an immutable variant — the `array (seq τ)` mutable-element rejection is about mutable containers and is irrelevant here. Python's `tuple(...)` result is itself immutable, so the pure `list`/`seq` lowering is also the *faithful* one. |
| **(T) termination** | **PASS** | `variant { size t }` / `variant { size_list l }` discharge with no axiom. The element-of-list-child decrease that §4.3 flagged as the suspected hard lemma is provable **without an axiom and without interactive induction**: as the termination VC it is immediate (the recursion threads through `flip_list`, so each step only needs head-decrease + arithmetic on the measure's defining equations), and even the general strict form (`mem x args -> size x < size (App h args)`) discharges as a `let rec lemma` (induction expressed as a recursive program whose VCs are plain SMT goals — `size_mem'vc` Valid, 93 steps). |

The one *shape* requirement the spike surfaced: the naive single `variant { size t }` cannot be
placed on a lone function that recurses into the list "directly" — the map must be a (mutually)
recursive helper carrying its own `variant { size_list l }`, and the measure must be the mutually
recursive `size`/`size_list` pair. That is precisely the "standard fix" the review brief
anticipated, and it discharges instantly. It is a code-generation shape, not a proof obstacle.

## 3. VERDICT: bounded feature, not a boundary

**A total, structurally-terminating `Term -> Term` rewriter is a BOUNDED FEATURE.** Every VC of
the report's minimal witness shape — construction, swapped-args rebuild, list-child map with list
rebuild, termination over the input subtree, element-of-list decrease — discharges in Why3 in
milliseconds, on two independent SMT solvers, with zero axioms, zero interactive proof, zero
transformations. Nothing in (C)/(L)/(T) resists; the proof side of this wall does not exist. The
whole residual cost is **emitter work** — making PyCSL *generate* this WhyML from the verbatim
Python. The smallest sufficient capability set, keyed to what I verified is missing (§4):

1. **Recursive-constructor emission**: extend the existing constructor path (see §4 — today only
   `IrVar/IrAttr/IrStr/IrNum/IrRaw` from inline `{"type": K, ...}` dict literals via
   `_IRNODE_CTORS`, expressions.py:661) to (a) constructors whose payloads are recursive-call
   results (`Binop op (flip l) (flip r)`), and (b) the mirror's actual Python surface — frozen
   **dataclass constructor calls** (`App(head=..., args=...)`), which is a Call node, not a dict
   literal, so it needs its own recognizer.
2. **Comprehension-over-recursive-ADT lowering**: lower `tuple(f(a) for a in t.args)` to a
   generated mutually-recursive helper (`flip_list` shape: its own `variant { size_list l }`,
   `Cons (f x) (helper rest)`) — or an equivalent proven map combinator — whose result type
   (`list term`) feeds the constructor. This is the only genuinely new emission *shape*.
3. **The list-leg of the measure**: emit the `size`/`size_list` mutually-recursive pair (with
   `1 +` per cons, per §2.2's robustness probe) next to the existing `size`, plus (optionally,
   for reuse) the `size_mem`-style `let rec lemma` — all proven in the spike, nothing axiomatic.
4. **`emit_ir`-typed returns** for the rewriter methods (params already lower as
   `(x: emit_ir)` — functions.py:140; return-side typing exists only in slot-shaped traces).

Route 1 of the report's §6 is the right one; route 2 (opaque result) is indeed vacuous and route 3
(accept the boundary) is now refuted by the oracle. Per the coupling rule the report cites, note a
constructed-Term value introduces no new WhyML *value shape* — it is the same `emit_ir`-style
variant the read-only ADT already certified — but that judgment call belongs to the campaign.

## 4. Sanity-check findings

**§3's "reads only" claim — substantively confirmed, one nuance.** In
`src/pycsl/module6_whyml/preamble.py::_emit_exprir_theory` (line 3234) the `emit_ir` theory is
constructors + `kind_of` + `is_*` discriminants + total projectors (`left_of`, `right_of`,
`body_of`, `orelse_of`, `args`…) + `size` + proven size-decrease lemmas — a read-oriented
apparatus. But in `src/pycsl/module6_whyml/expressions.py` there IS a constructor-emission path:
`_IRNODE_CTORS` (line 661) + `_lower_irnode_construction` (line 1267) lower an inline Python dict
literal `{"type": "Var", "name": e}` to the WhyML constructor application `(IrVar <e>)` — for
exactly five kinds (`Var/Attribute/String/Number/RawWhyml`) plus an `(IrOther "<kind>")`
fallback. So "no emitter path emits a constructor application" is false in the letter; what is
true, and is what the wall actually needs, is: (a) the *recursive* expression-family constructors
(`IrBinOp`, `IrIfExpr`, `IrCall`, `IrSub`, `IrTuple`) are absent from `_IRNODE_CTORS` — a
`{"type": "BinOp", ...}` literal today collapses to `(IrOther "BinOp")`, losing the sub-nodes;
(b) nothing lowers a Python *dataclass constructor call* (`App(...)`, `BinOp(...)` — the
`proof2why3` Term surface) to a WhyML constructor; (c) I found no converted method that
constructs a Term/emit_ir value from recursive results and *returns* it. The report's exact §3
sentence ("no converted method constructs an emit_ir/Term value and returns it") is accurate.
Helpfully, the existing 5-kind path means constructor emission is an *extension in kind already
proven in the codebase*, not a from-scratch mechanism.

**§5's SOTA claim — confirmed, and it undersells the answer.** Yes: `Term -> Term` by structural
recursion is textbook proof-assistant territory (in Rocq/Lean the recursion principle makes
termination automatic), and Dafny/F* handle datatype-to-datatype functions with `decreases`. The
open question really was the SMT/contract setting. The spike shows that setting is *sufficient*
here: Why3's VC generator does all the structural/lexicographic bookkeeping, and the residual SMT
goals are trivial linear arithmetic over the measure's defining equations — no interactive
induction is needed anywhere, and even the one induction-shaped side fact (element-of-list
decrease) is expressible as a `let rec lemma` whose VCs remain plain SMT goals.

## 5. Honest limits of this review

- **The spike proves the WhyML target shape, not the emitter path.** It establishes that IF PyCSL
  emits this shape from `_flip_comparisons`, Why3 discharges it. Building emitter capabilities
  1–4 (§3) and holding byte-diff-0 on the corpus is real, unspiked work; the campaign's usual
  risks (recognizer precision, additivity) live there, not in Why3.
- **5 constructors, not 9.** I modeled the report's required subset (incl. both fault-line
  shapes). `Forall(binders, ty, body)` adds a *binder list* (likely `list string` — non-recursive,
  strictly easier than `list term`); `substitute`/`_alpha_rename` carry an *environment* argument
  through the recursion, which changes contracts but not the (C)/(L)/(T) skeleton. `_ac_normalize`
  (if it sorts/flattens argument lists) may need list-manipulation lemmas beyond a plain map — the
  *hardest* family member was not spiked, only the report's named minimal witness.
- The contract proved is exactly the campaign's stated shape (type-safety + termination;
  `ensures { true }`) — I make no claim about functional-correctness contracts (e.g.
  size-preservation or semantics-preservation), which were not asked.
- The flip table was abstracted (`val function is_cmp/flip_op`, no axioms); the real
  `_FLIP_COMPARISON` dict lookup must lower through PyCSL's existing dict/string machinery —
  routine, but unverified by me.
- Environment: Why3 1.8.2 / Alt-Ergo 2.6.2 / Z3 4.13.3, as installed in this repo's toolchain.

**Process attestations:** I ran the oracle myself (all outputs above are verbatim). I edited no
source file; the only files I created are the spike `.mlw` (left in place at
`getting-better/composition-wall/term-rewriter-spike.mlw`) and this response; scratch probes
(bare-sum measure, negative control) live in the session scratchpad, outside the repo. I made no
commit.
