import streamlit as st
import csv

st.set_page_config(page_title="Budget Analyzer", page_icon="📊", layout="wide")

# ------------------  SIMPLE CLEAN UI ------------------
st.markdown("""
    <h1 style="text-align:center; 
               background:linear-gradient(90deg,#4e54c8,#8f94fb);
               padding:18px;border-radius:12px;color:white;">
        📊 Budget Analysis Dashboard
    </h1>
""", unsafe_allow_html=True)

st.write("Upload a CSV file with at least **Year** and **Budget** columns.")

# ------------------ FILE UPLOADER ------------------
file = st.file_uploader("Upload Budget CSV", type=["csv"])

if not file:
    st.stop()

# ------------------ READ CSV WITHOUT PANDAS ------------------
data = []
reader = csv.DictReader(file)
cols = reader.fieldnames

for row in reader:
    data.append(row)

if len(data) == 0:
    st.error("CSV is empty.")
    st.stop()

# ------------------ COLUMN SELECTION ------------------
year_col = st.selectbox("Select Year Column", cols)
budget_col = st.selectbox("Select Budget Column", cols)

# ------------------ CLEAN + CONVERT DATA ------------------
clean_years = []
clean_budgets = []

for row in data:
    try:
        year = int(float(row[year_col]))
        budget_str = row[budget_col].replace(",", "").replace("₹", "")
        budget = float(budget_str)
        clean_years.append(year)
        clean_budgets.append(budget)
    except:
        pass

if len(clean_years) == 0:
    st.error("Could not convert Year/Budget values. Check your CSV format.")
    st.stop()

# ------------------ SHOW RAW TABLE ------------------
if st.checkbox("Show Raw Data Table"):
    st.table(data)

# ------------------ ANALYSIS ------------------
st.subheader("📈 Budget Trend")

# STREAMLIT CHART (no pandas needed)
chart_data = {"Year": clean_years, "Budget": clean_budgets}

st.line_chart(chart_data, x="Year", y="Budget")

# ------------------ METRICS ------------------
st.subheader("📊 Summary Statistics")

total = sum(clean_budgets)
avg = total / len(clean_budgets)
max_budget = max(clean_budgets)
min_budget = min(clean_budgets)
max_year = clean_years[clean_budgets.index(max_budget)]
min_year = clean_years[clean_budgets.index(min_budget)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Budget", f"{total:,.2f}")
col2.metric("Average Budget", f"{avg:,.2f}")
col3.metric("Highest Budget Year", f"{max_year} → {max_budget:,.2f}")
col4.metric("Lowest Budget Year", f"{min_year} → {min_budget:,.2f}")

# ------------------ FOOTER ------------------
st.markdown("<hr><center>Made with ❤️ using Streamlit</center>", unsafe_allow_html=True)

