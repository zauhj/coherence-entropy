# Coherence Entropy: A Practical Framework for Hallucination and Misalignment

## Overview

- Code-only public repository for rendering and validating figures for the Coherence Entropy framework.
- Bring Your Own Data (BYOD): scripts expect lightweight JSON inputs; no datasets or manuscript are included.
- Outputs are JSON (figure data) and PNGs (renders) produced locally.

## At a Glance

- What: Figure generation and schema checks for F3 (detection compare/param) and F4 (timelines).
- Includes: `scripts/`, `Makefile` (F3/F4 targets), `tests/` (schema checks), CI workflow.
- Excludes: datasets, manuscript source/PDF, prebuilt artifacts.
- Requires: Python 3.10+, `matplotlib`, `numpy`. Install: `pip install -r requirements.txt`.
- Quickstart: `make test` → add JSON to `aiw/data/` → `make f3_compare` / `make f3_param` / `make f4`.

## Directory layout

- `scripts/` — figure generators and renderers
- `tests/` — JSON schema checks for figure artifacts
- `aiw/data/` — your BYOD inputs (series and detect_*.json)
- `figures/` — outputs written locally by scripts

## TL;DR

- Hc_post decreases with basin-preserving regularization λ; privacy noise preserves the trend.
- Simple detectors (z-threshold, two-sided CUSUM) identify spikes/dips on AIW timelines; parameter sweeps show robustness.
- Reproducible builds via Makefile (F3/F4) and JSON schema tests; code-only release (no data/manuscript).

## Scope (public code-only)

- This repository includes code, scripts, and schema tests only.
- No dataset snapshots are included. Bring your own data to reproduce figures.
- The manuscript source/PDF and build artifacts are intentionally excluded.

## One‑paragraph thesis
We propose a practical, systems‑level safety program centered on coherence entropy—a measurable proxy for incoherence that unifies hallucination and misalignment. Ethical Attractors provide an observable lens on basins; Basin‑Preserving adaptation keeps learning dynamics within low‑entropy (coherent) regions; attention‑preserving UX and privacy‑preserving context maintain human agency and verifiability. We consolidate these into EA‑Bench with a coherence track and show early evidence on simulated and real socio‑technical data.

## Contributions
- Unifying lens: connect dynamics (Ethical Attractors & detection), adaptation (Basin‑Preserving FT), UX (map‑first, attention‑preserving), and privacy (loss‑bounded compression) under measurable safety objectives.
- Benchmarking: EA‑Bench 1.0 tasks, detectors, and robustness regimes for reproducible evaluation.
- Methods: basin‑widening levers at three layers — Dynamics, Interface, Governance — with concrete policies.
- Real‑world observability: “Attractors‑in‑the‑Wild” validation on Wikipedia/OSS streams.

## Outline (v0)
1. Motivation: democratic, attention‑preserving AI; why basins of cooperation matter
2. Framework: Ethical Attractors — signals, detectors, metrics (latency, FPR, ROC/AUC)
3. Methods: Basin‑Preserving adaptation; interface safety (Syxion’s map‑first, JSON UI policy guard); privacy‑preserving context
4. Benchmark: EA‑Bench 1.0 — tasks, detectors, robustness (correlated, DP, adversarial)
5. Real‑world: Attractors‑in‑the‑Wild (Wikipedia/OSS) — pipelines, ethics, early baselines
6. Integrations: UX × dynamics × governance; deployment patterns and risks
7. Discussion: limitations, failure modes, standards, open artifacts

## Figures (what scripts render)
- F2: Basin‑preserving FT sweeps (λ, privacy)
- F3: Detection performance (threshold vs CUSUM) and parameter sweeps
- F4: Attractors‑in‑the‑Wild timelines with overlays

## Expected JSON outputs
- figures/f2_bpf_lambda_sweep.json
- figures/f2_bpf_privacy_sweep.json
- figures/f3_detection_compare.json
- figures/f3_param_sweep.json
- figures/f4_timeline.json

## Quick build (no data/manuscript included)

- **Env**
  - Python 3.10+
  - `pip install -r requirements.txt`
- **From repo root (`.`)**:
  - Render figures: `make f3_compare`, `make f3_param`, `make f4` (requires your data)
  - Schema tests (no-op if JSON files are absent): `make test`
- **Direct scripts** (no Makefile):
  - `python3 scripts/render_figs.py --which all --data-root figures --out-dir figures`
- **Paths**
  - `render_figs.py` accepts `--data-root` (JSON artifacts) and `--out-dir` (PNGs). Defaults point to `../figures` relative to the script.

## Data sources and detection

- **Wikipedia Talk (MediaWiki Revisions API)**
  - Endpoint: https://www.mediawiki.org/wiki/API:Revisions
  - Daily ratio: reverts / edits. Revert heuristic: has rollback tag OR comment contains "revert" (case-insensitive).
  - Dates are UTC ISO day boundaries. Missing days are omitted (no imputation).
- **GitHub Issues/PRs (REST v3)**
  - Endpoint: https://docs.github.com/en/rest
  - Daily ratio: responded_items / (issues_opened + prs_opened). Responded = comments > 0.
- **Detectors**
  - Threshold on per-track z-scores: first spike/dip crossing. Defaults up=2.0, down=-2.0.
  - Two-sided CUSUM against per-track mean with std scaling: k_factor=0.5, h_factor=5.0.

## Detector defaults used in figures

- **Normalization**
  - Per‑track z‑score using population standard deviation over the full series.
  - Dates are ISO (YYYY‑MM‑DD) derived from API timestamps; missing days are omitted (no imputation).
- **Threshold detector**
  - z_up = 2.0, z_down = -2.0; first index crossing per track for spike/dip.
- **CUSUM detector**
  - k_factor = 0.5, h_factor = 5.0; computed against per‑track mean with population std scaling.

## Evaluation plan
- Simulated: EA‑Bench baselines + robustness; BP‑FT PG vs tabular curves
- Real‑world: detection latency vs community ground events; ablation on privacy noise
- Human factors: attention‑preserving UX proxies (coverage/diversity; revisit rate)

## Notes
- Some scripts reference external datasets or companion repos; adjust paths per your environment.

## Artifacts
- Code and schema tests; see `CITATION.cff` for citation.

## License and citation

- Code is MIT licensed (see repo root `LICENSE`).
- Manuscript text and figures are CC BY 4.0 (see repo root `LICENSE-CC-BY-4.0`).
- Cite using the root `CITATION.cff` (ORCID: https://orcid.org/0009-0006-1694-2686).

## Acknowledgements
- Community open‑source and public APIs used for AIW practices.

<!-- Reproduction commands referencing companion repos intentionally omitted in public code-only release. -->
