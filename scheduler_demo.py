#!/usr/bin/env python3
"""
Scheduler - Complete Demo and Usage Guide
========================================

This comprehensive demo shows how to:
1. Create tasks with time windows and constraints
2. Create resources (integer and cumulative rate)
3. Run scheduling algorithms
4. Test with multiple scenarios
5. Iterate on algorithm development

This replaces multiple example files with a single, comprehensive demonstration.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.append('/app')

from src.common.tasks.task import Task, TaskConstraintType
from src.common.resources.resource import (
    Resource, ResourceType, ResourceStatus
)
from src.common.tasks.task_manager import TaskManager
from src.common.resources.resource_manager import ResourceManager
from src.algorithms.simple_scheduler import SimpleScheduler
from src.algorithms.milp.milp_scheduler import MILPScheduler
from src.algorithms.base import ScheduleResult, ScheduleStatus
from src.testing.test_framework import (
    TestRunner, TestCaseBuilder
)


class SchedulerDemo:
    """Comprehensive demo of the scheduler system."""
    
    def __init__(self):
        self.task_manager = TaskManager()
        self.resource_manager = ResourceManager()
    
    def demo_1_basic_usage(self):
        """Demo 1: Basic task and resource creation."""
        print("🤖 Demo 1: Basic Task and Resource Creation")
        print("=" * 50)
        
        base_time = datetime.now()
        
        # Create tasks with different characteristics
        print("📋 Creating tasks...")
        
        # Task 1: Simple inspection task
        task1 = Task.create(
            name="Inspect equipment",
            description="Visual inspection of equipment at location A",
            start_time=base_time,
            end_time=base_time + timedelta(hours=2),
            min_duration=timedelta(minutes=5),
            max_duration=timedelta(minutes=15),
            preferred_duration=timedelta(minutes=10),
            priority=1
        )
        
        # Task 2: Pick up task with resource constraint
        task2 = Task.create(
            name="Pick up object",
            description="Pick up object requiring gripper",
            start_time=base_time + timedelta(minutes=30),
            end_time=base_time + timedelta(hours=3),
            min_duration=timedelta(minutes=3),
            max_duration=timedelta(minutes=8),
            preferred_duration=timedelta(minutes=5),
            priority=2
        )
        
        # Task 3: Transport task with dependency
        task3 = Task.create(
            name="Transport object",
            description="Transport the picked up object to destination",
            start_time=base_time + timedelta(hours=1),
            end_time=base_time + timedelta(hours=4),
            min_duration=timedelta(minutes=20),
            max_duration=timedelta(minutes=40),
            preferred_duration=timedelta(minutes=30),
            priority=3
        )
        
        # Add dependency: task3 must start after task2 ends
        task3.add_task_constraint(
            TaskConstraintType.START_AFTER_END,
            task2.id
        )
        
        tasks = [task1, task2, task3]
        
        print(f"Created {len(tasks)} tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.name}")
            print(f"     Time: {task.start_time.strftime('%H:%M')} - {task.end_time.strftime('%H:%M')}")
            print(f"     Duration: {task.min_duration.total_seconds()/60:.1f}-{task.max_duration.total_seconds()/60:.1f} min")
            print(f"     Constraints: {len(task.task_constraints)} task, {len(task.resource_constraints)} resource")
        
        # Create resources
        print("\n🔧 Creating resources...")
        
        # Integer resource: Gripper
        gripper = Resource.create_integer_resource(
            name="Gripper",
            description="Robot gripper for picking up objects",
            max_capacity=1.0
        )
        
        # Cumulative rate resource: Battery
        battery = Resource.create_cumulative_rate_resource(
            name="Battery",
            description="Robot battery power",
            initial_value=100.0,
            min_value=0.0,
            max_value=100.0
        )
        
        # Add resource constraint to task2
        task2.add_resource_constraint(
            resource_id=gripper.id,
            min_amount=1.0,
            max_amount=1.0
        )
        
        resources = [gripper, battery]
        
        print(f"Created {len(resources)} resources:")
        for i, resource in enumerate(resources, 1):
            print(f"  {i}. {resource.name} ({resource.resource_type.value})")
            if resource.resource_type == ResourceType.INTEGER:
                print(f"     Capacity: {resource.max_capacity}")
            else:
                print(f"     Initial: {resource.initial_value}, Range: {resource.min_value}-{resource.max_value}")
        
        return tasks, resources
    
    def demo_2_scheduling_algorithms(self, tasks: List[Task], resources: List[Resource]):
        """Demo 2: Running different scheduling algorithms."""
        print("\n🤖 Demo 2: Scheduling Algorithms")
        print("=" * 50)
        
        # Set up managers
        for task in tasks:
            self.task_manager.add_task(task)
        for resource in resources:
            self.resource_manager.add_resource(resource)
        
        # Test different algorithms
        algorithms = [
            SimpleScheduler(time_limit=60),
            MILPScheduler(time_limit=60)
        ]
        
        for algorithm in algorithms:
            print(f"\n🧮 Testing {algorithm.name}...")
            
            # Set managers
            algorithm.set_managers(self.task_manager, self.resource_manager)
            
            # Run scheduling
            result = algorithm.schedule(tasks, resources)
            
            # Display results
            print(f"  Status: {result.status.value}")
            print(f"  Success rate: {result.success_rate:.1%}")
            print(f"  Scheduled: {result.total_scheduled_tasks}/{result.total_tasks} tasks")
            print(f"  Solve time: {result.solve_time:.3f}s")
            
            if result.schedule:
                print("  Schedule:")
                for scheduled_task in result.schedule:
                    print(f"    - {scheduled_task.task_id[:8]}... "
                          f"{scheduled_task.start_time.strftime('%H:%M')}-{scheduled_task.end_time.strftime('%H:%M')}")
            
            if result.unscheduled_tasks:
                print(f"  Unscheduled: {len(result.unscheduled_tasks)} tasks")
    
    def demo_3_testing_framework(self):
        """Demo 3: Using the testing framework."""
        print("\n🧪 Demo 3: Testing Framework")
        print("=" * 50)
        
        # Create test runner
        test_runner = TestRunner()
        
        # Add various test cases
        print("Creating test cases...")
        test_runner.add_test_case(TestCaseBuilder.create_simple_test())
        test_runner.add_test_case(TestCaseBuilder.create_dependency_test())
        test_runner.add_test_case(TestCaseBuilder.create_resource_constrained_test())
        test_runner.add_test_case(TestCaseBuilder.create_stress_test(num_tasks=5))
        
        print(f"Created {len(test_runner.test_cases)} test cases")
        
        # Test algorithms
        algorithms = [
            SimpleScheduler(time_limit=30),
            MILPScheduler(time_limit=30)
        ]
        
        for algorithm in algorithms:
            print(f"\n🧮 Testing {algorithm.name}...")
            results = test_runner.run_all_tests(algorithm)
            
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            print(f"  Results: {passed}/{total} tests passed")
            
            for result in results:
                status = "✅" if result.passed else "❌"
                print(f"    {status} {result.test_case.name}: {result.message}")
    
    def demo_4_algorithm_development(self):
        """Demo 4: Algorithm development and iteration."""
        print("\n🔄 Demo 4: Algorithm Development")
        print("=" * 50)
        
        print("To develop your own algorithm:")
        print()
        print("1. Create a new scheduler class:")
        print("""
from src.algorithms.base import BaseScheduler, ScheduleResult, ScheduleStatus

class MyScheduler(BaseScheduler):
    def __init__(self, time_limit: float = 300.0):
        super().__init__("My Algorithm", time_limit)
    
    def schedule(self, tasks, resources):
        # Your algorithm implementation here
        scheduled_tasks = []
        
        # Example: Simple priority-based scheduling
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)
        
        for task in sorted_tasks:
            # Try to schedule the task
            # ... your logic here ...
            pass
        
        return self.create_schedule_result(
            status=ScheduleStatus.SUCCESS,
            schedule=scheduled_tasks,
            message="Scheduled using my algorithm"
        )
""")
        
        print("2. Test your algorithm:")
        print("""
# Create test scenario
tasks, resources = create_test_scenario()

# Test your algorithm
scheduler = MyScheduler()
scheduler.set_managers(task_manager, resource_manager)
result = scheduler.schedule(tasks, resources)

# Analyze results
print(f"Success rate: {result.success_rate:.1%}")
print(f"Scheduled: {result.total_scheduled_tasks} tasks")
""")
        
        print("3. Iterate and improve:")
        print("   - Adjust algorithm parameters")
        print("   - Add new constraint handling")
        print("   - Optimize for different objectives")
        print("   - Test with more complex scenarios")
    
    def demo_5_advanced_features(self):
        """Demo 5: Advanced features and customization."""
        print("\n⚡ Demo 5: Advanced Features")
        print("=" * 50)
        
        print("Advanced features available:")
        print()
        print("1. Complex task constraints:")
        print("   - START_AFTER_END: Task must start after another ends")
        print("   - CONTAINED: Task must be contained within another")
        print()
        print("2. Resource types:")
        print("   - INTEGER: Discrete capacity (e.g., grippers, storage slots)")
        print("   - CUMULATIVE_RATE: Continuous with rate changes (e.g., battery, fuel)")
        print()
        print("3. Resource impacts:")
        print("   - RATE_CHANGE: Change resource consumption rate")
        print("   - SET_IN_USE: Mark resource as unavailable")
        print()
        print("4. Time windows and duration flexibility:")
        print("   - min_duration, max_duration, preferred_duration")
        print("   - Flexible scheduling within time windows")
        print()
        print("5. Priority-based scheduling:")
        print("   - Tasks have priority levels (1 = highest)")
        print("   - Algorithms can use priority for ordering")
    
    def run_complete_demo(self):
        """Run the complete demonstration."""
        print("🚀 Scheduler - Complete Demo")
        print("=" * 60)
        print("This demo shows the complete workflow for using the scheduler.")
        print()
        
        # Demo 1: Basic usage
        tasks, resources = self.demo_1_basic_usage()
        
        # Demo 2: Scheduling algorithms
        self.demo_2_scheduling_algorithms(tasks, resources)
        
        # Demo 3: Testing framework
        self.demo_3_testing_framework()
        
        # Demo 4: Algorithm development
        self.demo_4_algorithm_development()
        
        # Demo 5: Advanced features
        self.demo_5_advanced_features()
        
        print("\n🎯 Summary:")
        print("✅ Created tasks with time windows and constraints")
        print("✅ Created resources (integer and cumulative rate)")
        print("✅ Ran multiple scheduling algorithms")
        print("✅ Tested with comprehensive test framework")
        print("✅ Demonstrated algorithm development workflow")
        print("✅ Showed advanced features and customization")
        
        print("\n📚 Next Steps:")
        print("1. Implement your own scheduling algorithm")
        print("2. Create test cases for your specific scenarios")
        print("3. Benchmark different algorithms")
        print("4. Integrate with your robot control system")
        print("5. Add performance metrics and optimization")
        
        print("\n💡 Tips:")
        print("- Start with simple algorithms and add complexity gradually")
        print("- Use the testing framework to validate your implementations")
        print("- Consider both solution quality and computation time")
        print("- Test with edge cases and stress scenarios")


def main():
    """Run the complete demo."""
    demo = SchedulerDemo()
    demo.run_complete_demo()


if __name__ == "__main__":
    main()
