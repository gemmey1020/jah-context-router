from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from .runner import load, static_check, validate_suite, write_report


def _print(obj) -> None:
    print(json.dumps(asdict(obj), indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jah-router-harness",
        description="Ω JAH Context Router v0.1 frozen-R5 conformance harness (no semantic routing).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_static = sub.add_parser("static", help="Parse R5 and validate fixtures/catalog/schema mechanically")
    p_static.add_argument("--contract", required=True, type=Path)
    p_static.add_argument("--report", type=Path)

    p_validate = sub.add_parser("validate", help="Validate captured semantic routing_results against frozen R5")
    p_validate.add_argument("--contract", required=True, type=Path)
    p_validate.add_argument("--captures", required=True, type=Path)
    p_validate.add_argument("--report", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        contract = load(args.contract)
        if args.command == "static":
            report = static_check(contract)
        else:
            report = validate_suite(contract, args.captures)
        _print(report)
        if args.report:
            write_report(args.report, report)
        if args.command == "static":
            return 0 if report.verdict == "PASS" else 2
        return 0 if report.verdict == "CONFORMANT" else 3
    except Exception as exc:
        print(json.dumps({"verdict": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
