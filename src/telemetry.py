import datetime
from typing import Any, Dict, List


class Zone:
    def __init__(self, name: str, current_capacity: int, navigable_area: float) -> None:
        self.name: str = name
        self.current_capacity: int = current_capacity
        self.navigable_area: float = navigable_area

    def calculate_density(self) -> float:
        if self.navigable_area <= 0.0:
            return 0.0
        return float(self.current_capacity) / self.navigable_area

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "current_capacity": self.current_capacity,
            "navigable_area": self.navigable_area,
            "density": self.calculate_density(),
        }


class StadiumState:
    def __init__(self) -> None:
        self.event_name: str = "Semi-Final"
        self.location: str = "Dallas Stadium"
        self.event_date: datetime.date = datetime.date(2026, 7, 14)
        self.zones: List[Zone] = [
            Zone(name="Gate A", current_capacity=1500, navigable_area=500.0),
            Zone(name="Concourse B", current_capacity=3200, navigable_area=1200.0),
            Zone(name="VIP Lounge", current_capacity=150, navigable_area=300.0),
        ]

    def get_simulated_state(self) -> Dict[str, Any]:
        return {
            "event_name": self.event_name,
            "location": self.location,
            "event_date": self.event_date.isoformat(),
            "zones": [zone.to_dict() for zone in self.zones],
        }