# Annotated Bibliography — ACSL, MetAcsl, Frama-C

Primary sources and real-world corpora, grouped by purpose. Citations are given
in author/title form so they can be located even if a URL rots.

## Language and platform references (start here)

- **ACSL: ANSI/ISO C Specification Language** — Baudin, Filliâtre, Marché,
  Monate, Moy, Prevosto (the language reference manual; frama-c.com/acsl.html).
  The normative definition of every clause and predicate. Consult for exact
  semantics and the executable (E-ACSL) subset.
- **Frama-C: A Software Analysis Perspective** — Kirchner, Kosmatov, Prevosto,
  Signoles, Yakobowski, *Formal Aspects of Computing* 27(3), 2015. The platform
  overview: architecture, plug-ins, and how analyses combine.
- **Frama-C/WP Plug-in Manual** — Baudin, Bobot, Correnson, Dargaye, Blanchard
  (versioned per release, e.g. 26.1 "Iron"). The deductive-verification engine:
  memory models, prover integration, tactics.
- **Guide to Software Verification with Frama-C: Core Components, Usages, and
  Applications** — Kosmatov, Prevosto, Signoles (eds.), Springer, 2024. The most
  complete single modern resource: ACSL, core plug-ins, advanced analyses, *and*
  industrial case studies in one place. The high-level-properties chapter
  (Blatter, Kosmatov, Prevosto, Robles) covers MetAcsl, plus RPP and other
  dedicated specification front-ends.

## Learning by example

- **ACSL by Example — Towards a Verified C Standard Library** — Jens Gerlach,
  Fraunhofer FOKUS. Curated, continuously maintained (v32+, tracking recent
  Frama-C releases; repo: github.com/fraunhoferfokus/acsl-by-example). STL-style
  algorithms and data structures, each specified and proved with WP, with a
  report explaining the patterns. The best idiom corpus.
- **A Lesson on Proof of Programs with Frama-C** (Kosmatov, Signoles, TAP 2013
  tutorial) and **A Lesson on Runtime Assertion Checking with Frama-C** —
  tutorial-style introductions.
- **Allan Blanchard's WP/ACSL tutorial** (allan-blanchard.fr) — beginner-friendly,
  English and French.

## MetAcsl — primary sources

- **MetAcsl: Specification and Verification of High-Level Properties** — Robles,
  Kosmatov, Prevosto, Rilling, Le Gall, **TACAS 2019** (LNCS 11427, pp. 358–364);
  extended version arXiv:1811.10509. The tool paper: meta-properties, contexts,
  the transformation, and the confidentiality case study used throughout this
  skill.
- **Tame Your Annotations with MetAcsl: Specifying, Testing and Proving
  High-Level Properties** — same authors, **TAP 2019** (LNCS 11823). The detailed
  journal-style treatment; shows amenability to both proof *and* testing.
- **High-Level Program Properties in Frama-C: Definition, Verification and
  Deduction** — Robles, Kosmatov, Prevosto, Le Gall, **ISoLA 2024** (LNCS 15221).
  The most recent overview, including the cost of the annotation blow-up and
  deduction techniques to manage it.
- **MetAcsl plug-in page & repo** — frama-c.com/fc-plugins/metacsl.html;
  git.frama-c.com/pub/meta; opam package `frama-c-metacsl` (companion release per
  Frama-C version since 22.0 Titanium). The authoritative, version-matched
  concrete syntax lives here.

## Real-world / industrial case studies (genuine "real-life" ACSL)

- **Formal Verification of a JavaCard Virtual Machine with Frama-C** — Djoudi,
  Hána, Kosmatov, **FM 2021**. The EAL6 case the user remembered: a Thales JCVM,
  >7,000 lines of C, >52,000 proof goals, ACSL + WP + MetAcsl, for a Common
  Criteria **EAL6** certificate. The largest published deductive-verification
  effort on a real industrial smart-card product.
- **Contiki (IoT OS)** — a cluster of case studies on real OS code:
  - *Ghosts for Lists: A Critical Module of Contiki Verified in Frama-C* —
    Blanchard, Kosmatov, Loulergue, **NFM 2018** (companion-ghost-array technique
    for a non-classical linked-list API).
  - *Logic against Ghosts: comparison of two proof approaches for a list module*
    — Blanchard, Kosmatov, Loulergue, 2019 (logic-list alternative).
  - *Formal Verification of a Memory Allocation Module of Contiki* — Mangano,
    Duquennoy, Kosmatov.
  - *Towards Formal Verification of Contiki: Analysis of the AES–CCM* Modules* —
    Peyrard, Kosmatov, Duquennoy, Raza (cryptographic modules).
- **Linux kernel** — *Lemma Functions for Frama-C: C Programs as Proofs* (Volkov,
  Mandrykin, Efremov, 2018), the **VerKer** project on kernel string functions
  with the AstraVer tool; later work on the kernel scheduler (Lawall et al.,
  2025). Showcases auto-active verification via lemma functions.
- **Hypervisor** — *A Case Study on Formal Verification of the Anaxagoros
  Hypervisor Paging System with Frama-C* — Blanchard, Kosmatov, Lemerre,
  Loulergue, **FMICS 2015** (isolation/memory-separation, a motivating source for
  MetAcsl).
- **Aerospace** — air-traffic-management algorithm verification (Dutle et al.,
  2021); a report on using ACSL to express low-level requirements in a
  **DO-178C**-compliant project (arXiv:1508.03894).

## How to choose what to read

- *Just learning the language*: ACSL manual + ACSL by Example.
- *Doing a real proof*: WP manual + ACSL by Example idioms + the 2024 Guide.
- *Cross-cutting security property*: the MetAcsl TACAS/TAP papers + the JCVM EAL6
  paper for how it scales to certification.
- *Want a maintained corpus to mine*: ACSL by Example and the Frama-C
  book-companion repository.
