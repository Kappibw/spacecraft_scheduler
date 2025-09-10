"""
Test case definitions for algorithm evaluation.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from src.common.tasks import Task, TaskType
from src.common.resources import Resource, ResourceType


@dataclass
class TestCase:
    """Represents a test case for algorithm evaluation."""
    
    name: str
    description: str
    tasks: List[Task]
    resources: List[Resource]
    constraints: Dict[str, Any]
    expected_makespan: Optional[float] = None
    expected_objective: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test case to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
            "resources": [resource.to_dict() for resource in self.resources],
            "constraints": self.constraints,
            "expected_makespan": self.expected_makespan,
            "expected_objective": self.expected_objective,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """Create test case from dictionary."""
        tasks = [Task.from_dict(task_data) for task_data in data["tasks"]]
        resources = [Resource.from_dict(resource_data) for resource_data in data["resources"]]
        
        return cls(
            name=data["name"],
            description=data["description"],
            tasks=tasks,
            resources=resources,
            constraints=data.get("constraints", {}),
            expected_makespan=data.get("expected_makespan"),
            expected_objective=data.get("expected_objective"),
            metadata=data.get("metadata", {})
        )
    
    def save(self, filepath: str) -> None:
        """Save test case to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> "TestCase":
        """Load test case from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class TestCaseLoader:
    """Loads and manages test cases."""
    
    @staticmethod
    def create_simple_test() -> TestCase:
        """Create a simple test case with 3 tasks and 2 robots."""
        tasks = [
            Task.create(
                task_type=TaskType.PICKUP,
                description="Pick up package A",
                duration=timedelta(minutes=10),
                priority=1,
                location="warehouse_a"
            ),
            Task.create(
                task_type=TaskType.DELIVERY,
                description="Deliver package A",
                duration=timedelta(minutes=15),
                priority=2,
                location="location_b"
            ),
            Task.create(
                task_type=TaskType.INSPECTION,
                description="Inspect equipment",
                duration=timedelta(minutes=5),
                priority=3,
                location="zone_c"
            )
        ]
        
        resources = [
            Resource.create(
                resource_type=ResourceType.ROBOT,
                name="Robot-001",
                capacity=1.0,
                capabilities=["pickup", "delivery", "inspection"],
                location="warehouse"
            ),
            Resource.create(
                resource_type=ResourceType.ROBOT,
                name="Robot-002",
                capacity=1.0,
                capabilities=["pickup", "delivery", "inspection"],
                location="warehouse"
            )
        ]
        
        return TestCase(
            name="simple_3task_2robot",
            description="Simple test case with 3 tasks and 2 robots",
            tasks=tasks,
            resources=resources,
            constraints={"max_makespan": 60, "objective": "minimize_makespan"},
            expected_makespan=30.0
        )
    
    @staticmethod
    def create_complex_test() -> TestCase:
        """Create a complex test case with dependencies and constraints."""
        # Create tasks with dependencies
        task1 = Task.create(
            task_type=TaskType.PICKUP,
            description="Pick up raw materials",
            duration=timedelta(minutes=20),
            priority=1,
            location="warehouse"
        )
        
        task2 = Task.create(
            task_type=TaskType.TRANSPORT,
            description="Transport materials to production",
            duration=timedelta(minutes=15),
            priority=2,
            dependencies=[task1.id],
            location="production_floor"
        )
        
        task3 = Task.create(
            task_type=TaskType.ASSEMBLY,
            description="Assemble product",
            duration=timedelta(minutes=30),
            priority=2,
            dependencies=[task2.id],
            location="assembly_line"
        )
        
        task4 = Task.create(
            task_type=TaskType.INSPECTION,
            description="Quality inspection",
            duration=timedelta(minutes=10),
            priority=3,
            dependencies=[task3.id],
            location="quality_control"
        )
        
        task5 = Task.create(
            task_type=TaskType.DELIVERY,
            description="Deliver finished product",
            duration=timedelta(minutes=25),
            priority=1,
            dependencies=[task4.id],
            location="shipping_dock"
        )
        
        resources = [
            Resource.create(
                resource_type=ResourceType.ROBOT,
                name="Forklift-001",
                capacity=1.0,
                capabilities=["pickup", "transport"],
                location="warehouse"
            ),
            Resource.create(
                resource_type=ResourceType.ROBOT,
                name="Assembly-Bot-001",
                capacity=1.0,
                capabilities=["assembly", "inspection"],
                location="production_floor"
            ),
            Resource.create(
                resource_type=ResourceType.ROBOT,
                name="Delivery-Bot-001",
                capacity=1.0,
                capabilities=["delivery", "transport"],
                location="shipping_dock"
            )
        ]
        
        return TestCase(
            name="complex_assembly_line",
            description="Complex assembly line with dependencies",
            tasks=[task1, task2, task3, task4, task5],
            resources=resources,
            constraints={
                "max_makespan": 120,
                "objective": "minimize_makespan",
                "resource_constraints": True,
                "dependency_constraints": True
            },
            expected_makespan=100.0
        )
    
    @staticmethod
    def create_stress_test(num_tasks: int = 20, num_robots: int = 5) -> TestCase:
        """Create a stress test with many tasks and robots."""
        tasks = []
        for i in range(num_tasks):
            task_type = list(TaskType)[i % len(TaskType)]
            tasks.append(Task.create(
                task_type=task_type,
                description=f"Task {i+1}",
                duration=timedelta(minutes=5 + (i % 15)),
                priority=1 + (i % 3),
                location=f"location_{i % 10}"
            ))
        
        resources = []
        for i in range(num_robots):
            resources.append(Resource.create(
                resource_type=ResourceType.ROBOT,
                name=f"Robot-{i+1:03d}",
                capacity=1.0,
                capabilities=["pickup", "delivery", "inspection", "transport"],
                location="warehouse"
            ))
        
        return TestCase(
            name=f"stress_{num_tasks}task_{num_robots}robot",
            description=f"Stress test with {num_tasks} tasks and {num_robots} robots",
            tasks=tasks,
            resources=resources,
            constraints={
                "max_makespan": 300,
                "objective": "minimize_makespan"
            }
        )
