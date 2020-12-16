import codecs
import spacy
import numpy as np
from keras.backend import clear_session
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Bidirectional
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
from typing import List, Any, Dict, Union, Tuple
from basic_AI import BasicAI, BasicAIPadding, BasicAINoPadding

nlp = spacy.load('nl_core_news_md')


def get_word_data(file):
    tokens = nlp(file.lower())
    words = []
    POSs = []
    tags = []
    deps = []
    for token in tokens:
        if token.is_punct or token.is_bracket or token.is_currency or token.shape_ == "X" or token.shape_ == "x" or token.is_space:
            continue
        else:
            words.append(token.text)
            POSs.append(token.pos_)
            tags.append(token.tag_)
            deps.append(token.dep_)
    return words, POSs, tags, deps


def create_data(words, POSs, tags, deps, word_converter, POS_converter, tag_converter, dep_converter):
    zipped_datasets = []
    for dataset_index in range(0, len(words)):
        zipped_datasets.append(list(zip([word_converter[word]/len(words[dataset_index]) for word in words[dataset_index]], 
                                        [POS_converter[POS]/len(POSs[dataset_index]) for POS in POSs[dataset_index]],
                                        [tag_converter[tag]/len(tags[dataset_index]) for tag in tags[dataset_index]],
                                        [dep_converter[dep]/len(deps[dataset_index]) for dep in deps[dataset_index]])))
    return zipped_datasets


def add_uniques(existing_list, entry_list):
    #TODO: Useless? Check whether it is or not
    uniques = set(existing_list)
    for entry in entry_list:
        uniques.add(entry)
    return list(uniques)


def load_datasets(dataset_names):
    input_sets = []
    answer_sets = []
    unique_words = []
    unique_POSs = []
    unique_tags = []
    unique_deps = []
    for name in dataset_names:
        text = codecs.open("dataset\\{0}.txt".format(name), "r", encoding="utf8").read()
        ans = codecs.open("dataset\\{0}_keywords.txt".format(name), "r", encoding="utf8").read()
        processed_text = get_word_data(text)
        input_sets.append(processed_text)
        answer_sets.append(get_word_data(ans)[0])
        unique_words = add_uniques(unique_words, processed_text[0])
        unique_POSs = add_uniques(unique_POSs, processed_text[1])
        unique_tags = add_uniques(unique_tags, processed_text[2])
        unique_deps = add_uniques(unique_deps, processed_text[3])
    return list(zip(*input_sets)), answer_sets, [unique_words, unique_POSs, unique_tags, unique_deps]


class AI_LSTM_Padding(BasicAIPadding):
    ''' AI using LSTM, using padding to equalize all inputs/outputs and using 1/0 for every word to denote relevancy.
    '''
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filler: int) -> None:
        # Create model
        model = Sequential()
        model.add(LSTM(256, input_shape=(None, 4), return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(256, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(128))
        model.add(Dropout(0.2))
        model.add(Dense(filler))

        BasicAIPadding.__init__(self, datasets, filler, [1, 0, 1], model)


class AI_LSTM_NoPadding(BasicAINoPadding):
    ''' AI using Seq2Seq
    '''
    #TODO: Doesnt work; cant load weights from model with different amount of outputs
    #TODO: Other options include:
        # - Output instead of using 1/0 to denote relevancy, only display the relevant words via copying them from input
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]]) -> None:
        ''' Init the class

        datasets: A tuple containing the dataset inputs, dataset outputs and all unique entries in the dataset
        depth: Defines amount of LSTMs in the de- and encoders; 3 means 3 in both, while (3, 1) means 3 in the encoder
         and 1 in the decoder
        '''
        # Create temporary model
        model = Sequential()
        model.add(LSTM(256, input_shape=(None, 4), return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(256, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(128))
        model.add(Dropout(0.2))
        model.add(Dense(1))

        BasicAINoPadding.__init__(self, datasets, model)

    def update_model(self, output_length):
        clear_session()
        self.model = Sequential()
        self.model.add(LSTM(256, input_shape=(None, 4), return_sequences=True))
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(256, return_sequences=True))
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(128))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(output_length))


class AI_LSTM_Padding_bidirectional(BasicAIPadding):
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filler: int) -> None:
        # Create model
        model = Sequential()
        model.add(Bidirectional(LSTM(256, input_shape=(None, 4), return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(256, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(128)))
        model.add(Dropout(0.2))
        model.add(Dense(filler))

        BasicAIPadding.__init__(self, datasets, filler, [1, 0, 1], model)


def train_LSTM():
    #TODO: Fix preprocessing, is unnecessarily complicated i think
    #TODO: Preprocessing needs to filter out non-words

    # Connect to database and get data
    datasets = load_datasets(["vac_1", "vac_2", "vac_3"]) # Temporary measure
    
    # Create AI class
    AI_1 = AI_LSTM_Padding(datasets, 1000)
    AI_2 = AI_LSTM_NoPadding(datasets) # Doesnt work because weights
    AI_3 = AI_LSTM_Padding_bidirectional(datasets, 1000)

    # Train AI
    AI_1.train_AI(200, "AI/obj/LSTM_AI_weights.hdf5")
    AI_3.train_AI(200, "AI/obj/LSTM_AI_stateful_weights.hdf5")

    # Run the AI with selected input
    x = np.asarray([AI_1.get_x_data()[0]])
    AI_1.run_AI(x, "AI/obj/LSTM_AI_weights.hdf5", 10)
    x = np.asarray([AI_3.get_x_data()[0]])
    AI_3.run_AI(x, "AI/obj/LSTM_AI_stateful_weights.hdf5", 10)


# train_LSTM()