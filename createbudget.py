# app.py
import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Budget Analyzer (Robust)", page_icon="📊", layout="wide")
st.title("📊 Budget Analyzer — Robust CSV Handling")

st.markdown(
    """
This app is more tolerant of messy CSVs:
- auto-detects common Year / Budget column names,
- handles commas, currency symbols, parentheses for negatives,
- offers manual column selection if detection fails,
- shows problematic rows and allows download of cleaned data.
"""
)

def try_read_csv(uploaded):
    """
    Try reading CSV with automatic separator detection, fallback to comma.
    Returns DataFrame or raises Exception.
    """
    uploaded.seek(0)
    raw = uploaded.read()
    # If uploaded is bytes, decode
    if isinstance(raw, bytes):
        try:
            text = raw.decode("utf-8")
        except Exception:
            try:
                text = raw.decode("latin1")
            except Exception:
                text = None
    else:
        text = raw

    # attempt automatic sep detection by pandas (engine='python', sep=None)
    try:
        uploaded.seek(0)
        df = pd.read_csv(io.BytesIO(raw) if isinstance(raw, (bytes, bytearray)) else io.StringIO(text),
                         sep=None, engine="python")
        return df
    except Exception:
        # fallback to comma
        try:
            uploaded.seek(0)
            df = pd.read_csv(io.BytesIO(raw) if isinstance(raw, (bytes, bytearray)) else io.StringIO(text),
                             sep=",", engine="python")
            return df
        except Exception as e:
            raise e

def detect_columns(df):
    """
    Try to detect year and budget columns based on common names.
    Returns (year_col, budget_col) or (None, None).
    """
    lower = [c.lower() for c in df.columns]
    # possible candidates
    year_keywords = ["year", "yr"]
    budget_keywords = ["budget", "amount", "expenditure", "expend", "value", "total", "allocation", "outlay"]

    year_col = None
    budget_col = None

    for i, name in enumerate(lower):
        for ky in year_keywords:
            if ky == name or ky in name.split() or name.startswith(ky):
                year_col = df.columns[i]
                break
        if year_col:
            break

    for i, name in enumerate(lower):
        for kb in budget_keywords:
            if kb == name or kb in name or name.startswith(kb):
                # prefer different column than year_col
                if df.columns[i] != year_col:
                    budget_col = df.columns[i]
                    break
        if budget_col:
            break

    return year_col, budget_col

def clean_budget_column(series):
    """
    Convert a pandas Series to numeric budget values handling:
    - commas: "1,234"
    - currency symbols: "$", "₹", "INR", "Rs."
    - parentheses for negative: "(1,234)"
    - percentage (not expected) -> removed
    Returns (clean_series, issues_df) where issues_df are rows that couldn't convert.
    """
    def parse_val(x):
        if pd.isna(x):
            return None
        s = str(x).strip()
        if s == "":
            return None
        # parentheses -> negative
        negative = False
        if s.startswith("(") and s.endswith(")"):
            negative = True
            s = s[1:-1].strip()
        # remove currency symbols and letters (keep digits, dot, minus)
        s = re.sub(r"[^\d\.\-eE]", "", s)
        if s in ["", ".", "-", "+"]:
            return None
        try:
            val = float(s)
            if negative:
                val = -val
            return val
        except Exception:
            return None

    cleaned = series.apply(parse_val)
    issues = series[cleaned.isna() & series.notna()].to_frame(name="original_value")
    return cleaned, issues

# --- Upload ---
st.sidebar.header("Upload Budget CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv", "txt"], accept_multiple_files=False)

if not uploaded_file:
    st.info("Upload a CSV file (e.g., `Budget 2014-2025.csv`) to get started.")
    st.stop()

# read CSV
try:
    df_raw = try_read_csv(uploaded_file)
except Exception as e:
    st.error("Could not read the CSV file. Possible reasons: malformed CSV, encoding issues.")
    st.exception(e)
    st.stop()

st.subheader("Preview: first 10 rows (raw)")
st.dataframe(df_raw.head(10), use_container_width=True)

# detect columns
year_col, budget_col = detect_columns(df_raw)

st.sidebar.markdown("### Column selection (auto-detected when possible)")
st.sidebar.write(f"Detected year column: **{year_col}**" if year_col else "Year column: ❌ not detected")
st.sidebar.write(f"Detected budget column: **{budget_col}**" if budget_col else "Budget column: ❌ not detected")

# allow manual override
all_cols = list(df_raw.columns)
chosen_year = st.sidebar.selectbox("Select Year column", options=["--auto--"] + all_cols, index=0)
chosen_budget = st.sidebar.selectbox("Select Budget column", options=["--auto--"] + all_cols, index=0)

if chosen_year != "--auto--":
    year_col = chosen_year
if chosen_budget != "--auto--":
    budget_col = chosen_budget

if not year_col or not budget_col:
    st.error("Please select both a Year column and a Budget column (use the selectors in the sidebar).")
    st.stop()

# create working df
df = df_raw[[year_col, budget_col]].copy()
df = df.rename(columns={year_col: "Year", budget_col: "Budget"})

# parse Year column to int (try to extract 4-digit year)
def parse_year(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    # common: exact year "2019"
    # try to find 4-digit sequence
    m = re.search(r"(19|20)\d{2}", s)
    if m:
        return int(m.group(0))
    # try direct int
    try:
        return int(float(s))
    except Exception:
        return None

df["Year_parsed"] = df["Year"].apply(parse_year)

# clean budget
df["Budget_clean"], issues = clean_budget_column(df["Budget"])

# show issues
if issues.shape[0] > 0:
    st.warning(f"Found {len(issues)} budget values that could not be parsed automatically. See below.")
    st.dataframe(issues.reset_index().rename(columns={"index": "row_index"}), use_container_width=True)

# drop rows with no year or no budget after parsing
df_clean = df.dropna(subset=["Year_parsed", "Budget_clean"]).copy()
df_clean["Year_parsed"] = df_clean["Year_parsed"].astype(int)
df_clean["Budget_clean"] = df_clean["Budget_clean"].astype(float)

if df_clean.empty:
    st.error("After cleaning there are no valid rows. Check your Year/Budget columns and formatting.")
    st.stop()

# Allow user to pick range/filter etc.
st.sidebar.header("Analysis Controls")
years = sorted(df_clean["Year_parsed"].unique())
min_year = int(min(years))
max_year = int(max(years))
year_range = st.sidebar.slider("Select year range", min_year, max_year, (min_year, max_year), step=1)

filtered = df_clean[(df_clean["Year_parsed"] >= year_range[0]) & (df_clean["Year_parsed"] <= year_range[1])]

# Optional aggregation: if there are duplicate years, aggregate
agg_option = st.sidebar.selectbox("If multiple rows per year:", ["Sum budgets per year (default)", "Average budgets per year", "Keep raw rows"])
if agg_option.startswith("Sum"):
    agg_df = filtered.groupby("Year_parsed", as_index=False)["Budget_clean"].sum().rename(columns={"Year_parsed": "Year", "Budget_clean": "Budget"})
elif agg_option.startswith("Average"):
    agg_df = filtered.groupby("Year_parsed", as_index=False)["Budget_clean"].mean().rename(columns={"Year_parsed": "Year", "Budget_clean": "Budget"})
else:
    agg_df = filtered.rename(columns={"Year_parsed": "Year", "Budget_clean": "Budget"})[["Year", "Budget"]]

# Display cleaned table & stats
st.subheader("Cleaned Data (selected range)")
st.dataframe(agg_df.sort_values("Year").reset_index(drop=True), use_container_width=True)

total_budget = agg_df["Budget"].sum()
avg_budget = agg_df["Budget"].mean()
max_row = agg_df.loc[agg_df["Budget"].idxmax()]
min_row = agg_df.loc[agg_df["Budget"].idxmin()]

c1, c2, c3 = st.columns(3)
c1.metric("Total (selected)", f"{total_budget:,.2f}")
c2.metric("Average (selected)", f"{avg_budget:,.2f}")
c3.metric("Highest year", f"{int(max_row['Year'])} — {max_row['Budget']:,.2f}")

c4, c5 = st.columns(2)
c4.metric("Lowest year", f"{int(min_row['Year'])} — {min_row['Budget']:,.2f}")

# Charts
st.subheader("Charts")
st.line_chart(agg_df.set_index("Year")["Budget"])
st.bar_chart(agg_df.set_index("Year")["Budget"])

# Download cleaned filtered data
csv_bytes = agg_df.to_csv(index=False).encode("utf-8")
st.download_button(label="Download cleaned CSV", data=csv_bytes, file_name="cleaned_budget.csv", mime="text/csv")

st.success("Cleaning & analysis complete. If something still looks wrong, try:")
st.write(
    "- Check that the Year column contains a 4-digit year (e.g., 2019). "
    "- If Budget contains currency symbols or commas, the app will strip them automatically; if values use unusual formatting, fix them in your CSV or inspect the `original_value` issues table above."
)
