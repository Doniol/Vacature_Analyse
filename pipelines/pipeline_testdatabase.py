from pipelines.pipeline_base import database_connection
from typing import List


class pipeline_converter_to_testsetdb(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        ''' A function for initialising the pipeline

        host: A link to the host of the database
        port: The port on which the database is hosted
        database_name: The name of the desired database
        user: The username necessary to login into the database
        password: The password necessary to login into the database
        '''
        self.word_types = ['relevant_keywords', 'lemma_relevant_keywords', 'single_relevant_keywords', 'lemma_single_relevant_keywords', 'keywords', 'lemma_Keywords', 'single_keywords', 'lemma_single_keyword']
        database_connection.__init__(self, host, port, database_name, user, password)
    
    def push_to_database(self, texts: Tuple[str, List[str], List[str], List[str], List[str], List[str], List[str], List[str], List[str]]) -> None:
        ''' A function for storing a dataset in the database

        texts: The to be stored dataset
        '''
        for text in texts:
            text_id = self.fetch_command("INSERT INTO vacatures (vacature_tekst) VALUES (%s) RETURNING vacature_id", (text[0].replace("'", "''"),))[0][0]
            for word_list_index in range(1, len(self.word_types)):
                for word in text[word_list_index]:
                    self.enter_command("INSERT INTO {0} (woord) VALUES (%s) ON CONFLICT DO NOTHING".format(self.word_types[word_list_index]), (word,))
                    word_id = self.fetch_command("SELECT woord_id FROM {0} WHERE woord = %s ".format(self.word_types[word_list_index]), (word,))[0][0]
                    self.enter_command("INSERT INTO vacatures_{0} VALUES (%s, %s) ON CONFLICT DO NOTHING".format(self.word_types[word_list_index]), (text_id, word_id,))

    def pull_from_database(self) -> Tuple[str, List[str], List[str], List[str], List[str], List[str], List[str], List[str], List[str]]:
        ''' Function for getting the dataset from the database

        return: The dataset that is currently stored in the database
        '''
        texts = self.fetch_command("SELECT vacature_id, vacature_tekst FROM vacatures")
        output = []
        for text in texts:
            lists = [text[1]]
            for word_type in self.word_types:
                words = []
                for word in self.fetch_command("SELECT {0}.woord FROM {0} WHERE woord_id IN (SELECT woord_id FROM vacatures_{0} WHERE vacature_id = %s)".format(word_type), (text[0],)):
                    words.append(word[0])
                lists.append(words)
            output.append(lists)
        return output
