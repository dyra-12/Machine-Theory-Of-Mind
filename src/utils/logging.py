"""
Structured logging for reproducible experiments
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class ExperimentLogger:
    """JSONL logger for structured experiment data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.experiment_id = self._generate_experiment_id()
        self.log_file = self._setup_logging()
        
    def _generate_experiment_id(self) -> str:
        """Generate unique experiment ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_hash = self.get_config_hash(self.config)
        return f"exp_{timestamp}_{config_hash[:8]}"
    
    def _setup_logging(self) -> Path:
        """Setup logging directory and file"""
        log_dir = Path(f"results/week3/raw/{self.experiment_id}")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Save full config
        config_file = log_dir / "experiment_config.json"
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        return log_dir / "results.jsonl"
    
    def log_episode(self, episode_data: Dict[str, Any]):
        """Log single episode results in JSONL format"""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(episode_data) + '\n')
    
    @staticmethod
    def get_config_hash(config: Dict[str, Any]) -> str:
        """Generate hash for configuration reproducibility"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def log_aggregate_metrics(self, aggregate_data: Dict[str, Any]):
        """Log aggregated metrics"""
        agg_file = self.log_file.parent / "aggregate_metrics.json"
        with open(agg_file, 'w') as f:
            json.dump(aggregate_data, f, indent=2)