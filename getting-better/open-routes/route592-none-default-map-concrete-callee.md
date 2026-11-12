# OPEN ROUTE #592 — AN OMITTED `None` DEFAULT OF AN `Optional[Dict]` PARAMETER IS FILLED WITH THE OPAQUE MAP `pycsl_none_map`, SO A VERIFIED CALLEE'S CONTRACT (PROVED FOR EVERY MAP) IS APPLIED WHERE CPYTHON PASSES `None`
**Status: REPAIRED (driver run #6, executor u40, branch run6-u40 off run6-int56 fe057a6c1; annotations §7.592). Mechanism (front end, `pycsl.py::_run_pipeline`, twin `\trusted`; inline, no new def, no axiom): every `pycsl_none_map` fill Module 6 makes is observed together with its callee, and REFUSED, new `PYCSL-R592-NONE-DEFAULT-MAP-CONCRETE`, unless every binding of the callee has no verified body (`\abstract`, `\trusted`, or a mirror `#@ declared_in` whose definition is `\trusted` / `\abstract`).** Opened as: Status OPEN, Severity 1, INTRODUCED BY RUN #6 (capability cap-none-default-map-param, lvN, c9ef6badd, landed in L5); red team rt56 probe `hc1762_cl_isinstance_dict.py` (copied to `witnesses-r592/`).

## The defect

lvN changed the fill of an omitted `None` default of a map-typed parameter (`Optional[Dict[K, V]] = None`, WhyML
`map K (option V)`) from the int `0` (ill-typed: the file was refused at L3-tc) to the opaque constant
`val function pycsl_none_map : map 'k (option 'v)`. The constant itself decides nothing, but a VERIFIED callee body
reads the parameter AS A MAP, so its contract is proved for every map, and the caller inherits it at a call where
CPython passes `None`:

    #@ ensures \result == 1
    def g(x: int, d: Optional[Dict[str, str]] = None) -> int:
        return 1 if isinstance(d, dict) else 0      # true of every map
    #@ ensures \result == 1
    def h() -> int: return g(3)                     # PROVED; CPython returns 0

Measured by the driver: on the pre-run-#6 base (pycsl-base6) an L3 type error (not proved); on run6-int56 PROVED.

## The repair

RULE (annotations §7.592). The two fill sites are `ExpressionEmissionMixin._handle_dotted_call` (`self.m(..)`, key
`_dk`) and `_handle_call_expr` (module function, key `func_name`; the keyword-bound path included); both mirror twins
are `\trusted`, and they are the only `_add_abstract_op` calls of that `val`. `_run_pipeline` installs an
instance-attribute observer over `transpiler._add_abstract_op` (route #506's device: no emitter source change, emission
byte-identical) that, on the `pycsl_none_map` declaration, reads the filling frame's callee key and parameter name.
After `transpile()` each fill is judged: the callee's IR bindings (by name or `whyml_ident` name) must all be
`abstract`, or `trusted` without a `declared_in:` reviewer, or `declared_in:<relpath>::<Class.m>` whose definition in
`src/self-annotate/src/<relpath>` carries `#@ \trusted` / `#@ \abstract` in the `#@` block directly above its `def`.
Anything else (a verified body, no visible binding, an unresolvable declaration) is REFUSED. The refusal is at the
CALL SITE, so it covers every use the callee makes of the parameter (in its body or contracts).

Advice (audited FOLLOWABLE, see below): pass the argument explicitly; make the parameter required; or mark the callee
`#@ \trusted` only if its contract holds for `None`.

## Witnesses and measurements

- PROBE `witnesses-r592/hc1762_cl_isinstance_dict.py` (rt56): EMITTED at base fe057a6c1 (driver: PROVED), REFUSED
  R592 at HEAD.
- CORPUS witnesses (expected FAIL; CPython breaks each claim): 9630 (`isinstance`, module function), 9631 (the
  `self.g(3)` site), 9632 (truthiness vs `len`), 9633 (`len`, `self.` site), 9634 (a keyword-bound later argument
  `g(3, y=1)` skipping `d`): all EMITTED at base, all REFUSED R592 at HEAD (`--no-proof` triage). Full-proof verdicts at base NOT
  MEASURED (proof slots saturated until the time box; the driver measured hc1762, 9630's shape, PROVED at run6-int56).
- CONTROLS (expected PASS): 9640 (callee `#@ \trusted`, `h() == g(3) + 1`), 9641 (verified callee, `d` passed
  explicitly): EMITTED at base and HEAD. Full-proof verdicts NOT MEASURED (same reason): OWED.
- 9390 (lvN's own witness, expected PASS): its callees were VERIFIED bodies, so it is REFUSED R592 at HEAD as written
  (correctly: its subject is the fill, and the fill reached verified bodies). REWRITTEN with both callees `#@ \trusted`
  (contracts that hold for `d = None`; they never read `d`), keeping its subject (both fill sites still emit
  `pycsl_none_map`). Its emission MOVES exactly by the two callees becoming `val`s.
- OTHER USES (u40 probes `witnesses-r592/u40/`, the callee omitted-default call `g(3)` in each): under an `ensures`
  claim `bool(d) == (len(d) != 0)` (p_bool), `len(d) + x >= 3` (p_lenens), `if d: ...` (p_ifd) reach the fill and
  are REFUSED R592; under `#@ no_exception \all` `len(d)` (p_len), `list(d)` (p_list), `sorted(d)` (p_sorted),
  `d.keys()` (p_keys), `dict(d)` (p_dictcopy) are refused on the CALLEE side by pre-existing rules (the parameter
  may be `None` there), at base and HEAD alike; `d.get(..)` / `d[k]` / `for k in d` likewise (first-draft witnesses).
  A spec-context call (`#@ requires g(3) == 1`) fills too and is refused; a non-Optional `d: Dict[..] = None` was
  refused at base by the default-type rule and is now refused R592 first. A receiver-variable call `c.g(3)`, a
  static method `C.g(3)` and a constructor `C()` omitting the argument do NOT fill `pycsl_none_map` (an opaque `val`
  without the callee's contract / an unconstrained field), so nothing is decided there (emission unchanged).
- INERTNESS (own base = `git archive fe057a6c1`, same scripts): corpus root 3097 -> 3099 .mlw, 1 MOVED (9390, the
  declared source rewrite), 0 GONE, 0 APPEARED (+2 controls; the 5 witnesses refused); python-reference 2185 0 / 0 /
  0. Mirror: the full 53-file sweep did NOT RUN before the time box (heavy queue).
  Measured instead: `module6_whyml/statements.py`, the ONLY mirror file whose emission contains `pycsl_none_map`
  (grep of the driver's int56 mirror sweep: 20 occurrences, no other file), emitted byte-IDENTICAL at base and HEAD (and
  identical to the int56 sweep): its fills call the `#@ declared_in` `_expr_to_whyml`, whose definition is `\trusted`.
  Every other mirror file cannot move (the observer returns the emitter's own result; only a fill can refuse). The
  53/53 sweep is OWED.
- ADVICE (`witnesses-r592/advice/`): a592_pass_explicit (= 9641), a592_required_param, a592_trusted_callee (= 9640):
  not yet RUN under full proof (OWED; the advice
  audit entry is not written until they are).
- LEDGERS: refusal-witness census +5 rows (tool `_census_row`, interpreter wrapper adding `--no-proof`: R592 is
  raised in Module 6 emission before any proof), all REFUSAL R592. Fidelity x3 rc 0 / 0 / 0 (check-self-annotate-sync,
  self-annotate-mirror-check, doc-coherency --check). run-soundness-planes, check-vacuous-drivers, claim-vacuity,
  refusal-witness-coverage, open-route-carriers and the rule-18 planes: OWED (queue). check-refusal-advice-audited
  (run before the census append): rc 0, R592 listed as unaudited.
