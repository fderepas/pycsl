# OPEN ROUTE #342 — THE CONSTRUCTOR-INVARIANT GOAL READS ONLY PLAIN `self.f = e` STORES (for/tuple/with/del/setattr/alias/+=/loop/branch stores ignored; `__class__` reassignment)
**Status: REPAIRED, candidate (gen #37, 2026-10-24; r341 executor off 8984dce3 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 24; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r342/`: own class: `for self.x in ..` (i21), tuple target (i22), `del self.x` (i23), `with .. as self.x` (i24) give vacuous goals like
`goal _check_class_inv_b : forall x. x = 0 -> x = 0`; subclass after a leading `super().__init__()` (defeats #335): del (i10), setattr (i12), for (i17),
tuple (i18); #226's documented "computed / control-flow store: not covered" gap is a LIVE false proof: setattr (i20), `+=` (i25), setattr comprehension
(i26), alias `s = self; s.x = 5` (i35), while (i38), if (i39); `obj.__class__ = C` retypes an object (x03; #338's census does not count __class__ stores).
The same shapes in ordinary methods are refused (#301/with-binding), so __init__ takes a weaker path.
Repair: the constructor-invariant goal must be computed from the FULL constructor body semantics (every store form, control flow, aliases of
self) — or REFUSE any __init__ (of an invariant-carrying class or its subclasses) that stores an invariant field by any form other than
straight-line `self.f = e` (and any `self` alias/escape before the invariant is established); refuse `__class__` stores.

## REPAIR (2026-10-24, r341 executor off 8984dce3; code 88a8a4c7 + 7be6e53a, corpus 0904473f / 7be6e53a / ec7df9fe, census 41dddc52 / 768c1725, docs 83deebdc, stdlib baseline note 1a787512 + route docs)
**Design: sound refusal, no emission change** (same inline `_run_pipeline` block as #341; mirror twin `\trusted`; no new def; ledger 3).
A faithful model of every store form would mean a symbolic constructor semantics feeding route #226's goal (loops, branches,
aliasing, method effects) — and even the existing control-flow arms (`init_unknown_cf_fields`, route #150's opacity) end in
"unknown -> NO goal", which is the hole itself. The refusal moves nothing (measured below), so it was taken. RULES:
- `PYCSL-R342-CONSTRUCTOR-STORE-FORM`: for every record with merged (own or inherited) `class_invariants` and every file class on its
  base closure, `__init__` / `__post_init__` (nested classes / defs rebinding `self` skipped) is refused when it stores or deletes an
  invariant field (`FieldGet(self, f)` of the invariant; every field when the invariant mentions `self` otherwise) other than as the
  direct target of a TOP-LEVEL `self.f = e` / `self.f: T = e`; loads bare `self` other than as an attribute root or the first
  argument of builtin `type` / `isinstance` / `id`; rebinds `self`; touches `self.__dict__` / `__setattr__` / `__delattr__`; calls
  `self.m(..)`; uses `super()` other than as the leading `super().__init__(..)`; or contains a `return`.
- `PYCSL-R342-CLASS-REASSIGNMENT`: any `x.__class__` store / delete, or `setattr` / `delattr` / `__setattr__` / `__delattr__` with the
  constant `"__class__"`, anywhere in the file.
- `PYCSL-R342-EXTERNAL-INVARIANT-STORE` (new latent shape found while probing the repair): module-level / `__main__` code (not
  verified) storing / deleting an attribute named like an invariant field, or `setattr`/`delattr` with such a name or a dynamic one.
Docs: annotations §7.25 (2) and the route #226 table row (control-flow stores are now REFUSED; the straight-line COMPUTED store stays
"not covered"), translational §T.6.36, route #226 file note.
**Probe table** (full pycsl proof via heavy.sh; base = 8984dce3; CPython 1 = violates / raises):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| i21 own `for self.x in range(3)` | 4557 | violates | rc=0 PROVED | rc=1 REFUSED STORE-FORM |
| i22 own `(self.x, y) = (5, 1)` | 4558 | violates | rc=0 PROVED | rc=1 REFUSED |
| i23 own `del self.x`, `no_exception \all` | 4559 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| i24 own `with open(..) as self.x` | 4560 | violates | rc=0 PROVED | rc=1 REFUSED |
| i10 sub `super().__init__(); del self.x` | 4561 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| i12 sub `super().__init__(); setattr(self, "x", 5)` | 4562 | violates | rc=0 PROVED | rc=1 REFUSED (escape) |
| i17 sub `super().__init__(); for self.x in ..` | 4563 | violates | rc=0 PROVED | rc=1 REFUSED |
| i18 sub tuple target after super | 4564 | violates | rc=0 PROVED | rc=1 REFUSED |
| i20 own `setattr(self, "x", 5)` | 4565 | violates | rc=0 PROVED | rc=1 REFUSED (escape) |
| i25 own `self.x += 5` | 4566 | violates | rc=0 PROVED | rc=1 REFUSED |
| i26 own `if` store + `[setattr(self, ..) for ..]` | 4567 | violates | rc=0 PROVED | rc=1 REFUSED |
| i35 own `s = self; s.x = 5` | 4568 | violates | rc=0 PROVED | rc=1 REFUSED (alias) |
| i38 own store in `while` | 4569 | violates | rc=0 PROVED | rc=1 REFUSED |
| i39 own store in `if` | 4570 | violates | rc=0 PROVED | rc=1 REFUSED |
| x03 `d.__class__ = C` in `__main__` | 4571 | violates | rc=0 PROVED | rc=1 REFUSED CLASS-REASSIGNMENT |
| p1 (NEW) own `super().__setattr__("x", 5)` | 4577 | violates | rc=0 PROVED | rc=1 REFUSED STORE-FORM (super) |
| p7 (NEW) own `self.x = 5; self.helper()` (route #150 opacity -> no goal) | 4578 | violates | rc=0 PROVED | rc=1 REFUSED STORE-FORM (self.m) |
| p8 (NEW) `b = B(); b.x = 5` in `__main__` | 4579 | violates | rc=0 PROVED | rc=1 REFUSED EXTERNAL-INVARIANT-STORE |
| controls: super then control-flow / `for` stores of NON-invariant fields 4573; `self.x = k` under `requires k >= 0` + `type(self).__name__` 4574; no-invariant class with `for self.x` 4575; x03 with `d = C()` 4576 | 4573-4576 | ok | rc=0 | rc=0 PROVED |
Scratch, not filed: `self.__setattr__("x", 5)` / `object.__setattr__(self, ..)` / `self.__dict__["x"] = 5` were already REFUSED at base
by other checks; `exec("self.x = 5")` FAILS; `spoil(b)` from a verified function FAILS; non-leading `super().__init__()` over a
base storing 5 is REFUSED by R335.
**Blast radius / latent.** Root 2239 base / 2244 candidate 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186/2186 0/0/0 (`--min-files 2000`);
mirror 53/53 0/0/0 (`--min-files 50`): **no mirror file GONE, no OWED proof**. AST census before the change: 300 invariant-carrying
classes (own + closure) in 254 files; the only hits outside the new witnesses are corpus 4468 (already REFUSED by R335, which fires
first — census row unchanged) and two `pycsl_lib` stubs already outside the verifying set: `iomod.StringIO` (an `if`-guarded
`self._size = n`; baseline REFUSED) and `os/UnixInodeFileSystem.py` (`self._format_disk()`, `load_host_dir(self, ..)`; baseline
FAILS, now REFUSED — baseline note updated). **No latent false proof in the corpora.**
**Gates** (logs in `.r341tmp/`, removed at the end; rc): witnesses / controls above; byte-diff-compare root rc=0, pyref rc=0, mirror
rc=0; check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast
**61/61** rc=0 (first run 59/61: check-dropped-mutation CTXBIND 52 > 51 from witness 4560's `with .. as self.x` — exempted by name
like 1784; check-vacuous-drivers 10 > 9 from control 4575's tail return — rewritten to return `c.k`); doc-coherency --check rc=0;
check-assumed-facts rc=0 (ledger 3); check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61); check-refusal-witness-coverage rc=0
(285 demonstrated / 5 not, ceiling 5; rows 4550-4571, 4577-4579 via `_census_row`); check-dropped-mutation rc=0 (0 / 51 / 5 / 0);
check-refusal-advice-audited rc=0 (2 new advice sites audited FOLLOWABLE: 4572, 4576); check-open-route-carriers rc=0 (7);
check-stdlib-modules-verify: run in foreground chunks — modules 0-24 + hlib / iomod / UnixInodeFileSystem / plib re-proved
(verdicts match the baseline; csys TIMEOUT as baselined), and all 104 modules screened `--no-proof` for the new refusals: only
iomod and UnixInodeFileSystem hit (both in the non-verifying baseline), so no module can newly fail (the change only adds raises).
`--slow` planes NOT run.
**Residuals.** (1) Route #226's last carrier: a straight-line COMPUTED store (`self.n = three()`, `self.n = v`) still gets no goal and
the invariant is assumed (the advice therefore names literal / parameter values). (2) Over-refusal: `self.m()` / `B.__init__(self)`
/ `isinstance`-free helper calls on `self` / an early `return` in invariant constructors (0 users measured). (3) The check reads THIS
file's source: an imported class's constructor is checked only when its module is itself verified (a `pycsl_lib` stub outside the
verifying set, e.g. `iomod.StringIO`, is not refused at its importers). (4) Collection fields mutated in place (`self.buf.append(..)`
in a loop) are not stores of the field and are unchanged (route #226 emits no goal for non-int fields). (5) The external-store
refusal covers module-level code only; class-body code and `\trusted` functions storing invariant fields are not scanned; a store
through `exec` / `vars()` / `copy` is not seen. (6) `__new__`-based construction (`B.__new__(B)` + stores) is refused by an
existing check at the call; `__new__` bodies themselves are not scanned.
