import streamlit as st
import pandas as pd
import sqlite3

st.title("Student Database Manager")

conn = sqlite3.connect("Dataset.db", check_same_thread=False)

tab_filter, tab_insert = st.tabs(["Filter Students", "Insert Student"])

# Filter Tab
with tab_filter:
    st.header("Filter Students")
    # Age Slider
    age_min = st.slider("Minimum age", 18, 22, 18)
    #Build SQL query
    query = f"SELECT * FROM Students WHERE age >= {age_min};"
    # Fecth data
    try:
        df = pd.read_sql(query, conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Database error: {e}")
# Insert Tab
with tab_insert:
    st.header("Insert New Student")
    # Input Fields
    age = st.number_input("Age", min_value=18, max_value=22, value=18)
    gender = st.selectbox("Gender", ["M", "F", "N", "O"])
    # Button to insert
    if st.button("Inser Student"):
        st.success("Student added successfully!")
        