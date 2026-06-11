# 11-1850-convergence-spec-15 — Grammar: subscript a module-global's array field in a contract (`<global>.<field>[expr]`)

STATUS: DONE

<!-- COORDINATION APPROVAL (editorial): APPROVED — clean, localizable, byte-additive, validated end-to-end.
The 4 additive pieces (one `?atom` grammar alternative `global_field_subscript`; the GlobalFieldSubscript
AST node; the transformer; the Module5 lowering to `Subscript(Attribute(Var(global), field), index)`) ride
EXISTING Module6 machinery (no Module6/Module4 edit). Prototyped: `_fs.x[0]` lowered to a real `Array.get`
and proved VALID; coexistence with `self.field[i]` + `global.field`-whole confirmed byte-identical; LALR
builds with ZERO conflicts; no corpus driver uses the production.
MANDATORY GATE: full-corpus byte-diff IDENTICAL (no existing rule edited; the new production is strictly
more specific — an extra `[expr]` trailer on the `<global>.<field>` base); the /tmp repro parses + type-
checks + proves; conformance 38/38; doc green. The non-blocking note (the body's array-read bounds VC is
Unknown) is the orthogonal no_exception IndexError discipline, NOT this grammar's concern. On success set
STATUS: DONE — then the follow-on stdlib turn flips fstat/dup. -->

Tool-agent SPEC PHASE. NO source edits made; /tmp probes only. This spec is the
compiler-side enabler for gap-15's Wall B (`11-1850-convergence-gap-15.md`,
lines 82–120): `fstat`/`dup` consequences cannot cross to the public `open`/`fstat`/`dup`
wrappers because a wrapper `#@ ensures` that reads `_filesystem.fd_inode[fd]` FAILS AT PARSE.

---

## 1. Gap recap (the parse failure)

The PyCSL contract grammar admits `self.<field>[i]` and bare `name[i]`, and (gap-10)
passing a module-global's *whole* array field as a call argument (`dir_lookup(_filesystem.disk, 5, p)`),
but has NO production for the INDEXED read of a module-global's array field:
`<global>.<field>[expr]`, e.g. `_filesystem.fd_inode[fd]`.

Reproduced minimally (`/tmp/gap15_repro.py`):

```python
class FS:
    def __init__(self):
        self.x = [0, 0, 0, 0]
_fs = FS()
#@ ensures \result == _fs.x[0]
def peek() -> int:
    return _fs.x[0]
```

`src/pycsl/pycsl.py /tmp/gap15_repro.py` →

```
[parse]: PyCSL Syntax Error around line 8:
ensures \result == _fs.x[0]
Unexpected token Token('LSQB', '[') at line 1, column 25.
Previous tokens: [Token('CNAME', 'x')]
```

The `param_field_access` rule (`Module2_Parser.py:1103`, `CNAME "." CNAME -> param_field_access`)
consumes `_fs.x` as a whole-field access; the following `[` then has no production and the
parse aborts — matching the gap-15 report (`Unexpected token '[' … Previous tokens:
[Token('CNAME','fd_open')]`).

### Where the grammar admits the sibling shapes (cite)

`src/pycsl/frontend/Module2_Parser.py`, the `?atom` rule:
- line **1100**: `"self" "." CNAME "[" expr "]" -> field_subscript`   ← `self.<field>[i]` (admitted)
- line **1101**: `"self" "." CNAME -> field_access`
- line **1103**: `CNAME "." CNAME -> param_field_access`              ← `<global>.<field>` WHOLE (admitted; gap-10's whole-field crossing)
- line **1114**: `CNAME "[" expr "]" -> subscript_access`            ← bare `name[i]` (admitted)
- (NO production for `CNAME "." CNAME "[" expr "]"`)                   ← `<global>.<field>[i]` (THE GAP)

---

## 2. The fix — ONE grammar production + ONE Module5 lowering arm

The Module4/Module6 machinery for the *resolved* form already exists (see §2.3); the only
missing pieces are the front-end production and its IR lowering.

### 2.1 Grammar production (`Module2_Parser.py`, `?atom`, after line 1100)

Add one alternative, mirroring `field_subscript` with a module-global base instead of `self`:

```
         | CNAME "." CNAME "[" expr "]" -> global_field_subscript
```

Place it immediately after line 1100 (alongside `field_subscript`). Under LALR this is
strictly longer than `param_field_access` (`CNAME "." CNAME`, line 1103); the `[` lookahead
drives the shift into the longer rule, exactly as `self.<field>[i]` (1100) coexists with
`self.<field>` (1101) and `dict_view_expr` (`CNAME "." CNAME "(" ")"`, 1102) coexists with
`param_field_access`. PROVED no conflict: building the LALR table with this rule added emits
ZERO Lark warnings (probe in §4).

### 2.2 AST node + transformer + Module5 lowering arm

- **AST node** (`Module2_Parser.py`, near `FieldSubscript` ~line 158): a dataclass
  `GlobalFieldSubscript(obj: str, field: str, index: CSLNode)`.
- **Transformer** (`Module2_Parser.py`, near `field_subscript` ~line 1508): a method
  `global_field_subscript(self, children) -> GlobalFieldSubscript` (this transformer passes
  the rule's children as a single list for this rule shape — verified in §4: unpack
  `obj, field, index = children`).
- **Dispatch + lowering** (`Module5_IREmitter.py`): register
  `GlobalFieldSubscript: "_csl_global_field_subscript"` in `_CSL_HANDLERS`
  (the table at line **236**), and add the handler beside `_csl_field_subscript`
  (line **343**). It lowers to a `Subscript` of an `Attribute` whose receiver is the
  module-global `Var` — the EXACT shape `_csl_field_access` already emits for a non-`self`
  receiver (`Module5_IREmitter.py:338-340`):

```python
def _csl_global_field_subscript(self, node):
    return {"type": "Subscript",
            "value": {"type": "Attribute",
                      "object": {"type": "Var", "name": node.obj},
                      "attr": node.field},
            "index": self._csl_to_ir(node.index)}
```

Contrast `_csl_field_subscript` (Module5:343-348), which hardcodes `FieldGet object="self"`;
the global arm is the same with an `Attribute(Var(global))` base. (gap-10's whole-field
crossing already lowers `_filesystem.disk` via `param_field_access` → `Attribute`.)

### 2.3 Module6 lowering — ALREADY PRESENT (no change needed)

The `Subscript(Attribute(Var(global), field), index)` IR composes the gap-10 global-field
projection with `Array.get`, and BOTH halves already exist in `module6_whyml/`:

- **Global-field type resolution**: `module6_whyml/types.py:232` `_field_type_of` already
  resolves an `Attribute` receiver that is a module-global instance (lines **261-265**:
  looks up `_module_global_classes[receiver]` → class → `field_types[field]`). So the
  global's array field resolves to `"list"` (etc.).
- **Spec-context `Array.get` branch**: `module6_whyml/expressions.py:1815-1817` already
  fires for `value.get("type") in ("Attribute", "FieldGet")` when `_field_type_of(value)`
  is `list`/`tuple`/`bytes`/`bytearray`, emitting `({value_str}[{index}])`.
- **Global-field projection**: `module6_whyml/expressions.py:1931-1934` (`_handle_attribute_expr`)
  already lowers `_filesystem.disk` (module-global record field) to the qualified field
  label `_filesystem.fd_inode` (gap-10's `inline.md Phase 1` mechanism).

Composed, `_filesystem.fd_inode[fd]` lowers to `(_filesystem.fd_inode[fd])` — a well-typed
logic `Array.get` against the `array int` field, exactly the wrapper-side ensures
`fstat`/`dup` need.

### 2.4 Module4 (semantic validation)

`param_field_access` / module-global field access already validates today (gap-10's
whole-field crossing is accepted by Module4). The new node is the same receiver with an
added index; the index is an ordinary expression. No new Module4 rejection is expected.
(The /tmp repro passes L1/L2/L3-tc with the new rule — §4.)

---

## 3. Byte-additivity assessment

The change fires ONLY for `<global>.<field>[expr]` in a contract — a syntax that PARSES
NOWHERE TODAY (it is a hard parse error). Therefore the full-corpus byte-diff is IDENTICAL.

Confirmed by grep over `pure_lib/`, `pure_lib_test/`, `test-suite/` for an expression-context
contract clause (`ensures|requires|assert|invariant|loop_invariant|assigns`) referencing
`<name>.<field>[`, excluding `self.` and `\result.`:
- ZERO hits in expression contracts.
- The only `<name>.<field>[` hits anywhere are two `protects` FOOTPRINT *slices* with a
  PARAM base (`test-suite/corpus/pycsl-reference/0614.py:13`, `0615.py:11`:
  `protects d.disk[512 + n*64 : 512 + (n+1)*64]`). These are (a) a different grammar
  production (footprint slice, not `?atom` subscript), (b) a SLICE (`:`), (c) on a PARAM,
  not a module-global. Untouched.

Existing shapes stay byte-identical (PROVED by coexistence probe in §4): `self.<field>[i]`
(`field_subscript`, 1100), `<param/global>.<field>` whole (`param_field_access`, 1103),
and bare `name[i]` (`subscript_access`, 1114) all parse and lower exactly as before — the
new rule only adds a previously-failing case.

os's existing contracts: they use `self.field[i]` (methods) and `_filesystem.field` whole
(gap-10); neither is `<global>.<field>[i]`, so all are unaffected.

---

## 4. Probes run (the gate evidence)

All via a monkeypatched prototype of the §2 production+transformer+lowering (NO source edits),
`src/pycsl/pycsl.py`, `.venv/bin/python3`:

1. **Repro parse-fail (HEAD, unpatched):** `_fs.x[0]` in `ensures` → `Unexpected token LSQB '['`
   (§1). Confirms the gap.
2. **Repro after fix:** `/tmp/gap15_repro.py` parses, typechecks, and the emitted `.mlw` is:
   ```
   type fs = { mutable x: array int }
   let _fs : fs = { x = (Array.make 4 0) }
   let peek () : int
     requires { (0 <= (_fs.x[0])) }
     ensures  { (result = (_fs.x[0])) }
   = _fs.x[0]
   ```
   The contract `_fs.x[0]` lowered to a real `Array.get` (`(_fs.x[0])`), well-typed against
   `x: array int`. **Postcondition `result = (_fs.x[0])` proved VALID** (Alt-Ergo, 520 steps).
   (The only Unknown is the BODY read's `Index in array bounds` VC — an honest bounds/
   no_exception obligation on the program statement `return _fs.x[0]`, orthogonal to the
   spec lowering; the contract side is fully VALID. Add a body bounds-requires or
   `#@ no_exception IndexError`-style guard in the real demo as usual.)
3. **Coexistence (`/tmp/gap15_coexist.py`):** one file mixing `_fs.y` (whole-field),
   `_fs.x[0]` (new), and `self.a[0]` (existing `field_subscript`) → `L1 ✓ L2 ✓ L3-tc ✓`,
   `Verification SUCCESS (--no-proof)`. No grammar regression.
4. **LALR build:** constructing the LALR table with the new rule added → ZERO Lark
   conflict warnings.

---

## 5. Gate (for the IMPLEMENTING turn)

1. Byte-additive: full-corpus byte-diff IDENTICAL (`bin/byte-diff-sweep.sh`) — no existing
   driver uses `<global>.<field>[expr]` (§3).
2. `/tmp/gap15_repro.py` parses + typechecks; its postcondition proves VALID.
3. Coexistence probe (§4.3) still `L3-tc ✓`.
4. Reference corpus: add a `test-suite/corpus/pycsl-reference/070X.py` exercising
   `<global>.<field>[expr]` in a contract (memory: new PyCSL features require a corpus entry).
5. Doc-coherency: this is a contract-EXPRESSION production, not a `#@` directive, so the
   directive-parity check (`bin/doc-coherency.py`) is N/A; but the concrete-syntax reference
   (`docs/pycsl-concrete-syntax-reference.md`) and the language audit
   (`pycsl-audit-pycsl-language`) should record the new `?atom` alternative.
6. (Follow-on stdlib turn) `fstat_of_opened_fd_is_valid_inode` / `dup_yields_valid_fd` in
   `pure_lib_test/formal_os_fd.py` flip Unknown→VALID once the `open`/`fstat`/`dup` wrappers
   carry the `_filesystem.fd_inode[fd]`-keyed resolution ensures (gap-15 Wall B).

---

## 6. RISKS (for judgment)

- **LEAD — localizability: YES, fully localizable.** The fix is exactly ONE grammar
  alternative (`Module2_Parser.py` ~line 1100) + ONE AST dataclass + ONE transformer method
  + ONE Module5 lowering arm (4 small additions, all additive). Module4 and ALL of Module6
  are UNCHANGED — the `Subscript(Attribute(global))` IR rides the existing gap-10 + spec-
  `Array.get` machinery (§2.3, cited file:line). It does NOT ripple into other trailer/
  subscript contexts: the new rule is a single new `?atom` alternative; no existing rule is
  edited.
- **No perturbation of `self.field[i]` or `global.field` (whole).** PROVED by the LALR-no-
  warning build (§4.4) and the coexistence probe (§4.3): `field_subscript`, `param_field_access`
  (whole), and `subscript_access` all parse/emit identically. The new production is strictly
  more specific (extra `[expr]` trailer) and LALR shifts on `[` lookahead — the same pattern
  the grammar already uses for `self.<field>` (1101) vs `self.<field>[i]` (1100).
- **Body-VC vs contract-VC distinction (minor, not a fix concern).** In the repro the
  contract clause proves VALID; an Unknown remains on the BODY's array-read bounds VC. That
  is the normal `no_exception IndexError`/bounds discipline on the program statement and is
  independent of this grammar work — the wrappers in the follow-on stdlib turn carry trusted/
  body-proved bodies as today, so this does not block the fstat/dup flip.
- **Scope boundary.** This spec covers ONLY the transpiler surface (grammar + lowering).
  The actual wrapper ensures and the `formal_os_fd.py` flip are the follow-on stdlib turn;
  no Rocq/Lean lemma is needed for Wall B (the gap report already established this — the
  missing piece is array-subscript surface, not an inductive fact).
