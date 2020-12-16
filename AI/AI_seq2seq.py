import codecs
import spacy
import numpy as np
import seq2seq.seq2seq
from seq2seq.seq2seq.models import SimpleSeq2Seq
from keras.backend import clear_session
from typing import List, Any, Dict, Union, Tuple
import pickle
import os.path
from os import path
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


class AI_Seq2SeqPadding(BasicAIPadding):
    ''' AI using Seq2Seq, using padding to equalize all inputs/outputs and using 1/0 for every word to denote relevancy.
    '''
    #TODO: Other options include:
        # - Pad using either 0, -1 or other number
        # - Output instead of using 1/0 to denote relevancy, only display the relevant words via copying them from input
    #TODO: Padding creates this fucky bug where the best results are the ones gained from padding, ergo the 0's, which returns a list of the same useless word at word_to_num_converter[0]
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filler: int, 
                 depth: Union[int, List[int]]) -> None:
        # Create model
        model = SimpleSeq2Seq(input_dim=4, output_length=filler, output_dim=1, depth=depth)
        BasicAIPadding.__init__(self, datasets, filler, model)


class AI_Seq2SeqNoPadding(BasicAINoPadding):
    ''' AI using Seq2Seq
    '''
    #TODO: Other options include:
        # - Output instead of using 1/0 to denote relevancy, only display the relevant words via copying them from input
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], depth: Union[int, List[int]]) -> None:
        ''' Init the class

        datasets: A tuple containing the dataset inputs, dataset outputs and all unique entries in the dataset
        depth: Defines amount of LSTMs in the de- and encoders; 3 means 3 in both, while (3, 1) means 3 in the encoder
         and 1 in the decoder
        '''
        self.depth = depth
        # Create temporary model
        model = SimpleSeq2Seq(input_dim=4, output_length=1, output_dim=1, depth=self.depth)
        BasicAINoPadding.__init__(self, datasets, model)

    def update_model(self, output_length):
        clear_session()
        self.model = SimpleSeq2Seq(input_dim=4, output_length=output_length, output_dim=1, depth=self.depth)


def train_seq2seq():
    #TODO: Fix preprocessing, is unnecessarily complicated i think
    #TODO: Preprocessing needs to filter out non-words
    #TODO: Is seq2seq a good idea?
    #TODO: Moeten de dictionaries voor woorden niet globaal zijn ofz? Aangezien de AI wordt getrained op de getallen die hieruit komen, en deze getallen kunnen veranderen per vacature.
    #TODO: Gekut met dictionary die van grootte veranderd
    # This Seq2Seq requires an older version of Python: v3.7.8; because with this version of python, older versions of keras and tensorflow can be installed; v2.2.4 and v1.13.1 respectively. 
    #  And those version are necessary for running Seq2Seq
    
    # Connect to database and get data
    datasets = load_datasets(["vac_1", "vac_2", "vac_3"]) # Temporary measure
    
    # Create AI class
    AI_1 = AI_Seq2SeqPadding(datasets, 1000, 4)
    AI_2 = AI_Seq2SeqNoPadding(datasets, 4)

    # Train AI
    # AI_1.train_AI(1, "AI/obj/seq2seq_weights.hdf5", "AI/obj/seq2seq_weights.hdf5")
    # AI_2.train_AI(1, "AI/obj/seq2seq_nopad_weights.hdf5", "AI/obj/seq2seq_nopad_weights.hdf5")

    # Run the AI with selected input
    print("1")
    x = np.asarray([AI_1.get_x_data()[0]])
    AI_1.run_AI(x, "AI/obj/seq2seq_weights.hdf5", 10)
    print("2")
    x = np.asarray([AI_2.get_x_data()[0]])
    AI_2.run_AI(x, "AI/obj/seq2seq_nopad_weights.hdf5", 10)


# train_seq2seq()