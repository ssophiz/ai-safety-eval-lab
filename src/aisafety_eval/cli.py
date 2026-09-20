import argparse

from .adapters import BaselineAdapter, GuardedAdapter
from .dataset import load_cases
from .evaluator import evaluate
from .report import write_reports


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="data/cases.jsonl")
    parser.add_argument("--out", default="results")
    args = parser.parse_args()
    cases = load_cases(args.cases)
    results = [evaluate(BaselineAdapter(), cases), evaluate(GuardedAdapter(), cases)]
    write_reports(results, args.out)
    for result in results:
        print(
            f"{result['adapter']}: attack_success={result['attack_success_rate']:.2%}, "
            f"safety_pass={result['safety_pass_rate']:.2%}, benign_success={result['benign_task_success_rate']:.2%}"
        )


if __name__ == "__main__":
    main()
