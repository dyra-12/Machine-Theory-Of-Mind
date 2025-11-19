"""
Pareto frontier calculations for multi-objective optimization
"""
import numpy as np
from typing import List, Dict, Tuple, Any

class ParetoAnalyzer:
    """Analyzes Pareto optimality in task-social trade-offs"""
    
    @staticmethod
    def find_pareto_frontier(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Find Pareto-optimal points (maximizing both objectives)
        
        Args:
            points: List of (task_reward, social_score) tuples
            
        Returns:
            Pareto-optimal points sorted by task_reward
        """
        if not points:
            return []
        
        # Sort by task reward (first objective)
        sorted_points = sorted(points, key=lambda x: x[0])
        pareto_front = [sorted_points[0]]
        
        for point in sorted_points[1:]:
            # Check if this point dominates the last Pareto point
            last_pareto = pareto_front[-1]
            if point[1] > last_pareto[1]:  # Higher social score
                pareto_front.append(point)
        
        return pareto_front
    
    @staticmethod
    def calculate_pareto_metrics(agent_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """FIXED: Proper Pareto analysis with real data"""
        pareto_metrics = {}
        
        for agent_type, results in agent_results.items():
            # FIX: Filter out invalid results
            valid_results = [r for r in results if r['task_reward'] is not None and r['social_score'] is not None]
            
            if not valid_results:
                print(f"⚠️  No valid results for {agent_type}")
                continue
                
            # FIX: Extract points properly
            points = [(r['task_reward'], r['social_score']) for r in valid_results]
            
            # FIX: Remove duplicates and ensure minimum points
            unique_points = list(set(points))
            
            if len(unique_points) < 2:
                # Single point - can't have Pareto frontier
                pareto_metrics[agent_type] = {
                    'pareto_front': unique_points,
                    'auc': 0.0,
                    'task_range': 0.0,
                    'social_range': 0.0,
                    'hypervolume': unique_points[0][0] * unique_points[0][1] if unique_points else 0.0,
                    'num_pareto_points': len(unique_points),
                    'total_points': len(points)
                }
                continue
            
            # Find Pareto frontier
            pareto_front = ParetoAnalyzer.find_pareto_frontier(unique_points)
            
            # FIX: Calculate metrics only if we have a real frontier
            if len(pareto_front) > 1:
                auc = ParetoAnalyzer.calculate_auc(pareto_front)
                task_range = max(p[0] for p in pareto_front) - min(p[0] for p in pareto_front)
                social_range = max(p[1] for p in pareto_front) - min(p[1] for p in pareto_front)
                hypervolume = ParetoAnalyzer.calculate_hypervolume(pareto_front)
            else:
                auc = task_range = social_range = 0.0
                hypervolume = pareto_front[0][0] * pareto_front[0][1] if pareto_front else 0.0
            
            pareto_metrics[agent_type] = {
                'pareto_front': pareto_front,
                'auc': auc,
                'task_range': task_range,
                'social_range': social_range,
                'hypervolume': hypervolume,
                'num_pareto_points': len(pareto_front),
                'total_points': len(points)
            }
        
        return pareto_metrics
    @staticmethod
    def calculate_auc(pareto_front: List[Tuple[float, float]]) -> float:
        """Calculate Area Under Curve for Pareto frontier"""
        if len(pareto_front) < 2:
            return 0.0
        
        # Sort by task reward (x-axis)
        sorted_front = sorted(pareto_front, key=lambda x: x[0])
        
        # Trapezoidal rule for AUC
        auc = 0.0
        for i in range(1, len(sorted_front)):
            x1, y1 = sorted_front[i-1]
            x2, y2 = sorted_front[i]
            auc += (x2 - x1) * (y1 + y2) / 2
        
        return auc
    
    @staticmethod
    def calculate_hypervolume(pareto_front: List[Tuple[float, float]], 
                            reference: Tuple[float, float] = (0, 0)) -> float:
        """Calculate hypervolume dominated by Pareto front"""
        if not pareto_front:
            return 0.0
        
        # Sort by first objective
        sorted_front = sorted(pareto_front, key=lambda x: x[0])
        ref_x, ref_y = reference
        
        hypervolume = 0.0
        prev_x = ref_x
        
        for point in sorted_front:
            x, y = point
            hypervolume += (x - prev_x) * (y - ref_y)
            prev_x = x
        
        return hypervolume