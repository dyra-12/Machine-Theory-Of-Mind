"""Episode-level trace logger used for Week 7 analyses.

The logger captures per-action data including the acting agent's
beliefs and the social score computed from those beliefs.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

JsonScalar = Union[str, int, float, bool, None]
JsonValue = Union[JsonScalar, List["JsonValue"], Dict[str, "JsonValue"]]


class TraceLogger:
    """Utility for writing detailed negotiation traces to disk.

    The logger accumulates structured events in memory and writes them to a
    JSON file on demand (via :meth:`flush` or :meth:`close`). Each step entry
    can include the acting agent's beliefs as well as the computed social score
    for that mental state.
    """

    def __init__(
        self,
        episode_id: str,
        output_dir: Union[str, Path],
        *,
        metadata: Optional[Dict[str, Any]] = None,
        auto_flush: bool = False,
    ) -> None:
        self.episode_id = episode_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.trace_path = self.output_dir / f"{episode_id}.json"
        self.auto_flush = auto_flush

        self._trace: Dict[str, Any] = {
            "episode_id": episode_id,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "metadata": metadata.copy() if metadata else {},
            "steps": [],
            "outcome": None,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_metadata(self, extra: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        """Merge additional metadata fields into the trace header."""
        payload: Dict[str, Any] = {}
        if extra:
            payload.update(extra)
        if kwargs:
            payload.update(kwargs)
        if not payload:
            return
        self._trace["metadata"].update(self._coerce_value(payload))
        self._maybe_flush()

    def log_step(
        self,
        *,
        turn_index: int,
        proposer_id: int,
        action: Optional[Sequence[int]] = None,
        accepted: Optional[bool] = None,
        mental_state: Optional[Any] = None,
        social_score: Optional[float] = None,
        notes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a step entry.

        Args:
            turn_index: Negotiation turn when the action was taken.
            proposer_id: ID of the acting agent.
            action: Tuple/list representing the offer.
            accepted: Whether the offer was accepted immediately after.
            mental_state: Agent beliefs after the update step.
            social_score: Computed social score for those beliefs.
            notes: Optional free-form diagnostics (serialized to JSON).
        """
        entry: Dict[str, Any] = {
            "turn": int(turn_index),
            "agent_id": int(proposer_id),
            "action": self._normalize_action(action),
            "accepted": bool(accepted) if accepted is not None else None,
            "beliefs": self._serialize_mental_state(mental_state),
            "social_score": float(social_score) if social_score is not None else None,
        }
        if notes:
            entry["notes"] = self._coerce_value(notes)

        self._trace["steps"].append(entry)
        self._maybe_flush()

    def set_outcome(self, outcome: Dict[str, Any]) -> None:
        """Record episode-level outcome metadata (agreement, rewards, etc.)."""
        self._trace["outcome"] = self._coerce_value(outcome)
        self._maybe_flush()

    def flush(self) -> Path:
        """Write the current trace buffer to disk and return the path."""
        with self.trace_path.open("w", encoding="utf-8") as fh:
            json.dump(self._trace, fh, indent=2)
        return self.trace_path

    def close(self) -> Path:
        """Alias for :meth:`flush` to match file-like semantics."""
        return self.flush()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _maybe_flush(self) -> None:
        if self.auto_flush:
            self.flush()

    @staticmethod
    def _normalize_action(action: Optional[Sequence[int]]) -> Optional[List[int]]:
        if action is None:
            return None
        return [int(x) for x in action]

    @classmethod
    def _serialize_mental_state(cls, mental_state: Optional[Any]) -> Optional[Dict[str, JsonValue]]:
        if mental_state is None:
            return None

        if isinstance(mental_state, dict):
            return cls._coerce_value(mental_state)

        fields: Dict[str, Any] = {}
        for attr in ("warmth", "competence", "warmth_uncertainty", "competence_uncertainty", "goals", "beliefs"):
            if hasattr(mental_state, attr):
                value = getattr(mental_state, attr)
                if value is not None:
                    fields[attr] = value
        if not fields:
            return None
        return cls._coerce_value(fields)

    @classmethod
    def _coerce_value(cls, value: Any) -> JsonValue:
        """Best-effort conversion to JSON-serializable values."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, dict):
            return {str(k): cls._coerce_value(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [cls._coerce_value(v) for v in value]
        if hasattr(value, "tolist"):
            return cls._coerce_value(value.tolist())
        if hasattr(value, "item"):
            try:
                return cls._coerce_value(value.item())
            except Exception:  # pragma: no cover - fallback only
                pass
        try:
            return float(value)
        except (TypeError, ValueError):
            return str(value)