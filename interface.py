import plotly.graph_objects as go
import numpy as np
import pipeline_analyse_interface as pipeline

def split_dict(data_dict):
    words = []
    amounts = []
    for key in data_dict:
        # print(key)
        words.append(key)
        amounts.append(data_dict[key])
    return words, amounts


def main():
    desired_instute = "*"

    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_name = "innodb"
    user = "innouser"
    password = "innouser"
    db = pipeline.database_connection(host, port, database_name, user, password)
    db.connect()
    data_dict = db.create_dict(desired_instute)
    print(data_dict)
    data_words, data_amounts = split_dict(data_dict)
    # data_dict = {
    #         "Pindakaas": [0, 5],
    #         "Sociaal": [0, 25],
    #         "Aardappel": [2, 1],
    #         "penguin": [1, 90],
    #         "Python": [2, 67],
    #         "Random": [0, 4],
    #         "Snackbar": [0, 99],
    #         "Hallo": [2, 3]
    #         }
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

    return

if __name__ == "__main__":
    main()