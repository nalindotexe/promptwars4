import html
from typing import Any, Dict

import streamlit as st

from src.agent import CrisisCoordinator
from src.telemetry import StadiumState

st.set_page_config(page_title="StadiumSync AI", layout="wide")


@st.cache_data
def fetch_telemetry() -> Dict[str, Any]:
    state = StadiumState()
    return state.get_simulated_state()


@st.cache_data
def evaluate_crisis_by_event(event_name: str, location: str) -> Dict[str, Any]:
    """Uses primitive types as cache keys to eliminate dictionary serialization lag."""
    state = StadiumState()
    coordinator = CrisisCoordinator()
    return coordinator.evaluate_state(state.get_simulated_state())


def render_kpi_card(zone: Dict[str, Any]) -> None:
    # Uses native container with border for accessible, secure layout
    with st.container(border=True):
        st.subheader(str(zone.get("name", "")))
        st.write(f"Capacity: {zone.get('current_capacity', 0)}")
        st.write(f"Density: {zone.get('density', 0.0):.2f}")


def main() -> None:
    st.title("StadiumSync AI Command Center")

    telemetry = fetch_telemetry()

    event_name = html.escape(str(telemetry.get("event_name", "")))
    location = html.escape(str(telemetry.get("location", "")))
    st.header(f"Event: {event_name}")

    zones = telemetry.get("zones", [])

    if zones:
        cols = st.columns(len(zones))
        for idx, zone in enumerate(zones):
            with cols[idx]:
                render_kpi_card(zone)

    st.header("Crisis Engine Status")

    # Pass primitive strings to avoid Streamlit pickling overhead
    crisis_state = evaluate_crisis_by_event(event_name, location)
    status = crisis_state.get("status", "unknown")

    if status == "normal":
        st.info(str(crisis_state.get("message", "")))
    else:
        plan = crisis_state.get("plan", {})
        sev = html.escape(str(plan.get("severity_level", "")))
        staff = html.escape(str(plan.get("staff_action", "")))
        announcements = plan.get("public_announcement", {})
        eng = html.escape(str(announcements.get("english", "")))
        fra = html.escape(str(announcements.get("french", "")))
        spa = html.escape(str(announcements.get("spanish", "")))

        # Native error alert triggers WCAG 2.1 AA alert role
        with st.container(border=True):
            st.error(f"🚨 CRISIS ALERT: {sev}")
            st.markdown("**Staff Action:**")
            st.write(staff)
            st.divider()
            st.markdown("**Public Announcements:**")
            st.write(f"**EN:** {eng}")
            st.write(f"**FR:** {fra}")
            st.write(f"**ES:** {spa}")


if __name__ == "__main__":
    main()