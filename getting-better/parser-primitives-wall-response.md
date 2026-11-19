# parser-primitives-wall-response.md — Gate R independent review

**Verdict: CONFIRM (build viable).** The `_tok` record + `seq _tok` self-field + `int` index model of §7
typechecks in Why3, proves the field/`at_op` goals **Valid and non-vacuously** (the evil twin fails on two
provers), stays **axiom-free / ledger-clean**, and — the make-or-break §6b OOB question — `Seq.get` in a
PROGRAM `let` function under `requires True` **discharges with NO out-of-bounds proof obligation**.

Oracle: `/tmp/claude-1346829620/-home-fabrice-derepas-canonical-com-git-pycsl/9dd932d0-43ec-4eaf-b2b4-3686bbb5f588/scratchpad/parser-oracle.mlw`
(a copy is quoted below so the review survives scratchpad cleanup).

## What was modeled (faithful to §7)
- `type tok = { tok_type:int; tok_string:string; tok_start:int; tok_end:int }` — the `_Tok` record.
- `built_stream : seq tok` = `Seq.cons {OP,"("} (Seq.cons {NAME,"x"} Seq.empty)` — a concrete 2-token stream.
- `cur toks i = Seq.get toks i`; `at_op1 toks i v0 = (tok_type (Seq.get toks i) = op_const) /\ tok_string(...) = v0`
  (string membership as a str-eq disjunction, exactly the report's `str_eq_op` reuse).
- Kind constants are **concrete** literals (`op_const = 54`, `name_const = 1`, real tokenize codes) so their
  distinctness — needed by `at_op_false` — is *proven*, not axiomatized. This is what keeps the model ledger-clean;
  had they been `val constant` + `axiom distinct`, the ledger would have moved. The emitter must likewise lower
  token kinds to concrete int literals, not abstract vals.
- `cur_prog`/`peek_prog` re-expressed as PROGRAM `let` functions with the *fixed* contract shape
  `requires { true } ensures { true }` — the exact shape the wall is constrained to.

## Oracle output, goal by goal (`why3 prove -P z3`, cross-checked `-P alt-ergo`)

| Goal | Meaning | z3 | alt-ergo |
|------|---------|-----|----------|
| `cur_field` | `tok_string (cur built_stream 0) = "("` (field projects faithfully) | **Valid** (0.01s) | — |
| `at_op_true` | `at_op1 built_stream 0 "("` (OP token matches) | **Valid** (0.01s) | — |
| `at_op_false` | `not (at_op1 built_stream 1 "(")` (NAME@1 is not op "(") | **Valid** (0.01s) | — |
| `evil_twin` | `tok_string (cur built_stream 0) = "wrong"` — MUST NOT prove | **Unknown** (1.02s) | **Timeout** (5s) |
| `cur_prog'vc` | program `Seq.get toks i` under `requires True` | **Valid** (0.01s) | **Valid** (0.04s) |
| `peek_prog'vc` | program bounds-if + `Seq.get` under `requires True` | **Valid** (0.01s) | **Valid** (0.04s) |

Raw z3 lines:
```
Goal cur_field.   Prover result is: Valid (0.01s, 13756 steps).
Goal at_op_true.  Prover result is: Valid (0.01s, 13790 steps).
Goal at_op_false. Prover result is: Valid (0.01s, 14637 steps).
Goal evil_twin.   Prover result is: Unknown (unknown) (1.02s, 769814 steps).
Goal cur_prog'vc. Prover result is: Valid (0.01s, 543 steps).
Goal peek_prog'vc.Prover result is: Valid (0.01s, 543 steps).
```

## The make-or-break resolution (§6b — the OOB question)
`cur_prog'vc` and `peek_prog'vc` are **Valid under `requires { true }`**. In Why3's `seq.Seq`, the accessor
`Seq.get` / `([])` is a **total logic function** — it has no in-bounds precondition, so using it in program
position emits **no OOB verification condition**. The fixed `requires True / ensures True` contract shape the
wall is locked to therefore fully discharges the `self.toks[self.i]` / `self.toks[self.i+k]` reads. **No bounds
guard, no total-accessor wrapper, no forbidden `requires` is needed for the model to typecheck and prove.**

## Non-vacuity
`evil_twin` (`... = "wrong"`) is **Unknown on z3 and Timeout on alt-ergo** — it does *not* prove. The three
positive goals are therefore proving real content, not riding a vacuous/false context. `at_op_false` further shows
the model discriminates *between distinct tokens* (index 1 ≠ op "("), so the projectors are not collapsing.

## Axiom / ledger check
`grep -nE '^\s*(axiom|val )' parser-oracle.mlw` → **NONE**. Only `int.Int`, `seq.Seq`, `string.String` (Why3
stdlib) are used; the `tok` record and `Seq.get` are constructive. **Ledger-neutral — stays at 3**, provided the
emitter follows the concrete-kind-constant rule below.

## Conditions the emitter must honor (else CONFIRM degrades)
1. **Concrete int literals for token kinds** (`OP`, `NAME`, …). If they are emitted as abstract `val constant`s,
   `at_op_false`-style discrimination needs a distinctness *axiom* and the ledger moves off 3. The oracle proves
   the goals *only* because the kinds are concrete.
2. **Faithfulness caveat (not blocking, worth a note):** because `Seq.get` is total, an OOB read returns an
   *unspecified* token silently rather than raising `IndexError`. That is sound and harmless under the wall's
   `ensures True` (type-safety+frame) contract shape — which is all §7 claims — but the emitted primitives will
   **not** model Python's `IndexError` on OOB. If a later increment tightens these primitives to functional
   contracts that must witness the OOB path, a bounds guard / `IndexError`-raise would have to be added *then*.
   For the present cluster (peek/cur/advance/at_op/at_name/at_kw/accept_op/accept_kw/expect_op/expect_kw under the
   fixed shape) this is a non-issue.

## Bottom line
§7's central bet holds under a run oracle: **record + `seq record` self-field + `Seq.get`/projectors/str-eq
disjunction typechecks, proves non-vacuously, is axiom-free, and the OOB obligation is dischargeable under
`requires True`.** The ~10 clean primitives are viable to convert together on this model. Proceed to the emitter
spike, honoring condition (1).

---
### Oracle source (`parser-oracle.mlw`)
```why3
module ParserOracle
  use int.Int
  use seq.Seq
  use string.String

  type tok = { tok_type:int; tok_string:string; tok_start:int; tok_end:int }

  constant op_const   : int = 54
  constant name_const : int = 1

  function built_stream : seq tok =
    Seq.cons { tok_type=op_const;   tok_string="("; tok_start=0; tok_end=1 }
   (Seq.cons { tok_type=name_const; tok_string="x"; tok_start=1; tok_end=2 }
    (Seq.empty : seq tok))

  function cur (toks: seq tok) (i: int) : tok = Seq.get toks i
  predicate str_mem1 (s v0: string) = (s = v0)
  predicate at_op1 (toks: seq tok) (i: int) (v0: string) =
    (tok_type (Seq.get toks i) = op_const) /\ str_mem1 (tok_string (Seq.get toks i)) v0

  goal cur_field   : tok_string (cur built_stream 0) = "("
  goal at_op_true  : at_op1 built_stream 0 "("
  goal at_op_false : not (at_op1 built_stream 1 "(")
  goal evil_twin   : tok_string (cur built_stream 0) = "wrong"   (* must NOT prove *)

  let cur_prog (toks: seq tok) (i: int) : tok
    requires { true } ensures { true }
  = Seq.get toks i

  let peek_prog (toks: seq tok) (i: int) (k: int) : tok
    requires { true } ensures { true }
  = if i + k < Seq.length toks then Seq.get toks (i + k)
    else Seq.get toks (Seq.length toks - 1)
end
```
