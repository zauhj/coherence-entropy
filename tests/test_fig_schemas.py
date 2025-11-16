#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
FIG = os.path.join(ROOT, 'figures')

FAILS: List[str] = []


def read_json(p: str) -> Dict[str, Any]:
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)


def assert_true(cond: bool, msg: str):
    if not cond:
        FAILS.append(msg)


def test_f2_lambda():
    path = os.path.join(FIG, 'f2_bpf_lambda_sweep.json')
    if not os.path.exists(path):
        print(f"[warn] missing: {path}")
        return
    d = read_json(path)
    assert_true(isinstance(d.get('series'), list), 'f2_lambda: series list')
    assert_true(isinstance(d.get('metrics'), list), 'f2_lambda: metrics list')
    for i, rec in enumerate(d.get('series') or []):
        assert_true('lambda' in rec, f'f2_lambda[{i}]: missing lambda')
        has_hc = ('Hc_post' in rec) or ('Hc' in rec)
        assert_true(has_hc, f'f2_lambda[{i}]: missing Hc/Hc_post')


def test_f2_privacy():
    path = os.path.join(FIG, 'f2_bpf_privacy_sweep.json')
    if not os.path.exists(path):
        print(f"[warn] missing: {path}")
        return
    d = read_json(path)
    blocks = d.get('series_by_dp') or []
    assert_true(isinstance(blocks, list), 'f2_privacy: series_by_dp list')
    for bi, b in enumerate(blocks):
        assert_true('dp_sigma' in b, f'f2_privacy block[{bi}]: missing dp_sigma')
        pts = b.get('points') or []
        assert_true(isinstance(pts, list), f'f2_privacy block[{bi}]: points list')
        for pi, p in enumerate(pts):
            assert_true('lambda' in p, f'f2_privacy block[{bi}] point[{pi}]: missing lambda')


def test_f3_compare():
    path = os.path.join(FIG, 'f3_detection_compare.json')
    if not os.path.exists(path):
        print(f"[warn] missing: {path}")
        return
    d = read_json(path)
    assert_true('summary' in d, 'f3_compare: has summary')
    assert_true('records' in d, 'f3_compare: has records')


def test_f3_param():
    path = os.path.join(FIG, 'f3_param_sweep.json')
    if not os.path.exists(path):
        print(f"[warn] missing: {path}")
        return
    d = read_json(path)
    sweeps = d.get('sweeps') or {}
    assert_true('threshold' in sweeps, 'f3_param: threshold sweep present')
    assert_true('cusum' in sweeps, 'f3_param: cusum sweep present')


def test_f4_timeline():
    path = os.path.join(FIG, 'f4_timeline.json')
    if not os.path.exists(path):
        print(f"[warn] missing: {path}")
        return
    d = read_json(path)
    tracks = d.get('tracks') or []
    assert_true(isinstance(tracks, list), 'f4_timeline: tracks list')
    for ti, tr in enumerate(tracks):
        for key in ('label','dates','values'):
            assert_true(key in tr, f'f4_timeline track[{ti}]: missing {key}')
        # overlay dicts optional
        for det_key in ('detect_threshold','detect_cusum'):
            if det_key in tr and isinstance(tr[det_key], dict):
                # allow nulls but keys should exist if dict present
                det = tr[det_key]
                for k in ('spike_idx','dip_idx','spike_date','dip_date'):
                    assert_true(k in det, f'f4_timeline track[{ti}].{det_key}: missing {k}')


if __name__ == '__main__':
    test_f2_lambda()
    test_f2_privacy()
    test_f3_compare()
    test_f3_param()
    test_f4_timeline()
    if FAILS:
        print('\n'.join(f'[fail] {m}' for m in FAILS))
        sys.exit(1)
    print('[ok] schema checks passed')
    sys.exit(0)
