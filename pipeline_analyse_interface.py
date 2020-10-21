from pipeline_base import database_connection
from typing import Union, List, Dict, Tuple, Any
import datetime

class pipeline_analyse_to_db(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)
    
    def add_new_entry(self, word: str, count: int, institute: str) -> None:
        current_time = datetime.datetime.now()
        date_id = self.add_unique_entry("dates_", "date", "date_id", current_time.strftime("%Y") +"-" + current_time.strftime("%M"))
        word_id = self.add_unique_entry("words_", "word", "word_id", word)
        institute_id = self.add_unique_entry("institutes_", "institute", "institute_id", institute)
        self.enter_command("INSERT INTO entries_ (word, word_count, date, institute) VALUES ({0}, {1}, {2}, {3})".format(word_id, count, date_id, institute_id))
    
    def add_dict(self, words, institute: str) -> None:
        for key in words:
            self.add_new_entry(key, words[key], institute)

    def add_unique_entry(self, table_name, attribute_name, value):
        if not self.fetch_command("SELECT * FROM {0} WHERE {1} = {2}".format(table_name, attribute_name, value)):
            self.enter_command("INSERT INTO {0} ({1}) VALUES ({2})".format(table_name, attribute_name, value))
        return self.fetch_command("SELECT {0}_id FROM {1} WHERE {0} = {2}".format(attribute_name, table_name, value))


class pipeline_db_to_interface(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)

    def get_id_entity(self, table_name, attribute_name, value):
        return self.fetch_command("SELECT {0}_id FROM {1} WHERE {0} = {2}".format(attribute_name, table_name, value))

    def get_entries(self, date=None, word=None, institute=None):
        query = ""
        if date:
            query += self.add_to_query(query, "date", self.get_id_entity("dates_", "date", date))
        if word:
            query += self.add_to_query(query, "word", self.get_id_entity("words_", "word", word))
        if institute:
            query += self.add_to_query(query, "institute", self.get_id_entity("institutes_", "institute", institute))
        return self.fetch_command("SELECT * FROM entries_" + query) ## List[Tuple[entry_id, word_id, word_count, date_id, institute_id]]
    
    def add_to_query(self, query, attribute_name, attribute_id):
        if len(query) > 0:
            query += " AND "
        else:
            query += " WHERE "
        return query + attribute_name + " = " + attribute_id

    def get_by_time_period(self, start_date, end_date, word=None, institute=None):
        start_date_id = self.get_id_entity("dates_", "date", start_date)
        end_date_id = self.get_id_entity("dates_", "date", start_date)
        data = {}
        for date_id in range(end_date_id, start_date_id + 1):
            actual_date = self.fetch_command("SELECT date FROM dates_ WHERE date_id = {0}".format(date_id))
            data[actual_date] = self.get_entries(date=actual_date, word=word, institute=institute)
        return data
        
    def get_lookup_table(self, table_name):
        return self.fetch_command("SELECT * FROM {0}".format(table_name))

    
    def get_dict(self, data_entries):
        dates_all_info = self.get_lookup_table("")






    def create_dict(self, institute: str) -> Union[Dict[str, int], Dict[str, Dict[str, int]]]:
        if institute == "*":
            return self.get_multi_dict(self.get_all_entries())
        else:
            return self.get_dict(self.get_by_institute(institute))

    def get_dict(self, data_entries: List[Tuple[int, int, int]]) -> Dict[str, int]:
        dates_all_info = self.get_lookup_table("dates_") ## (word, word_id)
        words_all_info = self.get_lookup_table("words_") ## (date, date_id)

        entry_dict = {}

        for data_entry in data_entries:
            entry_dict[words_all_info[data_entry[0]][1]] += data_entry[1]
        return entry_dict
    
    def get_multi_dict(self, dataset: List[Tuple[List[str], List[Tuple[str, int, int]]]]) -> Dict[str, Dict[str, int]]:
        multi_dict = {}
        for data_entries in dataset:
            entry_dict = {}
            for data_entry in data_entries[1]:
                entry_dict[data_entry[0]] = data_entry[2]
            multi_dict[data_entries[0][0]] += entry_dict
        return multi_dict