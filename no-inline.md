# no-inline.md — `#@ no_inline`: a modular-verification boundary for large methods

**Date:** 2026-06-08
**Status:** IMPLEMENTED (`dcd1d6d`) — all pieces A/B/C landed; P3 measured os 45→39; driver 0650 proves.
**Owner:** PyCSL tool ([TOOL], `src/pycsl/**`)
**Motivation source:** the 07-2333 os-coverage work — 6 of the 14 SMT-timeout goals in the os module
are an **inlining artifact**, not a contract or solver problem.

---

## 1. The problem, validated

`pure_lib/os/__init__.py`'s `write` is a one-line wrapper:

```python
#@ ensures \result == -1 or \result >= 0
def write(fd, data: list):
    return _filesystem.sys_write(fd, data)
```

`_filesystem` is a module-global `UnixInodeFileSystem`, so the IR-inliner (`ir_inline.py`, Phase 2)
**splices `sys_write`'s entire body** into `write`. `sys_write` is a complex multi-block write loop
(non-linear block arithmetic, slice writes, on-demand allocation). Proving `write`'s postcondition
*through the inlined body* blows the SMT search up to billions of steps → **6 Timeout goals**.

**Key fact (measured):** `sys_write` **proves standalone** (`--fun unixinodefilesystem__sys_write`
→ 4/4 goals, after the 07-2333 invariant fix). Its postcondition (`\result == -1 or (\result >= 0
and \result <= \length(data))`) *implies* `write`'s. So if `write` consumed `sys_write`'s **contract**
instead of its inlined body, `write` would prove trivially and the 6 timeouts vanish — **with no new
proof work.** This is textbook **modular verification**: verify the callee once against its contract;
verify the caller against the callee's contract.

### 1.1 Why it isn't a one-line fix (PoC finding)

A PoC that added `sys_write` to the inliner's existing skip set (the `recursive` set) **failed**:

```
[!] PIPELINE ERROR: cannot inline recursive method 'unixinodefilesystem__sys_write' on global
    '_filesystem': a recursive method is verified by contract … not by inlining (inline.md Phase 3).
```

The inliner is **inline-or-error**: its only handling for a skipped method is to *raise* when a caller
reaches the call (`_Inliner._expand`, `ir_inline.py:203`). There is **no path that lowers the call as
a call to the callee's contract.** So the boundary needs a real new code path, not a flag.

---

## 2. The mechanism — three pieces

### Piece A — the `#@ no_inline` directive  *(grammar → weaver → Module5)*
Mark a method as a modular boundary. Threaded exactly like the existing `#@ \diverges` flag:
- **Module2 grammar** (`Module2_Parser.py`): recognise `no_inline` → a `NoInline` CSLNode + transformer
  (mirror `Diverges`). (Name TBD — see §6; `no_inline` is the proposal.)
- **Module3 weaver** (`Module3_Weaver.py:~205`): `elif isinstance(c, NoInline): node.csl_no_inline = True`
  (mirror `csl_diverges`).
- **Module5** (`Module5_IREmitter.py:~1555`): `"no_inline": getattr(node, 'csl_no_inline', False)` into
  the function IR (mirror `"diverges"`).

### Piece B — inliner surgery: lower a no_inline call as a **contract-call**  *(`ir_inline.py`)*
This is the substantive part. Today (`_inline_calls`, `ir_inline.py:341`) every global-instance method
call is expanded or, if in the `recursive`/skip set, errors. New behaviour:
- Collect `no_inline_methods = {f["name"] for f in funcs if f.get("no_inline")}`.
- When the inliner encounters a call `g.m(args)` whose callee method-key is in `no_inline_methods`,
  **do not splice the body and do not raise** — **leave the call in place** as a normal method call so
  Module6 lowers it as a *call to the verified function*.
- The callee itself is still emitted as a **verified `let` with its full contract and body** (so its
  postcondition is proven once) — **NOT a `val`.** *(The PoC's skip path emitted a `val`, which would
  drop body verification = unsound. The whole point is that the body IS verified, just once, and
  callers reuse the contract. The implementation must emit a `let`, and Module6/Why3 use the contract
  at the call site by construction.)*
- The Phase-1 `pure`-demotion and the depth cap are unchanged; recursive detection is unchanged (a
  no_inline method is independently a boundary, whether or not it recurses).

### Piece C — module-global contract resolution  *(`_resolve_dotted_signature`)*
For the non-inlined call `_filesystem.sys_write(...)`, Module6 must resolve the callee's return type +
**result-only `ensures`** so `write` can discharge its postcondition from them. `_resolve_dotted_signature`
(`expressions.py:611`) already does this for `self.<m>` and `<recordvar>.<m>`; extend its `<recv>.<m>`
branch to also match a **module-global** receiver (this is the one piece already validated in isolation):

```python
gv_classes = getattr(self, "_module_global_classes", {})
if len(parts) == 2 and (parts[0] in rv_classes or parts[0] in gv_classes):
    cls = (rv_classes.get(parts[0]) or gv_classes.get(parts[0])).lower()
    # … existing lookup of _module_method_return_types / _module_method_result_ensures …
```

### Piece D — apply it
Add `#@ no_inline` to `UnixInodeFileSystem.sys_write` (and any other large, standalone-proving syscall
whose inlining blows up — measure case by case: candidates are `sys_open`, `sys_symlink`, `sys_access`,
whose 3 timeouts are complex-body blow-ups that *may* also be inlining-driven; re-measure each).

---

## 3. Soundness

The boundary is sound **iff the callee's body is verified against its contract somewhere in the same
compilation** (Piece B's `let`, not a `val`). Then:
- callee `sys_write`: body ⊢ contract (proven once, standalone — already passes);
- caller `write`: contract(`sys_write`) ⊢ contract(`write`) (trivial).

This is strictly *more* honest than today's inlining (which re-proves the body in every caller's
context). The failure mode to guard against is the PoC's: emitting the callee as a `val` (contract
**assumed**, body unverified) — that would silently move `sys_write`'s body into the TCB. **Acceptance
gate §5 must assert the callee's body VCs still appear and pass.**

---

## 4. Phasing

| Phase | Delivers | Gate |
|---|---|---|
| **P0** validation (DONE, informal) | confirmed sys_write proves standalone; confirmed inliner is inline-or-error | — |
| **P1** Piece C (module-global resolution) | `_resolve_dotted_signature` resolves `_global.method` contract | corpus sweep byte-identical (no global-method call relies on the old int default) |
| **P2** Piece A + B (directive + inliner contract-call path) | `#@ no_inline` marks a method; its calls lower as contract-calls; its body stays a verified `let` | a 2-class driver (caller + no_inline callee) **proves**, and the callee's own body VCs still appear |
| **P3** Piece D (apply to os) | mark `sys_write` (+ measured others) | **os unproven 45 → ≤ 39**; os formal test 18/18; stdlib-coverage green |

Land P1 first (it's independently correct and gates cleanly); P2 is the surgery; P3 is the payoff +
measurement.

## 5. Acceptance criteria

1. **A no_inline method's BODY is still verified** — its `let … = body` and its body VCs appear in the
   emitted WhyML and pass (NOT emitted as a `val`). *(The soundness gate — §3.)*
2. **Its callers lower the call as a contract-call** — a driver: `caller()` proving its postcondition
   *solely* from the no_inline callee's `ensures` (the callee's body absent from the caller's VC).
3. **os improves**: unproven `45 → ≤ 39` (the 6 sys_write-inlining timeouts cleared); formal_0001 18/18;
   `bin/stdlib-coverage.py --check` green.
4. **No regression / byte-identical** for any file with no `#@ no_inline` method — the full
   `bin/run-reference-tests.sh --pycsl` corpus unchanged (the inliner is load-bearing for ~30 os proofs
   and the whole corpus; this is the primary risk, §7).
5. **Anti-unsoundness driver**: a no_inline method whose contract is *wrong* (a deliberately false
   `ensures`) must make the **callee** fail (its body ⊬ its contract) — proving the body is still checked.

## 6. Open design questions (for review)

- **Directive name/spelling.** `#@ no_inline` (plain, matches intent) vs `#@ \modular` / `#@ \boundary`
  (a `\`-prefixed contract keyword, consistent with `\trusted`/`\diverges`). The latter is more in-house
  but the former reads better. Recommend `#@ no_inline`.
- **doc-coherency surfaces.** A new `#@` directive must appear in `annotations.md` + the 3
  `docs/*reference*.md` + a skill (the 5-surface gate). Budget for that.
- **Auto vs explicit.** Should the inliner *auto*-boundary a method above a size/complexity threshold,
  instead of requiring `#@ no_inline`? Explicit is safer and predictable; auto risks surprising
  emission changes. Recommend **explicit** for v1, revisit auto later.
- **Interaction with `pure`-demotion + recursion.** A no_inline method that reads globals still needs the
  Phase-1 `pure`-demotion; a no_inline method that recurses is already a boundary — the sets should
  union cleanly. Verify no double-handling.

## 7. Risks

- **The inliner is load-bearing.** It currently makes ~30 os syscalls + the whole corpus verify by
  splicing global-method bodies. Piece B changes its control flow; a bug could silently alter emission
  for non-no_inline files. **Mitigation:** the byte-identical corpus gate (§5.4) + emit only the new
  path when `no_inline` is set (no behaviour change otherwise).
- **Soundness regression (val instead of let).** The single most important correctness risk — §3/§5.1.
- **Scope creep on os.** Only `sys_write` is confirmed inlining-driven (6 goals). `open`/`symlink`/
  `access` (3) may be intrinsic complex-body blow-ups that no_inline does **not** fix — measure each in
  P3, don't assume.

## 8. Out of scope
- The `walk` timeouts (3) — those need `listdir` to return a typed, length-bounded array (its own
  contract work), unrelated to inlining.
- Cross-*file* modular verification (verifying `UnixInodeFileSystem.py` and `os/__init__.py` as separate
  compilations sharing stubs) — a larger architecture change; `no_inline` is the in-compilation version.
- `#@ no_inline` on free functions (only global-instance methods drive the os blow-up; generalise later
  if a driver needs it).

> **In one line:** `#@ no_inline` turns a large, standalone-proving method into a modular boundary —
> its body is verified once, callers reuse its contract instead of re-proving the inlined body — which
> clears the 6 sys_write inlining-timeouts in os; the work is a new directive (grammar→weaver→Module5),
> inliner surgery to lower such calls as contract-calls (the PoC proved the inliner is inline-or-error
> today), and module-global contract resolution — gated by a byte-identical corpus sweep and a
> body-still-verified soundness check.
