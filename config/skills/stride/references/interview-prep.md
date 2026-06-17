# Interview Prep & Key Concepts

High-frequency threat-modeling interview questions with model answers, plus the
conceptual distinctions worth having crisp. Read this when the user is preparing for
a security/threat-modeling interview or wants the key knowledge rather than the
hands-on workflow.

## Core definitions to have ready

**What is STRIDE?** A threat modeling framework developed by Microsoft (Kohnfelder
and Garg, late 1990s) that classifies security threats into six categories:
Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, and
Elevation of privilege. It is built on the CIA triad (Confidentiality, Integrity,
Availability) plus authentication, authorization, and non-repudiation, and answers
"what could go wrong with this system?" by walking each element of a data flow
diagram through the six categories.

**The six categories and the property each violates:**
- Spoofing → authentication
- Tampering → integrity
- Repudiation → non-repudiation
- Information disclosure → confidentiality
- Denial of service → availability
- Elevation of privilege → authorization

**What is DREAD?** A risk-rating method: Damage, Reproducibility, Exploitability,
Affected users, Discoverability. Used to *score and prioritize* threats. Note DREAD's
original form is often considered cumbersome and has been largely simplified or
replaced in practice, but it remains the canonical pairing taught alongside STRIDE.

## Distinctions interviewers probe

**Threat modeling vs risk assessment.** Threat modeling answers "how could an
attacker exploit our system?" — it *identifies* threats and vulnerabilities. Risk
assessment answers "what could go wrong and how bad would it be?" — it *evaluates*
the severity and likelihood of identified risks in business terms. Threat modeling
feeds risk assessment by supplying the technical detail. In practice: use STRIDE to
find that authentication is vulnerable to credential stuffing (threat modeling), then
use DREAD or a risk matrix to decide it is a high business risk needing immediate
investment (risk assessment).

**STRIDE vs OWASP Top 10.** STRIDE is a framework for identifying *threat categories*
during design. The OWASP Top 10 is a list of the most critical real-world web
*vulnerabilities*, used to prioritize specific fixes. STRIDE is design-time and
categorical; OWASP Top 10 is empirical and vulnerability-specific.

**STRIDE vs NIST.** STRIDE is a developer-focused mnemonic for categorizing specific
software threats. NIST 800-154 is a broader, data-centric methodology for risk
assessment and compliance across an entire organization's infrastructure.

**What is a trust boundary?** Any place in the system where data flows and changes
its level of trust; often also an attack boundary. Example: a web server validating
incoming purchase orders raises the trust level of that data once inside. High-trust
data needs fewer restrictions; the scrutiny belongs at the inward crossings.

**What is an attack vector?** The series of steps a threat takes to carry out an
attack; vectors are frequently automated.

## Process questions

**How do you threat model using STRIDE?** Decompose the system into components and
data flows (build a DFD), mark trust boundaries, evaluate each element against the
six categories to enumerate threats, then prioritize by likelihood and impact and
implement countermeasures (encryption, MFA, input validation, etc.). Validate and
iterate.

**The four guiding questions.** What are we working on? (model the system) → What can
go wrong? (enumerate threats) → What are we going to do about it? (mitigate, accept,
transfer, or eliminate) → Did we do a good enough job? (validate and review,
pre-mortem and post-mortem).

**How do you prioritize threats?** Estimate likelihood of occurrence and impact
(data loss, financial, reputational) for each threat, then rank — typically with
DREAD or a likelihood×impact matrix — and address high-priority risks first.

**How do you threat model a web application?** Identify system boundaries (I/O, data
flows, trust boundaries), assess attack vectors (injection, XSS, CSRF, unauthorized
access), then prioritize by likelihood and impact and mitigate during development.

**How do you handle insider threats?** Differently from external threats: identify
what insiders could exploit, enforce least-privilege access control, review audit
logs regularly, detect abnormal behavior, and run security-awareness training.

**Supply-chain / third-party dependency threats.** Extend trust boundaries to
include maintainers and their security practices; model "what if this popular
library is compromised?" and add integrity-verification controls accordingly.

## Modern context (good to mention)

- **Continuous threat modeling / threat modeling as code:** encode models as
  YAML/JSON and validate them in CI/CD so the model evolves with the system.
- **AI-assisted tooling:** tools like STRIDE GPT use LLMs to generate STRIDE threats
  from system descriptions or architecture diagrams, speeding up elicitation.
- **Extensions:** ASTRIDE adds an "A" for AI-agent-specific attacks (prompt
  injection, context poisoning, unsafe tool use); ISADM integrates STRIDE with MITRE
  ATT&CK and D3FEND to add attacker-technique and defense data; strideSEA keeps
  STRIDE as a central classification scheme across the whole SDLC.

## Common pitfalls to name

Subjective scoring without a layered method; high manual effort; models going stale
quickly without a refresh cadence; failing to communicate threats to developers in
plain language (the single most common reason fixes do not happen). Without
automation, STRIDE can struggle to keep pace with rapid CI/CD and evolving cloud
environments — which is the argument for embedding it in the pipeline.
