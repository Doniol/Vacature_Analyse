import psycopg2
import json
from typing import Union, List, Dict, Tuple, Any


class database_connection:
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str):
    ''' This function initializes the pipeline object.

    host:           The name of the host, string
    port:           The port number, string
    database_name:  The name of the database, string
    user:           The name of the user, string
    password:       The password of the user, string
    '''
        self.host = host
        self.port = port
        self.database_name = database_name
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self) -> None:
        ''' This function establishes the connection to the database
        '''
        self.connection = psycopg2.connect(host=self.host, port=self.port, 
                          database=self.database_name, user=self.user, password=self.password)
        self.cursor = self.connection.cursor()
    
    def enter_command(self, command: str, vars: tuple) -> None:
        ''' This function is used to command the database directly
        
        command: The commando you want 
        vars: the output format
        '''
        self.cursor.execute(command, vars)
        self.connection.commit()
    
    def fetch_command(self, command: str, vars: tuple) -> List[Tuple[Any]]:
        ''' This function fetches data from the data_base

        command: The sql command you want to get data of
        vars: the output format
        return: a list of tuples which contain the information of the collums
        '''
        self.cursor.execute(command, vars)
        return self.cursor.fetchall()
    
    def clear_table(self, table_name: str) -> None:
        ''' This functions removes all the data of a table

        table_name: the table you want to clear
        '''
        self.enter_command("DELETE FROM {}".format(table_name), (tuple()))
