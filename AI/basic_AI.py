import codecs
import spacy
import numpy as np
import seq2seq.seq2seq
from seq2seq.seq2seq.models import SimpleSeq2Seq
from typing import List, Any, Dict, Union, Tuple
import pickle
import os.path
from os import path

nlp = spacy.load('nl_core_news_md')


class BasicAI():
    def __init__(self, num_to_word_converter, x, y, model) -> None:
        self.num_to_word_converter = num_to_word_converter
        self.x = x
        self.model = model
        self.y = y

    def get_dict(self, file_name, new_entries, reverse=True):
        # Save list of not only current words, but also previous ones, to list
        # Also creates a dict based on all of those words
        if path.exists("AI/obj/" + file_name + ".pkl"):
            read_file = open("AI/obj/" + file_name + ".pkl", "rb")
            entries = list(set(pickle.load(read_file) + new_entries))
        else:
            entries = new_entries
        
        write_file = open("AI/obj/" + file_name + ".pkl", "wb")
        pickle.dump(entries, write_file, pickle.HIGHEST_PROTOCOL)

        if reverse:
            return dict((key, value) for value, key in enumerate(entries))
        else:
            return dict((value, key) for value, key in enumerate(entries))

    def create_input_data(self, words: List[List[str]], POSs: List[List[str]], tags: List[List[str]], deps: List[List[str]], 
                          word_converter: Dict[str, int], POS_converter: Dict[str, int], tag_converter: Dict[str, int], 
                          dep_converter: Dict[str, int]) -> List[List[Tuple[float, float, float, float]]]:
        ''' Create and return a useable input dataset
             Is a part of the preprocessing of data, may be unnecessary later on depending on wtf Rick & Marty do
            
        For each dataset, creates a list of tuples. Each tuple contains 4 floats, one for each of the datapoints: the word
         itself, the POS, the tag and the dep. Each of those datapoints is converted into a integer using the given converters,
         and then divided by the amount of unique entries of that datapoint. That way you get a number between 0 and 1.
        
        words: A list filled with lists, each of those lists is filled with all of the words in the corresponding dataset
        POSs: The same as words, but for each word this list contains the corresponding Part Of Speach-tag
        tags: The same as words, but for each word this list contains the corresponding detailed Part Of Speach-tag
        deps: The same as words, but for each word this list contains the corresponding syntactic dependency
        word_converter: A converter for converting each word to a integer
        POS_converter: A converter for converting each POS to a integer
        tag_converter: A converter for converting each tag to a integer
        dep_converter: A converter for converting each dep to a integer
        return: A list with a list for each dataset, each of those lists is in turn filled with tuples containing each word
         contained within the dataset and it's corresponding POS, tag and dep
        '''
        #TODO: Dictionary constantly changes size, so when dividing existing numbers bij dict size, the numbers for the same word change. Find a fix for this
        zipped_datasets = []
        for dataset_index in range(0, len(words)):
            # For each dataset append a tuple of a word and it's corresponding datapoints
            zipped_datasets.append(list(zip([word_converter[word]/len(word_converter) for word in words[dataset_index]], 
                                            [POS_converter[POS]/len(POS_converter) for POS in POSs[dataset_index]],
                                            [tag_converter[tag]/len(tag_converter) for tag in tags[dataset_index]],
                                            [dep_converter[dep]/len(dep_converter) for dep in deps[dataset_index]])))
        return zipped_datasets

    def train_AI(self, epochs: int, weights_output: str, weights_input: str=None, x=[], y=[]) -> None:
        ''' Function that trains the AI

        epochs: The amount of training cycles to be gone through
        weights_input: The name of the file in which existing weights have been stored
        weights_output: The name of the file where the calculated weights are to be stored
        '''
        # Check if a set of existing weights has been given
        if weights_input:
            if path.exists(weights_input):
                self.model.load_weights(weights_input)
        # Train the model and save the resulting weights
        self.model.compile(loss='mse', optimizer='rmsprop')
        if len(x) > 0 and len(y) > 0:
            self.model.fit(x, y, epochs=epochs, batch_size=1)
        else:
            self.model.fit(self.x, self.y, epochs=epochs, batch_size=1)
        self.model.save_weights(weights_output)
    
    def run_AI(self, input_data, weights_file: str, desired_word_count: int):
        #TODO: Check if list of multiple lists of input data is possible
        #TODO: Results arent finished yet; need to return the words at the indexes that the current result returns
        ''' Function that runs the AI using the given data/parameters

        input_data: A list containing a list containing the input data for 1 run
            sidenote: In this case each input datapoint consists of a list of floats so the input type is
             np.ndarray(np.ndarray(np.ndarray(np.float64)))
        weights_file: A string containing the name of the file in which the models' weights are stored
        desired_word_count: The amount of desired relevant keywords to be returned
        return: A array filled with the indexes of the found relevant keywords
        '''
        # Get results
        self.model.load_weights(weights_file)
        self.model.compile(loss='mse', optimizer='rmsprop')
        prediction = self.model.predict(input_data)[0].flatten()
        # Get desired_word_count amount of best results
        results = np.argpartition(prediction, -desired_word_count)[-desired_word_count:]
        # print(prediction)
        # print(self.num_to_word_converter, len(self.num_to_word_converter))
        # print(results)
        # print([input_data[0][index][0] for index in results])
        # print([input_data[0][index][0] * len(self.num_to_word_converter) for index in results])
        # print([int(round(input_data[0][index][0] * len(self.num_to_word_converter))) for index in results])
        answers = [self.num_to_word_converter[int(round(input_data[0][index][0] * len(self.num_to_word_converter)))] for index in results]
        print(answers)
        return answers
    
    def get_x_data(self):
        ''' Returns the created input_data
        Temporary function
        '''
        return self.x


class BasicAIPadding(BasicAI):
    #TODO: What do when dataset is longer than filler?
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filler: int, model) -> None:
        # Read in datasets
        x_data, results, uniques = datasets
        
        # Create dicts to convert words to numbers
        word_to_num_converter = self.get_dict("word_to_num_converter", uniques[0])
        POS_to_num_converter = self.get_dict("POS_to_num_converter", uniques[1])
        tag_to_num_converter = self.get_dict("tag_to_num_converter", uniques[2])
        dep_to_num_converter = self.get_dict("dep_to_num_converter", uniques[3])
        # And one to convert numbers back to words
        num_to_word_converter = self.get_dict("num_to_word_converter", uniques[0], reverse=False)

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

        BasicAI.__init__(self, num_to_word_converter, x, y, model)


class BasicAINoPadding(BasicAI):
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], model) -> None:
        # Read in datasets
        x_data, results, uniques = datasets
        
        # Create dicts to convert words to numbers
        word_to_num_converter = self.get_dict("word_to_num_converter", uniques[0])
        POS_to_num_converter = self.get_dict("POS_to_num_converter", uniques[1])
        tag_to_num_converter = self.get_dict("tag_to_num_converter", uniques[2])
        dep_to_num_converter = self.get_dict("dep_to_num_converter", uniques[3])
        # And one to convert numbers back to words
        num_to_word_converter = self.get_dict("num_to_word_converter", uniques[0], reverse=False)
        # Get a useable form of input data
        processed_x_data = self.create_input_data(*x_data, word_to_num_converter, POS_to_num_converter, tag_to_num_converter, dep_to_num_converter)
        
        # Get a useable form of output data
        y_data = []
        for result_set_index in range(0, len(results)):
            # For each dataset, create list representing all words in the current result, 1 for relevant keywords, and 
            # 0 for irrelevant ones
            y_data.append([1 if word in results[result_set_index] else 0 for word in x_data[0][result_set_index]])
    
        # Pad each set of inputs so they're always the same size
        x = np.array(processed_x_data)
        y = np.array(y_data)

        BasicAI.__init__(self, num_to_word_converter, x, y, model)

    def update_model(self, output_length):
        pass

    def train_AI(self, epochs: int, weights_output: str, weights_input: str=None) -> None:
        ''' Function that trains the AI

        epochs: The amount of training cycles to be gone through
        weights_input: The name of the file in which existing weights have been stored
        weights_output: The name of the file where the calculated weights are to be stored
        '''
        #TODO: Currently trains epochs amount of times on the same dataset, before selecting next dataset
        for dataset_index in range(0, len(self.x)):
            # Create new model with an output shape that fits the dataset
            self.update_model(len(self.y[dataset_index]))
            BasicAI.train_AI(self, epochs, weights_output, weights_input, 
                             np.array([self.x[dataset_index]]), np.array([self.y[dataset_index]]))
            weights_input = weights_output
    
    def run_AI(self, input_data, weights_file: str, desired_word_count: int):
        #TODO: Check if list of multiple lists of input data is possible
        #TODO: Results arent finished yet; need to return the words at the indexes that the current result returns
        ''' Function that runs the AI using the given data/parameters

        input_data: A list containing a list containing the input data for 1 run
            sidenote: In this case each input datapoint consists of a list of floats so the input type is
             np.ndarray(np.ndarray(np.ndarray(np.float64)))
        weights_file: A string containing the name of the file in which the models' weights are stored
        desired_word_count: The amount of desired relevant keywords to be returned
        return: A array filled with the indexes of the found relevant keywords
        '''
        self.update_model(len(input_data[0]))
        return BasicAI.run_AI(self, input_data, weights_file, desired_word_count)