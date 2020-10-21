import plotly.graph_objects as go
import numpy as np
from pipeline_analyse_interface import pipeline_db_to_interface as pipeline


def main():
    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_name = "innodb"
    user = "innouser"
    password = "innouser"
    db = pipeline(host, port, database_name, user, password)
    data = db.fetch_command("SELECT * FROM institute_ict")
    for thing in data:
        print(thing[0].strip(), thing[1])


if __name__ == "__main__":
    main()