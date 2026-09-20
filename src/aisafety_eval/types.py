from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    case_id: str
    category: str
    prompt: str
    context: str
    context_trusted: bool
    requested_tool: str
    tool_authorized: bool
    approval_required: bool
    expected: str
    frameworks: tuple[str, ...]


@dataclass(frozen=True)
class Decision:
    action: str
    output: str
    reasons: tuple[str, ...]
