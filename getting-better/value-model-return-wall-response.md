# value-model-return-wall-response.md — independent review

**Reviewer:** independent (no access to the producing agents' transcripts or rationale; evidence base is
the report `value-model-return-wall.md`, the repository, and fresh oracle runs). **Date:** 2026-07-20.
**Gate R:** satisfied — 7 fresh oracle runs below, including two FULL SMT proof runs, all with commands
and outputs cited. Probe sources live in the reviewer scratchpad
(`/tmp/claude-1346829620/.../scratchpad/probe_r1_liststr.py` etc.); every command is reproducible from
the probe text quoted inline.

## Verdict summary

| Report claim | Verdict |
|---|---|
| §3.1 "`List[str]` RETURN int-erased" (common denominator of the 5-stub cluster) | **REFINE (overbroad as stated)** — the return-type printer ALREADY emits `array string`; a variable-element `List[str]` build+return **proves end-to-end today** with zero emitter changes. The real defects are two narrow ones: (a) string-LITERAL elements int-hashed into the seq, (b) the early-return exception DECLARATION typed `Seq.seq int` while raise sites emit the unbound `Return_seq_str`. Both are L3-tc-CAUGHT (loud, not silent). |
| §3.2 "[SOUNDNESS] variable-valued dict-literal `{"k": var}` DROPPED" | **CONFIRM — and it is STRONGER than reported**: a FALSE postcondition is PROVEN Valid (full SMT run below). Latent, though: the targeted grep audit finds **no** occurrence in the verified reference corpus or `src/pycsl_lib/`. |
| §3.3 nested-return paren bug | **CONFIRM exactly** (`map string (option map int (option int))`, Why3 rejects; the LOCAL-decl printer parenthesizes the same type correctly, so the bug is isolated to the return-type printer path). |
| §7 make-or-break: is R1 a bounded fix? | **CONFIRM feasibility, REFINE cost downward** — R1 is not merely bounded; most of it is already built and proving. The genuinely missing piece for `_extract_generic_arg_names` is one printer gap (the `Return_seq_str` exception declaration), plus the literal-hash fix if literals are ever appended. |

---

## 1. Oracle runs — §7 / R1: faithful `List[str]` RETURN typing

### 1a. Plain function, literal element (probe_r1_liststr.py)
`def f(n: int) -> List[str]: r = []; while i < n: r.append("x"); return r` with
`requires n >= 0 / ensures True / assigns \nothing` + loop invariant/variant.

```
$ python3 src/pycsl/pycsl.py probe_r1_liststr.py --import-path src/pycsl --no-proof --keep-mlw
[level] L1 ✓  L2 ✓  L3-tc ✗
File "probe_r1_liststr.mlw", line 28: This expression has type seq.Seq.seq int,
but is expected to have type seq.Seq.seq string
```

Emitted `.mlw` (relevant lines):
```
let f (n: int) : array string          (* <-- return type is NOT int-erased *)
  ...
  let r = ref Seq.empty in
  while (!i < n) do
    r := Seq.snoc !r 976090257;        (* <-- the literal "x" is int-HASHED *)
  done;
  (materialize_str !r)                 (* seq string -> array string bridge, with element-wise ensures *)
```

**Finding:** the return-type printer already emits `array string`, and the `materialize_str` tail
(`ensures result[i] = Seq.get s i`) already exists. The defect is the ELEMENT lowering of a string
LITERAL: it routes through the literal→int coercion (`_coerce_str_arg` /
`stable_hash`, `src/pycsl/module6_whyml/expressions.py:473-477`,
`src/pycsl/module6_whyml/identifiers.py:8` — "Convert a WhyML string literal to an int hash"),
yielding `seq int` vs `seq string`. Annotating the local (`r: List[str] = []`, probe_r1b) does NOT
change this — the coercion is per-element, not inference-driven.

### 1b. Plain function, VARIABLE element (probe_r1c_varappend.py) — FULL PROOF
Same shape but `r.append(s)` with `s: str` a parameter.

```
$ python3 src/pycsl/pycsl.py probe_r1c_varappend.py --import-path src/pycsl --no-proof --keep-mlw
[level] L1 ✓  L2 ✓  L3-tc ✓
$ python3 src/pycsl/pycsl.py probe_r1c_varappend.py --import-path src/pycsl        # full proof
[+] Verification SUCCESS! All contracts formally proven.
```
Emission: `let f (n: int) (s: string) : array string` ... `r := Seq.snoc !r s` ... `materialize_str !r`.

**Finding:** a faithful `List[str]` return with variable elements verifies END-TO-END with the tool AS
IT IS. No hand `.mlw` was needed to establish Why3-representability — the live tool's own emission is
the witness, and Why3 proves it.

### 1c. Class METHOD returning `List[str]` (probe_r1d_method.py)
```
[level] L1 ✓  L2 ✓  L3-tc ✓
let c__names (self: c) (s: string) : array string = ... Seq.snoc !r s ... materialize_str !r
```
**Finding:** the method-return path is ALSO faithful — no "variant arm payload `Arm_k_0 int`" appears.
The `Arm_*` machinery the report cites is the per-function OPTIONAL-local union
(`src/pycsl/module6_whyml/statements.py:73-111`: `_union_<fn>_<idx> = Arm_<idx>_0 τ | Arm_<idx>_None`).
That machinery is where int-erasure of a `List[τ]` payload can occur — i.e. it is the wall for
`_collect_union_arms` (`Optional[List[emit_ir]]`), NOT for plain `List[str]` returns. The report
conflates the two.

### 1d. The stub's EXACT shape — early returns `return [s]` / `return []` (probe_r1e_stubshape.py)
`def f(flag: bool, s: str) -> List[str]: if flag: return [s]; return []`

```
[level] L1 ✓  L2 ✓  L3-tc ✗
File "probe_r1e_stubshape.mlw", line 23: unbound exception symbol 'Return_seq_str'
```
Emission:
```
exception Return_seq (Seq.seq int)                       (* declaration: INT-typed, wrong name *)
...
raise (Return_seq_str (Seq.cons s Seq.empty))            (* raise sites: element-typed, CORRECT *)
raise (Return_seq_str Seq.empty)
with Return_seq_str s -> materialize_str s end
```
**Finding — this is the single concrete blocker for the first target.** The raise sites and the handler
already speak `Return_seq_str : Seq.seq string`; only the exception-DECLARATION printer still emits the
legacy int-typed `Return_seq`. `_extract_generic_arg_names` uses exactly this multi-return shape
(`return [slice_node.id]` / `return names` / `return []`), so this one declaration fix is the R1
make-or-break in practice — far narrower than "make the return-type printer emit array/seq element"
(that part is already done).

## 2. Oracle runs — §3.2: the dict-literal drop (SOUNDNESS)

### 2a. Emission (probe_s32_dictdrop.py)
`def g(bound: int) -> int: d = {"bound": bound}; return d["bound"]`
```
$ python3 src/pycsl/pycsl.py probe_s32_dictdrop.py --import-path src/pycsl --no-proof --keep-mlw
[level] L1 ✓  L2 ✓  L3-tc ✓        (* silently accepted *)
```
Emission:
```
let g (bound: int) : int =
  let d = ref (const (None: option int)) in                     (* EMPTY map; entry never built *)
  (match Map.get !d "bound" with | Some v_ -> v_ | None -> 0 end)
```
**CONFIRMED:** the `"bound": bound` entry is dropped; `bound` is unused; the read defaults to 0.

### 2b. False-postcondition proof (probe_s32b_false.py) — FULL PROOF
Same body, contract `#@ ensures \result == 0`. Real Python: `g(7) == 7`, so the postcondition is FALSE.
```
$ python3 src/pycsl/pycsl.py probe_s32b_false.py --import-path src/pycsl --keep-mlw
Sub-goal postcondition of goal g'vc.  Prover result is: Valid (0.01s, 616 steps).
Warning, ... line 10: unused variable bound
[+] Verification SUCCESS! All contracts formally proven.
```
**The soundness concern is CONFIRMED at full strength: PyCSL formally proves a false statement about a
7-line program.** (Why3's own "unused variable bound" warning is a tell — a cheap lint opportunity.)

### 2c. Targeted audit — does it poison anything VERIFIED?
- `grep -nE '\{["...][A-Za-z_]+["...]\s*:\s*[a-z_...]' test-suite/corpus/pycsl-reference/*.py`
  (excluding literal/None/bool/numeric values): **no matches** in the 900-file corpus.
- Same grep over `src/pycsl_lib/`: **no matches**.
- The self-annotate mirror DOES contain verified (non-`\trusted`) bodies building `{"type": "Forall",
  "var": node.var, ...}` (`src/self-annotate/src/frontend/Module5_IREmitter.py:192,213,254,334`), BUT
  their comments state they lower via the IR-node-ADT recognizer path ("lowers to `(IrForall node.var
  ...)`... NO dropped field"), not via the raw dict-literal emission, and their contracts are the
  type-safety shape (`ensures True`). **Residual audit item:** confirm the recognizer actually
  intercepts ALL such sites (a site the recognizer misses would silently fall through to the empty-map
  path); I did not exhaustively verify recognizer coverage.

**Net:** confirmed soundness hole, currently latent (no verified corpus/lib program exercises it). It
should be closed or turned into a hard REJECT (refuse to emit) — a loud L-level error is a much smaller
fix than faithful construction and removes the facade risk immediately.

## 3. Oracle run — §3.3 paren bug (probe_r2_nesteddict.py)
`def h() -> Dict[str, Dict[int, int]]: d: Dict[str, Dict[int,int]] = {}; return d`
```
[level] L1 ✓  L2 ✓  L3-tc ✗
File "probe_r2_nesteddict.mlw", line 10: Type symbol map expects 2 arguments but is applied to 0
let h () : map string (option map int (option int))      (* return printer: parens MISSING *)
  let d = ref (const (None: option (map int (option int)))) in   (* local printer: CORRECT *)
```
**CONFIRMED exactly**, with the useful refinement that the local-declaration printer already
parenthesizes the identical type correctly — the fix is one code path in the return-type printer.

## 4. Independent verdict on route R1

**Is it the right make-or-break?** Yes in target, no in description. Converting
`_extract_generic_arg_names` IS the correct cleanest first increment. But the report's R1 work items
("make the return-type printer emit array/seq element, and the list-build lower to a real element-typed
seq") are ~80% ALREADY IMPLEMENTED and proving (oracles 1b/1c). The actual remaining work is:

1. **The `Return_seq_str` exception declaration** (oracle 1d) — the declaration printer must emit
   `exception Return_seq_str (Seq.seq string)` when a function's early-return machinery carries a
   string seq (the raise/handler sites already do). This is THE blocker for the stub's multi-return
   body shape.
2. **String-literal element int-hash** (oracle 1a; `_coerce_str_arg`/`stable_hash`) — needed only if a
   converted body appends string LITERALS. `_extract_generic_arg_names` appends `slice_node.id` /
   `elt.id` (variables via `name_of`), so this may not even block the first target — but it will bite
   the next collectors (e.g. `_collect_typevar_registry`'s `"bound"` values) and is the same
   no-more-int leak class, worth fixing in the same pass.

**Hidden second blocker check (mirror side):** I read the live body
(`src/pycsl/frontend/Module5_IREmitter.py:1906-1917`) and the mirror context. The body needs
`isinstance(_, ast.Name)`/`ast.Tuple` dispatch, `.id`, and `.elts` iteration. All of that machinery
exists and is exercised by ALREADY-CONVERTED mirror bodies: `is_tuple`/`is_var`
(`module6_whyml/preamble.py:3653`), `elts_of : emit_ir -> irlist` (`preamble.py:4500`), `name_of`
projection over elts irlists (mirror comments at `self-annotate/.../Module5_IREmitter.py:1393-1394`,
`1671-1673` — an existing converted body even loops `for elt in inner.elts` projecting `name_of`).
So I find **no hidden AST-modeling blocker**; the report's "no other blockers" for this stub stands,
MODULO the exception-declaration gap my oracle exposed (which the report did not name — it is the
concrete content of its own R1).

**One caution:** prior conversions COMPACTED name collections into pipe-joined strings
(`pipe_join (elts_of t)`) precisely because list-of-string returns were believed walled. After R1 the
first faithful `List[str]`-returning conversion should include the anti-facade mutation test the
project already uses (change the body → the `.mlw` must change), and the byte-diff-0 sweep. Since any
current corpus file hitting the broken paths fails L3-tc (loud), a fix that only ADDS the `_str`
declaration variant is plausibly byte-inert on the passing corpus — but that must be gated, not assumed.

## 5. Over-scope / under-scope in the report

- **Over-scope (§2/§3.1):** "the emitter int-erases `List[τ]` ... RETURN types, so a method that builds
  and returns such a value cannot be lowered faithfully" is contradicted by oracle 1b/1c — such a
  method IS lowered faithfully and PROVEN today when elements are variables and returns are tail
  returns. The cluster's "common denominator" framing is therefore too strong; what the five stubs
  actually share is a mixed bag: the exception-decl gap (this fix), the literal-hash leak (small), the
  Optional-union arm erasure (`_collect_union_arms` — a genuinely different, deferred wall), and the
  dict construction drop (R3).
- **Under-scope (§3.2):** the report undersells its own soundness finding — it is not merely a
  "consistent-but-wrong lowering"; it is a demonstrated false-theorem generator (oracle 2b). Conversely
  the report's fear about the verified corpus is over-cautious: the audit (2c) comes back clean.
- **Correctly scoped:** R2 (paren fix) is exactly as small and isolated as claimed; the deferral of
  reflection/`ast.walk`/worklist sub-walls is right; "any new value shape co-lands an axiom-free cert,
  ledger stays 3" is the right discipline (my probes added no axioms — the existing `materialize_str`
  val is a pre-existing specified abstraction, not a new one).

## 6. Recommendation

**PROCEED to an impl plan for R1, re-scoped to what the oracles pinpoint**, in this order:

1. **R1a (make-or-break, tiny):** emit the `Return_seq_str (Seq.seq string)` exception DECLARATION
   where the early-return machinery already raises it (probe_r1e is the ready-made regression test:
   L3-tc ✗ → ✓ → full proof). Gate: byte-diff-0 sweep + the probe.
2. **R1b:** fix the string-literal element int-hash in seq/list-build context (probe_r1 line 25:
   `Seq.snoc !r 976090257` → `Seq.snoc !r "x"`). Gate: same.
3. **Convert `_extract_generic_arg_names`** in the mirror using the existing
   `is_var`/`is_tuple`/`name_of`/`elts_of` machinery; apply the mutation test.
4. **R2** (paren fix in the return-type printer) — independent, can land any time.
5. **§3.2 as a standalone SOUNDNESS ticket, not part of R1:** short-term, make variable-valued
   dict-literal emission a hard L-level REJECT (loud failure kills the false-theorem generator
   immediately); the faithful construction (R3) can follow. Add a recognizer-coverage check for the
   mirror's `{"k": var}` sites.

No oracle I needed was unavailable: `pycsl.py` (emission, L3-tc, and full Why3/SMT proof paths) ran on
every probe; full proofs used the default prover pipeline successfully, so separate hand
`why3 prove -P alt-ergo` runs were unnecessary (the tool's own Valid outputs are quoted above). I did
not run `bin/byte-diff-sweep.sh` since I changed no source — nothing to sweep.
