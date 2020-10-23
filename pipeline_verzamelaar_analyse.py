from pipeline_base import database_connection
import json
from html import entities


class pipeline_db_to_analyse(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)

    def get_json_all(self):
        return self.fetch_command(command="SELECT json FROM raw_json")


    '''
    Author: Prof Mo
    Source: https://stackoverflow.com/a/42774323
    '''
    def camel_case_to_phrase(self, s):
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

    def cleanup_json(self, json_string: str):
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

    def get_descriptions(self, amount):
        descriptions = []
        print("Grabbing jsons...", end="")
        jsons = self.get_json_all()
        print("Done!\nCleaning descriptions...", end="")

        for json in jsons[:amount]:
            descriptions.append(self.cleanup_json(json[0]))
        
        print("Done!\nAmount of descriptions: {}".format(len(descriptions)))
        return descriptions