from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

import yaml

from .contract import ContractData, Fixture, load_contract
from .hf import HFContext, HF_REGISTRY, run_assertions
from .normalize import normalize_result
from .schema import validate_fixture, validate_routing_result


EXPECTED_CASE_IDS = tuple(f"CR-{i:03d}" for i in range(1, 21))


@dataclass
class StaticReport:
    verdict: str
    r5_parse: str
    fixture_count: int
    fixture_ids_exact: bool
    hf_defined: int
    hf_used: int
    hf_registry_count: int
    hf_catalog_registry_exact: bool
    undefined_fixture_hf: list[str]
    unused_catalog_hf: list[str]
    schema_enum_validation: str
    expected_result_static_validation: str
    issues: list[str]


@dataclass
class CaseReport:
    case_id: str
    verdict: str
    schema_issues: list[str]
    result_match: bool | None
    hf_results: dict[str, list[str]]


@dataclass
class SuiteReport:
    verdict: str
    static_harness: str
    captures_present: int
    case_reports: list[CaseReport]
    pass_count: int
    fail_result_mismatch: int
    fail_hard_assertion: int
    invalid_output: int
    missing_capture: int
    semantic_regression_automation: str = "MANUAL_CHATGPT_INVOCATION_NOT_PERFORMED_BY_HARNESS"


def _fixture_hf_sets(contract: ContractData) -> tuple[set[str], set[str]]:
    used = {hf for fixture in contract.fixtures.values() for hf in fixture.hard_fail_assertions}
    defined = set(contract.hf_catalog)
    return used, defined


def static_check(contract: ContractData) -> StaticReport:
    issues: list[str] = []
    ids = tuple(sorted(contract.fixtures))
    exact_ids = ids == EXPECTED_CASE_IDS
    if not exact_ids:
        issues.append(f"fixture IDs mismatch: got={ids}")

    used, defined = _fixture_hf_sets(contract)
    undefined = sorted(used - defined)
    unused = sorted(defined - used)
    registry_exact = defined == set(HF_REGISTRY)
    if not registry_exact:
        issues.append(
            f"HF registry/catalog mismatch: missing={sorted(defined - set(HF_REGISTRY))}, extra={sorted(set(HF_REGISTRY) - defined)}"
        )

    fixture_issues: list[str] = []
    for fixture in contract.fixtures.values():
        fixture_issues.extend(issue.render() for issue in validate_fixture(fixture, contract))
    issues.extend(fixture_issues)

    if len(contract.fixtures) != 20:
        issues.append(f"fixture count is {len(contract.fixtures)}, expected 20")
    if len(defined) != 37:
        issues.append(f"HF catalog defines {len(defined)}, expected 37")
    if undefined:
        issues.append(f"undefined fixture HF IDs: {undefined}")
    if unused:
        issues.append(f"unused catalog HF IDs: {unused}")

    verdict = "PASS" if not issues else "BLOCKED"
    return StaticReport(
        verdict=verdict,
        r5_parse="PASS" if len(contract.fixtures) else "FAIL",
        fixture_count=len(contract.fixtures),
        fixture_ids_exact=exact_ids,
        hf_defined=len(defined),
        hf_used=len(used),
        hf_registry_count=len(HF_REGISTRY),
        hf_catalog_registry_exact=registry_exact,
        undefined_fixture_hf=undefined,
        unused_catalog_hf=unused,
        schema_enum_validation="PASS" if not fixture_issues else "FAIL",
        expected_result_static_validation="PASS" if not fixture_issues else "FAIL",
        issues=issues,
    )


def _load_capture(path: Path, fixture: Fixture) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"capture parse failure: {exc}"]
    if not isinstance(obj, dict):
        return None, ["capture must be a YAML mapping"]
    if set(obj) != {"id", "routing_result"}:
        return None, [f"capture wrapper must contain exactly id+routing_result; got keys={sorted(obj)}"]
    if obj.get("id") != fixture.case_id:
        return None, [f"capture id {obj.get('id')!r} != expected {fixture.case_id!r}"]
    if not isinstance(obj.get("routing_result"), dict):
        return None, ["routing_result must be a mapping"]
    return obj["routing_result"], []


def validate_capture(fixture: Fixture, capture_path: Path, contract: ContractData) -> CaseReport:
    actual, load_issues = _load_capture(capture_path, fixture)
    if load_issues:
        return CaseReport(fixture.case_id, "INVALID_OUTPUT", load_issues, None, {})

    assert actual is not None
    schema_issues = [i.render() for i in validate_routing_result(actual, fixture, contract)]
    if schema_issues:
        return CaseReport(fixture.case_id, "INVALID_OUTPUT", schema_issues, None, {})

    exact = normalize_result(actual) == normalize_result(fixture.expected_result)
    hf_results = run_assertions(HFContext(fixture=fixture, actual=actual, contract=contract))
    hf_failures = {k: v for k, v in hf_results.items() if v}

    if not exact:
        verdict = "FAIL_RESULT_MISMATCH"
    elif hf_failures:
        verdict = "FAIL_HARD_ASSERTION"
    else:
        verdict = "PASS"
    return CaseReport(fixture.case_id, verdict, [], exact, hf_results)


def validate_suite(contract: ContractData, captures_dir: Path) -> SuiteReport:
    static = static_check(contract)
    if static.verdict != "PASS":
        return SuiteReport(
            verdict="BLOCKED_STATIC_HARNESS",
            static_harness=static.verdict,
            captures_present=0,
            case_reports=[],
            pass_count=0,
            fail_result_mismatch=0,
            fail_hard_assertion=0,
            invalid_output=0,
            missing_capture=20,
        )

    reports: list[CaseReport] = []
    present = 0
    for case_id in EXPECTED_CASE_IDS:
        fixture = contract.fixtures[case_id]
        path = captures_dir / f"{case_id}.yaml"
        if not path.exists():
            reports.append(CaseReport(case_id, "MISSING_CAPTURE", [], None, {}))
            continue
        present += 1
        reports.append(validate_capture(fixture, path, contract))

    counts = {
        "PASS": sum(r.verdict == "PASS" for r in reports),
        "FAIL_RESULT_MISMATCH": sum(r.verdict == "FAIL_RESULT_MISMATCH" for r in reports),
        "FAIL_HARD_ASSERTION": sum(r.verdict == "FAIL_HARD_ASSERTION" for r in reports),
        "INVALID_OUTPUT": sum(r.verdict == "INVALID_OUTPUT" for r in reports),
        "MISSING_CAPTURE": sum(r.verdict == "MISSING_CAPTURE" for r in reports),
    }
    verdict = "CONFORMANT" if counts["PASS"] == 20 else ("INCOMPLETE" if counts["MISSING_CAPTURE"] else "NON_CONFORMANT")
    return SuiteReport(
        verdict=verdict,
        static_harness=static.verdict,
        captures_present=present,
        case_reports=reports,
        pass_count=counts["PASS"],
        fail_result_mismatch=counts["FAIL_RESULT_MISMATCH"],
        fail_hard_assertion=counts["FAIL_HARD_ASSERTION"],
        invalid_output=counts["INVALID_OUTPUT"],
        missing_capture=counts["MISSING_CAPTURE"],
    )


def write_report(path: Path, report: StaticReport | SuiteReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "report": asdict(report),
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path: str | Path) -> ContractData:
    return load_contract(path)
