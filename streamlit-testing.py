import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt;

df0 = {
    "Version": [1.0, 1.3, 2.0, 2.5, 2.7, 2.8, 3.0, 3.1, 3.2],
    "Performance": ["0.52", "0.56", "0.67", "0.84", "0.86", "0.88", "0.95", "0.96", "0.97"]
}
df = pd.DataFrame(df0)

df.plot(x = 'Version', y = 'Performance', kind = 'scatter')

st.title("Basic ATL Project Prototype")

fig, ax = plt.subplots()
df.plot(x = 'Version', y = 'Performance', kind = 'scatter', ax = ax)

st.pyplot(fig)
