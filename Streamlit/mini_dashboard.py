import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Mini Dashboard", layout="wide")

st.title("📊 Mini Sales Dashboard")

with st.sidebar:
    st.header("Filters")
    year = st.selectbox("Year", [2023, 2024, 2025])
    min_rev = st.slider("Minimum Revenue", 0, 100000, 20000, step=5000)

df = pd.DataFrame({
    "year": np.random.choice([2023, 2024, 2025], 200),
    "region": np.random.choice(["Europe", "Asia", "Americas"], 200),
    "revenue": np.random.randint(5000, 100000, 200),
})

filtered = df[(df["year"] == year) & (df["revenue"] >= min_rev)]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Region")
    st.bar_chart(filtered.groupby("region")["revenue"].sum())

with col2:
    st.subheader("Revenue Distribution")
    st.area_chart(filtered["revenue"])

with st.expander("Filtered Data"):
    st.dataframe(filtered)
