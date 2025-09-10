"""
MILP-based scheduling algorithm for Endurance robot using the new models.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ortools.linear_solver import pywraplp

from ..base import BaseScheduler, EnduranceScheduleResult, ScheduleStatus, EnduranceScheduledTask
from ...common.tasks.endurance_task import EnduranceTask, TaskConstraintType
from ...common.resources.endurance_resource import EnduranceResource, ResourceType


class EnduranceMILPScheduler(BaseScheduler):
    """MILP scheduler for Endurance robot using the new task and resource models."""
    
    def __init__(self, time_limit: int = 300):
        super().__init__("EnduranceMILPScheduler", time_limit)
    
    def schedule(self, tasks: List[EnduranceTask], resources: List[EnduranceResource]) -> EnduranceScheduleResult:
        """
        Schedule tasks using OR-Tools MILP optimization.
        
        Args:
            tasks: List of EnduranceTask objects to schedule
            resources: List of EnduranceResource objects available
            
        Returns:
            EnduranceScheduleResult containing the schedule and metadata
        """
        start_time = datetime.now()
        
        # Validate inputs
        validation_errors = self.validate_inputs(tasks, resources)
        if validation_errors:
            return self.create_schedule_result(
                status=ScheduleStatus.FAILED,
                message=f"Validation errors: {', '.join(validation_errors)}"
            )
        
        if not tasks or not resources:
            return self.create_schedule_result(
                status=ScheduleStatus.FAILED,
                message="No tasks or resources provided"
            )
        
        try:
            # Create OR-Tools solver
            solver = pywraplp.Solver.CreateSolver('SCIP')
            if not solver:
                return self.create_schedule_result(
                    status=ScheduleStatus.FAILED,
                    message="Could not create OR-Tools solver"
                )
            
            # Set time limit
            solver.SetTimeLimit(self.time_limit * 1000)  # Convert to milliseconds
            
            # Create time horizon based on task time windows
            time_horizon = self._calculate_time_horizon(tasks)
            
            # Decision variables
            # x[i,t] = 1 if task i starts at time t
            x = {}
            for i, task in enumerate(tasks):
                for t in range(time_horizon):
                    x[i, t] = solver.IntVar(0, 1, f'x_{i}_{t}')
            
            # y[i] = start time of task i
            y = {}
            for i, task in enumerate(tasks):
                y[i] = solver.IntVar(0, time_horizon - 1, f'y_{i}')
            
            # z[i] = completion time of task i
            z = {}
            for i, task in enumerate(tasks):
                z[i] = solver.IntVar(0, time_horizon, f'z_{i}')
            
            # Makespan variable
            makespan = solver.IntVar(0, time_horizon, 'makespan')
            
            # Constraints
            # Each task must start exactly once
            for i, task in enumerate(tasks):
                constraint = solver.Constraint(1, 1)
                for t in range(time_horizon):
                    constraint.SetCoefficient(x[i, t], 1)
            
            # Task duration constraints
            for i, task in enumerate(tasks):
                # Use preferred duration for simplicity
                duration = int(task.preferred_duration.total_seconds() / 60)  # Convert to minutes
                constraint = solver.Constraint(duration, duration)
                constraint.SetCoefficient(z[i], 1)
                constraint.SetCoefficient(y[i], -1)
            
            # Time window constraints
            for i, task in enumerate(tasks):
                # Start time must be within task's time window
                start_min = int((task.start_time - datetime.now()).total_seconds() / 60)
                start_max = int((task.end_time - task.preferred_duration - datetime.now()).total_seconds() / 60)
                
                # Constraint: y[i] >= start_min
                if start_min >= 0:
                    constraint = solver.Constraint(start_min, solver.infinity())
                    constraint.SetCoefficient(y[i], 1)
                
                # Constraint: y[i] <= start_max
                if start_max >= 0:
                    constraint = solver.Constraint(-solver.infinity(), start_max)
                    constraint.SetCoefficient(y[i], 1)
            
            # Task dependency constraints
            for i, task in enumerate(tasks):
                for constraint_obj in task.task_constraints:
                    if constraint_obj.constraint_type == TaskConstraintType.START_AFTER_END:
                        # Find the target task
                        target_index = next((j for j, t in enumerate(tasks) if t.id == constraint_obj.target_task_id), None)
                        if target_index is not None:
                            # y[i] >= z[target_index]
                            constraint = solver.Constraint(0, solver.infinity())
                            constraint.SetCoefficient(y[i], 1)
                            constraint.SetCoefficient(z[target_index], -1)
            
            # Resource constraints (simplified - assume single robot)
            # Only one task can be running at a time
            for t in range(time_horizon):
                constraint = solver.Constraint(0, 1)
                for i, task in enumerate(tasks):
                    duration = int(task.preferred_duration.total_seconds() / 60)
                    for start_t in range(max(0, t - duration + 1), min(time_horizon, t + 1)):
                        if (i, start_t) in x:
                            constraint.SetCoefficient(x[i, start_t], 1)
            
            # Makespan constraint
            for i, task in enumerate(tasks):
                constraint = solver.Constraint(0, solver.infinity())
                constraint.SetCoefficient(z[i], 1)
                constraint.SetCoefficient(makespan, -1)
            
            # Objective: minimize makespan
            objective = solver.Objective()
            objective.SetCoefficient(makespan, 1)
            objective.SetMinimization()
            
            # Solve
            status = solver.Solve()
            
            end_time = datetime.now()
            solve_time = (end_time - start_time).total_seconds()
            
            if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
                # Extract solution
                schedule = self._extract_solution(x, y, z, tasks, time_horizon)
                
                return self.create_schedule_result(
                    status=ScheduleStatus.SUCCESS,
                    schedule=schedule,
                    solve_time=solve_time,
                    message=f"Schedule created with {len(schedule)} tasks"
                )
            else:
                return self.create_schedule_result(
                    status=ScheduleStatus.FAILED,
                    solve_time=solve_time,
                    message=f"Solver failed with status: {status}"
                )
                
        except Exception as e:
            return self.create_schedule_result(
                status=ScheduleStatus.FAILED,
                message=f"Error in MILP scheduling: {str(e)}"
            )
    
    def _extract_solution(self, x: Dict, y: Dict, z: Dict, 
                         tasks: List[EnduranceTask], time_horizon: int) -> List[EnduranceScheduledTask]:
        """Extract the solution from OR-Tools solver."""
        schedule = []
        
        for i, task in enumerate(tasks):
            # Find start time
            start_time = None
            for t in range(time_horizon):
                if (i, t) in x and x[i, t].solution_value() > 0.5:
                    start_time = t
                    break
            
            if start_time is not None:
                start_datetime = datetime.now() + timedelta(minutes=start_time)
                end_datetime = start_datetime + task.preferred_duration
                
                scheduled_task = EnduranceScheduledTask(
                    task_id=task.id,
                    start_time=start_datetime,
                    end_time=end_datetime,
                    duration=task.preferred_duration,
                    priority=task.priority,
                    metadata={"algorithm": "MILP"}
                )
                
                # Add resource allocations
                for constraint in task.resource_constraints:
                    scheduled_task.resource_allocations[constraint.resource_id] = constraint.min_amount
                
                # Add resource impacts
                for impact in task.resource_impacts:
                    scheduled_task.resource_impacts[impact.resource_id] = {
                        "impact_type": impact.impact_type,
                        "impact_value": impact.impact_value
                    }
                
                schedule.append(scheduled_task)
        
        return schedule
    
    def _calculate_time_horizon(self, tasks: List[EnduranceTask]) -> int:
        """Calculate the time horizon for scheduling."""
        if not tasks:
            return 100
        
        # Find the latest end time
        latest_end = max(task.end_time for task in tasks)
        time_horizon = int((latest_end - datetime.now()).total_seconds() / 60)  # Convert to minutes
        
        return max(time_horizon, 100)  # Minimum 100 minutes
