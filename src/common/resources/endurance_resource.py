"""
Endurance Resource definitions for robot scheduling.
Redesigned for single robot with integer and cumulative rate resources.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class ResourceType(Enum):
    """Types of resources available for the Endurance robot."""
    INTEGER = "integer"  # Discrete resource with max capacity
    CUMULATIVE_RATE = "cumulative_rate"  # Continuous resource with rate changes


class ResourceStatus(Enum):
    """Status of a resource."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


@dataclass
class ResourceState:
    """Represents the current state of a resource."""
    current_value: float
    rate: float = 0.0  # Current rate of change (for cumulative resources)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnduranceResource:
    """
    Represents a resource for the Endurance robot.
    
    Two types:
    1. INTEGER: Discrete resource with max capacity (e.g., tools, storage slots)
    2. CUMULATIVE_RATE: Continuous resource with rate changes (e.g., battery, fuel)
    """
    
    id: str
    name: str
    description: str
    resource_type: ResourceType
    
    # For INTEGER resources
    max_capacity: Optional[float] = None  # Maximum capacity (required for INTEGER)
    
    # For CUMULATIVE_RATE resources
    initial_value: Optional[float] = None  # Starting value
    min_value: Optional[float] = None  # Minimum allowed value
    max_value: Optional[float] = None  # Maximum allowed value
    
    # Current state
    current_state: ResourceState = field(default_factory=lambda: ResourceState(0.0))
    status: ResourceStatus = ResourceStatus.AVAILABLE
    
    # Additional metadata
    location: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate resource configuration after initialization."""
        self._validate_configuration()
        self._initialize_state()
    
    def _validate_configuration(self):
        """Validate that resource configuration is consistent."""
        if self.resource_type == ResourceType.INTEGER:
            if self.max_capacity is None:
                raise ValueError("INTEGER resources must have max_capacity")
            if self.max_capacity <= 0:
                raise ValueError("max_capacity must be positive")
        elif self.resource_type == ResourceType.CUMULATIVE_RATE:
            if self.initial_value is None:
                raise ValueError("CUMULATIVE_RATE resources must have initial_value")
            if self.min_value is not None and self.max_value is not None:
                if self.min_value > self.max_value:
                    raise ValueError("min_value cannot exceed max_value")
    
    def _initialize_state(self):
        """Initialize the resource state based on type."""
        if self.resource_type == ResourceType.INTEGER:
            self.current_state.current_value = 0.0
        elif self.resource_type == ResourceType.CUMULATIVE_RATE:
            self.current_state.current_value = self.initial_value or 0.0
    
    @classmethod
    def create_integer_resource(
        cls,
        name: str,
        description: str,
        max_capacity: float,
        **kwargs
    ) -> "EnduranceResource":
        """Create an integer resource (discrete capacity)."""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            resource_type=ResourceType.INTEGER,
            max_capacity=max_capacity,
            **kwargs
        )
    
    @classmethod
    def create_cumulative_rate_resource(
        cls,
        name: str,
        description: str,
        initial_value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        **kwargs
    ) -> "EnduranceResource":
        """Create a cumulative rate resource (continuous with rate changes)."""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            resource_type=ResourceType.CUMULATIVE_RATE,
            initial_value=initial_value,
            min_value=min_value,
            max_value=max_value,
            **kwargs
        )
    
    def can_allocate(self, amount: float) -> bool:
        """Check if the resource can allocate the specified amount."""
        if self.status != ResourceStatus.AVAILABLE:
            return False
        
        if self.resource_type == ResourceType.INTEGER:
            return (self.current_state.current_value + amount <= 
                    self.max_capacity)
        elif self.resource_type == ResourceType.CUMULATIVE_RATE:
            new_value = self.current_state.current_value + amount
            if self.min_value is not None and new_value < self.min_value:
                return False
            if self.max_value is not None and new_value > self.max_value:
                return False
            return True
        
        return False
    
    def allocate(self, amount: float) -> bool:
        """Allocate the specified amount of the resource."""
        if not self.can_allocate(amount):
            return False
        
        self.current_state.current_value += amount
        self.current_state.last_updated = datetime.now()
        
        # Update status for integer resources
        if (self.resource_type == ResourceType.INTEGER and
                self.current_state.current_value >= self.max_capacity):
            self.status = ResourceStatus.IN_USE
        
        return True
    
    def deallocate(self, amount: float) -> bool:
        """Deallocate the specified amount of the resource."""
        if self.resource_type == ResourceType.INTEGER:
            if self.current_state.current_value < amount:
                return False
            self.current_state.current_value -= amount
        elif self.resource_type == ResourceType.CUMULATIVE_RATE:
            # For cumulative resources, deallocation might not make sense
            # This could be used for "returning" resources
            self.current_state.current_value -= amount
        
        self.current_state.last_updated = datetime.now()
        
        # Update status for integer resources
        if (self.resource_type == ResourceType.INTEGER and
                self.current_state.current_value < self.max_capacity and
                self.status == ResourceStatus.IN_USE):
            self.status = ResourceStatus.AVAILABLE
        
        return True
    
    def set_rate(self, rate: float) -> None:
        """Set the rate of change for cumulative rate resources."""
        if self.resource_type == ResourceType.CUMULATIVE_RATE:
            self.current_state.rate = rate
            self.current_state.last_updated = datetime.now()
    
    def update_value(self, delta_time: float) -> None:
        """Update the resource value based on current rate and time delta."""
        if self.resource_type == ResourceType.CUMULATIVE_RATE:
            new_value = self.current_state.current_value + (self.current_state.rate * delta_time)
            
            # Apply bounds
            if self.min_value is not None:
                new_value = max(new_value, self.min_value)
            if self.max_value is not None:
                new_value = min(new_value, self.max_value)
            
            self.current_state.current_value = new_value
            self.current_state.last_updated = datetime.now()
    
    @property
    def available_capacity(self) -> float:
        """Get the available capacity of the resource."""
        if self.resource_type == ResourceType.INTEGER:
            return self.max_capacity - self.current_state.current_value
        elif self.resource_type == ResourceType.CUMULATIVE_RATE:
            if self.max_value is not None:
                return (self.max_value - 
                        self.current_state.current_value)
            return float('inf')
        return 0.0
    
    @property
    def utilization(self) -> float:
        """Get the utilization percentage of the resource."""
        if self.resource_type == ResourceType.INTEGER:
            if self.max_capacity == 0:
                return 0.0
            return self.current_state.current_value / self.max_capacity
        elif self.resource_type == ResourceType.CUMULATIVE_RATE:
            if self.max_value is not None and self.min_value is not None:
                if self.max_value == self.min_value:
                    return 0.0
                return ((self.current_state.current_value - self.min_value) / 
                        (self.max_value - self.min_value))
            return 0.0
        return 0.0
    
    def is_within_bounds(self) -> bool:
        """Check if the current value is within the allowed bounds."""
        if self.resource_type == ResourceType.INTEGER:
            return 0 <= self.current_state.current_value <= self.max_capacity
        elif self.resource_type == ResourceType.CUMULATIVE_RATE:
            if self.min_value is not None and self.current_state.current_value < self.min_value:
                return False
            if self.max_value is not None and self.current_state.current_value > self.max_value:
                return False
            return True
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type.value,
            "max_capacity": self.max_capacity,
            "initial_value": self.initial_value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "current_state": {
                "current_value": self.current_state.current_value,
                "rate": self.current_state.rate,
                "last_updated": self.current_state.last_updated.isoformat(),
                "metadata": self.current_state.metadata
            },
            "status": self.status.value,
            "location": self.location,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnduranceResource":
        """Create resource from dictionary representation."""
        current_state_data = data.get("current_state", {})
        current_state = ResourceState(
            current_value=current_state_data.get("current_value", 0.0),
            rate=current_state_data.get("rate", 0.0),
            last_updated=datetime.fromisoformat(
                current_state_data.get("last_updated", datetime.now().isoformat())
            ),
            metadata=current_state_data.get("metadata", {})
        )
        
        resource = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            resource_type=ResourceType(data["resource_type"]),
            max_capacity=data.get("max_capacity"),
            initial_value=data.get("initial_value"),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            current_state=current_state,
            status=ResourceStatus(data.get("status", "available")),
            location=data.get("location"),
            capabilities=data.get("capabilities", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )
        
        return resource
