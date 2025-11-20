import streamlit as st
import pandas as pd
import sqlite3
import tempfile
import time
import shutil
import matplotlib.pyplot as plt
from io import BytesIO

# Initialize graph storage
if "saved_graphs" not in st.session_state:
    st.session_state.saved_graphs = []

# Main Window Switching
tutorial, tab_data_management, tab_data_analysis = st.tabs(["Tutorial", "Data Management", "Data Analysis"])

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
if "db_conn" not in st.session_state:
    st.session_state.db_conn = sqlite3.connect(st.session_state.db_path, check_same_thread=False)
if "global_df" not in st.session_state:
    st.session_state.global_df = ""
if "global_table" not in st.session_state:
    st.session_state.global_table = ""

# ----------------- TUTORIAL TAB ----------------------
with tutorial:
    st.header("Welcome to PsyOp!")
    st.text("This is an application used to study and analyze mental health data collected from college student. This page will teach you how to use our application to your full advantage.")
    data_schema, data_filtering, data_altering, data_analysis = st.tabs(["Data Schema", "Data Filtering", "Data Altering", "Data Analysis"])
    with data_schema:
        st.text("This section will teach you about how have our data organized and what it means.")
        st.text("Our data is organized into four tables:")
        st.text("""
            Students
                    •   student_id
                    •    age
                    •   gender
            Academic
                    •   student_id
                    •   academic_performance 
                    •   study_load
                    •   teacher_student_relationship
                    •   future_career_concerns
            Psychological
                    •   student_id
                    •   anxiety_level
                    •   self_esteem
                    •   mental_health_history
                    •   depression
            Physiological
                    •   student_id
                    •   blood_pressure
                    •   breathing_problem
                    •   sleep_quality
                    •   headache
        """)
        st.text("We'll break down further what each data piece means table by table")
        st.subheader("Students")
        st.text("•  The student_id is arbitrary and does not have any meaning, it is just the primary key that connects the data and keeps track of it.")
        st.text("•  age is in years. The default dataset we provide only includes ages 18-22.")
        st.text("""• gender has four options for the sake of simplicity:
            • 'M' for Male
            • 'F' for Female
            • 'N' for Non-Binary
            • 'O' for Other""")
        st.subheader("Academic")
        st.text("Academic is graded on a 0-5 scale where 0 is \"Not at all\" and 5 is \"Extremely\"")
        st.text("•  student_id")
        st.text("•  academic_performance: Do you lack confidence in your academic performance?")
        st.text("•  study_load: Do you feel overwhelmed with your academic workload?")
        st.text("•  teacher_student_relationship: Are you facing any difficulties with your professors or instructors?")
        st.text("•  future_career_concerns: Do you lack confidence in your choice of academic subjects?")
        st.subheader("Psychological")
        st.text("Psychological is measured using various official medical assesment tools which range in scale.")
        st.text("•  student_id")
        st.text("•  anxiety_level: Measured using GAD-7 (Generalized Anxiety Disorder-7) scale.")
        st.text("•  self_esteem: Assessed via Rosenberg Self-Esteem scale.")
        st.text("•  mental_health_history: Either 1 or 0, 1 meaning yes and 0 meaning no.")
        st.text("•  depression: Assesed via PHQ-9 (Patient Health Questionnaire-9).")
        st.subheader("Physiological")
        st.text("Physiological is graded on a 0-5 scale where 0 is \"Not at all\" and 5 is \"Extremely\"")
        st.text("•  student_id")
        st.text("•  blood_pressure: \"Have you noticed a rapid heartbeat or palpitations?\"")
        st.text("•  breathing_problem: \"Do you face any problems or difficulties breathing?\"")
        st.text("•  sleep_quality: \"Do you face any sleep problems or difficulties falling asleep?\"")
        st.text("•  headache: \"Have you been getting headaches more often than usual?\"")
        st.subheader("Where our schema is from")
        st.text("Our schema is based of an imputation of the national health survey of college students")
        st.text("This imputation was collected by research students from Kaggle here: https://www.kaggle.com/datasets/mdsultanulislamovi/student-stress-monitoring-datasets/data")
        st.text("Those students go deeper into their study of the data here which does a much better job of explaining the rationale behind the schema: https://arxiv.org/abs/2508.01105")
        st.subheader("Uploading your dataset")
        st.text("In order to upload data to the application, it must be of the exact same schema as the schema previously referenced down to the letter. If not, the app will reject it.")
        st.text("We provide the option to make a blank dataset of the schema or a duplication of the dataset we worked with under Data Management>DataView.")
        st.text("We know this is very rigid and limiting to larger more nuanced research and we are working to make it more flexible.")
    with data_filtering:
        st.subheader("Choosing your tables")
        st.text("For the tables, you are allowed to pick one active table and one join table, joined on the student_id")
        st.subheader("Making conditions")
        st.text("You can use the conditions slider to add or remove the number of coniditons")
        st.text("The not checkbox will just do the opposite of whatever condition you've wrote.")
        st.text("The first operand is the different columns you can choose from your table and join table.")
        st.text("The operator is the selection of operators you can choose from for your condition.")
        st.text("The second operand is an open input literal that can have anything inputted, so its careful that you make sure your condition is correct and relevant to the attribute you're referencing.")
        st.text("•  For gender, you must put \' around the gender initial in order for it to be valid. EX: gender = 'M'")
    with data_altering:
        st.text("Data can be altered by inserting, updating or deleting")
        st.subheader("Insertion/Updation")
        st.text("When inserting a new records, every data field must be filled to ensure that the data remains consistent across the dataset.")
        st.text("When updating a record, it will update every field in every table related to that id.")
        st.text("While this system is rather rigid, it ensures that all the data is correct and consistent no matter what. If you don't plan on using a certain part of data, you can leave it at its default value.")
        st.subheader("Deletion")
        st.text("Deleting records is simple. All you need to do is insert the student_id into the table and click delete record.")
        st.text("When deleting a record, it will delete that record from all the tables with the same student_id, ensuring data concurrency across the tables.")
    with data_analysis:
        st.text("The data analysis tool is extremely useful for aggregating and visualzing data and data relationships.")
        st.text("The aggregation methods are:")
        st.text("•  Max")
        st.text("•  Min")
        st.text("•  Avg")
        st.text("•  Sum")
        st.text("•  Count")
        st.text("Currently the grapher only graphs bar graphs, but we plan on expanding to support more graph types in the future.")

# ----------------- DATA MANAGEMENT TAB ----------------------
with tab_data_management:
    data_view, data_manipulation = st.tabs(["Data View", "Data Alteration"])
    with data_view:
        uploaded = st.file_uploader("Upload your SQLite DB", type=["db", "sqlite", "sqlite3"], key=st.session_state.uploader_key)
        if uploaded is None:
            st.session_state.db_valid = False
            st.header("or")
            st.write("Create a new blank dataset")
            text, extension = st.columns(2)
            with text:
                file_name = st.text_input(label="")
            with extension:
                st.write("")
                st.write("")
                st.write("")
                st.write(".db")
            if file_name:
                n = file_name +".db"
                with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                    temp_path = tmp.name
                    shutil.copyfile("Dataset.db", temp_path)
                    temp_conn = sqlite3.connect(temp_path, check_same_thread=False)
                    temp_conn.execute("DELETE FROM sqlite_sequence;")
                    temp_conn.execute("DELETE FROM Academic;")
                    temp_conn.execute("DELETE FROM Psychological;")
                    temp_conn.execute("DELETE FROM Physiological;")
                    temp_conn.execute("DELETE FROM Students;")
                    temp_conn.commit()
                    with open(temp_path, "rb") as f:
                        db_bytes = f.read()
                    st.download_button(label="Download Dataset", data=db_bytes, file_name=n, mime="application/octet-stream")
                    temp_conn.close()
            st.header("or")
            with open("Dataset.db", "rb") as f:
                db_bytes = f.read()
            if st.download_button(label="Download Premade Dataset", data=db_bytes, file_name="Dataset.db", mime="application/octet-stream"):
                st.success("Downloaded!")
        if uploaded and not st.session_state.db_valid:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded.getvalue())
                temp_path = tmp.name
            temp_conn = sqlite3.connect(temp_path, check_same_thread=False)
            temp_schema = pd.read_sql("PRAGMA table_info(Students);", temp_conn)
            test_schema = pd.read_sql("PRAGMA table_info(Students);", st.session_state.db_conn)
            if temp_schema.equals(test_schema): 
                st.session_state.db_path = temp_path
                st.session_state.db_valid = True
                st.session_state.db_conn.close()
                st.session_state.db_conn = sqlite3.connect(st.session_state.db_path, check_same_thread=False)
                st.session_state.global_df = pd.read_sql("SELECT * FROM Students;", st.session_state.db_conn)
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", st.session_state.db_conn)
                st.session_state.table_names = tables['name'].tolist()
                st.session_state.table_names.pop(0) 
                st.session_state.file_uploaded = True
            else: 
                st.error("There is an error in the file you uploaded")
                time.sleep(2)
                st.session_state.uploader_key += 1
                st.rerun()
        if uploaded is not None:
            table_dropdown_col, join_table_dropdown_col = st.columns(2)
            with table_dropdown_col:
                active_table = st.selectbox("Table", st.session_state.table_names)
            with join_table_dropdown_col:
                join_table = st.selectbox("Join Table", ["None"] + st.session_state.table_names)

            num_conditions_col, filter_button_col = st.columns(2)
            with num_conditions_col:
                num_conditions = st.slider("Conditions", 0, 10, 1)
            with filter_button_col:
                if st.button("Filter/Update"): print("Filtered")
            
            for i in range(num_conditions):
                not_condition, operand1, operator, operand2 = st.columns(4)
                with not_condition: not_condition_checkbox = st.checkbox("Not", key=f"not_{i}")
                with operand1: 
                    operand1_input = st.selectbox(label="Operand 1", options=st.session_state.global_df.columns, key=f"operand1_{i}")
                with operator: operator_input = st.selectbox("Operator", ["", ">", ">=", "=", "<=", "<"], key=f"operator_{i}")
                with operand2: 
                    if operand1_input == "gender": operand2_input = st.selectbox(label="Operand2", options=["\'M\'", "\'F\'", "\'N\'", "\'O\'"], key=f"operand2_{i}")
                    else: operand2_input = st.text_input("Operand 2", key=f"operand2_{i}")

            if active_table == join_table or join_table == "None":
                query = f"SELECT * FROM {active_table}"
            else: 
                query = f"SELECT * FROM {active_table} JOIN {join_table} ON {active_table}.student_id = {join_table}.student_id"

            conditions = []
            for i in range(num_conditions):
                if st.session_state.get(f"operand1_{i}") != "student_id":
                    cond = condition(st.session_state.get(f"operand1_{i}"), st.session_state.get(f"operand2_{i}"), st.session_state.get(f"operator_{i}"), st.session_state.get(f"not_{i}"))
                else:
                    cond = condition(f"{active_table}.student_id", st.session_state.get(f"operand2_{i}"), st.session_state.get(f"operator_{i}"), st.session_state.get(f"not_{i}"))
                if cond.operand1 == "" or cond.operand2 == "" or cond.operator == "": continue
                conditions.append(f"{cond.not_condition} {cond.operand1} {cond.operator} {cond.operand2} ")

            if conditions: query += " WHERE " + "AND ".join(conditions) 

            try:
                df = pd.read_sql(query+";", st.session_state.db_conn)
                df = df.loc[:, ~df.columns.duplicated()]
                st.dataframe(df)
                st.session_state.global_df = df
            except:
                st.error("There is an error in your condition")
    with data_manipulation:
        if uploaded is not None:
            data_updation, data_deletions = st.tabs(["Updation/Insertion", "Deletion"])
            with data_updation: 
                # Students
                st.write("Students")
                student_id_input = st.number_input("Student ID", min_value=-1, max_value=10000000, step=1)
                st.write("^^^^^ Leave as -1 if you are inserting new data ^^^^^")
                age, gender = st.columns(2)
                with age: age_input = st.number_input("Age", min_value=18, max_value=22, step=1)
                with gender: gender_input = st.selectbox("Gender", ["M", "F", "N", "O"])
                # Academic
                st.write("Academic")
                academic_performance, study_load = st.columns(2)
                with academic_performance: academic_performance_input = st.number_input("Academic Performance", min_value=0, max_value=5)
                with study_load: study_load_input = st.number_input("Study Load", min_value=0, max_value=5)
                teacher_student_relationship, future_career_concerns = st.columns(2)
                with teacher_student_relationship: teacher_student_relationship_input = st.number_input("Teacher-Student Relationship", min_value=0, max_value=5)
                with future_career_concerns: future_career_concerns_input = st.number_input("Future Career Concerns", min_value=0, max_value=5)
                # Psychological
                st.write("Psychological")
                anxiety_level, self_esteem = st.columns(2)
                with anxiety_level: anxiety_level_input = st.number_input("Anxiety Level", min_value=0, max_value=21)
                with self_esteem: self_esteem_input = st.number_input("Self Esteem", min_value=0, max_value=30)
                mental_health_history, depression = st.columns(2)
                with mental_health_history: mental_health_history_input = st.checkbox("Mental Health History")
                with depression: depression_input = st.number_input("Depression", min_value=0, max_value=27)
                # Physiological
                st.write("Physiological")
                blood_pressure, breathing_problem = st.columns(2)
                with blood_pressure: blood_pressure_input = st.number_input("Blood Pressure", min_value=0, max_value=5)
                with breathing_problem: breathing_problem_input = st.number_input("Breathing Problem", min_value=0, max_value=5)
                sleep_quality, headache = st.columns(2)
                with sleep_quality: sleep_quality_input = st.number_input("Sleep Quality", min_value=0, max_value=5)
                with headache: headache_input = st.number_input("Headache", min_value=0, max_value=5)

                if st.button("Insert/Update"):
                    df_target = pd.read_sql(f"SELECT * FROM Students WHERE student_id = {student_id_input}", st.session_state.db_conn)
                    if df_target.empty: message = "Data Inserted Successfully :)"
                    else: message = "Data Updated Successfully :)"
                    try: 
                        if mental_health_history_input == False: mental_health_history = 0
                        else: mental_health_history_input = 1 
                        if student_id_input == -1:
                            student_query = f"INSERT INTO Students (age, gender) VALUES ({age_input},'{gender_input}');"
                            academic_query = f"INSERT INTO Academic (academic_performance, study_load, teacher_student_relationship, future_career_concerns) VALUES ({academic_performance_input}, {study_load_input}, {teacher_student_relationship_input}, {future_career_concerns_input});" 
                            psychological_query = f"INSERT INTO Psychological (anxiety_level, self_esteem, mental_health_history, depression) VALUES ({anxiety_level_input}, {self_esteem_input}, {mental_health_history_input}, {depression_input});"
                            physiological_query = f"INSERT INTO Physiological (blood_pressure, breathing_problem, sleep_quality, headache) VALUES ({blood_pressure_input}, {breathing_problem_input}, {sleep_quality_input}, {headache_input});" 
                        else:
                            student_query = f"""INSERT INTO Students VALUES ({student_id_input}, {age_input}, '{gender_input}') 
                            ON CONFLICT(student_id) DO UPDATE SET 
                            age = excluded.age, 
                            gender = excluded.gender;"""
                            academic_query = f"""INSERT INTO Academic VALUES ({student_id_input}, {academic_performance_input}, {study_load_input}, {teacher_student_relationship_input}, {future_career_concerns_input}) 
                            ON CONFLICT (student_id) DO UPDATE SET 
                            academic_performance = excluded.academic_performance,
                            study_load = excluded.study_load,
                            teacher_student_relationship = excluded.teacher_student_relationship,
                            future_career_concerns = excluded.future_career_concerns;"""
                            psychological_query = f"""INSERT INTO Psychological VALUES ({student_id_input}, {anxiety_level_input}, {self_esteem_input}, {mental_health_history_input}, {depression_input})
                            ON CONFLICT (student_id) DO UPDATE SET
                            anxiety_level = excluded.anxiety_level,
                            self_esteem = excluded.self_esteem,
                            mental_health_history = excluded.mental_health_history,
                            depression = excluded.depression;"""
                            physiological_query = f"""INSERT INTO Physiological VALUES ({student_id_input}, {blood_pressure_input}, {breathing_problem_input}, {sleep_quality_input}, {headache_input})
                            ON CONFLICT (student_id) DO UPDATE SET
                            blood_pressure = excluded.blood_pressure,
                            breathing_problem = excluded.breathing_problem,
                            sleep_quality = excluded.sleep_quality,
                            headache = excluded.headache;"""
                        st.session_state.db_conn.execute(student_query)
                        st.session_state.db_conn.execute(academic_query)
                        st.session_state.db_conn.execute(psychological_query)
                        st.session_state.db_conn.execute(physiological_query)
                        st.session_state.db_conn.commit()
                        st.success(message)
                    except:
                        st.error("There is an error in the insertion data. Please double check your inputs")
                    
            with data_deletions:
                targeted_id = st.number_input("Student ID", step=1, min_value=0)
                if st.button("Delete Data Record"):
                    df_target = pd.read_sql(f"SELECT * FROM Students WHERE student_id={targeted_id};", st.session_state.db_conn)
                    if df_target.empty:
                        st.error("Record not found")
                    else:
                        academic_query = f"DELETE FROM Academic WHERE student_id={targeted_id};"
                        psychological_query = f"DELETE FROM Psychological WHERE student_id={targeted_id};"
                        physiological_query = f"DELETE FROM Physiological WHERE student_id={targeted_id};"
                        student_query = f"DELETE FROM Students WHERE student_id={targeted_id};"
                        st.session_state.db_conn.execute(academic_query)
                        st.session_state.db_conn.execute(psychological_query)
                        st.session_state.db_conn.execute(physiological_query)
                        st.session_state.db_conn.execute(student_query)
                        st.session_state.db_conn.commit()
                        st.success("Data record deleted successfully")
        else:
            st.write("Please upload a file")

# ----------------- AGGREGATE FUNCTION ----------------------
def argument_builder(dataframe, x_axis, y_axis, aggregate):
    # Use try-except to catch errors when performing math on text columns
    try:
        if y_axis == "None":
            match aggregate:
                case "Max": return dataframe[x_axis].max()
                case "Min": return dataframe[x_axis].min()
                case "Avg": return dataframe[x_axis].mean()
                case "Sum": return dataframe[x_axis].sum()
                case "Count": return dataframe[x_axis].count()
                case "None": return dataframe
        match aggregate:
            case "Max": return dataframe.groupby(x_axis)[y_axis].max().reset_index()
            case "Min": return dataframe.groupby(x_axis)[y_axis].min().reset_index()
            case "Avg": return dataframe.groupby(x_axis)[y_axis].mean().reset_index()
            case "Sum": return dataframe.groupby(x_axis)[y_axis].sum().reset_index()
            case "Count": return dataframe.groupby(x_axis)[y_axis].count().reset_index()
            case "None": return dataframe
    except (TypeError, ValueError):
        return None

# ----------------- DATA ANALYSIS TAB ----------------------
with tab_data_analysis:
    analysis_tab, saved_tab = st.tabs(["Analyze Data", "Saved Graphs"])

    # ----------- ANALYZE DATA TAB ---------------
    with analysis_tab:
        if st.session_state.db_valid:
            df = st.session_state.global_df
            
            # Populate options based on columns
            opts = list(df.columns) 

            x_axis = st.selectbox(label="X-Axis", options=opts)
            y_axis = st.selectbox(label="Y-Axis", options=["None"] + opts)
            
            st.text("^^^^ Leave as none if you simply just want to aggregate a single attribute ^^^^")
            
            aggregate_function = st.selectbox(label="Aggregate Function", options=["None", "Max", "Min", "Avg", "Sum", "Count"])

            if y_axis == x_axis:
                st.error("Please choose two different axes")

            elif y_axis == "None":
                # Handle single column aggregation
                aggregate = argument_builder(df, x_axis, y_axis, aggregate_function)
                
                # Safely display result or error
                if aggregate is None:
                    st.error(f"Cannot calculate '{aggregate_function}' for '{x_axis}'. Ensure the data is numeric (not text).")
                else:
                    match aggregate_function:
                        case "Max": st.write(f"Maximum: {aggregate}")
                        case "Min": st.write(f"Minimum: {aggregate}")
                        case "Avg": st.write(f"Global Average: {aggregate}")
                        case "Sum": st.write(f"Global Sum: {aggregate}")
                        case "Count": st.write(f"Global Count: {aggregate}")

            else:
                # --- GRAPH BUTTON ---
                if st.button("Graph"):
                    data = argument_builder(df, x_axis, y_axis, aggregate_function)
                    
                    if data is None:
                        st.error(f"Cannot calculate '{aggregate_function}' for '{y_axis}'. Ensure the data is numeric (not text).")
                    else:
                        st.session_state.graph_data = data
                        st.session_state.graph_x = x_axis
                        st.session_state.graph_y = y_axis
                        st.session_state.graph_agg = aggregate_function
                        st.session_state.graph_ready = True

                # --- SHOW GRAPH ---
                if st.session_state.get("graph_ready", False):
                    df_grouped = st.session_state.graph_data
                    st.dataframe(df_grouped)

                    # Display Global Stats safely
                    try:
                        match st.session_state.graph_agg:
                            case "Max": st.write(f"Global Maximum: {df[y_axis].max()}")
                            case "Min": st.write(f"Global Minimum: {df[y_axis].min()}")
                            case "Avg": st.write(f"Global Average: {df[y_axis].mean()}")
                            case "Sum": st.write(f"Global Sum: {df[y_axis].sum()}")
                            case "Count": st.write(f"Global Count: {df[y_axis].count()}")
                    except (TypeError, ValueError):
                        st.warning(f"Could not calculate {st.session_state.graph_agg} for {y_axis} (likely text data).")

                    st.bar_chart(
                        data=df_grouped,
                        x=st.session_state.graph_x,
                        x_label=st.session_state.graph_x,
                        y=st.session_state.graph_y,
                        y_label=st.session_state.graph_y
                    )

                    # --- SAVE BUTTON ---
                    if st.button("Save This Graph"):
                        # Create figure explicitly to avoid threading issues
                        fig, ax = plt.subplots()
                        ax.bar(df_grouped[st.session_state.graph_x], df_grouped[st.session_state.graph_y])
                        ax.set_xlabel(st.session_state.graph_x)
                        ax.set_ylabel(st.session_state.graph_y)
                        ax.set_title(f"{st.session_state.graph_x} vs {st.session_state.graph_y}")
                        
                        img_bytes = BytesIO()
                        fig.savefig(img_bytes, format="png")
                        img_bytes.seek(0)
                        plt.close(fig)

                        st.session_state.saved_graphs.append({
                            "title": f"{st.session_state.graph_x} vs {st.session_state.graph_y} ({st.session_state.graph_agg})", 
                            "image": img_bytes
                        })
                        st.success("Graph saved!")

        else:
            st.write("Please input a file in the data management tab")

    # ----------- SAVED GRAPHS TAB ---------------
    with saved_tab:
        if not st.session_state.saved_graphs:
            st.info("No graphs saved yet.")
        else:
            for i, graph in enumerate(st.session_state.saved_graphs):
                st.divider()
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(graph["title"])
                    st.image(graph["image"])
                with col2:
                    # Create a safe filename based on title
                    safe_title = "".join([c for c in graph["title"] if c.isalnum() or c in (' ','-','_')]).strip()
                    
                    st.download_button(
                        label="Download PNG",
                        data=graph["image"].getvalue(),
                        file_name=f"{safe_title}.png",
                        mime="image/png",
                        key=f"dnld_{i}"
                    )
                    
                    if st.button("Delete", key=f"del_{i}"):
                        st.session_state.saved_graphs.pop(i)
                        st.rerun()