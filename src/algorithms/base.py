"""
Base classes for Endurance scheduling algorithms.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..common.tasks.endurance_task import EnduranceTask
from ..common.tasks.endurance_task_manager import EnduranceTaskManager
from ..common.resources.endurance_resource import EnduranceResource
from ..common.resources.endurance_resource_manager import EnduranceResourceManager


class ScheduleStatus(Enum):
    """Status of a scheduling operation."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"


@dataclass
class EnduranceScheduledTask:
    """A task that has been scheduled for the Endurance robot."""
    
    task_id: str
    start_time: datetime
    end_time: datetime
    duration: timedelta
    resource_allocations: Dict[str, float] = field(default_factory=dict)
    resource_impacts: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate scheduled task after initialization."""
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        
        calculated_duration = self.end_time - self.start_time
        if abs(calculated_duration.total_seconds() - self.duration.total_seconds()) > 1.0:
            raise ValueError("duration must match end_time - start_time")
    
    @property
    def actual_duration(self) -> timedelta:
        """Get the actual duration of the scheduled task."""
        return self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_id": self.task_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration.total_seconds(),
            "resource_allocations": self.resource_allocations,
            "resource_impacts": self.resource_impacts,
            "priority": self.priority,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnduranceScheduledTask":
        """Create from dictionary representation."""
        return cls(
            task_id=data["task_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            duration=timedelta(seconds=data["duration"]),
            resource_allocations=data.get("resource_allocations", {}),
            resource_impacts=data.get("resource_impacts", {}),
            priority=data.get("priority", 1),
            metadata=data.get("metadata", {})
        )


@dataclass
class EnduranceScheduleResult:
    """Result of a scheduling operation for the Endurance robot."""
    
    status: ScheduleStatus
    schedule: List[EnduranceScheduledTask] = field(default_factory=list)
    unscheduled_tasks: List[str] = field(default_factory=list)
    solve_time: float = 0.0
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_successful(self) -> bool:
        """Check if the scheduling was successful."""
        return self.status == ScheduleStatus.SUCCESS
    
    @property
    def is_partial_success(self) -> bool:
        """Check if the scheduling was partially successful."""
        return self.status == ScheduleStatus.PARTIAL
    
    @property
    def total_scheduled_tasks(self) -> int:
        """Get the total number of scheduled tasks."""
        return len(self.schedule)
    
    @property
    def total_unscheduled_tasks(self) -> int:
        """Get the total number of unscheduled tasks."""
        return len(self.unscheduled_tasks)
    
    @property
    def total_tasks(self) -> int:
        """Get the total number of tasks (scheduled + unscheduled)."""
        return self.total_scheduled_tasks + self.total_unscheduled_tasks
    
    @property
    def success_rate(self) -> float:
        """Get the success rate of scheduling (0.0 to 1.0)."""
        if self.total_tasks == 0:
            return 0.0
        return self.total_scheduled_tasks / self.total_tasks
    
    def get_schedule_duration(self) -> timedelta:
        """Get the total duration of the schedule."""
        if not self.schedule:
            return timedelta(0)
        
        start_times = [task.start_time for task in self.schedule]
        end_times = [task.end_time for task in self.schedule]
        
        return max(end_times) - min(start_times)
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """Get resource utilization across the entire schedule."""
        resource_usage: Dict[str, float] = {}
        total_time = self.get_schedule_duration().total_seconds()
        
        if total_time == 0:
            return resource_usage
        
        for task in self.schedule:
            task_duration = task.duration.total_seconds()
            for resource_id, amount in task.resource_allocations.items():
                if resource_id not in resource_usage:
                    resource_usage[resource_id] = 0.0
                resource_usage[resource_id] += amount * task_duration
        
        # Normalize by total time
        for resource_id in resource_usage:
            resource_usage[resource_id] /= total_time
        
        return resource_usage
    
    def get_task_by_id(self, task_id: str) -> Optional[EnduranceScheduledTask]:
        """Get a scheduled task by ID."""
        for task in self.schedule:
            if task.task_id == task_id:
                return task
        return None
    
    def get_tasks_in_time_window(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[EnduranceScheduledTask]:
        """Get all tasks that overlap with the given time window."""
        overlapping_tasks = []
        for task in self.schedule:
            if (task.start_time < end_time and task.end_time > start_time):
                overlapping_tasks.append(task)
        return overlapping_tasks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "status": self.status.value,
            "schedule": [task.to_dict() for task in self.schedule],
            "unscheduled_tasks": self.unscheduled_tasks,
            "solve_time": self.solve_time,
            "message": self.message,
            "metadata": self.metadata,
            "statistics": {
                "total_scheduled_tasks": self.total_scheduled_tasks,
                "total_unscheduled_tasks": self.total_unscheduled_tasks,
                "success_rate": self.success_rate,
                "schedule_duration_seconds": self.get_schedule_duration().total_seconds(),
                "resource_utilization": self.get_resource_utilization()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnduranceScheduleResult":
        """Create from dictionary representation."""
        return cls(
            status=ScheduleStatus(data["status"]),
            schedule=[EnduranceScheduledTask.from_dict(task_data)
                     for task_data in data.get("schedule", [])],
            unscheduled_tasks=data.get("unscheduled_tasks", []),
            solve_time=data.get("solve_time", 0.0),
            message=data.get("message", ""),
            metadata=data.get("metadata", {})
        )


class BaseScheduler(ABC):
    """Base class for all Endurance robot scheduling algorithms."""
    
    def __init__(self, name: str, time_limit: float = 300.0):
        self.name = name
        self.time_limit = time_limit
        self.task_manager: Optional[EnduranceTaskManager] = None
        self.resource_manager: Optional[EnduranceResourceManager] = None
    
    def set_managers(
        self,
        task_manager: EnduranceTaskManager,
        resource_manager: EnduranceResourceManager
    ) -> None:
        """Set the task and resource managers."""
        self.task_manager = task_manager
        self.resource_manager = resource_manager
    
    @abstractmethod
    def schedule(
        self,
        tasks: List[EnduranceTask],
        resources: List[EnduranceResource]
    ) -> EnduranceScheduleResult:
        """
        Schedule tasks for the Endurance robot.
        
        Args:
            tasks: List of tasks to schedule
            resources: List of available resources
            
        Returns:
            EnduranceScheduleResult with the scheduling outcome
        """
        pass
    
    def validate_inputs(
        self,
        tasks: List[EnduranceTask],
        resources: List[EnduranceResource]
    ) -> List[str]:
        """Validate input tasks and resources."""
        errors = []
        
        if not tasks:
            errors.append("No tasks provided")
        
        if not resources:
            errors.append("No resources provided")
        
        # Validate individual tasks
        for task in tasks:
            try:
                # Check if task has valid time constraints
                if task.start_time >= task.end_time:
                    errors.append(f"Task {task.id} has invalid time window")
                
                # Check if task has valid duration constraints
                if task.min_duration > task.max_duration:
                    errors.append(f"Task {task.id} has invalid duration constraints")
                
                # Check if preferred duration is within bounds
                if not (task.min_duration <= task.preferred_duration <= task.max_duration):
                    errors.append(f"Task {task.id} preferred duration out of bounds")
                
                # Check if max duration fits in time window
                max_possible_duration = task.end_time - task.start_time
                if task.max_duration > max_possible_duration:
                    errors.append(f"Task {task.id} max duration exceeds time window")
                
            except Exception as e:
                errors.append(f"Error validating task {task.id}: {str(e)}")
        
        # Validate individual resources
        for resource in resources:
            try:
                if resource.resource_type.value == "integer" and resource.max_capacity is None:
                    errors.append(f"Integer resource {resource.id} missing max_capacity")
                
                if resource.resource_type.value == "cumulative_rate" and resource.initial_value is None:
                    errors.append(f"Cumulative rate resource {resource.id} missing initial_value")
                
            except Exception as e:
                errors.append(f"Error validating resource {resource.id}: {str(e)}")
        
        return errors
    
    def create_schedule_result(
        self,
        status: ScheduleStatus,
        schedule: List[EnduranceScheduledTask] = None,
        unscheduled_tasks: List[str] = None,
        solve_time: float = 0.0,
        message: str = "",
        metadata: Dict[str, Any] = None
    ) -> EnduranceScheduleResult:
        """Create a schedule result object."""
        if schedule is None:
            schedule = []
        if unscheduled_tasks is None:
            unscheduled_tasks = []
        if metadata is None:
            metadata = {}
        
        return EnduranceScheduleResult(
            status=status,
            schedule=schedule,
            unscheduled_tasks=unscheduled_tasks,
            solve_time=solve_time,
            message=message,
            metadata=metadata
        )
    
    def get_scheduler_info(self) -> Dict[str, Any]:
        """Get information about this scheduler."""
        return {
            "name": self.name,
            "time_limit": self.time_limit,
            "type": self.__class__.__name__
        }
    
    def check_task_constraints(
        self,
        task: EnduranceTask,
        scheduled_tasks: List[EnduranceScheduledTask]
    ) -> List[str]:
        """Check if a task's constraints can be satisfied."""
        errors = []
        
        for constraint in task.task_constraints:
            if constraint.constraint_type.value == "start_after_end":
                # Find the target task in scheduled tasks
                target_task = None
                for scheduled in scheduled_tasks:
                    if scheduled.task_id == constraint.target_task_id:
                        target_task = scheduled
                        break
                
                if not target_task:
                    errors.append(f"Task {task.id} depends on unscheduled task {constraint.target_task_id}")
                    continue
                
                # Check if this task can start after the target task ends
                if task.start_time < target_task.end_time:
                    errors.append(f"Task {task.id} cannot start after task {constraint.target_task_id} ends")
            
            elif constraint.constraint_type.value == "contained":
                # Find the target task in scheduled tasks
                target_task = None
                for scheduled in scheduled_tasks:
                    if scheduled.task_id == constraint.target_task_id:
                        target_task = scheduled
                        break
                
                if not target_task:
                    errors.append(f"Task {task.id} depends on unscheduled task {constraint.target_task_id}")
                    continue
                
                # Check if this task is contained within the target task
                if (task.start_time < target_task.start_time or 
                    task.end_time > target_task.end_time):
                    errors.append(f"Task {task.id} is not contained within task {constraint.target_task_id}")
        
        return errors
    
    def check_resource_constraints(
        self,
        task: EnduranceTask,
        scheduled_tasks: List[EnduranceScheduledTask]
    ) -> List[str]:
        """Check if a task's resource constraints can be satisfied."""
        errors = []
        
        if not self.resource_manager:
            return errors
        
        # Calculate current resource usage
        current_usage = {}
        for scheduled in scheduled_tasks:
            for resource_id, amount in scheduled.resource_allocations.items():
                if resource_id not in current_usage:
                    current_usage[resource_id] = 0.0
                current_usage[resource_id] += amount
        
        # Check each resource constraint
        for constraint in task.resource_constraints:
            resource_id = constraint.resource_id
            resource = self.resource_manager.get_resource(resource_id)
            
            if not resource:
                errors.append(f"Resource {resource_id} not found")
                continue
            
            # Check if resource can provide the required amount
            available = resource.available_capacity - current_usage.get(resource_id, 0.0)
            
            if constraint.min_amount > available:
                errors.append(f"Resource {resource_id} cannot provide "
                             f"minimum amount {constraint.min_amount}")
            
            if constraint.max_amount > resource.max_capacity:
                errors.append(f"Resource {resource_id} max amount "
                             f"{constraint.max_amount} exceeds capacity")
        
        return errors
