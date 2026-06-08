# b-impl.md — Implementation of Track B (opaque-on-export + `#@ reveal`)

**Date:** 2026-06-08
**Status:** Implementation plan (concrete; maps `b-spec.md` P0–P5 to file:line code changes — no code
written yet)
**Spec:** `b-spec.md` (rev. 2). **Umbrella:** `opaque-and-refine-rev2.md`. **Probes:**
`challenging-the-plan.md` / `challenging-the-plan2.md` (A reduces to B).
**Owner:** [TOOL] `src/pycsl/**`; [STDLIB] consumes at P4.

This document is the *how* for `b-spec.md`'s *what*. It is grounded in the real pipeline: every change
below cites a file:line and the existing analogue (`#@ no_inline`, `#@ lemma`, `#@ uses`, `#@ \abstract`)
it mirrors.

---

## 0. Architecture: the one line that fixes wall #3 (and what stays unchanged)

The bloat (`try.md` §3.7) is concrete and the fix is local. When `os/__init__.py` imports
`_pack_inode`, the import resolver injects it as a **trusted stub** and Module6 emits it as a `val`
**carrying its full contract**:

- **Import injection:** `pycsl.py::_inject_functions` (line 197) inserts dependency funcs into the
  consumer's IR; `_resolve_direct_imports` (line 211) prints "(trusted stubs)" (line 254). The injected
  `_pack_inode` IR carries its **definition** contract (19 ensures).
- **`val` emission:** `module6_whyml/functions.py` — `emit_as_val = func_trusted or func_abstract`
  (line 365); `if emit_as_val: kw = f"val {name}"` (line 402); `_emit_contracts(...)` (line 426) emits
  **all** ensures onto the stub; early-return (line 429). **This stub, at 8 call sites, is the bloat.**

**B's core change is one decision at line 426:** *if the function carries an `#@ interface` contract,
emit the interface clauses on the `val` stub instead of the definition clauses.* Everything else is
plumbing to (a) carry the interface contract to that point, (b) prove the narrowing in the owning unit,
and (c) optionally `#@ reveal` the definition at a chosen caller.

**The decisive simplification (from the probe analysis).** `_pack_inode`, `_read_inode`,
`_write_inode`, and any round-trip lemma all live in the **owning unit** (`UnixInodeFileSystem.py`),
where `_pack_inode` is a real `let` with its full contract **visible** — so *no opacity is needed within
the owning unit* (the round-trip / refinement consumer sees the definition directly). Opacity is only
needed at the **import boundary** into `os/__init__.py`, whose 8 syscalls prove *return codes* and do
**not** reveal. Therefore:

| Mechanism | Where | Effort |
|---|---|---|
| Interface on the imported/abstract `val` stub | the import boundary into os | **the core P1–P4 work** |
| Narrowing VC (`definition ⟹ interface`) | the **owning** unit (real `let`) | P2 |
| `#@ reveal` **within** the owning unit | trivial — the definition is already the `let`'s contract | free |
| `#@ reveal` **across** modules (an os caller wanting the 18 fields) | a def-fact lemma imported as a fact | **deferred to P5/v2** — not needed for the 23 |

This means **the near-term win (os light, held at 23) needs only P0–P4 with interface-on-stub; the
cross-module reveal — the genuinely hard part — is not on the critical path.**

---

## 1. Data model (ir_schema + weaver + Module5)

### 1.1 `ir_schema.py` — carry the interface contract and the reveal set
`ContractsIR` (lines 25–36) and `FunctionIR` (lines 38–56). Add:

```python
class FunctionIR(TypedDict, total=False):
    contracts: ContractsIR          # existing — the DEFINITION (verified vs body, unchanged)
    interface: ContractsIR          # NEW — the narrow contract importers see (absent ⇒ = contracts)
    reveal: List[str]               # NEW — fns whose DEFINITION this function opts into
```
`interface` reuses the `ContractsIR` shape (requires/ensures/assigns). **Absent `interface` ⇒
interface = definition** — the byte-identical-corpus invariant (`b-spec.md` §9) is *structural*: code
paths only diverge when `interface` is present.

### 1.2 `Module2_Parser.py` — two new directives (mirror `no_inline` / `uses`)
- **`#@ interface <clause>`** — a clause-set parallel to `requires`/`ensures`/`assigns`. Grammar near
  line 924 (the `no_inline_decl` / `lemma_decl` block); a clause carries a kind tag and an expression,
  e.g. `interface ensures \length(\result) == 64`. New dataclass `InterfaceClause(kind, expr)` (beside
  `NoInline` line 272). It is **not** an alternative of the plain contract rule — it is its own clause so
  definition and interface never collide.
- **`#@ reveal <fn>`** — exactly models `#@ uses <fn>` (line 928, `uses_decl` line 1252, `Uses` line
  307). New `Reveal(fn)` dataclass; grammar rule `reveal_decl: "reveal" CNAME`.

### 1.3 `Module3_Weaver.py` — attach to the AST node (mirror lines 208–221)
```python
elif isinstance(c, InterfaceClause):                 # beside csl_no_inline (line 208)
    node.csl_interface.setdefault(c.kind, []).append(c.expr)   # {"ensures":[...], "assigns":[...]}
elif isinstance(c, Reveal):                          # beside csl_uses
    node.csl_reveal.append(c.fn)
```
Initialise `node.csl_interface = {}` and `node.csl_reveal = []` beside `node.csl_abstract = False`
(line 53).

### 1.4 `Module5_IREmitter.py` — emit into the IR dict (mirror lines 1556–1575)
```python
"interface": dict(getattr(node, 'csl_interface', {}) or {}),   # beside "no_inline" (1556)
"reveal":    list(getattr(node, 'csl_reveal', []) or []),      # beside "uses" (1563)
```
**Import propagation (critical):** `_inject_functions` (`pycsl.py` line 205) inserts the *whole* dep
func IR — so the injected `_pack_inode` already carries `interface` once the source has it. No change to
the injector; the data rides along.

---

## 2. P0 — the emission shape (the one design decision to validate first)

Goal: a hand-written `.mlw` exhibiting *narrow on import, rich + proven in the owning unit*. Recommended
shape (validated against Why3 before any tool code):

**Owning unit (`UnixInodeFileSystem.mlw`) — unchanged `let` + a new narrowing goal:**
```whyml
  let _pack_inode (fields: array int) : array int
    requires { Array.length fields >= 18 }
    ensures  { Array.length result = 64 }
    ensures  { result[0]*16777216 + ... = fields[0] }   (* + 17 more — the DEFINITION, verified *)
  = <body>                                               (* leaf-compositional, try.md §3.6 *)

  goal _pack_inode__narrows :                            (* P2: definition ⟹ interface *)
    forall fields: array int, r: array int.
      Array.length fields >= 18 ->                       (* requires  *)
      (Array.length r = 64 /\ r[0]*16777216 + ... = fields[0] /\ ...) ->   (* DEFINITION ensures *)
      (Array.length r = 64)                              (* INTERFACE ensures *)
```

**Consuming unit (`os/__init__.mlw`) — the stub carries only the interface:**
```whyml
  val _pack_inode (fields: array int) : array int
    requires { Array.length fields >= 18 }
    ensures  { Array.length result = 64 }                (* INTERFACE only — 1 fact, not 19 *)
```

P0 confirms: (a) the `goal` form discharges (interface ⊑ definition), (b) the narrow `val` lets the 8
syscalls prove (they only need `\length`), (c) no Why3 well-formedness issue. **If P0 shows Why3 cannot
carry the split, stop — no module changes (b-spec §8 fail-safe).** (Expected to pass: this is just "a
goal + a weaker val," both ordinary Why3.)

---

## 3. P1 — parse `#@ interface`; default interface = definition (byte-diff gate)

Wire §1.2–§1.4. The only behavioural rule: **`interface` empty ⇒ use `contracts` verbatim everywhere**
(the existing path). Gate: full `bin/run-reference-tests.sh --pycsl` **byte-identical** (no file has
`#@ interface` yet, so every `.mlw` is unchanged). This proves opt-in safety before any emission logic
changes.

## 4. P2 — the narrowing VC (`definition ⊑ interface`), fail-loud

New method in `module6_whyml/functions.py` (after `_emit_contracts`, line ~306), emitted **only in the
owning unit** (where the function is a `let`, i.e. `not emit_as_val`) and **only when `interface` is
present**:

```python
def _emit_narrowing_vc(self, name, params, ret_ty, definition, interface, spec_refs):
    """b-spec §4: a Why3 `goal` that the interface is a sound weakening of the definition.
       ensures:  def_post ⟹ iface_post   (interface promises less)
       assigns:  def_assigns ⊆ iface_assigns
       requires: iface_pre  ⟹ def_pre
       Fail-loud: if the goal does not discharge, the interface over-claims → rejected."""
    # bind \result as a fresh `r` of ret_ty; emit each clause with _result_alias = "r"
    qs = " ".join(f"({p}: {t})" for p, t in params) + f" (r: {ret_ty})"
    hyp_req = _conj(definition.get("requires", []))      # def requires
    hyp_def = _conj(definition.get("ensures",  []))      # def ensures (the proven facts)
    for ie in interface.get("ensures", []):
        body = f"({hyp_req}) -> ({hyp_def}) -> ({self._expr_to_whyml(ie, spec_refs)})"
        lines.append(f"  goal {name}__narrows_ens_{k} : forall {qs}. {body}")
    # requires direction (iface_pre ⟹ def_pre) and assigns ⊆ symmetric goals likewise
```

Key detail — **`\result` binding.** In an `ensures`, `\result` lowers to Why3's `result`; in a `goal`
there is no bound `result`, so set a context alias (`self._result_alias = "r"`) around the clause
emission and have `_handle_result` honour it (a 2-line branch beside the L0 `Result` early-return in
`expressions.py:1594`). This reuses the L0/L0′ machinery (array-result `r[i]` already lowers to
`Array.get`).

Emission site: in `_emit_function`, after the body/`let` is closed (line ~431, the `let` branch), append
`_emit_narrowing_vc(...)` when `func.get("interface")`.

Gates: **[PROVE]** a sound narrowing (`(\length=64 ∧ 18 fields) ⟹ \length=64`) discharges; **[PROVE-neg]**
a driver whose `#@ interface ensures \result[0] == 7` (a fact the definition does *not* prove) makes the
goal **fail** → the build reports the function rejected. The neg driver is a new corpus test (e.g.
`0660-neg`) asserted to FAIL.

## 5. P3 — interface on the stub; `#@ reveal` restores the definition

### 5.1 Interface on the `val` stub — the wall-#3 fix
In `_emit_function` (`functions.py`), at the `emit_as_val` contract emission (line 426), select the
clause source:

```python
contract_src = func.get("interface") if (emit_as_val and func.get("interface")) else func.get("contracts", {})
lines += self._emit_contracts(contract_src, spec_refs, func_variants, func_diverges, func_exceptions)
```

So an imported/abstract `_pack_inode` whose source has `#@ interface ensures \length==64` emits a `val`
with **one** ensures. The 8 os syscalls now carry 1 fact, not 19. (The owning unit's `let` is untouched —
`emit_as_val` is False there, so it keeps the full definition + the body + the narrowing goal.)

### 5.2 `#@ reveal` — within-unit (free) and cross-module (deferred)
- **Within the owning unit:** a `#@ reveal _pack_inode` caller is in the same module where `_pack_inode`
  is a `let` with the full definition contract — Why3 already sees it. `reveal` here is a **no-op for
  emission** (the definition facts are in scope); it exists only as documentation/intent. This covers the
  round-trip / refinement consumer (`b-spec` §2(i)/(ii), all in `UnixInodeFileSystem.py`).
- **Cross-module (an `os/__init__` caller wanting the 18 fields):** the stub there carries only the
  interface. To reveal, emit in the **owning** unit a definition-fact lemma
  `lemma _pack_inode__def : forall fields. Array.length fields >= 18 -> <def_ensures>[(_pack_inode fields)/r]`
  (proven trivially from the `let`'s own contract), and have the importer pull it in as a `use`d fact;
  the `#@ reveal` caller then `#@ uses _pack_inode__def`. This needs cross-module lemma export — which
  PyCSL's importer (`_inject_functions`) does not do today — so it is **deferred to P5/v2**. It is **not
  needed for the os 23** (return codes don't use field values), per §0.

This is exactly `b-spec` §2: (i) reveal-and-compose = within-unit reveal; (ii) lemma-over-the-definition
= the deferred cross-module path.

## 6. P4 — apply to `_pack_inode`

1. Source: keep `_pack_inode`'s **definition** = the 18-field leaf-compositional contract (`try.md`
   §3.6); add `#@ interface ensures \length(\result) == 64`. Its body already proves the definition
   standalone.
2. Owning unit: the narrowing goal `_pack_inode__narrows` discharges (P2); the `let` + body + 18 fields
   verify (unchanged from `try.md` §3.6's standalone success).
3. os/__init__: the injected `val _pack_inode` now carries only `\length == 64`.

**Gates (the headline):** **[byte-diff]** os's 8 syscall `.mlw` bodies are byte-identical to today (they
saw `\length` before — via the *old full* contract the solver ignored the rest; now they see *only*
`\length`, so the proof obligations are identical or fewer) and **os holds at 23**; **[measure]** the os
`val _pack_inode` has 1 ensures, not 19; **[PROVE]** a within-unit `#@ reveal` read-back client
(`_read_inode(_write_inode(n, I)) == I` or a field of it) proves using the visible definition — the
concrete discharge of "the round-trip is established on top of B" (`b-spec` §11.5, via §2(i)).
Full corpus + `formal_0001` 18/18 + stdlib-coverage + doc-coherency green.

> **Note on the "os held at 23" claim.** Today os's `val _pack_inode` carries 19 ensures and os still
> reaches 23 (the bloat was the *1700s with the leaf-compositional definition*, not the light one). The
> measurable B win is **the contract on the stub drops 19→1** and the path to *adding* the rich
> definition (in the owning unit) without ever paying for it in os. P4's byte-diff confirms no
> regression; the strategic win is that the rich definition can now coexist with a light os.

## 7. P5 — generalize + (optionally) cross-module reveal

- Apply `#@ interface` to `_pack_direntry`/`_unpack_*` and any other rich-contract function imported
  into a light consumer; each application byte-diff-gated.
- **(v2)** Cross-module reveal: teach `_inject_functions` to also export a function's
  `<fn>__def` lemma (proven in the owning unit) so an importer can `#@ reveal`/`#@ uses` it. This is the
  only genuinely new cross-module machinery and is deferred until a consumer actually needs field facts.

---

## 8. Touch-point summary (the whole change, by file)

| File | Change | Mirrors |
|---|---|---|
| `ir_schema.py` 38–56 | add `interface: ContractsIR`, `reveal: List[str]` to `FunctionIR` | `contracts`, `uses` |
| `Module2_Parser.py` ~924/928, ~272/307 | `interface_clause` + `reveal_decl` rules; `InterfaceClause`, `Reveal` dataclasses | `no_inline_decl`, `uses_decl` |
| `Module3_Weaver.py` 53, 208–221 | init + attach `csl_interface`, `csl_reveal` | `csl_no_inline`, `csl_uses` |
| `Module5_IREmitter.py` 1556–1575 | emit `"interface"`, `"reveal"` IR keys | `"no_inline"`, `"uses"` |
| `module6_whyml/functions.py` 426 | **select interface clauses for the `val` stub** (the core fix) | `_emit_contracts` call |
| `module6_whyml/functions.py` ~306/431 | new `_emit_narrowing_vc`; call it for `let`s with `interface` | `_emit_contracts` |
| `module6_whyml/expressions.py` ~1594 | `_result_alias` branch (bind `\result` to `r` in the narrowing goal) | the L0 `Result` early-return |
| `pycsl.py` 197–256 | (P5/v2 only) export `<fn>__def` lemma for cross-module reveal | `_inject_functions` |

**No change** to: the body verification (definition proves exactly as today), the inliner
(`ir_inline.py`), the import injector for the near-term path, or any function lacking `#@ interface`.

## 9. Soundness & gating (per b-spec §8–§9)

- **No TCB growth.** Definition verified against the body (status quo); interface proven a weakening (P2
  goal); within-unit reveal uses the already-proven `let` contract. The only *assumed* artefact is the
  P5/v2 cross-module `<fn>__def` lemma — and it is **proven in the owning unit** before being imported,
  so it is a `use` of a theorem, not an axiom (a ledger note records the import edge).
- **Fail-loud.** An over-claiming `#@ interface` fails `_pack_inode__narrows` → function rejected (the
  P2 PROVE-neg driver locks this in). A false definition fails the body's own proof (unchanged).
- **Opt-in / byte-identical.** No `#@ interface` ⇒ `contract_src == func["contracts"]` ⇒ every existing
  `.mlw` unchanged (P1 byte-diff gate). os held at 23 (P4 byte-diff gate).

## 10. Risks & open questions

1. **P0 emission shape** — the recommended "narrow `val` + owning-unit `goal`" is ordinary Why3; the
   only risk is if PyCSL's import injector strips/normalizes contracts in a way that drops the interface
   selection. Mitigation: P0 is hand-`.mlw` first; P1 byte-diff catches any injector interaction.
2. **`\result` binding in the narrowing goal** — must alias `\result`→`r` cleanly, including the
   array-result `r[i]` (reuse L0/L0′). Risk low; it's the same code path.
3. **assigns/requires narrowing directions** — §4 emits all three directions; the codec case is
   `\nothing`/equal, so trivial, but the PROVE-neg driver should also cover a wrong-direction `assigns`
   to lock the soundness of the non-ensures clauses.
4. **Cross-module reveal (P5/v2)** — the one piece needing new importer machinery; explicitly off the
   near-term critical path. If a content-level os spec (Track C territory) ever needs field facts in
   `os/__init__`, this is where it lands — and at that point the §3 trade-off vs C (refinement) should be
   re-evaluated.
5. **Does B alone deliver a *visible* win for the inode case?** Honest answer (per §6 note): the
   immediate, measurable win is contract-on-stub 19→1 and the *capability* to carry the rich definition
   without os cost; the *consumer* of that capability (a content-level syscall spec) is Track C. B is the
   substrate that makes C affordable later — and the general fix for every imported rich contract — but a
   reviewer should know B-without-C does not by itself prove a new os property. (This mirrors the
   umbrella's "name the consumer" open point.)

## 11. Phasing → gates (mirrors b-spec §10)

| Phase | Deliverable | Gate |
|---|---|---|
| **P0** | hand `.mlw`: narrow `val` + owning-unit narrowing `goal` | both present; goal discharges; syscall-shaped caller proves with narrow `val` |
| **P1** | parse `#@ interface`/`#@ reveal`; default interface = definition | **[byte-diff]** whole corpus identical |
| **P2** | `_emit_narrowing_vc`; fail-loud | **[PROVE]** sound narrowing; **[PROVE-neg]** over-claim rejected (driver `0660-neg`) |
| **P3** | interface on `val` stub; within-unit `#@ reveal` | **[PROVE]** revealing caller sees definition; **[measure]** non-revealing stub carries interface only |
| **P4** | apply to `_pack_inode` | **[byte-diff]** os 8 syscalls unchanged, **held at 23**; **[measure]** stub 19→1 ensures; **[PROVE]** within-unit read-back/round-trip client |
| **P5** | generalize; (v2) cross-module reveal lemma export | corpus PASS; each application byte-diff-gated |

## 12. Implementation findings (what running P0–P4 revealed)

**P0–P3 landed and are validated.** P0 (Why3 shape) discharges + over-claim → Unknown. P1 parses
`#@ interface`/`#@ reveal`, corpus byte-clean. P2's narrowing VC proves for a sound narrowing and
**rejects an over-claim** (`#@ interface ensures \result[0] == 7` fails `pack16__narrows_ens_0` —
fail-loud). P3 emits the interface on the import `val` stub (os `_pack_inode` stub: **1 ensures, not
19**). Driver 0660 proves. **The B feature works and is sound.**

**P4 surfaced a residual the spec did not foresee — the `requires`-side bloat.** Giving `_pack_inode`
its rich 18-field definition + `#@ interface ensures \length==64` narrowed the *ensures* on the os stub
(1, confirmed by byte-diff) — but the interface **inherited the definition's 18 field-range `requires`**
(`0 <= fields[k] <= MAX`), which `_pack_inode` genuinely needs to call its value-contracted leaves
(`_pack_uint32_be` requires `0 <= v <= 2³²-1`). Those 18 `requires` then ride all 8 syscall call sites
(each caller must discharge them), and **os timed out (>1200s, run alone — not CPU load)**. So:

> **B narrows `ensures` soundly, but it cannot soundly narrow these `requires`.** The narrowing VC
> correctly *would reject* `#@ interface requires \valid(fields,18)` — `\valid ⟹ (\valid ∧ 18 ranges)`
> is false (fail-loud, §4 requires-direction). Dropping the ranges is unsound because the body needs
> them. So applying B to `_pack_inode` *trades* the ensures-bloat for a requires-bloat; **os does not
> reach 23 via B alone.**

**The real fix for the inode case is below B — a leaf restructure (call it L1′).** Make the byte leaves
*total*: `_pack_uintN_be` requires **nothing**, ensures `\length == N` unconditionally, and makes the
value reconstruction **conditional** on the range (`0 <= v <= MAX -> \result[0]*… == v`). Then
`_pack_inode` calls them with no precondition → its definition requires only `\valid(fields,18)` → the
interface (`requires \valid`, `ensures \length==64`) is a sound consequence (no field-range requires to
inherit) → the 8 syscalls carry **1 require + 1 ensure**, and os holds at 23 with the round-trip
established in the owning unit. **L1′ is the prerequisite for P4; B is necessary but not sufficient for
`_pack_inode` without it.** (This is the same "totalize the leaf so the composer needs no precondition"
move as the leaf-compositional `try.md` §3.6 fix, applied to the precondition side.)

**Committed:** the B feature (P0–P3) + driver 0660; `_pack_inode` reverted to its committed light
contract (os holds at 23). P4 is **parked on L1′** — a distinct, scoped follow-on, not a defect in B.

> **In one line:** B is implemented by adding an `interface: ContractsIR` to `FunctionIR` (parsed like
> `#@ no_inline`, woven like `#@ uses`), selecting those clauses at the single `val`-stub contract
> emission (`functions.py:426`) so an imported `_pack_inode` shows `\length == 64` to os's 8 syscalls
> instead of 19 ensures, and emitting a `goal _pack_inode__narrows` in the owning unit (`definition ⟹
> interface`, fail-loud on over-claim) so the narrowing is *proven*. Within-unit `#@ reveal` is free (the
> definition is the real `let`); cross-module reveal (a def-fact lemma export) is deferred to v2 and is
> off the critical path because os's return-code proofs never need the field values.
