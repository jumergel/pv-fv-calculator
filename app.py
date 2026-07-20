import streamlit as st
from calculator import calculate
import pandas as pd
import altair as alt

#layout of the page; two columns, left for inputs, right for results
st.set_page_config(layout="wide")
#center and give padding to the content
st.html("styles.css")

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

#donut chart showing the value breakdown
def create_breakdown_chart(timeline, starting_amount, total, value_type):
    if value_type == "FV":
        periodic_deposits = timeline["Annual Cash Flow"].sum()
        interest = total - starting_amount - periodic_deposits

        breakdown = pd.DataFrame({
            "Category": ["Starting Amount", "Periodic Deposits", "Interest"],
            "Amount": [starting_amount, periodic_deposits, max(interest, 0)]
        })

    else:
        future_cash_flow_pv = total - starting_amount

        breakdown = pd.DataFrame({
            "Category": ["Starting Amount", "PV of Future Cash Flows"],
            "Amount": [starting_amount, max(future_cash_flow_pv, 0)]
        })

    breakdown = breakdown[breakdown["Amount"] > 0]

    if breakdown["Amount"].sum() == 0:
        return None

    breakdown["Percent"] = breakdown["Amount"] / breakdown["Amount"].sum()

    base = alt.Chart(breakdown).encode(
        theta=alt.Theta("Amount:Q", stack=True),
        color=alt.Color("Category:N", legend=alt.Legend(title=None)),
        tooltip=[
            alt.Tooltip("Category:N", title="Category"),
            alt.Tooltip("Amount:Q", title="Amount", format="$,.2f"),
            alt.Tooltip("Percent:Q", title="Percent", format=".1%")
        ]
    )

    donut = base.mark_arc(innerRadius=55, outerRadius=95)

    labels = base.mark_text(radius=75, size=14, fontWeight="bold").encode(
        text=alt.Text("Percent:Q", format=".0%"),
        color=alt.value("white")
    )

    return (donut + labels).properties(width=300, height=230)


#MAIN PROGRAM
#!!!!!!!!
st.title("PV / FV Calculator")

#creates the left input column and right results column
left_column, right_column = st.columns(2, gap="large")


#LEFT COLUMN
with left_column:

    #INPUTS
    value_type = st.selectbox("PV or FV?", ["PV", "FV"])
    starting_amount = st.number_input("Starting amount", value=0)
    periods = st.number_input("Discrete no-growth periods", min_value=0, step=1, value=0)
    rate = st.number_input("Discount rate (e.g. 0.07 for 7%)", value=0.07, format="%g")
    cf = st.number_input("Base cash flow", value=100)
    growth_phases = st.number_input("Number of growth phases (0 for none)", min_value=0, step=1)


    #PHASE INPUTS according to number of growth phases inputted
    phases = []

    for i in range(int(growth_phases)): #creates a phase input box for number of growth_phases
        st.subheader(f"Phase {i + 1}")

        growth = st.number_input(f"Phase {i + 1} growth rate", value=None, format="%g", key=f"growth_{i}")

        if value_type == "PV" and i == growth_phases - 1:
            phase_type = st.selectbox(f"Phase {i + 1} type", ["annuity", "perpetuity"], key=f"type_{i}")
        else:
            phase_type = "annuity"

        if phase_type == "annuity":
            length = st.number_input(f"Phase {i + 1} length (years)", min_value=1, step=1, value=None, key=f"length_{i}")
        else:
            length = None

        phases.append({"growth": growth, "type": phase_type, "length": length})

    calculate_button = st.button("Calculate", use_container_width=True)


#RIGHT COLUMN
with right_column:

    st.subheader("Results")

    if calculate_button:
        basic_inputs_missing = periods is None or rate is None or cf is None or growth_phases is None

        #make sure all inputs inputted
        phase_inputs_missing = any(phase["growth"] is None or (phase["type"] == "annuity" and phase["length"] is None) for phase in phases)

        if basic_inputs_missing or phase_inputs_missing:
            st.error("Please fill in all input boxes.")

        else:
            try:
                #run our program calculator.py based on the inputs
                total, log = calculate(value_type, int(periods), rate, cf, int(growth_phases), phases, starting_amount)
                
                for line in log:
                    st.write(line)

                timeline = create_growth_timeline(int(periods), rate, cf, phases)
                st.subheader("Money Growth Over Time")
                st.line_chart(timeline, x="Year", y=["Annual Cash Flow", "Accumulated Value"], x_label="Year", y_label="Value ($)")
                st.subheader("Value Breakdown")
                breakdown_chart = create_breakdown_chart(timeline, starting_amount, total, value_type)
                st.altair_chart(breakdown_chart, width="stretch")

            except ValueError as e:
                st.error(str(e))