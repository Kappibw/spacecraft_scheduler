"""
Tests for resource management functionality.
"""

import pytest
from datetime import datetime

from src.common.resources import Resource, ResourceType, ResourceStatus, ResourceManager


class TestResource:
    """Test Resource class functionality."""
    
    def test_resource_creation(self):
        """Test basic resource creation."""
        resource = Resource.create(
            resource_type=ResourceType.ROBOT,
            name="Test Robot",
            capacity=1.0
        )
        
        assert resource.resource_type == ResourceType.ROBOT
        assert resource.name == "Test Robot"
        assert resource.capacity == 1.0
        assert resource.current_usage == 0.0
        assert resource.status == ResourceStatus.AVAILABLE
        assert resource.id is not None
    
    def test_resource_allocation(self):
        """Test resource allocation and deallocation."""
        resource = Resource.create(
            resource_type=ResourceType.TOOL,
            name="Test Tool",
            capacity=1.0
        )
        
        # Test allocation
        assert resource.can_allocate(0.5)
        assert resource.allocate(0.5)
        assert resource.current_usage == 0.5
        assert resource.available_capacity == 0.5
        
        # Test over-allocation
        assert not resource.can_allocate(0.6)
        assert not resource.allocate(0.6)
        
        # Test deallocation
        assert resource.deallocate(0.3)
        assert resource.current_usage == 0.2
        assert resource.available_capacity == 0.8
    
    def test_resource_utilization(self):
        """Test resource utilization calculation."""
        resource = Resource.create(
            resource_type=ResourceType.ROBOT,
            name="Test Robot",
            capacity=2.0
        )
        
        assert resource.utilization == 0.0
        
        resource.allocate(1.0)
        assert resource.utilization == 0.5
        
        resource.allocate(1.0)
        assert resource.utilization == 1.0


class TestResourceManager:
    """Test ResourceManager functionality."""
    
    def test_add_resource(self):
        """Test adding resources to manager."""
        manager = ResourceManager()
        resource = Resource.create(
            resource_type=ResourceType.ROBOT,
            name="Test Robot",
            capacity=1.0
        )
        
        manager.add_resource(resource)
        assert len(manager.get_all_resources()) == 1
        assert manager.get_resource(resource.id) == resource
    
    def test_resource_allocation(self):
        """Test resource allocation through manager."""
        manager = ResourceManager()
        
        # Add resources
        robot = Resource.create(
            resource_type=ResourceType.ROBOT,
            name="Robot-1",
            capacity=1.0
        )
        
        tool = Resource.create(
            resource_type=ResourceType.TOOL,
            name="Tool-1",
            capacity=1.0
        )
        
        manager.add_resource(robot)
        manager.add_resource(tool)
        
        # Test allocation
        requirements = {robot.id: 1.0, tool.id: 0.5}
        assert manager.allocate_resources("task-1", requirements)
        
        # Check allocations
        allocations = manager.get_task_allocations("task-1")
        assert allocations == requirements
        
        # Test deallocation
        assert manager.deallocate_resources("task-1")
        assert manager.get_task_allocations("task-1") == {}
    
    def test_resource_filtering(self):
        """Test resource filtering by type and status."""
        manager = ResourceManager()
        
        # Add different types of resources
        robot = Resource.create(
            resource_type=ResourceType.ROBOT,
            name="Robot-1",
            capacity=1.0
        )
        
        tool = Resource.create(
            resource_type=ResourceType.TOOL,
            name="Tool-1",
            capacity=1.0
        )
        
        manager.add_resource(robot)
        manager.add_resource(tool)
        
        # Test filtering by type
        robots = manager.get_resources_by_type(ResourceType.ROBOT)
        assert len(robots) == 1
        assert robots[0].id == robot.id
        
        # Test filtering by status
        available = manager.get_available_resources()
        assert len(available) == 2
        
        # Change status and test again
        manager.update_resource_status(robot.id, ResourceStatus.BUSY)
        available = manager.get_available_resources()
        assert len(available) == 1
        assert available[0].id == tool.id
