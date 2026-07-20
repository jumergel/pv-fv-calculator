import streamlit as st
from calculator import calculate
import pandas as pd

#graph
def create_growth_timeline(periods, rate, cf, phases, perpetuity_years=20):
    timeline = [{"Year": 0, "Annual Cash Flow": 0.0, "Accumulated Value": 0.0}]

    year = 0
    current_cf = cf
    accumulated_value = 0.0

    # Discrete no-growth periods
    for _ in range(int(periods)):
        year += 1
        accumulated_value = accumulated_value * (1 + rate) + current_cf

        timeline.append({
            "Year": year,
            "Annual Cash Flow": current_cf,
            "Accumulated Value": accumulated_value
        })

    # Growth phases
    for phase in phases:
        growth = phase["growth"]

        if phase["type"] == "perpetuity":
            phase_length = perpetuity_years
        else:
            phase_length = int(phase["length"])

        for _ in range(phase_length):
            year += 1
            current_cf = current_cf * (1 + growth)
            accumulated_value = accumulated_value * (1 + rate) + current_cf

            timeline.append({
                "Year": year,
                "Annual Cash Flow": current_cf,
                "Accumulated Value": accumulated_value
            })

    return pd.DataFrame(timeline)

st.title("PV / FV Calculator")

value_type = st.selectbox("PV or FV?", ["PV", "FV"])
periods = st.number_input("Discrete no-growth periods", min_value=0, step=1, value=None)
rate = st.number_input("Discount rate (e.g. 0.07 for 7%)", value=0.07, format="%g")
cf = st.number_input("Base cash flow", value=None)
growth_phases = st.number_input("Number of growth phases (0 for none)", min_value=0, step=1)

phases = []
for i in range(int(growth_phases)): #creates a phase input box for number of growth_phases
    st.subheader(f"Phase {i + 1}")
    growth = st.number_input(f"Phase {i + 1} growth rate", value=None, format="%g", key=f"growth_{i}")

    if value_type == "PV" and i == growth_phases - 1:
        phase_type = st.selectbox(f"Phase {i + 1} type", ["annuity", "perpetuity"], key=f"type_{i}")
    else:
        phase_type = "annuity"

    if phase_type == "annuity":
        length = st.number_input(f"Phase {i + 1} length (years)", min_value=1, step=1, key=f"length_{i}")
    else:
        length = None

    phases.append({"growth": growth, "type": phase_type, "length": length})

if st.button("Calculate"):
    basic_inputs_missing = (
        periods is None
        or rate is None
        or cf is None
        or growth_phases is None
    )

    phase_inputs_missing = any(phase["growth"] is None or (phase["type"] == "annuity"and phase["length"] is None )for phase in phases)

    if basic_inputs_missing or phase_inputs_missing:
        st.error("Please fill in all input boxes.")
    else:
        try:
            total, log = calculate(value_type, int(periods), rate, cf, int(growth_phases), phases)
            for line in log:
                st.write(line)
            timeline = create_growth_timeline(int(periods), rate, cf, phases)
            st.subheader("Money Growth Over Time")
            st.line_chart(timeline,x="Year", y=["Annual Cash Flow", "Accumulated Value"],x_label="Year",y_label="Value ($)")

        except ValueError as e:
            st.error(str(e))
