import streamlit as st

#Colummns
col1, col2 = st.columns(2)
with col1:
    st.number_input("Age")
with col2:
    st.selectbox("Gender", ["M", "F"])

# Tabs
tab1, tab2 = st.tabs(["Filter", "Insert"])
with tab1:
    st.write("Filer stuff")
with tab2:
    st.write("Insert stuff")

# Expanders
with st.expander("Advanced Settings"):
    st.slider("Threshold", 0, 100)