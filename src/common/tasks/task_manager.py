"""
Task management functionality for robot scheduling.
"""

from typing import List, Dict, Optional, Set
from datetime import datetime
from .task import Task, TaskStatus, TaskType


class TaskManager:
    """Manages tasks for robot scheduling."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []  # Ordered list of task IDs
    
    def add_task(self, task: Task) -> None:
        """Add a task to the manager."""
        self.tasks[task.id] = task
        if task.status == TaskStatus.PENDING:
            self._insert_into_queue(task)
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the manager."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return [task for task in self.tasks.values() 
                if task.status == TaskStatus.PENDING]
    
    def get_tasks_by_type(self, task_type: TaskType) -> List[Task]:
        """Get all tasks of a specific type."""
        return [task for task in self.tasks.values() 
                if task.task_type == task_type]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [task for task in self.tasks.values() 
                if task.status == status]
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update the status of a task."""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            if status == TaskStatus.PENDING and task_id not in self.task_queue:
                self._insert_into_queue(self.tasks[task_id])
            elif status != TaskStatus.PENDING and task_id in self.task_queue:
                self.task_queue.remove(task_id)
            return True
        return False
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next task in the queue."""
        if self.task_queue:
            task_id = self.task_queue[0]
            return self.tasks.get(task_id)
        return None
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to be scheduled (no unmet dependencies)."""
        ready_tasks = []
        for task in self.get_pending_tasks():
            if self._are_dependencies_met(task):
                ready_tasks.append(task)
        return ready_tasks
    
    def _are_dependencies_met(self, task: Task) -> bool:
        """Check if all dependencies for a task are completed."""
        for dep_id in task.dependencies:
            dep_task = self.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _insert_into_queue(self, task: Task) -> None:
        """Insert a task into the queue maintaining priority order."""
        if task.id in self.task_queue:
            return
        
        # Insert based on priority (higher priority = lower number)
        insert_index = 0
        for i, queued_task_id in enumerate(self.task_queue):
            queued_task = self.tasks[queued_task_id]
            if task.priority < queued_task.priority:
                insert_index = i
                break
            elif task.priority == queued_task.priority:
                # Same priority, maintain FIFO order
                continue
            else:
                insert_index = i + 1
        
        self.task_queue.insert(insert_index, task.id)
    
    def get_task_statistics(self) -> Dict[str, int]:
        """Get statistics about tasks."""
        stats = {
            "total": len(self.tasks),
            "pending": 0,
            "assigned": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        
        for task in self.tasks.values():
            stats[task.status.value] += 1
        
        return stats
