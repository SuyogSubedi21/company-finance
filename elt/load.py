import json
import uuid
from db import get_connection

CATALOG = "workspace"
SCHEMA = "bronze"


def create_bronze_table(cursor, table):
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.{table} (
            raw_json STRING,
            source_endpoint STRING,
            page_number INT,
            batch_id STRING,
            ingested_at TIMESTAMP
        )
    """)
    
    
def insert_rows(cursor, table, endpoint, page_number, batch_id, records, chunk_size=50):
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        params = {f"j{n}": json.dumps(record) for n, record in enumerate(chunk)}
        values = ", ".join(
            f"(:j{n}, '{endpoint}', {page_number}, '{batch_id}', current_timestamp())"
            for n in range(len(chunk))
        )
        cursor.execute(f"INSERT INTO {CATALOG}.{SCHEMA}.{table} VALUES {values}", params)
        
        
        
def load(endpoint, table, pages):
    batch_id = str(uuid.uuid4())
    total = 0

    with get_connection() as conn:
        with conn.cursor() as cursor:
            create_bronze_table(cursor, table)
            for page_number, records in pages:
                insert_rows(cursor, table, endpoint, page_number, batch_id, records)
                total += len(records)

    print(f"Loaded {total} rows into {CATALOG}.{SCHEMA}.{table} (batch {batch_id})")
    return batch_id