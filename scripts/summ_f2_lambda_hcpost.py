#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
from typing import Any, Dict, List, Tuple


def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def linreg(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    n = len(xs)
    if n < 2:
        return 0.0, 0.0
    sx = sum(xs); sy = sum(ys)
    sxx = sum(x*x for x in xs); sxy = sum(x*y for x,y in zip(xs,ys))
    den = n*sxx - sx*sx
    if den == 0:
        return 0.0, 0.0
    slope = (n*sxy - sx*sy) / den
    intercept = (sy - slope*sx) / n
    return slope, intercept


def main():
    ap = argparse.ArgumentParser(description='Summarize Hc_post vs lambda from F2 lambda sweep JSON')
    ap.add_argument('--input', default=os.path.join('Research','papers','macro-safety','figures','f2_bpf_lambda_sweep.json'))
    ap.add_argument('--out', default=os.path.join('Research','papers','macro-safety','figures','f2_bpf_lambda_hcpost_summary.json'))
    args = ap.parse_args()

    d = load_json(args.input)
    series = d.get('series', [])
    # prefer Hc_post if exists, else Hc
    use_key = 'Hc_post' if any('Hc_post' in s for s in series) else 'Hc'
    pts = sorted([(float(s['lambda']), float(s[use_key])) for s in series if 'lambda' in s and use_key in s], key=lambda t: t[0])
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    slope, intercept = linreg(xs, ys)

    out = {
        'figure': 'F2_BPF_Lambda_HcPost_Summary',
        'input': args.input,
        'metric': use_key,
        'points': [{'lambda': x, use_key: y} for x,y in pts],
        'summary': {
            'min': min(ys) if ys else None,
            'max': max(ys) if ys else None,
            'slope': slope,
            'intercept': intercept,
            'monotonicity': 'decreasing' if slope < 0 else ('increasing' if slope > 0 else 'flat')
        }
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
    print(json.dumps({'wrote': args.out, 'metric': use_key, 'slope': slope}, indent=2))


if __name__ == '__main__':
    main()
