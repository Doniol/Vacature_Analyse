from pipeline_base import database_connection
import json
from html import entities
from typing import List, Tuple
import re


class pipeline_db_to_analyse(database_connection):
    ''' A class for sending data between the first database and the analysis tool
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

    def get_json_all(self) -> List[Tuple[str]]:
        ''' This function returns all the JSON-strings from the database

        return: A list of JSON-strings
        '''
        return self.fetch_command(command="SELECT json FROM raw_json", vars=tuple())

    def camel_case_to_phrase(self, s: str) -> str:
        ''' This function splits camelCase words into seperate words

        s: The word or the whole sentence
        return: The new string without the camelCase
        '''
        prev = None
        t = []
        n = len(s)
        i = 0

        while i < n:
            next_char = s[i+1] if i < n -1 else ''
            c = s[i]
            if prev is None:
                t.append(c)
            elif c.isupper() and prev.isupper():
                if next_char.islower():
                    t.append(' ')
                    t.append(c)
                else:
                    t.append(c)
            elif c.isupper() and not prev.isupper():
                t.append(' ')
                t.append(c)
            else:
                t.append(c)
            prev = c
            i = i +1

        return "".join(t)

    def cleanup_json(self, json_string: str) -> str:
        ''' This function removes HTML-tags from the JSON strings

        The function removes HTML tags (<br>, </br>, <p>, etc.) from the JSON string and replaces the character
         references (&euml;, &egrave;, etc)with their UTF-8 counterpart.
        
        json_string: The JSON-file, as a string
        return: The cleaned up description
        '''
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
        
        # Regex or Regular Expression
        # . means every character except newline
        # * matches zero or unlimited times
        # ? matches zero or once
        # This expression only removes the tags: it doesn't matches the text between them
        tmp = re.compile("<.*?>")

        # FInd all matching substrings and replace them with an empty string
        desc_string = re.sub(tmp, "", desc_string)

        # Replace the HTML-chars with UTF-8 chars
        desc_string = desc_string.replace("&egrave;", entities.html5["egrave;"])    # è
        desc_string = desc_string.replace("&eacute;", entities.html5["eacute;"])    # é
        desc_string = desc_string.replace("&euml;", entities.html5["euml;"])        # ë
        desc_string = desc_string.replace("&ecirc;", entities.html5["ecirc;"])      # ê
        desc_string = desc_string.replace("&ouml;", entities.html5["ouml;"])        # ö
        desc_string = desc_string.replace("&iuml;", entities.html5["iuml;"])        # ï
        desc_string = desc_string.replace("&nbsp;", entities.html5["nbsp;"])        # whitespace
        desc_string = desc_string.replace("&rsquo;", "'")                           # '
        desc_string = desc_string.replace("&#39;", "'")                             # '
        desc_string = desc_string.replace("’", "'")                                 # '
        
        desc_string = self.camel_case_to_phrase(desc_string)
        return desc_string

    def get_descriptions(self, amount: int) -> List[str]:
        ''' This function returns the desired amount of job-offer descriptions

        amount: The desired amount of descriptions
        return: A list of descriptions
        '''
        descriptions = []
        print("Grabbing jsons...", end="")
        jsons = self.get_json_all()
        print("Done!\nCleaning descriptions...", end="")

        for json in jsons[:amount]:
            descriptions.append(self.cleanup_json(json[0]))
        
        print("Done!\nAmount of descriptions: {}".format(len(descriptions)))
        return descriptions