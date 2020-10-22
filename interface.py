import plotly.graph_objects as go
import numpy as np
from pipeline_analyse_interface import pipeline_db_to_interface as pipeline


def split_dict(data_dict):
    data_dict_sorted = sorted(data_dict.items(), key=lambda x: x[1]["word_count"], reverse=True)
    print(data_dict_sorted)
    words = []
    amounts = []
    for item in data_dict_sorted:
        words.append(item[1]["word_id"])
        amounts.append(item[1]["word_count"])
    return words, amounts


def link_ids_to_entities(db, table_name, ids, count):
    table = db.get_lookup_table(table_name)
    corresponding_data = []
    for id in ids:
        for entry in table:
            if id == entry[0]:
                corresponding_data.append(entry[1])
                print(id, entry)
                break
    return corresponding_data


def main():
    print("Give the desired institute")
    desired_instute = input()
    print("Give the desired tables: both, table or pie")
    show_table = input()

    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_name = "innodb"
    user = "innouser"
    password = "innouser"
    db = pipeline(host, port, database_name, user, password)
    data = db.get_dict(db.get_entries(institute=desired_instute))

    data_word_ids, data_amounts = split_dict(data)
    print(data_word_ids)
    print(data_amounts)
    data_words = link_ids_to_entities(db, "words_", data_word_ids, data_amounts)

    if not data_words:
        data_word.append("No data")
        data_amounts.append("No data")
    
    # show pie chart and table
    if show_table == "both":
        fig = go.Figure(data=[go.Table(header=dict(values=['Kernwoord', 'Komt voor']),
                    cells=dict(values=[data_words, data_amounts]))
                        ])
        fig.update_layout(title= "Institute of " + str(desired_instute), font=dict(
            family="Comic Sans MS, monospace",
            size=12,
            color="Black"))
        fig.show()
        
        excess_amount = sum(data_amounts[11:])
        pie_words = data_words[:10]
        pie_words.append("Other")
        pie_amounts = data_amounts[:10]
        pie_amounts.append(excess_amount)
        fig = go.Figure(data=[go.Pie(labels= pie_words, values= pie_amounts, textinfo='label+percent',
                                insidetextorientation='radial')])
        fig.update(layout_title_text='Instuut voor ' + str(desired_instute))
        
        fig.show()
    # show table
    elif show_table == "table":
        fig = go.Figure(data=[go.Table(header=dict(values=['Kernwoord', 'Komt voor']),
                    cells=dict(values=[data_words, data_amounts]))
                        ])
        fig.update_layout(title= "Instuut voor " + str(desired_instute), font=dict(
            family="Comic Sans MS, monospace",
            size=12,
            color="Black"))
        fig.show()
    # show pie chart
    elif show_table == "pie":
        excess_amount = sum(data_amounts[11:])
        pie_words = data_words[:10]
        pie_words.append("Other")
        pie_amounts = data_amounts[:10]
        pie_amounts.append(excess_amount)
        fig = go.Figure(data=[go.Pie(labels= pie_words, values= pie_amounts, textinfo='label+percent',
                                insidetextorientation='radial')])
        fig.update(layout_title_text='Instuut voor ' + str(desired_instute))
        
        fig.show()

    else:
        print("Invalid table choice, please choose from: both, table or pie")

    return

if __name__ == "__main__":
    main()