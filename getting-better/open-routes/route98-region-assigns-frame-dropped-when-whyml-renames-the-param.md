# ROUTE #98 — ROUTE #96's REPAIR IS KEYED ON THE **EMITTED** NAME WHILE THE `assigns`
# CARRIES THE **SOURCE** NAME, SO A PARAMETER WHY3 RENAMES LOSES ITS `writes` CLAUSE
# AND THE WHOLE OF #96 COMES BACK

**SEVERITY 1. FOUND, REPRODUCED, MECHANISM PINNED IN THE EMITTER, MINIMAL PAIR MEASURED,
CPython CONTRADICTS A PROVED RESULT, POSITIVE CONTROL PROVING.** Found by the
`continue`-census generator; it is the fourth hit in four tries.

>>> **A CARRIER SURVIVING A REPAIR IS A SECOND ROUTE, NOT A FAILED REPAIR.** Route #96's
>>> repair is CORRECT for every parameter name it can see. The defect is that it decides
>>> membership in one name space using a key from another.

## THE ONE-LINE STATEMENT

A `\trusted` stub declaring `#@ assigns model[0..n]` emits a bodyless `val` with **NO
`writes` clause**, so Why3 treats it as pure and the caller keeps every stale fact about the
array — exactly route #96. Rename the parameter from `model` to `a` and the `writes` clause
appears and the exploit is refused. The ONLY difference is the parameter's NAME.

## THE MINIMAL PAIR — IDENTICAL BUT FOR ONE IDENTIFIER

```python
#@ requires n >= 0
#@ assigns a[0..n]              #  <-- or: model[0..n] / Buf[0..n]
#@ \trusted reviewer: r98
def scramble(a: list, n: int) -> int:
    a[0] = 0
    return 0

#@ requires \length(arr) > 3
#@ requires arr[0] == 7
#@ ensures \result == 7
def driver(arr: list) -> int:
    scramble(arr, 1)
    return arr[0]
```

| param name | emitted signature | `writes` clause | verdict |
|---|---|---|---|
| `a` (control) | `val scramble (a: array int) (n: int) : int` | **`writes { a }`** | **FAILS** — #96 repaired, exploit refused |
| `model` | `val scramble (py_model: array int) …` | **ABSENT** | **PROVES `\result == 7`** |
| `Buf` | `val scramble (buf: array int) …` | **ABSENT** | **PROVES `\result == 7`** |

**CPython ground truth: `driver([7, 7, 7, 7])` returns `0`.** PyCSL proves `\result == 7`.

## THE MECHANISM, READ OFF THE EMITTER (not inferred)

`module6_whyml/functions.py:6605` builds the population from the **already-emitted** signature
text:

```python
self._current_array_param_names = set(
    re.findall(r"\((\w+)\s*:\s*array\b", args_str))
```

`args_str` has been through `whyml_ident` (`module6_whyml/identifiers.py:78-83`), which
**lowercases a leading capital** and **prefixes any WhyML reserved word with `py_`**.

`module6_whyml/statements.py:3446-3452` then tests the **source** name against that set:

```python
base = a.get("base")                       # the SOURCE identifier, from
                                           # Module5_IREmitter.py:769 -> Module2_Parser.py:1528
if base and base in _arr_params and base not in region_targets:
    region_targets.append(base)
```

So for `model`, `_arr_params == {"py_model"}` and `base == "model"`: the membership fails, no
region target is collected, `_val_targets` is empty, and the `val` is emitted with no frame.

**`WHYML_RESERVED` (identifiers.py:36-58) is full of ordinary Python parameter names** —
`model`, `range`, `check`, `label`, `result`, `old`, `ref`, `float`, `to`, `by`, `type`,
`function`, `variant`, `invariant`. This is not an exotic corner.

## WHY IT SURVIVED ITS OWN REVIEW — AND THIS IS THE TRANSFERABLE PART

The skip is commented, and the comment **names this exact case as accepted residue**:

> `FAIL-CLOSED, and deliberately so: a base that is not an array-typed PARAMETER of the
> signature being emitted … (a module global, a `str`, **a name the emitter renamed**)
> contributes nothing and emission is unchanged. … Any such residue stays visible as an
> un-framed val.`

Two separate errors are frozen in that sentence:

1. **"FAIL-CLOSED" IS A CLAIM ABOUT THE EMISSION, NOT ABOUT THE PROOF.** Emitting nothing is
   fail-closed for the *emitter* (no ill-typed `writes` is produced) and fail-**OPEN** for the
   *verifier* (the caller is told the stub is pure). The two were conflated. Dropping a frame
   clause is never conservative — an unframed `val` is the STRONGEST possible claim.
2. **"STAYS VISIBLE" NAMES NO OBSERVER.** Nothing checks for an un-framed `val` carrying a
   region `assigns`; there is no gate, no plane and no ratchet on it. Visible to whom?

>>> This is generator #1 of the campaign, in its purest form: **the refusal's own prose
>>> quoted the exploit and classified it as safe.** And it is the mirror of #94: *a perfectly
>>> honest message can sit on an incomplete guard* — here the message is honest about WHAT
>>> the code does and wrong about WHAT THAT MEANS.

Note also the reason gen #15's census measured this branch's in-tree population as **ZERO**
and was right to: no in-tree file writes a region `assigns` on a trusted stub at all. An empty
population is a place to look, not a reason to relax — and the residue it hides is not visible
to any sweep of the existing corpus.

## WHY THE OBVIOUS `requires`-CARRYING EXPLOIT IS **NOT** THE ROUTE (measured, so nobody re-probes it)

The first exploit attempt kept route #96's `#@ requires \length(model) > n + 1`. That file is
**LOUDLY REJECTED**: `File ".../x.mlw", line 9: unbound function or predicate symbol 'model'`
— the contract renders the SOURCE name while the signature renders `py_model`, so Why3
type-rejects the whole module. **A probe whose control refuses has measured nothing**, and this
one would have been read as "the fence holds" if it had been the only arm run. The route needs
the renamed parameter to appear in **no contract clause other than the `assigns`** — then there
is no unbound symbol, nothing is rejected, and the frame is dropped in silence.

## STATUS

**OPEN.** Repair scoped below.

## THE REPAIR, SCOPED

Compare the two names in ONE name space. The region base must be put through the SAME
`whyml_ident` the signature went through before the membership test:

```python
base = a.get("base")
base_emitted = whyml_ident(base) if base else base
if base_emitted and base_emitted in _arr_params and base_emitted not in region_targets:
    region_targets.append(base_emitted)
```

and the appended target must be the **emitted** name, because that is what `writes { … }`
must reference.

1. Both directions must be measured: the exploit must FAIL for `model`/`Buf` afterwards, AND
   the `a` control must still FAIL, AND route #96's capability arm (witness 1271: a trusted
   stub with both `assigns a[0..n]` and `ensures a[0] == 9` must still PROVE) must survive for
   a renamed parameter too.
2. **CO-LANDING, THE FAIL-CLOSED HALF:** the residue that remains after the rename fix (a base
   that is genuinely not an array parameter — a module global, a `str`) is still dropped in
   silence, and the comment's "stays visible" still names no observer. Give it an observer:
   either a refusal at emission, or a soundness PLANE that counts bodyless `val`s carrying a
   region `assigns` and no `writes`, so the residue is ratcheted instead of merely described.
   Negative-test whichever is chosen.
3. `whyml_ident` is imported in `statements.py`? CHECK — it is imported in `functions.py`
   (`from module6_whyml.identifiers import whyml_ident, …`). Verify before landing.

## WHY `assigns` IS THE **ONLY** CLAUSE THAT FAILS SILENTLY — the characterisation that
## makes this route precise, and bounds the repair

Measured on the same renamed parameter:

| clause mentioning the renamed param | outcome |
|---|---|
| `#@ requires \length(model) > n + 1` | **LOUD** — `unbound function or predicate symbol 'model'` |
| `#@ ensures ...` over it | same rendering path, same loud rejection |
| **`#@ assigns model[0..n]`** | **SILENT** — the clause is simply dropped |

The reason is structural: every other clause goes through EXPRESSION RENDERING, which emits
the SOURCE identifier into a module whose signature binds the MANGLED one — producing an
unbound symbol and a hard Why3 rejection. `assigns` is the one clause that does NOT go
through expression rendering: it is consumed structurally by `_emit_frame_condition`, which
turns it into a `writes` target or into nothing at all.

**So the mangling inconsistency is tree-wide, and it is fail-closed EVERYWHERE EXCEPT the one
clause whose consumer answers "nothing" instead of raising.** That is the whole of route #98,
and it is why the repair is correctly scoped to `_emit_frame_condition` rather than to the
renderer: the other clauses are already loud, and making the frame path loud (or correct)
closes the only silent one.

It also sharpens the CO-LANDING requirement: route #96's CAPABILITY witness (1271 — a trusted
stub with both `assigns a[0..n]` and `ensures a[0] == 9`, which must PROVE) **cannot currently
exist for a renamed parameter at all**, because its `ensures` would be loudly rejected. So
after the rename fix, verify the capability arm on the `a` spelling (which must still prove)
and record the renamed spelling as a LOUD, fail-closed boundary rather than expecting it to
prove.
