#!/usr/bin/env python3
"""
Coordinator Agent for PyCSL Testing and Reconciliation.

Orchestrates the full workflow:
1. Clean tests/annotated/ directory
2. Annotate all test files in tests/to_annotate/ using agent-annotate.py
3. Run pycsl proof on each annotated file
4. On proof failure, run agent-reconcile.py
5. Apply recommendations using agent-script-update.py

Loop-detection: if agent-reconcile produces the same recommendation 3 times in a row
the coordinator halts with exit code 73 so a human can intervene.

Meta-observability: after each fix attempt agent-meta-evaluator assesses the change.
After each file's retry loop agent-meta-monitor checks operational health.
On halt (72 or 73) agent-meta-reviewer produces a human-readable report.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

AGENT_NAME = "coordinator"
EXIT_MAX_RETRIES = 72    # pycsl still failing after MAX_RETRIES attempts
EXIT_LOOP_DETECTED = 73  # same recommendation 3× in a row — human needed


class CoordinatorAgent:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.pycsl_dir = repo_root / "ai" / "PyCSL"
        self.agents_dir = self.pycsl_dir / "agents"
        self.tests_dir = self.pycsl_dir / "tests"
        self.to_annotate_dir = self.tests_dir / "to_annotate"
        self.annotated_dir = self.tests_dir / "annotated"
        self.pycsl_bin = self.pycsl_dir / "pycsl"
        self.venv_activate = self.pycsl_dir / ".venv" / "bin" / "activate"
        self.metrics_dir = self.pycsl_dir / "metrics"

    def init_metrics(self) -> None:
        """Create the metrics/ directory tree at startup."""
        for subdir in ("logs", "evaluator", "monitor", "reviewer"):
            (self.metrics_dir / subdir).mkdir(parents=True, exist_ok=True)
        self.log(f"Metrics directory initialized at {self.metrics_dir}")

    def log(self, message: str) -> None:
        print(f"[{AGENT_NAME}] {message}")

    @staticmethod
    def _rec_key(rec: dict) -> tuple[str, str]:
        """Normalised (target, recommendation-text) pair for similarity checks."""
        return (
            rec.get("target", "").strip().lower(),
            rec.get("recommendation", "").strip().lower(),
        )

    @staticmethod
    def _are_similar(rec1: dict, rec2: dict) -> bool:
        return CoordinatorAgent._rec_key(rec1) == CoordinatorAgent._rec_key(rec2)

    def _consecutive_similar(self, new_rec: dict, history: list[dict]) -> int:
        """Count how many tail entries of history are similar to new_rec."""
        count = 0
        for past in reversed(history):
            if self._are_similar(new_rec, past):
                count += 1
            else:
                break
        return count

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
            config_path = self.agents_dir / "agents-config.json"
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
        cmd = ["python", str(self.pycsl_bin), "--keep-mlw", str(annotated_file)]
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
        config_path = self.agents_dir / "agents-config.json"

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

    # ------------------------------------------------------------------ main loop

    def run(self) -> int:
        """Run the full coordinator workflow, processing files one by one with per-file retry (max 10)."""
        MAX_RETRIES = 10
        self.log("Starting PyCSL Coordinator Agent")
        self.log(f"PyCSL root: {self.pycsl_dir}")

        self.init_metrics()

        # Step 1: Clean annotated directory
        if not self.clean_annotated():
            self.log("ERROR: Failed to clean annotated/ directory")
            return 1

        if not self.to_annotate_dir.exists():
            self.log("ERROR: tests/to_annotate/ directory does not exist.")
            return 1

        test_files = sorted(self.to_annotate_dir.glob("*.py"))
        if not test_files:
            self.log("No test files found in tests/to_annotate/")
            return 0

        overall_success = True

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

            for attempt in range(MAX_RETRIES + 1):
                label = f"attempt {attempt + 1}/{MAX_RETRIES + 1}"

                # Annotate the file fresh on every attempt
                if not self.annotate_file(test_file):
                    self.log(f"  ERROR: Annotation failed on {label} for {test_file.name}")
                    return 1

                # Verify with pycsl
                if self.run_pycsl_file(annotated_file):
                    self.log(f"  {test_file.name} passed on {label}")
                    passed = True
                    break

                if attempt == MAX_RETRIES:
                    self.log(
                        f"ERROR: {test_file.name} still failing after {MAX_RETRIES} retries. Halting."
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

                # Loop detection
                consecutive = self._consecutive_similar(recommendation, recommendation_history)
                if consecutive >= 2:
                    self.log(
                        f"ERROR: agent-reconcile produced the same recommendation "
                        f"{consecutive + 1} times in a row for {test_file.name}. "
                        f"Halting — human review required."
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

                success, files_changed = self.apply_recommendations(
                    recommendation, reconcile_out, annotated_file,
                    attempt=attempt,
                    is_similar=is_similar,
                    history_file=history_file,
                )

                # Collect the update log written by apply_recommendations
                upd_log = self.metrics_dir / "logs" / f"update_{annotated_file.stem}_{attempt}.log"
                if upd_log.exists():
                    update_log_paths.append(upd_log)

                if success:
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
    # Find the repo root
    current_dir = Path.cwd()
    repo_root = current_dir

    # Try to find the PyCSL directory
    while repo_root != repo_root.parent:
        if (repo_root / "ai" / "PyCSL").exists():
            break
        repo_root = repo_root.parent

    if not (repo_root / "ai" / "PyCSL").exists():
        print(f"ERROR: Could not find PyCSL directory starting from {current_dir}")
        return 1

    coordinator = CoordinatorAgent(repo_root)
    return coordinator.run()


if __name__ == "__main__":
    sys.exit(main())

