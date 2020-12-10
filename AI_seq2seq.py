import codecs
import spacy
import numpy as np
import seq2seq.seq2seq
from seq2seq.seq2seq.models import SimpleSeq2Seq
from typing import List, Any, Dict, Union, Tuple

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


class AI_Seq2SeqPadding():
    ''' AI using Seq2Seq, using padding to equalize all inputs/outputs and using 1/0 for every word to denote relevancy.
    '''
    #TODO: Other options include:
        # - Pad using either 0, -1 or other number
        # - Creating new model every time a different input/output size is required
        # - Output instead of using 1/0 to denote relevancy, only display the relevant words via copying them from input
    def __init__(self, datasets: Tuple(List(List(List(str))), List(List(str)), List(List(str))), filler: int, 
                 depth: Union(int, List(int))) -> None:
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
        self.num_to_word_converter = dict((num, word) for num, word in enumerate(uniques[0]))

        # Get a useable form of input data
        processed_x_data = self.create_input_data(*x_data, word_to_num_converter, POS_to_num_converter, tag_to_num_converter, dep_to_num_converter)
        
        # Get a useable form of output data
        y_data = []
        for result_set_index in range(0, len(results)):
            # For each dataset, create list representing all words in the current result, 1 for relevant keywords, and 
            # 0 for irrelevant ones
            # Afterwards pad the output data so it's always the same size
            y_data.append([[1] if word in results[result_set_index] else [0] for word in x_data[0][result_set_index]] + [[-1] for i in range(0, filler - len(x_data[0][result_set_index]))])
    
        # Pad each set of inputs so they're always the same size
        self.x = np.array([data + [[0, 0, 0, 0] for i in range(0, filler - len(data))] for data in processed_x_data])
        self.y = np.array(y_data)

        # Create model
        self.model = SimpleSeq2Seq(input_dim=4, output_length=filler, output_dim=1, depth=depth)

    def create_input_data(self, words: List(List(str)), POSs: List(List(str)), tags: List(List(str)), deps: List(List(str)), 
                          word_converter: Dict(str, int), POS_converter: Dict(str, int), tag_converter: Dict(str, int), 
                          dep_converter: Dict(str, int)) -> List(List(Tuple(float, float, float, float))):
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
        zipped_datasets = []
        for dataset_index in range(0, len(words)):
            # For each dataset append a tuple of a word and it's corresponding datapoints
            zipped_datasets.append(list(zip([word_converter[word]/len(word_converter) for word in words[dataset_index]], 
                                            [POS_converter[POS]/len(POS_converter) for POS in POSs[dataset_index]],
                                            [tag_converter[tag]/len(tag_converter) for tag in tags[dataset_index]],
                                            [dep_converter[dep]/len(dep_converter) for dep in deps[dataset_index]])))
        return zipped_datasets

    def train_AI(self, epochs: int, weights_output: str, weights_input: str=None) -> None:
        ''' Function that trains the AI

        epochs: The amount of training cycles to be gone through
        weights_input: The name of the file in which existing weights have been stored
        weights_output: The name of the file where the calculated weights are to be stored
        '''
        # Check if a set of existing weights has been given
        if weights_input:
            self.model.load_weights(weights_input)
        # Train the model and save the resulting weights
        self.model.compile(loss='mse', optimizer='rmsprop')
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
        print(prediction)
        # Get desired_word_count amount of best results
        results = np.argpartition(prediction, -desired_word_count)[-desired_word_count:]
        print(results)
        return results
    
    def get_x_data(self):
        ''' Returns the created input_data
        Temporary function
        '''
        return self.x


def train_seq2seq_padding_AI():
    #TODO: Fix preprocessing, is unnecessarily complicated i think
    # Connect to database and get data
    datasets = load_datasets(["vac_1", "vac_2", "vac_3"]) # Temporary measure
    
    # Create AI class
    AI = AI_Seq2SeqPadding(datasets, 1000, 4)

    # Train AI
    # AI.train_AI(200, "temp.hdf5")

    # Run the AI with selected input
    x = np.asarray([AI.get_x_data()[0]])
    AI.run_AI(x, "own_AI_v3_weights.hdf5", 10)



train_seq2seq_padding_AI()








