from pipeline_base import database_connection
import json
from html import entities


class pipeline_db_to_analyse(database_connection):
    ''' This function initializes the pipeline object.

    host:           The name of the host, string
    port:           The port number, string
    database_name:  The name of the database, string
    user:           The name of the user, string
    password:       The password of the user, string
    '''
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)


    ''' This function gets all the JSON-strings from the database.

    return:         A list of JSON-strings
    '''
    def get_json_all(self) -> list:
        return self.fetch_command(command="SELECT json FROM raw_json", vars=tuple())


    ''' This function splits camelCase words into seperate words.
    s:              The words or the whole sentence, string
    return:         The new string without the camelCase

    Author: Prof Mo
    Source: https://stackoverflow.com/a/42774323
    '''
    def camel_case_to_phrase(self, s: str) -> str:
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


    ''' This function removes from the description of the JSON the HTML-tags (<br>, </br>, 
        <p>, etc.) and replaces the character references (&euml;, &egrave;, etc) with their
        UTF-8 counterpart.
    
    json_string:    The JSON-file, as a string
    return:         The cleaned up description, string
    '''
    def cleanup_json(self, json_string: str) -> str:
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
        
        for i in desc_string:
            # Replace every instance of <p>, </p>, etc with empty string ""
            desc_string = desc_string.replace("<p>", " ")
            desc_string = desc_string.replace("</p>", " ")
            desc_string = desc_string.replace("<em>", " ")
            desc_string = desc_string.replace("</em>", " ")
            desc_string = desc_string.replace("<li>", " ")
            desc_string = desc_string.replace("</li>", " ")
            desc_string = desc_string.replace("<ul>", " ")
            desc_string = desc_string.replace("</ul>", " ")
            desc_string = desc_string.replace("<strong>", " ")
            desc_string = desc_string.replace("</strong>", " ")
            desc_string = desc_string.replace("<br />", " ")

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
        
        desc_string = self.camel_case_to_phrase(desc_string)
        return desc_string

    ''' This function return the descriptions.
    amount:         The amount of descriptions you want, int
    return:         A list of descriptions
    '''
    def get_descriptions(self, amount: int) -> list:
        descriptions = []
        print("Grabbing jsons...", end="")
        jsons = self.get_json_all()
        print("Done!\nCleaning descriptions...", end="")

        for json in jsons[:amount]:
            descriptions.append(self.cleanup_json(json[0]))
        
        print("Done!\nAmount of descriptions: {}".format(len(descriptions)))
        return descriptions