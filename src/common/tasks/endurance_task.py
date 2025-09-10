"""
Endurance Task definitions for robot scheduling.
Redesigned for single robot scheduling with time windows and constraints.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid


class TaskConstraintType(Enum):
    """Types of constraints between tasks."""
    START_AFTER_END = "start_after_end"  # Must begin after another task finishes
    CONTAINED = "contained"  # Must be entirely contained within another task's duration


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskConstraint:
    """Represents a constraint between tasks."""
    constraint_type: TaskConstraintType
    target_task_id: str  # The task this constraint relates to
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceConstraint:
    """Represents a constraint on resource usage."""
    resource_id: str
    min_amount: float = 0.0
    max_amount: float = float('inf')
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceImpact:
    """Represents how a task impacts a resource."""
    resource_id: str
    impact_type: str  # e.g., "rate_change", "set_in_use", "consume", "produce"
    impact_value: float  # The amount or rate of change
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnduranceTask:
    """
    Represents a task to be scheduled for the Endurance robot.
    
    Key features:
    - Time windows (start_time, end_time)
    - Duration range (min_duration, max_duration, preferred_duration)
    - Task-to-task constraints
    - Resource constraints and impacts
    """
    
    id: str
    name: str
    description: str
    
    # Time constraints
    start_time: datetime  # Earliest possible start time
    end_time: datetime    # Latest possible end time
    min_duration: timedelta  # Minimum duration allowed
    max_duration: timedelta  # Maximum duration allowed
    preferred_duration: timedelta  # User's preferred duration
    
    # Task constraints
    task_constraints: List[TaskConstraint] = field(default_factory=list)
    
    # Resource constraints (min/max amounts this task can use)
    resource_constraints: List[ResourceConstraint] = field(default_factory=list)
    
    # Resource impacts (how this task affects resources)
    resource_impacts: List[ResourceImpact] = field(default_factory=list)
    
    # Additional metadata
    priority: int = 1  # 1 = highest priority
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate task constraints after initialization."""
        self._validate_time_constraints()
        self._validate_duration_constraints()
    
    def _validate_time_constraints(self):
        """Validate that time constraints are consistent."""
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")

        max_possible_duration = self.end_time - self.start_time
        if self.max_duration > max_possible_duration:
            raise ValueError("max_duration cannot exceed available time window")
    
    def _validate_duration_constraints(self):
        """Validate that duration constraints are consistent."""
        if self.min_duration > self.max_duration:
            raise ValueError("min_duration cannot exceed max_duration")

        if not (self.min_duration <= self.preferred_duration <= self.max_duration):
            raise ValueError("preferred_duration must be within min/max range")
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        min_duration: timedelta,
        max_duration: timedelta,
        preferred_duration: timedelta,
        **kwargs
    ) -> "EnduranceTask":
        """Create a new task with a generated ID."""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            min_duration=min_duration,
            max_duration=max_duration,
            preferred_duration=preferred_duration,
            **kwargs
        )
    
    def add_task_constraint(
        self,
        constraint_type: TaskConstraintType,
        target_task_id: str,
        **metadata
    ) -> None:
        """Add a constraint to another task."""
        constraint = TaskConstraint(
            constraint_type=constraint_type,
            target_task_id=target_task_id,
            metadata=metadata
        )
        self.task_constraints.append(constraint)
    
    def add_resource_constraint(
        self,
        resource_id: str,
        min_amount: float = 0.0,
        max_amount: float = float('inf'),
        **metadata
    ) -> None:
        """Add a constraint on resource usage."""
        constraint = ResourceConstraint(
            resource_id=resource_id,
            min_amount=min_amount,
            max_amount=max_amount,
            metadata=metadata
        )
        self.resource_constraints.append(constraint)
    
    def add_resource_impact(
        self,
        resource_id: str,
        impact_type: str,
        impact_value: float,
        **metadata
    ) -> None:
        """Add an impact on a resource."""
        impact = ResourceImpact(
            resource_id=resource_id,
            impact_type=impact_type,
            impact_value=impact_value,
            metadata=metadata
        )
        self.resource_impacts.append(impact)
    
    def get_available_duration(self) -> timedelta:
        """Get the total available duration for this task."""
        return self.end_time - self.start_time
    
    def can_schedule_with_duration(self, duration: timedelta) -> bool:
        """Check if the task can be scheduled with the given duration."""
        return self.min_duration <= duration <= self.max_duration
    
    def get_resource_constraint(self, resource_id: str) -> Optional[ResourceConstraint]:
        """Get the resource constraint for a specific resource."""
        for constraint in self.resource_constraints:
            if constraint.resource_id == resource_id:
                return constraint
        return None
    
    def get_resource_impacts(self, resource_id: str) -> List[ResourceImpact]:
        """Get all resource impacts for a specific resource."""
        return [impact for impact in self.resource_impacts
                if impact.resource_id == resource_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "min_duration": self.min_duration.total_seconds(),
            "max_duration": self.max_duration.total_seconds(),
            "preferred_duration": self.preferred_duration.total_seconds(),
            "task_constraints": [
                {
                    "constraint_type": c.constraint_type.value,
                    "target_task_id": c.target_task_id,
                    "metadata": c.metadata
                }
                for c in self.task_constraints
            ],
            "resource_constraints": [
                {
                    "resource_id": c.resource_id,
                    "min_amount": c.min_amount,
                    "max_amount": c.max_amount,
                    "metadata": c.metadata
                }
                for c in self.resource_constraints
            ],
            "resource_impacts": [
                {
                    "resource_id": i.resource_id,
                    "impact_type": i.impact_type,
                    "impact_value": i.impact_value,
                    "metadata": i.metadata
                }
                for i in self.resource_impacts
            ],
            "priority": self.priority,
            "location": self.location,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnduranceTask":
        """Create task from dictionary representation."""
        task = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            min_duration=timedelta(seconds=data["min_duration"]),
            max_duration=timedelta(seconds=data["max_duration"]),
            preferred_duration=timedelta(seconds=data["preferred_duration"]),
            priority=data.get("priority", 1),
            location=data.get("location"),
            metadata=data.get("metadata", {}),
            status=TaskStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now().isoformat()))
        )
        
        # Add task constraints
        for c_data in data.get("task_constraints", []):
            task.add_task_constraint(
                TaskConstraintType(c_data["constraint_type"]),
                c_data["target_task_id"],
                **c_data.get("metadata", {})
            )
        
        # Add resource constraints
        for c_data in data.get("resource_constraints", []):
            task.add_resource_constraint(
                c_data["resource_id"],
                c_data.get("min_amount", 0.0),
                c_data.get("max_amount", float('inf')),
                **c_data.get("metadata", {})
            )
        
        # Add resource impacts
        for i_data in data.get("resource_impacts", []):
            task.add_resource_impact(
                i_data["resource_id"],
                i_data["impact_type"],
                i_data["impact_value"],
                **i_data.get("metadata", {})
            )
        
        return task
