"""
FIXED statistical testing with proper experimental design
"""
import numpy as np
from scipy import stats
from typing import Dict, List, Any
from statsmodels.stats.multitest import multipletests

class FixedStatisticalAnalyzer:
    """Proper statistical testing for agent comparisons"""
    
    @staticmethod
    def perform_corrected_significance_tests(agent_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        FIXED: Compare agents within the SAME lambda conditions
        """
        significance_results = {}
        
        # Get all lambda values used in experiments
        all_lambdas = set()
        for agent_data in agent_results.values():
            for result in agent_data:
                all_lambdas.add(result['lambda_social'])
        
        # Test each lambda condition separately
        for lambda_val in sorted(all_lambdas):
            print(f"🔍 Testing agents at λ={lambda_val}")
            
            # Extract results for this specific lambda
            lambda_results = {}
            for agent_type, results in agent_results.items():
                agent_lambda_results = [r for r in results if abs(r['lambda_social'] - lambda_val) < 1e-6]
                if len(agent_lambda_results) >= 5:  # Minimum sample size
                    lambda_results[agent_type] = [r['total_utility'] for r in agent_lambda_results]
            
            # Perform pairwise comparisons for this lambda
            agent_types = list(lambda_results.keys())
            for i, agent1 in enumerate(agent_types):
                for agent2 in agent_types[i+1:]:
                    key = f"λ={lambda_val}_{agent1}_vs_{agent2}"
                    
                    data1 = np.array(lambda_results[agent1])
                    data2 = np.array(lambda_results[agent2])
                    
                    # Check sample sizes
                    if len(data1) < 5 or len(data2) < 5:
                        continue
                    
                    # Welch's t-test (doesn't assume equal variances)
                    t_stat, p_value = stats.ttest_ind(data1, data2, equal_var=False)
                    
                    # Calculate effect size
                    mean1, mean2 = np.mean(data1), np.mean(data2)
                    std1, std2 = np.std(data1, ddof=1), np.std(data2, ddof=1)
                    n1, n2 = len(data1), len(data2)
                    pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1 + n2 - 2))
                    cohens_d = (mean1 - mean2) / pooled_std if pooled_std != 0 else 0
                    
                    significance_results[key] = {
                        't_statistic': float(t_stat),
                        'p_value': float(max(p_value, 1e-10)),  # Prevent 0.0000
                        'cohens_d': float(cohens_d),
                        'significant_0.05': p_value < 0.05,
                        'mean_difference': float(mean1 - mean2),
                        'n1': n1,
                        'n2': n2,
                        'lambda': lambda_val
                    }
        
        return significance_results
    
    @staticmethod
    def perform_anova_across_lambdas(agent_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        FIXED: ANOVA to test if agents behave differently ACROSS lambda values
        """
        anova_results = {}
        
        for agent_type, results in agent_results.items():
            # Group by lambda value
            lambda_groups = {}
            for result in results:
                lambda_val = result['lambda_social']
                if lambda_val not in lambda_groups:
                    lambda_groups[lambda_val] = []
                lambda_groups[lambda_val].append(result['total_utility'])
            
            # Only perform ANOVA if we have multiple lambda values with sufficient data
            if len(lambda_groups) >= 3:
                group_data = [np.array(values) for values in lambda_groups.values()]
                
                # One-way ANOVA
                f_stat, p_value = stats.f_oneway(*group_data)
                
                anova_results[agent_type] = {
                    'f_statistic': float(f_stat),
                    'p_value': float(max(p_value, 1e-10)),
                    'num_lambdas': len(lambda_groups),
                    'lambda_sensitivity': p_value < 0.05  # Significant = sensitive to lambda
                }
        
        return anova_results