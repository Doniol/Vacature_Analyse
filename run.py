from pipeline_analyse_interface import pipeline_analyse_to_db, pipeline_db_to_interface
from pipeline_verzamelaar_analyse import pipeline_db_to_analyse
import interface
from test_rake import get_rake_results
from test_TF_IDF import TF_IDF_get_results
from test_textrank import get_textrank_results
from test_rake_textrank_combo import get_combo_results
from typing import Dict, Union, Callable



def algorithm_selector(name: str) -> Union[Callable, str]:
    switch = {
        "rake": get_rake_results,
        "tf-idf": TF_IDF_get_results,
        "text-rank": get_textrank_results,
        "text-rank-rake-combo": get_combo_results
    }

    return switch.get(name, "invalid input")



def run():
    #connect to the database containing the job offers
    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_jobs = "pocdb"
    user_jobs = "pocuser"
    password_jobs = "pocuser"
    db_jobs = pipeline_db_to_analyse(host, port, database_jobs, user_jobs, password_jobs)

    #connect to the database where the analyzed keywords are stored
    database_analyzed = "InnoDB-test"
    user_analyzed = "innouser"
    password_analyzed = "innouser"
    db_analyzed_to = pipeline_analyse_to_db(host, port, database_analyzed, user_analyzed, password_analyzed)
    db_analyzed_from = pipeline_db_to_interface(host, port, database_analyzed, user_analyzed, password_analyzed)

    print("Which algorithm do you want to use?")
    desired_algo = input()

    print("Give the desired institute")
    desired_instute = input()

    print("Do you want to clear the keywords for this institute before uploading the new keywords? True/False")
    clear_data_base =  input()

    input_descriptions = db_jobs.get_descriptions(100)
    print("analysing")
    
    algorithm = algorithm_selector(desired_algo)
    if algorithm == "invalid input":
        quit()
    else:
        keywords = algorithm(input_descriptions) 

    if clear_data_base:
        db_analyzed_to.clear_entries_institute(desired_instute)
    print("Uploading...")
    db_analyzed_to.add_dict(keywords, desired_instute)

    # start interface
    print("starting interface")
    
    # get the desired interface parameters
    print("Give the desired tables for the interface: all, table, pie or cloud")
    show_table = input()
    
    data = db_analyzed_from.get_dict(db_analyzed_from.get_entries(institute=desired_instute))
    data_word_ids, data_amounts = interface.split_dict(data)
    data_words = interface.link_ids_to_entities(db_analyzed_from, "words", data_word_ids)
    if not data_words:
        data_words.append("No data")
        data_amounts.append("No data")
    
    # show pie chart, table and word cloud
    if show_table == "all":
        interface.create_show_table(desired_instute, data_words, data_amounts)
        interface.create_show_pie(desired_instute, data_words, data_amounts)
        interface.create_show_cloud(data_words, data_amounts)
    # show table
    elif show_table == "table":
        interface.create_show_table(desired_instute, data_words, data_amounts)
    # show pie chart
    elif show_table == "pie":
        interface.create_show_pie(desired_instute, data_words, data_amounts)
    # show word cloud
    elif show_table == "cloud":
        interface.create_show_cloud(data_words, data_amounts)
    else:
        print("Invalid table choice, please choose from: all, table, pie or cloud")
    return


if __name__ == "__main__":
    run()
