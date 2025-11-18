import streamlit as st

st.title("Hellow Streamlit!")
name = st.text_input("Enter your name")
age = st.slider("Age", 0, 120, 25)

if st.button("Submit"):
    st.write(f"Hello {name}, age {age}!")