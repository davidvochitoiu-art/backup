import streamlit as st
import pandas as pd

st.title("Basic Page Elements")

st.header("Text Examples")
st.subheader("Subheader Example")
st.caption("This is a caption.")

st.write("`st.write()` can display anything.")
st.text("Fixed-width text.")
st.markdown("**Markdown** is _supported_.")

st.divider()

st.header("Data Example")
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [21, 34, 29]
})
st.dataframe(df)

st.divider()

st.header("Images Example")
st.image(
    "https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png",
    caption="Streamlit Logo"
)
