#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
from typing import Any, Dict, List


def load_detection(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_methods(rec: Dict[str, Any]) -> Dict[str, Any]:
    thr = rec.get("threshold", {}) or {}
    cu = rec.get("cusum", {}) or {}
    label = rec.get("label")
    n = rec.get("n")

    thr_spike = thr.get("spike_idx") is not None
    thr_dip = thr.get("dip_idx") is not None
    cu_spike = cu.get("spike_idx") is not None
    cu_dip = cu.get("dip_idx") is not None

    # deltas if both present
    def delta(a, b):
        if a is None or b is None:
            return None
        try:
            return abs(int(a) - int(b))
        except Exception:
            return None

    spike_delta_idx = delta(thr.get("spike_idx"), cu.get("spike_idx"))
    dip_delta_idx = delta(thr.get("dip_idx"), cu.get("dip_idx"))

    out = {
        "label": label,
        "n": n,
        "threshold": {
            "spike": thr_spike,
            "dip": thr_dip,
            "spike_idx": thr.get("spike_idx"),
            "dip_idx": thr.get("dip_idx"),
            "spike_date": thr.get("spike_date"),
            "dip_date": thr.get("dip_date"),
        },
        "cusum": {
            "spike": cu_spike,
            "dip": cu_dip,
            "spike_idx": cu.get("spike_idx"),
            "dip_idx": cu.get("dip_idx"),
            "spike_date": cu.get("spike_date"),
            "dip_date": cu.get("dip_date"),
        },
        "agreement": {
            "spike": (thr_spike == cu_spike),
            "dip": (thr_dip == cu_dip),
        },
        "delta": {
            "spike_idx": spike_delta_idx,
            "dip_idx": dip_delta_idx,
        },
    }
    return out


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    thr_spike = sum(1 for r in records if r["threshold"]["spike"]) if total else 0
    cu_spike = sum(1 for r in records if r["cusum"]["spike"]) if total else 0
    thr_dip = sum(1 for r in records if r["threshold"]["dip"]) if total else 0
    cu_dip = sum(1 for r in records if r["cusum"]["dip"]) if total else 0

    both_spike = sum(1 for r in records if r["threshold"]["spike"] and r["cusum"]["spike"]) if total else 0
    either_spike = sum(1 for r in records if r["threshold"]["spike"] or r["cusum"]["spike"]) if total else 0
    both_dip = sum(1 for r in records if r["threshold"]["dip"] and r["cusum"]["dip"]) if total else 0
    either_dip = sum(1 for r in records if r["threshold"]["dip"] or r["cusum"]["dip"]) if total else 0

    agree_spike = sum(1 for r in records if r["agreement"]["spike"]) if total else 0
    agree_dip = sum(1 for r in records if r["agreement"]["dip"]) if total else 0

    # average deltas where both exist
    def avg_delta(key: str) -> float | None:
        vals = [r["delta"][key] for r in records if isinstance(r["delta"][key], int)]
        if not vals:
            return None
        return sum(vals) / len(vals)

    return {
        "counts": {
            "total": total,
            "threshold_spike": thr_spike,
            "cusum_spike": cu_spike,
            "threshold_dip": thr_dip,
            "cusum_dip": cu_dip,
            "both_spike": both_spike,
            "either_spike": either_spike,
            "both_dip": both_dip,
            "either_dip": either_dip,
        },
        "agreement_rate": {
            "spike": (agree_spike / total) if total else None,
            "dip": (agree_dip / total) if total else None,
        },
        "avg_delta_idx": {
            "spike": avg_delta("spike_idx"),
            "dip": avg_delta("dip_idx"),
        },
    }


def main():
    ap = argparse.ArgumentParser(description="F3: Compare threshold vs CUSUM detection across AIW series")
    ap.add_argument("--data-dir", default=os.path.join("aiw","data"))
    ap.add_argument("--out", default=os.path.join("figures","f3_detection_compare.json"))
    args = ap.parse_args()

    if not os.path.isdir(args.data_dir):
        print(json.dumps({"error": "data-dir not found", "data_dir": args.data_dir}, indent=2))
        sys.exit(2)

    # load all detect_*.json files
    det_files = [os.path.join(args.data_dir, fn) for fn in os.listdir(args.data_dir) if fn.startswith("detect_") and fn.endswith(".json")]
    det_files.sort()
    per: List[Dict[str, Any]] = []
    for fp in det_files:
        try:
            rec = load_detection(fp)
            cmp = compare_methods(rec)
            per.append(cmp)
        except Exception as e:
            # skip malformed
            sys.stderr.write(f"[warn] skipping {fp}: {e}\n")
            continue

    summary = summarize(per)
    out = {
        "figure": "F3_detection_compare",
        "inputs": det_files,
        "summary": summary,
        "records": per,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(json.dumps({"wrote": args.out, "n_series": len(per), "agreement_spike": summary["agreement_rate"]["spike"]}, indent=2))


if __name__ == "__main__":
    main()
