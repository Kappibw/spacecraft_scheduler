"""
Schedule visualization functionality.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np

from ...algorithms.base import ScheduleResult, ScheduledTask
from ...common.tasks.task_manager import TaskManager
from ...common.resources.resource_manager import ResourceManager


class ScheduleVisualizer:
    """Visualizes robot schedules and resource utilization."""
    
    def __init__(self, figsize: tuple = (14, 10)):
        self.figsize = figsize
        # Priority-based color spectrum: red (high priority) to blue (low priority)
        self.priority_colors = {
            1: '#DC143C',  # Crimson (highest priority)
            2: '#FF4500',  # Orange Red
            3: '#FF8C00',  # Dark Orange
            4: '#FFD700',  # Gold
            5: '#ADFF2F',  # Green Yellow
            6: '#32CD32',  # Lime Green
            7: '#00CED1',  # Dark Turquoise
            8: '#1E90FF',  # Dodger Blue
            9: '#4169E1',  # Royal Blue
            10: '#0000CD'  # Medium Blue (lowest priority)
        }
        self.resource_colors = [
            '#E74C3C', '#3498DB', '#2ECC71', '#F39C12',
            '#9B59B6', '#1ABC9C', '#34495E', '#E67E22'
        ]
    
    def plot_schedule_result(self, 
                           result: ScheduleResult,
                           task_manager: TaskManager,
                           resource_manager: ResourceManager,
                           title: str = "Schedule Visualization") -> plt.Figure:
        """
        Create a comprehensive visualization of a ScheduleResult.
        
        Args:
            result: The schedule result to visualize
            task_manager: Task manager to get task details
            resource_manager: Resource manager to get resource details
            title: Title for the plot
            
        Returns:
            matplotlib Figure object
        """
        if not result.schedule:
            fig, ax = plt.subplots(figsize=self.figsize)
            ax.set_title(title)
            ax.text(0.5, 0.5, 'No schedule data available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=16)
            return fig
        
        # Calculate time range
        start_times = [task.start_time for task in result.schedule]
        end_times = [task.end_time for task in result.schedule]
        min_time = min(start_times)
        max_time = max(end_times)
        
        # Add some padding
        time_padding = (max_time - min_time) * 0.05
        min_time -= time_padding
        max_time += time_padding
        
        # Create figure with subplots and set background color
        # Top plot: Tasks as rectangles
        # Bottom plot: All resources combined as line plots
        n_resources = len(resource_manager.get_all_resources())
        if n_resources == 0:
            # Only task plot if no resources
            fig, axes = plt.subplots(1, 1, figsize=self.figsize, facecolor='white')
            axes = [axes]
        else:
            # Tasks + combined resources
            fig, axes = plt.subplots(2, 1, figsize=(self.figsize[0], self.figsize[1] + 3), 
                                   sharex=True, gridspec_kw={'height_ratios': [3, 2]}, facecolor='white')
        
        # Set background colors for subplots
        for ax in axes:
            ax.set_facecolor('white')
        
        # Plot 1: Tasks as rectangles
        self._plot_tasks_rectangles(axes[0], result, task_manager, min_time, max_time)
        
        # Plot 2: All resources as combined line plots
        if n_resources > 0:
            self._plot_combined_resources(axes[1], result, resource_manager, 
                                          min_time, max_time)
        
        # Final formatting
        axes[0].set_title(title, fontsize=16, fontweight='bold')
        
        # Format x-axis only on bottom plot
        axes[-1].set_xlabel('Time', fontsize=14, fontweight='bold')
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # Calculate appropriate tick interval based on time range
        time_range = (max_time - min_time).total_seconds() / 60  # in minutes
        if time_range <= 60:  # 1 hour or less
            interval = 10  # 10 minute intervals
        elif time_range <= 240:  # 4 hours or less
            interval = 30  # 30 minute intervals
        elif time_range <= 720:  # 12 hours or less
            interval = 60  # 1 hour intervals
        else:
            interval = 120  # 2 hour intervals
        
        axes[-1].xaxis.set_major_locator(mdates.MinuteLocator(interval=interval))
        plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=45, fontsize=12)
        
        plt.tight_layout()
        return fig
    
    def _plot_tasks_rectangles(self, ax, result: ScheduleResult, task_manager: TaskManager, 
                              min_time: datetime, max_time: datetime):
        """Plot tasks as rectangles on the timeline."""
        
        # Create a list to track task levels (for overlapping tasks)
        task_levels = []
        
        # Sort tasks by start time to process them in chronological order
        sorted_tasks = sorted(result.schedule, key=lambda t: t.start_time)
        
        for task in sorted_tasks:
            # Find an available level by checking overlaps with already assigned tasks
            level = 0
            while True:
                # Check if this level is available (no overlapping tasks)
                level_available = True
                for existing_task, existing_level in task_levels:
                    if existing_level == level:
                        # Check for actual overlap (tasks touching at exact times are OK)
                        # Only stack if there's a real overlap (not just touching)
                        # Round to the nearest tenth of a second
                        task_start_time = round(task.start_time.timestamp(), 1)
                        task_end_time = round(task.end_time.timestamp(), 1)
                        existing_task_start_time = round(existing_task.start_time.timestamp(), 1)
                        existing_task_end_time = round(existing_task.end_time.timestamp(), 1)
                        if (task_start_time < existing_task_end_time or 
                            task_end_time > existing_task_start_time):
                            level_available = False
                            break
                
                if level_available:
                    break
                level += 1
            
            task_levels.append((task, level))
        
        # Calculate total levels needed
        max_level = max(level for _, level in task_levels) + 1
        
        # Create a mapping from task_id to level for constraint arrows
        task_level_map = {task.task_id: level for task, level in task_levels}
        
        # Plot each task
        for index, (task, level) in enumerate(task_levels):
            # Get task details
            task_obj = task_manager.get_task(task.task_id)
            task_name = task_obj.name if task_obj else f"Task {task.task_id[:8]}"
            
            # Calculate position and size
            start_num = mdates.date2num(task.start_time)
            end_num = mdates.date2num(task.end_time)
            width = end_num - start_num
            
            # Choose color based on priority
            priority = task_obj.priority if task_obj else 1
            color = self.priority_colors.get(priority, self.priority_colors[1])
            
            # Create rectangle
            rect = Rectangle(
                (start_num, level - 0.4),
                width,
                0.8,
                facecolor=color,
                edgecolor='black',
                alpha=0.7,
                linewidth=1
            )
            ax.add_patch(rect)
            
            # Add task label
            ax.text(
                start_num + width / 2,
                level - 0.1 * (index % 2),
                task_name,
                ha='center',
                va='center',
                fontsize=11,
                fontweight='bold',
                color='black'
            )
            
            # Add duration and priority labels on separate lines
            duration_min = task.duration.total_seconds() / 60
            priority = task_obj.priority if task_obj else 1
            
            # Duration label
            ax.text(
                start_num + width / 2,
                level - 0.2,
                f"{duration_min:.1f}min",
                ha='center',
                va='center',
                fontsize=10,
                color='black',
                fontweight='bold'
            )
            
            # Priority label
            ax.text(
                start_num + width / 2,
                level - 0.35,
                f"P{priority}",
                ha='center',
                va='center',
                fontsize=10,
                color='black',
                fontweight='bold'
            )
            
            # Add start and end time annotations
            start_str = task.start_time.strftime('%H:%M')
            end_str = task.end_time.strftime('%H:%M')
            
            # Start time annotation
            ax.annotate(
                start_str,
                xy=(start_num, level),
                xytext=(start_num, level + 0.4),
                ha='center',
                va='bottom',
                fontsize=10,
                color='black',
                fontweight='bold'
            )
            
            # End time annotation
            ax.annotate(
                end_str,
                xy=(start_num + width, level),
                xytext=(start_num + width, level + 0.4),
                ha='center',
                va='bottom',
                fontsize=10,
                color='black',
                fontweight='bold'
            )
        
        # Draw constraint arrows
        self._draw_constraint_arrows(ax, result, task_manager, task_level_map, min_time, max_time)
        
        # Formatting
        ax.set_ylim(-0.5, max_level - 0.5)
        ax.set_xlim(mdates.date2num(min_time), mdates.date2num(max_time))
        ax.set_ylabel('Tasks', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_yticklabels([])
        
        # Add legend for priority colors
        priority_legend_elements = []
        unique_priorities = sorted(set(task_obj.priority for task, _ in task_levels 
                                     for task_obj in [task_manager.get_task(task.task_id)] 
                                     if task_obj))
        
        for priority in unique_priorities[:8]:  # Limit legend items
            color = self.priority_colors.get(priority, self.priority_colors[1])
            priority_legend_elements.append(
                plt.Rectangle((0, 0), 1, 1, facecolor=color, 
                            label=f"Priority {priority}")
            )
        
        if priority_legend_elements:
            ax.legend(handles=priority_legend_elements, loc='upper right', 
                     bbox_to_anchor=(1.0, 1.0), fontsize=10, title="Task Priority")
    
    def _draw_constraint_arrows(self, ax, result: ScheduleResult, task_manager: TaskManager, 
                               task_level_map: Dict[str, int], min_time: datetime, max_time: datetime):
        """Draw arrows to show task constraints."""
        from matplotlib.patches import FancyArrowPatch
        
        for scheduled_task in result.schedule:
            task_obj = task_manager.get_task(scheduled_task.task_id)
            if not task_obj:
                continue
            
            # Get the level of the current task
            current_level = task_level_map.get(scheduled_task.task_id)
            if current_level is None:
                continue
            
            # Check each constraint
            for constraint in task_obj.task_constraints:
                target_task_id = constraint.target_task_id
                target_level = task_level_map.get(target_task_id)
                
                if target_level is None:
                    continue  # Target task not in schedule
                
                # Find the target task in the schedule
                target_task = None
                for st in result.schedule:
                    if st.task_id == target_task_id:
                        target_task = st
                        break
                
                if not target_task:
                    continue
                
                # Calculate arrow positions
                current_start = mdates.date2num(scheduled_task.start_time)
                current_end = mdates.date2num(scheduled_task.end_time)
                target_start = mdates.date2num(target_task.start_time)
                target_end = mdates.date2num(target_task.end_time)
                
                # Determine arrow direction and style based on constraint type
                if constraint.constraint_type.value == 'start_after_end':
                    # Arrow from current task to target task (constrained to constraining)
                    start_x = current_start
                    start_y = current_level
                    end_x = target_end
                    end_y = target_level
                    linestyle = '-'
                    color = '#00FF00'  # Green for start_after_end
                elif constraint.constraint_type.value == 'contained':
                    # Arrow from current task to target task (constrained to constraining)
                    start_x = (current_start + current_end) / 2
                    start_y = current_level
                    end_x = (target_start + target_end) / 2
                    end_y = target_level
                    linestyle = '--'
                    color = '#4ECDC4'  # Teal for contained
                else:
                    continue
                
                # Only draw if tasks are on different levels
                if current_level != target_level:
                    # Create arrow
                    arrow = FancyArrowPatch(
                        (start_x, start_y),
                        (end_x, end_y),
                        arrowstyle='->',
                        mutation_scale=20,
                        color=color,
                        linewidth=4,
                        linestyle=linestyle,
                        alpha=0.8
                    )
                    ax.add_patch(arrow)
    
    def _plot_combined_resources(self, ax, result: ScheduleResult, resource_manager: ResourceManager,
                                 min_time: datetime, max_time: datetime):
        """Plot all resources as combined line plots on the same chart."""
        
        # Create time series data for each resource
        all_time_points = set()
        resource_data = {}
        
        for resource in resource_manager.get_all_resources():
            resource_name = resource.name if resource else f"Resource {resource.id[:8]}"
            
            # Initial state
            initial_usage = resource.current_state.current_value if resource else 0.0
            
            # Track usage changes from tasks
            task_changes = []
            for task in result.schedule:
                if resource.id in task.resource_allocations:
                    task_changes.append((task.start_time, task.resource_allocations[resource.id], 'start'))
                    task_changes.append((task.end_time, task.resource_allocations[resource.id], 'end'))
            
            # Sort by time
            task_changes.sort(key=lambda x: x[0])
            
            # Create time series
            time_points = [min_time]
            usage_points = [initial_usage]
            all_time_points.add(min_time)
            
            current_usage = initial_usage
            for time_point, amount, change_type in task_changes:
                if change_type == 'start':
                    current_usage += amount
                else:  # end
                    current_usage -= amount
                
                time_points.append(time_point)
                usage_points.append(current_usage)
                all_time_points.add(time_point)
            
            # Final state
            time_points.append(max_time)
            usage_points.append(current_usage)
            all_time_points.add(max_time)
            
            resource_data[resource.id] = {
                'name': resource_name,
                'time_points': time_points,
                'usage_points': usage_points,
                'resource': resource
            }
        
        # Sort all time points
        sorted_time_points = sorted(all_time_points)
        
        # Plot each resource
        for resource in resource_manager.get_all_resources():
            data = resource_data[resource.id]
            resource_name = data['name']
            resource = data['resource']
            
            # Choose color
            color = self.resource_colors[hash(resource.id) % len(self.resource_colors)]
            
            # For integer resources, create step function
            if resource and resource.resource_type.value == 'integer':
                # Create step function data
                step_times = []
                step_values = []
                
                for i, (time_point, usage) in enumerate(zip(data['time_points'], data['usage_points'])):
                    # Add the point
                    step_times.append(time_point)
                    step_values.append(usage)
                    
                    # Add the next point at the same level (for step effect)
                    if i < len(data['time_points']) - 1:
                        next_time = data['time_points'][i + 1]
                        step_times.append(next_time)
                        step_values.append(usage)
                
                # Convert to matplotlib format
                time_nums = [mdates.date2num(t) for t in step_times]
                
                # Plot step function
                ax.plot(time_nums, step_values, color=color, linewidth=3, 
                       label=resource_name, drawstyle='steps-post')
                
                # Add capacity line
                if resource.max_capacity:
                    ax.axhline(y=resource.max_capacity, color=color, linestyle='--', 
                             alpha=0.7, linewidth=1)
            
            else:
                # For cumulative resources, use regular line plot
                time_nums = [mdates.date2num(t) for t in data['time_points']]
                ax.plot(time_nums, data['usage_points'], color=color, linewidth=3, 
                       marker='o', markersize=4, label=resource_name)
        
        # Formatting
        ax.set_xlim(mdates.date2num(min_time), mdates.date2num(max_time))
        ax.set_ylabel('Resource Usage', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.legend(fontsize=12, loc='upper right')
        
        # Set y-axis limits
        all_usage_points = []
        for data in resource_data.values():
            all_usage_points.extend(data['usage_points'])
        
        if all_usage_points:
            max_usage = max(all_usage_points)
            ax.set_ylim(0, max_usage * 1.1)
    
    def _is_dark_color(self, color: str) -> bool:
        """Check if a color is dark (for text color decision)."""
        # Convert hex to RGB
        hex_color = color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate luminance
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        return luminance < 0.5
    
    
    def plot_resource_utilization(self, utilization_data: Dict[str, List[Dict[str, Any]]],
                                 title: str = "Resource Utilization") -> plt.Figure:
        """Plot resource utilization over time."""
        fig, axes = plt.subplots(len(utilization_data), 1, figsize=self.figsize, sharex=True)
        
        if len(utilization_data) == 1:
            axes = [axes]
        
        for i, (resource_id, data) in enumerate(utilization_data.items()):
            df = pd.DataFrame(data)
            
            # Plot utilization
            axes[i].plot(df['timestamp'], df['utilization'], 
                        label=f'{resource_id} Utilization', linewidth=2)
            axes[i].fill_between(df['timestamp'], 0, df['utilization'], alpha=0.3)
            
            # Formatting
            axes[i].set_ylabel('Utilization %')
            axes[i].set_title(f'{resource_id} Resource Utilization')
            axes[i].grid(True, alpha=0.3)
            axes[i].set_ylim(0, 100)
        
        axes[-1].set_xlabel('Time')
        fig.suptitle(title, fontsize=16)
        plt.tight_layout()
        return fig
    
    def plot_task_distribution(self, tasks: List[Dict[str, Any]],
                              title: str = "Task Distribution") -> plt.Figure:
        """Plot distribution of tasks by type and status."""
        df = pd.DataFrame(tasks)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        # Task type distribution
        task_type_counts = df['task_type'].value_counts()
        ax1.pie(task_type_counts.values, labels=task_type_counts.index, autopct='%1.1f%%')
        ax1.set_title('Tasks by Type')
        
        # Task status distribution
        task_status_counts = df['status'].value_counts()
        ax2.pie(task_status_counts.values, labels=task_status_counts.index, autopct='%1.1f%%')
        ax2.set_title('Tasks by Status')
        
        fig.suptitle(title, fontsize=16)
        plt.tight_layout()
        return fig
    
    def save_plot(self, fig: plt.Figure, filename: str, dpi: int = 300) -> None:
        """Save plot to file."""
        fig.savefig(filename, dpi=dpi, bbox_inches='tight')
        plt.close(fig)