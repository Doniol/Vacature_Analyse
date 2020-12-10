import numpy
import sys
import codecs
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
import tensorflow as tf
import spacy
import seq2seq.seq2seq
from seq2seq.seq2seq.models import SimpleSeq2Seq
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


def main():
    # Get data from all given datasets
    x_data, results, uniques = load_datasets(["vac_1", "vac_2", "vac_3"])

    # Create dicts to convert words to numbers
    word_to_num_converter = dict((word, num) for num, word in enumerate(uniques[0]))
    POS_to_num_converter = dict((POS, num) for num, POS in enumerate(uniques[1]))
    tag_to_num_converter = dict((tag, num) for num, tag in enumerate(uniques[2]))
    dep_to_num_converter = dict((dep, num) for num, dep in enumerate(uniques[3]))

    # Process and reformat the data to make it ready for use
    processed_x_data = create_data(*x_data, word_to_num_converter, POS_to_num_converter, tag_to_num_converter, dep_to_num_converter)

    ### Temporary solution for finding out what tags for actual keywords are
    y_data = []
    # print(len(x_data), len(x_data[0]), len(x_data[0][0]), x_data)
    # print(processed_x_data, len(processed_x_data), len(processed_x_data[0]))
    # Loop through each set of results
    for result_set_index in range(0, len(results)):
        # Create list representing all words in the current result, 1 for relevant keywords, and 0 for irrelevant ones
        y_data.append([[1] if word in results[result_set_index] else [0] for word in x_data[0][result_set_index]] + [[0] for i in range(0, 1000 - len(x_data[0][result_set_index]))])
    # print(len(y_data), len(y_data[0]), len(y_data[0][0]), y_data)

    #TODO: Option: Instead of padding with 0's create new model for every dataset; load weights; and change output size according to dataset
    filepath = "own_AI_v3_weights.hdf5"
    load_weights = True
    x = numpy.array([data + [[0, 0, 0, 0] for i in range(0, 1000 - len(data))] for data in processed_x_data])
    y = numpy.array(y_data)
    
    model = SimpleSeq2Seq(input_dim=4, hidden_dim=10, output_length=1000, output_dim=1, depth=4)
    if load_weights:
        model.load_weights(filepath)
    model.compile(loss='mse', optimizer='rmsprop')
    model.fit(x, y, epochs=10, batch_size=1)
    model.save_weights(filepath)


    # for dataset_index in range(0, len(y_data)):
    #     x = numpy.array([processed_x_data[dataset_index]])
    #     y = numpy.array([y_data[dataset_index]])

    #     model = SimpleSeq2Seq(input_dim=4, hidden_dim=10, output_length=y.shape[1], output_dim=1, depth=4)
    #     if dataset_index >= 1:
    #         model.load_weights(filepath)
    #     model.compile(loss='mse', optimizer='rmsprop')

    #     # Train
    #     model.fit(x, y, epochs=10, batch_size=None)
    #     model.save_weights(filepath)


    # filepath = "own_AI_v2_weights.hdf5"

    # for dataset_index in range(0, len(y_data)):
    #     x = numpy.array([processed_x_data[dataset_index]])
    #     y = numpy.array([y_data[dataset_index]])
    #     print(x.shape, y.shape)

    #     model = Sequential()
    #     model.add(LSTM(256, input_shape=(None, 4), return_sequences=True))
    #     model.add(Dropout(0.2))
    #     model.add(LSTM(256, return_sequences=True))
    #     model.add(Dropout(0.2))
    #     model.add(LSTM(128, return_sequences=True))
    #     model.add(Dropout(0.2))
    #     model.add(Dense(1, activation='softmax')) # Softmax hoort hier niet

    #     if dataset_index >= 1:
    #         model.load_weights(filepath)

    #     model.compile(loss='categorical_crossentropy', optimizer='adam')

    #     # Train
    #     checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    #     desired_callbacks = [checkpoint]
    #     model.fit(x, y, epochs=10, batch_size=None, callbacks=desired_callbacks)

    
    # # print(x)
    # # print(y)
    # print(x.shape, y.shape)
    # print(type(x), type(y))
    # print(type(x[0]), type(y[0]))


main()