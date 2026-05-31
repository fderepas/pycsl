# SY3-Pycsl — Requirements

**Document ID:** REQ-PYCSL-SY3-001
**Layer:** L2 (System requirements derived from L1 Business Squeezes)
**Source system:** `src/pycsl/`
**Profile:** L
**Squeezes owned:** S1, S3, S6, S9

---

## BL-derived requirements

This System implements the following Business-Level Squeezes
(from `csl-from-scratch` §0.5 via `BL/specifications/main.md`):

- **S1** — CSL contracts (`requires`/`ensures`) — code satisfies the spec
- **S3** — Reference tests + traceability matrix — every grammar production has a passing test
- **S6** — IR schema validation — Module 5 → Module 6 boundary is machine-checkable
- **S9** — Auto-trust tracking — every escape hatch is a tracked bug

System-specific requirements expanding each Squeeze appear in the
companion [`../specifications/main.md`](../specifications/main.md).
