from pipeline_base import database_connection
from typing import Union, List, Dict, Tuple, Any

class pipeline_analyse_to_db(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)
    
    def add_new_entry(self, word: str, institute_id: int, count: int, institute: str) -> None:
        self.enter_command("INSERT INTO {0} VALUES (\'{1}\', {2}, {3})".format(institute, word, institute_id, count))
    
    def add_dict(self, words: List[str], institute: str) -> None:
        for key in words:
            self.add_new_entry(key, words[key][1], words[key][0], institute)


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
            return self.get_dict(self.get_by_institute(institute))

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