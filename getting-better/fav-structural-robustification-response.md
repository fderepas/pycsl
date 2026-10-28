# Independent review: `fav-structural-robustification` — VERDICT: **REFUTE (do not build)**

Reviewer: independent (worktree `agent-a9f46805c3fb7582b`, no access to the author's transcript).
Date: 2026-08-26.
Tree reviewed: the report's own commit `a406f7e1` (its `src/` tree is byte-identical to the
report's stated HEAD `31654938` — the 3 intervening commits touch only `bin/` and
`getting-better/`; verified with `git diff --stat eaaf85f7 a406f7e1`). My worktree was initially
checked out at the stale merge `f552646c` (mirror still 1242 all-stub markers); I detached to
`a406f7e1` before running any oracle, so every run below is at the report's HEAD.

Toolchain: `why3 1.8.2` + `alt-ergo 2.6.3` + `Z3 4.13.3` from `/home/fabrice/.opam/framac-coq8/bin`,
`.venv` symlinked from the main checkout. One environment caveat is called out in §5.

---

## 0. Headline

**The wall this report proposes to break was already broken on 2026-08-09 — seventeen days before
the report was written — by a different, cheaper, already-landed fix.** `_collect_mutations` and
`find_iteration_mutations` are both converted and proved at the report's own HEAD; the mirror
`ir_scanner.py` contains **zero** `#@ \trusted` markers; and `find_assigned_vars`' allegedly
razor-edge `__Lbody`/`__Lorelse` goals prove **Valid in ≤ 0.5 s** in the whole-file context that
already contains the converted sibling. The report's own refutation condition #4 ("the payoff is 0
and the build should not be started") fires, in a stronger form than it anticipated.

The report's §3 *mechanism* claim (structural variants delete the arithmetic size goals) is
**true** — I confirmed it with a hand `.mlw` — but it is moot: the landed resolution kept the
reader/size-measure style and fixed it by a reader-split, so there is nothing left for the
structural rewrite to buy. The proposed build would re-emit two landed, proven functions for a
yield of **0 markers**.

Secondary finding: the report is not describing the tree it claims to be written on. It is a
faithful resurrection of the 2026-08-03/04 state (workers #17–#22), contradicted by later entries
*in the same `wall-lessons.md` it quotes* (the 2026-08-08 spike and the 2026-08-09
"value-model ROOT BROKEN (796→794)" entries, lines ~1579–1620).

---

## 1. Oracle 1 — whole-file proof of the mirror `ir_scanner.py` at HEAD (report §5/§6, question 3)

Command (run at `a406f7e1`, foreground):

```
$ export PATH="/home/fabrice/.opam/framac-coq8/bin:$PATH"
$ PYTHONHASHSEED=0 timeout 560 .venv/bin/python3 src/pycsl/pycsl.py \
    src/self-annotate/src/module6_whyml/ir_scanner.py --import-path src/pycsl
```

Result (default prover config; see §5 for the Alt-Ergo caveat — this run effectively raced Z3 only):

```
[-] 1 goal(s) remain unproven after all provers:
    Prover result is: Timeout (30.00s, 513081202 steps).
[-] Verification FAILED or INCOMPLETE. Check the solver output.
```

with 1318 `Valid` sub-goal results, and the single non-Valid goal being

```
File "/tmp/.pycsl_52_ciix6.mlw", line 563, characters 32-63:
Sub-goal postcondition of goal irscanner__collection_binder_kinds'vc.
Prover result is: Timeout (30.00s, 513081202 steps).
```

**The one straggler is NOT a `find_assigned_vars` goal and NOT the wall's goal.** It is the
`setfold_leaf_empty obj result` postcondition of `collection_binder_kinds` — a function the report
never mentions, converted long ago (ledger line 842 records it proving green historically).

All **163** `irscanner__find_assigned_vars*` sub-goals are **Valid**, including the report's named
cliff goals:

```
Sub-goal postcondition of goal irscanner__find_assigned_vars__Lbody'vc.
Prover result is: Valid (0.50s, 7848164 steps).
Sub-goal postcondition of goal irscanner__find_assigned_vars__Lorelse_g'vc.
Prover result is: Valid (0.01s, 47786 steps).
```

— in the whole-file module that **already contains the fully converted `_collect_mutations` and
`find_iteration_mutations`**. The report's central empirical premise ("converting
`_collect_mutations` tips `find_assigned_vars` over a cliff") is false at HEAD: the coexistence it
declares impossible has been the landed, gated reality since c6557971.

A second whole-file run with both provers actually racing
(`--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'`) reproduced 1319 `Valid` sub-goal lines through the
proof phase; final verdict line recorded below in §1a.

### 1a. Dual-prover whole-file verdict

RESULT-PLACEHOLDER

---

## 2. Oracle 2 — the `__Lbody`/`__Lorelse` readers in the emitted WhyML (question 2)

```
$ PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py \
    src/self-annotate/src/module6_whyml/ir_scanner.py --import-path src/pycsl --no-proof --keep-mlw
$ grep -n 'size_list result <= size_dict' src/self-annotate/src/module6_whyml/ir_scanner.mlw
190: 307: 318: 329: 828: 839: 998: 1009: 1020:    ensures { size_list result <= size_dict d }
```

**CONFIRMED**: `irscanner__find_assigned_vars__Lbody` / `__Lorelse` exist (`.mlw` lines 819–840)
and carry exactly the `size_list result <= size_dict d` postcondition the report describes. But the
grep also shows the report's blind spot: lines 298–329 are
`irscanner___collect_mutations__Lbody/__Lorelse/__Lfinalbody` — **the landed `_collect_mutations`
uses the very same reader + size-postcondition style**, and its fold terminates by
`variant { size_list stmts }` (`.mlw` line 332), not by structural variants:

```
let rec irscanner___collect_mutations (stmts: list pyval) (target_name: string) (out: ref (list pyval)) : unit
  requires { true } ensures { true } writes { out } variant { size_list stmts }
= ... irscanner___collect_mutations (irscanner___collect_mutations__Lbody d) target_name out; ...
```

This directly refutes the report's §3 description of the sibling ("mutual structural descent
`__walk (v: pyval) variant {v}` / `__walkd (d: pydict) variant {d}` / `__walkl (xs) variant {xs}`
... no size lemma and no arithmetic goal at all"). That description matches the author's *scratchpad
build* (`cm_structvar.mlw`), which never landed. What landed (c6557971) is the reader style made
robust by the **reader-split**: each `__Lbody` is a two-layer `let rec __Lbody_g : option pyval`
(structural `variant { d }`, postcondition `pv_size v <= size_dict d`) plus a non-recursive
composer. The robustness the report attributes to structural variants actually comes from that
split.

---

## 3. Oracle 3 — hand `.mlw`, both styles (question 1 / §3 mechanism)

File: `scratch-review/style_compare.mlw` (in this worktree). One ADT (`pyval`/`pydict` with an
`irkey` that has a `K_body` constructor); module `StyleB` = mutual structural walkers with
**zero size functions in scope** and per-tag selectivity expressed by matching the key constructor
(`DCons K_body v rest -> walk_v v; ...` — `K_orelse` cells skipped); module `StyleA` = the
reader + size-measure style mimicking `emit_find_assigned_vars_group` (reader `lbody` with
`ensures { size_list result <= size_dict d }`, fold `variant { size_list stmts }` recursing on
`lbody d`).

```
$ why3 prove -P alt-ergo scratch-review/style_compare.mlw
Goal walk_v'vc.  Prover result is: Valid (0.04s, 106 steps).
Goal walk_d'vc.  Prover result is: Valid (0.04s, 84 steps).
Goal walk_l'vc.  Prover result is: Valid (0.03s, 37 steps).
Goal size_pos'vc.          Valid (0.05s, 264 steps).
Goal size_list_nonneg'vc.  Valid (0.04s, 124 steps).
Goal size_dict_nonneg'vc.  Valid (0.04s, 137 steps).
Goal lbody_g'vc.  Prover result is: Valid (0.07s, 494 steps).
Goal lbody'vc.    Prover result is: Valid (0.04s, 132 steps).
Goal fold'vc.     Prover result is: Valid (0.04s, 81 steps).
```

**§3's mechanism claim is CONFIRMED**: Style B generates only three structural
termination goals, discharged in ≤ 106 steps with no size measure, no lemma pack, no arithmetic —
the size-postcondition goals do not exist. And **§4's faithfulness worry is weaker than the report
fears**: per-tag/per-key selectivity is expressible structurally by matching the key constructor
inside `walk_d`, with no reader function — at least whenever the key is an interned `irkey`
constructor (the emitted preamble at HEAD interns `K_body`; a `K_dyn s` computed key would need a
`pystr_eq` guard on the cell, which is still structural). This corroborates the ledger's own
2026-08-08 spike: "The STRUCTURAL-variant encoding proves 16/16 fast under Z3+Alt-Ergo, zero
axioms."

So the report is *right about the physics and wrong about the war*: the structural style would
indeed have deleted the goals, but the reader-split already made deleting them unnecessary.

---

## 4. Oracle 4 — the payoff (question 4): `_collect_mutations` at HEAD

```
$ grep -cF 'trusted' src/self-annotate/src/module6_whyml/ir_scanner.py          # at a406f7e1
0
$ git grep -hF '#@ \trusted' a406f7e1 -- src/self-annotate/src | wc -l
675
$ git log --oneline -4 a406f7e1 -- src/self-annotate/src/module6_whyml/ir_scanner.py
925d5972 tcb: find_array_and_dict_vars — rsplit-leaf-gate + record-of-StrSets (787->786)
65be306e tcb: collect_escaping_exceptions — prior boundary broken ... (788->787)
fdbccc77 tcb: find_iteration_mutations — value-model-root record-embedding (795->794)
c6557971 tcb: _collect_mutations — heterogeneous value-model ROOT broken (796->795)
```

**REFUTED — payoff is 0, twice over.** The report's "1 marker guaranteed (`_collect_mutations`),
plausibly 2 (`find_iteration_mutations`)" were both converted on 2026-08-09. The mirror
`ir_scanner.py` at the report's HEAD has **no trusted markers at all**. The live tree contains the
dedicated pair `recognize_collect_mutations` / `emit_collect_mutations_group`
(`src/pycsl/module6_whyml/generic_fold.py:17852` / `:17903`) — sitting 800 lines below the
`emit_find_assigned_vars_group` (`:17031`) the report proposes to rewrite. The commit message of
c6557971 even records the landing gates: "authoritative whole-file proof SUCCESS 0 non-Valid,
find_assigned_vars still proves, _collect_mutations proves, NO sibling regression; ... full-corpus
byte-diff 0". The header count 675 is CONFIRMED, which makes the internal contradiction sharper:
the count the report quotes already includes the two conversions it proposes to earn.

---

## 5. Environment caveats (honest-oracle disclosure)

- **Prover-version drift**: the repo config (`config/agents-config.json:4`) pins
  `"Alt-Ergo,2.6.2,"`, but this machine's `~/.why3.conf` (dated Aug 4) registers only Alt-Ergo
  **2.6.3**. pycsl therefore prints `No prover in /home/fabrice/.why3.conf corresponds to
  "Alt-Ergo,2.6.2,"` and silently races **Z3 only** under the default config. My first whole-file
  run (§1) ran under exactly that config; the §1a rerun pinned `Alt-Ergo,2.6.3,,Z3,4.13.3,`
  explicitly. This drift is itself a campaign-hygiene finding: any recent "best-of-N racing"
  result obtained via the default config on this machine was Z3-only.
- **The `collection_binder_kinds` straggler** may be an artifact of that drift (best-of-N lost its
  Alt-Ergo leg) rather than a true regression; §1a is the discriminating run. Either way it is
  orthogonal to this report's wall.
- The mirror-fidelity plane is RED at the report's commit for **2 pre-existing divergences**
  (`bin/check-self-annotate-sync.sh`, exit 1: `expressions.py::_handle_var_expr`,
  `stmt_control_flow.py::_handle_for_stmt`) — the same two that c6557971 recorded as "fidelity
  drift 2 pre-existing untouched". None touch `ir_scanner.py`. Known, but it means "all planes
  green at HEAD" is not currently true tree-wide.
- I could not run `bin/byte-diff-sweep.sh` (nothing to sweep: I made no emitter change, and the
  proposed build was not performed — deliberately, per the verdict).

---

## 6. Claim-by-claim scorecard

| Report claim | Verdict | Evidence |
|---|---|---|
| Header: 675 trusted at HEAD | **CONFIRMED** | `git grep -hF '#@ \trusted' a406f7e1 -- src/self-annotate/src \| wc -l` = 675 |
| §1: `find_assigned_vars` converted & proved; recognizer/emitter at `generic_fold.py:16916`/`:17031` | **CONFIRMED** | exact line numbers verified; 163/163 subgoals Valid at HEAD |
| §1: `_collect_mutations` "still `#@ \trusted`", "the target" | **REFUTED** | converted 2026-08-09 (c6557971); mirror file has 0 trusted markers |
| §2: wall narrative + t2/t3 numbers (0.23 s/490 K vs 30 s/280 M) | historically accurate (ledger lines 1337–1341) but **STALE** — superseded by ledger entries at lines ~1579–1620 |
| §3: sibling `_collect_mutations` landed in structural `__walk/__walkd/__walkl` style | **REFUTED** | emitted `.mlw`: `variant { size_list stmts }` + `__Lbody/__Lorelse/__Lfinalbody` readers with size postconditions |
| §3: structural style deletes the size goals | **CONFIRMED as mechanism** | hand `.mlw` `scratch-review/style_compare.mlw`: 3 structural goals, 37–106 steps, zero size machinery |
| §3: "the only reopening ... never been tried" | **REFUTED** | a fourth reopening (reader-split) was tried and won on 2026-08-09 |
| §4: selectivity table (While body-only, If both, For body-only, Try body+handlers, Match cases) | **CONFIRMED** | live `src/pycsl/module6_whyml/ir_scanner.py:39–62` |
| §4: naive structural descent would over-collect; selectivity needs care | **CONFIRMED but overstated** | per-key selectivity is structural (key-constructor match), no reader needed — hand oracle §3 |
| §4: expected yield 1–2 markers | **REFUTED** | yield is 0; both targets already converted |
| §6.3: premise "find_assigned_vars may already be non-Valid at HEAD" | **REFUTED (premise intact)** | all its goals Valid, `__Lbody` postcondition 0.50 s / 7.8 M steps |
| §6.4: payoff-0 refutation condition | **FIRES** | see §4 above |

---

## 7. Recommendation

1. **Do not run the proposed build.** Rewriting `emit_find_assigned_vars_group` into the
   structural style would re-emit two landed, proven functions (regression risk the report itself
   flags as RISK (a)) for a yield of zero markers. Close this wall as
   **SUPERSEDED-BY c6557971 + fdbccc77** (reader-split resolution, ledger 2026-08-08/09 entries).
2. **Fix the driver's state ingestion.** A Phase-2 lever list that resurrects a wall which the
   quoted ledger itself records as broken 17 days earlier is a process failure: the report quotes
   `wall-lessons.md` lines ~1337 while missing lines ~1579–1620 of the same file. Wall reports
   should be required to cite the *last* ledger entry mentioning their target symbol, and the
   backlog generator should grep the mirror for the target's `\trusted` marker before emitting a
   lever.
3. **Spend the effort on the real open items instead**: (a) the `Alt-Ergo,2.6.2,` vs 2.6.3
   prover-config drift (silent Z3-only racing); (b) the `collection_binder_kinds` whole-file
   straggler if §1a confirms it under dual provers; (c) the 2 pre-existing mirror-fidelity
   divergences.
4. If a *future* wall genuinely needs the structural rewrite, §3's mechanism is now
   oracle-confirmed (hand `.mlw` banked in this worktree), and the faithfulness trap is milder
   than feared: per-tag selectivity survives structural descent via key-constructor matching. But
   the burden of proof for re-emitting a landed function should stay where the report put it:
   whole-file re-proof mandatory, corpus byte-diff 0.
