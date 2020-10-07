import psycopg2
import json
from typing import Union, List, Dict, Tuple, Any


class database_connection:
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database_name = database_name
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self) -> None:
        self.connection = psycopg2.connect(host=self.host, port=self.port, 
                          database=self.database_name, user=self.user, password=self.password)
        self.cursor = self.connection.cursor()
    
    def enter_command(self, command: str) -> None:
        self.cursor.execute(command)
        self.connection.commit()
    
    def fetch_command(self, command: str) -> List[Tuple[Any]]:
        self.cursor.execute(command)
        return self.cursor.fetchall()
    
    def clear_table(self, table_name: str) -> None:
        self.enter_command("DELETE FROM {}".format(table_name))


class pipeline_analyse_to_db(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)
    
    def add_new_entry(self, word: str, institute: str, count: int) -> None:
        self.enter_command("INSERT INTO output VALUES (\'{0}\', {1}, {2})".format(word, institute_id, count))


class pipeline_db_to_interface(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)

    def get_by_institute(self, institute: str) -> List[Tuple[str, int, int]]:
        return self.fetch_command("SELECT * FROM {}".format(institute))
    
    def get_all_entries(self) -> List[Tuple[List[str], List[Tuple[str, int, int]]]]:
        entries = []
        for institute in self.fetch_command("select table_name from innodb.INFORMATION_SCHEMA.TABLES where TABLE_TYPE = 'BASE TABLE' and not table_name like 'pg_%' and not table_name like 'sql_%'"):
            entries.append([institute, self.get_by_institute(institute[0])])
        return entries

    def create_dict(self, institute: str) -> Union[Dict[str, int], Dict[str, Dict[str, int]]]:
        if institute == "*":
            return self.get_multi_dict(self.get_all_entries())
        else:
            return self.get_dict(self.get_by_institute(int(institute)))

    def get_dict(self, data_entries: List[Tuple[str, int, int]]) -> Dict[str, int]:
        entry_dict = {}
        for data_entry in data_entries:
            entry_dict[data_entry[0]] = data_entry[2]
        return entry_dict
    
    def get_multi_dict(self, dataset: List[Tuple[List[str], List[Tuple[str, int, int]]]]) -> Dict[str, Dict[str, int]]:
        multi_dict = {}
        for data_entries in dataset:
            entry_dict = {}
            for data_entry in data_entries[1]:
                entry_dict[data_entry[0]] = data_entry[2]
            multi_dict[data_entries[0][0]] = entry_dict
        return multi_dict


class pipeline_db_to_analyse(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)


    def get_json_all(self):
        return self.fetch_command(command="SELECT json FROM raw_json")

    
    def cleanup_json(self, json_string: str):
        desc_string = ""
        if "description" in json_string:
            desc_string = json.loads(json_string)["description"]
        elif "content" in json_string:
            desc_string = json.loads(json_string)["content"]    
        
        # Some descriptions include the working hours. For this example (analyzing third word)
        # the line is removed.
        if "Working hours" in desc_string:
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
            desc_string = desc_string.replace("<strong>", "")
            desc_string = desc_string.replace("</strong>", "")
            desc_string = desc_string.replace("<br />", "")
        return desc_string

    def get_descriptions(self):
        descriptions = []
        print("Grabbing jsons...", end="")
        jsons = self.get_json_all()
        print("Done!\nCleaning descriptions...", end="")

        for json in jsons:
            descriptions.append(self.cleanup_json(json[0]))
        
        print("Done!\nAmount of descriptions: {}".format(len(descriptions)))
        return descriptions


test = pipeline_db_to_analyse(
    host="weert.lucimmerzeel.nl",
    port="5432",
    database_name="pocdb",
    user="pocuser",
    password="pocuser")

desc_list = test.get_descriptions()
print(desc_list[0])
print(desc_list[1])
print(desc_list[2])