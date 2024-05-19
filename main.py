import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.title(":green[Mortgage Repayments Calculator]")

st.write("## :blue[Input Data]")
col1, col2 = st.columns(2)
home_value = col1.number_input("Purchase Value", min_value=0, value=5000000)
deposit = col1.number_input("Down Payment", min_value=0, value=0)
interest_rate = col2.number_input("Interest Rate (in %)", min_value=0.0, value=8.6)
loan_term = col2.number_input("Loan Term (in years)", min_value=1, value=25)

st.divider()

# Calculate the repayments.
loan_amount = home_value - deposit
monthly_interest_rate = (interest_rate / 100) / 12
number_of_payments = loan_term * 12
monthly_payment = (
    loan_amount
    * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
    / ((1 + monthly_interest_rate) ** number_of_payments - 1)
)

# Display the repayments.
total_payments = monthly_payment * number_of_payments
total_interest = total_payments - loan_amount

st.write(f"#### Calculated Loan Amount = :red[Rs. {loan_amount}]")

st.write("## :blue[Normal Repayments]")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Monthly Repayments", value=f"Rs. {monthly_payment:,.2f}")
col2.metric(label="Total Repayments", value=f"Rs. {total_payments:,.0f}")
col3.metric(label="Total Interest", value=f"Rs. {total_interest:,.0f}")
col4.metric(label="Loan PaidUP in", value=f"{loan_term} years")


# Create a data-frame with the payment schedule.
schedule = []
remaining_balance = loan_amount

for i in range(1, number_of_payments + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance -= principal_payment
    year = math.ceil(i / 12)  # Calculate the year into the loan
    schedule.append(
        [
            i,
            round(monthly_payment,0),
            round(principal_payment,0),
            round(interest_payment,0),
            round(remaining_balance,0),
            year,
        ]
    )

df = pd.DataFrame(
    schedule,
    columns=["Month", "Payment", "Principal", "Interest", "Remaining Balance", "Year"],
)

# st.write(df)

# Display the data-frame as a chart.
chart1, chart2 = st.columns(2)
with chart1:
    st.write("#### Payment Schedule")
    payments_df = df[["Year", "Remaining Balance"]].groupby("Year").min()
    st.line_chart(payments_df)
with chart2:
    st.write("#### Breakeven Point for Principal vs Interest")
    st.line_chart(df, x='Year', y=["Principal", "Interest"])
        

st.divider()

### ----------------
st.write(f"## :blue[What happens if you pay just ONE ADDITIONAL EMI at year end every year?]")

col1, col2 = st.columns(2)
# step_up_perc = (col1.number_input("Step Up Percentage", min_value=0, value=10)) / 100
pay_one_extra_emi_per_year = col1.number_input("Pay just ONE ADDITIONAL EMI at year end", min_value=0.0, value=df.iloc[-1]['Payment'])
increase_per_year_emi = col2.number_input("Try if you make if n times EMI per year", min_value=1, value=1)

pay_one_extra_emi_per_year = pay_one_extra_emi_per_year * increase_per_year_emi
# st.write(step_up_perc, pay_one_extra_emi_per_year)

number_of_payments = number_of_payments + increase_per_year_emi

# Display the repayments.
total_payments = (monthly_payment * number_of_payments) + pay_one_extra_emi_per_year
total_interest = total_payments - loan_amount

# Create a data-frame with the payment schedule.
new_schedule = []
remaining_balance = loan_amount
year = 1
for i in range(1, number_of_payments + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance -= principal_payment
    prev_year = year
    year = math.ceil(i / 12)  # Calculate the year into the loan
    if prev_year != year:
        remaining_balance -= pay_one_extra_emi_per_year
    new_schedule.append(
        [
            i,
            round(monthly_payment,0),
            round(principal_payment,0),
            round(interest_payment,0),
            round(remaining_balance,0),
            year,
        ]
    )
    if remaining_balance < 0:
        break

df_1 = pd.DataFrame(
    new_schedule,
    columns=["Month", "Payment", "Principal", "Interest", "Bal_PayOff_OneExtraEMI", "Year"],
)

st.write("### Repayments")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Monthly Repayments", value=f"Rs. {monthly_payment:,.2f}")
col2.metric(label="Total Repayments", value=f"Rs. {df_1['Payment'].sum()}")
col3.metric(label="Total Interest", value=f"Rs. {df_1['Interest'].sum()}")
col4.metric(label="Loan PaidUP in", value=f"{len(df_1)/12} years")

# st.write(df_1)

# Display the data-frame as a chart.
chart1, chart2 = st.columns(2)
with chart1:
    st.write("### Payment Schedule")
    # payments_df = df_1[["Year", "Remaining Balance"]].groupby("Year").min()
    payments_df_1 = pd.concat([df['Remaining Balance'], df_1[f"Bal_PayOff_OneExtraEMI"]], axis=1)
    st.line_chart(payments_df_1)
with chart2:
    st.write("#### Breakeven Point for Principal vs Interest")
    st.line_chart(df_1, x='Year', y=["Principal", "Interest"])

st.divider()

### ----------------
st.write(f"## :blue[What happens if you step up your EMI annually by just x%?]")

col1, col2 = st.columns(2)
step_up_perc = (col1.number_input("Step Up Percentage", min_value=0, value=10)) / 100

# Display the repayments.
total_payments = (monthly_payment * number_of_payments) + pay_one_extra_emi_per_year
total_interest = total_payments - loan_amount

# Create a data-frame with the payment schedule.
new_schedule_1 = []
remaining_balance = loan_amount
year = 1
for i in range(1, number_of_payments + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance -= principal_payment
    prev_year = year
    year = math.ceil(i / 12)  # Calculate the year into the loan
    
    if prev_year != year:
        monthly_payment = round(monthly_payment + (monthly_payment * step_up_perc),2)
        
    new_schedule_1.append(
        [
            i,
            round(monthly_payment,0),
            round(principal_payment,0),
            round(interest_payment,0),
            round(remaining_balance,0),
            year,
        ]
    )
    if remaining_balance < 0:
        break

df_2 = pd.DataFrame(
    new_schedule_1,
    columns=["Month", "Payment", "Principal", "Interest", f"Bal_PayOff_{step_up_perc*100}%stepup", "Year"],
)

st.write("### Repayments")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Monthly Repayments", value=f"Rs. {monthly_payment:,.2f}")
col2.metric(label="Total Repayments", value=f"Rs. {df_2['Payment'].sum()}")
col3.metric(label="Total Interest", value=f"Rs. {df_2['Interest'].sum()}")
col4.metric(label="Loan PaidUP in", value=f"{round(len(df_2)/12,2)} years")

# st.write(df)

# Display the data-frame as a chart.
chart1, chart2 = st.columns(2)
with chart1:
    st.write("### Payment Schedule")
    # payments_df_2 = df_2[["Year", "Remaining Balance"]].groupby("Year").min()
    payments_df_2 = pd.concat([df['Remaining Balance'], df_2[f"Bal_PayOff_{step_up_perc*100}%stepup"]], axis=1)
    st.line_chart(payments_df_2)
with chart2:
    st.write("#### Breakeven Point for Principal vs Interest")
    st.line_chart(df_2, x='Year', y=["Principal", "Interest"])

st.divider()
