import psycopg2
import json
from typing import Union, List, Dict, Tuple, Any


class database_connection:
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str):
        ''' A function for initialising the pipeline

        host: A link to the host of the database
        port: The port on which the database is hosted
        database_name: The name of the desired database
        user: The username necessary to login into the database
        password: The password necessary to login into the database
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
    
    def enter_command(self, command: str, vars: Tuple[Any]) -> None:
        ''' This function is used to command the database directly
        
        command: The command you want to run
        vars: The parameters of the query
        '''
        self.cursor.execute(command, vars)
        self.connection.commit()
    
    def fetch_command(self, command: str, vars: Tuple[Any]) -> List[Tuple[Any]]:
        ''' This function fetches data from the data_base

        command: The sql command you want to use for data extraction
        vars: The parameters of the query
        return: A list of tuples which contain the desired data
        '''
        self.cursor.execute(command, vars)
        return self.cursor.fetchall()
    
    def clear_table(self, table_name: str) -> None:
        ''' This functions removes all the data of a table

        table_name: The name of the table you want to clear
        '''
        self.enter_command("DELETE FROM {}".format(table_name), (tuple()))
