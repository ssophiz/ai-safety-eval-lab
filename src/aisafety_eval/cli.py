import argparse

from .adapters import BaselineAdapter, GuardedAdapter
from .dataset import load_cases
from .evaluator import evaluate
from .model_adapter import OpenAICompatibleAdapter
from .report import write_reports


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="data/cases.jsonl")
    parser.add_argument("--out", default="results")
    parser.add_argument("--model-endpoint")
    parser.add_argument("--model", default="local-model")
    parser.add_argument("--model-timeout", type=float, default=30.0)
    args = parser.parse_args()
    cases = load_cases(args.cases)
    adapters = [BaselineAdapter(), GuardedAdapter()]
    if args.model_endpoint:
        adapters.append(OpenAICompatibleAdapter(args.model_endpoint, args.model, args.model_timeout))
    results = [evaluate(adapter, cases) for adapter in adapters]
    write_reports(results, args.out)
    for result in results:
        print(
            f"{result['adapter']}: attack_success={result['attack_success_rate']:.2%}, "
            f"safety_pass={result['safety_pass_rate']:.2%}, benign_success={result['benign_task_success_rate']:.2%}"
        )


if __name__ == "__main__":
    main()
