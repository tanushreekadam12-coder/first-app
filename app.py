import streamlit as st
import math

st.set_page_config(page_title="Scientific Calculator", page_icon="🧮")
st.title("🧮 Scientific Calculator")

# Input field
expression = st.text_input(
    "Enter expression (example: sin(30), log(10), 5*6, sqrt(49))"
)

# Map allowed functions
allowed_functions = {
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "pi": math.pi,
    "e": math.e
}

# Safe evaluation environment
safe_env = {
    **allowed_functions,
    "__builtins__": {}
}

# Calculate
if st.button("Calculate"):
    try:
        result = eval(expression, safe_env, {})
        st.success(f"Result: {result}")
    except Exception:
        st.error("Invalid expression. Check your syntax.")
