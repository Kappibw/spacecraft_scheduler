# Scheduler Scheduler - Complete Usage Guide

This guide explains how to use the consolidated Scheduler scheduler codebase to add tasks, create tests, and iterate on algorithms.

## Architecture

The codebase defines the objects necessary for simulating spacecraft task scheduling:

### Core Models
- **`SchedulerTask`**: Represents tasks with time windows, duration ranges, and constraints
- **`SchedulerResource`**: Represents resources (integer or cumulative rate types)
- **`SchedulerScheduledTask`**: Represents a scheduled task with start/end times
- **`SchedulerScheduleResult`**: Contains the result of a scheduling operation

### Managers
- **`SchedulerTaskManager`**: Manages tasks and their relationships
- **`SchedulerResourceManager`**: Manages resources and their state

### Algorithms
- **`BaseScheduler`**: Single base class for all scheduling algorithms
- **`SchedulerSimpleScheduler`**: Simple priority-based scheduler
- **`MILPScheduler`**: MILP-based scheduler using Gurobi

### Testing Framework
- **`SchedulerTestCase`**: Represents a test case
- **`SchedulerTestRunner`**: Runs test cases against schedulers
- **`SchedulerTestCaseBuilder`**: Helper for creating test cases

## Quick Start

### 1. Run Algorithm Comparison
```bash
python scheduler.py
```
This compares different scheduling algorithms on various test cases.

### 2. Run Comprehensive Example
```bash
python scheduler_example.py
```
This shows a complete example with testing and algorithm iteration.

### 3. Check Gurobi Installed and Licensed
```bash
python test_gurobi_integration.py
```

## Creating Tasks

### Basic Task Creation

```python
from datetime import datetime, timedelta
from src.common.tasks.task import SchedulerTask

# Create a task with time window and duration range
task = SchedulerTask.create(
    name="Pick up object",
    description="Pick up object from location A",
    start_time=datetime.now(),
    end_time=datetime.now() + timedelta(hours=1),
    min_duration=timedelta(minutes=2),
    max_duration=timedelta(minutes=5),
    preferred_duration=timedelta(minutes=3),
    priority=1  # 1 = highest priority
)
```

### Adding Task Constraints

```python
from src.common.tasks.task import TaskConstraintType

# Task must start after another task ends
task.add_task_constraint(
    TaskConstraintType.START_AFTER_END,
    other_task_id
)

# Task must be contained within another task's duration
task.add_task_constraint(
    TaskConstraintType.CONTAINED,
    other_task_id
)
```

### Adding Resource Constraints

```python
# Task requires specific amount of a resource
task.add_resource_constraint(
    resource_id="gripper_001",
    min_amount=1.0,  # Must use at least 1 unit
    max_amount=1.0   # Can use at most 1 unit
)
```

### Adding Resource Impacts

```python
from src.common.tasks.task import ResourceImpactType

# Task changes resource consumption rate
task.add_resource_impact(
    resource_id="battery_001",
    impact_type=ResourceImpactType.RATE_CHANGE,
    impact_value=2.0  # Doubles consumption rate
)

# Task marks resource as in use
task.add_resource_impact(
    resource_id="gripper_001",
    impact_type=ResourceImpactType.SET_IN_USE,
    impact_value=True
)
```

## Creating Resources

### Integer Resources (Discrete Capacity)

```python
from src.common.resources.resource import SchedulerResource

# Create a gripper that can hold 1 object
gripper = SchedulerResource.create_integer_resource(
    name="Gripper",
    description="Robot gripper for picking up objects",
    max_capacity=1.0
)

# Create storage that can hold 3 objects
storage = SchedulerResource.create_integer_resource(
    name="Storage Bay",
    description="Storage bay for carrying objects",
    max_capacity=3.0
)
```

### Cumulative Rate Resources (Continuous with Rate Changes)

```python
# Create a battery that starts at 100% and drains over time
battery = SchedulerResource.create_cumulative_rate_resource(
    name="Battery",
    description="Robot battery power",
    initial_value=100.0,
    min_value=0.0,
    max_value=100.0
)

# Create a fuel tank that can be refilled
fuel = SchedulerResource.create_cumulative_rate_resource(
    name="Fuel Tank",
    description="Robot fuel tank",
    initial_value=50.0,
    min_value=0.0,
    max_value=100.0
)
```

## Creating Scheduling Algorithms

### Basic Algorithm Structure

```python
from src.algorithms.base import BaseScheduler, SchedulerScheduleResult, ScheduleStatus

class MySchedulerScheduler(BaseScheduler):
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
```

### Using the Algorithm

```python
# Create and configure scheduler
scheduler = MySchedulerScheduler(time_limit=60)

# Set managers (optional, for advanced features)
scheduler.set_managers(task_manager, resource_manager)

# Run scheduling
result = scheduler.schedule(tasks, resources)

# Analyze results
print(f"Success rate: {result.success_rate:.1%}")
print(f"Scheduled: {result.total_scheduled_tasks} tasks")
print(f"Unscheduled: {result.total_unscheduled_tasks} tasks")
```

## Testing Your Algorithms

### Using the Test Framework

```python
from src.testing.test_framework import SchedulerTestRunner, SchedulerTestCaseBuilder

# Create test runner
test_runner = SchedulerTestRunner()

# Add test cases
test_runner.add_test_case(SchedulerTestCaseBuilder.create_simple_test())
test_runner.add_test_case(SchedulerTestCaseBuilder.create_dependency_test())
test_runner.add_test_case(SchedulerTestCaseBuilder.create_resource_constrained_test())
test_runner.add_test_case(SchedulerTestCaseBuilder.create_stress_test(num_tasks=10))

# Test your algorithm
scheduler = MySchedulerScheduler()
results = test_runner.run_all_tests(scheduler)

# Generate report
report = test_runner.generate_report()
print(report)
```

### Creating Custom Test Cases

```python
from src.testing.test_framework import SchedulerTestCase

# Create custom test case
custom_test = SchedulerTestCase(
    name="My Custom Test",
    description="Test case for my specific scenario",
    tasks=my_tasks,
    resources=my_resources,
    expected_success_rate=0.8,
    max_solve_time=30.0
)

# Add to test runner
test_runner.add_test_case(custom_test)
```
