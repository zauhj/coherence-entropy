# Build helpers for public code-only release
PY=python3
SCRIPTS=scripts
AIW_DATA=aiw/data
FIG_DIR=figures

.PHONY: all f3_compare f3_param f4 figs test

all: f3_compare f3_param f4

figs: all

f3_compare:
	$(PY) $(SCRIPTS)/fig_f3_detection_compare.py --data-dir $(AIW_DATA) --out $(FIG_DIR)/f3_detection_compare.json
	$(PY) $(SCRIPTS)/render_figs.py --which f3_compare

f3_param:
	$(PY) $(SCRIPTS)/fig_f3_param_sweep.py --data-dir $(AIW_DATA) --out $(FIG_DIR)/f3_param_sweep.json
	$(PY) $(SCRIPTS)/render_figs.py --which f3_param

f4:
	$(PY) $(SCRIPTS)/fig_f4_timeline.py --data-dir $(AIW_DATA) --out $(FIG_DIR)/f4_timeline.json
	$(PY) $(SCRIPTS)/render_figs.py --which f4

test:
	$(PY) tests/test_fig_schemas.py
