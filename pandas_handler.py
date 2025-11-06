import pandas as pd
import sqlite3
import os

def load_csv_to_dataframe(csv_file_name: str) -> pd.DataFrame | None:
    """
    Loads a specified CSV file into a pandas DataFrame.

    Args:
        csv_file_name (str): The name of the CSV file to load.

    Returns:
        pd.DataFrame | None: A DataFrame containing the CSV data, 
                              or None if an error occurs.
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

    Args:
        db_name (str): The name of the database file.

    Returns:
        pd.DataFrame | None: A DataFrame listing the table names, 
                              or None if an error occurs.
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

    Args:
        query (str): The SQL query to execute.
        db_name (str): The name of the database file.

    Returns:
        pd.DataFrame | None: A DataFrame with the query results, 
                              or None if an error occurs.
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