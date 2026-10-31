#!/usr/bin/env python3
"""check-trusted-frame-honesty — the FOURTH plane of the self-annotation gate battery.

WHAT IT MEASURES.  A `\\trusted` mirror stub's contract is ASSUMED, never checked: Module 6
emits it as an abstract `val` and Why3 takes it on faith.  So a stub that declares
`#@ assigns \\nothing` while the LIVE method it stands for really does mutate `self` state
states something FALSE, and every converted caller is entitled to assume the field is
unchanged across the call.  That is an unsoundness the proof planes cannot see: the
whole-file proof is GREEN, the corpus byte-diff is 0, and the mirror-sync gate is happy,
because a `\\trusted` stub HAS no body to check the claim against.

This is the trusted-surface twin of the CONVERTED-body frame gap that the object-state
write model closed (`module6_whyml/abstract_ops.py::_add_abstract_op`): there, an abstract
`setattr_*` had no effect, so a mutating body satisfied `assigns \\nothing` vacuously, and
Why3 now rejects it.  Here there is no body at all, so only this static check can see it.

HOW.  Parse the live tree, compute each function's DIRECT `self.<attr> = ...` stores, then
propagate along the call graph to a fixpoint.  `self.<m>()` resolves inside the caller's
class, its transitive bases, and — when the caller is itself a MIXIN — the bases of every
composite that mixes it in (so a mixin calling a sibling mixin resolves, while two
unrelated SUBCLASSES of a common base do not bleed into each other).  Module-level calls
resolve within the same file.  The analysis is an OVER-approximation of the call graph and
an UNDER-approximation of the mutation set (it does not model aliasing or `setattr()`), so
the number it reports is a LOWER BOUND on the false-frame surface.

TWO NUMBERS, AND THE SECOND IS THE ONE THAT BITES.  The headline count is every offending
stub.  The RATCHETED count is the subset whose class is `@mutable_state`, i.e. whose `self`
is emitted as a Why3 RECORD WITH REAL FIELDS: only there can a converted caller actually
READ the field and rely on the missing `writes`.  For an opaque-self class the field is not
modelled at all (reads go through unconstrained `getattr_*` oracles), so the annotation is
dishonest to a HUMAN reader but the model claims nothing false.  Correcting one of those is
cosmetic; correcting a `@mutable_state` one changes the emitted `val` and can break a caller
that was relying on the false assumption — which is exactly the point of finding it.

THE CONVERTED SURFACE (added 2026-08-31, relaunch #19) -- THE PLANE'S OWN BLIND SPOT.
The check above was scoped to `\\trusted` stubs on the reasoning that a CONVERTED method
has a body, so Why3 checks its frame.  Measured against the emitted `.mlw`, that reasoning
is only half true, and the half that fails is the half that matters:

  - IN ITS OWN FILE a converted method really is checked.  Module 6 emits an explicit
    `writes {  }` for `#@ assigns \\nothing` (NOT an omitted clause), and Why3 rejects an
    under-declared frame -- confirmed by spike: an omitted `writes` is INFERRED and
    silently accepted, an explicit empty one raises `this expression produces an unlisted
    write effect`.  But what it is checked against is the EMITTED body, which is an
    ERASURE of the live one: the very calls that do the writing are commonly lowered to
    effect-free abstract `val`s, so `writes {  }` can be true of the emission and false of
    the source.
  - IN EVERY OTHER FILE the method appears as a caller-side abstract `val` minted from the
    SAME declared `#@ assigns` (e.g. `val self__seq_init_expr_3 ... writes {
    self._current_self_type, self._in_spec, self._string_local_vars }`).  That `val` has
    no body, so the frame is ASSUMED there exactly as a `\\trusted` stub's is -- and a
    converted method declaring a false `assigns \\nothing` hands every cross-file caller
    an unchecked "this field did not change".

So the converted population is the same hazard one step removed, and no plane sees it: the
fidelity gate compares bodies, not frames; the whole-file proof checks the erased emission;
the byte-diff and the vacuity probe are blind to it.  It is reported as a SECOND population
with its own two ratchets.  First measurement: 567 converted methods declare
`assigns \\nothing`, 69 stand for a live body that transitively writes `self` (12 directly),
2 MODEL-VISIBLE -- `ControlFlowStmtMixin._handle_return_stmt` (18 fields, via-callee) and
`proof2why3/parser.py::_Parser.__init__` (2 fields, direct; a constructor, so it belongs to
the constructor bucket the trusted plane also bottoms out in).

TABLE-AWARE DISPATCH (added 2026-08-31, relaunch #19) -- WHY THE NUMBERS WENT UP.
The call-graph walk resolved `self.<m>(...)` by attribute name only, so it could not see a
DISPATCHER: `handler = self._TABLE.get(type(node))` followed by `getattr(self, handler)(x)`
names its callee through a class-level dict literal.  That is precisely how the emitter's
`_csl_to_ir` / `_py_expr_to_ir` reach their handlers, so the analysis was blind to the
methods whose frames matter most.  Handler tables are now collected (class- and
module-level `NAME = {K: "method", ...}`) and an edge is added to every method a table
names -- but ONLY from a body that also performs a `getattr(self, ...)` call, so a body
that merely TESTS membership in a table contributes nothing.  Measured: every table edge in
the tree comes from a genuine dispatcher (tightening the rule changed no count).

The ratchets were RAISED to the new measurements -- 3/73 -> 6/76 trusted, 2/69 -> 63/130
converted.  That is a MEASUREMENT improvement, not a tree regression: the same tree was
always this dishonest, the gate could not see it.  The three NEW trusted model-visible
offenders (`_get_mutex_invariant_ir`, `_csl_list_to_ir`, `_py_stmts_to_ir`) and 60 of the
new converted ones are ONE fact: the whole `_csl_*` handler family declares
`#@ assigns \\nothing` while reaching `_csl_in`, which writes `self._fresh_var_counter` --
and `_csl_in`'s OWN mirror declares that write honestly.  This is the same `unlisted write
effect` the `_csl_to_ir` CERTIFIED-BOUNDARY already names as the first of its three
blockers; the gate now MEASURES it instead of only recording it in prose.

MODEL-VISIBILITY IS DECIDED BY THE EMITTED RECORD (added 2026-08-31, relaunch #19).
The tool now EMITS every mirror itself (~35 s, needs `why3` on PATH) and asks the direct
question: does this file's emitted `type <cls> = { ... }` actually DECLARE the field?  The
previous source-assignment heuristic -- "the mirror file assigns `self.<f>` somewhere" -- is
wrong in BOTH directions, and both were measured:
  - OVER: `ControlFlowStmtMixin._handle_return_stmt` was reported model-visible for
    `_comp_content_counter` / `_current_params` / `_current_self_type` /
    `_frame_trigger_active`, and the emitted `type controlflowstmtmixin` carries NONE of
    those four.  (It stays model-visible for a DIFFERENT pair, `_func_return_type` and
    `_in_spec`, which the record does carry -- so the verdict survives and its REASON does
    not.)
  - UNDER: `ExpressionEmissionMixin._ifexpr_seq_arm` was reported unmodelled and the
    emitted `type expressionemissionmixin` carries FOUR of its written fields.  That one
    raised CONVERTED_RATCHET from 2 to 3.
A THIRD refinement, and it is the one that emptied the trusted plane: a method the emitted
`.mlw` DOES NOT DECLARE AT ALL carries no frame, so its `#@ assigns` cannot mislead any
prover.  MEASURED: not one of the four `__init__` offenders this plane used to report as
MODEL-VISIBLE is emitted as a WhyML symbol -- Python construction lowers to a record
literal, not to a method call -- and correcting all four left the emission of all 52 mirrors
BYTE-IDENTICAL.  The "three model-visible constructors" earlier sessions recorded as the
plane's floor were therefore never model-visible at all.

`--emit-dir DIR` reuses an existing emitted-mirror directory (either naming scheme);
`--no-emit` falls back to the heuristic and the ratchets then do NOT apply.

THE PARAMETER-WRITE ARM (added at route #401).  Every arm above compares a frame with the
live body's `self.<f>` writes.  A write THROUGH A PARAMETER is outside that population --
`pure_ast.NodeTransformer.generic_visit` declared `assigns \\nothing` over an in-place rewrite
of `node`.  The arm walks EVERY `\\trusted` stub (any frame, not only `\\nothing`) and every
converted method, computes the parameters its live body may write
(`bin/lib_param_write_closure.py`), and reports the ones the declared `#@ assigns` does not
name, each residual NAMED in a ledger with its reason.  A third count measures how many
declared parameter frames actually reach the emitted `writes` (only list parameters do).
See the constants block `PARAM_*`.

THE DECLARATION ARM (added driver run #3, wall `cross-mixin-declaration-stubs`, R0).
Every arm above looks a mirror method up in its LIVE TWIN: `(live file, class, name)`.  A
cross-mixin DECLARATION has no live twin -- it is a local bodyless stand-in (a `\\trusted`
stub, or a `#@ requires_method` window) for a method the composite's MRO resolves in ANOTHER
class -- so `trans.get(live_key)` was None and the plane passed all 26 of them unseen.  At
8fdfce794 nine of them declared a frame NARROWER than their definition's (e.g.
`ControlFlowStmtMixin._match_pattern_cond` `assigns \\nothing` over a 22-field definition), and
three more (the ghost `_e` / `_expr_to_whyml_string_ctx`) had been load-bearing for 30
verified frames (route #488).  The census and the MRO resolution live in
`bin/lib_declarations.py`, shared with `bin/check-declaration-conformance.py` so the two
planes cannot disagree about the population.  For each declaration, with LIVE = the resolved
definition's transitive `self` writes, DEF = its mirror twin's declared frame, DECL = the
declaration's own frame:
  OWN deficit       (LIVE & DEF) - DECL   the declaration understates a write its definition
                                          already declares. MODEL-VISIBLE (the field is in the
                                          declaring file's emitted record): HARD 0
                                          (`DECL_OWN_VISIBLE_RATCHET`). Unmodelled (no record
                                          in any unit that sees the declaration carries it, so
                                          naming it would only raise the assigns-writes-survival
                                          TRAP): ratcheted (`DECL_OWN_RATCHET`), and
                                          `bin/check-declaration-conformance.py` checks the
                                          projection is exact, composites included.
  INHERITED deficit LIVE - DEF - DECL     the DEFINITION's own frame understates its live
                                          closure; copying it cannot fix this: ratcheted
                                          separately (`DECL_INHERITED_RATCHET`).
The `\\nothing` populations above also resolve a declaration through the MRO now (a
`\\trusted` declaration claiming `assigns \\nothing` counts toward TOTAL_RATCHET).
NEGATIVE TEST: on the base tree 8fdfce794 the arm reports OWN 9, 5 of them MODEL-VISIBLE
(RED), and the trusted `\\nothing` total 3 > 1 / model-visible 2 > 0 (RED); after R1 (each
declaration widened by every definition field the declaring file's record carries) it is OWN 7,
0 model-visible, and total 1 / model-visible 0 (GREEN).

RATCHET.  The counts may go down, never up -- EXCEPT when the analysis itself gets sharper,
which must be stated in this docstring with what it newly sees, as the paragraph above does.
Lower them deliberately when a stub is converted or its `#@ assigns` is corrected.
"""
import argparse
import ast
import collections
import os
import re
import shutil
import sys
import tempfile

# (#49) Refuse to emit while the soundness battery holds the lock (bin/lib_plane_lock.py).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from lib_plane_lock import refuse_if_battery_running as _refuse_if_battery_running
except ImportError:                                   # helper absent: behave as before
    def _refuse_if_battery_running(_plane):
        return None


# ===========================================================================================
# RE-BASELINED 2026-09-02 (relaunch #31) — THE ANALYSIS GOT SHARPER, THE TREE DID NOT GET
# WORSE. This is the one condition under which any ratchet in this battery may RISE, and it
# is the same condition under which `check-shadowed-selfcalls.py` went 13 -> 14 at #30.
#
# The write detector saw `self.x = ...` and NOTHING ELSE. It did not see:
#     self.xs.append(v)      self.s.add(v)        self.d.update(m)     self.xs.sort()
#     self.d[k] = v          del self.d[k]        self.d.setdefault(k, v)
# — which is how the emitter mutates most of its state. (`self.d[k] = v` has an
# `ast.Subscript` target, not an `ast.Attribute` one, so it missed the store walk too.)
#
# ON THE SAME TREE, with the sharper detector:
#     trusted   total          63  ->  82   (direct writers 23 -> 32)
#     converted total          68  -> 133   (direct writers 11 -> 12)
#     converted MODEL-VISIBLE   2  ->   4
# The four model-visible CONVERTED offenders are `expressions._ifexpr_seq_arm`,
# `statements._materialize_bridge`, `._materialize_str_bridge`,
# `._wrap_body_with_return_catch` — all of them reach `_add_abstract_op`, whose
# `self._abstract_ops[k] = ...` is exactly the subscript store the old walk could not see.
# Relaunch #30 already recorded the lesson that a CONVERTED method must not call
# `_add_abstract_op` because it writes `_obj_state_written`; this makes the OTHER half of
# that write visible too.
#
# THE MOST INSTRUCTIVE SINGLE OFFENDER, and it is in the CONVERTED population:
# `pure_ast._Unparser.write` — the 97-call-site output hub. Its whole body is
# `self._source.extend(text)` and it is emitted as
#     let _unparser__write (self: _unparser) (text: seq int) : unit
#       writes {  }
#     = let _ = (self__source_extend_1 text) in ()
# a RECEIVER-LESS opaque op with no effect, under a frame that says the method changes
# nothing. Nothing in the battery could see it: L3-tc passes, the proof passes, non-vacuity
# passes (the body reads `text`), shadowed-selfcalls passes.
#
# These numbers are a re-baseline of the MEASUREMENT, not a licence: they may only go down
# from here, and the four model-visible converted offenders are a live ladder item.
# ===========================================================================================
RATCHET = 0           # MODEL-VISIBLE offenders: `@mutable_state` class AND a modelled field
# The Python collection mutators that write through a self field WITHOUT an
# attribute STORE. `sort`/`reverse` are in-place; `pop`/`popitem`/`clear`/`remove`/
# `discard`/`insert`/`setdefault`/`update`/`extend`/`append`/`add` all mutate.
_MUTATING_METHODS = frozenset({
    "append", "extend", "insert", "add", "update", "pop", "popitem", "clear",
    "remove", "discard", "setdefault", "sort", "reverse",
})

# (#43) 0 -> 1, AND THE POPULATION DID NOT GROW — IT BECAME VISIBLE. The single member is
# `pure_ast._Unparser.write`, which route #13 caught: its body `self._source.extend(text)`
# lowered to `val self__source_extend_1 (x0: seq int)` — no `self`, no `writes` — so the
# method emitted as `writes { }` and its `#@ assigns \nothing` was FALSE while it was
# CONVERTED and counted in the converted population below (which drops 95 -> 94 with it).
# Its honest frame `#@ assigns self._source` was written, and the whole class re-framed
# from the live transitive write set (58 mirror methods widened, 99 of 107 reach
# `self._source`); L3-tc then failed at `interleave`, which takes `write` AS A FIRST-CLASS
# CALLBACK — `This function has side effects, it cannot be used as pure`. 19 `_Unparser`
# methods build such a lambda. CERTIFIED BOUNDARY; reopening capability = a lowering for an
# effectful higher-order callback. Moving it to `\trusted` makes the assumption EXPLICIT
# and REVIEWED instead of silent, which is what this counter is for.
TOTAL_RATCHET = 1     # 63 -> 82 at #31 by the SHARPER DETECTOR; 82 -> 28 -> 19 -> **0** at
                      # #32. EVERY `\trusted` stub in the mirror now declares a frame that
                      # is TRUE of its live body, derived per stub from the same live
                      # transitive self-write closure this file computes
                      # (`scratchpad/w5/honest_trusted_frames.py`), with the caller fixpoint
                      # closed against Why3's own error text
                      # (`scratchpad/w5/framefix3.py`): 5 iterations on `expressions.py`,
                      # 7 on `statements.py`, 25 on `pure_ast.py`, 1 on `functions.py`.
                      # A `\trusted` stub's `assigns` is ASSUMED and never checked, so a
                      # false one is an unsoundness no proof plane can see — this is the
                      # plane's whole point, and it is now at its floor.
                      # 0 IS A HARD FLOOR: any new offender is a regression.
                      # THE HONEST CAVEAT, unchanged: the closure can still
                      # UNDER-approximate (the #31 `_walk_body` blind spot), so 0 means
                      # "nothing KNOWN false", not "every declaration proven true".
CONVERTED_RATCHET = 0         # 2 -> 4 at #31 by the SHARPER DETECTOR (the `_add_abstract_op`
                              # subscript store); 4 -> 1 at #32 by GIVING THE TWO
                              # `_add_abstract_op` CROSS-MIXIN PROTOCOL STUBS THEIR HONEST
                              # `#@ assigns self._abstract_ops, self._obj_state_written`
                              # and driving the caller frames to a FIXPOINT against Why3's
                              # own error text (6 iterations on `statements.py`).
                              # **1 -> 0 at #33**, and the plane is now at its floor in BOTH
                              # populations. The last one was `expressions._ifexpr_seq_arm`,
                              # recorded by #32 as a CERTIFIED BOUNDARY. It was not one: #32
                              # built the capability that closes it — a `requires_method` /
                              # `depends_method` window may DECLARE THE DEPENDENCY'S FRAME —
                              # and then deliberately did not use it, on the reasoning that
                              # Why3 would demand the declared `writes` be EXACTLY the
                              # model's effect while the live closure names ~20 fields the
                              # model erases. That reasoning was superseded by the label
                              # FILTER the same window put in: writing the honest 22-field
                              # `#@ assigns` on BOTH the window and the method leaves the
                              # SIX that the record actually labels, the avatar declares
                              # exactly those, and Why3 accepts it. The `writes {  }` it
                              # replaces was the false claim.
# (#43) 95 -> 94: `pure_ast._Unparser.write` left this population for the trusted one above.
CONVERTED_TOTAL_RATCHET = 63  # run #3 (z1, 2026-10-30): 93 -> 63, route #488 -- the 30 ghost handlers of expr_ghost_collections.py / expr_ghost_spec_ops.py given their true (widened) frames instead of `assigns \nothing` (29 re-proved, `_handle_mktuple_expr` re-trusted). (#49) gen #35: 94 -> 93, `_materialize_if_seq` given a concrete bridge + honest frame. Earlier: 68 -> 133 at #31 by the SHARPER DETECTOR; 133 -> 99 at #32;
                              # 99 -> 98 at #33 (`_ifexpr_seq_arm`), 98 -> 96 by the
                              # cross-mixin protocol stubs' caller fixpoint
                              # (the three `statements.py` callers above); 96 -> 95 at #34
                              # (`ConcurrencyChecker._walk_body`, the ONE offender this
                              # plane's own MODEL-VISIBLE predicate could not see -- see
                              # the note on `_visible` below). Every offender
# (#49) gen #31 — THE SECOND KIND OF DISHONEST FRAME, and this plane's own header names the
# shape while its analysis cannot reach it: *"a stub that declares `#@ assigns \\nothing`
# while the LIVE method it stands for really does mutate `self` state states something
# FALSE"*. The fixpoint below computes `self.<attr>` stores and propagates them along the
# call graph — so a MODULE-LEVEL function that shells out to `why3 prove` mutates no
# attribute and is invisible to it.
#
# `#@ assigns \nothing` does not mean "writes no modelled state". `test-suite/annotations.md`
# §926 and `docs/pycsl-static-semantics-reference.md` §2398 both gloss it the same way:
# **"(pure, side-effect-free)"**. A function that spawns a subprocess or creates a directory
# is not side-effect-free.
#
# RECEIVER-QUALIFIED ON PURPOSE. A first, looser census matched bare method names and
# produced two false positives immediately — `Module1_Ingestor::process` calls a LOCAL method
# named `run`, and `str.replace` is pure and everywhere. Only `subprocess.*` / `os.*` /
# `shutil.*` count here, which is why the measured number is 17 and not 21.
#
# NOT LOAD-BEARING TODAY: censused, ZERO un-trusted mirror functions call any of these, so no
# proof leans on a false frame. It is a TRAP, not a HOLE — and it is one green whole-file
# proof away from being a hole, which is exactly what a conversion session is hunting for.
# `getting-better/open-routes/finding-assigns-nothing-over-a-subprocess.md`
# (driver run #3, R0) THE DECLARATION ARM -- see the module docstring. OWN model-visible is a HARD 0;
# the unmodelled OWN total is ratcheted at 7; INHERITED is the measured residual of the trusted DEFINITIONS' own
# frames (13 declarations resolve to a definition whose frame omits live writes such as
# `_r188_stub_names` / `_r55_subsumed_name` / `r417_obls` / `r434_ok` / `ir` of the
# expressions.py `_e` family). Both may only SHRINK.
DECL_OWN_VISIBLE_RATCHET = 0
DECL_OWN_RATCHET = 7          # all unmodelled (see docstring); may only SHRINK
DECL_INHERITED_RATCHET = 13
MIN_DECLARATIONS = 20          # measured 26 (24 stubs + 2 requires_method windows)
EXTERNAL_EFFECT_CALLS = {
    ("subprocess", "run"), ("subprocess", "Popen"), ("subprocess", "check_output"),
    ("subprocess", "call"), ("subprocess", "check_call"),
    ("os", "system"), ("os", "makedirs"), ("os", "mkdir"), ("os", "remove"),
    ("os", "unlink"), ("os", "rmdir"), ("os", "rename"), ("os", "replace"),
    ("shutil", "rmtree"), ("shutil", "copytree"), ("shutil", "move"),
}
# Each entry NAMED with what it does, so a new one cannot arrive quietly. The clause is
# wrong for every one of them; the entry records that it is KNOWN wrong, not that it is fine.
KNOWN_EXTERNAL_EFFECT_NOTHING = {
    ("audit_proof_reverify.py", "_coqc_version"): "subprocess.run(coqc --version)",
    ("audit_proof_reverify.py", "_lean_version"): "subprocess.run(lean --version)",
    ("audit_proof_reverify.py", "verify_lean_file"): "subprocess.run(lake/lean)",
    ("audit_proof_reverify.py", "verify_rocq_file"): "subprocess.run(coqc)",
    ("proof2why3/extract.py", "extract_lean_statements"): "subprocess.run",
    ("proof2why3/extract.py", "extract_rocq_statements"): "subprocess.run",
    ("proof2why3/extract_lean_meta.py", "extract_lean_statements_meta"): "subprocess.run",
    ("proof2why3/sertop.py", "extract_via_sertop"): "subprocess.run(sertop)",
    ("proof2why3/sertop.py", "run_sertop_batch"): "subprocess.Popen(sertop)",
    ("proof2why3/sertop.py", "sertop_version"): "subprocess.run(sertop --version)",
    ("pycsl.py", "_check_rocq_proofs"): "subprocess.run(coqc)",
    ("pycsl.py", "_generate_rocq_obligations"): "os.makedirs",
    # NAMED BUT NOT REACHED, and that is the entry worth keeping. `_probe_one` is a NESTED
    # function (`def _probe_one` inside `_run_vacuity_gate`), carrying a real
    # `#@ \trusted` + `#@ assigns \nothing` and a live `os.remove`. `_mirror_nothing_stubs`
    # walks module and class bodies and does NOT descend into a function body, so the
    # population is 16 here and 17 in this table. DELETING THE ENTRY WOULD HIDE THE GAP:
    # every nested `\trusted` stub in the mirror is outside this plane's reach, and this
    # line is the only place that says so. Reopened by making the walk descend.
    ("pycsl.py", "_probe_one"): "os.remove (NESTED - outside the walk, see note)",
    ("pycsl.py", "_run_proofs"): "os.remove",
    ("pycsl.py", "_run_vacuity_gate"): "os.remove",
    ("pycsl.py", "_run_why3_prove"): "subprocess.run(why3 prove)",
    ("pycsl.py", "_why3_typecheck"): "subprocess.run(why3 prove --type-only)",
}
MIN_NOTHING_DECLARERS = 400   # (#49) gen #31 — a FLOOR on the POPULATION, and the only
                              # one here: RATCHET, TOTAL_RATCHET, CONVERTED_RATCHET and
                              # CONVERTED_TOTAL_RATCHET are all UPPER bounds, which an
                              # EMPTY walk satisfies perfectly. Measured 1 trusted +
                              # 499 converted = 500 methods declaring `#@ assigns
                              # \\nothing`. Raise it as the mirror grows.

# ===========================================================================================
# (#49) ROUTE #401 — THE PARAMETER-WRITE ARM. Everything above compares a stub's frame with
# the `self.<f>` writes of its live body. A write THROUGH A PARAMETER is outside that
# population, and the carrier was in the tree: `pure_ast.NodeTransformer.generic_visit` was
# `\trusted` with `#@ assigns \nothing` while its live body rewrites `node` IN PLACE
# (`old_value[:] = new_values`, `delattr(node, f)`, `setattr(node, f, v)`), so every caller
# (`desugar_chained_comparisons`, `splice_constant_exec`, both converted `\nothing`) was
# entitled to assume the tree it passed came back unchanged. The closure is computed by
# `bin/lib_param_write_closure.py` (flow-sensitive aliases, receiver-class-context call
# resolution; its docstring states where it over- and under-approximates).
#
# A NEW ARM WITH ITS OWN RATCHETS, never a loosening of the arms above. Population: every
# mirror method that is `\trusted` (resp. converted), keyed to its LIVE twin. Offender: the
# live closure writes a parameter the declared `#@ assigns` does not NAME (a target rooted at
# the parameter: `p`, `p.f`, `p[..]`). First measurement at dd8e572ad: **trusted 70 / 411,
# converted 19 / 904**. Route #401's repair re-framed 61 trusted + 7 converted to the honest
# frame; the residue is the ledger below, each entry NAMED with why the honest frame cannot be
# written today.
PARAM_TRUSTED_RATCHET = 9       # 70 -> 9 at route #401. May only SHRINK.
PARAM_CONVERTED_RATCHET = 13    # 19 -> 13 at route #401. May only SHRINK.
# THE SECOND HALF, AND IT IS THE ONE A PROVER SEES. Naming the parameter in `#@ assigns` is
# what a HUMAN and the source-level checks (route #278's override refinement, route #280's
# receiver-writer fixpoint) read; what a CALLER's proof reads is the emitted `writes`. Measured
# by emit-and-grep: `#@ assigns p` lowers to `writes { p }` ONLY when `p` is emitted as an
# `array` (a list parameter). An AST-node / record / object parameter is an `int` HANDLE whose
# field reads are `val function pycsl_getattr_* (o: 'a)` — PURE in the handle — and a set /
# dict parameter is a by-value `map`, so for those the clause is SOURCE-HONEST AND MODEL-INERT:
# the val carries no `writes`, and a caller can still prove a field of the argument unchanged
# across the call. This counts (stub, parameter) pairs whose declared parameter frame does not
# reach the emitted `writes`. It is the MISSING CAPABILITY, measured: a by-reference lowering
# for object handles (a heap the field-read functions depend on) and for set/dict parameters.
# It ROSE when route #401 wrote the honest frames — a NEW ratchet, landed at the value the
# honest declarations produce, and from here it may only SHRINK.
PARAM_NOT_LOWERED_RATCHET = 86   # measured at landing (trusted 69, converted 17)
MIN_PARAM_POPULATION = 1200     # trusted + converted mirror methods examined (measured 1315)
# The SENTINEL: the carrier itself. If the closure ever stops seeing this write, the arm is
# blind and its green is meaningless — the #44 rule, made specific.
PARAM_SENTINEL = ("frontend/pure_ast.py", "NodeTransformer", "generic_visit", "node")
# Each residual offender NAMED with the reason its honest frame cannot be written. An entry
# that no longer matches an offender FAILS the arm (a ledger that outlives its site hides the
# next one); an offender with no entry FAILS it.
_R62 = ("set parameter lowered BY VALUE (`map int (option int)`): `writes` cannot name it; "
        "declaring it trips PYCSL-METHOD-ARG-UNFRAMED (route #316) in statements.py and the "
        "route #62 collection-parameter refusal in stmt_control_flow.py / "
        "Module6_WhyMLTranspiler.py. Needs a by-reference set/dict lowering.")
KNOWN_PARAM_FRAME_DEFICITS = {
    ("frontend/pure_ast.py", "NodeVisitor.visit", "node"): (
        "dispatches (`getattr(self, 'visit_' + ...)(node)`, default `self.generic_visit`) "
        "into NodeTransformer.generic_visit's in-place rewrite. Declaring `assigns node` "
        "makes `visit` a receiver-writer for route #280's fixpoint, which then REFUSES "
        "the converted `_Unparser.traverse` (`super().visit(node)`, a computed receiver) "
        "and the whole pure_ast mirror stops emitting. The refusal is RIGHT: under an "
        "`_Unparser` receiver this dispatch also writes `self._source`, which `traverse`'s "
        "`assigns \\nothing` omits (a SELF-arm blind spot: the dispatch goes through a "
        "local name, not `self.<m>()`). Reopened by converting/re-framing `traverse`."),
}
for _m in ("_handle_assign_stmt", "_handle_ghost_assign_stmt", "_handle_tuple_unpack_stmt",
           "_handle_array_set_stmt", "_handle_augassign_stmt", "_handle_expr_stmt",
           "_stmts_to_whyml"):
    for _q in ("local_refs", "declared_refs"):
        KNOWN_PARAM_FRAME_DEFICITS[("module6_whyml/statements.py",
                                    "StatementEmissionMixin." + _m, _q)] = _R62
for _q in ("local_refs", "declared_refs"):
    KNOWN_PARAM_FRAME_DEFICITS[("module6_whyml/stmt_control_flow.py",
                                "ControlFlowStmtMixin._handle_for_stmt", _q)] = _R62
# The CONVERTED residue: the same by-value set parameters, in methods whose mirror body is
# verbatim. The emitter excludes them from route #316's refusal on purpose
# (`_func_mutated_collection_params` / `_func_stmt_seq_mut_params`), which is the
# by-value model saying "the callee's mutation is a no-op here" — the deficit, not a fix.
KNOWN_CONVERTED_PARAM_FRAME_DEFICITS = {}
for _f, _c, _m in (
        ("module6_whyml/statements.py", "StatementEmissionMixin", "_handle_seq_assign"),
        ("module6_whyml/statements.py", "StatementEmissionMixin", "_emit_new_ghost_ref"),
        ("module6_whyml/statements.py", "StatementEmissionMixin", "_handle_ghost_array_set_stmt"),
        ("module6_whyml/statements.py", "StatementEmissionMixin", "_handle_array_slice_set_stmt"),
        ("module6_whyml/statements.py", "StatementEmissionMixin", "_handle_critical_section_stmt"),
        ("module6_whyml/statements.py", "StatementEmissionMixin", "_handle_fieldassign_stmt"),
        ("module6_whyml/statements.py", "StatementEmissionMixin", "_handle_fieldaugassign_stmt"),
        ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin", "_handle_while_stmt"),
        ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin", "_handle_try_stmt"),
        ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin", "_try_union_is_none_match"),
        ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin", "_handle_if_stmt"),
        ("module6_whyml/stmt_control_flow.py", "ControlFlowStmtMixin", "_handle_match_stmt")):
    for _q in ("local_refs", "declared_refs"):
        KNOWN_CONVERTED_PARAM_FRAME_DEFICITS[(_f, _c + "." + _m, _q)] = _R62
KNOWN_CONVERTED_PARAM_FRAME_DEFICITS[("module6_whyml/expressions.py",
                                      "ExpressionEmissionMixin._handle_named_expr_expr",
                                      "local_refs")] = _R62

LIVE_ROOT = "src/pycsl"
MIRROR_ROOT = "src/self-annotate/src"


def _string_dict_tables(node):
    """Class- or module-level `NAME = {K: "method_name", ...}` handler tables.

    Returns {table_name: [method_name, ...]}.  A DISPATCHER resolves its callee through
    such a table plus `getattr(self, handler_name)`, which no attribute-based call-graph
    walk can see -- so without this the analysis silently misses exactly the methods that
    matter most.  Values may be plain string constants or `X.attr` spellings."""
    out = {}
    for member in node.body:
        if not isinstance(member, (ast.Assign, ast.AnnAssign)):
            continue
        val = member.value
        if not isinstance(val, ast.Dict):
            continue
        names = []
        for v in val.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                names.append(v.value)
            elif isinstance(v, ast.Attribute):
                names.append(v.attr)
        if not names:
            continue
        tgts = member.targets if isinstance(member, ast.Assign) else [member.target]
        for tgt in tgts:
            if isinstance(tgt, ast.Name):
                out[tgt.id] = names
    return out


def _parse_tree(root):
    """(classes, bases, funcs, tables) over every .py under `root`."""
    classes, funcs = {}, {}
    tables = {}
    bases = collections.defaultdict(set)
    for dirpath, _dirs, files in os.walk(root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            try:
                tree = ast.parse(open(path).read())
            except (OSError, SyntaxError):
                continue
            tables.update(_string_dict_tables(tree))
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    funcs[(path, "", node.name)] = node
                elif isinstance(node, ast.ClassDef):
                    tables.update(_string_dict_tables(node))
                    classes[node.name] = path
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases[node.name].add(base.id)
                        elif isinstance(base, ast.Attribute):
                            bases[node.name].add(base.attr)
                    for member in node.body:
                        if isinstance(member, ast.FunctionDef):
                            funcs[(path, node.name, member.name)] = member
    return classes, bases, funcs, tables


def _transitive_bases(cls, bases, seen=None):
    seen = set() if seen is None else seen
    out = set()
    for base in bases.get(cls, ()):
        if base in seen:
            continue
        seen.add(base)
        out.add(base)
        out |= _transitive_bases(base, bases, seen)
    return out


def _self_write_fixpoint(classes, bases, funcs, tables=None):
    tbases = {c: _transitive_bases(c, bases) for c in classes}
    descendants = collections.defaultdict(set)
    for cls in classes:
        for base in tbases[cls]:
            descendants[base].add(cls)
    resolvable = {}
    for cls in classes:
        scope = {cls} | tbases[cls]
        for sub in descendants[cls]:          # cls is a MIXIN of `sub`
            scope |= {sub} | tbases[sub]
        resolvable[cls] = scope

    by_name = collections.defaultdict(list)
    for key in funcs:
        by_name[key[2]].append(key)

    direct, calls = {}, {}
    for key, fn in funcs.items():
        direct[key] = {
            n.attr for n in ast.walk(fn)
            if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
            and isinstance(n.value, ast.Name) and n.value.id == "self"
        }
        # SHARPER ANALYSIS (relaunch #31) -- IN-PLACE MUTATION OF A SELF COLLECTION.
        # The store-context walk above sees `self.x = ...` and NOTHING ELSE. It does not
        # see `self.xs.append(v)`, `self.d[k] = v`, `self.s.add(v)`, `del self.d[k]` — and
        # those are how the emitter mutates most of its state. MEASURED: 18 methods
        # declaring `#@ assigns \nothing` mutate a self collection this way, and ONE of
        # them is CONVERTED — `_Unparser.write`, the 97-call-site output hub, whose entire
        # body is `self._source.extend(text)` and which was emitted as
        #     let _unparser__write (self: _unparser) (text: seq int) : unit
        #       writes {  }
        #     = let _ = (self__source_extend_1 text) in ()
        # i.e. a receiver-less opaque op with no effect, under a frame that says the method
        # changes nothing. `_Unparser` is `@mutable_state`, so a caller can read a field
        # through `getattr__unparser` and rely on `writes { }` across the call.
        # A subscript STORE (`self.d[k] = v`) is an `ast.Subscript` target, not an
        # `ast.Attribute` one, which is why it slipped through the same walk.
        for n in ast.walk(fn):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in _MUTATING_METHODS):
                b = n.func.value
                if (isinstance(b, ast.Attribute) and isinstance(b.value, ast.Name)
                        and b.value.id == "self"):
                    direct[key].add(b.attr)
            if isinstance(n, (ast.Assign, ast.AugAssign, ast.Delete)):
                tgts = (n.targets if isinstance(n, (ast.Assign, ast.Delete))
                        else [n.target])
                for t in tgts:
                    while isinstance(t, ast.Subscript):
                        t = t.value
                    if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                            and t.value.id == "self"
                            and not isinstance(getattr(t, "ctx", None), ast.Store)):
                        direct[key].add(t.attr)
        edges = set()
        for n in ast.walk(fn):
            if not isinstance(n, ast.Call):
                continue
            target = n.func
            if (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                    and target.value.id == "self"):
                edges.add(("self", target.attr))
            elif isinstance(target, ast.Name):
                edges.add(("mod", target.id))
        # TABLE-AWARE DISPATCH.  `handler = self._TABLE.get(type(x))` followed by
        # `getattr(self, handler)(...)` is invisible to the attribute walk above, and it is
        # exactly how the emitter's DISPATCHERS call their handlers -- the methods whose
        # frames matter most.  An edge is added to every method a table names ONLY when the
        # body ALSO performs a `getattr(self, ...)` call, which is the dispatch idiom; a
        # body that merely TESTS membership in a table gets no edges.
        _dyn_self = any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "getattr" and n.args
            and isinstance(n.args[0], ast.Name) and n.args[0].id == "self"
            for n in ast.walk(fn))
        if _dyn_self:
            for n in ast.walk(fn):
                tname = None
                if isinstance(n, ast.Attribute) and n.attr in (tables or {}):
                    tname = n.attr
                elif isinstance(n, ast.Name) and n.id in (tables or {}):
                    tname = n.id
                if tname:
                    for m in tables[tname]:
                        edges.add(("self", m))
        calls[key] = edges

    def targets(key, kind, name):
        path, cls, _ = key
        out = []
        for cand in by_name.get(name, ()):
            cpath, ccls, _ = cand
            if kind == "self":
                if ccls and cls and ccls in resolvable.get(cls, {cls}):
                    out.append(cand)
            elif ccls == "" and cpath == path:
                out.append(cand)
        return out

    trans = {k: set(v) for k, v in direct.items()}
    for _ in range(50):
        changed = False
        for key in funcs:
            acc = set(trans[key])
            for kind, name in calls[key]:
                for tgt in targets(key, kind, name):
                    acc |= trans[tgt]
            if acc != trans[key]:
                trans[key] = acc
                changed = True
        if not changed:
            break
    return direct, trans


def _emitted_record_fields(emit_dir, mirror_root):
    """PER MIRROR FILE and PER CLASS, the fields the EMITTED record actually declares.

    This is the DIRECT oracle for model-visibility, and it strictly refines the
    source-assignment heuristic below.  Module 5 does not promote every `self.<f> = ...`
    it sees into the emitted record -- it drops the ones it cannot type -- so a file can
    assign a field that its `.mlw` record does not carry, and a missing `writes` for such a
    field cannot mislead any prover.  MEASURED: `ControlFlowStmtMixin._handle_return_stmt`
    was reported MODEL-VISIBLE for `_comp_content_counter` / `_current_params` /
    `_current_self_type` / `_frame_trigger_active`, and the emitted
    `type controlflowstmtmixin = { ... }` carries NONE of the four.  Declaring the honest
    frame on it emits `writes {  }` unchanged, because the emitter filters the clause
    through the same record labels.

    `emit_dir` holds one `.mlw` per mirror, named by the mirror's repo-relative path with
    `/` replaced by `_` (what `scratchpad/w2/keepsweep.sh` produces).  Returns
    {mirror_path: {whyml_record_name: {field, ...}}}; a file with no entry falls back to
    the heuristic."""
    out = {}
    rec_re = re.compile(r"^  type ([a-z0-9_]+) = \{(.*?)\}", re.M)
    fld_re = re.compile(r"mutable ([A-Za-z_0-9]+):")
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            # Two naming schemes are in use for an emitted-mirror directory:
            # `scratchpad/w2/keepsweep.sh` keys by the REPO-relative path, while
            # `bin/check-shadowed-selfcalls.py --emit-dir` keys by the MIRROR-relative one.
            # Accept both, so either tool's output can be fed here.
            mlw = None
            for key in (path.replace(os.sep, "_") + ".mlw",
                        os.path.relpath(path, mirror_root)[:-3].replace(os.sep, "_") + ".mlw"):
                cand = os.path.join(emit_dir, key)
                if os.path.exists(cand):
                    mlw = cand
                    break
            if mlw is None:
                continue
            txt = open(mlw).read()
            out[path] = ({m.group(1): set(fld_re.findall(m.group(2)))
                          for m in rec_re.finditer(txt)},
                         set(re.findall(r"^  (?:val|let rec|let|with)\s+([A-Za-z_0-9]+)",
                                        txt, re.M)))
    return out


def _mirror_modelled_fields(mirror_root):
    """PER MIRROR FILE, the `self.<f>` names that file itself assigns.

    Module 5 registers a record field from an assignment IN THE FILE BEING EMITTED, and
    each mirror file is transpiled on its own, so the question "can a converted caller read
    this field?" is a PER-FILE question.  Two coarser tests were tried and both
    over-counted: the raw offender list rewards a purely cosmetic annotation fix on an
    opaque-self class, and a repo-wide field set still counts a class the file emits as
    `type <cls> = int` (measured: `GhostSpecOpsMixin` is decorated `@mutable_state` and its
    own `.mlw` still declares `type ghostspecopsmixin = int`, so a `writes { self._f }` on
    its val is an UNBOUND SYMBOL, not a frame).  A field the emitting file never assigns is
    not part of that file's record, so a missing `writes` for it cannot mislead the prover.
    """
    out = collections.defaultdict(set)
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            try:
                tree = ast.parse(open(path).read())
            except (OSError, SyntaxError):
                continue
            for n in ast.walk(tree):
                if (isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
                        and isinstance(n.value, ast.Name) and n.value.id == "self"):
                    out[path].add(n.attr)
    return out


def _mutable_state_classes(mirror_root):
    """Mirror classes decorated `@mutable_state` — the ones whose `self` becomes a Why3
    record with real, caller-readable fields."""
    out = set()
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            try:
                tree = ast.parse(open(os.path.join(dirpath, fname)).read())
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for dec in node.decorator_list:
                    name = (dec.id if isinstance(dec, ast.Name)
                            else dec.attr if isinstance(dec, ast.Attribute) else None)
                    if name == "mutable_state":
                        out.add(node.name)
    return out


def _mirror_nothing_stubs(mirror_root, want_trusted=True):
    """Every mirror method that declares `#@ assigns \\nothing`.

    `want_trusted=True`  -> the `\\trusted` stubs (the ASSUMED-contract population).
    `want_trusted=False` -> the CONVERTED methods (the second population, see the
    CONVERTED SURFACE note in the module docstring)."""
    out = []
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            src = open(path).read()
            lines = src.splitlines()
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue

            def walk(node, cls):
                for child in node.body:
                    if isinstance(child, ast.ClassDef):
                        walk(child, child.name)
                    elif isinstance(child, ast.FunctionDef):
                        first = (min(d.lineno for d in child.decorator_list)
                                 if child.decorator_list else child.lineno) - 1
                        i = first - 1
                        trusted = nothing = False
                        while i >= 0 and (lines[i].strip().startswith("#")
                                          or lines[i].strip() == ""):
                            stripped = lines[i].lstrip()
                            # LINE PREFIX, never substring: a prose mention of the marker
                            # inside a comment block must not count.
                            if stripped.startswith("#@") and "\\trusted" in stripped:
                                trusted = True
                            if stripped == "#@ assigns \\nothing":
                                nothing = True
                            i -= 1
                        if (trusted == want_trusted) and nothing:
                            out.append((path, cls, child.name))
            walk(tree, "")
    return out


def _mirror_param_frames(mirror_root, want_trusted):
    """(#49, route #401) Every mirror method (`\\trusted` or converted) with the ROOT names
    of its declared `#@ assigns` targets (`\\nothing` and an absent clause give the empty
    set). Same walk as `_mirror_nothing_stubs`: module and class bodies, not nested defs."""
    out = []
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            src = open(path).read()
            lines = src.splitlines()
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue

            def walk(node, cls):
                for child in node.body:
                    if isinstance(child, ast.ClassDef):
                        walk(child, child.name)
                    elif isinstance(child, ast.FunctionDef):
                        first = (min(d.lineno for d in child.decorator_list)
                                 if child.decorator_list else child.lineno) - 1
                        i = first - 1
                        trusted = False
                        roots = set()
                        while i >= 0 and (lines[i].strip().startswith("#")
                                          or lines[i].strip() == ""):
                            stripped = lines[i].lstrip()
                            if stripped.startswith("#@") and "\\trusted" in stripped:
                                trusted = True
                            if stripped.startswith("#@ assigns"):
                                for tgt in re.split(r",(?![^\[]*\])",
                                                    stripped[len("#@ assigns"):]):
                                    m = re.match(r"\s*([A-Za-z_]\w*)", tgt)
                                    if m:
                                        roots.add(m.group(1))
                            i -= 1
                        if trusted == want_trusted:
                            out.append((path, cls, child.name, roots))
            walk(tree, "")
    return out


def _emitted_writes(emit_dir, mirror_root):
    """(#49, route #401) {mirror_path: {whyml_symbol: set(names in its `writes`)}} for
    every `val` / `let` the emission declares."""
    out = {}
    head = re.compile(r"^  (?:val|let rec|let|with)\s+([A-Za-z_0-9]+)")
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            mlw = None
            for key in (path.replace(os.sep, "_") + ".mlw",
                        os.path.relpath(path, mirror_root)[:-3].replace(os.sep, "_") + ".mlw",
                        os.path.relpath(path, mirror_root)[:-3].replace(os.sep, "__")
                        + ".mlw"):
                cand = os.path.join(emit_dir, key)
                if os.path.exists(cand):
                    mlw = cand
                    break
            if mlw is None:
                continue
            syms, cur = {}, None
            for ln in open(mlw).read().splitlines():
                m = head.match(ln)
                if m:
                    cur = m.group(1)
                    syms.setdefault(cur, set())
                    continue
                if cur is None:
                    continue
                if not ln.strip() or ln.lstrip().startswith("="):
                    cur = None
                    continue
                w = re.match(r"\s*writes\s*\{(.*)\}", ln)
                if w:
                    syms[cur] |= {x.strip() for x in w.group(1).split(",") if x.strip()}
            out[path] = syms
    return out


def _emit_all(out_dir):
    """Emit every mirror's `.mlw` into `out_dir` (needs `why3` on PATH)."""
    import glob
    import subprocess
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py = os.path.join(root, ".venv", "bin", "python3")
    if not os.path.exists(py):
        py = sys.executable
    env = dict(os.environ, PYTHONHASHSEED="0")
    for src in sorted(glob.glob(os.path.join(root, MIRROR_ROOT, "**", "*.py"),
                                recursive=True)):
        mlw = src[:-3] + ".mlw"
        if os.path.exists(mlw):
            os.remove(mlw)
        subprocess.run([py, os.path.join(root, "src", "pycsl", "pycsl.py"), src,
                        "--import-path", os.path.join(root, "src", "pycsl"),
                        "--no-proof", "--keep-mlw"],
                       cwd=root, env=env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(mlw):
            rel = os.path.relpath(src, os.path.join(root, MIRROR_ROOT))
            shutil.move(mlw, os.path.join(out_dir, rel[:-3].replace(os.sep, "_") + ".mlw"))


def main():
    _refuse_if_battery_running("trusted-frame-honesty")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true",
                    help="list every offending stub with its transitive write set")
    ap.add_argument("--ratchet", type=int, default=RATCHET)
    ap.add_argument("--total-ratchet", type=int, default=TOTAL_RATCHET)
    ap.add_argument("--no-emit", action="store_true",
                    help="skip emission and fall back to the OVER/UNDER-approximating "
                         "source-assignment heuristic (the ratchets do NOT apply).")
    ap.add_argument("--emit-dir",
                    help="directory of emitted .mlw (scratchpad/w2/keepsweep.sh output). "
                         "With it, MODEL-VISIBLE is decided by the EMITTED record's fields "
                         "instead of the over-approximating source-assignment heuristic.")
    ap.add_argument("--converted-ratchet", type=int, default=CONVERTED_RATCHET)
    ap.add_argument("--converted-total-ratchet", type=int,
                    default=CONVERTED_TOTAL_RATCHET)
    ap.add_argument("--param-trusted-ratchet", type=int, default=PARAM_TRUSTED_RATCHET)
    ap.add_argument("--param-converted-ratchet", type=int, default=PARAM_CONVERTED_RATCHET)
    ap.add_argument("--param-not-lowered-ratchet", type=int,
                    default=PARAM_NOT_LOWERED_RATCHET)
    args = ap.parse_args()

    classes, bases, funcs, tables = _parse_tree(LIVE_ROOT)
    direct, trans = _self_write_fixpoint(classes, bases, funcs, tables)
    import lib_declarations as _ld
    _lclasses = _ld.live_graph(LIVE_ROOT)
    _lmros = {c: _ld.c3_mro(c, _lclasses) for c in _lclasses}

    ms_classes = _mutable_state_classes(MIRROR_ROOT)
    modelled = _mirror_modelled_fields(MIRROR_ROOT)
    _tmp = None
    _edir = args.emit_dir
    if _edir is None and not args.no_emit:
        _tmp = tempfile.mkdtemp(prefix="frame-honesty-")
        _emit_all(_tmp)
        _edir = _tmp
    emitted = _emitted_record_fields(_edir, MIRROR_ROOT) if _edir else {}
    emitted_writes = _emitted_writes(_edir, MIRROR_ROOT) if _edir else None
    if _tmp is not None:
        shutil.rmtree(_tmp, ignore_errors=True)

    def _sym_of(cls, name):
        """The WhyML symbol Module 6 emits for `<cls>.<name>` (lowercased class, `__`)."""
        return ((cls.lower() + "__" + name) if cls else name)

    def _visible(cls, path, writes, sym=None):
        """Is a missing `writes` for any of `writes` something a prover can be misled by?

        With `--emit-dir` this is the DIRECT question: does the file's emitted record for
        `cls` declare the field?  Without it, fall back to the source-assignment heuristic,
        which OVER-APPROXIMATES (see `_emitted_record_fields`)."""
        # (#34) THIS `@mutable_state` HARD GATE IS THE PLANE'S OWN BLIND SPOT, and it is
        # RECORDED, NOT YET CHANGED. A class can emit a `type c = { mutable a: int; ... }`
        # record WITHOUT the decorator, and that population is exactly where the frame
        # CLAIM/CHECK asymmetry bites: `functions.py` puts the declared frame on the
        # concrete `let` (the CHECK) only for `@mutable_state` classes, while the
        # arity-suffixed AVATAR every call site goes through carries `writes { self.f }`
        # for ANY class with a record (the CLAIM). Measured with this line relaxed to
        # `if ent is None and cls not in ms_classes` (the copy is
        # `scratchpad/w7/tfh_wide.py`): converted MODEL-VISIBLE goes 0 -> 1, and the one is
        # `ConcurrencyChecker._walk_body` -- the SAME method an independent experiment
        # (putting the declared frame on the `let`) flagged with Why3's "this expression
        # produces an unlisted write effect". It has been repaired, so the widened
        # predicate is ALSO 0. (#34, second half) THE WIDENING HAS NOW LANDED, together
        # with the frame-preservation fix it is the instrument for: whenever an EMISSION
        # is available the emitted record answers the question, and `@mutable_state` is
        # only the FALLBACK for the source-heuristic path.
        if emitted.get(path) is None and cls not in ms_classes:
            return False
        ent = emitted.get(path)
        if ent is not None:
            recs, syms = ent
            # A method the emitted `.mlw` DOES NOT DECLARE AT ALL carries no frame, so its
            # `#@ assigns` cannot mislead any prover. MEASURED: not one of the four
            # `__init__` offenders this plane used to report as MODEL-VISIBLE is emitted as
            # a WhyML symbol -- Python construction is lowered to a record literal, not to a
            # method call -- and correcting all four left the emission of all 52 mirrors
            # BYTE-IDENTICAL. Without this test the plane's headline number was dominated by
            # claims the model never made.
            if sym and sym not in syms:
                return False
            flds = recs.get(cls.lower())
            if flds is None:
                return False
            return any(w in flds for w in writes)
        return any(w in modelled.get(path, ()) for w in writes)

    def _population(want_trusted):
        stubs = _mirror_nothing_stubs(MIRROR_ROOT, want_trusted)
        offenders = []
        for path, cls, name in stubs:
            live_key = (LIVE_ROOT + path[len(MIRROR_ROOT):], cls, name)
            if live_key not in funcs and cls:
                # (R0) a DECLARATION: resolve it to its definition through the live MRO.
                _defs = _ld.resolve(cls, name, _lclasses, _lmros)
                if len(_defs) == 1:
                    live_key = (os.path.relpath(_defs[0][1]), _defs[0][0], name)
            writes = trans.get(live_key)
            if writes:
                offenders.append((path, cls, name, sorted(writes),
                                  bool(direct.get(live_key)), path))
        visible = [o for o in offenders
                   if _visible(o[1], o[5], o[3], _sym_of(o[1], o[2]))]
        return stubs, offenders, visible

    def _report(tag, stubs, offenders, visible):
        n_direct = sum(1 for o in offenders if o[4])
        print("[*] %s: %d method(s) declare `#@ assigns \\nothing`; "
              "%d stand for a live body that transitively writes `self` state "
              "(%d write DIRECTLY); %d of those are MODEL-VISIBLE (`@mutable_state` class)."
              % (tag, len(stubs), len(offenders), n_direct, len(visible)))
        if args.verbose:
            for path, cls, name, writes, is_direct, _p in sorted(offenders,
                                                                 key=lambda o: -len(o[3])):
                rel = path[len(MIRROR_ROOT) + 1:]
                print("    %-40s %-44s %3d %-10s %-13s %s"
                      % (rel, (cls + "." + name if cls else name)[:44], len(writes),
                         "DIRECT" if is_direct else "via-callee",
                         "MODEL-VISIBLE" if _visible(cls, path, writes,
                                                     _sym_of(cls, name))
                         else "unmodelled", writes[:4]))

    rc = 0

    def _ratchet(tag, pairs, why):
        nonlocal rc
        for label, got, want in pairs:
            if got > want:
                print("[!] %s: %s RATCHET BROKEN — %d > %d. %s" % (tag, label, got, want, why))
                rc = 1
            elif got < want:
                print("[+] %s: %s %d < ratchet %d — lower the constant."
                      % (tag, label, got, want))

    # (#49) gen #31 — the EXTERNAL-EFFECT half, run before the `self`-state half because it
    # is the cheaper question and it has a shorter answer.
    _ext_bad, _ext_known = [], []
    for _path, _cls, _name in _mirror_nothing_stubs(MIRROR_ROOT, want_trusted=True):
        _rel = _path[len(MIRROR_ROOT) + 1:]
        _live = os.path.join(LIVE_ROOT, _rel)
        if not os.path.isfile(_live):
            continue
        try:
            _lt = ast.parse(open(_live, errors="replace").read())
        except SyntaxError:
            continue
        for _fn in ast.walk(_lt):
            if not isinstance(_fn, ast.FunctionDef) or _fn.name != _name:
                continue
            for _c in ast.walk(_fn):
                if (isinstance(_c, ast.Call) and isinstance(_c.func, ast.Attribute)
                        and isinstance(_c.func.value, ast.Name)
                        and (_c.func.value.id, _c.func.attr) in EXTERNAL_EFFECT_CALLS):
                    _what = "%s.%s()" % (_c.func.value.id, _c.func.attr)
                    if (_rel, _name) in KNOWN_EXTERNAL_EFFECT_NOTHING:
                        _ext_known.append((_rel, _name, _what))
                    else:
                        _ext_bad.append((_rel, _name, _what))
                    break
            break
    print("[*] trusted-frame-honesty: EXTERNAL EFFECTS — %d `\\trusted` stub(s) declare "
          "`#@ assigns \\nothing` while their LIVE body calls `subprocess.*`/`os.*`/"
          "`shutil.*`; %d named in KNOWN_EXTERNAL_EFFECT_NOTHING. The clause is glossed "
          "\"pure, side-effect-free\" in annotations.md §926."
          % (len(_ext_bad) + len(_ext_known), len(_ext_known)))
    if args.verbose:
        for _e in sorted(_ext_known):
            print("    known-external  %-30s %-32s %s" % _e)
    for _e in sorted(_ext_bad):
        print("[!] trusted-frame-honesty: UNNAMED SIDE-EFFECTING `assigns \\nothing` STUB: "
              "%s::%s calls %s. While the marker is there the clause is ASSUMED and flagged; "
              "CONVERTING this stub would CERTIFY it over a real side effect. Name it in "
              "KNOWN_EXTERNAL_EFFECT_NOTHING with what it does, or correct the clause."
              % _e)
        rc = 1

    t_stubs, t_off, t_vis = _population(True)
    _report("trusted-frame-honesty", t_stubs, t_off, t_vis)
    # (#49) gen #31 — ZERO-INPUT GUARD. Every ratchet in this plane is an UPPER bound, and
    # an empty population satisfies an upper bound perfectly: if the mirror walk breaks or
    # `MIRROR_ROOT` moves, `_population` returns no stubs, no offenders, no visible ones,
    # and the plane prints "[+] frame-honesty: OK — measured trusted 0 / 0, converted 0 / 0"
    # over a measurement nobody made. The floor bounds the POPULATION — the `#@ assigns
    # \nothing` DECLARERS, which is what the plane reads — not the offenders. The #44 rule,
    # already carried by `byte-diff-sweep.sh` (900 sources), `run-soundness-planes.sh`
    # (MIN_PLANES) and `check-directive-enforcement.py` (its derived-population refusal).
    _ratchet("trusted-frame-honesty",
             (("model-visible", len(t_vis), args.ratchet),
              ("total", len(t_off), args.total_ratchet)),
             "A `\\trusted` stub's `assigns` is ASSUMED, never checked, so a false one is "
             "an unsoundness no proof plane can see.")

    c_stubs, c_off, c_vis = _population(False)
    _report("converted-frame-honesty", c_stubs, c_off, c_vis)
    if len(t_stubs) + len(c_stubs) < MIN_NOTHING_DECLARERS:
        print("[!] frame-honesty: REFUSING — only %d method(s) declare `#@ assigns "
              "\\nothing` across both populations, expected at least %d. The mirror walk is "
              "broken, so \"0 model-visible\" means nothing. THIS IS A REFUSAL, NOT A PASS."
              % (len(t_stubs) + len(c_stubs), MIN_NOTHING_DECLARERS), file=sys.stderr)
        return 2
    _ratchet("converted-frame-honesty",
             (("model-visible", len(c_vis), args.converted_ratchet),
              ("total", len(c_off), args.converted_total_ratchet)),
             "A CONVERTED method's `writes {  }` is checked against the EMITTED body, "
             "which is an ERASURE of the live one — and every OTHER file's caller-side "
             "abstract `val` is minted from the same declared `assigns`, so it inherits "
             "the false frame UNCHECKED.")

    # (driver run #3, R0) THE DECLARATION ARM (see the module docstring).
    _decls = _ld.declarations(".", _lclasses)
    _own, _inh, _unres = [], [], []
    for _d in _decls:
        if len(_d["defs"]) != 1:
            _unres.append(_d)
            continue
        _dcls, _dpath = _d["defs"][0]
        _live = trans.get((os.path.relpath(_dpath), _dcls, _d["name"]))
        _decl = {t[5:] for t in _ld.frame(_d["clauses"])[0] if t.startswith("self.")}
        _md = _ld.mirror_def(".", _dpath, _dcls, _d["name"])
        _dfr = ({t[5:] for t in _ld.frame(_md[2])[0] if t.startswith("self.")}
                if _md else None)
        _lw = set(_live or ())
        _o = (_lw & _dfr if _dfr is not None else _lw) - _decl
        _i = (_lw - _dfr - _decl) if _dfr is not None else set()
        _q = "%s::%s.%s%s" % (_d["rel"], _d["cls"], _d["name"],
                              " (requires_method window on %s)" % _d["host"]
                              if _d["kind"] == "window" else "")
        if _o:
            _vis = _visible(_d["cls"], os.path.join(MIRROR_ROOT, _d["rel"]), sorted(_o),
                            _sym_of(_d["cls"], _d["name"]) if _d["kind"] == "stub" else None)
            _own.append((_q, sorted(_o), _vis, "%s.%s" % (_dcls, _d["name"])))
        if _i:
            _inh.append((_q, sorted(_i), "%s.%s" % (_dcls, _d["name"])))
    print("[*] declaration-frame-honesty: %d declaration(s) (%d `\\trusted` stubs, %d "
          "`requires_method` windows) resolved through the live MRO; %d understate their "
          "DEFINITION's live writes that the definition itself declares (OWN, %d "
          "model-visible); %d inherit a definition frame that understates its live closure "
          "(INHERITED); %d unresolved."
          % (len(_decls), sum(1 for d in _decls if d["kind"] == "stub"),
             sum(1 for d in _decls if d["kind"] == "window"), len(_own),
             sum(1 for o in _own if o[2]), len(_inh), len(_unres)))
    for _q, _o, _vis, _def in _own:
        print("    OWN %-13s %-70s def %-44s missing %d: %s"
              % ("MODEL-VISIBLE" if _vis else "unmodelled", _q, _def, len(_o), _o[:6]))
    if args.verbose:
        for _q, _i, _def in _inh:
            print("    INHERITED %-70s def %-44s missing %s" % (_q, _def, _i))
    for _d in _unres:
        print("[!] declaration-frame-honesty: UNRESOLVED declaration %s::%s.%s -> %s (dead or "
              "ambiguous: no single live definition to check it against)."
              % (_d["rel"], _d["cls"], _d["name"], _d["defs"]))
        rc = 1
    if len(_decls) < MIN_DECLARATIONS:
        print("[!] declaration-frame-honesty: REFUSING — only %d declaration(s) found, "
              "expected at least %d. THIS IS A REFUSAL, NOT A PASS."
              % (len(_decls), MIN_DECLARATIONS), file=sys.stderr)
        return 2
    _ratchet("declaration-frame-honesty",
             (("own-model-visible", sum(1 for o in _own if o[2]), DECL_OWN_VISIBLE_RATCHET),
              ("own", len(_own), DECL_OWN_RATCHET),
              ("inherited", len(_inh), DECL_INHERITED_RATCHET)),
             "A declaration's frame is what every caller in its file ASSUMES; one narrower "
             "than its definition's lets a verified caller prove a false frame (route #488).")

    # (#49) ROUTE #401 — THE PARAMETER-WRITE ARM (see the constants' note).
    import lib_param_write_closure as _lpw
    _pfuncs, _pinfo, _pclosure = _lpw.analyse(LIVE_ROOT)
    _sent_live = (os.path.join(LIVE_ROOT, PARAM_SENTINEL[0]), PARAM_SENTINEL[1],
                  PARAM_SENTINEL[2])
    if PARAM_SENTINEL[3] not in (_pclosure.get(_sent_live) or {}):
        print("[!] param-frame-honesty: REFUSING — the closure no longer sees the route #401 "
              "carrier (%s::%s.%s writes `%s`). The analysis is blind, so any count it "
              "reports means nothing. THIS IS A REFUSAL, NOT A PASS." % PARAM_SENTINEL,
              file=sys.stderr)
        return 2

    def _param_ident(q):
        q = q[0].lower() + q[1:] if q and q[0].isupper() else q
        return {q, "py_" + q}

    def _param_arm(want_trusted, ledger):
        nonlocal rc
        tag = "param-frame-honesty(%s)" % ("trusted" if want_trusted else "converted")
        pop = _mirror_param_frames(MIRROR_ROOT, want_trusted)
        offenders, not_lowered, seen_ledger = [], [], set()
        for path, cls, name, roots in pop:
            rel = path[len(MIRROR_ROOT) + 1:]
            live_key = (LIVE_ROOT + path[len(MIRROR_ROOT):], cls, name)
            writes = _pclosure.get(live_key) or {}
            qual = (cls + "." if cls else "") + name
            for q in sorted(writes):
                if q in roots:
                    if emitted_writes is not None:
                        syms = emitted_writes.get(path)
                        sym = _sym_of(cls, name)
                        if syms is not None and sym in syms \
                                and not (_param_ident(q) & syms[sym]):
                            not_lowered.append((rel, qual, q))
                    continue
                key = (rel, qual, q)
                if key in ledger:
                    seen_ledger.add(key)
                offenders.append((rel, qual, q, writes[q][:2], key in ledger))
        n_stubs = len({(o[0], o[1]) for o in offenders})
        print("[*] %s: %d method(s) examined; %d declare a frame omitting a parameter their "
              "LIVE body writes (%d (method, parameter) pairs, %d of them ledgered)."
              % (tag, len(pop), n_stubs, len(offenders), sum(1 for o in offenders if o[4])))
        for o in offenders:
            if args.verbose or not o[4]:
                print("    %s %-34s %-48s %-16s %s" % ("ledgered" if o[4] else "[!] UNNAMED",
                                                       o[0], o[1][:48], o[2], o[3]))
            if not o[4]:
                rc = 1
        for key in sorted(set(ledger) - seen_ledger):
            print("[!] %s: STALE LEDGER ENTRY %s — no longer an offender. Remove it (and lower "
                  "the ratchet) in the same commit." % (tag, "::".join(key)))
            rc = 1
        if args.verbose:
            for nl in not_lowered:
                print("    not-lowered %-34s %-48s %s" % nl)
        return pop, n_stubs, not_lowered

    _pt_pop, _pt_n, _pt_nl = _param_arm(True, KNOWN_PARAM_FRAME_DEFICITS)
    _pc_pop, _pc_n, _pc_nl = _param_arm(False, KNOWN_CONVERTED_PARAM_FRAME_DEFICITS)
    if len(_pt_pop) + len(_pc_pop) < MIN_PARAM_POPULATION:
        print("[!] param-frame-honesty: REFUSING — only %d mirror method(s) examined, expected "
              "at least %d. THIS IS A REFUSAL, NOT A PASS."
              % (len(_pt_pop) + len(_pc_pop), MIN_PARAM_POPULATION), file=sys.stderr)
        return 2
    _ratchet("param-frame-honesty",
             (("trusted", _pt_n, args.param_trusted_ratchet),
              ("converted", _pc_n, args.param_converted_ratchet)),
             "A frame that omits a parameter the live body writes lets every caller assume "
             "the argument UNCHANGED across the call (route #401).")
    if emitted_writes is not None:
        _nl = len(_pt_nl) + len(_pc_nl)
        print("[*] param-frame-honesty: %d (method, parameter) frame(s) name a written "
              "parameter that the emitted `writes` does NOT carry (object handle / by-value "
              "set or dict: source-honest, model-inert; trusted %d, converted %d)."
              % (_nl, len(_pt_nl), len(_pc_nl)))
        _ratchet("param-frame-honesty",
                 (("not-lowered", _nl, args.param_not_lowered_ratchet),),
                 "A declared parameter frame that does not reach the emitted `writes` is a "
                 "claim the model drops: the caller may still prove the argument unchanged.")

    if rc == 0:
        print("[+] frame-honesty: OK — measured trusted %d model-visible / %d total, "
              "converted %d model-visible / %d total (ratchets %d/%d and %d/%d)."
              % (len(t_vis), len(t_off), len(c_vis), len(c_off),
                 args.ratchet, args.total_ratchet,
                 args.converted_ratchet, args.converted_total_ratchet))
    return rc


if __name__ == "__main__":
    sys.exit(main())
