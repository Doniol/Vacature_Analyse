import codecs
import spacy
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
from typing import List, Any, Dict, Union, Tuple
from basic_AI import BasicAI

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


class AILSTMPadding(BasicAI):
    ''' AI using LSTM, using padding to equalize all inputs/outputs and using 1/0 for every word to denote relevancy.
    '''
    #TODO: Other options include:
        # - Pad using either 0, -1 or other number
        # - Creating new model every time a different input/output size is required
        # - Output instead of using 1/0 to denote relevancy, only display the relevant words via copying them from input
    #TODO: Padding creates this fucky bug where the best results are the ones gained from padding, ergo the 0's, which returns a list of the same useless word at word_to_num_converter[0]
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filler: int, 
                 depth: Union[int, List[int]]) -> None:
        ''' Init the class

        datasets: A tuple containing the dataset inputs, dataset outputs and all unique entries in the dataset
        filler: How long the in- and outputs have to be, determines how much has to be padded
        depth: Defines amount of LSTMs in the de- and encoders; 3 means 3 in both, while (3, 1) means 3 in the encoder
         and 1 in the decoder
        '''
        # Read in datasets
        x_data, results, uniques = datasets
        
        # Create dicts to convert words to numbers
        word_to_num_converter = dict((word, num) for num, word in enumerate(uniques[0]))
        POS_to_num_converter = dict((POS, num) for num, POS in enumerate(uniques[1]))
        tag_to_num_converter = dict((tag, num) for num, tag in enumerate(uniques[2]))
        dep_to_num_converter = dict((dep, num) for num, dep in enumerate(uniques[3]))
        # And one to convert numbers back to words
        num_to_word_converter = dict((num, word) for num, word in enumerate(uniques[0]))

        # Get a useable form of input data
        processed_x_data = self.create_input_data(*x_data, word_to_num_converter, POS_to_num_converter, tag_to_num_converter, dep_to_num_converter)
        
        # Get a useable form of output data
        y_data = []
        for result_set_index in range(0, len(results)):
            # For each dataset, create list representing all words in the current result, 1 for relevant keywords, and 
            # 0 for irrelevant ones
            # Afterwards pad the output data so it's always the same size
            y_data.append([1 if word in results[result_set_index] else 0 for word in x_data[0][result_set_index]] + [1 for i in range(0, filler - len(x_data[0][result_set_index]))])
    
        # Pad each set of inputs so they're always the same size
        x = np.array([data + [[0, 0, 0, 0] for i in range(0, filler - len(data))] for data in processed_x_data])
        y = np.array(y_data)

        # Create model
        model = Sequential()
        model.add(LSTM(256, input_shape=(None, 4), return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(256, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(128))
        model.add(Dropout(0.2))
        model.add(Dense(filler))

        BasicAI.__init__(self, num_to_word_converter, x, y, model)    


def train_seq2seq_padding_AI():
    #TODO: Fix preprocessing, is unnecessarily complicated i think
    #TODO: Preprocessing needs to filter out non-words
    #TODO: Is seq2seq a good idea?
    # This Seq2Seq requires an older version of Python: v3.7.8; because with this version of python, older versions of keras and tensorflow can be installed; v2.2.4 and v1.13.1 respectively
    
    # Connect to database and get data
    datasets = load_datasets(["vac_1", "vac_2", "vac_3"]) # Temporary measure
    
    # Create AI class
    AI = AILSTMPadding(datasets, 1000, 4)

    # Train AI
    AI.train_AI(1, "AI/obj/LSTM_AI_weights.hdf5")

    # Run the AI with selected input
    x = np.asarray([AI.get_x_data()[0]])
    AI.run_AI(x, "AI/obj/LSTM_AI_weights.hdf5", 10)


train_seq2seq_padding_AI()
