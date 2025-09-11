#!/usr/bin/env python3
"""
Complete example of using the scheduler codebase.
This demonstrates the full workflow from creating tasks to running algorithms.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append('/app')

from src.common.tasks.task import Task, TaskConstraintType
from src.common.resources.resource import (
    Resource, ResourceType, ResourceStatus
)
from src.common.tasks.task_manager import TaskManager
from src.common.resources.resource_manager import ResourceManager
from src.algorithms.simple_scheduler import SimpleScheduler
from src.algorithms.base import ScheduleResult, ScheduleStatus
from src.testing.test_framework import (
    TestRunner, TestCaseBuilder
)
from src.common.visualization.schedule_printer import schedule_string_from_result
from src.common.visualization.schedule_visualizer import ScheduleVisualizer


def create_warehouse_scenario():
    """Create a realistic warehouse scenario with the robot."""
    print("Creating Warehouse Scenario")
    print("=" * 40)
    
    base_time = datetime.now()
    
    # Create resources
    print("Creating resources...")
    
    # Gripper (can hold 1 object at a time)
    gripper = Resource.create_integer_resource(
        name="Gripper",
        description="Robot gripper for picking up objects",
        max_capacity=1.0
    )
    
    # Storage bay (can hold 2 objects)
    storage = Resource.create_integer_resource(
        name="Storage Bay",
        description="Storage bay for carrying objects",
        max_capacity=2.0
    )
    
    # Battery (starts at 100%, drains over time)
    battery = Resource.create_cumulative_rate_resource(
        name="Battery",
        description="Robot battery power",
        initial_value=100.0,
        min_value=0.0,
        max_value=100.0
    )
    
    # Fuel tank (starts at 50L, can be refilled)
    fuel = Resource.create_cumulative_rate_resource(
        name="Fuel Tank",
        description="Robot fuel tank",
        initial_value=50.0,
        min_value=0.0,
        max_value=100.0
    )
    
    resources = [gripper, storage, battery, fuel]
    print(f"Created {len(resources)} resources")
    
    # Create tasks
    print("Creating tasks...")
    
    # Task 1: Pick up package A
    task1 = Task.create(
        name="Pick up Package A",
        description="Pick up package A from location 1",
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        min_duration=timedelta(minutes=2),
        max_duration=timedelta(minutes=5),
        preferred_duration=timedelta(minutes=3),
        priority=1
    )
    
    # Task 1 requires gripper
    task1.add_resource_constraint(
        resource_id=gripper.id,
        min_amount=1.0,
        max_amount=1.0
    )
    
    # Task 1 impacts battery (drains 5% per minute)
    task1.add_resource_impact(
        resource_id=battery.id,
        impact_type="rate_change",
        impact_value=-5.0  # 5% per minute
    )
    
    # Task 2: Pick up package B
    task2 = Task.create(
        name="Pick up Package B",
        description="Pick up package B from location 2",
        start_time=base_time + timedelta(minutes=10),
        end_time=base_time + timedelta(hours=1, minutes=10),
        min_duration=timedelta(minutes=2),
        max_duration=timedelta(minutes=5),
        preferred_duration=timedelta(minutes=3),
        priority=2
    )
    
    # Task 2 requires gripper
    task2.add_resource_constraint(
        resource_id=gripper.id,
        min_amount=1.0,
        max_amount=1.0
    )
    
    # Task 2 impacts battery
    task2.add_resource_impact(
        resource_id=battery.id,
        impact_type="rate_change",
        impact_value=-5.0
    )
    
    # Task 3: Transport packages (must start after both pickups)
    task3 = Task.create(
        name="Transport Packages",
        description="Transport packages A and B to destination",
        start_time=base_time + timedelta(minutes=20),
        end_time=base_time + timedelta(hours=2),
        min_duration=timedelta(minutes=15),
        max_duration=timedelta(minutes=30),
        preferred_duration=timedelta(minutes=20),
        priority=3
    )
    
    # Task 3 requires storage bay
    task3.add_resource_constraint(
        resource_id=storage.id,
        min_amount=2.0,  # Need space for both packages
        max_amount=2.0
    )
    
    # Task 3 impacts fuel (consumes 2L per minute)
    task3.add_resource_impact(
        resource_id=fuel.id,
        impact_type="rate_change",
        impact_value=-2.0  # 2L per minute
    )
    
    # Add dependencies: transport must start after both pickups
    task3.add_task_constraint(
        TaskConstraintType.START_AFTER_END,
        task1.id
    )
    task3.add_task_constraint(
        TaskConstraintType.START_AFTER_END,
        task2.id
    )
    
    # Task 4: Drop off packages
    task4 = Task.create(
        name="Drop off Packages",
        description="Drop off packages at destination",
        start_time=base_time + timedelta(minutes=30),
        end_time=base_time + timedelta(hours=2, minutes=30),
        min_duration=timedelta(minutes=1),
        max_duration=timedelta(minutes=3),
        preferred_duration=timedelta(minutes=2),
        priority=4
    )
    
    # Task 4 must be contained within transport task
    task4.add_task_constraint(
        TaskConstraintType.CONTAINED,
        task3.id
    )
    
    tasks = [task1, task2, task3, task4]
    print(f"Created {len(tasks)} tasks")
    
    return tasks, resources


def run_scheduling_example():
    """Run a complete scheduling example."""
    print("Running Scheduling Example")
    print("=" * 40)
    
    # Create scenario
    tasks, resources = create_warehouse_scenario()
    
    # Create managers
    task_manager = TaskManager()
    resource_manager = ResourceManager()
    
    for task in tasks:
        task_manager.add_task(task)
    
    for resource in resources:
        resource_manager.add_resource(resource)
    
    # Create scheduler
    scheduler = SimpleScheduler(time_limit=60.0)
    scheduler.set_managers(task_manager, resource_manager)
    
    # Run scheduling
    print("Running scheduler...")
    result = scheduler.schedule(tasks, resources)
    
    # Display results
    print(f"Status: {result.status.value}")
    print(f"Message: {result.message}")
    print(f"Success rate: {result.success_rate:.2%}")
    print(f"Solve time: {result.solve_time:.2f} seconds")
    print(f"Scheduled tasks: {result.total_scheduled_tasks}")
    print(f"Unscheduled tasks: {result.total_unscheduled_tasks}")
    
    if result.schedule:
        schedule_string = schedule_string_from_result(result, task_manager, resource_manager)
        print(schedule_string)
        
        # Generate visualization
        print("\nGenerating schedule visualization...")
        visualizer = ScheduleVisualizer()
        fig = visualizer.plot_schedule_result(
            result, task_manager, resource_manager,
            title="Warehouse Scenario Schedule"
        )
        
        # Save visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(f'/app/results/{timestamp}', exist_ok=True)
        viz_filename = f'/app/results/{timestamp}/warehouse_scenario_schedule.png'
        visualizer.save_plot(fig, viz_filename)
        print(f"Schedule visualization saved: {viz_filename}")
    
    if result.unscheduled_tasks:
        print("Unscheduled tasks:")
        for task_id in result.unscheduled_tasks:
            task = task_manager.get_task(task_id)
            print(f"  - {task.name}")
    
    return result


def run_testing_example():
    """Run a testing example."""
    print("Running Testing Example")
    print("=" * 40)
    
    # Create test runner
    test_runner = TestRunner()
    
    # Add test cases
    test_runner.add_test_case(TestCaseBuilder.create_simple_test())
    test_runner.add_test_case(TestCaseBuilder.create_dependency_test())
    test_runner.add_test_case(TestCaseBuilder.create_resource_constrained_test())
    test_runner.add_test_case(TestCaseBuilder.create_stress_test(num_tasks=5))
    
    # Create scheduler
    scheduler = SimpleScheduler()
    
    # Run all tests
    print("Running tests...")
    results = test_runner.run_all_tests(scheduler)
    
    # Generate report
    report = test_runner.generate_report()
    print(report)
    
    return results


def demonstrate_multiple_scheduler_testing():
    """Demonstrate how to test multiple schedulers."""
    print("Multiple Scheduler Testing Example")
    print("=" * 40)
    
    # Create a simple test case
    test_case = TestCaseBuilder.create_simple_test()
    
    # Test different scheduler configurations
    schedulers = [
        SimpleScheduler(time_limit=1.0),
        SimpleScheduler(time_limit=5.0),
        SimpleScheduler(time_limit=10.0),
    ]
    
    print("Testing different time limits:")
    for scheduler in schedulers:
        test_runner = TestRunner()
        test_runner.add_test_case(test_case)
        
        results = test_runner.run_all_tests(scheduler)
        result = results[0]
        
        print(f"  Time limit: {scheduler.time_limit}s")
        print(f"  Success rate: {result.schedule_result.success_rate:.2%}")
        print(f"  Solve time: {result.solve_time:.2f}s")
        print(f"  Status: {'PASSED' if result.passed else 'FAILED'}")
        print()


def main():
    """Run the complete example."""
    print("Scheduler Complete Example")
    print("=" * 60)
    print()
    
    # Run scheduling example
    scheduling_result = run_scheduling_example()
    print()
    
    # Run testing example
    testing_results = run_testing_example()
    print()
    
    # Demonstrate multiple scheduler testing
    demonstrate_multiple_scheduler_testing()
    
    print("Summary:")
    print("1. Created tasks with time windows and constraints")
    print("2. Created resources (integer and cumulative rate)")
    print("3. Ran scheduling algorithm")
    print("4. Tested testing single scheduler")
    print("5. Demonstrated multiple scheduler testing")


if __name__ == "__main__":
    main()
