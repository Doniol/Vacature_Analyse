import plotly.graph_objects as go
import numpy as np
import pipeline_analyse_interface as pipeline

def split_dict(data_dict):
    data_dict_sorted = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
    words = []
    amounts = []
    for item in data_dict_sorted:
        words.append(item[0])
        amounts.append(item[1])
    return words, amounts


def main():
    desired_instute = "*"
    show_table = True

    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_name = "innodb"
    user = "innouser"
    password = "innouser"
    db = pipeline.database_connection(host, port, database_name, user, password)
    db.connect()
    data_dict = db.create_dict(desired_instute)
    data_words, data_amounts = split_dict(data_dict)
    
    if not data_words:
        data_word.append("No data")
        data_amounts.append("No data")


    fig = go.Figure(data=[go.Table(header=dict(values=['Kernwoord', 'Komt voor']),
                cells=dict(values=[data_words, data_amounts]))
                    ])
    fig.update_layout(title= "Instuut voor " + str(desired_instute), font=dict(
        family="Comic Sans MS, monospace",
        size=12,
        color="Black"))
    fig.show()
    
    
    fig = go.Figure(data=[go.Pie(labels=data_words[:10], values=data_amounts[:10], textinfo='label+percent',
                             insidetextorientation='radial')])
    fig.update(layout_title_text='Instuut voor ' + str(desired_instute))
    
    fig.show()

    return

if __name__ == "__main__":
    main()