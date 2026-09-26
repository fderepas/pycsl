# The 116 type errors, measured one at a time — and they do not collapse

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

**Even with the full text, they do not collapse.** The largest cluster is 20 of 116 — 17% — and
it is the SAME string/int cluster the string closure just failed to clear, which means the
cluster is a symptom shared by several different sites rather than one missing rule. Four
markers show the `int -> option int` mismatch that is exactly the I4 bridge (#55): one end of a
call edge moved and the other did not.

## Why `trusted-reasons.tsv` still says `unclassified` for all 116

Because a classification is a CLAIM, and the measurement above does not support any grouping big
enough to be worth a capability name. Rule (k) says never re-baseline a gate to make it green;
the ledger's analogue is never CLASSIFY to make a ratchet move. `MAX_UNCLASSIFIED` went 442 ->
389 in the same hour on 53 markers whose reason the EMITTER ITSELF NAMED in a refusal
diagnostic — that is a measurement. These 116 have no such sentence, so they keep the default.

What they have instead is this table, which is strictly more information than a label: a next
generation can take one row, read the full error, fix the one site, and re-measure — and the
table says exactly how much that is worth (between one and twenty markers, and usually one).

## The transferable part

**A screen's column limit is a measurement instrument, and truncating a diagnostic destroys
exactly the information that distinguishes a cause from a symptom.** This generation built a
wall, a plan and a capability estimate on 48 characters, spent a day on the capability, got one
marker, and then spent eight minutes re-measuring all 116 at full width. The eight minutes
should have come first, and the reason they did not is that the truncated table LOOKED like
data.
