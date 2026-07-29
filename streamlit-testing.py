import pandas as pd
import numpy as np
import streamlit as st

# 1. Page setup and titles
st.title("My First Streamlit App 🚀 where i modified it lets hope i can see")
st.write("Welcome! Modify the controls below to update the chart in real time.")

# 2. Interactive user inputs (Widgets)
name = st.text_input("What is your name?", "Data Enthusiast")
num_points = st.slider("Select number of data points", min_value=10, max_value=200, value=50)

# 3. Dynamic content based on user input
st.subheader(f"Hello, {name}!")

# Generate sample data based on slider selection
chart_data = pd.DataFrame(
    np.random.randn(num_points, 2),
    columns=["Series A", "Series B"]
)

# 4. Display chart and raw data
st.line_chart(chart_data)

if st.checkbox("Show raw data table"):
    st.dataframe(chart_data)
