import numpy as np
from typing import List, Any, Dict, Union, Tuple
import pickle
import os.path
from os import path

# Notes from the start of research into AI (containing all kinds of different possibilities we wanted to try out, but never got to):
    # Wat is the input?
        # 1. TF-IDF results, words connected to a value between 0 and 1 that shows its relevance within multiple different texts
        # 2. Sentences
            # 2.1. Full sentences, containing stop-words
            # 2.2. Cleaned sentences, stripped of stop-words
            # 2.3. Lemmanized sentences, each word is lemmanized
            # 2.4. Processed sentences, stripped of stop-words and lemmanized
        # 3. List of words (adjectives, nouns and names) with associated data
        # 4. List of named entities and associated data
        # 5. List of noun chunks and associated data
        # 6. Other kinds of preprocessing? Stuff like the results from other algorithms

    # How to fix the problem with a varying amount of inputs? (Each job offer contains a different amount of words)
        # 1. Recurrent NNs
        # 2. Recursive NNs
        # 3. Sequence2sequence
        # 4. Transformers, like Google BERT
        # 5. Word2Vec

class BasicAI():
    #TODO: The preprocessing extracts all unique entries from a job offer, might be better to not do that there, and instead let the get_dict() function do this job
    ''' Superclass for all AI's
    '''
    def __init__(self, num_to_word_converter: Dict[int, str], x: List[List[Any]], y: List[List[Any]], model: Any) -> None:
        ''' Init AI

        num_to_word_converter: A dictionary containing the information about what integer corresponds with what word
        x: Input data for training
            sidenote: This is a list containing a list for each of the datasets, denoting their inputs
                      Considering the current input for the AI's is a list of 4 numbers, this means that x has the following shape: 
                      (amount of datasets, either filler or unpadded dataset equal to the input length, 4)
        y: Desired output data for given input data
            sidenote: This is a list containing a list for each of the datasets, denoting their outputs
                      Considering the current desired output data for the AI's, y should have the following shape:
                      (amount of datasets, either filler or unpadded dataset equal to the input length)
                      In the case of the seq2seq AI's, the dataset is slightly different:
                      (amount of datasets, either filler or unpadded dataset equal to the input length, 1)
        model: The model that's being trained and ran
            sidenote: The typehint is not defined because the model can be all kinds of types, the ones currently used are:
                      - keras.engine.sequential.Sequential
                      - keras.engine.training.Model
        '''
        self.num_to_word_converter = num_to_word_converter
        self.x = x
        self.y = y
        self.model = model

    def get_dict(self, file_name: str, new_entries: List[str], reverse: bool=True) -> Union[Dict[int, str], Dict[str, int]]:
        ''' Returns a dictionary of all unique entries found, and their corresponding integers
        This function not only returns above mentioned dictionary, but also saves a list of all unique entries as a external file.
        Using this external file, other models can use the same dictionary as this one.

        file_name: The name of the file in which to store all unique entries
        new_entries: A list containing new entries, these need to be unique from each other, but not necessarily from the already saved entries
        reverse: Define whether a dictionary needs to have the entry as a keyword, or to use the corresponding integer as a keyword
        return: A dictionary filled with unique entries and their corresponding integer, either a Dict[str, int] or a Dict[int, str]
        '''
        # Check whether file already exists
        if path.exists("AI/obj/" + file_name + ".pkl"):
            # If so, read it and create new set of unique entries from the existing entries and the new ones
            read_file = open("AI/obj/" + file_name + ".pkl", "rb")
            entries = list(set(pickle.load(read_file) + new_entries))
        else:
            # If not, just select the new entries
            entries = new_entries
        
        # Create new file, and save new unique entries to it
        write_file = open("AI/obj/" + file_name + ".pkl", "wb")
        pickle.dump(entries, write_file, pickle.HIGHEST_PROTOCOL)

        # Depending on the users wishes, return different kinds of dictionaries
        if reverse:
            return dict((key, value) for value, key in enumerate(entries))
        else:
            return dict((value, key) for value, key in enumerate(entries))

    def create_input_data(self, words: List[List[str]], POSs: List[List[str]], tags: List[List[str]], deps: List[List[str]], 
                          word_converter: Dict[str, int], POS_converter: Dict[str, int], tag_converter: Dict[str, int], 
                          dep_converter: Dict[str, int]) -> List[List[Tuple[float, float, float, float]]]:
        #TODO: Is a part of the preprocessing of data, may require changes later on depending on in what format the input data ends up being
        #TODO: Dictionary constantly changes size, so when dividing existing numbers bij dict size, the numbers for the same word change
        ''' Create and return a useable input dataset
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
        zipped_datasets = []
        for dataset_index in range(0, len(words)):
            # For each dataset append a tuple of a word and it's corresponding datapoints, as their corresponding numbers
            zipped_datasets.append(list(zip([word_converter[word]/len(word_converter) for word in words[dataset_index]], 
                                            [POS_converter[POS]/len(POS_converter) for POS in POSs[dataset_index]],
                                            [tag_converter[tag]/len(tag_converter) for tag in tags[dataset_index]],
                                            [dep_converter[dep]/len(dep_converter) for dep in deps[dataset_index]])))
        return zipped_datasets

    def train_AI(self, epochs: int, weights_output: str, weights_input: str=None, x:Union[None, List[List[Any]]]=[], y:Union[None, List[List[Any]]]=[]) -> None:
        ''' Function that trains the AI

        epochs: The amount of training cycles to be gone through
        weights_input: The name of the file in which existing weights have been stored
        weights_output: The name of the file where the calculated weights are to be stored
        x: A custom dataset with inputs, to be used instead of the currently stored one
        y: A custom dataset with outputs, to be used instead of the currently stored one
            sidenote: The way that these (both x and y) list are currently used, is for AI without padding. Training these for all the different sized datasets
                      in 1 go doesn't work and throws errors. Which is why these arguments exist, to provide the possibility to only pass a part of the datasets
                      and thus process them 1 by 1 and not cause any errors.
                      Both these lists are basically the same ones as the ones in self.x and self.y, but instead just contain 1 dataset within the list of datasets.
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
    
    def run_AI(self, input_data: List[List[Any]], weights_file: str, desired_word_count: int) -> Dict[str, int]:
        #TODO: Check if list of multiple lists of input data is possible
        ''' Function that runs the AI using the given data/parameters

        input_data: A list containing a list containing the input data for 1 run
            sidenote: Has the same shape as the original self.x, but with the list being filled with just 1 dataset.
        weights_file: A string containing the name of the file in which the models' weights are stored
        desired_word_count: The amount of desired relevant keywords to be returned
        return: A dictionary filled with the found words, and the amount of times they occured
        '''
        # Get results
        self.model.load_weights(weights_file)
        self.model.compile(loss='mse', optimizer='rmsprop')
        prediction = self.model.predict(input_data)[0].flatten()
        # Get desired_word_count amount of best results
        results = np.argpartition(prediction, -desired_word_count)[-desired_word_count:]
        # Turn selected results back into words
        answers = [self.num_to_word_converter[int(round(input_data[0][index][0] * len(self.num_to_word_converter)))] for index in results]
        dict_answers = dict((word, answers.count(word)) for word in answers)
        return dict_answers
    
    def get_x_data(self) -> List[List[Any]]:
        ''' Returns the created input_data
        Temporary function for getting viable input data

        return: Completely processed input data that is ready to be used
        '''
        return self.x


class BasicAIPadding(BasicAI):
    #TODO: Try padding using either 0, -1 or other number to check which is best
    #TODO: Padding creates this bug where the best results are the ones gained from padding, ergo the 0's, 
    # which returns a list of the same useless word at word_to_num_converter[0]
    #TODO: Find a solution for what to do when the dataset is longer than selected filler-size
    ''' Superclass for all AI's that use padding
    '''
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filler: int, filled_with: List[Any], model) -> None:
        ''' Init AI
        
        datasets: A tuple containing the dataset inputs, dataset desired outputs and all unique attributes in the dataset.
            sidenote: For a more specific denotion of what this tuple looks like, it's exactly the same as the output from the load_datasets() function in preprocessing.py.
        filler: An integer denoting the total length of both the in- and output arrays, said arrays will be padded up to the given size.
        filled_with: A list containing with what to fill the resulting lists, 1st pos for correct answers, 2nd pos for incorrect ones and 3rd pos
         for all the filler.
        model: The model that's being trained and ran
            sidenote: The typehint is not defined because the model can be all kinds of types, the ones currently used are:
                      - keras.engine.sequential.Sequential
                      - keras.engine.training.Model
        '''
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
            # For each dataset, create list representing all words in the current result
            # Afterwards pad the output data so it's always the same size
            y_data.append([filled_with[0] if word in results[result_set_index] else filled_with[1] for word in x_data[0][result_set_index]] + 
                          [filled_with[2] for i in range(0, filler - len(x_data[0][result_set_index]))])
    
        # Pad each set of inputs so they're always the same size
        x = np.array([data + [[0, 0, 0, 0] for i in range(0, filler - len(data))] for data in processed_x_data])
        y = np.array(y_data)

        # Create AI
        BasicAI.__init__(self, num_to_word_converter, x, y, model)


class BasicAINoPadding(BasicAI):
    ''' Superclass for all AI's that don't use padding
    '''
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filled_with, model) -> None:
        ''' Init AI
        
        datasets: A tuple containing the dataset inputs, dataset desired outputs and all unique attributes in the dataset.
            sidenote: For a more specific denotion of what this tuple looks like, it's exactly the same as the output from the load_datasets() function in preprocessing.py.
        filled_with: A list containing with what to fill the resulting lists, 1st pos for correct answers, 2nd pos for incorrect ones and 3rd pos
         for all the filler.
        model: The model that's being trained and ran
            sidenote: The typehint is not defined because the model can be all kinds of types, the ones currently used are:
                      - keras.engine.sequential.Sequential
                      - keras.engine.training.Model
        '''
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
            # For each dataset, create list representing all words in the current result
            y_data.append([filled_with[0] if word in results[result_set_index] else filled_with[1] for word in x_data[0][result_set_index]])
    
        x = np.array(processed_x_data)
        y = np.array(y_data)

        # Create AI
        BasicAI.__init__(self, num_to_word_converter, x, y, model)

    def update_model(self, output_length: int) -> None:
        ''' Empty function that is to be inherited and changed by subclasses

        output_length: The length of the output array for the new model
        '''
        pass

    def train_AI(self, epochs: int, weights_output: str, weights_input: str=None) -> None:
        #TODO: Currently trains epochs amount of times on the same dataset, before selecting next dataset
        ''' Function that trains the AI

        epochs: The amount of training cycles to be gone through
        weights_input: The name of the file in which existing weights have been stored
        weights_output: The name of the file where the calculated weights are to be stored
        '''
        for dataset_index in range(0, len(self.x)):
            # Create new model with an output shape that fits the dataset
            self.update_model(len(self.y[dataset_index]))
            # Train the new model
            BasicAI.train_AI(self, epochs, weights_output, weights_input, 
                             np.array([self.x[dataset_index]]), np.array([self.y[dataset_index]]))
            # Save the weights for use in next iteration
            weights_input = weights_output
    
    def run_AI(self, input_data, weights_file: str, desired_word_count: int) -> Dict[str, int]:
        ''' Function that runs the AI using the given data/parameters

        input_data: A list containing a list containing the input data for 1 run
            sidenote: Has the same shape as the original self.x, but with the list being filled with just 1 dataset.
        weights_file: A string containing the name of the file in which the models' weights are stored
        desired_word_count: The amount of desired relevant keywords to be returned
        return: A dictionary filled with the found words, and the amount of times they occured
        '''
        # Change the model
        self.update_model(len(input_data[0]))
        # Run
        return BasicAI.run_AI(self, input_data, weights_file, desired_word_count)
