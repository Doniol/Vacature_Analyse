import plotly.graph_objects as go

import numpy as np
from wordcloud import WordCloud
import multidict as multidict

import re
import os
from PIL import Image
from os import path
import matplotlib.pyplot as plt

from typing import List

# database connection
from pipeline_analyse_interface import pipeline_db_to_interface as pipeline


def split_dict(data_dict):
    ''' This function splits the dictionary into two strings and sorts the keys according to the amount

    data_dict: a dictionary with words and the amount of times it's used
    return: a list of words and a list of amounts
    '''
    data_dict_sorted = sorted(data_dict.items(), key=lambda x: x[1]["word_count"], reverse=True)
    words = []
    amounts = []
    for item in data_dict_sorted:
        words.append(item[1]["word_id"])
        amounts.append(item[1]["word_count"])
    return words, amounts


def link_ids_to_entities(db, table_name, ids, count):
    ''' This function generates a lookup table to match id's with their corresponding name
    
    return: a list of the corresponding data in the same order as the entries
    '''
    table = db.get_lookup_table(table_name)
    corresponding_data = []
    for id in ids:
        for entry in table:
            if id == entry[0]:
                corresponding_data.append(entry[1])
                break
    return corresponding_data

def dict_to_string(data_words: List[str], data_amounts: List[int]):
    ''' This function makes the dictionary into a string where each word is placed the amount of time its used

    data_words: a list of strings with the words
    data_amounts: a list containing the amount of usages
    return: The string with every word put in as its frequency
    '''
    converted_to_string = ""
    for index in range(len(data_words)):
        converted_to_string += str(data_words[index] + " ") * data_amounts[index]
    return converted_to_string


def create_show_table(desired_instute: str, data_words: List[str], data_amounts: List[int]):
    ''' This function creates the table and shows it

    desired_institute: a string with the institu name
    data_words: a list of strings with the words
    data_amounts: a list containing the amount of usages
    '''
    fig = go.Figure(data=[go.Table(header=dict(values=['Kernwoord', 'Komt voor']),
            cells=dict(values=[data_words, data_amounts]))
                ])
    fig.update_layout(title= str(desired_instute), font=dict(
        family="Comic Sans MS, monospace",
        size=12,
        color="Black"))
    fig.show()    


def create_show_pie(desired_instute: str, data_words: List[str], data_amounts: List[int], slices: int =10):
    ''' This function creates the pie chart and shows it

    desired_institute: a string with the institu name
    data_words: a list of strings with the words
    data_amounts: a list containing the amount of usages
    slices: an integer to determing the amount of words you want to show
    '''
    excess_amount = sum(data_amounts[slices+1:])
    pie_words = data_words[:slices]
    pie_words.append("Other")
    pie_amounts = data_amounts[:slices]
    pie_amounts.append(excess_amount)
    fig = go.Figure(data=[go.Pie(labels= pie_words, values= pie_amounts, textinfo='label+percent',
                            insidetextorientation='radial')])
    fig.update(layout_title_text= str(desired_instute))
    fig.show()    


def create_show_cloud(data_words: List[str], data_amounts: List[int], show_words: int= 20):
    ''' This function creates the wordcloud and shows it

    data_words: a list of strings with the words
    data_amounts: a list containing the amount of usages
    show_words: integer to determine the amount of words to show in the word cloud
    '''
    wc = WordCloud(collocations=False, background_color="white", max_words= show_words)
    wc.generate(dict_to_string(data_words, data_amounts))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def main():
    print("Give the desired institute")
    desired_instute = input()
    print("Give the desired tables: all, table, pie or cloud")
    show_table = input()

    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_name = "innodb"
    user = "innouser"
    password = "innouser"
    db = pipeline(host, port, database_name, user, password)
    data = db.get_dict(db.get_entries(institute=desired_instute))

    data_word_ids, data_amounts = split_dict(data)

    data_words = link_ids_to_entities(db, "words_", data_word_ids, data_amounts)

    if not data_words:
        data_word.append("No data")
        data_amounts.append("No data")
    
    # show pie chart and table
    if show_table == "all":
        create_show_table(desired_instute, data_words, data_amounts)
        create_show_pie(desired_instute, data_words, data_amounts)
        create_show_cloud(data_words, data_amounts)
    # show table
    elif show_table == "table":
        create_show_table(desired_instute, data_words, data_amounts)
    # show pie chart
    elif show_table == "pie":
        create_show_pie(desired_instute, data_words, data_amounts)
    # show word cloud
    elif show_table == "cloud":
        create_show_cloud(data_words, data_amounts)
    else:
        print("Invalid table choice, please choose from: all, table, pie or cloud")

    return

if __name__ == "__main__":
    main()