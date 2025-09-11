#!/usr/bin/env python3
"""
Scheduler - Spacecraft scheduling algorithm development and comparison
for the spacecraft.
"""

import sys
import os
from datetime import datetime

sys.path.append('/app')

from src.testing.test_framework import TestCaseBuilder, TestRunner
from src.algorithms.simple_scheduler import SimpleScheduler
from src.algorithms.milp.milp_scheduler import MILPScheduler
from src.common.visualization.schedule_printer import schedule_string_from_result
from src.common.visualization.schedule_visualizer import ScheduleVisualizer


def main():
    """Run spacecraft scheduling algorithm development and comparison."""
    print("Spacecraft Scheduling Algorithm Development")
    print("=" * 60)
    
    # Create test cases
    print("\nCreating test cases...")
    test_runner = TestRunner()
    
    test_runner.add_test_case(TestCaseBuilder.create_simple_test())
    test_runner.add_test_case(TestCaseBuilder.create_dependency_test())
    test_runner.add_test_case(TestCaseBuilder.create_resource_constrained_test())
    test_runner.add_test_case(TestCaseBuilder.create_stress_test(num_tasks=10))
    
    print(f"Created {len(test_runner.test_cases)} test cases:")
    for i, test_case in enumerate(test_runner.test_cases, 1):
        print(f"  {i}. {test_case.name}: {len(test_case.task_manager.tasks)} tasks, "
              f"{len(test_case.resource_manager.resources)} resources")
    
    # Initialize algorithms
    print("\nInitializing algorithms...")
    algorithms = [
        SimpleScheduler(time_limit=60),
        MILPScheduler(time_limit=60),
        # Add more algorithms here as you develop them
    ]
    
    print(f"Initialized {len(algorithms)} algorithms:")
    for i, algorithm in enumerate(algorithms, 1):
        print(f"  {i}. {algorithm.name}")
    
    # Run comparison
    print("\nRunning algorithm comparison...")
    
    # Test each algorithm
    all_results = {}
    for algorithm in algorithms:
        print(f"\nTesting {algorithm.name}...")
        results = test_runner.run_all_tests(algorithm)
        all_results[algorithm.name] = results
    
    # Generate report
    print("\nGenerating performance report...")
    for algorithm_name, results in all_results.items():
        print(f"\n{algorithm_name} Results:")
        for result in results:
            print()
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"  {status} {result.test_case.name}: {result.message}")
            print(schedule_string_from_result(result.schedule_result, result.test_case.task_manager, result.test_case.resource_manager))
            print('--------------------------------')
    
    # Save results
    print("\nSaving results...")
    os.makedirs('/app/results', exist_ok=True)

    # Make a directory for the results with the current date and time
    results_dir = f'/app/results/{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    os.makedirs(results_dir, exist_ok=True)
    
    # Save test results
    with open(f'{results_dir}/test_results.json', 'w', encoding='utf-8') as f:
        import json
        results_data = {}
        for algorithm_name, results in all_results.items():
            results_data[algorithm_name] = [
                {
                    "test_case": result.test_case.name,
                    "passed": result.passed,
                    "message": result.message,
                    "success_rate": result.schedule_result.success_rate,
                    "solve_time": result.solve_time
                }
                for result in results
            ]
        json.dump(results_data, f, indent=2)
    
    # Save comparison report
    with open(f'{results_dir}/comparison_report.txt', 'w', encoding='utf-8') as f:
        f.write("Scheduler Algorithm Comparison Report\n")
        f.write("=" * 50 + "\n\n")
        
        for algorithm_name, results in all_results.items():
            f.write(f"{algorithm_name}:\n")
            f.write("-" * 20 + "\n")
            for result in results:
                status = "PASSED" if result.passed else "FAILED"
                f.write(f"  {result.test_case.name}: {status}\n")
                f.write(f"    {result.message}\n")
            f.write("\n")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    visualizer = ScheduleVisualizer()
    
    # Create visualizations for each algorithm's best result
    for algorithm_name, results in all_results.items():
        # Save an image for each results
        for result in results:
            print(f"  Creating visualization for {algorithm_name}...")
            
            # Create visualization
            fig = visualizer.plot_schedule_result(
                result.schedule_result,
                result.test_case.task_manager,
                result.test_case.resource_manager,
                title=f"{algorithm_name} - {result.test_case.name}"
            )
            
            # Save visualization
            viz_filename = f"{results_dir}/{algorithm_name.lower().replace(' ', '_')}_{result.test_case.name}_visualization.png"
            visualizer.save_plot(fig, viz_filename)
            print(f"    Saved: {viz_filename}")
    
    print("\nResults saved:")
    print(f"  - results/{results_dir}/test_results.json")
    print(f"  - results/{results_dir}/comparison_report.txt")
    print(f"  - results/{results_dir}/*_visualization.png")


if __name__ == "__main__":
    main()