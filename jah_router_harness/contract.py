from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml


CASE_RE = re.compile(
    r"^### CASE (CR-\d{3})\b[^\n]*\n\n```yaml\n(.*?)^```",
    re.MULTILINE | re.DOTALL,
)
HF_SECTION_RE = re.compile(
    r"^## 24\. HARD_FAIL_ASSERTION_CATALOG\n(.*?)(?=^## 25\.)",
    re.MULTILINE | re.DOTALL,
)
HF_DEF_RE = re.compile(r"^- `(HF_[A-Z0-9_]+)`\s+—\s+(.*)$", re.MULTILINE)


@dataclass(frozen=True)
class Fixture:
    case_id: str
    title: str
    routing_input: dict[str, Any]
    expected_result: dict[str, Any]
    hard_fail_assertions: tuple[str, ...]


@dataclass(frozen=True)
class ContractData:
    path: Path
    text: str
    fixtures: dict[str, Fixture]
    hf_catalog: dict[str, str]
    enums: dict[str, tuple[str, ...]]


def _load_yaml_block(block: str, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        raise ValueError(f"{label}: YAML parse failure: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}: expected a YAML mapping")
    return value


def _extract_exact_vocab(text: str, symbol: str) -> tuple[str, ...]:
    pattern = re.compile(
        rf"`{re.escape(symbol)}`\s+is\s+exactly:\s*\n\n```text\n(.*?)```",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Unable to extract frozen vocabulary for {symbol}")
    return tuple(line.strip() for line in match.group(1).splitlines() if line.strip())


def _extract_exclusion_vocab(text: str) -> tuple[str, ...]:
    pattern = re.compile(
        r"The exclusion vocabulary remains exactly:\s*\n\n```text\n(.*?)```",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError("Unable to extract frozen exclusion vocabulary")
    return tuple(line.strip() for line in match.group(1).splitlines() if line.strip())


def _extract_runtime_reasons(text: str) -> tuple[str, ...]:
    marker = "## 22. RUNTIME_REASON_CODES"
    start = text.find(marker)
    if start < 0:
        raise ValueError("Unable to find RUNTIME_REASON_CODES section")
    tail = text[start:]
    match = re.search(r"```text\n(.*?)```", tail, re.DOTALL)
    if not match:
        raise ValueError("Unable to extract runtime reason vocabulary")
    return tuple(line.strip() for line in match.group(1).splitlines() if line.strip())


def load_contract(path: str | Path) -> ContractData:
    contract_path = Path(path)
    text = contract_path.read_text(encoding="utf-8")

    fixtures: dict[str, Fixture] = {}
    for heading_id, block in CASE_RE.findall(text):
        obj = _load_yaml_block(block, heading_id)
        case_id = obj.get("id")
        if case_id != heading_id:
            raise ValueError(f"{heading_id}: YAML id mismatch: {case_id!r}")
        expected = obj.get("expected")
        if not isinstance(expected, dict) or not isinstance(expected.get("routing_result"), dict):
            raise ValueError(f"{heading_id}: expected.routing_result missing")
        hfs = obj.get("hard_fail_assertions")
        if not isinstance(hfs, list) or not all(isinstance(x, str) for x in hfs):
            raise ValueError(f"{heading_id}: hard_fail_assertions must be a string list")
        fixture = Fixture(
            case_id=case_id,
            title=str(obj.get("title", "")),
            routing_input=obj.get("routing_input"),
            expected_result=expected["routing_result"],
            hard_fail_assertions=tuple(hfs),
        )
        if case_id in fixtures:
            raise ValueError(f"Duplicate fixture id: {case_id}")
        fixtures[case_id] = fixture

    hf_section = HF_SECTION_RE.search(text)
    if not hf_section:
        raise ValueError("Unable to find Section 24 hard-fail assertion catalog")
    hf_catalog = {hf_id: desc.strip() for hf_id, desc in HF_DEF_RE.findall(hf_section.group(1))}

    enums = {
        "SOURCE_CLASS": _extract_exact_vocab(text, "SOURCE_CLASS"),
        "PROVENANCE_STATE": _extract_exact_vocab(text, "PROVENANCE_STATE"),
        "AVAILABILITY_STATE": _extract_exact_vocab(text, "AVAILABILITY_STATE"),
        "FRESHNESS_STATE": _extract_exact_vocab(text, "FRESHNESS_STATE"),
        "VERIFICATION_STATE": _extract_exact_vocab(text, "VERIFICATION_STATE"),
        "CANON_INSTANCE_ROLE": _extract_exact_vocab(text, "CANON_INSTANCE_ROLE"),
        "MISSING_CONTEXT_STATE": _extract_exact_vocab(text, "MISSING_CONTEXT_STATE"),
        "ROUTING_ACTION": _extract_exact_vocab(text, "ROUTING_ACTION"),
        "EXCLUSION_REASON": _extract_exclusion_vocab(text),
        "RUNTIME_REASON_CODE": _extract_runtime_reasons(text),
    }

    return ContractData(
        path=contract_path,
        text=text,
        fixtures=fixtures,
        hf_catalog=hf_catalog,
        enums=enums,
    )
