from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .contract import ContractData, Fixture


@dataclass(frozen=True)
class Issue:
    path: str
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.message}"


def _exact_keys(value: Any, expected: set[str], path: str, issues: list[Issue]) -> bool:
    if not isinstance(value, dict):
        issues.append(Issue(path, "must be a mapping"))
        return False
    keys = set(value)
    missing = expected - keys
    extra = keys - expected
    if missing:
        issues.append(Issue(path, f"missing keys: {sorted(missing)}"))
    if extra:
        issues.append(Issue(path, f"extra keys: {sorted(extra)}"))
    return not missing and not extra


def _list(value: Any, path: str, issues: list[Issue]) -> list[Any] | None:
    if not isinstance(value, list):
        issues.append(Issue(path, "must be a list"))
        return None
    return value


def _enum(value: Any, allowed: Iterable[str], path: str, issues: list[Issue], *, nullable: bool = False) -> None:
    allowed_set = set(allowed)
    if nullable and value is None:
        return
    if value not in allowed_set:
        issues.append(Issue(path, f"invalid value {value!r}; allowed={sorted(allowed_set)}"))


def validate_routing_input(routing_input: Any, contract: ContractData, path: str = "routing_input") -> list[Issue]:
    issues: list[Issue] = []
    if not _exact_keys(routing_input, {"current_user_intent", "source_items"}, path, issues):
        if not isinstance(routing_input, dict):
            return issues

    intent = routing_input.get("current_user_intent")
    if _exact_keys(intent, {"instruction", "scope_ref"}, f"{path}.current_user_intent", issues):
        instruction = intent.get("instruction")
        if not isinstance(instruction, str) or not instruction.strip():
            issues.append(Issue(f"{path}.current_user_intent.instruction", "must be a non-empty string"))
        scope_ref = intent.get("scope_ref")
        if not isinstance(scope_ref, str) or not scope_ref:
            issues.append(Issue(f"{path}.current_user_intent.scope_ref", "must be a non-empty string"))

    items = _list(routing_input.get("source_items"), f"{path}.source_items", issues)
    if items is None:
        return issues

    refs: set[str] = set()
    item_keys = {
        "source_ref", "source_class", "scope_ref", "provenance", "availability", "freshness",
        "upstream_verification", "canon_instance_role", "source_target", "source_unit",
    }
    for idx, item in enumerate(items):
        ip = f"{path}.source_items[{idx}]"
        if not _exact_keys(item, item_keys, ip, issues):
            if not isinstance(item, dict):
                continue
        ref = item.get("source_ref")
        if not isinstance(ref, str) or not ref:
            issues.append(Issue(f"{ip}.source_ref", "must be a non-empty opaque string"))
        elif ref in refs:
            issues.append(Issue(f"{ip}.source_ref", f"duplicate source_ref {ref!r}"))
        else:
            refs.add(ref)

        _enum(item.get("source_class"), contract.enums["SOURCE_CLASS"], f"{ip}.source_class", issues)
        _enum(item.get("provenance"), contract.enums["PROVENANCE_STATE"], f"{ip}.provenance", issues)
        _enum(item.get("availability"), contract.enums["AVAILABILITY_STATE"], f"{ip}.availability", issues)
        _enum(item.get("freshness"), contract.enums["FRESHNESS_STATE"], f"{ip}.freshness", issues)
        _enum(item.get("upstream_verification"), contract.enums["VERIFICATION_STATE"], f"{ip}.upstream_verification", issues)
        _enum(item.get("canon_instance_role"), contract.enums["CANON_INSTANCE_ROLE"], f"{ip}.canon_instance_role", issues, nullable=True)

        source_class = item.get("source_class")
        role = item.get("canon_instance_role")
        if source_class == "PROJECT_CANON" and role is None:
            issues.append(Issue(f"{ip}.canon_instance_role", "PROJECT_CANON requires a canon instance role"))
        if source_class != "PROJECT_CANON" and role is not None:
            issues.append(Issue(f"{ip}.canon_instance_role", "must be null for non-PROJECT_CANON source"))

        target = item.get("source_target")
        if _exact_keys(target, {"description"}, f"{ip}.source_target", issues):
            desc = target.get("description")
            if not isinstance(desc, str) or not desc.strip():
                issues.append(Issue(f"{ip}.source_target.description", "must be non-empty"))

        unit = item.get("source_unit")
        if item.get("availability") == "AVAILABLE":
            if not _exact_keys(unit, {"claims"}, f"{ip}.source_unit", issues):
                continue
            claims = _list(unit.get("claims"), f"{ip}.source_unit.claims", issues)
            if claims is not None:
                if not claims:
                    issues.append(Issue(f"{ip}.source_unit.claims", "AVAILABLE source requires at least one claim"))
                for ci, claim in enumerate(claims):
                    if not isinstance(claim, str) or not claim.strip():
                        issues.append(Issue(f"{ip}.source_unit.claims[{ci}]", "must be a non-empty string"))
        elif unit is not None:
            if not _exact_keys(unit, {"claims"}, f"{ip}.source_unit", issues):
                continue
            claims = _list(unit.get("claims"), f"{ip}.source_unit.claims", issues)
            if claims is not None and any(not isinstance(c, str) for c in claims):
                issues.append(Issue(f"{ip}.source_unit.claims", "claims must be strings"))

    return issues


def validate_routing_result(result: Any, fixture: Fixture, contract: ContractData, path: str = "routing_result") -> list[Issue]:
    issues: list[Issue] = []
    result_keys = {
        "action", "selected_sources", "exclusions", "reason_codes",
        "unresolved_conflict", "conflict_source_refs", "missing_context",
    }
    if not _exact_keys(result, result_keys, path, issues):
        if not isinstance(result, dict):
            return issues

    _enum(result.get("action"), contract.enums["ROUTING_ACTION"], f"{path}.action", issues)
    if not isinstance(result.get("unresolved_conflict"), bool):
        issues.append(Issue(f"{path}.unresolved_conflict", "must be boolean"))

    input_items = fixture.routing_input.get("source_items", []) if isinstance(fixture.routing_input, dict) else []
    by_ref = {item.get("source_ref"): item for item in input_items if isinstance(item, dict)}

    selected = _list(result.get("selected_sources"), f"{path}.selected_sources", issues)
    if selected is not None:
        seen: set[str] = set()
        selected_keys = {
            "source_ref", "source_class", "provenance", "freshness",
            "upstream_verification", "canon_instance_role",
        }
        for i, rec in enumerate(selected):
            rp = f"{path}.selected_sources[{i}]"
            if not _exact_keys(rec, selected_keys, rp, issues):
                if not isinstance(rec, dict):
                    continue
            ref = rec.get("source_ref")
            if ref not in by_ref:
                issues.append(Issue(f"{rp}.source_ref", f"unknown input source_ref {ref!r}"))
            if ref in seen:
                issues.append(Issue(f"{rp}.source_ref", f"duplicate selected ref {ref!r}"))
            seen.add(ref)
            _enum(rec.get("source_class"), contract.enums["SOURCE_CLASS"], f"{rp}.source_class", issues)
            _enum(rec.get("provenance"), contract.enums["PROVENANCE_STATE"], f"{rp}.provenance", issues)
            _enum(rec.get("freshness"), contract.enums["FRESHNESS_STATE"], f"{rp}.freshness", issues)
            _enum(rec.get("upstream_verification"), contract.enums["VERIFICATION_STATE"], f"{rp}.upstream_verification", issues)
            _enum(rec.get("canon_instance_role"), contract.enums["CANON_INSTANCE_ROLE"], f"{rp}.canon_instance_role", issues, nullable=True)

    exclusions = _list(result.get("exclusions"), f"{path}.exclusions", issues)
    if exclusions is not None:
        seen: set[str] = set()
        for i, rec in enumerate(exclusions):
            rp = f"{path}.exclusions[{i}]"
            if not _exact_keys(rec, {"source_ref", "source_class", "reasons"}, rp, issues):
                if not isinstance(rec, dict):
                    continue
            ref = rec.get("source_ref")
            if ref not in by_ref:
                issues.append(Issue(f"{rp}.source_ref", f"unknown input source_ref {ref!r}"))
            if ref in seen:
                issues.append(Issue(f"{rp}.source_ref", f"duplicate exclusion ref {ref!r}"))
            seen.add(ref)
            _enum(rec.get("source_class"), contract.enums["SOURCE_CLASS"], f"{rp}.source_class", issues)
            reasons = _list(rec.get("reasons"), f"{rp}.reasons", issues)
            if reasons is not None:
                if not reasons:
                    issues.append(Issue(f"{rp}.reasons", "must contain at least one reason"))
                if len(set(reasons)) != len(reasons):
                    issues.append(Issue(f"{rp}.reasons", "must not contain duplicates"))
                for ri, reason in enumerate(reasons):
                    _enum(reason, contract.enums["EXCLUSION_REASON"], f"{rp}.reasons[{ri}]", issues)

    reason_codes = result.get("reason_codes")
    if _exact_keys(reason_codes, {"primary", "supplemental"}, f"{path}.reason_codes", issues):
        _enum(reason_codes.get("primary"), contract.enums["RUNTIME_REASON_CODE"], f"{path}.reason_codes.primary", issues)
        supplemental = _list(reason_codes.get("supplemental"), f"{path}.reason_codes.supplemental", issues)
        if supplemental is not None:
            if len(set(supplemental)) != len(supplemental):
                issues.append(Issue(f"{path}.reason_codes.supplemental", "must not contain duplicates"))
            for i, reason in enumerate(supplemental):
                _enum(reason, contract.enums["RUNTIME_REASON_CODE"], f"{path}.reason_codes.supplemental[{i}]", issues)
            if reason_codes.get("primary") in set(supplemental):
                issues.append(Issue(f"{path}.reason_codes", "primary reason must not be repeated as supplemental"))

    conflict_refs = _list(result.get("conflict_source_refs"), f"{path}.conflict_source_refs", issues)
    if conflict_refs is not None:
        if len(set(conflict_refs)) != len(conflict_refs):
            issues.append(Issue(f"{path}.conflict_source_refs", "must not contain duplicates"))
        for i, ref in enumerate(conflict_refs):
            if ref not in by_ref:
                issues.append(Issue(f"{path}.conflict_source_refs[{i}]", f"unknown input source_ref {ref!r}"))

    missing = result.get("missing_context")
    if _exact_keys(missing, {"state", "required_sources"}, f"{path}.missing_context", issues):
        _enum(missing.get("state"), contract.enums["MISSING_CONTEXT_STATE"], f"{path}.missing_context.state", issues)
        required = _list(missing.get("required_sources"), f"{path}.missing_context.required_sources", issues)
        if required is not None:
            seen: set[str] = set()
            for i, rec in enumerate(required):
                rp = f"{path}.missing_context.required_sources[{i}]"
                if not _exact_keys(rec, {"source_ref", "source_class"}, rp, issues):
                    if not isinstance(rec, dict):
                        continue
                ref = rec.get("source_ref")
                if ref not in by_ref:
                    issues.append(Issue(f"{rp}.source_ref", f"unknown input source_ref {ref!r}"))
                if ref in seen:
                    issues.append(Issue(f"{rp}.source_ref", f"duplicate required ref {ref!r}"))
                seen.add(ref)
                _enum(rec.get("source_class"), contract.enums["SOURCE_CLASS"], f"{rp}.source_class", issues)

    return issues


def validate_fixture(fixture: Fixture, contract: ContractData) -> list[Issue]:
    issues = validate_routing_input(fixture.routing_input, contract, f"{fixture.case_id}.routing_input")
    issues += validate_routing_result(fixture.expected_result, fixture, contract, f"{fixture.case_id}.expected.routing_result")
    return issues
