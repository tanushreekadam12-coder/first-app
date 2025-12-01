import streamlit as st
import pandas as pd

st.set_page_config(page_title="Budget Analyzer 2014–2025", page_icon="📊", layout="wide")

st.title("📊 Budget Analysis App (2014–2025)")
st.write("Analyze budgets year-wise with charts, insights, and interactive controls.")

# 1. Upload or Load File
st.sidebar.header("Upload Budget File")
uploaded_file = st.sidebar.file_uploader("Upload Budget CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.warning("Please upload the budget CSV file to continue.")
    st.stop()

# Ensure correct columns
if len(df.columns) < 2:
    st.error("❌ CSV format incorrect. Must contain 'Year' and 'Budget' columns.")
    st.stop()

# Standard column names
df.columns = ["Year", "Budget"]

# Convert data types
df["Year"] = df["Year"].astype(int)
df["Budget"] = df["Budget"].astype(float)

# Sidebar filters
st.sidebar.header("Filters")
min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

year_range = st.sidebar.slider(
    "Select Year Range",
    min_year, max_year, (min_year, max_year)
)

search_year = st.sidebar.text_input("Search for a specific year")

# Filter data
filtered_df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

if search_year.isdigit():
    filtered_df = filtered_df[filtered_df["Year"] == int(search_year)]

# Section: Data Table
st.subheader("📁 Budget Data")
st.dataframe(filtered_df, use_container_width=True)

# Section: Summary Statistics
st.subheader("📌 Summary (Selected Range)")
total_budget = filtered_df["Budget"].sum()
avg_budget = filtered_df["Budget"].mean()
max_budget = filtered_df["Budget"].max()
max_year_val = filtered_df.loc[filtered_df["Budget"].idxmax(), "Year"]
min_budget = filtered_df["Budget"].min()
min_year_val = filtered_df.loc[filtered_df["Budget"].idxmin(), "Year"]

col1, col2, col3 = st.columns(3)
col1.metric("Total Budget", f"{total_budget:,.2f}")
col2.metric("Average Budget", f"{avg_budget:,.2f}")
col3.metric("Highest Budget Year", f"{max_year_val} — {max_budget:,.2f}")

col4, col5 = st.columns(2)
col4.metric("Lowest Budget Year", f"{min_year_val} — {min_budget:,.2f}")

# Section: Line Chart
st.subheader("📈 Budget Trend (Line Chart)")
st.line_chart(filtered_df, x="Year", y="Budget")

# Section: Bar Chart
st.subheader("📊 Budget Comparison (Bar Chart)")
st.bar_chart(filtered_df, x="Year", y="Budget")

# Section: Download Button
st.subheader("⬇ Download Filtered Data")
csv_data = filtered_df.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="filtered_budget.csv",
    mime="text/csv"
)

st.success("App Loaded Successfully!")
