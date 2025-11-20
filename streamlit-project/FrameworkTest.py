import streamlit as st
import pandas as pd
import sqlite3
import tempfile
import time
import shutil
import os 
import matplotlib.pyplot as plt
from io import BytesIO

# Initialize graph storage
if "saved_graphs" not in st.session_state:
    st.session_state.saved_graphs = []

# Main Window Switching
tutorial, tab_data_management, tab_data_analysis = st.tabs(["Tutorial","Data Management", "Data Analysis"])

# Condition Logic Wrapper
class condition:
    operand1 = ""
    operand2 = ""
    operator = ""
    not_condition = ""

    def __init__(self, operand1, operand2, operator, not_condition):
        self.operand1 = operand1
        self.operand2 = operand2
        self.operator = operator
        if not_condition: self.not_condition = "NOT"
        else: self.not_condition = ""

# Initialize session state
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "db_valid" not in st.session_state:
    st.session_state.db_valid = True
if "table_names" not in st.session_state:
    st.session_state.table_names = []
if "db_path" not in st.session_state:
    st.session_state.db_path = "Dataset.db"

# FIX: Create empty DB if missing to prevent crash
if not os.path.exists(st.session_state.db_path):
    conn = sqlite3.connect(st.session_state.db_path)
    conn.close()

if "db_conn" not in st.session_state:
    st.session_state.db_conn = sqlite3.connect(st.session_state.db_path, check_same_thread=False)
if "global_df" not in st.session_state:
    st.session_state.global_df = ""
if "global_table" not in st.session_state:
    st.session_state.global_table = ""

# ----------------- TUTORIAL TAB ----------------------
with tutorial:
    st.header("Welcome to PsyOp!")
    st.text("This is an application used to study and analyze mental health data collected from college student.")
    data_schema, data_filtering, data_altering, data_analysis = st.tabs(["Data Schema", "Data Filtering", "Data Altering", "Data Analysis"])
    with data_schema:
        st.text("This section will teach you about how have our data organized and what it means.")
        st.text("""
            Students: student_id, age, gender
            Academic: academic_performance, study_load, teacher_student_relationship, future_career_concerns (0-5)
            Psychological: anxiety_level (GAD-7), self_esteem, mental_health_history, depression (PHQ-9)
            Physiological: blood_pressure, breathing_problem, sleep_quality, headache (0-5)
        """)
    with data_filtering:
        st.text("Use the sliders and inputs to filter your dataset based on specific conditions.")
    with data_altering:
        st.text("You can insert, update, or delete student records.")
    with data_analysis:
        st.text("Generate bar charts and aggregate statistics (Max, Min, Avg, etc.).")

# ----------------- DATA MANAGEMENT TAB ----------------------
with tab_data_management:
    data_view, data_manipulation = st.tabs(["Data View", "Data Alteration"])
    with data_view:
        uploaded = st.file_uploader("Upload your SQLite DB", type=["db", "sqlite", "sqlite3"], key=st.session_state.uploader_key)
        
        # Logic for downloading/creating DB
        if uploaded is None:
            st.session_state.db_valid = False
            st.header("or")
            st.write("Create a new blank dataset")
            col_text, col_ext = st.columns(2)
            with col_text: file_name = st.text_input(label="Filename")
            with col_ext: st.write("\n\n.db")
            
            if file_name:
                n = file_name + ".db"
                with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                    temp_path = tmp.name
                    shutil.copyfile("Dataset.db", temp_path)
                    temp_conn = sqlite3.connect(temp_path, check_same_thread=False)
                    # Clear data
                    for t in ["Students", "Academic", "Psychological", "Physiological", "sqlite_sequence"]:
                        try: temp_conn.execute(f"DELETE FROM {t};")
                        except: pass
                    temp_conn.commit()
                    with open(temp_path, "rb") as f:
                        db_bytes = f.read()
                    st.download_button(label="Download Empty Dataset", data=db_bytes, file_name=n, mime="application/octet-stream")
                    temp_conn.close()

            st.header("or")
            if os.path.exists("Dataset.db"):
                with open("Dataset.db", "rb") as f:
                    db_bytes = f.read()
                if st.download_button(label="Download Premade Dataset", data=db_bytes, file_name="Dataset.db", mime="application/octet-stream"):
                    st.success("Downloaded!")
            else:
                st.write("Standard dataset not found.")

        # Logic for processing uploaded file
        if uploaded and not st.session_state.db_valid:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded.getvalue())
                temp_path = tmp.name
            
            try:
                temp_conn = sqlite3.connect(temp_path, check_same_thread=False)
                temp_schema = pd.read_sql("PRAGMA table_info(Students);", temp_conn)
                if not temp_schema.empty: 
                    st.session_state.db_path = temp_path
                    st.session_state.db_valid = True
                    st.session_state.db_conn.close()
                    st.session_state.db_conn = sqlite3.connect(st.session_state.db_path, check_same_thread=False)
                    st.session_state.global_df = pd.read_sql("SELECT * FROM Students;", st.session_state.db_conn)
                    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", st.session_state.db_conn)
                    st.session_state.table_names = [x for x in tables['name'].tolist() if x != 'sqlite_sequence']
                    st.session_state.file_uploaded = True
                    st.rerun()
                else:
                    st.error("Invalid Schema")
            except:
                st.error("Error reading file")

        if uploaded is not None:
            # Filter Logic
            c1, c2 = st.columns(2)
            with c1: active_table = st.selectbox("Table", st.session_state.table_names)
            with c2: join_table = st.selectbox("Join Table", ["None"] + st.session_state.table_names)

            num_conditions = st.slider("Conditions", 0, 10, 1)
            
            # Dynamic Conditions
            conditions_list = []
            for i in range(num_conditions):
                c_not, c_op1, c_oper, c_op2 = st.columns(4)
                with c_not: is_not = st.checkbox("Not", key=f"not_{i}")
                with c_op1: 
                    try: cols = pd.read_sql(f"SELECT * FROM {active_table} LIMIT 1", st.session_state.db_conn).columns
                    except: cols = []
                    op1 = st.selectbox("Operand 1", cols, key=f"op1_{i}")
                with c_oper: operator = st.selectbox("Operator", ["", ">", ">=", "=", "<=", "<"], key=f"oper_{i}")
                with c_op2: 
                    if op1 == "gender": op2 = st.selectbox("Operand 2", ["'M'", "'F'", "'N'", "'O'"], key=f"op2_{i}")
                    else: op2 = st.text_input("Operand 2", key=f"op2_{i}")
                
                if op1 and operator and op2:
                    prefix = f"{active_table}." if op1 == "student_id" else ""
                    not_str = "NOT" if is_not else ""
                    conditions_list.append(f"{not_str} {prefix}{op1} {operator} {op2}")

            # Query Build
            query = f"SELECT * FROM {active_table}"
            if join_table != "None" and join_table != active_table:
                query += f" JOIN {join_table} ON {active_table}.student_id = {join_table}.student_id"
            
            if conditions_list:
                query += " WHERE " + " AND ".join(conditions_list)

            if st.button("Filter/Update"):
                try:
                    df = pd.read_sql(query, st.session_state.db_conn)
                    df = df.loc[:, ~df.columns.duplicated()]
                    st.session_state.global_df = df
                    st.dataframe(df)
                except Exception as e:
                    st.error(f"Query Error: {e}")

    with data_manipulation:
        if uploaded is not None:
            data_updation, data_deletions = st.tabs(["Insert/Update", "Delete"])
            
            with data_updation: 
                st.caption("Use ID -1 to create a NEW student.")
                sid = st.number_input("Student ID", -1, step=1)
                
                c1, c2 = st.columns(2)
                age = c1.number_input("Age", 18, 100, 18)
                gender = c2.selectbox("Gender", ["M", "F", "N", "O"])
                
                with st.expander("Academic"):
                    c1, c2 = st.columns(2)
                    ac_perf = c1.number_input("Performance", 0, 5)
                    load = c2.number_input("Load", 0, 5)
                    rel = c1.number_input("Teacher Rel", 0, 5)
                    career = c2.number_input("Career Concerns", 0, 5)
                
                with st.expander("Psychological"):
                    c1, c2 = st.columns(2)
                    anx = c1.number_input("Anxiety", 0, 21)
                    est = c2.number_input("Esteem", 0, 30)
                    dep = c1.number_input("Depression", 0, 27)
                    hist = c2.checkbox("History")
                
                with st.expander("Physiological"):
                    c1, c2 = st.columns(2)
                    bp = c1.number_input("BP", 0, 5)
                    breath = c2.number_input("Breathing", 0, 5)
                    sleep = c1.number_input("Sleep", 0, 5)
                    head = c2.number_input("Headache", 0, 5)

                if st.button("Submit Data"):
                    cursor = st.session_state.db_conn.cursor()
                    try:
                        hist_val = 1 if hist else 0
                        target_id = sid
                        
                        # Handle Student Creation/ID
                        if sid == -1:
                            cursor.execute(f"INSERT INTO Students (age, gender) VALUES ({age}, '{gender}')")
                            target_id = cursor.lastrowid
                            msg = f"Created Student ID: {target_id}"
                        else:
                            cursor.execute(f"INSERT OR REPLACE INTO Students (student_id, age, gender) VALUES ({sid}, {age}, '{gender}')")
                            msg = "Updated Student Record"

                        # Update other tables
                        queries = [
                            f"INSERT OR REPLACE INTO Academic VALUES ({target_id}, {ac_perf}, {load}, {rel}, {career})",
                            f"INSERT OR REPLACE INTO Psychological VALUES ({target_id}, {anx}, {est}, {hist_val}, {dep})",
                            f"INSERT OR REPLACE INTO Physiological VALUES ({target_id}, {bp}, {breath}, {sleep}, {head})"
                        ]
                        for q in queries: cursor.execute(q)
                        
                        st.session_state.db_conn.commit()
                        st.success(msg)
                    except Exception as e:
                        st.error(f"Error: {e}")

            with data_deletions:
                del_id = st.number_input("Delete ID", min_value=0)
                if st.button("Delete Record"):
                    try:
                        for t in ["Academic", "Psychological", "Physiological", "Students"]:
                            st.session_state.db_conn.execute(f"DELETE FROM {t} WHERE student_id={del_id}")
                        st.session_state.db_conn.commit()
                        st.success("Deleted.")
                    except Exception as e:
                        st.error(f"Error: {e}")

# ----------------- AGGREGATE FUNCTION (BULLETPROOF FIX) ----------------------
def argument_builder(dataframe, x_axis, y_axis, aggregate):
    if dataframe.empty: return dataframe
    
    # 1. Handle Count (Simple count of rows per group)
    if aggregate == "Count":
        return dataframe.groupby(x_axis).size().reset_index(name='Count')
    
    if y_axis == "None":
        return dataframe
    
    # 2. CRITICAL FIX: Force Y-Axis to Numeric AND Drop Bad Data
    # We work on a COPY (df_temp), not the original dataframe.
    df_temp = dataframe.copy()
    
    # 'coerce' turns text into NaN (empty)
    if aggregate in ["Avg", "Sum", "Max", "Min"]:
        df_temp[y_axis] = pd.to_numeric(df_temp[y_axis], errors='coerce')
        # DROP rows where Y became NaN. If we don't, mean() might still trip up on some versions.
        df_temp = df_temp.dropna(subset=[y_axis])

    if df_temp.empty:
        return pd.DataFrame(columns=[x_axis, y_axis])

    # 3. Perform Aggregation on the CLEANED dataframe (df_temp)
    grouper = df_temp.groupby(x_axis)[y_axis]
    
    match aggregate:
        case "Max": return grouper.max().reset_index()
        case "Min": return grouper.min().reset_index()
        case "Avg": return grouper.mean().reset_index()
        case "Sum": return grouper.sum().reset_index()
        case _: return dataframe

# ----------------- DATA ANALYSIS TAB ----------------------
with tab_data_analysis:
    analysis_tab, saved_tab = st.tabs(["Analyze Data", "Saved Graphs"])

    with analysis_tab:
        if st.session_state.db_valid and not st.session_state.global_df.empty:
            df = st.session_state.global_df
            opts = list(df.columns) 

            x_axis = st.selectbox("X-Axis", opts)
            y_axis = st.selectbox("Y-Axis", ["None"] + opts)
            
            st.caption("Select Y-Axis = 'None' if using Count")
            
            agg_func = st.selectbox("Function", ["None", "Max", "Min", "Avg", "Sum", "Count"])

            if st.button("Graph"):
                if agg_func != "Count" and (y_axis == "None" or y_axis == x_axis):
                     st.error("For Math (Max/Min/Avg/Sum), please choose a numeric Y-Axis.")
                else:
                    st.session_state.graph_data = argument_builder(df, x_axis, y_axis, agg_func)
                    st.session_state.graph_x = x_axis
                    st.session_state.graph_y = "Count" if agg_func == "Count" else y_axis
                    st.session_state.graph_agg = agg_func
                    st.session_state.graph_ready = True

            if st.session_state.get("graph_ready"):
                res = st.session_state.graph_data
                gx = st.session_state.graph_x
                gy = st.session_state.graph_y
                
                st.dataframe(res)
                st.bar_chart(data=res, x=gx, y=gy)

                if st.button("Save Graph to Gallery"):
                    fig, ax = plt.subplots()
                    # Convert X to string to ensure categories plot correctly
                    ax.bar(res[gx].astype(str), res[gy])
                    ax.set_xlabel(gx)
                    ax.set_ylabel(gy)
                    ax.set_title(f"{st.session_state.graph_agg} of {gy} by {gx}")
                    plt.xticks(rotation=45)
                    
                    img = BytesIO()
                    fig.savefig(img, format="png", bbox_inches='tight')
                    img.seek(0)
                    plt.close(fig)

                    st.session_state.saved_graphs.append({
                        "title": f"{st.session_state.graph_agg} - {gx} vs {gy}", 
                        "image": img
                    })
                    st.success("Saved!")

        else:
            st.info("Please load data first.")

    # ----------- SAVED GRAPHS DISPLAY (WITH EXPORT) ---------------
    with saved_tab:
        if not st.session_state.saved_graphs:
            st.info("No graphs saved.")
        else:
            st.markdown("### Saved Graphs")
            for i, graph in enumerate(st.session_state.saved_graphs):
                st.divider()
                # Create 3 columns: 1 for image, 1 for download, 1 for delete
                col1, col2, col3 = st.columns([4, 2, 1])
                
                with col1:
                    st.subheader(graph["title"])
                    st.image(graph["image"])
                
                with col2:
                    # INDIVIDUAL DOWNLOAD BUTTON
                    st.download_button(
                        label="Download PNG",
                        data=graph["image"],
                        file_name=f"graph_{i}.png",
                        mime="image/png",
                        key=f"dl_{i}"
                    )
                
                with col3:
                    if st.button("Delete", key=f"del_{i}"):
                        st.session_state.saved_graphs.pop(i)
                        st.rerun()