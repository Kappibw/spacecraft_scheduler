"""
Tests for task management functionality.
"""

import pytest
from datetime import datetime, timedelta

from src.common.tasks import Task, TaskType, TaskStatus, TaskManager


class TestTask:
    """Test Task class functionality."""
    
    def test_task_creation(self):
        """Test basic task creation."""
        task = Task.create(
            task_type=TaskType.PICKUP,
            description="Test task",
            duration=timedelta(minutes=15)
        )
        
        assert task.task_type == TaskType.PICKUP
        assert task.description == "Test task"
        assert task.duration == timedelta(minutes=15)
        assert task.status == TaskStatus.PENDING
        assert task.priority == 1
        assert task.id is not None
    
    def test_task_serialization(self):
        """Test task serialization to/from dictionary."""
        task = Task.create(
            task_type=TaskType.DELIVERY,
            description="Serialization test",
            duration=timedelta(minutes=20),
            priority=2
        )
        
        # Convert to dict and back
        task_dict = task.to_dict()
        restored_task = Task.from_dict(task_dict)
        
        assert restored_task.id == task.id
        assert restored_task.task_type == task.task_type
        assert restored_task.description == task.description
        assert restored_task.duration == task.duration
        assert restored_task.priority == task.priority


class TestTaskManager:
    """Test TaskManager functionality."""
    
    def test_add_task(self):
        """Test adding tasks to manager."""
        manager = TaskManager()
        task = Task.create(
            task_type=TaskType.INSPECTION,
            description="Test task",
            duration=timedelta(minutes=10)
        )
        
        manager.add_task(task)
        assert len(manager.get_all_tasks()) == 1
        assert manager.get_task(task.id) == task
    
    def test_task_queue_ordering(self):
        """Test task queue ordering by priority."""
        manager = TaskManager()
        
        # Add tasks with different priorities
        task1 = Task.create(
            task_type=TaskType.PICKUP,
            description="High priority",
            duration=timedelta(minutes=5),
            priority=1
        )
        
        task2 = Task.create(
            task_type=TaskType.DELIVERY,
            description="Low priority",
            duration=timedelta(minutes=10),
            priority=3
        )
        
        task3 = Task.create(
            task_type=TaskType.INSPECTION,
            description="Medium priority",
            duration=timedelta(minutes=8),
            priority=2
        )
        
        # Add in different order
        manager.add_task(task2)
        manager.add_task(task1)
        manager.add_task(task3)
        
        # Check ordering
        next_task = manager.get_next_task()
        assert next_task.id == task1.id  # Highest priority first
    
    def test_task_dependencies(self):
        """Test task dependency handling."""
        manager = TaskManager()
        
        # Create tasks with dependencies
        task1 = Task.create(
            task_type=TaskType.PICKUP,
            description="First task",
            duration=timedelta(minutes=5)
        )
        
        task2 = Task.create(
            task_type=TaskType.DELIVERY,
            description="Second task",
            duration=timedelta(minutes=10),
            dependencies=[task1.id]
        )
        
        manager.add_task(task1)
        manager.add_task(task2)
        
        # Initially, only task1 should be ready
        ready_tasks = manager.get_ready_tasks()
        assert len(ready_tasks) == 1
        assert ready_tasks[0].id == task1.id
        
        # After completing task1, task2 should be ready
        manager.update_task_status(task1.id, TaskStatus.COMPLETED)
        ready_tasks = manager.get_ready_tasks()
        assert len(ready_tasks) == 1
        assert ready_tasks[0].id == task2.id
