import json
from pathlib import Path


def write_reports(results: list[dict], output_dir: str | Path) -> None:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# AI Safety Evaluation Results", "", "| Adapter | Cases | Attack success | Safety pass | Benign success | Mean latency |", "|---|---:|---:|---:|---:|---:|"]
    for result in results:
        lines.append(
            f"| {result['adapter']} | {result['total']} | {result['attack_success_rate']:.2%} | "
            f"{result['safety_pass_rate']:.2%} | {result['benign_task_success_rate']:.2%} | "
            f"{result['mean_latency_ms']:.4f} ms |"
        )
    lines.extend(["", "## Category results", ""])
    for result in results:
        lines.append(f"### {result['adapter']}")
        lines.append("")
        lines.append("| Category | Passed | Total | Pass rate |")
        lines.append("|---|---:|---:|---:|")
        for category, values in result["categories"].items():
            lines.append(f"| {category} | {values['passed']} | {values['total']} | {values['pass_rate']:.2%} |")
        lines.append("")
    (destination / "report.md").write_text("\n".join(lines), encoding="utf-8")
