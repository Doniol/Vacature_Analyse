from pipeline_base import database_connection
import json


class pipeline_db_to_analyse(database_connection):
    def __init__(self, host: str, port: str, database_name: str, user: str, password: str) -> None:
        database_connection.__init__(self, host, port, database_name, user, password)

    def get_json_all(self):
        return self.fetch_command(command="SELECT json FROM raw_json")

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
        
        # Replace every instance of <p>, </p>, etc with empty string ""
        for i in desc_string:
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