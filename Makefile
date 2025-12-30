PY ?= python
PIP ?= pip

# Prefer the workspace virtualenv Python if present.
PY_VENV := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo $(PY); fi)

.PHONY: install test reproduce reproduce-main-figures demo docs-results-assets docs-results-regenerate docs-results-regenerate-smoke

.PHONY: update-pilot

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

test:
	$(PY) -m pytest tests/ -q

reproduce:
	# Reproduce core Week 5 Bayesian sweep and generate analysis plots
	$(PY) experiments/run_experiment.py --config experiments/config/week5_bayesian_sweep.yaml
	$(PY) src/experiments/analyze_week5.py

reproduce-main-figures:
	# One-shot generation of the main reproducibility figures (Weeks 5, 6, 7)
	$(PY) experiments/run_experiment.py --config experiments/config/week5_bayesian_sweep.yaml
	$(PY) src/experiments/analyze_week5.py
	$(PY) experiments/run_experiment.py --config experiments/config/week6_siq.yaml
	$(PY) src/experiments/siq_visualizations.py
	$(PY) experiments/run_trace_sweep.py
	$(PY) experiments/run_trace_sweep_extended.py

demo:
	# Launch interactive trace dashboard (Streamlit)
	streamlit run apps/trace_dashboard.py

update-pilot:
	# Update the human pilot README with the current participant count
	$(PY) tools/update_human_pilot_readme.py

docs-results-assets:
	# Export figures/tables referenced in docs/Results.md into docs/figures/ (read-only on results/)
	$(PY) tools/export_results_md_assets.py

docs-results-regenerate:
	# Regenerate docs/Results.md figures/tables into docs/figures/ without running experiments (does not write to results/)
	$(PY_VENV) tools/regenerate_results_md_assets.py

docs-results-regenerate-smoke:
	# Validate regeneration inputs/imports only (no outputs written)
	$(PY_VENV) tools/regenerate_results_md_assets.py --smoke-test
