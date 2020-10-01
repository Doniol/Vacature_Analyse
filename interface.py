import plotly.graph_objects as go
import numpy as np

def get_institute_data(institute, data: dict):

    data_words =[]
    data_amounts =[]
    for key in data:
        if data[key][0] == institute:
            data_words.append(key)
            data_amounts.append(data[key][1])

    return data_words, data_amounts


def main():
    desired_instute = 2

    data_dict = {
            "Pindakaas": [0, 5],
            "Sociaal": [0, 25],
            "Aardappel": [2, 1],
            "penguin": [1, 90],
            "Python": [2, 67],
            "Random": [0, 4],
            "Snackbar": [0, 99],
            "Hallo": [2, 3]
            }
    data_words, data_amounts = get_institute_data(desired_instute, data_dict)
    if not data_words:
        data_words.append("Geen data")
        data_amounts.append("Geen data")

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