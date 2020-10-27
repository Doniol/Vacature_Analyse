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
    
    def enter_command(self, command: str, vars: tuple) -> None:
        self.cursor.execute(command, vars)
        self.connection.commit()
    
    def fetch_command(self, command: str, vars: tuple) -> List[Tuple[Any]]:
        self.cursor.execute(command, vars)
        return self.cursor.fetchall()
    
    def clear_table(self, table_name: str) -> None:
        self.enter_command("DELETE FROM {}".format(table_name), (tuple()))
