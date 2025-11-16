#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
from statistics import mean
from typing import Any, Dict, List, Tuple

# Utilities largely mirrored from detect_series.py but with parameter grid

def zscores(vals: List[float]) -> List[float]:
    if not vals:
        return []
    m = mean(vals)
    # population std
    s = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5 if len(vals) > 1 else 0.0
    if s == 0:
        return [0.0 for _ in vals]
    return [(v - m) / s for v in vals]


def threshold_detect(z: List[float], up: float, down: float) -> Tuple[int | None, int | None]:
    up_idx = next((i for i, zi in enumerate(z) if zi >= up), None)
    down_idx = next((i for i, zi in enumerate(z) if zi <= down), None)
    return up_idx, down_idx


def cusum_detect(vals: List[float], k_factor: float, h_factor: float) -> Tuple[int | None, int | None]:
    if not vals:
        return None, None
    m = mean(vals)
    s = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5 if len(vals) > 1 else 0.0
    if s == 0:
        return None, None
    k = k_factor * s
    h = h_factor * s
    cp = 0.0
    cn = 0.0
    up_idx = None
    down_idx = None
    for i, x in enumerate(vals):
        cp = max(0.0, cp + (x - m - k))
        cn = min(0.0, cn + (x - m + k))
        if up_idx is None and cp > h:
            up_idx = i
        if down_idx is None and cn < -h:
            down_idx = i
        if up_idx is not None and down_idx is not None:
            break
    return up_idx, down_idx


def load_series(path: str) -> Tuple[str, List[str], List[float]]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if 'title' in data and 'series' in data and data['series']:
        series = data['series']
        edits = [d.get('edits', 0) for d in series]
        reverts = [d.get('reverts', 0) for d in series]
        vals = [(r / e) if e > 0 else 0.0 for r, e in zip(reverts, edits)]
        dates = [d.get('date') for d in series]
        label = f"wiki:{data.get('title')}"
        return label, dates, vals
    elif 'repo' in data and 'series' in data and data['series']:
        series = data['series']
        totals = [(d.get('issues_opened', 0) + d.get('prs_opened', 0)) for d in series]
        resp = [(d.get('responded_items', 0) / t) if t > 0 else 0.0 for d, t in zip(series, totals)]
        dates = [d.get('date') for d in series]
        label = f"gh:{data.get('repo')}"
        return label, dates, resp
    else:
        raise ValueError('Unknown input schema: ' + path)


def main():
    ap = argparse.ArgumentParser(description='F3: Parameter sweep for threshold and CUSUM over AIW series')
    ap.add_argument('--data-dir', default=os.path.join('Research','papers','aiw','data'))
    ap.add_argument('--out', default=os.path.join('Research','papers','macro-safety','figures','f3_param_sweep.json'))
    ap.add_argument('--thr-up', default='1.5,2.0,2.5')
    ap.add_argument('--thr-down', default='-1.5,-2.0,-2.5')
    ap.add_argument('--k-factors', default='0.25,0.5,0.75')
    ap.add_argument('--h-factors', default='3.0,5.0,7.0')
    args = ap.parse_args()

    if not os.path.isdir(args.data_dir):
        print(json.dumps({'error': 'data-dir not found', 'data_dir': args.data_dir}, indent=2))
        sys.exit(2)

    thr_up_vals = [float(x) for x in args.thr_up.split(',') if x]
    thr_down_vals = [float(x) for x in args.thr_down.split(',') if x]
    k_vals = [float(x) for x in args.k_factors.split(',') if x]
    h_vals = [float(x) for x in args.h_factors.split(',') if x]

    series_files = [os.path.join(args.data_dir, fn) for fn in os.listdir(args.data_dir)
                    if fn.endswith('.json') and not fn.startswith('detect_') and fn != 'summary.json']

    results: Dict[str, Any] = {
        'figure': 'F3_Param_Sweep',
        'inputs': series_files,
        'sweeps': {
            'threshold': [],
            'cusum': []
        }
    }

    # Threshold sweep
    for up in thr_up_vals:
        for down in thr_down_vals:
            per_series = []
            for fp in series_files:
                try:
                    _, dates, vals = load_series(fp)
                    z = zscores(vals)
                    up_idx, down_idx = threshold_detect(z, up=up, down=down)
                    per_series.append({'spike': up_idx is not None, 'dip': down_idx is not None})
                except Exception:
                    continue
            n = len(per_series)
            spike_rate = sum(1 for r in per_series if r['spike']) / n if n else None
            dip_rate = sum(1 for r in per_series if r['dip']) / n if n else None
            results['sweeps']['threshold'].append({'up': up, 'down': down, 'n': n, 'spike_rate': spike_rate, 'dip_rate': dip_rate})

    # CUSUM sweep
    for k in k_vals:
        for h in h_vals:
            per_series = []
            for fp in series_files:
                try:
                    _, dates, vals = load_series(fp)
                    up_idx, down_idx = cusum_detect(vals, k_factor=k, h_factor=h)
                    per_series.append({'spike': up_idx is not None, 'dip': down_idx is not None})
                except Exception:
                    continue
            n = len(per_series)
            spike_rate = sum(1 for r in per_series if r['spike']) / n if n else None
            dip_rate = sum(1 for r in per_series if r['dip']) / n if n else None
            results['sweeps']['cusum'].append({'k_factor': k, 'h_factor': h, 'n': n, 'spike_rate': spike_rate, 'dip_rate': dip_rate})

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(json.dumps({'wrote': args.out, 'thr_points': len(results['sweeps']['threshold']), 'cusum_points': len(results['sweeps']['cusum'])}, indent=2))


if __name__ == '__main__':
    main()
