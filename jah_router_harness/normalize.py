from __future__ import annotations

from copy import deepcopy
from typing import Any


def normalize_result(result: dict[str, Any]) -> dict[str, Any]:
    """Normalize only R5-declared non-semantic list ordering."""
    out = deepcopy(result)

    out["selected_sources"] = sorted(
        out.get("selected_sources", []), key=lambda x: x.get("source_ref", "")
    )

    exclusions = deepcopy(out.get("exclusions", []))
    for rec in exclusions:
        rec["reasons"] = sorted(rec.get("reasons", []))
    out["exclusions"] = sorted(exclusions, key=lambda x: x.get("source_ref", ""))

    if isinstance(out.get("reason_codes"), dict):
        out["reason_codes"]["supplemental"] = sorted(out["reason_codes"].get("supplemental", []))

    out["conflict_source_refs"] = sorted(out.get("conflict_source_refs", []))

    missing = out.get("missing_context")
    if isinstance(missing, dict):
        missing["required_sources"] = sorted(
            missing.get("required_sources", []), key=lambda x: x.get("source_ref", "")
        )

    return out
