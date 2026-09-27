import duckdb

SQL_FILE = "sql/analytics.sql"

with open(SQL_FILE, "r") as f:
    sql_script = f.read()

# Split the SQL file into individual queries
queries = [
    query.strip()
    for query in sql_script.split(";")
    if query.strip()
]

conn = duckdb.connect()

for i, query in enumerate(queries, start=1):
    print("\n" + "=" * 70)
    print(f"QUERY {i}")
    print("=" * 70)

    try:
        result = conn.execute(query).df()
        print(result.to_string(index=False))
    except Exception as e:
        print(f"ERROR: {e}")

conn.close()