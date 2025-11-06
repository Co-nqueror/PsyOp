import pandas as pd
import sqlite3
import os

def load_csv_to_dataframe(csv_file_name: str) -> pd.DataFrame | None:
    """
    Loads a specified CSV file into a pandas DataFrame.
    """
    if not os.path.exists(csv_file_name):
        print(f"Error: File not found at '{csv_file_name}'")
        return None
        
    try:
        df = pd.read_csv(csv_file_name)
        print(f"Successfully loaded '{csv_file_name}'")
        return df
    except Exception as e:
        print(f"An error occurred while loading {csv_file_name}: {e}")
        return None

def list_database_tables(db_name: str = 'Dataset.db') -> pd.DataFrame | None:
    """
    Lists all tables in the specified SQLite database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables_df = pd.read_sql_query(query, conn)
        return tables_df
    except sqlite3.Error as e:
        print(f"An error occurred with the database: {e}")
        return None
    finally:
        if conn:
            conn.close()

def query_db_to_dataframe(query: str, db_name: str = 'Dataset.db') -> pd.DataFrame | None:
    """
    Executes a SQL query on the database and returns the result as a
    pandas DataFrame.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"An error occurred executing query: {e}")
        print(f"Query: {query}")
        return None
    finally:
        if conn:
            conn.close()


# --- THIS BLOCK IS NEW ---
# This code will ONLY run when you execute `pandas_handler.py` directly.
# It will NOT run when you import it in Jupyter.
if __name__ == "__main__":
    
    print("--- Running pandas_handler.py as a script for testing ---")
    
    # Test 1: List tables
    print("\nTesting list_database_tables():")
    tables = list_database_tables()
    if tables is not None:
        print(tables)
    else:
        print("Could not list tables.")

    # Test 2: Load a CSV
    print("\nTesting load_csv_to_dataframe():")
    csv_df = load_csv_to_dataframe('StressLevelDataset.csv')
    if csv_df is not None:
        print("CSV loaded successfully. First 5 rows:")
        print(csv_df.head())
    else:
        print("Could not load CSV.")

    # Test 3: Run a query
    print("\nTesting query_db_to_dataframe():")
    query = "SELECT * FROM Academic LIMIT 3;"
    query_df = query_db_to_dataframe(query)
    if query_df is not None:
        print(f"Query '{query}' successful:")
        print(query_df)
    else:
        print("Query failed.")