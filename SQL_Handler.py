import sqlite3

conn = sqlite3.connect('Dataset.db')
cursor = conn.cursor()

def data_selection(table_name, column_name, condition=None, join_table=None):
    if join_table is None and condition is None:
        query = f"SELECT {column_name} FROM {table_name};"
    elif join_table is None and condition is not None:
        query = f"SELECT {column_name} FROM {table_name} WHERE {condition};"
    elif join_table is not None and condition is None:
        query = f"SELECT {column_name} FROM {table_name} JOIN {join_table} ON {table_name}.student_id = {join_table}.student_id;"
    elif join_table is not None and condition is not None:
        query = f"SELECT {column_name} FROM {table_name} INNER JOIN {join_table} ON {table_name}.student_id = {join_table}.student_id WHERE {condition};"
    cursor.execute(query)
    return cursor.fetchall()


