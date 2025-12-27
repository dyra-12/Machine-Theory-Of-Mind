PY ?= python
PIP ?= pip

.PHONY: install test reproduce reproduce-main-figures demo

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
