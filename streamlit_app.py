import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="NZ Property Tax & Mortgage Optimiser", layout="wide")

st.title("🏡 NZ Property Tax & Mortgage Optimisation Tool")

st.markdown("""
This tool helps property investors in New Zealand optimise their tax and mortgage strategy by comparing
deductible rental expenses with non-deductible home loan interest. It also projects the impact of using a
revolving credit facility on your owner-occupied home loan.
""")

# --- Sidebar Inputs ---
st.sidebar.header("🔧 Input Parameters")

st.sidebar.subheader("🏠 Owner-Occupied Home Loan")
home_loan = st.sidebar.number_input("Home Loan Balance ($)", value=975000, step=1000)
home_rate = st.sidebar.number_input("Home Loan Interest Rate (%)", value=4.99, step=0.01) / 100
home_term = st.sidebar.number_input("Home Loan Term (years)", value=30, step=1)
home_insurance = st.sidebar.number_input("Home Insurance ($/year)", value=4200, step=100)
home_rates = st.sidebar.number_input("Home Council Rates ($/year)", value=4300, step=100)

st.sidebar.subheader("🏘 Rental Property")
rental_loan = st.sidebar.number_input("Rental Loan Balance ($)", value=385000, step=1000)
rental_rate = st.sidebar.number_input("Rental Loan Interest Rate (%)", value=4.99, step=0.01) / 100
rental_term = st.sidebar.number_input("Rental Loan Term (years)", value=30, step=1)
rental_type = st.sidebar.selectbox("Rental Repayment Type", ["Interest-Only", "Principal & Interest"])
rental_income_weekly = st.sidebar.number_input("Weekly Rent ($)", value=760)
rental_insurance = st.sidebar.number_input("Rental Insurance ($/year)", value=3500, step=100)
rental_rates = st.sidebar.number_input("Rental Council Rates ($/year)", value=4300, step=100)
rental_maintenance = st.sidebar.number_input("Annual Rental Maintenance ($)", value=2000)
mgmt_fee_percent = st.sidebar.number_input("Property Management Fee (%)", value=5.2) / 100
depreciation = st.sidebar.number_input("Chattel Depreciation ($)", value=1500)

st.sidebar.subheader("⚙️ Global Settings")
tax_rate = st.sidebar.number_input("Marginal Tax Rate (%)", value=33) / 100
projection_years = st.sidebar.slider("Projection Period (years)", 1, 10, 5)

# --- Rental Calculation ---
annual_rent = rental_income_weekly * 52
rental_interest = rental_loan * rental_rate
property_mgmt_fee = annual_rent * mgmt_fee_percent

rental_expenses = rental_interest + rental_insurance + rental_rates + rental_maintenance + property_mgmt_fee + depreciation
net_rental_profit = annual_rent - rental_expenses
tax_savings = min(rental_expenses, annual_rent) * tax_rate

# --- Interest-Only vs P&I Cash Flow Comparison ---
pni_monthly = np.pmt(rental_rate / 12, rental_term * 12, -rental_loan)
pni_annual = pni_monthly * 12
interest_only_annual = rental_interest

cash_freed = pni_annual - interest_only_annual if rental_type == "Interest-Only" else 0

# --- Revolving Credit Impact (Home Loan Repayment Boost) ---
balance = home_loan
annual_savings = []
principal_paid = []
cumulative_interest_saved = []
cumulative_saved = 0

for year in range(1, projection_years + 1):
    balance -= cash_freed
    interest_saved = balance * home_rate
    cumulative_saved += interest_saved
    annual_savings.append(interest_saved)
    principal_paid.append(cash_freed * year)
    cumulative_interest_saved.append(cumulative_saved)

# --- Output Summary ---
st.header("📊 Summary")
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏘 Rental Property")
    st.write(f"**Annual Rent:** ${annual_rent:,.0f}")
    st.write(f"**Total Rental Expenses:** ${rental_expenses:,.0f}")
    st.write(f"**Net Rental Profit (Before Tax):** ${net_rental_profit:,.0f}")
    st.write(f"**Estimated Tax Saved:** ${tax_savings:,.0f}")

with col2:
    st.subheader("🏠 Owner-Occupied Loan Strategy")
    if rental_type == "Interest-Only":
        st.write(f"**Annual Cash Freed (from IO switch):** ${cash_freed:,.0f}")
    else:
        st.write("**Interest-only mode not enabled.**")
    st.write(f"**Total Extra Paid into Revolving Credit ({projection_years} yrs):** ${cash_freed * projection_years:,.0f}")
    st.write(f"**Cumulative Interest Saved on Home Loan:** ${cumulative_saved:,.0f}")

# --- Chart ---
st.subheader("📈 Impact of Redirecting Cash to Revolving Credit")
chart_data = pd.DataFrame({
    "Year": list(range(1, projection_years + 1)),
    "Total Extra Paid ($)": principal_paid,
    "Cumulative Interest Saved ($)": cumulative_interest_saved
})

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(chart_data["Year"], chart_data["Total Extra Paid ($)"], label="Total Extra Paid", marker='o')
ax.plot(chart_data["Year"], chart_data["Cumulative Interest Saved ($)"], label="Interest Saved", marker='s')
ax.set_xlabel("Year")
ax.set_ylabel("Amount ($)")
ax.set_title("Owner-Occupied Loan: Repayment vs Interest Saved")
ax.grid(True)
ax.legend()
st.pyplot(fig)
