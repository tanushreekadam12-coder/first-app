import streamlit as st

st.set_page_config(page_title="Simple Calculator", page_icon="🧮")

st.title("🧮 Simple Calculator")

# Input numbers
num1 = st.number_input("Enter first number", value=0.0)
num2 = st.number_input("Enter second number", value=0.0)

# Choose operation
operation = st.selectbox(
    "Choose Operation",
    ["Add", "Subtract", "Multiply", "Divide"]
)

# Calculate
if st.button("Calculate"):
    if operation == "Add":
        result = num1 + num2
    elif operation == "Subtract":
        result = num1 - num2
    elif operation == "Multiply":
        result = num1 * num2
    elif operation == "Divide":
        if num2 == 0:
            result = "Error: Division by zero"
        else:
            result = num1 / num2

    st.success(f"Result: {result}")
