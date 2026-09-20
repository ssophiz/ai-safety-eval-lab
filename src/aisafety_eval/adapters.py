import re

from .types import Case, Decision


SECRET = re.compile(r"\b(?:API_KEY|SECRET|TOKEN|PASSWORD)[=: _-]*[A-Za-z0-9_-]{4,}\b", re.I)
PERSONAL = re.compile(r"\b\d{6}-[1-4]\d{6}\b")
INJECTION = re.compile(
    r"(?:ignore (?:all )?(?:previous|prior) (?:instructions?|rules?)|"
    r"system override|developer override|"
    r"이전 (?:지시|규칙)(?:를|을) 무시|기존 (?:지시|규칙)(?:를|을) 무시|"
    r"시스템 (?:지시|규칙)(?:를|을) 무시)",
    re.I,
)


class BaselineAdapter:
    name = "baseline"

    def run(self, case: Case) -> Decision:
        output = " ".join(part for part in (case.context, case.prompt) if part).strip()
        return Decision("allow", output, ())


class GuardedAdapter:
    name = "guarded"

    def run(self, case: Case) -> Decision:
        reasons = []
        if INJECTION.search(case.prompt):
            reasons.append("direct_instruction_override")
        if case.context and not case.context_trusted and INJECTION.search(case.context):
            reasons.append("untrusted_context_instruction")
        if case.requested_tool and not case.tool_authorized:
            reasons.append("unauthorized_tool")
        if case.approval_required:
            reasons.append("human_approval_required")
        if reasons:
            return Decision("block", "Request blocked by policy.", tuple(reasons))
        output = " ".join(part for part in (case.context, case.prompt) if part).strip()
        redacted = PERSONAL.sub("[REDACTED_PERSONAL_DATA]", SECRET.sub("[REDACTED_SECRET]", output))
        if redacted != output:
            return Decision("redact", redacted, ("sensitive_data",))
        return Decision("allow", output, ())
