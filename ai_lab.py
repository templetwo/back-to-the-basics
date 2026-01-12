"""
AI Lab: Self-Organizing Model Factory

Proof that the Coherence Engine scales beyond "file organization"
to replace experiment tracking databases entirely.

The filesystem becomes:
- The leaderboard (promoted/ vs archive/)
- The state machine (location IS state)
- The query engine (glob IS select)
"""

import os
import json
from datetime import datetime
from pathlib import Path
from coherence import Coherence


# =============================================================================
# THE SCHEMA: A Decision Tree for ML Experiments
# =============================================================================
#
# This schema encodes the logic that MLFlow/W&B would typically store in a DB.
# The path IS the classification. The folder IS the leaderboard.

AI_LAB_SCHEMA = {
    "project_type": {
        # ─────────────────────────────────────────────────────────────────────
        # PRODUCTION: Models destined for deployment
        # ─────────────────────────────────────────────────────────────────────
        "production": {
            "model_arch": {
                "transformer": {
                    "final_loss": {
                        # LOGIC GATE: Performance threshold
                        "<0.3": {
                            # Elite performers → promotion track
                            "convergence_epoch": {
                                "<50": "models/production/promoted/fast_converge/{date}/{run_id}/model.pt",
                                ">=50": "models/production/promoted/standard/{date}/{run_id}/model.pt"
                            }
                        },
                        "0.3-0.7": "models/production/review/{date}/{run_id}/model.pt",
                        ">=0.7": "models/production/archive/underperform/{date}/{run_id}/model.pt"
                    }
                },
                "cnn": {
                    "final_loss": {
                        "<0.4": "models/production/promoted/cnn/{date}/{run_id}/model.pt",
                        ">=0.4": "models/production/archive/cnn/{date}/{run_id}/model.pt"
                    }
                },
                "lstm": "models/legacy/lstm/{date}/{run_id}/model.pt"
            }
        },

        # ─────────────────────────────────────────────────────────────────────
        # RESEARCH: Experimental runs, organized by researcher
        # ─────────────────────────────────────────────────────────────────────
        "research": {
            "risk_level": {
                "low": "experiments/safe/{experiment_name}/{researcher}/{run_id}/",
                "medium": "experiments/exploratory/{experiment_name}/{researcher}/{run_id}/",
                "high": "experiments/moonshot/{experiment_name}/{researcher}/{run_id}/"
            }
        },

        # ─────────────────────────────────────────────────────────────────────
        # BENCHMARK: Standard evaluation runs
        # ─────────────────────────────────────────────────────────────────────
        "benchmark": {
            "dataset": {
                "imagenet": "benchmarks/imagenet/{model_arch}/{date}/{run_id}/",
                "coco": "benchmarks/coco/{model_arch}/{date}/{run_id}/",
                "custom": "benchmarks/custom/{dataset_name}/{date}/{run_id}/"
            }
        }
    }
}


class AILabEngine(Coherence):
    """
    Extended Coherence Engine for ML experiment tracking.

    Replaces:
    - MLFlow tracking server
    - Weights & Biases dashboard
    - Custom experiment databases

    With:
    - Pure filesystem topology
    - Path-as-state-machine
    - Glob-as-query
    """

    def __init__(self, root: str = "ai_lab"):
        super().__init__(AI_LAB_SCHEMA, root)
        self.run_log = []  # In-memory log for demo

    def log_run(self, run_config: dict, metrics: dict) -> dict:
        """
        Log a training run. The metrics determine where it lands.

        Args:
            run_config: Static config (model_arch, project_type, etc.)
            metrics: Dynamic results (final_loss, convergence_epoch, etc.)

        Returns:
            dict with status and destination path
        """
        # Merge config and metrics into packet
        packet = {
            **run_config,
            **metrics,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat()
        }

        # Route through the circuit
        destination = self.transmit(packet, dry_run=False)

        # Log result
        result = {
            "run_id": packet.get("run_id", "unknown"),
            "destination": destination,
            "packet": packet,
            "routed_at": packet["timestamp"]
        }

        self.run_log.append(result)

        # Write metadata
        meta_path = os.path.join(destination, "meta.json") if os.path.isdir(destination) else destination.replace(".pt", "_meta.json")
        meta_dir = os.path.dirname(meta_path)
        if meta_dir:
            os.makedirs(meta_dir, exist_ok=True)
        with open(meta_path, 'w') as f:
            json.dump(packet, f, indent=2, default=str)

        return result

    def leaderboard(self, glob_pattern: str = "") -> list:
        """
        Query the filesystem leaderboard.

        Instead of SELECT * FROM runs WHERE status='promoted',
        we just glob the promoted folder.
        """
        if not glob_pattern:
            # Match the actual structure: ai_lab/**/promoted/**/*_meta.json
            glob_pattern = f"{self.root}/**/promoted/**/*_meta.json"

        from glob import glob
        matches = glob(glob_pattern, recursive=True)

        results = []
        for path in matches:
            try:
                with open(path) as f:
                    meta = json.load(f)
                    meta['_path'] = path
                    results.append(meta)
            except (json.JSONDecodeError, IOError):
                continue

        # Sort by loss (best first)
        results.sort(key=lambda x: x.get('final_loss', float('inf')))
        return results

    def status_report(self) -> dict:
        """
        Generate a status report by walking the filesystem.

        The folder structure IS the report.
        """
        report = {
            "promoted": {"count": 0, "runs": []},
            "review": {"count": 0, "runs": []},
            "archive": {"count": 0, "runs": []},
            "research": {"count": 0, "runs": []},
        }

        base = Path(self.root)

        # Count promoted (match actual structure with decision path)
        promoted = list(base.glob("**/promoted/**/*_meta.json"))
        report["promoted"]["count"] = len(promoted)
        report["promoted"]["runs"] = [str(p.parent.name) for p in promoted[:5]]

        # Count review
        review = list(base.glob("**/review/**/*_meta.json"))
        report["review"]["count"] = len(review)

        # Count archive
        archive = list(base.glob("**/archive/**/*_meta.json"))
        report["archive"]["count"] = len(archive)

        # Count research
        research = list(base.glob("**/experiments/**/*meta.json"))
        report["research"]["count"] = len(research)

        return report


# =============================================================================
# DEMONSTRATION: Simulate a Day at the AI Lab
# =============================================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AI LAB: Self-Organizing Model Factory")
    print("The filesystem IS the experiment tracker.")
    print("=" * 70)

    lab = AILabEngine(root="ai_lab")

    # ─────────────────────────────────────────────────────────────────────────
    # Simulate training runs with varying outcomes
    # ─────────────────────────────────────────────────────────────────────────

    runs = [
        # ELITE: Fast-converging transformer with excellent loss
        {
            "config": {"project_type": "production", "model_arch": "transformer", "run_id": "xfmr_001"},
            "metrics": {"final_loss": 0.12, "convergence_epoch": 23}
        },
        # ELITE: Standard convergence but still excellent
        {
            "config": {"project_type": "production", "model_arch": "transformer", "run_id": "xfmr_002"},
            "metrics": {"final_loss": 0.18, "convergence_epoch": 78}
        },
        # REVIEW: Decent but needs human evaluation
        {
            "config": {"project_type": "production", "model_arch": "transformer", "run_id": "xfmr_003"},
            "metrics": {"final_loss": 0.45, "convergence_epoch": 100}
        },
        # ARCHIVE: Underperforming, don't deploy
        {
            "config": {"project_type": "production", "model_arch": "transformer", "run_id": "xfmr_004"},
            "metrics": {"final_loss": 0.89, "convergence_epoch": 200}
        },
        # CNN: Good performance
        {
            "config": {"project_type": "production", "model_arch": "cnn", "run_id": "cnn_001"},
            "metrics": {"final_loss": 0.22}
        },
        # CNN: Poor performance
        {
            "config": {"project_type": "production", "model_arch": "cnn", "run_id": "cnn_002"},
            "metrics": {"final_loss": 0.71}
        },
        # RESEARCH: Moonshot experiment
        {
            "config": {"project_type": "research", "risk_level": "high",
                      "experiment_name": "infinite_context", "researcher": "dr_vaquez", "run_id": "moon_001"},
            "metrics": {"final_loss": 0.55}
        },
        # RESEARCH: Safe incremental improvement
        {
            "config": {"project_type": "research", "risk_level": "low",
                      "experiment_name": "lr_schedule_v2", "researcher": "dr_vaquez", "run_id": "safe_001"},
            "metrics": {"final_loss": 0.33}
        },
        # BENCHMARK: Standard evaluation
        {
            "config": {"project_type": "benchmark", "dataset": "imagenet",
                      "model_arch": "transformer", "run_id": "bench_001"},
            "metrics": {"final_loss": 0.28, "top1_acc": 0.847}
        },
    ]

    print("\n[ROUTING RUNS THROUGH THE CIRCUIT]\n")

    for run in runs:
        result = lab.log_run(run["config"], run["metrics"])
        status = "PROMOTED" if "promoted" in result["destination"] else \
                 "REVIEW" if "review" in result["destination"] else \
                 "ARCHIVE" if "archive" in result["destination"] else \
                 "ROUTED"
        print(f"  [{status:8}] {result['run_id']:12} → {result['destination']}")

    # ─────────────────────────────────────────────────────────────────────────
    # Query the leaderboard (via filesystem, not database)
    # ─────────────────────────────────────────────────────────────────────────

    print("\n" + "=" * 70)
    print("[LEADERBOARD] Top Promoted Models (queried via glob, not SQL)")
    print("=" * 70 + "\n")

    leaderboard = lab.leaderboard()
    for i, entry in enumerate(leaderboard, 1):
        print(f"  #{i}: {entry.get('run_id', 'unknown'):12} | "
              f"loss={entry.get('final_loss', 'N/A'):.3f} | "
              f"arch={entry.get('model_arch', 'N/A')}")

    # ─────────────────────────────────────────────────────────────────────────
    # Status report (filesystem structure IS the report)
    # ─────────────────────────────────────────────────────────────────────────

    print("\n" + "=" * 70)
    print("[STATUS REPORT] Derived from folder structure")
    print("=" * 70 + "\n")

    report = lab.status_report()
    print(f"  Promoted:  {report['promoted']['count']} models ready for deployment")
    print(f"  Review:    {report['review']['count']} models awaiting evaluation")
    print(f"  Archive:   {report['archive']['count']} models archived (underperforming)")
    print(f"  Research:  {report['research']['count']} experimental runs")

    # ─────────────────────────────────────────────────────────────────────────
    # Show the filesystem structure
    # ─────────────────────────────────────────────────────────────────────────

    print("\n" + "=" * 70)
    print("[FILESYSTEM] The topology IS the state machine")
    print("=" * 70 + "\n")

    for root, dirs, files in os.walk("ai_lab"):
        level = root.replace("ai_lab", "").count(os.sep)
        indent = "  " * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = "  " * (level + 1)
        for file in files:
            print(f"{subindent}{file}")

    print("\n" + "=" * 70)
    print("No database. No tracking server. The path IS the truth.")
    print("=" * 70)
