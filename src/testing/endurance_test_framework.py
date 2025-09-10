"""
Test framework for Endurance scheduler algorithms.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time

sys.path.append('/app')

from src.common.tasks.endurance_task import EnduranceTask, TaskConstraintType
from src.common.resources.endurance_resource import (
    EnduranceResource, ResourceType, ResourceStatus
)
from src.common.tasks.endurance_task_manager import EnduranceTaskManager
from src.common.resources.endurance_resource_manager import EnduranceResourceManager
from src.algorithms.base import BaseScheduler, EnduranceScheduleResult, ScheduleStatus


class EnduranceTestCase:
    """Represents a test case for the Endurance scheduler."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tasks: List[EnduranceTask] = []
        self.resources: List[EnduranceResource] = []
        self.expected_min_success_rate: float = 0.0
        self.expected_max_solve_time: float = float('inf')
        self.metadata: Dict[str, Any] = {}
    
    def add_task(self, task: EnduranceTask) -> None:
        """Add a task to the test case."""
        self.tasks.append(task)
    
    def add_resource(self, resource: EnduranceResource) -> None:
        """Add a resource to the test case."""
        self.resources.append(resource)
    
    def set_expectations(self, min_success_rate: float = 0.0, max_solve_time: float = float('inf')) -> None:
        """Set expectations for this test case."""
        self.expected_min_success_rate = min_success_rate
        self.expected_max_solve_time = max_solve_time


class EnduranceTestResult:
    """Represents the result of running a test case."""
    
    def __init__(self, test_case: EnduranceTestCase, schedule_result: EnduranceScheduleResult, solve_time: float):
        self.test_case = test_case
        self.schedule_result = schedule_result
        self.solve_time = solve_time
        self.passed = self._evaluate_result()
        self.message = self._generate_message()
    
    def _evaluate_result(self) -> bool:
        """Evaluate whether the test passed."""
        # Check success rate
        if self.schedule_result.success_rate < self.test_case.expected_min_success_rate:
            return False
        
        # Check solve time
        if self.solve_time > self.test_case.expected_max_solve_time:
            return False
        
        return True
    
    def _generate_message(self) -> str:
        """Generate a message describing the test result."""
        if self.passed:
            return f"PASSED - Success rate: {self.schedule_result.success_rate:.2%}, Solve time: {self.solve_time:.2f}s"
        else:
            issues = []
            if self.schedule_result.success_rate < self.test_case.expected_min_success_rate:
                issues.append(f"Success rate {self.schedule_result.success_rate:.2%} < expected {self.test_case.expected_min_success_rate:.2%}")
            if self.solve_time > self.test_case.expected_max_solve_time:
                issues.append(f"Solve time {self.solve_time:.2f}s > expected {self.test_case.expected_max_solve_time:.2f}s")
            return f"FAILED - {', '.join(issues)}"


class EnduranceTestRunner:
    """Runs test cases against Endurance schedulers."""
    
    def __init__(self):
        self.test_cases: List[EnduranceTestCase] = []
        self.results: List[EnduranceTestResult] = []
    
    def add_test_case(self, test_case: EnduranceTestCase) -> None:
        """Add a test case to the runner."""
        self.test_cases.append(test_case)
    
    def run_test(self, scheduler: BaseScheduler, test_case: EnduranceTestCase) -> EnduranceTestResult:
        """Run a single test case against a scheduler."""
        start_time = time.time()
        
        # Set up managers
        task_manager = EnduranceTaskManager()
        resource_manager = EnduranceResourceManager()
        
        for task in test_case.tasks:
            task_manager.add_task(task)
        
        for resource in test_case.resources:
            resource_manager.add_resource(resource)
        
        scheduler.set_managers(task_manager, resource_manager)
        
        # Run the scheduler
        schedule_result = scheduler.schedule(test_case.tasks, test_case.resources)
        
        solve_time = time.time() - start_time
        
        return EnduranceTestResult(test_case, schedule_result, solve_time)
    
    def run_all_tests(self, scheduler: BaseScheduler) -> List[EnduranceTestResult]:
        """Run all test cases against a scheduler."""
        results = []
        
        for test_case in self.test_cases:
            result = self.run_test(scheduler, test_case)
            results.append(result)
        
        self.results = results
        return results
    
    def generate_report(self) -> str:
        """Generate a test report."""
        if not self.results:
            return "No test results available."
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("🧪 Endurance Scheduler Test Report")
        report.append("=" * 50)
        report.append(f"Total tests: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success rate: {passed_tests/total_tests:.2%}")
        report.append("")
        
        # Detailed results
        report.append("Detailed Results:")
        report.append("-" * 30)
        
        for result in self.results:
            status = "✅" if result.passed else "❌"
            report.append(f"{status} {result.test_case.name}")
            report.append(f"   {result.message}")
            report.append(f"   Scheduled: {result.schedule_result.total_scheduled_tasks}/{len(result.test_case.tasks)}")
            report.append("")
        
        return "\n".join(report)


class EnduranceTestCaseBuilder:
    """Builder for creating test cases."""
    
    @staticmethod
    def create_simple_test() -> EnduranceTestCase:
        """Create a simple test case with basic tasks."""
        test_case = EnduranceTestCase(
            name="Simple Test",
            description="Basic test with 3 independent tasks"
        )
        
        base_time = datetime.now()
        
        # Create 3 simple tasks
        for i in range(3):
            task = EnduranceTask.create(
                name=f"Task {i+1}",
                description=f"Simple task {i+1}",
                start_time=base_time + timedelta(minutes=i*30),
                end_time=base_time + timedelta(hours=1, minutes=i*30),
                min_duration=timedelta(minutes=5),
                max_duration=timedelta(minutes=15),
                preferred_duration=timedelta(minutes=10),
                priority=i+1
            )
            test_case.add_task(task)
        
        # Create basic resources
        gripper = EnduranceResource.create_integer_resource(
            name="Gripper",
            description="Robot gripper",
            max_capacity=1.0
        )
        test_case.add_resource(gripper)
        
        battery = EnduranceResource.create_cumulative_rate_resource(
            name="Battery",
            description="Robot battery",
            initial_value=100.0,
            min_value=0.0,
            max_value=100.0
        )
        test_case.add_resource(battery)
        
        test_case.set_expectations(min_success_rate=1.0, max_solve_time=1.0)
        
        return test_case
    
    @staticmethod
    def create_dependency_test() -> EnduranceTestCase:
        """Create a test case with task dependencies."""
        test_case = EnduranceTestCase(
            name="Dependency Test",
            description="Test with task dependencies"
        )
        
        base_time = datetime.now()
        
        # Create a chain of dependent tasks
        tasks = []
        for i in range(4):
            task = EnduranceTask.create(
                name=f"Chain Task {i+1}",
                description=f"Task {i+1} in dependency chain",
                start_time=base_time + timedelta(minutes=i*20),
                end_time=base_time + timedelta(hours=2, minutes=i*20),
                min_duration=timedelta(minutes=10),
                max_duration=timedelta(minutes=30),
                preferred_duration=timedelta(minutes=20),
                priority=i+1
            )
            
            # Add dependency on previous task
            if i > 0:
                task.add_task_constraint(
                    TaskConstraintType.START_AFTER_END,
                    tasks[i-1].id
                )
            
            tasks.append(task)
            test_case.add_task(task)
        
        # Create resources
        gripper = EnduranceResource.create_integer_resource(
            name="Gripper",
            description="Robot gripper",
            max_capacity=1.0
        )
        test_case.add_resource(gripper)
        
        test_case.set_expectations(min_success_rate=1.0, max_solve_time=2.0)
        
        return test_case
    
    @staticmethod
    def create_resource_constrained_test() -> EnduranceTestCase:
        """Create a test case with resource constraints."""
        test_case = EnduranceTestCase(
            name="Resource Constrained Test",
            description="Test with resource constraints"
        )
        
        base_time = datetime.now()
        
        # Create tasks that compete for the same resource
        for i in range(3):
            task = EnduranceTask.create(
                name=f"Resource Task {i+1}",
                description=f"Task {i+1} requiring gripper",
                start_time=base_time + timedelta(minutes=i*10),
                end_time=base_time + timedelta(hours=1, minutes=i*10),
                min_duration=timedelta(minutes=5),
                max_duration=timedelta(minutes=15),
                preferred_duration=timedelta(minutes=10),
                priority=i+1
            )
            
            # All tasks require the same resource
            task.add_resource_constraint(
                resource_id="gripper_001",
                min_amount=1.0,
                max_amount=1.0
            )
            
            test_case.add_task(task)
        
        # Create the constrained resource
        gripper = EnduranceResource.create_integer_resource(
            name="Gripper",
            description="Robot gripper (limited capacity)",
            max_capacity=1.0
        )
        gripper.id = "gripper_001"  # Set specific ID for constraints
        test_case.add_resource(gripper)
        
        test_case.set_expectations(min_success_rate=0.33, max_solve_time=1.0)  # Only 1/3 can be scheduled
        
        return test_case
    
    @staticmethod
    def create_stress_test(num_tasks: int = 10, num_robots: int = 1) -> EnduranceTestCase:
        """Create a stress test with many tasks."""
        test_case = EnduranceTestCase(
            name=f"Stress Test ({num_tasks} tasks)",
            description=f"Stress test with {num_tasks} tasks"
        )
        
        base_time = datetime.now()
        
        # Create many tasks
        for i in range(num_tasks):
            task = EnduranceTask.create(
                name=f"Stress Task {i+1}",
                description=f"Task {i+1} for stress testing",
                start_time=base_time + timedelta(minutes=i*5),
                end_time=base_time + timedelta(hours=2, minutes=i*5),
                min_duration=timedelta(minutes=2),
                max_duration=timedelta(minutes=10),
                preferred_duration=timedelta(minutes=5),
                priority=(i % 3) + 1  # Vary priorities
            )
            test_case.add_task(task)
        
        # Create resources
        for i in range(num_robots):
            gripper = EnduranceResource.create_integer_resource(
                name=f"Gripper {i+1}",
                description=f"Robot gripper {i+1}",
                max_capacity=1.0
            )
            test_case.add_resource(gripper)
        
        test_case.set_expectations(min_success_rate=0.5, max_solve_time=5.0)
        
        return test_case
