# HANDOFF — read this FIRST on relaunch (prepended 2026-09-01, RELAUNCH #26 worker)

## #26 IN ONE LINE: **#25's 4-site "cost-shaped lowering selection" IS NOT ONE. Three of the four
## clash sites are INT-SOURCED, so `str_concat_op` cannot take them — the residue is a VALUE-MODEL
## capability (string-model the node-field projectors / `_str_literal_helper` returns), not a gate.**

#26 got the final ~10 minutes of the 96h window. Per the supervisor it started no prover run and
attempted no port. It spent the sliver locating the ROOT CAUSE of #25's four sites, and the answer
CORRECTS #25's reopening capability in the unfavourable direction (the first time in nine windows
that a re-pricing went the wrong way — record it as such, it is the counter-example to the streak).

### WHAT #25 CLAIMED, AND WHERE IT IS WRONG

#25 wrote: "under a `string` vararg element type, a computed string argument must lower through
`str_concat_op`/`+` rather than the hash-int `str_concat`; both symbols already exist; this is a
lowering SELECTION driven by `_vararg_elem_type`, COST-shaped." **The selection premise is false.**

`str_concat_op` has signature `(a: string) (b: string) : string`. Selecting it only helps if the
OPERANDS are Why3 `string`s. #26 read the four sites back to their mirror sources:

| emitted line | mirror source | operands |
|---|---|---|
| 4113 | `pure_ast.py:5087` `self.write(f"{quote_type}{string}{quote_type}")` | `quote_type`, `string` are **ints** — they are unpacked from `self._str_literal_helper(...)`, **which is still a `\trusted` stub returning ints** |
| 4120 | `_write_constant` inf/nan `repr` chain | `repr_conv`/`replace_3` results, int-modelled |
| 4348 | `(str_concat (str_concat 1376817993 !operator) 1376817993)` | `!operator` is an **int-typed local**; only the two literals are string-able |
| 4537 | `(str_concat 1174530543 (get_name node))` | `get_name` is one of the **int-modelled node-field projectors** |

So exactly ONE of the four (the literal halves of 4348) is a selection question. The other three are
int VALUES. Routing them through `str_concat_op` produces the *mirror-image* type error.

### THIS IS ALREADY RECORDED IN THE TREE, BY #20, AND IT WAS READ PAST TWICE

`src/self-annotate/src/frontend/pure_ast.py:5030-5044` (a comment #20 left in the mirror) states it
outright, and names the same first failure #25 rediscovered:

> "The remaining 16 come from INT-MODELLED sources — the `get_name` / `get_id` / `get_attr` /
> `get_arg` node-field projectors, `str_concat` over int-typed locals, and int-typed parameters
> (`extra`, `start`, `py_end`, `!operator`) … **L3-tc FAILS on the first one
> (`_write_str_avoiding_backslashes`, whose `quote_type`/`string` locals are ints because
> `_str_literal_helper` is still a stub returning ints)**. There is no int->string direction
> available: `str_hash_op` goes the other way and is not invertible, so no coercion can bridge it
> without a fiction."

#25 measured the residue as 4 sites (down from #20's 16 — that part of the re-pricing STANDS and is
a genuine gain: `seq string` really does clear 54 of 58) but attributed those 4 to the wrong
mechanism. **The count was re-measured; the CAUSE was not.**

### THE CORRECTED REOPENING CAPABILITY (for #27)

Not a lowering selection. It is: **the int-modelled node-field projectors (`get_name`/`get_id`/
`get_attr`/`get_arg`) and the tuple return of the still-`\trusted` `_str_literal_helper` must
produce Why3 `string`s.** Two independent sub-moves, either of which shrinks the 4:

1. **`_str_literal_helper` is one of #24's body-blocked leaves** (nested `def`, `map`, `lambda`,
   list comps, tuple return, `repr`). Porting it is what makes 4113 a string site. Body-blocked
   still, so this is NOT the cheap half.
2. **`get_name` & friends** are emitter-side projectors, not mirror bodies. Whether they can carry a
   `string` return model is UNMEASURED and is the ~2-minute probe #27 should open with. If they can,
   4537 (and the `!operator` half of 4348) go string and the residue may reach 1-2 sites.

**Per the standing lesson, #26 did NOT try either and therefore files NEITHER as a boundary.** What
is established here is only that the WORK IS NOT the work #25 named. `*text: str` still cannot land
until the residue is 0, because all 58 sites share the one `write` formal.

### THE LESSON — the streak's counter-example, and it is the more useful half

Eight windows re-priced a recorded boundary FAVOURABLY. #26 is the ninth and it went the other way:
**a re-measured NUMBER does not re-measure the MECHANISM.** #25 correctly recensused 16 -> 4 and then
inferred the cause of the 4 from the emitted symbol name (`str_concat` vs `str_concat_op`) instead of
from the operands' provenance. One `grep` back to the mirror source — 60 seconds — would have shown
that three of the four operands are values, not spellings. **When a census shrinks a residue, trace
the SURVIVORS to their source; do not assume they are small instances of the same cause as the ones
that went away.** They are usually the hard core that the easy cause was hiding.

Corollary, and it stings: **the answer was in a comment in the file under edit.** #20 wrote it, #24
and #25 both edited within 50 lines of it. Before pricing a blocker in a mirror, read the mirror's
own comments near the failing construct.

### #26 hygiene

No edit was made to `src/` at all — this window bought a diagnosis, not a build, so there was nothing
to revert. Metric verified fresh at window end: **markers 491 · grep 516 · offset 25 · attached 491 ·
unattached 0 · ledger 3.** No prover process started, none left running. Tracked `src/` clean.

### #27's #1 ITEM

Probe (2 min) whether the node-field projectors `get_name`/`get_id`/`get_attr`/`get_arg` can carry a
`string` return model. That is the cheap half of the corrected capability and it is the gate on the
54-marker `_Unparser` lever. If it clears, re-census the residue; if it refutes, the lever's residue
is `_str_literal_helper` alone and the question becomes whether that body-blocked leaf is portable —
which is the value-model floor, and THEN it may be recorded as one.

---

# HANDOFF — read this FIRST on relaunch (prepended 2026-09-01, RELAUNCH #25 worker)

## #25 IN ONE LINE: **`seq string` CLEARS #24's blocker. The 54-marker `_Unparser` lever is LIVE
## again — it is NOT a value-model boundary. Residue is FOUR int-model call sites, not fifty-eight.**

#25 got the final ~13 minutes and ran exactly the probe #24 queued: exercise degree of freedom 1
(`vararg_elem_type` as a PER-FUNCTION choice) on `_Unparser.write`, then re-run #24's port probe.

### HOW YOU SET IT (the mechanism, measured — do not re-derive)

`vararg_elem_type` is NOT a knob you pass; it is selected in
`src/pycsl/frontend/Module5_IREmitter.py:4979-5000` **from the vararg's own annotation**:
`*text: str` -> `"string"`, unannotated `*text` -> `"int"` (ladder 1a), star-forwarded -> dropped.
So the per-function choice is made **in the mirror source**, one annotation:

```python
def write(self, *text: str):      # was: def write(self, *text):
    self._source.extend(text)
```

`fill` needs nothing — its `text=''` is a plain default arg, not a vararg.

### RESULT — L3-tc gets MUCH further, and the two ported bodies are CORRECT

With `*text: str`, `let _unparser__write (self: _unparser) (text: seq string)` (line 4851), and
#24's two ported leaves lower exactly as wanted:

```
let _unparser__visit_ParamSpec   … = self_write_1 (Seq.cons ("**" + (get_name node)) (Seq.empty: seq string))
let _unparser__visit_TypeVarTuple… = self_write_1 (Seq.cons ("*"  + (get_name node)) (Seq.empty: seq string))
```

**A COMPUTED STRING IS NOW A FIRST-CLASS ELEMENT.** #24's decisive failure ("computed string cannot
be an element of `seq int`", old line 4605) is GONE. All 58 write/fill call sites re-materialize as
`seq string`, and the literals become REAL Why3 strings (`" in "`, `":"`, `"\n"`) instead of
`str_hash_op` ints — the fidelity gain #20 predicted.

### THE NEW BLOCKER IS SMALL AND IT IS IN THE *ALREADY-CONVERTED* BODIES, NOT THE PORT

L3-tc now fails at `pure_ast.mlw:4113`:

```
self_write_1 (Seq.cons (str_concat (str_concat !quote_type !string) !quote_type) (Seq.empty: seq string))
  This expression has type seq.Seq.seq string, but is expected to have type seq.Seq.seq int
```

because `val str_concat (x: int) (y: int) : int` (line 628) is the **hash-int** concat, while
`str_concat_op (a: string) (b: string) : string` (line 629) is the string one. The element is an
int, so `Seq.cons` fixes the sequence to `seq int` and the annotated `seq string` tail clashes.

**#25 CENSUSED THE WHOLE SURFACE (python over the emitted .mlw, not grep):**

| write/fill argument sites in `pure_ast.mlw` | **58** |
|---|---|
| already fine under `seq string` | **54** |
| int-model, would clash | **4** |

The four, with line numbers in the `seq string` emission:

```
4113  (str_concat (str_concat !quote_type !string) !quote_type)          _write_str_avoiding_backslashes
4120  (replace_3 (replace_3 (repr_conv value) …) … (str_concat …))       _write_constant (inf/nan repr)
4348  (str_concat (str_concat 1376817993 !operator) 1376817993)          visit_BinOp-family
4537  (str_concat 1174530543 (get_name node))                            a visit_* name write
```

### VERDICT — RE-PRICE, DO NOT RECORD A BOUNDARY

#24 asked for a two-way answer and this is the favourable one. **The 54-marker `_Unparser` lever is
NOT a value-model CERTIFIED-BOUNDARY.** It is gated on a bounded, named, 4-site capability:

**REOPENING CAPABILITY (precise, and it is a COST item, not a correctness one): under a `string`
vararg element type, a computed string argument must lower through the STRING concat
(`str_concat_op`/`+`) rather than the hash-int `str_concat`.** Both symbols already exist in the
preamble — this is a lowering *selection* in `module6_whyml/expressions.py`, driven by the same
`_vararg_elem_type` that already gates `seq_mem_str` (expressions.py:1088) and the abstract
self-call param typing (expressions.py:5675). It is the identical gating idiom, one call site over.

**#1 ITEM FOR THE NEXT WINDOW:** make those 4 sites string-model under `_vararg_elem_type ==
"string"`, land `*text: str` on the mirror's `write`, re-run L3-tc, then port the leaf batch —
which #24 showed is at most ~5 bodies (`fill`, `visit_TypeVarTuple`, `visit_ParamSpec`,
`visit_alias`, `visit_MatchStar`), all of them computed-string writes and hence all of them
unblocked by exactly this change. The other 8 of #24's 13 stay body-blocked (dict / generator /
higher-order / `super().visit`) — that finding stands unchanged.

### THE LESSON, NOW SEVEN TIMES IN SIX HOURS

**#24 wrote a conditional record ("if it does not clear, this is a value-model boundary"). The probe
cleared it. A boundary that has not been TRIED is not a boundary even when the worker who named it
had just measured the failure it predicts.** #24's measurement was correct *for `seq int`*; the axis
it did not measure was the element type it had itself identified as free. Two minutes bought back an
11.0%-of-campaign lever that was one sentence from being filed as a floor.

Corollary for the census habit: **census the emitted `.mlw`, not the plan.** "Computed writes break"
sounded like it covered most of 58 sites. It covered 4.

### #25 hygiene

Probe FULLY REVERTED (mirror byte-restored, 134 markers in file). Metric re-verified after revert:
**markers 491 · grep 516 · offset 25 · attached 491 · unattached 0 · ledger 3.** `src/` clean.
No prover process started, none left running. Nothing banked as a conversion — this window bought a
re-pricing, which is what the supervisor asked for.

---

# HANDOFF — read this FIRST on relaunch (prepended 2026-09-01, RELAUNCH #24 worker)

## #24 IN ONE LINE: **the 13-leaf batch is NOT 13 — the `seq int` element type of ladder 1a blocks
## every body that writes a COMPUTED string, and only ~3 of the 13 leaves are body-portable at all.**

#24 got the last ~16 minutes of the 96h window. Per the supervisor's instruction it did NOT start the
port batch; it ran ONE cheap probe against the port plan #23 wrote an hour earlier. The probe
corrected the plan again — the fifth consecutive window in which a record's claim failed on first
contact.

### FINDING 1 — LEAF-NESS IS A CALL-GRAPH PROPERTY. PORTABILITY NEEDS A SECOND, INDEPENDENT GATE.

#23's "13 leaves are portable now" was measured purely on the call graph (calls no still-trusted
sibling). #24 read the 13 LIVE BODIES (`src/pycsl/frontend/pure_ast.py`, `ast` census, 1 min) and
classified what each body actually needs. **Most of them are blocked by a body feature that has
nothing to do with the call graph:**

| leaf | live body needs | portable? |
|---|---|---|
| `set_precedence` | `self._precedences[node] = precedence` — **dict store keyed by an AST node** | NO — the object-identity / value-model floor |
| `__init__` | `{}` / `[]` dict+list field init | NO — dict model |
| `get_type_comment` | `dict.get` + dynamic `getattr` + f-string | NO |
| `interleave` | `iter()`/`next()`/`StopIteration` + **higher-order callable formals `f`, `inter`** | NO |
| `buffered` | `@contextmanager` with `yield` — a generator | NO |
| `delimit_if` | **returns a context-manager object** (`self.delimit(...)` / `_nullcontext()`) | NO |
| `traverse` | `isinstance(node, list)` + recursion + **`super().visit(node)`** | NO |
| `_str_literal_helper` | nested `def`, `map`, `lambda`, list comps, tuple return, `repr` | NO |
| `fill` | `self.write("    " * self._indent + text)` — computed string | see FINDING 2 |
| `visit_TypeVarTuple` | `self.write("*" + node.name)` | see FINDING 2 |
| `visit_ParamSpec` | `self.write("**" + node.name)` | see FINDING 2 |
| `visit_alias` | `self.write(node.name)` + `" as " + node.asname` | see FINDING 2 |
| `visit_MatchStar` | f-string `f"*{name}"` + None-default | see FINDING 2 |

**So the top hubs `traverse`, `interleave`, `set_precedence` — the three that #23 counted on to
unblock 23+18+8 dependents — are ALL body-blocked.** The DAG analysis is correct and still useful,
but it is a NECESSARY condition for porting, not a sufficient one. Batch 1 is at most the 5 rows in
the bottom group, and FINDING 2 cuts that further.

### FINDING 2 — THE `seq int` ELEMENT TYPE OF LADDER 1a IS A HARD BLOCKER FOR COMPUTED WRITES

#24 ported the two smallest candidate leaves (`visit_TypeVarTuple`, `visit_ParamSpec`, 1 line each)
into the mirror and emitted (`--no-proof --keep-mlw`, 134 -> 132 markers). **L3-tc FAILS:**

```
let _unparser__visit_ParamSpec (self: _unparser) (node: int) : unit =
  let _ = (self_write_1 (Seq.cons ("**" + (get_name node)) (Seq.empty: seq int))) in ()
File "…/pure_ast.mlw", line 4605: This expression has type string, but is expected to have type int
```

`write`'s formal is `let _unparser__write (self: _unparser) (text: seq int)` (line 4851). A **string
LITERAL** write lowers fine — it becomes a `str_hash_op` int (`self_fill_1 2128406761` in an
already-converted caller right below the failure). A **COMPUTED** string (`"**" + node.name`, `"    "
* self._indent + text`, an f-string) is a genuine Why3 `string` and cannot be an element of
`seq int`. The failure is again LOUD (a type error at L3-tc), never a silent mis-lowering.

**This is the decisive fact for the whole 54-marker lever.** Ladder 1a's uniform `seq int` was gated
on all four planes against the mirror AS IT STANDS — where every `_Unparser` body is an empty stub
and every live write call site passes a literal. The moment real bodies are ported, the overwhelming
majority of `_Unparser` writes are computed strings. **1a is proved, and 1a is still not the element
type the port needs.**

### CONSEQUENCE — THE #1 ITEM FOR THE NEXT WINDOW HAS CHANGED

Do **NOT** open the next window by porting leaves. Open it by exercising **degree of freedom 1,
which has now been sitting unused for four windows**: `vararg_elem_type` makes the element type a
PER-FUNCTION choice (#21's infrastructure carries it; #20 measured `seq string` turning 40 of 56
write sites into real Why3 string literals). Set `_Unparser.write` (and `fill`) to `seq string` and
re-run the probe above. That is the gate on batch 1, and it is a ~2-minute probe, not a scope.
If `seq string` clears it, re-price the batch; if it does not, the 54-marker lever is a
CERTIFIED-BOUNDARY on the value model and should be recorded as one.

The 3 starred-blocked bodies (`visit_Compare`, `visit_comprehension`, `visit_MatchOr`) are now moot
for batch 1 — their target `set_precedence` is body-blocked on the dict model anyway.

### #24 hygiene

Probe fully REVERTED; mirror byte-restored (134 markers, re-confirmed). Metric UNCHANGED:
**markers 491 · grep 516 · offset 25 · ledger 3.** No prover process left running. Tree clean.
Nothing was banked as an increment — this window bought a plan correction, which is what the
supervisor asked for.

### The method note #24 paid for

**A DEPENDENCY ANALYSIS IS A CLAIM ABOUT ONE AXIS ONLY.** #23's DAG was measured correctly and
answers "may I port X before Y?" It silently got read as "X is portable." Whenever a plan is built
on a structural census, ask which axis it measured and which axes it did NOT — then spend two
minutes reading the actual artifacts along the unmeasured axis. Here the unmeasured axis (what the
body's Python features require of the value model) knocked out 8 of 13 outright and the element-type
axis knocked out most of the rest.

---

## #23 IN ONE LINE: the vacuity plane on `pure_ast.py` is CLOSED, GREEN. Ladder 1a is fully paid for.

#23 got a ~20-minute window and the supervisor named exactly one job: finish the per-goal
NON-VACUITY gate that #22 had to kill at window end. It is done, and it did not need the slow
per-goal `why3 prove -g` loop at all — `bin/check-emitted-vacuity.py --emit` is the same plane
and it runs in well under a minute:

```
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad
python3 bin/check-emitted-vacuity.py --emit      # EXIT 0
```

**VERDICT: `[+] emitted-vacuity: no NEW erasure (8 known param-erasures gated; 0 input-blind).`**
Evidence: `scratchpad/r23/vacuity.log`.

Read the 8 gated rows carefully, because two of them are in this very file and they are NOT a
finding against 1a:

- `pure_ast.mlw::_parser___dict_rest` (erases `t`) and `pure_ast.mlw::_parser___sequence_pattern`
  (erases `t`) are **PRE-EXISTING, already in `KNOWN_ERASURES`, banked in commit `87f9cdb9` in an
  earlier window.** They sit in `_Parser`, not `_Unparser`. `bin/check-emitted-vacuity.py` is
  byte-unmodified in this tree — #23 added no entry to the ledger to make the gate pass.
- The other 6 are the long-standing `core_ir_semantic` / `Module3_Weaver` / `expr_ghost_spec_ops`
  / `statements` rows, unchanged.

### LADDER ITEM 1a IS NOW GATED ON ALL FOUR PLANES — nothing is left owing on it

| plane | verdict | who |
|---|---|---|
| fidelity (`check-self-annotate-sync.sh` + mirror-check) | green (2-DIVERGED baseline) | #21, inherited — tracked tree unchanged since `44150508` |
| whole-file proof | **2857 / 2857 Valid, 0 non-Valid** | #22, `scratchpad/r22/pure_ast_proof.log` |
| byte-inertness | 3/3 | #21, inherited |
| **non-vacuity** | **0 NEW erasures, 0 input-blind** | **#23, `scratchpad/r23/vacuity.log`** |

Plus: **`src/self-annotate/src/frontend/pure_ast.mlw` declares ZERO `axiom`s** (re-measured by #23
on the freshly emitted file). Ledger stays 3. `#22`'s caveat — "the vacuity plane is UNFINISHED,
not failed" — is now RESOLVED as FINISHED and GREEN. Do not re-run it as a precondition for step 3.

Metric re-verified fresh by #23, UNCHANGED by this window:
**markers 491 · grep-substring 516 · offset 25 · attached 491 · unattached 0 · ledger 3.**

### The instrument note #23 paid for

**Instrument fact 3 says `check-emitted-vacuity.py` is a false green without `--emit`. The
converse is the useful half: WITH `--emit` it is CHEAP.** It re-emits every mirror at
`-P 7 --no-proof --no-typecheck --keep-mlw` and finishes in under a minute — i.e. the whole
vacuity plane for the entire mirror surface costs less than one `--fun` probe. #22 spent its
window's tail inside pycsl.py's per-goal `why3 prove -g` vacuity loop, which was ~200 goals in
after many minutes. **Those are not two speeds of the same check to choose between on time
budget; the standalone probe is the one to reach for, and it covers all 52 mirrors, not one file.**
Generalization worth carrying: when a gate is embedded in a slow driver AND exists as a standalone
`bin/` probe, price the standalone one before assuming the plane is expensive.

---


## #23's SECOND FINDING — **PORT ORDER, not body length, is what gates step 3**

With the vacuity plane closed, #23 spent its remaining minutes on ONE cheap probe (2 min, fully
reverted, tree clean) rather than starting the port: it ported the single SHORTEST live body,
`_Unparser.require_parens` (1 line), into the mirror and emitted with `--no-proof --keep-mlw`.

**It FAILED L3-tc — and not for the starred reason.**

```
    (self_delimit_if_3 747334986 1226926668 ((_unparser__get_precedence self node) > precedence))
File "…/pure_ast.mlw", line 4242: This expression has type bool, but is expected to have type int
```

because the *callee is still a stub*:

```
val _unparser__delimit_if (self: _unparser) (start: int) (py_end: int) (condition: int) : unit
```

**A `\trusted` stub has a `pass` body, so its formals get the default `int` type. Port a CALLER
before its CALLEE and any non-int actual (here a `bool` comparison) is a hard type error.** As with
the starred residue, the failure is LOUD, never a silent mis-lowering — but it means the port is
not a flat batch.

### THE DEPENDENCY STRUCTURE (measured, `ast`, 30 s)

Of the 51 trusted `_Unparser` methods, counting `self.X(...)` calls in the LIVE body where `X` is
also still `\trusted`:

- **13 are LEAVES** — they call no still-trusted sibling: `__init__`, `_str_literal_helper`,
  `buffered`, `delimit_if`, `fill`, `get_type_comment`, `interleave`, `set_precedence`, `traverse`,
  `visit_MatchStar`, `visit_ParamSpec`, `visit_TypeVarTuple`, `visit_alias`.
- **38 depend on at least one** still-trusted sibling.
- The hubs are `traverse` (23 dependents), `interleave` (18), `fill` (14), `set_precedence` (8),
  `get_type_comment` (4), `require_parens` (3), `delimit_if` (2). **All the top hubs are themselves
  LEAVES**, so the 13-leaf batch is both portable now and unblocks nearly all of the 38.

**PORT ORDER FOR THE NEXT WINDOW: the 13 leaves first, then re-emit and take the 38 in topological
order.** This SUPERSEDES #22's "start with the 23 shortest bodies" — `require_parens` is the
shortest body in the class and it is *not* portable first. **Shortest != portable-first.** Note the
happy accident: `set_precedence` is a leaf, so it ports in batch 1; the 3 starred-blocked bodies
(`visit_Compare`, `visit_comprehension`, `visit_MatchOr`) are its CALLERS and stay deferred.

---

## WHAT #22 ESTABLISHED (all still valid; its vacuity caveat is now closed by #23 above)

A **~55-minute** window against the same deadline (`.driver-deadline` = 1788251064). The window was
too short to start a build, and the supervisor named exactly one job: **run a prover on ladder item
1a**, which #21 built and gated only to `L3-tc`. Lesson (hh) — *type-check success is not a
conversion criterion* — is the whole reason this had to happen before anything was banked on 1a.

## THE JOB: whole-file proof of `src/self-annotate/src/frontend/pure_ast.py`

Launched at T-53min, detached (`nohup`, so it survives a turn ending — instrument fact 8 is about
watchers, not about the proof process itself):

```
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad
PYTHONHASHSEED=0 python3 -u src/pycsl/pycsl.py \
  src/self-annotate/src/frontend/pure_ast.py \
  --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' \
  > scratchpad/r22/pure_ast_proof.log 2>&1 &
```

## PROOF VERDICT — **GREEN. 2857 / 2857 Valid, 0 non-Valid.**

**Ladder item 1a STANDS.** The unannotated-vararg -> `seq int` pyval lowering is not merely
type-checking; the whole of `pure_ast.py` proves under it.

| | |
|---|---|
| proof obligations | **2857** |
| `Valid` | **2857** |
| `Unknown` / `Timeout` / `Failure` / `Invalid` | **0** |
| provers | Alt-Ergo 2.6.3, Z3 4.13.3 (`--timelimit 5`, `-a split_vc`) |
| wall clock to full flush | ~13 min (the proof engine phase) |

Evidence: `scratchpad/r22/pure_ast_proof.log` (2857 `Prover result is: Valid` lines, zero
non-Valid; tally it with a python heredoc, NOT `grep` — instrument fact 14).

**This retires lesson (hh)'s open exposure on 1a.** #21 landed 1a on `L3-tc` alone and the campaign's
own rule is that a type-check is not a conversion criterion. It has now been paid: the criterion was
applied, and 1a passed it. Nothing built on top of 1a is resting on an unproved emitter change.

**Caveat, stated precisely so nobody over-reads the green.** The run had, at window end, moved past
the proof engine into pycsl.py's **per-goal non-vacuity phase** (one `why3 prove -g` per goal against
`scratchpad/.pycsl_vac_*.mlw`; it was ~200 goals in and still going). That phase is a SEPARATE gate
from the proof and it had NOT finished. **The proof plane is green; the vacuity plane is UNFINISHED,
not failed.** First action next window: re-run and let it finish, or run
`bin/check-emitted-vacuity.py --emit` (remember: a false green without `--emit`, instrument fact 3).

**One more fact worth having: the emitted `pure_ast.mlw` declares ZERO `axiom`s.** So those 2857
goals are discharged without the module contributing anything to the ledger. The campaign ledger
stays at 3 and this file adds nothing to it.

**The other two L-planes are INHERITED, not re-run.** The tracked tree has not changed since #21
gated them at `44150508` (this window's commits touch `getting-better/` only), so #21's fidelity
(2-DIVERGED baseline) and byte-inertness (3/3) results carry over unchanged. #22 re-verified the
metric itself fresh: **markers 491 · grep 516 · offset 25 · unattached 0 · ledger 3.**


## What #22 VERIFIED about 1a independently (all fresh, from the emitted `.mlw`)

`--no-proof --keep-mlw` on `pure_ast.py` (1.8 s, instrument fact 7) leaves
`src/self-annotate/src/frontend/pure_ast.mlw` on disk (gitignored, so it never dirties the tree).
In it, **the 1a capability is really present** — this is not a no-op emission:

- `let _unparser__write (self: _unparser) (text: seq int) : unit` at line 4847 — a **real
  parameterized `let`**, not a `val`, and not a zero-parameter facade.
- `val _unparser__set_precedence (self: _unparser) (precedence: int) (nodes: seq int) : unit`
  at line 4241 — the vararg is a formal here too.
- **58 `write` call sites**, every one materialized as `Seq.cons … (Seq.empty: seq int)`
  (266 `Seq.cons` occurrences file-wide). Element values are the same `str_hash_op` ints the
  drop-behaviour used: `self_write_1 (Seq.cons 260070937 (Seq.empty: seq int))`.
- `L1 ✓ L2 ✓ L3-tc ✓` reproduced independently of #21.

## THE RECORDED PRICE OF THE NEXT LEVER WAS WRONG (again) — and it is BIGGER, not smaller

Applying #21's own lesson (*a recorded price is a claim too*) to the price #21 itself recorded:

| record | recorded | **measured by #22** |
|---|---|---|
| markers in `pure_ast.py` | 96 | **95** |
| `_Unparser` family lever | 51 | **54 markers** (51 of them attach to `_Unparser` methods; 1 sits behind an `@_contextmanager` decorator; the rest are nested/decorated defs) |

Per-class marker census of `pure_ast.py` (95 total):
`_Unparser` **54** · `_Parser` 24 · `AST` 5 · `Comment` 3 · `NodeVisitor` 3 · `_Tok` 2 ·
`_ABC`/`Ellipsis`/`NodeTransformer`/`_Precedence` 1 each.

So `_Unparser` is **54 of 491 = 11.0%** of the whole campaign's remaining metric in ONE class in ONE
file. It is by a wide margin the largest single lever left, and the recorded figure understated it.

**Also measured, and it matters for how step 3 is planned:** all 51 trusted `_Unparser` methods are
`\trusted` *stubs with elided bodies* — an `ast.walk` over the mirror finds **zero** `self.write`
calls and **zero** starred forwarding inside them, because there is nothing inside them. The 58
`Seq.cons` call sites above are in the ALREADY-CONVERTED methods. Step 3 is therefore a *porting*
job (bring each real body into the mirror), not a *repair* job, and the `write` signature it must
target is the one now verified above.

## THE #1 ITEM FOR THE NEXT WINDOW

**Un-trust the `_Unparser.write` family — 54 of the 491 markers.** It is the campaign's largest
remaining single lever and, as of this window, the emitter capability under it is proved-or-refuted
(see the verdict) rather than merely type-checked.

Two live degrees of freedom, both opened in the last two windows and **neither one used yet**:

1. **`vararg_elem_type` makes the element type a PER-FUNCTION choice.** #20 measured that
   `seq string` turns **40 of 56** write call sites into real Why3 string literals (a fidelity gain)
   while 16 int-sourced sites are unbridgeable; #21's `seq int` is uniform and annotation-free.
   These were believed mutually exclusive. They are not, since #21's infrastructure carries the
   element type per function. Worth ONE probe, not a scope.
2. **STARRED-ARGUMENT FORWARDING (`g(*args)`) is deliberately still gated out** (Module5 `ast.walk`
   for `Starred(Name(vararg))`; a starred arg lowers to its bare inner value at
   `expressions._expr_to_whyml` `"Starred"` ~14613). It keeps the historical drop behaviour.
   Reopening capability: positional re-binding of an unknown-length sequence against the callee's
   arity. **It affects `_new` / `Ellipsis.__new__` / `Constant.__init__` ONLY — `_Unparser.write`
   and `set_precedence` are NOT affected, so the 54-marker lever is unblocked by it.**
   Per lesson (#20): the first move against this capability is to TRY it, not to scope it.

## STEP 3 IS FULLY SCOPED BY #22 — it is 503 lines of PORTING, and 48/51 are unblocked

`src/pycsl/frontend/pure_ast.py` is the live counterpart of the mirror (note the path: it is under
`frontend/`, NOT `src/pycsl/pure_ast.py`). Measured by AST diff against it:

- **All 51** trusted `_Unparser` stubs have a live body available. **Zero missing.**
- **Total live body lines to port: 503.** Size distribution: **23 bodies are <=5 lines**,
  19 are 6-15, only 9 are 16+. Largest five: `visit_arguments` 50, `_str_literal_helper` 38,
  `visit_JoinedStr` 32, `visit_ClassDef` 23, `visit_MatchClass` 22. Smallest are 2-3 lines
  (`require_parens`, `visit_ParamSpec`, `visit_TypeVarTuple`, `fill`, `set_precedence`,
  `visit_Delete`, `visit_Global`, `visit_Import`).
- **Start with the 23 <=5-line bodies.** They are a natural first batch and, at ~0.45 markers per
  line ported, the cheapest markers left anywhere in the campaign.

### THE STARRED BLOCKER IS REAL FOR THIS FAMILY — but it is NOT the shape the record names

The record (and `Module5_IREmitter.py:4986-4999`) says star-forwarding "affects `_new` /
`Ellipsis.__new__` / `Constant.__init__` only" and that "`_Unparser.write` and `set_precedence` are
NOT affected". **The first half is right about the GATE; the second half is wrong about the FAMILY.**

Read the gate: it walks the *defining* function and drops the vararg only when that function's OWN
vararg NAME is star-forwarded (`isinstance(_n.value, ast.Name) and _n.value.id == _va0.arg`).
`set_precedence`'s own 3-line body forwards nothing, so it correctly keeps its `seq int` formal —
confirmed in the `.mlw`. **But three of the 51 live bodies to be ported are CALLERS that pass a
starred actual INTO that vararg formal:**

```
visit_comprehension : self.set_precedence(_Precedence.TEST.next(), node.iter, *node.ifs)
visit_Compare       : self.set_precedence(_Precedence.CMP.next(),  node.left, *node.comparators)
visit_MatchOr       : self.set_precedence(_Precedence.BOR.next(),  *node.patterns)
```

This is a **different capability** from the recorded one: not `g(*args)` forwarding of an enclosing
vararg, but **MIXED positional-plus-starred packing at a call site into a `seq int` formal**
(`f(a, *b)` — concat a materialized prefix onto an existing sequence). Nothing in the tree gates it
today, so its behaviour on port is UNKNOWN and must be probed, not assumed. Two of the three even
have a non-starred positional *before* the star, which is the hard sub-case.

**#22 RAN THAT PROBE.** Isolated it in a 15-line standalone file (`scratchpad/r22/star_probe.py`,
a `sink(self, p, *nodes)` plus a star-only caller and a mixed caller) rather than editing the mirror
— zero risk, ~2 s. **The result is unambiguous, and it is the same for BOTH shapes:**

```
let p__caller_star_only (self: p) (xs: array int) : unit =
  let _ = (self_sink_2 1 (Seq.cons xs (Seq.empty: seq int))) in ()
let p__caller_mixed (self: p) (a: int) (xs: array int) : unit =
  let _ = (self_sink_2 1 (Seq.cons a (Seq.cons xs (Seq.empty: seq int)))) in ()
```

A `Starred` actual in a vararg position is packed **as a single ELEMENT** — `Seq.cons xs …` — so the
whole sequence lands where one element belongs. It does not splat. `L3-tc ✗`:

> `This expression has type seq.Seq.seq int, but is expected to have type seq.Seq.seq (array.Array.array int @rho)`

**Two things follow, and the second is the important one:**

1. The 3 bodies are genuinely blocked. Star-only (`visit_MatchOr`) is blocked exactly as hard as
   mixed (`visit_Compare`, `visit_comprehension`) — the prefix is not the hard part; the splat is.
2. **The failure is LOUD, not silent.** It is a Why3 TYPE error at L3-tc, not a mis-typed-but-
   accepted lowering. So this residue can never quietly produce a wrong proof — porting one of the
   3 by accident fails the gate immediately. That makes "port the 48 now" safe to do without first
   solving the 3.

**PRECISE REOPENING CAPABILITY (supersedes the vaguer `g(*args)` wording):** at a call site, a
`Starred` actual in a vararg position must lower to a sequence **CONCATENATION** of its inner value
(coerced to `seq elem`) onto the materialized prefix — `Seq.(++) (Seq.cons a Seq.empty) (to_seq xs)`
— instead of today's `Seq.cons xs`. That is a call-site packing change in the same materialization
code #21 added, not the "positional re-binding against the callee's arity" the record describes;
re-binding is only needed when a starred actual feeds NON-vararg formals, which is the
`_new`/`__new__`/`Constant.__init__` case, not this one. **These are two different capabilities and
the record conflates them.**

**Consequence for the plan: port the 48 unblocked bodies now — do not let the 3 hold up 94% of the
lever.** The 3 are a bounded, well-typed follow-on.

## Then, in this order (carried forward, still valid)

2. **`ControlFlowStmtMixin._handle_return_stmt`** — the ONE non-constructor model-visible false
   frame left (18 fields via-callee). `module6_whyml/stmt_control_flow` is 1846 goals, ~45 min.
3. **`scratchpad/w3/fix_assigns.py` IS THE REUSABLE TOOL.** It converges `#@ assigns` / `#@ raises`
   / `#@ \diverges` against Why3's own error text. Point its `MIR` constant at another mirror.
   **Every wall whose recorded reason is "the effect summary cannot be made exact" should be
   re-tested with it FIRST.**
4. **The `pyx_view` ADT redesign / record AST model** remains the soundness floor under the
   object-identity question. Obstacle: `pure_ast`'s node classes are SYNTHESIZED AT IMPORT by
   `type(name, (base,), body)` from `_NODE_SPEC`.
5. `val function csl_to_ir_op` is **CLOSED** (relaunch #19). Do not re-open it.

## Recorded boundaries carried forward — do not re-grind without the named capability

- `_csl_to_ir` is **BROKEN**; strike it from any ladder that still lists it.
- **The attribute-store third horn** works and is axiom-free; blocked on OBJECT-IDENTITY INJECTIVITY.
- **`crosscheck_ir.pairwise`** — spiked and working, demand NIL.
- **The shadowed TCFAIL residue — [PYVAL / ARRAY-INT MODEL SPLIT]** (33 sites / 13 methods).
  Same disease as the `_Unparser` finding, one type-family over.
- `_fin` / `_max_end` / `_fin_block` — [ERASURE-LEDGER]; `node(self, name, start_tok, **kw)` —
  [MODEL]; `_slice`; **`Module2_Parser`'s contract-expression cluster** (TERMINUS);
  `_decode_escapes` / `_decode_string`; `identifiers.whyml_ident` / `stable_hash`;
  `struct_format.parse_format` / `calcsize`; `proof2why3/normalize`'s whole file (regex).
- `pure_ast._Parser.error` / `.unsupported` — they DO convert (491→489) but
  `bin/check-emitted-vacuity.py --emit` reports 2 NEW erasures. **REOPENING: a modelled message
  payload on the raise** — the same decision `_fin` needs.
- **`exception_model.bases_closure`** — the wall is the VALUE MODEL, not termination.

## Instrument facts — unchanged and still load-bearing

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. `--import-path src/pycsl` is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit` — but WITH `--emit` it is CHEAP
   (re-emits all 52 mirrors `-P 7 --no-proof --no-typecheck --keep-mlw`, **under a minute**, and it
   IS the vacuity plane). Prefer it over pycsl.py's slow embedded per-goal `why3 prove -g` loop.
4. `.gitignore` has `*.mlw` — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof. A run can sit at ZERO prover results for 50 minutes and then
   flush 1500 — do NOT conclude "stuck"; check for live `alt-ergo`/`z3` children.
   **#22 confirms this directly: `pure_ast.py` produced 0 `Prover result` lines for its entire
   first 20 minutes with exactly one live prover child throughout.**
7. A FAILING `pycsl.py` run is much FASTER than a passing one. **Emitting `pure_ast.py` alone
   with `--no-proof --keep-mlw` takes 1.8 SECONDS** — a vastly cheaper probe than a sweep.
8. BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING. **But a `nohup … &` proof process DOES**
   (#22 relied on this). `scratchpad/w3/prove.sh` / `prove_wt.sh` prove a list sequentially;
   `bin/byte-diff-sweep.sh` runs `--no-typecheck`.
9. `scratchpad/w2/sweep.sh <abs-root> <abs-outdir>` emits all 52 mirrors WITH L3-tc in ~35 s
   and writes an md5 manifest. **PASS ABSOLUTE PATHS.**
10. `--fun` CANNOT probe `Module5_IREmitter` at all — whole-file or nothing.
11. A git worktree is the right place for a spike. Sync with
    `git checkout --detach $(git -C <main> rev-parse HEAD)`.
12. A PROOF TRANSFERS BETWEEN TREES WHEN THE EMISSION MANIFEST IS IDENTICAL.
13. The Alt-Ergo pin at `pycsl.py:1318` is stale. Pass `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'`
    EXPLICITLY; do NOT edit the pin.
14. `grep` here is ugrep and MISBEHAVES on `driver-progress.log`. Use python, via a
    `python3 - <<'PYEOF'` heredoc, never inline `-c`.
15. `cd` PERSISTS ACROSS A COMPOUND BASH COMMAND. Use absolute paths after any `cd`.
16. **NEVER put a `\trusted` marker LITERAL in a mirror comment** — it counts as a MARKER.
17. `TMPDIR=/home/fabrice/git/pycsl/scratchpad` for `bin/check-shadowed-selfcalls.py`.

## The method note THIS session paid for (#22)

**THE PRICE LESSON IS NOT A ONE-OFF — IT REPEATS ON THE VERY NEXT RECORD YOU READ.** #21 discovered
that a recorded price is a claim and corrected #20's. #22 then applied the same five-minute
`ast`-and-`grep` census to the price #21 itself had just written down, and it was wrong too — in the
*favourable* direction (54, not 51). Both directions matter: an overstated price stops a build that
should happen, and an understated one under-funds it. **The census that corrects a price costs
minutes; the record it corrects has stood for windows.** Run it as reflex on any figure you are
about to plan against, including one written an hour ago by the immediately preceding worker.

Corollary specific to this metric: **counting `\trusted` markers is not the same as counting
convertible methods.** In `pure_ast._Unparser` those numbers are 54 and 51 — the gap is markers on
decorated and nested defs. Quote the marker count for the metric, the method count for the plan,
and never silently substitute one for the other.

## The method notes #20 and #21 paid for (still the operating rule)

**A REOPENING CAPABILITY IS A CLAIM, AND SO IS A RECORDED PRICE.** This campaign has now found a
recorded boundary's *reason* wrong seven times, a recorded *price* wrong twice, and a named
*capability* already-built-and-working once. The standing rule: **verify every part of a record —
reason, capability, AND price — against the emitted `.mlw` and the actual tree**, before you spend
a window on it. `check-self-annotate-sync.sh` is a live plane for EMITTER edits too, not only
mirror edits; run it after ANY `src/pycsl/` change.
