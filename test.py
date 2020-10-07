from pipeline_verzamelaar_analyse import pipeline_db_to_analyse
from pipeline_analyse_interface import pipeline_analyse_to_db, pipeline_db_to_interface


test = pipeline_db_to_analyse(
    host="weert.lucimmerzeel.nl",
    port="5432",
    database_name="pocdb",
    user="pocuser",
    password="pocuser")

test = pipeline_analyse_to_db(
    host="weert.lucimmerzeel.nl",
    port="5432",
    database_name="pocdb",
    user="pocuser",
    password="pocuser")

test = pipeline_db_to_interface(
    host="weert.lucimmerzeel.nl",
    port="5432",
    database_name="pocdb",
    user="pocuser",
    password="pocuser")