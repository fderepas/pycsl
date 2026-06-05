# Measurement and Metrics

*Practice area: MPM SP 1.1 — quantitative tracking of lifecycle execution.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Level completion rate | (levels completed) / (levels in scope) × 100 | Level exit-criteria records | 100% level execution for all projects |
| Specification-verification pairing rate | (levels with passing tests) / (levels with specifications) × 100 | Level records | 100% pairing — no level left unverified |
| Gap closure rate | (gaps closed) / (gaps identified in Phase 1) × 100 | Phase 12 re-run vs Phase 1 | 100% Critical + Major gaps closed |
| Test pass rate per level | (tests passing) / (total tests) × 100 per level | Test execution reports | >95% pass rate at each level |
| Traceability completeness | (requirements with ≥1 test) / (total requirements) × 100 | RTM | 100% traceability |
| Independence compliance | (levels with 3 distinct actors) / (total levels) × 100 | Level records | 100% independence |
| Reconciliation re-work count | Total re-work loops triggered per level per project | Reconciliation logs | Minimize re-work; trend downward over projects |
| Fault attribution distribution | Percentage of faults classified as Specifier / Verifier / Level-below | Reconciliation logs | Identify systemic weaknesses by fault type |

## Metric Collection Path

All lifecycle metrics are collected in `projects/<project>/docs/reports/metrics-collection-<NNN>.md`. Each level completion appends a row. The EPG Lead reviews at Phase 12; the Metrics Analyst archives the final version alongside the SQA audit report. Findings feed into `cmmi-glue` Workflow 4 (Continuous Improvement Loop) to refine the lifecycle for future projects.
