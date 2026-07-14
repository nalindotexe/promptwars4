import html
from typing import Any, Dict

import streamlit as st  # type: ignore

from src.agent import CrisisCoordinator
from src.telemetry import StadiumState

st.set_page_config(page_title="StadiumSync AI", layout="wide")

@st.cache_data  # type: ignore
def fetch_telemetry() -> Dict[str, Any]:
    state = StadiumState()
    return state.get_simulated_state()

@st.cache_data  # type: ignore
def evaluate_crisis(telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
    coordinator = CrisisCoordinator()
    return coordinator.evaluate_state(telemetry_data)

def render_kpi_card(zone: Dict[str, Any]) -> None:
    name = html.escape(str(zone.get("name", "")))
    capacity = zone.get("current_capacity", 0)
    density = zone.get("density", 0.0)
    
    card_html = (
        "<div style='background-color: #0b0c10; padding: 1.5rem; border-radius: 8px; border: 1px solid #1f2937;'>"
        f"<h3 style='color: #94a3b8; font-size: 1.25rem; margin-top: 0; font-weight: 600;'>{name}</h3>"
        f"<p style='color: #94a3b8; font-size: 1rem; margin-bottom: 0.5rem;'>Capacity: {capacity}</p>"
        f"<p style='color: #94a3b8; font-size: 1rem; margin-bottom: 0;'>Density: {density:.2f}</p>"
        "</div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)

def main() -> None:
    st.title("StadiumSync AI Command Center")
    
    telemetry = fetch_telemetry()
    
    event_name = html.escape(str(telemetry.get("event_name", "")))
    st.header(f"Event: {event_name}")
    
    zones = telemetry.get("zones", [])
    
    if zones:
        cols = st.columns(len(zones))
        for idx, zone in enumerate(zones):
            with cols[idx]:
                render_kpi_card(zone)
                
    st.header("Crisis Engine Status")
    
    crisis_state = evaluate_crisis(telemetry)
    status = crisis_state.get("status", "unknown")
    
    if status == "normal":
        msg = html.escape(str(crisis_state.get("message", "")))
        normal_html = (
            "<div style='background-color: #0b0c10; padding: 1rem; border-radius: 8px; border: 1px solid #059669;'>"
            f"<p style='color: #94a3b8; font-size: 1rem; margin: 0;'>{msg}</p>"
            "</div>"
        )
        st.markdown(normal_html, unsafe_allow_html=True)
    else:
        plan = crisis_state.get("plan", {})
        sev = html.escape(str(plan.get("severity_level", "")))
        staff = html.escape(str(plan.get("staff_action", "")))
        announcements = plan.get("public_announcement", {})
        eng = html.escape(str(announcements.get("english", "")))
        fra = html.escape(str(announcements.get("french", "")))
        spa = html.escape(str(announcements.get("spanish", "")))
        
        alert_html = (
            "<div style='background-color: #0b0c10; padding: 1.5rem; border-radius: 8px; border: 1px solid #dc2626;'>"
            f"<h3 style='color: #dc2626; margin-top: 0;'>CRISIS ALERT: {sev}</h3>"
            "<p style='color: #94a3b8; font-weight: bold;'>Staff Action:</p>"
            f"<p style='color: #94a3b8;'>{staff}</p>"
            "<hr style='border-color: #1f2937;' />"
            "<p style='color: #94a3b8; font-weight: bold;'>Public Announcements:</p>"
            "<ul style='color: #94a3b8;'>"
            f"<li><strong>EN:</strong> {eng}</li>"
            f"<li><strong>FR:</strong> {fra}</li>"
            f"<li><strong>ES:</strong> {spa}</li>"
            "</ul>"
            "</div>"
        )
        st.markdown(alert_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
