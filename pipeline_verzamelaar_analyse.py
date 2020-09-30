import psycopg2
import json

def get_table_names(cursor):
    cur.execute('''
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_type='BASE TABLE';
    ''')


def get_json_from_id(cursor, id):
    cursor.execute("SELECT json FROM raw_json WHERE id=%s", (id,))
    return cursor.fetchall()


def cleanup_json(json_string):
    json.loads(json_string)
    pass

def main():
    return

# dbname: pocdb
# dbuser: pocuser
# dbpassword: pocuser
# HOST: weert.lucimmerzeel.nl
# PORT: 5432

# Connect to your postgres DB
conn = psycopg2.connect(
    host="weert.lucimmerzeel.nl",
    port="5432",
    database="pocdb",
    user="pocuser",
    password="pocuser")

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a query
json_out = get_json_from_id(cur, 69)


# Retrieve query results
records = cur.fetchall()

if __name__ == "__main__":
    main()