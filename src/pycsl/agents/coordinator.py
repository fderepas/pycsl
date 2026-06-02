#!/usr/bin/env python3
"""
Coordinator Agent for PyCSL Testing and Reconciliation.

Orchestrates the full workflow:
1. Clean tests/annotated/ directory
2. Annotate all test files in tests/to_annotate/ using agent-annotate.py
3. Run pycsl proof on each annotated file
4. On proof failure, run agent-reconcile.py
5. Apply recommendations using agent-script-update.py
6. On exhausted retries, generate Rocq proof obligations via agent-rocq-proof-writer.py

Loop-detection: if agent-reconcile produces the same recommendation 3 times in a row
the coordinator halts with exit code 73 so a human can intervene.

Cross-level (L5->L4) reconciliation: agent-reconcile classifies each failure's
fault_class. A "specifier" fault (the file's decomposition / callee-contract
ordering is wrong, not this unit's body) escalates to L4 — the coordinator
re-decomposes the file via agent-splitter instead of re-patching the unit. A
per-file MAX_REDECOMPOSE cap bounds L5<->L4 ping-pong, halting via exit 73.

Workflow-3 escalation: on halt (72 or 73) the coordinator emits a Non-Conformance
Report (NCR) conforming to cmmi-glue Workflow 3 (the escalation chain
`coordinator exit 72/73 -> agent-meta-monitor -> agent-feature-supervisor -> human`
is bound in config/skills/cmmi-glue/SKILL.md), then agent-meta-reviewer produces a
human-readable report.

Meta-observability: after each fix attempt agent-meta-evaluator assesses the change.
After each file's retry loop agent-meta-monitor checks operational health.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import coordinator_loopdetect as loop_detect

AGENT_NAME = "coordinator"
EXIT_MAX_RETRIES = 72    # pycsl still failing after MAX_RETRIES attempts
EXIT_LOOP_DETECTED = 73  # same recommendation 3× in a row — human needed
MAX_REDECOMPOSE = 2      # per-file cap on L5->L4 re-decomposition (ping-pong guard)


class CoordinatorAgent:
    def __init__(self, pycsl_dir: Path):
        self.pycsl_dir = pycsl_dir
        self.agents_dir = self.pycsl_dir / "src" / "pycsl" / "agents"
        self.config_dir = self.pycsl_dir / "config"
        self.tests_dir = self.pycsl_dir / "tests"
        self.to_annotate_dir = self.tests_dir / "to_annotate"
        self.annotated_dir = self.tests_dir / "annotated"
        self.pycsl_bin = self._find_pycsl_bin()
        self.venv_activate = self.pycsl_dir / ".venv" / "bin" / "activate"
        self.metrics_dir = self.pycsl_dir / "metrics"

    def _find_pycsl_bin(self) -> Path:
        """Locate the pycsl binary: .venv/bin/pycsl > PATH > src/pycsl/pycsl.py."""
        venv_bin = self.pycsl_dir / ".venv" / "bin" / "pycsl"
        if venv_bin.exists():
            return venv_bin
        which = shutil.which("pycsl")
        if which:
            return Path(which)
        src_bin = self.pycsl_dir / "src" / "pycsl" / "pycsl.py"
        if src_bin.exists():
            return src_bin
        return venv_bin  # will fail with a clear error later

    def init_metrics(self) -> None:
        """Create the metrics/ directory tree at startup."""
        for subdir in ("logs", "evaluator", "monitor", "reviewer", "ncr"):
            (self.metrics_dir / subdir).mkdir(parents=True, exist_ok=True)
        self.log(f"Metrics directory initialized at {self.metrics_dir}")

    def log(self, message: str) -> None:
        print(f"[{AGENT_NAME}] {message}")

    # Loop-detection (exit-73 trigger) lives in `coordinator_loopdetect`; these
    # delegators keep the class API stable for callers/tests.
    @staticmethod
    def _rec_key(rec: dict) -> tuple[str, str]:
        return loop_detect.rec_key(rec)

    @staticmethod
    def _are_similar(rec1: dict, rec2: dict) -> bool:
        return loop_detect.are_similar(rec1, rec2)

    def _consecutive_similar(self, new_rec: dict, history: list[dict]) -> int:
        return loop_detect.consecutive_similar(new_rec, history)

    def run_command(
        self,
        cmd: list,
        cwd: Optional[Path] = None,
        check: bool = True,
        capture: bool = False,
        log_file: Optional[Path] = None,
    ) -> subprocess.CompletedProcess:
        """Run a command and return the result.

        When log_file is provided and capture=True, stdout+stderr are also written
        to that file so the meta-agents can read them afterwards.
        """
        self.log(f"Running: {' '.join(str(c) for c in cmd)}")
        result = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True, check=check)
        if capture and result.stdout:
            self.log(f"  STDOUT: {result.stdout}")
        if capture and result.stderr:
            self.log(f"  STDERR: {result.stderr}")
        if log_file is not None and capture:
            try:
                log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(log_file, "w", encoding="utf-8") as f:
                    if result.stdout:
                        f.write("=== STDOUT ===\n")
                        f.write(result.stdout)
                        f.write("\n")
                    if result.stderr:
                        f.write("=== STDERR ===\n")
                        f.write(result.stderr)
                        f.write("\n")
            except Exception as e:
                self.log(f"  WARNING: Could not write log file {log_file}: {e}")
        return result

    def clean_annotated(self) -> bool:
        """Clean the tests/annotated/ directory."""
        self.log("Step 1: Cleaning tests/annotated/ directory...")
        if not self.annotated_dir.exists():
            self.log("  annotated/ directory does not exist, creating it.")
            self.annotated_dir.mkdir(parents=True, exist_ok=True)
            return True

        try:
            for file in self.annotated_dir.glob("*"):
                if file.is_file():
                    file.unlink()
                    self.log(f"  Removed {file.name}")
            self.log("  Cleaned annotated/ directory.")
            return True
        except Exception as e:
            self.log(f"  ERROR: Failed to clean annotated/ directory: {e}")
            return False

    def annotate_file(self, test_file: Path) -> bool:
        """Annotate a single file from tests/to_annotate/ into tests/annotated/."""
        out_file = self.annotated_dir / test_file.name
        self.log(f"  Annotating {test_file.name}...")

        cmd = [
            "python",
            str(self.agents_dir / "agent-annotate.py"),
            "--in",
            str(test_file),
            "--out",
            str(out_file),
        ]

        result = self.run_command(cmd, cwd=self.pycsl_dir, check=False, capture=True)

        if result.returncode != 0:
            self.log(f"  ERROR: Failed to annotate {test_file.name} (exit {result.returncode})")
            if result.stdout:
                self.log(f"  Agent stdout:\n{result.stdout}")
            if result.stderr:
                self.log(f"  Agent stderr:\n{result.stderr}")
            return False

        self.log(f"  Annotated {test_file.name} -> {out_file.name}")
        return True

    def reconcile_failure(
        self,
        annotated_file: Path,
        out_std: Path,
        out_err: Path,
        ret_code: int,
        attempt: int,
    ) -> tuple[Optional[dict], Optional[Path]]:
        """Run agent-reconcile on a failed file.

        Returns (recommendation_dict, log_path). log_path is where the agent's
        stdout/stderr was captured (written to metrics/logs/).
        """
        self.log(f"Step 4: Running agent-reconcile for {annotated_file.name}...")

        reconcile_out = self.pycsl_dir / f"reconcile_{annotated_file.name}.json"
        log_path = self.metrics_dir / "logs" / f"reconcile_{annotated_file.stem}_{attempt}.log"

        cmd = [
            "python",
            str(self.agents_dir / "agent-reconcile.py"),
            "--script",
            str(annotated_file),
            "--stdout",
            str(out_std),
            "--stderr",
            str(out_err),
            "--ret-code",
            str(ret_code),
            "--out",
            str(reconcile_out),
        ]

        result = self.run_command(
            cmd, cwd=self.pycsl_dir, check=False, capture=True, log_file=log_path
        )

        if result.returncode != 0:
            self.log(f"  ERROR: agent-reconcile failed for {annotated_file.name}")
            return None, log_path

        try:
            with open(reconcile_out, "r", encoding="utf-8") as f:
                recommendation = json.load(f)
            self.log(f"  Reconciliation recommendation: {recommendation}")
            return recommendation, log_path
        except Exception as e:
            self.log(f"  ERROR: Failed to parse reconciliation JSON: {e}")
            return None, log_path

    def apply_recommendations(
        self,
        recommendation: dict,
        reconcile_out: Path,
        annotated_file: Path,
        attempt: int,
        is_similar: bool = False,
        history_file: Optional[Path] = None,
    ) -> tuple[bool, list[str]]:
        """Apply the recommendation using agent-script-update.py.

        Returns (success, files_changed). files_changed is populated from the
        history file written by agent-script-update.py.
        """
        self.log(
            f"Step 5: Applying recommendations (target: {recommendation.get('target')}"
            f"{', SIMILAR — trying different approach' if is_similar else ''})..."
        )

        if recommendation.get("target") not in ("update-pycsl-scripts", "error-in-annotations"):
            self.log(f"  WARNING: Unknown target: {recommendation.get('target')}")
            return False, []

        try:
            config_path = self.config_dir / "agents-config.json"
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)  # noqa: F841 — kept for future use
        except Exception as e:
            self.log(f"  ERROR: Failed to load config: {e}")
            return False, []

        log_path = self.metrics_dir / "logs" / f"update_{annotated_file.stem}_{attempt}.log"

        cmd = [
            "python",
            str(self.agents_dir / "agent-script-update.py"),
            "--recommendation",
            str(reconcile_out),
            "--config",
            str(config_path),
            "--annotated-file",
            str(annotated_file),
        ]

        if history_file is not None:
            cmd += ["--history-file", str(history_file)]

        if is_similar:
            cmd.append("--is-similar")

        result = self.run_command(
            cmd, cwd=self.pycsl_dir, check=False, capture=True, log_file=log_path
        )

        if result.returncode != 0:
            self.log("  ERROR: agent-script-update failed")
            return False, []

        # Retrieve files_changed from the history file written by the update agent
        files_changed: list[str] = []
        if history_file is not None and history_file.exists():
            try:
                history = json.loads(history_file.read_text(encoding="utf-8"))
                if history:
                    files_changed = history[-1].get("files_changed", [])
            except Exception as e:
                self.log(f"  WARNING: Could not read history file for files_changed: {e}")

        self.log(f"  SUCCESS: Recommendations applied. Files changed: {files_changed}")
        return True, files_changed

    def run_pycsl_file(self, annotated_file: Path) -> bool:
        """Run pycsl on a single annotated file. Captures output to out.std/out.err. Returns True on success."""
        if not self.pycsl_bin.exists():
            self.log(f"  ERROR: pycsl binary not found at {self.pycsl_bin}")
            return False

        self.log(f"  Running pycsl on {annotated_file.name}...")
        cmd = [str(self.pycsl_bin), "--keep-mlw", str(annotated_file)]
        result = self.run_command(cmd, cwd=self.pycsl_dir, check=False, capture=True)

        # Always write captured output so agent-reconcile gets fresh context.
        (self.pycsl_dir / "out.std").write_text(result.stdout or "", encoding="utf-8")
        (self.pycsl_dir / "out.err").write_text(result.stderr or "", encoding="utf-8")

        if result.returncode == 0:
            self.log(f"  SUCCESS: {annotated_file.name} passed pycsl proof")
            return True
        else:
            self.log(f"  FAILED: {annotated_file.name} failed pycsl proof")
            if result.stdout:
                self.log(f"  stdout: {result.stdout}")
            if result.stderr:
                self.log(f"  stderr: {result.stderr}")
            return False

    # ------------------------------------------------------------------ RAG index

    def rebuild_rag_index(self) -> bool:
        """Rebuild the RAG index from skill files after a skill update.

        Returns True on success, False on failure (Ollama unreachable, etc.).
        """
        try:
            skill_dir = str(self.config_dir / "skills")
            index_path = str(self.pycsl_dir / "data" / "embeddings" / "skills_index.json")

            sys.path.insert(0, str(self.pycsl_dir / "src"))
            from skill2rag.indexer import build_index

            self.log("Rebuilding RAG index after skill file update...")
            build_index(skill_dir=skill_dir, index_path=index_path)
            self.log(f"RAG index rebuilt at {index_path}")
            return True
        except Exception as e:
            self.log(f"WARNING: Could not rebuild RAG index: {e}")
            return False

    # ------------------------------------------------------------------ Rocq fallback

    @staticmethod
    def _parse_rocq_marker(stdout: str, returncode: int) -> tuple[Optional[int], str]:
        """Parse the ROCQ-SUMMARY marker emitted by agent-rocq-proof-writer.

        Returns (retries_used, status) where status is completed|aborted|incomplete.
        Falls back to the exit code when the marker is absent."""
        for line in (stdout or "").splitlines():
            line = line.strip()
            if line.startswith("ROCQ-SUMMARY "):
                try:
                    obj = json.loads(line[len("ROCQ-SUMMARY "):])
                    return obj.get("retries"), obj.get("status", "incomplete")
                except Exception:
                    break
        return None, ("completed" if returncode == 0 else "incomplete")

    def attempt_rocq_proof(self, annotated_file: Path) -> tuple[bool, Optional[dict]]:
        """Generate Rocq proof obligations and attempt to complete them.

        Called when SMT provers exhaust all retries. Uses pycsl --rocq to
        generate .v skeletons, then calls agent-rocq-proof-writer on each.

        Returns (all_ok, rocq_summary) where rocq_summary is the L4 accounting
        {generated, completed, aborted, incomplete, obligations:[{name,retries,status}]}
        or None if Rocq generation could not run.
        """
        rocq_dir = self.pycsl_dir / "to_be_proven" / annotated_file.stem
        rocq_dir.mkdir(parents=True, exist_ok=True)

        self.log(f"  Step 6: Generating Rocq proof obligations for {annotated_file.name}...")

        # Generate .v skeletons via pycsl --rocq
        cmd = [str(self.pycsl_bin), "--keep-mlw", "--rocq", str(rocq_dir), str(annotated_file)]
        result = self.run_command(cmd, cwd=self.pycsl_dir, check=False, capture=True)

        if result.returncode not in (0, 2):
            self.log(f"  ERROR: pycsl --rocq failed (exit {result.returncode})")
            if result.stderr:
                self.log(f"  stderr: {result.stderr}")
            return False, None

        # Find generated .v files
        v_files = sorted(rocq_dir.glob("*.v"))
        if not v_files:
            self.log("  WARNING: No .v files generated")
            return False, {"generated": 0, "completed": 0, "aborted": 0,
                           "incomplete": 0, "obligations": []}

        self.log(f"  Generated {len(v_files)} .v file(s)")

        # Find .mlw file for context
        mlw_files = list(rocq_dir.glob("*.mlw"))
        mlw_path = mlw_files[0] if mlw_files else None

        # Attempt to complete each .v file via agent-rocq-proof-writer
        all_ok = True
        obligations: list[dict] = []
        tally = {"completed": 0, "aborted": 0, "incomplete": 0}
        for v_file in v_files:
            self.log(f"  Completing proof: {v_file.name}...")
            out_file = v_file  # overwrite in place

            cmd = [
                "python",
                str(self.agents_dir / "agent-rocq-proof-writer.py"),
                "--in", str(v_file),
                "--out", str(out_file),
            ]
            if mlw_path:
                cmd += ["--mlw", str(mlw_path)]

            log_path = self.metrics_dir / "logs" / f"rocq_{v_file.stem}.log"
            agent_result = self.run_command(
                cmd, cwd=self.pycsl_dir, check=False, capture=True, log_file=log_path
            )

            retries, status = self._parse_rocq_marker(
                agent_result.stdout, agent_result.returncode)
            tally[status] = tally.get(status, 0) + 1
            obligations.append({"name": v_file.name, "retries": retries, "status": status})

            if agent_result.returncode == 0:
                self.log(f"  ✓ {v_file.name} — proof completed (retries={retries})")
            else:
                self.log(f"  ✗ {v_file.name} — proof {status} (retries={retries})")
                all_ok = False

        status_msg = "all completed" if all_ok else "some incomplete"
        self.log(f"  Rocq proofs: {status_msg}. Files in {rocq_dir}/")
        rocq_summary = {
            "generated": len(v_files),
            "completed": tally["completed"],
            "aborted": tally["aborted"],
            "incomplete": tally["incomplete"],
            "obligations": obligations,
        }
        return all_ok, rocq_summary

    # ------------------------------------------------------------------ meta agents

    def run_meta_evaluator(
        self,
        annotated_file: Path,
        modified_files: list[str],
        attempt: int,
    ) -> Optional[Path]:
        """Run agent-meta-evaluator after a successful update. Returns output JSON path or None."""
        if not modified_files:
            self.log("  META: No modified files reported — skipping evaluator")
            return None

        out_path = self.metrics_dir / "evaluator" / f"{annotated_file.stem}_{attempt}.json"

        for mf_str in modified_files:
            mf = Path(mf_str)
            if not mf.is_absolute():
                mf = self.pycsl_dir / mf
            if not mf.exists():
                self.log(f"  META: modified file not found: {mf} — skipping")
                continue

            cmd = [
                "python",
                str(self.agents_dir / "agent-meta-evaluator.py"),
                "--annotated-file", str(annotated_file),
                "--modified-file", str(mf),
                "--out", str(out_path),
            ]
            result = self.run_command(cmd, cwd=self.pycsl_dir, check=False, capture=True)
            if result.returncode != 0:
                self.log(f"  META: agent-meta-evaluator failed for {mf.name}")
            else:
                self.log(f"  META: Evaluator wrote {out_path}")
            break  # evaluate the first valid modified file

        return out_path if out_path.exists() else None

    def run_meta_monitor(
        self,
        file_stem: str,
        reconcile_log_paths: list[Path],
        update_log_paths: list[Path],
    ) -> Optional[Path]:
        """Run agent-meta-monitor after all retry attempts for a file. Returns JSON path or None."""
        out_path = self.metrics_dir / "monitor" / f"{file_stem}.json"

        # Merge per-attempt logs into a single combined log for each agent
        combined_reconcile = self.metrics_dir / "logs" / f"reconcile_{file_stem}_combined.log"
        combined_update = self.metrics_dir / "logs" / f"update_{file_stem}_combined.log"

        for combined, paths in (
            (combined_reconcile, reconcile_log_paths),
            (combined_update, update_log_paths),
        ):
            lines: list[str] = []
            for p in paths:
                if p and p.exists():
                    lines.append(f"=== {p.name} ===\n")
                    lines.append(p.read_text(encoding="utf-8"))
            combined.write_text("".join(lines), encoding="utf-8")

        cmd = [
            "python",
            str(self.agents_dir / "agent-meta-monitor.py"),
            "--reconcile-log", str(combined_reconcile),
            "--update-log", str(combined_update),
            "--out", str(out_path),
        ]
        result = self.run_command(cmd, cwd=self.pycsl_dir, check=False, capture=True)
        if result.returncode != 0:
            self.log(f"  META: agent-meta-monitor failed for {file_stem}")
            return None
        self.log(f"  META: Monitor wrote {out_path}")
        return out_path

    def run_meta_reviewer(
        self,
        annotated_file: Path,
        reconcile_out: Optional[Path],
        eval_json: Optional[Path],
        monitor_json: Optional[Path],
    ) -> None:
        """Run agent-meta-reviewer (called on halt 72/73). Writes to metrics/reviewer/."""
        file_stem = annotated_file.stem
        out_json = self.metrics_dir / "reviewer" / f"{file_stem}.json"
        out_md = self.metrics_dir / "reviewer" / f"{file_stem}.md"
        config_path = self.config_dir / "agents-config.json"

        cmd = [
            "python",
            str(self.agents_dir / "agent-meta-reviewer.py"),
            "--reconcile-json", str(reconcile_out or ""),
            "--eval-json", str(eval_json or ""),
            "--monitor-json", str(monitor_json or ""),
            "--out-json", str(out_json),
            "--out-md", str(out_md),
            "--config", str(config_path),
        ]
        result = self.run_command(cmd, cwd=self.pycsl_dir, check=False, capture=True)
        if result.returncode != 0:
            self.log(f"  META: agent-meta-reviewer failed for {file_stem}")
        else:
            self.log(f"  META: Reviewer wrote {out_json} and {out_md}")

    # ------------------------------------------------------------------ Workflow-3 NCR

    # The Workflow-3 escalation chain this NCR feeds (see cmmi-glue/SKILL.md
    # Profile-P binding: coordinator exit 72/73 -> meta-monitor -> supervisor -> human).
    ESCALATION_PATH = (
        "coordinator exit {code} -> agent-meta-monitor -> agent-feature-supervisor "
        "-> human review (cmmi-glue Workflow 3)"
    )

    @staticmethod
    def _responsible_role(recommendation: Optional[dict]) -> str:
        """Map the reconcile target to the CMMI engineering role bound to remediate."""
        target = (recommendation or {}).get("target")
        if target == "error-in-annotations":
            return "Specifier (agent-writer / agent-splitter)"
        if target == "update-pycsl-scripts":
            return "Sub-actor (agent-script-update)"
        return "Unknown"

    def write_ncr(
        self,
        *,
        exit_code: int,
        annotated_file: Path,
        recommendation: Optional[dict],
        attempt: int,
        consecutive: Optional[int] = None,
        log_paths: Optional[list[Path]] = None,
        finding: Optional[str] = None,
    ) -> Optional[Path]:
        """Emit a Workflow-3 Non-Conformance Report when the loop cannot converge.

        Deterministic governance artifact (NOT the LLM meta-reviewer): always written,
        schema-validated, so the escalation chain has a concrete record even if the
        reviewer LLM call later fails. Returns the NCR path (or None on write error).
        """
        try:
            from schema_validator import validate_or_warn
        except Exception:  # pragma: no cover — validator is optional
            validate_or_warn = None

        now = datetime.now(timezone.utc)
        ts = now.strftime("%Y%m%dT%H%M%SZ")
        stem = annotated_file.stem
        ncr_id = f"NCR-{ts}-{stem}"

        if finding is None:
            if exit_code == EXIT_MAX_RETRIES:
                finding = (
                    f"Automated reconciliation could not produce a passing artifact "
                    f"for {annotated_file.name} after {attempt + 1} attempts (max retries)."
                )
            else:
                finding = (
                    f"Reconciliation loop detected for {annotated_file.name}: the same "
                    f"recommendation recurred {(consecutive or 0) + 1} times without resolution."
                )

        ncr = {
            "ncr_id": ncr_id,
            "date_issued": now.isoformat(),
            "issued_by": AGENT_NAME,
            "responsible_role": self._responsible_role(recommendation),
            "checkpoint": f"PyCSL annotate->prove->reconcile loop for {annotated_file.name}",
            "finding": finding,
            "gate_failed": "Gate 1",
            "evidence": {
                "exit_code": exit_code,
                "retry_count": attempt + 1,
                "consecutive_identical": consecutive,
                "recurring_recommendation": (recommendation or {}).get("recommendation"),
                "target": (recommendation or {}).get("target"),
                "fault_class": (recommendation or {}).get("fault_class"),
                "log_paths": [str(p) for p in (log_paths or [])],
            },
            "severity": "high",
            "response_timeframe": "5 business days",
            "escalation_path": self.ESCALATION_PATH.format(code=exit_code),
            "cap_placeholder": "",
            "status": "OPEN",
        }

        if validate_or_warn is not None:
            validate_or_warn(ncr, "ncr", logger=self.log)

        out_dir = self.metrics_dir / "ncr"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{ncr_id}.md"
        body = (
            f"# Non-Conformance Report — {ncr_id}\n\n"
            f"- **Issued by:** {ncr['issued_by']} (SQA Auditor role)\n"
            f"- **Date:** {ncr['date_issued']}\n"
            f"- **Responsible role:** {ncr['responsible_role']}\n"
            f"- **Checkpoint:** {ncr['checkpoint']}\n"
            f"- **Gate failed:** {ncr['gate_failed']}\n"
            f"- **Severity:** {ncr['severity']}\n"
            f"- **Response timeframe:** {ncr['response_timeframe']}\n"
            f"- **Status:** {ncr['status']}\n\n"
            f"## Finding\n\n{ncr['finding']}\n\n"
            f"## Escalation path\n\n{ncr['escalation_path']}\n\n"
            f"## Corrective Action Plan\n\n_(to be completed by the responsible role)_\n\n"
            f"## Machine record\n\n```json\n{json.dumps(ncr, indent=2)}\n```\n"
        )
        try:
            out_path.write_text(body, encoding="utf-8")
        except Exception as e:
            self.log(f"  ERROR: Could not write NCR {out_path}: {e}")
            return None
        self.log(f"  NCR {ncr_id} emitted per cmmi-glue Workflow 3 -> {out_path}")
        return out_path

    # ------------------------------------------------------------------ L4 re-decomposition

    def redecompose_at_l4(self, test_file: Path, annotated_file: Path, attempt: int) -> bool:
        """Cross-level escalation: re-decompose the file at L4 via agent-splitter.

        Invoked when agent-reconcile classifies the fault as "specifier" — the
        file's decomposition / callee-contract ordering is wrong, so re-patching the
        unit (L5) cannot fix it. agent-splitter is the L4 actor that revises the
        call-graph decomposition. Writes directly into annotated/; the caller must
        skip the next iteration's fresh re-annotate so this artifact is the one proved.
        """
        self.log(f"  L4 ESCALATION: re-decomposing {test_file.name} via agent-splitter...")
        log_path = self.metrics_dir / "logs" / f"redecompose_{test_file.stem}_{attempt}.log"
        cmd = [
            "python",
            str(self.agents_dir / "agent-splitter.py"),
            "--in", str(test_file),
            "--out", str(annotated_file),
        ]
        result = self.run_command(
            cmd, cwd=self.pycsl_dir, check=False, capture=True, log_file=log_path
        )
        if result.returncode != 0:
            self.log(f"  ERROR: agent-splitter re-decomposition failed for {test_file.name}")
            return False
        self.log(f"  L4 ESCALATION: {test_file.name} re-decomposed -> {annotated_file.name}")
        return True

    # ------------------------------------------------------------------ L4 run summary

    def write_run_summary(
        self,
        *,
        test_file: Path,
        attempts: list[dict],
        outcome: str,
        exit_code: Optional[int] = None,
        rocq_summary: Optional[dict] = None,
        ncr_emitted: bool = False,
    ) -> Optional[Path]:
        """Emit the per-file CMMI Level-4 run summary to metrics/run-summary/.

        Computes inter-agent loop counters, the reconciliation diagnostic-accuracy
        DOWNSTREAM PROXY (a recommendation+action at attempt i is "right" iff the
        next attempt's proof passes), and folds in the Rocq accounting. Deterministic;
        validated against run-summary.schema.json.
        """
        # Downstream proxy: link each attempt's reconcile/action to the next
        # attempt's pycsl outcome.
        by_class: dict[str, dict] = {}
        overall = {"correct": 0, "total": 0}
        rec_keys: list[str] = []
        for i, att in enumerate(attempts):
            rec = att.get("reconcile") or {}
            if rec.get("rec_key"):
                rec_keys.append(rec["rec_key"])
            has_action = att.get("action") is not None
            if rec and has_action and i + 1 < len(attempts):
                converged = bool(attempts[i + 1].get("pycsl_pass"))
                att["right_cause"] = converged
                fc = rec.get("fault_class") or "unknown"
                slot = by_class.setdefault(fc, {"correct": 0, "total": 0})
                slot["total"] += 1
                overall["total"] += 1
                if converged:
                    slot["correct"] += 1
                    overall["correct"] += 1
            else:
                att.setdefault("right_cause", None)

        # max consecutive identical rec_keys
        max_streak = streak = 0
        prev = None
        for k in rec_keys:
            streak = streak + 1 if k == prev else 1
            max_streak = max(max_streak, streak)
            prev = k

        summary = {
            "file": test_file.name,
            "outcome": outcome,
            "exit_code": exit_code,
            "attempts_used": len(attempts),
            "attempts": attempts,
            "loop": {
                "distinct_recommendations": len(set(rec_keys)),
                "max_consecutive_similar": max_streak,
                "redecompose_count": self._redecompose_count.get(test_file.name, 0),
            },
            "fault_correctness": {"by_class": by_class, "overall": overall},
            "rocq": rocq_summary,
            "ncr_emitted": ncr_emitted,
        }
        try:
            from schema_validator import validate_or_warn
            validate_or_warn(summary, "run-summary", logger=self.log)
        except Exception:
            pass

        out_dir = self.metrics_dir / "run-summary"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{test_file.stem}.json"
        try:
            out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            self.log(f"  L4: run-summary written -> {out_path}")
        except Exception as e:
            self.log(f"  WARNING: Could not write run-summary {out_path}: {e}")
            return None
        return out_path

    # ------------------------------------------------------------------ main loop

    def run(self, start_at: int = 1) -> int:
        """Run the full coordinator workflow, processing files one by one with per-file retry (max 10).

        Args:
            start_at: Skip files whose leading number is less than this value.
                      When > 1, the annotated/ directory is NOT cleaned so existing
                      outputs for earlier files are preserved.
        """
        MAX_RETRIES = 10
        self.log("Starting PyCSL Coordinator Agent")
        self.log(f"PyCSL root: {self.pycsl_dir}")
        if start_at > 1:
            self.log(f"--start-at {start_at}: skipping files 001–{start_at - 1:03d}, keeping existing annotated/")

        self.init_metrics()

        # Step 1: Clean annotated directory (skipped when --start-at > 1)
        if start_at <= 1:
            if not self.clean_annotated():
                self.log("ERROR: Failed to clean annotated/ directory")
                return 1
        else:
            if not self.annotated_dir.exists():
                self.annotated_dir.mkdir(parents=True, exist_ok=True)

        if not self.to_annotate_dir.exists():
            self.log("ERROR: tests/to_annotate/ directory does not exist.")
            return 1

        all_test_files = sorted(self.to_annotate_dir.glob("*.py"))
        if not all_test_files:
            self.log("No test files found in tests/to_annotate/")
            return 0

        # Filter to files whose leading number >= start_at
        def _file_number(p: Path) -> int:
            m = re.match(r'^(\d+)', p.name)
            return int(m.group(1)) if m else 0

        test_files = [f for f in all_test_files if _file_number(f) >= start_at]
        skipped = len(all_test_files) - len(test_files)
        if skipped:
            self.log(f"Skipping {skipped} file(s) before {start_at:03d} (--start-at {start_at})")
        if not test_files:
            self.log(f"No test files with number >= {start_at} found.")
            return 0

        overall_success = True

        # Cross-level (L5->L4) escalation state, keyed by file name:
        #  - _skip_reannotate: files whose next attempt must prove the re-decomposed
        #    artifact instead of re-running agent-annotate (which would overwrite it).
        #  - _redecompose_count: per-file L4 escalation count (ping-pong guard).
        self._skip_reannotate: set[str] = set()
        self._redecompose_count: dict[str, int] = {}

        for test_file in test_files:
            self.log(f"=== Processing {test_file.name} ===")
            passed = False

            # Per-file state
            recommendation_history: list[dict] = []
            history_file = self.pycsl_dir / f"update_{test_file.name}_history.json"
            if history_file.exists():
                history_file.unlink()

            reconcile_log_paths: list[Path] = []
            update_log_paths: list[Path] = []
            last_reconcile_out: Optional[Path] = None
            last_eval_json: Optional[Path] = None
            annotated_file = self.annotated_dir / test_file.name
            # L4 run-summary accumulator (per-attempt records for the metrics framework).
            attempts: list[dict] = []

            for attempt in range(MAX_RETRIES + 1):
                label = f"attempt {attempt + 1}/{MAX_RETRIES + 1}"
                att: dict = {"attempt": attempt, "pycsl_pass": False,
                             "reconcile": None, "action": None}
                attempts.append(att)

                # Annotate the file fresh on every attempt — UNLESS the previous
                # attempt escalated to L4 and re-decomposed (agent-splitter wrote
                # annotated_file directly); in that case prove that artifact so the
                # escalation is observable, not masked by a fresh re-annotate.
                if test_file.name in self._skip_reannotate:
                    self._skip_reannotate.discard(test_file.name)
                    self.log(f"  Skipping re-annotate on {label}: proving re-decomposed {test_file.name}")
                elif not self.annotate_file(test_file):
                    self.log(f"  ERROR: Annotation failed on {label} for {test_file.name}")
                    self.write_run_summary(test_file=test_file, attempts=attempts,
                                           outcome="annotate-failed")
                    return 1

                # Verify with pycsl
                proof_ok = self.run_pycsl_file(annotated_file)
                att["pycsl_pass"] = proof_ok
                if proof_ok:
                    self.log(f"  {test_file.name} passed on {label}")
                    passed = True
                    self.write_run_summary(test_file=test_file, attempts=attempts,
                                           outcome="passed")
                    break

                if attempt == MAX_RETRIES:
                    self.log(
                        f"ERROR: {test_file.name} still failing after {MAX_RETRIES} retries. Halting."
                    )
                    # Emit the Workflow-3 NCR first (deterministic governance artifact)
                    self.write_ncr(
                        exit_code=EXIT_MAX_RETRIES,
                        annotated_file=annotated_file,
                        recommendation=recommendation_history[-1] if recommendation_history else None,
                        attempt=attempt,
                        log_paths=reconcile_log_paths + update_log_paths,
                    )
                    # Attempt Rocq proof as last resort
                    _, rocq_summary = self.attempt_rocq_proof(annotated_file)
                    self.write_run_summary(
                        test_file=test_file, attempts=attempts, outcome="max-retries",
                        exit_code=EXIT_MAX_RETRIES, rocq_summary=rocq_summary,
                        ncr_emitted=True,
                    )
                    monitor_json = self.run_meta_monitor(
                        test_file.stem, reconcile_log_paths, update_log_paths
                    )
                    if last_reconcile_out:
                        self.run_meta_reviewer(
                            annotated_file, last_reconcile_out, last_eval_json, monitor_json
                        )
                    return EXIT_MAX_RETRIES

                # Reconcile failure
                self.log(f"  Reconciling {test_file.name} ({label})...")
                out_std = self.pycsl_dir / "out.std"
                out_err = self.pycsl_dir / "out.err"
                reconcile_out = self.pycsl_dir / f"reconcile_{annotated_file.name}.json"

                recommendation, rec_log_path = self.reconcile_failure(
                    annotated_file, out_std, out_err, 1, attempt
                )
                if rec_log_path:
                    reconcile_log_paths.append(rec_log_path)
                last_reconcile_out = reconcile_out

                if not recommendation:
                    self.log(
                        f"  WARNING: Reconciliation produced no recommendation for {test_file.name}"
                    )
                    continue

                att["reconcile"] = {
                    "target": recommendation.get("target"),
                    "fault_class": recommendation.get("fault_class", "sub-actor"),
                    "rec_key": " | ".join(loop_detect.rec_key(recommendation)),
                }

                # Loop detection
                consecutive = self._consecutive_similar(recommendation, recommendation_history)
                if consecutive >= 2:
                    self.log(
                        f"ERROR: agent-reconcile produced the same recommendation "
                        f"{consecutive + 1} times in a row for {test_file.name}. "
                        f"Halting — human review required."
                    )
                    # Emit the Workflow-3 NCR first (deterministic governance artifact)
                    self.write_ncr(
                        exit_code=EXIT_LOOP_DETECTED,
                        annotated_file=annotated_file,
                        recommendation=recommendation,
                        attempt=attempt,
                        consecutive=consecutive,
                        log_paths=reconcile_log_paths + update_log_paths,
                    )
                    # Attempt Rocq proof as last resort
                    _, rocq_summary = self.attempt_rocq_proof(annotated_file)
                    self.write_run_summary(
                        test_file=test_file, attempts=attempts, outcome="loop-detected",
                        exit_code=EXIT_LOOP_DETECTED, rocq_summary=rocq_summary,
                        ncr_emitted=True,
                    )
                    monitor_json = self.run_meta_monitor(
                        test_file.stem, reconcile_log_paths, update_log_paths
                    )
                    self.run_meta_reviewer(
                        annotated_file, reconcile_out, last_eval_json, monitor_json
                    )
                    return EXIT_LOOP_DETECTED

                is_similar = consecutive >= 1
                if is_similar:
                    self.log(
                        f"  WARNING: Recommendation is similar to the previous one "
                        f"({consecutive} consecutive). Instructing update agent to try a different approach."
                    )

                recommendation_history.append(recommendation)

                # Cross-level (L5->L4) reconciliation routing. A "specifier" fault
                # means the file's decomposition is wrong, not this unit's body —
                # re-decompose at L4 rather than re-patch the unit. Default
                # "sub-actor" preserves the existing per-unit fix path (and keeps
                # older reconcile outputs that lack fault_class behaving as before).
                fault_class = recommendation.get("fault_class", "sub-actor")
                if fault_class == "specifier":
                    self._redecompose_count[test_file.name] = (
                        self._redecompose_count.get(test_file.name, 0) + 1
                    )
                    if self._redecompose_count[test_file.name] > MAX_REDECOMPOSE:
                        self.log(
                            f"ERROR: L5<->L4 re-decomposition exceeded {MAX_REDECOMPOSE} "
                            f"escalations for {test_file.name} without convergence. Halting."
                        )
                        self.write_ncr(
                            exit_code=EXIT_LOOP_DETECTED,
                            annotated_file=annotated_file,
                            recommendation=recommendation,
                            attempt=attempt,
                            consecutive=consecutive,
                            log_paths=reconcile_log_paths + update_log_paths,
                            finding=(
                                f"L5<->L4 ping-pong: re-decomposition of {test_file.name} "
                                f"exceeded {MAX_REDECOMPOSE} escalations without convergence."
                            ),
                        )
                        _, rocq_summary = self.attempt_rocq_proof(annotated_file)
                        self.write_run_summary(
                            test_file=test_file, attempts=attempts, outcome="ping-pong",
                            exit_code=EXIT_LOOP_DETECTED, rocq_summary=rocq_summary,
                            ncr_emitted=True,
                        )
                        monitor_json = self.run_meta_monitor(
                            test_file.stem, reconcile_log_paths, update_log_paths
                        )
                        self.run_meta_reviewer(
                            annotated_file, reconcile_out, last_eval_json, monitor_json
                        )
                        return EXIT_LOOP_DETECTED
                    redecomposed = self.redecompose_at_l4(test_file, annotated_file, attempt)
                    att["action"] = {"kind": "redecompose", "success": redecomposed}
                    if redecomposed:
                        # Prove the re-decomposed artifact next iteration (skip the
                        # fresh re-annotate that would otherwise overwrite it).
                        self._skip_reannotate.add(test_file.name)
                    continue

                success, files_changed = self.apply_recommendations(
                    recommendation, reconcile_out, annotated_file,
                    attempt=attempt,
                    is_similar=is_similar,
                    history_file=history_file,
                )
                att["action"] = {"kind": "script-update", "success": success}

                # Collect the update log written by apply_recommendations
                upd_log = self.metrics_dir / "logs" / f"update_{annotated_file.stem}_{attempt}.log"
                if upd_log.exists():
                    update_log_paths.append(upd_log)

                if success:
                    # Rebuild RAG index if any skill file was modified
                    if any("config/skills/" in f for f in files_changed):
                        self.rebuild_rag_index()
                    eval_json = self.run_meta_evaluator(annotated_file, files_changed, attempt)
                    if eval_json:
                        last_eval_json = eval_json
                else:
                    self.log(f"  WARNING: Failed to apply recommendations for {test_file.name}")

            if not passed:
                overall_success = False

            # Run monitor after each file's retry loop completes normally
            self.run_meta_monitor(test_file.stem, reconcile_log_paths, update_log_paths)

        self.log(f"SUMMARY: {'All files passed' if overall_success else 'Some files failed'} pycsl proof")
        return 0 if overall_success else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PyCSL Coordinator Agent"
    )
    parser.add_argument(
        "--pycsl-dir",
        dest="pycsl_dir",
        type=str,
        help="Path to the PyCSL directory"
    )
    parser.add_argument(
        "--start-at",
        dest="start_at",
        type=int,
        default=1,
        metavar="N",
        help=(
            "Start processing at the file whose leading number is N "
            "(e.g. --start-at 10 starts at 010-*.py). "
            "When N > 1 the annotated/ directory is NOT cleaned."
        ),
    )
    args = parser.parse_args()

    # Automatic discovery of pycsl_dir
    current_dir = Path.cwd()
    pycsl_dir = None

    if args.pycsl_dir:
        pycsl_dir = Path(args.pycsl_dir)
    elif (current_dir / "agents" / "coordinator.py").exists():
        # If we are in the PyCSL directory already
        pycsl_dir = current_dir
    else:
        # Fallback to search for ai/PyCSL upwards from current_dir
        search_root = current_dir
        while search_root != search_root.parent:
            if (search_root / "ai" / "PyCSL").exists():
                pycsl_dir = search_root / "ai" / "PyCSL"
                break
            search_root = search_root.parent

    if not pycsl_dir or not pycsl_dir.exists():
        print(f"ERROR: Could not find PyCSL directory starting from {current_dir}")
        return 1

    coordinator = CoordinatorAgent(pycsl_dir)
    return coordinator.run(start_at=args.start_at)


if __name__ == "__main__":
    sys.exit(main())

