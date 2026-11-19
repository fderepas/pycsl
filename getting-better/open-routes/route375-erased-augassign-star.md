# OPEN ROUTE #375 — AUGMENTED ASSIGNMENT / STAR-UNPACK OF AN ERASED VALUE IS UNCHECKED
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r373 executor off dc378283c — failing assertions, see REPAIR). Was OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r375/`: `p12_star_list.py`, `p21_augadd_self.py`, `p45_alias_add_param.py`, `p47_star_set_erased.py`, `p49_alias_mul_noexc.py`.

R337 refuses `self += 1` directly but not through an alias (`t = self; t += 1` / `*= 2`, p21/p49) or on a parameter (p45); a starred display element `[*self]` / `{*self}` is emitted as the plain element (p12/p47). Slips past #358/#337/R343. CPython TypeError.

Repair: Propagate erasure through simple aliases into AugAssign (refuse / failing assertion under no_exception); lower starred elements of an erased value through the failing iteration assertion.

## REPAIR (2026-10-25, r373 executor off dc378283c, repaired with routes #373 / #374 / #376; code 34a579bb + 9d029328, corpus e8488149, census 98378213, docs f19c7b7a + c037431b (annotations §7.36, translational §T.6.47))
**Design: route #358's failing assertion, at the two seams that bypassed it** (VC labels, no refusal, no new def; mirror twins
`\trusted`). (a) `_handle_augassign_stmt`: under `no_exception` (program context), when route #251's probe `r251_erased?` calls
the target (`Var t`) or the value erased, the update is preceded by `assert { [@expl:PyCSL-R375 ..] false }` (the `+=` lowered
to the int `+` and never reached `_handle_binop`'s route #252 assertion; R337 refuses only `self op= v`). (b) At the head of
`_expr_to_whyml`: a list / set / tuple display with a `Starred` element whose value the probe calls erased carries the same
assertion in ANY program context (the Starred node lowered as the bare element: `[*self]` was the one-element array, and
`len([*x]) == 1` PROVED for `x: Any` without `no_exception`), and so does a call with such a starred argument under
`no_exception`; route #310's pure-display placeholder in `_handle_assign_stmt` keeps an asserted display evaluated
(`{*self}` was replaced by `(any int)` with its element dropped).
**Probe table** (full proof via heavy.sh; base = dc378283c):
| witness | corpus | base | after |
|---|---|---|---|
| p12 `[*self]`, no_exception | 5066 | rc=0 PROVED | rc=1 FAIL (PyCSL-R375) |
| p21 `t = self; t += 1` | 5067 | rc=0 PROVED | rc=1 FAIL (PyCSL-R375) |
| p45 `t = w; t += 1`, `w: W` field-less | 5068 | rc=0 PROVED | rc=1 FAIL |
| p47 `{*self}` | 5069 | rc=0 PROVED | rc=1 FAIL |
| p49 `t = self; t *= 2` | 5070 | rc=0 PROVED | rc=1 FAIL |
| NEW `(*self,)` | 5071 | rc=0 PROVED | rc=1 FAIL |
| NEW `g(*self)` | 5072 | rc=1 FAIL | rc=1 FAIL (PyCSL-R375 too) |
| NEW (no no_exception) `xs = [*x]`, `x: Any`, `len(xs) == 1` | 5073 | rc=0 PROVED | rc=1 FAIL |
| NEW `t = 0; t += x`, `x: Any` | 5074 | rc=0 PROVED | rc=1 FAIL |
| control: int augmented assignments in a record method, `len([1, 2])`, no_exception | 5092 | rc=0 PROVED | rc=0 PROVED |
**Blast radius** (base worktree at dc378283c vs candidate 9d029328, `bin/byte-diff-sweep.sh` + `bin/byte-diff-compare.py`,
shared by routes #373-#376): root 2341 base / 2357 candidate, **0 MOVED / 0 GONE / 0 APPEARED** (17 of the 37 new sources
emit, the rest refuse; one GONE in the first compare, `1723_route212_verify_imports_control`, is a resource artefact —
`--verify-imports` proves its dependency inside the emission and timed out under load; it failed the same way at BASE when
re-run standalone, and re-emitted individually via heavy.sh it is byte-IDENTICAL to the base emission); pyref 2186/2186
0/0/0; mirror 53/53 0/0/0 (`bin/mirror-emit-sweep.sh`, `--min-files 50`) — **no mirror mover, no OWED whole-file proof**.
MEASURED on the way (first candidate, then narrowed): the mirror GONE'd `errors.py` (a bare `__str__` call spelling matched a
method's short name: the #373 rule is now keyed on the SOURCE's nested-in-a-method def names), `module6_whyml/expressions` and
`statements` (`getattr(self, "_x", d)` on emitter mixins deriving from IMPORTED mixins: the "outside base = unknown" arm of #376
was dropped, a recorded residual), and MOVED `frontend/pure_ast` (`self.set_precedence(p, *node.comparators)`: a starred CALL
argument is asserted under `no_exception` only). Ledger 3, no new def, one new refusal code
(`PYCSL-R376-GETATTR-CLASS-BINDING`, 2 raise sites, both witnessed), no gate loosened.
**Gates** (one run for routes #373-#376 on the final tree; logs in the executor scratchpad `r373/g/`): witnesses / controls
above (full proof via heavy.sh, base dc378283c vs candidate); byte-diff root + pyref and mirror sweep (above, rc=0 after the
1723 re-emission); `check-self-annotate-sync.sh` rc=0 (926 verbatim); `self-annotate-mirror-check.sh` rc=0 (53);
`check-trusted-reasons` rc=0 (420 / 420, unclassified 259); `check-trusted-raises-honesty` rc=0 (19 / 61, ratchet 61 — the
R376 raises sit in `_lower_getattr`, which has no mirror twin; #373 / #375 add no raise); `check-assigns-underdeclaration
--transitive` rc=0; `check-dropped-mutation` rc=0 (0 / 51 / 5 / 0); `check-refusal-witness-coverage` rc=0 (303 demonstrated,
5 not = ceiling 5; rows 5050-5082 via `_census_row`); `doc-coherency --check` rc=0; `check-getattr-erasure` rc=0 (DECLARED 0; rows for 5082 (UNKNOWN 1, refused after the census line) and control 5093 (ABSENT 1) registered by `--emit-baseline`, diff = exactly those two rows);
`check-assumed-facts` rc=0 (85 facts, ledger 3); `run-soundness-planes.sh` fast 61/61 rc=0 (`--slow` not run); `check-stdlib-modules-verify` rc=0 (one command via heavy.sh: 104 modules, 83 VERIFY, the known 21).
**Residuals.** (1) A starred CALL argument of an erased value outside `no_exception` keeps the bare-element lowering (the callee's
vararg sequence holds one element; the mirror forwards erased `*nodes` to variadic emitters — measured MOVED, so it was scoped
out). (2) A starred element of a NON-erased value (`[*xs]`, `xs: List[int]`) is untouched (route #297 refuses its size folds;
the element lowering itself is not this route's). (3) `self.f op= v` on an erased field, and augmented assignment outside
`no_exception`, keep the int lowering (the target stays erased for every later use).
