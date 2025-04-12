
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Safe rerun trigger
if st.session_state.get("trigger_rerun"):
    st.session_state["trigger_rerun"] = False
    st.experimental_rerun()

st.set_page_config(page_title="SEV Escalation + Customer Impact", layout="centered")
st.title("SEV Escalation & Customer Impact Calculator")

# Default site thresholds
default_sites = {
    "YXU1": {"ob_units": 10000, "ob_shipments": 5000, "ib_units": 25000, "lph": 100},
    "YYZ2": {"ob_units": 7000, "ob_shipments": 3000, "ib_units": 18000, "lph": 80},
    "LAX9": {"ob_units": 12000, "ob_shipments": 6000, "ib_units": 30000, "lph": 120},
}

if "custom_sites" not in st.session_state:
    st.session_state.custom_sites = {}

all_sites = {**default_sites, **st.session_state.custom_sites}

with st.expander("+ Add Custom Site"):
    new_site = st.text_input("Custom Site Name (e.g., BDL3)")
    ob_units = st.number_input("OB Units Threshold", min_value=1000, value=10000, key="ob_units_custom")
    ob_shipments = st.number_input("OB Shipments Threshold", min_value=1000, value=5000, key="ob_shipments_custom")
    ib_units = st.number_input("IB Units Threshold", min_value=10000, value=25000, key="ib_threshold_input")
    lph = st.number_input("LPH Threshold", min_value=50, value=100, key="lph_custom")
    if st.button("Add Site"):
        if new_site:
            st.session_state.custom_sites[new_site] = {
                "ob_units": ob_units,
                "ob_shipments": ob_shipments,
                "ib_units": ib_units,
                "lph": lph
            }
            st.session_state["trigger_rerun"] = True
            st.success(f"Site {new_site} added!")

if 'log' not in st.session_state:
    st.session_state['log'] = []

tab1, tab2, tab3 = st.tabs(["SEV Escalation", "Customer Impact", "Logs"])

# TAB 1: SEV Escalation Calculator
with tab1:
    st.header("SEV Escalation Calculator")
    site = st.selectbox("Select Site", list(all_sites.keys()))
    thresholds = all_sites[site]

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
        elif (lph >= thresholds['lph'] or ob_units_lost >= thresholds['ob_units'] or
              ob_shipments_missed >= thresholds['ob_shipments'] or ib_units_lost >= thresholds['ib_units']):
            if mitigation == "No" or root_cause_known == "No" or fix_within_30 == "No":
                sev_level = "SEV2"
                reason = "Thresholds exceeded and either no mitigation or unclear root cause."
        elif mitigation == "No" and fix_within_30 == "No":
            sev_level = "SEV2"
            reason = "No mitigation available and fix will exceed 30 minutes."

        st.subheader("Justification Checklist")
        l7_involved = st.checkbox("Site Leadership (L7+) involved")
        attempted_mitigation = st.checkbox("Attempted mitigation")
        workaround = st.checkbox("Workaround in place or attempted")
        repeated_issue = st.checkbox("Similar issue occurred in last 7 days")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['last_log'] = {
            "Time": timestamp,
            "Site": site,
            "SEV": sev_level,
            "LPH": lph,
            "OB Units Lost": ob_units_lost,
            "OB Shipments Missed": ob_shipments_missed,
            "IB Units Lost": ib_units_lost,
            "Mitigation": mitigation,
            "Root Cause Known": root_cause_known,
            "Fix <30 min": fix_within_30,
            "Checklist L7": l7_involved,
            "Checklist Mitigation": attempted_mitigation,
            "Repeat Issue": repeated_issue,
            "SEV Reason": reason
        }

        st.markdown("### SEV Summary")
        st.markdown(f"- SEV Level: **{sev_level}**")
        st.markdown(f"- Reason: {reason}")
        st.markdown(f"- Time: {timestamp}")
        st.markdown(f"- Site: {site}")

# TAB 2: Customer Impact
with tab2:
    st.header("Customer Impact Calculator")
    ib_units = st.number_input("Inbound Units Lost", min_value=0, key="ib_units_tab2")
    ib_throughput = st.number_input("Avg IB Throughput/hr", value=500, min_value=1, key="ib_throughput")
    ib_delay = ib_units / ib_throughput
    ob_units = st.number_input("Outbound Units Lost", min_value=0, key="ob_units")
    ob_shipments = st.number_input("Outbound Shipments Missed", min_value=0, key="ob_shipments")
    units_per_order = st.number_input("Avg Units per Order", value=3, min_value=1, key="units_order")
    orders_affected = ob_units / units_per_order if units_per_order else 0

    st.markdown(f"**IB Delay:** {ib_delay:.2f} hrs")
    st.markdown(f"**Estimated OB Orders Affected:** {orders_affected:.0f}")
    st.markdown(f"**Shipments Missed:** {ob_shipments}")

    if st.button("Log Full Entry"):
        if 'last_log' in st.session_state:
            log_entry = st.session_state['last_log'].copy()
            log_entry["IB Delay (hrs)"] = round(ib_delay, 2)
            log_entry["OB Orders Affected"] = round(orders_affected, 0)
            st.session_state['log'].append(log_entry)
            st.success("Full entry logged!")
        else:
            st.warning("Please complete the SEV Escalation tab before logging.")

# TAB 3: Logs + Charts
with tab3:
    st.header("Event Logs")
    if st.session_state['log']:
        df = pd.DataFrame(st.session_state['log'])
        st.dataframe(df)

        st.subheader("SEV Level Distribution")
        sev_counts = df["SEV"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(sev_counts, labels=sev_counts.index, autopct="%1.1f%%", startangle=90)
        ax1.axis("equal")
        st.pyplot(fig1)

        st.subheader("LPH Impact by Event")
        fig2, ax2 = plt.subplots()
        ax2.bar(df["Time"], df["LPH"])
        plt.xticks(rotation=45, ha='right')
        ax2.set_ylabel("LPH")
        ax2.set_title("LPH Impact Over Time")
        st.pyplot(fig2)

        st.subheader("Events Over Time")
        df["Date"] = pd.to_datetime(df["Time"]).dt.date
        time_counts = df["Date"].value_counts().sort_index()
        fig3, ax3 = plt.subplots()
        ax3.plot(time_counts.index, time_counts.values, marker='o')
        ax3.set_ylabel("Events")
        ax3.set_title("Number of Events per Day")
        st.pyplot(fig3)

        csv = df.drop(columns=["Date"]).to_csv(index=False).encode("utf-8")
        st.download_button("Download Logs as CSV", csv, "sev_logs.csv", "text/csv")
    else:
        st.info("No logs available yet.")
