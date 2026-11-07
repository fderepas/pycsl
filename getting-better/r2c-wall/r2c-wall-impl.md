# r2c-ir-tree-mutation — implementation plan (driver, gen #37, 2026-10-22)

Inputs: `r2c-wall.md` (report, 1ee5a1c3) and `r2c-wall-response.md` (independent fable review, b878ce6c, 8 oracle
runs). Agreed: the 11 markers are C=3 caller-param trees / S=2 self.program_ir / L=4 local trees / X=2 self-state
sets; caller-tree write-back proves but is UNSOUND under sharing (`alias_hole`, and the review's
`derived_local_hole`: `funcs = ir["functions"]; rewrite(ir); funcs[0][...]` still old). Ranking: (c) R2c-local >
(a) ref-root write-back (needs a call-site kill rule (v)) > (d) boundary for `_inline_calls` only > (b) heap.
No route alone completes a chain (0 complete chains); this plan builds the cheapest capability and stops at a
measured verdict.

## Step 1 — (c) R2c-local, SPIKE FIRST (make-or-break, Gate S)
A hand driver `cgd_min(funcs: List[Dict[str, PyVal]])` that builds a LOCAL `generics` dict (from a dict literal)
and does `generics[t]["methods"].append(func)`. PASS iff ALL of:
 (1) emitted WhyML (`--no-proof --keep-mlw`) is L3-tc clean, the append lowered to a functional write-back on the
     LOCAL root (`generics := hval_set_path ...` or equivalent), and the dict literal lowered to a real `HMap`
     (not `any_map ()`);
 (2) witness `len(generics["G"]["methods"]) == 1` proves (z3) and its `== 0` twin does not;
 (3) a store BELOW a stored parameter element (`generics["G"]["methods"][0]["x"] = 1; return funcs[0]`) is REFUSED
     at emit (it would write through a shared object), never proved.
A local root is one bound in the function from a literal / dict() / copy.deepcopy whose value never escapes before
the write (no return, no store into a param/self/global, no pass to a may-write callee) — fail-closed syntactic
check, same family as #279/#283/#295.
REFUTATION EXIT: if (1)-(3) cannot all hold axiom-free -> CERTIFIED-BOUNDARY for R2c-local (record reason + spike
files in r2c-wall/R2c-local-verdict.md); stop.

## Step 2 — BUILD on PASS
Module 6 lowering of nested stores/appends/setdefault-append on a LOCAL hval root (path write-back), the
escape/partner check (refuse otherwise), dict-literal -> HMap where values are hval-typed. No helper extraction /
nested def in src/pycsl (lesson a4); no kernel axiom (only realizable val specs, precedent hpairs_key_eq). Then
re-measure the 4 L markers (`_collect_generic_decls`, `_specialize_decl`, `_specialize_function`,
`sort_functions_by_scc`) and convert any that is honest.

## Recorded, not executed here
(a) ref-root write-back with rule (v) (call-site kill: after a call that may write a root, every name derived from
that root by projection is killed/refreshed); (d) CERTIFIED-BOUNDARY for `_inline_calls` (relies on sharing),
after the frame-honesty audit of trusted `assigns \nothing` appenders; (b) heap model rejected as next step.

## Gate battery
fidelity ∧ trusted-reasons ∧ mirror emit diff (movers L3-tc + whole-file, LOW queue) ∧ corpus+pyref byte-diff (M1)
∧ witnesses incl. false twins and the (3) refusal witness ∧ fast planes ∧ --slow on the landed stack ∧ ledger 3.
