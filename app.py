import streamlit as st
from calculator import calculate

st.title("PV / FV Calculator")

value_type = st.selectbox("PV or FV?", ["PV", "FV"])
periods = st.number_input("Discrete no-growth periods", min_value=0, step=1)
rate = st.number_input("Discount rate (e.g. 0.07 for 7%)", value=0.07, format="%.4f")
cf = st.number_input("Base cash flow", value=0.0)
growth_phases = st.number_input("Number of growth phases (0 for none)", min_value=0, step=1)

phases = []
for i in range(int(growth_phases)):
    st.subheader(f"Phase {i + 1}")
    growth = st.number_input(f"Phase {i + 1} growth rate", value=0.0, format="%.4f", key=f"growth_{i}")

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
    try:
        total, log = calculate(value_type, int(periods), rate, cf, int(growth_phases), phases)
        for line in log:
            st.write(line)
    except ValueError as e:
        st.error(str(e))
