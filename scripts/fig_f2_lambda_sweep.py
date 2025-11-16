#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys, math
from statistics import mean, pstdev
from typing import Any, Dict, List, Tuple, Iterable


def read_records(path: str) -> List[Dict[str, Any]]:
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and 'runs' in data and isinstance(data['runs'], list):
            return data['runs']
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    recs: List[Dict[str, Any]] = []
    for ln in raw.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
            if isinstance(obj, dict):
                recs.append(obj)
        except json.JSONDecodeError:
            continue
    if recs:
        return recs
    raise ValueError(f'Unrecognized input format: {path}')


def ci95(vals: List[float]) -> Tuple[float, float]:
    if not vals:
        return 0.0, 0.0
    m = mean(vals)
    if len(vals) == 1:
        return m, m
    s = pstdev(vals)
    se = s / math.sqrt(len(vals)) if len(vals) > 0 else 0.0
    return m - 1.96 * se, m + 1.96 * se


def is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def main():
    ap = argparse.ArgumentParser(description='F2: BP-FT lambda sweep aggregator (lambda vs cooperation/reward/Hc)')
    ap.add_argument('--input', default=os.path.join('Research','papers','macro-safety','examples','bpft_lambda_sweep.jsonl'))
    ap.add_argument('--out', default=os.path.join('Research','papers','macro-safety','figures','f2_bpf_lambda_sweep.json'))
    args = ap.parse_args()

    recs = read_records(args.input)
    groups: Dict[float, List[Dict[str, Any]]] = {}
    for r in recs:
        if 'lambda' not in r:
            continue
        lam = float(r['lambda'])
        groups.setdefault(lam, []).append(r)

    # Discover numeric metric keys (excluding reserved)
    reserved = {'lambda', 'seed', 'task', 'model', 'config'}
    metric_keys: List[str] = []
    for rs in groups.values():
        for r in rs:
            for k, v in r.items():
                if k in reserved:
                    continue
                if is_num(v) and k not in metric_keys:
                    metric_keys.append(k)

    series: List[Dict[str, Any]] = []
    for lam in sorted(groups.keys()):
        rs = groups[lam]
        entry: Dict[str, Any] = {'lambda': lam, 'n': len(rs)}
        for mk in metric_keys:
            vals = [float(r.get(mk)) for r in rs if is_num(r.get(mk))]
            if not vals:
                continue
            m = mean(vals)
            lo, hi = ci95(vals)
            entry[mk] = m
            entry[f'{mk}_ci'] = [lo, hi]
        series.append(entry)

    out = {
        'figure': 'F2_BPF_Lambda_Sweep',
        'input': args.input,
        'metrics': metric_keys,
        'series': series,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)

    print(json.dumps({'wrote': args.out, 'points': len(series), 'metrics': metric_keys}, indent=2))


if __name__ == '__main__':
    main()
