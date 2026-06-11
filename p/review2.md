# Second review of `p/os.tex` (independent of `p/reveiew.md`)

This review is a fresh critical reading focused on **accuracy against the
actual artifact**, claims that over/understate, and missing context. It does
not repeat the existing review's points (missing metrics, repo-URL
inconsistency, "Module 6" naming, duality intuition, `\resizebox`, prose
polish). Where I assert a number, it was computed from the tree (see
`p/answer.md`).


---

## C. Missing context the paper should add

### C1. The test-must-call-the-API discipline
The "formal test" §6 is the paper's methodological centerpiece, but it omits
the discipline that makes it sound: **a formal test must CALL the public API,
never simulate the operation on the data structure**. The project enforces this
(the consequence drivers go through the imported `os.mkdir`/`os.open` wrappers,
not the internal `sys_*`), and it is precisely what distinguishes a
"consequence" proof from a vacuous self-assertion. One paragraph stating this
rule — and that a test asserting an op's own return code is treated as vacuous —
would pre-empt the "how do we know the formal test isn't trivially true?"
objection and sharpen the contribution.

### C2. The dual-kernel cross-validation is under-substantiated
§5.2 lists the trust conditions but never says how many lemmas were actually
cross-validated or where the artifacts live. State it: **6 Rocq `.v` + 6 Lean
`.lean` files** for the directory family in
`unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/`, with `.vok`/`.vos`
evidencing kernel acceptance, audited by `src/pycsl/audit_proof.py`. Concrete
artifact pointers make the "machine-audited" claim checkable.

### C3. Backend versions are inconsistent across the paper's own machinery
The paper pins Alt-Ergo 2.6.2 / Z3 4.13.3 (good). It should also pin the
offline kernels it relies on for the registry: **Rocq/Coq 8.20.1 and Lean
4.30.0** (both present in the tool: `pycsl.py -P Coq,8.20.1`, `preamble.py`
Lean 4.30.0 audit notes). A registry whose soundness rests on two kernels
should name their versions.

### C4. LOS:LOC is computable now — give it
The review's final question asks for the LOS:LOC ratio. It is **743:1215 ≈
0.61:1** (≈ 1 spec line per 1.6 code lines; full breakdown in `p/answer.md`).
This is a cheap, defensible descriptive metric that directly answers the
"missing metrics" objection. The PyCSL tool itself is **~39.3 K LoC** — worth a
sentence to convey the engineering scale behind a "small case study."

---

## D. Structural / clarity suggestions

### D1. The body-VC count is the missing headline number
The paper repeatedly says "zero unproven goals" but never says *how many goals*.
"0 unproven of ~1200 body VCs" is far more convincing than "0 unproven" alone —
the denominator is what makes "zero" meaningful. Add the VC count (the
artifact's logs put the `os` body at ~1191–1480 VCs depending on which
consequence layer is active; pick the configuration the paper's numbers
correspond to and state it).

### D2. Separate "module-level proved" from "API-level proved" once, early
The paper's strongest and weakest claims both live in the gap between
*module/body-level* verification (genuinely complete, 0 unproven) and
*public-import-API consequence* proofs (namespace 7/7, fd 3/5). Define these two
levels explicitly in §5 or §6 and use the terms consistently thereafter; almost
all of A1/A2 above are really one unstated distinction surfacing repeatedly.

### D3. §7.4 and §8(3) could be merged or cross-linked
The non-vacuity argument appears twice (the §7.3 mechanism and the §8(3)
contribution) with significant overlap. Tighten: state the mechanism once, cite
it from the contributions list.

### D4. The convergence narrative (47→39→23→0) is a selling point and is absent
The artifact's own record of driving the unproven count from 47 down to 0 by a
faithful (non-totalizing, no-new-axiom) path is a compelling, honest engineering
story and directly supports the "auto-active is practical" thesis. A two-line
mention (with the trail) would humanize the result and pre-empt "did you just
weaken the contracts until they proved?" — the answer (no totalization, no new
axioms, contracts strengthened) is exactly what a skeptic wants to hear.

---

## E. Net assessment

The paper is strong and the core result — a fully discharged WP proof of a
byte-faithful `os` filesystem model in idiomatic typed Python, with a
dual-kernel audited axiom registry — is real and well-told. 