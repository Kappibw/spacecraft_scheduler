"""
Gantt chart visualization for robot schedules.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


class GanttChart:
    """Interactive Gantt chart for robot scheduling."""
    
    def __init__(self):
        self.colors = {
            'pickup': '#FF6B6B',
            'delivery': '#4ECDC4',
            'inspection': '#45B7D1',
            'maintenance': '#96CEB4',
            'transport': '#FFEAA7',
            'assembly': '#DDA0DD'
        }
    
    def create_gantt_chart(self, schedule: List[Dict[str, Any]], 
                          title: str = "Robot Schedule") -> go.Figure:
        """Create an interactive Gantt chart."""
        if not schedule:
            fig = go.Figure()
            fig.add_annotation(
                text="No schedule data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        df = pd.DataFrame(schedule)
        
        # Convert time columns
        df['Start'] = pd.to_datetime(df['start_time'])
        df['Finish'] = pd.to_datetime(df['end_time'])
        df['Duration'] = df['Finish'] - df['Start']
        
        # Create Gantt chart
        fig = go.Figure()
        
        # Group by robot
        for robot_id in df['robot_id'].unique():
            robot_tasks = df[df['robot_id'] == robot_id]
            
            for _, task in robot_tasks.iterrows():
                task_type = task.get('task_type', 'unknown')
                color = self.colors.get(task_type, '#CCCCCC')
                
                fig.add_trace(go.Scatter(
                    x=[task['Start'], task['Finish'], task['Finish'], task['Start'], task['Start']],
                    y=[robot_id, robot_id, robot_id, robot_id, robot_id],
                    fill='toself',
                    fillcolor=color,
                    line=dict(color='black', width=1),
                    mode='lines',
                    name=task_type.title(),
                    showlegend=False,
                    hovertemplate=f"<b>Task:</b> {task.get('task_id', '')}<br>" +
                                 f"<b>Type:</b> {task_type}<br>" +
                                 f"<b>Start:</b> {task['Start']}<br>" +
                                 f"<b>Finish:</b> {task['Finish']}<br>" +
                                 f"<b>Duration:</b> {task['Duration']}<br>" +
                                 "<extra></extra>"
                ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Robot ID",
            hovermode='closest',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        # Add legend for task types
        for task_type, color in self.colors.items():
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=task_type.title(),
                showlegend=True
            ))
        
        return fig
    
    def create_multi_resource_gantt(self, schedule: List[Dict[str, Any]],
                                   resources: List[str],
                                   title: str = "Multi-Resource Schedule") -> go.Figure:
        """Create a Gantt chart showing multiple resource types."""
        if not schedule:
            fig = go.Figure()
            fig.add_annotation(
                text="No schedule data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        df = pd.DataFrame(schedule)
        
        # Create subplots for each resource type
        fig = make_subplots(
            rows=len(resources), cols=1,
            subplot_titles=resources,
            vertical_spacing=0.05
        )
        
        for i, resource in enumerate(resources, 1):
            resource_tasks = df[df['resource_type'] == resource]
            
            for _, task in resource_tasks.iterrows():
                task_type = task.get('task_type', 'unknown')
                color = self.colors.get(task_type, '#CCCCCC')
                
                fig.add_trace(go.Scatter(
                    x=[task['start_time'], task['end_time'], task['end_time'], 
                       task['start_time'], task['start_time']],
                    y=[task['resource_id'], task['resource_id'], task['resource_id'], 
                       task['resource_id'], task['resource_id']],
                    fill='toself',
                    fillcolor=color,
                    line=dict(color='black', width=1),
                    mode='lines',
                    name=task_type.title(),
                    showlegend=(i == 1),  # Only show legend for first subplot
                    hovertemplate=f"<b>Resource:</b> {task['resource_id']}<br>" +
                                 f"<b>Task:</b> {task.get('task_id', '')}<br>" +
                                 f"<b>Type:</b> {task_type}<br>" +
                                 "<extra></extra>"
                ), row=i, col=1)
        
        fig.update_layout(
            title=title,
            height=200 * len(resources),
            showlegend=True
        )
        
        return fig
    
    def create_timeline_view(self, schedule: List[Dict[str, Any]],
                            title: str = "Schedule Timeline") -> go.Figure:
        """Create a timeline view of the schedule."""
        if not schedule:
            fig = go.Figure()
            fig.add_annotation(
                text="No schedule data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        df = pd.DataFrame(schedule)
        
        # Create timeline
        fig = go.Figure()
        
        for _, task in df.iterrows():
            task_type = task.get('task_type', 'unknown')
            color = self.colors.get(task_type, '#CCCCCC')
            
            fig.add_trace(go.Scatter(
                x=[task['start_time'], task['end_time']],
                y=[task['robot_id'], task['robot_id']],
                mode='lines+markers',
                line=dict(color=color, width=6),
                marker=dict(size=8),
                name=task_type.title(),
                showlegend=False,
                hovertemplate=f"<b>Robot:</b> {task['robot_id']}<br>" +
                             f"<b>Task:</b> {task.get('task_id', '')}<br>" +
                             f"<b>Type:</b> {task_type}<br>" +
                             f"<b>Start:</b> {task['start_time']}<br>" +
                             f"<b>End:</b> {task['end_time']}<br>" +
                             "<extra></extra>"
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Robot ID",
            hovermode='closest'
        )
        
        return fig
