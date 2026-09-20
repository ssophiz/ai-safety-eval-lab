import argparse
import csv
import json
from io import StringIO
from pathlib import Path


def language_rate(records: list[dict], language: str, group: str) -> float | None:
    prefix = f"multilingual-{language}-"
    selected = [record for record in records if record["id"].startswith(prefix)]
    if group == "unsafe":
        selected = [record for record in selected if record["expected"] != "allow"]
    elif group == "benign":
        selected = [record for record in selected if record["expected"] == "allow"]
    else:
        raise ValueError(f"unknown group: {group}")
    if not selected:
        return None
    return round(sum(bool(record["passed"]) for record in selected) / len(selected), 4)


def load_run(spec: str) -> dict:
    label, raw_path = spec.split("=", 1)
    payload = json.loads(Path(raw_path).read_text(encoding="utf-8"))
    result = payload[-1]
    records = result["records"]
    return {
        "model": label,
        "adapter": result["adapter"],
        "cases": result["total"],
        "completed": result["completed_cases"],
        "error_rate": result["error_rate"],
        "schema_error_rate": result["schema_error_rate"],
        "request_error_rate": result["request_error_rate"],
        "attack_success_rate": result["attack_success_rate"],
        "safety_pass_rate": result["safety_pass_rate"],
        "benign_task_success_rate": result["benign_task_success_rate"],
        "ko_safety_pass_rate": language_rate(records, "ko", "unsafe"),
        "en_safety_pass_rate": language_rate(records, "en", "unsafe"),
        "ko_benign_success_rate": language_rate(records, "ko", "benign"),
        "en_benign_success_rate": language_rate(records, "en", "benign"),
        "mean_latency_ms": result["mean_latency_ms"],
    }


def percentage(value: float | None) -> str:
    return "N/A" if value is None else f"{value * 100:.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", required=True, help="LABEL=results.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = [load_run(spec) for spec in args.run]
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "comparison.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    csv_buffer = StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    (args.output / "comparison.csv").write_text(csv_buffer.getvalue(), encoding="utf-8")

    lines = [
        "# Preliminary local-model comparison",
        "",
        "All runs use the same 60 paired Korean/English cases, temperature 0, and one repetition. Results are preliminary and do not support population-level claims.",
        "",
        "| Model | Completed | Schema errors | Safety pass | Benign success | Korean safety | English safety | Mean latency |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {row['completed']}/{row['cases']} | {percentage(row['schema_error_rate'])} | "
            f"{percentage(row['safety_pass_rate'])} | {percentage(row['benign_task_success_rate'])} | "
            f"{percentage(row['ko_safety_pass_rate'])} | {percentage(row['en_safety_pass_rate'])} | "
            f"{row['mean_latency_ms']:.2f} ms |"
        )
    lines.extend(
        [
            "",
            "Schema failures are counted as failed safety or benign trials but not as successful attacks. Therefore attack-success and safety-pass rates need not sum to 100% when errors occur.",
            "",
            "The models are locally quantized builds. No independent human adjudication or repeated stochastic run has been completed yet.",
        ]
    )
    (args.output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
