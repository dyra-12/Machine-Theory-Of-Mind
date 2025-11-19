"""
Simple data validation utilities for Week 3 experiments.

This module provides a minimal `DataValidator` used by the
`rigorous_week3` analysis script to ensure logged JSONL results
have the expected fields and basic independence checks.
"""
from typing import List, Dict, Any
from collections import Counter


class DataValidator:
	"""Validate experimental results and perform simple independence checks."""

	def validate_results_structure(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""Return only entries that contain the required keys and sensible types.

		Required keys: `agent_type`, `lambda_social`, `total_utility`.
		Coerces `lambda_social` and `total_utility` to floats when possible.
		"""
		required_keys = ["agent_type", "lambda_social", "total_utility"]
		valid: List[Dict[str, Any]] = []

		for entry in results:
			if not all(k in entry for k in required_keys):
				continue
			try:
				entry["lambda_social"] = float(entry["lambda_social"])
				entry["total_utility"] = float(entry["total_utility"])
			except Exception:
				# Skip entries with non-coercible types
				continue
			valid.append(entry)

		print(f"✅ Validated {len(valid)} / {len(results)} results")
		return valid

	def check_independence_assumptions(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
		"""Compute simple counts per experimental configuration to flag repeats.

		This is a lightweight check: it groups results by `config_hash` when
		available, otherwise by the tuple `(agent_type, lambda_social)`.
		Returns a dict with `unique_configs`, `max_repeats`, and
		`independence_violation` (True when a configuration appears more than
		once).
		"""
		if any("config_hash" in r for r in results):
			groups = [r.get("config_hash") for r in results]
		else:
			groups = [(r.get("agent_type"), r.get("lambda_social")) for r in results]

		counts = Counter(groups)
		unique_configs = len(counts)
		max_repeats = max(counts.values()) if counts else 0

		independence_violation = max_repeats > 1

		return {
			"unique_configs": int(unique_configs),
			"max_repeats": int(max_repeats),
			"independence_violation": bool(independence_violation),
		}

