# What 922 conversions are actually worth, priced for the first time

Generation #31, 2026-09-26T03:20Z. The campaign's headline number is the `\trusted` MARKER
COUNT, and its complement — 922 mirror functions CONVERTED — has been reported for many
generations. Nobody had measured what a conversion establishes. Here it is.

## The split

All 1373 function definitions in `src/self-annotate/src`; 451 carry `#@ \trusted`, 922 are
converted. Of the 922, by the strongest thing their contract claims:

| claim | count | share |
|---|---|---|
| a FUNCTIONAL postcondition (`#@ ensures` that is not `True`) | **146** | 16% |
| PURITY only (`#@ assigns \nothing`, no functional postcondition) | **495** | 54% |
| a NON-TRIVIAL FRAME only (`#@ assigns <fields>`) | **207** | 22% |
| neither a real `ensures` nor an `assigns` | 74 | 8% |

**Five out of six conversions prove no functional postcondition at all.** That is not a
scandal and it is not nothing, and the difference between those two readings is the point of
writing it down.

## Why it is not nothing

A conversion with `ensures True; assigns \nothing` still establishes, mechanically:

* **PURITY** — the emitted body provably writes no record field, which is exactly the claim a
  frame-erasure exploit needs to break (`check-trusted-frame-honesty.py` exists because 82
  `\trusted` stubs once declared `assigns \nothing` over live bodies that wrote `self`);
* **TYPE SAFETY** of the emitted model (L3-tc), which caught route #57's ill-typed landing;
* **TERMINATION**, unless the body is a loop without a variant (54 such bodies are counted and
  ratcheted by `check-trusted-termination-honesty.py`);
* **FRAME PRESERVATION FOR EVERY RECORD FIELD** — and this one is SYNTHESIZED, not written.
  `errors.py::PyCSLError.message` carries no `#@` line of any kind in the mirror, and emits

        let pycslerror__message (self: pycslerror) : string
          ensures  { self.pycslerror_code = old self.pycslerror_code }
          ensures  { self.pycslerror_filename = old self.pycslerror_filename }
          ensures  { self.pycslerror_line = old self.pycslerror_line }
          ensures  { self.pycslerror_stage = old self.pycslerror_stage }

  four clauses the abstract `val` merely assumed, now PROVED. A blank contract block is not a
  blank obligation.

## Why it is not everything, either

None of the above says the function COMPUTES THE RIGHT THING. That was this session's
expensive lesson twice over: six conversions passed every one of those checks and were
hollow, and the criterion that admitted them audited declarations rather than bodies
(`finding-check-one-is-a-quarter-of-the-criterion.md`). A marker count is a measure of
SURFACE REMOVED, not of KNOWLEDGE GAINED, and the two diverge exactly where the contract is
`True`.

## The 74, opened up, because the raw number reads worse than it is

    50  NESTED CLOSURES — a closure has no `#@` block by design; it is FOLDED into its
        enclosing definition and `check-untrusted-emitted.py` counts all 41 of the folded
        ones explicitly.
    24  top-level or method, of which:
         9  `mutable_state` — the DECORATOR function itself, in nine files
        10  `module6_whyml/irx.py` accessors (`ir_kind`, `ir_op`, `ir_name`, …)
         3  `errors.py` (`__init__`, `__str__`, `message`) — the synthesized-frame case above
         2  `Module6_WhyMLTranspiler._heap_var` and one more

So the claim-free set has no substance in it. The number that matters is the first one:
**146 functional postconditions out of 922.**

## What to do with it

Nothing, yet — this is a measurement, not a verdict, and it is recorded so the next
generation states the campaign's result the way the evidence supports it:

> 922 of 1373 mirror functions no longer rest on a trust marker. 146 of them carry a proved
> functional postcondition; the other 776 carry proved purity or a proved frame, and say
> nothing about what they compute.

Re-run it with `bin/price-the-conversions.py`.
