"""
Endurance Resource Manager for handling EnduranceResource objects.
"""

from typing import Dict, List, Optional, Any
from .endurance_resource import EnduranceResource, ResourceType, ResourceStatus


class EnduranceResourceManager:
    """Manages EnduranceResource objects and their state."""
    
    def __init__(self):
        self.resources: Dict[str, EnduranceResource] = {}
        self.resource_usage: Dict[str, Dict[str, float]] = {}  # resource_id -> {task_id: amount}
    
    def add_resource(self, resource: EnduranceResource) -> None:
        """Add a resource to the manager."""
        self.resources[resource.id] = resource
        self.resource_usage[resource.id] = {}
    
    def remove_resource(self, resource_id: str) -> bool:
        """Remove a resource from the manager."""
        if resource_id in self.resources:
            # Clear any usage tracking
            if resource_id in self.resource_usage:
                del self.resource_usage[resource_id]
            del self.resources[resource_id]
            return True
        return False
    
    def get_resource(self, resource_id: str) -> Optional[EnduranceResource]:
        """Get a resource by ID."""
        return self.resources.get(resource_id)
    
    def get_all_resources(self) -> List[EnduranceResource]:
        """Get all resources."""
        return list(self.resources.values())
    
    def get_resources_by_type(self, resource_type: ResourceType) -> List[EnduranceResource]:
        """Get all resources of a specific type."""
        return [r for r in self.resources.values() if r.resource_type == resource_type]
    
    def get_integer_resources(self) -> List[EnduranceResource]:
        """Get all integer resources."""
        return self.get_resources_by_type(ResourceType.INTEGER)
    
    def get_cumulative_rate_resources(self) -> List[EnduranceResource]:
        """Get all cumulative rate resources."""
        return self.get_resources_by_type(ResourceType.CUMULATIVE_RATE)
    
    def get_resources_by_status(self, status: ResourceStatus) -> List[EnduranceResource]:
        """Get all resources with a specific status."""
        return [r for r in self.resources.values() if r.status == status]
    
    def get_available_resources(self) -> List[EnduranceResource]:
        """Get all available resources."""
        return self.get_resources_by_status(ResourceStatus.AVAILABLE)
    
    def can_allocate_resources(
        self, 
        task_id: str, 
        resource_requirements: Dict[str, float]
    ) -> bool:
        """Check if resources can be allocated for a task."""
        for resource_id, amount in resource_requirements.items():
            resource = self.get_resource(resource_id)
            if not resource:
                return False
            
            # Check if resource can allocate the required amount
            if not resource.can_allocate(amount):
                return False
        
        return True
    
    def allocate_resources(
        self, 
        task_id: str, 
        resource_requirements: Dict[str, float]
    ) -> bool:
        """Allocate resources for a task."""
        if not self.can_allocate_resources(task_id, resource_requirements):
            return False
        
        # Allocate each resource
        for resource_id, amount in resource_requirements.items():
            resource = self.get_resource(resource_id)
            if resource.allocate(amount):
                self.resource_usage[resource_id][task_id] = amount
            else:
                # Rollback previous allocations
                self.deallocate_resources(task_id)
                return False
        
        return True
    
    def deallocate_resources(self, task_id: str) -> bool:
        """Deallocate all resources for a task."""
        deallocated = True
        for resource_id, usage in self.resource_usage.items():
            if task_id in usage:
                resource = self.get_resource(resource_id)
                if resource:
                    amount = usage[task_id]
                    if not resource.deallocate(amount):
                        deallocated = False
                    del usage[task_id]
        return deallocated
    
    def get_task_resource_usage(self, task_id: str) -> Dict[str, float]:
        """Get resource usage for a specific task."""
        usage = {}
        for resource_id, task_usage in self.resource_usage.items():
            if task_id in task_usage:
                usage[resource_id] = task_usage[task_id]
        return usage
    
    def get_resource_usage(self, resource_id: str) -> Dict[str, float]:
        """Get all task usage for a specific resource."""
        return self.resource_usage.get(resource_id, {})
    
    def update_resource_rates(self, rate_changes: Dict[str, float]) -> None:
        """Update rates for cumulative rate resources."""
        for resource_id, new_rate in rate_changes.items():
            resource = self.get_resource(resource_id)
            if resource and resource.resource_type == ResourceType.CUMULATIVE_RATE:
                resource.set_rate(new_rate)
    
    def update_resources_over_time(self, delta_time: float) -> None:
        """Update all cumulative rate resources over time."""
        for resource in self.get_cumulative_rate_resources():
            resource.update_value(delta_time)
    
    def get_resource_utilization(self, resource_id: str) -> float:
        """Get utilization percentage for a resource."""
        resource = self.get_resource(resource_id)
        if resource:
            return resource.utilization
        return 0.0
    
    def get_all_resource_utilization(self) -> Dict[str, float]:
        """Get utilization for all resources."""
        return {resource_id: self.get_resource_utilization(resource_id) 
                for resource_id in self.resources.keys()}
    
    def validate_resource_constraints(
        self,
        task_id: str,
        resource_constraints: List[Dict[str, Any]]
    ) -> List[str]:
        """Validate that resource constraints can be satisfied."""
        errors = []
        
        for constraint in resource_constraints:
            resource_id = constraint.get("resource_id")
            min_amount = constraint.get("min_amount", 0.0)
            max_amount = constraint.get("max_amount", float('inf'))
            
            resource = self.get_resource(resource_id)
            if not resource:
                errors.append(f"Resource {resource_id} not found")
                continue
            
            # Check if resource can provide the required amount
            if resource.resource_type == ResourceType.INTEGER:
                if min_amount > resource.available_capacity:
                    errors.append(f"Resource {resource_id} cannot provide "
                                 f"minimum amount {min_amount}")
                if max_amount > resource.max_capacity:
                    errors.append(f"Resource {resource_id} max amount "
                                 f"{max_amount} exceeds capacity")
            elif resource.resource_type == ResourceType.CUMULATIVE_RATE:
                # For cumulative resources, we need to check bounds
                if resource.min_value is not None and min_amount < resource.min_value:
                    errors.append(f"Resource {resource_id} minimum amount "
                                 f"below resource minimum")
                if resource.max_value is not None and max_amount > resource.max_value:
                    errors.append(f"Resource {resource_id} maximum amount "
                                 f"exceeds resource maximum")
        
        return errors
    
    def get_resource_statistics(self) -> Dict[str, Any]:
        """Get statistics about resources in the manager."""
        stats = {
            "total_resources": len(self.resources),
            "integer_resources": len(self.get_integer_resources()),
            "cumulative_rate_resources": len(self.get_cumulative_rate_resources()),
            "available_resources": len(self.get_available_resources()),
            "utilization": self.get_all_resource_utilization()
        }
        return stats
    
    def reset_all_resources(self) -> None:
        """Reset all resources to their initial state."""
        for resource in self.resources.values():
            if resource.resource_type == ResourceType.INTEGER:
                resource.current_state.current_value = 0.0
                resource.status = ResourceStatus.AVAILABLE
            elif resource.resource_type == ResourceType.CUMULATIVE_RATE:
                resource.current_state.current_value = resource.initial_value or 0.0
                resource.current_state.rate = 0.0
        
        # Clear usage tracking
        self.resource_usage.clear()
        for resource_id in self.resources.keys():
            self.resource_usage[resource_id] = {}
    
    def clear(self) -> None:
        """Clear all resources from the manager."""
        self.resources.clear()
        self.resource_usage.clear()
