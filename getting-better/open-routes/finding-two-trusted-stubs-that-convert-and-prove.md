# TWO `\trusted` stubs that convert and prove — measured, not landed

**Status: MEASURED, READY TO LAND.** The first movement of this campaign's headline number
that has been demonstrated end to end: two mirror stubs whose `\trusted` marker can be
removed, with the whole-file proof run and passing.

    errors.py::message                    converted -> file PROVES in ~11 s
    audit_proof_reverify.py::_cache_root  converted -> file PROVES in ~28 s

Both were found by the conversion SCREEN (`--no-proof`, emit + typecheck) and then confirmed
by the REAL whole-file proof, which is the step the screen does not replace.

## How they were found

The screen walks every still-`\trusted` mirror function, converts it ALONE on a copied tree
(the live body verbatim, the stub's own `#@` clauses untouched, only the `\trusted` line
deleted) and runs emit+typecheck. It costs seconds instead of the file's proof time — 14 s
in the cheapest mirror file, 15m12s in `Module2_Parser`, 2h57m in `expressions.py`.

Of the first 106 candidates screened, nine reported LOWERS; re-checked with a wider failure
filter (the first filter did not grep for `syntax error`), seven survived; and the two in
SMALL files were taken to a real proof immediately, because a small file's proof is cheap.

Both passed.

## What must be checked before landing, and it is NOT optional

`errors.py::message` carries a comment beside its marker:

    #@ \trusted reviewer: pycsl-self-annotate
    # super().__str__() is opaque (Exception base); returns string but PyCSL cannot see that
    def message(self) -> str:
        return super().__str__()

**The stub's body is ALREADY the live body verbatim.** So "converting" it is exactly
removing the marker — and the question that decides whether that is honest is what the model
then says about `super().__str__()`. A `\trusted` function asserts nothing it cannot back; an
UNtrusted one whose body calls an opaque operation must model that operation soundly, and
the whole point of this session's findings is that an opaque value with a declared type is
where fidelity goes wrong.

So before this lands:

1. Emit the file both ways and DIFF, exactly as the `compose_from` diagnosis was done. If
   the converted `message` is emitted with a `: string` result that nothing justifies, the
   removal buys a smaller TCB and a larger lie, which is the wrong trade and the opposite of
   this campaign's purpose.
2. Run the three trust planes — `check-trusted-raises-honesty.py`,
   `check-trusted-frame-honesty.py`, `check-trust-blast-radius.py` — because a marker
   leaving the set moves all three.
3. Run `bin/count-trusted-directives.py` and record the new number (it is 460 today) in the
   same commit, with the ceiling-free convention that script already documents.
4. The corpus must be byte-inert: a mirror-only change should not move a corpus emission,
   and if it does, that is the finding rather than the landing.

## Why this is written down instead of landed

The driver session that measured it lost its shell mid-investigation (a `pkill -f <script>`
whose pattern matched the harness's own persistent shell — wall-lesson (c6) with teeth), so
it could not run the checks above or the gate. Everything needed is recorded here:

    $SCRATCH/g31/convert_one.py      converts one stub on a copied tree
    $SCRATCH/g31/tcb_try.sh          converts + runs the REAL whole-file proof
    $SCRATCH/g31/screen_all.sh       screens every still-`\trusted` function
    $SCRATCH/g31/recheck_lowers.sh   re-checks a LOWERS list with the wider filter
    $SCRATCH/g31/tcb_errors.log      the errors.py proof, SUCCESS
    $SCRATCH/g31/tcb_audit.log       the audit_proof_reverify.py proof, SUCCESS

## The five other candidates that LOWER but are unproven

    Module6_WhyMLTranspiler.py  __init__          (that file's proof is 40m43s)
    Module6_WhyMLTranspiler.py  _emit_funcs
    frontend/Module2_Parser.py  _parse_quantifier (that file's proof is 15m12s)
    frontend/Module2_Parser.py  _try
    frontend/Module2_Parser.py  parse_contract

And two that the wider filter caught as **SYNTAX ERROR**, which the first screen had called
LOWERS: `Module2_Parser::_parse_atom_name` and `::_parse_contract`, both emitting
`raise (Return {  })` — an empty record literal Why3 cannot parse.

---

## CHECK 1 of 4 — the emit-diff. **PASSES, and it is the check that decides the honesty.**

The question the record posed: does removing the marker make the model ASSERT something it
cannot back? Emitted both ways from two copied trees and diffed.

BEFORE (the `\trusted` stub):

    val pycslerror__message (self: pycslerror) : string

An abstract `val`: the result type is DECLARED and the field frame is ASSUMED. Nothing about
the body is checked, which is exactly what `\trusted` means.

AFTER (converted):

    val str_dunder_op () : string          (* no defining axiom *)

    let pycslerror__message (self: pycslerror) : string
      ensures { self.pycslerror_code     = old self.pycslerror_code }
      ensures { self.pycslerror_filename = old self.pycslerror_filename }
      ensures { self.pycslerror_line     = old self.pycslerror_line }
      ensures { self.pycslerror_stage    = old self.pycslerror_stage }
    =
      (str_dunder_op ())

**Two things change and both go the right way.**

1. The four field-preservation clauses move from ASSUMED to PROVED. The `val` form carried
   no frame at all; the `let` form carries one and the file's proof discharges it. The
   caller's guarantee about `message()` is strictly stronger after the conversion than
   before.

2. `super().__str__()` — the reason the marker was there, per the stub's own comment
   ("opaque (Exception base); returns string but PyCSL cannot see that") — becomes
   `str_dunder_op ()`, a `val` with NO defining axiom. That is route #41's
   sound-by-opacity device, and it is the SAME opacity the `val` form already had: the
   result is a `string` because the signature says `-> str`, and nothing is known about its
   value in either version.

   It is a plain `val`, not a `val function`, so two calls are NOT provably equal — the
   per-name-vs-shared-constant hazard route #41 documents does not arise here.

**So the trade is: an assumed frame becomes a proved frame, and the opacity is unchanged.**
That is a real TCB reduction and not a relabelled assumption — which is precisely what this
check existed to decide, and it could not have been decided by reading the source.

Six mirror classes share the method, and all six move the same way (`pycslerror`,
`pycslirerror`, `pycslparseerror`, …).
