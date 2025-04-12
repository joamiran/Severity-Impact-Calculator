
import streamlit as st

st.set_page_config(page_title="SEV Escalation + Customer Impact", layout="centered")

st.title("SEV Escalation & Customer Impact Calculator")

# Tabs
tab1, tab2 = st.tabs(["SEV Escalation", "Customer Impact"])

# --- SEV ESCALATION TAB ---
with tab1:
    st.header("SEV Escalation Calculator")

    multi_site = st.radio("Are 2 or more sites impacted?", ["No", "Yes"])
    full_ob_down = st.radio("Is the entire Outbound path down for more than 1 hour with no ETR?", ["No", "Yes"])
    lph = st.number_input("How many Lost Production Hours (LPH)?", min_value=0)
    ob_units_lost = st.number_input("How many outbound units lost?", min_value=0)
    ob_shipments_missed = st.number_input("How many outbound shipments missed?", min_value=0)
    ib_units_lost = st.number_input("How many inbound units lost?", min_value=0)
    mitigation = st.radio("Is there operational mitigation in place?", ["Yes", "No"])
    root_cause_known = st.radio("Is the root cause known within 20 minutes?", ["Yes", "No"])
    fix_within_30 = st.radio("Is the issue repairable within 30 minutes?", ["Yes", "No"])

    if st.button("Calculate SEV Level"):
        sev_level = "SEV3"
        reason = "Issue is repairable within 30 minutes or mitigation is in place."

        if multi_site == "Yes" or full_ob_down == "Yes":
            sev_level = "SEV1"
            reason = "Multiple sites impacted or full Outbound path is down without ETR."
        elif lph >= 100 or ob_units_lost >= 10000 or ob_shipments_missed >= 5000 or ib_units_lost >= 25000:
            if mitigation == "No" or root_cause_known == "No" or fix_within_30 == "No":
                sev_level = "SEV2"
                reason = "Thresholds exceeded and either no mitigation or unclear root cause."
        elif mitigation == "No" and fix_within_30 == "No":
            sev_level = "SEV2"
            reason = "No mitigation available and fix will exceed 30 minutes."

        st.markdown(f"### Severity Level: **{sev_level}**")
        st.markdown(f"**Reason:** {reason}")

# --- CUSTOMER IMPACT TAB ---
with tab2:
    st.header("Customer Impact Calculator")

    st.subheader("Inbound (IB)")
    ib_units = st.number_input("Units lost in Inbound", min_value=0, key="ib_units")
    ib_avg_throughput = st.number_input("Avg. IB throughput per hour", min_value=1, value=500, key="ib_throughput")
    ib_hours_lost = ib_units / ib_avg_throughput
    st.markdown(f"**Estimated hours of stow delay:** {ib_hours_lost:.2f} hrs")

    st.divider()

    st.subheader("Outbound (OB)")
    ob_units = st.number_input("Outbound units lost", min_value=0, key="ob_units")
    ob_shipments = st.number_input("Shipments missed", min_value=0, key="ob_shipments")
    units_per_order = st.number_input("Average units per order", min_value=1, value=3, key="units_per_order")

    est_orders_affected = ob_units / units_per_order if units_per_order else 0
    st.markdown(f"**Estimated customer orders affected:** {est_orders_affected:.0f}")
    st.markdown(f"**Shipments missed:** {ob_shipments}")
