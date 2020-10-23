from pipeline_base import database_connection
from typing import Union, List, Dict, Tuple, Any
import datetime

class pipeline_analyse_to_db(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)
    
    def add_new_entry(self, word: str, count: int, institute: str) -> None:
        current_time = datetime.datetime.now()
        date = current_time.strftime("%Y") + "-" + current_time.strftime("%m")
        date_id = self.add_unique_entry("dates_", "date", date)[0][0]
        word_id = self.add_unique_entry("words_", "word", word)[0][0]
        institute_id = self.add_unique_entry("institutes_", "institute", institute)[0][0]
        self.enter_command("INSERT INTO entries_ (word_id, word_count, date_id, institute_id) VALUES ({0}, {1}, {2}, {3})".format(word_id, count, date_id, institute_id))
    
    def add_dict(self, words, institute: str) -> None:
        for key in words:
            self.add_new_entry(key, words[key], institute)

    def add_unique_entry(self, table_name, attribute_name, value):
        if self.fetch_command("SELECT * FROM {0} WHERE {1} = \'{2}\'".format(table_name, attribute_name, value)) == []:
            self.enter_command("INSERT INTO {0} ({1}) VALUES (\'{2}\')".format(table_name, attribute_name, value))
        return self.fetch_command("SELECT {0}_id FROM {1} WHERE {0} = \'{2}\'".format(attribute_name, table_name, value))

    def clear_all_tables(self):
        self.clear_table("entries_")
        self.clear_table("dates_")
        self.clear_table("institutes_")
        self.clear_table("words_")


class pipeline_db_to_interface(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)

    def get_entity_id(self, table_name, attribute_name, value):
        return self.fetch_command("SELECT {0}_id FROM {1} WHERE {0} = \'{2}\'".format(attribute_name, table_name, value))

    def get_entries(self, date=None, word=None, institute=None):
        query = ""
        if date:
            query += self.add_to_query(query, "date_id", self.get_entity_id("dates_", "date", date)[0][0])
        if word:
            query += self.add_to_query(query, "word_id", self.get_entity_id("words_", "word", word)[0][0])
        if institute:
            query += self.add_to_query(query, "institute_id", self.get_entity_id("institutes_", "institute", institute)[0][0])
        return self.fetch_command("SELECT * FROM entries_" + query) ## List[Tuple[entry_id, word_id, word_count, date_id, institute_id]]
    
    def add_to_query(self, query, attribute_name, attribute_id):
        if len(query) > 0:
            query += " AND "
        else:
            query += " WHERE "
        return query + attribute_name + " = " + str(attribute_id)

    def get_by_time_period(self, start_date, end_date, word=None, institute=None):
        start_date_id = self.get_entity_id("dates_", "date", start_date)
        end_date_id = self.get_entity_id("dates_", "date", start_date)
        data = {}
        for date_id in range(end_date_id, start_date_id + 1):
            actual_date = self.fetch_command("SELECT date FROM dates_ WHERE date_id = {0}".format(date_id))
            data[actual_date] = self.get_entries(date=actual_date, word=word, institute=institute)
        return data
        
    def get_lookup_table(self, table_name):
        return self.fetch_command("SELECT * FROM {0}".format(table_name))

    def get_dict(self, data_entries):
        dates_all_info = self.get_lookup_table("dates_")
        words_all_info = self.get_lookup_table("words_")

        entry_dict = {}

        for data_entry in data_entries:
            data_dict = {}
            data_dict["word_id"] = data_entry[1]
            data_dict["word_count"] = data_entry[2]
            data_dict["date_id"] = data_entry[3]
            data_dict["institute_id"] = data_entry[4]
            entry_dict[data_entry[0]] = data_dict
        return entry_dict