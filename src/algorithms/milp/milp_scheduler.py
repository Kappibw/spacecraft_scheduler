"""
MILP-based scheduling algorithm for robot using the new models.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import gurobipy as gp
from gurobipy import GRB

from ..base import BaseScheduler, ScheduleResult, ScheduleStatus, ScheduledTask
from ...common.tasks.task import Task, TaskConstraintType
from ...common.resources.resource import Resource, ResourceType


class MILPScheduler(BaseScheduler):
    """MILP scheduler for robot using the new task and resource models."""
    
    def __init__(self, time_limit: int = 300):
        super().__init__("MILPScheduler", time_limit)
    
    def schedule(self, tasks: List[Task], resources: List[Resource]) -> ScheduleResult:
        """
        Schedule tasks using Gurobi MILP optimization.
        
        Args:
            tasks: List of Task objects to schedule
            resources: List of Resource objects available
            
        Returns:
            ScheduleResult containing the schedule and metadata
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
            # Create Gurobi model
            model = gp.Model("MILPScheduler")
            model.setParam('TimeLimit', self.time_limit)
            model.setParam('OutputFlag', 0)  # Suppress Gurobi output
            
            # Create time horizon based on task time windows
            time_horizon = self._calculate_time_horizon(tasks)
            
            # Decision variables
            # x[i,t] = 1 if task i starts at time t
            x = {}
            for i, task in enumerate(tasks):
                for t in range(time_horizon):
                    x[i, t] = model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{t}')
            
            # y[i] = start time of task i
            y = {}
            for i, task in enumerate(tasks):
                y[i] = model.addVar(vtype=GRB.INTEGER, lb=0, ub=time_horizon - 1, name=f'y_{i}')
            
            # z[i] = completion time of task i
            z = {}
            for i, task in enumerate(tasks):
                z[i] = model.addVar(vtype=GRB.INTEGER, lb=0, ub=time_horizon, name=f'z_{i}')
            
            # Makespan variable
            makespan = model.addVar(vtype=GRB.INTEGER, lb=0, ub=time_horizon, name='makespan')
            
            # Constraints
            # Each task must start exactly once
            for i, task in enumerate(tasks):
                model.addConstr(gp.quicksum(x[i, t] for t in range(time_horizon)) == 1, 
                               name=f'task_{i}_start_once')
            
            # Task duration constraints
            for i, task in enumerate(tasks):
                # Use preferred duration for simplicity
                duration = int(task.preferred_duration.total_seconds() / 60)  # Convert to minutes
                model.addConstr(z[i] - y[i] == duration, name=f'task_{i}_duration')
            
            # Time window constraints
            for i, task in enumerate(tasks):
                # Start time must be within task's time window
                start_min = int((task.start_time - datetime.now()).total_seconds() / 60)
                start_max = int((task.end_time - task.preferred_duration - datetime.now()).total_seconds() / 60)
                
                # Constraint: y[i] >= start_min
                if start_min >= 0:
                    model.addConstr(y[i] >= start_min, name=f'task_{i}_start_min')
                
                # Constraint: y[i] <= start_max
                if start_max >= 0:
                    model.addConstr(y[i] <= start_max, name=f'task_{i}_start_max')
            
            # Task dependency constraints
            for i, task in enumerate(tasks):
                for constraint_obj in task.task_constraints:
                    if constraint_obj.constraint_type == TaskConstraintType.START_AFTER_END:
                        # Find the target task
                        target_index = next((j for j, t in enumerate(tasks) if t.id == constraint_obj.target_task_id), None)
                        if target_index is not None:
                            # y[i] >= z[target_index]
                            model.addConstr(y[i] >= z[target_index], 
                                          name=f'task_{i}_after_{target_index}')
            
            # Resource constraints (simplified - assume single robot)
            # Only one task can be running at a time
            for t in range(time_horizon):
                model.addConstr(gp.quicksum(x[i, start_t] for i, task in enumerate(tasks)
                                          for start_t in range(max(0, t - int(task.preferred_duration.total_seconds() / 60) + 1), 
                                                              min(time_horizon, t + 1))
                                          if (i, start_t) in x) <= 1, 
                               name=f'resource_t_{t}')
            
            # Makespan constraint
            for i, task in enumerate(tasks):
                model.addConstr(makespan >= z[i], name=f'makespan_{i}')
            
            # Objective: minimize makespan
            model.setObjective(makespan, GRB.MINIMIZE)
            
            # Solve
            model.optimize()
            
            end_time = datetime.now()
            solve_time = (end_time - start_time).total_seconds()
            
            if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
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
                    message=f"Solver failed with status: {model.status}"
                )
                
        except Exception as e:
            return self.create_schedule_result(
                status=ScheduleStatus.FAILED,
                message=f"Error in MILP scheduling: {str(e)}"
            )
    
    def _extract_solution(self, x: Dict, y: Dict, z: Dict, 
                         tasks: List[Task], time_horizon: int) -> List[ScheduledTask]:
        """Extract the solution from Gurobi solver."""
        schedule = []
        
        for i, task in enumerate(tasks):
            # Find start time
            start_time = None
            for t in range(time_horizon):
                if (i, t) in x and x[i, t].x > 0.5:
                    start_time = t
                    break
            
            if start_time is not None:
                start_datetime = datetime.now() + timedelta(minutes=start_time)
                end_datetime = start_datetime + task.preferred_duration
                
                scheduled_task = ScheduledTask(
                    task_id=task.id,
                    start_time=start_datetime,
                    end_time=end_datetime,
                    duration=task.preferred_duration,
                    priority=task.priority,
                    metadata={"algorithm": "MILP-Gurobi"}
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
    
    def _calculate_time_horizon(self, tasks: List[Task]) -> int:
        """Calculate the time horizon for scheduling."""
        if not tasks:
            return 100
        
        # Find the latest end time
        latest_end = max(task.end_time for task in tasks)
        time_horizon = int((latest_end - datetime.now()).total_seconds() / 60)  # Convert to minutes
        
        return max(time_horizon, 100)  # Minimum 100 minutes
