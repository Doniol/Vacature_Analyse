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
    print(len(x_data), len(x_data[0]), len(x_data[0][0]), x_data[0][0][0])
    # Loop through each set of results
    for result_set_index in range(0, len(results)):
        # Create list representing all words in the current result
        y_data.append([[0] for word in x_data[0][result_set_index]])
        # Loop through each individual result within the current set
        for result_index in range(0, len(results[result_set_index])):
            #TODO: Mark multiple words instead of 1
            # Mark the word(s) that corresponds to the currently selected result
            word_index = x_data[0][result_set_index].index(results[result_set_index][result_index])
            print(len(y_data), len(y_data[result_set_index]), result_set_index, word_index)

    # print(zipped_x_data, type(zipped_x_data))
    # print(len(zipped_x_data), len(zipped_x_data[0]), len(zipped_x_data[0][0]))
    # x = numpy.reshape(zipped_x_data, (len(zipped_x_data), len(zipped_x_data[0]), len(zipped_x_data[0][0])))
    # x = numpy.ndarray(shape=(len(zipped_x_data), len(zipped_x_data[0])))
    x = numpy.array(x_data)
    # print([len(x[i]) for i in range(len(x))])
    # print(len(x), len(x[0]), len(x[0][0]))
    # print(x.shape, type(x))
    
    print(x)
    print(x.shape)

    y = numpy.empty([len(x), len(x[0]), 1], dtype=int)
    for word_index in range(0, len(x_data[0])):
        print(x_data[0][word_index])
        if x_data[0][word_index] in y_data[0]:
            y.itemset((0, word_index, 0), 1)
        else:
            y.itemset((0, word_index, 0), 0)
    print(y)
    print(y.shape)

    model = Sequential()
    model.add(LSTM(256, input_shape=(None, x.shape[2]), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(256, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(128))
    model.add(Dropout(0.2))
    model.add(Dense(len(y[0]), activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam')

    filepath = "own_AI_weights"
    # Train
    checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    desired_callbacks = [checkpoint]

    model.fit(x, y, epochs=500, batch_size=None, callbacks=desired_callbacks)


main()