# The postcondition frontier is bound by the CONTRACT LANGUAGE, not by the prover

Generation #31, 2026-09-26T12:20Z. Written at the point where the postcondition line stopped
paying, so that the next generation does not re-walk it.

## Where the line got to

    functional postconditions   146  ->  237 of 922 converted mirror functions (16% -> 26%)

in three sittings: 19 by hand in six cheap files, 72 by removing ONE spec-language wall
(`\result["<key>"]` on an `emit_ir`-returning constructor, backlog #60a), and 0 from the fourth
attempt. **Every remaining candidate I examined is blocked by the contract language, and not
one of them is blocked by the prover.** Four limits, each located and each measured with a
one-production probe:

| # | limit | probe | blocks |
|---|---|---|---|
| #60a | a dict subscript on `\result` was `unbound symbol 'subscript_get'` | — | **REMOVED** — 72 IR constructors |
| #60b | the grammar has NO METHOD CALL, only a bare-name call | `\result == self._e(node.list, lr)` → `unexpected trailing input ('(')` | every emitter mixin handler — hundreds |
| #60c | only `.keys()/.values()/.items()` are recognised | `name.strip() in ALLOWLIST` → named refusal (07-1311) | the two kernel-axiom allowlist predicates, `_clean`, `_method_key` |
| #60d | NO module-level constant is in scope; the scope is exactly the parameters | `OP_MAP` → `Available variables in scope: ['op']` | every lookup-table function: `op_translate`, `triggers_for`, `all_phase1_exceptions` |

## And two of the three remaining walls are behind a PURITY analysis, not a grammar

This is the part worth carrying, because it is not obvious and it cost one grep to find.

Suppose #60b's production existed. The clause `\result == self._deref(self._e(node.list, lr))`
would lower to an application of `ghostcollectionopsmixin___deref` — and that function is
emitted

    let ghostcollectionopsmixin___deref …            NOT `let function`

a PROGRAM function, which cannot appear in a logical term at all. So the clause would fail
L3-tc with `unbound function or predicate symbol` — **the same wall #60a hit, one level up.**
Measured across the emitted mirror: **1323 of 3091 definitions are `let function` (pure) and
1768 are not, and every `ensures True` handler is in the second group.**

The same is true of #60d for DICT constants: a module dict is emitted as an opaque
`val constant <NAME> : int`, so admitting the name into scope buys an opaque clause, not a
faithful one. (A SET constant with literal members is the exception — `x in <SET>` has an
exact, pure, axiom-free lowering as a disjunction of string equalities — and that is the only
part of #60d worth building.)

So the honest shape of the frontier is:

    the cheap postconditions are DONE
    the next tranche needs `scc.emits_as_logic_symbol` to extend to the emitter's own
      mixin methods — a PURITY ANALYSIS, which is a different and much larger build
    two small grammar gaps (#60c `.strip()`, #60d set constants) are worth a few functions
      each and should be CENSUSED before either is built

## What already works, and is the cheapest thing left

A BARE-NAME call to a function that IS emitted `let function` parses and proves today:

    #@ ensures \result == ir_get_str(node, "op", "")      PARSES · L3-tc ✓ · PROVED

because `module6_whyml/irx.py`'s accessors are pure. **Any module-level pure helper can carry a
compositional postcondition right now, with no capability at all.** That is where a next
generation should look first, and the census is one grep: intersect the `ensures True`
population with the `let function` symbols in the emitted mirror. Done here: 27 module-level
pure functions carry `ensures True`, and of those, the ones whose postcondition needs only
parameters and bare-name pure calls are the landable set.

## The methodological point

Three of the four walls were found by writing the postcondition I wanted and reading the error,
at a cost of about a minute each — no proof, no gate, no scratch tree. **A capability question
answered by a one-production probe is worth more than the same question answered by a design
argument, and this generation got the ratio wrong twice before getting it right** (the FIELD
value model was declared a 174-witness wall by inspection and turned out to be already built;
the string closure was predicted to retire many and retired one of 103).
