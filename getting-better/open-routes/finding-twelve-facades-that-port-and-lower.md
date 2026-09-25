# Eight of the fifty cheap facades PORT AND LOWER — the first path past 460

> **CORRECTED 04:51Z, from twelve to eight.** The screen classified failure by a BLACKLIST of
> error strings — 'PIPELINE ERROR', 'syntax error', 'but is expected', 'unbound ' — and Why3
> has more ways to fail than that. Four of the twelve were false:
>
>     _try, interleave, items_view   "This expression has type int, it cannot be applied"
>     parse_contract                 "this expression raises unlisted exception PyCSLParseError"
>
> The first three take a CALLABLE parameter, which the model carries as `int`. **That is a
> fourth distinct wall** — higher-order arguments — with a population of three here.
>
> This is the same bug as the first screen's missing 'syntax error', in the same session, in a
> script written after that lesson. A blacklist of failure strings is incomplete in the
> dangerous direction by construction. The driver prints a POSITIVE marker —
> `[+] Verification SUCCESS (--no-proof: WhyML generated AND type-checks [L3-tc ✓]...)` — and
> that is the only thing worth matching. All twelve were re-run against it
> (`$S/recheck_ports.sh`, a separate script: never edit a screen that is running).

Generation #31, 2026-09-25T04:35Z.

## What was run

All 50 facade candidates whose LIVE body is ten lines or fewer had that body copied into the
mirror (`port_one.py`, which keeps the mirror's own `def` line and `#@` contract lines and
ABORTS rather than guessing), their `\trusted` marker deleted, and the file emitted in
`--no-proof` mode.

| verdict | count |
|---|---|
| **PORTS + LOWERS** (confirmed against the POSITIVE marker) | **8** |
| reported PORTS+LOWERS by the blacklist, refuted by the positive marker | 4 |
| TYPE error | 32 |
| REFUSED | 5 |
| SYNTAX | 1 |

## The eight

    frontend/Module2_Parser.py     _err          PROVED (whole file, 04:48Z)
    proof2why3/sertop.py           __enter__     PROVED (whole file, 04:27Z)
    frontend/monomorphize.py       _rewrite_call_sites
    frontend/pure_ast.py           error
    frontend/pure_ast.py           iter_fields
    frontend/pure_ast.py           unsupported
    module6_whyml/identifiers.py   stable_hash
    proof2why3/parser.py           __repr__

`__enter__` has already been taken all the way: check 1 clean (11 additive diff lines, no new
`val`), and `[+] Verification SUCCESS!`. It is the existence proof for the other eleven.

`_err`'s check 1 is the most interesting so far — **34 diff lines and ZERO new abstract
operations**, and it converts TWO functions rather than one, because the ported body calls
`_contractparser__cur`, which was sitting unemitted as a `val` and becomes a `let` with it:

    - val _contractparser___err (self: _contractparser) (msg: string) : unit
    + let _contractparser__cur (self: _contractparser) : _tok
    +   ensures { (result = (self.toks[self.i])) }   ... = self.toks[self.i]
    + let _contractparser___err (self: _contractparser) (msg: string) : unit
    +   ensures { false }   raises { ContractSyntaxError }   writes { }
    + = let t = ref {...} in t := (_contractparser__cur self); raise ContractSyntaxError

## Which of them will be trust-DEPENDENT afterwards

Checked statically before any of them is landed, because `errors.py::message` taught this the
expensive way — retiring a marker on a function that CALLS a trusted function relabels it
rather than shrinking the surface:

    _err, _try, error, unsupported                   call NO trusted sibling — the clean ones
    parse_contract       calls trusted `parse`
    _rewrite_call_sites  calls trusted `_rewrite_subscript_calls_in_stmt`
    interleave           calls trusted `next`

The four clean ones are the ones to land first.

## And the 32 that do not

Overwhelmingly the SAME capability the 62 verbatim candidates named: `int` / `string` /
`array.Array.array` / `seq.Seq.seq int`. Two carry a different and interesting message —
`pure_ast.py::_const_value_getter` and `_const_value_setter` fail with

    unbound function or predicate symbol 'self'

because they are MODULE-LEVEL functions that take `self` and are attached to a class
dynamically. That is a third distinct wall, not a variant of the value model, and it has a
population of exactly two.

## What this changes

Before this screen, the campaign's position was: 62 candidates can be retired by a proof, two
of them land, and everything else needs a capability. **The porting tier adds twelve more
candidates that need no capability at all — only a body copied from the file next door.**

That is the first path past 460 that does not run through the value model, and it is entirely
mechanical. The 185 facades with live bodies longer than ten lines have not been screened; on
this hit rate (12 of 50) they are worth screening before anyone budgets the 22,252 lines.

## The whole 235 screened — THIRTEEN port and lower

The remaining 185 facades (live body longer than ten lines) were ported and screened the same
way, and their passes re-checked against the POSITIVE marker:

| verdict, all 235 facades | count |
|---|---|
| **PORT + LOWER, confirmed** | **13** |
| TYPE error (the value model) | 124 |
| REFUSED (mutators, nested lifts, reassignment, dynamic names, ...) | ~40 |
| higher-order / callable argument (`cannot be applied`) | 5 |
| unlisted exception | 2 |
| SYNTAX | 3 |

The five the longer tier adds:

    frontend/pure_ast.py            __instancecheck__
    frontend/pure_ast.py            visit_If
    module6_whyml/expressions.py    _emit_metatype_tags
    proof2why3/from_sexp.py         _find_construct_idx
    proof2why3/sertop.py            _sexp_tokens

`module6_whyml/expressions.py::_emit_metatype_tags` is the one to notice: that file holds 36
facades and 45% of the porting programme's lines, and it has exactly one candidate that ports
and lowers today.

## The final accounting of the 410 strict candidates

    62   VERBATIM      of which 6 lower, 2 land, and the rest need the value model
    235  FACADE        of which 13 port and lower
    105  DIFFERS       not screened; 11 are near-verbatim and would re-port mechanically
    8    AMBIGUOUS

So the reachable surface, TODAY, with no new capability at all, is **2 proved + 13 to
adjudicate = at most 15 markers**, against 460. That is the honest size of the campaign's
current frontier, and it is the first time it has been measured rather than estimated.

Everything else is one of four named walls, in order of population: the string/list/array
**field value model** (124 + 36 = 160 witnesses), the **in-place mutator** refusal, the
**nested-closure lift**, and **higher-order arguments** (5).
