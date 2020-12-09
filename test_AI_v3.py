import numpy
import sys
import codecs
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
import tensorflow as tf
import spacy
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
        y_data.append([[1] if word in results[result_set_index] else [0] for word in x_data[0][result_set_index]])
    # print(len(y_data), len(y_data[0]), len(y_data[0][0]), y_data)

    # print(zipped_x_data, type(zipped_x_data))
    # print(len(zipped_x_data), len(zipped_x_data[0]), len(zipped_x_data[0][0]))
    # x = numpy.reshape(zipped_x_data, (len(zipped_x_data), len(zipped_x_data[0]), len(zipped_x_data[0][0])))
    # x = numpy.ndarray(shape=(len(zipped_x_data), len(zipped_x_data[0])))
    # x = numpy.array(processed_x_data)
    # x = numpy.asarray([numpy.array(data_point) for data_point in processed_x_data])
    # x = numpy.asarray(processed_x_data).astype(numpy.float32)
    # y = numpy.array(y_data)
    # y = numpy.asarray([numpy.array(data_point) for data_point in y_data])
    # y = numpy.asarray(y_data).astype(numpy.float32)
    # print(x.shape, type(x))

    model = Sequential()
    model.add(LSTM(256, input_shape=(None, 4), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(256, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(128, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(Dense(None, activation='softmax')) # Softmax hoort hier niet, None werkt niet; daar moet een variabele komen die veranderd afhankelijk van output size

    model.compile(loss='categorical_crossentropy', optimizer='adam')

    filepath = "own_AI_v2_weights.hdf5"
    # Train
    checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    desired_callbacks = [checkpoint]

    # print("model: ")
    # model.summary()
    # print("x:")
    # print([len(x[i]) for i in range(len(x))])
    # print(len(x), len(x[0]), len(x[0][0]))
    # print(x.shape)
    # print("y:")
    # print([len(y[i]) for i in range(len(y))])
    # print(len(y), len(y[0]), len(y[0][0]))
    # print(y.shape)

    x = numpy.array([processed_x_data[0]])
    # x = numpy.array([numpy.asarray(entry) for entry in processed_x_data])
    y = numpy.array([y_data[0]])
    # y = numpy.array([numpy.asarray(entry) for entry in y_data])
    
    # print(x)
    # print(y)
    print(x.shape, y.shape)
    print(type(x), type(y))
    print(type(x[0]), type(y[0]))

    model.fit(x, y, epochs=1, batch_size=1, callbacks=desired_callbacks)


main()