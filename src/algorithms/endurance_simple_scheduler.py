"""
Simple Endurance scheduler implementation for demonstration.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base import BaseScheduler, EnduranceScheduleResult, ScheduleStatus, EnduranceScheduledTask
from ..common.tasks.endurance_task import EnduranceTask
from ..common.resources.endurance_resource import EnduranceResource


class EnduranceSimpleScheduler(BaseScheduler):
    """
    Simple scheduler that schedules tasks in priority order.
    
    This is a basic implementation for demonstration purposes.
    It schedules tasks in priority order (1 = highest priority) and
    tries to fit them within their time windows.
    """
    
    def __init__(self, time_limit: float = 300.0):
        super().__init__("Simple Endurance Scheduler", time_limit)
    
    def schedule(
        self,
        tasks: List[EnduranceTask],
        resources: List[EnduranceResource]
    ) -> EnduranceScheduleResult:
        """
        Schedule tasks using a simple priority-based approach.
        
        Algorithm:
        1. Sort tasks by priority (1 = highest)
        2. For each task, try to schedule it as early as possible
        3. Check constraints and resource availability
        4. Use preferred duration when possible
        """
        start_time = datetime.now()
        
        # Validate inputs
        validation_errors = self.validate_inputs(tasks, resources)
        if validation_errors:
            return self.create_schedule_result(
                status=ScheduleStatus.FAILED,
                message=f"Validation errors: {', '.join(validation_errors)}"
            )
        
        # Sort tasks by priority (1 = highest priority)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)
        
        scheduled_tasks = []
        unscheduled_tasks = []
        current_time = datetime.now()
        
        for task in sorted_tasks:
            # Try to schedule this task
            scheduled_task = self._try_schedule_task(
                task, current_time, scheduled_tasks, resources
            )
            
            if scheduled_task:
                scheduled_tasks.append(scheduled_task)
                # Update current time to the end of this task
                current_time = max(current_time, scheduled_task.end_time)
            else:
                unscheduled_tasks.append(task.id)
        
        # Calculate solve time
        solve_time = (datetime.now() - start_time).total_seconds()
        
        # Determine status
        if not unscheduled_tasks:
            status = ScheduleStatus.SUCCESS
            message = f"Successfully scheduled all {len(scheduled_tasks)} tasks"
        elif scheduled_tasks:
            status = ScheduleStatus.PARTIAL
            message = f"Scheduled {len(scheduled_tasks)} of {len(tasks)} tasks"
        else:
            status = ScheduleStatus.FAILED
            message = "Failed to schedule any tasks"
        
        return self.create_schedule_result(
            status=status,
            schedule=scheduled_tasks,
            unscheduled_tasks=unscheduled_tasks,
            solve_time=solve_time,
            message=message
        )
    
    def _try_schedule_task(
        self,
        task: EnduranceTask,
        current_time: datetime,
        scheduled_tasks: List[Dict[str, Any]],
        resources: List[EnduranceResource]
    ) -> Dict[str, Any]:
        """Try to schedule a single task."""
        
        # Check if task can be scheduled within its time window
        if current_time > task.end_time:
            return None  # Too late to schedule
        
        # Determine start time
        start_time = max(current_time, task.start_time)
        
        # Check if we can fit the task within its time window
        available_time = task.end_time - start_time
        if available_time < task.min_duration:
            return None  # Not enough time
        
        # Use preferred duration if possible, otherwise use max duration
        if available_time >= task.preferred_duration:
            duration = task.preferred_duration
        elif available_time >= task.min_duration:
            duration = available_time
        else:
            return None  # Not enough time
        
        end_time = start_time + duration
        
        # Check task constraints
        constraint_errors = self.check_task_constraints(task, scheduled_tasks)
        if constraint_errors:
            return None  # Constraints not satisfied
        
        # Check resource constraints
        resource_errors = self.check_resource_constraints(task, scheduled_tasks)
        if resource_errors:
            return None  # Resource constraints not satisfied
        
        # Create scheduled task
        scheduled_task = EnduranceScheduledTask(
            task_id=task.id,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            priority=task.priority,
            metadata={"algorithm": "Simple"}
        )
        
        # Allocate resources (simplified - just mark as used)
        for constraint in task.resource_constraints:
            resource_id = constraint.resource_id
            amount = constraint.min_amount
            scheduled_task.resource_allocations[resource_id] = amount
        
        # Apply resource impacts (simplified)
        for impact in task.resource_impacts:
            resource_id = impact.resource_id
            scheduled_task.resource_impacts[resource_id] = {
                "impact_type": impact.impact_type,
                "impact_value": impact.impact_value
            }
        
        return scheduled_task
