# STRIDE Categories — Definitions, Examples, Countermeasures

Depth reference for the six STRIDE categories. Read the matching section when you
need a precise definition, more examples, or a catalog of mitigations to choose
from. Each category is the negation of one desired security property; fixing a
threat means restoring that property.

## Contents
- Spoofing Identity (authentication)
- Tampering (integrity)
- Repudiation (non-repudiation)
- Information Disclosure (confidentiality)
- Denial of Service (availability)
- Elevation of Privilege (authorization)
- Quick mitigation lookup

---

## Spoofing Identity — violates Authentication

**Definition.** An attacker impersonates a legitimate user, device, or system to
bypass authentication and gain unauthorized access. The attacker assumes a false
identity to lure information or reach protected portals beyond their rights.

**Examples.**
- Stealing credentials or session tokens and logging in as another user.
- Sending email from a forged address to appear as a trusted sender.
- Network-level spoofing: DNS spoofing, ARP spoofing, DNS compromise, IP spoofing
  (e.g., spoofing a trusted IP to bypass firewall rules).
- Presenting fake credentials to a secure API endpoint.

**Countermeasures.** Multi-factor authentication (MFA); certificate-based
authentication and mutual TLS; digital certificates for identity verification;
strong session management; anti-spoofing network controls.

---

## Tampering — violates Integrity

**Definition.** An attacker modifies data, code, or system components without
authorization to alter behavior or corrupt data. Tampering is fundamentally an
attack on integrity, letting an unauthorized party change systems that should be
protected.

**Examples.**
- Intercepting and modifying API requests in transit (e.g., changing a transaction
  amount).
- Injecting malicious code into software updates during the build process.
- Altering a configuration file to gain control, or deleting/replacing a log file
  with a malicious one.

**Countermeasures.** Cryptographic hashing; digital signatures and code signing;
input validation; secure transport (TLS); integrity verification of dependencies
and build artifacts; write-protected/append-only stores for critical data.

---

## Repudiation — violates Non-repudiation

**Definition.** A user or attacker denies performing an action, and the system
cannot prove otherwise. Repudiation threats exist when a system does not record the
controls/evidence needed to attribute actions, so malicious activity cannot be
traced to an actor.

**Examples.**
- A user claims they never made a transfer that they in fact made.
- A malicious insider deletes critical files and denies ever accessing the system.
- An attacker acts in a way that leaves no traceable evidence, or causes wrong data
  to be written to log files.

**Countermeasures.** Comprehensive, tamper-evident logging and audit trails; digital
signatures for non-repudiation; trusted timestamping; user notifications for
sensitive actions (e.g., transfer alerts); append-only or blockchain-based audit
logs; regular audit-log review.

---

## Information Disclosure — violates Confidentiality

**Definition.** Unauthorized access to or exposure of confidential information,
through vulnerabilities, misconfigurations, or weak access controls. It can
compromise the data, processes, and storage of an application.

**Examples.**
- SQL injection used to extract a customer database.
- Sensitive data left in a publicly accessible cloud storage bucket.
- Source code or secrets exposed via temporary backups, verbose error messages, or
  accidental disclosure of background information.
- Intercepting unencrypted traffic to steal data.

**Countermeasures.** Encryption at rest and in transit (e.g., HTTPS everywhere);
least-privilege access controls; data-loss-prevention (DLP) tooling; data masking;
careful error handling that does not leak internals; regular security assessments;
secrets management.

---

## Denial of Service (DoS) — violates Availability

**Definition.** Disrupting system availability by consuming resources, exploiting
vulnerabilities, or overwhelming services so legitimate users cannot access them.
Operates at both the network and application layers and causes costly downtime.

**Examples.**
- Distributed denial-of-service (DDoS) using botnets to flood a service.
- Exploiting an application vulnerability to crash a service with minimal requests.
- Flooding a login endpoint with invalid requests.

**Countermeasures.** DDoS protection services; rate limiting and CAPTCHAs; resource
quotas; auto-scaling infrastructure; circuit breakers and failover; load balancing;
firewalls as a network- and application-layer defense; input/length validation to
prevent cheap crashes.

---

## Elevation of Privilege — violates Authorization

**Definition.** Exploiting weaknesses to gain higher privileges than intended,
reaching restricted resources or administrative functions. Lets an attacker move
from limited access to the ability to steal, manipulate, or exploit more of the
system.

**Examples.**
- Exploiting a buffer overflow to gain root access.
- Leveraging misconfigured permissions to reach admin panels.
- A user starting with read-only access finding a path to modify system settings and
  then edit files they should not, potentially spreading to other files.
- SQL injection used to gain admin rights.

**Countermeasures.** Principle of least privilege; role-based access control (RBAC);
regular privilege reviews; secure coding practices; patch management; privileged
access management (PAM); input sanitization.

---

## Quick mitigation lookup

| Threat | First-reach controls |
|---|---|
| Spoofing | MFA, mutual TLS, certificate-based auth |
| Tampering | Digital signatures, hashing, input validation, TLS |
| Repudiation | Audit logging, signed records, timestamps, notifications |
| Information disclosure | Encryption (rest + transit), least-privilege access, DLP, error hygiene |
| Denial of service | Rate limiting, quotas, auto-scaling, DDoS protection, circuit breakers |
| Elevation of privilege | Least privilege, RBAC, patching, PAM, secure coding |
