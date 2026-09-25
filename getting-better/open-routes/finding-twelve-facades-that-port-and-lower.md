# Twelve of the fifty cheap facades PORT AND LOWER — the first path past 460

Generation #31, 2026-09-25T04:35Z.

## What was run

All 50 facade candidates whose LIVE body is ten lines or fewer had that body copied into the
mirror (`port_one.py`, which keeps the mirror's own `def` line and `#@` contract lines and
ABORTS rather than guessing), their `\trusted` marker deleted, and the file emitted in
`--no-proof` mode.

| verdict | count |
|---|---|
| **PORTS + LOWERS** | **12** |
| TYPE error | 32 |
| REFUSED | 5 |
| SYNTAX | 1 |

## The twelve

    frontend/Module2_Parser.py     _err                  frontend/pure_ast.py   error
    frontend/Module2_Parser.py     _try                  frontend/pure_ast.py   interleave
    frontend/Module2_Parser.py     parse_contract        frontend/pure_ast.py   items_view
    frontend/monomorphize.py       _rewrite_call_sites   frontend/pure_ast.py   iter_fields
    module6_whyml/identifiers.py   stable_hash           frontend/pure_ast.py   unsupported
    proof2why3/parser.py           __repr__              proof2why3/sertop.py   __enter__

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
