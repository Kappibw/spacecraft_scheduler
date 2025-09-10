"""
Resource utilization plotting functionality.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


class ResourcePlot:
    """Plots resource utilization and availability."""
    
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    def plot_resource_utilization(self, utilization_data: Dict[str, List[Dict[str, Any]]],
                                 title: str = "Resource Utilization") -> plt.Figure:
        """Plot resource utilization over time using matplotlib."""
        fig, axes = plt.subplots(len(utilization_data), 1, figsize=(12, 4 * len(utilization_data)))
        
        if len(utilization_data) == 1:
            axes = [axes]
        
        for i, (resource_id, data) in enumerate(utilization_data.items()):
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Plot utilization
            axes[i].plot(df['timestamp'], df['utilization'], 
                        label=f'{resource_id} Utilization', linewidth=2, color=self.colors[i % len(self.colors)])
            axes[i].fill_between(df['timestamp'], 0, df['utilization'], alpha=0.3, color=self.colors[i % len(self.colors)])
            
            # Add capacity line
            if 'capacity' in df.columns:
                axes[i].axhline(y=df['capacity'].iloc[0], color='red', linestyle='--', alpha=0.7, label='Capacity')
            
            # Formatting
            axes[i].set_ylabel('Utilization %')
            axes[i].set_title(f'{resource_id} Resource Utilization')
            axes[i].grid(True, alpha=0.3)
            axes[i].set_ylim(0, 100)
            axes[i].legend()
        
        axes[-1].set_xlabel('Time')
        fig.suptitle(title, fontsize=16)
        plt.tight_layout()
        return fig
    
    def plot_interactive_utilization(self, utilization_data: Dict[str, List[Dict[str, Any]]],
                                    title: str = "Resource Utilization") -> go.Figure:
        """Create interactive resource utilization plot using plotly."""
        fig = go.Figure()
        
        for i, (resource_id, data) in enumerate(utilization_data.items()):
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Add utilization trace
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['utilization'],
                mode='lines+markers',
                name=f'{resource_id} Utilization',
                line=dict(color=self.colors[i % len(self.colors)], width=3),
                marker=dict(size=6),
                fill='tonexty' if i > 0 else 'tozeroy',
                hovertemplate=f"<b>{resource_id}</b><br>" +
                             "Time: %{x}<br>" +
                             "Utilization: %{y}%<br>" +
                             "<extra></extra>"
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Utilization %",
            hovermode='x unified',
            showlegend=True,
            height=500
        )
        
        return fig
    
    def plot_resource_heatmap(self, resource_data: Dict[str, Dict[str, float]],
                             title: str = "Resource Usage Heatmap") -> go.Figure:
        """Create a heatmap of resource usage."""
        # Convert data to matrix format
        resources = list(resource_data.keys())
        time_slots = set()
        for resource_data in resource_data.values():
            time_slots.update(resource_data.keys())
        
        time_slots = sorted(time_slots)
        
        # Create matrix
        matrix = []
        for resource in resources:
            row = []
            for time_slot in time_slots:
                value = resource_data[resource].get(time_slot, 0)
                row.append(value)
            matrix.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=time_slots,
            y=resources,
            colorscale='Viridis',
            hovertemplate='<b>%{y}</b><br>' +
                         'Time: %{x}<br>' +
                         'Usage: %{z}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Resource",
            height=400
        )
        
        return fig
    
    def plot_resource_capacity(self, resources: List[Dict[str, Any]],
                              title: str = "Resource Capacity Overview") -> go.Figure:
        """Plot resource capacity and current usage."""
        df = pd.DataFrame(resources)
        
        # Create grouped bar chart
        fig = go.Figure()
        
        # Add capacity bars
        fig.add_trace(go.Bar(
            name='Capacity',
            x=df['name'],
            y=df['capacity'],
            marker_color='lightblue',
            opacity=0.7
        ))
        
        # Add current usage bars
        fig.add_trace(go.Bar(
            name='Current Usage',
            x=df['name'],
            y=df['current_usage'],
            marker_color='darkblue',
            opacity=0.9
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Resource",
            yaxis_title="Capacity/Usage",
            barmode='group',
            height=500
        )
        
        return fig
    
    def plot_resource_status_distribution(self, resources: List[Dict[str, Any]],
                                         title: str = "Resource Status Distribution") -> go.Figure:
        """Plot distribution of resource statuses."""
        df = pd.DataFrame(resources)
        status_counts = df['status'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.3
        )])
        
        fig.update_layout(
            title=title,
            height=500
        )
        
        return fig
    
    def plot_resource_efficiency(self, efficiency_data: Dict[str, List[Dict[str, Any]]],
                                title: str = "Resource Efficiency") -> go.Figure:
        """Plot resource efficiency metrics."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Utilization Rate', 'Availability', 'Throughput', 'Efficiency Score'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        for resource_id, data in efficiency_data.items():
            df = pd.DataFrame(data)
            
            # Utilization rate
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['utilization'],
                mode='lines',
                name=f'{resource_id} Utilization',
                showlegend=False
            ), row=1, col=1)
            
            # Availability
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['availability'],
                mode='lines',
                name=f'{resource_id} Availability',
                showlegend=False
            ), row=1, col=2)
            
            # Throughput
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['throughput'],
                mode='lines',
                name=f'{resource_id} Throughput',
                showlegend=False
            ), row=2, col=1)
            
            # Efficiency score
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['efficiency'],
                mode='lines',
                name=f'{resource_id} Efficiency',
                showlegend=False
            ), row=2, col=2)
        
        fig.update_layout(
            title=title,
            height=800,
            showlegend=False
        )
        
        return fig
