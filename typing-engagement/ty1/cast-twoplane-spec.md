# cast — two-plane spec (TY1)

**Construct:** `typing.cast(t, v)` (PEP 484, §"The Any type" / "Casts").
**Tier:** TY1 (monomorphic refinements).
**Classification:** **Shimmed on BOTH planes** (static "assertion" is NOT a dischargeable VC).
**Authorities cited:** S1 (typing spec), S2 (PEP 484), S3 (library reference), S4 (CPython
`Lib/typing.py`). No S5 conformance case is committed (see §1, §4).

---

## 1. STATIC PLANE

**Claim.** `cast(t, v)` is a static *type assertion*: it instructs the static checker to
treat the value `v` as having static type `t`. That is the entire static meaning — there
is no further judgment. Per **S1** (the typing specification, which **supersedes S2** on
conflict) and **S2/PEP 484**, the cast carries **no new obligation**: it does not check,
does not narrow at runtime, does not constrain `v`'s actual type, and does not generate a
proof obligation that `v` *actually* has type `t`. The static checker *trusts* the cast at
the type level; the assertion is unchecked by definition (this is PEP 484's documented
semantics: "the cast function returns its second argument unchanged at runtime, but tells a
type checker that the returned value has the first argument's type").

**PyCSL soundness stance — the honesty point.** Because the static "assertion" is an
unchecked hint rather than a dischargeable obligation, PyCSL does **not** lower `cast(t, v)`
to a verification condition. There is no VC that says `v : t`; there is no `requires`
clause over `t`; there is no narrowing predicate emitted. The construct is **Shimmed on the
static plane** in exactly the sense that it is Shimmed on the runtime plane: the assertion
is recorded as a *hint* the checker accepts, not as a proof goal PyCSL must discharge. This
is the key honesty point and the degenerate case of the two-plane model: `cast` is the one
typing construct where the static plane does **NOT** lower to an obligation. A spec that
claimed `cast` lowered to a `requires`/`ensures` VC over `t` would be blending the planes
and would be incoherent: there is no runtime check to back such a clause, and S1/S2 grant
no static obligation to back it either.

**No S5 case is committed.** S5 (the typing conformance suite) tests static judgments that
can be checked; `cast`'s assertion is unchecked, so there is no conformance case to declare.
This is **not** a gap — it is a consequence of `cast` carrying no dischargeable static
obligation. The declared S5 subset for `cast` is empty by construction.

## 2. RUNTIME PLANE

**Claim.** `cast(t, v)` returns `v` unchanged at runtime. Per **S3** (the library
reference), `typing.cast` is documented as "return `v` unchanged" — pure identity. S3's
central sentence is **negative**: annotations are not enforced at runtime, and `cast` is
the sharpest instance of that — it performs **no** type check, **no** conversion, **no**
narrowing, **no** validation of any kind. Resolving S3 against **S4** (CPython
`Lib/typing.py`): the implementation is literally `def cast(typ, val): return val` —
identity, observable as identity.

**PyCSL shim.** The shim at `src/pycsl_lib/typ/__init__.py:cast` carries exactly:

```
#@ ensures \result == val
def cast(typ, val) -> int:
    return val
```

The single postcondition `ensures \result == val` carries **only** the identity claim. It
does not mention `typ`; it does not assert `val : typ`; it does not emit any clause that
could be read as a runtime type check. A shim that *checked* anything S3 says is unchecked
would be unfaithful in exactly the way an over-strong axiom is, and would fail the S4
shim-faithfulness gate. The shim is classified **Shimmed (runtime identity)**.

## 3. DIVERGENCE

**There is NO divergence for `cast`.** Both planes agree, fully and vacuously: `v` is
returned unchanged. The static plane carries no obligation that could diverge from the
runtime plane; the runtime plane carries only the identity postcondition, which the static
plane also accepts trivially.

`cast` is the **degenerate case** where the no-blend rule (§0 of `typing-global-impl.md`)
is **vacuously satisfied**: there is no static claim to blend with the runtime claim, so
the rule that "neither plane's contract may stand in for the other" has nothing to forbid.
This is stated explicitly so the absence of a divergence section is not mistaken for an
omission — it is the substantive finding. The no-blend trap table (§3.2) names `cast`'s
trap as "a `cast` that validates"; this spec rules that trap out by carrying no validation
clause on either plane.

## 4. CLASSIFICATION

**Shimmed on BOTH planes.**

- **Static plane:** Shimmed. The static "assertion" is an unchecked hint the checker
  accepts; it is **not** a dischargeable VC and is not lowered to a `requires`/`ensures`
  obligation in PyCSL. This is the one construct where the static plane does not lower to
  an obligation — recorded here as the honesty point, not as a weakness.
- **Runtime plane:** Shimmed (identity). `ensures \result == val`, no check, no
  conversion.
- **GT gap:** **None.** No gap code is assigned. `cast` is fully specified on both planes
  with no refusal, no loud-fail, and no deferred delivery. (Contrast GT1 `Any`, GT6
  `# type: ignore`, GT7 `Protocol` — `cast`'s honesty is that it carries no obligation to
  refuse or defer.)
- **S5 subset:** empty by construction (no dischargeable static judgment to conform to).
  Recorded as the declared subset for this construct.
