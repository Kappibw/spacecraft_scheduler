from src.common.tasks.task_manager import TaskManager
from src.common.resources.resource_manager import ResourceManager
from src.algorithms.base import ScheduleResult


def schedule_string_from_result(result: ScheduleResult, task_manager: TaskManager, resource_manager: ResourceManager) -> str:
    """Print the schedule to a string."""
    schedule_string = "\nSchedule:\n"
    for i, scheduled_task in enumerate(result.schedule, 1):
        # Look up task name from task manager
        task = task_manager.get_task(scheduled_task.task_id)
        task_name = task.name if task else f"Task {scheduled_task.task_id[:8]}"
        
        schedule_string += f"  {i}. {task_name}\n"
        schedule_string += f"     Start: {scheduled_task.start_time.strftime('%H:%M:%S')}\n"
        schedule_string += f"     End: {scheduled_task.end_time.strftime('%H:%M:%S')}\n"
        schedule_string += f"     Duration: {scheduled_task.duration.total_seconds()/60:.1f} min\n"
        
        # Format resource allocations with names
        resource_names = {}
        for resource_id, amount in scheduled_task.resource_allocations.items():
            resource = resource_manager.get_resource(resource_id)
            resource_name = resource.name if resource else f"Resource {resource_id[:8]}"
            resource_names[resource_name] = amount
        
        schedule_string += f"     Resources: {resource_names}\n"
        schedule_string += "\n\n"
    return schedule_string