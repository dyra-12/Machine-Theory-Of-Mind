"""
Statistical testing for agent performance comparisons
"""
import numpy as np
from scipy import stats
from typing import Dict, List, Any, Tuple

class StatisticalAnalyzer:
    """Performs statistical tests on experiment results"""
    
    @staticmethod
    def calculate_agent_performance(results: List[Dict]) -> Dict[str, Dict]:
        """Calculate performance metrics for each agent type"""
        agent_metrics = {}
        
        for result in results:
            agent_type = result['agent_type']
            if agent_type not in agent_metrics:
                agent_metrics[agent_type] = {
                    'task_rewards': [],
                    'social_scores': [],
                    'total_utilities': [],
                    'warmth_values': [],
                    'competence_values': []
                }
            
            metrics = agent_metrics[agent_type]
            metrics['task_rewards'].append(result['task_reward'])
            metrics['social_scores'].append(result['social_score'])
            metrics['total_utilities'].append(result['total_utility'])
            metrics['warmth_values'].append(result['warmth_final'])
            metrics['competence_values'].append(result['competence_final'])
        
        return agent_metrics
    
    @staticmethod
    def perform_significance_tests(agent_metrics: Dict) -> Dict[str, Any]:
        """FIXED: Proper statistical testing with realistic p-values"""
        agent_types = list(agent_metrics.keys())
        significance_results = {}
        
        for i, agent1 in enumerate(agent_types):
            for agent2 in agent_types[i+1:]:
                key = f"{agent1}_vs_{agent2}"
                
                # FIX: Use total_utilities, not aggregated metrics
                rewards1 = np.array(agent_metrics[agent1]['total_utilities'])
                rewards2 = np.array(agent_metrics[agent2]['total_utilities'])
                
                # FIX: Check for sufficient sample size
                if len(rewards1) < 5 or len(rewards2) < 5:
                    print(f"⚠️  Insufficient samples: {agent1}({len(rewards1)}), {agent2}({len(rewards2)})")
                    continue
                
                # FIX: Use Welch's t-test (doesn't assume equal variances)
                t_stat, p_value = stats.ttest_ind(rewards1, rewards2, equal_var=False)
                
                # FIX: Handle extreme p-values
                p_value = max(p_value, 1e-10)  # Prevent 0.0000
                
                # FIX: Proper effect size calculation
                mean1, mean2 = np.mean(rewards1), np.mean(rewards2)
                std1, std2 = np.std(rewards1, ddof=1), np.std(rewards2, ddof=1)
                n1, n2 = len(rewards1), len(rewards2)
                
                # Cohen's d with pooled standard deviation
                pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1 + n2 - 2))
                cohens_d = (mean1 - mean2) / pooled_std if pooled_std != 0 else 0
                
                significance_results[key] = {
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d),
                    'significant_0.05': p_value < 0.05,
                    'significant_0.01': p_value < 0.01,
                    'mean_difference': float(mean1 - mean2),
                    'n1': n1,
                    'n2': n2
                }
        
        return significance_results
    @staticmethod
    def calculate_confidence_intervals(agent_metrics: Dict, confidence: float = 0.95) -> Dict:
        """Calculate confidence intervals for agent performance"""
        ci_results = {}
        
        for agent_type, metrics in agent_metrics.items():
            ci_results[agent_type] = {}
            
            for metric_name, values in metrics.items():
                if values:  # Check if list is not empty
                    mean = np.mean(values)
                    sem = stats.sem(values)  # Standard error of the mean
                    ci = sem * stats.t.ppf((1 + confidence) / 2, len(values) - 1)
                    
                    ci_results[agent_type][metric_name] = {
                        'mean': mean,
                        'std': np.std(values),
                        'ci_lower': mean - ci,
                        'ci_upper': mean + ci,
                        'n': len(values)
                    }
        
        return ci_results