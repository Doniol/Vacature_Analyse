import psycopg2
import json

def get_table_names(cursor):
    cursor.execute('''
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_type='BASE TABLE';
    ''')


def get_json_from_id(cursor, id):
    cursor.execute("SELECT json FROM raw_json WHERE id=%s", (id,))
    return cursor.fetchall()

def get_json_all(cursor):
    cursor.execute("SELECT json FROM raw_json")
    return cursor.fetchall()


def cleanup_json(json_string):
    # Clean the description up by removing the HTML-tags and remove
    # first line (this line not needed for example word count)

    # =================================
    # Some json's don't have a 'description' tag
    # =================================

    # Load json as dict() and put the ["description"] in desc_string
    desc_string = ""
    try:
        desc_string = json.loads(json_string)["description"]
    except KeyError:
        desc_string = json.loads(json_string)["content"]
    
    
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

    # List of strings. This will later be used for the cleaned up descriptions
    descriptions = []

    print("Grabbing json-files...", end="")
    jsons = get_json_all(cur)
    print(jsons[0])
    print("Done!\nCleaning descriptions...", end="")
    for json in jsons:
        # Elements are in a tupple, at index 0
        # Store the cleaned descriptions in a list of strings
        descriptions.append(cleanup_json(json[0]))    
    print("Done!\nAmount of descriptions: {}".format(len(descriptions)))

if __name__ == "__main__":
    main()