import json
from pathlib import Path

from .types import Case


def load_cases(path: str | Path) -> list[Case]:
    cases = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            raw = json.loads(line)
            try:
                cases.append(
                    Case(
                        case_id=raw["id"],
                        category=raw["category"],
                        prompt=raw["prompt"],
                        context=raw.get("context", ""),
                        context_trusted=bool(raw.get("context_trusted", True)),
                        requested_tool=raw.get("requested_tool", ""),
                        tool_authorized=bool(raw.get("tool_authorized", True)),
                        approval_required=bool(raw.get("approval_required", False)),
                        expected=raw["expected"],
                        frameworks=tuple(raw.get("frameworks", [])),
                    )
                )
            except KeyError as error:
                raise ValueError(f"{path}:{line_number}: missing {error.args[0]}") from error
    if not cases:
        raise ValueError("dataset is empty")
    ids = [case.case_id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case id")
    return cases
