"""
Tests for task management functionality.
"""

import pytest
from datetime import datetime, timedelta

from src.common.tasks import Task, TaskStatus, TaskManager, TaskConstraintType


class TestTask:
    """Test Task class functionality."""
    
    def test_task_creation(self):
        """Test basic task creation."""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        task = Task.create(
            name="Test Task",
            description="Test task description",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=5),
            max_duration=timedelta(minutes=15),
            preferred_duration=timedelta(minutes=10)
        )
        
        assert task.name == "Test Task"
        assert task.description == "Test task description"
        assert task.start_time == start_time
        assert task.end_time == end_time
        assert task.min_duration == timedelta(minutes=5)
        assert task.max_duration == timedelta(minutes=15)
        assert task.preferred_duration == timedelta(minutes=10)
        assert task.status == TaskStatus.PENDING
        assert task.priority == 1
        assert task.id is not None
    
    def test_task_serialization(self):
        """Test task serialization to/from dictionary."""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        task = Task.create(
            name="Serialization Test",
            description="Test serialization",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=10),
            max_duration=timedelta(minutes=20),
            preferred_duration=timedelta(minutes=15),
            priority=2
        )
        
        # Convert to dict and back
        task_dict = task.to_dict()
        restored_task = Task.from_dict(task_dict)
        
        assert restored_task.id == task.id
        assert restored_task.name == task.name
        assert restored_task.description == task.description
        assert restored_task.start_time == task.start_time
        assert restored_task.end_time == task.end_time
        assert restored_task.min_duration == task.min_duration
        assert restored_task.max_duration == task.max_duration
        assert restored_task.preferred_duration == task.preferred_duration
        assert restored_task.priority == task.priority
    
    def test_task_constraints_validation(self):
        """Test task constraint validation."""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        # Test invalid time constraints
        with pytest.raises(ValueError, match="start_time must be before end_time"):
            Task.create(
                name="Invalid Task",
                description="Invalid time constraints",
                start_time=end_time,  # start_time after end_time
                end_time=start_time,
                min_duration=timedelta(minutes=5),
                max_duration=timedelta(minutes=15),
                preferred_duration=timedelta(minutes=10)
            )
        
        # Test invalid duration constraints
        with pytest.raises(ValueError, match="min_duration cannot exceed max_duration"):
            Task.create(
                name="Invalid Task",
                description="Invalid duration constraints",
                start_time=start_time,
                end_time=end_time,
                min_duration=timedelta(minutes=20),  # min > max
                max_duration=timedelta(minutes=15),
                preferred_duration=timedelta(minutes=10)
            )
    
    def test_task_constraints(self):
        """Test adding task constraints."""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        task1 = Task.create(
            name="Task 1",
            description="First task",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=5),
            max_duration=timedelta(minutes=15),
            preferred_duration=timedelta(minutes=10)
        )
        
        task2 = Task.create(
            name="Task 2",
            description="Second task",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=5),
            max_duration=timedelta(minutes=15),
            preferred_duration=timedelta(minutes=10)
        )
        
        # Add constraint
        task2.add_task_constraint(
            TaskConstraintType.START_AFTER_END,
            task1.id
        )
        
        assert len(task2.task_constraints) == 1
        constraint = task2.task_constraints[0]
        assert constraint.constraint_type == TaskConstraintType.START_AFTER_END
        assert constraint.target_task_id == task1.id


class TestTaskManager:
    """Test TaskManager functionality."""
    
    def test_add_task(self):
        """Test adding tasks to manager."""
        manager = TaskManager()
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        task = Task.create(
            name="Test Task",
            description="Test task",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=10),
            max_duration=timedelta(minutes=20),
            preferred_duration=timedelta(minutes=15)
        )
        
        manager.add_task(task)
        assert len(manager.get_all_tasks()) == 1
        assert manager.get_task(task.id) == task
    
    def test_task_priority_ordering(self):
        """Test task ordering by priority."""
        manager = TaskManager()
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        # Add tasks with different priorities
        task1 = Task.create(
            name="High Priority",
            description="High priority task",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=5),
            max_duration=timedelta(minutes=15),
            preferred_duration=timedelta(minutes=10),
            priority=1  # Highest priority
        )
        
        task2 = Task.create(
            name="Low Priority",
            description="Low priority task",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=10),
            max_duration=timedelta(minutes=20),
            preferred_duration=timedelta(minutes=15),
            priority=3  # Lowest priority
        )
        
        task3 = Task.create(
            name="Medium Priority",
            description="Medium priority task",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=8),
            max_duration=timedelta(minutes=18),
            preferred_duration=timedelta(minutes=13),
            priority=2  # Medium priority
        )
        
        # Add in different order
        manager.add_task(task2)
        manager.add_task(task1)
        manager.add_task(task3)
        
        # Check ordering
        ordered_tasks = manager.get_tasks_by_priority()
        assert ordered_tasks[0].id == task1.id  # Highest priority first
        assert ordered_tasks[1].id == task3.id  # Medium priority second
        assert ordered_tasks[2].id == task2.id  # Lowest priority last
    
    def test_task_filtering(self):
        """Test filtering tasks by status."""
        manager = TaskManager()
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        # Create tasks with different statuses
        task1 = Task.create(
            name="Pending Task",
            description="Pending task",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=5),
            max_duration=timedelta(minutes=15),
            preferred_duration=timedelta(minutes=10),
            status=TaskStatus.PENDING
        )
        
        task2 = Task.create(
            name="Scheduled Task",
            description="Scheduled task",
            start_time=start_time,
            end_time=end_time,
            min_duration=timedelta(minutes=5),
            max_duration=timedelta(minutes=15),
            preferred_duration=timedelta(minutes=10),
            status=TaskStatus.SCHEDULED
        )
        
        manager.add_task(task1)
        manager.add_task(task2)
        
        # Test filtering by status
        pending_tasks = manager.get_tasks_by_status(TaskStatus.PENDING)
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == task1.id
        
        scheduled_tasks = manager.get_tasks_by_status(TaskStatus.SCHEDULED)
        assert len(scheduled_tasks) == 1
        assert scheduled_tasks[0].id == task2.id