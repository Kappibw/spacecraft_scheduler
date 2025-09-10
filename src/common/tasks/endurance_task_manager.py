"""
Endurance Task Manager for handling EnduranceTask objects.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from .endurance_task import EnduranceTask, TaskConstraintType, TaskStatus


class EnduranceTaskManager:
    """Manages EnduranceTask objects and their relationships."""
    
    def __init__(self):
        self.tasks: Dict[str, EnduranceTask] = {}
        self.task_dependencies: Dict[str, Set[str]] = {}  # task_id -> set of dependent task IDs
    
    def add_task(self, task: EnduranceTask) -> None:
        """Add a task to the manager."""
        self.tasks[task.id] = task
        self._update_dependencies(task)
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the manager."""
        if task_id in self.tasks:
            # Remove from dependencies
            if task_id in self.task_dependencies:
                del self.task_dependencies[task_id]
            
            # Remove from other tasks' dependencies
            for deps in self.task_dependencies.values():
                deps.discard(task_id)
            
            del self.tasks[task_id]
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[EnduranceTask]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[EnduranceTask]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[EnduranceTask]:
        """Get all tasks with a specific status."""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_pending_tasks(self) -> List[EnduranceTask]:
        """Get all pending tasks."""
        return self.get_tasks_by_status(TaskStatus.PENDING)
    
    def get_scheduled_tasks(self) -> List[EnduranceTask]:
        """Get all scheduled tasks."""
        return self.get_tasks_by_status(TaskStatus.SCHEDULED)
    
    def _update_dependencies(self, task: EnduranceTask) -> None:
        """Update dependency relationships based on task constraints."""
        # Clear existing dependencies for this task
        if task.id in self.task_dependencies:
            del self.task_dependencies[task.id]
        
        # Add new dependencies based on constraints
        dependencies = set()
        for constraint in task.task_constraints:
            if constraint.constraint_type == TaskConstraintType.START_AFTER_END:
                dependencies.add(constraint.target_task_id)
            elif constraint.constraint_type == TaskConstraintType.CONTAINED:
                dependencies.add(constraint.target_task_id)
        
        if dependencies:
            self.task_dependencies[task.id] = dependencies
    
    def get_dependencies(self, task_id: str) -> Set[str]:
        """Get all tasks that the given task depends on."""
        return self.task_dependencies.get(task_id, set())
    
    def get_dependents(self, task_id: str) -> Set[str]:
        """Get all tasks that depend on the given task."""
        dependents = set()
        for dependent_id, deps in self.task_dependencies.items():
            if task_id in deps:
                dependents.add(dependent_id)
        return dependents
    
    def can_schedule_task(self, task_id: str, scheduled_tasks: Set[str]) -> bool:
        """Check if a task can be scheduled given currently scheduled tasks."""
        if task_id not in self.tasks:
            return False

        dependencies = self.get_dependencies(task_id)

        # Check if all dependencies are scheduled
        return dependencies.issubset(scheduled_tasks)
    
    def get_schedulable_tasks(self, scheduled_tasks: Set[str]) -> List[EnduranceTask]:
        """Get all tasks that can be scheduled given currently scheduled tasks."""
        schedulable = []
        for task in self.get_pending_tasks():
            if self.can_schedule_task(task.id, scheduled_tasks):
                schedulable.append(task)
        return schedulable
    
    def validate_task_constraints(self, task_id: str) -> List[str]:
        """Validate that all task constraints are satisfied."""
        if task_id not in self.tasks:
            return [f"Task {task_id} not found"]
        
        task = self.tasks[task_id]
        errors = []
        
        for constraint in task.task_constraints:
            target_task = self.get_task(constraint.target_task_id)
            if not target_task:
                errors.append(f"Constraint target task {constraint.target_task_id} not found")
                continue
            
            if constraint.constraint_type == TaskConstraintType.START_AFTER_END:
                # This constraint will be validated during scheduling
                pass
            elif constraint.constraint_type == TaskConstraintType.CONTAINED:
                # This constraint will be validated during scheduling
                pass
        
        return errors
    
    def get_tasks_in_time_window(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[EnduranceTask]:
        """Get all tasks that overlap with the given time window."""
        overlapping_tasks = []
        for task in self.tasks.values():
            # Check if task's time window overlaps with the given window
            if (task.start_time < end_time and task.end_time > start_time):
                overlapping_tasks.append(task)
        return overlapping_tasks
    
    def get_tasks_by_priority(self) -> List[EnduranceTask]:
        """Get all tasks sorted by priority (1 = highest)."""
        return sorted(self.tasks.values(), key=lambda t: t.priority)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update the status of a task."""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            return True
        return False
    
    def get_task_statistics(self) -> Dict[str, int]:
        """Get statistics about tasks in the manager."""
        stats = {}
        for status in TaskStatus:
            stats[status.value] = len(self.get_tasks_by_status(status))
        return stats
    
    def clear(self) -> None:
        """Clear all tasks from the manager."""
        self.tasks.clear()
        self.task_dependencies.clear()
