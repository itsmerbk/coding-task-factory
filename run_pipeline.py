import json
from dataclasses import asdict
from pathlib import Path
from factory.generator import synthesize_tasks
from factory.validator import validate_task
from factory.benchmark import evaluate_models

def main() -> None:
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    print("[1/3] Synthesizing parameterized coding tasks...")
    raw_tasks = synthesize_tasks(count=15, seed=2026)

    print("[2/3] Running AST static gate & isolated sandbox verification...")
    verified_tasks = []
    validation_logs = []
    for task in raw_tasks:
        is_valid, status = validate_task(task)
        validation_logs.append({
            "task_id": task.task_id,
            "domain": task.domain,
            "difficulty": task.difficulty,
            "status": status,
        })
        if is_valid:
            verified_tasks.append(task)

    with (results_dir / "verified_tasks.jsonl").open("w", encoding="utf-8") as f:
        for t in verified_tasks:
            f.write(json.dumps(asdict(t)) + "\n")

    (results_dir / "validation_report.json").write_text(json.dumps(validation_logs, indent=2), encoding="utf-8")
    print(f"      Verified {len(verified_tasks)}/{len(raw_tasks)} tasks.")

    print("[3/3] Benchmarking models on verified task suite...")
    models = ["frontier-model-alpha", "frontier-model-beta", "baseline-model-lite"]
    summary = evaluate_models(verified_tasks, models)
    (results_dir / "benchmark_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_lines = [
        "# Coding Task Factory - Benchmark Report\n",
        f"- **Generated Tasks:** {len(raw_tasks)}",
        f"- **Verified Tasks:** {len(verified_tasks)}\n",
        "| Model | Passed | Total | pass@1 (%) |",
        "| :--- | :---: | :---: | :---: |",
    ]
    for model, stats in summary.items():
        md_lines.append(f"| `{model}` | {stats['passed']} | {stats['total']} | **{stats['pass_at_1']}%** |")

    (results_dir / "benchmark_summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(md_lines))

if __name__ == "__main__":
    main()
