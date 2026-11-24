# Run #9 u74 report: `_to_cache_payload` converted; `parse_format` and `bases_closure` measured

Executor u74, driver run #9, self-tcb-reduction base loop.

- Branch `run9-u74` in `/home/fabrice/git/pycsl-u74`. Base = `run9-u67` **96eac515d** (main L20 + the u67 type_of_batch conversion). `ghost-assign-bc6` had no `src`/`bin`/`test-suite` change past the base when checked (15:00Z), and `main` (f552646c4) is already contained, so no merge was needed.
- Base tree (detached at 96eac515d): `/home/fabrice/git/pycsl-u74b`. Head snapshot tree: `/home/fabrice/git/pycsl-u74h`.
- Paths are relative to `scratchpad/u74/` unless absolute. Never pushed.

__STATUS__

## 1. Measured chains (QUICK `--no-proof` probes of scratch copies; `probe.sh`, variants `v/*.py`, logs `v/*.log`)

All three chains were walked at the base before anything was built. Every probe passes `--verification-image`.

### 1.1 `_to_cache_payload` (audit_proof_reverify.py): 4 links + 1 free [T]. CLOSED, converted.

| step | variant | verdict |
|---|---|---|
| verbatim port (marker dropped) | `c0` | L3-TC: bare `-> dict` is `map int (option int)`; `HStr`-less string values (`string` vs `int`) |
| [T] live+mirror return annotation `-> Dict[str, PyVal]` (runtime-inert under `from __future__ import annotations`; the `PyVal` sentinel as in Module5) | `c1` | L3-TC: `HInt report.elapsed_compile_s` (`real` vs `int`) = **link 1** |
| — after link 1 | — | TC-OK but a FACADE (cv15): `"qualname_results"` is `HInt (list_comp 0)`, input-blind. The field `qualname_results: List[tuple[str, bool, List[str]]]` is `array int` = **link 2a**; the tuple target `(qn, ok, axs)` is erased to `_comp_var` in the IR = **link 2b**; the comprehension in hval position = **link 2c** |
| all four links | `c2` | **TC-OK**, faithful (below) |

### 1.2 `parse_format` (module6_whyml/struct_format.py): ≥ 6 links + 2 live rewrites. NOT attempted.

| step | variant | verdict |
|---|---|---|
| verbatim port + [T] class sync (`slots: Tuple[str, ...]`, `chars`) | `p0` | REFUSED: `slots.extend(...)` has no certified mutation lowering |
| class sync only (stub kept) | `p1` | L3-TC: a variadic `Tuple[str, ...]` field is `array int` (erased), which also breaks the VERIFIED `slot_id` (`_short_type(self.slots[0])`) |
| [R] `slots = slots + [slot_type] * count` | `p2` | REFUSED R325: `tuple(slots)` is the opaque `tuple_1` |
| stand-in `slots=slots` | `p3` | REFUSED R551 (list passed to a tuple parameter) |
| + [R] termination guard `if m.end() <= pos: return None` + `#@ loop variant len(fmt) - pos` | `p4` | same R551 |
| stand-in class fields `List[str]` | `p5` | L3-TC: `Return__union_parse_format_0 has mutable components` (an `Optional[<record>]` return of a mutable record) |
| stand-in return `Optional[int]` | `p6` | L3-TC: the tuple assignment `count_str, char = m.group(1), m.group(2)` erases both to `int` (calcsize uses annotated single assignments); `_CHAR_TO_TYPE.get(char)` is the opaque `_CHAR_TO_TYPE_get_1 : int`; `[slot_type] * count` is an `array` of an `Optional[str]` |

Links measured: (1) list `extend` (or a live rewrite), (2) `tuple(<list local>)`, (3) a typed `Tuple[str, ...]` field as a pure `seq string` + re-proof of the VERIFIED `arity` / `slot_id`, (4) a PURE (non-`mutable`) record for an `Optional[<frozen dataclass>]` exception payload (emitter-wide record change), (5) typed tuple-assignment of `str` results, (6) `_CHAR_TO_TYPE` as an `option string` map plus the `Optional[str]` narrowing of `slot_type` (it is non-None only through `not (slot_type is None and char != "x")` ∧ `char != "x"`). Plus the [R] live termination guard: `re_end_op` is law-free, so `len(fmt) - pos` decreases only through the guard calcsize already carries (no axiom may state that the token pattern consumes a character).

### 1.3 `bases_closure` (exception_model.py): ≥ 5 links, one of them a termination proof over a finite universe. NOT attempted.

| step | variant | verdict |
|---|---|---|
| verbatim port | `b0` | REFUSED: `frontier.pop()` has no certified mutation lowering |
| stand-ins `frontier[len-1]` / slice / `frontier + list(..)` | `b1` | L3-TC; the emission shows the rest of the chain: `EXCEPTION_BASES.get(exc, ())` is the opaque int-hashed `eXCEPTION_BASES_get_2 (str_hash_op exc) ()`; `seen: set` is `map int (option int)`; `frozenset(seen)` is the opaque `frozenset_1` against a bare `frozenset` codomain (`map int (option int)`); and the `while frontier` loop has NO variant |

Termination is the deciding wall. A `while` with no variant in a non-`\diverges` function is an unprovable termination VC (checked: Why3 1.8.2 `w/t.mlw`). The only variant is `K * (|U| - |seen|) + len(frontier)` (U = the finite set of base names, K = the longest base tuple), which needs a CONCRETE model of the ~70-entry `EXCEPTION_BASES` literal, the invariant `frontier ∪ seen ⊆ U`, and set cardinality, none of which the current set model (`map int (option int)`) has. Declaring it `\diverges` would be a contract change cascading to the VERIFIED `handler_catches`' callers. So this is a capability boundary (no axiom is needed in principle, but it is not a bounded build).

**Ranking by complete-chain cost:** `_to_cache_payload` (4 links, all local, one mirror re-proof outside its file) < `parse_format` (6 links + 2 live rewrites, one emitter-wide record change) < `bases_closure` (termination over a finite universe).

## 2. Capability edits (commit cdd7db154)

Every edited method has a `\trusted` mirror twin or none, except `_comprehension_generators_to_ir` (VERIFIED twin, re-ported in the same commits: cdd7db154 first version, **b1d9c092f final**).

| file / method | mirror twin | change |
|---|---|---|
| `audit_proof_reverify.py` `_to_cache_payload` (live and mirror) | the converted stub | [T] return annotation `-> dict` → `-> Dict[str, PyVal]` (runtime-inert under `from __future__ import annotations`; `PyVal` is the unimported sentinel Module5 already uses) |
| `frontend/Module5_IREmitter.py` `_collect_class_fields` (dataclass `List[Tuple[..]]` field rule) | `\trusted` | **link 2a**: a nested `List[str]` tuple slot is `seq string` (deep), so `qualname_results: List[tuple[str, bool, List[str]]]` is `seq (string, int, seq string)`, was `array int` |
| `frontend/Module5_IREmitter.py` `_comprehension_generators_to_ir` | VERIFIED (re-ported verbatim) | **link 2b**: a TUPLE comprehension target gets `"target_elts": [names]` (a non-Name slot is `"_"`), merged with `\|` ONLY for a tuple target, so every other comprehension's IR dict and its `repr` are unchanged (the first version added the key everywhere and moved `stmt_control_flow.mlw` by a `repr`-hashed temp name; fixed in b1d9c092f) |
| `module6_whyml/expressions.py` `_pyval_wrap` | ABSENT from the mirror | **link 1**: a `float`-typed record-field read is `HInt (real_hcarrier_op <real>)`, a law-free program `val` (fresh int per call, reads the real). Not `HFloat`: the positive tag decides `isinstance(.., float)`, and a `float` slot can hold a Python int (numeric tower; PyCSL keeps `isinstance(<float param>, float)` opaque via `typeof_op` for the same reason, `rt/f1.mlw`). **link 2c**: `[<names>] / (<names>) / <name> for (<t1>, .., <tn>) in <recv>.<field>` over a `seq (t1, .., tn)` field (slots `string` / `int` / `seq string`) is a faithful `HArr` built by a backward `for` fold, slots bound by position from `target_elts`, `string` → `HStr`, `int` → the erased `HInt`, `seq string` → `HArr` of `HStr` (inner fold). Fail-closed on: >1 generator, `ifs`, a `_` or repeated slot name, an element that is not made of slot names, a field name with ≠ 1 declared value_type across the records, any other slot type, spec context |

- No edit touches `pycsl.py` or `frontend/ir_resolve.py`. No new `\trusted`, no axiom (`real_hcarrier_op` is a program `val` with no postcondition), no gate change, `proof_axiom_allowlist.py` untouched.
- Scope by construction (rt82 W1): nothing is keyed on a class or field NAME. Link 2a/2c fire for any record with such a field; in a user module the record decl names `seq` without `use seq.Seq` unless something else pulls it, which fails closed (`rt/a2`, `rt/a3`: `unbound type symbol 'seq'`).

## 3. Mirror and contract

```python
#@ requires True
#@ ensures True
#@ assigns \nothing
def _to_cache_payload(report: ReverifyReport) -> Dict[str, PyVal]:
    return {
        "compile_ok": report.compile_ok,
        "compile_stdout": report.compile_stdout,
        "compile_stderr": report.compile_stderr,
        "elapsed_compile_s": report.elapsed_compile_s,
        "qualname_results": [
            [qn, ok, axs] for (qn, ok, axs) in report.qualname_results
        ],
    }
```

The body is byte-verbatim the live body. The emitted body (`pr/whole.mlw`) reads all five fields:

```
(map_update_some (... (const (None: option hval)) "compile_ok" (HInt report.compile_ok)) "compile_stdout" (HStr report.compile_stdout))
  "compile_stderr" (HStr report.compile_stderr)) "elapsed_compile_s" (HInt (real_hcarrier_op report.elapsed_compile_s)))
  "qualname_results" (HArr (let _u74s1 = report.qualname_results in let _u74a1 = ref HNil in
     for _u74i1 = Seq.length _u74s1 - 1 downto 0 do let (_u74x1_0, _u74x1_1, _u74x1_2) = Seq.get _u74s1 _u74i1 in
       _u74a1 := HCons (HArr (HCons (HStr _u74x1_0) (HCons (HInt _u74x1_1) (HCons (HArr <fold of HStr over _u74x1_2>) HNil)))) !_u74a1 done; !_u74a1)))
```

`ok` is a `bool` slot, so it is the erased `HInt` (sound, not `HBool`). The value is low (a cache-payload builder for trusted callers), but the body is now input-reading in every field (cv15's facade is gone).

## 4. Proofs

`proofs.sh` (worktree, NORMAL, `PYTHON_CPU_COUNT=2`, `TMPDIR` under the worktree), summary `pr/summary.txt`. The 21:35Z run is VOID (EDQUOT: Why3 `Sys_error("Disk quota exceeded")`), kept in `pr/void/`. The 22:32Z re-run below has no quota string in any log.

| run | command | result | oom_kill | log |
|---|---|---|---|---|
| `--fun _to_cache_payload` | `pycsl.py src/self-annotate/src/audit_proof_reverify.py --fun _to_cache_payload --import-path src/pycsl --verification-image src/self-annotate/src` | rc 0, SUCCESS (22:32–22:35Z) | 15 / 15 | `pr/fun.log` |
| **whole file** audit_proof_reverify.py | same, no `--fun` | **rc 0, "All contracts formally proven"**: 88 Valid, 0 non-Valid; the non-vacuity gate passed (prints only on failure) (22:35–22:41Z) | 15 / 15 | `pr/whole.log`, `pr/whole.mlw` |
| carry-over to the final head b1d9c092f | the head mirror-sweep emission `sw/head/mir/audit_proof_reverify.mlw` and a worktree re-emission (`v/w_apr.mlw`) are BYTE-IDENTICAL to `pr/whole.mlw`; no proof tooling changed (rule 34) | carries over | — | `cmp` (§7) |
| **whole file** audit_proof.py (moved mirror file) | `apw.sh` | __APW__ | __APWOOM__ | `pr/ap_whole.log` |

Module5_IREmitter.py: its mirror `.mlw` is byte-identical to the base (the re-ported `_comprehension_generators_to_ir` body lowers to the same opaque `list_comp_int`), so its whole-file proof carries over; no Module5 proof was run.

## 5. Leaf reachability and mutation

| check | result | log |
|---|---|---|
| leaf: `#@ assert 1 == 2` at the head of the single body block, `--fun` | **NOT proved** (the assertion goal: Timeout 30 s), rc 1: the body is reachable | `pr/leaf.log` |
| arm (.mlw): OUTER fold body → `absurd; …` (`arm_outer.mlw`) | "Unreachable point" **NOT proved** by z3 (Timeout) and alt-ergo (Timeout), rc 2: the outer loop body runs | `pr/arm_outer_{z3,alt-ergo}.log` |
| arm (.mlw): INNER fold body (the `seq string` slot) → `absurd; …` | **NOT proved** by z3 and alt-ergo (Timeout), rc 2 | `pr/arm_inner_{z3,alt-ergo}.log` |
| mutation 1: `report.cached = True` added (violates `assigns \nothing`) | **PROVED** (rc 0) — see finding F1 | `pr/mut_frame.log` |
| mutation 2: `report.compile_stdout[0]` | **PROVED** (rc 0) — see finding F2 | `pr/mut2.log`, `pr/mut2.mlw` |
| mutation 3: `report.compile_ok // len(report.qualname_results)` | __MUT3__ | `pr/mut3.log` |

**F1 (PRE-EXISTING, not introduced): `#@ assigns \nothing` is not enforced on a record PARAMETER of a module function.** The mutant emits `report.cached <- 1;` with no frame `ensures` for `report` and no `writes`; Why3 infers the write effect from the `let` body, so a CALLER sees it (no false proof through the effect system), but the source annotation is decorative for record params (lesson-10 class). Base-tree reproduction (`rt/fr1.py`, `frb.sh` on pycsl-u74b): __FRB__.

**F2 (PRE-EXISTING, plan §5 item 4):** a `str` subscript outside `no_exception` lowers to the slice `str_sub_op s 0 1` with no IndexError VC, so `s[0]` on a possibly-empty string proves.

## 6. Red-team notes (QUICK probes, `rt/`)

QUICK `--no-proof` probes in `rt/` (commands in `rtq.sh`, logs beside each file):
- `f1.py`: an `int` passed to a `float` param, or stored in a `float` field, is a Why3 type error (fail-closed), and `isinstance(<float param>, float)` is the opaque `typeof_op`. This is why link 1 uses the erased `HInt` carrier, not `HFloat`.
- `a1.py` (append a tuple holding a local list to the `seq` field, then mutate the list): REFUSED (route #283, field append untracked), so the `seq string` snapshot of an aliased list cannot be observed through this path. CPython: 1.
- `a2.py`, `a3.py` (user modules): fail-closed, `unbound type symbol 'seq'`.
- `a4.py`, `a5.py` (`seq.Seq` pulled in by a `Dict[int, List[int]]` field): the comprehension arm fires in a user program and is faithful even with reordered / partial slots (`[[b, a] for (a, b, c) in r.f]` → `HArr [HInt b; HStr a]`; `[c for (a, b, c) in r.f]` → `HArr` of `HArr HStr`); both files still fail L3-tc elsewhere (`d["x"]` / the for-loop over the field).
- No proof-level red team was run. Open axis for the driver's red team: a user program where `seq.Seq` is in scope and a claim reads the built `HArr` back (`len`, `in`) after the source list was mutated through an alias the route #81/#279/#283 fences do not see.

## 7. Gates

Base = `/home/fabrice/git/pycsl-u74b` (96eac515d), head = `/home/fabrice/git/pycsl-u74h` (b1d9c092f; src identical to the final branch). Each sweep ran in its own tree with cwd = tree root (`base.sh` and `G.sh`, NORMAL, `TMPDIR` under the worktree). oom_kill 15 throughout. No log of a counted gate contains EDQUOT / "Disk quota exceeded" / "No space left".

| gate | result | log |
|---|---|---|
| byte-diff root, base vs head | rc 0: **3329 / 3329**, 0 MOVED / 0 GONE / 0 APPEARED (emitted 3330 each side) | `logs/G/C-root.txt`, `sw/{base,head}/bd.log` |
| byte-diff pyref | rc 0: **2185 / 2185**, 0 / 0 / 0 | `logs/G/C-pyref.txt` |
| mirror sweep 53 / 53 + `diff -rq` | **2 MOVED**: `audit_proof_reverify.mlw` (the converted file; its head emission is byte-identical to the proved `pr/whole.mlw`), `audit_proof.mlw` (it imports `ReverifyReport`/`_to_cache_payload`: the pyval theory is now pulled in and the `_to_cache_payload` val returns `map string (option hval)`; its whole-file proof is in §4). Module5_IREmitter.mlw does NOT move | `logs/G/C-mir.txt`, `logs/G/diffrq-mir.txt` |
| (superseded) first head cdd7db154 | mirror sweep moved `module6_whyml__stmt_control_flow.mlw` too, by ONE `repr`-hashed temp name (`_pycsl_seq186928770_0` → `_pycsl_seq1580240762_0`; identical modulo that name): the first `target_elts` was added to every comprehension's IR. Fixed in b1d9c092f (key only for tuple targets), so no stmt_control_flow proof is owed | `logs/G-v1/`, `logs/G-v1.out` |
| check-self-annotate-sync.sh | rc 0 | `logs/G/sync.txt` |
| self-annotate-mirror-check.sh | rc 0 | `logs/G/mircheck.txt` |
| doc-coherency --check | rc 0 | `logs/G/doccoh.txt` |
| check-assigns-writes-survival (single-underscore head emission, 53 files) | rc 0 | `logs/G/lg/check-assigns-writes-survival.txt` |
| check-trusted-frame-honesty | rc 0 | `logs/G/lg/check-trusted-frame-honesty.txt` |
| check-getattr-erasure | rc 0 | `logs/G/lg/check-getattr-erasure.txt` |
| run-soundness-planes.sh (fast), teed in full | rc 0: **62 / 62 green** (fast + conversion tier), incl. check-trusted-reasons after ec91ef197 | `logs/G/planes.txt` |
| count-trusted-directives | rc 0 | `logs/G/count-trusted.txt` |
| `\trusted` (canonical grep) | 365 (base) → **364** | `logs/G.out` |
| proof_axiom_allowlist diff vs base | 0 lines (ledger stays 3) | `logs/G.out` |

M1: no corpus file moved, so no corpus re-proof is owed.
