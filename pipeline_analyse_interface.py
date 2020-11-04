from pipeline_base import database_connection
from typing import Union, List, Dict, Tuple, Any
import datetime

class pipeline_analyse_to_db(database_connection):
    ''' A class that creates a pipeline between the analysis and it's corresponding database
    '''
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        ''' A function for initialising the pipeline

        host: A link to the host of the database
        port: The port on which the database is hosted
        database_name: The name of the desired database
        user: The username necessary to login into the database
        password: The password necessary to login into the database
        '''
        database_connection.__init__(self, host, port, database_name, user, password)
    
    def add_new_entry(self, word: str, count: int, institute: str) -> None:
        ''' A function to add a new entry into the analysis database

        word: The word that needs to be inserted into the database
        count: The amount of times that that word has been counted
        institute: The institute that this entry belongs to
        '''
        current_time = datetime.datetime.now()
        date = current_time.strftime("%Y") + "-" + current_time.strftime("%m")
        date_id = self.add_unique_entry("date", date)
        word_id = self.add_unique_entry("word", word)
        institute_id = self.add_unique_entry("institute", institute)
        self.enter_command("INSERT INTO entries_ {} VALUES (%s, %s, %s, %s)".format("(word_id, word_count, date_id, institute_id)"), (word_id, count, date_id, institute_id,))

    def add_dict(self, words: Dict[str, int], institute: str) -> None:
        ''' Stores the given dict in the database as seperate entries

        words: A dict containing the counted words, and how many times they've been counted
        institute: The name of the institute that these words belong to
        '''
        for key in words:
            self.add_new_entry(key, words[key], institute)

    def add_unique_entry(self, attribute_name: str, value: str) -> int:
        ''' Adds the given value to the selected table

        attribute_name: The name of the attribute that is to be saved, we can determine the table-name and id-name of the table using this
        value: The value that is te be stored
        return: The ID of the newly created entry
        '''
        if self.fetch_command("SELECT * FROM {0}s_ WHERE {0} = %s".format(attribute_name), (value,)) == []:
            self.enter_command("INSERT INTO {0}s_ ({0}) VALUES (%s)".format(attribute_name), (value,))
        return self.fetch_command("SELECT {0}_id FROM {0}s_ WHERE {0} = %s".format(attribute_name), (value,))[0][0]

    def clear_all_tables(self, reset_increment: bool=False) -> None:
        ''' Function for clearing all database tables and, if selected, resetting the AUTO_INCREMENT valeus

        reset_increment: A bool to determine wether the ID's should start at 1 again
        '''
        self.clear_table("entries_")
        self.clear_table("dates_")
        self.clear_table("institutes_")
        self.clear_table("words_")

        if reset_increment:
            self.enter_command("ALTER TABLE entries_ AUTO_INCREMENT = 1")
            self.enter_command("ALTER TABLE dates_ AUTO_INCREMENT = 1")
            self.enter_command("ALTER TABLE institutes_ AUTO_INCREMENT = 1")
            self.enter_command("ALTER TABLE words_ AUTO_INCREMENT = 1")


class pipeline_db_to_interface(database_connection):
    ''' A class that creates a pipeline between the analysis database and the interface
    '''
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        ''' A function for initialising the pipeline

        host: A link to the host of the database
        port: The port on which the database is hosted
        database_name: The name of the desired database
        user: The username necessary to login into the database
        password: The password necessary to login into the database
        '''
        database_connection.__init__(self, host, port, database_name, user, password)

    def get_entity_id(self, attribute_name: str, value: str) -> int:
        ''' Returns the ID of the selected attribute containing the given value

        attribute_name: The name of the attribute that is to be fetched, we can determine the table-name and ID-name of the table using this
        value: The value that the selected attribute needs to contain
        return: The ID of the selected attribute with the given value
        '''
        return self.fetch_command("SELECT {0}_id FROM {0}s_ WHERE {0} = %s".format(attribute_name), (value,))[0][0]

    def get_entries(self, date: str=None, word: str=None, institute: str=None) -> List[Tuple[int, int, int, int, int]]:
        ''' Returns all entries that correspond to whatever requirements have been provided

        date: If given, the date on which the desired entries have been added
        word: If given, the word which the desired entries refer to
        institute: If given, the institute to which the word has to be linked to
        return: A list containing tuples of each selected entry
        '''
        query = ""
        if date:
            query += self.add_to_query(query, "date_id", self.get_entity_id("date", date))
        if word:
            query += self.add_to_query(query, "word_id", self.get_entity_id("word", word))
        if institute:
            query += self.add_to_query(query, "institute_id", self.get_entity_id("institute", institute))
        return self.fetch_command("SELECT * FROM entries_" + query, tuple()) ## List[Tuple[entry_id, word_id, word_count, date_id, institute_id]]
    
    def add_to_query(self, query: str, attribute_name: str, attribute_id: int) -> str:
        ''' Returns the given query combined with a new command

        query: The existing query
        attribute_name: The name of the to be added attribute
        attribute_id: The id of the to be added attribute
        return: The new query
        '''
        if len(query) > 0:
            query += " AND "
        else:
            query += " WHERE "
        return query + attribute_name + " = " + str(attribute_id)

    def get_by_time_period(self, start_date: str, end_date: str, word: str=None, institute: str=None) -> Dict[str, List[Tuple[int]]]:
        ''' Function that returns all entries that were added between 2 selected dates

        start_date: First date, after which entries need to be selected
        end_date: Second date, before which entries need to be selected
        word: If selected, select only entries that refer to this word
        institute: If selected, select only entries that refer to this institute
        return: A dict coupling a date with a list of tuples containing all selected entries
        '''
        start_date_id = self.get_entity_id("date", start_date)
        end_date_id = self.get_entity_id("date", start_date)
        data = {}
        for date_id in range(end_date_id, start_date_id + 1):
            actual_date = self.fetch_command("SELECT date FROM dates_ WHERE date_id = %s", (date_id,))
            data[actual_date] = self.get_entries(date=actual_date, word=word, institute=institute)
        return data
        
    def get_lookup_table(self, table_name: str) -> List[Tuple[int, str]]:
        ''' Function that returns the selected lookup_table

        table_name: The name of the selected lookup_table
        return: A list of tuples containing all entries from the selected table
        '''
        return self.fetch_command("SELECT * FROM {}".format(table_name), tuple())

    def get_dict(self, data_entries: List[Tuple[int, int, int, int, int]]) -> Dict[int, Dict[str, Any]]:
        ''' A function that turns the given data_entries into a dict

        data_entries: A list of tuples containing each entry
        return: A dict containing a dict for each entry_id, containing all of it's data
        '''
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