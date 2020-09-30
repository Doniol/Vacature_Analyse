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
    # Clean the description up by removing the HTML-tags and remove
    # first line (this line not needed for example word count)
    # Load json as dict() and put the ["description"] in desc_string
    desc_string = json.loads(json_string)["description"]
    
    index = None
    for i in range(0,len(desc_string)):
        if desc_string[i] == "\n":
            index = i+1
            break
    desc_string = desc_string[index:]
    
    # Replace every instance of <p>, </p>, etc with empty string ""
    for i in desc_string:
        desc_string = desc_string.replace("<p>", "")
        desc_string = desc_string.replace("</p>", "")
        desc_string = desc_string.replace("<li>", "")
        desc_string = desc_string.replace("</li>", "")
        desc_string = desc_string.replace("<ul>", "")
        desc_string = desc_string.replace("</ul>", "")
    return desc_string
    

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

# Print the cleaned description
print(cleanup_json(get_json_from_id(cur, 69)[0][0]))

if __name__ == "__main__":
    main()