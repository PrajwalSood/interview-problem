"""Small in-memory private-markets domain for the interview."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from coworker_agent.tools import Tool, ToolRegistry


FUNDS = {
    "FUND-ALPHA": {
        "name": "Alpha Growth Fund IV",
        "manager": "Alpha Capital",
        "operations_contact": "ops@alpha.example",
    },
    "FUND-BETA": {
        "name": "Beta Ventures II",
        "manager": "Beta Ventures",
        "operations_contact": "finance@beta.example",
    },
}

EXPECTED = {
    ("FUND-ALPHA", "2026-Q2"): [
        "capital_account_statement",
        "quarterly_report",
        "statement_of_investments",
    ],
    ("FUND-BETA", "2026-Q2"): [
        "capital_account_statement",
        "quarterly_report",
    ],
}

RECEIVED = {
    ("FUND-ALPHA", "2026-Q2"): ["capital_account_statement"],
    ("FUND-BETA", "2026-Q2"): [
        "capital_account_statement",
        "quarterly_report",
    ],
}


def _require_fund(fund_code: str) -> Mapping[str, Any]:
    if fund_code not in FUNDS:
        raise ValueError("unknown fund")
    return FUNDS[fund_code]


def get_fund_profile(arguments: Mapping[str, Any]) -> Mapping[str, Any]:
    fund_code = str(arguments["fund_code"])
    return {"fund_code": fund_code, **_require_fund(fund_code)}


def list_expected_documents(arguments: Mapping[str, Any]) -> Mapping[str, Any]:
    fund_code = str(arguments["fund_code"])
    quarter = str(arguments["quarter"])
    _require_fund(fund_code)
    return {
        "fund_code": fund_code,
        "quarter": quarter,
        "documents": EXPECTED.get((fund_code, quarter), []),
    }


def list_received_documents(arguments: Mapping[str, Any]) -> Mapping[str, Any]:
    fund_code = str(arguments["fund_code"])
    quarter = str(arguments["quarter"])
    _require_fund(fund_code)
    return {
        "fund_code": fund_code,
        "quarter": quarter,
        "documents": RECEIVED.get((fund_code, quarter), []),
    }


def create_follow_up_draft(arguments: Mapping[str, Any]) -> Mapping[str, Any]:
    missing = list(arguments["missing_documents"])
    canonical = json.dumps(arguments, sort_keys=True).encode()
    draft_id = "draft-" + hashlib.sha256(canonical).hexdigest()[:10]
    return {
        "draft_id": draft_id,
        "status": "draft_only_not_sent",
        "to": arguments["recipient"],
        "subject": arguments["subject"],
        "missing_documents": missing,
    }


def _object_schema(
    properties: Mapping[str, Any], required: list[str]
) -> Mapping[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def build_document_chase_registry() -> ToolRegistry:
    fund = {"fund_code": {"type": "string"}}
    period = {
        "fund_code": {"type": "string"},
        "quarter": {"type": "string"},
    }
    tools = [
        Tool(
            "get_fund_profile",
            "Get fund name, manager, and operations contact.",
            _object_schema(fund, ["fund_code"]),
            get_fund_profile,
        ),
        Tool(
            "list_expected_documents",
            "List document types expected for a fund and quarter.",
            _object_schema(period, ["fund_code", "quarter"]),
            list_expected_documents,
        ),
        Tool(
            "list_received_documents",
            "List document types already received for a fund and quarter.",
            _object_schema(period, ["fund_code", "quarter"]),
            list_received_documents,
        ),
        Tool(
            "create_follow_up_draft",
            "Create, but do not send, a follow-up email draft.",
            _object_schema(
                {
                    "recipient": {"type": "string"},
                    "subject": {"type": "string"},
                    "missing_documents": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                ["recipient", "subject", "missing_documents"],
            ),
            create_follow_up_draft,
        ),
    ]
    return ToolRegistry({tool.name: tool for tool in tools})
