# The 116 type errors, measured one at a time — and they DO collapse, at 102 of 116

> **CORRECTION, 2026-09-26T12:45Z, twenty minutes after this file was written, and it is the
> correction rather than the finding that is worth reading.** The title used to end "and they do
> not collapse". That conclusion was drawn from a measurement that captured ONE LINE of each Why3
> message — and a Why3 type error is TWO lines: `has type X,` then `but is expected to have type
> Y`. So this file diagnosed a truncated instrument using a truncated instrument, in the same
> hour, having just written the paragraph that warns about exactly that. Re-measured at three
> lines, **102 of the 116 have exactly ONE side `int`** — they fail at the seam between the
> faithful value model and the int-erased one, crossed in both directions. That is one cause, it
> is now backlog #62, and 102 rows of `trusted-reasons.tsv` are classified against it
> (`unclassified` 442 -> 287 across two commits). The body below is kept as written, with the superseded claims
> marked, because the sequence is the lesson.


Generation #31, 2026-09-26T12:35Z. The last measurement of the window, and it closes the loop
on the one this generation got wrong twice.

## What was claimed, and how it was claimed

`finding-the-whole-conversion-frontier-measured.md` bucketed 230 emitter type errors by the type
the emitter EXPECTED and concluded:

> **`int` and `string` together are 144 of 230 — 63%.** … it is a value model that carries a
> Python `str` as a Why3 `string` in parameter and return position and as an `int` in
> record-FIELD position

and sized a 174-witness wall from it. Two things were wrong with that, and both are about METHOD
rather than about strings:

1. the numbers came from a screen that **TRUNCATED the Why3 message at 48 characters**, so the
   only thing they could group by was the expected TYPE;
2. the cause was then inferred from the grouping. A distribution of error MESSAGES was read as a
   distribution of CAUSES.

The first refutation was `finding-the-field-value-model-already-landed.md`: the carrier the wall
named already existed. The second was the string CLOSURE, predicted to clear a large share of
174 and measured to clear **ONE of 103**.

## So each one was measured individually

Every live marker whose recorded verdict was `TYPE` — 116 of them — was ported (or `--replace`d)
into a fresh `git archive HEAD src bin json` tree, its marker deleted, its file emitted, and the
**FIRST Why3 error recorded IN FULL**. The table is
`getting-better/trusted-type-error-causes.tsv`, one row per marker. 115 still produce a type
error; **one now LOWERS** — `pure_ast.py::NodeVisitor.generic_visit`, the one the string closure
unlocked, and the amended criterion refused it in five minutes for a different reason
(`shadowed-selfcalls` 14 -> 15).

The full messages cluster like this:

    20  int, but is expected to have type string
    15  string, but is expected to have type <…>
    13  list.List.list PyCSL_Program.pyval, but …
    11  int, but is expected to have type array.Array.array
     7  array.Array.array string @rho, …
     6  int, but is expected to have type PyCSL_Program.<record>
     6  'mu -> option.Option.option int, …
     4  int -> option.Option.option int, …          <- the I4 BRIDGE shape
     3  int, but is expected to have type real
     3  array.Array.array int @rho, …
     3  PyCSL_Program.term, but is expected …
     6  unbound symbol 'toks' / 'self' / 'body' / 'ctx'
     …  and a dozen one-offs (ref int @rho, seq.Seq.seq 'mu, ref emit_ir @rho, …)

~~**Even with the full text, they do not collapse.** The largest cluster is 20 of 116 — 17% —~~
**SUPERSEDED: that was not the full text.** With the second line of each message, the
grouping that matters appears at once — not the expected TYPE, but whether exactly one side
is `int` — and it holds for 102 of 116. See backlog #62. The sentence below was still true
of the truncated data, and
it is the SAME string/int cluster the string closure just failed to clear, which means the
cluster is a symptom shared by several different sites rather than one missing rule. Four
markers show the `int -> option int` mismatch that is exactly the I4 bridge (#55): one end of a
call edge moved and the other did not.

## Why `trusted-reasons.tsv` said `unclassified` for all 116 — and why 103 no longer do

Because a classification is a CLAIM, and the measurement above does not support any grouping big
enough to be worth a capability name. Rule (k) says never re-baseline a gate to make it green;
the ledger's analogue is never CLASSIFY to make a ratchet move. `MAX_UNCLASSIFIED` went 442 ->
389 in the same hour on 53 markers whose reason the EMITTER ITSELF NAMED in a refusal
diagnostic — that is a measurement. These 116 have no such sentence, so they keep the default.

What they have instead is this table, which is strictly more information than a label: a next
generation can take one row, read the full error, fix the one site, and re-measure.

**AND THE TABLE IS WHAT OVERTURNED THE PARAGRAPH ABOVE.** Widening the capture from one line to
three cost eight minutes and turned "no defensible grouping" into "102 of 116 share a structural
property of the error". The classification that followed is NOT a grouping by expected type — the
thing this file correctly warned against — it is a grouping by WHICH SIDE IS `int`, which
corresponds to a real defect with a name: two coexisting value models. It is falsifiable one row
at a time, which is why the table ships beside it.

## The transferable part

**A screen's column limit is a measurement instrument, and truncating a diagnostic destroys
exactly the information that distinguishes a cause from a symptom.** This generation built a
wall, a plan and a capability estimate on 48 characters, spent a day on the capability, got one
marker, and then spent eight minutes re-measuring all 116 at full width. The eight minutes
should have come first, and the reason they did not is that the truncated table LOOKED like
data.

**AND THEN IT HAPPENED TWICE MORE, INSIDE THIS FILE, WITHIN THE HOUR.** The first version of the
per-marker table captured one line of a two-line message, and this paragraph was written from it.
The failure is not ignorance of the lesson — the lesson is in the paragraph above — it is that a
truncation you INTRODUCED YOURSELF does not announce itself, and "I captured the error" feels
complete whether or not it is. The only defence that worked was reading a handful of rows in full
and noticing the sentence ended in a comma.

**THE THIRD TRUNCATION WAS NOT OF THE MESSAGE BUT OF THE RESET.** The measuring script restored a
pristine copy of the FILE it was about to edit and left the PREVIOUS candidate's file converted,
so once the list crossed a file boundary every later candidate was measured against a mirror in
which earlier files were still converted — and the mirror files import each other. THIRTEEN of 116
rows changed when the whole mirror was restored per candidate, one of them changed its
CLASSIFICATION, and `MAX_UNCLASSIFIED` had to RISE by one with that member named
(`pycsl.py::_run_audit_mode`). The detection that worked is worth institutionalising: **the porter
ABORTED on a candidate — it made no change at all — and the emission still reported an error.** An
error with no edit is the signal. Wall-lesson (t6).

So this file was measured three times, and the CONCLUSION survived all three instruments (103,
then 102 — both ~88%) while the MEMBERSHIP did not. That asymmetry is the practical reason the
per-marker table ships beside the classification: an aggregate can be right while every ninth row
is wrong, and only the table lets the next generation tell which.
