
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Severity Impact Calculator", layout="centered")

st.title("Severity Impact Calculator")
st.subheader("Calculate severity for Lost Production Hours (LPH), Volume Miss, and CE Misses")

# Input Section
area = st.text_input("Area/Asset Name")
shift_date = st.date_input("Shift Date", datetime.today())
lph = st.number_input("Lost Production Hours (LPH)", min_value=0.0, step=0.1)
volume_missed = st.number_input("Volume Missed", min_value=0)
ce_misses = st.number_input("CE Misses", min_value=0)

# Severity thresholds
def classify_severity_lph(val):
    return 1 if val <= 1 else 2 if val <= 2 else 3

def classify_severity_volume(val):
    return 1 if val <= 100 else 2 if val <= 300 else 3

def classify_severity_ce(val):
    return 1 if val <= 1 else 2 if val <= 3 else 3

# Calculation
if st.button("Calculate Severity Impact"):
    sev_lph = classify_severity_lph(lph)
    sev_volume = classify_severity_volume(volume_missed)
    sev_ce = classify_severity_ce(ce_misses)

    total_score = (3 * sev_lph) + (2 * sev_volume) + (1 * sev_ce)

    if total_score <= 5:
        severity_level = "SEV3 - Low"
        color = "green"
    elif total_score <= 7:
        severity_level = "SEV2 - Medium"
        color = "orange"
    else:
        severity_level = "SEV1 - High"
        color = "red"

    st.markdown(f"### Severity Level: <span style='color:{color}'>{severity_level}</span>", unsafe_allow_html=True)
    st.markdown(f"- **Total Score:** {total_score}")
    st.markdown(f"- **LPH Severity:** {sev_lph} (x3)")
    st.markdown(f"- **Volume Severity:** {sev_volume} (x2)")
    st.markdown(f"- **CE Severity:** {sev_ce} (x1)")

    st.success("Severity score calculated successfully!")
