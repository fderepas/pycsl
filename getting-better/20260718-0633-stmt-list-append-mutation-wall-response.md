# Fable response: in-place `list.append` through a parameter wall

**Reviewer:** independent fable (no prior context; judged from repo + own oracle runs only).
**Target report:** `getting-better/20260718-0633-stmt-list-append-mutation-wall.md`.
**Repo state at review:** branch `ghost-assign-bc6`, HEAD `2b2927bc` (confirmed via `git log --oneline -1`).
**Bottom line:** CLAIM A **CONFIRMED**, CLAIM B **CONFIRMED**, verdict **BREAKABLE** (not a certified boundary).

I did not edit any source file, TODO, or session.txt. All scratch artifacts live in `/tmp/wall-oracle/`.

---

## Oracle artifacts (verbatim)

### Oracle 1 — PyCSL emits a *local-copy* append; mutation does NOT reach the caller

Program `/tmp/wall-oracle/append_param.py`:

```python
#@ requires True
#@ ensures len(xs) == 1
#@ assigns xs
def push(xs: list) -> None:
    xs.append(5)

#@ requires True
#@ ensures \result == 1
def driver() -> int:
    xs = []
    push(xs)
    return len(xs)
```

Command:
```
python3 src/pycsl/pycsl.py /tmp/wall-oracle/append_param.py --import-path src/pycsl --keep-mlw --check-vacuity
```

Generated WhyML (`/tmp/wall-oracle/append_param.mlw`, verbatim):
```
  val snapshot (a: array int) : seq int
    ensures { Seq.length result = Array.length a }
    ensures { forall i:int. 0 <= i < Array.length a -> Seq.get result i = a[i] }

  let push (xs: array int) : unit
    requires { true }
    ensures  { ((Array.length xs) = 1) }
  =
    let xs = ref (snapshot xs) in
    xs := Seq.snoc !xs 5

  let driver () : int
    requires { true }
    ensures  { (result = 1) }
  =
    let xs = (Array.make 1024 0) in
    let _ = (push xs) in ();
    0
```

Prover result (verbatim, trimmed):
```
Sub-goal postcondition of goal push'vc.
Prover result is: Unknown (why3: Unknown (unknown)) (0.42s, 1219925 steps).
Sub-goal postcondition of goal driver'vc.
Prover result is: Valid (0.00s, 924 steps).
```

**Reading.**
- `push` shadows its array parameter with a *fresh local copy*: `let xs = ref (snapshot xs)`. `snapshot : array int -> seq int` copies the entries into a new `seq`. The append `xs := Seq.snoc !xs 5` grows the **local ref**. The caller's `array int xs` is **never written** — there is **no `writes` clause on `push`** and no assignment to the array. Hence `ensures Array.length xs = 1` is **Unknown/unprovable**: the array length is whatever entered and is untouched.
- The mutation is invisible to the caller by construction: `driver` builds `xs = Array.make 1024 0` (length 1024) and passes it. The callee's append changes a copy, not this array.

### Oracle 2 — the caller is a *vacuous false green*

Same run: `driver` returns the literal `0` yet `ensures result = 1` proves **Valid**. This is a vacuity, not a real proof. Modular verification lets `driver` *assume* `push`'s postcondition `Array.length xs = 1`; but `xs = Array.make 1024 0` has immutable length `1024`, so the assumption is `1024 = 1` → **false** → every downstream goal (including the false `result = 1`) is vacuously provable. Note `push`'s own contract was **Unknown** (unproven), yet `driver` still consumed it — the classic modular false-green. `--check-vacuity` did **not** flag this driver-side vacuity.

### Oracle 3 — distinct handlers emit BYTE-IDENTICAL WhyML (node tag erased to `0`)

Program `/tmp/wall-oracle/node_erase.py` — two handlers appending *distinct* stmt-node dicts:
```python
#@ assigns ir_stmts
def emit_pass(ir_stmts: list) -> None:  ir_stmts.append({"stmt": "pass"})
#@ assigns ir_stmts
def emit_break(ir_stmts: list) -> None: ir_stmts.append({"stmt": "break"})
```
Command: `python3 src/pycsl/pycsl.py /tmp/wall-oracle/node_erase.py --import-path src/pycsl --keep-mlw --no-proof`

Generated bodies (verbatim):
```
  let emit_break (ir_stmts: array int) : unit
    requires { true }
  =
    let ir_stmts = ref (snapshot ir_stmts) in
    ir_stmts := Seq.snoc !ir_stmts 0

  let emit_pass (ir_stmts: array int) : unit
    requires { true }
  =
    let ir_stmts = ref (snapshot ir_stmts) in
    ir_stmts := Seq.snoc !ir_stmts 0
```
`diff` of the two bodies (modulo function name) = **identical**. Both dict nodes `{"stmt":"pass"}` and `{"stmt":"break"}` were erased to the integer `0`. No `writes` clause on either signature.

### Oracle 4 — Why3 CAN express a SOUND in-place append, axiom-free

Hand `.mlw` `/tmp/wall-oracle/sound_append.mlw`:
```
  type stmt_ir = SPass | SBreak | SContinue | SReturn int

  let push (s: ref (seq stmt_ir)) (v: stmt_ir) : unit
    writes  { s }
    ensures { !s = Seq.snoc (old !s) v }
    ensures { Seq.length !s = Seq.length (old !s) + 1 }
  = s := Seq.snoc !s v

  let driver () : unit =
    let ir_stmts = ref (Seq.empty : seq stmt_ir) in
    push ir_stmts SPass;
    push ir_stmts (SReturn 7);
    assert { Seq.length !ir_stmts = 2 };
    assert { Seq.get !ir_stmts 0 = SPass };
    assert { Seq.get !ir_stmts 1 = SReturn 7 };
    assert { SPass <> SBreak }
```
Command + result (`why3 prove -P alt-ergo`, verbatim):
```
Goal push'vc.   Prover result is: Valid (0.03s, 16 steps).
Goal driver'vc. Prover result is: Valid (0.03s, 51 steps).
```
`grep` confirms **0 abstract `val`s and 0 `axiom`s** in this file. The caller observes both appended nodes *and* their preserved tags; distinct tags are provably distinct.

---

## 1. CLAIM A verdict — **CONFIRMED**

A passed-list mutation hits a **local copy**, not the caller's region (Oracle 1). PyCSL lowers a `list` parameter to `array int`, then at function entry emits `let xs = ref (snapshot xs)` — a fresh `seq int` copy — and lowers `list.append(v)` to `ref := Seq.snoc !ref v` on that local. The array parameter carries **no `writes` clause** and is never assigned, so the append is unobservable to any caller. The `#@ assigns xs` frame lowers to *no caller-visible write at all* (CLAIM B(iii): effectively empty). Confirmed against `src/pycsl/module6_whyml/statements.py:2464-2485` (the `append_targets` seq-param shadow: `let tgt = ref (snapshot tgt) in`) and `:2436-2442` (the `pre_decl` seq-param shadow). Bonus finding: the current model is also **int-only** (`snapshot : array int -> seq int`) and it *introduces an abstract `val snapshot`* — i.e. the "faithful" path today rests on an assumption the sound model (Oracle 4) does not need.

## 2. CLAIM B verdict — **CONFIRMED** (all three sub-claims)

- **(i) content not observable to caller** — Oracle 1: `push`'s postcondition about the caller-side array is Unknown; the append lives on a discarded local. Worse, a caller that *assumes* the contract goes vacuously green (Oracle 2): `driver` proves `result = 1` while literally returning `0`.
- **(ii) distinct handlers emit byte-identical WhyML** — Oracle 3: `emit_pass` and `emit_break` produce identical bodies; the node dict is erased to `0`. A verbatim port of the 22 handlers would collapse `_py_stmt_{pass,break,continue,...}` into indistinguishable procedures — the proof cannot witness that the right node was emitted.
- **(iii) `#@ assigns ir_stmts` → empty frame** — Oracle 3: neither handler carries a `writes` clause; the declared list-frame produces no caller-visible write.

Any one of these is a Gate-C reject; all three hold. A verbatim port would be a **FALSE GREEN**.

## 3. THE VERDICT — **BREAKABLE** (not a certified boundary)

A sound in-place-append-through-parameter model **exists and is expressible in Why3 today, axiom-free** (Oracle 4: `ref (seq τ)` parameter + real `writes { s }` + a `stmt_ir` ADT whose tags are preserved and provably distinct; both VCs Valid with zero abstract `val`s/axioms). So the wall is not a limitation of the logic — it is a limitation of PyCSL's current *single* lowering convention.

Can PyCSL adopt it without (a) a new axiom, (b) perturbing the build-and-return corpus byte-diff, (c) breaking other List-param frames? **Yes, via a discriminated second convention** — and the demand supplies a clean, syntactic discriminator:

- The 22 handlers all **return `None` and declare `#@ assigns <list-param>`**. Build-and-return programs **return the list** and do not frame a param. These two shapes are statically separable at emit time.
- Keep the existing `array int` → `let x = ref (snapshot x)` → materialize-on-return path for **return-a-list** functions → **byte-diff preserved** on the current corpus (that path is untouched).
- Route **None-returning + `assigns list-param`** functions to the new convention: parameter typed `ref (seq stmt_ir)`, body appends with `Seq.snoc` **on the ref itself** (no `snapshot`, no local shadow), signature carries `writes { p }` and an `ensures` relating `!p` to `old !p`. This is a *new* code path keyed on a syntactic property; it does not force existing List params to become mutable, so frame-fidelity of other List-param methods is untouched.

The models are therefore **not fundamentally in tension** — they coexist, partitioned by return-type-and-frame. The cost is a genuine multi-part **build**, not a one-line patch: (1) a `stmt_ir` ADT (sibling of the certified `emit_ir`/`pyconst_val` ADTs, referencing `pyconst_val` for expr children, no mutual recursion) with a co-landed axiom-free `src/formal-semantics/` certificate per the report's constraint §4; (2) a node-**constructor** lowering that preserves the tag instead of erasing to `0`; (3) the mutable-ref calling convention above with a non-vacuous `writes` frame. Non-trivial, but each piece is known-feasible (Oracle 4 discharges the logic core; `pyconst_val` already landed per HEAD `2b2927bc`). Hence **BREAKABLE and worth a spike-gated build** — record it as such, not as a certified boundary.

One caveat worth flagging to the base loop: the sound model must NOT reintroduce `snapshot` as the entry bridge for the mutable path (that `val` is an assumption). A ref-of-seq parameter is passed directly; no snapshot needed.

## 4. Make-or-break SPIKE the next run must pass

Smallest test that would **refute** this "breakable" verdict if it failed — one handler, end to end:

1. **ADT (axiom-free):** add `type stmt_ir = SPass | SBreak | ... | SReturn pyconst_val | ...` (expr children via the landed `pyconst_val`; no mutual recursion). Co-land a Rocq `Print Assumptions`-closed + Lean stdlib-kernel-only certificate in `src/formal-semantics/` (the `Phase2c_PyConstVal.v` precedent). **Gate:** ledger stays at 3 axioms.
2. **Convert exactly one handler** (`_py_stmt_pass` is the cleanest; or `_py_stmt_return` to also exercise an expr child) under the fixed `#@ requires True / ensures True / assigns ir_stmts` shape, routed to the new `ref (seq stmt_ir)` convention. **Gate — non-vacuity:** the emitted WhyML for `_py_stmt_pass` MUST carry a real `writes { ir_stmts }` and MUST differ from `_py_stmt_break`'s WhyML (kill the Oracle-3 byte-identity). The element must be a real ctor (`SPass`), never `0`.
3. **Driver that OBSERVES the append:** a caller that starts from an empty `ir_stmts`, invokes the handler, then reads back and **proves** `Seq.length !ir_stmts = old+1` AND `Seq.get !ir_stmts (len-1) = SPass`. This must prove **Valid and be non-vacuous** — i.e. re-run it asserting the *wrong* tag (`... = SBreak`) and confirm that variant **fails** (guards against a vacuous context à la Oracle 2). If the correct-tag driver cannot be proven Valid, or the wrong-tag driver also proves Valid, the verdict is refuted and the wall is a boundary.
4. **Inertness:** full-corpus byte-diff 0 on build-and-return programs (the old path untouched); self-annotation suite 35/35; mirror-check 52/52.

If steps 1-4 all pass on one handler, the 22-marker C bucket build is authorized; if step 3's observation or non-vacuity check fails, my "breakable" call is wrong and this is a certified boundary.
