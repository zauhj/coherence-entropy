#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
from typing import Any, Dict, List, Tuple


def load_json(p: str) -> Dict[str, Any]:
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)


def wiki_series_to_values(data: Dict[str, Any]) -> Tuple[str, List[str], List[float]]:
    series = data.get('series', [])
    dates = [d.get('date') for d in series]
    edits = [d.get('edits', 0) for d in series]
    reverts = [d.get('reverts', 0) for d in series]
    vals = [(r/e) if e>0 else 0.0 for r,e in zip(reverts, edits)]
    label = f"wiki:{data.get('title')}"
    return label, dates, vals


def gh_series_to_values(data: Dict[str, Any]) -> Tuple[str, List[str], List[float]]:
    series = data.get('series', [])
    dates = [d.get('date') for d in series]
    totals = [(d.get('issues_opened',0) + d.get('prs_opened',0)) for d in series]
    resp = [(d.get('responded_items',0) / t) if t>0 else 0.0 for d,t in zip(series, totals)]
    label = f"gh:{data.get('repo')}"
    return label, dates, resp


def main():
    ap = argparse.ArgumentParser(description='F4: AIW timeline with detection overlays')
    ap.add_argument('--data-dir', default=os.path.join('aiw','data'))
    ap.add_argument('--out', default=os.path.join('figures','f4_timeline.json'))
    args = ap.parse_args()

    if not os.path.isdir(args.data_dir):
        print(json.dumps({'error':'data-dir not found','data_dir':args.data_dir}, indent=2)); sys.exit(2)

    # Identify paired files: base series and detect_* outputs
    files = os.listdir(args.data_dir)
    series_files = [fn for fn in files if fn.endswith('.json') and not fn.startswith('detect_') and fn != 'summary.json']
    detect_files = [fn for fn in files if fn.startswith('detect_') and fn.endswith('.json')]

    # Map detect label -> record
    detect_map: Dict[str, Dict[str, Any]] = {}
    for fn in detect_files:
        try:
            rec = load_json(os.path.join(args.data_dir, fn))
            label = rec.get('label')
            if label:
                detect_map[label] = rec
        except Exception as e:
            sys.stderr.write(f"[warn] skipping detect file {fn}: {e}\n")

    tracks: List[Dict[str, Any]] = []
    for fn in series_files:
        path = os.path.join(args.data_dir, fn)
        try:
            data = load_json(path)
            label = None
            dates: List[str] = []
            vals: List[float] = []
            if 'title' in data and 'series' in data:
                label, dates, vals = wiki_series_to_values(data)
            elif 'repo' in data and 'series' in data:
                label, dates, vals = gh_series_to_values(data)
            else:
                continue
            det = detect_map.get(label, {})
            track = {
                'label': label,
                'dates': dates,
                'values': vals,
                'detect_threshold': det.get('threshold') if isinstance(det, dict) else None,
                'detect_cusum': det.get('cusum') if isinstance(det, dict) else None,
            }
            tracks.append(track)
        except Exception as e:
            sys.stderr.write(f"[warn] skipping series file {fn}: {e}\n")
            continue

    out = {
        'figure': 'F4_Timeline',
        'data_dir': args.data_dir,
        'tracks': tracks,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)

    print(json.dumps({'wrote': args.out, 'tracks': len(tracks)}, indent=2))


if __name__ == '__main__':
    main()
