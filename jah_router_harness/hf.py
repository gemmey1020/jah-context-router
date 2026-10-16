from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .contract import ContractData, Fixture
from .normalize import normalize_result


@dataclass(frozen=True)
class HFContext:
    fixture: Fixture
    actual: dict[str, Any]
    contract: ContractData

    @property
    def expected(self) -> dict[str, Any]:
        return self.fixture.expected_result

    @property
    def input_items(self) -> list[dict[str, Any]]:
        return self.fixture.routing_input.get("source_items", [])

    @property
    def by_ref(self) -> dict[str, dict[str, Any]]:
        return {item["source_ref"]: item for item in self.input_items}


Predicate = Callable[[HFContext], list[str]]


def _refs(records: Iterable[dict[str, Any]]) -> set[str]:
    return {r.get("source_ref") for r in records}


def _expected_refs(ctx: HFContext, field: str) -> set[str]:
    return _refs(ctx.expected.get(field, []))


def _actual_refs(ctx: HFContext, field: str) -> set[str]:
    return _refs(ctx.actual.get(field, []))


def _required_refs(result: dict[str, Any]) -> set[str]:
    return _refs(result.get("missing_context", {}).get("required_sources", []))


def _selected(ctx: HFContext) -> list[dict[str, Any]]:
    return ctx.actual.get("selected_sources", [])


def _exclusions(ctx: HFContext) -> list[dict[str, Any]]:
    return ctx.actual.get("exclusions", [])


def _error_if(condition: bool, message: str) -> list[str]:
    return [message] if condition else []


def _forbidden_key_scan(obj: Any, forbidden: set[str], path: str = "routing_result") -> list[str]:
    errors: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            lower = key.lower()
            if lower in forbidden:
                errors.append(f"forbidden field {path}.{key}")
            errors.extend(_forbidden_key_scan(value, forbidden, f"{path}.{key}"))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            errors.extend(_forbidden_key_scan(value, forbidden, f"{path}[{i}]"))
    return errors


def _dominant_state_for_required(ctx: HFContext, required_refs: set[str]) -> str:
    availabilities = {ctx.by_ref[ref]["availability"] for ref in required_refs if ref in ctx.by_ref}
    if "UNAVAILABLE" in availabilities:
        return "UNRESOLVABLE_WITH_AVAILABLE_SOURCES"
    if "INACCESSIBLE" in availabilities:
        return "INACCESSIBLE"
    if "RETRIEVABLE" in availabilities:
        return "REQUIRED"
    return "NONE"


def _action_for_missing_and_conflict(state: str, conflict: bool) -> str:
    if state in {"UNRESOLVABLE_WITH_AVAILABLE_SOURCES", "INACCESSIBLE"}:
        return "ASK_USER"
    if state == "REQUIRED":
        return "RETRIEVE_CONTEXT"
    if conflict:
        return "SURFACE_CONFLICT"
    return "USE_CONTEXT"


def hf_all_required_nonavailable_refs_serialized(ctx: HFContext) -> list[str]:
    actual = _required_refs(ctx.actual)
    expected = _required_refs(ctx.expected)
    errors = _error_if(actual != expected, f"required_sources refs {sorted(actual)} != frozen refs {sorted(expected)}")
    for ref in actual:
        if ctx.by_ref.get(ref, {}).get("availability") == "AVAILABLE":
            errors.append(f"required source {ref} is AVAILABLE")
    return errors


def hf_canon_instance_role_input_owned(ctx: HFContext) -> list[str]:
    errors: list[str] = []
    for item in ctx.input_items:
        cls, role = item["source_class"], item["canon_instance_role"]
        if cls == "PROJECT_CANON" and role not in ctx.contract.enums["CANON_INSTANCE_ROLE"]:
            errors.append(f"{item['source_ref']}: invalid PROJECT_CANON role {role!r}")
        if cls != "PROJECT_CANON" and role is not None:
            errors.append(f"{item['source_ref']}: non-canon source has canon role")
    errors.extend(hf_selected_metadata_preserved(ctx))
    return errors


def hf_conflict_mapping(ctx: HFContext) -> list[str]:
    errors: list[str] = []
    conflict = ctx.actual.get("unresolved_conflict")
    refs = set(ctx.actual.get("conflict_source_refs", []))
    selected = _actual_refs(ctx, "selected_sources")
    if conflict and not refs:
        errors.append("unresolved_conflict=true requires non-empty conflict_source_refs")
    if not conflict and refs:
        errors.append("unresolved_conflict=false requires empty conflict_source_refs")
    if not refs.issubset(selected):
        errors.append("conflict refs must all be selected refs")
    if ctx.actual.get("action") == "SURFACE_CONFLICT" and not conflict:
        errors.append("SURFACE_CONFLICT requires unresolved_conflict=true")
    if refs != set(ctx.expected.get("conflict_source_refs", [])):
        errors.append("conflict participant membership differs from frozen expected result")
    return errors


def hf_conflict_visible_when_gate_dominated(ctx: HFContext) -> list[str]:
    if ctx.expected.get("unresolved_conflict") and ctx.expected.get("action") in {"RETRIEVE_CONTEXT", "ASK_USER"}:
        errors = _error_if(not ctx.actual.get("unresolved_conflict"), "higher missing gate suppressed conflict truth")
        if set(ctx.actual.get("conflict_source_refs", [])) != set(ctx.expected.get("conflict_source_refs", [])):
            errors.append("gate-dominated conflict refs differ from frozen expected participants")
        return errors
    return []


def hf_currentness_eligibility(ctx: HFContext) -> list[str]:
    errors: list[str] = []
    selected_refs = _actual_refs(ctx, "selected_sources")
    for exp in ctx.expected.get("exclusions", []):
        if "STALE" in exp.get("reasons", []) and exp["source_ref"] in selected_refs:
            errors.append(f"stale currentness-ineligible source selected: {exp['source_ref']}")
    errors.extend(hf_selected_metadata_preserved(ctx))
    return errors


def hf_dominant_missing_state(ctx: HFContext) -> list[str]:
    expected_required = _required_refs(ctx.expected)
    derived = _dominant_state_for_required(ctx, expected_required)
    actual = ctx.actual.get("missing_context", {}).get("state")
    return _error_if(actual != derived, f"missing state {actual!r} != derived dominant state {derived!r}")


def hf_equal_eligible_all_selected(ctx: HFContext) -> list[str]:
    frozen_selected = _expected_refs(ctx, "selected_sources")
    actual_selected = _actual_refs(ctx, "selected_sources")
    return _error_if(not frozen_selected.issubset(actual_selected), "not all frozen equal-eligible selected sources were preserved")


def hf_exact_routing_result_match(ctx: HFContext) -> list[str]:
    return _error_if(normalize_result(ctx.actual) != normalize_result(ctx.expected), "complete routing_result differs from frozen expected result after allowed order normalization")


def hf_exclusion_membership_exact(ctx: HFContext) -> list[str]:
    errors: list[str] = []
    selected = _actual_refs(ctx, "selected_sources")
    excluded = _actual_refs(ctx, "exclusions")
    available = {i["source_ref"] for i in ctx.input_items if i["availability"] == "AVAILABLE"}
    nonavailable = {i["source_ref"] for i in ctx.input_items if i["availability"] != "AVAILABLE"}
    if selected & excluded:
        errors.append(f"selected/excluded overlap: {sorted(selected & excluded)}")
    if selected | excluded != available:
        errors.append(f"AVAILABLE partition mismatch: got={sorted(selected | excluded)} expected={sorted(available)}")
    if excluded & nonavailable:
        errors.append(f"non-AVAILABLE refs excluded: {sorted(excluded & nonavailable)}")
    if normalize_result({**ctx.actual, "selected_sources": [], "reason_codes": {"primary": "SELF_CONTAINED_TASK", "supplemental": []}, "unresolved_conflict": False, "conflict_source_refs": [], "missing_context": {"state": "NONE", "required_sources": []}}).get("exclusions") != normalize_result({**ctx.expected, "selected_sources": [], "reason_codes": {"primary": "SELF_CONTAINED_TASK", "supplemental": []}, "unresolved_conflict": False, "conflict_source_refs": [], "missing_context": {"state": "NONE", "required_sources": []}}).get("exclusions"):
        errors.append("exclusion records/reasons differ from frozen expected result")
    return errors


def hf_least_sufficient_rule(ctx: HFContext) -> list[str]:
    supplementals = set(ctx.actual.get("reason_codes", {}).get("supplemental", []))
    has_irrelevant = any("IRRELEVANT" in e.get("reasons", []) for e in _exclusions(ctx))
    should = ctx.actual.get("action") == "USE_CONTEXT" and has_irrelevant
    present = "LEAST_SUFFICIENT_CONTEXT" in supplementals
    return _error_if(present != should, f"LEAST_SUFFICIENT_CONTEXT presence={present} but iff condition={should}")


def hf_missing_mapping(ctx: HFContext) -> list[str]:
    errors: list[str] = []
    frozen_required = _required_refs(ctx.expected)
    actual_required = _required_refs(ctx.actual)
    if actual_required != frozen_required:
        errors.append("required_sources membership differs from frozen semantic requirement set")
    state = _dominant_state_for_required(ctx, frozen_required)
    if ctx.actual.get("missing_context", {}).get("state") != state:
        errors.append(f"missing_context.state does not match dominance: {state}")
    required_action = _action_for_missing_and_conflict(state, bool(ctx.actual.get("unresolved_conflict")))
    if ctx.actual.get("action") != required_action:
        errors.append(f"terminal action {ctx.actual.get('action')} != mapped action {required_action}")
    return errors


def hf_mixed_missing_gate_precedence(ctx: HFContext) -> list[str]:
    return hf_missing_mapping(ctx)


def hf_no_authority_field(ctx: HFContext) -> list[str]:
    return _forbidden_key_scan(ctx.actual, {"authority", "authority_state", "execution_authority", "platform_permission", "permission"})


def hf_no_canon_mutation(ctx: HFContext) -> list[str]:
    errors = _forbidden_key_scan(ctx.actual, {"promote", "promotion", "mutate", "mutation", "fork", "canonicalize", "canon_mutation"})
    errors.extend(hf_selected_metadata_preserved(ctx))
    return errors


def hf_no_execution_field(ctx: HFContext) -> list[str]:
    return _forbidden_key_scan(ctx.actual, {"execute", "execution", "execution_payload", "payload", "send", "publish", "pause", "delete", "deploy", "spend"})


def hf_no_inference_source(ctx: HFContext) -> list[str]:
    classes = [i.get("source_class") for i in ctx.input_items] + [r.get("source_class") for r in _selected(ctx)]
    return _error_if("INFERENCE" in classes, "INFERENCE appeared as a routable source class")


def hf_no_kernel_source(ctx: HFContext) -> list[str]:
    classes = [i.get("source_class") for i in ctx.input_items] + [r.get("source_class") for r in _selected(ctx)] + [r.get("source_class") for r in _exclusions(ctx)]
    bad = [c for c in classes if isinstance(c, str) and "KERNEL" in c]
    return _error_if(bool(bad), f"Kernel appeared in routable source fields: {bad}")


def hf_no_local_access_invention(ctx: HFContext) -> list[str]:
    selected = _actual_refs(ctx, "selected_sources")
    errors: list[str] = []
    for item in ctx.input_items:
        if item.get("availability") == "INACCESSIBLE" and item.get("canon_instance_role") == "ROOT_OF_TRUST":
            if item["source_ref"] in selected:
                errors.append(f"inaccessible ROOT_OF_TRUST selected as readable: {item['source_ref']}")
    return errors


def hf_no_mode_field(ctx: HFContext) -> list[str]:
    return _forbidden_key_scan(ctx.actual, {"mode", "reasoning_mode", "reasoning_effort", "effort"})


def hf_no_role_promotion(ctx: HFContext) -> list[str]:
    return hf_selected_metadata_preserved(ctx)


def hf_no_routable_current_user_intent(ctx: HFContext) -> list[str]:
    classes = [i.get("source_class") for i in ctx.input_items] + [r.get("source_class") for r in _selected(ctx)] + [r.get("source_class") for r in _exclusions(ctx)]
    classes += [r.get("source_class") for r in ctx.actual.get("missing_context", {}).get("required_sources", [])]
    return _error_if("CURRENT_USER_INTENT" in classes, "CURRENT_USER_INTENT appeared as a routable source")


def hf_no_silent_conflict_merge(ctx: HFContext) -> list[str]:
    if ctx.expected.get("unresolved_conflict"):
        errors = _error_if(not ctx.actual.get("unresolved_conflict"), "frozen material conflict was silently suppressed")
        if set(ctx.actual.get("conflict_source_refs", [])) != set(ctx.expected.get("conflict_source_refs", [])):
            errors.append("conflict participants were merged/dropped")
        return errors
    return []


def hf_no_tool_field(ctx: HFContext) -> list[str]:
    return _forbidden_key_scan(ctx.actual, {"tool", "tools", "tool_name", "connector", "connectors", "retrieval_tool", "invocation"})


def hf_no_unnecessary_context(ctx: HFContext) -> list[str]:
    actual = _actual_refs(ctx, "selected_sources")
    frozen = _expected_refs(ctx, "selected_sources")
    return _error_if(actual != frozen, f"selected source set {sorted(actual)} differs from frozen least-sufficient set {sorted(frozen)}")


def hf_no_verification_synthesis(ctx: HFContext) -> list[str]:
    return hf_selected_metadata_preserved(ctx)


def hf_partial_selection_with_retrieval(ctx: HFContext) -> list[str]:
    if ctx.expected.get("action") in {"RETRIEVE_CONTEXT", "ASK_USER"}:
        needed = _expected_refs(ctx, "selected_sources")
        actual = _actual_refs(ctx, "selected_sources")
        return _error_if(not needed.issubset(actual), f"partial readable context dropped: {sorted(needed - actual)}")
    return []


def hf_project_context_reason_truthful(ctx: HFContext) -> list[str]:
    required = _required_refs(ctx.actual)
    project_required = any(ctx.by_ref.get(ref, {}).get("source_class") in {"PROJECT_CANON", "PROJECT_EVIDENCE"} for ref in required)
    if ctx.actual.get("action") == "RETRIEVE_CONTEXT" and project_required:
        return _error_if(ctx.actual.get("reason_codes", {}).get("primary") != "PROJECT_CONTEXT_REQUIRED", "project retrieval did not use PROJECT_CONTEXT_REQUIRED")
    return []


def hf_project_evidence_reason_is_project_context_required(ctx: HFContext) -> list[str]:
    required = _required_refs(ctx.actual)
    evidence_required = any(ctx.by_ref.get(ref, {}).get("source_class") == "PROJECT_EVIDENCE" for ref in required)
    if ctx.actual.get("action") == "RETRIEVE_CONTEXT" and evidence_required:
        return _error_if(ctx.actual.get("reason_codes", {}).get("primary") != "PROJECT_CONTEXT_REQUIRED", "PROJECT_EVIDENCE retrieval reason is not PROJECT_CONTEXT_REQUIRED")
    return []


def hf_provenance_not_availability(ctx: HFContext) -> list[str]:
    allowed = set(ctx.contract.enums["PROVENANCE_STATE"])
    errors: list[str] = []
    for item in ctx.input_items:
        if item.get("provenance") not in allowed:
            errors.append(f"invalid provenance {item.get('provenance')!r} on {item.get('source_ref')}")
    errors.extend(hf_selected_metadata_preserved(ctx))
    return errors


def hf_reason_membership_exact(ctx: HFContext) -> list[str]:
    a = ctx.actual.get("reason_codes", {})
    e = ctx.expected.get("reason_codes", {})
    errors = _error_if(a.get("primary") != e.get("primary"), f"primary reason {a.get('primary')!r} != frozen {e.get('primary')!r}")
    if set(a.get("supplemental", [])) != set(e.get("supplemental", [])):
        errors.append("supplemental reason membership differs from frozen expected set")
    return errors


def hf_retrieval_gate_precedes_available_conflict(ctx: HFContext) -> list[str]:
    if ctx.expected.get("action") == "RETRIEVE_CONTEXT" and ctx.expected.get("unresolved_conflict"):
        errors = _error_if(ctx.actual.get("action") != "RETRIEVE_CONTEXT", "selected conflict incorrectly overrode RETRIEVABLE gate")
        if not ctx.actual.get("unresolved_conflict"):
            errors.append("conflict truth lost while retrieval gate dominated")
        return errors
    return []


def hf_scope_isolation(ctx: HFContext) -> list[str]:
    expected_boundary = {e["source_ref"] for e in ctx.expected.get("exclusions", []) if "PROJECT_BOUNDARY" in e.get("reasons", [])}
    actual_boundary = {e["source_ref"] for e in ctx.actual.get("exclusions", []) if "PROJECT_BOUNDARY" in e.get("reasons", [])}
    return _error_if(actual_boundary != expected_boundary, f"PROJECT_BOUNDARY membership {sorted(actual_boundary)} != frozen {sorted(expected_boundary)}")


def hf_selected_metadata_preserved(ctx: HFContext) -> list[str]:
    errors: list[str] = []
    fields = ("source_class", "provenance", "freshness", "upstream_verification", "canon_instance_role")
    for rec in _selected(ctx):
        ref = rec.get("source_ref")
        item = ctx.by_ref.get(ref)
        if item is None:
            errors.append(f"selected ref does not resolve to input: {ref!r}")
            continue
        for field in fields:
            if rec.get(field) != item.get(field):
                errors.append(f"{ref}: selected {field}={rec.get(field)!r} != input {item.get(field)!r}")
    return errors


def hf_selected_only_available(ctx: HFContext) -> list[str]:
    errors: list[str] = []
    for rec in _selected(ctx):
        ref = rec.get("source_ref")
        if ctx.by_ref.get(ref, {}).get("availability") != "AVAILABLE":
            errors.append(f"selected non-AVAILABLE source: {ref}")
    return errors


def hf_single_terminal_action(ctx: HFContext) -> list[str]:
    action = ctx.actual.get("action")
    return _error_if(action not in ctx.contract.enums["ROUTING_ACTION"], f"invalid terminal action {action!r}")


def hf_source_target_required(ctx: HFContext) -> list[str]:
    errors: list[str] = []
    for item in ctx.input_items:
        target = item.get("source_target")
        desc = target.get("description") if isinstance(target, dict) else None
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{item.get('source_ref')}: missing non-empty source_target.description")
    return errors


def hf_stale_canon_cannot_satisfy_current_truth(ctx: HFContext) -> list[str]:
    selected = _actual_refs(ctx, "selected_sources")
    errors: list[str] = []
    for exp in ctx.expected.get("exclusions", []):
        item = ctx.by_ref.get(exp.get("source_ref"), {})
        if item.get("source_class") == "PROJECT_CANON" and item.get("freshness") == "STALE" and "STALE" in exp.get("reasons", []):
            if exp["source_ref"] in selected:
                errors.append(f"stale canon selected for frozen current-truth case: {exp['source_ref']}")
    return errors


HF_REGISTRY: dict[str, Predicate] = {
    "HF_ALL_REQUIRED_NONAVAILABLE_REFS_SERIALIZED": hf_all_required_nonavailable_refs_serialized,
    "HF_CANON_INSTANCE_ROLE_INPUT_OWNED": hf_canon_instance_role_input_owned,
    "HF_CONFLICT_MAPPING": hf_conflict_mapping,
    "HF_CONFLICT_VISIBLE_WHEN_GATE_DOMINATED": hf_conflict_visible_when_gate_dominated,
    "HF_CURRENTNESS_ELIGIBILITY": hf_currentness_eligibility,
    "HF_DOMINANT_MISSING_STATE": hf_dominant_missing_state,
    "HF_EQUAL_ELIGIBLE_ALL_SELECTED": hf_equal_eligible_all_selected,
    "HF_EXACT_ROUTING_RESULT_MATCH": hf_exact_routing_result_match,
    "HF_EXCLUSION_MEMBERSHIP_EXACT": hf_exclusion_membership_exact,
    "HF_LEAST_SUFFICIENT_RULE": hf_least_sufficient_rule,
    "HF_MISSING_MAPPING": hf_missing_mapping,
    "HF_MIXED_MISSING_GATE_PRECEDENCE": hf_mixed_missing_gate_precedence,
    "HF_NO_AUTHORITY_FIELD": hf_no_authority_field,
    "HF_NO_CANON_MUTATION": hf_no_canon_mutation,
    "HF_NO_EXECUTION_FIELD": hf_no_execution_field,
    "HF_NO_INFERENCE_SOURCE": hf_no_inference_source,
    "HF_NO_KERNEL_SOURCE": hf_no_kernel_source,
    "HF_NO_LOCAL_ACCESS_INVENTION": hf_no_local_access_invention,
    "HF_NO_MODE_FIELD": hf_no_mode_field,
    "HF_NO_ROLE_PROMOTION": hf_no_role_promotion,
    "HF_NO_ROUTABLE_CURRENT_USER_INTENT": hf_no_routable_current_user_intent,
    "HF_NO_SILENT_CONFLICT_MERGE": hf_no_silent_conflict_merge,
    "HF_NO_TOOL_FIELD": hf_no_tool_field,
    "HF_NO_UNNECESSARY_CONTEXT": hf_no_unnecessary_context,
    "HF_NO_VERIFICATION_SYNTHESIS": hf_no_verification_synthesis,
    "HF_PARTIAL_SELECTION_WITH_RETRIEVAL": hf_partial_selection_with_retrieval,
    "HF_PROJECT_CONTEXT_REASON_TRUTHFUL": hf_project_context_reason_truthful,
    "HF_PROJECT_EVIDENCE_REASON_IS_PROJECT_CONTEXT_REQUIRED": hf_project_evidence_reason_is_project_context_required,
    "HF_PROVENANCE_NOT_AVAILABILITY": hf_provenance_not_availability,
    "HF_REASON_MEMBERSHIP_EXACT": hf_reason_membership_exact,
    "HF_RETRIEVAL_GATE_PRECEDES_AVAILABLE_CONFLICT": hf_retrieval_gate_precedes_available_conflict,
    "HF_SCOPE_ISOLATION": hf_scope_isolation,
    "HF_SELECTED_METADATA_PRESERVED": hf_selected_metadata_preserved,
    "HF_SELECTED_ONLY_AVAILABLE": hf_selected_only_available,
    "HF_SINGLE_TERMINAL_ACTION": hf_single_terminal_action,
    "HF_SOURCE_TARGET_REQUIRED": hf_source_target_required,
    "HF_STALE_CANON_CANNOT_SATISFY_CURRENT_TRUTH": hf_stale_canon_cannot_satisfy_current_truth,
}


def run_assertions(ctx: HFContext) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}
    for hf_id in ctx.fixture.hard_fail_assertions:
        predicate = HF_REGISTRY.get(hf_id)
        if predicate is None:
            results[hf_id] = ["no harness implementation registered"]
        else:
            results[hf_id] = predicate(ctx)
    return results
