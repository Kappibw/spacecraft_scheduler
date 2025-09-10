"""
Task definitions for robot scheduling.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid


class TaskType(Enum):
    """Types of tasks a robot can perform."""
    PICKUP = "pickup"
    DELIVERY = "delivery"
    INSPECTION = "inspection"
    MAINTENANCE = "maintenance"
    TRANSPORT = "transport"
    ASSEMBLY = "assembly"


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a task to be scheduled for a robot."""
    
    id: str
    task_type: TaskType
    description: str
    duration: timedelta
    priority: int = 1  # 1 = highest priority
    required_resources: Dict[str, Any] = None
    constraints: Dict[str, Any] = None
    dependencies: List[str] = None
    location: Optional[str] = None
    deadline: Optional[datetime] = None
    created_at: datetime = None
    status: TaskStatus = TaskStatus.PENDING
    
    def __post_init__(self):
        if self.required_resources is None:
            self.required_resources = {}
        if self.constraints is None:
            self.constraints = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @classmethod
    def create(
        cls,
        task_type: TaskType,
        description: str,
        duration: timedelta,
        **kwargs
    ) -> "Task":
        """Create a new task with a generated ID."""
        return cls(
            id=str(uuid.uuid4()),
            task_type=task_type,
            description=description,
            duration=duration,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "task_type": self.task_type.value,
            "description": self.description,
            "duration": self.duration.total_seconds(),
            "priority": self.priority,
            "required_resources": self.required_resources,
            "constraints": self.constraints,
            "dependencies": self.dependencies,
            "location": self.location,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary representation."""
        return cls(
            id=data["id"],
            task_type=TaskType(data["task_type"]),
            description=data["description"],
            duration=timedelta(seconds=data["duration"]),
            priority=data.get("priority", 1),
            required_resources=data.get("required_resources", {}),
            constraints=data.get("constraints", {}),
            dependencies=data.get("dependencies", []),
            location=data.get("location"),
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            status=TaskStatus(data["status"])
        )
