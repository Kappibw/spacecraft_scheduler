"""
Schedule visualization functionality.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd


class ScheduleVisualizer:
    """Visualizes robot schedules and resource utilization."""
    
    def __init__(self, figsize: tuple = (12, 8)):
        self.figsize = figsize
        self.colors = {
            'pickup': '#FF6B6B',
            'delivery': '#4ECDC4',
            'inspection': '#45B7D1',
            'maintenance': '#96CEB4',
            'transport': '#FFEAA7',
            'assembly': '#DDA0DD'
        }
    
    def plot_schedule(self, schedule: List[Dict[str, Any]], 
                     robots: List[str] = None,
                     title: str = "Robot Schedule") -> plt.Figure:
        """Plot a Gantt chart of the robot schedule."""
        if not schedule:
            fig, ax = plt.subplots(figsize=self.figsize)
            ax.set_title(title)
            ax.text(0.5, 0.5, 'No schedule data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return fig
        
        # Convert schedule to DataFrame for easier manipulation
        df = pd.DataFrame(schedule)
        
        # Extract unique robots if not provided
        if robots is None:
            robots = sorted(df['robot_id'].unique())
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot each task
        for i, robot in enumerate(robots):
            robot_tasks = df[df['robot_id'] == robot]
            
            for _, task in robot_tasks.iterrows():
                start_time = pd.to_datetime(task['start_time'])
                duration = pd.to_timedelta(task['duration'])
                end_time = start_time + duration
                
                # Get color for task type
                task_type = task.get('task_type', 'unknown')
                color = self.colors.get(task_type, '#CCCCCC')
                
                # Create rectangle for task
                rect = Rectangle(
                    (mdates.date2num(start_time), i - 0.4),
                    mdates.date2num(end_time) - mdates.date2num(start_time),
                    0.8,
                    facecolor=color,
                    edgecolor='black',
                    alpha=0.7
                )
                ax.add_patch(rect)
                
                # Add task label
                ax.text(
                    mdates.date2num(start_time) + (mdates.date2num(end_time) - mdates.date2num(start_time)) / 2,
                    i,
                    f"{task.get('task_id', '')[:8]}",
                    ha='center',
                    va='center',
                    fontsize=8
                )
        
        # Formatting
        ax.set_ylim(-0.5, len(robots) - 0.5)
        ax.set_yticks(range(len(robots)))
        ax.set_yticklabels(robots)
        ax.set_xlabel('Time')
        ax.set_ylabel('Robot ID')
        ax.set_title(title)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.xticks(rotation=45)
        
        # Add legend
        legend_elements = [plt.Rectangle((0, 0), 1, 1, facecolor=color, label=task_type.title())
                          for task_type, color in self.colors.items()]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        plt.tight_layout()
        return fig
    
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
