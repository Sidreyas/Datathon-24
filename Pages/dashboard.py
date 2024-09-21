import streamlit as st

fastapi_url = "http://localhost:8000"  

# Embed the FastAPI app using an iframe
st.components.v1.html(
    f'<iframe src="{fastapi_url}" width="100%" height="800" frameBorder="0"></iframe>',
    height=800,
)
