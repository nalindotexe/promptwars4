import pytest
from typing import Any, Dict
from src.telemetry import Zone, StadiumState
from src.agent import CrisisCoordinator

def test_zone_density_calculation() -> None:
    # Test valid density logic
    zone1 = Zone("Gate A", 1500, 500.0)
    assert zone1.calculate_density() == 3.0

    # Test edge case: Zero Navigable Area
    zone2 = Zone("Gate B", 1500, 0.0)
    assert zone2.calculate_density() == 0.0

    # Test edge case: Negative Navigable Area
    zone3 = Zone("Gate C", 1500, -100.0)
    assert zone3.calculate_density() == 0.0

def test_stadium_state_output() -> None:
    state = StadiumState()
    output = state.get_simulated_state()

    assert output["event_name"] == "Semi-Final"
    assert output["location"] == "Dallas Stadium"
    assert "event_date" in output
    assert len(output["zones"]) == 3

    gate_a = next(z for z in output["zones"] if z["name"] == "Gate A")
    assert gate_a["density"] == 3.0

def test_crisis_coordinator_normal_state(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock the API key so the new SDK client initializes without throwing an error
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key_123")
    
    coord = CrisisCoordinator()
    telemetry: Dict[str, Any] = {
        "zones": [
            {"name": "Safe Zone", "current_capacity": 40, "navigable_area": 100.0, "density": 0.4}
        ]
    }
    result = coord.evaluate_state(telemetry)
    assert result["status"] == "normal"
    assert "safe limits" in result["message"]

def test_crisis_coordinator_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock the API key here as well
    monkeypatch.setenv("GEMINI_API_KEY", "fake_test_key_123")
    
    coord = CrisisCoordinator()
    telemetry: Dict[str, Any] = {
        "zones": [
            {"name": "Danger Zone 1", "density": 0.9},
            {"name": "Danger Zone 2", "density": 1.2}
        ]
    }

    def mock_generate_content(*args: Any, **kwargs: Any) -> Any:
        raise Exception("Simulated API Error / Timeout")

    # Mock the new client.models object on the instance
    monkeypatch.setattr(coord.client.models, "generate_content", mock_generate_content)

    result = coord.evaluate_state(telemetry)

    assert result["status"] == "fallback_action_required"
    assert result["plan"]["severity_level"] == "HIGH"
    
    staff_action = result["plan"]["staff_action"]
    assert "Danger Zone 1" in staff_action
    assert "Danger Zone 2" in staff_action
    
    announcements = result["plan"]["public_announcement"]
    assert "english" in announcements
    assert "french" in announcements
    assert "spanish" in announcements