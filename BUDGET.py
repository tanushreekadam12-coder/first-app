streamlit
import streamlit as st
import csv
import io

st.set_page_config(page_title="Budget Analyzer", page_icon="📊", layout="wide")

# ------------------ HEADER ------------------
st.markdown("""
    <h1 style="text-align:center;
               background: linear-gradient(90deg,#4e54c8,#8f94fb);
               padding:20px;border-radius:12px;color:white;">
        📊 Budget Analysis Dashboard
    </h1>
""", unsafe_allow_html=True)

st.write("Upload a CSV file containing Year and Budget columns.")

# ------------------ FILE UPLOADER ------------------
file = st.file_uploader("Upload CSV File", type=["csv"])

if not file:
    st.stop()

# --------------- FIX: DECODE CSV TO TEXT ---------------
try:
    decoded = file.read().decode("utf-8")
except:
    st.error("Could not decode file. Make sure it is a UTF-8 CSV file.")
    st.stop()

data = []
reader = csv.DictReader(io.StringIO(decoded))

cols = reader.fieldnames
if not cols:
    st.error("Could not read CSV header. Make sure your file has column names.")
    st.stop()

for row in reader:
    data.append(row)

# ------------------ SELECT COLUMNS ------------------
year_col = st.selectbox("Select Year Column", cols)
budget_col = st.selectbox("Select Budget Column", cols)

# ------------------ CLEAN DATA ------------------
clean_years = []
clean_budgets = []

for row in data:
    try:
        year = int(float(row[year_col]))
        budget_str = str(row[budget_col]).replace(",", "").replace("₹", "").strip()
        budget = float(budget_str)
        clean_years.append(year)
        clean_budgets.append(budget)
    except:
        pass

if len(clean_years) == 0:
    st.error("No valid numeric Year/Budget data found.")
    st.stop()

# ---------------- SHOW DATA ----------------
st.subheader("📋 Parsed Data Preview")
preview_rows = min(10, len(clean_years))

table_data = {
    "Year": clean_years[:preview_rows],
    "Budget": clean_budgets[:preview_rows]
}
st.table(table_data)

# ---------------- CHART ----------------
st.subheader("📈 Budget Trend Chart")
chart_data = {"Year": clean_years, "Budget": clean_budgets}
st.line_chart(chart_data, x="Year", y="Budget")

# ---------------- METRICS ----------------
total = sum(clean_budgets)
avg = total / len(clean_budgets)
max_budget = max(clean_budgets)
min_budget = min(clean_budgets)
max_year = clean_years[clean_budgets.index(max_budget)]
min_year = clean_years[clean_budgets.index(min_budget)]

st.subheader("📊 Summary Statistics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Budget", f"{total:,.2f}")
c2.metric("Average Budget", f"{avg:,.2f}")
c3.metric("Highest Budget", f"{max_year} → {max_budget:,.2f}")
c4.metric("Lowest Budget", f"{min_year} → {min_budget:,.2f}")

st.markdown("<hr><center>Made with ❤️ in Streamlit</center>", unsafe_allow_html=True)




