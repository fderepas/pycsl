# PyCSL axiom-plumbing internals — the generic cross-validated-lemma end-to-end path

This document describes the **generic path** by which any cross-validated
lemma shipped as `MyModule.proofs/{rocq,lean}/MyProof.{v,lean}` and cited as
`#@ proof rocq|lean MyModule.MyLemma` becomes a *registered*, *bound*, and
*citable* Why3 `axiom` — constraining the real logic symbols of `MyModule`
and surviving propagation across a module-global method-call boundary and an
`import` boundary. The path is the same for every such lemma; only the
registry entry, its backing logic symbols, and the proof pair differ.

The path is realized by six PyCSL **compiler-pipeline modules** — NOT
auxiliary "helper tools"; they are core stages of the PyCSL tool itself, all
living under `src/pycsl/`. Five are the **Module-6 WhyML transpiler**
(`src/pycsl/module6_whyml/` + `Module6_WhyMLTranspiler.py`) and one is the
**front-end import-resolver** (`src/pycsl/frontend/ir_resolve.py`). They are
grouped here only by their shared *role in one feature* — the cross-validated
axiom plumbing of the gap-9→gap-12 arc — not as a standalone category. For the
generic mechanism the relevant trust contract is the
[axiom registry](glossary/axiom-registry.md) and its
[proof companion](glossary/proof-companion.md) (the generic Rocq + Lean
pairing every registered axiom must carry).

**The running example.** Throughout, the generic mechanism is illustrated by
one worked instance: the cross-validated axiom
[`UnixFs.Dir.scan_reflects_present`](glossary/axiom-registry.md) from the
standard-library `os` directory family. That family —
`scan_reflects_present`, `remove_reflects_absent`, `insert_preserves_unique`,
`empty_disk_slots_dead`, and `block5_decode_frame` — is exactly the set of
lemmas that first exercised this path end to end; they are the concrete
`MyModule.MyLemma` instances against which each module below is shown working.
Wherever a snippet names `UnixFs.Dir.scan_reflects_present`, read it as one
filling of the generic `MyModule.MyLemma` slot.

The worked example's motivating property is the directory-scan reflection
lemma (`pure_lib/os/UnixInodeFileSystem.py:_dir_lookup`): the bounded scan
over the 16 root-directory slots returns a non-negative inode **iff** some
live slot decodes to `name`. This is inductive over the slot loop, so the SMT
backend (Alt-Ergo/Z3) times out (gap-9 measured 14.6M / 11.6M / 18.8M
solver steps). Per the *CSL family rule — generic to any module — an SMT wall
on an inductive loop property is sourced from the proof assistants: a paired
Rocq + Lean proof (here
`unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean}`,
the concrete `MyModule.proofs/{rocq,lean}/MyProof.{v,lean}`, Rocq closed under
the global context, Lean axioms ⊆ {propext, Quot.sound}) is registered as a
Why3 preamble `axiom` and cited via
`#@ proof rocq|lean MyModule.MyLemma`.

Registering the axiom is the easy half — and that half is generic: any
validated body keyed by its dotted qualname becomes a preamble `axiom`. The
hard half, also generic, is making the citation **non-vacuous** — making the
axiom constrain the *real* logic symbols of the module, then carrying that
constraint through a chain of indirections: a method call on a module-global
object, and an `import` of the module's public wrappers into a driver. (In
the worked example the global is a filesystem object and the wrappers are the
public `os` functions.) The six modules form that path:

| # | File | Role in the path |
|---|------|------------------|
| 1 | `module6_whyml/preamble.py` | **Register** the axiom + declare its backing logic functions |
| 2 | `Module6_WhyMLTranspiler.py` | **Initialize** the transpiler state that recognizes those functions |
| 3 | `module6_whyml/expressions.py` | **Bind** the functions RAW in contracts (the load-bearing risk-2 binding) |
| 4 | `module6_whyml/functions.py` | **Propagate** a mixed self-field + param `ensures` across a method call |
| 5 | `module6_whyml/abstract_ops.py` | **Order** the declarations so referencing symbols come after them |
| 6 | `frontend/ir_resolve.py` | **Resolve** the import boundary (inductive-decl + var-name machinery) |

The path, read end to end (generic, with the worked example in parentheses):
tool 1 makes the axiom and its `val function` symbols (for the example,
`slot_inode`, `slot_name`, `dir_lookup`) exist in the preamble; tool 2 wires
up the per-module state (`_axiom_logic_funcs`, `_emitting_val_contract`) that
lets the rest of the pipeline recognize those symbols; tool 3 makes a contract
reference to a backing logic function (the example's `dir_lookup(...)`) lower
to the *real* registry symbol instead of degrading into a fresh,
axiom-unconstrained abstract op; tool 4 lets a postcondition that mixes a
self-field with a parameter (the example's
`(\result == 0) <==> dir_lookup(self.disk, 5, pathname) >= 0`) survive being
propagated to a call site; tool 5 fixes emission ordering so the
`val function` decls land before the abstract ops that reference them; tool 6
carries the imported predicate signatures and stub-citation surgery across the
`import` boundary.

> **Honest scope note (for the worked example).** As of the spec-9
> implementation report, the os-LEVEL non-vacuity is demonstrated (the syscall
> postconditions prove *only* via the binding), but the END-TO-END public-API
> flip is blocked on a pre-existing module-global / logic-vs-program duality
> gap. Tool 6 is therefore **dormant for the os case** (the importer
> deliberately keeps `name_present` opaque to avoid an E-matching blow-up) but
> is part of the same generic import-boundary surface and is documented here
> for completeness. This caveat is a property of that one example, not of the
> generic path.

---

## Tool 1 — `module6_whyml/preamble.py`: register the axiom + declare its functions

### (a) Purpose

The transpiler needs a place where a `#@ proof rocq|lean <qualname>`
citation can resolve to (i) the Why3 axiom body it injects into the module
preamble, and (ii) the logic symbols that body mentions, declared before
the axiom so the axiom typechecks. This file is the *single source of
truth* for both — the "make the axiom exist in the preamble" change.

### (b) What it does / feature list

- Hosts `_AXIOM_REGISTRY` (`preamble.py:18`), the curated catalogue of
  hand-validated axiom bodies keyed by dotted qualname.
- Hosts `_AXIOM_FUNCTIONS` (`preamble.py:153`), the map from a qualname
  *prefix* to the `val function` / `predicate` declarations its axioms
  need.
- Emits the axiom block (`_emit_preamble_axioms`, `preamble.py:737`):
  declares each backing function once, then emits each cited axiom under a
  sanitized name `pycsl_axiom_<qualname>` with a provenance comment.
- Forces `use array.Array` / `use string.String` etc. into scope when a
  cited axiom or an axiom-backing function mentions those types
  (`_scan_preamble_needs`, `preamble.py:214`, esp. the gap-9 `array int`
  forcing at lines 238–269).
- Precomputes the set of axiom-backing logic-function *names* the module
  must bind raw (`_precompute_axiom_logic_funcs`, `preamble.py:664`).
- Emits declarations for axiom functions that are *referenced but not
  cited* (the importer case): `_emit_uncited_axiom_func_decls`
  (`preamble.py:991`) and `_inductive_referenced_axiom_decls`
  (`preamble.py:952`).

### (c) Internal structure

`_AXIOM_REGISTRY` is `Dict[str, str]`: dotted qualname → Why3 universal
formula (the axiom body); any `MyModule.MyLemma` lands here. The worked
example's `UnixFs.Dir.scan_reflects_present` entry
(`preamble.py:123-131`) is the IFF

```
forall disk : array int. forall blk : int. forall name : string.
( forall j : int. 0 <= j < 16 -> slot_inode disk blk j >= 0 ) ->
( ( dir_lookup disk blk name >= 0 )
  <->
  ( exists k : int. 0 <= k < 16
    /\ slot_inode disk blk k <> 0
    /\ slot_inode disk blk k < 32
    /\ slot_name disk blk k = name ) )
```

The leading `forall j. ... slot_inode disk blk j >= 0` antecedent mirrors
the proofs' `slot_inode_nonneg` / `hnn` hypothesis — the unsigned-byte fact
that a decoded inode is non-negative. It is *not* smuggled into the IFF; it
is an explicit antecedent, keeping the axiom faithful (not over-strong).
The companion entry `UnixFs.Dir.slot_inode_nonneg` (`preamble.py:143-145`)
states that fact as a named axiom, so a caller can discharge the antecedent
without a per-call class invariant. Callers cite both.

`_AXIOM_FUNCTIONS` is `Dict[str, List[str]]`: a qualname *prefix* →
declarations (one prefix per module family). The worked example's
`"UnixFs.Dir."` entry (`preamble.py:207-211`) declares the three backing
symbols as Why3 `val function` (both a program symbol and a logic symbol):

```
val function slot_inode (disk: array int) (blk: int) (k: int) : int
val function slot_name  (disk: array int) (blk: int) (k: int) : string
val function dir_lookup (disk: array int) (blk: int) (name: string) : int
```

The `val function` idiom is what makes the binding possible: `dir_lookup`
is callable from a program body *and* nameable in the axiom and in logic
contracts. `List[str]` (not `str`) lets one prefix carry several decls (the
struct round-trip axioms need both `struct_pack_<id>` and
`struct_unpack_<id>`).

`_emit_preamble_axioms` (`preamble.py:737`) drives the citation pull:

1. Scan every function for `proof` entries; collect the cited qualnames
   (dedup — Rocq + Lean cite the same target). Return `[]` early if none,
   so non-citing files emit byte-identically.
2. For each cited qualname, match it against every `_AXIOM_FUNCTIONS`
   prefix; emit each backing decl once (tracked in `declared_fns` and
   recorded in `self._axiom_emitted_decls` so the abstract-op dedup in
   tool 5 knows exactly which symbols were emitted here).
3. Call `_precompute_axiom_logic_funcs` (tool 2 plumbing).
4. For each cited qualname, look it up in `_AXIOM_REGISTRY` (a missing
   entry is a hard `PyCSLIRError` at transpile time), and emit
   `axiom pycsl_axiom_<qualname> : <body>` with a `(* ... cross-validated
   Rocq + Lean *)` comment.

`_scan_preamble_needs` additionally forces `use array.Array` when a cited
axiom body contains `array int` (lines 228–237) OR when an axiom-backing
function with an `array int` parameter is *applied in a contract* even
without its qualname being cited in this module — the importer/driver case
(`_refs_array_fn`, lines 244–269). Without this the emitted
`val function dir_lookup (disk: array int) ...` decl would fail to
typecheck.

### (d) How to use

**PyCSL author.** Cite the axiom on the function whose VC needs it:

```python
#@ proof rocq UnixFs.Dir.scan_reflects_present
#@ proof lean UnixFs.Dir.scan_reflects_present
#@ proof rocq UnixFs.Dir.slot_inode_nonneg
#@ proof lean UnixFs.Dir.slot_inode_nonneg
def sys_access(self, pathname: str) -> int: ...
```

The transpiler then injects both axioms into the module preamble, where
they become hypotheses in scope for every goal in the module.

**Maintainer.** To add a new axiom — for *any* module, not just the worked
example: (1) add the validated body to `_AXIOM_REGISTRY` keyed by
`MyModule.MyLemma`, (2) if it mentions new logic symbols, add their
`val function`/`predicate` decls under the right `MyModule.` prefix in
`_AXIOM_FUNCTIONS`, (3) ship the paired Rocq + Lean proofs into
`MyModule.proofs/{rocq,lean}/MyProof.{v,lean}` and document the family in
`docs/glossary/axiom-registry.md`. The trust model
([axiom-registry](glossary/axiom-registry.md)) and the generic Rocq + Lean
pairing ([proof-companion](glossary/proof-companion.md)) require a paired
proof, no extraneous kernel axioms, and an `audit_proof.py` cross-check.

---

## Tool 2 — `Module6_WhyMLTranspiler.py`: initialization / state plumbing

### (a) Purpose

The other five tools recognize axiom-backing logic functions and propagate
mixed-leaf contracts by consulting per-transpiler state. This file is the
mixin base that declares and initializes that state and orders the emission
passes so the state is populated before it is read.

### (b) What it does / feature list

- Declares the transpiler as a composition of mixins (tools 1, 3, 4, 5 are
  mixed in here): `class Module6_WhyMLTranspiler(ExpressionEmissionMixin,
  StatementEmissionMixin, PreambleEmissionMixin, FunctionEmissionMixin,
  TypeInferenceMixin, AutoTrustMixin, AbstractOpsMixin)` (lines 17–25).
- Initializes the flags and maps the path relies on (`__init__`,
  lines 28–134).
- Drives the full emission order in `transpile()` (lines 378–513),
  including the gap-9 conditional reorder.

### (c) Internal structure

Two `__init__` members are load-bearing for this path:

- `self._emitting_val_contract` (line 78) — `False` except while emitting a
  bodyless `val` / trusted-stub contract. It gates the narrow logic-symbol
  safety net in tool 3 (`_emit_contract_logic_symbol`), so an unknown
  applied symbol is treated as a logic predicate only inside a stub's
  contract, never in body position.
- `self._module_global_classes` (lines 71–72) — `name → class` for every
  module-level global object instance (e.g. `_filesystem → UnixFs`),
  available in every function so `g.method(...)` resolves to the global
  record's class. This is what lets a method call on a module global pick
  up the callee's propagated contract.
- `self._imported_inductive_sigs` (lines 66–67) — imported `#@ inductive`
  predicate signatures whose rule was deliberately not crossed (tool 6
  populates this; tool 3's fallback reads it).
- The whole family of `self._module_method_*_ensures` maps
  (lines 113–120), including
  `self._module_method_field_param_result_ensures` (line 117) — the "4th
  map" that tool 4 builds.

`self._axiom_logic_funcs` is *not* declared in `__init__`; it is created by
`_precompute_axiom_logic_funcs` (tool 1), which `transpile()` calls
explicitly (line 407) before inductive emission. Tools 3 and 5 read it via
`getattr(self, "_axiom_logic_funcs", set())`, so an early access is safe.

`transpile()` (lines 378–513) sequences the passes. The key ordering
decision is the gap-9 conditional reorder (lines 415–429): if any
`#@ inductive` rule references an axiom-backing logic function OR a
module-global (`_inductive_refs_global_or_axiom_func`, in tool 1), it emits
**axioms → uncited-axiom-func decls → module globals → inductive**;
otherwise it keeps the historical **inductive → axioms → globals** order so
every existing inductive/axiom file emits byte-identically. After all
functions are emitted, `_insert_abstract_val_block` (tool 5) splices in the
accumulated abstract ops.

The maps are built from `funcs_for_maps` (line 453) — the real functions
*plus* mixin dependency pseudo-functions — so imported `\trusted` stubs are
covered. `_module_method_field_param_result_ensures` is built at lines
489–490.

### (d) How to use

**PyCSL author.** No direct surface — this is internal plumbing. The author
exercises it indirectly by citing axioms (tool 1) and writing the contracts
tools 3 and 4 propagate.

**Maintainer.** When adding a new propagation map or a new
axiom-recognition flag, declare it in `__init__` (so accessing it before
the first reset is safe), populate it in `transpile()` from
`funcs_for_maps`, and decide whether it needs to be computed before or
after the inductive/axiom reorder. Preserve the gated, byte-identical
property: any new behavior must be a no-op for files that do not trigger it.

---

## Tool 3 — `module6_whyml/expressions.py`: bind axiom functions RAW in contracts

### (a) Purpose

A contract reference to a backing logic function (the worked example's
`dir_lookup(self.disk, 5, pathname)`) must lower to the *raw logic
application* `(dir_lookup ...)` bound to the registry's `val function`
symbol. The default lowering for an applied symbol with no native WhyML
equivalent is an arity-suffixed abstract op (`dir_lookup_3`) — a *fresh,
axiom-unconstrained* symbol. If the contract bound to `dir_lookup_3`, the
cited axiom (which constrains `dir_lookup`) would say nothing about it, and
the citation would be vacuous. This holds for any `MyModule.MyLemma` whose
body mentions a backing function; this tool makes the citation refer to the
real symbol — the load-bearing **risk-2 binding**.

### (b) What it does / feature list

- In `_handle_call_expr` (`expressions.py:1090`), recognizes a call whose
  function name is in `self._axiom_logic_funcs` and emits the raw
  application with no int-coercion and no abstract op.
- Likewise recognizes applied `#@ datatype` constructors and applied
  `#@ inductive` predicates, lowering each to a raw `(p args)`.
- Provides the narrow contract-position logic-symbol fallback
  (`_emit_contract_logic_symbol`, `expressions.py:1037`) used at the import
  boundary.

### (c) Internal structure

The binding is `expressions.py:1120-1121`:

```python
if func_name in getattr(self, "_axiom_logic_funcs", set()):
    return f"({func_name} {' '.join(args)})" if args else func_name
```

This arm sits in `_handle_call_expr` after the constructor arm (1103) and
the inductive-predicate arm (1109), and *before* the struct-call, named-
builtin, dotted-call, and generic abstract-op paths. Because it returns the
raw `(dir_lookup self.disk 5 pathname)`:

- The args keep their faithful types (`self.disk : array int`,
  `pathname : string`), so no `_coerce_to_int` collapses them.
- No `_add_abstract_op("val dir_lookup_3 ...")` is emitted — so there is no
  fresh symbol to bind to.

The result is that `_dir_lookup`'s `ensures \result == dir_lookup(...)` and
the `name_present` inductive rule's `slot_inode/slot_name` applications all
bind to the **same** symbols the axiom constrains. That is what ties the
citation to the *real* scan rather than to a vacuous abstract twin.

`_emit_contract_logic_symbol` (`expressions.py:1037`) is the narrow safety
net for the import boundary: in contract position (`_in_spec`) an unknown
applied symbol is a *logic* predicate reference, so it must emit a logic
`predicate name argtypes`, not an illegal program `val name_N (x0:int):int`.
For an imported `#@ inductive` predicate whose rule was not crossed
(recorded by tool 6 in `_imported_inductive_sigs`), it recovers the correct
param types from the dependency signature (lines 1065–1074) — e.g.
`predicate name_present (array int) (string)` rather than the mistyped
`int` default. Part 1 (carrying the real `#@ inductive` decl across the
boundary, tool 6) always wins when it can: a propagated decl puts the name
in `_inductive_preds`, so the inductive arm (1109) fires first and this
fallback is never reached.

### (d) How to use

**PyCSL author.** Write the contract over the logic function directly:

```python
#@ ensures \result == dir_lookup(self.disk, block_num, pathname)
def _dir_lookup(self, block_num: int, pathname: str) -> int: ...
```

Once any function in the module cites a `MyModule.*` axiom (in the example,
a `UnixFs.Dir.*` axiom) — or applies the symbol in a contract / inductive
rule — the backing function (here `dir_lookup`) is in `_axiom_logic_funcs`
and lowers raw, so the contract is bound to the axiom-constrained symbol.

**Maintainer.** The set membership is everything: a symbol binds raw iff it
is in `_axiom_logic_funcs`, which tool 1's `_precompute_axiom_logic_funcs`
populates from cited qualnames *and* from names applied by inductive rules
or function contracts. If a new axiom symbol is binding to an `_N` abstract
op instead of raw, check that its `val function` decl is reachable from a
cited (or applied) qualname prefix in `_AXIOM_FUNCTIONS`.

---

## Tool 4 — `module6_whyml/functions.py`: propagate the mixed field + param `ensures`

### (a) Purpose

A registered axiom is often cited on a method whose `ensures` references
**both** a self-field **and** a parameter — in the worked example, the os
syscall presence link
`(\result == 0) <==> dir_lookup(self.disk, 5, pathname) >= 0`, mixing the
self-field `self.disk` and the parameter `pathname`. PyCSL propagates a
callee's `ensures` to a call site through a family of maps, but the three
pre-existing maps each reject the *other* leaf kind: result-only,
result+param, and result+field. A clause mixing a self-field with a param
fell through all three and propagated nowhere — so a caller that constructs
the object and calls the method (in the example, constructs a filesystem and
calls a syscall) could prove nothing about the result. This tool adds the
missing fourth map (the A2c+ case); it serves any axiom citation of this
mixed shape, not just the worked example.

### (b) What it does / feature list

- Adds `_build_method_field_param_result_ensures_map`
  (`functions.py:807`) — the "4th map": clauses referencing `\result` AND a
  self-field AND at least one param.
- Sits alongside the three existing maps:
  `_build_method_result_ensures_map` (606),
  `_build_method_param_result_ensures_map` (649),
  `_build_method_field_result_ensures_map` (735).
- Renames each formal param to the abstract stub's positional name `x_i`
  while keeping the `self.x` FieldGet verbatim.

### (c) Internal structure

The four maps partition the propagatable `ensures` clauses by which leaf
kinds they touch:

| Map | `\result` | self-field | param | `\old`/local |
|-----|:---------:|:----------:|:-----:|:------------:|
| `result_ensures` | yes | no | no | no |
| `param_result_ensures` | yes | no | yes | no |
| `field_result_ensures` | yes | yes | no | no |
| **`field_param_result_ensures`** (new) | yes | **yes** | **yes** | no |

`_build_method_field_param_result_ensures_map` (`functions.py:807-912`) has
three inner helpers:

- `classify(node, params)` (823) — returns `False` if the subtree touches a
  *disallowed* leaf (`\old`, a local, or a non-`self` object field); a bare
  `Var` is allowed only if it is a param.
- `saw(node, kind, params)` (847) — detects presence of a `\result` or a
  `self.<field>` reference.
- `rename(node, pmap)` (862) — rewrites each formal-param `Var` to `x_i`.
- `refs_param(node, params)` (879) — confirms at least one param appears.

The retained clauses (lines 905–909) require `result` AND `field` AND at
least one `param`. The "at least one param" requirement is what keeps the
map disjoint from `field_result_ensures` (a `\result == self.x` clause has
no param and stays in the old map), so existing files emit byte-identically.

The renaming is sound because `self` and `x_i` live in distinct namespaces
— there is no collision when the call site adds a leading `(self: <class>)`
receiver param and renames params to positional `x_i`.

**Consumer side** (`expressions.py`). `_resolve_dotted_signature`
(`expressions.py:708`) folds the four maps into `field_spec` for both
`self.<m>(...)` (lines 743–751) and `<recordvar>.<m>(...)` /
`_global.<m>(...)` (lines 776–789). `_handle_dotted_call`
(`expressions.py:802`) then gives the abstract op a leading
`(self: <receiver_class>)` parameter and passes the receiver record (lines
877–890), and `_dotted_ensures_suffix` (`expressions.py:929`) renders the
propagated clauses as `ensures { ... }` lines with `_current_self_type` set
to the receiver class so `self.x` binds to the actual instance and the
positional `x_i` params are in scope.

### (d) How to use

**PyCSL author.** Write the natural mixed contract; it now survives the call:

```python
#@ ensures (\result == 0) <==> dir_lookup(self.disk, 5, pathname) >= 0
def sys_access(self, pathname: str) -> int: ...
```

A caller `fs.sys_access(name)` now sees the abstract op carry
`ensures { (result = 0) <-> (dir_lookup (self).disk 5 x0) >= 0 }` with `self`
bound to `fs` and `x0` to `name`.

**Maintainer.** When extending the propagation surface, mirror the
four-map partition: a new clause shape needs a `classify`/`saw`/`rename`
triplet, must be disjoint from the existing maps (gate it on the genuinely-
new combination), and must be folded into both branches of
`_resolve_dotted_signature` and into `Module6_WhyMLTranspiler.transpile()`'s
map-building block.

---

## Tool 5 — `module6_whyml/abstract_ops.py`: order decls before their references

### (a) Purpose

Abstract `val` declarations are accumulated during emission and spliced in
as one block late, after the last `type` declaration. But an abstract op
(in the worked example, a `_filesystem_sys_access` stub) may *reference* an
axiom-backing `val function` (the example's `dir_lookup ...`) that the
preamble emits at a position at or after the chosen insert point. Why3 rejects a forward reference ("unbound
symbol"). This tool advances the insert point past any such referenced
axiom-function declaration so the abstract block lands after its
dependencies.

### (b) What it does / feature list

- `_add_abstract_op` (`abstract_ops.py:18`) — registers a decl, dedup by
  name; same-name different-arity collisions get an `_N` suffix.
- `_find_abstract_val_insert_idx` (`abstract_ops.py:54`) — picks the insert
  point (after the last `type`, skipping `invariant`/`by`/`with`
  continuation lines and a trailing blank).
- **`_advance_past_referenced_axiom_decls`** (`abstract_ops.py:93`) — the
  ordering correction: advances the insert index past any
  `val function`/`function`/`inductive`/`predicate` declaration whose
  symbol the pending abstract ops reference.
- `_insert_abstract_val_block` (`abstract_ops.py:150`) — splices the block,
  skipping any decl whose name the axiom block already emitted (avoiding a
  double declaration Why3 would reject).

### (c) Internal structure

`_advance_past_referenced_axiom_decls(out, idx)` (`abstract_ops.py:93-148`):

1. Build `axiom_names` — the symbols the axiom block itself declares (read
   from `self._axiom_emitted_decls`, set by tool 1). Their abstract-op
   *twins* are deduped away later, so they must NOT count as "referenced"
   here (otherwise the block would drag past its own kept declaration).
2. Build `abs_text` — the concatenated text of the pending abstract ops,
   *excluding* those `axiom_names` twins.
3. Walk `out` from `idx`; for every `val function`/`function`/`inductive`/
   `predicate` line whose declared symbol (`_decl_symbol`) appears in
   `abs_text`, set `new_idx = j + 1`.
4. If advanced, skip continuation lines (`invariant`, `by`, `with`, `| `,
   `axiom`) and a trailing blank so the block is not spliced
   mid-declaration.
5. Returns `idx` unchanged when there is no forward reference — so every
   existing file is byte-identical.

It is called from both branches of `_find_abstract_val_insert_idx` (after
the last `type`, line 84; and at the first `let`/non-ghost `val`, lines
88/90), so the correction applies regardless of which insert strategy wins.

`_insert_abstract_val_block` (`abstract_ops.py:150-191`) computes
`axiom_decl_names` from `self._axiom_emitted_decls` and skips any abstract
op whose name is already declared by the axiom block — so `dir_lookup`,
`bit_and`, `struct_pack_<id>`, etc. are declared exactly once.

### (d) How to use

**PyCSL author.** No surface — this is emission-ordering internals. The
author benefits transparently: a stub citing `dir_lookup` produces a
well-formed `.mlw` instead of an "unbound symbol" rejection.

**Maintainer.** The invariant to preserve is *gated byte-identity*:
`_advance_past_referenced_axiom_decls` and the
`_insert_abstract_val_block` dedup must be no-ops unless a real forward
reference / double declaration exists. When adding a new preamble-logic
declaration kind, extend `_decl_symbol` and the continuation-line skip set
together, and make sure the new kind is recorded in
`_axiom_emitted_decls` if its twin should be deduped.

---

## Tool 6 — `frontend/ir_resolve.py`: import-boundary resolution machinery

### (a) Purpose

When a module's public wrappers are imported into a driver, and those
wrappers' contracts cite a registered axiom, the logic symbols the contracts
reference — any imported `#@ inductive` predicate, and the module-global
objects their self-field clauses name — must also be made available, with the
correct types, on the importer side. (In the worked example the wrappers are
the public `os` functions `mkdir`/`access`, imported via
`from pure_lib.os import mkdir, access`, and the inductive predicate is
`name_present`.) This is the gap-8 lineage: the `#@ inductive` declaration was
*dropped* across the import boundary, leaving the predicate call (the
example's `name_present(...)`) as an unknown call that the abstract-op
fallback emitted as an illegal program value. This tool carries the needed
declarations and signatures across — generically, for any
import-of-an-inductive-predicate case.

> **Dormant for the worked example (os case).** For `UnixFs.Dir`, the
> importer deliberately does NOT cross the `name_present` rule (its
> `\exists k. slot_inode ...` premise has a high-fan-out E-matching trigger
> that OOMs the large wrapper VCs). Instead it strips the heavy scan-axiom
> citation from the injected stub and keeps `name_present` opaque, recording
> only its signature. This is a tuning choice for that one lemma family; the
> machinery below is the same generic surface used by gap-8/spec-8 for any
> import-of-an-inductive-predicate case.

### (b) What it does / feature list

- `_strip_dir_scan_proofs` (`ir_resolve.py:193`) — drops the
  `UnixFs.Dir.*` `#@ proof` citations from an injected trusted stub.
- `_contract_referenced_var_names` (`ir_resolve.py:217`) — collects every
  Var/object name referenced in the injected stubs' contracts (including
  the object of an `Attribute`/`FieldGet`), to scope module-global
  propagation.
- `_contract_referenced_names` (`ir_resolve.py:246`) — collects every
  callee name applied in the injected stubs' contracts, to scope inductive-
  declaration propagation (spec-8 Part 1).
- The direct-import resolver copies the dependency's `inductive_decls` into
  the importer's IR, scoped to referenced predicate names
  (`_resolve_direct_imports`, `ir_resolve.py:337-348`).
- The imported-class resolver records imported inductive predicate
  *signatures* into `_imported_inductive_sigs`
  (`ir_resolve.py:506-512`), and strips the heavy citation from each
  injected method/helper stub (lines 469, 487).

### (c) Internal structure

`_strip_dir_scan_proofs(func)` (`ir_resolve.py:193-214`) returns a copy of
the stub with every `proof` entry whose `qualname` starts with
`"UnixFs.Dir."` removed. Rationale: a trusted stub's contract is *assumed*
in the importer (its body is not re-verified), so injecting the heavy scan
axiom would only pollute the importer's proof context with a high-fan-out
E-matching trigger. The axiom is cited where it is actually used — the
standalone `UnixInodeFileSystem.py` body verification. The
`slot_inode`/`slot_name`/`dir_lookup` `val function` decls the
`name_present` inductive still needs are emitted independently by tool 1's
`_emit_inductive_decls`.

`_contract_referenced_names(dep_funcs)` (`ir_resolve.py:246-267`) walks the
`requires`/`ensures` of the injected stubs and collects every `Call`
`func` name. `_resolve_direct_imports` (lines 337–348) uses it to copy only
the dependency `inductive_decls` whose predicate name set intersects the
referenced names — so an internal predicate the public contracts do not
reference does not cross the boundary. Module 6 then registers the copied
predicate in `_inductive_preds`, and `_emit_inductive_decls` emits the real
logic block — the program-`val` fallback (tool 3's
`_emit_contract_logic_symbol`) is never reached for it.

`_contract_referenced_var_names(dep_funcs)` (`ir_resolve.py:217-243`) is the
companion for module-global scoping: it additionally collects the `object`
string of an `Attribute`/`FieldGet` (so `_filesystem.disk` contributes
`_filesystem`), letting module-global propagation be scoped to the globals
the injected contracts actually touch.

In the imported-class path (`_resolve_imported_classes`,
`ir_resolve.py:416+`), each injected `<class>__<method>` stub (line 469)
and module-level helper (line 487) is passed through
`_strip_dir_scan_proofs` and marked `trusted`. Then, instead of copying the
`name_present` *rule* (whose `\exists` premise would blow up the wrapper
VCs), it records the dependency's inductive predicate *signatures* into
`ir_data["_imported_inductive_sigs"]` (lines 506–512). Tool 3's
`_emit_contract_logic_symbol` reads that map to emit a correctly-typed
opaque `predicate name_present (array int) (string)` — so the importer
type-checks while reasoning via the lighter, equivalent
`dir_lookup(disk, 5, name) >= 0` form.

### (d) How to use

**PyCSL author.** Import the public API normally:

```python
from pure_lib.os import mkdir, access
#@ ensures \result == 1
def mkdir_then_access_present(d: str) -> int:
    rc = mkdir(d, 0o777)
    if rc != 0: return 1
    return access(d, 0)
```

The resolver injects the trusted stubs and carries the predicate signatures
/ inductive decls the stubs' contracts reference, so the driver
type-checks. (For `UnixFs.Dir`, the end-to-end flip is blocked on the
separate module-global / logic-vs-program duality gap — see the scope note
in the intro.)

**Maintainer.** Two scoping helpers exist deliberately:
`_contract_referenced_names` (callee names → which inductive decls to
copy) and `_contract_referenced_var_names` (var/object names → which
globals to propagate). Keep import-boundary propagation *scoped* to what the
public contracts reference, so internal symbols do not leak across the
boundary. When a propagated decl carries a heavy E-matching trigger, prefer
the opaque-signature route (`_imported_inductive_sigs` +
`_strip_dir_scan_proofs`) over copying the rule, and reason at the boundary
via a lighter equivalent form.

---

## See also

- [axiom-registry](glossary/axiom-registry.md) — the registry concept and trust model (generic to any `MyModule.MyLemma`)
- [proof-companion](glossary/proof-companion.md) — the generic Rocq + Lean pairing every registered axiom carries
- `11-0743-convergence-spec-9.md` — the worked example's axiom + binding (the validated Rocq + Lean proofs)
- `11-0743-convergence-gap-9.md` — the inductive lemma and the SMT wall
- `11-0632-convergence-gap-8.md` / `11-0632-convergence-spec-8.md` — the import-boundary lineage of tool 6
