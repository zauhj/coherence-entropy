#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
from typing import Any, Dict, List, Tuple


def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def try_import_matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore
        return plt
    except Exception as e:
        print(json.dumps({
            'error': 'matplotlib not available',
            'hint': 'pip install matplotlib',
            'detail': str(e)
        }, indent=2))
        sys.exit(2)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'figures'))
DATA_DIR = DEFAULT_DATA_DIR  # set in main()

def read_json(name: str) -> Dict[str, Any]:
    candidates = [
        os.path.join(DATA_DIR, name),
    ]
    for p in candidates:
        try:
            if os.path.exists(p):
                return load_json(p)
        except Exception:
            pass
    print(json.dumps({
        'error': 'data_not_found',
        'file': name,
        'tried': candidates,
        'hint': 'Pass --data-root <path/to/figures> or run from repo root.'
    }, indent=2))
    sys.exit(2)


# ---------- F2: lambda sweep ----------

def render_f2_lambda(fig_dir: str):
    plt = try_import_matplotlib()
    d = read_json('f2_bpf_lambda_sweep.json')
    series = d.get('series', [])
    xs = sorted({ float(s.get('lambda')) for s in series if 'lambda' in s })
    avail = d.get('metrics', [])
    hc_key = 'Hc_post' if 'Hc_post' in avail else 'Hc'
    metrics = ['cooperation_rate','reward', hc_key]

    plt.figure(figsize=(7, 6))
    for i, mk in enumerate(metrics, start=1):
        ax = plt.subplot(len(metrics), 1, i)
        ys = { x: None for x in xs }
        ci = { x: (None, None) for x in xs }
        for s in series:
            lam = float(s.get('lambda'))
            if mk in s:
                ys[lam] = float(s[mk])
            ci_key = f'{mk}_ci'
            if ci_key in s:
                lo, hi = s[ci_key]
                ci[lam] = (float(lo), float(hi))
        X = [x for x in xs if ys[x] is not None]
        Y = [ys[x] for x in X]
        ax.plot(X, Y, marker='o', label=mk)
        lows, highs = [], []
        for x in X:
            lo, hi = ci.get(x, (None,None))
            if lo is None or hi is None:
                lows.append(ys[x]); highs.append(ys[x])
            else:
                lows.append(lo); highs.append(hi)
        ax.fill_between(X, lows, highs, alpha=0.2)
        ax.set_ylabel(mk)
        if mk in ('cooperation_rate','Hc','Hc_post'):
            ax.set_ylim(0,1)
        if i == len(metrics):
            ax.set_xlabel('lambda')
        if i == 1:
            ax.set_title('F2: BP-FT lambda sweep')
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    os.makedirs(fig_dir, exist_ok=True)
    out = os.path.join(fig_dir, 'f2_bpf_lambda_sweep.png')
    plt.savefig(out, dpi=160)
    print(json.dumps({'wrote': out}, indent=2))


# ---------- F2: privacy sweep ----------

def render_f2_privacy(fig_dir: str):
    plt = try_import_matplotlib()
    d = read_json('f2_bpf_privacy_sweep.json')
    series = d.get('series_by_dp', [])
    # determine which coherence metric is present in points
    has_hc_post = False
    for block in series:
        for p in block.get('points', []):
            if 'Hc_post' in p:
                has_hc_post = True
                break
        if has_hc_post:
            break
    hc_key = 'Hc_post' if has_hc_post else 'Hc'
    metrics = ['cooperation_rate','reward', hc_key]
    fig = plt.figure(figsize=(9, 8))
    handles_labels = []
    for i, mk in enumerate(metrics, start=1):
        ax = plt.subplot(len(metrics), 1, i)
        for idx, block in enumerate(series):
            dp = float(block.get('dp_sigma'))
            pts = sorted(block.get('points', []), key=lambda r: float(r.get('lambda', 0.0)))
            X = [float(p.get('lambda')) for p in pts if p.get('lambda') is not None and p.get(mk) is not None]
            Y = [float(p.get(mk)) for p in pts if p.get('lambda') is not None and p.get(mk) is not None]
            h, = ax.plot(X, Y, marker='o', label=f'dp={dp}')
            if i == 1:
                handles_labels.append((h, f'dp={dp}'))
        ax.set_ylabel(mk)
        if mk in ('cooperation_rate','Hc','Hc_post'):
            ax.set_ylim(0,1)
        if i == len(metrics):
            ax.set_xlabel('lambda')
        ax.grid(True, alpha=0.3)
    # consolidated legend
    if handles_labels:
        handles, labels = zip(*handles_labels)
        fig.legend(handles, labels, loc='upper center', ncol=min(4, len(handles)))
    plt.tight_layout(rect=[0,0,1,0.95])
    os.makedirs(fig_dir, exist_ok=True)
    out = os.path.join(fig_dir, 'f2_bpf_privacy_sweep.png')
    plt.savefig(out, dpi=160)
    print(json.dumps({'wrote': out}, indent=2))


# ---------- F3: compare ----------

def render_f3_compare(fig_dir: str):
    plt = try_import_matplotlib()
    d = read_json('f3_detection_compare.json')
    summary = d.get('summary', {})
    agree = summary.get('agreement_rate', {})
    deltas = d.get('records', [])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
    bars = ax1.bar(['spike','dip'], [agree.get('spike', 0.0) or 0.0, agree.get('dip', 0.0) or 0.0], color=['#4CAF50','#2196F3'])
    ax1.set_ylim(0, 1)
    ax1.set_ylabel('agreement rate')
    ax1.set_title('Threshold vs CUSUM')
    for b in bars:
        h = b.get_height()
        ax1.text(b.get_x()+b.get_width()/2, h+0.02, f"{h:.2f}", ha='center', va='bottom', fontsize=9)
    vals = []
    for r in deltas:
        dd = r.get('delta', {})
        v = dd.get('spike_idx')
        if isinstance(v, int):
            vals.append(abs(v))
        v2 = dd.get('dip_idx')
        if isinstance(v2, int):
            vals.append(abs(v2))
    if vals:
        ax2.hist(vals, bins=min(10, max(3, len(vals)//2)), color='#9C27B0', alpha=0.7)
    ax2.set_title('Index delta distribution')
    ax2.set_xlabel('|delta idx|')
    ax2.set_ylabel('count')
    plt.tight_layout()
    os.makedirs(fig_dir, exist_ok=True)
    out = os.path.join(fig_dir, 'f3_detection_compare.png')
    fig.savefig(out, dpi=160)
    print(json.dumps({'wrote': out}, indent=2))


# ---------- F3: param sweep ----------

def render_f3_param(fig_dir: str):
    plt = try_import_matplotlib()
    import numpy as np  # type: ignore
    d = read_json('f3_param_sweep.json')
    thr = d.get('sweeps',{}).get('threshold',[])
    cu = d.get('sweeps',{}).get('cusum',[])

    def heatmap(ax, xs, ys, vals, title, xlabel, ylabel):
        X = sorted(list(set(xs)))
        Y = sorted(list(set(ys)))
        grid = np.full((len(Y), len(X)), np.nan)
        for x,y,v in zip(xs,ys,vals):
            xi = X.index(x); yi = Y.index(y)
            grid[yi, xi] = v
        im = ax.imshow(grid, aspect='auto', origin='lower', cmap='viridis', vmin=0.0, vmax=1.0)
        # annotate cells with values
        for yi in range(len(Y)):
            for xi in range(len(X)):
                val = grid[yi, xi]
                if not np.isnan(val):
                    col = 'white' if val > 0.6 else 'black'
                    ax.text(xi, yi, f"{val:.2f}", ha='center', va='center', fontsize=8, color=col)
        ax.set_xticks(range(len(X))); ax.set_xticklabels([str(x) for x in X], rotation=45)
        ax.set_yticks(range(len(Y))); ax.set_yticklabels([str(y) for y in Y])
        ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig, axes = plt.subplots(2, 2, figsize=(10,6))
    if thr:
        xs = [float(t['up']) for t in thr]
        ys = [float(t['down']) for t in thr]
        vs = [float(t.get('spike_rate') or 0.0) for t in thr]
        heatmap(axes[0,0], xs, ys, vs, 'Threshold spike rate', 'up (z)', 'down (z)')
        vd = [float(t.get('dip_rate') or 0.0) for t in thr]
        heatmap(axes[1,0], xs, ys, vd, 'Threshold dip rate', 'up (z)', 'down (z)')
    if cu:
        xs = [float(t['k_factor']) for t in cu]
        ys = [float(t['h_factor']) for t in cu]
        vs = [float(t.get('spike_rate') or 0.0) for t in cu]
        heatmap(axes[0,1], xs, ys, vs, 'CUSUM spike rate', 'k_factor', 'h_factor')
        vd = [float(t.get('dip_rate') or 0.0) for t in cu]
        heatmap(axes[1,1], xs, ys, vd, 'CUSUM dip rate', 'k_factor', 'h_factor')
    plt.tight_layout()
    os.makedirs(fig_dir, exist_ok=True)
    out = os.path.join(fig_dir, 'f3_param_sweep.png')
    fig.savefig(out, dpi=160)
    print(json.dumps({'wrote': out}, indent=2))


# ---------- F4: timeline ----------

def render_f4_timeline(fig_dir: str):
    plt = try_import_matplotlib()
    d = read_json('f4_timeline.json')
    tracks = d.get('tracks', [])
    n = max(1, len(tracks))
    plt.figure(figsize=(11, 1 + 2.4*n))
    for i, tr in enumerate(tracks, start=1):
        # Use independent x-axes so shorter series don't leave large blank spans
        ax = plt.subplot(n, 1, i)
        vals = tr.get('values', [])
        dates = tr.get('dates', []) or []
        label = tr.get('label', f'track_{i}')
        npts = len(vals)
        ax.plot(range(npts), vals, color='#455A64')
        thr = tr.get('detect_threshold') or {}
        cu = tr.get('detect_cusum') or {}
        xmax = max(0, npts - 1)
        for k, color in ((thr, '#E91E63'), (cu, '#3F51B5')):
            si = k.get('spike_idx')
            di = k.get('dip_idx')
            if si is not None and npts > 0:
                xi = max(0, min(int(si), xmax))
                ax.axvline(xi, color=color, linestyle='--', alpha=0.8, linewidth=1.2)
            if di is not None and npts > 0:
                xj = max(0, min(int(di), xmax))
                ax.axvline(xj, color=color, linestyle=':', alpha=0.8, linewidth=1.2)
        ax.set_ylim(0, 1)
        ax.set_xlim(0, xmax if npts > 0 else 1)
        ax.set_ylabel(label, fontsize=10)
        # Sparse date ticks if dates are available and aligned
        if dates and len(dates) == npts:
            idxs = [0]
            if npts > 2:
                idxs.append(npts // 2)
            if xmax not in idxs:
                idxs.append(xmax)
            ticks = sorted(set(idxs))
            ticklabels = [dates[j] for j in ticks]
            ax.set_xticks(ticks)
            ax.set_xticklabels(ticklabels, rotation=30, ha='right')
            ax.tick_params(axis='x', labelsize=8)
        ax.grid(True, alpha=0.2)
    # tiny legend hint at top
    plt.suptitle('F4: AIW timelines (pink dashed = threshold spike, blue dotted = CUSUM dip)', fontsize=10)
    # Increase left margin to avoid clipped/illegible y-labels
    plt.tight_layout(rect=[0.24,0,1,0.94])
    os.makedirs(fig_dir, exist_ok=True)
    out = os.path.join(fig_dir, 'f4_timeline.png')
    plt.savefig(out, dpi=180)
    print(json.dumps({'wrote': out}, indent=2))


def main():
    ap = argparse.ArgumentParser(description='Render macro figure PNGs from JSON artifacts (requires matplotlib)')
    ap.add_argument('--which', default='all', choices=['all','f2_lambda','f2_privacy','f3_compare','f3_param','f4'])
    ap.add_argument('--data-root', default=DEFAULT_DATA_DIR, help='Directory containing JSON figure artifacts (defaults to ../figures relative to this script)')
    ap.add_argument('--out-dir', default=DEFAULT_DATA_DIR, help='Directory to write PNGs (defaults to ../figures relative to this script)')
    args = ap.parse_args()

    # Set global data dir from args
    global DATA_DIR
    DATA_DIR = os.path.abspath(args.data_root)

    which = args.which
    if which in ('all','f2_lambda'):
        render_f2_lambda(args.out_dir)
    if which in ('all','f2_privacy'):
        render_f2_privacy(args.out_dir)
    if which in ('all','f3_compare'):
        render_f3_compare(args.out_dir)
    if which in ('all','f3_param'):
        render_f3_param(args.out_dir)
    if which in ('all','f4'):
        render_f4_timeline(args.out_dir)

if __name__ == '__main__':
    main()
