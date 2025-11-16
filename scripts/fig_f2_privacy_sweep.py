#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys, math
from statistics import mean, pstdev
from typing import Any, Dict, List, Tuple


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    with open(path, 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                obj = json.loads(ln)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                out.append(obj)
    return out


def ci95(vals: List[float]) -> Tuple[float, float]:
    if not vals:
        return 0.0, 0.0
    m = mean(vals)
    if len(vals) == 1:
        return m, m
    s = pstdev(vals)
    se = s / math.sqrt(len(vals)) if len(vals) > 0 else 0.0
    return m - 1.96 * se, m + 1.96 * se


def main():
    ap = argparse.ArgumentParser(description='F2: Privacy sweep over dp_sigma for BP-FT sweeps')
    ap.add_argument('--runs-dir', default=os.path.join('Research','papers','basin-preserving-finetune','runs'))
    ap.add_argument('--pattern', default='bpft_lambda_sweep_dp_')
    ap.add_argument('--out', default=os.path.join('Research','papers','macro-safety','figures','f2_bpf_privacy_sweep.json'))
    args = ap.parse_args()

    if not os.path.isdir(args.runs_dir):
        print(json.dumps({'error':'runs-dir not found','runs_dir':args.runs_dir}, indent=2))
        sys.exit(2)

    files = [os.path.join(args.runs_dir, fn) for fn in os.listdir(args.runs_dir) if fn.startswith(args.pattern) and fn.endswith('.jsonl')]
    if not files:
        # fallback: include any sweep file containing dp_sigma field
        files = [os.path.join(args.runs_dir, fn) for fn in os.listdir(args.runs_dir) if fn.endswith('.jsonl')]
    files.sort()

    all_rows: List[Dict[str, Any]] = []
    for fp in files:
        try:
            rows = read_jsonl(fp)
            all_rows.extend(rows)
        except Exception as e:
            sys.stderr.write(f"[warn] skipping {fp}: {e}\n")

    # Determine which coherence metric to use
    has_hc_post = any(isinstance(r, dict) and ('Hc_post' in r) for r in all_rows)
    hc_key = 'Hc_post' if has_hc_post else 'Hc'

    # group by dp_sigma then lambda
    groups: Dict[float, Dict[float, List[Dict[str, Any]]]] = {}
    for r in all_rows:
        if 'dp_sigma' not in r or 'lambda' not in r:
            continue
        ds = float(r.get('dp_sigma'))
        lam = float(r.get('lambda'))
        groups.setdefault(ds, {}).setdefault(lam, []).append(r)

    series: List[Dict[str, Any]] = []
    metrics = ['cooperation_rate','reward', hc_key]
    for dp in sorted(groups.keys()):
        lam_groups = groups[dp]
        lam_series: List[Dict[str, Any]] = []
        for lam in sorted(lam_groups.keys()):
            rs = lam_groups[lam]
            entry: Dict[str, Any] = {'dp_sigma': dp, 'lambda': lam, 'n': len(rs)}
            for mk in metrics:
                vals = [float(r.get(mk)) for r in rs if r.get(mk) is not None]
                if not vals:
                    continue
                m = mean(vals)
                lo, hi = ci95(vals)
                entry[mk] = m
                entry[f'{mk}_ci'] = [lo, hi]
            lam_series.append(entry)
        series.append({'dp_sigma': dp, 'points': lam_series})

    out = {
        'figure': 'F2_BPF_Privacy_Sweep',
        'inputs': files,
        'series_by_dp': series,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)

    print(json.dumps({'wrote': args.out, 'dp_levels': len(series), 'metric': hc_key}, indent=2))


if __name__ == '__main__':
    main()
