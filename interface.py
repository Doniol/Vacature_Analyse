import plotly.graph_objects as go

import numpy as np
from wordcloud import WordCloud
#import multidict as multidict

import re
import os
from PIL import Image
from os import path
import matplotlib.pyplot as plt

from typing import List, Tuple, Dict, Any

# database connection
from pipelines.pipeline_analyse_interface import pipeline_db_to_interface as pipeline


def split_dict(data_dict: Dict[int, Dict[str, int]]) -> Tuple[List[str], List[int]]:
    ''' This function splits the dictionary into two lists, one filled with all the dictionary's keys, the other with the values
    The dictionary is sorted by value before being split.

    data_dict: A dictionary with every entry in it, the id is the key and the value is a dict, 
     the dict contains the word_id, word_count, date_id and institute_id
    return: A list of words and a list of amounts
    '''
    data_dict_sorted = sorted(data_dict.items(), key=lambda x: x[1]["word_count"], reverse=True)
    words = []
    amounts = []
    for item in data_dict_sorted:
        words.append(item[1]["word_id"])
        amounts.append(item[1]["word_count"])
    return words, amounts


def link_ids_to_entities(db: pipeline, table_name: str, ids: List[int]) -> List[Any]:
    ''' This function uses a lookup table to match id's with their corresponding names and returns these
    
    db: The database you get the information from
    table_name: A string with the name of the table you want to get
    ids: A list of the ids you want to get actual value of
    return: A list of the corresponding data in the same order as the entries
    '''
    table = db.get_lookup_table(table_name)
    corresponding_data = []
    for id in ids:
        for entry in table:
            if id == entry[0]:
                corresponding_data.append(entry[1])
                break
    return corresponding_data

def create_show_table(desired_instute: str, data_words: List[str], data_amounts: List[int]) -> None:
    ''' This function creates the table and shows it

    desired_institute: A string with the desired institute name
    data_words: A list containing words
    data_amounts: A list containing the amount of times a word is used, corresponding to the words in data_words
    '''
    fig = go.Figure(data=[go.Table(header=dict(values=['Kernwoord', 'Komt voor']),
            cells=dict(values=[data_words, data_amounts]))
                ])
    fig.update_layout(title= str(desired_instute), font=dict(
        size=12,
        color="Black"))
    fig.show()    


def create_show_pie(desired_instute: str, data_words: List[str], data_amounts: List[int], slices: int=10) -> None:
    ''' This function creates the pie chart and shows it

    desired_institute: A string with the desired institute name
    data_words: A list containing words
    data_amounts: A list containing the amount of times a word is used, corresponding to the words in data_words
    slices: An integer to determing the amount of words you want to show
    '''
    excess_amount = sum(data_amounts[slices+1:])
    pie_words = data_words[:slices]
    pie_words.append("Other")
    pie_amounts = data_amounts[:slices]
    pie_amounts.append(excess_amount)
    fig = go.Figure(data=[go.Pie(labels= pie_words, values= pie_amounts, textinfo='label+percent',
                            insidetextorientation='radial')])
    fig.update(layout_title_text= str(desired_instute))
    fig.update_layout(title= str(desired_instute), font=dict(
        size=12,
        color="Black"))
    fig.show()


def create_show_cloud(data_dict: Dict[str, int], show_words: int=10) -> None:
    ''' This function creates the wordcloud and shows it

    data_words: A list containing words
    data_amounts: A list containing the amount of times a word is used, corresponding to the words in data_words
    show_words: A integer to determine the amount of words to show in the word cloud
    '''
    wc = WordCloud(background_color='white',
                      width=1500,
                      height=1000,
                      max_words= show_words
                      ).generate_from_frequencies(data_dict)
    plt.figure(figsize=(9,6))
    plt.imshow(wc)
    plt.axis('off')
    plt.show()


def main():
    print("Give the desired institute")
    desired_instute = input()
    print("Give the desired tables: all, table, pie or cloud")
    show_table = input()

    # setup databse connection 
    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_name = "InnoDB-test"
    user = "innouser"
    password = "innouser"
    db = pipeline(host, port, database_name, user, password)
    
    # retrieve data from the database
    data = db.get_dict(db.get_entries(institute=desired_instute))
    data_word_ids, data_amounts = split_dict(data)

    data_words = link_ids_to_entities(db, "words", data_word_ids)
    if not data_words:
        data_words.append("No data")
        data_amounts.append("No data")

    word_cloud_dict = {}
    for index in range(len(data_words)):
        word_cloud_dict[data_words[index]] = data_amounts[index] 
    
    # show pie chart and table
    if show_table == "all":
        create_show_table(desired_instute, data_words, data_amounts)
        create_show_pie(desired_instute, data_words, data_amounts)
        create_show_cloud(word_cloud_dict, 20)
        #create_show_cloud(data_words, data_amounts)
    # show table
    elif show_table == "table":
        create_show_table(desired_instute, data_words, data_amounts)
    # show pie chart
    elif show_table == "pie":
        create_show_pie(desired_instute, data_words, data_amounts)
    # show word cloud
    elif show_table == "cloud":
        create_show_cloud(word_cloud_dict, 20)
        
    else:
        print("Invalid table choice, please choose from: all, table, pie or cloud")

    return

if __name__ == "__main__":
    main()