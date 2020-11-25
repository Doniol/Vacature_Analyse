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


def main():
    file = codecs.open("test_vacature.txt", "r", encoding="utf8").read()
    words = RegexpTokenizer(r'\w+').tokenize(file.lower())
    unique_words = list(set(words))
    word_to_num_converter = dict((word, num) for num, word in enumerate(words))

    x_data = [[word_to_num_converter[word] for word in words]]
    y_data = [[word_to_num_converter[word] for word in ["informatietechnologie", "netwerkbeheerder", "ict", "specialist", "it", "infrastructuur", 
                                              "netwerkbeheer", "netwerk", "security", "systeembeheergerelateerde", "databasebeheer", "systeem", "netwerk", 
                                              "applicatie", "beveiligingsprotocollen", "hbo", "ccna", "mcsa", "linux", "lan", "wan", "infrastructuren",
                                              "itil", "ids", "ips", "siem", "2fa", "vmware", "prtg", "centos", "windows", "firewalls", 
                                              "pki", "nederlandse", "nationaliteit", "nederlands", "analytisch", "creatieve", "zelfstandig", "teamverband", 
                                              "organiseren", "verantwoordelijkheidsgevoel", "fulltime", "rijksoverheid", "projectmanagement", "informatietechniek"]]]

    x = numpy.reshape(x_data, (len(x_data), len(x_data[0]), 1))
    x = x/float(len(words))
    print(x.shape)

    y = numpy.empty([1, len(x_data[0]), 1], dtype=int)
    for word_index in range(0, len(x_data[0])):
        if x_data[0][word_index] in y_data[0]:
            y.itemset((0, word_index, 0), 1)
        else:
            y.itemset((0, word_index, 0), 0)
    print(y, y.shape)

    model = Sequential()
    model.add(LSTM(256, input_shape=(None, 1), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(256, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(128))
    model.add(Dropout(0.2))
    model.add(Dense(len(y[0]), activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam')

    filepath = "own_AI_weights.hdf5"
    # Train
    checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    desired_callbacks = [checkpoint]

    model.fit(x, y, epochs=600, batch_size=None, callbacks=desired_callbacks)


main()