# CMMI v2.0 Practice Area to Document Type Mapping

This reference maps common organizational document types to the CMMI v2.0
practice areas they satisfy. Use this table when the agent needs to determine
which practice area a target document addresses, or when an appraiser needs
traceability from an artifact back to the model.

## Mapping Table

| Document Type | CMMI v2.0 Practice Area(s) | Abbreviation | Level |
|---|---|---|---|
| Business Requirements Document (BRD) | Requirements Development and Management (RDM) | RDM | — |
| System Requirements Specification (SRS) | Requirements Development and Management (RDM) | RDM | — |
| System Architecture Document (SAD) | Requirements Development and Management (RDM), Verification and Validation (VV) | RDM, VV | — |
| Interface Control Document (ICD) | Requirements Development and Management (RDM), Configuration Management (CM) | RDM, CM | — |
| Component Specification (HLD) | Requirements Development and Management (RDM) | RDM | — |
| Module-Level Design (MLD) | Requirements Development and Management (RDM) | RDM | — |
| Unit Specification (LLD) | Requirements Development and Management (RDM) | RDM | — |
| Software Development Plan | Planning (PLAN), Estimating (EST) | PLAN, EST | — |
| Quality Assurance Plan | Process Quality Assurance (PQA) | PQA | — |
| Configuration Management Procedure | Configuration Management (CM) | CM | — |
| Requirements Specification | Requirements Development and Management (RDM) | RDM | — |
| Peer Review Procedure | Peer Reviews (PR) | PR | — |
| Risk Management Plan | Risk and Opportunity Management (RSK) | RSK | — |
| Supplier Agreement | Supplier Agreement Management (SAM) | SAM | — |
| Training Plan | Organizational Training (OT) | OT | — |
| Process Improvement Plan | Organizational Performance Management (OPM), Managing Performance and Measurement (MPM) | OPM, MPM | — |
| Incident / Problem Management Procedure | Causal Analysis and Resolution (CAR) | CAR | — |
| Verification and Validation Plan | Verification and Validation (VV) | VV | — |
| Decision Analysis Procedure | Decision Analysis and Resolution (DAR) | DAR | — |
| Monitor and Control Procedure | Monitor and Control (MC) | MC | — |
| Governance Framework | Governance (GOV) | GOV | — |
| Implementation Infrastructure Plan | Implementation Infrastructure (II) | II | — |
| Use Case Blueprint | Requirements Development and Management (RDM) — SP 1.1 | RDM | Business |
| Domain Model | Requirements Development and Management (RDM) — SP 1.1 | RDM | Business |
| UAT Plan | Verification and Validation (VV) — SP 1.1 | VV | Business |
| System Test Plan | Verification and Validation (VV) — SP 1.1 | VV | System |
| Component (Integration) Test Plan | Verification and Validation (VV) — SP 1.1 | VV | Component |
| Module Test Plan | Verification and Validation (VV) — SP 1.1 | VV | Module |
| Unit Test Plan / Proof Obligations | Verification and Validation (VV) — SP 1.1 | VV | Unit |

## Maturity Level Coverage

| Maturity Level | Key Practice Areas |
|---|---|
| **Level 2 — Managed** | CM, MC, PLAN, EST, PQA, RDM, SAM, PR, RSK, GOV, II |
| **Level 3 — Defined** | All Level 2 + DAR, OT, VV, CAR + organizational process definition and tailoring |

## Usage Notes

- A single document may satisfy multiple practice areas (e.g., a Software
  Development Plan typically covers both PLAN and EST).
- When generating a document, the agent should cite the specific practice area
  abbreviation in the document's Purpose section and in each relevant ETVX
  workflow heading.
- This mapping follows the CMMI v2.0 unified model. If working with CMMI v1.3
  legacy artifacts, note that v1.3 uses "Process Areas (PAs)" instead of
  "Practice Areas" and separates into DEV/SVC/ACQ constellations.
