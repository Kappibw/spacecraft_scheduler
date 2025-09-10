#!/usr/bin/env python3
"""
Scheduler - Robot scheduling algorithm development and comparison
for the robot.
"""

import sys
import os
import matplotlib.pyplot as plt

sys.path.append('/app')

from src.testing.test_framework import TestCaseBuilder, TestRunner
from src.algorithms.simple_scheduler import SimpleScheduler
from src.algorithms.milp.milp_scheduler import MILPScheduler


def main():
    """Run robot scheduling algorithm development and comparison."""
    print("🤖 Robot Scheduling Algorithm Development")
    print("=" * 60)
    
    # Create test cases
    print("\n📋 Creating test cases...")
    test_runner = TestRunner()
    
    test_runner.add_test_case(TestCaseBuilder.create_simple_test())
    test_runner.add_test_case(TestCaseBuilder.create_dependency_test())
    test_runner.add_test_case(TestCaseBuilder.create_resource_constrained_test())
    test_runner.add_test_case(TestCaseBuilder.create_stress_test(num_tasks=10))
    
    print(f"Created {len(test_runner.test_cases)} test cases:")
    for i, test_case in enumerate(test_runner.test_cases, 1):
        print(f"  {i}. {test_case.name}: {len(test_case.tasks)} tasks, "
              f"{len(test_case.resources)} resources")
    
    # Initialize algorithms
    print("\n🤖 Initializing algorithms...")
    algorithms = [
        SimpleScheduler(time_limit=60),
        MILPScheduler(time_limit=60),
        # Add more algorithms here as you develop them
    ]
    
    print(f"Initialized {len(algorithms)} algorithms:")
    for i, algorithm in enumerate(algorithms, 1):
        print(f"  {i}. {algorithm.name}")
    
    # Run comparison
    print("\n🔄 Running algorithm comparison...")
    
    # Test each algorithm
    all_results = {}
    for algorithm in algorithms:
        print(f"\nTesting {algorithm.name}...")
        results = test_runner.run_all_tests(algorithm)
        all_results[algorithm.name] = results
    
    # Generate report
    print("\n📊 Generating performance report...")
    for algorithm_name, results in all_results.items():
        print(f"\n{algorithm_name} Results:")
        for result in results:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"  {status} {result.test_case.name}: {result.message}")
    
    # Save results
    print("\n💾 Saving results...")
    os.makedirs('/app/results', exist_ok=True)
    
    # Save test results
    with open('/app/results/endurance_test_results.json', 'w', encoding='utf-8') as f:
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
    with open('/app/results/endurance_comparison_report.txt', 'w', encoding='utf-8') as f:
        f.write("Endurance Scheduler Algorithm Comparison Report\n")
        f.write("=" * 50 + "\n\n")
        
        for algorithm_name, results in all_results.items():
            f.write(f"{algorithm_name}:\n")
            f.write("-" * 20 + "\n")
            for result in results:
                status = "PASSED" if result.passed else "FAILED"
                f.write(f"  {result.test_case.name}: {status}\n")
                f.write(f"    {result.message}\n")
            f.write("\n")
    
    print("📊 Results saved:")
    print("  - results/endurance_test_results.json")
    print("  - results/endurance_comparison_report.txt")
    
    print("\nEndurance scheduler development complete! "
          "Check the results/ directory for outputs.")


if __name__ == "__main__":
    main()