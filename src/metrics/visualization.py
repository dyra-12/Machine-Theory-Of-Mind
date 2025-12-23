"""
Plotting utilities for experiment analysis
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import numpy as np

class ResultVisualizer:
    """Creates publication-quality plots from experiment results"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style for publication
        plt.style.use('seaborn-v0_8-whitegrid')
        self.colors = sns.color_palette("husl", 8)
    
    def create_pareto_plot(self, pareto_metrics: Dict[str, Any], 
                          all_results: List[Dict]) -> Path:
        """Create Pareto frontier comparison plot"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot all points with transparency
        df = pd.DataFrame(all_results)
        sns.scatterplot(data=df, x='task_reward', y='social_score', 
                       hue='agent_type', alpha=0.3, ax=ax)
        
        # Plot Pareto frontiers
        for i, (agent_type, metrics) in enumerate(pareto_metrics.items()):
            if metrics['pareto_front']:
                front_x, front_y = zip(*metrics['pareto_front'])
                ax.plot(front_x, front_y, '--', color=self.colors[i], 
                       linewidth=2, label=f'{agent_type} Pareto')
        
        ax.set_xlabel('Task Reward', fontsize=12)
        ax.set_ylabel('Social Score', fontsize=12)
        ax.set_title('Pareto Frontiers: Task vs Social Trade-offs', fontsize=14)
        ax.legend()
        
        # Save plot
        plot_path = self.output_dir / "pareto_frontiers.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def create_performance_comparison(self, agent_metrics: Dict, 
                                    significance_results: Dict) -> Path:
        """Create performance comparison box plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()

        metric_specs = [
            ('task_rewards', 'Task Reward'),
            ('social_scores', 'Social Score'),
            ('total_utilities', 'Total Utility'),
            ('warmth_values', 'Warmth'),
        ]

        # Prepare data for plotting
        plot_rows = []
        for agent_type, metrics in agent_metrics.items():
            for metric_key, metric_title in metric_specs:
                values = metrics.get(metric_key)
                if values is None:
                    continue
                for value in values:
                    plot_rows.append({
                        'agent_type': agent_type,
                        'metric_key': metric_key,
                        'metric_title': metric_title,
                        'value': value,
                    })

        df = pd.DataFrame(plot_rows)

        # Create box plots
        for i, (metric_key, metric_title) in enumerate(metric_specs):
            metric_data = df[df['metric_key'] == metric_key] if not df.empty else df
            if metric_data.empty:
                axes[i].set_title(f'{metric_title} by Agent Type')
                axes[i].set_xlabel('agent_type')
                axes[i].set_ylabel('value')
                axes[i].text(0.5, 0.5, 'No data', ha='center', va='center', transform=axes[i].transAxes)
                axes[i].set_xticks([])
                continue

            sns.boxplot(data=metric_data, x='agent_type', y='value', ax=axes[i])
            axes[i].set_title(f'{metric_title} by Agent Type')
            axes[i].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plot_path = self.output_dir / "performance_comparison.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def create_lambda_sensitivity_plot(self, results: List[Dict]) -> Path:
        """Plot how performance changes with lambda values"""
        df = pd.DataFrame(results)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        # Plot metrics vs lambda for each agent type
        metrics = ['task_reward', 'social_score', 'total_utility', 'warmth_final']
        titles = ['Task Reward', 'Social Score', 'Total Utility', 'Warmth']
        
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            for agent_type in df['agent_type'].unique():
                agent_data = df[df['agent_type'] == agent_type]
                if not agent_data.empty:
                    # Group by lambda and calculate mean ± std
                    grouped = agent_data.groupby('lambda_social')[metric].agg(['mean', 'std'])
                    axes[i].plot(grouped.index, grouped['mean'], 'o-', label=agent_type)
                    axes[i].fill_between(grouped.index, 
                                       grouped['mean'] - grouped['std'],
                                       grouped['mean'] + grouped['std'], alpha=0.2)
            
            axes[i].set_xlabel('Lambda (Social Weight)')
            axes[i].set_ylabel(title)
            axes[i].set_title(f'{title} vs Lambda')
            axes[i].legend()
        
        plt.tight_layout()
        plot_path = self.output_dir / "lambda_sensitivity.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_path