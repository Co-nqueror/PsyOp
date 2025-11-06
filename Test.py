# Import the new pandas_handler module
import pandas_handler as ph
import pandas as pd
import SQL_Handler

print(SQL_Handler.data_selection("Students", "*", "Students.gender = \'M\'", "Academic"))

# Set pandas to display all columns (optional, but helpful)
pd.set_option('display.max_columns', None)

# --- Example 1: List all tables in the database ---
print("--- Tables in Database ---")
tables_df = ph.list_database_tables()
if tables_df is not None:
    print(tables_df)
else:
    print("Could not list tables.")

# --- Example 2: Load the 'StressLevelDataset.csv' file ---
print("\n--- Loading 'StressLevelDataset.csv' ---")
csv_data = ph.load_csv_to_dataframe('StressLevelDataset.csv')
if csv_data is not None:
    print("Successfully loaded CSV, here's the top 5 rows:")
    print(csv_data.head())
else:
    print("Could not load CSV.")

# --- Example 3: Run the JOIN query from your original Test.py ---
print("\n--- Running JOIN Query for Male Students ---")

# This is the same query you had, but now it will be returned 
# as a clean pandas DataFrame.
my_query = """
SELECT 
    s.*, 
    a.academic_performance, 
    a.study_load,
    a.future_career_concerns
FROM 
    Students s
JOIN 
    Academic a ON s.student_id = a.student_id
WHERE 
    s.gender = 'M';
"""

# Use the new function to run the query
joined_data = ph.query_db_to_dataframe(my_query)

if joined_data is not None:
    print("Query successful, here's the result:")
    print(joined_data)
else:
    print("Query failed.")