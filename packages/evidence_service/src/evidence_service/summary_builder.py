from collections import Counter
from typing import Any


def build_summary(records: list[dict[str, Any]], intent: str | None = None) -> str:
    if not records:
        return "No Jira issues matched the request."

    statuses = Counter((record.get("status") or "Unknown") for record in records)
    top = ", ".join(f"{name}: {count}" for name, count in statuses.most_common(3))

    if intent:
        return (
            f"Found {len(records)} Jira issues for '{intent}'. Top statuses -> {top}."
        )
    return f"Found {len(records)} Jira issues. Top statuses -> {top}."
