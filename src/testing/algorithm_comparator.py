"""
Algorithm comparison and visualization tools.
"""

from typing import List, Dict, Any
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .test_runner import TestRunner, TestResult
from .test_case import TestCase


class AlgorithmComparator:
    """Compares algorithms and generates comparison reports."""
    
    def __init__(self, test_runner: TestRunner):
        self.test_runner = test_runner
    
    def compare_algorithms(self, test_cases: List[TestCase], algorithms: List[Any]) -> Dict[str, Any]:
        """Run comparison tests and return results."""
        results = self.test_runner.run_test_suite(test_cases, algorithms)
        return self._analyze_results(results)
    
    def _analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analyze test results and generate comparison metrics."""
        if not results:
            return {"error": "No results to analyze"}
        
        # Convert to DataFrame for easier analysis
        data = []
        for result in results:
            row = {
                "algorithm": result.algorithm_name,
                "test_case": result.test_case_name,
                "execution_time": result.execution_time,
                "status": result.schedule_result.status.value,
                "tasks_scheduled": result.metrics.get("tasks_scheduled", 0),
                "total_tasks": result.metrics.get("total_tasks", 0),
                "success_rate": result.metrics.get("scheduling_success_rate", 0),
                "makespan": result.metrics.get("makespan", None),
                "objective_value": result.schedule_result.objective_value
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Calculate comparison metrics
        comparison = {
            "dataframe": df,
            "summary": self._calculate_summary(df),
            "performance_metrics": self._calculate_performance_metrics(df),
            "ranking": self._calculate_algorithm_ranking(df)
        }
        
        return comparison
    
    def _calculate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics."""
        summary = {
            "total_tests": len(df),
            "algorithms": df["algorithm"].unique().tolist(),
            "test_cases": df["test_case"].unique().tolist(),
            "overall_success_rate": (df["status"] == "success").mean(),
            "average_execution_time": df["execution_time"].mean(),
            "average_success_rate": df["success_rate"].mean()
        }
        
        return summary
    
    def _calculate_performance_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance metrics by algorithm."""
        metrics = {}
        
        for algorithm in df["algorithm"].unique():
            alg_data = df[df["algorithm"] == algorithm]
            
            metrics[algorithm] = {
                "success_rate": (alg_data["status"] == "success").mean(),
                "average_execution_time": alg_data["execution_time"].mean(),
                "average_scheduling_success_rate": alg_data["success_rate"].mean(),
                "average_makespan": alg_data["makespan"].mean() if "makespan" in alg_data.columns else None,
                "total_tests": len(alg_data),
                "successful_tests": (alg_data["status"] == "success").sum()
            }
        
        return metrics
    
    def _calculate_algorithm_ranking(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate algorithm ranking based on multiple criteria."""
        rankings = []
        
        for algorithm in df["algorithm"].unique():
            alg_data = df[df["algorithm"] == algorithm]
            
            # Calculate composite score
            success_rate = (alg_data["status"] == "success").mean()
            avg_success_rate = alg_data["success_rate"].mean()
            avg_execution_time = alg_data["execution_time"].mean()
            
            # Normalize execution time (lower is better)
            max_time = df["execution_time"].max()
            normalized_time = 1 - (avg_execution_time / max_time) if max_time > 0 else 1
            
            # Composite score (weighted average)
            composite_score = (
                0.4 * success_rate +           # 40% weight on success rate
                0.4 * avg_success_rate +       # 40% weight on scheduling success rate
                0.2 * normalized_time          # 20% weight on execution time
            )
            
            rankings.append({
                "algorithm": algorithm,
                "composite_score": composite_score,
                "success_rate": success_rate,
                "scheduling_success_rate": avg_success_rate,
                "average_execution_time": avg_execution_time,
                "total_tests": len(alg_data)
            })
        
        # Sort by composite score (descending)
        rankings.sort(key=lambda x: x["composite_score"], reverse=True)
        
        return rankings
    
    def plot_performance_comparison(self, comparison_results: Dict[str, Any], save_path: str = None) -> plt.Figure:
        """Create performance comparison plots."""
        df = comparison_results["dataframe"]
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Algorithm Performance Comparison", fontsize=16)
        
        # 1. Success Rate by Algorithm
        success_rates = df.groupby("algorithm")["status"].apply(lambda x: (x == "success").mean())
        axes[0, 0].bar(success_rates.index, success_rates.values)
        axes[0, 0].set_title("Success Rate by Algorithm")
        axes[0, 0].set_ylabel("Success Rate")
        axes[0, 0].set_ylim(0, 1)
        
        # 2. Execution Time by Algorithm
        exec_times = df.groupby("algorithm")["execution_time"].mean()
        axes[0, 1].bar(exec_times.index, exec_times.values)
        axes[0, 1].set_title("Average Execution Time by Algorithm")
        axes[0, 1].set_ylabel("Execution Time (seconds)")
        
        # 3. Scheduling Success Rate by Algorithm
        sched_success = df.groupby("algorithm")["success_rate"].mean()
        axes[1, 0].bar(sched_success.index, sched_success.values)
        axes[1, 0].set_title("Average Scheduling Success Rate by Algorithm")
        axes[1, 0].set_ylabel("Scheduling Success Rate")
        axes[1, 0].set_ylim(0, 1)
        
        # 4. Makespan Comparison (if available)
        if "makespan" in df.columns and df["makespan"].notna().any():
            makespan_data = df[df["makespan"].notna()]
            if not makespan_data.empty:
                makespan_avg = makespan_data.groupby("algorithm")["makespan"].mean()
                axes[1, 1].bar(makespan_avg.index, makespan_avg.values)
                axes[1, 1].set_title("Average Makespan by Algorithm")
                axes[1, 1].set_ylabel("Makespan (minutes)")
            else:
                axes[1, 1].text(0.5, 0.5, "No makespan data available", 
                               ha='center', va='center', transform=axes[1, 1].transAxes)
        else:
            axes[1, 1].text(0.5, 0.5, "No makespan data available", 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def generate_report(self, comparison_results: Dict[str, Any]) -> str:
        """Generate a text report of the comparison results."""
        report = []
        report.append("=" * 80)
        report.append("ALGORITHM COMPARISON REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        summary = comparison_results["summary"]
        report.append("SUMMARY:")
        report.append(f"  Total Tests: {summary['total_tests']}")
        report.append(f"  Algorithms Tested: {', '.join(summary['algorithms'])}")
        report.append(f"  Test Cases: {', '.join(summary['test_cases'])}")
        report.append(f"  Overall Success Rate: {summary['overall_success_rate']:.2%}")
        report.append(f"  Average Execution Time: {summary['average_execution_time']:.3f}s")
        report.append("")
        
        # Performance metrics
        report.append("PERFORMANCE METRICS BY ALGORITHM:")
        report.append("-" * 50)
        for alg_name, metrics in comparison_results["performance_metrics"].items():
            report.append(f"\n{alg_name}:")
            report.append(f"  Success Rate: {metrics['success_rate']:.2%}")
            report.append(f"  Scheduling Success Rate: {metrics['average_scheduling_success_rate']:.2%}")
            report.append(f"  Average Execution Time: {metrics['average_execution_time']:.3f}s")
            report.append(f"  Total Tests: {metrics['total_tests']}")
            if metrics['average_makespan']:
                report.append(f"  Average Makespan: {metrics['average_makespan']:.2f} minutes")
        
        # Ranking
        report.append("\n" + "=" * 80)
        report.append("ALGORITHM RANKING (by composite score):")
        report.append("=" * 80)
        for i, ranking in enumerate(comparison_results["ranking"], 1):
            report.append(f"{i}. {ranking['algorithm']}")
            report.append(f"   Composite Score: {ranking['composite_score']:.3f}")
            report.append(f"   Success Rate: {ranking['success_rate']:.2%}")
            report.append(f"   Scheduling Success Rate: {ranking['scheduling_success_rate']:.2%}")
            report.append(f"   Average Execution Time: {ranking['average_execution_time']:.3f}s")
            report.append("")
        
        return "\n".join(report)
