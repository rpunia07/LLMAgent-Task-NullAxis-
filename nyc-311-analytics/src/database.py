import duckdb
import pandas as pd
import os

def init_database(csv_path):
    conn = duckdb.connect(database=':memory:')
    
    if os.path.exists(csv_path):
        conn.execute(f"CREATE TABLE data AS SELECT * FROM read_csv_auto('{csv_path}')")
    else:
        print(f"File not found: {csv_path}")
        
    return conn

def execute_query(conn, sql):
    try:
        return conn.execute(sql).df()
    except Exception as e:
        print(f"SQL Error: {e}")
        return pd.DataFrame()

def get_schema_info(conn):
    try:
        df = conn.execute("DESCRIBE data").df()
        return {
            "columns": df['column_name'].tolist(),
            "types": df['column_type'].tolist(),
            "samples": conn.execute("SELECT * FROM data LIMIT 1").df().iloc[0].to_dict()
        }
    except Exception as e:
        print(f"Schema Error: {e}")
        return {"columns": [], "error": str(e)}
