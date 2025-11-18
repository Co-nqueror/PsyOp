import streamlit as st

# Text Inputs
text = st.text_input("Your name")
area = st.text_area("Story")
password = st.text_input("Passowrd", type="password")

# Numeric Inputs
number = st.number_input("Pick a number", 0, 100)
slider = st.slider("Age", 0, 120, 25)

# Selection Widgets
choice = st.selectbox("Gender", ["M", "F", "N", "O"])
multichoice = st.multiselect("Hobbies", ["Sports", "Reading"])
radio = st.radio("Status", ["Active", "Inactive"])

# Boolean Widgets
flag = st.checkbox("I agree")

# Buttons
if st.button("Save"):
    st.write("Data saved!")

# File Uploading
uploaded_file = st.file_uploader("Upload a CSV")