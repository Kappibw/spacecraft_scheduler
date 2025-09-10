"""
Test runner for algorithm evaluation and comparison.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import time

from .test_case import TestCase
from src.algorithms.base import BaseScheduler, ScheduleResult


@dataclass
class TestResult:
    """Result of running a test case with an algorithm."""
    
    test_case_name: str
    algorithm_name: str
    schedule_result: ScheduleResult
    execution_time: float
    timestamp: datetime
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


class TestRunner:
    """Runs test cases against algorithms and collects results."""
    
    def __init__(self):
        self.results: List[TestResult] = []
    
    def run_test(self, test_case: TestCase, algorithm: BaseScheduler) -> TestResult:
        """Run a single test case with an algorithm."""
        print(f"Running {test_case.name} with {algorithm.name}...")
        
        start_time = time.time()
        
        # Run the algorithm
        schedule_result = algorithm.schedule(
            test_case.tasks, 
            test_case.resources, 
            test_case.constraints
        )
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        metrics = self._calculate_metrics(test_case, schedule_result, execution_time)
        
        # Create result
        result = TestResult(
            test_case_name=test_case.name,
            algorithm_name=algorithm.name,
            schedule_result=schedule_result,
            execution_time=execution_time,
            timestamp=datetime.now(),
            metrics=metrics
        )
        
        self.results.append(result)
        
        print(f"  Status: {schedule_result.status.value}")
        print(f"  Execution time: {execution_time:.3f}s")
        print(f"  Tasks scheduled: {len(schedule_result.schedule)}")
        if schedule_result.objective_value:
            print(f"  Objective value: {schedule_result.objective_value:.2f}")
        
        return result
    
    def run_test_suite(self, test_cases: List[TestCase], algorithms: List[BaseScheduler]) -> List[TestResult]:
        """Run multiple test cases against multiple algorithms."""
        all_results = []
        
        for test_case in test_cases:
            print(f"\n{'='*60}")
            print(f"Test Case: {test_case.name}")
            print(f"Description: {test_case.description}")
            print(f"Tasks: {len(test_case.tasks)}, Resources: {len(test_case.resources)}")
            print(f"{'='*60}")
            
            for algorithm in algorithms:
                result = self.run_test(test_case, algorithm)
                all_results.append(result)
                print()
        
        return all_results
    
    def _calculate_metrics(self, test_case: TestCase, schedule_result: ScheduleResult, execution_time: float) -> Dict[str, Any]:
        """Calculate performance metrics for a test result."""
        metrics = {
            "execution_time": execution_time,
            "status": schedule_result.status.value,
            "tasks_scheduled": len(schedule_result.schedule),
            "total_tasks": len(test_case.tasks),
            "scheduling_success_rate": len(schedule_result.schedule) / len(test_case.tasks) if test_case.tasks else 0
        }
        
        if schedule_result.objective_value:
            metrics["objective_value"] = schedule_result.objective_value
        
        if schedule_result.solve_time:
            metrics["solve_time"] = schedule_result.solve_time
        
        # Calculate makespan from schedule
        if schedule_result.schedule:
            start_times = []
            end_times = []
            
            for task_schedule in schedule_result.schedule:
                start_time = datetime.fromisoformat(task_schedule["start_time"])
                end_time = datetime.fromisoformat(task_schedule["end_time"])
                start_times.append(start_time)
                end_times.append(end_time)
            
            if start_times and end_times:
                makespan = (max(end_times) - min(start_times)).total_seconds() / 60  # minutes
                metrics["makespan"] = makespan
                
                # Compare with expected makespan if available
                if test_case.expected_makespan:
                    metrics["makespan_ratio"] = makespan / test_case.expected_makespan
        
        return metrics
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get a summary of all test results."""
        if not self.results:
            return {"message": "No test results available"}
        
        summary = {
            "total_tests": len(self.results),
            "algorithms_tested": list(set(r.algorithm_name for r in self.results)),
            "test_cases_tested": list(set(r.test_case_name for r in self.results)),
            "success_rate": sum(1 for r in self.results if r.schedule_result.status.value == "success") / len(self.results),
            "average_execution_time": sum(r.execution_time for r in self.results) / len(self.results),
            "results_by_algorithm": {},
            "results_by_test_case": {}
        }
        
        # Group by algorithm
        for result in self.results:
            alg_name = result.algorithm_name
            if alg_name not in summary["results_by_algorithm"]:
                summary["results_by_algorithm"][alg_name] = {
                    "total_tests": 0,
                    "successful_tests": 0,
                    "average_execution_time": 0,
                    "average_makespan": 0
                }
            
            alg_summary = summary["results_by_algorithm"][alg_name]
            alg_summary["total_tests"] += 1
            if result.schedule_result.status.value == "success":
                alg_summary["successful_tests"] += 1
            
            alg_summary["average_execution_time"] += result.execution_time
            if "makespan" in result.metrics:
                alg_summary["average_makespan"] += result.metrics["makespan"]
        
        # Calculate averages
        for alg_name, alg_summary in summary["results_by_algorithm"].items():
            alg_summary["average_execution_time"] /= alg_summary["total_tests"]
            alg_summary["average_makespan"] /= alg_summary["total_tests"]
            alg_summary["success_rate"] = alg_summary["successful_tests"] / alg_summary["total_tests"]
        
        return summary
    
    def save_results(self, filepath: str) -> None:
        """Save test results to JSON file."""
        import json
        
        results_data = []
        for result in self.results:
            result_data = {
                "test_case_name": result.test_case_name,
                "algorithm_name": result.algorithm_name,
                "execution_time": result.execution_time,
                "timestamp": result.timestamp.isoformat(),
                "metrics": result.metrics,
                "schedule_result": {
                    "status": result.schedule_result.status.value,
                    "schedule": result.schedule_result.schedule,
                    "objective_value": result.schedule_result.objective_value,
                    "solve_time": result.schedule_result.solve_time,
                    "message": result.schedule_result.message
                }
            }
            results_data.append(result_data)
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
    
    def clear_results(self) -> None:
        """Clear all test results."""
        self.results = []
