# FINDING (gen #33, 2026-09-29) — `(any int)` IS A PROGRAM EXPRESSION AND THE EMITTER PUTS IT IN A LOGIC CLAUSE

**Verdict: FAIL-CLOSED (Why3 refuses to parse), but a genuine emitter BUG, and the diagnostic it
produces is the single unhelpful word `syntax error`.**

Gen #32's screen filed one row away from the int-erasure seam with the right comment: *"An emitter
that can emit unparseable output for a legal input is not a modelling gap; it is a bug."* It was never
probed. Reproduced and localised here.

## THE SITE

Porting `frontend/monomorphize.py::_collect_instantiations` emits, at `monomorphize.mlw:600`:

    variant { Array.length (_find_subscript_calls (func_get_2 1070911546 (any int)) !generic_names)
              - !_idx_site }

    File "…/monomorphize.mlw", line 600, characters 78-81:
    syntax error

Characters 78-81 are **`any`**. In Why3 `any τ` is a PROGRAM expression — an effectful "some value of
type τ" — and `variant { … }` / `invariant { … }` are LOGIC TERMS. `any` is not a term, so the clause
cannot parse.

## WHERE THE `(any int)` COMES FROM, AND WHY IT IS SOUND IN ITS OWN PLACE

`expressions.py::_coerce_to_int` answers `(any int)` for an operand it cannot model as an int — a
map-shaped expression, or a genuine tuple, whose own comment says: *"A GENUINE tuple has no int
encoding here that is a function of its VALUE, so it becomes an UNCONSTRAINED int, Why3's `(any int)`
— sound (a key that is merely unknown)."* That reasoning is correct **for a program position**. The
defect is not the placeholder; it is that the SAME lowered text is then copied into the loop's
`variant` and `invariant`, where a program expression is not grammatical.

>>> **A PLACEHOLDER CHOSEN FOR A PROGRAM POSITION IS NOT AUTOMATICALLY LEGAL IN A SPEC POSITION, AND
>>> THE EMITTER REUSES ONE LOWERING FOR BOTH.** The soundness argument for `(any int)` is about what
>>> it DENOTES; the bug is about where it may STAND. Those are different questions and only the first
>>> was asked.

## WHY IT IS NOT A SOUNDNESS ROUTE

Why3 rejects the file outright, so nothing is proved. The cost is a blocked conversion and a
diagnostic that tells the reader nothing: `syntax error`, with no construct named and no advice.

## THE POPULATION IS ONE, AND MY FIRST COUNT SAID TWO

The committed screen has exactly ONE `['syntax error']` row. Gen #32's handoff also named
`_parse_contract` and `_parse_atom_name`, which do not carry that verdict in the committed
`Module2_Parser` screen (an earlier pass). **And my first grep for "syntax error" also matched
`ir_resolve.py::resolve`, whose message contains the phrase inside a REFUSAL'S ADVICE** (*"`#@ shared`
alone is a syntax error"*). That is the fourth loose match to manufacture a candidate in this
generation — read the outlier rows.

## TWO REPAIRS, AND THEY ARE NOT THE SAME SIZE

1. **The honest minimum: diagnose it.** When a lowered expression that will be placed in a `variant`
   or `invariant` contains `any`, REFUSE with a message that names the construct and says the loop
   bound is not expressible — instead of handing Why3 something unparseable and surfacing the word
   `syntax error`. Cheap; owes the LEDGERS lesson (d5) names (witness census, advice audit, and the
   raises ledger if the site has a `\trusted` mirror stub — `once per mirror file that stubs it`).
2. **The faithful fix: hoist.** Bind the bound expression to a local BEFORE the loop and use `!local`
   in the variant — a `ref` read IS a term, so the clause becomes grammatical and keeps the bound.
   Larger, and it changes emitted text for any loop whose bound is a call, so it owes an M1 byte-diff.

Neither is built here. **Recorded with its cause localised to one line and one token**, which is the
part that cost the time.
