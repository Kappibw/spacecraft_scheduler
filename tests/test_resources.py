"""
Tests for resource management functionality.
"""

import pytest

from src.common.resources import Resource, ResourceType, ResourceStatus, ResourceManager


class TestResource:
    """Test Resource class functionality."""
    
    def test_integer_resource_creation(self):
        """Test basic integer resource creation."""
        resource = Resource.create_integer_resource(
            name="Test Robot",
            description="Test robot resource",
            max_capacity=1.0
        )
        
        assert resource.resource_type == ResourceType.INTEGER
        assert resource.name == "Test Robot"
        assert resource.description == "Test robot resource"
        assert resource.max_capacity == 1.0
        assert resource.current_state.current_value == 0.0
        assert resource.status == ResourceStatus.AVAILABLE
        assert resource.id is not None
    
    def test_cumulative_rate_resource_creation(self):
        """Test basic cumulative rate resource creation."""
        resource = Resource.create_cumulative_rate_resource(
            name="Test Battery",
            description="Test battery resource",
            initial_value=100.0,
            min_value=0.0,
            max_value=100.0
        )
        
        assert resource.resource_type == ResourceType.CUMULATIVE_RATE
        assert resource.name == "Test Battery"
        assert resource.description == "Test battery resource"
        assert resource.initial_value == 100.0
        assert resource.min_value == 0.0
        assert resource.max_value == 100.0
        assert resource.current_state.current_value == 100.0
        assert resource.status == ResourceStatus.AVAILABLE
        assert resource.id is not None
    
    def test_integer_resource_allocation(self):
        """Test integer resource allocation and deallocation."""
        resource = Resource.create_integer_resource(
            name="Test Tool",
            description="Test tool resource",
            max_capacity=1.0
        )
        
        # Test allocation
        assert resource.can_allocate(1.0)
        assert resource.allocate(1.0)
        assert resource.current_state.current_value == 1.0
        
        # Test over-allocation
        assert not resource.can_allocate(0.1)
        assert not resource.allocate(0.1)
        assert resource.current_state.current_value == 1.0  # Should remain unchanged
        
        # Test deallocation
        assert resource.deallocate(1.0)
        assert resource.current_state.current_value == 0.0
    
    def test_cumulative_rate_resource_allocation(self):
        """Test cumulative rate resource allocation and deallocation."""
        resource = Resource.create_cumulative_rate_resource(
            name="Test Fuel Tank",
            description="Test fuel tank resource",
            initial_value=50.0,
            min_value=0.0,
            max_value=100.0
        )
        
        # Test allocation
        assert resource.can_allocate(30.0)
        assert resource.allocate(30.0)
        assert resource.current_state.current_value == 80.0
        
        # Test over-allocation (would exceed max_value)
        assert not resource.can_allocate(25.0)
        assert not resource.allocate(25.0)
        assert resource.current_state.current_value == 80.0  # Should remain unchanged
        
        # Test deallocation
        assert resource.deallocate(30.0)
        assert resource.current_state.current_value == 50.0
    
    def test_resource_validation(self):
        """Test resource configuration validation."""
        # Test integer resource without max_capacity
        with pytest.raises(ValueError, match="INTEGER resources must have max_capacity"):
            Resource.create_integer_resource(
                name="Invalid Resource",
                description="Invalid resource",
                max_capacity=None
            )
        
        # Test cumulative rate resource without initial_value
        with pytest.raises(ValueError, match="CUMULATIVE_RATE resources must have initial_value"):
            Resource.create_cumulative_rate_resource(
                name="Invalid Resource",
                description="Invalid resource",
                initial_value=None
            )
    
    def test_resource_serialization(self):
        """Test resource serialization to/from dictionary."""
        resource = Resource.create_integer_resource(
            name="Serialization Test",
            description="Test serialization",
            max_capacity=2.0
        )
        
        # Convert to dict and back
        resource_dict = resource.to_dict()
        restored_resource = Resource.from_dict(resource_dict)
        
        assert restored_resource.id == resource.id
        assert restored_resource.name == resource.name
        assert restored_resource.description == resource.description
        assert restored_resource.resource_type == resource.resource_type
        assert restored_resource.max_capacity == resource.max_capacity
        assert restored_resource.status == resource.status


class TestResourceManager:
    """Test ResourceManager functionality."""
    
    def test_add_resource(self):
        """Test adding resources to manager."""
        manager = ResourceManager()
        resource = Resource.create_integer_resource(
            name="Test Robot",
            description="Test robot resource",
            max_capacity=1.0
        )
        
        manager.add_resource(resource)
        assert len(manager.get_all_resources()) == 1
        assert manager.get_resource(resource.id) == resource
    
    def test_resource_allocation(self):
        """Test resource allocation through manager."""
        manager = ResourceManager()
        
        # Add resources
        robot = Resource.create_integer_resource(
            name="Robot-1",
            description="Test robot",
            max_capacity=1.0
        )
        
        tool = Resource.create_integer_resource(
            name="Tool-1",
            description="Test tool",
            max_capacity=1.0
        )
        
        manager.add_resource(robot)
        manager.add_resource(tool)
        
        # Test allocation
        requirements = {robot.id: 1.0, tool.id: 1.0}
        assert manager.allocate_resources("task-1", requirements)
        
        # Check allocations
        allocations = manager.get_task_resource_usage("task-1")
        assert allocations == requirements
        
        # Test deallocation
        assert manager.deallocate_resources("task-1")
        assert manager.get_task_resource_usage("task-1") == {}
    
    def test_resource_filtering(self):
        """Test resource filtering by type and status."""
        manager = ResourceManager()
        
        # Add different types of resources
        robot = Resource.create_integer_resource(
            name="Robot-1",
            description="Test robot",
            max_capacity=1.0
        )
        
        battery = Resource.create_cumulative_rate_resource(
            name="Battery-1",
            description="Test battery",
            initial_value=100.0,
            min_value=0.0,
            max_value=100.0
        )
        
        manager.add_resource(robot)
        manager.add_resource(battery)
        
        # Test filtering by type
        integer_resources = manager.get_resources_by_type(ResourceType.INTEGER)
        assert len(integer_resources) == 1
        assert integer_resources[0].id == robot.id
        
        cumulative_resources = manager.get_resources_by_type(ResourceType.CUMULATIVE_RATE)
        assert len(cumulative_resources) == 1
        assert cumulative_resources[0].id == battery.id
        
        # Test filtering by status
        available = manager.get_available_resources()
        assert len(available) == 2
        
        # Change status and test again
        robot.status = ResourceStatus.IN_USE
        available = manager.get_available_resources()
        assert len(available) == 1
        assert available[0].id == battery.id
    
    def test_resource_utilization(self):
        """Test resource utilization calculation."""
        manager = ResourceManager()
        
        # Add a resource
        resource = Resource.create_integer_resource(
            name="Test Resource",
            description="Test resource",
            max_capacity=2.0
        )
        
        manager.add_resource(resource)
        
        # Test utilization calculation
        assert manager.get_resource_utilization(resource.id) == 0.0
        
        # Allocate some capacity
        manager.allocate_resources("task-1", {resource.id: 1.0})
        assert manager.get_resource_utilization(resource.id) == 0.5
        
        # Allocate more capacity
        manager.allocate_resources("task-2", {resource.id: 1.0})
        assert manager.get_resource_utilization(resource.id) == 1.0