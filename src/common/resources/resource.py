"""
Resource definitions for robot scheduling.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import uuid


class ResourceType(Enum):
    """Types of resources available for robot tasks."""
    ROBOT = "robot"
    TOOL = "tool"
    STORAGE = "storage"
    TRANSPORT = "transport"
    POWER = "power"
    COMMUNICATION = "communication"


class ResourceStatus(Enum):
    """Status of a resource."""
    AVAILABLE = "available"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    RESERVED = "reserved"


@dataclass
class Resource:
    """Represents a resource that can be used by robots."""
    
    id: str
    resource_type: ResourceType
    name: str
    capacity: float = 1.0
    current_usage: float = 0.0
    capabilities: List[str] = None
    location: Optional[str] = None
    status: ResourceStatus = ResourceStatus.AVAILABLE
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @classmethod
    def create(
        cls,
        resource_type: ResourceType,
        name: str,
        capacity: float = 1.0,
        **kwargs
    ) -> "Resource":
        """Create a new resource with a generated ID."""
        return cls(
            id=str(uuid.uuid4()),
            resource_type=resource_type,
            name=name,
            capacity=capacity,
            **kwargs
        )
    
    @property
    def available_capacity(self) -> float:
        """Get the available capacity of the resource."""
        return self.capacity - self.current_usage
    
    @property
    def utilization(self) -> float:
        """Get the utilization percentage of the resource."""
        if self.capacity == 0:
            return 0.0
        return self.current_usage / self.capacity
    
    def can_allocate(self, amount: float) -> bool:
        """Check if the resource can allocate the specified amount."""
        return (self.status == ResourceStatus.AVAILABLE and 
                self.available_capacity >= amount)
    
    def allocate(self, amount: float) -> bool:
        """Allocate the specified amount of the resource."""
        if self.can_allocate(amount):
            self.current_usage += amount
            if self.current_usage >= self.capacity:
                self.status = ResourceStatus.BUSY
            return True
        return False
    
    def deallocate(self, amount: float) -> bool:
        """Deallocate the specified amount of the resource."""
        if self.current_usage >= amount:
            self.current_usage -= amount
            if self.current_usage < self.capacity and self.status == ResourceStatus.BUSY:
                self.status = ResourceStatus.AVAILABLE
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary representation."""
        return {
            "id": self.id,
            "resource_type": self.resource_type.value,
            "name": self.name,
            "capacity": self.capacity,
            "current_usage": self.current_usage,
            "capabilities": self.capabilities,
            "location": self.location,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resource":
        """Create resource from dictionary representation."""
        return cls(
            id=data["id"],
            resource_type=ResourceType(data["resource_type"]),
            name=data["name"],
            capacity=data["capacity"],
            current_usage=data["current_usage"],
            capabilities=data.get("capabilities", []),
            location=data.get("location"),
            status=ResourceStatus(data["status"]),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"])
        )
