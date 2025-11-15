import sqlite3

DB_NAME = 'Dataset.db'

def data_selection(table_name, column_name, condition=None, join_table=None):
    """Fetches data from the database."""
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = "" 
    
    try:
        if join_table is None and condition is None:
            query = f"SELECT {column_name} FROM {table_name};"
        
        elif join_table is None and condition is not None:
            query = f"SELECT {column_name} FROM {table_name} WHERE {condition};"
        
        elif join_table is not None and condition is None:
            query = f"SELECT {column_name} FROM {table_name} JOIN {join_table} ON {table_name}.student_id = {join_table}.student_id;"
        
        elif join_table is not None and condition is not None:
            query = f"SELECT {column_name} FROM {table_name} INNER JOIN {join_table} ON {table_name}.student_id = {join_table}.student_id WHERE {condition};"
        
        cursor.execute(query)
        results = cursor.fetchall()
        
    except Exception as e:
        print(f"SQL Error: {e}")
        print(f"Failed Query: {query}")
        return [] 
        
    finally:
        conn.close()
        
    return results