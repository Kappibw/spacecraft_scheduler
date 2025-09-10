"""
Resource management functionality for robot scheduling.
"""

from typing import List, Dict, Optional, Set, Any
from datetime import datetime
from .resource import Resource, ResourceStatus, ResourceType


class ResourceManager:
    """Manages resources for robot scheduling."""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.allocations: Dict[str, Dict[str, float]] = {}  # task_id -> {resource_id: amount}
    
    def add_resource(self, resource: Resource) -> None:
        """Add a resource to the manager."""
        self.resources[resource.id] = resource
    
    def remove_resource(self, resource_id: str) -> bool:
        """Remove a resource from the manager."""
        if resource_id in self.resources:
            # Check if resource is currently allocated
            for task_id, allocations in self.allocations.items():
                if resource_id in allocations:
                    return False  # Cannot remove allocated resource
            del self.resources[resource_id]
            return True
        return False
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID."""
        return self.resources.get(resource_id)
    
    def get_all_resources(self) -> List[Resource]:
        """Get all resources."""
        return list(self.resources.values())
    
    def get_resources_by_type(self, resource_type: ResourceType) -> List[Resource]:
        """Get all resources of a specific type."""
        return [resource for resource in self.resources.values() 
                if resource.resource_type == resource_type]
    
    def get_resources_by_status(self, status: ResourceStatus) -> List[Resource]:
        """Get all resources with a specific status."""
        return [resource for resource in self.resources.values() 
                if resource.status == status]
    
    def get_available_resources(self, resource_type: Optional[ResourceType] = None) -> List[Resource]:
        """Get all available resources, optionally filtered by type."""
        available = [resource for resource in self.resources.values() 
                    if resource.status == ResourceStatus.AVAILABLE]
        
        if resource_type:
            available = [resource for resource in available 
                        if resource.resource_type == resource_type]
        
        return available
    
    def allocate_resources(self, task_id: str, resource_requirements: Dict[str, float]) -> bool:
        """Allocate resources for a task."""
        # Check if all required resources are available
        for resource_id, amount in resource_requirements.items():
            resource = self.get_resource(resource_id)
            if not resource or not resource.can_allocate(amount):
                # Rollback any partial allocations
                self.deallocate_resources(task_id)
                return False
        
        # Allocate resources
        for resource_id, amount in resource_requirements.items():
            resource = self.get_resource(resource_id)
            resource.allocate(amount)
        
        # Track allocations
        self.allocations[task_id] = resource_requirements.copy()
        return True
    
    def deallocate_resources(self, task_id: str) -> bool:
        """Deallocate resources for a task."""
        if task_id not in self.allocations:
            return False
        
        # Deallocate resources
        for resource_id, amount in self.allocations[task_id].items():
            resource = self.get_resource(resource_id)
            if resource:
                resource.deallocate(amount)
        
        # Remove allocation tracking
        del self.allocations[task_id]
        return True
    
    def get_task_allocations(self, task_id: str) -> Dict[str, float]:
        """Get resource allocations for a task."""
        return self.allocations.get(task_id, {})
    
    def find_suitable_resources(self, requirements: Dict[str, Any]) -> Dict[str, List[Resource]]:
        """Find resources that can satisfy the given requirements."""
        suitable = {}
        
        for resource_type_str, amount in requirements.items():
            try:
                resource_type = ResourceType(resource_type_str)
                available_resources = self.get_available_resources(resource_type)
                
                # Filter by capacity and capabilities if specified
                suitable_resources = []
                for resource in available_resources:
                    if resource.available_capacity >= amount:
                        # Check capabilities if specified
                        if "capabilities" in requirements:
                            required_capabilities = requirements["capabilities"]
                            if all(cap in resource.capabilities for cap in required_capabilities):
                                suitable_resources.append(resource)
                        else:
                            suitable_resources.append(resource)
                
                suitable[resource_type_str] = suitable_resources
            except ValueError:
                # Invalid resource type
                continue
        
        return suitable
    
    def update_resource_status(self, resource_id: str, status: ResourceStatus) -> bool:
        """Update the status of a resource."""
        if resource_id in self.resources:
            self.resources[resource_id].status = status
            return True
        return False
    
    def get_resource_statistics(self) -> Dict[str, int]:
        """Get statistics about resources."""
        stats = {
            "total": len(self.resources),
            "available": 0,
            "busy": 0,
            "maintenance": 0,
            "offline": 0,
            "reserved": 0
        }
        
        for resource in self.resources.values():
            stats[resource.status.value] += 1
        
        return stats
    
    def get_utilization_report(self) -> Dict[str, Dict[str, float]]:
        """Get utilization report for all resources."""
        report = {}
        
        for resource in self.resources.values():
            report[resource.id] = {
                "name": resource.name,
                "type": resource.resource_type.value,
                "utilization": resource.utilization,
                "available_capacity": resource.available_capacity,
                "status": resource.status.value
            }
        
        return report
