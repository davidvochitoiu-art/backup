import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Layout Demo")

with st.sidebar:
    st.header("Controls")
    num = st.slider("Number of points", 10, 500, 100)
    show = st.checkbox("Show raw data")

df = pd.DataFrame(
    np.random.randn(num, 3),
    columns=["A", "B", "C"]
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Line Chart")
    st.line_chart(df)

with col2:
    st.subheader("Area Chart")
    st.area_chart(df)

with st.expander("Raw Data"):
    if show:
        st.dataframe(df)
    else:
        st.info("Enable the checkbox to view raw data.")
