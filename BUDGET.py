import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config(
    page_title="Budget Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------------------------
# Custom CSS for UI Styling
# --------------------------
st.markdown("""
    <style>
        .main-title {
            background: linear-gradient(90deg, #4e54c8, #8f94fb);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            font-size: 40px;
            font-weight: 900;
            margin-bottom: 20px;
        }
        .feature-button {
            background-color: #6C63FF;
            padding: 15px;
            border-radius: 12px;
            color: white;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            cursor: pointer;
            transition: 0.3s;
            border: 2px solid #ffffff10;
        }
        .feature-button:hover {
            background-color: #5149e6;
            transform: scale(1.02);
        }
        .card {
            background-color: #f8f9ff;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 10px;
            border: 1px solid #e4e6ff;
        }
        .metric-box {
            background: #ffffff;
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #dcdcff;
            text-align: center;
            font-size: 20px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------------
# Header
# --------------------------
st.markdown('<div class="main-title">📊 Budget Analysis Dashboard (2014–2025)</div>', unsafe_allow_html=True)

# --------------------------
# Load Data
# --------------------------
df = pd.read_csv("Budget 2014-2025.csv")

# Convert Year to numeric if not already
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

# --------------------------
# Feature Selection Section
# --------------------------
st.subheader("✨ Choose an Analysis Feature")

col1, col2, col3 = st.columns(3)

with col1:
    feature = st.radio(
        "",
        ["📈 Year-wise Trend", "💸 Revenue vs Expenditure"],
        help="Select the analysis you want to perform"
    )

with col2:
    feature2 = st.radio(
        "",
        ["📊 Category Comparison", "🏦 Summary Statistics"],
        help="Additional analytics"
    )

with col3:
    feature3 = st.radio(
        "",
        ["📉 Deficit / Surplus Trend", "🔍 Detailed Table"],
        help="More insights"
    )


# --------------------------
# Plotting Helper
# --------------------------
def plot_line(x, y, title, ylabel):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y)
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    st.pyplot(fig)


# --------------------------
# Cards for Results
# --------------------------
st.markdown("### 📁 Analysis Output")
st.markdown('<div class="card">', unsafe_allow_html=True)

# ========== Feature 1 ==========
if feature == "📈 Year-wise Trend":
    st.write("### 📈 Year-wise Budget Trend")
    numeric_cols = df.select_dtypes(include="number").columns
    col = st.selectbox("Select a Column to Visualize:", numeric_cols)
    plot_line(df["Year"], df[col], f"{col} Over the Years", col)

elif feature == "💸 Revenue vs Expenditure":
    st.write("### 💸 Revenue vs Expenditure Comparison")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["Year"], df["Revenue"], label="Revenue")
    ax.plot(df["Year"], df["Expenditure"], label="Expenditure")
    ax.legend()
    ax.set_title("Revenue vs Expenditure")
    ax.grid(True)
    st.pyplot(fig)

# ========== Feature 2 ==========
if feature2 == "📊 Category Comparison":
    st.write("### 📊 Compare Any Two Columns")
    colA = st.selectbox("Column A", df.columns)
    colB = st.selectbox("Column B", df.columns)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["Year"], df[colA], label=colA)
    ax.plot(df["Year"], df[colB], label=colB)
    ax.legend()
    ax.grid(True)
    ax.set_title(f"{colA} vs {colB}")
    st.pyplot(fig)

elif feature2 == "🏦 Summary Statistics":
    st.write("### 🏦 Summary of Budget Data")
    st.dataframe(df.describe())

# ========== Feature 3 ==========
if feature3 == "📉 Deficit / Surplus Trend":
    st.write("### 📉 Deficit / Surplus Over the Years")
    if "Revenue" in df.columns and "Expenditure" in df.columns:
        df["Deficit/Surplus"] = df["Revenue"] - df["Expenditure"]
        plot_line(df["Year"], df["Deficit/Surplus"], "Deficit / Surplus Trend", "Amount")
        st.metric("Latest Year Balance", value=df["Deficit/Surplus"].iloc[-1])
    else:
        st.error("Revenue or Expenditure columns missing, cannot calculate balance.")

elif feature3 == "🔍 Detailed Table":
    st.write("### 🔍 Complete Budget Dataset")
    st.dataframe(df)

st.markdown('</div>', unsafe_allow_html=True)


# --------------------------
# Footer
# --------------------------
st.markdown("""
<hr>
<center>
Made with ❤️ using Streamlit  
</center>
""", unsafe_allow_html=True)
