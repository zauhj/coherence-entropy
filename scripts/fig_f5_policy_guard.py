#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
from typing import Any, Dict, List


def default_stub() -> Dict[str, Any]:
    return {
        "figure": "F5_Policy_Guard_Diagram",
        "layers": [
            {
                "name": "Dynamics",
                "policies": [
                    {
                        "id": "bp_ft",
                        "title": "Basin‑Preserving Fine‑Tuning",
                        "controls": ["lambda_reg", "curriculum", "noise_sink"],
                        "monitors": ["Hc", "trap_pass_rate"],
                        "detectors": ["threshold", "cusum"],
                        "actions": ["reduce_lr", "increase_lambda", "halt_training"],
                    }
                ],
            },
            {
                "name": "Interface",
                "policies": [
                    {
                        "id": "attention_preserve",
                        "title": "Attention‑Preserving UX",
                        "controls": ["map_first_ui", "evidence_view", "inline_citations"],
                        "monitors": ["click_diversion", "time_on_source", "citation_toggle"],
                        "detectors": ["incoherence_ui_events"],
                        "actions": ["expand_sources", "prompt_for_clarification"],
                    }
                ],
            },
            {
                "name": "Governance",
                "policies": [
                    {
                        "id": "json_ui_guard",
                        "title": "JSON‑UI Policy Guard",
                        "controls": ["schema_enforcement", "refusal_reason_codes"],
                        "monitors": ["spec_valid"],
                        "detectors": ["schema_violation"],
                        "actions": ["reject_output", "request_retry", "escalate"],
                    }
                ],
            },
        ],
        "wiring": [
            {"from": "Hc", "to": "threshold", "type": "monitor"},
            {"from": "threshold", "to": "increase_lambda", "type": "trigger"},
            {"from": "schema_violation", "to": "reject_output", "type": "trigger"},
            {"from": "incoherence_ui_events", "to": "prompt_for_clarification", "type": "trigger"},
        ],
        "notes": "This is a data stub for figure rendering; downstream plotting can layout nodes/edges."
    }


def main():
    ap = argparse.ArgumentParser(description='F5: Policy/Guard diagram data stub generator')
    ap.add_argument('--input', default=None, help='Optional path to a JSON schema for policies/guards; if omitted, uses a default stub')
    ap.add_argument('--out', default=os.path.join('Research','papers','macro-safety','figures','f5_policy_guard.json'))
    args = ap.parse_args()

    if args.input and os.path.isfile(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = default_stub()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(json.dumps({'wrote': args.out, 'layers': len(data.get('layers', []))}, indent=2))


if __name__ == '__main__':
    main()
