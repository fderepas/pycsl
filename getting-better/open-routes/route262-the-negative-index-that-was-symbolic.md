# OPEN ROUTE #262 — A SYMBOLIC NEGATIVE INDEX IN A CONTRACT READS CELL -1 OF THE LOGICAL ARRAY

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 2; driver-reproduced at HEAD e152fa15 (rc=0).
`witnesses-r262/F5_contract_symbolic_negindex.py`: `requires len(xs) == 2 and k == -1`, `requires xs[1] == 0`,
`ensures xs[k] == \old(xs[k])`, `assigns xs[1]`, body `xs[1] = 7` PROVES (CPython: xs[-1] goes 0 -> 7).
A literal `xs[-1]` is rewritten to `xs[length-1]`; a symbolic `xs[k]` lowers to raw `xs[k]`.
Repair: contract-side `xs[e]` with a possibly-negative `e` lowers to `xs[if e < 0 then length xs + e else e]` (or
requires `e >= 0` / refuses); check body-side symbolic negative indexing too.

## REPAIR (2026-10-17, branch r259 off b35d9c5e, landed with #259)
Rule (inline in `_handle_subscript`, mirror `\trusted`): in a CONTRACT (`_in_spec`: requires/ensures/loop
invariants/asserts, incl. inside `\old` and quantifiers) a list/str/`\result`/`self.<list field>` read takes
Python's index -- a non-negative int literal is kept, a negative literal `-k` reads `len - k` (the string,
`\result` and field arms had NO rewrite at all: `s[-1] == ""` PROVED, Why3's `substring` is `""` for `i < 0`),
anything else reads `(if e < 0 then a[len + e] else a[e])`. The split stays OUTSIDE the read so the raw term `a[e]`
survives for cited-axiom triggers/E-matching (an inside-the-brackets first cut sent 0708/0711/0714 Unknown).
Body reads are unchanged: a Why3 program array read carries `0 <= e`, so a negative body index fails closed
(seq/str body reads are opaque outside bounds); 2-D `matrix` reads are bounds-guarded (fail closed); contract
slices do not parse; a symbolic tuple index is `subscript_get`, unbound in logic (fail closed).

Witnesses (PROVED at b35d9c5e, CPython disagrees; FAIL after on the postcondition/invariant goal, no type error):
2710 F5, 2711 `\result[k]`, 2712 `\old(xs[k])`, 2713 unguarded `\forall i; i == -1 ==> ...`, 2714 str `s[k]`,
2715 str `s[-1]`, 2716 loop invariant `xs[k]`, 2720 `self.items[k]`. Controls keep PASS: 2717 `xs[-1]`,
2718 `xs[k]` with `0 <= k`, 2719 guarded `\forall`. Coverage FAIL -> PASS (faithful, not merely refusing):
2721 `xs[k] == 7`, 2722 `s[k] == s[1]`, 2723 `\result[k] == 7`.

Gates (both routes): corpus root 100 MOVED / 0 GONE / 0 APPEARED (1731 = 1709 + 22 new; 2701/2705 refused, no
.mlw), pyref 2186/2186 0 MOVED/GONE; M1 for all 100: 340 contract read sites rewritten (array arm only) + 1162's
`py_pow` requires + the 3 declared source repairs below; ALL 100 movers re-proved on the patched tree, verdicts
unchanged (77 PASS, 23 FAIL). SOURCE REPAIRS (declared): 0708 `decode_field`, 0714 `field_frame` gain
`requires 0 <= off`, 0711 `slot_inode_value` gains `requires blk >= 0 and k >= 0` -- their cited Rocq/Lean lemmas
read an abstract RAW reader `rd : Z -> Z`, which equals the Python read only for a non-negative index; with an
unbounded offset the base PASS rested on the raw-cell conflation this route removes. Core goldens 0100/0583
`.expected.mlw` regenerated (exactly the rewrite). Mirror: 2 MOVED (frontend/Module2_Parser 5 sites,
frontend/pure_ast 40 sites, all the rewrite), both `why3 --type-only` clean; Module2_Parser whole-file re-proved
868 Valid / 0 (rc=0, `--no-check-vacuity`; a run with the vacuity phase reached 868/0 before the window cut it);
pure_ast OWED. Planes 61/61, check-self-annotate-sync + self-annotate-mirror-check rc=0.

RESIDUAL (pre-existing, not widened): cited axioms are stated over raw Why3 cells with no `0 <= idx` guard
(e.g. `UnixFs.Dir.slot_inode_byte_decode`); after this repair no contract read reaches a negative raw cell except an
index below `-len` (Python IndexError), the same unconstrained out-of-range value a positive past-the-end read has.
